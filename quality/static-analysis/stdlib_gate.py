"""Stdlib-only import gate for packages/ (MR-4). Intra-core imports are allowed."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

THIRD_PARTY_DENYLIST = (
    "langgraph",
    "langchain",
    "redis",
    "mcp",
    "fastapi",
    "jinja2",
    "httpx",
    "requests",
    "networkx",
    "rdflib",
    "openai",
    "azure",
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES = _REPO_ROOT / "packages"


def _stdlib_names() -> set[str]:
    names = set(getattr(sys, "stdlib_module_names", ()))
    names.update({"__future__", "typing", "annotations"})
    return names


def _top_level(module: str) -> str:
    return module.split(".")[0]


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _imported_modules(tree: ast.AST) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and not node.module:
                continue
            if node.level:
                continue
            if node.module:
                found.append((node.lineno, node.module))
    return found


def scan_source(source: str, filename: str = "<memory>") -> list[str]:
    tree = ast.parse(source, filename=filename)
    stdlib = _stdlib_names()
    errors: list[str] = []
    for lineno, module in _imported_modules(tree):
        top = _top_level(module)
        if top == "packages" or module.startswith("packages."):
            continue
        if top in stdlib:
            continue
        named = ""
        for banned in THIRD_PARTY_DENYLIST:
            if top == banned or top.startswith(banned):
                named = f" (denied third-party dependency {banned})"
                break
        errors.append(f"{filename}:{lineno} imports {module}{named}")
    return errors


def scan_tree(root: Path | None = None) -> list[str]:
    target = root if root is not None else PACKAGES
    errors: list[str] = []
    for path in _iter_py_files(target):
        text = path.read_text(encoding="utf-8")
        rel = path.as_posix()
        errors.extend(scan_source(text, filename=rel))
    return errors


def assert_stdlib_only(root: Path | None = None) -> None:
    errors = scan_tree(root)
    if errors:
        raise SystemExit("stdlib import gate failed:\n" + "\n".join(errors))
