"""Role spelling → canonical role_id. Unmapped spelling is unresolved (BR-039)."""

from __future__ import annotations

import json
from pathlib import Path

_PATH = Path(__file__).with_name("roles.yaml")


def _payload() -> dict[str, object]:
    return json.loads(_PATH.read_text(encoding="utf-8"))


def _spellings() -> dict[str, str]:
    payload = _payload()
    return dict(payload.get("spellings") or {})


def canonical_role(spelling: str) -> str | None:
    text = (spelling or "").strip()
    if not text:
        return None
    return _spellings().get(text)


def role_label(role_id: str | None) -> str:
    if not role_id:
        return "unresolved role"
    payload = _payload()
    labels = dict(payload.get("labels") or {})
    return str(labels.get(role_id) or role_id)
