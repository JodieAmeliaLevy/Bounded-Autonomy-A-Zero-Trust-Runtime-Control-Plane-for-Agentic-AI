from __future__ import annotations

from dataclasses import dataclass, field

from .models import ActionRequest


@dataclass
class PermissionStore:
    grants: dict[str, set[str]] = field(default_factory=dict)

    def grant(self, principal_id: str, capability: str) -> None:
        self.grants.setdefault(principal_id, set()).add(capability)

    def revoke(self, principal_id: str, capability: str) -> None:
        self.grants.setdefault(principal_id, set()).discard(capability)

    def is_allowed(self, request: ActionRequest) -> bool:
        capabilities = self.grants.get(request.actor.principal_id, set())
        return request.capability in capabilities or "*" in capabilities
