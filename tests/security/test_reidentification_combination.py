from __future__ import annotations

import json
import unittest

from packages.config.privacy_thresholds import REIDENTIFICATION_K
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import CONTEXT


class ReidentificationCombinationTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_combination_is_withheld_and_fields_remain_separate(self) -> None:
        self.assertGreaterEqual(REIDENTIFICATION_K, 2)
        fixture = {
            "scenario": {"id": "REIDENT", "workflow": "privacy"},
            "authorized_context": dict(CONTEXT),
            "evidence": [
                {
                    "source": "data/genomic_data.csv",
                    "records": [
                        {
                            "participant": "G-001",
                            "disease": "ultra_rare_X",
                            "variant": "chr7:rare",
                            "country": "DE",
                            "age": "17",
                            "postal_prefix": "101",
                        },
                        {
                            "participant": "G-002",
                            "disease": "ultra_rare_X",
                            "variant": "chr7:rare2",
                            "country": "US",
                            "age": "12",
                            "postal_prefix": "021",
                        },
                    ],
                }
            ],
            "response_contract": "advisory_nonexecuting",
        }
        pack = advisory_pack(fixture)
        review = pack["human_review"]["reidentification"]
        self.assertTrue(review["combination_withheld"])
        separate = review["separate_fields"]
        names = {item.get("field") for item in separate}
        self.assertIn("disease", names)
        self.assertIn("country", names)
        statements = " ".join(item.get("statement") or "" for item in pack["findings"])
        self.assertIn("combination", statements.casefold())
        self.assertNotIn("chr7:rare", statements)
        self.assertNotIn("G-001", statements)
        rendered = json.dumps(pack)
        self.assertNotIn("G-001", rendered)
        self.assertIn("ultra_rare_X", json.dumps(separate))
        joined = 0

        def walk(obj: object) -> None:
            nonlocal joined
            if isinstance(obj, dict):
                if sum(1 for key in ("disease", "variant", "country", "age", "postal_prefix") if key in obj) >= 2:
                    joined += 1
                for value in obj.values():
                    walk(value)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(pack)
        self.assertEqual(joined, 0)
