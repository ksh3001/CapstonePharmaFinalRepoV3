from __future__ import annotations

import unittest

from nondeterminism_gate import scan_source, scan_tree
from packages.config.paths import repo_root


class NondeterminismGateTests(unittest.TestCase):
    def test_packages_tree_is_clean(self) -> None:
        self.assertEqual(scan_tree(repo_root() / "packages"), [])

    def test_uuid4_fails(self) -> None:
        source = "from uuid import uuid4\nvalue = uuid4()\n"
        errors = scan_source(source, filename="packages/domain/ids.py")
        self.assertTrue(any("uuid4" in item for item in errors), errors)
