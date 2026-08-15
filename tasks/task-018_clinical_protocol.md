# TASK-018 — Clinical protocol applicability

**Goal:** emit schema-valid clinical advisory packs where site approval governs version, reference ranges are contradictions not rankings, and no eligibility, allocation or adjudication conclusion is asserted.

## Specs to load

`specs/features/FR-010` (whole file) · TASK-008 ontology already Done · consent withholding already TASK-013 · protocol injection already TASK-010.

Do not decide eligibility. Do not unblind. Do not adjudicate endpoints. Do not score sites.

## Out of scope

Eligibility or screen-failure statements · selecting a reference range · adjusting device clocks · counting pending packets as adjudicated · site scores or inspection recommendations.

## Steps

1. `packages/domain/clinical.py` constructs classification types (MR-5).
2. Site `approved_protocol` governs; global current is reported and is not a fallback.
3. Pending amendment is a gap; obsolete-but-cached versions are a risk.
4. All supplied ULN values are retained as a `reference_range` contradiction with range-dependent outcomes and no selected limit.
5. Allocation, kit and arm keys are absent for every role; inferential unblinding is a finding routed to `unblinding_authority`.
6. Pending endpoint packets are excluded from adjudicated counts and raise `adjudication_backlog`.
7. Site metrics render as observations; absence is not evidence of quality.

## Done when

`python -m aegis test` is green; `python -m aegis run --workflow clinical` emits a schema-valid PUB-15 pack.
