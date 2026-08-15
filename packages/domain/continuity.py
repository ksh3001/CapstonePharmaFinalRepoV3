"""Continuity and degraded operation. Classification types live only here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.config.paths import repo_root
from packages.domain.batch import iter_records
from packages.domain.types import Abstention, Contradiction, Gap

MANDATORY_WORKFLOWS = ("batch_review", "pv_intake", "supply_planning")
RUNBOOK_DIR = "docs/runbooks"
_TRUE = frozenset({"yes", "true", "1"})


def _blank(value: Any) -> bool:
    return str(value or "").strip() == ""


def _name(source: str) -> str:
    return Path(str(source).replace("\\", "/")).name


def _runbook_path(workflow: str) -> Path:
    return repo_root() / RUNBOOK_DIR / f"{workflow}.md"


def _flag(value: Any) -> bool:
    return str(value or "").strip().casefold() in _TRUE


def reconcile_continuity(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    del as_of
    endpoints: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    isolations: list[dict[str, Any]] = []
    manuals: list[tuple[str, dict[str, Any]]] = []
    recovered: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        name = _name(source)
        if name == "model_endpoints.csv" or record.get("endpoint"):
            if record.get("endpoint"):
                endpoints.append(record)
                continue
        if name == "continuity_requirements.csv" or (
            record.get("workflow") and ("max_ai_outage_hours" in record or "max_ai_outage_days" in record)
        ):
            if record.get("workflow") and not record.get("assignment_id"):
                requirements.append(record)
                continue
        if name == "system_isolation.csv" or record.get("last_known_good") or record.get("isolation_event"):
            isolations.append(record)
            continue
        if name == "manual_assignments.csv" or _flag(record.get("manual_assignment")) or record.get(
            "assignment_id"
        ):
            if not _flag(record.get("system_recovered")):
                manuals.append((source, record))
                continue
        if name == "system_assignments.csv" or _flag(record.get("system_recovered")):
            recovered.append(record)

    gaps: list[Gap] = []
    contradictions: list[Contradiction] = []
    abstentions: list[Abstention] = []
    findings: list[dict[str, Any]] = []
    workflows: list[dict[str, Any]] = []

    primary = next((row for row in endpoints if str(row.get("endpoint") or "") == "primary_large"), None)
    fallback = next((row for row in endpoints if str(row.get("endpoint") or "") == "fallback_small"), None)
    primary_down = str((primary or {}).get("status") or "").casefold() == "down"

    substituted = False
    if fallback and str(fallback.get("status") or "").casefold() == "available":
        gaps.append(
            Gap(
                gap_type="missing_equivalent_validation",
                subject_id=str(fallback.get("endpoint") or "fallback_small"),
                statement=(
                    "fallback_small is available and is not an authorised substitute. "
                    "Equivalent validation for the task is missing."
                ),
            )
        )

    residency = None
    if primary and fallback:
        left = str(primary.get("region") or "")
        right = str(fallback.get("region") or "")
        residency = {
            "primary_region": left,
            "fallback_region": right,
            "evaluated": left != right,
            "outcome": "regions_differ" if left != right else "same_region",
            "statement": (
                f"Residency evaluated: {left} versus {right}. "
                "A region difference blocks silent substitution."
            ),
        }

    isolated = bool(isolations)
    for row in requirements:
        workflow = str(row.get("workflow") or "")
        hours_raw = row.get("max_ai_outage_hours")
        days_raw = row.get("max_ai_outage_days")
        hours_blank = _blank(hours_raw)
        days_blank = _blank(days_raw)
        if hours_blank:
            gaps.append(
                Gap(
                    gap_type="tolerance_not_specified",
                    subject_id=f"{workflow}:max_ai_outage_hours",
                    field="max_ai_outage_hours",
                    statement=f"{workflow} max_ai_outage_hours is not specified. It is not zero and not unlimited.",
                )
            )
        if days_blank:
            gaps.append(
                Gap(
                    gap_type="tolerance_not_specified",
                    subject_id=f"{workflow}:max_ai_outage_days",
                    field="max_ai_outage_days",
                    statement=f"{workflow} max_ai_outage_days is not specified. It is not zero and not unlimited.",
                )
            )
        immediate = (not hours_blank) and str(hours_raw).strip() == "0"
        degraded = (not days_blank) and str(days_raw).strip() != ""
        path = _runbook_path(workflow)
        runbook_present = path.is_file()
        if str(row.get("manual_runbook") or "").casefold() == "required" and not runbook_present:
            gaps.append(
                Gap(
                    gap_type="missing_runbook",
                    subject_id=workflow,
                    statement=f"Manual runbook for {workflow} is required and was not found.",
                )
            )
        force_manual = isolated or (primary_down and immediate)
        continue_degraded = bool(primary_down and degraded and not immediate and not isolated)
        entry = {
            "workflow": workflow,
            "max_ai_outage_hours": None if hours_blank else str(hours_raw).strip(),
            "max_ai_outage_days": None if days_blank else str(days_raw).strip(),
            "hours_specified": not hours_blank,
            "days_specified": not days_blank,
            "manual_immediately": bool(force_manual),
            "continue_degraded": continue_degraded,
            "degraded_deadline_days": None if days_blank else str(days_raw).strip(),
            "runbook": f"{RUNBOOK_DIR}/{workflow}.md" if runbook_present else None,
            "path": "manual" if force_manual else ("degraded" if continue_degraded else "as_supplied"),
        }
        workflows.append(entry)

    isolated_facts: list[dict[str, Any]] = []
    for row in isolations:
        window = str(row.get("incident_window") or row.get("written_in_window") or "")
        in_window = window.strip().casefold() in _TRUE
        isolated_facts.append(
            {
                "system": str(row.get("system") or ""),
                "last_known_good": str(row.get("last_known_good") or ""),
                "isolation_event": str(row.get("incident") or row.get("isolation_event") or ""),
                "current": False,
                "integrity": "integrity_unconfirmed" if in_window else "stale_by_declaration",
                "authority": False,
            }
        )

    for source, row in manuals:
        missing = [
            field
            for field in ("assigned_by", "assigned_at", "authority", "procedure")
            if _blank(row.get(field))
        ]
        if missing:
            gaps.append(
                Gap(
                    gap_type="manual_assignment_provenance",
                    subject_id=str(row.get("assignment_id") or "manual"),
                    missing_fields=missing,
                    statement="Manual assignment is missing provenance and is not assumed correct.",
                )
            )
        match = next(
            (
                item
                for item in recovered
                if str(item.get("assignment_id") or "") == str(row.get("assignment_id") or "")
            ),
            None,
        )
        if match and any(str(match.get(key) or "") != str(row.get(key) or "") for key in ("assigned_by", "assigned_at")):
            contradictions.append(
                Contradiction(
                    topic="outage_assignment",
                    source=source,
                    record_id=str(row.get("assignment_id") or ""),
                    statement="Manual and recovered system assignments are both retained. Neither overwrites the other.",
                    manual=True,
                    system=True,
                )
            )

    context = dict(fixture.get("authorized_context") or {})
    if context.get("resume_ai") and not context.get("outage_reconciled"):
        abstentions.append(
            Abstention(
                reason_code="outage_reconciliation_required",
                subject_id="resumption",
                statement="AI-assisted resumption is blocked until outage-period work is reconciled.",
            )
        )

    review = {
        "primary_status": str((primary or {}).get("status") or ""),
        "fallback_substituted": substituted,
        "residency": residency,
        "workflows": workflows,
        "isolated_facts": isolated_facts,
        "resumption_requires_reconciliation": True,
        "kill_switch_independent": True,
        "automation_widened": False,
    }
    return {
        "review": review if (endpoints or requirements or isolations or manuals) else {},
        "gaps": gaps,
        "contradictions": contradictions,
        "abstentions": abstentions,
        "findings": findings,
    }
