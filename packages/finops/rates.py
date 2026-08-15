"""Listed unit prices. Cost is tokens times the card; never an estimate."""

from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from packages.config.paths import synthetic_dir

MILLION = Decimal("1000000")
ROUNDING = ROUND_HALF_EVEN
LISTED_MODEL = "large-1"
PRICE_FILE = "model_costs.csv"


def listed_model(name: str = LISTED_MODEL) -> dict[str, str] | None:
    path = synthetic_dir() / "data" / PRICE_FILE
    if not path.is_file():
        return None
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({str(key): str(value) for key, value in row.items()})
    if not rows:
        return None
    return next((row for row in rows if str(row.get("model") or "") == name), rows[0])


def price_tokens(prompt_tokens: int, completion_tokens: int, *, model: str = LISTED_MODEL) -> dict[str, Any]:
    listed = listed_model(model)
    if listed is None:
        return {
            "priced": False,
            "estimated": False,
            "total_complete": False,
            "basis": "listed_price_unavailable",
        }
    prompt = Decimal(int(prompt_tokens))
    completion = Decimal(int(completion_tokens))
    input_price = Decimal(str(listed.get("input_per_million") or "0"))
    output_price = Decimal(str(listed.get("output_per_million") or "0"))
    prompt_cost = (prompt / MILLION) * input_price
    completion_cost = (completion / MILLION) * output_price
    total = prompt_cost + completion_cost
    return {
        "priced": True,
        "estimated": False,
        "total_complete": False,
        "currency": "USD",
        "basis": "recorded_tokens_x_listed_unit_price",
        "source": f"tests/fixtures/synthetic/data/{PRICE_FILE}",
        "model": str(listed.get("model") or model),
        "vendor": str(listed.get("vendor") or ""),
        "input_per_million": format(input_price, "f"),
        "output_per_million": format(output_price, "f"),
        "prompt_cost": format(prompt_cost, "f"),
        "completion_cost": format(completion_cost, "f"),
        "inference_cost": format(total, "f"),
        "rounding": str(ROUNDING),
        "missing_components": [
            "human_quality_review",
            "medical_review",
            "platform",
            "observability",
        ],
    }
