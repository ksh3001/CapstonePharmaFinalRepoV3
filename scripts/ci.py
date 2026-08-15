"""Platform-neutral CI. GitHub Actions is an optional wrapper around this script.

Always runs the same command as `python -m aegis test` (tests/ plus quality gates).
A failed or errored case fails the pipeline. Tests that need the FDE challenge
package skip; a skip is not a pass of that case, but it does not fail CI.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from aegis.cli import cmd_evaluate, cmd_setup, cmd_test  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python scripts/ci.py")
    parser.add_argument(
        "--skip-evaluate",
        action="store_true",
        help="Run setup and the full test suite only (faster PR feedback).",
    )
    args = parser.parse_args(argv)
    os.environ.setdefault("AEGIS_RUNTIME_MODE", "assessment")
    os.environ.setdefault("AEGIS_LLM_ENABLED", "false")
    ns = argparse.Namespace()
    setup_rc = cmd_setup(ns)
    if setup_rc != 0:
        return setup_rc
    test_rc = cmd_test(ns)
    if test_rc != 0:
        return test_rc
    if args.skip_evaluate:
        return 0
    return cmd_evaluate(ns)


if __name__ == "__main__":
    raise SystemExit(main())
