"""In-process cache that refuses authorisation, consent, residency and hold keys (AP-9)."""

from __future__ import annotations

from typing import Any

PROTECTED_NAMESPACES = (
    "authz",
    "authorization",
    "entitlement",
    "consent",
    "residency",
    "hold",
    "legal_hold",
    "dsr",
    "kill_switch",
    "runtime_mode",
    "personal",
    "checkpoint",
)


class ProtectedCacheError(ValueError):
    """A non-cacheable namespace was offered to the cache."""


def _protected(key: str) -> bool:
    folded = (key or "").strip().casefold()
    return any(token in folded for token in PROTECTED_NAMESPACES)


class Cache:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        if _protected(key):
            raise ProtectedCacheError(f"non-cacheable key refused: {key}")
        self._store[key] = value

    def get(self, key: str) -> Any:
        if _protected(key):
            raise ProtectedCacheError(f"non-cacheable key refused: {key}")
        return self._store.get(key)

    def keys(self) -> list[str]:
        return sorted(self._store)

    def clear(self) -> None:
        self._store.clear()


CACHE = Cache()
