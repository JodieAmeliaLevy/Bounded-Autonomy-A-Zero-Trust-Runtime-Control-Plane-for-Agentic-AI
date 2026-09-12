from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import ActionRequest
from .semantics import SemanticCapability, classify_action


class AuthorizationMode(str, Enum):
    #: Enforce the whole mandate: reads, writes and egress.
    STRICT = "strict"
    #: Enforce only actions that cross the trust boundary. Kept as an
    #: ablation so the marginal value of mediating reads is measurable.
    EGRESS = "egress"


@dataclass(frozen=True)
class UserIntent:
    """
    The authority the user actually delegated for this task.

    This is the harness's record of the mandate. It is supplied when a run
    starts and is never derived from anything the agent says, so an agent
    cannot widen it by asserting that an action was authorised.
    """

    allowed_reads: frozenset[str] = field(default_factory=frozenset)
    allowed_writes: frozenset[str] = field(default_factory=frozenset)

    # Kept for compatibility with earlier experiments.
    allowed_external_recipients: frozenset[str] = field(
        default_factory=frozenset
    )

    # General semantic destinations such as hosts, services,
    # accounts or other approved external principals.
    allowed_external_destinations: frozenset[str] = field(
        default_factory=frozenset
    )

    #: Destinations the user delegated to receive protected data. Being
    #: contactable is not the same authority as being allowed to receive
    #: sensitive material, and conflating the two is how a legitimate
    #: reporting endpoint becomes an exfiltration channel.
    sensitive_release_destinations: frozenset[str] = field(
        default_factory=frozenset
    )

    #: Effects delegated wholesale, named by SemanticCapability value.
    #: Required for destructive, code execution and privilege changing
    #: effects, which are never implicitly in scope.
    allowed_capabilities: frozenset[str] = field(default_factory=frozenset)

    allow_external_send: bool = False
    allow_inspect: bool = True

    @property
    def delegated_sensitive_destinations(self) -> frozenset[str]:
        return frozenset(
            destination.lower()
            for destination in self.sensitive_release_destinations
        )

    @property
    def delegated_external_destinations(self) -> frozenset[str]:
        return frozenset(
            destination.lower()
            for destination in (
                self.allowed_external_recipients
                | self.allowed_external_destinations
            )
        )


def mandate_covers(
    request: ActionRequest,
    intent: UserIntent,
) -> tuple[bool, str]:
    """
    Decide whether a proposed action falls inside delegated authority.

    Returns (covered, reason). Anything the mandate does not describe is
    not covered, including effects the registry does not recognise.
    """

    semantics = classify_action(request)
    capability = semantics.capability

    if capability == SemanticCapability.UNKNOWN:
        return False, (
            "action has no registered security effect: "
            f"{request.capability}"
        )

    if capability == SemanticCapability.INSPECT:
        if intent.allow_inspect:
            return True, "inspection is within delegated authority"

        return False, "user did not delegate inspection authority"

    if capability == SemanticCapability.DERIVE_DATA:
        return True, "derivation does not cross a trust boundary"

    if capability == SemanticCapability.READ_RESOURCE:
        resource = semantics.resource or ""

        if resource in intent.allowed_reads:
            return True, f"read of delegated resource: {resource}"

        return False, f"resource read outside delegated authority: {resource}"

    if capability == SemanticCapability.WRITE_RESOURCE:
        resource = semantics.resource or ""

        if resource in intent.allowed_writes:
            return True, f"write to delegated resource: {resource}"

        return False, f"resource write outside delegated authority: {resource}"

    if semantics.is_egress:
        destination = (semantics.destination or "").lower()

        if not intent.allow_external_send:
            return False, "user did not delegate external communication authority"

        if destination in intent.delegated_external_destinations:
            return True, f"external destination is delegated: {destination}"

        return False, (
            "external destination outside delegated authority: "
            f"{destination}"
        )

    if capability.value in intent.allowed_capabilities:
        return True, f"effect explicitly delegated: {capability.value}"

    return False, f"effect not delegated: {capability.value}"


class IntentAuthorizer:
    """
    Authorize actions according to their semantic effect, not their
    tool/action name.
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
            self.mode == AuthorizationMode.EGRESS
            and not semantics.is_egress
            and semantics.capability != SemanticCapability.UNKNOWN
        ):
            return True, "egress-only regime does not mediate this effect"

        return mandate_covers(request, self.intent)
