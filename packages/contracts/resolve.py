"""Resolve a fixture's response_contract. Unknown values are errors, never a default."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.contracts.validator import SchemaError, load_schema

_REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_contract(response_contract: str) -> dict[str, Any]:
    value = (response_contract or "").strip()
    if not value:
        raise SchemaError("response_contract is missing")
    if value in {"advisory_nonexecuting", "advisory_nonexecuting.schema.json"}:
        return load_schema("advisory_nonexecuting")
    if value.endswith(".schema.json"):
        return load_schema(Path(value).name)
    raise SchemaError(f"unknown response_contract {value!r}")


def contract_path(response_contract: str) -> Path:
    value = (response_contract or "").strip()
    root = _REPO_ROOT / "packages" / "contracts"
    if value in {"advisory_nonexecuting", "advisory_nonexecuting.schema.json"}:
        return root / "internal" / "advisory_nonexecuting.schema.json"
    if value.endswith(".schema.json"):
        return root / "regulated" / Path(value).name
    raise SchemaError(f"unknown response_contract {value!r}")
