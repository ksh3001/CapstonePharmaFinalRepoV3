from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class AvoidedInferenceTests(unittest.TestCase):
    def test_assessment_run_reports_zero_model_calls(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        avoided = pack["human_review"]["finops"]["avoided_inference"]
        self.assertEqual(avoided["model_calls"], "0")
        self.assertEqual(avoided["count"], "0")
