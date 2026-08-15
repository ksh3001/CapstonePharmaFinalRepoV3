# ADR-004: Advisory non-executing contract

- Status: Accepted
- Date: 2026-08-13

## Decision

Seven public fixtures declare `response_contract: advisory_nonexecuting` and the challenge package ships no such schema. The team authors `advisory_nonexecuting.schema.json`. It may add obligations, never relax one. The `workflow` enum is derived from the **feature** set (eight values, including `regulatory` for FR-012).

## Consequences

An unknown `response_contract` is an error, never a default. Representability is asserted by `tests/contract/test_contract_representability.py`.
