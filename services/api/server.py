"""Stdlib HTTP transport for the JSON API and server-rendered console.

FastAPI is the planned optional transport for ui/cloud modes. Assessment keeps
this stdlib server so the console can be opened with zero installs.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from packages.config.catalog import TITLES, board_entities, defaults, search_href
from packages.config.demo_auth import verify_demo_password
from packages.config.identities import default_console_user, resolve_identity
from packages.config.runtime import llm_enabled, runtime_mode
from services.api.chrome import bind_identity
from services.api.console import (
    dashboard_health_html,
    render_agents_page,
    render_contradiction_follow_panel,
    render_contradictions,
    render_entity_directory,
    render_evidence,
    render_evidence_fragment,
    render_gates_page,
    render_health_page,
    render_history_page,
    render_home,
    render_injects_page,
    render_list_page,
    render_login,
    render_message,
    render_pack_page,
    render_saved_toast,
    render_status,
    render_status_follow_panel,
)
from services.api.graphics import render_home_dashboard
from services.api.handlers import get_pack, handle, list_contradictions, list_follow_ups, list_sessions, outstanding_critical
from services.api.pack_view import render_review_actions
from services.api.templating import jinja_available, render_jinja, render_pack_jinja, web_root

DEFAULTS = defaults()
WORKFLOW_FROM_PACK = {
    "batch_evidence": "batch",
    "pv_intake": "pv",
    "supply_options": "supply",
}
PREPARER = "preparer_1"
COOKIE_NAME = "aegis_user"

_PACK_KEYS: dict[str, str] = {}


def reset_server_state() -> None:
    _PACK_KEYS.clear()


def _console_user() -> str:
    return default_console_user() or "reviewer_9"


def _safe_next(raw: str) -> str:
    href = (raw or "/").strip() or "/"
    if not href.startswith("/") or href.startswith("//"):
        return "/"
    return href


def _session_cookie(user: str) -> str:
    return f"{COOKIE_NAME}={user}; Path=/; HttpOnly; SameSite=Lax"


def _query_first(query: dict[str, list[str]], key: str, default: str = "") -> str:
    values = query.get(key) or []
    return values[0] if values else default


def _workflow_href(workflow: str, entity_id: str, request_id: str) -> str:
    path = f"/workflows/{workflow}/{entity_id}"
    if request_id:
        return path + "?request_id=" + request_id
    return path


def _load_pack(workflow: str, entity_id: str, *, request_id: str, fresh: bool) -> dict[str, Any]:
    key = f"{workflow}:{entity_id}"
    if request_id:
        packed = get_pack(request_id)
        if packed is not None:
            return {"status": 200, "payload": packed, "headers": {"content-type": "application/json"}}
    if not fresh:
        cached = _PACK_KEYS.get(key)
        if cached:
            packed = get_pack(cached)
            if packed is not None:
                return {"status": 200, "payload": packed, "headers": {"content-type": "application/json"}}
    response = handle("GET", f"/api/workflows/{workflow}/{entity_id}", user=PREPARER)
    pack = response.get("payload") or {}
    loaded = str(pack.get("request_id") or "")
    if loaded:
        _PACK_KEYS[key] = loaded
    return response


def _demo_packs() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    for item in board_entities():
        response = _load_pack(item.workflow, item.entity_id, request_id="", fresh=False)
        if response.get("status") == 200 and response.get("payload"):
            packs.append(response["payload"])
    return packs


def _wants_html(accept: str, path: str) -> bool:
    if path.startswith("/api/"):
        return False
    lowered = (accept or "").lower()
    return "application/json" not in lowered or "text/html" in lowered


def _search_target(raw: str) -> str:
    return search_href(raw)


def dispatch(
    method: str,
    path: str,
    *,
    query: dict[str, list[str]] | None = None,
    body: dict[str, Any] | None = None,
    user: str | None = None,
    accept: str = "text/html",
    hx: bool = False,
    renderer: str = "console",
) -> dict[str, Any]:
    method = method.upper()
    query = query or {}
    body = dict(body or {})
    path = unquote(path)
    if not user:
        user = _console_user()
    bind_identity(user)
    request_id = _query_first(query, "request_id") or str(body.get("request_id") or "")
    fresh = _query_first(query, "fresh") in {"1", "true", "yes"}
    if request_id and "request_id" not in body:
        body["request_id"] = request_id

    if method == "POST" and path == "/session":
        wanted = str(body.get("user") or "").strip()
        password = str(body.get("password") or "")
        ident = resolve_identity(wanted)
        next_href = _safe_next(str(body.get("next") or "/home"))
        if next_href in {"/", "/index.html", "/login"}:
            next_href = "/home"
        if ident is None or not ident.assumable:
            return _html(
                400,
                render_login(
                    next_href=next_href,
                    notice="That identity is not in the entitlement table or is not assumable.",
                ),
            )
        if not verify_demo_password(ident.user, password):
            return _html(
                401,
                render_login(
                    next_href=next_href,
                    notice="Username or password is incorrect.",
                ),
            )
        return {
            "status": 303,
            "headers": {
                "content-type": "text/html; charset=utf-8",
                "location": next_href,
                "set-cookie": _session_cookie(ident.user),
            },
            "body": f'<p>Identity set to {ident.user}. <a href="{next_href}">Continue</a></p>',
            "payload": None,
        }

    if path.rstrip("/") == "/mcp":
        from services.integration.mcp.server import handle_http

        return handle_http(method, body)

    if path.startswith("/api/"):
        result = handle(method, path, body=body, user=user)
        if method == "POST" and path.startswith("/api/reviews/"):
            payload = result.get("payload") or {}
            if hx:
                return _form_result(
                    result,
                    str(body.get("next") or "/"),
                    fragment=True,
                    panel=str(body.get("panel") or ""),
                    subject_id=str(body.get("subject_id") or ""),
                    request_id=str(payload.get("request_id") or ""),
                )
            if body.get("next"):
                return _form_result(result, str(body.get("next") or "/"))
        if hx and method == "POST" and path == "/api/ask":
            from services.api.console import render_ask_answer

            return _html(200, render_ask_answer(result.get("payload") or {}))
        return result

    if method == "GET" and path.startswith("/static/"):
        return _static(path)

    if method == "GET" and path == "/healthz":
        return {
            "status": 200,
            "headers": {"content-type": "application/json"},
            "body": None,
            "payload": {"mode": runtime_mode(), "llm": "on" if llm_enabled() else "off"},
        }

    if method == "GET" and path in {"/login", "/", "/index.html"}:
        next_href = _safe_next(_query_first(query, "next") or "/home")
        if next_href in {"/", "/index.html", "/login"}:
            next_href = "/home"
        return _html(200, render_login(next_href=next_href))

    if method == "GET" and path == "/home":
        packs = _demo_packs()
        use_jinja = renderer == "jinja" and jinja_available()
        if use_jinja:
            html = render_jinja(
                "home.html",
                {
                    "title": "AEGIS",
                    "locale": "en",
                    "direction": "ltr",
                    "mode": runtime_mode(),
                    "llm_label": "on" if llm_enabled() else "off",
                    "dashboard_html": render_home_dashboard(packs),
                    "directory_html": render_entity_directory(),
                    "health_html": dashboard_health_html(session_count=len(packs)),
                },
            )
        else:
            html = render_home(mode=runtime_mode(), llm=llm_enabled(), packs=packs)
        return _html(200, html)

    if method == "GET" and path == "/search":
        wanted = _search_target(_query_first(query, "q"))
        return dispatch(method, wanted, query=query, body=body, user=user, accept=accept, hx=hx, renderer=renderer)

    if method == "GET" and path == "/status":
        for item in board_entities():
            _load_pack(item.workflow, item.entity_id, request_id="", fresh=False)
        html = render_status(list_sessions())
        return _html(200, html)

    if method == "GET" and path == "/history":
        payload = handle("GET", "/api/history", user=user)["payload"]
        return _html(200, render_history_page(payload))

    if method == "GET" and path == "/contradictions":
        _demo_packs()
        html = render_contradictions(
            list_contradictions(),
            workflow=_query_first(query, "workflow"),
            product=_query_first(query, "product"),
        )
        return _html(200, html)

    if method == "GET" and path == "/gates":
        payload = handle("GET", "/api/gates", user=user)["payload"]
        rows = [str(item) for item in payload.get("gates") or []]
        return _html(200, render_gates_page(rows))

    if method == "GET" and path == "/injects":
        payload = handle("GET", "/api/injects/coverage", user=user)["payload"]
        return _html(200, render_injects_page(list(payload.get("injects") or [])))

    if method == "GET" and path == "/agents":
        payload = handle("GET", "/api/agents", user=user)["payload"]
        return _html(200, render_agents_page(list(payload.get("agents") or [])))

    if method == "GET" and path == "/health":
        payload = handle("GET", "/api/health", user=user)["payload"]
        return _html(200, render_health_page(payload))

    if method == "GET" and path.startswith("/evidence/"):
        record_id = path.rsplit("/", 1)[-1]
        response = handle("GET", f"/api/evidence/{record_id}", body=body, user=user)
        if response["status"] != 200:
            return _html_error(response)
        pack = get_pack(request_id) or {}
        workflow = WORKFLOW_FROM_PACK.get(str(pack.get("workflow") or ""), "batch")
        case_ids = pack.get("case_ids") or []
        entity = str(
            pack.get("batch_id")
            or (case_ids[0] if case_ids else "")
            or pack.get("event_id")
            or DEFAULTS[workflow]
        )
        html = render_evidence(
            response["payload"],
            request_id=request_id,
            return_href=_workflow_href(workflow, entity, request_id),
        )
        if hx:
            html = render_evidence_fragment(response["payload"], pack=pack)
        return _html(200, html)

    for workflow, default_id in DEFAULTS.items():
        prefix = f"/workflows/{workflow}"
        if method == "GET" and (path == prefix or path.startswith(prefix + "/")):
            rest = path[len(prefix) :].lstrip("/")
            entity_id = rest or _query_first(query, "entity") or _query_first(query, "q") or default_id
            response = _load_pack(workflow, entity_id, request_id=request_id, fresh=fresh)
            if response["status"] != 200:
                return _html_error(response)
            pack = response["payload"]
            if renderer == "jinja" and jinja_available():
                html = render_pack_jinja(
                    pack,
                    title=TITLES[workflow],
                    workflow=workflow,
                    entity_id=entity_id,
                    fragment=hx,
                )
            else:
                html = render_pack_page(
                    pack,
                    title=TITLES[workflow],
                    workflow=workflow,
                    entity_id=entity_id,
                )
            return _html(200, html)

    if not _wants_html(accept, path):
        return handle(method, path, body=body, user=user)
    return _html(404, render_message("Not found", f"No console route for {path}"))


def _html(status: int, document: str) -> dict[str, Any]:
    return {
        "status": status,
        "headers": {"content-type": "text/html; charset=utf-8"},
        "body": document,
        "payload": None,
    }


def _html_error(response: dict[str, Any]) -> dict[str, Any]:
    payload = response.get("payload") or {}
    error = payload.get("error") or {}
    message = str(error.get("message") or "Request failed")
    extra = f'<p><a href="/home">Home</a></p>'
    return _html(int(response.get("status") or 400), render_message("Request declined", message, extra=extra))


def _form_result(
    response: dict[str, Any],
    next_href: str,
    *,
    fragment: bool = False,
    panel: str = "",
    subject_id: str = "",
    request_id: str = "",
) -> dict[str, Any]:
    payload = response.get("payload") or {}
    if response["status"] != 200:
        return _html_error(response)
    message = str(payload.get("label") or payload.get("reason") or "Recorded.")
    extra = f'<p><a href="{next_href or "/"}">Back to pack</a></p>'
    title = "Recorded" if payload.get("recorded") else "Result"
    if fragment:
        rid = request_id or str(payload.get("request_id") or "")
        toast = render_saved_toast(message)
        if panel == "contradiction":
            item = next(
                (
                    row
                    for row in list_contradictions()
                    if str(row.get("request_id") or "") == rid
                    and str(row.get("record_id") or "") == subject_id
                ),
                {"request_id": rid, "record_id": subject_id, "follow_ups": []},
            )
            return _html(200, render_contradiction_follow_panel(item) + toast)
        if panel == "status":
            row = next(
                (item for item in list_sessions() if str(item.get("request_id") or "") == rid),
                {"request_id": rid, "responses": [], "remaining": []},
            )
            return _html(200, render_status_follow_panel(row) + toast)
        pack = get_pack(rid) or {}
        remaining = outstanding_critical(rid) if rid else []
        html = render_review_actions(
            pack,
            remaining=remaining,
            follow_ups=list_follow_ups(rid),
        )
        return _html(200, html + toast)
    return _html(200, render_message(title, message, extra=extra))


def _static(path: str) -> dict[str, Any]:
    relative = path[len("/static/") :]
    if ".." in relative.replace("\\", "/").split("/"):
        return _html(404, render_message("Not found", "Invalid static path"))
    target = (web_root() / "static" / relative).resolve()
    root = (web_root() / "static").resolve()
    if not str(target).startswith(str(root)) or not target.is_file():
        return _html(404, render_message("Not found", f"No static file {relative}"))
    data = target.read_bytes()
    types = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8"}
    media = types.get(target.suffix, "application/octet-stream")
    return {"status": 200, "headers": {"content-type": media}, "body": data, "payload": None}


class ConsoleHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        self._respond("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._respond("POST")

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _cookie_user(self) -> str:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == COOKIE_NAME and value:
                ident = resolve_identity(value)
                if ident is not None and ident.assumable:
                    return ident.user
        return ""

    def _user(self, query: dict[str, list[str]]) -> str:
        header = self.headers.get("X-Aegis-User", "").strip()
        if header:
            return header
        from_query = _query_first(query, "user")
        if from_query:
            return from_query
        return self._cookie_user() or _console_user()

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype == "application/json":
            parsed = json.loads(raw.decode("utf-8") or "{}")
            return parsed if isinstance(parsed, dict) else {}
        pairs = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
        return {key: values[-1] if values else "" for key, values in pairs.items()}

    def _respond(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path or "/"
        query = parse_qs(parsed.query, keep_blank_values=True)
        body = self._body() if method == "POST" else {}
        user = self._user(query)
        accept = self.headers.get("Accept") or "text/html"
        hx = (self.headers.get("HX-Request") or "").lower() == "true"
        result = dispatch(method, path, query=query, body=body, user=user, accept=accept, hx=hx)
        status = int(result["status"])
        headers = dict(result.get("headers") or {})
        payload_body = result.get("body")
        if payload_body is None and result.get("payload") is not None:
            payload_body = json.dumps(result["payload"])
            headers.setdefault("content-type", "application/json")
        if isinstance(payload_body, bytes):
            data = payload_body
        else:
            data = str(payload_body or "").encode("utf-8")
        headers.setdefault("content-length", str(len(data)))
        headers.setdefault("cache-control", "no-store")
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, str(value))
        self.end_headers()
        self.wfile.write(data)


def serve(host: str = "127.0.0.1", port: int = 8000) -> int:
    from services.integration.azure.openai import configure_inference

    configure_inference(override=True)
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        from services.api.fastapi_app import serve_uvicorn

        sys.stdout.write(
            f"AEGIS console (FastAPI) http://{host}:{port}/ mode={runtime_mode()} llm_enabled={llm_enabled()}\n"
        )
        sys.stdout.flush()
        return serve_uvicorn(host, port)
    except ImportError:
        pass
    server = ThreadingHTTPServer((host, port), ConsoleHandler)
    url = f"http://{host}:{port}/"
    sys.stdout.write(f"AEGIS console {url} mode={runtime_mode()} llm_enabled={llm_enabled()}\n")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nstopped\n")
    finally:
        server.server_close()
    return 0
