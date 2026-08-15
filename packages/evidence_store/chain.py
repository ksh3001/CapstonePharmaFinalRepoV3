"""Append-only evidence chain. Stdlib only. Classification types are not constructed here."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from packages.evidence_store.codec import dumps, sha256_bytes

GENESIS = "0" * 64
RECORD_TYPES = (
    "request",
    "inputs",
    "pack",
    "decisions",
    "audit",
    "review",
    "llm",
    "guard",
    "outcome",
    "expiry",
    "hold_refusal",
)
OUTCOMES = (
    "completed",
    "abstained",
    "denied",
    "budget_exhausted",
    "source_unavailable",
    "contract_invalid",
    "guard_failed",
    "timeout",
    "internal_error",
)
DELIBERATE = frozenset({"completed", "abstained", "denied"})


class StoreUnwritable(RuntimeError):
    """BR-116: a request that cannot write evidence does not proceed."""


class ChainBreak(ValueError):
    """Tamper evidence: first broken link."""


def store_root() -> Path:
    env = os.environ.get("AEGIS_EVIDENCE_ROOT", "").strip()
    if env:
        return Path(env)
    from packages.config.paths import repo_root

    return repo_root() / "out" / "evidence"


def chain_path(request_id: str) -> Path:
    return store_root() / "chains" / f"{request_id}.jsonl"


def index_path() -> Path:
    return store_root() / "index.json"


def _ensure_writable() -> Path:
    if os.environ.get("AEGIS_EVIDENCE_READONLY", "").strip() == "1":
        raise StoreUnwritable("evidence store is not writable")
    root = store_root()
    try:
        root.mkdir(parents=True, exist_ok=True)
        (root / "chains").mkdir(parents=True, exist_ok=True)
        probe = root / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        raise StoreUnwritable(f"evidence store is not writable: {root}") from exc
    return root


def assert_writable() -> None:
    _ensure_writable()


def load_chain(request_id: str) -> list[dict[str, Any]]:
    path = chain_path(request_id)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_record(request_id: str, record_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if record_type not in RECORD_TYPES:
        raise ValueError(f"unknown record type {record_type}")
    _ensure_writable()
    existing = load_chain(request_id)
    prev = existing[-1]["entry_hash"] if existing else GENESIS
    body = {
        "seq": len(existing) + 1,
        "type": record_type,
        "request_id": request_id,
        "prev_hash": prev,
        "payload": payload,
    }
    digest = sha256_bytes(dumps(body))
    body["entry_hash"] = digest
    path = chain_path(request_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(dumps(body).decode("utf-8").rstrip("\n") + "\n")
    return body


def verify_chain(request_id: str) -> list[dict[str, Any]]:
    rows = load_chain(request_id)
    prev = GENESIS
    for row in rows:
        expected_prev = prev
        if str(row.get("prev_hash") or "") != expected_prev:
            raise ChainBreak(f"first broken link at seq={row.get('seq')} type={row.get('type')}")
        clone = dict(row)
        stored = clone.pop("entry_hash", "")
        recomputed = sha256_bytes(dumps(clone))
        if stored != recomputed:
            raise ChainBreak(f"first broken link at seq={row.get('seq')} type={row.get('type')}")
        prev = stored
    return rows


def verify_all() -> dict[str, Any]:
    folder = store_root() / "chains"
    if not folder.is_dir():
        return {"ok": True, "chains": 0}
    errors: list[str] = []
    count = 0
    for path in sorted(folder.glob("*.jsonl")):
        count += 1
        request_id = path.stem
        try:
            verify_chain(request_id)
        except ChainBreak as exc:
            errors.append(f"{request_id}: {exc}")
    if errors:
        raise ChainBreak(errors[0])
    return {"ok": True, "chains": count}


def rebuild_index() -> dict[str, Any]:
    folder = store_root() / "chains"
    index: dict[str, Any] = {"chains": []}
    if folder.is_dir():
        for path in sorted(folder.glob("*.jsonl")):
            rows = load_chain(path.stem)
            types = [str(row.get("type") or "") for row in rows]
            index["chains"].append(
                {
                    "request_id": path.stem,
                    "records": len(rows),
                    "types": types,
                    "head": rows[-1]["entry_hash"] if rows else GENESIS,
                }
            )
    _ensure_writable()
    index_path().write_bytes(dumps(index))
    return index


def has_outcome(request_id: str) -> bool:
    return any(row.get("type") == "outcome" for row in load_chain(request_id))


def reset_store() -> None:
    folder = store_root() / "chains"
    if not folder.is_dir():
        return
    for path in folder.glob("*.jsonl"):
        path.unlink()
    index = index_path()
    if index.is_file():
        index.unlink()
