"""Canonical JSON for the evidence store. Stdlib only; does not import kernel."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any


def dumps(obj: Any) -> bytes:
    def default(value: Any) -> Any:
        if isinstance(value, Decimal):
            return format(value, "f")
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serialisable")

    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=default)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
