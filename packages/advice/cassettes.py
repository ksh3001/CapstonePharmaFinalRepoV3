"""Cassette record-and-replay keyed by prompt hash, deployment and model version."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from packages.config.paths import repo_root


def _dumps(obj: Any) -> bytes:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def cassette_dir() -> Path:
    return repo_root() / "evals" / "cassettes"


def cassette_key(prompt: str, deployment: str, model_version: str) -> str:
    material = _dumps({"prompt": prompt, "deployment": deployment, "model_version": model_version})
    return hashlib.sha256(material).hexdigest()


def load_cassette(key: str) -> dict[str, Any] | None:
    path = cassette_dir() / f"{key}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_cassette(key: str, payload: dict[str, Any]) -> Path:
    folder = cassette_dir()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{key}.json"
    path.write_bytes(_dumps(payload))
    return path
