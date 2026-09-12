from __future__ import annotations

from typing import Protocol

from .models import ActionRequest


class FlowGuard(Protocol):
    """Common interface for runtime information-flow enforcement."""

    def authorize(
        self,
        request: ActionRequest,
    ) -> tuple[bool, str]:
        ...

    def observe(
        self,
        request: ActionRequest,
        tool_result: dict,
    ) -> None:
        ...
