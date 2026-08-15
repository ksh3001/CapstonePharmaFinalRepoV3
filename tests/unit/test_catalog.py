from __future__ import annotations

import csv
import unittest

from packages.config.catalog import board_entities, find_in_text, fixture_for, picker_entities, product_for, search_href
from packages.config.paths import synthetic_dir


class CatalogTests(unittest.TestCase):
    def test_picker_covers_synthetic_batch_ids(self) -> None:
        path = synthetic_dir() / "data" / "batches.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        picker = {item.entity_id for item in picker_entities("batch")}
        for row in rows:
            self.assertIn(row["batch_id"], picker)

    def test_fixture_maps_and_search(self) -> None:
        self.assertEqual(fixture_for("batch", "NCS310-S26033"), "PUB-02.json")
        self.assertEqual(fixture_for("pv", "SM-77"), "PUB-05.json")
        self.assertEqual(fixture_for("supply", "NCB-204-shortage"), "PUB-07.json")
        self.assertEqual(search_href("PV-1009"), "/workflows/pv/PV-1009")
        self.assertEqual(search_href("SH-902"), "/workflows/supply/SH-902")
        self.assertEqual(search_href("NCB-204"), "/workflows/pv/NCB-204")
        ids = {item.entity_id for item in board_entities()}
        self.assertIn("NCB204-B24071", ids)
        self.assertIn("NCS310-S26033", ids)
        self.assertIn("SM-77", ids)
        self.assertIn("SH-901", ids)

    def test_find_in_text_picks_longest_catalog_id(self) -> None:
        hit = find_in_text("What is the status of NCB204-B24071?")
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit.entity_id, "NCB204-B24071")
        self.assertEqual(hit.workflow, "batch")
        longer = find_in_text("Compare NCB-204 and NCB204-B24071")
        self.assertIsNotNone(longer)
        assert longer is not None
        self.assertEqual(longer.entity_id, "NCB204-B24071")
        self.assertIsNone(find_in_text("no catalog id here"))

    def test_product_for_each_selectable_id(self) -> None:
        self.assertEqual(product_for("batch", "NCB204-B24071"), "NCB-204")
        self.assertEqual(product_for("batch", "NCS310-S26033"), "NCS-310")
        self.assertEqual(product_for("pv", "PV-1001"), "NCB-204")
        self.assertEqual(product_for("supply", "SH-901"), "NCB-204")
        self.assertEqual(product_for("supply", "SH-902"), "NCS-310")
        self.assertEqual(product_for("supply", "NCB-204-shortage"), "NCB-204")
