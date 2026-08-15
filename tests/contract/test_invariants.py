from __future__ import annotations

import unittest

from packages.contracts.invariants import InvariantError, assert_invariants
from packages.contracts.validator import SchemaError, validate
from packages.contracts.resolve import resolve_contract


def _pack(**overrides):
    base = {
        "request_id": "REQ-aaaaaaaaaaaaaaaa",
        "scenario_id": "PUB-09",
        "workflow": "security",
        "as_of": "2026-08-01T08:00:00Z",
        "authorization": {
            "user": "participant_test_user",
            "purpose": "capstone_evaluation",
            "checked_at": "2026-08-01T08:00:00Z",
            "decision": "allow",
        },
        "evidence": [
            {
                "source": "data/batches.csv",
                "record_id": "NCB204-B24071",
                "authority": "challenge-package",
                "effective_at": None,
                "retrieved_at": "2026-08-01T08:00:00Z",
                "facts": {"status": "quality_hold"},
                "integrity": {
                    "sha256": "a" * 64,
                    "source_preserved": True,
                },
            }
        ],
        "contradictions": [],
        "gaps": [],
        "abstentions": [],
        "findings": [],
        "required_reviews": [],
        "human_review": {},
        "execution_status": "not_executed",
        "gate_outcome": "advisory_only",
        "no_side_effects": True,
        "audit": {"hash_scope": "source_artifact"},
    }
    base.update(overrides)
    return base


class InvariantTests(unittest.TestCase):
    def test_valid_pack_passes(self) -> None:
        pack = _pack()
        assert_invariants(pack)
        validate(pack, resolve_contract("advisory_nonexecuting"))

    def test_execution_status_must_be_not_executed(self) -> None:
        with self.assertRaises(InvariantError):
            assert_invariants(_pack(execution_status="executed"))

    def test_missing_required_property_is_named(self) -> None:
        pack = _pack()
        del pack["audit"]
        with self.assertRaises(SchemaError) as ctx:
            validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertIn("audit", str(ctx.exception))

    def test_undeclared_property_fails(self) -> None:
        pack = _pack()
        pack["side_channel"] = True
        with self.assertRaises(SchemaError) as ctx:
            validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertIn("side_channel", str(ctx.exception))

    def test_no_side_effects_must_be_true(self) -> None:
        with self.assertRaises(InvariantError):
            assert_invariants(_pack(no_side_effects=False))
