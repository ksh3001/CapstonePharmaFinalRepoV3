from __future__ import annotations

import json
import unittest

from packages.kernel.packs import batch_pack
from tests.helpers import fixture_with


class PatRecipeDesyncTests(unittest.TestCase):
    def test_both_versions_are_retained_and_neither_is_preferred(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/batches.csv",
                    "records": [
                        {
                            "batch_id": "NCB204-B24071",
                            "product_id": "NCB-204",
                            "site": "CMO-IE",
                            "status": "quality_hold",
                            "manufacture_date": "2026-07-10",
                        }
                    ],
                },
                {
                    "source": "data/pat_models.csv",
                    "records": [
                        {
                            "model_id": "PAT-NIR-7",
                            "version": "2.4",
                            "approved_version": "2.3",
                            "deployed_time": "2026-07-09",
                            "change_control": "missing",
                        }
                    ],
                },
                {
                    "source": "data/recipes.csv",
                    "records": [
                        {
                            "recipe_id": "NCB-UP-19",
                            "pat_model_version": "2.3",
                            "effective_date": "2026-06-01",
                        }
                    ],
                },
            ],
            scenario_id="SYN-PAT",
        )
        pack = batch_pack(fixture, batch_id="NCB204-B24071")
        desync = [item for item in pack["contradictions"] if item.get("topic") == "pat_recipe_version"]
        self.assertTrue(desync, pack["contradictions"])
        values = {str(value) for value in desync[0].get("values") or []}
        self.assertEqual(values, {"2.4", "2.3"})
        sources = {
            (desync[0].get("left") or {}).get("source"),
            (desync[0].get("right") or {}).get("source"),
        }
        self.assertEqual(sources, {"data/pat_models.csv", "data/recipes.csv"})
        rendered = json.dumps(pack).lower()
        self.assertNotIn("confirming the batch", rendered)
        self.assertNotIn("correct version", rendered)
        self.assertNotIn("preferred version", rendered)
