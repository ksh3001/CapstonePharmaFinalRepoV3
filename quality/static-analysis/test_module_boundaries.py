from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from module_boundaries import evaluate, evaluate_source


class ModuleBoundaryTests(unittest.TestCase):
    def test_legal_intra_core_import_passes(self) -> None:
        source = "from packages.ontology import units\n"
        errors = evaluate_source(source, filename="packages/domain/engine.py", module="packages.domain.engine")
        self.assertEqual(errors, [])

    def test_upward_import_fails_naming_tiers(self) -> None:
        source = "from packages.domain import types\n"
        errors = evaluate_source(
            source,
            filename="packages/ontology/units.py",
            module="packages.ontology.units",
        )
        self.assertTrue(errors)
        self.assertTrue(any("ontology" in item and "domain" in item for item in errors), errors)
        self.assertTrue(any("tier" in item for item in errors), errors)

    def test_cycle_is_printed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ontology").mkdir()
            (root / "domain").mkdir()
            (root / "ontology" / "__init__.py").write_text("from packages.domain import types\n", encoding="utf-8")
            (root / "domain" / "__init__.py").write_text("from packages.ontology import units\n", encoding="utf-8")
            report = evaluate(root)
        self.assertTrue(any("cycle" in item for item in report.errors), report.errors)

    def test_contradiction_outside_domain_fails_mr5(self) -> None:
        source = "Contradiction('topic', 'src', 'rid')\n"
        errors = evaluate_source(source, filename="packages/kernel/bad.py", module="packages.kernel.bad")
        self.assertTrue(any("Contradiction" in item and "MR-5" in item for item in errors), errors)

    def test_audit_write_outside_kernel_fails_mr6(self) -> None:
        source = "write_audit({'event': 'x'})\n"
        errors = evaluate_source(source, filename="packages/domain/bad.py", module="packages.domain.bad")
        self.assertTrue(any("write_audit" in item and "MR-6" in item for item in errors), errors)

    def test_test_support_from_non_test_fails(self) -> None:
        source = "from packages.test_support import loaders\n"
        errors = evaluate_source(source, filename="packages/kernel/bad.py", module="packages.kernel.bad")
        self.assertTrue(any("test-support" in item for item in errors), errors)

    def test_live_packages_tree_passes(self) -> None:
        from packages.config.paths import repo_root

        report = evaluate(repo_root() / "packages")
        self.assertEqual(report.errors, [], msg="\n".join(report.errors))
