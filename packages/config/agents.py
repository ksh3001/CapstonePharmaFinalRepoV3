"""Runtime agent roster. Capability boundaries are data, not prompt text (plan §32.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PATH = Path(__file__).with_name("agents.yaml")

AGENT_IDS = ("AG-1", "AG-2", "AG-3", "AG-4", "AG-5", "AG-6")


def load_agents() -> dict[str, dict[str, Any]]:
    payload = json.loads(_PATH.read_text(encoding="utf-8"))
    agents = dict(payload.get("agents") or {})
    return {key: dict(agents[key]) for key in AGENT_IDS if key in agents}


def agent_record(agent_id: str) -> dict[str, Any]:
    agents = load_agents()
    record = agents.get(agent_id)
    if record is None:
        raise KeyError(agent_id)
    return dict(record)


def permitted_tools(agent_id: str) -> frozenset[str]:
    return frozenset(str(item) for item in (agent_record(agent_id).get("tools") or []))


def inference_permitted(agent_id: str) -> bool:
    return bool(agent_record(agent_id).get("inference"))


def tool_allowed(agent_id: str, tool: str) -> bool:
    allowed = permitted_tools(agent_id)
    return str(tool) in allowed
