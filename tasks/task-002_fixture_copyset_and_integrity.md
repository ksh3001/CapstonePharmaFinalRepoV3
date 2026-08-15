# TASK-002 — Fixture copy set, hash verification and provenance

**Goal:** bring the challenge fixtures and reference data into the new repo in a way that proves nothing was altered, and make the copy set derived rather than remembered.

## Specs to load

`00_plan/MASTER_BUILD_PLAN.md` §3.1, §3.2 · AMB-02, AMB-09 in §27 · `01_specs/api/api_contracts.md` §3 (hash meaning).

## Out of scope

Parsing fixture content into domain objects. Building evidence items — that is TASK-007.

## Steps

1. Write `scripts/build_fixture_copyset.py`: read every `evaluation/public_fixtures/PUB-*.json`, collect `evidence_references[]` and `evidence[].source`, union with the fixed governance set listed in plan §3.2, and emit a copy manifest sorted deterministically.
2. Copy each listed file into `tests/fixtures/synthetic/`, preserving relative structure.
3. Verify every copied file's SHA-256 against `FILE_HASHES.csv`. A mismatch aborts the copy with the path and both hashes.
4. Emit `tests/fixtures/synthetic/PROVENANCE.csv` with `source_path, sha256, copied_at, authority, synthetic`. `copied_at` is the run's `as_of`, not the clock.
5. Add a CI check that re-derives the manifest and fails on any diff against the committed one.
6. Add the integrity-failure path: a corrupted artefact must cause abstention downstream, never silent use.

## Acceptance checks

- The derived manifest includes every file referenced by any fixture; deliberately deleting one entry from the committed manifest fails CI.
- Every copied file's hash matches `FILE_HASHES.csv`.
- Mutating one byte of a copied fixture fails verification on the next run and names the file.
- `PROVENANCE.csv` is byte-identical across repeated runs.
- No file outside the copy set is written into the new repo, and no file in the challenge package is modified.

## Test expectations

`tests/unit/test_copyset.py` — derivation completeness and stability.
`tests/security/test_integrity_failure.py` — corrupted artefact leads to abstention and exclusion of its facts (AC-FR001-11).

## Done when

The copy set is reproducible from the fixtures alone, provenance is recorded, tampering is detectable, and the challenge package hashes are unchanged — verified with `tools/verify_package.py`.
