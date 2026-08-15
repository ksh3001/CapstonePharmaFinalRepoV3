"""Optional Jinja rendering for ui mode. Assessment never imports jinja2."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

from packages.config.paths import repo_root
from services.api.pack_view import render_pack_body

WEB = repo_root() / "apps" / "web"
TEMPLATES = WEB / "templates"


def web_root() -> Path:
    return WEB


def _context_pack(
    pack: dict[str, Any],
    *,
    title: str,
    locale: str,
    workflow: str,
    api_available: bool,
    entity_id: str = "",
) -> dict[str, Any]:
    return {
        "title": title,
        "locale": locale,
        "direction": "rtl" if locale.startswith("ar") else "ltr",
        "pack_html": render_pack_body(
            pack,
            title=title,
            api_available=api_available,
            workflow=workflow,
            locale=locale,
            entity_id=entity_id,
        ),
    }


def jinja_available() -> bool:
    try:
        import jinja2  # noqa: F401
    except ImportError:
        return False
    return TEMPLATES.is_dir()


def render_jinja(name: str, context: dict[str, Any]) -> str:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from services.api.chrome import sidebar, user_cluster_html
    from services.api.console import render_ask_panel

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    merged = dict(context)
    merged.setdefault("user_cluster_html", user_cluster_html())
    merged.setdefault("sidebar_html", sidebar())
    merged.setdefault("chat_html", render_ask_panel())
    return env.get_template(name).render(**merged)


def render_pack_jinja(
    pack: dict[str, Any],
    *,
    title: str,
    locale: str = "en",
    api_available: bool = True,
    workflow: str = "batch",
    entity_id: str = "",
    fragment: bool = False,
) -> str:
    ctx = _context_pack(
        pack,
        title=title,
        locale=locale,
        workflow=workflow,
        api_available=api_available,
        entity_id=entity_id,
    )
    return render_jinja("pack_body.html" if fragment else "pack.html", ctx)


def evidence_href(record_id: str, request_id: str) -> str:
    href = "/evidence/" + quote(record_id, safe="")
    if request_id:
        href += "?request_id=" + quote(request_id, safe="")
    return href
