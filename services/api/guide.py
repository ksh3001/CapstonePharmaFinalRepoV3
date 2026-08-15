"""In-console user guide. Presentation only — no classification (BR-064)."""

from __future__ import annotations

from html import escape

from services.api.chrome import icon


def _preview(href: str, caption: str) -> str:
    slug = href.strip("/").replace("/", "-") or "home"
    src = f"/static/guide/{slug}.jpg"
    return (
        f'<figure class="guide-shot">'
        f'<img src="{escape(src)}" alt="Screenshot of the {escape(caption)} page" width="1000" height="628"/>'
        f"<figcaption>{escape(caption)} — live console</figcaption></figure>"
    )


_PAGES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "home",
        "/",
        "Dashboard",
        "Start here after you assume an identity. The dashboard shows runtime mode, whether the model is on, a health strip, and cards into the three workflows.",
        "Open Batch, PV, or Supply from the left rail or the directory. Pack chat (bottom right) answers status or graph questions for a catalog id. This page does not decide a batch, case, or shipment.",
    ),
    (
        "pack",
        "/workflows/batch",
        "Batch evidence",
        "Workflow A. Pick a batch id (for example NCB204-B24071). The pack shows findings, contradictions, gaps, abstentions, and cited evidence with equal prominence.",
        "Open every critical evidence row (Viewed / hx-get drawer) before Acknowledge is offered. Acknowledge and Contest are workflow events, not signatures and not a disposition. The graphical view counts this pack only — it is not analytics.",
    ),
    (
        "pack",
        "/workflows/pv",
        "PV intake",
        "Workflow B. Pick a case or signal id. The pack retains clocks, duplicate candidates, listedness context, and terminology versions without pooling or expectedness.",
        "Sensitive segments (for example pregnancy) appear only for an entitled role such as the safety physician. An unentitled role sees them withheld. The console never confirms a safety signal.",
    ),
    (
        "pack",
        "/workflows/supply",
        "Supply / cold-chain",
        "Workflow C. Pick a shipment or event id. Options, constraints, and quality holds are draft descriptions. Contested capacity is not treated as available stock.",
        "The pack may name a substitute or a customs mismatch. It does not move stock, reserve, or start a recall. Approvals required where stock would move stay on the pack as text.",
    ),
    (
        "board",
        "/contradictions",
        "Contradictions",
        "A board of both-positions findings across loaded packs. Filter by workflow or product. Each row can store a per-item follow-up as evidence.",
        "Both sides of a contradiction stay visible. The board does not pick a winner or merge records.",
    ),
    (
        "list",
        "/status",
        "Workflow status",
        "Review progress for packs already opened in this session. When critical evidence is opened, record the action taken. That note is stored on the evidence chain.",
        "The bell in the header jumps here. Remaining critical items keep acknowledgement unavailable. This is not a work-queue product — only packs this process has loaded appear.",
    ),
    (
        "list",
        "/history",
        "Evidence history",
        "Append-only chain of reviewer actions: evidence opened, acknowledgement, contest, and stored follow-ups.",
        "Use this to show what was recorded for a request id. The chain is hash-linked. Tamper or a deleted middle record is a finding, not a silent edit.",
    ),
    (
        "list",
        "/gates",
        "Gates",
        "Oversight page. Lists the controls the product claims: deny-by-default, kill switch, forced evidence view, and non-execution.",
        "Gates are not agents. This page explains controls; it is not a queue of items to clear.",
    ),
    (
        "list",
        "/injects",
        "Injects",
        "Challenge-coverage map (INJ-001…084). Shows which injects have a business rule, an acceptance criterion, and a test class.",
        "Use it in a defence demo to show coverage. It does not run the injects.",
    ),
    (
        "list",
        "/agents",
        "Agents",
        "The six declared runtime agent roles and what each may do. Orchestration sequences; engines classify.",
        "If LangGraph is installed it still calls the same stdlib engines. This page does not start an unbounded agent.",
    ),
    (
        "list",
        "/health",
        "Runtime health",
        "In-process snapshot: mode, kill switch, token counts, listed inference cost, denials, and evidence-chain rollups. Not OpenTelemetry.",
        "Open full telemetry from the dashboard strip. Counters are for this process. They are not an SLO burn chart.",
    ),
    (
        "chat",
        "/api/ask",
        "Pack chat",
        "The purple button at the bottom right. Ask for pack status or what is linked to a catalog batch, case, or event id.",
        "You get the engine or graph tool result, then a short restatement. Decide-language is refused. This is not a disposition chatbot.",
    ),
)


def _page_article(kind: str, href: str, title: str, lede: str, detail: str) -> str:
    return (
        '<article class="guide-page" id="guide-'
        + escape(href.strip("/").replace("/", "-") or "home")
        + '">'
        f'<div class="guide-page-copy"><h3>{escape(title)}</h3>'
        f'<p class="guide-path"><a href="{escape(href)}">{escape(href)}</a></p>'
        f"<p>{escape(lede)}</p><p>{escape(detail)}</p></div>"
        f"{_preview(href, title)}"
        "</article>"
    )


def guide_button() -> str:
    return (
        '<label class="icon-btn guide-open" for="guide-toggle" title="User guide">'
        f'{icon("guide")}'
        '<span class="sr-only">Open user guide</span>'
        "</label>"
    )


def guide_panel() -> str:
    toc = "".join(
        f'<a href="#guide-{escape(href.strip("/").replace("/", "-") or "home")}">{escape(title)}</a>'
        for _kind, href, title, _lede, _detail in _PAGES
    )
    articles = "".join(_page_article(*row) for row in _PAGES)
    return (
        '<div class="guide-layer" id="user-guide" role="dialog" aria-modal="true" '
        'aria-labelledby="guide-title">'
        '<label class="guide-scrim" for="guide-toggle"><span class="sr-only">Close user guide</span></label>'
        '<div class="guide-sheet">'
        '<header class="guide-head">'
        "<div><p class=\"guide-kicker\">AEGIS console</p>"
        '<h2 id="guide-title">User guide</h2></div>'
        '<label class="guide-close" for="guide-toggle">Close</label>'
        "</header>"
        '<p class="guide-lede">Advisory, human-in-the-loop evidence reconciliation. '
        "Deterministic engines produce the pack. This console is how a reviewer sees it, "
        "opens evidence, and records a follow-up. It is not a batch-disposition, PV-decision, "
        "eligibility, stock-movement, or recall system.</p>"
        f'<nav class="guide-toc" aria-label="Guide sections">{toc}</nav>'
        '<section class="guide-block">'
        "<h3>Header (top right)</h3>"
        "<p>After you assume an identity, the question-mark icon opens this guide. "
        "The bell opens Workflow status. The name picker changes the assumed role "
        "(Qualified Person, safety physician, reviewer, and others). Entitlement changes "
        "what you can see; it never grants the console authority to act in a system of record.</p>"
        "</section>"
        '<section class="guide-block">'
        "<h3>How a review works</h3>"
        "<ol>"
        "<li>Assume an identity in the header (Qualified Person, safety physician, reviewer, and others).</li>"
        "<li>Open a workflow pack and read findings, contradictions, gaps, and abstentions together.</li>"
        "<li>Open every critical evidence item. Acknowledgement stays unavailable until they are opened.</li>"
        "<li>On Status, record the action taken. That note is stored on the evidence chain.</li>"
        "<li>Open Evidence history to see every stored acknowledgement, contest, and opened item.</li>"
        "</ol>"
        "</section>"
        f'<div class="guide-pages">{articles}</div>'
        "</div></div>"
    )


def guide_toggle() -> str:
    return '<input id="guide-toggle" class="guide-toggle" type="checkbox"/>'
