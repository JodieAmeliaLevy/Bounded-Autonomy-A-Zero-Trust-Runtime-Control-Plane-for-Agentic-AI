from __future__ import annotations

from dataclasses import dataclass

from .models import ActionRequest, Decision


@dataclass
class ReviewOutcome:
    approved: bool
    reviewer: str
    note: str = ""


class HumanReviewQueue:
    """In-memory review queue for research/demo use only."""

    def __init__(self) -> None:
        self.pending: list[tuple[ActionRequest, Decision]] = []

    def submit(self, request: ActionRequest, decision: Decision) -> None:
        self.pending.append((request, decision))
