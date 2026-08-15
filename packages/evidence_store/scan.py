"""Write-time scan: no secrets or direct identifiers in the store (BR-124)."""

from __future__ import annotations

import json
from typing import Any

SECRET_TOKENS = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "bearer ",
    "azure_openai_api_key",
)
DIRECT_ID_TOKENS = (
    "patient_id",
    "date_of_birth",
    "email",
    "patient_key",
)


class StoreScanError(ValueError):
    """A forbidden token was offered to the evidence store."""


def _walk(obj: Any) -> list[str]:
    found: list[str] = []
    if isinstance(obj, str):
        found.append(obj)
    elif isinstance(obj, dict):
        found.extend(str(key) for key in obj)
        for value in obj.values():
            found.extend(_walk(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_walk(item))
    return found


def assert_clean_payload(payload: Any) -> None:
    rendered = " ".join(_walk(payload)).casefold()
    for token in SECRET_TOKENS:
        if token in rendered:
            raise StoreScanError(f"secret token blocked at write: {token}")
    for token in DIRECT_ID_TOKENS:
        if token in rendered:
            raise StoreScanError(f"direct identifier blocked at write: {token}")


def scan_store(rows: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    blob = json.dumps(rows).casefold()
    for token in SECRET_TOKENS + DIRECT_ID_TOKENS:
        if token in blob:
            hits.append(token)
    return hits
