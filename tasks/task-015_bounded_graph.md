# TASK-015 — Bounded graph projection with provenance and forbidden-edge guard

**Goal:** in-process read-only graph; provenance mandatory; forbidden edges unrepresentable; BFS default 4 / cap 6.

## Specs to load

plan §5.3, §5.4, §29.4 · `specs/data/data_model.md` §3 · ADR-007.

## Done when

`python -m aegis test` is green; hop-limit incompleteness is honest; each forbidden edge type raises.
