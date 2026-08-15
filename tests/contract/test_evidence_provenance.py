from __future__ import annotations

import re
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from tests.helpers import load_pub

_SHA = re.compile(r"^[a-f0-9]{64}$")

PACKERS = {
    "PUB-01": lambda fixture: batch_pack(fixture, batch_id="NCB204-B24071"),
    "PUB-02": lambda fixture: batch_pack(fixture, batch_id="NCS310-S26033"),
    "PUB-03": lambda fixture: batch_pack(fixture, batch_id="NCB204-B24071"),
    "PUB-04": lambda fixture: pv_pack(fixture, case_ids=["PV-1001"]),
    "PUB-05": lambda fixture: pv_pack(fixture, case_ids=["SM-77"]),
    "PUB-06": lambda fixture: pv_pack(fixture, case_ids=["NCB-204"]),
    "PUB-07": lambda fixture: supply_pack(fixture, event_id="NCB-204-shortage"),
    "PUB-08": lambda fixture: supply_pack(fixture, event_id="SH-901"),
}


class EvidenceProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_regulatory_facts_carry_source_authority_version_and_effective_date(self) -> None:
        from tests.unit.test_identity_conflict import regulatory_fixture

        pack = advisory_pack(regulatory_fixture())
        validate(pack, resolve_contract("advisory_nonexecuting"))
        facts = pack["human_review"]["regulatory"]["facts"]
        self.assertTrue(facts)
        for item in facts:
            self.assertTrue(item.get("source"), item)
            self.assertTrue(item.get("authority"), item)
            self.assertTrue(item.get("version"), item)
            self.assertTrue(item.get("effective_date"), item)

    def test_every_evidence_item_on_all_fifteen_fixtures_carries_provenance(self) -> None:
        for index in range(1, 16):
            name = f"PUB-{index:02d}"
            with self.subTest(name=name):
                reset_replay()
                fixture = load_pub(name)
                packer = PACKERS.get(name, advisory_pack)
                pack = packer(fixture)
                for item in pack.get("evidence") or []:
                    self.assertTrue(item.get("source"), item)
                    self.assertTrue(item.get("record_id"), item)
                    self.assertTrue(item.get("authority"), item)
                    self.assertTrue(item.get("retrieved_at"), item)
                    self.assertRegex(item["integrity"]["sha256"], _SHA)
                    self.assertIs(item["integrity"]["source_preserved"], True)
