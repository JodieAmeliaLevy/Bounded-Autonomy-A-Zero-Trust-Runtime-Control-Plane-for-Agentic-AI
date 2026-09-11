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
    Minimal research prototype for tracking sensitive information
    across agent actions.

    This version uses exact synthetic-value tracking. It is deliberately
    simple; later experiments will test transformations that defeat it.
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
