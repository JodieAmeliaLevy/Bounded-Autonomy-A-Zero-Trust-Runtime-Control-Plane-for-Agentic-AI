from __future__ import annotations

from .base import Environment
from ..models import ActionRequest


class SyntheticBrowser(Environment):
    def __init__(self) -> None:
        self.submissions: list[dict] = []

    def execute(self, request: ActionRequest) -> dict:
        if request.action == "submit_form":
            submission = dict(request.arguments)
            self.submissions.append(submission)

            return {
                "ok": True,
                "submitted": submission,
            }

        if request.action == "read_page":
            return {
                "ok": True,
                "content": "synthetic page content",
            }

        return {
            "ok": False,
            "error": "unsupported action",
        }
