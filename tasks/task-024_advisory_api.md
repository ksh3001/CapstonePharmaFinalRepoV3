# TASK-024 — Advisory API surface for the console

**Goal:** expose workflow packs over a stdlib JSON handler. Assessment calls `handle()`, not a live server. Templates and handlers compute no business rule (BR-064).

## Specs to load

`specs/api/api_contracts.md`; FR-008 BR-064, BR-069, BR-071; AC-FR008-05, AC-FR008-12.

Do not add a third mutation. Do not implement FastAPI as a test dependency.

## Out of scope

Jinja screens (TASK-025) · Azure OpenAI (TASK-030).

## Steps

1. `services/api/handlers.py` dispatches GET workflow/scenario/evidence/gates/injects and POST acknowledge/contest.
2. Unentitled segments are absent from the payload body.
3. The preparer of a pack cannot acknowledge it.

## Done when

`python -m aegis test` is green; `tests/security/test_payload_entitlement.py` and `tests/security/test_segregation_of_duties.py` pass.
