# TASK-023 — Tool manifest signing and model qualification at execution time

**Goal:** refuse unsigned, altered, unlisted or unapproved tools at execution time, and refuse models whose documented intended use does not cover the requested purpose.

## Specs to load

`specs/features/FR-005` BR-048a / AC-FR005-14, BR-136 / AC-FR005-18.

Do not call a refused tool. Do not include derived model output after a qualification refusal. Do not read missing challenge files as live manifests.

## Out of scope

MCP runtime (ADR-010) · Azure OpenAI (TASK-030) · changing IAM (TASK-005).

## Steps

1. `packages/domain/tools.py` constructs classification types (MR-5).
2. A tool is callable only when it is listed, approved, and has a signed unaltered manifest.
3. Refusal is a finding; `human_review.tools.called` stays empty.
4. A model outside its intended use, or validated for another purpose, is refused on the same path and names the missing qualification.

## Done when

`python -m aegis test` is green; `tests/security/test_tool_manifest.py` and `tests/security/test_model_qualification.py` pass.
