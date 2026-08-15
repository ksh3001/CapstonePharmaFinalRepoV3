# ADR-001: Separate product repository

- Status: Accepted
- Date: 2026-08-13

## Decision

The product lives in `aegis-sdd`, outside the challenge package. Challenge evidence is read-only and hash-verified. Product code is not grown under challenge `submission/src`.

## Consequences

A later FDE bridge (`scripts/export_to_submission.py`) snapshots evidence into the challenge package at defence tags. Until then the two trees stay separate.
