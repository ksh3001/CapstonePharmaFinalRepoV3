from __future__ import annotations

import json
import unittest

from packages.config.matching import BAND_HIGH, BAND_MID, BAND_WEAK
from packages.domain.duplicates import MERGE_KEYS, compare_pair, find_duplicate_candidates


def _case(case_id: str, **overrides: object) -> dict:
    row = {
        "case_id": case_id,
        "patient_id": "P-7X",
        "date_of_birth": "1980-01-01",
        "sex": "F",
        "product": "NCB-204",
        "pt": "Anaphylactic reaction",
        "onset_date": "2026-07-20",
    }
    row.update(overrides)
    return row


ALIASES = {"NCB204": "NCB-204", "brand_alias_B": "NCB-204"}


class DuplicateCandidateTests(unittest.TestCase):
    def test_exact_worldwide_id_is_high_without_merge(self) -> None:
        left = _case("PV-A", worldwide_unique_id="WW-1", product="OTHER", pt="other", onset_date="2020-01-01")
        right = _case("PV-B", worldwide_unique_id="WW-1")
        row = compare_pair(left, right)
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["band"], BAND_HIGH)
        self.assertEqual(row["strategy"], "worldwide_unique_id")
        self.assertEqual(row["score"], 6)
        self.assertEqual(set(row) & MERGE_KEYS, set())

    def test_score_six_composite_is_high(self) -> None:
        row = compare_pair(_case("A"), _case("B"))
        assert row is not None
        self.assertEqual(row["band"], BAND_HIGH)
        self.assertEqual(row["score"], 6)
        self.assertEqual(row["matched_fields"], [
            "patient_id",
            "dob_or_age",
            "sex",
            "product",
            "reaction",
            "onset",
        ])
        self.assertEqual(row["mismatched_fields"], [])

    def test_score_four_is_duplicate_candidate(self) -> None:
        right = _case("B", sex="M", pt="Headache")
        row = compare_pair(_case("A"), right)
        assert row is not None
        self.assertEqual(row["score"], 4)
        self.assertEqual(row["band"], BAND_MID)
        self.assertIn("sex", row["mismatched_fields"])
        self.assertIn("reaction", row["mismatched_fields"])

    def test_score_three_is_weak_and_lists_matched_fields(self) -> None:
        right = _case("B", sex="M", pt="Headache", date_of_birth="1990-01-01")
        row = compare_pair(_case("A"), right)
        assert row is not None
        self.assertEqual(row["score"], 3)
        self.assertEqual(row["band"], BAND_WEAK)
        self.assertEqual(set(row["matched_fields"]), {"patient_id", "product", "onset"})

    def test_score_two_is_not_surfaced(self) -> None:
        right = _case(
            "B",
            sex="M",
            pt="Headache",
            date_of_birth="1990-01-01",
            onset_date="2026-08-20",
        )
        self.assertIsNone(compare_pair(_case("A"), right))

    def test_boundaries_at_three_and_four(self) -> None:
        weak = compare_pair(_case("A"), _case("B", sex="M", pt="Headache", date_of_birth="1990-01-01"))
        mid = compare_pair(_case("A"), _case("B", sex="M", pt="Headache"))
        assert weak is not None and mid is not None
        self.assertEqual(weak["score"], 3)
        self.assertEqual(weak["band"], BAND_WEAK)
        self.assertEqual(mid["score"], 4)
        self.assertEqual(mid["band"], BAND_MID)

    def test_onset_window_is_inclusive_seven_days(self) -> None:
        inside = compare_pair(_case("A"), _case("B", onset_date="2026-07-27"))
        outside = compare_pair(_case("A"), _case("B", onset_date="2026-07-28"))
        assert inside is not None
        self.assertIn("onset", inside["matched_fields"])
        # 8 days: onset mismatches; other five still match → still surfaced as mid
        assert outside is not None
        self.assertIn("onset", outside["mismatched_fields"])
        self.assertEqual(outside["score"], 5)

    def test_empty_and_unknown_do_not_match(self) -> None:
        self.assertIsNone(
            compare_pair(
                _case("A", patient_id="unknown", date_of_birth="", sex="", product="", pt="", onset_date=""),
                _case("B", patient_id="unknown", date_of_birth="", sex="", product="", pt="", onset_date=""),
            )
        )

    def test_product_alias_is_not_fuzzy_match(self) -> None:
        with_alias = compare_pair(_case("A"), _case("B", product="NCB204"), product_aliases=ALIASES)
        without = compare_pair(_case("A"), _case("B", product="NCB204"))
        assert with_alias is not None and without is not None
        self.assertIn("product", with_alias["matched_fields"])
        self.assertIn("product", without["mismatched_fields"])

    def test_pairs_are_not_transitively_clustered(self) -> None:
        cases = [
            _case("A"),
            _case("B"),
            _case("C", patient_id="P-OTHER", date_of_birth="1970-01-01", sex="M", product="OTHER", pt="Cough"),
        ]
        # A-B score 6; B-C and A-C score 1 (onset only) → only A-B
        rows = find_duplicate_candidates(cases)
        self.assertEqual([(item["case_a"], item["case_b"]) for item in rows], [("A", "B")])
        rendered = json.dumps(rows)
        for key in MERGE_KEYS:
            self.assertNotIn(f'"{key}"', rendered)

    def test_source_similarity_is_not_the_score(self) -> None:
        left = _case("PV-1001")
        right = _case("PV-1014", sex="M", pt="Headache", date_of_birth="1990-01-01")
        row = compare_pair(left, right)
        assert row is not None
        self.assertEqual(row["score"], 3)
        self.assertNotEqual(row["score"], 0.93)
        self.assertIsInstance(row["score"], int)
        self.assertEqual(row["config_status"], "AMB-05a")
