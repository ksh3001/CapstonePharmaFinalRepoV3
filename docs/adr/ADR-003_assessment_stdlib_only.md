# ADR-003: Assessment mode is stdlib-only

- Status: Accepted
- Date: 2026-08-13

## Decision

The graded default is `assessment`: CPython standard library, zero installs, no network, inference off. Every regulated pack must be producible with `python -m aegis` on a clean machine.

## Consequences

Third-party libraries are confined to `services/integration/` and optional requirement files. The stdlib import gate walks `packages/` and fails on any other import.
