"""Interface contract reconciliation. Classification types live only here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.domain.batch import iter_records
from packages.domain.types import Abstention, Contradiction, Gap
from packages.ontology.mappings import is_approved_status
from packages.ontology.temporal import preserve_time
from packages.ontology.ucum import ucum_valid
from packages.ontology.units import REASON_UNAPPROVED, compare_quantities
from packages.ontology.types import Quantity

V1_UNIT = "unit"
V2_UNIT = "ucum_code"
V1_STATUS = "status"
V2_STATUS = "lifecycleState"


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def reconcile_interfaces(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    del as_of
    contracts: list[dict[str, Any]] = []
    mappings: list[tuple[str, dict[str, Any]]] = []
    results: list[tuple[str, dict[str, Any]]] = []
    for source, record in iter_records(fixture):
        name = _source_name(source)
        if name == "api_contract_versions.csv":
            contracts.append(record)
        elif name == "interface_mappings.csv":
            rid = str(record.get("interface") or source)
            mappings.append((rid, record))
        elif name in {"lab_results.csv", "lims_results.csv"} or record.get("result_id") or record.get("resultId"):
            rid = str(record.get("result_id") or record.get("resultId") or record.get("record_id") or source)
            results.append((rid, record))

    abstentions: list[Abstention] = []
    gaps: list[Gap] = []
    findings: list[dict[str, Any]] = []
    contradictions: list[Contradiction] = []
    presented: list[dict[str, Any]] = []

    for rid, record in mappings:
        left = Quantity(value="", unit_code=str(record.get("source_unit") or ""), unit_system="source")
        right = Quantity(value="", unit_code=str(record.get("target_unit") or ""), unit_system="source")
        comparison = compare_quantities(left, right, mappings=(record,))
        presented.append(
            {
                "interface": rid,
                "source_unit": str(record.get("source_unit") or ""),
                "target_unit": str(record.get("target_unit") or ""),
                "source_record": rid,
                "approved": str(record.get("approved") or ""),
                "conversion_rule": str(record.get("conversion_rule") or ""),
            }
        )
        if not is_approved_status(str(record.get("approved") or "")):
            abstentions.append(
                Abstention(
                    reason_code=REASON_UNAPPROVED,
                    subject_id=rid,
                    mapping_id=rid,
                    conversion_rule=str(record.get("conversion_rule") or ""),
                    statement=(
                        f"Mapping {rid} is not approved. "
                        f"{record.get('source_unit')} and {record.get('target_unit')} "
                        "are retained in source units. No converted value is emitted."
                    ),
                )
            )
        del comparison

    by_api: dict[str, list[dict[str, Any]]] = {}
    for row in contracts:
        by_api.setdefault(str(row.get("api") or ""), []).append(row)
        presented.append(
            {
                "api": str(row.get("api") or ""),
                "contract_version": str(row.get("version") or ""),
                "unit_field": str(row.get("unit_field") or ""),
                "status_field": str(row.get("status_field") or ""),
                "date_semantics": str(row.get("date_semantics") or ""),
            }
        )

    for rid, record in results:
        version = str(record.get("contract_version") or record.get("version") or "").strip()
        if not version:
            gaps.append(
                Gap(
                    gap_type="contract_version_missing",
                    subject_id=rid,
                    statement="Contract version is not declared; version is not inferred from field shape.",
                )
            )
            presented.append({"record_id": rid, "contract_version": None, "retained": True})
            continue
        unit = record.get("unit")
        ucum = record.get("ucum_code") or record.get("ucumCode")
        if version == "v2" and ucum is not None and not ucum_valid(str(ucum)):
            findings.append(
                {
                    "finding_id": f"F-UCUM-{rid}",
                    "statement": f"UCUM code {ucum!r} is invalid. The record is retained uncorrected.",
                    "evidence_refs": [rid],
                    "severity": "concern",
                }
            )
        if version == "v1" and unit is not None:
            presented.append(
                {
                    "record_id": rid,
                    "contract_version": "v1",
                    "unit_field": V1_UNIT,
                    "unit": str(unit),
                    "status_field": V1_STATUS,
                    "status": str(record.get("status") or ""),
                    "value": str(record.get("value") or record.get("numericValue") or ""),
                }
            )
        elif version == "v2":
            presented.append(
                {
                    "record_id": rid,
                    "contract_version": "v2",
                    "unit_field": V2_UNIT,
                    "ucum_code": str(ucum or ""),
                    "status_field": V2_STATUS,
                    "lifecycleState": str(record.get("lifecycleState") or record.get("status") or ""),
                    "value": str(record.get("numericValue") or record.get("value") or ""),
                }
            )
        else:
            presented.append({"record_id": rid, "contract_version": version, "retained": True})
        if version == "v1" and ucum:
            findings.append(
                {
                    "finding_id": f"F-UNIT-FIELD-{rid}",
                    "statement": "v1 free-text unit is distinct from ucum_code and is not emitted as a UCUM code.",
                    "evidence_refs": [rid],
                    "severity": "info",
                }
            )

    v1_status = {str(row.get("status") or "") for _rid, row in results if str(row.get("contract_version") or "") == "v1"}
    v2_status = {
        str(row.get("lifecycleState") or row.get("status") or "")
        for _rid, row in results
        if str(row.get("contract_version") or "") == "v2"
    }
    if v1_status and v2_status and v1_status != v2_status:
        contradictions.append(
            Contradiction(
                topic="status_vocabulary",
                source="data/api_contract_versions.csv",
                record_id="LIMS result",
                v1_status=sorted(v1_status),
                v2_lifecycleState=sorted(v2_status),
                statement="Status values are presented per contract version. No cross-version equivalence is asserted.",
            )
        )

    dates: list[dict[str, Any]] = []
    for row in contracts:
        if "variable" in str(row.get("date_semantics") or "").casefold():
            for _rid, record in results:
                raw = str(record.get("date") or record.get("observedAt") or record.get("awareness_date") or "")
                if not raw:
                    continue
                point = preserve_time(raw, basis="event_time")
                dates.append(
                    {
                        "record_id": _rid,
                        "value": point.value,
                        "precision": point.precision,
                        "timezone_known": point.timezone_known,
                    }
                )

    contract_versions = sorted(
        {str(row.get("version") or "") for row in contracts if row.get("version")}
    )
    return {
        "abstentions": abstentions,
        "gaps": gaps,
        "findings": findings,
        "contradictions": contradictions,
        "presented": presented,
        "contract_versions": contract_versions,
        "dates": dates,
    }
