"""Privacy and purpose gates. Evaluated live from the fixture; never cached (AP-9)."""

from __future__ import annotations

import hashlib
from typing import Any

from packages.config.entitlements import entitled_groups, role_entitled
from packages.config.purposes import BIOMARKER_PURPOSES, CONSENT_PURPOSES, PURPOSE_REGISTER
from packages.config.roles import canonical_role
from packages.domain.batch import iter_records
from packages.kernel.audit import write_audit

DIRECT_ID_KEYS = frozenset(
    {
        "patient_key",
        "patient_id",
        "initials",
        "date_of_birth",
        "dob",
        "name",
        "email",
    }
)
_MISSING = frozenset({"", "unknown", "unk", "n/a", "na", "none"})
SEGMENT_KEYS = frozenset(
    {
        "pregnancy",
        "pregnant",
        "minor",
        "paediatric",
        "pediatric",
        "genomic",
        "PV_PREGNANCY",
        "PV_PAEDIATRIC",
        "allocation",
        "treatment_arm",
        "arm",
        "kit",
        "unblinded",
        "randomization_code",
        "treatment",
    }
)
PSEUDONYM_PREFIX = "PN-"


def _rows(fixture: dict[str, Any], filename: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        if source.replace("\\", "/").endswith(filename):
            found.append(record)
    return found


def resolve_role(fixture: dict[str, Any], user: str) -> str | None:
    for record in _rows(fixture, "users_entitlements.csv"):
        if str(record.get("user") or "") == user:
            return canonical_role(str(record.get("role") or ""))
    return canonical_role(user)


def consent_covers(record: dict[str, Any], purpose: str) -> bool:
    declared = str(record.get("purpose") or "")
    status = str(record.get("status") or "").casefold()
    if purpose in BIOMARKER_PURPOSES:
        if "withdrawn" in status and "biomarker" in status:
            return False
        return "biomarker" in declared and status == "active"
    if purpose == "trial":
        if status == "active" and "trial" in declared:
            return True
        if "withdrawn_biomarker" in status and "trial" in declared:
            return True
        return False
    if purpose == "trial_and_biomarker":
        return status == "active" and declared == "trial_and_biomarker"
    return declared == purpose and status == "active"


def _hold_active(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in _rows(fixture, "legal_holds.csv") if str(row.get("status") or "").casefold() == "active"]


def _approved_regions(text: str) -> set[str]:
    return {part.strip() for part in (text or "").split(",") if part.strip()}


def evaluate_privacy(context: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    purpose = str(context.get("purpose") or "").strip()
    user = str(context.get("user") or "").strip()
    findings: list[dict[str, Any]] = []
    withhold: list[str] = []
    decision = "allow"
    reason = ""

    if purpose and purpose not in PURPOSE_REGISTER:
        decision = "deny"
        reason = f"PURPOSE_NOT_COVERED:unregistered:{purpose}"
        findings.append(
            {
                "finding_id": "F-PURPOSE-UNREGISTERED",
                "statement": f"Purpose {purpose} is absent from the purpose register and is denied.",
                "evidence_refs": [],
            }
        )

    consents = _rows(fixture, "consents.csv")
    if decision == "allow" and purpose in CONSENT_PURPOSES:
        covering = [row for row in consents if consent_covers(row, purpose)]
        covered_subjects = {
            str(row.get("subject_id") or "")
            for row in covering
            if row.get("subject_id")
        }
        mentioned = {str(row.get("subject_id") or "") for row in consents if row.get("subject_id")}
        if not covering:
            decision = "deny"
            reason = f"PURPOSE_NOT_COVERED:{purpose}"
            withhold.extend(sorted(mentioned))
            findings.append(
                {
                    "finding_id": "F-CONSENT-PURPOSE",
                    "statement": (
                        f"Purpose {purpose} is not covered by consent; subject data is withheld "
                        "and no subject content is loaded."
                    ),
                    "evidence_refs": sorted(mentioned),
                }
            )
        elif withhold or mentioned - covered_subjects:
            withhold.extend(sorted(mentioned - covered_subjects))
            findings.append(
                {
                    "finding_id": "F-CONSENT-WITHHOLD",
                    "statement": "Subject data is withheld where consent for the purpose is withdrawn.",
                    "evidence_refs": list(withhold),
                }
            )

    for row in _rows(fixture, "processing_events.csv"):
        if str(row.get("consent_check") or "").casefold() == "cached_active":
            findings.append(
                {
                    "finding_id": f"F-CONSENT-CACHE-{row.get('event_id')}",
                    "statement": (
                        f"Processing event {row.get('event_id')} used consent_check cached_active; "
                        "this is a control failure."
                    ),
                    "evidence_refs": [str(row.get("event_id") or "")],
                }
            )

    for row in _rows(fixture, "users_entitlements.csv"):
        if str(row.get("user") or "") != user:
            continue
        if str(row.get("iam_state") or "").casefold() != "revoked":
            continue
        decision = "deny"
        reason = "AUTHZ_DENIED"
        cache_rows = [item for item in _rows(fixture, "access_cache.csv") if str(item.get("user") or "") == user]
        refs = ["data/users_entitlements.csv"]
        window = ""
        if cache_rows:
            refs.append("data/access_cache.csv")
            revoked_at = str(cache_rows[0].get("revoked_at") or "")
            cached_until = str(cache_rows[0].get("cached_until") or "")
            window = f" between {revoked_at} and {cached_until}"
        findings.append(
            {
                "finding_id": "F-IAM-REVOKED",
                "statement": (
                    f"IAM state for {user} is revoked while gateway state is "
                    f"{row.get('ai_gateway_state')}. Cached entitlement is not load-bearing."
                    f" Revocation-lag window{window}."
                ),
                "evidence_refs": refs,
            }
        )

    for row in _rows(fixture, "access_logs.csv"):
        actor = str(row.get("user") or "")
        action = str(row.get("action") or "")
        if "shared" in actor.casefold() and "approve" in action.casefold():
            findings.append(
                {
                    "finding_id": "F-ATTR-SHARED",
                    "statement": (
                        f"Action {action} recorded against {actor} is unattributable "
                        "and cannot support a regulated decision."
                    ),
                    "evidence_refs": [str(row.get("event_id") or actor)],
                }
            )
        if action == "login_from_two_devices":
            findings.append(
                {
                    "finding_id": "F-ATTR-TWO-DEVICE",
                    "statement": (
                        f"{actor} login_from_two_devices is an anomaly and does not by itself deny."
                    ),
                    "evidence_refs": [str(row.get("event_id") or actor)],
                }
            )

    holds = _hold_active(fixture)
    deletions = _rows(fixture, "deletion_requests.csv")
    if deletions and holds:
        hold_ids = [str(row.get("hold_id") or "") for row in holds]
        dsr_ids = [str(row.get("request_id") or "") for row in deletions]
        findings.append(
            {
                "finding_id": "F-DSR-HOLD",
                "statement": (
                    f"{dsr_ids[0]} collides with active hold {hold_ids[0]}. "
                    "Outcome is restriction. Both obligations are documented. Records are retained."
                ),
                "evidence_refs": [dsr_ids[0], hold_ids[0]],
            }
        )

    hold_check = {
        "checked": True,
        "active_holds": [str(row.get("hold_id") or "") for row in holds],
    }
    for row in _rows(fixture, "retention_rules.csv"):
        action = str(row.get("action") or "").casefold()
        record_type = str(row.get("record_type") or "")
        if "delete after 90" in action and "unless" in action:
            if holds:
                findings.append(
                    {
                        "finding_id": "F-RETENTION-HOLD",
                        "statement": (
                            f"{record_type} 90-day expiry is not applied because an evidence hold is active. "
                            f"Hold check: {', '.join(hold_check['active_holds'])} active."
                        ),
                        "evidence_refs": hold_check["active_holds"],
                    }
                )
            else:
                findings.append(
                    {
                        "finding_id": "F-RETENTION-EXPIRY",
                        "statement": f"{record_type} may expire at 90 days; no evidence hold is active.",
                        "evidence_refs": [record_type],
                    }
                )

    if decision == "allow":
        for row in _rows(fixture, "data_residency.csv"):
            approved = _approved_regions(str(row.get("approved_regions") or ""))
            observed = str(row.get("observed_region") or "").strip()
            if observed and approved and observed not in approved:
                decision = "deny"
                reason = "RESIDENCY_BLOCKED"
                findings.append(
                    {
                        "finding_id": "F-RESIDENCY",
                        "statement": (
                            f"Cross-border path {observed} is outside approved regions "
                            f"{sorted(approved)}; no lawful basis is in evidence."
                        ),
                        "evidence_refs": [str(row.get("data_class") or "")],
                    }
                )
        endpoint = str(context.get("endpoint_region") or context.get("destination_region") or "").strip()
        for row in _rows(fixture, "data_residency.csv"):
            approved = _approved_regions(str(row.get("approved_regions") or ""))
            if endpoint and approved and endpoint not in approved:
                decision = "deny"
                reason = "RESIDENCY_BLOCKED"
                findings.append(
                    {
                        "finding_id": "F-RESIDENCY-ENDPOINT",
                        "statement": (
                            f"Inference endpoint region {endpoint} is outside approved regions "
                            f"{sorted(approved)}; the call is not made."
                        ),
                        "evidence_refs": [str(row.get("data_class") or "")],
                    }
                )
        for row in _rows(fixture, "data_exports.csv"):
            if str(row.get("approved") or "").casefold() in {"no", "false", "denied"}:
                decision = "deny"
                reason = "RESIDENCY_BLOCKED"
                findings.append(
                    {
                        "finding_id": f"F-EXPORT-{row.get('export_id')}",
                        "statement": (
                            f"Export {row.get('export_id')} from {row.get('from_region')} to "
                            f"{row.get('to_region')} lacks a lawful basis; safety data is not moved."
                        ),
                        "evidence_refs": [str(row.get("export_id") or "")],
                    }
                )

    role = resolve_role(fixture, user)
    groups = sorted(entitled_groups(role))
    write_audit(
        {
            "event": "privacy_gate",
            "decision": decision,
            "reason": reason,
            "purpose": purpose,
            "user": user,
            "role": role or "",
            "hold_check": hold_check,
        }
    )
    return {
        "decision": decision,
        "reason": reason,
        "findings": findings,
        "withhold_subjects": withhold,
        "hold_check": hold_check,
        "role": role,
        "entitled_groups": groups,
    }


def purpose_salt(purpose: str) -> bytes:
    return hashlib.sha256(f"aegis-purpose|{purpose}".encode("utf-8")).digest()


def pseudonym_for(identifier: str, purpose: str) -> str:
    digest = hashlib.sha256(purpose_salt(purpose) + b"|" + identifier.encode("utf-8")).hexdigest()
    return f"{PSEUDONYM_PREFIX}{digest[:20]}"


def _is_direct_identifier(value: Any) -> bool:
    text = str(value or "").strip()
    if not text or text.casefold() in _MISSING:
        return False
    if text.startswith(PSEUDONYM_PREFIX):
        return False
    return True


def pseudonymise(obj: Any, purpose: str, *, keys: frozenset[str] | None = None) -> Any:
    """Replace direct identifiers. The mapping is not returned."""
    target_keys = keys if keys is not None else DIRECT_ID_KEYS
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key in target_keys and _is_direct_identifier(value):
                out[key] = pseudonym_for(str(value).strip(), purpose)
            else:
                out[key] = pseudonymise(value, purpose, keys=target_keys)
        return out
    if isinstance(obj, list):
        return [pseudonymise(item, purpose, keys=target_keys) for item in obj]
    return obj


_DROPPED = object()


def strip_sensitive(obj: Any, role_id: str | None) -> tuple[Any, bool]:
    """Drop sensitive-segment keys and unentitled rows. Absence, not redaction."""
    withheld = False

    def drop_record(value: dict[str, Any]) -> bool:
        access = str(value.get("access_group") or "")
        if access and not role_entitled(role_id, access):
            return True
        segment = str(value.get("segment") or "").casefold()
        if segment == "pregnancy" and not role_entitled(role_id, "PV_PREGNANCY"):
            return True
        if segment in {"minor", "paediatric", "pediatric"} and not role_entitled(role_id, "PV_PAEDIATRIC"):
            return True
        if segment == "genomic":
            return True
        return False

    def drop(value: Any) -> Any:
        nonlocal withheld
        if isinstance(value, dict):
            if drop_record(value):
                withheld = True
                return _DROPPED
            cleaned: dict[str, Any] = {}
            for key, item in value.items():
                if key in SEGMENT_KEYS and not _key_entitled(role_id, key):
                    withheld = True
                    continue
                nested = drop(item)
                if nested is _DROPPED:
                    withheld = True
                    if key == "facts":
                        return _DROPPED
                    continue
                cleaned[key] = nested
            return cleaned
        if isinstance(value, list):
            kept = []
            for item in value:
                nested = drop(item)
                if nested is _DROPPED:
                    withheld = True
                    continue
                kept.append(nested)
            return kept
        return value

    return drop(obj), withheld


def _key_entitled(role_id: str | None, key: str) -> bool:
    if key in {"pregnancy", "pregnant", "PV_PREGNANCY"}:
        return role_entitled(role_id, "PV_PREGNANCY")
    if key in {"minor", "paediatric", "pediatric", "PV_PAEDIATRIC"}:
        return role_entitled(role_id, "PV_PAEDIATRIC")
    if key == "genomic":
        return False
    if key in {
        "allocation",
        "treatment_arm",
        "arm",
        "kit",
        "unblinded",
        "randomization_code",
        "treatment",
    }:
        return False
    return False


def record_pseudonymisation(purpose: str, field_count: int) -> None:
    write_audit(
        {
            "event": "pseudonymisation",
            "purpose": purpose,
            "field_count": field_count,
            "algorithm": "sha256-purpose-salt",
        }
    )


def count_direct_identifiers(obj: Any, originals: set[str]) -> int:
    found = 0
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in DIRECT_ID_KEYS and _is_direct_identifier(value):
                found += 1
                originals.add(str(value).strip())
            found += count_direct_identifiers(value, originals)
    elif isinstance(obj, list):
        for item in obj:
            found += count_direct_identifiers(item, originals)
    return found


def filter_withheld_subjects(fixture: dict[str, Any], withhold: list[str]) -> dict[str, Any]:
    blocked = {item for item in withhold if item}
    if not blocked:
        return fixture
    clone = dict(fixture)
    evidence = []
    for blob in fixture.get("evidence") or []:
        records = blob.get("records")
        if not isinstance(records, list):
            evidence.append(blob)
            continue
        kept = [row for row in records if str(row.get("subject_id") or "") not in blocked]
        next_blob = dict(blob)
        next_blob["records"] = kept
        evidence.append(next_blob)
    clone["evidence"] = evidence
    return clone


def apply_emission_controls(pack: dict[str, Any], *, purpose: str, role_id: str | None) -> dict[str, Any]:
    stripped, withheld = strip_sensitive(pack, role_id)
    originals: set[str] = set()
    count = count_direct_identifiers(stripped, originals)
    emitted = pseudonymise(stripped, purpose)
    if count:
        record_pseudonymisation(purpose, count)
    if withheld:
        review = dict(emitted.get("human_review") or {})
        review["sensitive_segments_withheld"] = True
        emitted["human_review"] = review
    return emitted
