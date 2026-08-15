from __future__ import annotations

import ast
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PACKAGES = HERE.parents[1] / "packages"
ALLOWED = PACKAGES / "domain" / "evidence.py"


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


class EvidenceConstructionTests(unittest.TestCase):
    def test_evidence_item_is_constructed_only_in_evidence_module(self) -> None:
        hits: list[str] = []
        for path in sorted(PACKAGES.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            if path.resolve() == ALLOWED.resolve():
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                short = _call_name(node.func).split(".")[-1]
                if short == "EvidenceItem":
                    hits.append(f"{path.as_posix()}:{node.lineno}")
        self.assertEqual(hits, [], msg="EvidenceItem constructed outside packages/domain/evidence.py:\n" + "\n".join(hits))
