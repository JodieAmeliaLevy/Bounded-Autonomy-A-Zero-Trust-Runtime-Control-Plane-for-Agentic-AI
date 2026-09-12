from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentStep:
    """
    What an agent is permitted to say to the harness.

    An agent proposes a tool call and nothing else. It cannot state its own
    provenance, whether the user authorised the action, or whether the
    action is reversible: those are security claims, and a component inside
    the trust boundary does not get to make them about itself. The harness
    derives all three. See docs/findings/agent_supplied_metadata_bypass.md
    for the failure this interface change closes.
    """

    text: str
    tool_name: str | None = None
    tool_action: str | None = None
    tool_arguments: dict | None = None


class AgentProvider(ABC):
    @abstractmethod
    def next_step(self, task: str, transcript: list[dict]) -> AgentStep:
        raise NotImplementedError
