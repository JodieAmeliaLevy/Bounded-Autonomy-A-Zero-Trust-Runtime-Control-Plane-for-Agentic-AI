from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models import Provenance


@dataclass
class AgentStep:
    text: str
    tool_name: str | None = None
    tool_action: str | None = None
    tool_arguments: dict | None = None
    provenance: tuple[Provenance, ...] = ()
    user_authorized: bool = True
    reversible: bool = True


class AgentProvider(ABC):
    @abstractmethod
    def next_step(self, task: str, transcript: list[dict]) -> AgentStep:
        raise NotImplementedError
