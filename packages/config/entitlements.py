"""Role → access-group matrix (AMB-15). Loaded live per call; never cached."""

from __future__ import annotations

import json
from pathlib import Path

_PATH = Path(__file__).with_name("entitlements.yaml")


def _matrix() -> dict[str, tuple[str, ...]]:
    payload = json.loads(_PATH.read_text(encoding="utf-8"))
    return {str(key): tuple(value) for key, value in payload.items()}


def entitled_groups(role_id: str | None) -> frozenset[str]:
    if not role_id:
        return frozenset()
    return frozenset(group for group, roles in _matrix().items() if role_id in roles)


def role_entitled(role_id: str | None, access_group: str) -> bool:
    matrix = _matrix()
    if access_group not in matrix:
        return False
    return bool(role_id) and role_id in matrix[access_group]
