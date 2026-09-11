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
    MODIFY = "modify"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class Provenance:
    source: str
    trusted: bool
    notes: str = ""


@dataclass(frozen=True)
class ActionRequest:
    actor: Principal
    task_id: str
    tool: str
    action: str
    arguments: dict[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = ()
    user_authorized: bool = True
    reversible: bool = True

    @property
    def capability(self) -> str:
        return f"{self.tool}:{self.action}"


@dataclass
class MonitorResult:
    suspicious: bool
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class Decision:
    decision: DecisionType
    risk: RiskTier
    reasons: list[str]
    monitor: MonitorResult | None = None
    modified_arguments: dict[str, Any] | None = None
