from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .authorization import IntentAuthorizer, UserIntent, mandate_covers
from .control_plane import ControlPlane
from .flow_guard import FlowGuard
from .models import ActionRequest, Principal, Provenance
from .providers.base import AgentProvider
from .environments.base import Environment
from .semantics import classify_action


@dataclass
class AgentRun:
    task: str
    controlled: bool
    transcript: list[dict[str, Any]] = field(default_factory=list)
    executed_actions: list[str] = field(default_factory=list)
    executed_requests: list[ActionRequest] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    escalated_actions: list[str] = field(default_factory=list)
    review_count: int = 0
    approved_reviews: int = 0


class AgentRunner:
    """
    Runs an agent against synthetic environments behind the control plane.

    The runner owns every security relevant fact about a proposed action.
    The agent supplies a tool name, an action and arguments; the runner
    stamps provenance from what the session has actually ingested,
    authority from the user's mandate, and reversibility from the effect
    registry.
    """

    def __init__(
        self,
        provider: AgentProvider,
        environments: dict[str, Environment],
        principal: Principal,
        mandate: UserIntent | None = None,
        control_plane: ControlPlane | None = None,
        authorizer: IntentAuthorizer | None = None,
        flow_guard: FlowGuard | None = None,
        stop_on_block: bool = True,
    ) -> None:
        self.provider = provider
        self.environments = environments
        self.principal = principal
        self.mandate = mandate
        self.control_plane = control_plane
        self.authorizer = authorizer
        self.flow_guard = flow_guard
        self.stop_on_block = stop_on_block

    def _stamp(
        self,
        request: ActionRequest,
        ingested: list[Provenance],
    ) -> ActionRequest:
        semantics = classify_action(request)

        if self.mandate is None:
            authorized = False
        else:
            authorized, _ = mandate_covers(request, self.mandate)

        return replace(
            request,
            provenance=tuple(ingested),
            user_authorized=authorized,
            reversible=semantics.reversible,
        )

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

        ingested: list[Provenance] = []
        ingested_sources: set[str] = set()

        for step_index in range(max_steps):
            step = self.provider.next_step(task, result.transcript)

            result.transcript.append({
                "role": "assistant",
                "content": step.text,
            })

            if not step.tool_name or not step.tool_action:
                break

            request = self._stamp(
                ActionRequest(
                    actor=self.principal,
                    task_id=f"agent-step-{step_index + 1}",
                    tool=step.tool_name,
                    action=step.tool_action,
                    arguments=step.tool_arguments or {},
                ),
                ingested,
            )

            blocked = False

            if self.authorizer is not None:
                allowed, reason = self.authorizer.authorize(request)

                result.transcript.append({
                    "role": "authorization",
                    "capability": request.capability,
                    "allowed": allowed,
                    "reason": reason,
                })

                if not allowed:
                    blocked = True

            if not blocked and self.flow_guard is not None:
                allowed, reason = self.flow_guard.authorize(request)

                result.transcript.append({
                    "role": "information_flow",
                    "capability": request.capability,
                    "allowed": allowed,
                    "reason": reason,
                })

                if not allowed:
                    blocked = True

            if not blocked and self.control_plane is not None:
                decision = self.control_plane.evaluate(request)

                result.transcript.append({
                    "role": "control_plane",
                    "capability": request.capability,
                    "decision": decision.decision.value,
                    "risk": decision.risk.value,
                    "reasons": decision.reasons,
                    "review": (
                        {
                            "approved": decision.review.approved,
                            "reviewer": decision.review.reviewer,
                            "note": decision.review.note,
                        }
                        if decision.review
                        else None
                    ),
                })

                if decision.review is not None:
                    result.review_count += 1
                    result.escalated_actions.append(request.capability)

                    if decision.review.approved:
                        result.approved_reviews += 1

                if not decision.permits_execution:
                    blocked = True

            if blocked:
                result.blocked_actions.append(request.capability)

                if self.stop_on_block:
                    break

                continue

            environment = self.environments.get(request.tool)

            if environment is None:
                result.transcript.append({
                    "role": "harness",
                    "error": f"no environment registered for tool {request.tool}",
                })
                break

            tool_result = environment.execute(request)

            if self.flow_guard is not None:
                self.flow_guard.observe(request, tool_result)

            if request.tool not in ingested_sources:
                ingested_sources.add(request.tool)
                ingested.append(
                    Provenance(
                        source=request.tool,
                        trusted=environment.trusted_output,
                        notes=(
                            f"output of {request.capability} ingested at step "
                            f"{step_index + 1}"
                        ),
                    )
                )

            result.executed_actions.append(request.capability)
            result.executed_requests.append(request)

            result.transcript.append({
                "role": "tool",
                "tool": request.tool,
                "action": request.action,
                "result": tool_result,
            })

        return result
