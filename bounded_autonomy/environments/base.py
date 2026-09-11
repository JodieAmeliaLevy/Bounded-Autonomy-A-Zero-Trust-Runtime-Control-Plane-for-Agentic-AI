from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import ActionRequest


class Environment(ABC):
    @abstractmethod
    def execute(self, request: ActionRequest) -> dict[str, Any]:
        raise NotImplementedError
