#!/usr/bin/env bash
# Azure App Service Linux startup. Working directory is the site root.
# Keep this file LF-only (.gitattributes). CRLF breaks bash on Linux.
# Must use ASGI (uvicorn). Plain gunicorn sync = WSGI and crashes FastAPI.
set -euo pipefail
PORT="${PORT:-8000}"
exec python -m uvicorn app:app --host 0.0.0.0 --port "${PORT}"
