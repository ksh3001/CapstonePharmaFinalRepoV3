"""Workflow C supply options. Classification types are constructed only here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.domain.batch import iter_records, iter_text_blobs
from packages.domain.evidence import EvidenceItem, build_evidence_item
from packages.domain.types import Abstention, Contradiction, Gap
from packages.ontology.instructions import (
    contains_embedded_instruction,
    facts_excluding_instructions,
    flatten_strings,
)
from packages.ontology.trust import trust_for_document

HOLD_STATUSES = frozenset({"quarantine", "quality_hold", "hold", "customs_hold"})
RELEASED = frozenset({"released"})
RECONCILE_CALLS = 0


def reset_reconcile_calls() -> None:
    global RECONCILE_CALLS
    RECONCILE_CALLS = 0


def infer_event_id(fixture: dict[str, Any], requested: str = "") -> str:
    if requested:
        return requested
    for _source, record in iter_records(fixture):
        if record.get("shipment_id"):
            return str(record["shipment_id"])
        if record.get("event_id"):
            return str(record["event_id"])
        if record.get("product"):
            return f"{record['product']}-shortage"
    return "UNSET"


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def _record_id(record: dict[str, Any], source: str, index: int) -> str:
    for key in (
        "shipment_id",
        "logger",
        "hold_id",
        "option_id",
        "cmo",
        "supplier",
        "serial",
        "lot",
        "export_id",
        "constraint",
        "channel",
        "use_case",
        "product",
    ):
        value = record.get(key)
        if value:
            extra = record.get("market") or record.get("document") or record.get("pallet") or record.get("window") or ""
            if extra and key in {"product", "logger", "cmo", "shipment_id", "serial"}:
                return f"{value}:{extra}"
            return str(value)
    return f"{source}:{index}"


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


def stale_checkpoint_abstention(subject_id: str, detail: str) -> Abstention:
    return Abstention(
        reason_code="checkpoint_stale",
        subject_id=subject_id,
        statement="Automatic resume is blocked; human confirmation is required before a fresh interrupt.",
        detail=detail,
    )


def reconcile_supply(
    fixture: dict[str, Any],
    *,
    event_id: str,
    as_of: str,
) -> dict[str, Any]:
    global RECONCILE_CALLS
    RECONCILE_CALLS += 1
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
            authority=str(record.get("authority") or "challenge-package"),
            effective_at=record.get("timestamp") or record.get("effective_date"),
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
        rid = _source_name(source)
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
            facts={"kind": "retrieved_document", "cited": True},
        )
        if isinstance(built, Abstention):
            abstentions.append(built)
            continue
        evidence.append(built)

    inventory: list[tuple[str, dict[str, Any]]] = []
    demand: list[tuple[str, dict[str, Any]]] = []
    constraints: list[dict[str, Any]] = []
    shipments: list[tuple[str, dict[str, Any]]] = []
    loggers: list[tuple[str, dict[str, Any]]] = []
    cmo_rows: list[tuple[str, dict[str, Any]]] = []
    substitutes: list[tuple[str, dict[str, Any]]] = []
    trade: list[tuple[str, dict[str, Any]]] = []
    serials: list[tuple[str, dict[str, Any]]] = []
    forensics: list[tuple[str, dict[str, Any]]] = []
    recalls: list[tuple[str, dict[str, Any]]] = []

    for source, rid, record in usable:
        name = _source_name(source)
        if name == "inventory.csv":
            inventory.append((rid, record))
        elif name == "demand_forecast.csv":
            demand.append((rid, record))
        elif name == "allocation_constraints.csv":
            constraints.append(
                {
                    "constraint_id": str(record.get("constraint") or rid),
                    "priority": str(record.get("priority") or ""),
                    "record_id": rid,
                }
            )
        elif name == "shipments.csv":
            shipments.append((rid, record))
        elif name == "temperature_loggers.csv":
            loggers.append((rid, record))
        elif name == "cmo_capacity.csv":
            cmo_rows.append((rid, record))
        elif name == "supplier_risks.csv":
            substitutes.append((rid, record))
        elif name == "trade_documents.csv":
            trade.append((rid, record))
        elif name == "serialisation_events.csv":
            serials.append((rid, record))
        elif name == "image_forensics.csv":
            forensics.append((rid, record))
        elif name == "recall_candidates.csv":
            recalls.append((rid, record))

    holds: list[dict[str, Any]] = []
    for rid, record in inventory:
        status = str(record.get("quality_status") or "").casefold()
        if status in HOLD_STATUSES:
            holds.append(
                {
                    "hold_id": rid,
                    "product": str(record.get("product") or ""),
                    "market": str(record.get("market") or ""),
                    "quality_status": str(record.get("quality_status") or ""),
                    "units": str(record.get("units") or ""),
                    "record_id": rid,
                }
            )
    for rid, record in shipments:
        status = str(record.get("status") or "").casefold()
        if status in HOLD_STATUSES:
            holds.append(
                {
                    "hold_id": f"SHIP-{rid}",
                    "shipment_id": str(record.get("shipment_id") or ""),
                    "lots": str(record.get("lots") or ""),
                    "quality_status": str(record.get("status") or ""),
                    "record_id": rid,
                }
            )

    hold_ids = [item["hold_id"] for item in holds]
    options: list[dict[str, Any]] = []
    for index, (_rid, record) in enumerate(demand, start=1):
        channel = str(record.get("channel") or f"channel-{index}")
        options.append(
            {
                "option_id": f"OPT-{channel}",
                "status": "draft",
                "channel": channel,
                "product": str(record.get("product") or ""),
                "demand_units_8w": str(record.get("units_8w") or ""),
                "uses_quality_cleared_positions_only": True,
                "released_positions": [
                    {
                        "product": str(row.get("product") or ""),
                        "market": str(row.get("market") or ""),
                        "units": str(row.get("units") or ""),
                    }
                    for _hid, row in inventory
                    if str(row.get("quality_status") or "").casefold() in RELEASED
                    and str(row.get("product") or "") == str(record.get("product") or "")
                ],
                "quality_holds": list(hold_ids),
                "approvals_required": ["supply_governance", "quality_reviewer"],
                "trade_off": (
                    f"Draft description of {channel} demand against quality-cleared positions. "
                    "Populations remain named; no ranking function is applied."
                ),
            }
        )
        if "compassionate" in channel:
            options[-1]["approvals_required"] = [
                "supply_governance",
                "quality_reviewer",
                "ethics_board",
            ]

    if not options and (inventory or shipments or loggers):
        options.append(
            {
                "option_id": "OPT-ASSESS",
                "status": "draft",
                "quality_holds": list(hold_ids),
                "approvals_required": ["supply_governance", "quality_reviewer"],
                "trade_off": "Draft assessment of shipment and logger evidence. Quality decides usability.",
            }
        )

    for rid, record in substitutes:
        qualified = str(record.get("alternate_qualified") or "").casefold()
        status = "unqualified" if qualified in {"no", "false", "unqualified"} else "qualified"
        options.append(
            {
                "option_id": f"OPT-SUB-{record.get('supplier') or rid}",
                "status": "draft",
                "material": str(record.get("material") or ""),
                "qualification_status": status,
                "change_control_required": True,
                "regulatory_variation_required": True,
                "presented_as_available_supply": False,
                "quality_holds": list(hold_ids),
                "approvals_required": ["supply_governance", "quality_reviewer"],
                "statement": (
                    "Unqualified substitute is described only; it is not released stock "
                    "and is not included in any released-position total."
                ),
            }
        )

    contradictions: list[Contradiction] = []
    by_logger: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for rid, record in loggers:
        by_logger.setdefault(str(record.get("logger") or rid), []).append((rid, record))
    for logger_id, rows in by_logger.items():
        pallets = {str(row.get("pallet") or "") for _rid, row in rows}
        temps = {str(row.get("temp_c") or "") for _rid, row in rows}
        if len(rows) > 1 and (len(pallets) > 1 or len(temps) > 1):
            contradictions.append(
                Contradiction(
                    topic="cold_chain",
                    source="data/temperature_loggers.csv",
                    record_id=rows[0][0],
                    values=sorted(temps),
                    pallets=sorted(pallets),
                    timestamps=[str(row.get("timestamp") or "") for _rid, row in rows],
                    timezones=[str(row.get("timezone") or "") for _rid, row in rows],
                    evidence_refs=[rid for rid, _row in rows],
                    statement="Logger and pallet positions are retained with source time and timezone; Quality decides usability.",
                )
            )

    gaps: list[Gap] = []
    for rid, record in serials:
        pallet = str(record.get("pallet") or "").strip()
        case = str(record.get("case") or "")
        event = str(record.get("event") or "").casefold()
        if event == "commission" and not pallet:
            gaps.append(
                Gap(
                    gap_type="aggregation_gap",
                    subject_id=str(record.get("serial") or rid),
                    expected_parent="pallet",
                    case=case,
                    statement=(
                        f"Serial {record.get('serial')} case {case} has no aggregation record to a pallet. "
                        "No parent is inferred."
                    ),
                    evidence_refs=[rid],
                )
            )

    for rid, record in cmo_rows:
        try:
            capacity = int(str(record.get("capacity_batches") or "0"))
            promised = int(str(record.get("promised_NTG") or "0")) + int(
                str(record.get("promised_other_sponsor") or "0")
            )
        except ValueError:
            continue
        if promised > capacity:
            findings.append(
                {
                    "finding_id": f"F-CMO-{rid}",
                    "kind": "capacity_conflict",
                    "statement": (
                        f"CMO {record.get('cmo')} window {record.get('window')} has committed "
                        f"{record.get('promised_NTG')} and {record.get('promised_other_sponsor')} "
                        f"against capacity {record.get('capacity_batches')}. Contested capacity "
                        "is not treated as a released position."
                    ),
                    "evidence_refs": [rid],
                    "capacity_batches": str(record.get("capacity_batches") or ""),
                    "promised_NTG": str(record.get("promised_NTG") or ""),
                    "promised_other_sponsor": str(record.get("promised_other_sponsor") or ""),
                }
            )
            constraints.append(
                {
                    "constraint_id": f"cmo-overcommit-{rid}",
                    "priority": "hard",
                    "record_id": rid,
                    "contested": True,
                }
            )

    by_shipment: dict[str, list[tuple[str, dict[str, Any]]] ] = {}
    for rid, record in trade:
        by_shipment.setdefault(str(record.get("shipment_id") or rid), []).append((rid, record))
    for shipment, rows in by_shipment.items():
        descriptions = {str(row.get("description") or "") for _rid, row in rows}
        documents = {str(row.get("document") or "") for _rid, row in rows}
        if len(descriptions) > 1:
            findings.append(
                {
                    "finding_id": f"F-CUSTOMS-{shipment}",
                    "kind": "customs_mismatch",
                    "statement": (
                        f"Consignment {shipment} descriptions differ across {sorted(documents)}: "
                        f"{sorted(descriptions)}. Differing field: description. "
                        "Positions are retained with their issuing documents."
                    ),
                    "fields": ["description"],
                    "evidence_refs": [rid for rid, _row in rows],
                }
            )

    for rid, record in forensics:
        findings.append(
            {
                "finding_id": f"F-SUSPECT-{rid}",
                "kind": "counterfeit_suspicion",
                "statement": (
                    f"Indicators recorded for {record.get('study_id') or rid}: "
                    f"similarity_to={record.get('similarity_to')} "
                    f"note={record.get('metadata_note')}. Escalate to quality_reviewer."
                ),
                "escalation": "quality_reviewer",
                "evidence_refs": [rid],
            }
        )

    if recalls:
        abstentions.append(
            Abstention(
                reason_code="recall_scope_unbounded",
                subject_id=event_id,
                statement="Recall-scope completeness is not asserted from candidate lots.",
                evidence_refs=[rid for rid, _row in recalls],
            )
        )

    approvals = sorted(
        {
            item
            for option in options
            for item in option.get("approvals_required") or ["supply_governance"]
        }
    )
    if not approvals and options:
        approvals = ["supply_governance"]

    return {
        "event_id": event_id,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "abstentions": abstentions,
        "options": sorted(options, key=lambda item: str(item.get("option_id") or "")),
        "constraints": sorted(constraints, key=lambda item: str(item.get("constraint_id") or "")),
        "approvals_required": approvals,
        "quality_holds": sorted(holds, key=lambda item: str(item.get("hold_id") or "")),
        "security_findings": findings,
    }
