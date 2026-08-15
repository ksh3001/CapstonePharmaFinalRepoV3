# TASK-011 — Duplicate candidate engine with fixed strategy and scores

**Goal:** pairwise ICSR duplicate candidates. No merge, no fuzzy identity.

## Specs to load

`specs/registers/matching_confidence_checklist.md` §2 · FR-002 BR-014 · plan §29.2.

## Done when

Score ≤2 is absent; score 3 is `duplicate_candidate_weak`; `python -m aegis test` is green.
