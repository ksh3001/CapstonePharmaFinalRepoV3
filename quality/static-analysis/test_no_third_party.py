from __future__ import annotations

import unittest

from stdlib_gate import scan_source, scan_tree
from packages.config.paths import repo_root


class StdlibGateTests(unittest.TestCase):
    def test_packages_tree_is_clean(self) -> None:
        errors = scan_tree(repo_root() / "packages")
        self.assertEqual(errors, [])

    def test_requests_import_fails_and_names_file(self) -> None:
        source = "import requests\n"
        errors = scan_source(source, filename="packages/domain/violator.py")
        self.assertTrue(errors)
        self.assertIn("packages/domain/violator.py", errors[0])
        self.assertIn("requests", errors[0])

    def test_intra_core_import_passes(self) -> None:
        source = "from packages.ontology import units\n"
        errors = scan_source(source, filename="packages/domain/__init__.py")
        self.assertEqual(errors, [])

    def test_fastapi_is_named_in_message(self) -> None:
        source = "import fastapi\n"
        errors = scan_source(source, filename="packages/kernel/bad.py")
        self.assertTrue(any("fastapi" in item for item in errors))
