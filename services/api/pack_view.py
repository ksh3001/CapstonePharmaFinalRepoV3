"""Format a pack for the console. Presentation only — no classification (BR-064)."""

from __future__ import annotations

import json
from html import escape
from typing import Any
from urllib.parse import quote

from packages.config.catalog import picker_entities, product_for
from packages.config.runtime import inference_allowed, llm_enabled
from services.api.graphics import render_pack_graphics
from services.api.handlers import critical_record_ids, get_pack, opened_record_ids, outstanding_critical

EXTRA_TABLES = (
    ("applicable_documents", "Applicable documents", ("document_id", "status", "source", "record_id")),
    ("source_facts", "Source facts", ("case_id", "source_channel", "product", "event", "country", "awareness_date", "language")),
    ("clock_evidence", "Clock evidence", ("case_id", "clock_kind", "channel", "timestamp", "source", "record_id")),
    ("listedness_context", "Listedness context", ("product", "source", "listed", "market", "record_id")),
    ("duplicate_candidates", "Duplicate candidates", ("case_a", "case_b", "score", "status", "record_id")),
    ("terminology", "Terminology", ("case_id", "term", "dictionary", "version", "verbatim", "record_id")),
    ("options", "Draft options", ("option_id", "status", "channel", "product", "trade_off")),
    ("constraints", "Constraints", ("constraint_id", "channel", "note")),
    ("quality_holds", "Quality holds", ("hold_id", "shipment_id", "quality_status", "lots", "record_id")),
)


def _items(pack: dict[str, Any], key: str) -> list[Any]:
    return list(pack.get(key) or [])


def evidence_href(record_id: str, request_id: str = "") -> str:
    href = "/evidence/" + quote(record_id, safe="")
    if request_id:
        href += "?request_id=" + quote(request_id, safe="")
    return href


def _cell(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, (list, dict)):
        return escape(json.dumps(value, ensure_ascii=False, default=str))
    return escape(str(value))


def _open_link(record_id: str, request_id: str, *, label: str | None = None) -> str:
    if not record_id:
        return "—"
    href = evidence_href(record_id, request_id)
    shown = escape(label or record_id)
    return (
        f'<a class="evidence-link" href="{escape(href)}" data-record="{escape(record_id)}" '
        f'hx-get="{escape(href)}" hx-target="#evidence-drawer" hx-swap="innerHTML">{shown}</a>'
    )


def _viewed_box(record_id: str, request_id: str, *, slot: str = "") -> str:
    if not record_id or not request_id:
        return ""
    href = evidence_href(record_id, request_id)
    box_id = "viewed-" + quote(f"{request_id}|{record_id}|{slot}", safe="")
    checked = " checked" if record_id in opened_record_ids(request_id) else ""
    return (
        f'<label class="viewed" for="{escape(box_id)}">'
        f'<input id="{escape(box_id)}" class="viewed-check" type="checkbox" '
        f'data-record="{escape(record_id)}"{checked} '
        f'hx-get="{escape(href)}" hx-target="#evidence-drawer" hx-swap="innerHTML" '
        'hx-trigger="click"/>'
        '<span class="viewed-mark" aria-hidden="true"></span>'
        f'<span class="viewed-text">Viewed</span>'
        f'<span class="viewed-id">{escape(record_id)}</span>'
        "</label>"
    )


def _notes(pack: dict[str, Any]) -> list[dict[str, Any]]:
    raw = pack.get("human_review", {}).get("annotations") or []
    items = raw if isinstance(raw, list) else [raw]
    out: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            refs = [str(ref) for ref in (item.get("evidence_refs") or []) if ref]
            if text:
                out.append({"text": text, "evidence_refs": refs})
        else:
            text = str(item or "").strip()
            if text:
                out.append({"text": text, "evidence_refs": []})
    return out


def _note_for(item: dict[str, Any], notes: list[dict[str, Any]]) -> str:
    known = {str(item.get("record_id") or "")}
    known.update(str(ref) for ref in (item.get("evidence_refs") or []) if ref)
    for left_key in ("left", "right"):
        nested = item.get(left_key)
        if isinstance(nested, dict) and nested.get("record_id"):
            known.add(str(nested["record_id"]))
    chunks = []
    for note in notes:
        refs = set(note["evidence_refs"])
        if refs and known.intersection(refs):
            chunks.append(note["text"])
    if not chunks:
        return ""
    return (
        '<p class="advisory-note"><span class="note-label">Advisory note · model-generated</span>'
        f"{escape(chunks[0])}</p>"
    )


def _side(item: dict[str, Any], which: str) -> tuple[str, str, str]:
    nested = item.get(which)
    if isinstance(nested, dict):
        value = nested.get("value") or nested.get("verbatim") or nested.get("statement") or ""
        return str(value), str(nested.get("source") or ""), str(nested.get("record_id") or "")
    values = list(item.get("values") or [])
    if which == "left":
        value = item.get("statement") or (values[0] if values else "")
        return str(value), str(item.get("source") or ""), str(item.get("record_id") or "")
    value = values[1] if len(values) > 1 else item.get("notebook_state") or item.get("topic") or ""
    return str(value or ""), "", str(item.get("record_id") or "")


def _workflow_path(workflow: str) -> str:
    return {"pv_intake": "pv", "supply_options": "supply", "batch_evidence": "batch"}.get(workflow, workflow or "batch")


def render_review_actions(
    pack: dict[str, Any],
    *,
    remaining: list[str],
    oob: bool = False,
    entity_id: str = "",
    workflow: str = "",
    follow_ups: list[dict[str, Any]] | None = None,
) -> str:
    request_id = str(pack.get("request_id") or "")
    wf = _workflow_path(workflow or str(pack.get("workflow") or "batch"))
    cases = pack.get("case_ids") or []
    current = entity_id or str(
        pack.get("batch_id") or (cases[0] if cases else "") or pack.get("event_id") or ""
    )
    next_href = f"/workflows/{wf}/{current}" if current else f"/workflows/{wf}"
    oob_attr = ' hx-swap-oob="true"' if oob else ""
    rid = escape(request_id)
    if remaining:
        ack_block = (
            f'<p class="gate">Acknowledgement unavailable. Remaining critical evidence: '
            f"{escape(', '.join(remaining))}</p>"
        )
    else:
        ack = f"/api/reviews/{rid}/acknowledge"
        ack_block = (
            f'<form method="post" action="{ack}" hx-post="{ack}" hx-target="#review-actions" hx-swap="innerHTML">'
            f'<input type="hidden" name="next" value="{escape(next_href)}"/>'
            '<button type="submit" class="ack">Acknowledge (workflow event, not a signature, not a disposition)</button>'
            "</form>"
        )
    return f'<div id="review-actions"{oob_attr}>{ack_block}</div>'


def render_evidence_fragment(item: dict[str, Any], *, pack: dict[str, Any] | None = None) -> str:
    record_id = escape(str(item.get("record_id") or ""))
    integrity = item.get("integrity") or {}
    facts = item.get("facts") or {}
    fact_rows = "".join(
        f"<tr><th>{escape(str(key))}</th><td>{_cell(value)}</td></tr>" for key, value in facts.items()
    )
    facts_table = (
        f'<table class="work-table compact"><tbody>{fact_rows}</tbody></table>' if fact_rows else ""
    )
    body = (
        '<section class="region" data-region="evidence-detail">'
        f"<h2>Evidence {record_id}</h2>"
        f"<p>source={escape(str(item.get('source') or ''))}</p>"
        f"<p>authority={escape(str(item.get('authority') or ''))}</p>"
        f"<p>effective_at={escape(str(item.get('effective_at')))}</p>"
        f"<p>retrieved_at={escape(str(item.get('retrieved_at') or ''))}</p>"
        f"<p>hash={escape(str(integrity.get('sha256') or ''))}</p>"
        f"{facts_table}"
        "</section>"
    )
    if pack and pack.get("request_id"):
        remaining = outstanding_critical(str(pack["request_id"]))
        body += render_review_actions(pack, remaining=remaining, oob=True)
    return body


def _table(title: str, rows: list[Any], columns: tuple[str, ...], *, request_id: str = "") -> str:
    if not rows:
        return ""
    dict_rows = [row if isinstance(row, dict) else {"value": row} for row in rows]
    headers = list(columns)
    if dict_rows and "value" in dict_rows[0] and "value" not in headers:
        headers = ["value"]
    head = "".join(f"<th>{escape(col)}</th>" for col in headers)
    body_rows = []
    for row in dict_rows:
        cells = []
        for col in headers:
            value = row.get(col)
            if col == "record_id" and value:
                cells.append(f"<td>{_open_link(str(value), request_id)}</td>")
            else:
                cells.append(f"<td>{_cell(value)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<section class="region" data-region="{escape(title.casefold())}">'
        f"<h2>{escape(title)}</h2>"
        f'<div class="table-wrap"><table class="work-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table></div>'
        "</section>"
    )


def _findings(pack: dict[str, Any]) -> str:
    rows = []
    for item in _items(pack, "findings"):
        if isinstance(item, dict):
            rows.append(escape(str(item.get("statement") or item)))
        else:
            rows.append(escape(str(item)))
    body = "".join(f"<li>{row}</li>" for row in rows) or "<li>None</li>"
    return f'<section class="region equal" data-region="findings"><h2>Findings</h2><ul>{body}</ul></section>'


def _contradictions(pack: dict[str, Any], *, request_id: str, notes: list[dict[str, Any]]) -> str:
    cards = []
    for item in _items(pack, "contradictions"):
        if not isinstance(item, dict):
            continue
        left_v, left_s, left_r = _side(item, "left")
        right_v, right_s, right_r = _side(item, "right")
        refs = [str(ref) for ref in (item.get("evidence_refs") or []) if ref]
        if left_r and left_r not in refs:
            refs.append(left_r)
        if right_r and right_r not in refs:
            refs.append(right_r)
        viewed = "".join(
            _viewed_box(ref, request_id, slot=f"contradiction-{len(cards)}-{index}")
            for index, ref in enumerate(refs)
        )
        notebook = item.get("notebook_state")
        extra = (
            f'<p class="muted">Notebook state: {escape(str(notebook))}</p>' if notebook else ""
        )
        cards.append(
            '<article class="conflict-card">'
            f'<div class="meta-strip">'
            f'<span class="chip warn">{escape(str(item.get("topic") or "contradiction"))}</span>'
            f'<span class="chip">record {escape(str(item.get("record_id") or ""))}</span>'
            "</div>"
            '<div class="positions">'
            f'<p class="left"><strong>Position A</strong><br/>{escape(left_v) or "—"}'
            f'<span class="evidence-meta">{escape(left_s)} · {_open_link(left_r, request_id)}</span></p>'
            f'<p class="right"><strong>Position B</strong><br/>{escape(right_v) or "—"}'
            f'<span class="evidence-meta">{escape(right_s)} · {_open_link(right_r, request_id)}</span></p>'
            "</div>"
            f"{extra}"
            f"{_note_for(item, notes)}"
            f'<p class="muted">The console does not pick a winner.</p>'
            f'<div class="viewed-row">{viewed}</div>'
            "</article>"
        )
    inner = "".join(cards) or "<p class=\"muted\">None</p>"
    return (
        '<section class="region equal" data-region="contradictions">'
        "<h2>Contradictions</h2>"
        f"{inner}"
        "</section>"
    )


def _gaps(pack: dict[str, Any], *, request_id: str, notes: list[dict[str, Any]]) -> str:
    cards = []
    for item in _items(pack, "gaps"):
        if not isinstance(item, dict):
            cards.append(f"<li>{escape(str(item))}</li>")
            continue
        gap_type = str(item.get("gap_type") or "gap")
        detail = str(item.get("packet_item") or item.get("statement") or item.get("boundary") or "")
        subject = str(item.get("subject_id") or "")
        source = str(item.get("source") or "")
        record_id = str(item.get("record_id") or "")
        refs = [str(ref) for ref in (item.get("evidence_refs") or []) if ref]
        if record_id and record_id not in refs:
            refs.append(record_id)
        viewed = "".join(
            _viewed_box(ref, request_id, slot=f"gap-{len(cards)}-{index}")
            for index, ref in enumerate(refs)
        )
        headline = detail or gap_type
        cards.append(
            '<article class="gap-card">'
            f'<div class="meta-strip">'
            f'<span class="chip warn">{escape(gap_type)}</span>'
            f'<span class="chip">subject {escape(subject) or "—"}</span>'
            "</div>"
            f"<p><strong>{escape(headline)}</strong></p>"
            f'<p class="muted">{escape(source)} · {_open_link(record_id, request_id)}</p>'
            f"{_note_for(item, notes)}"
            f'<div class="viewed-row">{viewed}</div>'
            "</article>"
        )
    inner = "".join(cards) or "<p class=\"muted\">None</p>"
    return (
        '<section class="region equal" data-region="gaps"><h2>Gaps</h2>'
        f"{inner}</section>"
    )


def _abstentions(pack: dict[str, Any], *, request_id: str) -> str:
    cards = []
    for item in _items(pack, "abstentions"):
        if not isinstance(item, dict):
            cards.append(f"<li>{escape(str(item))}</li>")
            continue
        reason = str(item.get("reason_code") or item.get("statement") or "abstention")
        observed = str(item.get("observed_unit") or "")
        spec = str(item.get("spec_unit") or "")
        units = ""
        if observed or spec:
            units = (
                '<div class="positions">'
                f'<p class="left"><strong>Observed unit</strong><br/>{escape(observed) or "—"}</p>'
                f'<p class="right"><strong>Specification unit</strong><br/>{escape(spec) or "—"}</p>'
                "</div>"
            )
        refs = [str(ref) for ref in (item.get("evidence_refs") or []) if ref]
        subject = str(item.get("subject_id") or "")
        viewed = "".join(
            _viewed_box(ref, request_id, slot=f"abstention-{len(cards)}-{index}")
            for index, ref in enumerate(refs)
        )
        cards.append(
            '<article class="gap-card">'
            f'<div class="meta-strip"><span class="chip">{escape(reason)}</span>'
            f'<span class="chip">subject {escape(subject) or "—"}</span></div>'
            f"{units}"
            f'<div class="viewed-row">{viewed}</div>'
            "</article>"
        )
    inner = "".join(cards) or "<p class=\"muted\">None</p>"
    return (
        '<section class="region equal" data-region="abstentions"><h2>Abstentions</h2>'
        f"{inner}</section>"
    )


def _evidence_table(pack: dict[str, Any], *, request_id: str) -> str:
    rows = []
    for item in _items(pack, "evidence"):
        if not isinstance(item, dict):
            continue
        record_id = str(item.get("record_id") or "")
        digest = str((item.get("integrity") or {}).get("sha256") or "")
        short = digest[:12] + "…" if len(digest) > 12 else digest
        rows.append(
            "<tr>"
            f"<td>{_open_link(record_id, request_id)}</td>"
            f"<td>{_cell(item.get('source'))}</td>"
            f"<td>{_cell(item.get('authority'))}</td>"
            f"<td>{_cell(item.get('effective_at'))}</td>"
            f"<td>{_cell(item.get('retrieved_at'))}</td>"
            f"<td class=\"hash-cell\" data-hash=\"{escape(digest)}\" title=\"{escape(digest)}\">{escape(short)}</td>"
            "</tr>"
        )
    inner = "".join(rows) or '<tr><td colspan="6">None</td></tr>'
    return (
        '<section class="region equal" data-region="evidence"><h2>Evidence</h2>'
        '<p class="muted">Open a row to mark it viewed. Acknowledgement stays unavailable until cited evidence is opened.</p>'
        '<div class="table-wrap"><table class="work-table">'
        "<thead><tr><th>Record id</th><th>Source</th><th>Authority</th><th>Effective at</th><th>Retrieved at</th><th>Integrity</th></tr></thead>"
        f"<tbody>{inner}</tbody></table></div>"
        "</section>"
    )


def _inference_banner(pack: dict[str, Any], notes: list[dict[str, Any]]) -> str:
    if notes:
        blocks = []
        for note in notes:
            refs = "".join(
                f'<span class="chip">{escape(ref)}</span>' for ref in note.get("evidence_refs") or []
            )
            cite = f'<p class="muted">Cited evidence {refs}</p>' if refs else ""
            blocks.append(
                '<aside class="annotation" data-origin="model-generated">'
                "<h2>Evidence summary · model-generated</h2>"
                f"<p>Model-generated: {escape(note['text'])}</p>{cite}</aside>"
            )
        return "".join(blocks)
    if not inference_allowed() or not llm_enabled():
        return (
            '<p class="banner-rules" role="status">Rules-only pack. No model text. '
            "Engines remain the source of truth.</p>"
        )
    return (
        '<p class="banner-rules" role="status">Model text was discarded by output guards. '
        "The pack is unchanged.</p>"
    )


def render_entity_picker(workflow: str, current: str = "") -> str:
    items = picker_entities(workflow)
    if not items:
        return ""
    labels = {
        "batch": "Batch id",
        "pv": "Case or signal id",
        "supply": "Shipment or event id",
    }
    field_id = "pack-" + workflow
    grouped: dict[str, list[Any]] = {}
    order: list[str] = []
    for item in items:
        product = item.product or "unspecified"
        if product not in grouped:
            order.append(product)
            grouped[product] = []
        grouped[product].append(item)
    groups = []
    for product in order:
        options = []
        for item in grouped[product]:
            selected = " selected" if item.entity_id == current else ""
            shown = f"{item.entity_id} — {item.label}"
            options.append(
                f'<option value="{escape(item.entity_id)}"{selected}>{escape(shown)}</option>'
            )
        groups.append(
            f'<optgroup label="Product {escape(product)}">{"".join(options)}</optgroup>'
        )
    current_product = product_for(workflow, current)
    product_chip = (
        f'<span class="chip teal">Product {escape(current_product)}</span>' if current_product else ""
    )
    return (
        f'<form class="entity-picker" method="get" action="/workflows/{escape(workflow)}">'
        f'<label class="picker-label" for="{escape(field_id)}">'
        f"{escape(labels.get(workflow, 'Pack id'))}"
        "</label>"
        '<div class="picker-row">'
        f'<select id="{escape(field_id)}" name="entity" required '
        'onchange="this.form.submit()">'
        f"{''.join(groups)}</select>"
        '<button type="submit">Open</button>'
        "</div>"
        f'<p class="picker-hint">Each id is listed under the product it belongs to. {product_chip}</p>'
        "</form>"
    )


def _readiness_banner(pack: dict[str, Any]) -> str:
    readiness = str(pack.get("readiness_state") or pack.get("execution_status") or "not_executed")
    batch_id = str(pack.get("batch_id") or "")
    cases = pack.get("case_ids") or []
    event = str(pack.get("event_id") or "")
    entity = batch_id or (cases[0] if cases else "") or event
    workflow_key = {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}.get(
        str(pack.get("workflow") or ""), ""
    )
    product = product_for(workflow_key, entity) if workflow_key else ""
    product_chip = f'<span class="chip teal">Product {escape(product)}</span>' if product else ""
    return (
        '<p class="banner-readiness" role="status">'
        f"<strong>Readiness: {escape(readiness)}</strong>. Advisory only — "
        "a qualified person decides outside this system. No disposition action here."
        "</p>"
        '<div class="meta-strip">'
        f'<span class="chip">Request {escape(str(pack.get("request_id") or "unset"))}</span>'
        f'<span class="chip teal">{escape(str(pack.get("execution_status") or "not_executed"))}</span>'
        f'<span class="chip">as_of {escape(str(pack.get("as_of") or ""))}</span>'
        f'<span class="chip">{escape(str(pack.get("workflow") or ""))}</span>'
        + (f'<span class="chip">{escape(str(entity))}</span>' if entity else "")
        + product_chip
        + "</div>"
    )


def _graph_projection(pack: dict[str, Any]) -> str:
    projection = (pack.get("human_review") or {}).get("graph_projection") or {}
    if not isinstance(projection, dict) or not projection:
        return ""
    visited = [str(item) for item in (projection.get("visited") or []) if item]
    shown = visited[:24]
    chips = "".join(f'<span class="chip">{escape(node)}</span>' for node in shown)
    extra = ""
    if len(visited) > len(shown):
        extra = f'<p class="muted">{len(visited) - len(shown)} further nodes within the hop cap.</p>'
    incomplete = (
        " Traversal stopped at the hop cap; the frontier is listed, not guessed."
        if projection.get("traversal_incomplete")
        else ""
    )
    seed = str(projection.get("seed") or "none")
    return (
        '<section class="region" data-region="knowledge-graph">'
        "<h2>Knowledge graph · per-run projection</h2>"
        '<p class="muted">Rebuilt from '
        f"{escape(str(projection.get('source') or 'data/RELATIONSHIP_MODEL.csv'))}. "
        f"Not a system of record.{incomplete}</p>"
        '<div class="meta-strip">'
        f'<span class="chip">{escape(str(projection.get("node_count") or 0))} nodes</span>'
        f'<span class="chip">{escape(str(projection.get("edge_count") or 0))} edges</span>'
        f'<span class="chip">seed {escape(seed)}</span>'
        f'<span class="chip">{escape(str(projection.get("hops_used") or 0))}/'
        f'{escape(str(projection.get("max_hops") or 4))} hops</span>'
        "</div>"
        f'<div class="chip-row">{chips}</div>'
        f"{extra}"
        "</section>"
    )


def render_pack_body(
    pack: dict[str, Any],
    *,
    title: str,
    api_available: bool = True,
    workflow: str = "batch",
    locale: str = "en",
    entity_id: str = "",
) -> str:
    hindi = "समीक्षा" if locale.startswith("hi") else ""
    heading = f'<div class="page-title"><h1>{escape(title)} {escape(hindi)}</h1></div>'
    if not api_available:
        return (
            heading
            + '<p class="degraded" role="status">API unavailable. Use the manual runbook '
            f"docs/runbooks/{escape(workflow)}.md. No stale pack is current.</p>"
        )
    request_id = str(pack.get("request_id") or "")
    if request_id and get_pack(request_id):
        remaining = outstanding_critical(request_id)
    else:
        remaining = critical_record_ids(pack)
    notes = _notes(pack)
    extras = "".join(
        _table(title_text, _items(pack, key), columns, request_id=request_id)
        for key, title_text, columns in EXTRA_TABLES
    )
    cases = pack.get("case_ids") or []
    current = entity_id or str(
        pack.get("batch_id") or (cases[0] if cases else "") or pack.get("event_id") or ""
    )
    critical = critical_record_ids(pack)
    return (
        heading
        + render_entity_picker(workflow, current)
        + _readiness_banner(pack)
        + render_pack_graphics(
            pack,
            request_id=request_id,
            opened=max(0, len(critical) - len(remaining)),
            total=len(critical),
        )
        + _graph_projection(pack)
        + _inference_banner(pack, notes)
        + _findings(pack)
        + _contradictions(pack, request_id=request_id, notes=notes)
        + _gaps(pack, request_id=request_id, notes=notes)
        + _abstentions(pack, request_id=request_id)
        + extras
        + _evidence_table(pack, request_id=request_id)
        + '<div id="evidence-drawer" aria-live="polite"></div>'
        + render_review_actions(pack, remaining=remaining, entity_id=current, workflow=workflow)
    )
