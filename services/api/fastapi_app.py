"""Optional FastAPI transport. Assessment does not import FastAPI at collection unless this module is loaded."""

from __future__ import annotations

from typing import Any

from services.api.server import dispatch
from services.api.templating import web_root

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse, Response
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover
    FastAPI = None  # type: ignore[misc, assignment]
    Request = None  # type: ignore[misc, assignment]
    JSONResponse = None  # type: ignore[misc, assignment]
    Response = None  # type: ignore[misc, assignment]
    StaticFiles = None  # type: ignore[misc, assignment]


def create_app() -> Any:
    if FastAPI is None:
        raise ImportError("FastAPI is not installed; pip install -r requirements-ui.txt")

    app = FastAPI(
        title="AEGIS",
        version="1.0",
        description="Advisory HITL console. Mutations: acknowledge and contest only.",
    )
    static = web_root() / "static"
    if static.is_dir():
        app.mount("/static", StaticFiles(directory=str(static)), name="static")

    def _user(request: Request) -> str:
        header = request.headers.get("x-aegis-user", "").strip()
        if header:
            return header
        query_user = str(request.query_params.get("user") or "").strip()
        if query_user:
            return query_user
        cookie = str(request.cookies.get("aegis_user") or "").strip()
        if cookie:
            from packages.config.identities import resolve_identity

            ident = resolve_identity(cookie)
            if ident is not None and ident.assumable:
                return ident.user
        from packages.config.identities import default_console_user

        return default_console_user() or "reviewer_9"

    async def _dispatch(request: Request, path: str) -> Response:
        query: dict[str, list[str]] = {}
        for key in request.query_params:
            query[key] = list(request.query_params.getlist(key))
        body: dict[str, Any] = {}
        if request.method == "POST":
            ctype = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
            if ctype == "application/json":
                try:
                    payload = await request.json()
                except Exception:  # noqa: BLE001 — empty or non-JSON body
                    payload = {}
                if isinstance(payload, dict):
                    body = payload
            else:
                form = await request.form()
                body = {str(key): str(form.get(key) or "") for key in form}
        result = dispatch(
            request.method,
            path,
            query=query,
            body=body,
            user=_user(request),
            accept=request.headers.get("accept") or "text/html",
            hx=request.headers.get("hx-request", "").lower() == "true",
            renderer="jinja",
        )
        status = int(result["status"])
        headers = dict(result.get("headers") or {})
        if result.get("payload") is not None and result.get("body") is None:
            response = JSONResponse(result["payload"], status_code=status)
            for key, value in headers.items():
                if key.lower() in {"content-type", "content-length"}:
                    continue
                response.headers[key] = str(value)
            return response
        raw = result.get("body") or b""
        media = str(headers.get("content-type") or "text/html; charset=utf-8")
        response = Response(content=raw, status_code=status, media_type=media)
        for key, value in headers.items():
            if key.lower() in {"content-type", "content-length"}:
                continue
            response.headers[key] = str(value)
        return response

    @app.api_route("/", methods=["GET", "POST", "OPTIONS"])
    async def root(request: Request) -> Response:
        return await _dispatch(request, "/")

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "OPTIONS"])
    async def catch_all(request: Request, full_path: str) -> Response:
        return await _dispatch(request, "/" + full_path)

    return app


def serve_uvicorn(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run(create_app(), host=host, port=port, log_level="info")
    return 0
