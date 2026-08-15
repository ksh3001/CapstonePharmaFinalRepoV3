"""EvidenceItem builder. Hash is the published source-artefact hash (AMB-02), never a row digest."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from packages.contracts.hashes import published_hash
from packages.domain.types import Abstention

_REPO_ROOT = Path(__file__).resolve().parents[2]


class EvidenceItem(dict):
    """Mapping that matches evidence_item.schema.json. Construct only through build_evidence_item."""


class IntegrityFailure(Abstention):
    def __init__(self, source: str, detail: str) -> None:
        super().__init__(reason_code="INTEGRITY_FAILED", subject_id=source, detail=detail)


def _resolve_source_file(source: str) -> Path | None:
    relative = source.replace("\\", "/").lstrip("./")
    candidates = [
        _REPO_ROOT / "tests" / "fixtures" / "synthetic" / relative,
        _REPO_ROOT / relative,
    ]
    challenge = _REPO_ROOT.parent / "fde-training-team3-pharma-project" / relative
    candidates.append(challenge)
    for path in candidates:
        if path.is_file():
            return path
    return None


def build_evidence_item(
    *,
    source: str,
    record_id: str,
    authority: str,
    effective_at: str | None,
    as_of: str,
    facts: dict[str, Any],
) -> EvidenceItem | Abstention:
    published = published_hash(source)
    source_file = _resolve_source_file(source)
    if published is None:
        return IntegrityFailure(source, "source path is absent from FILE_HASHES.csv")
    if source_file is None:
        return IntegrityFailure(source, "source artefact is not readable")
    actual = hashlib.sha256(source_file.read_bytes()).hexdigest()
    if actual != published:
        return IntegrityFailure(
            source,
            f"hash mismatch for {source}: expected {published}, actual {actual}",
        )
    return EvidenceItem(
        {
            "source": source,
            "record_id": record_id,
            "authority": authority,
            "effective_at": effective_at,
            "retrieved_at": as_of,
            "facts": facts,
            "integrity": {
                "sha256": published,
                "source_preserved": True,
            },
        }
    )
