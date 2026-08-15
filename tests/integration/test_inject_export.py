from __future__ import annotations

import json
import unittest
from argparse import Namespace

from aegis.cli import cmd_evidence_export
from packages.config.paths import repo_root
from packages.kernel.checkpoint import reset_replay


class InjectExportTests(unittest.TestCase):
    def test_evidence_export_lists_injects_and_commands(self) -> None:
        reset_replay()
        self.assertEqual(cmd_evidence_export(Namespace()), 0)
        payload = json.loads((repo_root() / "out" / "evidence-export.json").read_text(encoding="utf-8"))
        self.assertIn("injects", payload)
        self.assertGreaterEqual(len(payload["injects"]), 1)
        self.assertIn("evidence", payload["commands"])
        self.assertIn("verify-evidence", payload["commands"])
        self.assertIn("index", payload)
