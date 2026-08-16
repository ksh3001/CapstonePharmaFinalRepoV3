from __future__ import annotations

import unittest

from compliance.tripwires.evaluate import PROTECTED, change_class_drift, file_sha256
from packages.config.paths import repo_root


class ChangeClassTests(unittest.TestCase):
    def test_protected_files_match_signed_baseline(self) -> None:
        drifted = change_class_drift()
        self.assertEqual(drifted, [], drifted)

    def test_every_protected_path_exists(self) -> None:
        root = repo_root()
        for rel in PROTECTED:
            self.assertTrue((root / rel).is_file(), rel)
            self.assertEqual(len(file_sha256(rel)), 64)
