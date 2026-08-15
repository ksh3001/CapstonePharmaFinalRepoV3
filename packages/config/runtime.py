"""Runtime mode and kill-switch. Default graded mode is assessment."""

from __future__ import annotations

import os

MODES = ("assessment", "ai_disabled", "advisory", "ui", "cloud")
DEFAULT_MODE = "assessment"


def runtime_mode() -> str:
    raw = os.environ.get("AEGIS_RUNTIME_MODE", DEFAULT_MODE).strip() or DEFAULT_MODE
    if raw not in MODES:
        raise ValueError(f"Unknown AEGIS_RUNTIME_MODE={raw!r}; expected one of {MODES}")
    return raw


def llm_enabled() -> bool:
    raw = os.environ.get("AEGIS_LLM_ENABLED", "false").strip().lower()
    if raw in {"0", "false", "no", "off", ""}:
        return False
    if raw in {"1", "true", "yes", "on"}:
        return False if runtime_mode() in {"assessment", "ai_disabled"} else True
    return False


def inference_allowed() -> bool:
    if not llm_enabled():
        return False
    return runtime_mode() in {"advisory", "cloud"}
