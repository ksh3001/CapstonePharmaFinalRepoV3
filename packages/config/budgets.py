"""Per-request budget ceilings. Changing these values requires an ADR (FR-006, NFR-07)."""

from __future__ import annotations

MAX_TOKENS_PER_REQUEST = 50000
MAX_STEPS_PER_REQUEST = 9
MAX_TOOL_CALLS_PER_REQUEST = 8
MAX_RETRIES = 1
MAX_ELAPSED_MS = 300000
MAX_COST_UNITS = 0
REQUIRED_BUDGET_KEYS = (
    "max_steps",
    "max_elapsed_ms",
    "max_input_tokens",
    "max_output_tokens",
    "max_tool_calls",
    "max_cost",
)
CONFIG_STATUS = "FR-006 / NFR-07 defaults; not a validated GxP limit"


def default_budgets() -> dict[str, int]:
    return {
        "max_steps": MAX_STEPS_PER_REQUEST,
        "max_elapsed_ms": MAX_ELAPSED_MS,
        "max_input_tokens": MAX_TOKENS_PER_REQUEST,
        "max_output_tokens": MAX_TOKENS_PER_REQUEST,
        "max_tool_calls": MAX_TOOL_CALLS_PER_REQUEST,
        "max_cost": MAX_COST_UNITS,
        "max_retries": MAX_RETRIES,
    }
