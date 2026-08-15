"""Load a local .env into os.environ. Stdlib only. Never log values."""

from __future__ import annotations

import os
from pathlib import Path

from packages.config.paths import repo_root

_ALIASES = (
    ("GENERATOR_DEPLOYMENT", "AZURE_OPENAI_DEPLOYMENT"),
    ("GENERATOR_MODEL", "AZURE_OPENAI_DEPLOYMENT"),
)


def load_envfile(path: Path | None = None, *, override: bool = False) -> Path | None:
    target = path or (repo_root() / ".env")
    if not target.is_file():
        _apply_aliases(override=override)
        return None
    text = target.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value
    _apply_aliases(override=override)
    return target


def _apply_aliases(*, override: bool) -> None:
    for source, dest in _ALIASES:
        incoming = os.environ.get(source, "").strip()
        if not incoming:
            continue
        current = os.environ.get(dest, "").strip()
        if override or not current:
            os.environ[dest] = incoming
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "").strip()
    pinned = os.environ.get("AZURE_OPENAI_MODEL_VERSION", "").strip()
    if deployment and not pinned and deployment.lower() not in {"latest", "current", "alias"}:
        os.environ["AZURE_OPENAI_MODEL_VERSION"] = deployment
