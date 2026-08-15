"""Budget admission and counters. Classification types are not constructed here (MR-5)."""

from __future__ import annotations

from typing import Any

from packages.config.budgets import REQUIRED_BUDGET_KEYS, default_budgets


def admit_budgets(declared: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a complete budget set, or None when a required ceiling is missing."""
    if declared is None:
        return default_budgets()
    missing = [key for key in REQUIRED_BUDGET_KEYS if key not in declared]
    if missing:
        return None
    payload = default_budgets()
    payload.update({key: int(declared[key]) for key in REQUIRED_BUDGET_KEYS})
    if "max_retries" in declared:
        payload["max_retries"] = int(declared["max_retries"])
    return payload


def exhausted(counters: dict[str, int], budgets: dict[str, Any]) -> str:
    if counters.get("steps", 0) > int(budgets["max_steps"]):
        return "steps"
    if counters.get("tokens", 0) > int(budgets["max_input_tokens"]):
        return "tokens"
    if counters.get("tool_calls", 0) > int(budgets["max_tool_calls"]):
        return "tool_calls"
    return ""
