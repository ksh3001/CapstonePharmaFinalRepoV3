"""Fail if packages/ references uuid4, random, time.time, or datetime.now."""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES = _REPO_ROOT / "packages"


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def scan_source(source: str, filename: str = "<memory>") -> list[str]:
    tree = ast.parse(source, filename=filename)
    errors: list[str] = []
    imported_random = False
    imported_uuid4 = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "random" or alias.name.startswith("random."):
                    imported_random = True
                    errors.append(f"{filename}:{node.lineno} imports random")
                if alias.name == "uuid":
                    pass
        elif isinstance(node, ast.ImportFrom):
            if node.module == "random":
                imported_random = True
                errors.append(f"{filename}:{node.lineno} imports from random")
            if node.module == "uuid" and any(alias.name == "uuid4" for alias in node.names):
                imported_uuid4 = True
                errors.append(f"{filename}:{node.lineno} imports uuid4")
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in {"uuid4", "uuid.uuid4"} or name.endswith(".uuid4"):
                errors.append(f"{filename}:{node.lineno} calls {name}")
            if name in {"time.time"} or name.endswith(".time") and "time.time" in name:
                if name == "time.time":
                    errors.append(f"{filename}:{node.lineno} calls time.time")
            if name in {"datetime.now", "datetime.datetime.now"} or name.endswith(".now"):
                if "datetime" in name and name.endswith(".now"):
                    errors.append(f"{filename}:{node.lineno} calls {name}")
            if imported_random and name.startswith("random"):
                errors.append(f"{filename}:{node.lineno} calls {name}")
            if imported_uuid4 and name == "uuid4":
                errors.append(f"{filename}:{node.lineno} calls uuid4")
    return errors


def scan_tree(root: Path | None = None) -> list[str]:
    target = root if root is not None else PACKAGES
    errors: list[str] = []
    for path in sorted(target.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        errors.extend(scan_source(path.read_text(encoding="utf-8"), filename=path.as_posix()))
    return errors


def assert_deterministic(root: Path | None = None) -> None:
    errors = scan_tree(root)
    if errors:
        raise SystemExit("nondeterminism gate failed:\n" + "\n".join(errors))
