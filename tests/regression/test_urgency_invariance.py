from __future__ import annotations

import copy
import unittest

from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub
from tests.unit.test_identity_conflict import regulatory_fixture


class UrgencyInvarianceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_inspection_surge_does_not_change_bytes(self) -> None:
        base = regulatory_fixture()
        surged = copy.deepcopy(base)
        surged["authorized_context"]["urgency"] = "inspection_surge"
        surged["authorized_context"]["deadline_hours"] = "72"
        first = dumps(advisory_pack(base))
        reset_replay()
        second = dumps(advisory_pack(surged))
        self.assertEqual(first, second)

    def test_urgency_does_not_change_bytes_on_gate_bearing_fixtures(self) -> None:
        for name in ("PUB-09", "PUB-11"):
            with self.subTest(name=name):
                reset_replay()
                base = load_pub(name)
                surged = copy.deepcopy(base)
                surged["authorized_context"]["urgency"] = "inspection_surge"
                surged["authorized_context"]["deadline_hours"] = "1"
                surged["authorized_context"]["commercial_exposure"] = "maximum"
                first = dumps(advisory_pack(base))
                reset_replay()
                second = dumps(advisory_pack(surged))
                self.assertEqual(first, second)
