from __future__ import annotations

from .models import ActionRequest


def untrusted_sources(request: ActionRequest) -> list[str]:
    return [p.source for p in request.provenance if not p.trusted]


def has_untrusted_provenance(request: ActionRequest) -> bool:
    return bool(untrusted_sources(request))
