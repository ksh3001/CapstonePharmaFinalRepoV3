"""FDE submission bridge stub. Emits a scorecard envelope; vendoring is a later defence-tag step."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from packages.kernel.canonical import dumps  # noqa: E402


def export(destination: Path | None = None) -> Path:
    target = destination if destination is not None else _REPO_ROOT / "out" / "submission_bridge.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "stub",
        "phase": "0",
        "message": "Phase 0 bridge stub. Vendored snapshot is produced at defence tags (plan §3.3).",
    }
    target.write_bytes(dumps(payload))
    return target


def main() -> int:
    path = export()
    sys.stdout.write(str(path) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
