from __future__ import annotations

from .base import Environment
from ..models import ActionRequest


class SyntheticFilesystem(Environment):
    def __init__(self) -> None:
        self.files: dict[str, str] = {
            "/workspace/readme.txt": "hello",
            "/workspace/private.txt": "synthetic sensitive content",
        }

    def execute(self, request: ActionRequest) -> dict:
        path = str(request.arguments.get("path", ""))
        if request.action == "read":
            return {"ok": path in self.files, "content": self.files.get(path)}
        if request.action == "delete":
            existed = path in self.files
            self.files.pop(path, None)
            return {"ok": existed}
        return {"ok": False, "error": "unsupported action"}
