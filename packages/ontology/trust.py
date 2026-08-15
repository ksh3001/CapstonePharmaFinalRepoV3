"""Trust status. Untrusted content cannot ground an assertion (INJ-031/065)."""

from __future__ import annotations

from packages.ontology.types import NON_GROUNDING_TRUST, TrustStatus

AUTHORITY_STATUSES_UNUSABLE = frozenset({"draft", "retired", "unknown"})


def can_ground_assertion(status: TrustStatus) -> bool:
    return status == "trusted"


def trust_for_document(*, status: str, hash_ok: bool, contains_instruction: bool) -> TrustStatus:
    if not hash_ok:
        return "reduced_integrity"
    if contains_instruction:
        return "untrusted"
    if (status or "").strip().lower() in AUTHORITY_STATUSES_UNUSABLE:
        return "untrusted"
    if (status or "").strip().lower() == "superseded":
        return "superseded"
    return "trusted"


def referenced_missing() -> TrustStatus:
    return "referenced_missing"
