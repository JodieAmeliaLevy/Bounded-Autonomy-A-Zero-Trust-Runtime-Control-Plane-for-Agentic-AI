from __future__ import annotations

import json
from dataclasses import dataclass, field

from .models import ActionRequest
from .semantics import (
    SemanticCapability,
    classify_action,
)


@dataclass
class InformationFlowGuard:
    """
    Superseded control, kept as a comparison arm.

    This tracks the exact string returned by a protected read and blocks
    outbound payloads containing it. Transformation defeats it: base64,
    reversal, chunking and paraphrase all pass. That is the finding in
    docs/findings/transformation_and_lineage.md, and it is why
    `data_lineage.LineageFlowGuard` exists.

    It is deliberately not fixed. Deleting the broken control would remove
    the arm that makes the improvement measurable, and a reader should be
    able to reproduce the failure rather than take the write-up on trust.
    Do not use it as the guard in new experiments.
    """

    protected_resources: frozenset[str]
    allowed_sensitive_destinations: frozenset[str] = field(
        default_factory=frozenset
    )

    def __post_init__(self) -> None:
        self._sensitive_values: set[str] = set()

    def observe(
        self,
        request: ActionRequest,
        tool_result: dict,
    ) -> None:
        semantics = classify_action(request)

        if (
            semantics.capability
            == SemanticCapability.READ_RESOURCE
            and semantics.resource
            in self.protected_resources
        ):
            content = tool_result.get("content")

            if isinstance(content, str) and content:
                self._sensitive_values.add(content)

    def authorize(
        self,
        request: ActionRequest,
    ) -> tuple[bool, str]:
        semantics = classify_action(request)

        if (
            semantics.capability
            != SemanticCapability.EXTERNAL_COMMUNICATION
        ):
            return True, "no information-flow restriction"

        destination = (
            semantics.destination
            or ""
        ).lower()

        payload = json.dumps(
            request.arguments,
            sort_keys=True,
            default=str,
        )

        carries_sensitive_data = any(
            value in payload
            for value in self._sensitive_values
        )

        if not carries_sensitive_data:
            return True, "no tracked sensitive data in outbound payload"

        if destination in {
            item.lower()
            for item in self.allowed_sensitive_destinations
        }:
            return (
                True,
                "sensitive data release explicitly delegated",
            )

        return (
            False,
            (
                "outbound action carries data derived from "
                "a protected resource"
            ),
        )

    @property
    def tracked_sensitive_values_count(self) -> int:
        return len(self._sensitive_values)
