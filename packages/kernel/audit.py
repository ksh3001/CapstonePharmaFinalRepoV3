"""Audit trail writer. Callable only from packages.kernel (MR-6)."""

from __future__ import annotations

from typing import Any

_EVENTS: list[dict[str, Any]] = []


def write_audit(event: dict[str, Any]) -> dict[str, Any]:
    """Append a deterministic audit event. Do not call this outside packages.kernel."""
    record = dict(event)
    _EVENTS.append(record)
    return record


def reset_audit() -> None:
    _EVENTS.clear()


def audit_events() -> list[dict[str, Any]]:
    return list(_EVENTS)
