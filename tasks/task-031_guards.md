# TASK-031 — Output guards G-1…G-5

**Goal:** discard model text that fails deny-list, citation closure, numeric closure, additionalProperties or abstention narration. Never repair the text.

## Specs to load

FR-013 BR-102/103/104; AC-FR013-03…07.

Do not import domain logic from `packages/advice`. Do not put a failed advice object onto the pack.

## Out of scope

Azure transport (TASK-030).

## Steps

1. `packages/advice/guards.py` returns `advice: None` on failure.
2. G-1 uses the deny-list; G-5 fires only when the pack already has abstentions.

## Done when

`python -m aegis test` is green; `tests/security/test_guard_*.py` pass.
