# TASK-030 — Azure OpenAI adapter behind InferencePort

**Goal:** advisory-only narrative. Assessment and unconfigured modes make zero outbound calls. Key auth is forbidden. Floating aliases are refused. Annotations sit on `human_review` only.

## Specs to load

`specs/features/FR-013`; plan §34.4; AC-FR013-01, 02, 08–12, 14, 17, 19; AC-FR014-05.

Do not import `services/` from `packages/`. Do not put `AZURE_OPENAI_API_KEY` in `.env.example`. Do not start a network call.

TASK-033 must exist first (BR-116).

## Out of scope

Live Azure traffic · cassette eval suite (TASK-032).

## Steps

1. `packages/advice/port.py` and `packages/advice/resolve.py` keep a Null adapter by default.
2. `services/integration/azure/openai.py` fails closed without endpoint, deployment, version or region.
3. Advisory packs match assessment once annotations are stripped.

## Done when

`python -m aegis test` is green; `tests/orchestration/test_advisory_parity.py` and Azure fail-closed tests pass.
