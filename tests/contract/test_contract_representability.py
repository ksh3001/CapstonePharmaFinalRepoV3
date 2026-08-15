from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from packages.contracts.representability import assert_representable, representability_errors


class RepresentabilityTests(unittest.TestCase):
    def test_current_features_are_representable(self) -> None:
        errors = representability_errors()
        self.assertEqual(errors, [], msg="\n".join(errors))
        assert_representable()

    def test_unlisted_workflow_fails_naming_feature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "FR-099_new.md"
            path.write_text(
                "| Contract | `advisory_nonexecuting.schema.json`, `workflow: \"weather\"` |\n",
                encoding="utf-8",
            )
            errors = representability_errors(Path(tmp))
        self.assertTrue(errors)
        self.assertTrue(any("FR-099" in item and "weather" in item for item in errors), errors)
