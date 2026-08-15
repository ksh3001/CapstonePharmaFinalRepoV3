"""Platform-neutral CI. GitHub Actions is an optional wrapper around this script.

Assessment installs nothing. The committed fixture copy set is enough for setup,
gates, and evaluate when the challenge package is not on the runner. The full
unittest suite still needs the FDE sibling (or AEGIS_CHALLENGE_ROOT).
"""

from __future__ import annotations

import argparse
import os
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from aegis.cli import cmd_evaluate, cmd_setup, cmd_test  # noqa: E402
from packages.config.paths import challenge_available, repo_root  # noqa: E402


def _run_offline_tests() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    quality = repo_root() / "quality" / "static-analysis"
    sys.path.insert(0, str(quality))
    suite.addTests(loader.discover(str(quality), pattern="test_*.py", top_level_dir=str(quality)))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python scripts/ci.py")
    parser.add_argument(
        "--skip-evaluate",
        action="store_true",
        help="Run setup and tests only (faster PR feedback).",
    )
    parser.add_argument(
        "--full-tests",
        action="store_true",
        help="Run python -m aegis test even when the challenge package is absent.",
    )
    args = parser.parse_args(argv)
    os.environ.setdefault("AEGIS_RUNTIME_MODE", "assessment")
    os.environ.setdefault("AEGIS_LLM_ENABLED", "false")
    ns = argparse.Namespace()
    setup_rc = cmd_setup(ns)
    if setup_rc != 0:
        return setup_rc
    if args.full_tests or challenge_available():
        test_rc = cmd_test(ns)
    else:
        sys.stdout.write("ci: challenge package absent; running quality-gate tests only\n")
        test_rc = _run_offline_tests()
    if test_rc != 0:
        return test_rc
    if args.skip_evaluate:
        return 0
    return cmd_evaluate(ns)


if __name__ == "__main__":
    raise SystemExit(main())
