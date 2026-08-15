# TASK-035 — Azure Blob WORM adapter

**Goal:** cloud-mode immutability envelope. Overwrite of a stored object is rejected. Assessment uses a local WORM directory under `out/worm/`.

## Specs to load

FR-014 BR-117; plan §35.4; AC-FR014-15.

Do not call live Azure Blob from assessment.

## Out of scope

Provisioning a real immutable policy in a subscription.

## Steps

1. `services/integration/azure/blob.py` writes once and raises `ImmutableBlobError` on overwrite.
2. A sidecar `.policy` file records time-based immutability.

## Done when

`python -m aegis test` is green; `tests/security/test_blob_immutability.py` passes.
