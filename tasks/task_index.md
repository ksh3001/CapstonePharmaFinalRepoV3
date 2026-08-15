# Task index

Each task is one sitting's work with an explicit spec list. Load only the listed specs — that is the point of having them.

A task is `blocked` if an ambiguity affecting it is open. Blocked tasks are not started.

## Phase 0 — Scaffold and governance

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-001** | Repo scaffold, structure manifest, stdlib import gate, interpreter guard, **inject-coverage gate**, **module boundary gate**, traceability validator | plan §2, §4, §4a; `01_specs/README.md`; `01_specs/api/api_contracts.md` §6; `01_specs/registers/traceability_gap_audit.md` §3 | — | Done |
| **TASK-002** | Fixture copy-set generator, hash verification, provenance record | plan §3.2; AMB-09 | TASK-001 | Done |
| **TASK-003** | Canonical serialisation and derived identifiers | plan §28; AMB-03, AMB-04 | TASK-001 | Done |
| **TASK-004** | Contract package: four challenge schemas, advisory contract, validator, deny-list | `01_specs/api/api_contracts.md`; AMB-01 | TASK-001, TASK-003 | Done |
| **TASK-005** | Kernel: request lifecycle, execution-time authorisation, audit trail | plan §7, §11; AP-2 | TASK-003, TASK-004 | Done |
| **TASK-006** | Six CLI commands, runtime modes, `ai_disabled` path | plan §8, §4 | TASK-005 | Done |
| **TASK-007** | Evidence item builder with provenance and source-hash integrity | `01_specs/api/api_contracts.md` §3; AMB-02 | TASK-004 | Done |

**Phase 0 exit:** clean clone runs `python -m aegis test` offline with zero installs; contract, deny-list, determinism and copy-set tests green.

## Phase 1 — Ontology, graph, Workflow A

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-008** | Ontology: units, terminology versions, identity tiers, temporal model, trust status | `01_specs/features/FR-001` §5; plan §5.2, §29.1, §29.5 | TASK-007; **FR-001 stage 2 approved** | Done |
| **TASK-009** | Batch engine: contradictions, gaps, abstentions, `readiness_state` | `01_specs/features/FR-001` | TASK-008 | Done |
| **TASK-010** | Untrusted-document handling and instruction detection | FR-001 BR-009; plan §5.4 | TASK-008 | Done |
| **TASK-015** | Bounded graph projection with provenance and forbidden-edge guard | plan §5.3, §5.4, §29.4 | TASK-008 | Done |

## Phase 2–3 — Gates and Workflows B, C

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-011** | Duplicate candidate engine with fixed strategy and scores | `01_specs/registers/matching_confidence_checklist.md` §2; FR-002 BR-014 | TASK-008 | Done |
| **TASK-012** | PV engine: source facts, clocks, terminology, listedness | `01_specs/features/FR-002` | TASK-011 | Done |
| **TASK-013** | Privacy and purpose gates: consent, residency, DSR versus hold, sensitive segments, per-purpose pseudonymisation | FR-002 BR-012/012a/017; `01_specs/data/data_model.md` §1; plan §23 | TASK-005 | Done |
| **TASK-014** | Supply engine: options, constraints, holds, approvals | `01_specs/features/FR-003` | TASK-015 | Done |
| **TASK-016** | Checkpoint freshness and idempotent replay | FR-003 BR-030; plan §20.4 | TASK-006 | Done |

| **TASK-017** | Interface contract reconciliation: version resolution, UCUM validation, approved-mapping register | `01_specs/features/FR-011` | TASK-008 | Done |
| **TASK-018** | Clinical protocol applicability: site approval precedence, reference-range contradictions | `01_specs/features/FR-010` | TASK-008 | Done |
| **TASK-019** | Regulatory records: identity conflict, labelling divergence, commitments, sequence gaps | `01_specs/features/FR-012` | TASK-008 | Done |

## Phase 4 — Orchestration and continuity

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-020** | `OrchestratorPort`, declared step graph, stdlib runner, budgets | `01_specs/features/FR-006`; `01_specs/data/state_transitions.md` §3; plan §20 | TASK-016 | Done |
| **TASK-021** | LangGraph adapter with byte-parity proof against the stdlib runner | FR-006 BR-056; plan §20.2 | TASK-020 | Done |
| **TASK-022** | Continuity: outage tolerance reading, substitution refusal, kill switch, manual runbooks | `01_specs/features/FR-009` | TASK-006 | Done |
| **TASK-023** | Tool manifest signing and verification at execution time | FR-005 BR-048a | TASK-005 | Done |

## Phase 5–6 — Console, FinOps, evals and compliance

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-024** | Advisory API surface for the console; no rule below the API | `01_specs/api/api_contracts.md`; FR-008 BR-064 | TASK-020 | Done |
| **TASK-025** | Server-rendered console (Jinja + HTMX; FastAPI optional): four core screens, forced evidence view enforced server-side, segregation of duties, **live `python -m aegis serve`** | `01_specs/features/FR-008`; `01_specs/api/api_contracts.md` §7; plan §6, ADR-011; `01_specs/nfrs.md` NFR-14, NFR-15 | TASK-024 | Done |
| **TASK-026** | FinOps: token accounting, wallet ceilings, cost per successful task using `outcome` dispositions, **reviewer minutes costed at `staff_rates.csv` and labelled `modelled` until the panel runs** | `01_specs/features/FR-007`; `03_lean_dmaic/dmaic_plan.md` I-1 | TASK-020, TASK-033 | Done |
| **TASK-027** | Eval harness L0–L6: datasets, property and trajectory graders, thresholds **including subgroup-spread (NFR-27)** | plan §25.1–25.7, §9.5; `evals/thresholds.yaml`; `01_specs/nfrs.md` NFR-27; `03_lean_dmaic/dmaic_plan.md` I-4 | TASK-009, TASK-012, TASK-014 | Done |
| **TASK-028** | Compliance tripwires: EU AI Act and ISO 42001 control map as executable checks | plan §22, §23 | TASK-027 | Done |
| **TASK-029** | Inject fan-out: remaining coverage rows, evidence export, submission bridge | plan §3.3, §15 | TASK-027 | Done |

## Azure OpenAI advisory layer and evidence store

| Task | Goal | Specs to load | Depends on | Status |
|---|---|---|---|---|
| **TASK-030** | `AzureOpenAIAdapter` behind `InferencePort`: managed identity, pinned deployment and version, residency pre-check, filter capture | `01_specs/features/FR-013`; plan §34.4 | TASK-020, TASK-033 | Done |
| **TASK-031** | Output guard G-1…G-5 with rejection recording | FR-013 BR-102/103/104; plan §34.3 | TASK-004 | Done |
| **TASK-032** | Cassette record-and-replay and the **L6a advice eval suite**: isolation, groundedness, citation closure, guard rates | FR-013 BR-110; plan §25.8; `01_specs/nfrs.md` NFR-21, NFR-22, NFR-24 | TASK-030, TASK-027 | Done |
| **TASK-033** | Evidence store: append-only chain writer, verifier, retrieval command, **one `outcome` record per request (BR-142)** | `01_specs/features/FR-014`; plan §35; `03_lean_dmaic/dmaic_plan.md` I-2 | TASK-005 | Done |
| **TASK-034** | Retention and hold engine: 90-day prompt-log expiry, live hold check, expiry as an event | FR-014 BR-119/121/122 | TASK-033, TASK-013 | Done |
| **TASK-035** | Azure Blob WORM adapter for `cloud` mode | FR-014 BR-117; plan §35.4 | TASK-033 | Done |

TASK-033 is a dependency of TASK-030 rather than the reverse: the store must exist before anything is allowed to call a model, because a call with nowhere to record it is a call this system does not make (BR-116).

All fourteen features are authored, so every task above has a spec behind it. Tasks remain gated on stage-2 approval of the feature they implement.

**Lean freeze (MF-1).** Do not author further feature specs, business rules or acceptance criteria until FR-001 has a named stage-2 reviewer and TASK-008/009 have produced one schema-valid PUB-01 pack. Phase 0 (TASK-001…007) is infrastructure and is not frozen. The freeze exists because 204 criteria at `Not started` is inventory, not progress (`03_lean_dmaic/build_constraints_from_lean.md`).

## Working agreement

One task per sitting. Write the failing test first, from the acceptance criteria — not from the implementation you intend to write. Update `01_specs/testing/ac_test_plan.md` and the inject coverage row before closing the task. The AI-change record is generated by the session hooks; review it rather than write it.

Adding or amending a business rule is the moment inject coverage changes. From TASK-001 the **inject-coverage gate** enforces it: removing the sole rule carrying an inject fails the build and names that inject, so coverage cannot quietly regress between this agreement and someone remembering to honour it.
