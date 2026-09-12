from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from .models import ActionRequest


class SemanticCapability(str, Enum):
    """
    Security relevant effect of an action, independent of the tool that
    performs it.

    Policy reasons over these effects. Reasoning over tool names was the
    cause of the cross tool egress bypass recorded in
    docs/findings/cross_tool_egress_bypass.md.
    """

    INSPECT = "inspect"
    READ_RESOURCE = "read_resource"
    WRITE_RESOURCE = "write_resource"
    DERIVE_DATA = "derive_data"
    DESTRUCTIVE = "destructive"
    EXTERNAL_COMMUNICATION = "external_communication"
    CODE_EXECUTION = "code_execution"
    PRIVILEGE_CHANGE = "privilege_change"
    RESOURCE_TRANSFER = "resource_transfer"

    #: Assigned to any tool/action pair that is not in the registry.
    #: Callers must treat this as the most dangerous case, never the least.
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class EffectSpec:
    """Declared, reviewable security effect of one tool/action pair."""

    capability: SemanticCapability
    reversible: bool
    resource_arg: str | None = None
    destination_arg: str | None = None
    destination_is_url: bool = False


#: The only place in the codebase where a tool/action pair acquires a
#: security meaning. Adding a tool without adding it here leaves it
#: UNKNOWN, which fails closed rather than defaulting to low risk.
EFFECT_REGISTRY: dict[tuple[str, str], EffectSpec] = {
    ("filesystem", "read"): EffectSpec(
        SemanticCapability.READ_RESOURCE,
        reversible=True,
        resource_arg="path",
    ),
    ("filesystem", "write"): EffectSpec(
        SemanticCapability.WRITE_RESOURCE,
        reversible=False,
        resource_arg="path",
    ),
    ("filesystem", "write_sensitive"): EffectSpec(
        SemanticCapability.WRITE_RESOURCE,
        reversible=False,
        resource_arg="path",
    ),
    ("filesystem", "delete"): EffectSpec(
        SemanticCapability.DESTRUCTIVE,
        reversible=False,
        resource_arg="path",
    ),
    ("email", "read_inbox"): EffectSpec(
        SemanticCapability.INSPECT,
        reversible=True,
    ),
    ("email", "draft"): EffectSpec(
        SemanticCapability.WRITE_RESOURCE,
        reversible=True,
    ),
    ("email", "send_external"): EffectSpec(
        SemanticCapability.EXTERNAL_COMMUNICATION,
        reversible=False,
        destination_arg="to",
    ),
    ("browser", "read_page"): EffectSpec(
        SemanticCapability.INSPECT,
        reversible=True,
        resource_arg="url",
    ),
    ("browser", "submit_form"): EffectSpec(
        SemanticCapability.EXTERNAL_COMMUNICATION,
        reversible=False,
        destination_arg="url",
        destination_is_url=True,
    ),
    ("browser", "submit_artifact"): EffectSpec(
        SemanticCapability.EXTERNAL_COMMUNICATION,
        reversible=False,
        destination_arg="url",
        destination_is_url=True,
    ),
    ("transform", "transform"): EffectSpec(
        SemanticCapability.DERIVE_DATA,
        reversible=True,
    ),
    ("shell", "execute"): EffectSpec(
        SemanticCapability.CODE_EXECUTION,
        reversible=False,
    ),
    ("shell", "execute_privileged"): EffectSpec(
        SemanticCapability.PRIVILEGE_CHANGE,
        reversible=False,
    ),
    ("identity", "change_permissions"): EffectSpec(
        SemanticCapability.PRIVILEGE_CHANGE,
        reversible=False,
    ),
    ("payments", "transfer"): EffectSpec(
        SemanticCapability.RESOURCE_TRANSFER,
        reversible=False,
        destination_arg="to",
    ),
}


#: Effects that move information or control outside the trust boundary.
EGRESS_CAPABILITIES = frozenset({
    SemanticCapability.EXTERNAL_COMMUNICATION,
    SemanticCapability.RESOURCE_TRANSFER,
})


@dataclass(frozen=True)
class ActionSemantics:
    capability: SemanticCapability
    resource: str | None = None
    destination: str | None = None
    reversible: bool = False
    registered: bool = True

    @property
    def is_egress(self) -> bool:
        return self.capability in EGRESS_CAPABILITIES


def _normalise_destination(raw: str, is_url: bool) -> str:
    value = raw.strip().lower()

    if not is_url:
        return value

    parsed = urlparse(value)
    return (parsed.hostname or value).lower()


def classify_action(request: ActionRequest) -> ActionSemantics:
    """
    Map a tool call onto its declared security effect.

    An unregistered tool/action pair is reported as UNKNOWN and
    irreversible so that every downstream control treats it as the worst
    case rather than the best case.
    """

    spec = EFFECT_REGISTRY.get((request.tool, request.action))

    if spec is None:
        return ActionSemantics(
            capability=SemanticCapability.UNKNOWN,
            reversible=False,
            registered=False,
        )

    resource = None
    if spec.resource_arg is not None:
        resource = str(request.arguments.get(spec.resource_arg, ""))

    destination = None
    if spec.destination_arg is not None:
        destination = _normalise_destination(
            str(request.arguments.get(spec.destination_arg, "")),
            spec.destination_is_url,
        )

    return ActionSemantics(
        capability=spec.capability,
        resource=resource,
        destination=destination,
        reversible=spec.reversible,
        registered=True,
    )


def registered_capabilities() -> tuple[str, ...]:
    return tuple(sorted(f"{tool}:{action}" for tool, action in EFFECT_REGISTRY))
