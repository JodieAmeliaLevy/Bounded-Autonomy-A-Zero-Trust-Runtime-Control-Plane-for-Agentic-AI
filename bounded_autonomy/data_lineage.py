from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ActionRequest
from .semantics import (
    SemanticCapability,
    classify_action,
)


PROTECTED = "protected"


@dataclass(frozen=True)
class DataArtifact:
    artifact_id: str
    value: Any
    labels: frozenset[str]
    parents: tuple[str, ...] = ()


class ArtifactStore:
    def __init__(self) -> None:
        self._artifacts: dict[str, DataArtifact] = {}
        self._counter = 0

    def create(
        self,
        value: Any,
        labels: frozenset[str] = frozenset(),
        parents: tuple[str, ...] = (),
    ) -> DataArtifact:
        # Sequential rather than random: ids only need to be unique within
        # a store, and a deterministic experiment should produce
        # byte-identical output so that a diff of results/ shows which
        # outcome changed rather than which identifiers were regenerated.
        self._counter += 1

        artifact = DataArtifact(
            artifact_id=f"artifact-{self._counter:04d}",
            value=value,
            labels=labels,
            parents=parents,
        )

        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def derive(
        self,
        parent_id: str,
        value: Any,
    ) -> DataArtifact:
        parent = self.get(parent_id)

        return self.create(
            value=value,
            labels=parent.labels,
            parents=(parent.artifact_id,),
        )

    def get(
        self,
        artifact_id: str,
    ) -> DataArtifact:
        return self._artifacts[artifact_id]

    def is_protected(
        self,
        artifact_id: str,
    ) -> bool:
        return PROTECTED in self.get(artifact_id).labels


class LineageFlowGuard:
    """
    Enforces sensitive-data policy using persistent provenance labels
    rather than literal string matching.

    Two properties matter for the guard to mean anything:

    1. Labels are attached by the guard when it observes a protected read,
       not by the agent choosing to carry an ``artifact_id``.
    2. Once the session has touched protected data, an outbound payload
       whose lineage cannot be established is denied. Allowing unlabelled
       egress reproduced the cross-tool bypass one layer down: an agent
       could simply drop the ``artifact_id`` and send the raw value.
       See docs/findings/unlabelled_egress_bypass.md.
    """

    def __init__(
        self,
        store: ArtifactStore,
        protected_resources: frozenset[str] = frozenset(),
        allowed_sensitive_destinations: frozenset[str] = frozenset(),
    ) -> None:
        self.store = store
        self.protected_resources = frozenset(protected_resources)
        self.allowed_sensitive_destinations = frozenset(
            item.lower()
            for item in allowed_sensitive_destinations
        )
        self._session_touched_protected = False

    @property
    def session_touched_protected(self) -> bool:
        return self._session_touched_protected

    def _destination_is_delegated(
        self,
        semantics,
    ) -> bool:
        destination = (semantics.destination or "").lower()
        return destination in self.allowed_sensitive_destinations

    def observe(
        self,
        request: ActionRequest,
        tool_result: dict,
    ) -> None:
        """
        Attach labels and record taint from what the tool actually returned.

        This runs on every executed action. An earlier version was a no-op,
        which meant nothing in the system ever labelled data at runtime and
        the guard only worked on artifacts the attacker volunteered.
        """

        if not isinstance(tool_result, dict):
            return

        semantics = classify_action(request)

        artifact_id = tool_result.get("artifact_id")

        if artifact_id:
            try:
                if self.store.is_protected(str(artifact_id)):
                    self._session_touched_protected = True
            except KeyError:
                pass

            return

        if semantics.capability != SemanticCapability.READ_RESOURCE:
            return

        if semantics.resource not in self.protected_resources:
            return

        content = tool_result.get("content")

        if content is None:
            return

        artifact = self.store.create(
            value=content,
            labels=frozenset({PROTECTED}),
        )

        tool_result["artifact_id"] = artifact.artifact_id
        tool_result["labels"] = sorted(artifact.labels)
        self._session_touched_protected = True

    def authorize(
        self,
        request: ActionRequest,
    ) -> tuple[bool, str]:
        semantics = classify_action(request)

        if not semantics.is_egress:
            return True, "no lineage restriction"

        artifact_id = request.arguments.get("artifact_id")

        if artifact_id:
            try:
                protected = self.store.is_protected(str(artifact_id))
            except KeyError:
                return False, "unknown artifact reference"

            if not protected:
                return True, "artifact is not protected"

            if self._destination_is_delegated(semantics):
                return True, "protected artifact release explicitly delegated"

            return (
                False,
                "external action carries an artifact derived from protected data",
            )

        if not self._session_touched_protected:
            return True, "session has not read protected data"

        if self._destination_is_delegated(semantics):
            return True, "unlabelled release to a delegated destination"

        return (
            False,
            (
                "outbound payload has no lineage and this session has read "
                "protected data"
            ),
        )
