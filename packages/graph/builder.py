"""Deterministic graph builder. Rebuilt from CSV each run; never a store."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

from packages.config.paths import synthetic_dir
from packages.graph.projection import DEFAULT_HOPS, HARD_CAP, OrphanEdgeError, Projection, UngroundedEdgeError
from packages.graph.types import Provenance
from packages.ontology.trust import can_ground_assertion
from packages.ontology.types import TrustStatus

MODEL_NAME = "RELATIONSHIP_MODEL.csv"
SOURCE_LABEL = "data/RELATIONSHIP_MODEL.csv"

_SKIP_PARENT_MARKERS = ("*", "/")
_NON_CSV_PARENTS = frozenset({"injects.json"})

_ROW_KEYS: dict[str, tuple[str, ...]] = {
    "access_cache.csv": ("user",),
    "adverse_events.csv": ("case_id",),
    "batches.csv": ("batch_id",),
    "consents.csv": ("consent_id",),
    "continuity_requirements.csv": ("workflow",),
    "demand_forecast.csv": ("channel", "product"),
    "duplicate_candidates.csv": ("case_a", "case_b"),
    "eligibility_evidence.csv": ("subject_id",),
    "environmental_monitoring.csv": ("sample_id",),
    "icsr_cases.csv": ("case_id",),
    "inject_evidence_map.csv": ("inject_id",),
    "inventory.csv": ("product", "market"),
    "knowledge_catalog.csv": ("doc_id",),
    "lab_results.csv": ("result_id",),
    "listedness_sources.csv": ("product", "source"),
    "market_authorisations.csv": ("product", "market"),
    "material_genealogy.csv": ("material_lot",),
    "microbiology_results.csv": ("sample_id",),
    "model_performance.csv": ("model_id", "slice", "metric"),
    "model_usage.csv": ("workflow",),
    "oos_investigations.csv": ("investigation_id",),
    "processing_events.csv": ("event_id",),
    "product_complaints.csv": ("complaint_id",),
    "product_labels.csv": ("product", "market"),
    "protocol_versions.csv": ("trial_id", "version"),
    "recall_candidates.csv": ("lot",),
    "release_packets.csv": ("batch_id", "packet_item"),
    "safety_receipts.csv": ("case_id", "channel"),
    "shipments.csv": ("shipment_id",),
    "site_approvals.csv": ("site_id",),
    "subjects.csv": ("subject_id",),
    "temperature_loggers.csv": ("logger", "timestamp"),
    "users_entitlements.csv": ("user",),
    "warehouse_movements.csv": ("movement_id",),
}

_KIND: dict[str, str] = {
    "adverse_events.csv": "reaction",
    "batches.csv": "batch",
    "consents.csv": "document",
    "duplicate_candidates.csv": "case",
    "environmental_monitoring.csv": "equipment",
    "icsr_cases.csv": "case",
    "knowledge_catalog.csv": "document",
    "lab_results.csv": "test_result",
    "material_genealogy.csv": "material",
    "microbiology_results.csv": "test_result",
    "oos_investigations.csv": "test_result",
    "product_complaints.csv": "document",
    "product_labels.csv": "document",
    "protocol_versions.csv": "document",
    "release_packets.csv": "document",
    "recall_candidates.csv": "material",
    "safety_receipts.csv": "case",
    "shipments.csv": "shipment",
    "temperature_loggers.csv": "equipment",
    "warehouse_movements.csv": "material",
}

_SEED_DATASETS = (
    "batches.csv",
    "icsr_cases.csv",
    "shipments.csv",
    "subjects.csv",
    "material_genealogy.csv",
    "recall_candidates.csv",
)

_EFFECTIVE_FIELDS = (
    "effective",
    "effective_time",
    "effective_date",
    "manufacture_date",
    "awareness_date",
    "timestamp",
    "receipt",
    "cached_until",
)


def build_projection(
    *,
    as_of: str,
    data_dir: Path | None = None,
) -> Projection:
    """Rebuild the in-process graph from RELATIONSHIP_MODEL.csv and sibling CSVs."""
    retrieved = (as_of or "").strip()
    if not retrieved:
        raise ValueError("graph projection requires as_of")
    root = data_dir if data_dir is not None else synthetic_dir() / "data"
    model_path = root / MODEL_NAME
    relationships = _load_relationships(model_path)
    datasets = _datasets_for(relationships)
    tables = {name: _load_table(root / name) for name in datasets if (root / name).is_file()}
    file_hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in tables}
    graph = Projection()
    node_rows: dict[str, tuple[str, dict[str, str]]] = {}
    for dataset in sorted(tables):
        for row in tables[dataset]:
            node_id = _node_id(dataset, row)
            if node_id in node_rows:
                continue
            provenance = _provenance(
                dataset,
                node_id,
                row,
                retrieved_at=retrieved,
                digest=file_hashes[dataset],
            )
            graph.add_node(
                node_id,
                _kind_for(dataset),
                provenance,
                trust_status=_trust_for(dataset, row),
                facts=dict(row),
            )
            node_rows[node_id] = (dataset, row)
    by_field = _index_by_field(node_rows)
    seen_edges: set[tuple[str, str, str]] = set()
    for rel in relationships:
        child_dataset = rel["child_dataset"]
        parent_dataset = rel["parent_dataset"]
        child_field = rel["child_field"]
        parent_field = rel["parent_field"]
        if child_dataset not in tables:
            continue
        if _skip_parent(parent_dataset, parent_field):
            continue
        if parent_dataset not in tables:
            continue
        if child_dataset == "duplicate_candidates.csv" and child_field == "case_a":
            _link_duplicates(
                graph,
                tables[child_dataset],
                by_field,
                retrieved_at=retrieved,
                digest=file_hashes[child_dataset],
                seen=seen_edges,
            )
            continue
        if child_dataset == "duplicate_candidates.csv":
            continue
        parent_index = by_field.get(parent_dataset, {}).get(parent_field, {})
        for row in tables[child_dataset]:
            child_value = (row.get(child_field) or "").strip()
            if not child_value:
                continue
            child_id = _node_id(child_dataset, row)
            parents = parent_index.get(child_value) or ()
            if not parents:
                continue
            kind = _edge_kind(child_dataset, child_field, row)
            edge_prov = _provenance(
                child_dataset,
                f"{child_id}->{kind}",
                row,
                retrieved_at=retrieved,
                digest=file_hashes[child_dataset],
            )
            for parent_id in parents:
                source, target = _endpoints(kind, child_dataset, child_id, parent_id)
                _try_add_edge(graph, source, target, kind, edge_prov, seen_edges)
                if kind == "MONITORED_BY":
                    _try_add_edge(graph, target, source, kind, edge_prov, seen_edges)
    return graph


def graph_summary(
    graph: Projection,
    entity_id: str = "",
    *,
    as_of: str = "",
    max_hops: int = DEFAULT_HOPS,
) -> dict[str, Any]:
    seed = seed_for(graph, entity_id)
    if seed:
        walked = graph.traverse(seed, max_hops=max_hops, as_of=as_of)
        visited = list(walked.visited)
        frontier = list(walked.frontier)
        incomplete = walked.traversal_incomplete
        hops_used = walked.hops_used
        hops = walked.max_hops
    else:
        visited = []
        frontier = []
        incomplete = bool(entity_id)
        hops_used = 0
        hops = min(max(max_hops, 0), HARD_CAP)
    return {
        "store": "in_process",
        "source": SOURCE_LABEL,
        "node_count": len(graph.node_ids()),
        "edge_count": len(graph.edges()),
        "seed": seed,
        "visited": visited,
        "frontier": frontier,
        "traversal_incomplete": incomplete,
        "hops_used": hops_used,
        "max_hops": hops,
    }


def seed_for(graph: Projection, entity_id: str) -> str:
    needle = (entity_id or "").strip()
    if not needle:
        return ""
    matches = [node_id for node_id in graph.node_ids() if _entity_in_node(node_id, needle)]
    if not matches:
        return ""
    preferred = [node_id for node_id in matches if node_id.split(":", 1)[0] in _SEED_DATASETS]
    pool = preferred or matches
    exact = [node_id for node_id in pool if node_id.endswith(":" + needle)]
    return (exact or pool)[0]


def _entity_in_node(node_id: str, entity_id: str) -> bool:
    rest = node_id.split(":", 1)[1] if ":" in node_id else node_id
    if rest == entity_id or rest.startswith(entity_id + ":") or rest.endswith(":" + entity_id):
        return True
    return entity_id in rest.split(":")


def _load_relationships(path: Path) -> list[dict[str, str]]:
    rows = _read_csv(path)
    return sorted(
        rows,
        key=lambda row: (
            row.get("child_dataset") or "",
            row.get("child_field") or "",
            row.get("parent_dataset") or "",
            row.get("parent_field") or "",
        ),
    )


def _datasets_for(relationships: list[dict[str, str]]) -> list[str]:
    names: set[str] = set()
    for row in relationships:
        child = row.get("child_dataset") or ""
        parent = row.get("parent_dataset") or ""
        if child.endswith(".csv"):
            names.add(child)
        if parent.endswith(".csv") and not _skip_parent(parent, row.get("parent_field") or ""):
            names.add(parent)
    return sorted(names)


def _load_table(path: Path) -> list[dict[str, str]]:
    return _read_csv(path)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def _skip_parent(parent_dataset: str, parent_field: str) -> bool:
    if parent_field == "__filename__":
        return True
    if parent_dataset in _NON_CSV_PARENTS:
        return True
    if not parent_dataset.endswith(".csv"):
        return True
    return any(marker in parent_dataset for marker in _SKIP_PARENT_MARKERS)


def _node_id(dataset: str, row: dict[str, str]) -> str:
    keys = _ROW_KEYS.get(dataset)
    if keys:
        parts = [(row.get(key) or "").strip() for key in keys]
        if all(parts):
            return dataset + ":" + ":".join(parts)
    digest = hashlib.sha256("|".join(f"{key}={row[key]}" for key in sorted(row)).encode("utf-8")).hexdigest()[:16]
    return f"{dataset}:{digest}"


def _kind_for(dataset: str) -> str:
    if dataset in _KIND:
        return _KIND[dataset]
    return dataset.removesuffix(".csv")


def _trust_for(dataset: str, row: dict[str, str]) -> TrustStatus:
    status = (row.get("status") or row.get("trust") or "").strip().lower()
    if status == "superseded":
        return "superseded"
    if status in {"draft", "retired", "unknown", "untrusted"}:
        return "untrusted"
    if dataset == "knowledge_catalog.csv" and (row.get("trust") or "").strip().lower() in {
        "untrusted",
        "reduced_integrity",
    }:
        return "untrusted"
    return "trusted"


def _provenance(
    dataset: str,
    record_id: str,
    row: dict[str, str],
    *,
    retrieved_at: str,
    digest: str,
) -> Provenance:
    effective = ""
    for field in _EFFECTIVE_FIELDS:
        value = (row.get(field) or "").strip()
        if value:
            effective = value
            break
    return Provenance(
        source_system=f"data/{dataset}",
        record_id=record_id,
        authority="challenge-package",
        effective_time=effective or None,
        retrieved_at=retrieved_at,
        sha256=digest,
        source_preserved=True,
    )


def _index_by_field(
    node_rows: dict[str, tuple[str, dict[str, str]]],
) -> dict[str, dict[str, dict[str, list[str]]]]:
    index: dict[str, dict[str, dict[str, list[str]]]] = {}
    for node_id, (dataset, row) in node_rows.items():
        fields = index.setdefault(dataset, {})
        for field, value in row.items():
            text = (value or "").strip()
            if not text:
                continue
            fields.setdefault(field, {}).setdefault(text, []).append(node_id)
    for dataset in index:
        for field in index[dataset]:
            for value in index[dataset][field]:
                index[dataset][field][value] = sorted(index[dataset][field][value])
    return index


def _edge_kind(child_dataset: str, child_field: str, row: dict[str, str]) -> str:
    if child_dataset == "duplicate_candidates.csv":
        return "DUPLICATE_CANDIDATE_OF"
    if child_dataset == "deviations.csv" and child_field == "similarity_to":
        return "POSSIBLY_RELATED_TO"
    if child_dataset == "material_genealogy.csv" and child_field == "batch_id":
        if (row.get("relation") or "").strip().lower() == "consumed":
            return "CONSUMED"
        return "REFERENCES"
    if child_dataset == "warehouse_movements.csv" and child_field == "material_lot":
        return "CONSUMED"
    if child_dataset in {"lab_results.csv", "microbiology_results.csv", "oos_investigations.csv"}:
        return "TESTED_BY"
    if child_dataset in {
        "release_packets.csv",
        "knowledge_catalog.csv",
        "trade_documents.csv",
        "ebr_steps.csv",
        "protocol_versions.csv",
    }:
        return "DOCUMENTED_BY"
    if child_dataset in {"environmental_monitoring.csv", "temperature_loggers.csv"} or child_field == "logger":
        return "MONITORED_BY"
    if child_dataset in {"adverse_events.csv", "product_complaints.csv", "safety_receipts.csv"}:
        return "REPORTED_IN"
    return "REFERENCES"


def _endpoints(kind: str, child_dataset: str, child_id: str, parent_id: str) -> tuple[str, str]:
    if kind == "POSSIBLY_RELATED_TO":
        return child_id, parent_id
    if kind == "MONITORED_BY" and child_dataset in {"shipments.csv", "environmental_monitoring.csv"}:
        return child_id, parent_id
    return parent_id, child_id


def _link_duplicates(
    graph: Projection,
    rows: list[dict[str, str]],
    by_field: dict[str, dict[str, dict[str, list[str]]]],
    *,
    retrieved_at: str,
    digest: str,
    seen: set[tuple[str, str, str]],
) -> None:
    cases = by_field.get("icsr_cases.csv", {}).get("case_id", {})
    for row in rows:
        left = (row.get("case_a") or "").strip()
        right = (row.get("case_b") or "").strip()
        left_ids = cases.get(left) or ()
        right_ids = cases.get(right) or ()
        if not left_ids or not right_ids:
            continue
        provenance = _provenance(
            "duplicate_candidates.csv",
            f"duplicate_candidates.csv:{left}:{right}",
            row,
            retrieved_at=retrieved_at,
            digest=digest,
        )
        for source in left_ids:
            for target in right_ids:
                _try_add_edge(graph, source, target, "DUPLICATE_CANDIDATE_OF", provenance, seen)
                _try_add_edge(graph, target, source, "DUPLICATE_CANDIDATE_OF", provenance, seen)


def _try_add_edge(
    graph: Projection,
    source: str,
    target: str,
    kind: str,
    provenance: Provenance,
    seen: set[tuple[str, str, str]],
) -> None:
    if source == target:
        return
    key = (source, kind, target)
    if key in seen:
        return
    try:
        src = graph.node(source)
    except KeyError:
        return
    if not can_ground_assertion(src.trust_status):
        return
    try:
        graph.add_edge(source, target, kind, provenance)
    except (UngroundedEdgeError, OrphanEdgeError, KeyError):
        return
    seen.add(key)


__all__ = [
    "MODEL_NAME",
    "SOURCE_LABEL",
    "build_projection",
    "graph_summary",
    "seed_for",
]
