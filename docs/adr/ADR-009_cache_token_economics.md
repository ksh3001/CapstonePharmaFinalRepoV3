# ADR-009: Cache and token economics

- Status: Accepted
- Date: 2026-08-13

## Decision

`CachePort` is stdlib: in-process memo in `assessment`, file cache in `ui`, Redis only in `cloud`. Authorisation, purpose, and residency decisions are non-cacheable. FinOps records token/step/cost even when inference is off. Wallet ceilings fail closed.

## Consequences

Redis is never required to produce a pack. Cost reports label modelled reviewer minutes until the human panel runs.
