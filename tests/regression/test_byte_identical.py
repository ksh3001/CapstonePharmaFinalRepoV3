from __future__ import annotations

import unittest

from packages.kernel.canonical import dumps, sort_abstentions, sort_contradictions, sort_evidence, sort_gaps
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from tests.helpers import load_pub


class ByteIdenticalTests(unittest.TestCase):
    def test_three_consecutive_dumps_match(self) -> None:
        pack = {
            "evidence": sort_evidence(
                [
                    {"source": "data/lab_results.csv", "record_id": "LR-89"},
                    {"source": "data/batches.csv", "record_id": "NCB204-B24071"},
                ]
            ),
            "contradictions": sort_contradictions(
                [{"topic": "genealogy", "source": "data/material_genealogy.csv", "record_id": "G-1"}]
            ),
            "gaps": sort_gaps([{"gap_type": "missing_coa", "subject_id": "NCB204-B24071"}]),
            "abstentions": sort_abstentions([{"reason_code": "unit_unmapped", "subject_id": "LR-88"}]),
            "execution_status": "not_executed",
        }
        runs = [dumps(pack) for _ in range(3)]
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])
        self.assertTrue(runs[0].endswith(b"\n"))

    def test_pub01_pack_is_byte_identical_across_three_runs(self) -> None:
        fixture = load_pub("PUB-01")
        runs = [dumps(batch_pack(fixture, batch_id="NCB204-B24071")) for _ in range(3)]
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])

    def test_pub04_pv_pack_is_byte_identical_across_three_runs(self) -> None:
        fixture = load_pub("PUB-04")
        runs = [dumps(pv_pack(fixture, case_ids=["PV-1001"])) for _ in range(3)]
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])

    def test_pub07_supply_pack_is_byte_identical_across_three_runs(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        fixture = load_pub("PUB-07")
        runs = [dumps(supply_pack(fixture, event_id="NCB-204-shortage")) for _ in range(3)]
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])

    def test_pub15_clinical_pack_is_byte_identical_across_three_runs(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        fixture = load_pub("PUB-15")
        runs = [dumps(advisory_pack(fixture)) for _ in range(3)]
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[1], runs[2])

    def test_pub10_reliability_pack_is_byte_identical_across_three_runs(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        fixture = load_pub("PUB-10")
        first = dumps(advisory_pack(fixture))
        reset_replay()
        second = dumps(advisory_pack(fixture))
        reset_replay()
        third = dumps(advisory_pack(fixture))
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_pub09_security_pack_is_byte_identical_across_three_runs(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        fixture = load_pub("PUB-09")
        first = dumps(advisory_pack(fixture))
        reset_replay()
        second = dumps(advisory_pack(fixture))
        reset_replay()
        third = dumps(advisory_pack(fixture))
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_pub13_agent_pack_is_byte_identical_across_three_runs(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        fixture = load_pub("PUB-13")
        first = dumps(advisory_pack(fixture))
        reset_replay()
        second = dumps(advisory_pack(fixture))
        reset_replay()
        third = dumps(advisory_pack(fixture))
        self.assertEqual(first, second)
        self.assertEqual(second, third)
