from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import ActionRequest
from .semantics import (
    SemanticCapability,
    classify_action,
)


class AuthorizationMode(str, Enum):
    STRICT = "strict"
    EGRESS = "egress"


@dataclass(frozen=True)
class UserIntent:
    allowed_reads: frozenset[str] = field(
        default_factory=frozenset
    )

    # Kept for compatibility with earlier experiments.
    allowed_external_recipients: frozenset[str] = field(
        default_factory=frozenset
    )

    # General semantic destinations such as hosts, services,
    # accounts or other approved external principals.
    allowed_external_destinations: frozenset[str] = field(
        default_factory=frozenset
    )

    allow_external_send: bool = False

    @property
    def delegated_external_destinations(
        self,
    ) -> frozenset[str]:
        return frozenset(
            destination.lower()
            for destination in (
                self.allowed_external_recipients
                | self.allowed_external_destinations
            )
        )


class IntentAuthorizer:
    """
    Authorize actions according to their semantic effect,
    not merely their tool/action name.
    """

    def __init__(
        self,
        intent: UserIntent,
        mode: AuthorizationMode,
    ) -> None:
        self.intent = intent
        self.mode = mode

    def authorize(
        self,
        request: ActionRequest,
    ) -> tuple[bool, str]:
        semantics = classify_action(request)

        if (
            semantics.capability
            == SemanticCapability.READ_RESOURCE
        ):
            resource = semantics.resource or ""

            if (
                self.mode
                == AuthorizationMode.STRICT
                and resource
                not in self.intent.allowed_reads
            ):
                return (
                    False,
                    (
                        "resource read outside delegated "
                        f"authority: {resource}"
                    ),
                )

            return (
                True,
                "resource read permitted by authorization regime",
            )

        if (
            semantics.capability
            == SemanticCapability.EXTERNAL_COMMUNICATION
        ):
            destination = (
                semantics.destination
                or ""
            ).lower()

            if not self.intent.allow_external_send:
                return (
                    False,
                    (
                        "user did not delegate external "
                        "communication authority"
                    ),
                )

            allowed = (
                self.intent
                .delegated_external_destinations
            )

            if destination not in allowed:
                return (
                    False,
                    (
                        "external destination outside delegated "
                        f"authority: {destination}"
                    ),
                )

            return (
                True,
                (
                    "external communication matches "
                    "delegated destination"
                ),
            )

        return (
            True,
            "no semantic authorization restriction",
        )
