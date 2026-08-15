from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import CONTEXT


def regulatory_fixture(extra: list[dict] | None = None) -> dict:
    evidence = [
        {
            "source": "data/medicinal_products.csv",
            "records": [
                {
                    "product_id": "NCB-204",
                    "source": "RIM",
                    "strength": "100 mg/10 mL",
                    "dose_form": "concentrate_for_infusion",
                    "substance": "SUB-204",
                },
                {
                    "product_id": "NCB204-DE",
                    "source": "ERP",
                    "strength": "10 mg/mL",
                    "dose_form": "solution",
                    "substance": "NCB antibody",
                },
            ],
        },
        {
            "source": "data/idmp_mappings.csv",
            "records": [
                {
                    "local_product": "NCB204-DE",
                    "idmp_product": "NCB-204",
                    "mapping_status": "ambiguous_strength_presentation",
                }
            ],
        },
        {
            "source": "data/product_labels.csv",
            "records": [
                {
                    "product": "NCB-204",
                    "market": "EU",
                    "version": "6",
                    "risk_text": "severe infusion reactions including anaphylaxis",
                    "status": "approved",
                },
                {
                    "product": "NCB-204",
                    "market": "US",
                    "version": "5",
                    "risk_text": "serious infusion reactions",
                    "status": "approved",
                },
            ],
        },
        {
            "source": "data/regulatory_commitments.csv",
            "records": [
                {
                    "commitment_id": "PMC-88",
                    "product": "NCB-204",
                    "tracker_due": "2026-10-15",
                    "authority_letter_due": "2026-09-30",
                    "status": "open",
                }
            ],
        },
        {
            "source": "data/authority_correspondence.csv",
            "records": [
                {
                    "document": "EMA_letter_2026_114.pdf",
                    "commitment_id": "PMC-88",
                    "text_due_date": "within 60 calendar days of receipt",
                    "tracker_due_date": "2026-09-30",
                    "receipt_time": "2026-07-28T09:14:00Z",
                }
            ],
        },
        {
            "source": "data/ectd_sequences.csv",
            "records": [
                {
                    "sequence": "EU-0041",
                    "product": "NCB-204",
                    "index_document": "m3-a.pdf",
                    "archive_present": "yes",
                },
                {
                    "sequence": "EU-0043",
                    "product": "NCB-204",
                    "index_document": "m3-c.pdf",
                    "archive_present": "yes",
                },
            ],
        },
        {
            "source": "data/regulatory_changes.csv",
            "records": [
                {
                    "change_id": "RC-19",
                    "change": "PAT model and control limit update",
                    "EU_classification": "Type II proposed",
                    "US_classification": "CBE-30 proposed",
                    "dispute": "open",
                }
            ],
        },
    ]
    if extra:
        evidence.extend(extra)
    return {
        "scenario": {"id": "REG-1", "workflow": "regulatory"},
        "authorized_context": dict(CONTEXT),
        "evidence": evidence,
        "response_contract": "advisory_nonexecuting",
    }


class IdentityConflictTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_rim_and_erp_conflict_selects_no_winner(self) -> None:
        pack = advisory_pack(regulatory_fixture())
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["workflow"], "regulatory")
        conflicts = [item for item in pack["contradictions"] if item.get("verdict") == "IdentityConflict"]
        self.assertTrue(conflicts)
        fields = conflicts[0].get("differing_fields") or []
        self.assertIn("product_id", fields)
        self.assertIn("strength", fields)
        rendered = str(pack).casefold()
        self.assertNotIn("golden record", rendered)
        self.assertNotIn("authoritative source", rendered)

    def test_variation_positions_are_retained_without_classification(self) -> None:
        pack = advisory_pack(regulatory_fixture())
        positions = pack["human_review"]["regulatory"]["variation_positions"]
        parties = {item.get("party") for item in positions}
        self.assertEqual(parties, {"EU", "US"})
        texts = {item.get("position") for item in positions}
        self.assertTrue(any("Type II" in str(item) for item in texts))
        self.assertTrue(any("CBE-30" in str(item) for item in texts))
        rendered = str(pack).casefold()
        self.assertNotIn("classified as", rendered)
        self.assertNotIn("the variation is type ii", rendered)
