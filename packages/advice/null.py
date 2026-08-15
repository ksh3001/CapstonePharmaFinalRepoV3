"""Default inference port. Assessment never leaves this adapter."""

from __future__ import annotations

from typing import Any


class NullInference:
    def generate(self, pack: dict[str, Any]) -> dict[str, Any]:
        del pack
        return {"called": False, "reason": "null", "annotations": None, "outbound": 0}
