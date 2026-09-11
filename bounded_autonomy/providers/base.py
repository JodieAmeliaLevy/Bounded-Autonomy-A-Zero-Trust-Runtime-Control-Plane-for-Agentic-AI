from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentStep:
    text: str
    tool_name: str | None = None
    tool_action: str | None = None
    tool_arguments: dict | None = None


class AgentProvider(ABC):
    """Provider-neutral interface for future OpenAI/Anthropic/Gemini adapters."""

    @abstractmethod
    def next_step(self, task: str, transcript: list[dict]) -> AgentStep:
        raise NotImplementedError
