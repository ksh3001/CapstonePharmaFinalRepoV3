"""Cursor MCP entry. Resolves the repo root so cwd does not matter."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from services.integration.mcp.server import serve_stdio  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(serve_stdio())
