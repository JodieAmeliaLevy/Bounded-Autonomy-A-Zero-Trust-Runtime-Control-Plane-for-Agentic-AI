from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import ActionRequest


class AuthorizationMode(str, Enum):
    STRICT = "strict"
    EGRESS = "egress"


@dataclass(frozen=True)
class UserIntent:
    allowed_reads: frozenset[str] = field(default_factory=frozenset)
    allowed_external_recipients: frozenset[str] = field(default_factory=frozenset)
    allow_external_send: bool = False


class IntentAuthorizer:
    """
    Enforces authority derived from the user's original intent.

    STRICT:
        Unauthorized sensitive reads are blocked as soon as they are attempted.

    EGRESS:
        Reads may proceed, but external sends remain bound to the user's
        delegated recipient set.
    """

    def __init__(self, intent: UserIntent, mode: AuthorizationMode) -> None:
        self.intent = intent
        self.mode = mode

    def authorize(self, request: ActionRequest) -> tuple[bool, str]:
        if request.tool == "filesystem" and request.action == "read":
            path = str(request.arguments.get("path", ""))

            if (
                self.mode == AuthorizationMode.STRICT
                and path not in self.intent.allowed_reads
            ):
                return False, f"read not delegated by user: {path}"

            return True, "read permitted by authorization regime"

        if request.tool == "email" and request.action == "send_external":
            recipient = str(request.arguments.get("to", ""))

            if not self.intent.allow_external_send:
                return False, "user did not delegate external email authority"

            if recipient not in self.intent.allowed_external_recipients:
                return (
                    False,
                    f"recipient outside delegated authority: {recipient}",
                )

            return True, "external send matches delegated recipient"

        return True, "no additional intent restriction"
