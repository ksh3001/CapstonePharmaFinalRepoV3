# ADR-011: Server-rendered HITL console

- Status: Accepted
- Date: 2026-08-13

## Decision

The human-review console is Jinja + HTMX, served from `services/api`. FastAPI is the optional `ui` transport (`requirements-ui.txt`). Assessment uses the stdlib server so the console can be opened with zero installs. There is no Node runtime.

Rejected alternatives:

- **Next.js 15 / React 19** — second runtime, second lockfile, second SBOM; client data paths that BR-065 forbids.
- **Vite + React SPA** — same client-fetch problem; gating would be a discipline rather than a construction.
- **Taipy / Streamlit / Dash** — session-centric Python UIs that do not bind cleanly to validated pack contracts or segregation-of-duties re-evaluation on POST.

## Consequences

The console cannot fetch a data source. It renders validated packs and posts only to acknowledge / contest. FastAPI and Jinja are absent from `packages/` (stdlib import deny-list). Assessment mode still produces packs from the CLI with no UI process required. `python -m aegis serve` is the live console.
