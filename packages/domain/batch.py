"""Workflow A batch reconciliation. Classification types are constructed only here (MR-5)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from packages.domain.evidence import EvidenceItem, build_evidence_item
from packages.domain.types import Abstention, Contradiction, Gap
from packages.ontology.instructions import (
    contains_embedded_instruction,
    facts_excluding_instructions,
    flatten_strings,
)
from packages.ontology.trust import trust_for_document
from packages.ontology.types import Quantity
from packages.ontology.units import compare_quantities

BLOCKING_GAP_TYPES = frozenset(
    {
        "missing_required_element",
        "referenced_missing",
        "cmo_commitment_missing",
        "cleaning_boundary",
    }
)
ABSENT_RELATIONS = frozenset({"missing_branch", "absent", "missing"})
PRESENT_MOVEMENT = frozenset({"issued", "received", "in_stock"})
_SPEC_UNIT = re.compile(r"(?P<unit>%|ug/mL|mg/L|mg/mL|IU/mL|[A-Za-zµμ/%]+)\s*$")


def compute_readiness(gaps: list[Gap], contradictions: list[Contradiction]) -> str:
    """BR-006: blocking gap → insufficient; else contradiction → conflicted; else ready."""
    if any(gap.gap_type in BLOCKING_GAP_TYPES for gap in gaps):
        return "insufficient_evidence"
    if contradictions:
        return "conflicted_evidence"
    return "ready_for_authorized_review"


def infer_batch_id(fixture: dict[str, Any], requested: str = "") -> str:
    if requested:
        return requested
    for _source, record in iter_records(fixture):
        batch_id = record.get("batch_id")
        if batch_id:
            return str(batch_id)
    return "UNSET"


def iter_records(fixture: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for blob in fixture.get("evidence") or []:
        source = str(blob.get("source") or "")
        for record in blob.get("records") or []:
            if isinstance(record, dict):
                rows.append((source, record))
    return rows


def _record_id(record: dict[str, Any], source: str, index: int) -> str:
    for key in (
        "record_id",
        "result_id",
        "movement_id",
        "investigation_id",
        "audit_id",
        "coa_id",
        "sample_id",
        "complaint_id",
        "doc_id",
        "model_id",
        "recipe_id",
        "tool_id",
        "interface",
    ):
        value = record.get(key)
        if value:
            extra = record.get("material_lot") or record.get("packet_item") or record.get("source_unit") or ""
            if extra and key in {"batch_id", "interface"}:
                return f"{value}:{extra}"
            return str(value)
    batch_id = record.get("batch_id")
    extra = record.get("material_lot") or record.get("packet_item") or ""
    if batch_id and extra:
        return f"{batch_id}:{extra}"
    if batch_id:
        return str(batch_id)
    equipment = record.get("equipment")
    if equipment:
        return f"{equipment}:{record.get('campaign') or record.get('previous_product') or index}"
    return f"{source}:{index}"


def _spec_unit(spec: str) -> str | None:
    text = (spec or "").strip()
    if not text:
        return None
    if text.endswith("%"):
        return "%"
    match = _SPEC_UNIT.search(text)
    if match:
        return match.group("unit")
    parts = text.split()
    if len(parts) >= 2:
        return parts[-1]
    return None


def _product_family(product_id: str) -> str:
    return (product_id or "").split("-", 1)[0]


def _security_finding(source: str, record_id: str) -> dict[str, Any]:
    return {
        "finding_id": f"SEC-INSTR-{record_id}",
        "kind": "embedded_instruction",
        "subject_id": record_id,
        "source": source,
        "statement": "Embedded instruction detected; content treated as data and excluded from reasoning.",
        "trust_status": trust_for_document(status="effective", hash_ok=True, contains_instruction=True),
        "evidence_refs": [record_id],
    }


def iter_text_blobs(fixture: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for blob in fixture.get("evidence") or []:
        source = str(blob.get("source") or "")
        text = blob.get("text")
        if source and isinstance(text, str) and text.strip():
            rows.append((source, text))
    return rows


def reconcile_batch(
    fixture: dict[str, Any],
    *,
    batch_id: str,
    as_of: str,
) -> dict[str, Any]:
    evidence: list[EvidenceItem] = []
    abstentions: list[Abstention] = []
    findings: list[dict[str, Any]] = []
    usable: list[tuple[str, str, dict[str, Any]]] = []
    finding_sources: set[str] = set()

    for index, (source, record) in enumerate(iter_records(fixture)):
        rid = _record_id(record, source, index)
        injected = contains_embedded_instruction(flatten_strings(record))
        facts = facts_excluding_instructions(record)
        if injected:
            facts["trust_status"] = "untrusted"
            facts["cited"] = True
            if source not in finding_sources:
                findings.append(_security_finding(source, rid))
                finding_sources.add(source)
        built = build_evidence_item(
            source=source,
            record_id=rid,
            authority=str(record.get("authority") or record.get("source") or "challenge-package"),
            effective_at=record.get("effective")
            or record.get("manufacture_date")
            or record.get("time")
            or record.get("correction_time")
            or record.get("effective_date")
            or record.get("deployed_time"),
            as_of=as_of,
            facts=facts,
        )
        if isinstance(built, Abstention):
            abstentions.append(built)
            continue
        evidence.append(built)
        if not injected:
            usable.append((source, rid, record))

    for source, text in iter_text_blobs(fixture):
        rid = Path(source.replace("\\", "/")).name
        injected = contains_embedded_instruction(text)
        if injected and source not in finding_sources:
            findings.append(_security_finding(source, rid))
            finding_sources.add(source)
        built = build_evidence_item(
            source=source,
            record_id=rid,
            authority="challenge-package",
            effective_at=None,
            as_of=as_of,
            facts={
                "kind": "retrieved_document",
                "cited": True,
            },
        )
        if isinstance(built, Abstention):
            abstentions.append(built)
            continue
        evidence.append(built)

    contradictions: list[Contradiction] = []
    gaps: list[Gap] = []
    applicable: list[dict[str, Any]] = []

    genealogy: list[tuple[str, dict[str, Any]]] = []
    movements: list[tuple[str, dict[str, Any]]] = []
    lab_rows: list[tuple[str, dict[str, Any]]] = []
    lab_ids: set[str] = set()
    samples_for_batch: set[str] = set()
    batch_product = ""
    cleaning_rows: list[tuple[str, dict[str, Any]]] = []
    schedule_rows: list[tuple[str, dict[str, Any]]] = []
    pat_rows: list[tuple[str, dict[str, Any]]] = []
    recipe_rows: list[tuple[str, dict[str, Any]]] = []
    lots_for_batch: set[str] = set()

    for source, rid, record in usable:
        if record.get("batch_id") == batch_id and record.get("product_id"):
            batch_product = str(record.get("product_id"))
        if source.endswith("material_genealogy.csv") and record.get("batch_id") == batch_id:
            genealogy.append((rid, record))
            if record.get("material_lot"):
                lots_for_batch.add(str(record.get("material_lot")))
        elif source.endswith("warehouse_movements.csv") and record.get("batch_id") == batch_id:
            movements.append((rid, record))
        elif source.endswith("lab_results.csv") and record.get("batch_id") == batch_id:
            lab_rows.append((rid, record))
            lab_ids.add(rid)
            if record.get("result_id"):
                lab_ids.add(str(record.get("result_id")))
        elif source.endswith("environmental_monitoring.csv") and record.get("batch_id") == batch_id:
            if record.get("sample_id"):
                samples_for_batch.add(str(record.get("sample_id")))
        elif source.endswith("cleaning_validation.csv"):
            cleaning_rows.append((rid, record))
        elif source.endswith("production_schedule.csv"):
            schedule_rows.append((rid, record))
        elif source.endswith("pat_models.csv"):
            pat_rows.append((rid, record))
        elif source.endswith("recipes.csv"):
            recipe_rows.append((rid, record))

    for source, rid, record in usable:
        if source.endswith("oos_investigations.csv") and str(record.get("result_id") or "") in lab_ids:
            _oos_contradiction(record, rid, source, contradictions)
        elif source.endswith("release_packets.csv") and record.get("batch_id") == batch_id:
            _release_gap(record, rid, source, gaps, applicable)
        elif source.endswith("microbiology_results.csv"):
            sample = str(record.get("sample_id") or "")
            if not samples_for_batch or sample in samples_for_batch:
                _organism_history(record, rid, source, contradictions)
        elif source.endswith("certificates_analysis.csv") and record.get("coa_id"):
            lot = str(record.get("material_lot") or "")
            if lot and lot in lots_for_batch:
                applicable.append(
                    {
                        "document_id": str(record.get("coa_id")),
                        "status": "present",
                        "source": source,
                        "record_id": rid,
                    }
                )

    _genealogy_contradictions(genealogy, movements, contradictions)
    _unit_abstentions(lab_rows, abstentions)
    _cleaning_gap(batch_id, batch_product, cleaning_rows, schedule_rows, gaps)
    _pat_desync(batch_product, pat_rows, recipe_rows, contradictions)

    return {
        "batch_id": batch_id,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "abstentions": abstentions,
        "applicable_documents": applicable,
        "readiness_state": compute_readiness(gaps, contradictions),
        "security_findings": findings,
    }


def _oos_contradiction(
    record: dict[str, Any],
    rid: str,
    source: str,
    contradictions: list[Contradiction],
) -> None:
    lims = record.get("lims_state")
    stats = record.get("stats_state")
    if lims and stats and lims != stats:
        contradictions.append(
            Contradiction(
                topic="oos_status",
                source=source,
                record_id=rid,
                values=[str(lims), str(stats)],
                notebook_state=record.get("notebook_state"),
                final_state=record.get("final_state"),
                evidence_refs=[rid],
            )
        )


def _release_gap(
    record: dict[str, Any],
    rid: str,
    source: str,
    gaps: list[Gap],
    applicable: list[dict[str, Any]],
) -> None:
    item = str(record.get("packet_item") or "")
    status = str(record.get("status") or "")
    subject = str(record.get("batch_id") or "")
    if status == "missing":
        gap_type = (
            "cmo_commitment_missing"
            if "CMO" in item.upper() or "audit commitment" in item.lower()
            else "missing_required_element"
        )
        gaps.append(
            Gap(
                gap_type=gap_type,
                subject_id=subject,
                packet_item=item,
                source=source,
                record_id=rid,
                evidence_refs=[rid],
            )
        )
        return
    applicable.append(
        {
            "document_id": item,
            "status": status,
            "source": source,
            "record_id": rid,
        }
    )


def _organism_history(
    record: dict[str, Any],
    rid: str,
    source: str,
    contradictions: list[Contradiction],
) -> None:
    initial = record.get("initial_id")
    corrected = record.get("corrected_id")
    if initial and corrected and initial != corrected:
        contradictions.append(
            Contradiction(
                topic="organism_identification",
                source=source,
                record_id=rid,
                values=[str(initial), str(corrected)],
                identifications=[
                    {
                        "identification": str(initial),
                        "time": record.get("initial_time") or record.get("time"),
                        "method": record.get("initial_method"),
                    },
                    {
                        "identification": str(corrected),
                        "time": record.get("correction_time"),
                        "method": record.get("correction_method") or record.get("method"),
                    },
                ],
                evidence_refs=[rid],
            )
        )


def _genealogy_contradictions(
    genealogy: list[tuple[str, dict[str, Any]]],
    movements: list[tuple[str, dict[str, Any]]],
    contradictions: list[Contradiction],
) -> None:
    by_lot: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for rid, record in genealogy:
        by_lot.setdefault(str(record.get("material_lot")), []).append((rid, record))
    for rid, record in movements:
        lot = str(record.get("material_lot"))
        for gene_id, gene in by_lot.get(lot) or []:
            left = str(gene.get("relation") or "")
            right = str(record.get("status") or "")
            if left in ABSENT_RELATIONS and right in PRESENT_MOVEMENT:
                contradictions.append(
                    Contradiction(
                        topic="genealogy",
                        source="data/material_genealogy.csv",
                        record_id=lot,
                        values=[left, right],
                        left={
                            "value": left,
                            "source": "data/material_genealogy.csv",
                            "record_id": gene_id,
                        },
                        right={
                            "value": right,
                            "source": "data/warehouse_movements.csv",
                            "record_id": rid,
                        },
                        evidence_refs=[gene_id, rid],
                    )
                )


def _unit_abstentions(
    lab_rows: list[tuple[str, dict[str, Any]]],
    abstentions: list[Abstention],
) -> None:
    for rid, record in lab_rows:
        observed_unit = str(record.get("unit") or "")
        spec = str(record.get("spec") or "")
        spec_unit = _spec_unit(spec)
        if not observed_unit or not spec_unit:
            continue
        left = Quantity(value=str(record.get("value") or ""), unit_code=observed_unit, unit_system="UCUM")
        right = Quantity(value=spec, unit_code=spec_unit, unit_system="UCUM")
        compared = compare_quantities(left, right)
        if not compared.comparable:
            abstentions.append(
                Abstention(
                    reason_code=compared.reason_code or "unit_mapping_unapproved",
                    subject_id=str(record.get("result_id") or rid),
                    observed_unit=observed_unit,
                    spec_unit=spec_unit,
                    evidence_refs=[rid],
                )
            )


def _in_validation_scope(product_id: str, scope: str, previous_product: str) -> bool:
    if not product_id:
        return True
    text = (scope or "").strip()
    token = text[: -len("only")].strip() if text.lower().endswith("only") else text
    allowed = {previous_product, token, token.replace(" ", "-")}
    if product_id in allowed:
        return True
    family = _product_family(product_id)
    return any(_product_family(item) == family and family for item in allowed if item)


def _cleaning_gap(
    batch_id: str,
    product_id: str,
    cleaning_rows: list[tuple[str, dict[str, Any]]],
    schedule_rows: list[tuple[str, dict[str, Any]]],
    gaps: list[Gap],
) -> None:
    if not product_id or not cleaning_rows:
        return
    for sched_id, schedule in schedule_rows:
        sequence = str(schedule.get("product_sequence") or "")
        parts = [part for part in sequence.split(">") if part]
        if product_id not in parts:
            continue
        equipment = schedule.get("equipment")
        for clean_id, clean in cleaning_rows:
            if equipment and clean.get("equipment") != equipment:
                continue
            previous = str(clean.get("previous_product") or "")
            scope = str(clean.get("validation_scope") or "")
            if _in_validation_scope(product_id, scope, previous):
                continue
            gaps.append(
                Gap(
                    gap_type="cleaning_boundary",
                    subject_id=batch_id,
                    boundary=scope,
                    preceding_product=previous,
                    product_id=product_id,
                    source="data/cleaning_validation.csv",
                    record_id=clean_id,
                    evidence_refs=[clean_id, sched_id],
                )
            )


def _pat_desync(
    product_id: str,
    pat_rows: list[tuple[str, dict[str, Any]]],
    recipe_rows: list[tuple[str, dict[str, Any]]],
    contradictions: list[Contradiction],
) -> None:
    if not product_id or not pat_rows or not recipe_rows:
        return
    family = _product_family(product_id)
    applicable = [
        (rid, row)
        for rid, row in recipe_rows
        if str(row.get("recipe_id") or "").startswith(family)
    ]
    if not applicable:
        applicable = list(recipe_rows)
    for recipe_id, recipe in applicable:
        recipe_version = str(recipe.get("pat_model_version") or "")
        for pat_id, pat in pat_rows:
            pat_version = str(pat.get("version") or "")
            if recipe_version and pat_version and recipe_version != pat_version:
                contradictions.append(
                    Contradiction(
                        topic="pat_recipe_version",
                        source="data/pat_models.csv",
                        record_id=str(pat.get("model_id") or pat_id),
                        values=[pat_version, recipe_version],
                        left={
                            "value": pat_version,
                            "source": "data/pat_models.csv",
                            "record_id": pat_id,
                        },
                        right={
                            "value": recipe_version,
                            "source": "data/recipes.csv",
                            "record_id": recipe_id,
                        },
                        evidence_refs=[pat_id, recipe_id],
                    )
                )
