"""Document authority, supersession, missing references, back-entry and integrity concerns."""

from __future__ import annotations

from typing import Any

from packages.domain.batch import iter_records
from packages.domain.types import Gap
from packages.ontology.temporal import back_entry
from packages.ontology.trust import AUTHORITY_STATUSES_UNUSABLE, can_ground_assertion, trust_for_document

_UNUSABLE = AUTHORITY_STATUSES_UNUSABLE | frozenset({"untrusted"})


def _as_of_date(value: str) -> str:
    text = (value or "").strip()
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def _filename(source: str) -> str:
    return str(source).replace("\\", "/").rsplit("/", 1)[-1]


def _is_catalog_row(source: str, record: dict[str, Any]) -> bool:
    if _filename(source) == "knowledge_catalog.csv":
        return True
    return bool(record.get("doc_id") and record.get("status") and (record.get("file") or record.get("authority")))


def reconcile_authority(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    gaps: list[Gap] = []
    catalog: list[dict[str, Any]] = []
    catalog_ids: set[str] = set()
    back_entries: list[dict[str, Any]] = []
    as_of_day = _as_of_date(as_of)

    rows = list(iter_records(fixture))
    for source, record in rows:
        if not _is_catalog_row(source, record):
            continue
        catalog.append(record)
        for key in ("doc_id", "document_id", "file"):
            value = str(record.get(key) or "").strip()
            if value:
                catalog_ids.add(value)

    for source, record in rows:
        name = _filename(source)
        event_time = str(record.get("event_time") or "")
        recorded_at = str(record.get("recorded_at") or "")
        if event_time and recorded_at and event_time != recorded_at:
            flag = back_entry(event_time, recorded_at)
            subject = str(
                record.get("record_id")
                or record.get("result_id")
                or record.get("doc_id")
                or record.get("id")
                or source
            )
            back_entries.append(
                {
                    "flagged": flag.flagged,
                    "magnitude": flag.magnitude,
                    "event_time": flag.event_time,
                    "recorded_at": flag.recorded_at,
                    "subject_id": subject,
                }
            )
        referenced = str(record.get("references") or record.get("referenced_document") or "").strip()
        if referenced and referenced not in catalog_ids:
            gaps.append(
                Gap(
                    gap_type="referenced_missing",
                    subject_id=referenced,
                    statement=f"Referenced document {referenced} is missing; silence is not compliance.",
                )
            )
        indicator = str(record.get("manipulation") or record.get("image_concern") or "")
        if name in {"image_forensics.csv", "preclinical_studies.csv"}:
            indicator = indicator or str(record.get("concern") or "")
        if indicator and indicator.casefold() not in {"", "none", "cleared"}:
            subject = str(record.get("record_id") or record.get("image_id") or source)
            findings.append(
                {
                    "finding_id": f"F-MANIP-{subject}",
                    "statement": (
                        f"Manipulation concern {indicator} is raised for human review. "
                        "Affected facts are reduced_integrity. A later record does not clear the concern."
                    ),
                    "evidence_refs": [subject],
                    "severity": "blocking",
                }
            )
        has_change = "change_date" in record or "changed_at" in record
        if has_change or name in {"change_controls.csv", "vendor_releases.csv"}:
            change_date = str(record.get("change_date") or record.get("changed_at") or "")
            approval = str(record.get("approval_date") or record.get("approved_at") or "")
            approval_ref = str(record.get("approval_ref") or record.get("change_control") or "")
            missing_ref = approval_ref.casefold() in {"", "missing", "none", "n/a"}
            retrospective = bool(change_date and approval and approval > change_date)
            if missing_ref or retrospective:
                subject = str(record.get("change_id") or record.get("record_id") or source)
                findings.append(
                    {
                        "finding_id": f"F-CC-BYPASS-{subject}",
                        "statement": (
                            "Change occurred outside change control. "
                            "Retrospective approval is reported as retrospective and does not clear the integrity finding."
                        ),
                        "evidence_refs": [subject],
                        "severity": "blocking",
                    }
                )

    supersessions: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in catalog:
        doc_id = str(row.get("doc_id") or row.get("document_id") or "")
        status = str(row.get("status") or "").casefold()
        effective = _as_of_date(str(row.get("effective") or row.get("effective_date") or ""))
        file_name = str(row.get("file") or doc_id)
        trust = trust_for_document(status=status or "effective", hash_ok=True, contains_instruction=False)
        if status == "superseded":
            pass
        elif status in _UNUSABLE or not can_ground_assertion(trust):
            excluded.append({"document_id": doc_id or file_name, "reason": f"status_{status or 'unknown'}_not_authority"})
            findings.append(
                {
                    "finding_id": f"F-AUTH-{doc_id or file_name}",
                    "statement": (
                        f"Document {doc_id or file_name} has status {status or 'unknown'} and is not used as authority."
                    ),
                    "evidence_refs": [doc_id or file_name],
                }
            )
        if effective and as_of_day and effective > as_of_day:
            excluded.append({"document_id": doc_id or file_name, "reason": "effective_after_as_of"})
            findings.append(
                {
                    "finding_id": f"F-AUTH-FUTURE-{doc_id or file_name}",
                    "statement": (
                        f"Document {doc_id or file_name} is effective {effective}, after as_of {as_of_day}, "
                        "and is excluded from authority."
                    ),
                    "evidence_refs": [doc_id or file_name],
                }
            )
        supersedes = str(row.get("supersedes") or "").strip()
        if supersedes:
            supersessions.append(
                {
                    "superseding": file_name or doc_id,
                    "superseded": supersedes,
                    "both_retained": True,
                }
            )

    return {
        "findings": findings,
        "gaps": gaps,
        "review": {
            "supersessions": supersessions,
            "excluded_from_authority": excluded,
            "back_entry": back_entries,
        },
    }


def apply_authority_to_evidence(evidence: list[dict[str, Any]], result: dict[str, Any]) -> None:
    reduced: set[str] = set()
    for finding in result.get("findings") or []:
        finding_id = str(finding.get("finding_id") or "")
        if finding_id.startswith("F-MANIP-") or finding_id.startswith("F-CC-"):
            reduced.update(str(item) for item in finding.get("evidence_refs") or [])
    back = {
        str(item.get("subject_id") or ""): item for item in (result.get("review") or {}).get("back_entry") or []
    }
    for item in evidence:
        facts = dict(item.get("facts") or {})
        record_id = str(item.get("record_id") or "")
        aliases = {
            record_id,
            str(facts.get("record_id") or ""),
            str(facts.get("image_id") or ""),
            str(facts.get("change_id") or ""),
            str(facts.get("doc_id") or ""),
        }
        if reduced & aliases:
            facts["trust_status"] = "reduced_integrity"
        payload = back.get(record_id) or back.get(str(facts.get("record_id") or ""))
        if payload is None:
            event_time = str(facts.get("event_time") or "")
            recorded_at = str(facts.get("recorded_at") or "")
            if event_time and recorded_at and event_time != recorded_at:
                flag = back_entry(event_time, recorded_at)
                payload = {
                    "flagged": flag.flagged,
                    "magnitude": flag.magnitude,
                    "event_time": flag.event_time,
                    "recorded_at": flag.recorded_at,
                }
        if payload:
            facts["back_entry"] = {
                "flagged": payload.get("flagged"),
                "magnitude": payload.get("magnitude"),
                "event_time": payload.get("event_time"),
                "recorded_at": payload.get("recorded_at"),
            }
        item["facts"] = facts
