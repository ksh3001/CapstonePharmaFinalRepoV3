from __future__ import annotations

import json
import unittest

from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


FORBIDDEN = (
    "resolved",
    "invalidated",
    "laboratory error",
    "lab error",
)


class OrganismIdCorrectionTests(unittest.TestCase):
    def test_both_identifications_are_retained(self) -> None:
        pack = batch_pack(load_pub("PUB-02"), batch_id="NCS310-S26033")
        organism = [item for item in pack["contradictions"] if item.get("topic") == "organism_identification"]
        self.assertTrue(organism, pack["contradictions"])
        values = [str(value) for value in organism[0].get("values") or []]
        self.assertIn("Micrococcus spp", values)
        self.assertIn("Bacillus cereus group", values)
        identifications = organism[0].get("identifications") or []
        times = [item.get("time") for item in identifications if item.get("time")]
        self.assertTrue(times)
        rendered = json.dumps(pack).lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, rendered)
