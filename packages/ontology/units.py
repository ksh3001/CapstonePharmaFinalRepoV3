"""Quantity comparison. Never convert. Unapproved mappings abstain (BR-003, INJ-024)."""

from __future__ import annotations

from packages.ontology.mappings import is_approved_status, load_unit_mappings
from packages.ontology.types import ComparisonResult, Quantity

REASON_UNAPPROVED = "unit_mapping_unapproved"


def _pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))  # type: ignore[return-value]


def compare_quantities(
    left: Quantity,
    right: Quantity,
    *,
    mappings: tuple[dict[str, str], ...] | None = None,
    as_of: str = "",
) -> ComparisonResult:
    """Return whether two quantities may be compared. Never returns a converted number."""
    del as_of  # register has no effective window today; argument kept for the contract
    if left.unit_code == right.unit_code and left.unit_system == right.unit_system:
        return ComparisonResult(comparable=True, converted_value=None)
    rows = mappings if mappings is not None else load_unit_mappings()
    for row in rows:
        source = row.get("source_unit") or ""
        target = row.get("target_unit") or ""
        if _pair_key(source, target) != _pair_key(left.unit_code, right.unit_code):
            continue
        mapping_id = row.get("interface") or None
        if is_approved_status(row.get("approved") or ""):
            return ComparisonResult(comparable=True, mapping_id=mapping_id, converted_value=None)
        return ComparisonResult(
            comparable=False,
            reason_code=REASON_UNAPPROVED,
            mapping_id=mapping_id,
            converted_value=None,
        )
    return ComparisonResult(comparable=False, reason_code=REASON_UNAPPROVED, converted_value=None)


def compare_measurements(
    left: Quantity,
    right: Quantity,
    *,
    left_method: str,
    left_method_version: str,
    right_method: str,
    right_method_version: str,
    comparability_approved: bool,
    mappings: tuple[dict[str, str], ...] | None = None,
    as_of: str = "",
) -> ComparisonResult:
    """BR-130: different method versions are not comparable without an approved assessment."""
    same_method = left_method == right_method and left_method_version == right_method_version
    if not same_method and not comparability_approved:
        return ComparisonResult(
            comparable=False,
            reason_code="method_comparability_unapproved",
            converted_value=None,
        )
    return compare_quantities(left, right, mappings=mappings, as_of=as_of)
