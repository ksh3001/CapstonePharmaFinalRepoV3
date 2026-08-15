from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay, step_checkpoints
from packages.orchestrator.deterministic import StdlibOrchestrator
from tests.helpers import load_pub

PERSONAL_DATA_KEYS = frozenset(
    {
        "patient_key",
        "patient_id",
        "initials",
        "date_of_birth",
        "dob",
        "email",
        "name",
        "narrative",
        "pregnancy",
        "pregnant",
        "genomic",
        "variant",
        "postal_prefix",
        "kit",
        "allocation",
    }
)


def _keys(obj: object) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, dict):
        found.update(obj.keys())
        for value in obj.values():
            found.update(_keys(value))
    elif isinstance(obj, list):
        for item in obj:
            found.update(_keys(item))
    return found


class CheckpointContentsTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_step_checkpoints_contain_no_personal_data_fields(self) -> None:
        runner = StdlibOrchestrator()
        for name in ("PUB-01", "PUB-04", "PUB-07", "PUB-13", "PUB-15"):
            runner.run({"fixture": load_pub(name)})
        stored = step_checkpoints()
        self.assertTrue(stored)
        found = _keys(stored) & PERSONAL_DATA_KEYS
        self.assertEqual(found, set())
        self.assertTrue(all(item.get("durability") == "sync" for item in stored))
