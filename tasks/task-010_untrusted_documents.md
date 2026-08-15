# TASK-010 — Untrusted-document handling and instruction detection

**Goal:** retrieved document text is data. Embedded instructions are detected, reported, excluded from reasoning, and change no pack value.

## Specs to load

FR-001 BR-009 · FR-004 BR-035 · plan §5.4 · PUB-03.

## Done when

PUB-03 raises a security finding and contains none of the injection payload; `python -m aegis test` is green.
