"""Server-rendered dashboard charts. Counts and labels only; no classification."""

from __future__ import annotations

import math
from html import escape
from typing import Any
from urllib.parse import quote

from packages.config.catalog import product_for

PURPLE = "#6f42c1"
ORANGE = "#ff7a45"
BLUE = "#4da6ff"
NAVY = "#3d5afe"
GREY = "#c5cad3"
INK = "#2c3344"
MUTED = "#7b8494"
PAPER = "#ffffff"
FONT = "Segoe UI, system-ui, sans-serif"


def _count(pack: dict[str, Any], key: str) -> int:
    value = pack.get(key) or []
    return len(value) if isinstance(value, list) else 0


def composition(pack: dict[str, Any]) -> list[tuple[str, int, str]]:
    return [
        ("Findings", _count(pack, "findings"), PURPLE),
        ("Contradictions", _count(pack, "contradictions"), ORANGE),
        ("Gaps", _count(pack, "gaps"), BLUE),
        ("Abstentions", _count(pack, "abstentions"), NAVY),
        ("Evidence", _count(pack, "evidence"), GREY),
    ]


def kpi_row(items: list[tuple[str, str, str, str]]) -> str:
    cards = []
    tones = ("purple", "orange", "blue", "navy")
    for index, (label, value, footnote, href) in enumerate(items):
        tone = tones[index % 4]
        inner = (
            f'<span class="kpi-ico {tone}"></span>'
            f'<p class="kpi-label">{escape(label)}</p>'
            f'<p class="kpi-value">{escape(str(value))}</p>'
            f'<p class="kpi-foot">{escape(footnote)}</p>'
        )
        if href:
            cards.append(f'<a class="kpi card" href="{escape(href)}">{inner}</a>')
        else:
            cards.append(f'<article class="kpi card">{inner}</article>')
    return '<div class="kpi-row">' + "".join(cards) + "</div>"


def pie_chart(slices: list[tuple[str, int, str]], *, title: str = "Pack mix") -> str:
    total = sum(item[1] for item in slices) or 1
    cx, cy, radius = 120, 108, 72
    angle = -math.pi / 2
    paths: list[str] = [
        f'<svg class="pack-chart chart-svg" viewBox="0 0 240 260" role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
    ]
    nonzero = [(label, value, color) for label, value, color in slices if value > 0]
    if len(nonzero) == 1:
        paths.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{nonzero[0][2]}"/>')
    elif not nonzero:
        paths.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{GREY}"/>')
    else:
        for _label, value, color in slices:
            if value <= 0:
                continue
            sweep = 2 * math.pi * (value / total)
            x1 = cx + radius * math.cos(angle)
            y1 = cy + radius * math.sin(angle)
            angle += sweep
            x2 = cx + radius * math.cos(angle)
            y2 = cy + radius * math.sin(angle)
            large = 1 if sweep > math.pi else 0
            paths.append(
                f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f} Z" fill="{color}"/>'
            )
    paths.append(f'<circle cx="{cx}" cy="{cy}" r="38" fill="{PAPER}"/>')
    paths.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="18" font-family="{FONT}" fill="{INK}">{total}</text>')
    paths.append(f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="10" font-family="{FONT}" fill="{MUTED}">items</text>')
    legend_y = 210
    x = 12
    for label, value, color in slices:
        paths.append(f'<rect x="{x}" y="{legend_y}" width="8" height="8" rx="2" fill="{color}"/>')
        paths.append(
            f'<text x="{x + 12}" y="{legend_y + 8}" font-size="8" font-family="{FONT}" fill="{MUTED}">{escape(label[:10])} {value}</text>'
        )
        x += 46
    paths.append("</svg>")
    return "".join(paths)


def bar_chart(slices: list[tuple[str, int, str]], *, title: str = "Counts") -> str:
    """Category counts as equal-weight bars. Not a trend and not a ranking."""
    width, left, right, top = 420, 128, 40, 8
    row_h = 32
    height = top + 8 + row_h * max(len(slices), 1)
    peak = max((value for _label, value, _color in slices), default=0)
    peak = max(peak, 1)
    bar_max = width - left - right
    parts = [
        f'<svg class="chart-svg bar-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
    ]
    for index, (label, value, color) in enumerate(slices):
        y = top + index * row_h
        bar_w = bar_max * (value / peak)
        parts.append(
            f'<text x="{left - 8}" y="{y + 16}" text-anchor="end" font-size="11" '
            f'font-family="{FONT}" fill="{INK}">{escape(label)}</text>'
        )
        parts.append(f'<rect x="{left}" y="{y + 6}" width="{bar_max}" height="14" rx="4" fill="#eef0f4"/>')
        parts.append(
            f'<rect x="{left}" y="{y + 6}" width="{max(bar_w, 2 if value else 0):.1f}" height="14" rx="4" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{left + bar_max + 8}" y="{y + 17}" font-size="11" font-family="{FONT}" fill="{INK}">{value}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _pack_entity(pack: dict[str, Any]) -> str:
    cases = pack.get("case_ids") or []
    return str(pack.get("batch_id") or (cases[0] if cases else "") or pack.get("event_id") or "")


def _pack_workflow_key(pack: dict[str, Any]) -> str:
    return {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}.get(
        str(pack.get("workflow") or ""), ""
    )


def _tally(rows: list[str], colors: tuple[str, ...]) -> list[tuple[str, int, str]]:
    counts: dict[str, int] = {}
    order: list[str] = []
    for key in rows:
        label = key or "unspecified"
        if label not in counts:
            order.append(label)
            counts[label] = 0
        counts[label] += 1
    return [(label, counts[label], colors[index % len(colors)]) for index, label in enumerate(order)]


def review_ring(opened: int, total: int, label: str = "Critical evidence opened") -> str:
    total = max(int(total), 0)
    opened = max(0, min(int(opened), total if total else 0))
    ratio = (opened / total) if total else 1.0
    radius = 46
    circ = 2 * math.pi * radius
    dash = f"{ratio * circ:.2f} {circ:.2f}"
    return (
        f'<svg class="status-ring" viewBox="0 0 140 140" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>"
        f'<circle cx="70" cy="70" r="{radius}" fill="none" stroke="#eceff5" stroke-width="12"/>'
        f'<circle cx="70" cy="70" r="{radius}" fill="none" stroke="{PURPLE}" stroke-width="12" '
        f'stroke-dasharray="{dash}" stroke-linecap="round" transform="rotate(-90 70 70)"/>'
        f'<text x="70" y="66" text-anchor="middle" font-size="18" font-family="{FONT}" fill="{INK}">{opened}/{total or 0}</text>'
        f'<text x="70" y="86" text-anchor="middle" font-size="10" font-family="{FONT}" fill="{MUTED}">opened</text>'
        "</svg>"
    )


def evidence_map(pack: dict[str, Any], request_id: str = "") -> str:
    evidence = list(pack.get("evidence") or [])[:8]
    cited: list[tuple[str, str]] = []
    colors = {"gaps": ORANGE, "contradictions": NAVY, "abstentions": BLUE}
    for key, color in colors.items():
        for item in pack.get(key) or []:
            label = str(item.get("gap_type") or item.get("topic") or item.get("reason_code") or key)
            cited.append((label[:18], color))
    if not evidence and not cited:
        return (
            f'<svg class="evidence-map chart-svg" viewBox="0 0 520 140" role="img" aria-label="Evidence map">'
            f'<rect width="520" height="140" fill="{PAPER}"/>'
            f'<text x="260" y="76" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="13">No evidence in this pack</text>'
            "</svg>"
        )
    parts = [
        '<svg class="evidence-map chart-svg" viewBox="0 0 640 200" role="img" aria-label="Evidence citation map">',
        "<title>Evidence citation map</title>",
        f'<rect width="640" height="200" fill="{PAPER}"/>',
    ]
    top_n = cited[:5] or [("Pack", PURPLE)]
    for index, (label, color) in enumerate(top_n):
        x = 70 + index * 120
        parts.append(f'<circle cx="{x}" cy="54" r="18" fill="{color}"/>')
        parts.append(f'<text x="{x}" y="86" text-anchor="middle" font-size="10" font-family="{FONT}" fill="{INK}">{escape(label)}</text>')
    for index, item in enumerate(evidence):
        x = 50 + index * 74
        record_id = str(item.get("record_id") or f"E{index}")
        href = "/evidence/" + quote(record_id, safe="")
        if request_id:
            href += "?request_id=" + quote(request_id, safe="")
        parts.append(f'<a href="{escape(href)}">')
        parts.append(f'<rect x="{x - 26}" y="128" width="52" height="32" rx="8" fill="{PURPLE}"/>')
        parts.append(f'<text x="{x}" y="148" text-anchor="middle" font-size="9" fill="#fff" font-family="{FONT}">{escape(record_id[:8])}</text>')
        parts.append("</a>")
        tx = 70 + (index % len(top_n)) * 120
        parts.append(f'<line x1="{tx}" y1="72" x2="{x}" y2="128" stroke="{GREY}" stroke-width="1.4"/>')
    parts.append("</svg>")
    return "".join(parts)


def workflow_specific(pack: dict[str, Any]) -> str:
    workflow = str(pack.get("workflow") or "")
    href_key = {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}.get(workflow, "")
    cases = pack.get("case_ids") or []
    entity = str(pack.get("batch_id") or (cases[0] if cases else "") or pack.get("event_id") or "")
    product = product_for(href_key, entity) if href_key else ""
    product_chip = f'<span class="chip teal">Product {escape(product)}</span>' if product else ""
    if workflow == "batch_evidence":
        readiness = escape(str(pack.get("readiness_state") or "unknown"))
        return (
            '<div class="meta-strip">'
            f'<span class="chip warn">Readiness {readiness}</span>'
            '<span class="chip">Advisory only — not executed</span>'
            f'<span class="chip">Batch {escape(str(pack.get("batch_id") or ""))}</span>'
            + product_chip
            + "</div>"
        )
    if workflow == "pv_intake":
        return (
            '<div class="meta-strip">'
            f'<span class="chip">Duplicate candidates {_count(pack, "duplicate_candidates")}</span>'
            f'<span class="chip warn">Listedness rows {_count(pack, "listedness_context")}</span>'
            f'<span class="chip">Clock evidence {_count(pack, "clock_evidence")}</span>'
            + product_chip
            + "</div>"
        )
    if workflow == "supply_options":
        return (
            '<div class="meta-strip">'
            f'<span class="chip">Draft options {_count(pack, "options")}</span>'
            f'<span class="chip warn">Quality holds {_count(pack, "quality_holds")}</span>'
            f'<span class="chip">Constraints {_count(pack, "constraints")}</span>'
            + product_chip
            + "</div>"
        )
    return (
        '<div class="meta-strip"><span class="chip">Advisory only — not executed</span>'
        + product_chip
        + "</div>"
    )


def workflow_bars(pack: dict[str, Any]) -> list[tuple[str, int, str]]:
    workflow = str(pack.get("workflow") or "")
    if workflow == "pv_intake":
        return [
            ("Duplicates", _count(pack, "duplicate_candidates"), PURPLE),
            ("Listedness", _count(pack, "listedness_context"), ORANGE),
            ("Clocks", _count(pack, "clock_evidence"), BLUE),
        ]
    if workflow == "supply_options":
        return [
            ("Draft options", _count(pack, "options"), PURPLE),
            ("Quality holds", _count(pack, "quality_holds"), ORANGE),
            ("Constraints", _count(pack, "constraints"), BLUE),
        ]
    return [
        ("Findings", _count(pack, "findings"), PURPLE),
        ("Contradictions", _count(pack, "contradictions"), ORANGE),
        ("Gaps", _count(pack, "gaps"), BLUE),
        ("Abstentions", _count(pack, "abstentions"), NAVY),
    ]


def render_pack_graphics(
    pack: dict[str, Any],
    *,
    request_id: str = "",
    opened: int = 0,
    total: int = 0,
) -> str:
    rid = request_id or str(pack.get("request_id") or "")
    series = composition(pack)
    prominence = series[:4]
    kpis = kpi_row(
        [
            ("Findings", series[0][1], "From this pack", ""),
            ("Contradictions", series[1][1], "Both positions shown", ""),
            ("Gaps", series[2][1], "Equal prominence", ""),
            ("Evidence", series[4][1], "Open to review", ""),
        ]
    )
    specific = workflow_bars(pack)
    return (
        '<section class="dash-block" aria-label="Graphical pack view">'
        "<h2>Graphical view</h2>"
        '<p class="chart-caption">Counts from this pack. Not a trend, not analytics, and charts do not decide.</p>'
        + workflow_specific(pack)
        + kpis
        + '<div class="dash-grid">'
        + '<article class="card chart-card"><div class="card-head"><h3>Pack mix</h3></div>'
        + pie_chart(series)
        + "</article>"
        + '<article class="card chart-card"><div class="card-head"><h3>Equal prominence</h3></div>'
        + '<p class="chart-caption">Findings, contradictions, gaps and abstentions share the same scale.</p>'
        + bar_chart(prominence, title="Equal prominence")
        + "</article>"
        + '<article class="card chart-card"><div class="card-head"><h3>This workflow</h3></div>'
        + bar_chart(specific, title="This workflow")
        + "</article>"
        + '<article class="card chart-card"><div class="card-head"><h3>Critical evidence opened</h3></div>'
        + review_ring(opened, total)
        + f'<p class="kpi-foot">{opened} of {total} critical items opened</p>'
        + "</article>"
        + '<article class="card chart-card tall"><div class="card-head"><h3>Cited evidence</h3></div>'
        + evidence_map(pack, rid)
        + "</article>"
        + "</div>"
        + "</section>"
    )


def merge_packs(packs: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, list[Any]] = {key: [] for key in ("findings", "contradictions", "gaps", "abstentions", "evidence")}
    for pack in packs:
        for key in merged:
            merged[key].extend(list(pack.get(key) or []))
    return merged


def render_home_dashboard(packs: list[dict[str, Any]]) -> str:
    merged = merge_packs(packs)
    series = composition(merged)
    products = _tally(
        [product_for(_pack_workflow_key(pack), _pack_entity(pack)) or "unspecified" for pack in packs],
        (PURPLE, ORANGE, BLUE, NAVY),
    )
    workflows = _tally(
        [
            {"batch": "Batch", "pv": "PV intake", "supply": "Supply"}.get(_pack_workflow_key(pack), "Other")
            for pack in packs
        ],
        (PURPLE, ORANGE, BLUE),
    )
    kpis = kpi_row(
        [
            ("Evidence", series[4][1], "Across loaded packs", "/workflows/batch"),
            ("Gaps", series[2][1], "Unanswered questions", "/status"),
            ("Contradictions", series[1][1], "Positions preserved", "/contradictions"),
            ("Packs", len(packs), "Every selectable id", "/status"),
        ]
    )
    product_block = (
        '<article class="card chart-card"><div class="card-head"><h3>By product</h3></div>'
        + (bar_chart(products, title="By product") if products else '<p class="muted">Open a workflow to load packs.</p>')
        + "</article>"
    )
    workflow_block = (
        '<article class="card chart-card"><div class="card-head"><h3>By workflow</h3></div>'
        + (bar_chart(workflows, title="By workflow") if workflows else '<p class="muted">No packs loaded yet.</p>')
        + "</article>"
    )
    return (
        '<div class="home-map">'
        + kpis
        + '<div class="dash-grid">'
        + '<article class="card chart-card"><div class="card-head"><h3>What reviewers must inspect</h3></div>'
        + pie_chart(series, title="What reviewers must inspect")
        + "</article>"
        + product_block
        + workflow_block
        + '<article class="card chart-card"><div class="card-head"><h3>Equal prominence</h3></div>'
        + bar_chart(series[:4], title="Equal prominence")
        + "</article>"
        + "</div></div>"
    )


def home_map() -> str:
    return render_home_dashboard([])
