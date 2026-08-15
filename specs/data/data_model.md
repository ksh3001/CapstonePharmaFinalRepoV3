# Data model

**Question this file answers:** what entities exist, how they are identified, and what may legally connect to what.

This is a **projection model**, not a persistence model. Nothing here is stored between runs (AP-8); every structure is rebuilt from hash-verified source on each execution.

## 1. Core value types

| Type | Shape | Rule |
|---|---|---|
| `Identifier` | `scheme`, `value`, `org_namespace` | Equality requires all three to match. Same `value` under different namespaces is a different entity (INJ-005, 008) |
| `Quantity` | `value` (string), `unit_code`, `unit_system`, `mapping_id?` | Comparable only under an approved effective mapping, else abstain. Never converted (INJ-024) |
| `TimePoint` | `value` (verbatim), `precision`, `timezone_known` (bool), `basis` (`event_time` \| `recorded_at`) | Reproduced exactly as sourced. A missing timezone stays missing (INJ-018, 025) |
| `Authority` | `document_id`, `status`, `effective_from`, `effective_to?`, `jurisdiction?` | Applicability is evaluated at `as_of`; superseded documents are retained, not deleted (INJ-013, 031) |
| `TrustStatus` | `trusted` \| `untrusted` \| `referenced_missing` \| `superseded` \| `reduced_integrity` | Drives whether content may ground an assertion (INJ-029, 032, 065) |
| `Provenance` | `source_system`, `record_id`, `authority`, `effective_time`, `retrieved_at`, `integrity{sha256, source_preserved}` | Mandatory on every node and edge. A node without it is rejected at build |
| `Pseudonym` | `purpose_scoped_hash` | Replaces direct identifiers in PV data (BR-012a). The mapping never leaves the kernel |

## 2. Entities

| Entity | Key | Notes |
|---|---|---|
| `Batch` | `Identifier` | Genealogy parent/child per `RELATIONSHIP_MODEL.csv` |
| `Material` / `Lot` | `Identifier` | Consumed by batches; carries quality holds |
| `TestResult` | source + `record_id` | Carries status history (OOS/OOT), never a single collapsed verdict |
| `Document` | `Authority` | SOPs, CoAs, protocols, labels, letters; carries `TrustStatus` |
| `Equipment` / `Logger` | `Identifier` | Calibration state and time basis matter for cold-chain disputes |
| `Case` (ICSR) | `Identifier` + `Pseudonym` for subject | Duplicate *candidates* only; no master case exists |
| `Reaction` | coded term + dictionary version | Version is part of the identity of a coding (INJ-039) |
| `Product` | `Identifier`, IDMP mappings | RIM and ERP disagreements retained as `IdentityConflict` |
| `Shipment` / `Pallet` / `Case-pack` | `Identifier` | Aggregation gaps are reported, never repaired |
| `SupplyEvent` | `event_id` | Root of workflow C |
| `Commitment` | source + `record_id` | Regulatory commitments, CMO capacity promises |
| `EvidenceItem` | `source` + `record_id` | The only thing a pack may cite |

## 3. Graph projection

Nodes are the entities above; every node and edge carries `Provenance` and `TrustStatus`.

**Permitted edge types:** `DERIVED_FROM`, `CONSUMED`, `TESTED_BY`, `DOCUMENTED_BY`, `MONITORED_BY`, `AGGREGATED_INTO`, `SHIPPED_IN`, `REPORTED_IN`, `CODED_AS`, `SUPERSEDES`, `REFERENCES`, `DUPLICATE_CANDIDATE_OF`, `POSSIBLY_RELATED_TO`.

**Forbidden edge types — the builder raises, and each has a negative test:** `RESERVED_FOR`, `ALLOCATED_TO`, `SHIPPED_AS`, `DISPOSITION_SET`, `RELEASED`, `SIGNAL_CONFIRMED`, `ELIGIBILITY_DECIDED`, `RECALL_INITIATED`.

The distinction is deliberate: permitted edges describe what the evidence says happened; forbidden edges would assert a decision the system is not allowed to make. Note that `DUPLICATE_CANDIDATE_OF` and `POSSIBLY_RELATED_TO` are explicitly *candidate* relations — there is no `SAME_AS` or `MERGED_INTO` edge in the model at all, so a merge is not representable.

**Traversal:** breadth-first, default depth 4, hard cap 6, filtered by entitlement and by effective time at `as_of`. Truncation sets `traversal_incomplete` and lists the frontier (§29.4).

## 4. Identity resolution outcomes

`SAME` · `SAME_BY_MAPPING` (cites `mapping_id`) · `RELATED` · `IdentityConflict`. There is no probabilistic identity verdict (§29.1).

## 5. What is not modelled

Disposition state · release state · allocation state · signal status · eligibility status · submission status. These belong to systems of record. The absence of a field is the control: a state that cannot be represented cannot be set (§31.1).

## 6. Ordering

Every collection derived from this model is emitted through the canonical sort rules in plan §28. The model itself imposes no ordering, so ordering is never accidental.
