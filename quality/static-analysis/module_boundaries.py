"""Module boundary gate: layering, cycles, MR-5, MR-6, test-support isolation."""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES = _REPO_ROOT / "packages"

TIERS = {
    "contracts": 0,
    "config": 0,
    "observability": 1,
    "cache": 1,
    "finops": 1,
    "evidence_store": 1,
    "ontology": 2,
    "graph": 3,
    "domain": 4,
    "advice": 4,
    "orchestrator": 5,
    "kernel": 5,
    "test-support": 99,
    "test_support": 99,
}

CLASSIFICATION_TYPES = frozenset({"Contradiction", "Gap", "Abstention"})
AUDIT_CALLS = frozenset({"write_audit"})


def _module_name(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return "packages." + ".".join(parts) if parts else "packages"


def _top_package(module: str) -> str | None:
    if not module.startswith("packages."):
        return None
    rest = module[len("packages.") :]
    return rest.split(".")[0]


def _normalise_top(name: str) -> str:
    if name == "test_support":
        return "test-support"
    return name


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _imports(tree: ast.AST) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("packages"):
                    found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("packages"):
            found.append((node.lineno, node.module))
    return found


def _constructions(tree: ast.AST) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        short = name.split(".")[-1]
        if short in CLASSIFICATION_TYPES:
            found.append((node.lineno, short))
        if short in AUDIT_CALLS:
            found.append((node.lineno, short))
    return found


class BoundaryReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.edges: list[tuple[str, str]] = []

    @property
    def ok(self) -> bool:
        return not self.errors


def _cycle(edges: list[tuple[str, str]]) -> list[str] | None:
    graph: dict[str, set[str]] = {}
    for src, dst in edges:
        graph.setdefault(src, set()).add(dst)
        graph.setdefault(dst, set())

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def dfs(node: str) -> list[str] | None:
        visiting.add(node)
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if nxt in visiting:
                start = stack.index(nxt)
                return stack[start:] + [nxt]
            if nxt not in visited:
                found = dfs(nxt)
                if found:
                    return found
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(graph):
        if node not in visited:
            found = dfs(node)
            if found:
                return found
    return None


def evaluate_source(source: str, *, filename: str, module: str) -> list[str]:
    tree = ast.parse(source, filename=filename)
    errors: list[str] = []
    top = _normalise_top(_top_package(module) or "")
    in_domain = top == "domain"
    in_kernel = top == "kernel"
    for lineno, imported in _imports(tree):
        other_top = _normalise_top(_top_package(imported) or "")
        if other_top in {"test-support", "test_support"}:
            errors.append(f"{filename}:{lineno} imports packages/test-support from non-test module {module}")
        if top in TIERS and other_top in TIERS:
            src_tier = TIERS[top]
            dst_tier = TIERS[other_top]
            if src_tier == 0 and other_top != top:
                errors.append(
                    f"{filename}:{lineno} {top} (tier 0) imports {other_top} (tier {dst_tier}); "
                    "tier 0 may import the standard library only"
                )
            elif dst_tier > src_tier:
                errors.append(
                    f"{filename}:{lineno} upward import {top} (tier {src_tier}) -> "
                    f"{other_top} (tier {dst_tier})"
                )
            elif top == "advice" and other_top == "domain":
                errors.append(f"{filename}:{lineno} advice must not import domain logic")
    for lineno, constructed in _constructions(tree):
        if constructed in CLASSIFICATION_TYPES and not in_domain:
            errors.append(
                f"{filename}:{lineno} constructs {constructed} outside packages/domain (MR-5)"
            )
        if constructed in AUDIT_CALLS and not in_kernel:
            errors.append(
                f"{filename}:{lineno} calls {constructed} outside packages/kernel (MR-6)"
            )
    return errors


def evaluate(root: Path | None = None) -> BoundaryReport:
    target = root if root is not None else PACKAGES
    report = BoundaryReport()
    for path in sorted(target.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        module = _module_name(path, target)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        top = _normalise_top(_top_package(module) or "")
        for lineno, imported in _imports(tree):
            other = _normalise_top(_top_package(imported) or "")
            if top and other:
                report.edges.append((top, other))
        report.errors.extend(evaluate_source(source, filename=path.as_posix(), module=module))
    cycle = _cycle([(src, dst) for src, dst in report.edges if src != dst])
    if cycle:
        report.errors.append("import cycle: " + " -> ".join(cycle))
    return report


def assert_boundaries(root: Path | None = None) -> BoundaryReport:
    report = evaluate(root)
    if not report.ok:
        raise SystemExit("module boundary gate failed:\n" + "\n".join(report.errors))
    return report
