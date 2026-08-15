"""Eval runner L0–L6 over public fixtures."""

from __future__ import annotations

from packages.kernel.canonical import dumps
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from evals.graders.deterministic import l0_contract, l1_deny_list, l6_byte_identical
from tests.helpers import load_pub


def main() -> int:
    pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
    rows = [
        l0_contract(pack, "batch_response.schema.json"),
        l1_deny_list(pack),
        l6_byte_identical(dumps(pack), dumps(pack), dumps(pack)),
    ]
    failed = [row for row in rows if not row.get("passed")]
    if failed:
        raise SystemExit("eval failed: " + str(failed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
