from __future__ import annotations

from dataclasses import dataclass, field

from .authorization import UserIntent, mandate_covers
from .models import ActionRequest, Decision, ReviewOutcome


class Reviewer:
    """A trusted party that adjudicates escalated actions."""

    name = "reviewer"

    def review(
        self,
        request: ActionRequest,
        decision: Decision,
    ) -> ReviewOutcome:
        raise NotImplementedError


class DenyAllReviewer(Reviewer):
    """
    Default reviewer. Nothing is approved unless a real reviewer is
    configured, so an unattended deployment fails closed.
    """

    name = "deny-all"

    def review(
        self,
        request: ActionRequest,
        decision: Decision,
    ) -> ReviewOutcome:
        return ReviewOutcome(
            approved=False,
            reviewer=self.name,
            note="no reviewer configured",
        )


class MandateReviewer(Reviewer):
    """
    Stand in for a user who approves an escalated action when, and only
    when, it falls inside the authority they actually delegated.

    This is an oracle reviewer for experiments. It makes human review
    measurable as a cost (how many approvals the task needed) rather than
    treating every escalation as a failure. It deliberately does not model
    a reviewer who can be persuaded, which is its main limitation.
    """

    name = "mandate-oracle"

    def __init__(self, intent: UserIntent) -> None:
        self.intent = intent

    def review(
        self,
        request: ActionRequest,
        decision: Decision,
    ) -> ReviewOutcome:
        covered, reason = mandate_covers(request, self.intent)

        return ReviewOutcome(
            approved=covered,
            reviewer=self.name,
            note=reason,
        )


@dataclass
class HumanReviewQueue:
    """In memory review queue for research use only."""

    reviewer: Reviewer = field(default_factory=DenyAllReviewer)
    handled: list[tuple[ActionRequest, Decision, ReviewOutcome]] = field(
        default_factory=list
    )

    def submit(
        self,
        request: ActionRequest,
        decision: Decision,
    ) -> ReviewOutcome:
        outcome = self.reviewer.review(request, decision)
        self.handled.append((request, decision, outcome))
        return outcome

    @property
    def review_count(self) -> int:
        return len(self.handled)

    @property
    def approved_count(self) -> int:
        return sum(1 for _, _, outcome in self.handled if outcome.approved)
