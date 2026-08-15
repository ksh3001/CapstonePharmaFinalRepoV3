"""Invariants that hold across every contract (api_contracts.md §3)."""

from __future__ import annotations

import re
from typing import Any

from packages.contracts.deny import assert_clean

HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class InvariantError(ValueError):
    """A cross-contract invariant failed."""


def assert_invariants(pack: dict[str, Any]) -> None:
    if pack.get("execution_status") != "not_executed":
        raise InvariantError("execution_status must be not_executed")
    if "no_side_effects" in pack and pack.get("no_side_effects") is not True:
        raise InvariantError("no_side_effects must be true where present")
    evidence = pack.get("evidence") or []
    if not isinstance(evidence, list):
        raise InvariantError("evidence must be an array")
    for index, item in enumerate(evidence):
        integrity = (item or {}).get("integrity") or {}
        digest = integrity.get("sha256") or ""
        if HASH_PATTERN.search(str(digest)) is None:
            raise InvariantError(f"evidence[{index}] missing well-formed sha256")
        if integrity.get("source_preserved") is not True:
            raise InvariantError(f"evidence[{index}] source_preserved must be true")
    assert_clean(pack)
