from __future__ import annotations

from .base import Environment
from ..models import ActionRequest


class SyntheticShell(Environment):
    trusted_output = False

    """Never executes real system commands."""

    def execute(self, request: ActionRequest) -> dict:
        if request.action in {"execute", "execute_privileged"}:
            return {"ok": True, "simulated": True, "command": request.arguments.get("command", "")}
        return {"ok": False, "error": "unsupported action"}
