"""Domain wrappers over the graph projection. Classification types live only here (MR-5)."""

from __future__ import annotations

from typing import Any

from packages.domain.types import Abstention, Gap
from packages.graph.projection import HARD_CAP, Projection


def traverse_recall_scope(
    graph: Projection,
    seed: str,
    *,
    max_hops: int = 4,
    as_of: str = "",
    allowed: frozenset[str] | None = None,
) -> tuple[Any, Abstention | None]:
    """BR-028 / AC-FR003-07: hop-limit truncation is an abstention, never a complete scope."""
    result = graph.traverse(seed, max_hops=max_hops, as_of=as_of, allowed=allowed)
    if not result.traversal_incomplete:
        return result, None
    abstention = Abstention(
        reason_code="traversal_incomplete",
        subject_id=seed,
        frontier=list(result.frontier),
        hops_used=result.hops_used,
        max_hops=min(max_hops, HARD_CAP),
        evidence_refs=[seed],
    )
    return result, abstention


def licence_scoped_claims(
    claims: list[dict[str, Any]],
    licences: list[dict[str, Any]],
    *,
    purpose: str,
) -> dict[str, Any]:
    """AC-FR004-15: retain permitted claims; exclude licence-barred content as a gap."""
    by_dataset = {str(row.get("dataset") or ""): row for row in licences}
    kept: list[dict[str, Any]] = []
    gaps: list[Gap] = []
    for claim in claims:
        dataset = str(claim.get("dataset") or "")
        licence = by_dataset.get(dataset) or {}
        if licence and not _purpose_permitted(str(licence.get("permitted_use") or ""), purpose):
            gaps.append(
                Gap(
                    gap_type="licence_scope",
                    subject_id=dataset,
                    permitted_use=licence.get("permitted_use"),
                    requested_purpose=purpose,
                    evidence_refs=[dataset],
                )
            )
            continue
        kept.append(dict(claim))
    return {
        "claims": kept,
        "gaps": [item.as_dict() for item in gaps],
    }


def recurrence_candidates(deviations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """AC-FR004-16: candidate links only. No effectiveness verdict, no closure statement."""
    by_id = {str(row.get("deviation_id") or ""): row for row in deviations}
    found: list[dict[str, Any]] = []
    for row in deviations:
        other_id = str(row.get("similarity_to") or "")
        other = by_id.get(other_id)
        if not other:
            continue
        found.append(
            {
                "kind": "POSSIBLY_RELATED_TO",
                "left": str(row.get("deviation_id") or ""),
                "right": other_id,
                "basis": "similarity_to",
                "taxonomies": [str(row.get("taxonomy") or ""), str(other.get("taxonomy") or "")],
            }
        )
    return found


def uncontrolled_calculation(
    *,
    value: str,
    tool: str,
    verified: str,
) -> tuple[dict[str, Any], Abstention | None]:
    """AC-FR004-17: unvalidated tool output is never authority."""
    record = {
        "value": value,
        "tool": tool,
        "uncontrolled_calculation": True,
        "authority": False,
    }
    if (verified or "").strip().lower() == "yes":
        record["uncontrolled_calculation"] = False
        record["authority"] = True
        return record, None
    abstention = Abstention(
        reason_code="uncontrolled_calculation",
        subject_id=tool,
        tool=tool,
        evidence_refs=[tool],
    )
    return record, abstention


def _purpose_permitted(permitted_use: str, purpose: str) -> bool:
    allowed = (permitted_use or "").strip().lower()
    requested = (purpose or "").strip().lower()
    if not allowed or "review required" in allowed or allowed == "unclear":
        return False
    if "research" in allowed:
        return "research" in requested
    return requested == allowed or requested in allowed
