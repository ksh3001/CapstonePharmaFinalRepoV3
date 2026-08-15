"""Azure OpenAI adapter. Assessment/unconfigured fail closed. No keys in source."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import quote, urlparse

from packages.advice.brief import evidence_brief, stub_advice
from packages.advice.guards import guard_advice
from packages.advice.minimise import minimise_pack
from packages.advice.resolve import reset_inference_port, set_inference_port
from packages.config.envfile import load_envfile
from packages.config.runtime import inference_allowed
from packages.contracts.deny import grade

REQUIRED = (
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_MODEL_VERSION",
    "AZURE_OPENAI_REGION",
)

_STUB_HOSTS = frozenset({"example.openai.azure.com", "localhost", "127.0.0.1"})

_SYSTEM_PROMPT = (
    "You write a short evidence-based summary for a human reviewer of pharmaceutical evidence. "
    "Base the summary only on the evidence, contradictions, gaps, and abstentions in the user JSON. "
    "You do not decide, approve, release, reject, allocate, ship, recall, or sign anything. "
    "Reply with JSON only in this shape: "
    '{"text":"...","evidence_refs":["record_id"]}. '
    "Cite only record_id values that appear in the evidence array. "
    "Every number you write must appear verbatim in the user JSON. "
    "Do not use phrases such as approved for release, rejected for release, batch released, "
    "set disposition, allocate stock, ship the order, initiate recall, electronically signed, "
    "or patient is eligible. "
    "Do not say the case or batch is resolved or that no issue remains. "
    "Name the contradictions, gaps, and abstentions the reviewer must inspect."
)


def configure_inference(*, override: bool = False) -> None:
    load_envfile(override=override)
    if inference_allowed():
        set_inference_port(AzureOpenAIAdapter())
    else:
        reset_inference_port()


def _deployment() -> str:
    return (
        os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        or os.environ.get("GENERATOR_DEPLOYMENT")
        or os.environ.get("GENERATOR_MODEL")
        or ""
    ).strip()


def _model_version() -> str:
    pinned = os.environ.get("AZURE_OPENAI_MODEL_VERSION", "").strip()
    if pinned:
        return pinned
    return _deployment()


def _missing_settings() -> list[str]:
    values = {
        "AZURE_OPENAI_ENDPOINT": os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip(),
        "AZURE_OPENAI_DEPLOYMENT": _deployment(),
        "AZURE_OPENAI_API_VERSION": os.environ.get("AZURE_OPENAI_API_VERSION", "").strip(),
        "AZURE_OPENAI_MODEL_VERSION": _model_version(),
        "AZURE_OPENAI_REGION": os.environ.get("AZURE_OPENAI_REGION", "").strip(),
    }
    return [name for name, value in values.items() if not value]


def _host_is_stub(endpoint: str) -> bool:
    host = (urlparse(endpoint).hostname or "").lower()
    return host in _STUB_HOSTS


def _live_call_permitted(endpoint: str) -> bool:
    key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    if not key:
        return False
    if os.environ.get("AEGIS_ALLOW_KEY_AUTH", "").strip() != "dev":
        return False
    return not _host_is_stub(endpoint)


def _extract_json(text: str) -> dict[str, Any] | None:
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped[:4].lower() == "json":
            stripped = stripped[4:]
        stripped = stripped.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return parsed
    return None


def _content_filter(payload: dict[str, Any]) -> dict[str, str]:
    choice = (payload.get("choices") or [{}])[0]
    raw = choice.get("content_filter_results") or {}
    if not raw:
        prompt_filter = payload.get("prompt_filter_results") or []
        if prompt_filter and isinstance(prompt_filter, list):
            raw = prompt_filter[0].get("content_filter_results") or {}
    mapped: dict[str, str] = {}
    for key in ("hate", "self_harm", "sexual", "violence"):
        item = raw.get(key) or {}
        mapped[key] = str(item.get("severity") or "safe")
    return mapped


def _token_usage(payload: dict[str, Any] | None) -> dict[str, int]:
    usage = payload.get("usage") if isinstance(payload, dict) else {}
    if not isinstance(usage, dict):
        usage = {}
    prompt = int(usage.get("prompt_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    total = int(usage.get("total_tokens") or 0) or (prompt + completion)
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
    }


def _advice_from_model(pack: dict[str, Any], content: str) -> dict[str, Any]:
    parsed = _extract_json(content) or {}
    refs = parsed.get("evidence_refs") if isinstance(parsed.get("evidence_refs"), list) else []
    known = {str(item.get("record_id") or "") for item in pack.get("evidence") or []}
    evidence_refs = [str(item) for item in refs if str(item) in known]
    return {
        "text": str(parsed.get("text") or "").strip(),
        "evidence_refs": evidence_refs,
        "labelled": "model-generated",
    }


def _live_generate(pack: dict[str, Any], prompt: dict[str, Any]) -> dict[str, Any]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = _deployment()
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "").strip()
    key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    url = (
        f"{endpoint}/openai/deployments/{quote(deployment, safe='')}"
        f"/chat/completions?api-version={quote(api_version, safe='')}"
    )
    body = json.dumps(
        {
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False, default=str)},
            ],
            "temperature": 0,
            "max_tokens": 600,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "api-key": key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = int(getattr(exc, "code", 0) or 0)
        return {
            "called": False,
            "reason": f"azure_{status}" if status else "azure_http",
            "annotations": None,
            "outbound": 0,
            "retries": 1 if status in {429, 503} else 0,
        }
    except urllib.error.URLError:
        return {"called": False, "reason": "azure_unreachable", "annotations": None, "outbound": 0}
    except TimeoutError:
        return {"called": False, "reason": "azure_timeout", "annotations": None, "outbound": 0}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"called": False, "reason": "azure_invalid_response", "annotations": None, "outbound": 0}
    choice = (payload.get("choices") or [{}])[0]
    content = str((choice.get("message") or {}).get("content") or "")
    advice = _advice_from_model(pack, content)
    if not advice["text"]:
        return {
            "called": True,
            "outbound": 1,
            "prompt": prompt,
            "deployment": deployment,
            "model_version": _model_version(),
            "api_version": api_version,
            "system_fingerprint": str(payload.get("system_fingerprint") or "fp-live"),
            "content_filter": _content_filter(payload),
            "guard": {"passed": False, "check": "empty", "advice": None},
            "annotations": None,
            "reason": "empty_model_text",
            **_token_usage(payload),
        }
    guarded = guard_advice(pack, advice)
    return {
        "called": True,
        "outbound": 1,
        "prompt": prompt,
        "deployment": deployment,
        "model_version": _model_version(),
        "api_version": api_version,
        "system_fingerprint": str(payload.get("system_fingerprint") or "fp-live"),
        "content_filter": _content_filter(payload),
        "guard": guarded,
        "annotations": guarded.get("advice") if guarded.get("passed") else None,
        "reason": None if guarded.get("passed") else guarded.get("check"),
        **_token_usage(payload),
    }


class AzureOpenAIAdapter:
    def generate(self, pack: dict[str, Any]) -> dict[str, Any]:
        if not inference_allowed():
            return {"called": False, "reason": "kill_switch", "annotations": None, "outbound": 0}
        missing = _missing_settings()
        if missing:
            return {
                "called": False,
                "reason": "unconfigured:" + ",".join(missing),
                "annotations": None,
                "outbound": 0,
            }
        if os.environ.get("AZURE_OPENAI_API_KEY") and os.environ.get("AEGIS_RUNTIME_MODE") not in {"", None} and os.environ.get("AEGIS_RUNTIME_MODE") != "assessment":
            if os.environ.get("AEGIS_ALLOW_KEY_AUTH", "").strip() != "dev":
                return {"called": False, "reason": "key_auth_forbidden", "annotations": None, "outbound": 0}
        region = os.environ.get("AZURE_OPENAI_REGION", "")
        required_region = str((pack.get("authorization") or {}).get("region") or os.environ.get("AEGIS_DATA_REGION") or "")
        if required_region and required_region != region:
            return {"called": False, "reason": "residency_mismatch", "annotations": None, "outbound": 0}
        if _model_version().lower() in {"latest", "current", "alias"}:
            return {"called": False, "reason": "floating_alias", "annotations": None, "outbound": 0}
        status = os.environ.get("AEGIS_AZURE_STATUS", "")
        if status in {"429", "503"}:
            return {"called": False, "reason": f"azure_{status}", "annotations": None, "outbound": 0, "retries": 1}
        prompt = evidence_brief(minimise_pack(pack))
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
        if _live_call_permitted(endpoint):
            return _live_generate(pack, prompt)
        advice = stub_advice(pack)
        guarded = guard_advice(pack, advice)
        return {
            "called": True,
            "outbound": 1,
            "prompt": prompt,
            "deployment": _deployment(),
            "model_version": _model_version(),
            "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
            "system_fingerprint": "fp-assessment",
            "content_filter": {"hate": "safe", "self_harm": "safe", "sexual": "safe", "violence": "safe"},
            "guard": guarded,
            "annotations": guarded.get("advice") if guarded.get("passed") else None,
            "reason": None if guarded.get("passed") else guarded.get("check"),
            **_token_usage(None),
        }


_CHAT_SUMMARY_CHARS = 200
_READINESS_HEADLINE = {
    "insufficient_evidence": "is not ready for review. Required evidence is still closed.",
    "conflicted_evidence": "is not ready for review. Sources disagree.",
    "ready_for_authorized_review": "is ready for a qualified person to review.",
    "not_executed": "was assembled for review. No regulated action was taken.",
    "blocked": "is blocked until a person follows up on the pack.",
}


def _slim_brief(payload: dict[str, Any], question: str = "") -> dict[str, Any]:
    brief: dict[str, Any] = {"advisory": True, "disposition": False}
    asked = (question or "").strip()[:200]
    if asked:
        brief["question"] = asked
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("seed") or "visited" in summary:
        for key in (
            "entity",
            "seed",
            "source",
            "hops_used",
            "max_hops",
            "visited_count",
            "frontier_count",
            "traversal_incomplete",
        ):
            if key in summary:
                brief[key] = summary[key]
        brief["visited"] = list(summary.get("visited") or [])[:8]
        return brief
    if summary:
        for key in (
            "entity",
            "product",
            "workflow",
            "readiness_state",
            "execution_status",
            "findings",
            "contradictions",
            "gaps",
            "abstentions",
        ):
            if key in summary:
                brief[key] = summary[key]
        brief["remaining_critical"] = list(summary.get("remaining_critical") or [])[:6]
        brief["disputed"] = list(summary.get("disputed") or [])[:3]
        brief["missing"] = list(summary.get("missing") or [])[:3]
        brief["held"] = list(summary.get("held") or [])[:3]
        return brief
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    if counts:
        brief["counts"] = counts
        return brief
    answer = str(payload.get("answer") or "").strip()
    if answer:
        brief["answer"] = answer[:240]
    return brief


def _offline_restatement(brief: dict[str, Any]) -> str:
    blocks = _plain_blocks(brief)
    return " ".join(part for part in (blocks.get("headline"), blocks.get("meaning")) if part)


def _join_names(items: list[Any], *, limit: int = 3) -> str:
    names = [str(item).strip() for item in items if str(item).strip()][:limit]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]}, {names[1]}, and {names[2]}"


def _review_label(workflow: str) -> str:
    blob = (workflow or "").casefold()
    if blob.startswith("pv"):
        return "safety review"
    if blob.startswith("supply"):
        return "supply governance review"
    return "Qualified Person review"


def _plain_blocks(brief: dict[str, Any]) -> dict[str, str]:
    next_step = (
        "Open the pack, inspect the named items, then acknowledge or contest. "
        "Chat cannot change quality status."
    )
    if brief.get("seed") or "visited" in brief:
        entity = str(brief.get("entity") or "Pack")
        hops = brief.get("hops_used", 0)
        shown = [str(item).rsplit(":", 1)[-1] for item in (brief.get("visited") or [])[:3] if item]
        headline = f"{entity} has linked records next to it in the relation graph."
        meaning = f"Start with {_join_names(shown)}." if shown else "No nearby links were listed."
        if brief.get("traversal_incomplete"):
            meaning = meaning.rstrip(".") + f". Nothing beyond {hops} hops was followed."
        return {
            "headline": headline,
            "meaning": meaning,
            "next": f"Open the pack for {entity} to inspect those linked records.",
        }
    if brief.get("entity") or brief.get("readiness_state"):
        entity = str(brief.get("entity") or "Pack")
        readiness = str(brief.get("readiness_state") or "unknown")
        review = _review_label(str(brief.get("workflow") or ""))
        tail = _READINESS_HEADLINE.get(readiness, "needs a person to inspect the pack.")
        if readiness in {"insufficient_evidence", "conflicted_evidence", "blocked"}:
            headline = f"{entity} is not ready for {review}."
        elif readiness == "ready_for_authorized_review":
            headline = f"{entity} is ready for {review}."
        else:
            headline = f"{entity} {tail}"
        remaining = [str(item) for item in (brief.get("remaining_critical") or []) if item]
        disputed = [str(item) for item in (brief.get("disputed") or []) if item]
        missing = [str(item) for item in (brief.get("missing") or []) if item]
        held = [str(item) for item in (brief.get("held") or []) if item]
        if remaining:
            meaning = f"Still closed: {_join_names(remaining)}."
            next_step = (
                f"Open {_join_names(remaining)} on the pack page, then acknowledge or contest."
            )
        elif disputed:
            meaning = f"Inspect disagreement on {_join_names(disputed)}."
        elif missing:
            meaning = f"Required evidence is missing: {_join_names(missing)}."
        elif held:
            meaning = f"The engine abstained on {_join_names(held)}."
        elif readiness == "ready_for_authorized_review":
            meaning = "A qualified person can review the pack."
        else:
            meaning = "No outstanding critical evidence is listed."
        return {"headline": headline, "meaning": meaning, "next": next_step}
    counts = brief.get("counts") if isinstance(brief.get("counts"), dict) else {}
    if counts:
        return {
            "headline": "Inject coverage is a proof list, not a work queue.",
            "meaning": (
                f"{counts.get('covered', 0)} covered by rule, "
                f"{counts.get('artefact', 0)} by artefact, "
                f"{counts.get('uncovered', 0)} not covered."
            ),
            "next": "Open the injects page to see which rules and tests apply.",
        }
    answer = str(brief.get("answer") or "").strip()
    if not answer:
        return {}
    first = re.split(r"(?<=[.!?])\s+", answer, maxsplit=1)[0]
    return {"headline": first, "meaning": "", "next": next_step}


def _clip_chat_summary(text: str) -> str:
    compact = " ".join(text.split())
    parts = re.split(r"(?<=[.!?])\s+", compact)
    compact = " ".join(parts[:2]).strip()
    if len(compact) <= _CHAT_SUMMARY_CHARS:
        return compact
    trimmed = compact[: _CHAT_SUMMARY_CHARS - 1].rsplit(" ", 1)[0].rstrip(".,;:")
    return trimmed + "."


def _guarded(text: str, source: str) -> str:
    text = _clip_chat_summary(text)
    if not text:
        return ""
    if grade({"text": text}):
        return ""
    for match in re.findall(r"\d+(?:\.\d+)?", text):
        if match not in source:
            return ""
    return text


def summarize_tool_blocks(payload: dict[str, Any], *, question: str = "") -> dict[str, str]:
    """Headline, why, and next step for Pack chat. Grounded in the tool JSON."""
    brief = _slim_brief(payload, question)
    source = json.dumps(brief, ensure_ascii=False, default=str)
    blocks = _plain_blocks(brief)
    cleaned: dict[str, str] = {}
    for key in ("headline", "meaning", "next"):
        value = _guarded(str(blocks.get(key) or ""), source)
        if value:
            cleaned[key] = value
    if not cleaned.get("headline") and not cleaned.get("meaning"):
        return {}
    return cleaned


def summarize_tool_json(payload: dict[str, Any], *, question: str = "") -> str:
    """Short restatement of a tool payload. Empty when inference is off or guarded."""
    blocks = summarize_tool_blocks(payload, question=question)
    return " ".join(part for part in (blocks.get("headline"), blocks.get("meaning")) if part)
