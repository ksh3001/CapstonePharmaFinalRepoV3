from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with

DRAFT = {
    "doc_id": "K-026",
    "file": "RESEARCH_NOTE_UNAPPROVED.md",
    "authority": "Research working note",
    "effective": "2026-07-12",
    "status": "draft",
}
FUTURE = {
    "doc_id": "K-FUTURE",
    "file": "FUTURE_EFFECTIVE.md",
    "authority": "NovaCura Global Policy",
    "effective": "2026-12-01",
    "status": "approved",
}
RETIRED = {
    "doc_id": "K-RETIRED",
    "file": "RETIRED_SOP.md",
    "authority": "NovaCura Global Policy",
    "effective": "2025-01-01",
    "status": "retired",
}


def _catalog(*rows: dict[str, str]) -> dict:
    return fixture_with(
        [{"source": "data/knowledge_catalog.csv", "records": list(rows)}],
        scenario_id="SYN-AUTH",
        workflow="security",
    )


class AuthorityResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_draft_is_never_cited_as_authority(self) -> None:
        pack = advisory_pack(_catalog(DRAFT))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        rendered = " ".join(item["statement"] for item in pack["findings"]).casefold()
        self.assertIn("draft", rendered)
        self.assertIn("not used as authority", rendered)
        for item in pack["evidence"]:
            self.assertNotEqual(item["authority"], "Research working note")
            self.assertNotEqual(item["authority"], "K-026")
        excluded = pack["human_review"]["authority"]["excluded_from_authority"]
        self.assertTrue(any(row["document_id"] in {"K-026", "RESEARCH_NOTE_UNAPPROVED.md"} for row in excluded))

    def test_future_effective_and_retired_are_excluded_with_reason(self) -> None:
        pack = advisory_pack(_catalog(FUTURE, RETIRED))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        reasons = {row["reason"] for row in pack["human_review"]["authority"]["excluded_from_authority"]}
        self.assertIn("effective_after_as_of", reasons)
        self.assertTrue(any(reason.startswith("status_retired") for reason in reasons))
        statements = " ".join(item["statement"] for item in pack["findings"])
        self.assertIn("2026-12-01", statements)
        self.assertIn("retired", statements.casefold())
