from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from services.integration.azure.openai import (
    _clip_chat_summary,
    _offline_restatement,
    _plain_blocks,
    summarize_tool_json,
)


class ChatSummaryTests(unittest.TestCase):
    def test_offline_restatement_is_two_short_sentences(self) -> None:
        text = _offline_restatement(
            {
                "entity": "NCB204-B24071",
                "readiness_state": "insufficient_evidence",
                "remaining_critical": ["LR-88", "batch record", "CMO 2025-14", "extra"],
            }
        )
        self.assertIn("NCB204-B24071", text)
        self.assertIn("not ready for Qualified Person review", text)
        self.assertIn("LR-88", text)
        self.assertNotIn("insufficient_evidence", text)
        self.assertLessEqual(len(text), 280)

    def test_plain_blocks_are_labelled_for_a_reviewer(self) -> None:
        blocks = _plain_blocks(
            {
                "entity": "NCB204-B24071",
                "workflow": "batch_evidence",
                "readiness_state": "insufficient_evidence",
                "remaining_critical": ["LR-88"],
            }
        )
        self.assertEqual(blocks["headline"], "NCB204-B24071 is not ready for Qualified Person review.")
        self.assertEqual(blocks["meaning"], "Still closed: LR-88.")
        self.assertIn("Open LR-88 on the pack page", blocks["next"])
        self.assertNotIn("not a decision", blocks.get("limit", ""))

    def test_clip_keeps_two_sentences(self) -> None:
        long = "First sentence. Second sentence. Third should drop."
        self.assertEqual(_clip_chat_summary(long), "First sentence. Second sentence.")

    @patch("services.integration.azure.openai._live_call_permitted", return_value=False)
    def test_summarize_does_not_echo_the_long_answer(self, _live: object) -> None:
        old = {key: os.environ.get(key) for key in ("AEGIS_RUNTIME_MODE", "AEGIS_LLM_ENABLED")}
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            text = summarize_tool_json(
                {
                    "ok": True,
                    "answer": "Very long pack dump. " * 20,
                    "summary": {
                        "entity": "NCB204-B24071",
                        "readiness_state": "insufficient_evidence",
                        "remaining_critical": ["LR-88"],
                    },
                },
                question="What is the status of NCB204-B24071?",
            )
            self.assertIn("NCB204-B24071", text)
            self.assertIn("not ready for Qualified Person review", text)
            self.assertIn("LR-88", text)
            self.assertNotIn("Very long pack dump", text)
            self.assertLessEqual(len(text), 280)
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
