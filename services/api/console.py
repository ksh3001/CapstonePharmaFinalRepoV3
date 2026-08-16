"""Server-rendered console. Templates format packs; they compute no rule (BR-064)."""

from __future__ import annotations

from html import escape
from typing import Any
from urllib.parse import quote

from packages.config.catalog import TITLES as WORKFLOW_TITLES
from packages.config.catalog import WORKFLOWS, picker_entities
from services.api.chrome import icon, wrap_shell
from services.api.graphics import home_map, render_home_dashboard, review_ring
from services.api.handlers import outstanding_critical
from services.api.pack_view import render_pack_body
from services.api.pack_view import render_evidence_fragment as render_pack_evidence_fragment

CORE_ROUTES = (
    "/workflows/batch",
    "/workflows/pv",
    "/workflows/supply",
    "/evidence/{id}",
)

FOCUS_CSS = (
    "a:focus,button:focus,textarea:focus,select:focus,"
    "input:not([type=checkbox]):not([type=radio]):focus"
    "{outline:3px solid #000;outline-offset:2px}"
)
PAGE_CSS = f".region{{display:block}} {FOCUS_CSS}"
NAV = (
    '<nav class="aegis" aria-label="AEGIS">'
    '<a href="/home">Home</a>'
    '<a href="/workflows/batch">Batch</a>'
    '<a href="/workflows/pv">PV</a>'
    '<a href="/workflows/supply">Supply</a>'
    '<a href="/contradictions">Contradictions</a>'
    '<a href="/status">Status</a>'
    "</nav>"
)


def _items(pack: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return list(pack.get(key) or [])


def _evidence_link(item: dict[str, Any], request_id: str = "") -> str:
    record_id = str(item.get("record_id") or "")
    href = "/evidence/" + quote(record_id, safe="")
    if request_id:
        href += "?request_id=" + quote(request_id, safe="")
    shown = escape(record_id)
    return (
        f'<a class="evidence-link" href="{escape(href)}" data-record="{shown}"'
        f' hx-get="{escape(href)}" hx-target="#evidence-drawer" hx-swap="innerHTML">'
        f"{shown}</a>"
        f'<span class="evidence-meta"> source={escape(str(item.get("source") or ""))}'
        f" authority={escape(str(item.get('authority') or ''))}"
        f" effective_at={escape(str(item.get('effective_at')))}"
        f" retrieved_at={escape(str(item.get('retrieved_at') or ''))}"
        f" hash={escape(str((item.get('integrity') or {}).get('sha256') or ''))}</span>"
    )


def _region(title: str, rows: list[str]) -> str:
    body = "".join(f"<li>{row}</li>" for row in rows) or "<li>None</li>"
    return f'<section class="region equal" data-region="{escape(title.casefold())}"><h2>{escape(title)}</h2><ul>{body}</ul></section>'


def render_entity_directory() -> str:
    sections = []
    for workflow in WORKFLOWS:
        grouped: dict[str, list[Any]] = {}
        order: list[str] = []
        for item in picker_entities(workflow):
            product = item.product or "unspecified"
            if product not in grouped:
                order.append(product)
                grouped[product] = []
            grouped[product].append(item)
        blocks = []
        for product in order:
            cards = []
            for item in grouped[product]:
                cards.append(
                    f'<a class="card" href="/workflows/{item.workflow}/{item.entity_id}">'
                    f"<h2>{escape(item.entity_id)}</h2>"
                    f"<p>{escape(item.label)}</p>"
                    f'<p class="chip teal">Product {escape(item.product)}</p></a>'
                )
            blocks.append(
                f'<h3 class="product-heading">Product {escape(product)}</h3>'
                f'<div class="hero-grid">{"".join(cards)}</div>'
            )
        sections.append(
            f"<h2>{escape(WORKFLOW_TITLES[workflow])}</h2>"
            + "".join(blocks)
        )
    return "".join(sections)


def render_pack_page(
    pack: dict[str, Any],
    *,
    title: str,
    locale: str = "en",
    api_available: bool = True,
    workflow: str = "batch",
    entity_id: str = "",
) -> str:
    direction = "rtl" if locale.startswith("ar") else "ltr"
    body = render_pack_body(
        pack,
        title=title,
        api_available=api_available,
        workflow=workflow,
        locale=locale,
        entity_id=entity_id,
    )
    return _document(title, locale=locale, direction=direction, body=body)


def _document(title: str, *, body: str, locale: str = "en", direction: str = "ltr") -> str:
    return wrap_shell(body, title=title, locale=locale, direction=direction, css=PAGE_CSS)


def render_chat_thread() -> str:
    from services.api.engine_chat import turns

    rows = turns()
    if not rows:
        return (
            '<div class="chat-empty">'
            "<p><strong>Pack chat</strong></p>"
            "<p>This is the advisory chatbot for loaded packs. Name a catalog batch, case, or event. "
            "Ask for pack status, or what is linked to that id. "
            "You get the engine tool result, then a model restatement. This is not a disposition.</p>"
            '<p class="muted">Try: What is the status of NCB204-B24071? or What is linked to NCB204-B24071?</p>'
            "</div>"
        )
    parts: list[str] = []
    for item in rows:
        parts.append(_render_chat_turn(item))
    return "".join(parts)


def _render_chat_turn(item: dict[str, Any]) -> str:
    question = escape(str(item.get("question") or ""))
    answer = escape(str(item.get("answer") or ""))
    tool = escape(str(item.get("tool") or "ask"))
    narrative = str(item.get("narrative") or "")
    facts = item.get("facts") if isinstance(item.get("facts"), dict) else {}
    tone = "" if item.get("ok") else " muted"
    if facts.get("seed") or "visited" in facts:
        body = _render_graph_card(facts, answer)
    elif facts:
        body = _render_tool_card(facts, answer)
    else:
        body = f"<p>{answer}</p>"
    note = _render_narrative_card(item.get("narrative_blocks"), narrative)
    return (
        f'<div class="chat-turn">'
        f'<p class="chat-bubble user">{question}</p>'
        f'<article class="chat-card ask-answer{tone}">'
        f'<p class="chat-tool">MCP · {tool}</p>'
        f"{body}"
        "</article>"
        f"{note}"
        "</div>"
    )


def _render_narrative_card(blocks: Any, fallback: str) -> str:
    rows = blocks if isinstance(blocks, dict) else {}
    headline = str(rows.get("headline") or "").strip()
    meaning = str(rows.get("meaning") or "").strip()
    nxt = str(rows.get("next") or "").strip()
    if not headline and not meaning and fallback:
        headline = fallback
    if not headline and not meaning:
        return '<p class="chat-meta">No model summary. The tool result stands.</p>'
    parts = ['<article class="chat-card narrative">']
    if headline:
        parts.append(f'<p class="chat-headline">{escape(headline)}</p>')
    parts.append('<dl class="chat-plain">')
    if meaning:
        parts.append(f"<div><dt>Why</dt><dd>{escape(meaning)}</dd></div>")
    if nxt:
        parts.append(f"<div><dt>Do next</dt><dd>{escape(nxt)}</dd></div>")
    parts.append("</dl>")
    parts.append(
        '<p class="chat-meta">Advisory only. Not a release, allocation, or certificate.</p>'
    )
    parts.append("</article>")
    return "".join(parts)


def _render_tool_card(facts: dict[str, Any], fallback: str) -> str:
    entity = escape(str(facts.get("entity") or ""))
    product = escape(str(facts.get("product") or ""))
    workflow = escape(str(facts.get("workflow") or ""))
    readiness = escape(str(facts.get("readiness_state") or ""))
    execution = escape(str(facts.get("execution_status") or ""))
    if not entity and not readiness:
        return f"<p>{escape(fallback)}</p>"
    chip_class = "warn" if readiness in {"insufficient_evidence", "not_executed", "blocked"} else (
        "ok" if readiness in {"ready", "executed", "sufficient"} else ""
    )
    remaining = facts.get("remaining_critical") or []
    chips = "".join(f'<li>{escape(str(item))}</li>' for item in remaining[:8]) or "<li>None listed</li>"
    subtitle = " · ".join(part for part in (product, workflow) if part)
    return (
        f"<h3>{entity or 'Pack'}</h3>"
        f'<p class="chat-sub">{subtitle}</p>'
        f'<p class="chip {chip_class}">{readiness or "unknown"}</p>'
        '<dl class="chat-facts">'
        f"<div><dt>Execution</dt><dd>{execution or 'unknown'}</dd></div>"
        f"<div><dt>Findings</dt><dd>{escape(str(facts.get('findings', '—')))}</dd></div>"
        f"<div><dt>Contradictions</dt><dd>{escape(str(facts.get('contradictions', '—')))}</dd></div>"
        f"<div><dt>Gaps</dt><dd>{escape(str(facts.get('gaps', '—')))}</dd></div>"
        f"<div><dt>Abstentions</dt><dd>{escape(str(facts.get('abstentions', '—')))}</dd></div>"
        "</dl>"
        '<p class="chat-crit">Remaining critical evidence</p>'
        f'<ul class="chat-crit-list">{chips}</ul>'
        '<p class="chat-meta">Advisory only. The engine does not dispose, allocate, or certify.</p>'
    )


def _node_label(node_id: str) -> str:
    if ":" not in node_id:
        return node_id
    dataset, key = node_id.split(":", 1)
    kind = dataset.replace(".csv", "").replace("_", " ")
    return f"{key} · {kind}"


def _render_graph_card(facts: dict[str, Any], fallback: str) -> str:
    entity = escape(str(facts.get("entity") or ""))
    seed = escape(str(facts.get("seed") or "none"))
    source = escape(str(facts.get("source") or "data/RELATIONSHIP_MODEL.csv"))
    hops_used = escape(str(facts.get("hops_used", "—")))
    max_hops = escape(str(facts.get("max_hops", "—")))
    visited = [str(item) for item in (facts.get("visited") or []) if item]
    if not entity and not seed and not visited:
        return f"<p>{escape(fallback)}</p>"
    chips = "".join(
        f'<li>{escape(_node_label(item))}</li>' for item in visited[:12]
    ) or "<li>None listed</li>"
    incomplete = (
        '<p class="chat-meta">Traversal stopped at the hop cap. The frontier is listed, not guessed.</p>'
        if facts.get("traversal_incomplete")
        else ""
    )
    return (
        f"<h3>{entity or 'Relation graph'}</h3>"
        f'<p class="chat-sub">{source}</p>'
        f'<p class="chip">relation graph</p>'
        '<dl class="chat-facts">'
        f"<div><dt>Seed</dt><dd>{seed}</dd></div>"
        f"<div><dt>Hops</dt><dd>{hops_used}/{max_hops}</dd></div>"
        f"<div><dt>Visited</dt><dd>{escape(str(facts.get('visited_count', len(visited))))}</dd></div>"
        f"<div><dt>Frontier</dt><dd>{escape(str(facts.get('frontier_count', '—')))}</dd></div>"
        "</dl>"
        '<p class="chat-crit">Related nodes</p>'
        f'<ul class="chat-crit-list">{chips}</ul>'
        f"{incomplete}"
        '<p class="chat-meta">Advisory only. Per-run projection. Not a system of record.</p>'
    )


def render_ask_panel() -> str:
    return (
        '<aside class="engine-chat" data-region="ask" aria-label="Pack chat">'
        '<div class="chat-head">'
        '<p class="chat-kicker">Advisory chatbot</p>'
        "<h2>Pack chat</h2>"
        '<label class="chat-close" for="chat-toggle">Close</label>'
        '<p class="muted">Read-only pack status or relation-graph neighbourhood from MCP tools, '
        "plus a model summary. Not a disposition. The engine does not dispose, allocate, or certify.</p>"
        "</div>"
        f'<div id="engine-thread" class="chat-thread" aria-live="polite">{render_chat_thread()}</div>'
        '<form class="ask-form" method="post" action="/api/ask" hx-post="/api/ask" '
        'hx-target="#engine-thread" hx-swap="innerHTML">'
        '<label class="sr-only" for="ask-q">Pack chat question</label>'
        '<input id="ask-q" name="q" type="search" '
        'placeholder="Status of NCB204-B24071, or what is linked to it" autocomplete="off"/>'
        '<button type="submit">Send</button>'
        "</form>"
        "</aside>"
        '<div class="chat-hint" aria-hidden="true">'
        "<strong>Pack chat</strong>"
        "<span>Advisory chatbot for batch, case, and event packs</span>"
        "</div>"
        '<label class="chat-fab" for="chat-toggle" title="Open Pack chat">'
        f'{icon("chat")}'
        '<span class="when-closed">Pack chat</span>'
        '<span class="when-open">Close</span>'
        "</label>"
    )


def render_ask_answer(payload: dict[str, Any]) -> str:
    return render_chat_thread() or (
        f'<p class="ask-answer">{escape(str(payload.get("answer") or "No answer."))}</p>'
    )


def dashboard_health_html(*, session_count: int = 0) -> str:
    from packages.kernel.audit import audit_events
    from packages.observability.health import runtime_health

    return render_health_strip(runtime_health(session_count=session_count, audit_events=audit_events()))


def render_health_strip(snapshot: dict[str, Any]) -> str:
    status = str(snapshot.get("status") or "nominal")
    tone = {"nominal": "ok", "attention": "warn", "inference_off": "off"}.get(status, "ok")
    cost = snapshot.get("cost") if isinstance(snapshot.get("cost"), dict) else {}
    inference_on = not bool(snapshot.get("kill_switch"))
    cost_figure = (
        _fmt_money(cost.get("inference_cost"), currency=str(cost.get("currency") or "USD"))
        if cost.get("priced")
        else "unpriced"
    )
    return (
        f'<section class="health-strip {tone}" aria-label="Runtime health">'
        '<div class="health-strip-copy">'
        "<h2>Runtime health</h2>"
        f'<p>{escape(str(snapshot.get("status_reason") or "In-process evidence chain."))}</p>'
        "</div>"
        '<p class="chip-row">'
        f'<span class="chip {tone}">{escape(status.replace("_", " "))}</span>'
        f'<span class="chip">Inference {"on" if inference_on else "off"}</span>'
        f'<span class="chip">Tokens {_fmt_count(snapshot.get("total_tokens"))}</span>'
        f'<span class="chip">LLM cost {escape(cost_figure)}</span>'
        f'<span class="chip">Denials {_fmt_count(snapshot.get("authz_denials"))}</span>'
        "</p>"
        '<a class="chip" href="/health">Open full telemetry</a>'
        "</section>"
    )


def render_login(*, next_href: str = "/home", notice: str = "") -> str:
    """Username/password gate. Posts to /session; lands on /home for qp_eu_1."""
    safe_next = next_href if next_href.startswith("/") and not next_href.startswith("//") else "/home"
    if safe_next in {"/", "/index.html", "/login"}:
        safe_next = "/home"
    notice_html = f'<p class="login-notice" role="status">{escape(notice)}</p>' if notice else ""
    # Critical layout is inlined so a stale /static/aegis.css cache cannot break Azure.
    critical_css = """
html,body{height:100%;margin:0}
body.login-body{
  min-height:100vh;margin:0;overflow-x:hidden;
  background:radial-gradient(ellipse 80% 50% at 10% 0%,rgba(111,66,193,.18),transparent 55%),
    radial-gradient(ellipse 60% 40% at 90% 100%,rgba(255,122,69,.14),transparent 50%),#f3f4f8;
  color:#2c3344;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;font-size:14px;line-height:1.45
}
.login-shell{
  box-sizing:border-box;min-height:100vh;width:100%;margin:0;padding:1.5rem;
  display:flex;align-items:center;justify-content:center
}
.login-panel{
  box-sizing:border-box;width:100%;max-width:22rem;margin:0 auto;
  background:#fff;border:1px solid #e6e8ee;border-radius:14px;
  box-shadow:0 8px 24px rgba(44,51,68,.06);padding:2rem 1.75rem 1.75rem;text-align:left
}
.login-brand{display:flex;align-items:center;gap:.55rem;margin:0 0 1.25rem;font-size:.95rem;letter-spacing:.08em}
.login-brand .logo-ring{
  flex:0 0 22px;width:22px;height:22px;border-radius:50%;
  background:conic-gradient(#6f42c1,#ff7a45,#4da6ff,#6f42c1);box-shadow:inset 0 0 0 5px #fff
}
.login-panel h1{margin:0 0 .4rem;font-size:1.45rem;font-weight:600}
.login-panel .lede{margin:0 0 1.35rem;max-width:none;color:#7b8494}
.login-notice{margin:0 0 1rem;padding:.65rem .75rem;border-radius:8px;background:#fff4f0;color:#8a3b1d;border:1px solid #f0c9b8}
.login-form{display:flex;flex-direction:column;gap:1rem;margin:0;width:100%}
.login-field{display:flex;flex-direction:column;gap:.4rem;width:100%;margin:0}
.login-field label{display:block;margin:0;font-size:.82rem;font-weight:600;color:#2c3344}
.login-form input[type=text],.login-form input[type=password]{
  box-sizing:border-box;display:block;width:100%;max-width:100%;margin:0;
  padding:.75rem .85rem;border:1px solid #e6e8ee;border-radius:8px;font:inherit;font-size:.95rem;
  background:#fff;color:#2c3344;min-height:44px
}
.login-form button{
  box-sizing:border-box;display:block;width:100%;margin:.25rem 0 0;border:0;border-radius:8px;
  background:#6f42c1;color:#fff;font:inherit;font-weight:600;font-size:.95rem;padding:.8rem 1rem;
  min-height:44px;cursor:pointer
}
""".replace("\n", "")
    body = (
        '<main class="login-shell">'
        '<section class="login-panel" aria-labelledby="login-title">'
        '<p class="login-brand"><span class="logo-ring" aria-hidden="true"></span><strong>AEGIS</strong></p>'
        '<h1 id="login-title">Sign in</h1>'
        '<p class="lede">Enter your username and password to open the console.</p>'
        + notice_html
        + f'<form class="login-form" method="post" action="/session" autocomplete="on">'
        f'<input type="hidden" name="next" value="{escape(safe_next)}"/>'
        '<div class="login-field">'
        '<label for="login-user">Username</label>'
        '<input id="login-user" name="user" type="text" autocomplete="username" '
        'required spellcheck="false" autofocus value="qp_eu_1"/>'
        "</div>"
        '<div class="login-field">'
        '<label for="login-password">Password</label>'
        '<input id="login-password" name="password" type="password" '
        'autocomplete="current-password" required/>'
        "</div>"
        '<button type="submit">Log in</button>'
        "</form>"
        "</section>"
        "</main>"
    )
    return (
        "<!DOCTYPE html><html lang=\"en\" dir=\"ltr\"><head>"
        '<meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        "<title>AEGIS sign-in</title>"
        f"<style>{critical_css}</style>"
        '<link rel="stylesheet" href="/static/aegis.css?v=login2"/>'
        "</head><body class=\"login-body\">"
        + body
        + "</body></html>"
    )


def render_home(*, mode: str, llm: bool, packs: list[dict[str, Any]] | None = None) -> str:
    llm_label = "on" if llm else "off"
    dashboard = render_home_dashboard(list(packs or [])) if packs else home_map()
    body = (
        '<div class="page-title"><h1>Dashboard</h1></div>'
        f'<p class="lede">Runtime mode <strong>{escape(mode)}</strong>. Model {escape(llm_label)}. '
        "The engines produce the pack. This console is how a reviewer sees it, opens evidence, and records a follow-up. "
        'Start from <a href="/">demo sign-in</a> to assume a fixture identity, or use <strong>Pack chat</strong> for a catalog id.</p>'
        + dashboard_health_html(session_count=len(packs or []))
        + dashboard
        + render_entity_directory()
        + '<div class="hero-grid">'
        '<a class="card" href="/"><h2>Demo sign-in</h2><p>Assume a fixture user from the entitlement table before the walkthrough.</p></a>'
        '<a class="card" href="/status"><h2>Workflow status</h2><p>See review progress and store the action taken as evidence.</p></a>'
        '<a class="card" href="/history"><h2>Evidence history</h2><p>Read the append-only chain of reviewer actions.</p></a>'
        "</div>"
        '<h2>How to review</h2>'
        '<ol class="how-list">'
        "<li>Open a workflow pack and read the graphical view.</li>"
        "<li>Open every critical evidence item. Acknowledgement stays unavailable until they are opened.</li>"
        "<li>On Status, record the action taken in response to the advisory. That is stored on the evidence chain.</li>"
        "<li>Open Evidence history to see every stored acknowledgement, contest, and opened item.</li>"
        "</ol>"
    )
    return _document("AEGIS", body=body)


def render_saved_toast(message: str = "Follow-up stored as evidence.") -> str:
    return (
        '<div id="aegis-toast" class="toast is-on" hx-swap-oob="true" '
        'role="status" aria-live="polite">'
        "<strong>Data saved</strong>"
        f"<p>{escape(message)}</p>"
        "</div>"
    )


def _follow_timeline(actions: list[dict[str, Any]], empty: str) -> str:
    lines = []
    for item in actions:
        lines.append(
            "<li>"
            f"<strong>{escape(str(item.get('event') or ''))}</strong> "
            f"by {escape(str(item.get('user') or ''))} — "
            f"{escape(str(item.get('action_taken') or item.get('reason') or 'recorded'))}"
            "</li>"
        )
    if not lines:
        return f'<li class="muted">{escape(empty)}</li>'
    return "".join(lines)


def render_status_follow_panel(row: dict[str, Any]) -> str:
    request_id = escape(str(row.get("request_id") or ""))
    remaining = list(row.get("remaining") or [])
    actions = list(row.get("responses") or [])
    timeline = _follow_timeline(actions, "No reviewer follow-up stored yet.")
    if remaining:
        ack = (
            f'<p class="gate">Acknowledgement unavailable. Remaining critical evidence: '
            f"{escape(', '.join(str(item) for item in remaining))}</p>"
        )
    else:
        ack_href = f"/api/reviews/{request_id}/acknowledge"
        ack = (
            f'<form class="follow-form" method="post" action="{ack_href}" '
            f'hx-post="{ack_href}" hx-target="#follow-status-{request_id}" hx-swap="outerHTML">'
            '<input type="hidden" name="next" value="/status"/>'
            '<input type="hidden" name="panel" value="status"/>'
            f'<label for="ack-{request_id}">Action taken in response to this advisory</label>'
            f'<textarea id="ack-{request_id}" name="action_taken"></textarea>'
            '<button type="submit" class="ack">Acknowledge (workflow event, not a signature, not a disposition)</button>'
            "</form>"
        )
    contest = f"/api/reviews/{request_id}/contest"
    return (
        f'<div class="follow-panel" id="follow-status-{request_id}">'
        + ack
        + f'<form class="follow-form" method="post" action="{contest}" '
        f'hx-post="{contest}" hx-target="#follow-status-{request_id}" hx-swap="outerHTML">'
        '<input type="hidden" name="next" value="/status"/>'
        '<input type="hidden" name="panel" value="status"/>'
        f'<label for="reason-{request_id}">Contest reason or follow-up note</label>'
        f'<textarea id="reason-{request_id}" name="reason"></textarea>'
        f'<label for="act-{request_id}">Action taken in response to this advisory</label>'
        f'<textarea id="act-{request_id}" name="action_taken" required></textarea>'
        '<button type="submit">Store follow-up as evidence</button>'
        "</form>"
        f'<h3>Stored follow-up</h3><ul class="timeline">{timeline}</ul>'
        "</div>"
    )


def render_contradiction_follow_panel(item: dict[str, Any]) -> str:
    request_id = escape(str(item.get("request_id") or ""))
    record_id = escape(str(item.get("record_id") or ""))
    topic = escape(str(item.get("topic") or ""))
    follow = list(item.get("follow_ups") or [])
    timeline = _follow_timeline(follow, "No follow-up stored yet.")
    contest = f"/api/reviews/{request_id}/contest"
    return (
        f'<div class="follow-panel" id="follow-{record_id}">'
        f'<form class="follow-form" method="post" action="{contest}" '
        f'hx-post="{contest}" hx-target="#follow-{record_id}" hx-swap="outerHTML">'
        '<input type="hidden" name="next" value="/contradictions"/>'
        '<input type="hidden" name="panel" value="contradiction"/>'
        f'<input type="hidden" name="subject_id" value="{record_id}"/>'
        f'<input type="hidden" name="reason" value="contradiction:{record_id}:{topic}"/>'
        f'<label for="act-{record_id}">Action taken on this disagreement</label>'
        f'<textarea id="act-{record_id}" name="action_taken" required '
        'placeholder="What did you do with this disagreement?"></textarea>'
        '<button type="submit">Store follow-up as evidence</button>'
        "</form>"
        f'<ul class="timeline">{timeline}</ul>'
        "</div>"
    )


def render_status(sessions: list[dict[str, Any]]) -> str:
    cards = []
    for row in sessions:
        request_id = escape(str(row.get("request_id") or ""))
        workflow = escape(str(row.get("workflow") or ""))
        entity = escape(str(row.get("entity") or ""))
        product = escape(str(row.get("product") or ""))
        href = escape(str(row.get("href") or "/"))
        remaining = list(row.get("remaining") or [])
        critical = list(row.get("critical") or [])
        opened = len(critical) - len(remaining)
        state = escape(str(row.get("review_state") or "open"))
        cards.append(
            '<article class="card">'
            f"<h2>{workflow} · {entity}</h2>"
            f'<div class="meta-strip"><span class="chip">{state}</span>'
            + (f'<span class="chip teal">Product {product}</span>' if product else "")
            + f'<span class="chip">request {request_id}</span></div>'
            '<div class="chart-row">'
            + review_ring(opened, len(critical) or 0)
            + f'<p class="muted"><a href="{href}">Open pack</a></p>'
            + "</div>"
            + render_status_follow_panel(row)
            + "</article>"
        )
    body = (
        "<h1>Workflow status</h1>"
        '<p class="lede">Review progress for loaded packs. Recording a follow-up writes an audit event and an evidence-chain entry. '
        "It is not a signature and it does not change a regulated record.</p>"
        + '<div class="status-grid">'
        + ("".join(cards) or '<p class="muted">No packs loaded yet. Open a workflow first.</p>')
        + "</div>"
    )
    return _document("Workflow status", body=body)


def _history_rows(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="muted">None on the chain yet.</p>'
    lines = [
        "<thead><tr>"
        "<th>Event</th><th>Entity</th><th>User</th><th>Action or reason</th>"
        "<th>Request</th><th>Seq</th>"
        "</tr></thead><tbody>"
    ]
    for item in items:
        entity = str(item.get("entity") or "")
        href = str(item.get("href") or "")
        entity_cell = (
            f'<a href="{escape(href)}">{escape(entity)}</a>'
            if href and entity
            else escape(entity or "—")
        )
        detail = str(item.get("action_taken") or item.get("reason") or item.get("subject_id") or "recorded")
        digest = str(item.get("entry_hash") or "")
        short = digest[:12] if digest else ""
        lines.append(
            "<tr>"
            f"<td><span class=\"chip\">{escape(str(item.get('event') or ''))}</span></td>"
            f"<td>{entity_cell}</td>"
            f"<td>{escape(str(item.get('user') or ''))}</td>"
            f"<td>{escape(detail)}"
            + (f'<span class="evidence-meta">{escape(short)}</span>' if short else "")
            + "</td>"
            f"<td>{escape(str(item.get('request_id') or ''))}</td>"
            f"<td>{escape(str(item.get('seq') or ''))}</td>"
            "</tr>"
        )
    lines.append("</tbody>")
    return '<div class="table-wrap"><table class="work-table history-table">' + "".join(lines) + "</table></div>"


def render_history_page(snapshot: dict[str, Any]) -> str:
    rows = [item for item in (snapshot.get("events") or []) if isinstance(item, dict)]
    decisions = [item for item in rows if item.get("decision")]
    opened = [item for item in rows if str(item.get("event") or "") == "evidence_opened"]
    body = (
        "<h1>Evidence history</h1>"
        '<p class="lede">Reviewer acknowledgements, contests, and opened evidence items are append-only '
        "<code>review</code> records on the evidence chain "
        "(<code>out/evidence/chains/&lt;request_id&gt;.jsonl</code>). "
        "They are not signatures and they do not change a regulated record. "
        "Status is the work queue for packs in this process. This page is the ledger.</p>"
        '<p class="chip-row">'
        f'<span class="chip ok">{int(snapshot.get("decisions") or len(decisions))} decisions</span>'
        f'<span class="chip">{int(snapshot.get("opened") or len(opened))} evidence opened</span>'
        f'<span class="chip">Store {escape(str(snapshot.get("store") or "evidence_chain"))}</span>'
        "</p>"
        "<h2>Decisions</h2>"
        + _history_rows(decisions)
        + "<h2>Evidence opened</h2>"
        + _history_rows(opened)
        + '<p class="lede">Machine-readable: <a href="/api/history">/api/history</a>.</p>'
    )
    return _document("Evidence history", body=body)


def render_message(title: str, message: str, *, extra: str = "") -> str:
    return _document(title, body=f"<h1>{escape(title)}</h1><p>{escape(message)}</p>{extra}")


def render_list_page(title: str, rows: list[str]) -> str:
    items = "".join(f"<li>{escape(row)}</li>" for row in rows) or "<li>None</li>"
    return _document(title, body=f"<h1>{escape(title)}</h1><ul>{items}</ul>")


def render_evidence_fragment(item: dict[str, Any], *, pack: dict[str, Any] | None = None) -> str:
    return render_pack_evidence_fragment(item, pack=pack)


def render_evidence(
    item: dict[str, Any],
    *,
    locale: str = "en",
    request_id: str = "",
    return_href: str = "/",
) -> str:
    html = render_pack_page(
        {
            "evidence": [item],
            "findings": [],
            "gaps": [],
            "abstentions": [],
            "contradictions": [],
            "human_review": {},
            "request_id": request_id,
        },
        title="Evidence",
        locale=locale,
        workflow="batch",
    )
    back = f'<p><a href="{escape(return_href)}">Back to pack</a></p>'
    return html.replace("<main>", "<main>" + back, 1)


GATE_HELP = (
    (
        "authz",
        "Who may see this pack",
        "Checks identity and role against live entitlement. A revoked user is denied even if a cache still says active. You cannot override this here.",
    ),
    (
        "purpose",
        "Why the data is being requested",
        "The same person may see a batch for quality review and be refused the same records for another purpose. Purpose is never inferred from free text.",
    ),
    (
        "residency",
        "Where the data may travel",
        "Cross-border paths without a lawful basis are blocked. The pack names the restriction; it does not move the data.",
    ),
    (
        "hold",
        "Legal hold vs deletion",
        "A deletion request against data on hold becomes restriction plus documentation. Nothing is deleted from this screen.",
    ),
    (
        "tool",
        "Which tools may run",
        "Only signed, approved tool manifests execute. An altered or unlisted tool is refused and the refusal is audited.",
    ),
    (
        "model",
        "Which models may speak",
        "A model is usable only for a qualified intended use at as_of. Research-only or substituted models are refused for GxP work.",
    ),
    (
        "continuity",
        "What happens when something is down",
        "If the API or a source is unavailable, the console shows the manual runbook. It never presents a stale pack as current.",
    ),
)


def render_gates_page(names: list[str]) -> str:
    cards = []
    help_map = {item[0]: item for item in GATE_HELP}
    for name in names:
        meta = help_map.get(name, (name, name, "This control ran on the request."))
        cards.append(
            '<article class="card">'
            f"<h2>{escape(meta[1])}</h2>"
            f'<p class="chip">{escape(name)}</p>'
            f"<p>{escape(meta[2])}</p>"
            "</article>"
        )
    body = (
        "<h1>Gates</h1>"
        '<p class="lede">Gates are automatic controls. They already ran on this request. '
        "A reviewer does not operate them. This page is for an auditor or evaluator who needs to see "
        "why a pack was allowed, denied, or incomplete. There is no switch here to turn a gate off.</p>"
        '<div class="hero-grid">' + "".join(cards) + "</div>"
    )
    return _document("Gates", body=body)


def _inject_basis(item: dict[str, Any]) -> str:
    artefact = str(item.get("artefact_path") or "").strip()
    if artefact:
        return artefact
    brs = [str(value) for value in (item.get("business_rules") or [])]
    acs = [str(value) for value in (item.get("acceptance_criteria") or [])]
    cited = brs[:3] + acs[:2]
    leftover = max(0, len(brs) - 3) + max(0, len(acs) - 2)
    if leftover:
        cited.append(f"+{leftover}")
    return ", ".join(cited)


def _inject_proof(item: dict[str, Any]) -> str:
    parts: list[str] = []
    sources = [str(value) for value in (item.get("evidence_sources") or []) if value]
    if sources:
        parts.append("Evidence " + ", ".join(sources[:4]))
    tests = [str(value) for value in (item.get("verifying_tests") or []) if value]
    if not tests:
        single = str(item.get("verifying_test") or "").strip()
        if single:
            tests = [single]
    if tests:
        shown = tests[0].rsplit("/", 1)[-1]
        extra = f" +{len(tests) - 1}" if len(tests) > 1 else ""
        parts.append("Test " + shown + extra)
    return " · ".join(parts)


def _coverage_chip(item: dict[str, Any]) -> str:
    coverage = str(item.get("coverage") or "")
    label = str(item.get("status_label") or "")
    if not coverage:
        covered = bool(item.get("covered"))
        coverage = "covered" if covered else "uncovered"
        label = "Covered" if covered else "Not covered"
    klass = {"covered": "ok", "artefact": "teal", "uncovered": "warn"}.get(coverage, "warn")
    return f'<span class="chip {klass}">{escape(label)}</span>'


def render_injects_page(rows: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    covered = artefact = uncovered = 0
    lanes = {"Batch": 0, "PV intake": 0, "Supply": 0, "Shared": 0}
    for item in rows:
        dim = str(item.get("dimension") or "D")
        grouped.setdefault(dim, []).append(item)
        coverage = str(item.get("coverage") or "")
        if coverage == "artefact":
            artefact += 1
        elif coverage == "covered" or (not coverage and item.get("covered")):
            covered += 1
        else:
            uncovered += 1
        lane = str(item.get("lane") or "Shared")
        lanes[lane] = lanes.get(lane, 0) + 1
    sections = []
    for dim in sorted(grouped):
        items = []
        for item in grouped[dim]:
            title = f"{item.get('id')} — {item.get('title')}"
            basis = _inject_basis(item)
            proof = _inject_proof(item)
            basis_html = f'<span class="muted">{escape(basis)}</span>' if basis else ""
            proof_html = f'<span class="muted inject-proof">{escape(proof)}</span>' if proof else ""
            result = str(item.get("participant_result") or "").strip()
            result_chip = ""
            if result and result.upper() != "NOT_RUN":
                result_chip = f'<span class="chip">{escape(result)}</span>'
            lane = str(item.get("lane") or "Shared")
            items.append(
                '<li class="inject-row">'
                f'<span class="inject-copy">{escape(str(title))}{basis_html}{proof_html}</span>'
                f'<span class="chip-row"><span class="chip">{escape(lane)}</span>'
                f"{_coverage_chip(item)}{result_chip}</span>"
                "</li>"
            )
        sections.append(
            f'<article class="card"><h2>{escape(dim)}</h2>'
            f'<ul class="inject-list">{"".join(items)}</ul></article>'
        )
    complete = covered + artefact + uncovered
    coverage_line = (
        f"The product covers all {complete} injects: {covered} by a business rule and an acceptance criterion, "
        f"{artefact} by artefact tests (INJ-001–003)."
        if uncovered == 0 and complete
        else f"{covered} covered in rules, {artefact} artefact, {uncovered} not covered."
    )
    body = (
        "<h1>Injects</h1>"
        '<p class="lede">Injects are the 84 challenge situations the product must survive: urgency pressure, poisoned tools, '
        "conflicting sources, privacy holds, and so on. Coverage here is whether each inject is carried by a business rule "
        "and an acceptance criterion, or by the closed artefact allow-list (INJ-001–003). "
        f"{escape(coverage_line)} "
        "The three workflows are how a reviewer opens packs. They do not each carry all 84 injects. "
        f"Batch owns {lanes.get('Batch', 0)}, PV intake {lanes.get('PV intake', 0)}, "
        f"Supply {lanes.get('Supply', 0)}; the other {lanes.get('Shared', 0)} are shared gates "
        "(privacy, integrity, console, cost, continuity). "
        "Proof on each card is the challenge evidence, the rule and criterion, and a verifying test. "
        "This board is for evaluators and auditors. It is not a work queue. "
        "Daily review happens on Batch, PV, Supply, and Contradictions.</p>"
        '<div class="chip-row">'
        f'<span class="chip ok">{covered} covered</span>'
        f'<span class="chip teal">{artefact} artefact</span>'
        f'<span class="chip warn">{uncovered} not covered</span>'
        f'<span class="chip">Batch {lanes.get("Batch", 0)}</span>'
        f'<span class="chip">PV {lanes.get("PV intake", 0)}</span>'
        f'<span class="chip">Supply {lanes.get("Supply", 0)}</span>'
        f'<span class="chip">Shared {lanes.get("Shared", 0)}</span>'
        "</div>"
        '<div class="hero-grid">' + "".join(sections) + "</div>"
    )
    return _document("Injects", body=body)


def _fmt_count(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _fmt_money(value: Any, *, currency: str = "USD") -> str:
    raw = str(value or "0")
    if raw in {"", "0"}:
        return f"{currency} 0"
    return f"{currency} {raw}"


def _health_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return '<p class="muted">None recorded on this process yet.</p>'
    head = "".join(f"<th>{escape(item)}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (
        '<div class="table-wrap"><table class="work-table history-table health-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def render_health_page(snapshot: dict[str, Any]) -> str:
    fill = max(0, min(100, int(snapshot.get("token_fill_pct") or 0)))
    prompt_share = max(0, min(100, int(snapshot.get("prompt_share_pct") or 0)))
    completion_share = max(0, min(100, int(snapshot.get("completion_share_pct") or 0)))
    meter_class = "health-fill warn" if fill >= 80 else "health-fill"
    inference_on = not bool(snapshot.get("kill_switch"))
    status = str(snapshot.get("status") or "nominal")
    banner_class = {"nominal": "ok", "attention": "warn", "inference_off": "off"}.get(status, "ok")
    inference_chip = "ok" if inference_on else "warn"
    inference_label = "on" if inference_on else "off"
    cost = snapshot.get("cost") if isinstance(snapshot.get("cost"), dict) else {}
    cost_figure = (
        _fmt_money(cost.get("inference_cost"), currency=str(cost.get("currency") or "USD"))
        if cost.get("priced")
        else "unpriced"
    )
    wallet = snapshot.get("wallet") if isinstance(snapshot.get("wallet"), dict) else {}
    budgets = snapshot.get("budgets") if isinstance(snapshot.get("budgets"), dict) else {}
    missing = [str(item) for item in (cost.get("missing_components") or [])]
    deployments = [item for item in (snapshot.get("deployments") or []) if isinstance(item, dict)]
    recent = [item for item in (snapshot.get("recent_llm") or []) if isinstance(item, dict)]
    sessions = [item for item in (snapshot.get("sessions") or []) if isinstance(item, dict)]
    audit_rows = [item for item in (snapshot.get("audit_by_event") or []) if isinstance(item, dict)]
    kpis = (
        ("Status", status.replace("_", " "), str(snapshot.get("status_reason") or "")),
        ("Mode", str(snapshot.get("mode") or ""), "AEGIS_RUNTIME_MODE for this process"),
        ("Inference", inference_label, "Kill switch is the conjunction of mode and LLM enablement"),
        ("LLM calls", _fmt_count(snapshot.get("llm_calls")), f"{_fmt_count(snapshot.get('llm_live_calls'))} with recorded tokens"),
        ("Tokens", _fmt_count(snapshot.get("total_tokens")), "Azure usage; stub rows stay at zero"),
        ("Inference cost", cost_figure, "Partial. Listed card × recorded tokens"),
        ("AuthZ denials", _fmt_count(snapshot.get("authz_denials")), "deny or *_refused on the in-memory audit"),
        ("Reviewer actions", _fmt_count(snapshot.get("review_decisions")), f"{_fmt_count(snapshot.get('evidence_opened'))} evidence items opened"),
    )
    cards = "".join(
        '<article class="kpi">'
        f'<p class="kpi-label">{escape(label)}</p>'
        f'<p class="kpi-value">{escape(value)}</p>'
        f'<p class="kpi-foot">{escape(foot)}</p>'
        "</article>"
        for label, value, foot in kpis
    )
    dep_rows = [
        [
            escape(str(item.get("deployment") or "")),
            escape(_fmt_count(item.get("calls"))),
            escape(_fmt_count(item.get("prompt_tokens"))),
            escape(_fmt_count(item.get("completion_tokens"))),
            escape(_fmt_money(item.get("inference_cost"), currency=str(cost.get("currency") or "USD"))),
        ]
        for item in deployments
    ]
    recent_rows = [
        [
            escape(str(item.get("request_id") or "")),
            escape(str(item.get("deployment") or "")),
            escape(_fmt_count(item.get("prompt_tokens"))),
            escape(_fmt_count(item.get("completion_tokens"))),
            escape(_fmt_money(item.get("inference_cost"), currency=str(cost.get("currency") or "USD"))),
        ]
        for item in recent
    ]
    session_rows = [
        [
            escape(str(item.get("entity") or "—")),
            escape(str(item.get("product") or "—")),
            escape(str(item.get("workflow") or "")),
            escape(str(item.get("request_id") or "")),
        ]
        for item in sessions[:12]
    ]
    audit_html = "".join(
        f'<span class="chip">{escape(str(item.get("event") or ""))} {escape(_fmt_count(item.get("count")))}</span>'
        for item in audit_rows
    ) or '<span class="muted">No audit events in this process yet.</span>'
    leftover = len(sessions) - 12
    extra_sessions = ""
    if leftover > 0:
        extra_sessions = f'<p class="muted">{leftover} more loaded packs are in this process.</p>'
    missing_html = ", ".join(escape(item) for item in missing) or "none named"
    body = (
        '<div class="page-title"><h1>Runtime health</h1>'
        f'<span class="chip {inference_chip}">Inference {escape(inference_label)}</span></div>'
        f'<section class="health-banner {banner_class}">'
        f"<strong>{escape(status.replace('_', ' ').title())}</strong>"
        f"<p>{escape(str(snapshot.get('status_reason') or ''))}</p>"
        '<p class="muted">In-process evidence chain and kernel audit. Not OpenTelemetry. '
        "No collector, exporter, or scrape. Assessment still runs offline.</p>"
        "</section>"
        f'<p class="chip-row">'
        f'<span class="chip">Store {escape(str(snapshot.get("store") or "in_process"))}</span>'
        f'<span class="chip">Telemetry {escape(str(snapshot.get("telemetry") or "evidence_chain"))}</span>'
        f'<span class="chip">Guard fails {_fmt_count(snapshot.get("guard_fail"))}</span>'
        f'<span class="chip">Chains {_fmt_count(snapshot.get("chain_count"))}</span>'
        f'<span class="chip">Zero-token calls {_fmt_count(snapshot.get("llm_zero_token_calls"))}</span>'
        "</p>"
        f'<div class="kpi-row">{cards}</div>'
        '<div class="health-grid">'
        '<article class="card">'
        "<h2>Control plane</h2>"
        "<p>Mode, kill switch, and per-request ceilings. Changing a ceiling needs an ADR.</p>"
        "<dl class=\"health-dl\">"
        f"<div><dt>Mode</dt><dd>{escape(str(snapshot.get('mode') or ''))}</dd></div>"
        f"<div><dt>LLM enabled</dt><dd>{'yes' if snapshot.get('llm_enabled') else 'no'}</dd></div>"
        f"<div><dt>Inference allowed</dt><dd>{'yes' if snapshot.get('inference_allowed') else 'no'}</dd></div>"
        f"<div><dt>Kill switch</dt><dd>{'engaged' if snapshot.get('kill_switch') else 'clear'}</dd></div>"
        f"<div><dt>Max tokens / request</dt><dd>{escape(_fmt_count(budgets.get('max_input_tokens')))}</dd></div>"
        f"<div><dt>Max steps</dt><dd>{escape(_fmt_count(budgets.get('max_steps')))}</dd></div>"
        f"<div><dt>Max tool calls</dt><dd>{escape(_fmt_count(budgets.get('max_tool_calls')))}</dd></div>"
        "</dl>"
        "</article>"
        '<article class="card health-cost">'
        "<h2>LLM cost</h2>"
        "<p>Recorded prompt and completion tokens multiplied by the listed unit prices. "
        "This is not an invoice and not cost per successful task. The total is <strong>partial</strong>.</p>"
        f'<p class="kpi-value">{escape(cost_figure)}</p>'
        '<p class="chip-row">'
        f'<span class="chip">Prompt {_fmt_money(cost.get("prompt_cost"), currency=str(cost.get("currency") or "USD"))}</span>'
        f'<span class="chip">Completion {_fmt_money(cost.get("completion_cost"), currency=str(cost.get("currency") or "USD"))}</span>'
        f'<span class="chip">Card {escape(str(cost.get("model") or "unlisted"))}</span>'
        f'<span class="chip">Vendor {escape(str(cost.get("vendor") or "unlisted"))}</span>'
        "</p>"
        "<dl class=\"health-dl\">"
        f"<div><dt>Input / 1M</dt><dd>{escape(str(cost.get('currency') or 'USD'))} {escape(str(cost.get('input_per_million') or '—'))}</dd></div>"
        f"<div><dt>Output / 1M</dt><dd>{escape(str(cost.get('currency') or 'USD'))} {escape(str(cost.get('output_per_million') or '—'))}</dd></div>"
        f"<div><dt>Basis</dt><dd>{escape(str(cost.get('basis') or 'recorded_tokens_x_listed_unit_price'))}</dd></div>"
        f"<div><dt>Source</dt><dd>{escape(str(cost.get('source') or 'tests/fixtures/synthetic/data/model_costs.csv'))}</dd></div>"
        f"<div><dt>Missing from TCO</dt><dd>{missing_html}</dd></div>"
        "</dl>"
        "<p>Stub calls contribute zero because Azure <code>usage</code> was recorded as zero. "
        "Human review, platform, and observability are named missing — they are not treated as zero.</p>"
        "</article>"
        '<article class="card">'
        "<h2>Token utilisation</h2>"
        "<p>Process total against the per-request ceiling — a budget reference, not cluster capacity.</p>"
        f'<p class="chip-row"><span class="chip">Prompt {_fmt_count(snapshot.get("prompt_tokens"))}</span>'
        f'<span class="chip">Completion {_fmt_count(snapshot.get("completion_tokens"))}</span>'
        f'<span class="chip">Ceiling {_fmt_count(snapshot.get("token_ceiling"))}</span>'
        f'<span class="chip">{fill}% of one-request ceiling</span></p>'
        f'<div class="health-meter" role="meter" aria-valuemin="0" aria-valuemax="100" '
        f'aria-valuenow="{fill}" aria-label="Recorded tokens versus per-request ceiling">'
        f'<span class="{meter_class}" style="width:{fill}%"></span></div>'
        '<p class="muted">Prompt versus completion of recorded tokens</p>'
        '<div class="health-stack" role="img" aria-label="Prompt versus completion share">'
        f'<span class="prompt" style="width:{prompt_share}%"></span>'
        f'<span class="completion" style="width:{completion_share}%"></span>'
        "</div>"
        "</article>"
        '<article class="card">'
        "<h2>Wallet</h2>"
        "<p>Cumulative admission ceiling. Exhaustion refuses a new run. This page does not debit the wallet.</p>"
        "<dl class=\"health-dl\">"
        f"<div><dt>Ceiling</dt><dd>{escape(_fmt_money(wallet.get('ceiling')))}</dd></div>"
        f"<div><dt>Spent</dt><dd>{escape(_fmt_money(wallet.get('spent')))}</dd></div>"
        f"<div><dt>Remaining</dt><dd>{escape(_fmt_money(wallet.get('remaining')))}</dd></div>"
        "</dl>"
        "</article>"
        "</div>"
        "<h2>Deployments</h2>"
        + _health_table(
            ["Deployment", "Calls", "Prompt", "Completion", "Listed cost"],
            dep_rows,
        )
        + "<h2>Recent LLM records</h2>"
        + _health_table(
            ["Request", "Deployment", "Prompt", "Completion", "Listed cost"],
            recent_rows,
        )
        + "<h2>Loaded packs</h2>"
        + _health_table(["Entity", "Product", "Workflow", "Request"], session_rows)
        + extra_sessions
        + "<h2>Integrity this process</h2>"
        f'<p class="chip-row">{audit_html}</p>'
        f'<p class="muted">Acknowledge refused {_fmt_count(snapshot.get("acknowledge_refused"))}. '
        f'Guard fails {_fmt_count(snapshot.get("guard_fail"))}. '
        "See <a href=\"/history\">Evidence history</a> for the durable reviewer ledger.</p>"
        '<p class="lede">Machine-readable snapshot: <a href="/api/health">/api/health</a>.</p>'
    )
    return _document("Runtime health", body=body)


def render_agents_page(agents: list[dict[str, Any]]) -> str:
    cards = []
    for item in agents:
        tools = ", ".join(str(tool) for tool in (item.get("tools") or [])) or "none"
        interrupts = ", ".join(str(name) for name in (item.get("interrupts") or [])) or "none"
        inference = "annotations only" if item.get("inference") else "no model"
        cards.append(
            '<article class="card">'
            f"<h2>{escape(str(item.get('id')))} · {escape(str(item.get('name')))}</h2>"
            f'<p class="chip">{escape(inference)}</p>'
            f"<p>Steps: {escape(', '.join(str(step) for step in (item.get('steps') or [])) or 'kernel')}</p>"
            f"<p>Tools: {escape(tools)}. Interrupts: {escape(interrupts)}.</p>"
            "</article>"
        )
    body = (
        "<h1>Agents</h1>"
        '<p class="lede">Six runtime roles on a LangGraph that is identical to the stdlib runner. '
        "They sequence work. They do not decide, allocate, release, or merge cases. "
        "Assessment still runs the same nodes as plain functions with inference off.</p>"
        '<div class="hero-grid">' + "".join(cards) + "</div>"
    )
    return _document("Agents", body=body)


def render_contradictions(rows: list[dict[str, Any]], *, workflow: str = "", product: str = "") -> str:
    products = sorted({str(item.get("product") or "") for item in rows if item.get("product")})
    workflows = sorted({str(item.get("workflow") or "") for item in rows if item.get("workflow")})
    visible = []
    for item in rows:
        if workflow and str(item.get("workflow") or "") != workflow:
            continue
        if product and str(item.get("product") or "") != product:
            continue
        visible.append(item)
    chips = ['<a class="chip" href="/contradictions">All</a>']
    for name in workflows:
        chips.append(f'<a class="chip" href="/contradictions?workflow={quote(name)}">{escape(name)}</a>')
    for name in products:
        chips.append(f'<a class="chip" href="/contradictions?product={quote(name)}">{escape(name)}</a>')
    cards = []
    for item in visible:
        request_id = escape(str(item.get("request_id") or ""))
        record_id = escape(str(item.get("record_id") or ""))
        topic = escape(str(item.get("topic") or ""))
        left = escape(str(item.get("left") or item.get("statement") or "—"))
        right = escape(str(item.get("right") or "—"))
        values = item.get("values") or []
        if values and left == "—":
            left = escape(str(values[0]))
            right = escape(str(values[1] if len(values) > 1 else "—"))
        follow = list(item.get("follow_ups") or [])
        status = "follow-up recorded" if follow else "open"
        cards.append(
            '<article class="card contra-card">'
            f'<div class="meta-strip">'
            f'<span class="chip">{escape(str(item.get("product") or ""))}</span>'
            f'<span class="chip">{escape(str(item.get("workflow") or ""))}</span>'
            f'<span class="chip">{escape(str(item.get("entity") or ""))}</span>'
            f'<span class="chip warn">{topic}</span>'
            f'<span class="chip">{status}</span>'
            "</div>"
            '<div class="positions">'
            f'<p class="left"><strong>Position A</strong><br/>{left}'
            f'<span class="evidence-meta">{escape(str(item.get("left_source") or item.get("source") or ""))}</span></p>'
            f'<p class="right"><strong>Position B</strong><br/>{right}'
            f'<span class="evidence-meta">{escape(str(item.get("right_source") or ""))}</span></p>'
            "</div>"
            f'<p class="muted">Record {record_id}. The console does not pick a winner.</p>'
            f'<p><a href="{escape(str(item.get("href") or "/"))}">Open source pack</a></p>'
            + render_contradiction_follow_panel(item)
            + "</article>"
        )
    empty = '<p class="muted">No contradictions in the loaded packs.</p>'
    body = (
        "<h1>Consolidated contradictions</h1>"
        '<p class="lede">Every disagreement the engines found across products and workflows, in one place. '
        "Both positions stay visible. Recording a follow-up stores evidence of what you did; it does not settle the disagreement "
        "and it is not a signature.</p>"
        f'<div class="meta-strip">{"".join(chips)}</div>'
        f'<p class="muted">{len(visible)} shown of {len(rows)} total.</p>'
        + '<div class="status-grid">'
        + ("".join(cards) or empty)
        + "</div>"
    )
    return _document("Contradictions", body=body)
