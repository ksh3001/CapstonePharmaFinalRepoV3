"""Workflow B PV intake. Classification types are constructed only here (MR-5)."""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from packages.config.language import MINIMUM_CRITERIA, VALIDATED_LANGUAGES
from packages.domain.batch import iter_records, iter_text_blobs
from packages.domain.duplicates import find_duplicate_candidates
from packages.domain.evidence import EvidenceItem, build_evidence_item
from packages.domain.types import Abstention, Contradiction, Gap
from packages.ontology.instructions import (
    contains_embedded_instruction,
    facts_excluding_instructions,
    flatten_strings,
)
from packages.ontology.terminology import retain_coding
from packages.ontology.trust import trust_for_document

_STATUS = re.compile(r"^\s*-\s*Status:\s*(\S+)", re.MULTILINE | re.IGNORECASE)
_PRESENT = frozenset({"yes", "true", "present", "y", "1"})
_ABSENT = frozenset({"no", "false", "absent", "n", "0"})


def infer_case_ids(fixture: dict[str, Any], requested: str = "") -> list[str]:
    found: list[str] = []
    products: list[str] = []
    for _source, record in iter_records(fixture):
        if record.get("case_id"):
            found.append(str(record["case_id"]))
        elif record.get("post_id"):
            found.append(str(record["post_id"]))
        elif record.get("product"):
            products.append(str(record["product"]))
    ids = sorted(set(found))
    if not ids:
        ids = sorted(set(products))
    if not ids:
        ids = [requested or "UNSET"]
    return ids


def _record_id(record: dict[str, Any], source: str, index: int) -> str:
    if record.get("case_id") and record.get("channel"):
        return f"{record['case_id']}:{record['channel']}"
    if record.get("case_id") and record.get("meddra_version"):
        return f"{record['case_id']}:MedDRA:{record['meddra_version']}"
    if record.get("case_id"):
        return str(record["case_id"])
    if record.get("post_id"):
        return str(record["post_id"])
    if record.get("product") and record.get("source") and "listed" in record:
        return f"{record['product']}:{record['source']}"
    if record.get("product") and record.get("market"):
        return f"{record['product']}:{record['market']}"
    if record.get("model_id") and record.get("slice"):
        return f"{record['model_id']}:{record['slice']}"
    if record.get("alias"):
        return str(record["alias"])
    if record.get("case_a") and record.get("case_b"):
        return f"{record['case_a']}:{record['case_b']}"
    if record.get("terminology") and record.get("version"):
        return f"{record['terminology']}:{record['version']}"
    return f"{source}:{index}"


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def _document_status(text: str) -> str:
    match = _STATUS.search(text or "")
    if match:
        return match.group(1).strip()
    return "unknown"


def _security_finding(source: str, record_id: str) -> dict[str, Any]:
    return {
        "finding_id": f"SEC-INSTR-{record_id}",
        "kind": "embedded_instruction",
        "subject_id": record_id,
        "source": source,
        "statement": "Embedded instruction detected; content treated as data and excluded from reasoning.",
        "trust_status": trust_for_document(status="effective", hash_ok=True, contains_instruction=True),
        "evidence_refs": [record_id],
    }


def _language_in_scope(language: str) -> bool:
    return (language or "").strip().casefold() in VALIDATED_LANGUAGES


def _criterion_state(value: Any) -> str:
    text = str(value or "").strip().casefold()
    if text in _PRESENT:
        return "present"
    if text in _ABSENT:
        return "absent"
    return "unverifiable"


def classify_listedness_source(source: str, market: str = "") -> tuple[str, str]:
    text = (source or "").strip()
    folded = text.casefold()
    if folded.startswith("ib"):
        return "IB", "IB"
    if "ccds" in folded:
        return "CCDS", "CCDS"
    if "local label" in folded:
        token = text.split()[0] if text.split() else "unspecified"
        return "local_label", token
    if market:
        return "local_label", str(market)
    return "unspecified", "unspecified"


def _sort_maps(items: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: tuple(str(item.get(key) or "") for key in keys))


def _aliases(rows: list[tuple[str, dict[str, Any]]]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for source, record in rows:
        if _source_name(source) == "product_master_aliases.csv":
            alias = str(record.get("alias") or "")
            canonical = str(record.get("canonical_product") or "")
            if alias and canonical:
                aliases[alias] = canonical
                aliases[alias.upper()] = canonical
    return aliases


def _subgroup_limitations(model_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in model_rows:
        model_id = str(record.get("model_id") or "")
        if model_id:
            grouped[model_id].append(record)
    limitations: list[dict[str, Any]] = []
    for model_id, records in grouped.items():
        parsed: list[tuple[Decimal, dict[str, Any]]] = []
        for record in records:
            try:
                parsed.append((Decimal(str(record.get("value") or "")), record))
            except InvalidOperation:
                continue
        if len(parsed) < 2:
            continue
        best_value, best = max(parsed, key=lambda item: item[0])
        kind = "language_scope" if model_id.startswith("PV-NER") else "cohort_underrepresentation"
        for value, record in parsed:
            if value >= best_value:
                continue
            subgroup = str(record.get("slice") or "")
            reference = str(best.get("slice") or "")
            metric = str(record.get("metric") or "")
            limitation_id = f"LIM-{model_id}-{subgroup}"
            limitations.append(
                {
                    "limitation_id": limitation_id,
                    "kind": kind,
                    "subgroup": subgroup,
                    "compared_to": reference,
                    "model_id": model_id,
                    "metric": metric,
                    "subgroup_value": str(record.get("value") or ""),
                    "reference_value": str(best.get("value") or ""),
                    "statement": (
                        f"{subgroup} is under-represented relative to {reference} on "
                        f"{model_id} {metric} ({record.get('value')} vs {best.get('value')}). "
                        "Statistics from this cohort do not generalise beyond the represented population."
                    ),
                }
            )
    return _sort_maps(limitations, ("limitation_id",))


def _social_facts(record: dict[str, Any]) -> dict[str, Any]:
    criteria = []
    for name in MINIMUM_CRITERIA:
        if name in record:
            evidence = str(record.get(name) or "")
            state = _criterion_state(record.get(name))
        else:
            evidence = "not_in_source"
            state = "unverifiable"
        criteria.append({"criterion": name, "state": state, "evidence": evidence})
    return {
        "case_id": str(record.get("post_id") or ""),
        "channel": "social_media",
        "verbatim_text": str(record.get("text") or ""),
        "country": str(record.get("country") or ""),
        "authenticity": "uncertain",
        "minimum_criteria": criteria,
        "validity": "undetermined",
        "extraction_status": "source_record",
    }


def reconcile_pv(
    fixture: dict[str, Any],
    *,
    case_ids: list[str],
    as_of: str,
) -> dict[str, Any]:
    evidence: list[EvidenceItem] = []
    abstentions: list[Abstention] = []
    gaps: list[Gap] = []
    findings: list[dict[str, Any]] = []
    usable: list[tuple[str, str, dict[str, Any]]] = []
    finding_sources: set[str] = set()

    for index, (source, record) in enumerate(iter_records(fixture)):
        rid = _record_id(record, source, index)
        injected = contains_embedded_instruction(flatten_strings(record))
        facts = facts_excluding_instructions(record)
        if injected:
            facts["trust_status"] = "untrusted"
            facts["cited"] = True
            if source not in finding_sources:
                findings.append(_security_finding(source, rid))
                finding_sources.add(source)
        built = build_evidence_item(
            source=source,
            record_id=rid,
            authority=str(record.get("authority") or record.get("source") or "challenge-package"),
            effective_at=record.get("awareness_date") or record.get("receipt") or record.get("effective_date"),
            as_of=as_of,
            facts=facts,
        )
        if isinstance(built, Abstention):
            abstentions.append(built)
            continue
        evidence.append(built)
        if not injected:
            usable.append((source, rid, record))

    for source, text in iter_text_blobs(fixture):
        rid = _source_name(source)
        injected = contains_embedded_instruction(text)
        status = _document_status(text)
        trust = trust_for_document(status=status, hash_ok=True, contains_instruction=injected)
        if injected and source not in finding_sources:
            findings.append(_security_finding(source, rid))
            finding_sources.add(source)
        built = build_evidence_item(
            source=source,
            record_id=rid,
            authority="challenge-package",
            effective_at=None,
            as_of=as_of,
            facts={
                "kind": "retrieved_document",
                "cited": True,
                "trust_status": trust,
                "document_status": status,
            },
        )
        if isinstance(built, Abstention):
            abstentions.append(built)
            continue
        evidence.append(built)

    icsr: list[tuple[str, dict[str, Any]]] = []
    receipts: list[tuple[str, dict[str, Any]]] = []
    events: list[tuple[str, dict[str, Any]]] = []
    listed_rows: list[tuple[str, dict[str, Any]]] = []
    label_rows: list[tuple[str, dict[str, Any]]] = []
    social_rows: list[tuple[str, dict[str, Any]]] = []
    model_rows: list[dict[str, Any]] = []
    raw_records = [(source, record) for source, _rid, record in usable]
    aliases = _aliases(raw_records)

    for source, rid, record in usable:
        name = _source_name(source)
        if name == "icsr_cases.csv":
            icsr.append((rid, record))
        elif name == "safety_receipts.csv":
            receipts.append((rid, record))
        elif name == "adverse_events.csv":
            events.append((rid, record))
        elif name == "listedness_sources.csv":
            listed_rows.append((rid, record))
        elif name == "product_labels.csv":
            label_rows.append((rid, record))
        elif name == "social_listening.csv":
            social_rows.append((rid, record))
        elif name == "model_performance.csv":
            model_rows.append(record)

    limitations = _subgroup_limitations(model_rows)
    limitation_by_slice = {
        (item["model_id"], item["subgroup"]): item["limitation_id"] for item in limitations
    }
    for item in evidence:
        facts = item.get("facts") or {}
        key = (str(facts.get("model_id") or ""), str(facts.get("slice") or ""))
        if key in limitation_by_slice:
            facts["limitations"] = [limitation_by_slice[key]]

    source_facts: list[dict[str, Any]] = []
    for rid, record in icsr:
        language = str(record.get("language") or "")
        in_scope = _language_in_scope(language)
        if not in_scope:
            abstentions.append(
                Abstention(
                    reason_code="language_out_of_scope",
                    subject_id=str(record.get("case_id") or rid),
                    language=language,
                    statement=(
                        f"Case language {language} is outside validated extraction scope "
                        "(English, German). Extraction abstained; human translation required."
                    ),
                )
            )
        source_facts.append(
            {
                "case_id": str(record.get("case_id") or rid),
                "source_channel": str(record.get("source") or ""),
                "product": str(record.get("product") or ""),
                "event": str(record.get("event") or ""),
                "country": str(record.get("country") or ""),
                "awareness_date": str(record.get("awareness_date") or ""),
                "language": language,
                "patient_key": str(record.get("patient_key") or ""),
                "extraction_status": "in_scope" if in_scope else "abstained",
            }
        )
    for rid, record in social_rows:
        facts = _social_facts(record)
        source_facts.append(facts)
        if not any(item.get("state") == "present" for item in facts["minimum_criteria"]):
            gaps.append(
                Gap(
                    gap_type="minimum_criteria_undetermined",
                    subject_id=str(record.get("post_id") or rid),
                    statement="Validity is undetermined; no criterion was inferred beyond its own evidence.",
                )
            )

    clocks: list[dict[str, Any]] = []
    for rid, record in receipts:
        clocks.append(
            {
                "case_id": str(record.get("case_id") or ""),
                "clock_kind": "receipt",
                "channel": str(record.get("channel") or ""),
                "timestamp": str(record.get("receipt") or ""),
                "source": "data/safety_receipts.csv",
                "record_id": rid,
            }
        )
    for rid, record in icsr:
        clocks.append(
            {
                "case_id": str(record.get("case_id") or ""),
                "clock_kind": "awareness",
                "channel": "icsr_awareness",
                "timestamp": str(record.get("awareness_date") or ""),
                "source": "data/icsr_cases.csv",
                "record_id": rid,
            }
        )

    terminology: list[dict[str, Any]] = []
    for rid, record in events:
        coding = retain_coding(
            str(record.get("pt") or record.get("verbatim") or ""),
            "MedDRA",
            str(record.get("meddra_version") or ""),
        )
        terminology.append(
            {
                "case_id": str(record.get("case_id") or ""),
                "term": coding.term,
                "dictionary": coding.dictionary,
                "version": coding.version,
                "verbatim": str(record.get("verbatim") or ""),
                "record_id": rid,
            }
        )

    cases_for_dup = [record for _rid, record in icsr]
    duplicate_candidates = find_duplicate_candidates(cases_for_dup, product_aliases=aliases)

    listedness: list[dict[str, Any]] = []
    listed_values: dict[str, set[str]] = defaultdict(set)
    listed_refs: dict[str, list[str]] = defaultdict(list)
    for rid, record in listed_rows:
        source_class, jurisdiction = classify_listedness_source(str(record.get("source") or ""))
        listed = str(record.get("listed") or "")
        product = str(record.get("product") or "")
        listedness.append(
            {
                "product": product,
                "jurisdiction": jurisdiction,
                "source_class": source_class,
                "source_document": str(record.get("source") or ""),
                "risk": str(record.get("risk") or ""),
                "listed": listed,
                "record_id": rid,
            }
        )
        if listed:
            listed_values[product].add(listed)
            listed_refs[product].append(rid)
    for rid, record in label_rows:
        source_class, jurisdiction = classify_listedness_source("", market=str(record.get("market") or ""))
        listedness.append(
            {
                "product": str(record.get("product") or ""),
                "jurisdiction": jurisdiction,
                "source_class": source_class,
                "source_document": f"{record.get('market')} local label v{record.get('version')}",
                "label_version": str(record.get("version") or ""),
                "risk_text": str(record.get("risk_text") or ""),
                "record_id": rid,
            }
        )

    contradictions: list[Contradiction] = []
    for product, values in listed_values.items():
        if len(values) > 1:
            contradictions.append(
                Contradiction(
                    topic="listedness",
                    source="data/listedness_sources.csv",
                    record_id=listed_refs[product][0],
                    values=sorted(values),
                    product=product,
                    evidence_refs=listed_refs[product],
                    statement="Listedness sources disagree; listed flags are retained as context only.",
                )
            )

    discovered = infer_case_ids(fixture, requested=case_ids[0] if case_ids else "")
    reviews = ["safety_physician"]
    if any(item.reason_code == "language_out_of_scope" for item in abstentions):
        reviews.append("language_translation")
    if listedness:
        reviews.append("listedness_review")
    if social_rows:
        reviews.append("social_media_validity")
    if limitations:
        reviews.append("subgroup_limitation_review")

    return {
        "case_ids": discovered,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "abstentions": abstentions,
        "source_facts": _sort_maps(source_facts, ("case_id", "channel", "source_channel")),
        "duplicate_candidates": duplicate_candidates,
        "clock_evidence": _sort_maps(clocks, ("case_id", "channel", "timestamp")),
        "terminology": _sort_maps(terminology, ("case_id", "version", "term")),
        "listedness_context": _sort_maps(listedness, ("jurisdiction", "source_class", "source_document")),
        "required_reviews": sorted(set(reviews)),
        "security_findings": findings,
        "subgroup_limitations": limitations,
    }
