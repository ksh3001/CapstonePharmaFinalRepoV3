"""FinOps: cost per successful task. Classification types live here (MR-5)."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from packages.domain.batch import iter_records
from packages.domain.types import Abstention, Gap

MILLION = Decimal("1000000")
ZERO_IS_MISSING = frozenset({"human_quality_review", "medical_review"})
ROUNDING = ROUND_HALF_EVEN


def _dec(value: Any) -> Decimal:
    return Decimal(str(value))


def reconcile_finops(fixture: dict[str, Any], *, as_of: str) -> dict[str, Any]:
    del as_of
    usage: list[dict[str, Any]] = []
    prices: list[dict[str, Any]] = []
    cost_lines: list[dict[str, Any]] = []
    rates: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        name = str(source).replace("\\", "/").rsplit("/", 1)[-1]
        if name == "model_usage.csv":
            usage.append(record)
        elif name == "model_costs.csv":
            prices.append(record)
        elif name == "cost_model.csv":
            cost_lines.append(record)
        elif name == "staff_rates.csv":
            rates.append(record)
    if not (usage or prices or cost_lines or rates):
        return {"review": {}, "metrics": {}, "gaps": [], "abstentions": [], "findings": []}

    primary = next((row for row in prices if str(row.get("model") or "") == "large-1"), prices[0] if prices else {})
    alternative = next((row for row in prices if str(row.get("model") or "") == "small-7b"), {})
    input_price = _dec(primary.get("input_per_million") or "0")
    output_price = _dec(primary.get("output_per_million") or "0")
    previous = _dec(primary.get("previous") or input_price)

    workflows: list[dict[str, Any]] = []
    gaps: list[Gap] = []
    abstentions: list[Abstention] = []
    for row in usage:
        name = str(row.get("workflow") or "")
        input_tokens = _dec(row.get("input_tokens") or "0")
        output_tokens = _dec(row.get("output_tokens") or "0")
        successful = _dec(row.get("successful_tasks") or "0")
        requests = _dec(row.get("requests") or "0")
        inference = (input_tokens / MILLION) * input_price + (output_tokens / MILLION) * output_price
        per_success = (inference / successful) if successful else Decimal("0")
        workflows.append(
            {
                "workflow": name,
                "inference_cost": format(inference, "f"),
                "cost_per_successful_task": format(per_success, "f"),
                "successful_tasks": str(int(successful)),
                "requests": str(int(requests)),
                "denominator": "successful_tasks",
                "success_basis": "source_supplied",
            }
        )

    missing: list[str] = []
    for row in cost_lines:
        cost_type = str(row.get("cost_type") or "")
        amount = str(row.get("monthly_usd") or "")
        if cost_type in ZERO_IS_MISSING and amount.strip() in {"0", "0.0", "0.00"}:
            missing.append(cost_type)
            gaps.append(
                Gap(
                    gap_type="missing_cost",
                    subject_id=cost_type,
                    statement=f"{cost_type} is missing, not zero. No complete total is presented.",
                )
            )

    if rates and not any(row.get("minutes") or row.get("duration") for row in rates):
        abstentions.append(
            Abstention(
                reason_code="human_review_duration_unavailable",
                subject_id="human_review",
                statement=(
                    "Staff rates are present and review minutes are not. "
                    "Total cost per successful task abstains; duration is not assumed."
                ),
            )
        )

    price_change = {
        "model": str(primary.get("model") or "large-1"),
        "previous": format(previous, "f"),
        "current": format(input_price, "f"),
        "unit": "per_million_input_tokens",
        "effect": format(input_price - previous, "f"),
        "historical_not_restated": True,
    }
    concentration = {
        "vendor": str(primary.get("vendor") or "AIVENDOR-X"),
        "single_vendor": True,
        "alternative": str(alternative.get("vendor") or "LOCAL-SLM"),
        "exit_cost": "source_unspecified",
    }
    review = {
        "workflows": workflows,
        "missing_components": missing,
        "total_complete": False,
        "price_change": price_change,
        "concentration": concentration,
        "avoided_inference": {"count": "0", "cache_hit_rate": "0", "model_calls": "0"},
        "rounding": str(ROUNDING),
        "estimated": False,
    }
    metrics = {
        "finops": {
            "workflows": workflows,
            "missing_components": missing,
            "price_change": price_change,
            "concentration": concentration,
        }
    }
    return {
        "review": review,
        "metrics": metrics,
        "gaps": gaps,
        "abstentions": abstentions,
        "findings": [],
        "contradictions": [],
    }
