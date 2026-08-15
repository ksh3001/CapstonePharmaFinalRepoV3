"""Stdlib MCP stdio server. Read-only tools only. No third-party mcp import.

MCP stdio is newline-delimited JSON-RPC (not LSP Content-Length).
"""

from __future__ import annotations

import json
import sys
from typing import Any

PROTOCOL = "2024-11-05"
KNOWN_PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")


def _write(message: dict[str, Any], stream: Any) -> None:
    raw = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    stream.write(raw + b"\n")
    stream.flush()


def _read_content_length(stream: Any, first_line: bytes) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    key, _, value = first_line.decode("ascii", errors="replace").partition(":")
    headers[key.strip().casefold()] = value.strip()
    while True:
        line = stream.readline()
        if not line:
            return None
        if line in {b"\r\n", b"\n"}:
            break
        key, _, value = line.decode("ascii", errors="replace").partition(":")
        headers[key.strip().casefold()] = value.strip()
    length = int(headers.get("content-length") or 0)
    if length <= 0:
        return None
    payload = stream.read(length)
    parsed = json.loads(payload.decode("utf-8"))
    return parsed if isinstance(parsed, dict) else None


def _read(stream: Any) -> dict[str, Any] | None:
    while True:
        line = stream.readline()
        if not line:
            return None
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith(b"content-length:"):
            return _read_content_length(stream, stripped)
        parsed = json.loads(stripped.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else None


def handle_http(method: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Streamable HTTP transport for Cursor. Avoids spawning a stdio Python process."""
    headers = {
        "content-type": "application/json",
        "mcp-protocol-version": PROTOCOL,
        "mcp-session-id": "aegis-mcp-demo",
        "access-control-allow-origin": "*",
        "access-control-allow-headers": "content-type,mcp-protocol-version,mcp-session-id",
        "access-control-allow-methods": "GET,POST,OPTIONS",
    }
    method = method.upper()
    if method == "OPTIONS":
        return {"status": 204, "headers": headers, "body": "", "payload": None}
    if method == "GET":
        return {
            "status": 200,
            "headers": headers,
            "body": None,
            "payload": {"name": "aegis-engine", "transport": "streamable-http"},
        }
    reply = handle_rpc(body or {})
    if reply is None:
        return {"status": 202, "headers": headers, "body": None, "payload": {}}
    return {"status": 200, "headers": headers, "body": None, "payload": reply}


def handle_rpc(message: dict[str, Any], *, user: str = "reviewer_9") -> dict[str, Any] | None:
    method = str(message.get("method") or "")
    req_id = message.get("id")
    params = message.get("params") if isinstance(message.get("params"), dict) else {}
    if method == "initialize":
        wanted = str(params.get("protocolVersion") or PROTOCOL)
        version = wanted if wanted in KNOWN_PROTOCOLS else PROTOCOL
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aegis-engine", "version": "1.0"},
                "instructions": (
                    "Read-only AEGIS engine. Ask for a catalog id such as "
                    "NCB204-B24071, PV-1001, or SH-901 for pack status or "
                    "the relation-graph neighbourhood. Advisory only."
                ),
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        from services.integration.mcp.tools import approved_tools

        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": approved_tools()}}
    if method == "tools/call":
        from services.integration.mcp.tools import call_tool, tool_is_read_only

        name = str(params.get("name") or "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        if not tool_is_read_only(name):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "WRITE_TOOL_REFUSED"},
            }
        result = call_tool(name, arguments, user=user)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "isError": not bool(result.get("ok")),
            },
        }
    if req_id is None:
        return None
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def serve_stdio() -> int:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    try:
        while True:
            message = _read(stdin)
            if message is None:
                return 0
            reply = handle_rpc(message)
            if reply is not None:
                _write(reply, stdout)
    except Exception as exc:  # noqa: BLE001 — surface startup/read failures to Cursor output
        sys.stderr.write(f"aegis-engine mcp failed: {exc}\n")
        return 1
