from __future__ import annotations

import ast
import unittest
from pathlib import Path

from packages.config.paths import repo_root
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub

VENDOR = ("langgraph", "langchain", "openai", "azure", "httpx", "redis")


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module.split(".")[0])
    return found


class VendorRemovalTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_packages_have_no_vendor_imports_and_packs_reproduce(self) -> None:
        packages = repo_root() / "packages"
        for path in packages.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            imported = _imports(path)
            for name in VENDOR:
                self.assertNotIn(name, imported, msg=str(path))
        fixture = load_pub("PUB-10")
        reset_replay()
        first = dumps(advisory_pack(fixture))
        reset_replay()
        second = dumps(advisory_pack(fixture))
        self.assertEqual(first, second)
