"""In-process runtime health. Evidence chain + audit; not OpenTelemetry."""

from __future__ import annotations

from typing import Any

from packages.config.budgets import MAX_STEPS_PER_REQUEST, MAX_TOKENS_PER_REQUEST, MAX_TOOL_CALLS_PER_REQUEST
from packages.config.runtime import inference_allowed, llm_enabled, runtime_mode
from packages.evidence_store.chain import load_chain, store_root
from packages.finops.rates import price_tokens
from packages.finops.wallet import WALLET_CEILING, remaining, spent


def runtime_health(
    *,
    session_count: int = 0,
    audit_events: list[dict[str, Any]] | None = None,
    sessions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rollup = _chain_rollups()
    events = list(audit_events or [])
    denials = sum(
        1
        for item in events
        if str(item.get("decision") or "") == "deny"
        or str(item.get("event") or "").endswith("_refused")
    )
    audit_by_event = _count_audit(events)
    ceiling = int(MAX_TOKENS_PER_REQUEST)
    used = int(rollup["total_tokens"])
    fill = 0 if ceiling <= 0 else min(100, int((used * 100) / ceiling))
    mode = runtime_mode()
    model_on = llm_enabled() and inference_allowed()
    status, status_reason = _status(
        model_on=model_on,
        denials=denials,
        guard_fail=int(rollup["guard_fail"]),
        mode=mode,
    )
    priced = price_tokens(int(rollup["prompt_tokens"]), int(rollup["completion_tokens"]))
    prompt = int(rollup["prompt_tokens"])
    completion = int(rollup["completion_tokens"])
    token_total = prompt + completion if used == 0 else used
    prompt_share = 0 if token_total <= 0 else min(100, int((prompt * 100) / token_total))
    completion_share = 0 if token_total <= 0 else max(0, 100 - prompt_share)
    return {
        "store": "in_process",
        "telemetry": "evidence_chain",
        "status": status,
        "status_reason": status_reason,
        "mode": mode,
        "llm_enabled": llm_enabled(),
        "inference_allowed": inference_allowed(),
        "kill_switch": not model_on,
        "session_count": int(session_count),
        "sessions": list(sessions or []),
        "chain_count": rollup["chains"],
        "llm_calls": rollup["calls"],
        "llm_live_calls": rollup["live_calls"],
        "llm_zero_token_calls": rollup["zero_calls"],
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": used,
        "token_ceiling": ceiling,
        "token_fill_pct": fill,
        "prompt_share_pct": prompt_share,
        "completion_share_pct": completion_share,
        "guard_fail": rollup["guard_fail"],
        "review_decisions": rollup["review_decisions"],
        "evidence_opened": rollup["evidence_opened"],
        "acknowledge_refused": rollup["acknowledge_refused"],
        "audit_events": len(events),
        "authz_denials": denials,
        "audit_by_event": audit_by_event,
        "deployments": rollup["deployments"],
        "recent_llm": rollup["recent_llm"],
        "cost": priced,
        "wallet": {
            "ceiling": format(WALLET_CEILING, "f"),
            "spent": format(spent(), "f"),
            "remaining": format(remaining(), "f"),
        },
        "budgets": {
            "max_input_tokens": ceiling,
            "max_output_tokens": ceiling,
            "max_steps": int(MAX_STEPS_PER_REQUEST),
            "max_tool_calls": int(MAX_TOOL_CALLS_PER_REQUEST),
        },
        "advisory": True,
        "estimated": False,
    }


def _status(*, model_on: bool, denials: int, guard_fail: int, mode: str) -> tuple[str, str]:
    if denials or guard_fail:
        return "attention", "AuthZ denials or failed advice guards are on the trail."
    if not model_on:
        return "inference_off", f"Inference is off in {mode}. Deterministic engines still run."
    return "nominal", "Counters in this process are within recorded bounds. Not an SLO burn."


def _count_audit(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in events:
        key = str(item.get("event") or item.get("decision") or "event")
        counts[key] = counts.get(key, 0) + 1
    return [{"event": key, "count": counts[key]} for key in sorted(counts)]


def _chain_rollups() -> dict[str, Any]:
    prompt = completion = total = calls = guard_fail = chains = 0
    live_calls = zero_calls = 0
    review_decisions = evidence_opened = acknowledge_refused = 0
    deployments: dict[str, dict[str, Any]] = {}
    recent: list[dict[str, Any]] = []
    folder = store_root() / "chains"
    if folder.is_dir():
        for path in sorted(folder.glob("*.jsonl")):
            chains += 1
            request_id = path.stem
            for row in load_chain(request_id):
                kind = str(row.get("type") or "")
                payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
                if kind == "llm":
                    calls += 1
                    ptok = int(payload.get("prompt_tokens") or 0)
                    ctok = int(payload.get("completion_tokens") or 0)
                    ttok = int(payload.get("total_tokens") or 0) or (ptok + ctok)
                    prompt += ptok
                    completion += ctok
                    total += ttok
                    if ttok:
                        live_calls += 1
                    else:
                        zero_calls += 1
                    dep = str(payload.get("deployment") or payload.get("cost_model") or "unspecified")
                    bucket = deployments.setdefault(
                        dep,
                        {
                            "deployment": dep,
                            "calls": 0,
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                    )
                    bucket["calls"] += 1
                    bucket["prompt_tokens"] += ptok
                    bucket["completion_tokens"] += ctok
                    bucket["total_tokens"] += ttok
                    recent.append(
                        {
                            "request_id": request_id,
                            "seq": int(row.get("seq") or 0),
                            "deployment": dep,
                            "prompt_tokens": ptok,
                            "completion_tokens": ctok,
                            "total_tokens": ttok,
                            "inference_cost": str(payload.get("inference_cost") or ""),
                        }
                    )
                elif kind == "guard" and not payload.get("passed", True):
                    guard_fail += 1
                elif kind == "review":
                    event = str(payload.get("event") or "")
                    if event == "evidence_opened":
                        evidence_opened += 1
                    elif event == "acknowledge_refused":
                        acknowledge_refused += 1
                    elif event in {"acknowledge", "contest"}:
                        review_decisions += 1
    if total == 0:
        total = prompt + completion
    recent = recent[-8:]
    for bucket in deployments.values():
        priced = price_tokens(int(bucket["prompt_tokens"]), int(bucket["completion_tokens"]))
        bucket["inference_cost"] = str(priced.get("inference_cost") or "0")
    return {
        "chains": chains,
        "calls": calls,
        "live_calls": live_calls,
        "zero_calls": zero_calls,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "guard_fail": guard_fail,
        "review_decisions": review_decisions,
        "evidence_opened": evidence_opened,
        "acknowledge_refused": acknowledge_refused,
        "deployments": [deployments[key] for key in sorted(deployments)],
        "recent_llm": recent,
    }
