from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from .models import ActionRequest


class SemanticCapability(str, Enum):
    READ_RESOURCE = "read_resource"
    EXTERNAL_COMMUNICATION = "external_communication"
    OTHER = "other"


@dataclass(frozen=True)
class ActionSemantics:
    capability: SemanticCapability
    resource: str | None = None
    destination: str | None = None


def classify_action(
    request: ActionRequest,
) -> ActionSemantics:
    """
    Map tool-specific actions onto security-relevant semantic effects.

    Security policy should reason over these effects rather than relying
    exclusively on tool names.
    """

    if (
        request.tool == "filesystem"
        and request.action == "read"
    ):
        return ActionSemantics(
            capability=SemanticCapability.READ_RESOURCE,
            resource=str(
                request.arguments.get("path", "")
            ),
        )

    if (
        request.tool == "email"
        and request.action == "send_external"
    ):
        return ActionSemantics(
            capability=(
                SemanticCapability.EXTERNAL_COMMUNICATION
            ),
            destination=str(
                request.arguments.get("to", "")
            ).lower(),
        )

    if (
        request.tool == "browser"
        and request.action in {"submit_form", "submit_artifact"}
    ):
        url = str(
            request.arguments.get("url", "")
        )

        parsed = urlparse(url)

        destination = (
            parsed.hostname
            or url
        ).lower()

        return ActionSemantics(
            capability=(
                SemanticCapability.EXTERNAL_COMMUNICATION
            ),
            destination=destination,
        )

    return ActionSemantics(
        capability=SemanticCapability.OTHER,
    )
