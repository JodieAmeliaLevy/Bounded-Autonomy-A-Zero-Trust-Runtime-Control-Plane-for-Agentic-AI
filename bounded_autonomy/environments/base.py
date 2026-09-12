from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import ActionRequest


class Environment(ABC):
    #: Whether output from this environment may be treated as a trusted
    #: source of authority. Nothing is trusted by default: a file, a web
    #: page and an inbox can all carry instructions written by someone
    #: other than the user.
    trusted_output: bool = False

    @abstractmethod
    def execute(self, request: ActionRequest) -> dict[str, Any]:
        raise NotImplementedError
