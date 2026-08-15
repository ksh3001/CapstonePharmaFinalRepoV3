"""Every feature declaring advisory_nonexecuting must have a workflow enum value."""

from __future__ import annotations

import re
from pathlib import Path

from packages.contracts.validator import load_schema

_SPECS_FEATURES = Path(__file__).resolve().parents[2] / "specs" / "features"

FEATURE_GLOB = "FR-*.md"
CONTRACT_RE = re.compile(r"^\|\s*Contract\s*\|\s*(.+?)\s*\|", re.IGNORECASE)
WORKFLOW_RE = re.compile(r'workflow:\s*"([a-z_]+)"')
PUB_RE = re.compile(r"PUB-(\d+)")


FIXTURE_WORKFLOW = {
    "09": "security",
    "10": "reliability",
    "11": "privacy",
    "12": "integration",
    "13": "agent",
    "14": "finops",
    "15": "clinical",
}


def advisory_enum() -> list[str]:
    schema = load_schema("advisory_nonexecuting")
    return list(schema["properties"]["workflow"]["enum"])


def declared_features(features_dir: Path | None = None) -> list[dict[str, object]]:
    folder = features_dir if features_dir is not None else _SPECS_FEATURES
    rows: list[dict[str, object]] = []
    for path in sorted(folder.glob(FEATURE_GLOB)):
        text = path.read_text(encoding="utf-8")
        contract_line = ""
        for line in text.splitlines():
            match = CONTRACT_RE.match(line)
            if match:
                contract_line = match.group(1)
                break
        if "advisory_nonexecuting" not in contract_line:
            continue
        workflows = WORKFLOW_RE.findall(contract_line) + WORKFLOW_RE.findall(text)
        if not workflows:
            for pub in PUB_RE.findall(contract_line):
                mapped = FIXTURE_WORKFLOW.get(pub.zfill(2)[-2:])
                if mapped:
                    workflows.append(mapped)
        rows.append(
            {
                "feature": path.name,
                "path": str(path),
                "contract": contract_line,
                "workflows": sorted(set(workflows)),
            }
        )
    return rows


def representability_errors(features_dir: Path | None = None) -> list[str]:
    allowed = set(advisory_enum())
    errors: list[str] = []
    for row in declared_features(features_dir):
        workflows = list(row["workflows"])
        feature = str(row["feature"])
        if not workflows:
            errors.append(f"{feature} declares advisory_nonexecuting but names no workflow enum value")
            continue
        for value in workflows:
            if value not in allowed:
                errors.append(f"{feature} workflow {value!r} is not in the advisory enum")
    return errors


def assert_representable(features_dir: Path | None = None) -> None:
    errors = representability_errors(features_dir)
    if errors:
        raise ValueError("; ".join(errors))
