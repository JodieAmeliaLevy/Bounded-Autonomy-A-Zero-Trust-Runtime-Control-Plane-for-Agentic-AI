from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionType(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class Provenance:
    """
    A record of where information influencing an action came from.

    Provenance is an observation made by the harness about what the agent
    has ingested. It is never supplied by the agent itself: an agent that
    can label its own inputs as trusted can grant itself authority, which
    is the failure recorded in
    docs/findings/agent_supplied_metadata_bypass.md.
    """

    source: str
    trusted: bool
    notes: str = ""


@dataclass(frozen=True)
class ActionRequest:
    """
    A proposed action, normalised for policy evaluation.

    The agent supplies only `tool`, `action` and `arguments`. Every other
    field is stamped by the harness: `provenance` from observed taint,
    `user_authorized` from the user's mandate, and `reversible` from the
    effect registry in `semantics.py`.
    """

    actor: Principal
    task_id: str
    tool: str
    action: str
    arguments: dict[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = ()
    user_authorized: bool = False
    reversible: bool = False

    @property
    def capability(self) -> str:
        return f"{self.tool}:{self.action}"


@dataclass
class MonitorResult:
    suspicious: bool
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class ReviewOutcome:
    approved: bool
    reviewer: str
    note: str = ""


@dataclass
class Decision:
    decision: DecisionType
    risk: RiskTier
    reasons: list[str]
    monitor: MonitorResult | None = None
    review: ReviewOutcome | None = None

    @property
    def permits_execution(self) -> bool:
        if self.decision == DecisionType.ALLOW:
            return True

        if self.decision == DecisionType.ESCALATE:
            return bool(self.review and self.review.approved)

        return False
