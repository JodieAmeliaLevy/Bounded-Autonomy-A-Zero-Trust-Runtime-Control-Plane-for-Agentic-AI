from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import ActionRequest, Decision


class AuditLogger:
    def __init__(self, path: str | Path = "results/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, request: ActionRequest, decision: Decision) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": asdict(request),
            "decision": asdict(decision),
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
