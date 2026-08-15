"""Keys that must never influence a rule or a request identifier (BR-097)."""

from __future__ import annotations

from typing import Any

URGENCY_KEYS = frozenset(
    {
        "urgency",
        "deadline_hours",
        "inspection_surge",
        "priority",
        "deadline",
        "surge",
        "commercial_exposure",
    }
)


def rule_context(context: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in context.items() if key not in URGENCY_KEYS}
