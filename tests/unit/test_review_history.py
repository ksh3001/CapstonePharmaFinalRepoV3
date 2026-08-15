from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from packages.evidence_store.chain import load_chain, reset_store
from packages.evidence_store.history import list_review_events
from packages.evidence_store.writer import persist_review


class ReviewHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="aegis-history-")
        self._old = os.environ.get("AEGIS_EVIDENCE_ROOT")
        os.environ["AEGIS_EVIDENCE_ROOT"] = self._tmp
        reset_store()

    def tearDown(self) -> None:
        reset_store()
        if self._old is None:
            os.environ.pop("AEGIS_EVIDENCE_ROOT", None)
        else:
            os.environ["AEGIS_EVIDENCE_ROOT"] = self._old
        root = Path(self._tmp)
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        if root.is_dir():
            root.rmdir()

    def test_reviewer_action_is_a_review_record_not_a_signature(self) -> None:
        stored = persist_review(
            "REQ-history",
            {
                "event": "contest",
                "user": "reviewer_9",
                "reason": "missing commitment",
                "action_taken": "Asked quality for the CMO packet",
                "entity": "NCB204-B24071",
                "workflow": "batch_evidence",
            },
        )
        rows = [row for row in load_chain("REQ-history") if row["type"] == "review"]
        self.assertEqual(len(rows), 1)
        payload = rows[0]["payload"]
        self.assertEqual(payload["kind"], "reviewer_action")
        self.assertFalse(payload["signature"])
        self.assertFalse(payload["execution"])
        self.assertEqual(payload["action_taken"], "Asked quality for the CMO packet")
        self.assertEqual(stored["seq"], 1)
        events = list_review_events()
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["decision"])
        self.assertEqual(events[0]["entity"], "NCB204-B24071")
        self.assertEqual(events[0]["href"], "/workflows/batch/NCB204-B24071")

    def test_bulk_audit_dump_is_not_listed_as_a_reviewer_action(self) -> None:
        from packages.evidence_store.chain import append_record

        append_record("REQ-audit", "audit", {"events": [{"event": "acknowledge"}]})
        self.assertEqual(list_review_events(), [])
