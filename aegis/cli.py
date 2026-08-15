"""AEGIS command-line interface. Stdlib only. `python -m aegis <command>`."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from packages.config.catalog import default_entity, fixture_for  # noqa: E402
from packages.config.paths import repo_root, synthetic_dir  # noqa: E402
from packages.config.runtime import llm_enabled, runtime_mode  # noqa: E402
from packages.kernel.canonical import dumps  # noqa: E402
from packages.kernel.interpreter import guard as interpreter_guard  # noqa: E402


def _quality_dir() -> Path:
    return repo_root() / "quality" / "static-analysis"


def _run_gates() -> None:
    sys.path.insert(0, str(_quality_dir()))
    from inject_coverage_gate import assert_coverage
    from module_boundaries import assert_boundaries
    from nondeterminism_gate import assert_deterministic
    from stdlib_gate import assert_stdlib_only
    from traceability import assert_traceable, write_traceability_csv

    assert_stdlib_only()
    assert_deterministic()
    assert_boundaries()
    assert_coverage()
    write_traceability_csv()
    assert_traceable()


def cmd_setup(_args: argparse.Namespace) -> int:
    interpreter_guard()
    from scripts.build_fixture_copyset import build
    from scripts.generate_structure_manifest import write_manifest

    build()
    write_manifest()
    _run_gates()
    sys.stdout.write(f"setup ok mode={runtime_mode()} llm_enabled={llm_enabled()}\n")
    return 0


def _load_fixture(name: str) -> dict:
    fixtures = synthetic_dir() / "evaluation" / "public_fixtures"
    if not fixtures.is_dir():
        from scripts.build_fixture_copyset import build

        build()
    return json.loads((fixtures / name).read_text(encoding="utf-8"))


def _select_batch_fixture(entity_id: str) -> dict:
    return _load_fixture(fixture_for("batch", entity_id or default_entity("batch")))


def _select_pv_fixture(entity_id: str) -> dict:
    return _load_fixture(fixture_for("pv", entity_id or default_entity("pv")))


def _select_supply_fixture(entity_id: str) -> dict:
    return _load_fixture(fixture_for("supply", entity_id or default_entity("supply")))


def cmd_run(args: argparse.Namespace) -> int:
    interpreter_guard()
    from services.integration.langgraph.resolve import resolve_runtime_orchestrator
    from services.integration.azure.openai import configure_inference

    configure_inference(override=True)

    workflow = (args.workflow or "batch").strip()
    entity_id = args.entity_id or ""
    if workflow in {"batch", "batch_evidence"}:
        entity_id = entity_id or default_entity("batch")
        payload = _select_batch_fixture(entity_id)
    elif workflow in {"pv", "pv_intake"}:
        entity_id = entity_id or default_entity("pv")
        payload = _select_pv_fixture(entity_id)
    elif workflow in {"supply", "supply_options"}:
        entity_id = entity_id or default_entity("supply")
        payload = _select_supply_fixture(entity_id)
    elif workflow in {"clinical"}:
        payload = _load_fixture("PUB-15.json")
    elif workflow in {"agent"}:
        payload = _load_fixture("PUB-13.json")
    elif workflow in {"reliability", "continuity"}:
        payload = _load_fixture("PUB-10.json")
    elif workflow in {"finops"}:
        payload = _load_fixture("PUB-14.json")
    else:
        payload = _load_fixture("PUB-09.json")
    pack = resolve_runtime_orchestrator().run(
        {"fixture": payload, "workflow": workflow, "entity_id": entity_id}
    )
    sys.stdout.buffer.write(dumps(pack))
    return 0


def cmd_test(_args: argparse.Namespace) -> int:
    interpreter_guard()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    sys.path.insert(0, str(repo_root()))
    quality = _quality_dir()
    sys.path.insert(0, str(quality))
    suite.addTests(loader.discover(str(repo_root() / "tests"), pattern="test_*.py", top_level_dir=str(repo_root())))
    suite.addTests(loader.discover(str(quality), pattern="test_*.py", top_level_dir=str(quality)))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def cmd_evaluate(_args: argparse.Namespace) -> int:
    interpreter_guard()
    from packages.contracts.resolve import resolve_contract
    from scripts.build_fixture_copyset import build

    fixtures_dir = synthetic_dir() / "evaluation" / "public_fixtures"
    if not fixtures_dir.is_dir():
        build()
    rows = []
    for path in sorted(fixtures_dir.glob("PUB-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        contract = payload.get("response_contract")
        resolve_contract(str(contract))
        rows.append({"fixture": path.name, "response_contract": contract, "resolved": True})
    dest = repo_root() / "out" / "evaluate.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(dumps({"mode": runtime_mode(), "fixtures": rows}))
    sys.stdout.write(str(dest) + "\n")
    return 0


def cmd_reset(_args: argparse.Namespace) -> int:
    interpreter_guard()
    import shutil

    from packages.kernel.checkpoint import reset_replay

    reset_replay()
    out = repo_root() / "out"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    sys.stdout.write("reset ok\n")
    return 0


def cmd_evidence_export(_args: argparse.Namespace) -> int:
    interpreter_guard()
    from packages.evidence_store.chain import rebuild_index

    injects = json.loads((repo_root() / "data" / "injects.json").read_text(encoding="utf-8"))
    dest = repo_root() / "out" / "evidence-export.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(
        dumps(
            {
                "phase": "6",
                "mode": runtime_mode(),
                "llm_enabled": llm_enabled(),
                "commands": [
                    "setup",
                    "run",
                    "test",
                    "evaluate",
                    "reset",
                    "evidence-export",
                    "evidence",
                    "verify-evidence",
                    "serve",
                    "mcp",
                ],
                "injects": [{"id": item["id"], "title": item["title"]} for item in injects],
                "index": rebuild_index(),
            }
        )
    )
    sys.stdout.write(str(dest) + "\n")
    return 0


def cmd_evidence(args: argparse.Namespace) -> int:
    interpreter_guard()
    from packages.evidence_store.chain import load_chain, verify_chain

    request_id = args.request_id
    verify_chain(request_id)
    rows = load_chain(request_id)
    sys.stdout.buffer.write(dumps({"request_id": request_id, "chain": rows}))
    return 0


def cmd_verify_evidence(_args: argparse.Namespace) -> int:
    interpreter_guard()
    from packages.evidence_store.chain import verify_all

    result = verify_all()
    sys.stdout.buffer.write(dumps(result))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    interpreter_guard()
    from services.api.server import serve

    return serve(host=args.host, port=int(args.port))


def cmd_mcp(_args: argparse.Namespace) -> int:
    interpreter_guard()
    from services.integration.mcp.server import serve_stdio

    return serve_stdio()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aegis")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("setup").set_defaults(func=cmd_setup)
    run = sub.add_parser("run")
    run.add_argument("--workflow", default="batch")
    run.add_argument("--id", dest="entity_id", default="")
    run.set_defaults(func=cmd_run)
    sub.add_parser("test").set_defaults(func=cmd_test)
    sub.add_parser("evaluate").set_defaults(func=cmd_evaluate)
    sub.add_parser("reset").set_defaults(func=cmd_reset)
    sub.add_parser("evidence-export").set_defaults(func=cmd_evidence_export)
    evidence = sub.add_parser("evidence")
    evidence.add_argument("--request-id", required=True)
    evidence.set_defaults(func=cmd_evidence)
    sub.add_parser("verify-evidence").set_defaults(func=cmd_verify_evidence)
    serve_cmd = sub.add_parser("serve")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", default=8000, type=int)
    serve_cmd.set_defaults(func=cmd_serve)
    sub.add_parser("mcp").set_defaults(func=cmd_mcp)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
