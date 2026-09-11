from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .authorization import IntentAuthorizer
from .control_plane import ControlPlane
from .information_flow import InformationFlowGuard
from .models import ActionRequest, DecisionType, Principal
from .providers.base import AgentProvider
from .environments.base import Environment


@dataclass
class AgentRun:
    task: str
    controlled: bool
    transcript: list[dict[str, Any]] = field(default_factory=list)
    executed_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)


class AgentRunner:
    def __init__(
        self,
        provider: AgentProvider,
        environments: dict[str, Environment],
        principal: Principal,
        control_plane: ControlPlane | None = None,
        authorizer: IntentAuthorizer | None = None,
        flow_guard: InformationFlowGuard | None = None,
        stop_on_block: bool = True,
    ) -> None:
        self.provider = provider
        self.environments = environments
        self.principal = principal
        self.control_plane = control_plane
        self.authorizer = authorizer
        self.flow_guard = flow_guard
        self.stop_on_block = stop_on_block

    def run(self, task: str, max_steps: int = 8) -> AgentRun:
        result = AgentRun(
            task=task,
            controlled=any([
                self.control_plane is not None,
                self.authorizer is not None,
                self.flow_guard is not None,
            ]),
        )

        result.transcript.append({
            "role": "user",
            "content": task,
        })

        for step_index in range(max_steps):
            step = self.provider.next_step(
                task,
                result.transcript,
            )

            result.transcript.append({
                "role": "assistant",
                "content": step.text,
            })

            if not step.tool_name or not step.tool_action:
                break

            request = ActionRequest(
                actor=self.principal,
                task_id=f"agent-step-{step_index + 1}",
                tool=step.tool_name,
                action=step.tool_action,
                arguments=step.tool_arguments or {},
                provenance=step.provenance,
                user_authorized=step.user_authorized,
                reversible=step.reversible,
            )

            if self.authorizer is not None:
                allowed, reason = (
                    self.authorizer.authorize(request)
                )

                result.transcript.append({
                    "role": "authorization",
                    "capability": request.capability,
                    "allowed": allowed,
                    "reason": reason,
                })

                if not allowed:
                    result.blocked_actions.append(
                        request.capability
                    )

                    if self.stop_on_block:
                        break

                    continue

            if self.flow_guard is not None:
                allowed, reason = (
                    self.flow_guard.authorize(request)
                )

                result.transcript.append({
                    "role": "information_flow",
                    "capability": request.capability,
                    "allowed": allowed,
                    "reason": reason,
                })

                if not allowed:
                    result.blocked_actions.append(
                        request.capability
                    )

                    if self.stop_on_block:
                        break

                    continue

            if self.control_plane is not None:
                decision = self.control_plane.evaluate(
                    request
                )

                result.transcript.append({
                    "role": "control_plane",
                    "capability": request.capability,
                    "decision": decision.decision.value,
                    "risk": decision.risk.value,
                    "reasons": decision.reasons,
                })

                if (
                    decision.decision
                    != DecisionType.ALLOW
                ):
                    result.blocked_actions.append(
                        request.capability
                    )

                    if self.stop_on_block:
                        break

                    continue

            environment = self.environments.get(
                request.tool
            )

            if environment is None:
                break

            tool_result = environment.execute(request)

            if self.flow_guard is not None:
                self.flow_guard.observe(
                    request,
                    tool_result,
                )

            result.executed_actions.append(
                request.capability
            )

            result.transcript.append({
                "role": "tool",
                "tool": request.tool,
                "action": request.action,
                "result": tool_result,
            })

        return result
