# TASK-025 — Server-rendered console screens

**Goal:** four core screens as HTML in assessment, plus a live HTMX console. Templates format packs; they compute no rule. Forced evidence view, equal prominence, keyboard focus, RTL/Hindi, degraded runbook state.

## Specs to load

`specs/features/FR-008`; `specs/api/api_contracts.md` §7; NFR-14, NFR-15; AC-FR008-01…04, 06…11; AC-FR013-16; ADR-011.

Do not put a regulated-action control in the markup. Do not require Playwright, axe, or Node for assessment.

## Out of scope

Changing engines · electronic signatures · a Node/React client.

## Steps

1. `services/api/console.py` renders findings, gaps, abstentions, contradictions and evidence as sibling regions (assessment, zero installs).
2. Acknowledge is absent until critical evidence is opened; the label is not a signature.
3. Annotations are labelled `Model-generated`.
4. `python -m aegis serve` serves those screens over HTTP (`services/api/server.py`).
5. `apps/web/templates/` Jinja templates and `apps/web/static/htmx.min.js` provide the live HTMX UI. FastAPI (`services/api/fastapi_app.py`) is optional transport when `requirements-ui.txt` is installed.
6. HTMX attributes (`hx-get`, `hx-post`, `hx-target`) request fragments; the server still re-evaluates the acknowledgement gate on POST.

## Done when

`python -m aegis test` is green; `tests/e2e/` console and HTMX tests pass. FastAPI tests skip when FastAPI is not installed.
