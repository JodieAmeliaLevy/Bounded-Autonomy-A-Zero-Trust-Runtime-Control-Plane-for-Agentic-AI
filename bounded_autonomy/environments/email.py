from __future__ import annotations

from .base import Environment
from ..models import ActionRequest


class SyntheticEmailEnvironment(Environment):
    """Safe in-memory email environment for evals."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def execute(self, request: ActionRequest) -> dict:
        if request.action != "send_external":
            return {"ok": False, "error": "unsupported action"}
        message = {
            "to": request.arguments.get("to"),
            "subject": request.arguments.get("subject", ""),
            "body": request.arguments.get("body", ""),
        }
        self.sent.append(message)
        return {"ok": True, "message": message}
