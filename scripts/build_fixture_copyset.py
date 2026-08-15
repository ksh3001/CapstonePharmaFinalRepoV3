"""Derive the fixture copy set, hash-verify, and record provenance. Never modify the challenge package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from packages.config.paths import challenge_root, repo_root, synthetic_dir  # noqa: E402
from packages.kernel.canonical import dumps  # noqa: E402

GOVERNANCE = (
    "data/injects.json",
    "data/INJECT_TEST_COVERAGE.csv",
    "data/inject_evidence_map.csv",
    "data/RELATIONSHIP_MODEL.csv",
    "data/ai_use_boundaries.csv",
    "data/terminology_versions.csv",
    "data/interface_mappings.csv",
    "data/idmp_mappings.csv",
    "data/timezone_rules.csv",
    "data/controlled_vocabularies.csv",
)

SCHEMA_NAMES = (
    "batch_response.schema.json",
    "pv_response.schema.json",
    "supply_response.schema.json",
    "evidence_item.schema.json",
)

DEFAULT_AS_OF = "2026-08-01T08:00:00Z"
AUTHORITY = "challenge-package"


class CopysetError(SystemExit):
    """Copy aborted because of a missing file or hash mismatch."""


def load_hashes(challenge: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    path = challenge / "FILE_HASHES.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rel = (row.get("path") or "").replace("\\", "/").strip()
            digest = (row.get("sha256") or "").strip().lower()
            if rel and digest:
                mapping[rel] = digest
    return mapping


def published_bytes(path: Path, expected: str) -> bytes:
    """Return the bytes that match FILE_HASHES.csv.

    A Windows checkout may store CRLF. If stripping CR restores the published
    digest, those published bytes are copied — the working tree is not rewritten
    and no other normalisation is applied.
    """
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual == expected:
        return raw
    lf = raw.replace(b"\r\n", b"\n")
    if hashlib.sha256(lf).hexdigest() == expected:
        return lf
    raise CopysetError(
        f"hash mismatch for {path.as_posix()}: FILE_HASHES={expected} actual={actual}"
    )


def collect_sources(challenge: Path) -> list[str]:
    found: set[str] = set(GOVERNANCE)
    fixtures = sorted((challenge / "evaluation" / "public_fixtures").glob("PUB-*.json"))
    if not fixtures:
        raise CopysetError("no PUB-*.json fixtures found in the challenge package")
    for fixture in fixtures:
        rel = fixture.relative_to(challenge).as_posix()
        found.add(rel)
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        for ref in payload.get("evidence_references") or []:
            found.add(str(ref).replace("\\", "/"))
        for item in payload.get("evidence") or []:
            source = item.get("source")
            if source:
                found.add(str(source).replace("\\", "/"))
    for name in SCHEMA_NAMES:
        found.add(f"evaluation/contracts/{name}")
    return sorted(found)


def destination_for(relative: str) -> Path:
    name = Path(relative).name
    if relative.startswith("evaluation/contracts/") and name in SCHEMA_NAMES:
        return repo_root() / "packages" / "contracts" / "regulated" / name
    if relative == "data/injects.json":
        return repo_root() / "data" / "injects.json"
    return synthetic_dir() / relative


def build(as_of: str = DEFAULT_AS_OF, *, challenge: Path | None = None) -> dict:
    root = challenge if challenge is not None else challenge_root()
    hashes = load_hashes(root)
    sources = collect_sources(root)
    rows: list[dict[str, str]] = []
    for relative in sources:
        src = root / relative
        if not src.is_file():
            raise CopysetError(f"copy set references missing file {relative}")
        expected = hashes.get(relative)
        if expected is None:
            raise CopysetError(f"{relative} is not in FILE_HASHES.csv")
        payload = published_bytes(src, expected)
        dest = destination_for(relative)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        if hashlib.sha256(dest.read_bytes()).hexdigest() != expected:
            raise CopysetError(f"copied file drifted: {dest}")
        rows.append(
            {
                "source_path": relative,
                "sha256": expected,
                "copied_at": as_of,
                "authority": AUTHORITY,
                "synthetic": "true",
                "dest_path": dest.relative_to(repo_root()).as_posix(),
            }
        )
    synthetic_dir().mkdir(parents=True, exist_ok=True)
    provenance = synthetic_dir() / "PROVENANCE.csv"
    fieldnames = ["source_path", "sha256", "copied_at", "authority", "synthetic"]
    with provenance.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})
    hashes_dest = synthetic_dir() / "FILE_HASHES.csv"
    shutil.copy2(root / "FILE_HASHES.csv", hashes_dest)
    manifest = {
        "as_of": as_of,
        "files": [
            {"source_path": row["source_path"], "dest_path": row["dest_path"], "sha256": row["sha256"]}
            for row in rows
        ],
    }
    manifest_path = synthetic_dir() / "COPYSET_MANIFEST.json"
    manifest_path.write_bytes(dumps(manifest))
    advisory_src = repo_root() / "specs" / "api" / "advisory_nonexecuting.schema.json"
    advisory_dst = repo_root() / "packages" / "contracts" / "internal" / "advisory_nonexecuting.schema.json"
    if advisory_src.is_file():
        advisory_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(advisory_src, advisory_dst)
    return manifest


def verify_manifest() -> None:
    committed = json.loads((synthetic_dir() / "COPYSET_MANIFEST.json").read_text(encoding="utf-8"))
    derived = build(as_of=committed.get("as_of") or DEFAULT_AS_OF)
    if dumps(derived) != dumps(committed):
        raise CopysetError("COPYSET_MANIFEST.json drifted from the derived copy set")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    as_of = DEFAULT_AS_OF
    if "--as-of" in args:
        as_of = args[args.index("--as-of") + 1]
    build(as_of=as_of)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
