"""Read-only engine tools for MCP and the console ask box. No classification (BR-064)."""

from __future__ import annotations

from typing import Any

from packages.config.catalog import find_in_text, lookup

PREPARER = "preparer_1"

WRITE_MARKERS = (
    "acknowledge",
    "contest",
    "delete",
    "dispose",
    "allocate",
    "release",
    "recall",
    "submit",
    "write",
    "update",
    "merge",
)

TOOLS: tuple[dict[str, Any], ...] = (
    {
        "name": "get_evidence_pack",
        "description": "Read the engine pack for a catalog batch, case, or event id. Advisory only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Catalog id such as NCB204-B24071"},
                "workflow": {"type": "string", "description": "batch, pv, or supply"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_evidence_item",
        "description": "Read one evidence item from a loaded pack. Does not change quality status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "record_id": {"type": "string"},
                "request_id": {"type": "string"},
            },
            "required": ["record_id", "request_id"],
        },
    },
    {
        "name": "explain_abstention",
        "description": "List abstentions the engine already emitted for a catalog id.",
        "inputSchema": {
            "type": "object",
            "properties": {"entity_id": {"type": "string"}},
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_inject_coverage",
        "description": "Read inject coverage proof (rules, tests, challenge evidence). Not a work queue.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_graph_neighbourhood",
        "description": (
            "Read the bounded relation-graph neighbourhood for a catalog batch, case, or event id. "
            "Per-run projection from RELATIONSHIP_MODEL.csv. Not a system of record. Advisory only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Catalog id such as NCB204-B24071"},
                "workflow": {"type": "string", "description": "batch, pv, or supply"},
            },
            "required": ["entity_id"],
        },
    },
)


def tool_is_read_only(name: str, description: str = "") -> bool:
    blob = f"{name} {description}".casefold()
    return not any(marker in blob for marker in WRITE_MARKERS)


def approved_tools() -> list[dict[str, Any]]:
    return [dict(item) for item in TOOLS if tool_is_read_only(str(item["name"]), str(item.get("description") or ""))]


def _workflow_for(entity_id: str, workflow: str = "") -> str:
    wanted = (workflow or "").strip().casefold()
    if wanted in {"batch", "pv", "supply"}:
        return wanted
    found = lookup("batch", entity_id) or lookup("pv", entity_id) or lookup("supply", entity_id)
    if found is not None:
        return found.workflow
    hit = find_in_text(entity_id)
    return hit.workflow if hit is not None else "batch"


def _pack_for(entity_id: str, *, workflow: str = "", user: str) -> dict[str, Any]:
    from services.api.handlers import handle

    wf = _workflow_for(entity_id, workflow)
    return handle("GET", f"/api/workflows/{wf}/{entity_id}", user=PREPARER or user)


def _named_values(rows: Any, *keys: str, limit: int = 3) -> list[str]:
    found: list[str] = []
    for item in rows or []:
        if not isinstance(item, dict):
            continue
        for key in keys:
            value = str(item.get(key) or "").strip()
            if value and value not in found:
                found.append(value)
                break
        if len(found) >= limit:
            break
    return found


def _summarize_pack(pack: dict[str, Any]) -> dict[str, Any]:
    from services.api.handlers import outstanding_critical, pack_product

    request_id = str(pack.get("request_id") or "")
    remaining = outstanding_critical(request_id) if request_id else []
    cases = pack.get("case_ids") or []
    entity = str(
        pack.get("batch_id") or (cases[0] if cases else "") or pack.get("event_id") or ""
    )
    return {
        "entity": entity,
        "product": pack_product(pack) or str(pack.get("product") or ""),
        "workflow": str(pack.get("workflow") or ""),
        "request_id": request_id,
        "readiness_state": str(pack.get("readiness_state") or ""),
        "execution_status": str(pack.get("execution_status") or ""),
        "findings": len(pack.get("findings") or []),
        "contradictions": len(pack.get("contradictions") or []),
        "gaps": len(pack.get("gaps") or []),
        "abstentions": len(pack.get("abstentions") or []),
        "remaining_critical": remaining,
        "disputed": _named_values(pack.get("contradictions"), "topic", "statement"),
        "missing": _named_values(pack.get("gaps"), "packet_item", "gap_type", "subject_id"),
        "held": _named_values(pack.get("abstentions"), "reason_code", "code", "subject_id"),
        "advisory": True,
        "disposition": False,
    }


def _summarize_neighbourhood(entity_id: str, projection: dict[str, Any]) -> dict[str, Any]:
    visited = [str(item) for item in (projection.get("visited") or []) if item]
    frontier = [str(item) for item in (projection.get("frontier") or []) if item]
    return {
        "entity": entity_id,
        "seed": str(projection.get("seed") or ""),
        "store": str(projection.get("store") or "in_process"),
        "source": str(projection.get("source") or "data/RELATIONSHIP_MODEL.csv"),
        "hops_used": int(projection.get("hops_used") or 0),
        "max_hops": int(projection.get("max_hops") or 0),
        "visited_count": len(visited),
        "visited": visited[:16],
        "frontier_count": len(frontier),
        "frontier": frontier[:8],
        "traversal_incomplete": bool(projection.get("traversal_incomplete")),
        "advisory": True,
        "disposition": False,
    }


def _projection_for(pack: dict[str, Any], entity_id: str) -> dict[str, Any]:
    review = pack.get("human_review") if isinstance(pack.get("human_review"), dict) else {}
    projection = review.get("graph_projection") if isinstance(review.get("graph_projection"), dict) else {}
    if projection.get("seed") or projection.get("visited"):
        return projection
    as_of = str(pack.get("as_of") or "").strip()
    if not as_of:
        return {}
    from packages.graph.builder import build_projection, graph_summary

    return graph_summary(build_projection(as_of=as_of), entity_id, as_of=as_of)


def call_tool(name: str, arguments: dict[str, Any] | None, *, user: str) -> dict[str, Any]:
    arguments = dict(arguments or {})
    if not tool_is_read_only(name):
        return {"ok": False, "error": "WRITE_TOOL_REFUSED", "tool": name}
    if name == "get_evidence_pack":
        entity_id = str(arguments.get("entity_id") or "").strip()
        if not entity_id:
            return {"ok": False, "error": "entity_id is required"}
        response = _pack_for(entity_id, workflow=str(arguments.get("workflow") or ""), user=user)
        if response.get("status") != 200:
            return {"ok": False, "error": (response.get("payload") or {}).get("error") or response}
        pack = response["payload"]
        from services.api.handlers import list_sessions

        return {"ok": True, "tool": name, "summary": _summarize_pack(pack), "sessions": list_sessions()}
    if name == "get_evidence_item":
        from services.api.handlers import get_pack

        record_id = str(arguments.get("record_id") or "").strip()
        request_id = str(arguments.get("request_id") or "").strip()
        pack = get_pack(request_id) or {}
        item = next(
            (
                row
                for row in pack.get("evidence") or []
                if isinstance(row, dict) and str(row.get("record_id") or "") == record_id
            ),
            None,
        )
        if item is None:
            return {"ok": False, "error": "Evidence item is not in a loaded pack"}
        return {
            "ok": True,
            "tool": name,
            "record_id": item.get("record_id"),
            "source": item.get("source"),
            "authority": item.get("authority"),
        }
    if name == "explain_abstention":
        entity_id = str(arguments.get("entity_id") or "").strip()
        response = _pack_for(entity_id, user=user)
        if response.get("status") != 200:
            return {"ok": False, "error": (response.get("payload") or {}).get("error") or response}
        pack = response["payload"]
        rows = []
        for item in pack.get("abstentions") or []:
            if isinstance(item, dict):
                rows.append(
                    {
                        "reason_code": item.get("reason_code"),
                        "subject_id": item.get("subject_id"),
                        "observed_unit": item.get("observed_unit"),
                        "spec_unit": item.get("spec_unit"),
                    }
                )
        return {"ok": True, "tool": name, "entity": entity_id, "abstentions": rows}
    if name == "get_inject_coverage":
        from services.api.inject_coverage import list_inject_coverage

        rows = list_inject_coverage()
        return {
            "ok": True,
            "tool": name,
            "counts": {
                "covered": sum(1 for item in rows if item.get("coverage") == "covered"),
                "artefact": sum(1 for item in rows if item.get("coverage") == "artefact"),
                "uncovered": sum(1 for item in rows if item.get("coverage") == "uncovered"),
            },
        }
    if name == "get_graph_neighbourhood":
        entity_id = str(arguments.get("entity_id") or "").strip()
        if not entity_id:
            return {"ok": False, "error": "entity_id is required"}
        response = _pack_for(entity_id, workflow=str(arguments.get("workflow") or ""), user=user)
        if response.get("status") != 200:
            return {"ok": False, "error": (response.get("payload") or {}).get("error") or response}
        pack = response["payload"]
        projection = _projection_for(pack, entity_id)
        if not projection:
            return {"ok": False, "error": "No relation-graph projection for that id"}
        return {"ok": True, "tool": name, "summary": _summarize_neighbourhood(entity_id, projection)}
    return {"ok": False, "error": "UNKNOWN_TOOL", "tool": name}
