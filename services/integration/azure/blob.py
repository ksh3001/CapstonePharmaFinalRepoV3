"""Azure Blob WORM adapter. Assessment uses a local immutability envelope."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.config.paths import repo_root
from packages.kernel.canonical import dumps


class ImmutableBlobError(PermissionError):
    """Overwrite of a WORM object is rejected."""


def worm_root() -> Path:
    return repo_root() / "out" / "worm"


def put_immutable(name: str, payload: dict[str, Any]) -> Path:
    folder = worm_root()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    if path.exists():
        raise ImmutableBlobError(f"WORM overwrite rejected: {name}")
    path.write_bytes(dumps(payload))
    (folder / f"{name}.policy").write_text("immutability=time-based\n", encoding="utf-8")
    return path
