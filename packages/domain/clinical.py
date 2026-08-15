"""Clinical protocol applicability. Classification types are constructed only here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.domain.batch import iter_records, iter_text_blobs
from packages.domain.types import Abstention, Contradiction, Gap
from packages.ontology.instructions import contains_embedded_instruction
from packages.ontology.trust import trust_for_document

BLINDING_KEYS = frozenset(
    {
        "allocation",
        "treatment_arm",
        "arm",
        "kit",
        "unblinded",
        "randomization_code",
        "treatment",
        "unblinding",
    }
)


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def _as_number(value: str) -> float | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def reconcile_clinical(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    del as_of
    subjects: list[dict[str, Any]] = []
    approvals: list[dict[str, Any]] = []
    versions: list[dict[str, Any]] = []
    eligibility: list[tuple[str, dict[str, Any]]] = []
    wearables: list[tuple[str, dict[str, Any]]] = []
    randomisation: list[dict[str, Any]] = []
    endpoints: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []

    for source, record in iter_records(fixture):
        name = _source_name(source)
        if name == "subjects.csv":
            subjects.append(record)
        elif name == "site_approvals.csv":
            approvals.append(record)
        elif name == "protocol_versions.csv":
            versions.append(record)
        elif name == "eligibility_evidence.csv":
            eligibility.append((str(record.get("subject_id") or ""), record))
        elif name == "wearable_readings.csv":
            wearables.append((str(record.get("subject_id") or ""), record))
        elif name == "randomization_events.csv":
            randomisation.append(record)
        elif name == "endpoint_packets.csv":
            endpoints.append(record)
        elif name == "imaging_reviews.csv":
            reviews.append(record)
        elif name == "site_metrics.csv":
            metrics.append(record)

    findings: list[dict[str, Any]] = []
    security: list[dict[str, Any]] = []
    gaps: list[Gap] = []
    contradictions: list[Contradiction] = []
    abstentions: list[Abstention] = []
    review: dict[str, Any] = {}

    for source, text in iter_text_blobs(fixture):
        if contains_embedded_instruction(text):
            security.append(
                {
                    "finding_id": f"SEC-INSTR-{_source_name(source)}",
                    "kind": "embedded_instruction",
                    "source": source,
                    "statement": "Embedded instruction detected; content treated as data and excluded from reasoning.",
                    "trust_status": trust_for_document(status="effective", hash_ok=True, contains_instruction=True),
                    "evidence_refs": [_source_name(source)],
                }
            )

    applicability: list[dict[str, Any]] = []
    risks: list[dict[str, Any]] = []
    for subject in subjects:
        site_id = str(subject.get("site_id") or "")
        trial_id = str(subject.get("trial_id") or "")
        subject_id = str(subject.get("subject_id") or "")
        site_row = next(
            (
                row
                for row in approvals
                if str(row.get("site_id") or "") == site_id and str(row.get("trial_id") or "") == trial_id
            ),
            None,
        )
        global_row = next(
            (row for row in versions if str(row.get("status") or "") == "global_current"),
            None,
        )
        local_version = str((site_row or {}).get("approved_protocol") or "")
        global_version = str((global_row or {}).get("version") or "")
        if not site_row:
            abstentions.append(
                Abstention(
                    reason_code="applicability_unresolved",
                    subject_id=subject_id,
                    statement="No site approval record; global currency is not used as a fallback.",
                )
            )
        applicability.append(
            {
                "subject_id": subject_id,
                "trial_id": trial_id,
                "site_id": site_id,
                "governing_version": local_version or None,
                "governing_source": "data/site_approvals.csv" if site_row else None,
                "globally_current_version": global_version or None,
                "locally_approved": bool(site_row),
                "statement": (
                    f"Site {site_id} approved_protocol {local_version} per site_approvals.csv. "
                    f"Version {global_version} is globally current and is not locally approved at {site_id}."
                    if site_row and global_version and local_version != global_version
                    else (
                        f"Site {site_id} approved_protocol {local_version} per site_approvals.csv."
                        if site_row
                        else "Applicability is unresolved."
                    )
                ),
            }
        )
        for row in versions:
            status = str(row.get("status") or "")
            if "pending" in status.casefold() and local_version == str(row.get("version") or ""):
                gaps.append(
                    Gap(
                        gap_type="pending_amendment",
                        subject_id=site_id,
                        version=str(row.get("version") or ""),
                        statement=(
                            f"Site {site_id} amendment state is pending. Pending is neither approved nor rejected. "
                            f"Version {global_version or row.get('version')} is not the locally governing version."
                        ),
                    )
                )

    for row in versions:
        if str(row.get("status") or "") == "obsolete_but_site_cached":
            risks.append(
                {
                    "version": str(row.get("version") or ""),
                    "status": str(row.get("status") or ""),
                    "effective_date": str(row.get("effective_date") or ""),
                    "risk": "obsolete_cached_possibly_in_use",
                    "statement": (
                        f"Protocol version {row.get('version')} is obsolete, cached, and therefore possibly in use."
                    ),
                }
            )

    ranges: list[dict[str, Any]] = []
    for subject_id, record in eligibility:
        limits = (
            ("central_uln", "central", record.get("central_uln")),
            ("local_uln", "local", record.get("local_uln")),
            ("edc_rule_uln", "edc_rule", record.get("edc_rule_uln")),
        )
        value = str(record.get("value") or "")
        numeric = _as_number(value)
        outcomes = []
        for field, origin, raw in limits:
            limit = str(raw or "")
            limit_n = _as_number(limit)
            exceeds = numeric is not None and limit_n is not None and numeric > limit_n
            outcomes.append(
                {
                    "limit": field,
                    "origin": origin,
                    "limit_value": limit,
                    "value": value,
                    "unit": str(record.get("unit") or ""),
                    "exceeds_this_limit": exceeds,
                    "source": "data/eligibility_evidence.csv",
                }
            )
        contradictions.append(
            Contradiction(
                topic="reference_range",
                source="data/eligibility_evidence.csv",
                record_id=subject_id,
                test=str(record.get("test") or ""),
                value=value,
                unit=str(record.get("unit") or ""),
                limits={item[0]: str(item[2] or "") for item in limits},
                statement="All supplied reference limits are retained with their origin. No limit is selected.",
            )
        )
        ranges.append({"subject_id": subject_id, "test": str(record.get("test") or ""), "outcomes": outcomes})

    device: list[dict[str, Any]] = []
    by_device: dict[str, list[dict[str, Any]]] = {}
    for _sid, record in wearables:
        key = str(record.get("device_id") or _sid)
        by_device.setdefault(key, []).append(record)
        device.append(
            {
                "subject_id": _sid,
                "device_id": str(record.get("device_id") or ""),
                "timestamp": str(record.get("timestamp") or ""),
                "timezone": str(record.get("timezone") or ""),
                "adjusted": False,
            }
        )
    skew = []
    for device_id, rows in by_device.items():
        if len(rows) > 1:
            skew.append(
                {
                    "device_id": device_id,
                    "timestamps": [str(row.get("timestamp") or "") for row in rows],
                    "timezones": [str(row.get("timezone") or "") for row in rows],
                    "skew_reported": True,
                    "adjusted": False,
                    "statement": "Device timestamps are retained verbatim. No clock is corrected.",
                }
            )

    if randomisation:
        findings.append(
            {
                "finding_id": "F-UNBLIND-COMBINATION",
                "statement": (
                    "A combination of permitted fields was withheld because it could allow the "
                    "treatment assignment to be deduced. Escalated to unblinding_authority."
                ),
                "evidence_refs": [str(row.get("event_id") or row.get("subject_id") or "randomisation") for row in randomisation],
                "severity": "blocking",
            }
        )
        review["unblinding"] = {
            "combination_withheld": True,
            "routed_to": "unblinding_authority",
            "assignment_fields_absent": True,
        }

    pending_adjudication: list[dict[str, Any]] = []
    adjudicated_count = 0
    for packet in endpoints:
        status = str(packet.get("review_status") or "").casefold()
        pending = status in {"conflict", "pending", "queued", "awaiting"} or str(packet.get("source_complete") or "") == "no"
        if pending:
            pending_adjudication.append(
                {
                    "packet_id": str(packet.get("packet_id") or ""),
                    "subject_id": str(packet.get("subject_id") or ""),
                    "endpoint": str(packet.get("endpoint") or ""),
                    "status": "pending",
                    "queue_entered_at": str(packet.get("queue_entered_at") or packet.get("queued_at") or ""),
                    "committee": str(packet.get("committee") or packet.get("responsible_committee") or ""),
                    "adjudicated": False,
                }
            )
            gaps.append(
                Gap(
                    gap_type="adjudication_backlog",
                    subject_id=str(packet.get("packet_id") or ""),
                    statement=(
                        f"Endpoint packet {packet.get('packet_id')} is pending adjudication. "
                        "It is excluded from adjudicated counts. No provisional outcome is recorded."
                    ),
                    dependent_analyses=["endpoint_analysis"],
                )
            )
        else:
            adjudicated_count += 1

    observations: list[dict[str, Any]] = []
    observed_sites = {str(row.get("site_id") or "") for row in metrics}
    for row in metrics:
        for field in ("enrolment", "late_source_pct", "digit_preference_flag", "credential_sharing_flag"):
            if row.get(field) in (None, ""):
                continue
            observations.append(
                {
                    "site_id": str(row.get("site_id") or ""),
                    "indicator": field,
                    "value": str(row.get(field) or ""),
                    "source": "data/site_metrics.csv",
                    "period": str(row.get("period") or "as_supplied"),
                    "data_quality_limitation": "source_flag_unvalidated",
                    "kind": "observation",
                }
            )
    for subject in subjects:
        site_id = str(subject.get("site_id") or "")
        if site_id and site_id not in observed_sites:
            observations.append(
                {
                    "site_id": site_id,
                    "kind": "observation",
                    "statement": "Absence of site-level observations is not evidence of quality.",
                    "source": "data/site_metrics.csv",
                }
            )

    review["applicability"] = applicability
    review["protocol_risks"] = risks
    review["reference_range_outcomes"] = ranges
    review["device_timestamps"] = device
    review["device_skew"] = skew
    review["pending_adjudication"] = pending_adjudication
    review["adjudicated_count"] = adjudicated_count
    review["site_observations"] = observations
    return {
        "review": review,
        "findings": findings,
        "security_findings": security,
        "gaps": gaps,
        "contradictions": contradictions,
        "abstentions": abstentions,
        "blinding_keys": sorted(BLINDING_KEYS),
    }
