from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from inject_coverage_gate import CLOSED_ALLOWLIST, evaluate, load_inject_ids


class InjectCoverageGateTests(unittest.TestCase):
    def test_current_registers_cover_behavioural_injects(self) -> None:
        report = evaluate()
        self.assertEqual(report.errors, [], msg="\n".join(report.errors))
        known = set(load_inject_ids())
        behavioural = known - CLOSED_ALLOWLIST
        self.assertEqual(len(behavioural), 81)
        self.assertEqual(len(known), 84)
        for inject_id in behavioural:
            self.assertTrue(report.br_by_inject.get(inject_id), inject_id)
            self.assertTrue(report.ac_by_inject.get(inject_id), inject_id)

    def test_artefact_allowlist_files_exist(self) -> None:
        from packages.config.paths import repo_root

        allowlist = json.loads(
            (repo_root() / "quality" / "static-analysis" / "inject_coverage_allowlist.json").read_text(
                encoding="utf-8"
            )
        )
        for inject_id in CLOSED_ALLOWLIST:
            meta = allowlist["artefacts"][inject_id]
            self.assertTrue((repo_root() / meta["path"]).is_file(), meta["path"])
            self.assertTrue((repo_root() / meta["test"]).is_file(), meta["test"])

    def test_missing_artefact_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "allow.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_ids": ["001", "002", "003"],
                        "artefacts": {
                            "001": {
                                "path": "docs/product/does-not-exist.md",
                                "test": "tests/compliance/test_benefit_claims.py",
                            },
                            "002": {
                                "path": "docs/product/success-metrics.md",
                                "test": "tests/compliance/test_metric_conflicts.py",
                            },
                            "003": {
                                "path": "docs/product/no-ai-baseline.md",
                                "test": "tests/compliance/test_no_ai_baseline.py",
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            report = evaluate(allowlist_path=path)
        self.assertTrue(any("missing file" in error for error in report.errors), report.errors)

    def test_removing_sole_carrier_fails_naming_inject(self) -> None:
        from packages.config.paths import repo_root

        br_path = repo_root() / "specs" / "registers" / "business_rules_register.md"
        original = br_path.read_text(encoding="utf-8")
        report = evaluate()
        target = None
        for inject_id, carriers in report.br_by_inject.items():
            if inject_id in CLOSED_ALLOWLIST:
                continue
            if len(carriers) == 1:
                target = (inject_id, next(iter(carriers)))
                break
        self.assertIsNotNone(target)
        inject_id, br_id = target
        stripped = "\n".join(line for line in original.splitlines() if not line.startswith(f"| {br_id} "))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "br.md"
            path.write_text(stripped + "\n", encoding="utf-8")
            failed = evaluate(br_path=path)
        self.assertTrue(any(inject_id in error for error in failed.errors), failed.errors)

    def test_widened_allowlist_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "allow.json"
            path.write_text(
                json.dumps({"allowed_ids": ["001", "002", "003", "004"], "artefacts": {}}),
                encoding="utf-8",
            )
            report = evaluate(allowlist_path=path)
        self.assertTrue(any("allow-list" in error for error in report.errors), report.errors)

    def test_unknown_inject_in_register_fails(self) -> None:
        from packages.config.paths import repo_root

        br_path = repo_root() / "specs" / "registers" / "business_rules_register.md"
        text = br_path.read_text(encoding="utf-8") + "\n| BR-999 | FR-001 | ghost | n/a | AC-FR001-01 | 999 |\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "br.md"
            path.write_text(text, encoding="utf-8")
            report = evaluate(br_path=path)
        self.assertTrue(any("absent from data/injects.json" in error for error in report.errors), report.errors)
