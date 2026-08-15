# Matching and confidence checklist

Required because several features are confidence-gated. For each one: strategy priority order, numeric threshold or declared Unknown, rejection behaviour below threshold, and dedup or quantity rules. No feature may say "validate confidence" without one of these.

## 1. Identity resolution (FR-001, FR-002, FR-003 — INJ-005, 008, 045)

**Priority order:** exact identifier within namespace → approved effective mapping → declared relationship edge → *stop*. String similarity is not used for identity.

**Threshold:** none — the tiers are categorical, which is the point. There is no score at which two identifiers become the same thing.

**Below threshold:** emit `IdentityConflict` and an abstention. Never merge, never prefer the more recent, never prefer the more complete record.

**Dedup rule:** identical local codes under different organisation prefixes are distinct entities by construction.

## 2. ICSR duplicate candidates (FR-002 — INJ-037)

**Priority order:** exact worldwide-unique-id → six-field composite → stop.

**Composite fields:** patient identifier or initials · date of birth, or age bucket where absent · sex · suspect product · reaction preferred term · onset date within ±7 days.

**Thresholds:** score is a count of matched fields out of six. 6 or exact id → `duplicate_candidate_high`; 4–5 → `duplicate_candidate`; 3 → `duplicate_candidate_weak` with matched fields listed; ≤2 → not surfaced.

**Below threshold:** the pair is absent from the pack. It is not recorded as "not a duplicate" — absence of a candidate is not a negative finding.

**Dedup rule:** candidates are pairwise and never transitively closed into clusters that imply a master case. No merge exists at any score.

**Status:** window and cut points are **declared Unknown AMB-05a**, owned by the safety physician role, shipped as surfaced configuration.

## 3. Cross-domain linkage — complaint ↔ batch ↔ ICSR (FR-002 — INJ-043)

**Priority order:** shared batch or lot identifier → approved mapping → stop.

**Threshold:** events within ±30 days.

**Below threshold:** abstention with reason `unconfirmed_link`, reusing the vocabulary the existing scorecard already applies to PUB-11.

**Quantity rule:** the number of candidate links is reported; a link set larger than the display limit reports the count rather than truncating silently.

**Status:** declared Unknown AMB-05b.

## 4. Recall scope traversal (FR-003 — INJ-058)

**Priority order:** direct genealogy edges → aggregation edges → shipment edges, breadth-first.

**Threshold:** depth 4 by default, hard cap 6.

**Below or beyond threshold:** `traversal_incomplete: true`, the unexplored frontier listed by node id, and an abstention. Completeness of scope is never asserted.

**Quantity rule:** frontier node ids are reported in full, never sampled.

## 5. Counterfeit suspicion (FR-003 — INJ-053)

**Priority order:** enumerate indicators; no scoring model.

**Threshold:** none by design. One credible indicator is enough to escalate.

**Below threshold:** not applicable — indicators are reported, and the absence of indicators is not a clearance.

## 6. Where a threshold is deliberately refused

Unit comparison (INJ-024), terminology equivalence across dictionary versions (INJ-039) and expectedness (INJ-040) have no tolerance and never will. Either an approved mapping applies, or the system abstains. A tolerance here would be a silent conversion, which AP-3 prohibits.

## Audit

| Confidence-gated feature | Order fixed | Number or Unknown | Rejection behaviour | Dedup / quantity |
|---|---|---|---|---|
| Identity resolution | Yes | Categorical by design | Yes | Yes |
| ICSR duplicates | Yes | Yes, AMB-05a | Yes | Yes |
| Cross-domain linkage | Yes | Yes, AMB-05b | Yes | Yes |
| Recall traversal | Yes | Yes | Yes | Yes |
| Counterfeit suspicion | Yes | Refused by design | Yes | n/a |
| Unit / terminology / expectedness | Yes | Refused by design | Yes | n/a |

No unmarked entries.
