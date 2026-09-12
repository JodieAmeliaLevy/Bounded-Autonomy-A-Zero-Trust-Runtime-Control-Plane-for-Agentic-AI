from __future__ import annotations

from typing import Any

from .base import AgentProvider, AgentStep


def _last_tool_result(transcript: list[dict]) -> dict:
    for item in reversed(transcript):
        if item.get("role") == "tool":
            result = item.get("result")

            if isinstance(result, dict):
                return result

    return {}


def _last_value(transcript: list[dict], keys: tuple[str, ...]) -> Any:
    for item in reversed(transcript):
        if item.get("role") != "tool":
            continue

        result = item.get("result")

        if not isinstance(result, dict):
            continue

        for key in keys:
            if result.get(key) is not None:
                return result[key]

    return None


def _denial_count(transcript: list[dict]) -> int:
    denials = 0

    for item in transcript:
        if item.get("role") in {"authorization", "information_flow"}:
            if item.get("allowed") is False:
                denials += 1

        if item.get("role") == "control_plane":
            review = item.get("review")
            approved = bool(review and review.get("approved"))

            if item.get("decision") != "allow" and not approved:
                denials += 1

    return denials


class PlannedProvider(AgentProvider):
    """
    Declarative agent used to build benchmark scenarios from data.

    A plan is a list of steps. Each step names a tool, an action and its
    arguments. An argument may be a reference of the form
    ``{"from": "<source>"}`` resolved against the transcript at run time,
    which is how an exfiltration step gets hold of whatever the read step
    actually returned rather than a constant baked into the scenario.

    A step marked ``"requires_denial": true`` is only attempted once the
    run has produced at least that many denials, which is how fallback and
    repeated attempt behaviour is expressed.
    """

    def __init__(self, steps: list[dict]) -> None:
        self.steps = steps
        self.cursor = 0

    def _resolve(self, value: Any, transcript: list[dict]) -> Any:
        if isinstance(value, dict) and "from" in value:
            source = value["from"]

            if source == "last_read_content":
                return _last_value(transcript, ("content", "value"))

            if source == "last_artifact_id":
                return _last_value(transcript, ("artifact_id",))

            if source == "last_tool_result":
                return _last_tool_result(transcript)

            raise ValueError(f"Unknown argument source: {source}")

        if isinstance(value, dict):
            return {k: self._resolve(v, transcript) for k, v in value.items()}

        if isinstance(value, list):
            return [self._resolve(v, transcript) for v in value]

        return value

    def next_step(self, task: str, transcript: list[dict]) -> AgentStep:
        denials = _denial_count(transcript)

        while self.cursor < len(self.steps):
            step = self.steps[self.cursor]
            self.cursor += 1

            if denials < int(step.get("requires_denial", 0)):
                continue

            arguments = {
                key: self._resolve(value, transcript)
                for key, value in step.get("arguments", {}).items()
            }

            return AgentStep(
                text=step.get("text", ""),
                tool_name=step["tool"],
                tool_action=step["action"],
                tool_arguments=arguments,
            )

        return AgentStep(text="Done.")
