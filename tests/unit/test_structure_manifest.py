from __future__ import annotations

import unittest
from pathlib import Path

from packages.config.paths import repo_root
from scripts.generate_structure_manifest import build_manifest, write_manifest


class StructureManifestTests(unittest.TestCase):
    def test_regeneration_is_stable(self) -> None:
        root = repo_root()
        first = write_manifest(root)
        first_bytes = first.read_bytes()
        second_payload = build_manifest(root)
        from packages.kernel.canonical import dumps

        self.assertEqual(first_bytes, dumps(second_payload))
        write_manifest(root)
        self.assertEqual(first_bytes, first.read_bytes())
        self.assertNotIn("STRUCTURE_MANIFEST.json", str(second_payload["entries"]))
        self.assertNotIn("file:.env", second_payload["entries"])
        self.assertIn("file:docs/product/business-case.md", second_payload["entries"])
