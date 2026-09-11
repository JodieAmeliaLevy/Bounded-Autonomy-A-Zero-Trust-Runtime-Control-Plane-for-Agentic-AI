from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

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

    def create(
        self,
        value: Any,
        labels: frozenset[str] = frozenset(),
        parents: tuple[str, ...] = (),
    ) -> DataArtifact:
        artifact = DataArtifact(
            artifact_id=f"artifact-{uuid4().hex[:12]}",
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
    """

    def __init__(
        self,
        store: ArtifactStore,
        allowed_sensitive_destinations: frozenset[str] = frozenset(),
    ) -> None:
        self.store = store
        self.allowed_sensitive_destinations = frozenset(
            item.lower()
            for item in allowed_sensitive_destinations
        )

    def authorize(
        self,
        request: ActionRequest,
    ) -> tuple[bool, str]:
        semantics = classify_action(request)

        if (
            semantics.capability
            != SemanticCapability.EXTERNAL_COMMUNICATION
        ):
            return True, "no lineage restriction"

        artifact_id = request.arguments.get("artifact_id")

        if not artifact_id:
            return True, "no labeled artifact attached"

        try:
            protected = self.store.is_protected(str(artifact_id))
        except KeyError:
            return False, "unknown artifact reference"

        if not protected:
            return True, "artifact is not protected"

        destination = (
            semantics.destination
            or ""
        ).lower()

        if destination in self.allowed_sensitive_destinations:
            return (
                True,
                "protected artifact release explicitly delegated",
            )

        return (
            False,
            "external action carries an artifact derived from protected data",
        )

    def observe(
        self,
        request: ActionRequest,
        tool_result: dict,
    ) -> None:
        return None
