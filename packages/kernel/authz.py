"""Execution-time authorisation. Deny by default on stale or ambiguous state."""

from __future__ import annotations

from typing import Any

from packages.config.purposes import PURPOSE_REGISTER
from packages.kernel.canonical import derived_timestamp
from packages.kernel.audit import write_audit

ERROR_CODES = (
    "AUTHZ_DENIED",
    "PURPOSE_NOT_COVERED",
    "RESIDENCY_BLOCKED",
    "INTEGRITY_FAILED",
    "TOOL_UNTRUSTED",
    "MODEL_UNVERIFIED",
    "BUDGET_EXHAUSTED",
    "CHECKPOINT_STALE",
    "CONTRACT_INVALID",
    "SOURCE_UNAVAILABLE",
)


def authorize(context: dict[str, Any]) -> dict[str, Any]:
    user = (context.get("user") or "").strip()
    purpose = (context.get("purpose") or "").strip()
    as_of = context.get("as_of") or ""
    execution = context.get("execution") or "disabled"
    checked_at = derived_timestamp(str(as_of))

    if not user or not purpose or not as_of:
        decision = {
            "user": user,
            "purpose": purpose,
            "checked_at": checked_at,
            "decision": "deny",
            "reason": "AUTHZ_DENIED",
        }
        write_audit({"event": "authz", "decision": "deny", "reason": "AUTHZ_DENIED"})
        return decision

    if execution != "disabled":
        decision = {
            "user": user,
            "purpose": purpose,
            "checked_at": checked_at,
            "decision": "deny",
            "reason": "AUTHZ_DENIED",
        }
        write_audit({"event": "authz", "decision": "deny", "reason": "execution_not_disabled"})
        return decision

    if purpose not in PURPOSE_REGISTER:
        decision = {
            "user": user,
            "purpose": purpose,
            "checked_at": checked_at,
            "decision": "deny",
            "reason": f"PURPOSE_NOT_COVERED:unregistered:{purpose}",
        }
        write_audit({"event": "authz", "decision": "deny", "reason": decision["reason"]})
        return decision

    decision = {
        "user": user,
        "purpose": purpose,
        "checked_at": checked_at,
        "decision": "allow",
    }
    write_audit({"event": "authz", "decision": "allow", "user": user, "purpose": purpose})
    return decision
