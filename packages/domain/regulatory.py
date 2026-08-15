"""Regulatory identity, labelling, commitments and sequences. Classification types live only here (MR-5)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from packages.domain.batch import iter_records
from packages.domain.types import Contradiction, Gap
from packages.ontology.identity import Identifier, resolve_identity
from packages.ontology.mappings import load_idmp_mappings

_SEQ = re.compile(r"(\d+)$")


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def _fact(
    *,
    source: str,
    authority: str,
    version: str,
    effective_date: str,
    **fields: Any,
) -> dict[str, Any]:
    payload = {
        "source": source,
        "authority": authority,
        "version": version,
        "effective_date": effective_date,
    }
    payload.update(fields)
    return payload


def reconcile_regulatory(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    products: list[tuple[str, dict[str, Any]]] = []
    labels: list[dict[str, Any]] = []
    commitments: list[dict[str, Any]] = []
    letters: list[dict[str, Any]] = []
    sequences: list[dict[str, Any]] = []
    variations: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        name = _source_name(source)
        if name == "medicinal_products.csv":
            products.append((source, record))
        elif name == "product_labels.csv":
            labels.append(record)
        elif name == "regulatory_commitments.csv":
            commitments.append(record)
        elif name == "authority_correspondence.csv":
            letters.append(record)
        elif name == "ectd_sequences.csv":
            sequences.append(record)
        elif name == "regulatory_changes.csv":
            variations.append(record)

    contradictions: list[Contradiction] = []
    gaps: list[Gap] = []
    facts: list[dict[str, Any]] = []

    if len(products) >= 2:
        left_source, left = products[0]
        right_source, right = products[1]
        left_id = Identifier(scheme=str(left.get("source") or "rim"), value=str(left.get("product_id") or ""), org_namespace="NTG")
        right_id = Identifier(scheme=str(right.get("source") or "erp"), value=str(right.get("product_id") or ""), org_namespace="NTG")
        result = resolve_identity(left_id, right_id, mappings=load_idmp_mappings())
        differing = [
            field
            for field in ("product_id", "source", "strength", "dose_form", "substance")
            if str(left.get(field) or "") != str(right.get(field) or "")
        ]
        contradictions.append(
            Contradiction(
                topic="product_identity",
                source=left_source,
                record_id=str(left.get("product_id") or ""),
                verdict="IdentityConflict",
                reason_code=result.reason_code,
                systems=[str(left.get("source") or ""), str(right.get("source") or "")],
                identifiers=[str(left.get("product_id") or ""), str(right.get("product_id") or "")],
                differing_fields=differing,
                statement="IdentityConflict: both records are retained. No preferred identity is created and no source is ranked.",
            )
        )
        facts.append(
            _fact(
                source=left_source,
                authority=str(left.get("source") or "RIM"),
                version="as_supplied",
                effective_date=as_of,
                product_id=str(left.get("product_id") or ""),
            )
        )
        facts.append(
            _fact(
                source=right_source,
                authority=str(right.get("source") or "ERP"),
                version="as_supplied",
                effective_date=as_of,
                product_id=str(right.get("product_id") or ""),
            )
        )

    label_entries = []
    for row in labels:
        entry = _fact(
            source="data/product_labels.csv",
            authority="labelling",
            version=str(row.get("version") or ""),
            effective_date=as_of,
            product=str(row.get("product") or ""),
            market=str(row.get("market") or ""),
            risk_text=str(row.get("risk_text") or ""),
            approval_state=str(row.get("status") or ""),
        )
        label_entries.append(entry)
        facts.append(entry)

    deadline_candidates: list[dict[str, Any]] = []
    for row in commitments:
        cid = str(row.get("commitment_id") or "")
        for field, basis in (("tracker_due", "tracker"), ("authority_letter_due", "authority_letter")):
            if row.get(field):
                item = _fact(
                    source="data/regulatory_commitments.csv",
                    authority="commitment_tracker",
                    version="as_supplied",
                    effective_date=str(row.get(field) or ""),
                    commitment_id=cid,
                    deadline=str(row.get(field) or ""),
                    basis=basis,
                    status=str(row.get("status") or ""),
                )
                deadline_candidates.append(item)
                facts.append(item)
    for row in letters:
        item = _fact(
            source="data/authority_correspondence.csv",
            authority="authority_letter",
            version="as_supplied",
            effective_date=str(row.get("receipt_time") or as_of),
            commitment_id=str(row.get("commitment_id") or ""),
            deadline=str(row.get("text_due_date") or ""),
            basis="relative_to_receipt",
            receipt_time=str(row.get("receipt_time") or ""),
        )
        deadline_candidates.append(item)
        facts.append(item)

    numbers: list[tuple[int, str]] = []
    for row in sequences:
        token = str(row.get("sequence") or "")
        match = _SEQ.search(token)
        if match:
            numbers.append((int(match.group(1)), token))
        facts.append(
            _fact(
                source="data/ectd_sequences.csv",
                authority="ectd",
                version=token or "as_supplied",
                effective_date=as_of,
                sequence=token,
                product=str(row.get("product") or ""),
                archive_present=str(row.get("archive_present") or ""),
            )
        )
    ordered = sorted(numbers)
    for index in range(len(ordered) - 1):
        current, current_id = ordered[index]
        nxt, _nxt_id = ordered[index + 1]
        missing = current + 1
        if nxt > missing:
            named = f"{current_id[: current_id.rfind(str(current))]}{missing:0{len(str(current))}d}"
            gaps.append(
                Gap(
                    gap_type="sequence_gap",
                    subject_id=named,
                    missing=named,
                    statement=f"Submission sequence {named} is missing. Sequences are not rewritten or inferred.",
                )
            )

    variation_positions: list[dict[str, Any]] = []
    for row in variations:
        for field, party in (("EU_classification", "EU"), ("US_classification", "US")):
            variation_positions.append(
                {
                    "change_id": str(row.get("change_id") or ""),
                    "party": party,
                    "position": str(row.get(field) or ""),
                    "rationale_source": "data/regulatory_changes.csv",
                    "dispute": str(row.get("dispute") or ""),
                    "change": str(row.get("change") or ""),
                }
            )
        facts.append(
            _fact(
                source="data/regulatory_changes.csv",
                authority="regulatory_change",
                version=str(row.get("change_id") or "as_supplied"),
                effective_date=as_of,
                change_id=str(row.get("change_id") or ""),
                dispute=str(row.get("dispute") or ""),
            )
        )

    return {
        "contradictions": contradictions,
        "gaps": gaps,
        "facts": facts,
        "labels": label_entries,
        "deadline_candidates": deadline_candidates,
        "variation_positions": variation_positions,
    }
