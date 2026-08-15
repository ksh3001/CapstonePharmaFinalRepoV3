"""Pack assembly. Advisory packs stay fixture-thin; workflow packs run domain engines."""

from __future__ import annotations

from typing import Any

from packages.domain.authority import apply_authority_to_evidence, reconcile_authority
from packages.domain.batch import infer_batch_id, reconcile_batch
from packages.domain.checkpoints import hash_mismatch_finding, stale_checkpoint_abstention
from packages.domain.clinical import reconcile_clinical
from packages.domain.combinations import reidentification_assessment, strip_joined_quasi
from packages.domain.continuity import reconcile_continuity
from packages.domain.evidence import build_evidence_item
from packages.domain.finops import reconcile_finops
from packages.domain.interfaces import reconcile_interfaces
from packages.domain.links import cross_domain_candidates
from packages.domain.pv import infer_case_ids, reconcile_pv
from packages.domain.regulatory import reconcile_regulatory
from packages.domain.supply import infer_event_id, reconcile_supply
from packages.domain.tools import reconcile_tools
from packages.domain.types import Abstention
from packages.kernel.audit import audit_events, write_audit
from packages.kernel.canonical import (
    sort_abstentions,
    sort_contradictions,
    sort_evidence,
    sort_findings,
    sort_gaps,
)
from packages.kernel.checkpoint import (
    checkpoint_from_fixture,
    drafts_from_run,
    evaluate_checkpoint,
    input_hash,
    store_replay,
    take_replay,
)
from packages.kernel.lifecycle import start_request
from packages.kernel.privacy import (
    apply_emission_controls,
    evaluate_privacy,
    filter_withheld_subjects,
)
from packages.evidence_store.writer import persist_run


def _merge_authorization(started: dict[str, Any], privacy: dict[str, Any]) -> dict[str, Any]:
    auth = dict(started.get("authorization") or {})
    if auth.get("decision") == "deny":
        return auth
    if privacy.get("decision") == "deny":
        auth["decision"] = "deny"
        auth["reason"] = str(privacy.get("reason") or "AUTHZ_DENIED")
        write_audit({"event": "authz", "decision": "deny", "reason": auth["reason"]})
    return auth


def _as_dicts(items: list[Any]) -> list[dict[str, Any]]:
    return [item.as_dict() if hasattr(item, "as_dict") else dict(item) for item in items]


def advisory_pack(fixture: dict[str, Any], *, annotation: str = "") -> dict[str, Any]:
    context = dict(fixture.get("authorized_context") or {})
    scenario = dict(fixture.get("scenario") or {})
    scenario_id = str(scenario.get("id") or "UNSET")
    started = start_request(context, scenario_id=scenario_id)
    replayed = take_replay(started["request_id"])
    if replayed is not None:
        return replayed
    privacy = evaluate_privacy(context, fixture)
    authorization = _merge_authorization(started, privacy)
    as_of = str(context.get("as_of") or "")
    evidence: list[dict[str, Any]] = []
    abstentions: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    contradictions: list[dict[str, Any]] = []
    denied = authorization.get("decision") != "allow"
    if not denied:
        for blob in fixture.get("evidence") or []:
            source = str(blob.get("source") or "")
            records = blob.get("records") or [{}]
            record = records[0] if records else {}
            record_id = str(
                record.get("record_id")
                or record.get("request_id")
                or record.get("hold_id")
                or record.get("consent_id")
                or record.get("event_id")
                or record.get("batch_id")
                or record.get("assignment_id")
                or record.get("tool_id")
                or record.get("model_id")
                or record.get("doc_id")
                or record.get("document_id")
                or record.get("image_id")
                or record.get("change_id")
                or record.get("result_id")
                or record.get("id")
                or source
            )
            built = build_evidence_item(
                source=source,
                record_id=record_id,
                authority="challenge-package",
                effective_at=None,
                as_of=as_of,
                facts=record if isinstance(record, dict) else {},
            )
            if isinstance(built, Abstention):
                abstentions.append(built.as_dict())
            else:
                evidence.append(dict(built))
    if not denied:
        iface = reconcile_interfaces(fixture, as_of=as_of)
        abstentions.extend(_as_dicts(iface.get("abstentions") or []))
        gaps.extend(_as_dicts(iface.get("gaps") or []))
        contradictions.extend(_as_dicts(iface.get("contradictions") or []))
        findings_iface = list(iface.get("findings") or [])
        safe = filter_withheld_subjects(fixture, list(privacy.get("withhold_subjects") or []))
        clinical = reconcile_clinical(safe, as_of=as_of)
        regulatory = reconcile_regulatory(safe, as_of=as_of)
        reident = reidentification_assessment(safe)
        continuity = reconcile_continuity(safe, as_of=as_of)
        tools = reconcile_tools(safe, purpose=str(context.get("purpose") or ""))
        finops = reconcile_finops(safe, as_of=as_of)
        abstentions.extend(_as_dicts(clinical.get("abstentions") or []))
        abstentions.extend(_as_dicts(reident.get("abstentions") or []))
        abstentions.extend(_as_dicts(continuity.get("abstentions") or []))
        abstentions.extend(_as_dicts(tools.get("abstentions") or []))
        abstentions.extend(_as_dicts(finops.get("abstentions") or []))
        gaps.extend(_as_dicts(clinical.get("gaps") or []))
        gaps.extend(_as_dicts(regulatory.get("gaps") or []))
        gaps.extend(_as_dicts(continuity.get("gaps") or []))
        gaps.extend(_as_dicts(finops.get("gaps") or []))
        contradictions.extend(_as_dicts(clinical.get("contradictions") or []))
        contradictions.extend(_as_dicts(regulatory.get("contradictions") or []))
        contradictions.extend(_as_dicts(continuity.get("contradictions") or []))
        findings_iface.extend(list(clinical.get("findings") or []))
        findings_iface.extend(list(reident.get("findings") or []))
        findings_iface.extend(list(continuity.get("findings") or []))
        findings_iface.extend(list(tools.get("findings") or []))
        findings_iface.extend(list(finops.get("findings") or []))
        authority = reconcile_authority(safe, as_of=as_of)
        findings_iface.extend(list(authority.get("findings") or []))
        gaps.extend(_as_dicts(authority.get("gaps") or []))
        apply_authority_to_evidence(evidence, authority)
    else:
        iface = {}
        clinical = {"review": {}, "security_findings": []}
        regulatory = {}
        reident = {}
        continuity = {}
        tools = {}
        finops = {}
        authority = {}
        findings_iface = []
    findings = list(privacy.get("findings") or []) + findings_iface
    if annotation:
        findings.append(
            {
                "finding_id": "F-0",
                "statement": annotation,
                "evidence_refs": [],
            }
        )
    checkpoint = checkpoint_from_fixture(fixture, context)
    review: dict[str, Any] = {"hold_check": privacy.get("hold_check") or {}}
    if checkpoint:
        current = input_hash(context, scenario_id)
        verdict = evaluate_checkpoint(checkpoint, current)
        subject = str(checkpoint.get("run_id") or checkpoint.get("checkpoint_id") or scenario_id)
        if not verdict.get("fresh"):
            abstentions.append(
                stale_checkpoint_abstention(
                    subject,
                    str(verdict.get("reason") or "CHECKPOINT_STALE"),
                ).as_dict()
            )
            if verdict.get("reason") == "CHECKPOINT_HASH_MISMATCH":
                findings.append(
                    hash_mismatch_finding(
                        subject,
                        str(verdict.get("stored") or ""),
                        str(verdict.get("current") or ""),
                    )
                )
        drafts = drafts_from_run(checkpoint)
        review["checkpoint"] = {
            "run_id": str(checkpoint.get("run_id") or ""),
            "checkpoint_id": str(
                checkpoint.get("checkpoint_id") or checkpoint.get("checkpoint") or ""
            ),
            "state_age_minutes": verdict.get("state_age_minutes", checkpoint.get("state_age_minutes")),
            "fresh": bool(verdict.get("fresh")),
            "auto_resume": False if not verdict.get("fresh") else bool(verdict.get("resume")),
            "human_confirmation_required": not bool(verdict.get("fresh")),
            "reason": str(verdict.get("reason") or ""),
        }
        review["preexisting_drafts"] = drafts
        review["draft_count"] = len(drafts)
    if iface.get("presented") or iface.get("contract_versions"):
        review["interface_reconciliation"] = {
            "presented": list(iface.get("presented") or []),
            "contract_versions": list(iface.get("contract_versions") or []),
            "dates": list(iface.get("dates") or []),
        }
    clinical_review = dict(clinical.get("review") or {})
    if any(
        clinical_review.get(key)
        for key in (
            "applicability",
            "reference_range_outcomes",
            "pending_adjudication",
            "device_timestamps",
            "unblinding",
            "site_observations",
            "protocol_risks",
        )
    ):
        review["clinical"] = clinical_review
    if clinical.get("security_findings"):
        review["security_findings"] = sort_findings(list(clinical["security_findings"]))
    if regulatory.get("facts") or regulatory.get("labels"):
        review["regulatory"] = {
            "facts": list(regulatory.get("facts") or []),
            "labels": list(regulatory.get("labels") or []),
            "deadline_candidates": list(regulatory.get("deadline_candidates") or []),
            "variation_positions": list(regulatory.get("variation_positions") or []),
        }
    if reident.get("combination_withheld"):
        review["reidentification"] = {
            "combination_withheld": True,
            "separate_fields": list(reident.get("separate_fields") or []),
        }
    if continuity.get("review"):
        review["continuity"] = dict(continuity["review"])
    if tools.get("review"):
        review["tools"] = dict(tools["review"])
    if finops.get("review"):
        review["finops"] = dict(finops["review"])
    if authority.get("review"):
        review["authority"] = dict(authority["review"])
    pack = {
        "request_id": started["request_id"],
        "scenario_id": scenario_id,
        "workflow": scenario.get("workflow") or "security",
        "as_of": as_of,
        "authorization": authorization,
        "evidence": sort_evidence(evidence),
        "contradictions": sort_contradictions(contradictions),
        "gaps": sort_gaps(gaps),
        "abstentions": sort_abstentions(abstentions),
        "findings": sort_findings(findings),
        "required_reviews": (
            (["privacy_review"] if privacy.get("findings") else [])
            + (["integrity_review"] if (authority.get("findings") or []) else [])
        ),
        "human_review": review,
        "execution_status": "not_executed",
        "gate_outcome": "advisory_only" if authorization.get("decision") == "allow" else "abstained",
        "no_side_effects": True,
        "audit": {"hash_scope": "source_artifact"},
    }
    if finops.get("metrics"):
        pack["metrics"] = dict(finops["metrics"])
    if reident.get("combination_withheld"):
        pack = strip_joined_quasi(pack)
    emitted = apply_emission_controls(
        pack,
        purpose=str(context.get("purpose") or ""),
        role_id=privacy.get("role"),
    )
    persist_run(emitted, fixture, audit_tail=audit_events()[-8:])
    store_replay(started["request_id"], emitted)
    return emitted


def _empty_batch_body(batch_id: str) -> dict[str, Any]:
    return {
        "batch_id": batch_id,
        "evidence": [],
        "contradictions": [],
        "gaps": [],
        "abstentions": [],
        "applicable_documents": [],
        "readiness_state": "insufficient_evidence",
        "security_findings": [],
    }


def batch_pack(fixture: dict[str, Any], *, batch_id: str = "") -> dict[str, Any]:
    context = dict(fixture.get("authorized_context") or {})
    scenario = dict(fixture.get("scenario") or {})
    scenario_id = str(scenario.get("id") or "UNSET")
    resolved_id = infer_batch_id(fixture, batch_id)
    started = start_request(context, scenario_id=scenario_id, subject_id=resolved_id)
    privacy = evaluate_privacy(context, fixture)
    authorization = _merge_authorization(started, privacy)
    as_of = str(context.get("as_of") or "")
    if authorization.get("decision") != "allow":
        body = _empty_batch_body(resolved_id)
    else:
        body = reconcile_batch(fixture, batch_id=resolved_id, as_of=as_of)
    review: dict[str, Any] = {}
    if body.get("security_findings"):
        review["security_findings"] = sort_findings(list(body.get("security_findings") or []))
    if privacy.get("findings"):
        review["privacy_findings"] = sort_findings(list(privacy["findings"]))
    pack = {
        "request_id": started["request_id"],
        "workflow": "batch_evidence",
        "as_of": as_of,
        "authorization": authorization,
        "evidence": sort_evidence([dict(item) for item in body["evidence"]]),
        "contradictions": sort_contradictions(_as_dicts(body["contradictions"])),
        "gaps": sort_gaps(_as_dicts(body["gaps"])),
        "abstentions": sort_abstentions(_as_dicts(body["abstentions"])),
        "human_review": review,
        "execution_status": "not_executed",
        "audit": {"hash_scope": "source_artifact"},
        "batch_id": body["batch_id"],
        "readiness_state": body["readiness_state"],
        "applicable_documents": body["applicable_documents"],
    }
    emitted = apply_emission_controls(
        pack,
        purpose=str(context.get("purpose") or ""),
        role_id=privacy.get("role"),
    )
    persist_run(emitted, fixture, audit_tail=audit_events()[-8:])
    return emitted


def _empty_pv_body(case_ids: list[str]) -> dict[str, Any]:
    return {
        "case_ids": case_ids or ["UNSET"],
        "evidence": [],
        "contradictions": [],
        "gaps": [],
        "abstentions": [],
        "source_facts": [],
        "duplicate_candidates": [],
        "clock_evidence": [],
        "terminology": [],
        "listedness_context": [],
        "required_reviews": [],
        "security_findings": [],
        "subgroup_limitations": [],
    }


def pv_pack(fixture: dict[str, Any], *, case_ids: list[str] | None = None) -> dict[str, Any]:
    context = dict(fixture.get("authorized_context") or {})
    scenario = dict(fixture.get("scenario") or {})
    scenario_id = str(scenario.get("id") or "UNSET")
    requested = [item for item in (case_ids or []) if item]
    resolved = infer_case_ids(fixture, requested[0] if requested else "")
    subject = requested[0] if requested else (resolved[0] if resolved else "")
    started = start_request(context, scenario_id=scenario_id, subject_id=subject)
    privacy = evaluate_privacy(context, fixture)
    authorization = _merge_authorization(started, privacy)
    as_of = str(context.get("as_of") or "")
    if authorization.get("decision") != "allow":
        body = _empty_pv_body(resolved)
        links: dict[str, Any] = {"unconfirmed_links": [], "count": 0}
    else:
        safe = filter_withheld_subjects(fixture, list(privacy.get("withhold_subjects") or []))
        body = reconcile_pv(safe, case_ids=resolved, as_of=as_of)
        links = cross_domain_candidates(safe)
    review: dict[str, Any] = {}
    findings = list(body.get("security_findings") or [])
    limitations = list(body.get("subgroup_limitations") or [])
    if findings:
        review["security_findings"] = sort_findings(findings)
    if limitations:
        review["subgroup_limitations"] = limitations
    if privacy.get("findings"):
        review["privacy_findings"] = sort_findings(list(privacy["findings"]))
    if links.get("unconfirmed_links"):
        review["unconfirmed_links"] = list(links["unconfirmed_links"])
        review["unconfirmed_link_count"] = links["count"]
    pack = {
        "request_id": started["request_id"],
        "workflow": "pv_intake",
        "as_of": as_of,
        "authorization": authorization,
        "evidence": sort_evidence([dict(item) for item in body["evidence"]]),
        "contradictions": sort_contradictions(_as_dicts(body["contradictions"])),
        "gaps": sort_gaps(_as_dicts(body["gaps"])),
        "abstentions": sort_abstentions(_as_dicts(body["abstentions"])),
        "human_review": review,
        "execution_status": "not_executed",
        "audit": {"hash_scope": "source_artifact"},
        "case_ids": list(body["case_ids"]),
        "source_facts": list(body["source_facts"]),
        "duplicate_candidates": list(body["duplicate_candidates"]),
        "clock_evidence": list(body["clock_evidence"]),
        "terminology": list(body["terminology"]),
        "listedness_context": list(body["listedness_context"]),
        "required_reviews": list(body["required_reviews"]),
    }
    emitted = apply_emission_controls(
        pack,
        purpose=str(context.get("purpose") or ""),
        role_id=privacy.get("role"),
    )
    persist_run(emitted, fixture, audit_tail=audit_events()[-8:])
    return emitted


def _empty_supply_body(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "evidence": [],
        "contradictions": [],
        "gaps": [],
        "abstentions": [],
        "options": [],
        "constraints": [],
        "approvals_required": [],
        "quality_holds": [],
        "security_findings": [],
    }


def supply_pack(fixture: dict[str, Any], *, event_id: str = "") -> dict[str, Any]:
    context = dict(fixture.get("authorized_context") or {})
    scenario = dict(fixture.get("scenario") or {})
    scenario_id = str(scenario.get("id") or "UNSET")
    resolved_id = infer_event_id(fixture, event_id)
    started = start_request(context, scenario_id=scenario_id, subject_id=resolved_id)
    replayed = take_replay(started["request_id"])
    if replayed is not None:
        return replayed
    privacy = evaluate_privacy(context, fixture)
    authorization = _merge_authorization(started, privacy)
    as_of = str(context.get("as_of") or "")
    checkpoint = checkpoint_from_fixture(fixture, context)
    extra_abstentions: list[Any] = []
    extra_findings: list[dict[str, Any]] = []
    review: dict[str, Any] = {}
    if checkpoint:
        current = input_hash(context, scenario_id)
        verdict = evaluate_checkpoint(checkpoint, current)
        subject = str(checkpoint.get("run_id") or resolved_id)
        if not verdict.get("fresh"):
            extra_abstentions.append(
                stale_checkpoint_abstention(subject, str(verdict.get("reason") or "CHECKPOINT_STALE"))
            )
            if verdict.get("reason") == "CHECKPOINT_HASH_MISMATCH":
                extra_findings.append(
                    hash_mismatch_finding(
                        subject,
                        str(verdict.get("stored") or ""),
                        str(verdict.get("current") or ""),
                    )
                )
        review["checkpoint"] = {
            "fresh": bool(verdict.get("fresh")),
            "auto_resume": False if not verdict.get("fresh") else bool(verdict.get("resume")),
            "human_confirmation_required": not bool(verdict.get("fresh")),
            "reason": str(verdict.get("reason") or ""),
            "state_age_minutes": verdict.get("state_age_minutes", checkpoint.get("state_age_minutes")),
        }
    if authorization.get("decision") != "allow":
        body = _empty_supply_body(resolved_id)
    else:
        safe = filter_withheld_subjects(fixture, list(privacy.get("withhold_subjects") or []))
        body = reconcile_supply(safe, event_id=resolved_id, as_of=as_of)
    body["abstentions"] = list(body.get("abstentions") or []) + extra_abstentions
    findings = list(body.get("security_findings") or []) + extra_findings
    if findings:
        review["security_findings"] = sort_findings(findings)
    if privacy.get("findings"):
        review["privacy_findings"] = sort_findings(list(privacy["findings"]))
    pack = {
        "request_id": started["request_id"],
        "workflow": "supply_options",
        "as_of": as_of,
        "authorization": authorization,
        "evidence": sort_evidence([dict(item) for item in body["evidence"]]),
        "contradictions": sort_contradictions(_as_dicts(body["contradictions"])),
        "gaps": sort_gaps(_as_dicts(body["gaps"])),
        "abstentions": sort_abstentions(_as_dicts(body["abstentions"])),
        "human_review": review,
        "execution_status": "not_executed",
        "audit": {"hash_scope": "source_artifact"},
        "event_id": body["event_id"],
        "options": list(body["options"]),
        "constraints": list(body["constraints"]),
        "approvals_required": list(body["approvals_required"]),
        "quality_holds": list(body["quality_holds"]),
        "no_side_effects": True,
    }
    emitted = apply_emission_controls(
        pack,
        purpose=str(context.get("purpose") or ""),
        role_id=privacy.get("role"),
    )
    persist_run(emitted, fixture, audit_tail=audit_events()[-8:])
    store_replay(started["request_id"], emitted)
    return emitted
