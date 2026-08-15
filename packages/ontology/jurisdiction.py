"""Jurisdiction qualifiers. Listedness is never pooled across jurisdictions (INJ-040)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ListednessAssertion:
    product_id: str
    term: str
    jurisdiction: str
    source: str
    listed: bool
    version: str


def pooled(left: ListednessAssertion, right: ListednessAssertion) -> bool:
    """True only when both assertions share jurisdiction, product, term and version."""
    return (
        left.product_id == right.product_id
        and left.term == right.term
        and left.jurisdiction == right.jurisdiction
        and left.version == right.version
        and left.listed == right.listed
    )


def conflict(left: ListednessAssertion, right: ListednessAssertion) -> bool:
    """Disagreement is retained; jurisdictions are not merged to hide it."""
    same_subject = (
        left.product_id == right.product_id
        and left.term == right.term
        and left.jurisdiction == right.jurisdiction
    )
    return same_subject and left.listed != right.listed
