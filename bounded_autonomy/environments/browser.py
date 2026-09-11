from __future__ import annotations

from .base import Environment
from ..models import ActionRequest


class SyntheticBrowser(Environment):
    def execute(self, request: ActionRequest) -> dict:
        if request.action == "submit_form":
            return {"ok": True, "submitted": dict(request.arguments)}
        if request.action == "read_page":
            return {"ok": True, "content": "synthetic page content"}
        return {"ok": False, "error": "unsupported action"}
