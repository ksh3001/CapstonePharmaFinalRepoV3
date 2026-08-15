from __future__ import annotations

import unittest

from packages.config.paths import synthetic_dir
from scripts.build_fixture_copyset import build, collect_sources, destination_for, load_hashes
from packages.config.paths import challenge_root


class CopysetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = build()

    def test_every_referenced_file_is_in_the_manifest(self) -> None:
        challenge = challenge_root()
        expected = set(collect_sources(challenge))
        listed = {item["source_path"] for item in self.manifest["files"]}
        self.assertEqual(expected, listed)

    def test_hashes_match_file_hashes_csv(self) -> None:
        hashes = load_hashes(challenge_root())
        for item in self.manifest["files"]:
            self.assertEqual(item["sha256"], hashes[item["source_path"]], item["source_path"])
            dest = destination_for(item["source_path"])
            self.assertTrue(dest.is_file(), dest)

    def test_provenance_is_stable(self) -> None:
        first = (synthetic_dir() / "PROVENANCE.csv").read_bytes()
        build(as_of="2026-08-01T08:00:00Z")
        second = (synthetic_dir() / "PROVENANCE.csv").read_bytes()
        self.assertEqual(first, second)
        self.assertIn(b"2026-08-01T08:00:00Z", first)

    def test_deleting_a_manifest_entry_is_detectable(self) -> None:
        from packages.kernel.canonical import dumps
        import json

        committed = json.loads((synthetic_dir() / "COPYSET_MANIFEST.json").read_text(encoding="utf-8"))
        reduced = dict(committed)
        reduced["files"] = committed["files"][1:]
        self.assertNotEqual(dumps(reduced), dumps(committed))
