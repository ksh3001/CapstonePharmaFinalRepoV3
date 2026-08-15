"""Request lifecycle skeleton: mode, authZ, audit. Engines arrive in later tasks."""

from __future__ import annotations

from typing import Any

from packages.config.runtime import llm_enabled, runtime_mode
from packages.kernel.audit import write_audit
from packages.kernel.authz import authorize
from packages.kernel.canonical import derive_request_id, dumps, sha256_bytes
from packages.kernel.context import rule_context
from packages.kernel.interpreter import guard as interpreter_guard


CODE_VERSION = "phase-0"


def start_request(
    context: dict[str, Any],
    scenario_id: str = "UNSET",
    *,
    subject_id: str = "",
) -> dict[str, Any]:
    interpreter_guard()
    mode = runtime_mode()
    write_audit(
        {
            "event": "request_start",
            "mode": mode,
            "llm_enabled": llm_enabled(),
            "scenario_id": scenario_id,
        }
    )
    authorization = authorize(context)
    as_of = str(context.get("as_of") or "")
    material: dict[str, Any] = {"context": rule_context(context), "scenario_id": scenario_id}
    if subject_id:
        material["subject_id"] = str(subject_id)
    input_hash = sha256_bytes(dumps(material))
    request_id = derive_request_id(scenario_id, as_of, input_hash, CODE_VERSION)
    return {
        "request_id": request_id,
        "scenario_id": scenario_id,
        "as_of": as_of,
        "mode": mode,
        "authorization": authorization,
        "execution_status": "not_executed",
        "llm_enabled": llm_enabled(),
    }
