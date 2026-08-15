"""Repository and challenge-package path resolution."""

from __future__ import annotations

import os
from pathlib import Path

_PACKAGES_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = _PACKAGES_DIR.parent


def repo_root() -> Path:
    return REPO_ROOT


def challenge_root() -> Path:
    env = os.environ.get("AEGIS_CHALLENGE_ROOT", "").strip()
    if env:
        path = Path(env)
        if path.is_dir():
            return path
        raise FileNotFoundError(f"AEGIS_CHALLENGE_ROOT is not a directory: {path}")
    sibling = repo_root().parent / "fde-training-team3-pharma-project"
    if sibling.is_dir():
        return sibling
    raise FileNotFoundError(
        "Challenge package not found. Set AEGIS_CHALLENGE_ROOT to the FDE package root."
    )


def data_dir() -> Path:
    return repo_root() / "data"


def specs_dir() -> Path:
    return repo_root() / "specs"


def synthetic_dir() -> Path:
    return repo_root() / "tests" / "fixtures" / "synthetic"
