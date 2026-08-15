# ADR-006: Canonical serialisation

- Status: Accepted
- Date: 2026-08-13

## Decision

Packs are emitted with `json.dumps(..., sort_keys=True, ensure_ascii=False, separators=(",", ":"))`, UTF-8, LF, one trailing newline. Identifiers and timestamps are derived from `as_of` and content. Binary floats are rejected at serialisation. Source timestamps are reproduced verbatim.

## Consequences

Three consecutive runs are byte-identical with no excluded fields. Hostile `TZ` / `LANG` / `PYTHONHASHSEED` must not change bytes.
