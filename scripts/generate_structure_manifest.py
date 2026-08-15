"""Generate STRUCTURE_MANIFEST.json from the repository tree. Never hand-edit the manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from packages.kernel.canonical import dumps  # noqa: E402

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "out"}
SKIP_FILES = {".DS_Store", "Thumbs.db", ".env"}
MANIFEST_NAME = "STRUCTURE_MANIFEST.json"


def iter_entries(root: Path) -> list[str]:
    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.name == MANIFEST_NAME:
            continue
        rel = path.relative_to(root).as_posix()
        kind = "dir" if path.is_dir() else "file"
        entries.append(f"{kind}:{rel}")
    return entries


def build_manifest(root: Path | None = None) -> dict:
    target = root if root is not None else _REPO_ROOT
    return {"entries": iter_entries(target)}


def write_manifest(root: Path | None = None) -> Path:
    target = root if root is not None else _REPO_ROOT
    payload = build_manifest(target)
    path = target / MANIFEST_NAME
    path.write_bytes(dumps(payload))
    return path


def main() -> int:
    write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
