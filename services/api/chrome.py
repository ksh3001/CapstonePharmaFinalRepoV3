"""Shared console chrome. Presentation only."""

from __future__ import annotations

from contextvars import ContextVar
from html import escape

from packages.config.identities import (
    SessionIdentity,
    default_console_user,
    resolve_identity,
    unresolved_identity,
)

ICONS = {
    "home": '<path d="M4 11 12 4l8 7"/><path d="M6 10.5V20h4.5v-5h3v5H18v-9.5"/>',
    "batch": '<rect x="4" y="5" width="16" height="14" rx="2"/><path d="M8 9h8M8 12h8M8 15h5"/>',
    "pv": '<path d="M12 21s7-4.4 7-11a7 7 0 1 0-14 0c0 6.6 7 11 7 11z"/><circle cx="12" cy="10" r="2.2"/>',
    "supply": '<path d="M3 16h13l5-6H9L3 16z"/><circle cx="8" cy="18.5" r="1.6"/><circle cx="16" cy="18.5" r="1.6"/>',
    "status": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "history": '<path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h6"/>',
    "split": '<rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="14" y="4" width="7" height="16" rx="1.5"/><path d="M12 8v8"/>',
    "gates": '<path d="M5 11V7a7 7 0 0 1 14 0v4"/><rect x="5" y="11" width="14" height="10" rx="2"/>',
    "injects": '<path d="M12 3v12"/><path d="m8 11 4 4 4-4"/><path d="M5 19h14"/>',
    "agents": '<circle cx="8" cy="8" r="2.4"/><circle cx="16" cy="8" r="2.4"/><circle cx="12" cy="16" r="2.4"/><path d="M9.6 9.6 11 14.2M14.4 9.6 13 14.2M10.2 8h3.6"/>',
    "health": '<path d="M3 12h3.5l2-7 3 14 2.5-7H21"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>',
    "bell": '<path d="M6 16h12l-1.2-2.2V10a4.8 4.8 0 1 0-9.6 0v3.8L6 16z"/><path d="M10 16a2 2 0 0 0 4 0"/>',
    "chat": '<path d="M5 6h14v10H9l-4 3V6z"/>',
    "menu": '<path d="M5 7h14M5 12h14M5 17h14"/>',
}


def icon(name: str) -> str:
    path = ICONS.get(name) or ICONS["home"]
    return (
        f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


def sidebar() -> str:
    primary = (
        ("/home", "home", "Dashboard"),
        ("/workflows/batch", "batch", "Batch"),
        ("/workflows/pv", "pv", "PV intake"),
        ("/workflows/supply", "supply", "Supply"),
        ("/contradictions", "split", "Contradictions"),
        ("/status", "status", "Status"),
        ("/history", "history", "Evidence history"),
    )
    oversight = (
        ("/gates", "gates", "Gates"),
        ("/injects", "injects", "Injects"),
        ("/agents", "agents", "Agents"),
        ("/health", "health", "Runtime health"),
    )
    primary_links = "".join(
        f'<a class="side-link" href="{href}">{icon(name)}<span>{label}</span></a>'
        for href, name, label in primary
    )
    oversight_links = "".join(
        f'<a class="side-link quiet" href="{href}">{icon(name)}<span>{label}</span></a>'
        for href, name, label in oversight
    )
    return (
        '<aside class="sidebar" id="app-nav" aria-label="AEGIS">'
        f'<a class="side-brand" href="/home">{icon("batch")}<span>AEGIS</span></a>'
        f'<nav class="side-primary" aria-label="Review">{primary_links}</nav>'
        '<p class="side-heading">Oversight</p>'
        f'<nav class="side-oversight" aria-label="Oversight">{oversight_links}</nav>'
        '<p class="side-note">Daily review is Batch, PV, Supply, Contradictions, Status, and Evidence history. '
        "Gates, Injects, Agents, and Runtime health explain controls, challenge coverage, "
        "declared LangGraph roles, and in-process evidence-chain counts. "
        "They are not a work queue.</p>"
        "</aside>"
    )


_SESSION: ContextVar[SessionIdentity | None] = ContextVar("aegis_session", default=None)


def bind_identity(user: str) -> SessionIdentity:
    ident = resolve_identity(user) or unresolved_identity(user or default_console_user())
    _SESSION.set(ident)
    return ident


def current_identity() -> SessionIdentity:
    ident = _SESSION.get()
    if ident is not None:
        return ident
    return resolve_identity(default_console_user()) or unresolved_identity(default_console_user())


def user_cluster_html() -> str:
    current = current_identity()
    return (
        '<div class="user-chip">'
        f'<span class="avatar">{escape(current.initials)}</span>'
        '<span class="user-meta">'
        f'<span class="user-name">{escape(current.user)}</span>'
        f'<span class="user-role">{escape(current.display_role)}</span>'
        "</span>"
        '<a class="login-link" href="/">Switch</a>'
        "</div>"
    )


def topbar() -> str:
    return (
        '<header class="topbar">'
        '<label class="top-menu" for="nav-toggle">'
        f'{icon("menu")}'
        '<span class="sr-only">Open or close navigation</span>'
        "</label>"
        '<form class="top-search" method="get" action="/search" role="search">'
        f'{icon("search")}'
        '<label class="sr-only" for="q">Search pack id</label>'
        '<input id="q" name="q" type="search" placeholder="Search batch, case or event id"/>'
        "</form>"
        '<a class="top-logo" href="/home">'
        '<span class="logo-ring"></span><strong>AEGIS</strong>'
        "</a>"
        '<div class="top-right">'
        f'<a class="login-link" href="/">Demo sign-in</a>'
        f'<a class="icon-btn" href="/status" title="Status">{icon("bell")}</a>'
        + user_cluster_html()
        + "</div>"
        "</header>"
    )


def _chat_panel() -> str:
    from services.api.console import render_ask_panel

    return render_ask_panel()


def wrap_shell(body: str, *, title: str, locale: str = "en", direction: str = "ltr", css: str = "") -> str:
    return (
        "<!DOCTYPE html>"
        f'<html lang="{escape(locale)}" dir="{escape(direction)}">'
        '<head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        f"<title>{escape(title)}</title>"
        '<link rel="stylesheet" href="/static/aegis.css"/>'
        '<script src="/static/htmx.min.js" defer></script>'
        f"<style>{css}</style>"
        "</head><body>"
        '<input id="nav-toggle" class="nav-toggle" type="checkbox"/>'
        '<label class="nav-scrim" for="nav-toggle"><span class="sr-only">Close navigation</span></label>'
        '<input id="chat-toggle" class="chat-toggle" type="checkbox"/>'
        '<div class="app">'
        + sidebar()
        + '<div class="app-frame">'
        + topbar()
        + f'<main class="canvas">{body}</main>'
        + "</div></div>"
        + _chat_panel()
        + '<div id="aegis-toast" class="toast" role="status" aria-live="polite" hidden></div>'
        + '<script>var n=document.getElementById("identity-next");'
        "if(n)n.value=location.pathname+location.search;</script>"
        "</body></html>"
    )
