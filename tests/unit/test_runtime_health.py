from __future__ import annotations

import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from packages.config.budgets import MAX_TOKENS_PER_REQUEST
from packages.evidence_store.chain import reset_store
from packages.evidence_store.writer import persist_llm
from packages.observability.health import runtime_health


class RuntimeHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="aegis-health-")
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

    def test_empty_snapshot_is_evidence_chain_not_otel(self) -> None:
        snap = runtime_health(session_count=0)
        self.assertEqual(snap["store"], "in_process")
        self.assertEqual(snap["telemetry"], "evidence_chain")
        self.assertTrue(snap["advisory"])
        self.assertEqual(snap["llm_calls"], 0)
        self.assertEqual(snap["total_tokens"], 0)
        self.assertEqual(snap["prompt_tokens"], 0)
        self.assertEqual(snap["completion_tokens"], 0)
        self.assertEqual(snap["token_ceiling"], MAX_TOKENS_PER_REQUEST)
        self.assertEqual(snap["token_fill_pct"], 0)
        self.assertEqual(snap["authz_denials"], 0)
        self.assertFalse(snap["estimated"])
        self.assertIn("cost", snap)
        self.assertFalse(snap["cost"]["estimated"])
        self.assertNotIn("opentelemetry", str(snap).casefold())

    def test_sums_recorded_tokens_and_denials(self) -> None:
        persist_llm(
            "req-health",
            {
                "called": True,
                "prompt": {"role": "system"},
                "deployment": "dep",
                "outbound": 1,
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "total_tokens": 20,
                "guard": {"check": "schema", "passed": False},
            },
        )
        snap = runtime_health(
            session_count=2,
            audit_events=[
                {"decision": "deny"},
                {"event": "tool_refused"},
                {"event": "acknowledge"},
            ],
        )
        self.assertEqual(snap["session_count"], 2)
        self.assertEqual(snap["chain_count"], 1)
        self.assertEqual(snap["llm_calls"], 1)
        self.assertEqual(snap["prompt_tokens"], 12)
        self.assertEqual(snap["completion_tokens"], 8)
        self.assertEqual(snap["total_tokens"], 20)
        self.assertEqual(snap["guard_fail"], 1)
        self.assertEqual(snap["authz_denials"], 2)
        self.assertEqual(snap["audit_events"], 3)
        self.assertEqual(snap["token_fill_pct"], 0)
        cost = snap["cost"]
        self.assertFalse(cost["estimated"])
        self.assertFalse(cost["total_complete"])
        self.assertTrue(cost["priced"])
        self.assertEqual(cost["model"], "large-1")
        expected = (Decimal("12") / Decimal("1000000")) * Decimal("8.50") + (
            Decimal("8") / Decimal("1000000")
        ) * Decimal("22.00")
        self.assertEqual(cost["inference_cost"], format(expected, "f"))
        self.assertIn("human_quality_review", cost["missing_components"])
        self.assertEqual(snap["deployments"][0]["deployment"], "dep")
        self.assertEqual(snap["llm_live_calls"], 1)
