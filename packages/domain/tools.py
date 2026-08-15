"""Tool and model manifest verification at execution time. Classification types live here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.domain.batch import iter_records
from packages.domain.types import Abstention

_TRUE = frozenset({"yes", "true", "1"})
_FALSE = frozenset({"no", "false", "0", ""})


def _name(source: str) -> str:
    return Path(str(source).replace("\\", "/")).name


def _blank(value: Any) -> bool:
    return str(value or "").strip() == ""


def _flag(value: Any) -> bool:
    return str(value or "").strip().casefold() in _TRUE


def _invoked(record: dict[str, Any]) -> bool:
    return _flag(record.get("invoke")) or _flag(record.get("call")) or _flag(record.get("requested"))


def _purpose_tokens(raw: str) -> set[str]:
    return {part.strip().casefold() for part in raw.replace(";", ",").split(",") if part.strip()}


def reconcile_tools(fixture: dict[str, Any], *, purpose: str) -> dict[str, Any]:
    catalog: dict[str, dict[str, Any]] = {}
    requested: list[dict[str, Any]] = []
    models: list[dict[str, Any]] = []
    context = dict(fixture.get("authorized_context") or {})
    for source, record in iter_records(fixture):
        name = _name(source)
        tool_id = str(record.get("tool_id") or "").strip()
        if tool_id and ("approved" in record or "permissions" in record):
            catalog[tool_id] = record
        if tool_id and _invoked(record):
            requested.append(record)
        if name == "model_registry.csv" or "intended_use" in record or "validated_for" in record:
            models.append(record)

    context_tool = str(context.get("tool_id") or "").strip()
    if context_tool:
        requested.append({"tool_id": context_tool, "invoke": "yes"})

    findings: list[dict[str, Any]] = []
    abstentions: list[Abstention] = []
    called: list[str] = []
    refused: list[dict[str, Any]] = []
    derived_output: list[Any] = []

    for row in requested:
        tool_id = str(row.get("tool_id") or "").strip() or "unlisted"
        listed = catalog.get(tool_id)
        signed = str((listed or row).get("signed") or "").strip().casefold()
        manifest = str((listed or row).get("manifest") or "").strip()
        approved = str((listed or {}).get("approved") or row.get("approved") or "").strip().casefold()
        declared = str((listed or row).get("manifest_hash") or "").strip()
        observed = str((listed or row).get("observed_hash") or row.get("observed_hash") or "").strip()
        altered = _flag((listed or row).get("altered")) or (declared and observed and declared != observed)
        unsigned = listed is None or approved in _FALSE or _blank(manifest) or signed in {"no", "false", "0"}
        if listed is None or unsigned or altered:
            reason = "unlisted" if listed is None else ("altered" if altered else "unsigned")
            statement = (
                f"Tool {tool_id} was refused at execution time ({reason} manifest). "
                "The tool was not called."
            )
            findings.append(
                {
                    "finding_id": f"F-TOOL-{tool_id}",
                    "statement": statement,
                    "evidence_refs": [tool_id],
                    "severity": "blocking",
                }
            )
            refused.append({"tool_id": tool_id, "reason": reason, "called": False})
            continue
        called.append(tool_id)

    requested_purpose = str(context.get("purpose") or purpose or "").strip()
    for row in models:
        model_id = str(row.get("model_id") or row.get("model") or "unqualified")
        intended = str(row.get("intended_use") or "")
        validated_for = str(row.get("validated_for") or "")
        qualification = str(row.get("qualification") or "")
        covered = _purpose_tokens(intended) | _purpose_tokens(validated_for)
        purpose_key = requested_purpose.casefold()
        in_scope = bool(purpose_key) and purpose_key in covered
        missing = qualification or intended or validated_for or "documented intended use"
        if not in_scope:
            statement = (
                f"Model {model_id} was refused: documented intended use does not cover "
                f"{requested_purpose or 'the requested purpose'}. "
                f"Missing qualification: {missing}. No derived output is included."
            )
            findings.append(
                {
                    "finding_id": f"F-MODEL-{model_id}",
                    "statement": statement,
                    "evidence_refs": [model_id],
                    "severity": "blocking",
                }
            )
            abstentions.append(
                Abstention(
                    reason_code="model_unqualified",
                    subject_id=model_id,
                    statement=statement,
                    missing_qualification=missing,
                )
            )

    review = {}
    if requested or models or catalog:
        review = {
            "called": called,
            "refused": refused,
            "derived_output": derived_output,
            "tools_invoked": bool(called),
        }
    return {
        "review": review,
        "findings": findings,
        "abstentions": abstentions,
        "gaps": [],
        "contradictions": [],
    }
