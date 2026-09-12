from __future__ import annotations

import base64

from .base import Environment
from ..data_lineage import ArtifactStore
from ..models import ActionRequest


class TransformEnvironment(Environment):
    """
    Derives a new artifact from an existing one, keeping the lineage link.

    Transformation is where literal content matching fails, which is the
    finding recorded in docs/findings/transformation_and_lineage.md.
    """

    trusted_output = False

    def __init__(self, store: ArtifactStore) -> None:
        self.store = store

    def execute(self, request: ActionRequest) -> dict:
        if request.action != "transform":
            return {"ok": False, "error": "unsupported action"}

        artifact_id = str(request.arguments.get("artifact_id", ""))
        operation = str(request.arguments.get("operation", ""))

        try:
            parent = self.store.get(artifact_id)
        except KeyError:
            return {"ok": False, "error": "unknown artifact"}

        value = str(parent.value)

        if operation == "base64":
            transformed = base64.b64encode(value.encode()).decode()
        elif operation == "reverse":
            transformed = value[::-1]
        elif operation == "chunks":
            transformed = " ".join(
                value[i:i + 5] for i in range(0, len(value), 5)
            )
        elif operation == "paraphrase":
            transformed = (
                "The file describes material that is synthetic and "
                "classified as sensitive."
            )
        else:
            return {"ok": False, "error": "unknown transformation"}

        derived = self.store.derive(parent_id=artifact_id, value=transformed)

        return {
            "ok": True,
            "artifact_id": derived.artifact_id,
            "value": derived.value,
            "labels": sorted(derived.labels),
            "parents": list(derived.parents),
        }
