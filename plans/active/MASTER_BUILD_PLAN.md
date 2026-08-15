# AEGIS Agentic App — Master Build Plan (v3.7)

| Field | Entry |
|---|---|
| Version | **3.9 — Lean DMAIC applied.** v3.8 plus the Measure-first improvement spine in `03_lean_dmaic/`: no further feature specification until FR-001 clears stage 2; reviewer cost and failure taxonomy instrumented before any efficiency claim; subgroup spread gated (NFR-27). Fourteen features, **146 business rules, 204 acceptance criteria**, 27 NFRs, 35 tasks |
| Roles and agents | **7** runtime roles · **6** accountability roles · **6** runtime agents · **3** build-time agents — four disjoint populations (§26.1, §32) |
| Status | Spec set complete. **Not yet approved** — stage 2 requires a named human reviewer per feature (`01_specs/README.md`) |
| Date | 2026-08-12 |
| Model | **Azure OpenAI**, narrative advice only, behind `InferencePort`, the output guard and the kill switch (§34) |
| Evidence | **Append-only hash-chained store**; Azure Blob with immutability policy in `cloud` (§35) |
| Console | **HTMX + Jinja, served by FastAPI.** No Node, no JS build, no client-side state. The review gates are enforced by what the server renders (§6, ADR-011) |
| Supersedes | v3.6 (Next.js console requiring a Node runtime), v3.5, v3.4, v3.3, v3.2, v3.1, v3, v2, v1 |
| Role of this document | **Index and rationale.** From v3.3 the authoritative build inputs are the specs in `01_specs/` and the tasks in `02_tasks/` (§30) |
| Agents | **6 runtime agent roles** (§32). Gates are never agents |
| Knowledge graph store | **In-process property graph rebuilt from source each run.** Cosmos DB for Gremlin is an optional `cloud`-mode adapter only (§33) |
| Product home | **New repo outside the challenge package** (`aegis-sdd`) |
| Challenge package | `fde-training-team3-pharma-project` — evidence immutable |
| Default runtime | `assessment` — offline, deterministic, **zero-install stdlib core** |
| Agentic framework | **LangGraph** in `ui` / `cloud`; stdlib deterministic runner in `assessment` — both behind `OrchestratorPort`, byte-parity enforced (§20) |
| Canonical location after scaffold | `{NEW_REPO}/plans/active/MASTER_BUILD_PLAN.md` |

---

## 0. Validation report

### 0.1 Verified facts (re-checked against the repo, not assumed)

| Fact | Verified value | Source |
|---|---|---|
| Inject count | **84** (INJ-001…084, dimensions D01–D13) | `data/injects.json` |
| Coverage rows | 84 + header, all `NOT_RUN` | `data/INJECT_TEST_COVERAGE.csv` |
| Coverage columns | `test_id, inject_id, dimension, title, required_test_class, minimum_evidence, release_gate, participant_result` | same |
| Public fixtures | **15** (PUB-01…15), `expected_answer_included: false` | `evaluation/public_fixtures/` |
| Response contracts | **4** — batch, pv, supply, evidence_item | `evaluation/contracts/` |
| Data files | 143 CSVs | `data/` |
| AI boundaries | batch: reconcile/cite/flag/abstain · PV: extract/normalize/cluster/cite · supply: generate options | `data/ai_use_boundaries.csv` |
| Edge rules | explicit parent/child relationships (genealogy, duplicates, loggers, MA…) | `data/RELATIONSHIP_MODEL.csv` |
| Integrity baseline | `FILE_HASHES.csv` + `tools/verify_package.py`, `tools/hash_submission.py`, `tools/check_submission_structure.py` | package root / `tools/` |

### 0.2 Blindspot register

**From the v2 → v3 review:**

| ID | Blindspot | Severity | Fix |
|---|---|---|---|
| BS-01 | UI was Taipy, a framework that owns the rendering model and invites business logic into the view | High | §6 — replaced by a pure-consumer console |
| BS-02 | KG/ontology absent, and artefact 08 **D-205 explicitly rejects a KG** | Critical | §5.1 superseding ADR + T1–T5 parity |
| BS-03 | Ontology was docs-only (artefact 07 R-703: no OWL authored) | High | §5.2 |
| BS-04 | No rule that the graph must not be a system of record; no forbidden-edge list | Critical | §5.4 |
| BS-05 | A JS-framework console needs a Node runtime, a second lockfile and a second SBOM; DoD demands a no-install deterministic mode | Critical | §4, §8 — **dissolved in v3.7**: the console is server-rendered, so Node leaves the stack entirely (ADR-011) |
| BS-06 | Response schemas are `additionalProperties: false` — no slot for graph paths/traces | Critical | §5.5 |
| BS-07 | `evidence_item.integrity.sha256` must match `^[a-f0-9]{64}$`, `source_preserved: true` | High | §7 |
| BS-08 | Fixtures carry no expected answers — golden-diff testing impossible | High | §9.2 |
| BS-09 | Only ~14 capability rows, not all 84 injects | High | §15 |
| BS-10 | Tests not keyed to `required_test_class` / `release_gate` | Medium | §9.3 |
| BS-11 | Repo split risked failing `check_submission_structure.py --final` | Critical | §3.3 |
| BS-12 | Multilingual + a11y not enforceable | High | §6.3 |
| BS-13 | `authorized_context.execution: "disabled"` not honoured explicitly | Medium | §7 |
| BS-14 | Graph traversal adds new attack surface | High | §5.4 |
| BS-15 | FinOps undefined when inference is off | Medium | §9.6 |

**Added in the v3 → v3.1 DoD compliance pass:**

| ID | Blindspot | DoD clause | Fix |
|---|---|---|---|
| **BS-16** | Plan contradicted itself: `assessment` = "Python only" while proposing `networkx` + FastAPI | §3 *"Dependencies are locked or the deterministic standard-library mode needs no installation"* | §4 dependency policy; §5.3 **stdlib graph core** |
| **BS-17** | Adopting a KG makes challenge artefacts 07/08/10/11 stale and self-contradictory | §6 *"All 30 required artefacts are completed or mapped"* | §3.3 bridge now updates artefacts + manifest |
| **BS-18** | Brownfield coexistence, migration, rollback, decommissioning, data reconciliation absent | §3 | §12 |
| **BS-19** | Records/signatures boundary (Part 11 / Annex 11) absent | §4 | §11 |
| **BS-20** | SLI/SLO, capacity, observability, incident response, backup/restore, retirement absent | §5 | §13 |
| **BS-21** | No measurable release thresholds | §5 *"Release thresholds are measurable; failed gates block release"* | §9.5 |
| **BS-22** | No test recipe for non-behavioural injects (D01, D12, D13-083/084) | §5, §6 | §9.1 test taxonomy incl. `T-ARTEFACT` |
| **BS-23** | No requirement IDs / traceability matrix; no risk register or stop-pivot thresholds; UI sequenced ahead of hard security gates; copied fixtures unverified | §1, §3 | §10, §14, §16, §3.2 |

**Added in the v3.1 → v3.2 capability pass (LangGraph · MCP · hooks · compliance · performance · evals):**

| ID | Blindspot | Why it matters | Fix |
|---|---|---|---|
| **BS-24** | LangGraph, Redis and MCP clients are third-party and (Redis/MCP) networked — dropping them into the core breaks *"the deterministic standard-library mode needs no installation"* and the offline assessment path | Naive adoption forfeits the DoD zero-install clause and the AI-disabled continuity claim | §20.1 `OrchestratorPort` + §4 mode gating |
| **BS-25** | A LangGraph checkpointer **persists graph state**, which for workflow B contains PV personal data — that silently creates a new data store subject to residency, retention, DSR and corruption controls (INJ-060/061/064/080) | An "orchestration detail" becomes a privacy and data-integrity surface with no owner | §20.4 checkpoint data policy |
| **BS-26** | MCP tool names, descriptions and results are attacker-controllable text — this *is* INJ-065 (prompt injection) and INJ-066 (tool-manifest poisoning), not an analogue of them | Adding MCP without the trust gate hands the injects a live exploit path | §21.3 |
| **BS-27** | Cursor hooks run in the **developer's IDE**, not in the product. Citing a hook as a runtime control would put a false claim into the assurance case | Corrupts artefact 21 and the EU AI Act oversight argument | §22.1 boundary statement |
| **BS-28** | Artefact 23 §4 already warns that entitlement/consent caches caused safety and privacy failures; a Redis layer that caches authorisation re-creates INJ-067 exactly | Performance work reintroduces a solved hard-gate failure | §24.2 non-cacheable set |
| **BS-29** | Artefact 22 records **PUB-14 `not_implemented`** and R-2301 "no executable cost-per-successful-task calculator" — a token-economics claim without that calculator repeats the existing gap | A stated deliverable stays unmet and PUB-14 cannot move to pass | §24.4 |
| **BS-30** | Artefact 22 gaps R-2201 (no adversarial corpus) and R-2202 (human-review rubric never scored) remain open; an LLM judge could quietly become a release gate | Evals would grade the easy cases and let a non-deterministic judge block or pass regulated output | §25.3, §25.5 |
| **BS-31** | Artefact 19 §7 lists change triggers that invalidate the non-high-risk EU AI Act posture (write tool added, forced review removed, model swapped without change control) — **nothing enforces them** | The compliance claim decays silently the first time someone adds a tool | §23.3 tripwires |

**Added in the v3.2 → v3.3 spec-readiness pass:**

| ID | Blindspot | Why it blocked spec-driven work | Fix |
|---|---|---|---|
| **BS-32** | The plan is a single 1 098-line document — the exact failure mode `spec-driven-delivery` names first: *"one enormous document that answers everything badly."* An agent implementing one workflow loads all of it | No specs-to-load, so every task inherits the whole context and drifts | §30 specification layer |
| **BS-33** | **7 of the 15 fixtures declare `"response_contract": "advisory_nonexecuting"`, and no such schema exists in the package** (only batch, pv, supply, evidence_item). "100% of packs schema-valid" was undefined for PUB-09/10/11/12/13/14/15 | Four of those fixtures are exactly the ones the current submission reports as `not_implemented` | AMB-01 |
| **BS-34** | Determinism was a threshold with no engineering rules; `evidence_item.retrieved_at` is required, and a wall-clock value makes byte-identical runs impossible | The headline reproducibility claim was unreachable by construction | §28 |
| **BS-35** | Confidence-gated matching (duplicates, identity, linkage, recall scope) had policy — "candidate, no auto-merge" — but no strategy order, no numbers and no rejection rule | `spec-driven-delivery` forbids leaving "validate confidence" without a number or an explicit Unknown | §29 |
| **BS-36** | No acceptance criteria, business rules or ambiguity registers; §15 held one-line test hints, not verifiable ACs | Nothing to write tests against, so "tests first" had no source | §30.2, registers |
| **BS-37** | No review gates (architecture review, structural reopen) and no PoC-vs-production labelling | Contracts could lock before review; POC scaffolding could be mistaken for product | §30.3 |
| **BS-38** | Nine phases with no timebox, owner or cut line; no definition of the minimum defensible submission | Under time pressure the team would cut arbitrarily, likely losing scoreable work | §30.4 |

**Added in the v3.3 → v3.4 lifecycle and platform pass:**

| ID | Blindspot | Why it matters | Fix |
|---|---|---|---|
| **BS-39** | The spec set existed but the **lifecycle around it did not** — no named stages, stage outputs or exit gates, so "spec-driven" was a structure rather than a process | A spec that is written once and never validated, or a build that drifts from it, is the failure the method exists to prevent | §30.5 |
| **BS-40** | The plan described the application but not the **platform layers it runs inside** — access and model routing, connector governance, evidence gating, release control and observability were scattered or absent | Enterprise AI controls sit at layer boundaries; without the mapping, controls are claimed but unassigned | §31 |
| **BS-41** | **How many agents, and what may each one do?** was never answered. Capability boundary, model-risk class and HITL policy per agent were undefined | An unbounded agent population is the single most common way a governed system loses its boundary | §32 |
| **BS-43** | The product had **no model layer at all**. Every mode was deterministic, so the system could reconcile evidence but never explain it to the person who has to act on it. "Advisory" described the authority level, not the experience | A reviewer facing a pack of contradictions and abstentions with no narrative gets analysis, not help. The gap between correct and useful was unaddressed | §34 |
| **BS-44** | Evidence was written to `evidence/` as **files with no integrity chain, no retention rule and no retrieval command**. The plan claimed auditability while offering a directory | The first inspection question — "show me everything behind this pack, and prove it has not changed" — had no answer. Worse, the system enforced retention rules on others while ignoring its own | §35 |
| **BS-42** | Graph **storage** was decided for the assessed path but the cloud option was left as "Neo4j / Cosmos Gremlin, cloud mode only" with no rationale, constraints or rejection criteria | The first person to ask "should we use Cosmos?" would re-litigate it without the constraints that make the answer obvious | §33 |
| **BS-46** | Modularity was **designed but not enforced**. Of six module rules only MR-4 had a gate; MR-5 and MR-6 had none, and nothing checked layering or cycles *inside* `packages/`, so `ontology` could import `domain` and pass. The stdlib gate was also worded to reject legitimate intra-core imports, so it would have been loosened the first time it fired | MR-5 keeps classification out of orchestrator nodes, which is the basis of the determinism claim. Risk R-10 predicts exactly that erosion and offered "design review rejects it" as the mitigation | §4a; TASK-001 steps 5 and 9; `api_contracts.md` §6 |
| **BS-45** | The **runtime role model was undeclared**. Five business roles were listed in scope; the feature specs used seven, and BR-046 gated sensitive segments by role while the package supplies no role → access-group edge at all | An entitlement gate with no entitlement table is not a control. Governance had accountability roles and an agent roster, but nothing said who the product serves or what each may see | §26.1; `01_specs/registers/roles_and_entitlements.md`; AMB-15 |

### 0.3 Verdict

v3 was architecturally sound; v3.1 closed the operational and compliance surface an examiner checks mechanically; v3.2 added the agentic framework, the tool protocol, the performance layer and the evaluation subsystem **without** giving up zero-install, offline determinism — every new dependency sits behind a port and a runtime mode, and every compliance claim is wired to a test that fails when the claim stops being true.

v3.3 makes it **spec-ready**: the ten open ambiguities are closed with decisions and rationale (§27), determinism has engineering rules rather than an aspiration (§28), every confidence-gated behaviour has a number or a declared Unknown with an owner (§29), and the plan steps back into being an index while the authoritative build inputs move to `01_specs/` and `02_tasks/` (§30).

v3.4 closes the loop around that spec set: the six-stage spec-first lifecycle with named outputs and exit gates (§30.5), the nine platform layers with a control owner each (§31), a fixed roster of six agents with explicit capability boundaries and a standing rule that **gates are never agents** (§32), and a graph-storage decision with the constraints that produced it (§33). **Spec-driven implementation can start from TASK-001.**

---

## 1. Decision summary

1. Build in a **separate repo** (`aegis-sdd`) scaffolded to the AI-Assisted SDLC structure (§2).
2. **Deterministic engines are the source of truth.** The agent orchestrates; it never decides.
3. Adopt **Knowledge Graph + Ontology** as the evidence-assembly layer — offline, in-process, provenance-first — via a formal supersession of D-205 (§5.1).
4. **Stdlib-only core.** The assessed path installs nothing; FastAPI and the console belong to optional modes (§4).
5. **The human-review console is server-rendered HTMX on FastAPI**, so the review gates are properties of what the server emits rather than promises the client keeps. The **CLI/JSON path remains authoritative** (§6, ADR-011).
6. **Security hard gates land before the UI** (§16).
7. Cover **all 84 injects** with a 1:1 `TC-INJ-###` map and a test taxonomy that fits each inject type (§9.1, §15).
8. Never implement prohibited regulated actions; deny by default.
9. **LangGraph is the agentic framework** for `ui`/`cloud`; `assessment` uses a stdlib deterministic runner. Both implement `OrchestratorPort` and must emit byte-identical packs (§20).
10. **MCP** is used two ways, kept strictly apart: as a build-time accelerator in Cursor, and as an optional read-only runtime tool transport behind the trust gate. It is **off in `assessment`** (§21).
11. **Cursor hooks** enforce build discipline and auto-generate AI-assisted change records. They are development controls and are never claimed as product controls (§22).
12. **EU AI Act and ISO 42001 obligations become executable controls** — a control map plus tripwires that fail CI when a compliance precondition is broken (§23).
13. **Caching and budgets are correctness features first.** Authorisation, consent and entitlement are never cached; cache-on and cache-off results must be identical (§24).
14. **Evaluation is a first-class subsystem** with deterministic release gates; LLM-as-judge is advisory-only and can never gate a release (§25).
15. Every capability moves through the **six-stage spec-first lifecycle** — define, validate, design, implement, test, evolve — with named outputs and exit gates (§30.5).
16. **Six runtime agent roles**, fixed and boundary-enforced. Gates are never agents (§32).
17. The knowledge graph is a **per-run projection with no database**; a managed graph store is an optional cloud demo, never a dependency (§33).
18. **Azure OpenAI writes prose, never a regulated field.** The deployed default is `advisory` mode; removing the model changes no computed value, and that is proven per fixture rather than asserted (§34).
19. **Evidence is append-only and hash-chained**, and a request that cannot record evidence does not run. Our own prompt logs obey the same 90-day retention rule the system enforces on others (§35).

---

## 2. Target repository structure

```
aegis-sdd/
├── .cursor/{rules,agents,skills,commands,hooks}/ + mcp.json, hooks.json, .cursorignore, .cursorindexingignore
├── docs/{product,architecture,adr,engineering,quality,security,operations,governance}/
├── specs/{product,features,api,data,testing,registers}/   ← authoritative build inputs (§30)
├── tasks/                                                 ← TASK-0NN with specs-to-load
├── plans/{active,completed,superseded}/
├── apps/
│   ├── web/                 ← HITL console: Jinja templates + HTMX + Tailwind, served by services/api
│   │   ├── templates/       ← server-rendered pages and fragments; the gate lives here (§6.3)
│   │   └── static/          ← htmx.min.js (vendored, hash-pinned), compiled CSS, no build step at runtime
│   └── admin/               ← not built until needed
├── services/
│   ├── api/                 ← FastAPI (Python 3.11–3.13) — advisory/ui/cloud modes; absent in assessment
│   │                          serves both the JSON API and the console's HTML fragments
│   ├── worker/              ← deferred
│   └── integration/         ← **all third-party adapters live here**
│       ├── langgraph/       ← LangGraphOrchestrator (implements OrchestratorPort)
│       ├── mcp/             ← MCP client + optional read-only MCP server
│       ├── redis/           ← RedisCache (implements CachePort)
│       ├── inference/       ← AzureOpenAIAdapter behind InferencePort + kill switch + cassettes (§34)
│       ├── evidence_store/  ← chain writer; Azure Blob WORM adapter for cloud (§35)
│       └── sources/         ← GraphPort adapters / source-system readers
├── packages/
│   ├── kernel/              ← request lifecycle, authZ, budgets, checkpoints, kill switch  (stdlib)
│   ├── domain/              ← engines A/B/C, evidence, contradict, resolve  (stdlib, SoT)
│   ├── ontology/            ← vocabularies, units, identity, temporal/jurisdiction  (stdlib)
│   ├── graph/               ← KG builder + bounded traversal + provenance  (stdlib)
│   ├── orchestrator/        ← OrchestratorPort + deterministic stdlib runner  (stdlib)
│   ├── cache/               ← CachePort + memo/file cache, non-cacheable registry  (stdlib)
│   ├── finops/              ← token/step budgets, wallet, cost-per-successful-task  (stdlib)
│   ├── advice/              ← prompt templates (versioned), output guard G-1…G-5  (stdlib)
│   ├── evidence_store/      ← append-only hash-chained record writer + verifier  (stdlib)
│   ├── contracts/           ← regulated schemas + internal trace schemas
│   ├── config/              ← runtime modes, budgets, thresholds, agents.yaml (capability boundaries)
│   ├── observability/       ← audit trail, structured logs
│   └── test-support/        ← fixture loaders, property graders
├── evals/
│   ├── datasets/{scenario,adversarial,subgroup,regression,advice}/
│   ├── cassettes/           ← recorded model interactions; evals replay, never call live (§34.5)
│   ├── graders/{deterministic,property,trajectory,judge}/
│   ├── human-panel/         ← rubric, scoring sheets, results
│   ├── thresholds.yaml      ← release gates; judge scores explicitly non-gating
│   └── run_evals.py
├── compliance/
│   ├── eu-ai-act/           ← obligation register, transparency notices, oversight design
│   ├── iso42001/            ← AIMS clause + Annex A control mapping
│   ├── control-map.csv      ← obligation → control → test_id → evidence_path
│   └── tripwires/           ← executable checks for artefact-19 §7 change triggers
├── tests/{unit,integration,contract,e2e,performance,security,resilience,regression,subgroup,orchestration,compliance}/ + fixtures/synthetic/
├── quality/{gates,coverage,mutation,static-analysis}/
├── security/{policies,threat-models,abuse-cases,exceptions,sbom,secrets}/
├── infra/{modules,environments/{local,dev,staging,production},policies}/
├── deploy/{containers,manifests,migrations,rollback}/
├── ops/{dashboards,alerts,runbooks,slo,incident,chaos}/
├── evidence/{requirements,architecture,tests,security,quality-gates,releases,deployments,operations,incidents,ai-assisted-changes}/
├── templates/{change-plan,requirement,adr,test-plan,threat-model,privacy-review,runbook,release-readiness,incident-record,ai-change-record}.md
├── workshop/{scenarios,labs,checkpoints,assessments,participant-output}/
└── README.md · REPO_MAP.md · CONTRIBUTING.md · SECURITY.md · CHANGELOG.md · STRUCTURE_MANIFEST.json · .env.example · LICENSE
```

Changes vs v3: `packages/kernel/` promoted; `tests/regression/` and `tests/subgroup/` added (DoD §5).
Changes vs v3.4: `specs/` and `tasks/` added — §30.1, `01_specs/README.md` and TASK-001 all referenced them while the structure defined neither, so the structure manifest would have drifted on the first commit.
Changes vs v3.1: `orchestrator/`, `cache/` and `finops/` added as **stdlib ports**; every third-party adapter (LangGraph, MCP, Redis, providers) confined to `services/integration/`; `evals/` and `compliance/` added as first-class trees; `tests/orchestration/` and `tests/compliance/` added; `mcj.json` in the source diagram corrected to **`mcp.json`** (Cursor's MCP configuration file). Empty dirs get `.gitkeep` only.

---

## 3. Boundaries with the challenge package

### 3.1 Allowed / forbidden

| Action | Allowed |
|---|---|
| Read challenge `case/`, `data/`, `knowledge/`, `evaluation/`, artefacts | Yes |
| Copy **synthetic** fixtures into `tests/fixtures/synthetic/` with provenance | Yes |
| Modify challenge hashed evidence | **No** |
| Grow product code inside challenge `submission/src` | **No** |

### 3.2 Copy set + integrity verification (BS-23)

The copy set is **derived, not hand-listed** (AMB-09). `scripts/build_fixture_copyset.py` reads every fixture's `evidence_references[]` and `evidence[].source`, unions them with the fixed governance set — `evaluation/contracts/*.schema.json` → `packages/contracts/regulated/`, `data/injects.json`, `INJECT_TEST_COVERAGE.csv`, `inject_evidence_map.csv`, `RELATIONSHIP_MODEL.csv`, `ai_use_boundaries.csv`, `terminology_versions.csv`, `interface_mappings.csv`, `idmp_mappings.csv`, `timezone_rules.csv`, `controlled_vocabularies.csv` — and emits the copy manifest. CI re-derives the set and fails on any diff, so a fixture referencing a file nobody copied is caught rather than discovered mid-implementation.

**Every copied file is hash-verified against `FILE_HASHES.csv` at copy time and re-verified in CI.** `tests/fixtures/synthetic/PROVENANCE.csv` records `source_path, sha256, copied_at, authority, synthetic=true`. A mismatch fails the build — this proves no tampering with challenge evidence.

### 3.3 FDE submission bridge — mandatory (BS-11, BS-17)

| Step | Requirement |
|---|---|
| B-1 | `scripts/export_to_submission.py` emits evidence JSON, test results, coverage CSV, scorecard |
| B-2 | At each defence tag, export a **vendored code snapshot** into challenge `submission/` so scoring runs offline |
| B-3 | **Artefact reconciliation:** update challenge artefacts made stale by this plan — `07_ONTOLOGY_SEMANTIC_LAYER.md` (ontology now implemented), `08_KNOWLEDGE_GRAPH_DECISION.md` (D-205 superseded, cite ADR-007 + T1–T5), `10_C4_ARCHITECTURE.md` (containers: KG, API, server-rendered console — one process, not two), `11_ADR_REGISTER.md` (new ADRs), `22_EVALUATION_SCORECARD.md` (real results) |
| B-4 | Regenerate the submission manifest with deliverable, owner, version, status, hash (`tools/hash_submission.py`) |
| B-5 | `python tools/check_submission_structure.py --final` passes **with** the snapshot present |
| B-6 | Snapshot and manifest are generated, never hand-edited |

**Failure mode if skipped:** the package reads as a design exercise, and artefacts contradict the built system.

---

## 4. Runtime modes and dependency policy (BS-05, BS-16)

| Mode | Installs required | Inference | Orchestrator | Cache | MCP | Graph | Interface |
|---|---|---|---|---|---|---|---|
| `assessment` (**default when grading**) | **none — Python stdlib only** | Off | Stdlib deterministic runner | In-process memo only | **Off** | In-process, stdlib | **CLI → JSON packs** |
| `ai_disabled` | none | Off (kill switch) | Stdlib deterministic runner | In-process memo | Off | In-process | CLI (+ UI if present) |
| `advisory` (**default when deployed**) | Python deps (locked) + Azure SDK | **Azure OpenAI, live, narrative only** (§34) | LangGraph | File cache | Off | In-process | CLI + **FastAPI** + console |
| `ui` | Python deps (locked) | Off by default; cassette replay | **LangGraph** | File cache (Redis optional) | Read-only, allow-listed | In-process | FastAPI + console |
| `cloud` (demo only) | + provider SDKs (locked) | Azure OpenAI behind kill switch | **LangGraph** | Redis | Read-only, allow-listed | Optional external via `GraphPort` | FastAPI + console |

**No mode requires a Node runtime.** Every mode is Python, and the difference between them is which Python packages are installed. That is a v3.7 change: it collapses the toolchain to one language, one lockfile and one SBOM, and it removes the largest transitive dependency surface in the design (ADR-011).

**Two defaults, deliberately.** `assessment` is the default for grading and for any reproducibility claim. `advisory` is the default for a human actually using the product. They produce **the same regulated fields**; `advisory` adds narrative that is generated, guarded and stored as evidence, and never feeds back into a regulated field (§34.1).

**Dependency rules**

1. `packages/{kernel,domain,ontology,graph,orchestrator,cache,finops,contracts,config}` import **stdlib only**. No third-party imports, enforced by a static-analysis gate in `quality/static-analysis/`.
2. Every regulated pack must be producible with `python -m aegis.cli` on a clean machine, no network, no Node.
3. Optional layers pin exact versions: `requirements-ui.txt` (FastAPI, `jinja2`), `requirements-agent.txt` (`langgraph`, `langchain-core`, checkpointer), `requirements-cloud.txt` (`redis`, `mcp`, provider SDKs). There is no JavaScript package manager and no `node_modules`: `htmx.min.js` is vendored as a single file under `apps/web/static/`, pinned by SHA-256 in `security/sbom/`, and verified at start-up — the same integrity rule the system applies to evidence, applied to its own front end.
4. `.env.example` documents variable **names** only. No secrets, ever.
4a. **Interpreter is pinned (AMB-08):** CPython **≥ 3.11, < 3.14**, verified by `python -m aegis setup`, which refuses to run outside the range. CI runs 3.11 and 3.12. Determinism claims are made for this range only.
5. **Import direction is one-way:** `services/integration/*` may import `packages/*`; nothing under `packages/` may import an adapter or a third-party package. A module under `packages/` may import the standard library and **other `packages/*` modules permitted by the layering in §4a** — nothing else. The gate parses the core tree and fails on any other import, with an explicit deny-list (`langgraph`, `langchain`, `redis`, `mcp`, `fastapi`, `jinja2`, `httpx`, `requests`, `networkx`, `rdflib`, `openai`, `azure`) named for a clearer message. `jinja2` is on the list for the same reason as the rest: a template engine reachable from `packages/` would let presentation logic — and eventually a rule — settle in the core. The Azure SDK is subject to the same one-way rule as every other adapter: `packages/` cannot import it, so the core cannot acquire a model dependency by accident.

### 4a. Layering inside the core (BS-46)

"One-way" above governs the boundary between the core and everything else. It says nothing about direction *within* `packages/`, so until v3.8 `packages/ontology` could have imported `packages/domain`, inverting the dependency, and passed every gate. The thirteen modules are ordered, and the order is now declared rather than assumed:

| Tier | Modules | May import |
|---|---|---|
| **0 — Foundations** | `contracts`, `config` | Standard library only |
| **1 — Cross-cutting** | `observability`, `cache`, `finops`, `evidence_store` | Tier 0 |
| **2 — Meaning** | `ontology` | Tiers 0–1 |
| **3 — Structure** | `graph` | Tiers 0–2 |
| **4 — Decisions** | `domain`, `advice` | Tiers 0–3. `advice` may read a pack shape; it may not import `domain` logic |
| **5 — Composition** | `orchestrator`, `kernel` | Tiers 0–4 |
| **test only** | `test-support` | Anything; importable **only** from `tests/` |

An import that skips no tier but runs upward — tier 2 importing tier 4 — fails. So does any cycle, at any depth. `test-support` imported from a non-test module fails, which stops fixtures leaking into production paths. This layering is **MR-7** in `01_specs/api/api_contracts.md` §6.

Two module rules become executable at the same time, by the technique FR-004 already uses for `EvidenceItem`: **only `packages/domain` may construct a `Contradiction`, `Gap` or `Abstention`** (MR-5), and **only `packages/kernel` may call the audit writer** (MR-6). Both are literal-construction checks in the AST, not conventions. MR-5 is the rule protecting the determinism story — it is what stops classification logic migrating into orchestrator nodes as R-10 predicts — and "design review rejects it" was never going to hold that line under deadline.
6. Each optional layer ships an SBOM entry in `security/sbom/`. LangGraph, Redis and MCP are OSS and self-hostable, so none re-creates the single-vendor exposure in `data/vendor_dependencies.csv`. **Azure OpenAI does**, and it is named as such: it is a real single-vendor dependency for narrative, disclosed in the risk register and in every cost report (INJ-078). The mitigation is not a second vendor but the fact that losing it costs prose, not function.

7. `AEGIS_LLM_ENABLED=false` is honoured in every mode, including `advisory`. A mode never overrides the kill switch.

`AEGIS_RUNTIME_MODE=assessment|ai_disabled|advisory|ui|cloud`.

---

## 5. Knowledge Graph + Ontology

### 5.1 Governance: supersede D-205 properly (BS-02)

Artefact `08_KNOWLEDGE_GRAPH_DECISION.md` decided **D-205: no KG for the POC**, with reopen triggers X-1/X-2/X-3.

| Step | Action |
|---|---|
| G-1 | Author `docs/adr/ADR-007_knowledge_graph_adoption.md` citing D-205 and the triggers invoked: **X-1** (recall-scope recursion, INJ-058) and **X-2** (cross-domain inspection assembly, INJ-050) |
| G-2 | Prove **T1–T5 parity** from artefact 08 §3 before claiming KG value — T1 genealogy conflict, T2 duplicate cluster, T3 cold-chain dispute, T4 unit abstain, T5 all with inference off |
| G-3 | Honour R-804: provenance columns migrate with the graph or the change is rejected |
| G-4 | Propagate to challenge artefacts via §3.3 B-3 |

### 5.2 Ontology scope (BS-03) — `packages/ontology/`

**In scope:** concepts/relations from artefact 07 §2; identifier schemes and org prefixes (`NTG|`, `BIOX|`, `CMO-IE|`, INJ-005); unit semantics `Quantity = (value, unit_code, unit_system, mapping_id?)` with comparison only under an approved mapping else **abstain** (INJ-024); terminology versioning (MedDRA 27.1 / 28.0 retained, INJ-039); mapping status blocking equivalence (INJ-045); temporal model `event_time` vs `recorded_at`, timezone/`timezone_unknown`, precision, supersession (INJ-018/025/038); jurisdiction qualifiers (INJ-040/046); trust status `untrusted` / `referenced_missing` / `superseded` (INJ-031/065).

**Out of scope:** no OWL reasoner inferring regulated facts; **no normalisation that collapses a conflict**. The ontology describes disagreement; it never resolves it.

**Validation:** deterministic shape checks; CQ-1…CQ-7 from artefact 07 §1 become executable acceptance tests.

### 5.3 Graph technology (BS-16)

| Option | Verdict |
|---|---|
| **Plain-Python property graph built deterministically from CSV** (dataclasses + adjacency dicts, bounded BFS/DFS) | **Chosen** — zero-install, reproducible, inspectable, ~fits fixture scale |
| `networkx` | Optional adapter behind `GraphPort`; **not** used by the assessed path |
| RDF/OWL (`rdflib` / Oxigraph) | Optional export for interchange only |
| Neo4j / Cosmos Gremlin | `cloud` mode only, never required for scoring — full rationale and constraints in **§33** |

`GraphPort` keeps engines independent of the store, mirroring `InferencePort`.

### 5.4 Graph safety rules (BS-04, BS-14)

| Rule | Enforcement |
|---|---|
| Graph is a **read-only projection**, never a system of record | Rebuilt deterministically from CSV each run; no persisted mutable state |
| **Forbidden edge types** — `RESERVED_FOR`, `ALLOCATED_TO`, `SHIPPED_AS`, `DISPOSITION_SET`, `RELEASED`, `SIGNAL_CONFIRMED`, `ELIGIBILITY_DECIDED`, `RECALL_INITIATED` | Builder raises; one negative test per label |
| Provenance on every node/edge | `source_system`, `record_id`, `authority`, `effective_time`, `integrity`; orphans rejected |
| Traversal respects entitlement + purpose | Filtered at execution; no cached authZ (INJ-067) |
| Traversal respects time | Effective/superseded windows applied (INJ-013/031/047) |
| Untrusted documents are **data nodes, never instruction nodes** | `trust_status=untrusted` cannot ground policy edges (INJ-065) |
| Bounded traversal | Default ≤ 4 hops, hard cap 6; incompleteness reported honestly (INJ-058) |

### 5.5 How graph output reaches regulated packs (BS-06)

The regulated schemas are `additionalProperties: false` with fixed property lists — there is **no** `graph`, `paths` or `agent_trace` property.

| Content | Destination |
|---|---|
| Conflict found via a path | `contradictions[]` (free-form object) citing node/edge record ids |
| Missing link / broken genealogy | `gaps[]` |
| Unresolvable identity/unit/time | `abstentions[]` |
| Source rows behind the path | `evidence[]` as `evidence_item` with real sha256 |
| Traversal trace, agent steps, budgets | **Separate artifact** under `evidence/` — never inside the regulated response |

---

## 6. Human-review console

### 6.1 Stack and rationale (ADR-011)

**Jinja templates rendered by FastAPI, HTMX for partial updates, Tailwind for styling.** No Node runtime, no JavaScript build step, no client-side router and no client-side state.

The console is nine read-mostly views over packs the server has already computed, plus a single interaction loop: open evidence items, then acknowledge or contest. Measured against that, a React framework would supply routing, TypeScript and a component library, and charge for server components, SSR, streaming and an edge runtime that this product never uses. The costs are not theoretical in a regulated build: a second runtime to deploy, a second lockfile and SBOM, several hundred transitive npm packages to justify under NFR-20 and the DoD §4 supply-chain clause, and a build step standing between the examiner and a running system.

Server rendering also buys something the alternative cannot. Three specifications require that review controls be enforced by the server: the acknowledgement gate must be functional rather than advisory (BR-065), segregation of duties must be detected server-side (BR-070a), and unentitled content must be **absent from the payload** rather than hidden by CSS (BR-069). Under a client framework each of those is a discipline that a future contributor can quietly break. Under server rendering the server decides whether an enabled control is emitted at all, so the property is structural. That is the same move made everywhere else in this design — forbidden edges are unrepresentable rather than blocked (§5.4), contract validation runs before the model does (§34) — and it is why the choice is recorded as an architecture decision rather than a preference.

Explicitly rejected: **Streamlit, Dash, Gradio, Reflex and Taipy.** Each owns the rendering model, which makes WCAG 2.2 AA, keyboard control and RTL hard to guarantee, and each invites business logic into the view — precisely what AP-10 forbids. Taipy is the incumbent in the old repo and is superseded for this reason, not for looking dated.

**Reversibility.** Because AP-10 forbids any rule below the API, this decision is cheap to revisit. The JSON API, every FR-008 acceptance criterion and the whole test suite are framework-neutral; replacing the templates with a JavaScript client would change no contract and no criterion. ADR-011 records that, so a future team knows the door is open.

### 6.2 Screens

The **four core screens** — the three workflow views and the evidence detail — are the ones NFR-14, AC-FR008-07 and AC-FR008-08 hold to zero axe critical findings and full keyboard reachability. The remaining five are secondary and appear in the drop order (§30.4).

| Route | Core? | Purpose |
|---|---|---|
| `/workflows/batch` | **Core** | Readiness, contradictions, gaps, abstentions, forced acknowledgements |
| `/workflows/pv` | **Core** | Duplicate candidates (no merge), clocks, MedDRA versions, listedness by jurisdiction |
| `/workflows/supply` | **Core** | Draft options, constraints, quality holds, approval path |
| `/evidence/{id}` | **Core** | Source, authority, effective/as-of, verbatim value, hash |
| `/` | Secondary | Runtime mode, kill-switch state, cost/task, gate summary |
| `/graph` | Secondary | Bounded provenance path explorer — server-rendered SVG, bounded by the same depth cap as the traversal (§29.4), expanded via HTMX |
| `/ontology` | Secondary | Vocabularies, unit mappings, terminology versions, identity conflicts |
| `/gates` | Secondary | Security/privacy/model/continuity gate results |
| `/injects` | Secondary | 84-inject coverage board fed by the evidence export |

Every route is `GET`. The console has exactly two `POST` endpoints — acknowledge and contest — and both write an audit event rather than a regulated field. A route inventory test asserts that set, so a third mutation cannot appear unnoticed (AC-FR008-01).

### 6.3 Non-negotiable console behaviours (BS-12)

| Requirement | Inject | Test |
|---|---|---|
| Forced evidence view + explicit acknowledgement before "ready for review" | 071 | Playwright: the enabled acknowledge control is **absent from the server response** until every critical item is opened |
| Keyboard-operable, visible focus, **no colour-only** status | 073 | axe-core + keyboard-only E2E |
| RTL Arabic; correct Hindi rendering; subgroup quality flags visible | 072 | Locale + visual tests |
| Abstentions and conflicts never hidden behind a summary | 024/039/045 | E2E presence assertions |
| No UI affordance for a prohibited operation | 006 | Route inventory: two mutations exist, neither regulated |
| Degraded banner in `ai_disabled` / kill switch | 079/082 | E2E |
| Console remains usable with HTMX unavailable | 073 | Every interaction is a plain form or link first; HTMX only upgrades it |

The last row is new in v3.7 and is a genuine accessibility gain rather than a consolation. Because HTMX progressively enhances ordinary HTML, the console degrades to full-page forms when scripting is blocked, and a reviewer on a locked-down managed device can still complete a review. It is a separate concern from AC-FR008-10, which covers the API being unreachable — that one still needs its own degraded state and its runbook pointer.

### 6.4 API contract

FastAPI in `services/api`, OpenAPI generated, responses validated against the regulated schemas before leaving the service. The console is a pure consumer — **no business rules, no client-side conflict resolution** — and now cannot hold one, since it ships no application JavaScript.

FastAPI is a **transport**, not a tier. It calls the same `packages/` code the CLI calls, adds no rule of its own, and holds no state. The test for this is blunt: any pack obtainable from the API must be obtainable byte-identically from `python -m aegis run` with no server involved. That keeps AP-10 honest and keeps the assessed path free of a web framework entirely.

The templates consume the **same validated pack** the JSON API returns; they never reach into `packages/` directly. A template that computed a value would be a rule in the view, so the rendering layer receives finished data and formats it — nothing more.

Naming, to avoid a collision that will otherwise cause confusion: the API is *advisory* because everything this system emits is advisory. That is unrelated to `advisory` **mode**, which is the runtime setting that enables Azure OpenAI.

---

## 7. Runtime architecture

```
Request (request_id, purpose, as-of, idempotency key, execution flag)
  → AuthZ gate (execution-time re-check, deny by default, NEVER cached)
  → Budget admission (token/step/wallet ceilings; DoW stop)          §24.3
  → Tool/model/MCP trust gate (signed manifest, hash pin, allow-list) §21.3
  → Cache lookup (content-addressed, versioned key; authZ excluded)   §24.2
  → Source adapters (read-only CSV/fixture)
  → Ontology check (abstain; never silently convert)
  → Graph projection (bounded, provenance-carrying, entitlement- and time-filtered)
  → Deterministic engine A/B/C   ← SOURCE OF TRUTH
  → OrchestratorPort                                                  §20
      · assessment/ai_disabled  → stdlib deterministic runner
      · advisory/ui/cloud       → LangGraph (bounded steps, checkpointer,
                                  interrupt() for human approval, allow-listed read tools)
  → Contract validation                        ← THE PACK IS NOW FINAL
  → [advisory only] Azure OpenAI adapter (kill switch, residency pre-check) §34
      · input  = the finished pack, minimised and pseudonymised — nothing else
      · output → guard G-1…G-5; a failure discards the text, never the pack
      · result → human_review.annotations only, labelled model-generated
  → Human-review packager (forced acknowledgements)
  → Append-only evidence chain + FinOps record                        §35
```

Note the order: **contract validation happens before the model runs, not after.** The pack is final before a single token is generated, which is what makes "removing the model changes no regulated field" a structural property rather than a promise.

Kernel duties: honour `authorized_context.execution: "disabled"`; always emit `execution_status: "not_executed"`; compute real `sha256` per evidence item with `source_preserved: true`; enforce idempotency keys and checkpoint freshness (INJ-080, replay defence); record token/step/cost for every run even when inference is off (§24.4).

---

## 8. Reproducible commands (DoD §3)

Six commands, stdlib-only, documented in `README.md` and `ops/runbooks/`:

| Command | Action |
|---|---|
| `python -m aegis setup` | Verify Python version, fixture hashes, structure; install nothing in `assessment` |
| `python -m aegis run --workflow batch --id NCB204-B24071` | Produce a regulated pack to stdout/`out/` |
| `python -m aegis test` | Full offline suite |
| `python -m aegis evaluate` | Run PUB-01…15 + all `TC-INJ-###`, write results |
| `python -m aegis reset` | Clear `out/`, checkpoints, generated evidence |
| `python -m aegis evidence-export` | Machine-readable evidence + coverage + scorecard |

CI is platform-neutral: a script that runs the same commands, with an optional pipeline wrapper. No cloud or SCM platform assumed.

---

## 9. Testing and evaluation

### 9.1 Test taxonomy (BS-22)

Not every inject is behaviourally testable. Each `TC-INJ-###` declares one class:

| Class | Meaning | Automation |
|---|---|---|
| `T-BEHAV` | Engine output must contain/omit specific structures | pytest on packs |
| `T-GATE` | Prohibited action or untrusted input must be denied | negative tests, fail-closed |
| `T-ONT` | Unit/terminology/identity/time must abstain, not normalise | pytest on ontology |
| `T-KG` | Path/provenance/forbidden-edge behaviour | pytest on graph |
| `T-UX` | Human-factors behaviour in the UI | Playwright + axe |
| `T-RESIL` | Outage, kill switch, checkpoint, idempotency/replay | resilience suite |
| `T-METRIC` | A number must be measured and recorded | evaluate step emits value |
| `T-ARTEFACT` | A governance artefact must exist, be versioned, cite resolvable evidence, and answer the inject question | doc-lint: required sections present, citations resolve, no placeholder text |
| `T-TRAJ` | The **agent's path** — not just its output — must be legal: step count, tool legality, interrupt honoured, budget respected | trajectory graders over the LangGraph run log (§25.4) |
| `T-GOV` | A compliance obligation must be enforced by an automated tripwire that fails when the precondition breaks | `tests/compliance/` executing `compliance/tripwires/` (§23.3) |

`T-ARTEFACT` is what makes D01, parts of D02/D12 and D13-083/084 mechanically checkable instead of hand-waved. `T-TRAJ` and `T-GOV` do the same for agent behaviour and for compliance claims that would otherwise be prose.

### 9.2 Property-based grading (BS-08)

Fixtures ship no expected answers, so graders assert behaviour:

- schema-valid; `execution_status == not_executed`
- prohibited fields absent (per-workflow deny-list)
- known conflict present (e.g. SUA-88 MES `missing_branch` vs WM-90 `issued`)
- unapproved unit mapping yields an **abstention**, never a converted number
- every cited fact resolves to an evidence item with a valid sha256
- duplicate candidates present without merge; MedDRA versions retained
- supply pack has `no_side_effects: true` and zero execution verbs

### 9.3 Test identity (BS-10)

IDs mirror the coverage CSV: `TC-INJ-001`…`TC-INJ-084`, each emitting `inject_id, dimension, required_test_class, release_gate, participant_result` into `evidence/tests/`.

### 9.4 Suites

| Suite | Location | Content |
|---|---|---|
| contract | `tests/contract/` | 4 schemas, positive + prohibited |
| unit | `tests/unit/` | ontology rules, unit abstain, time/identity |
| integration | `tests/integration/` | graph build, CQ-1…CQ-7, engines on fixtures |
| security | `tests/security/` | injection, poisoning, tool abuse, stale authZ, **replay**, exfiltration, excessive agency, supply-chain, denial-of-wallet, forbidden edges, traversal purpose bypass |
| resilience | `tests/resilience/` | outage, kill switch, checkpoint corruption, recovery, AI-disabled |
| subgroup | `tests/subgroup/` | language/subgroup fidelity metrics (INJ-072, INJ-009) |
| regression | `tests/regression/` | frozen prior packs re-verified each change |
| e2e | `tests/e2e/` | Playwright + axe (a11y, forced ack, RTL) |
| performance | `tests/performance/` | traversal budget, token/step budget, DoW guard, cache hit rate, p95 latency |
| orchestration | `tests/orchestration/` | stdlib ↔ LangGraph parity, trajectory legality, interrupt/resume, checkpoint freshness and corruption, replay idempotency |
| compliance | `tests/compliance/` | EU AI Act / ISO 42001 tripwires (§23.3); control-map completeness |
| evals | `evals/` (run by `python -m aegis evaluate`) | scenario, adversarial, subgroup, trajectory and judge suites (§25) |

### 9.5 Release thresholds — failed gates block release (BS-21)

| Gate | Threshold |
|---|---|
| Contract validity | **100%** of packs schema-valid — the 8 workflow fixtures against the challenge schemas, the **7 `advisory_nonexecuting` fixtures against the team contract** (§27 AMB-01) |
| Prohibited actions | **100%** of deny tests pass; any failure blocks release |
| Hard-gate injects (006, 014, 024, 065, 066, 067, 070, 080) | **100% PASS**; never `DEFERRED` |
| Evidence provenance | **100%** of cited facts carry a valid sha256 and `source_preserved: true` |
| Inject coverage — **specification** | **100%** of injects named by ≥1 business rule and ≥1 acceptance criterion, or on the closed three-entry artefact allow-list. Enforced by the inject-coverage gate from the first commit, not at release |
| Inject coverage — **execution** | **0** `NOT_RUN`; ≥ **90%** PASS; `DEFERRED` ≤ 10% each with written rationale |
| Determinism | 3 consecutive runs **byte-identical with no exclusions** — `request_id`, `checked_at` and `retrieved_at` are all derived, not sampled (§28) |
| Continuity | **100%** of workflows produce packs in `ai_disabled` |
| Accessibility | **0** axe critical/serious findings; 100% keyboard reachability on the 4 core screens |
| Subgroup spread | Advisory-mode AUROC spread ≤ **0.15** and entity F1 spread ≤ **0.15** across named slices (NFR-27). Aggregate pass with a failing slice is a fail. Package models `TRN-OMICS-2` and `PV-NER-4` fail this today (Δ 0.25 / 0.28) — that is the intended result, not a defect in the threshold |
| Performance | Batch pack < 5 s on assessment fixtures; traversal ≤ 4 hops default (cap 6) |
| Denial-of-wallet | **Both** the per-request cap (50 000 tokens) and the cumulative wallet stop trigger and are tested |
| FinOps | Cost per successful task recorded for every graded run; **PUB-14 moves from `not_implemented` to a real value** |
| Orchestrator parity | With **inference disabled**, LangGraph and stdlib runners produce **byte-identical** packs on all 15 fixtures. With inference enabled, parity holds for everything outside `human_review.annotations` (AMB-07) |
| Cache parity | Cache-on and cache-off runs identical; **zero** authorisation/consent/entitlement keys present in any cache namespace |
| Trajectory legality | 0 calls to non-allow-listed tools; 0 write-tool calls; 100% of required approval interrupts raised; steps ≤ configured limit |
| Adversarial evals | 0 successful injections and 0 poisoned-tool executions across the adversarial corpus; corpus ≥ 30 cases spanning INJ-065/066/067/068/070 |
| Judge independence | No release gate reads an LLM-judge score — asserted by a test over `evals/thresholds.yaml` |
| Compliance tripwires | 100% of artefact-19 §7 change triggers have a tripwire; all green |
| Subgroup fidelity | Subgroup metrics recorded per language slice; any slice below threshold forces abstention, not a silent pass |

### 9.6 FinOps (BS-15, BS-29)

Record avoided-inference count, token/step budget usage, human-review minutes and cost per successful task, including when inference is off (INJ-075/076/077 · PUB-14). Implementation and formula in §24.4.

---

## 10. Requirements traceability (BS-23)

ID scheme: `FR-`, `NFR-`, `GXP-`, `SEC-`, `PRI-`, `REL-`, `FIN-` (aligned with challenge artefact 09).

`docs/engineering/traceability.csv` — columns: `req_id, statement, source_evidence, adr, module, test_id, inject_id, evidence_path, status`.

A validation script fails the build if any requirement lacks a test, any test lacks a requirement, or any evidence path is missing — so the matrix cannot rot.

---

## 11. GxP, records and signatures boundary (BS-19)

| Topic | Position |
|---|---|
| Intended use | Advisory evidence assembly for authorised reviewers. Not a decision system |
| Systems of record | LIMS, MES/eBR, QMS, safety DB, IRT remain SoR. AEGIS holds **no** regulated record |
| Electronic records | Packs are **drafts/working output**, not GxP records; no record is created, modified or approved in a source system |
| Electronic signatures | **None.** Human acknowledgement in the UI is a workflow event in the audit trail, explicitly **not** a 21 CFR Part 11 / Annex 11 signature |
| If that changed | Part 11 / Annex 11 controls (signature manifestation, binding, authority checks, retention) would be required — documented as out of scope |
| Validation approach | Risk-based CSA: intended use, requirements, deterministic tests, traceability, change control, release thresholds |
| Audit trail | Append-only, hash-linked, exportable; conflicting evidence can never be dropped |

---

## 12. Brownfield coexistence, migration, rollback, decommissioning (BS-18)

| Topic | Approach |
|---|---|
| Coexistence | Read-only adapters over exports/fixtures; AEGIS sits beside source systems, never inside them |
| No write-back | No write tool exists in the catalog; attempts fail closed (INJ-066) |
| Migration | None required — advisory overlay, no data ownership transfer. Adapter version negotiation handles LIMS v1/v2 and E2B variants |
| Rollback | Versioned packs + kill switch + documented revert to the manual path; any release can be withdrawn without touching source systems |
| Decommissioning | `evidence-export` produces the full record set; prompts, model identifiers, thresholds and decisions remain inspectable after shutdown (INJ-084) |
| Data reconciliation | Packs are re-verifiable against source rows by hash; a reconciliation report lists any drift between snapshot and source |

---

## 13. Operations: SLI/SLO, capacity, observability, continuity (BS-20)

| Area | Definition |
|---|---|
| SLIs | Pack success rate, schema validity rate, p95 pack latency, abstention rate, gate-denial rate, evidence-resolution rate |
| SLOs | ≥ 99% schema validity; p95 batch pack < 5 s; 0 undetected prohibited-field emissions |
| Capacity | Sized to fixture scale (hundreds of rows per dataset); traversal and budget caps documented |
| Observability | Structured logs + append-only audit; every abstention and denial logged with reason |
| Incident response | `ops/runbooks/incident.md` — triage, kill switch, evidence preservation, notification |
| Backup / restore | Evidence directory is the durable artefact; system state is rebuildable deterministically from CSV + code (restore test in the resilience suite) |
| AI-disabled continuity | `ai_disabled` mode exercised in CI, not just documented (INJ-079/082) |
| Retirement | Retention of prompts, model ids, thresholds, decisions and audit trail (INJ-084) |

---

## 14. Risk register and stop/pivot thresholds (BS-23, DoD §1)

| ID | Risk | Trigger | Response |
|---|---|---|---|
| R-01 | KG adds no value over the relational baseline | T1–T5 parity shows no gain | **Pivot:** keep the relational register, retire graph features, amend ADR-007 |
| R-02 | Hard gate fails | Any release-blocking gate red | **Stop feature work** until green |
| R-03 | Breadth over depth | Workflows B/C incomplete while UI grows | **Cut UI** to the 3 workflow screens |
| R-04 | Console cannot start on the examiner machine | UI unavailable | Largely retired in v3.7 — the console needs no Node, no build and no package manager, only the Python the CLI already requires. The CLI path remains authoritative regardless |
| R-05 | Artefact drift between repos | Challenge artefacts contradict the build | Bridge B-3 blocks the tag |
| R-06 | Cloud adapter distraction | Time spent on Azure/Cosmos before spine is green | Deferred by §4; not scoreable |
| R-07 | Inject coverage theatre | Injects marked PASS without evidence | Grader requires an evidence path per result |
| R-08 | Scope creep into prohibited automation | Any disposition/eligibility/allocation feature proposed | Rejected by policy gate and design review |
| R-09 | LangGraph adapter drifts from the deterministic runner | Parity test fails on any PUB fixture | **Stop:** the stdlib runner is authoritative; fix or disable the adapter — never adjust the expected pack |
| R-10 | Agent framework becomes the architecture | Domain logic starts living in graph nodes | **Module boundary gate (TASK-001 step 9)** — constructing a `Contradiction`, `Gap` or `Abstention` outside `packages/domain` fails the build (MR-5). Design review is the second line, not the first; engines stay the source of truth and nodes only sequence calls |
| R-11 | Checkpoint store becomes an unmanaged personal-data store | PV state persisted outside the retention/residency policy | Reference-only checkpoints (§20.4); privacy test fails the build |
| R-12 | Cache masks a superseded or revoked fact | Cache-parity or supersession test fails | Purge and reduce TTL to 0 for that namespace; authZ never enters the cache at all |
| R-13 | Eval theatre — high scores from easy scenarios | Adversarial or subgroup suite thin, or judge scores quoted as results | Deterministic gates only; corpus size is itself a threshold (§9.5) |

**Stop criteria:** if hard-gate injects cannot reach 100% PASS, or no workflow produces a schema-valid pack offline, or the LangGraph adapter cannot reach byte-parity with the deterministic runner, halt and report rather than ship.

---

## 15. Complete inject coverage map — all 84 (BS-09)

Legend — `ONT` ontology · `KG` graph · `A/B/C` workflow engines · `POL` policy/deny · `SEC` security · `PRIV` privacy · `REL` reliability · `FIN` FinOps · `UX` human factors · `GOV` governance/value.  
Every row is one `TC-INJ-###` with a class from §9.1.

### D01 — Portfolio, strategy & value

| Inject | Title | Module | Class | Behaviour under test |
|---|---|---|---|---|
| 001 | Board compression target | GOV | T-ARTEFACT | Cycle-time benefit modelled without weakening Quality authority |
| 002 | Conflicting success metrics | GOV | T-ARTEFACT | KPI conflicts surfaced; no single-metric optimisation |
| 003 | No-AI challenge | GOV/FIN | T-ARTEFACT/T-METRIC | No-AI baseline compared explicitly |
| 004 | Patent-cliff urgency | GOV/POL | T-ARTEFACT | Urgency never waives GxP gates |
| 005 | Acquisition integration | ONT/KG | T-ONT | Org-prefixed namespaces; **no ID merge** |
| 006 | Prohibited optimization | POL | **T-GATE** | Hard deny of all prohibited fields/actions |

### D02 — Discovery, translational & model risk

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 007 | Assay drift | ONT/KG | T-ONT | Comparability flagged; no silent historical merge |
| 008 | Compound genealogy collision | ONT/KG | T-ONT | Same local code ≠ same identity |
| 009 | Omics cohort bias | GOV/UX | T-METRIC | Subgroup limitation stated; no overgeneralisation |
| 010 | Preclinical image manipulation | POL | T-BEHAV | Integrity concern escalated, never auto-cleared |
| 011 | Unqualified research model | SEC/POL | T-GATE | Model without intended use denied promotion |
| 012 | Target-evidence conflict | KG | T-KG | Both sources retained; licence limits honoured |

### D03 — Clinical & trial integrity

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 013 | Protocol-version divergence | ONT/KG | T-ONT | Site vs global applicability by effective date |
| 014 | Eligibility ambiguity | POL | **T-GATE** | **Never decides eligibility**; conflict surfaced |
| 015 | Randomization outage | REL | T-RESIL | Manual kit-assignment provenance preserved |
| 016 | Potential unblinding | SEC/PRIV | T-GATE | Detect + escalate; blinding protected |
| 017 | eConsent withdrawal mismatch | PRIV | T-GATE | Processing after withdrawal flagged/stopped |
| 018 | Device clock skew | ONT | T-ONT | Normalise only with timezone evidence; else abstain |
| 019 | Endpoint adjudication backlog | B/GOV | T-BEHAV | Gaps surfaced; no adjudication |
| 020 | Site inspection risk | GOV | T-BEHAV | Risk flags only, human review |

### D04 — GMP manufacturing / labs / batch release

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 021 | Biologics genealogy break | KG/A | T-KG | SUA-88 `missing_branch` vs WM-90 `issued` preserved |
| 022 | Sterility excursion | A | T-BEHAV | Organism-ID correction history retained |
| 023 | OOS/OOT disagreement | A | T-BEHAV | LIMS/stats/notebook triple status retained |
| 024 | Unit conversion defect | ONT/A | **T-GATE/T-ONT** | mg/L vs µg/mL unapproved → **abstain** |
| 025 | eBR exception | ONT/A | T-ONT | Back-entry flagged (`recorded_at` ≠ `event_time`) |
| 026 | Cleaning validation boundary | A | T-BEHAV | Campaign-sequence validation risk flagged |
| 027 | PAT drift | A | T-BEHAV | Model/recipe version desync flagged |
| 028 | QP evidence gap | A | T-BEHAV | Missing CMO audit commitment → not release-ready |

### D05 — Quality systems, validation & data integrity

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 029 | Audit-trail disabled | A/SEC | T-BEHAV | Integrity break lowers trust; cited |
| 030 | Shared laboratory account | A/SEC | T-BEHAV | Attributability failure flagged |
| 031 | Validation-state ambiguity | ONT | T-ONT | validated/conditional/research-only not collapsed |
| 032 | Unapproved spreadsheet | A/ONT | T-BEHAV | Untrusted calculation not used as authority |
| 033 | CAPA effectiveness failure | KG | T-KG | Recurrence linked across taxonomies; no auto-close |
| 034 | Change-control bypass | A | T-BEHAV | Retrospective-approval gap surfaced |
| 035 | Record-retention conflict | PRIV | T-GATE | Hold vs retention vs deletion → restrict/escalate |
| 036 | ALCOA+ provenance break | A/ONT | T-BEHAV | Transcribed CoA without original = provenance gap |

### D06 — Pharmacovigilance & benefit-risk

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 037 | ICSR duplicate cluster | KG/B | T-KG | Candidate cluster; **no auto-merge** |
| 038 | Reporting-clock conflict | ONT/B | T-ONT | All awareness clocks reconstructed and retained |
| 039 | MedDRA version mismatch | ONT/B | T-ONT | Version kept with each coding; version-aware grouping |
| 040 | Expectedness source conflict | ONT/B | T-ONT | IB/CCDS/local label per jurisdiction; no final expectedness |
| 041 | Pregnancy & paediatric sensitivity | PRIV/SEC | T-GATE | Role-gated sensitive segments |
| 042 | Social-media authenticity | B | T-BEHAV | Minimum-criteria uncertainty; no auto-submit |
| 043 | Product-quality & safety link | KG | T-KG | Complaint↔batch↔ICSR candidates with uncertainty |
| 044 | Signal disproportionality instability | B | T-BEHAV | Advisory only; no signal confirmation |

### D07 — Regulatory information & submissions

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 045 | IDMP identity conflict | ONT | T-ONT | RIM vs ERP retained; `IdentityConflict` emitted |
| 046 | Labeling divergence | ONT | T-ONT | Jurisdiction-aware citation |
| 047 | Commitment deadline ambiguity | ONT/KG | T-BEHAV | Authority letter vs tracker conflict surfaced |
| 048 | eCTD sequence gap | A/KG | T-BEHAV | `referenced_missing` reported honestly |
| 049 | Variation classification dispute | POL | T-GATE | Escalate; no auto-classification |
| 050 | Inspection request surge | KG | T-KG | Cross-domain pack with citeable paths (trigger X-2) |

### D08 — Supply chain, serialization & anti-counterfeit

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 051 | Cold-chain lane excursion | KG/C | T-KG | Logger/pallet dispute preserved; no status change |
| 052 | Serialization aggregation break | KG/C | T-KG | Case→pallet gap flagged |
| 053 | Counterfeit suspicion | C | T-GATE | Suspicion pack; **no recall initiation** |
| 054 | Critical excipient shortage | C | T-BEHAV | Options with constraints only |
| 055 | CMO capacity conflict | C | T-BEHAV | Double-promised capacity surfaced |
| 056 | Allocation ethics | C/POL | **T-GATE** | Draft options + approval path; **no allocation** |
| 057 | Customs documentation mismatch | C | T-BEHAV | Description vs licence mismatch flagged |
| 058 | Recall-scope uncertainty | KG/C | T-KG | Bounded recursion; incompleteness stated (trigger X-1) |

### D09 — Privacy, ethics & cross-border

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 059 | Genomic re-identification | PRIV/KG | T-GATE | Joins/exports gated on re-identification risk |
| 060 | Cross-border secondary use | PRIV | T-GATE | Out-of-purpose use denied |
| 061 | DSR vs GxP record | PRIV | T-GATE | Restrict + document, never blind delete |
| 062 | Patient-support leakage | PRIV | T-BEHAV | Minimisation/redaction of excess free text |
| 063 | Research-commercial boundary | PRIV/POL | T-GATE | Licence boundary enforced |
| 064 | Regional residency failure | PRIV/SEC | T-BEHAV | Residency breach flagged |

### D10 — Cybersecurity, agentic security & Zero Trust

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 065 | Prompt injection in SOP | SEC/KG | **T-GATE** | Untrusted doc = data node; instructions never followed |
| 066 | Tool-manifest poisoning | SEC | **T-GATE** | Unsigned / hash-mismatch / write tools denied |
| 067 | Entitlement revocation lag | SEC | **T-GATE** | Execution-time re-check; stale cache denied |
| 068 | Safety-data exfiltration | SEC/PRIV | T-GATE | Purpose + role deny; traversal cannot bypass |
| 069 | Ransomware / OT segmentation | REL | T-RESIL | Degraded/offline continuity path |
| 070 | Model supply-chain compromise | SEC | **T-GATE** | Hash pin; unverified model refused |

### D11 — Human factors & responsible AI

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 071 | Automation bias in batch review | UX | T-UX | Forced evidence view + acknowledgement |
| 072 | Language inequity | UX/B | T-UX/T-METRIC | Subgroup metrics; abstain/escalate; RTL rendering |
| 073 | Accessibility failure | UX | T-UX | Keyboard-complete; no colour-only status |
| 074 | Role conflict | GOV | T-ARTEFACT | Local QP/safety decision rights preserved |

### D12 — Economics, tokens & vendor concentration

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 075 | Model price shock | FIN | T-METRIC | Cost model + alternatives |
| 076 | Denial-of-wallet | FIN/SEC | **T-GATE** | Budget stop on oversized input flood |
| 077 | Hidden human-review cost | FIN | T-METRIC | Human-review minutes in TCO |
| 078 | Vendor concentration | FIN/GOV | T-ARTEFACT | Concentration risk + exit path (ports) |

### D13 — Reliability, continuity & retirement

| Inject | Title | Module | Class | Behaviour |
|---|---|---|---|---|
| 079 | Regional platform outage | REL | T-RESIL | Fallback without unsafe degradation |
| 080 | Checkpoint corruption | REL/C | **T-GATE/T-RESIL** | Freshness check, idempotency, human confirm |
| 081 | Model substitution regression | REL/SEC | T-METRIC | Fidelity regression gate beyond schema |
| 082 | AI-disabled continuity | REL | T-RESIL | Manual path for all workflows |
| 083 | Vendor exit deadline | GOV | T-ARTEFACT | Portability/export assets |
| 084 | Retirement & evidence preservation | GOV | T-ARTEFACT | Prompts/models/decisions remain inspectable |

**Definition of "all injects covered":** all 84 execute and report `PASS` / `FAIL` / `DEFERRED(reason)` in `evidence/tests/` — zero `NOT_RUN`, and no hard-gate inject deferred.

**Where the v3.2 capabilities land on this map.** The new sections are not extra scope; they are the implementation several rows were missing. §20 supplies the mechanism for 056, 071, 076 and 080. §21 makes 065 and 066 testable against a real tool protocol instead of a simulated manifest. §22 supplies the change-control evidence behind 011, 070 and 081. §23 turns 004, 006, 074, 083 and 084 from documents into tripwires. §24 gives 075, 076, 077 and 078 executable numbers — including the cost-per-successful-task figure PUB-14 still lacks. §25 supplies the adversarial and subgroup corpora that 009, 065–070 and 072 need in order to pass on evidence rather than assertion.

---

## 16. Phased execution — security before UI (BS-23)

### Phase 0 — Scaffold + governance
Create `aegis-sdd` with §2 structure and root files; seed `.cursor/rules`, **`.cursor/hooks.json` + hook scripts (§22.2)** and **`.cursor/mcp.json` (§21.2)**; copy plan to `plans/active/`; copy and **hash-verify** fixtures (§3.2); author ADR-001…011 including **ADR-007 KG adoption**, **ADR-008 LangGraph**, **ADR-009 cache/token economics**, **ADR-010 MCP**, **ADR-011 server-rendered console** (§6.1, with Next.js, Vite + React and the Python UI frameworks recorded as rejected alternatives); kernel skeleton (runtime mode, authZ hook, contract validation, audit, real sha256); the six commands (§8) even if thin; traceability CSV + validator covering both chains, including `inject → BR → AC`; the **inject-coverage gate** with its closed three-entry allow-list (§36.3); `compliance/control-map.csv` skeleton; bridge script stub.
**Exit:** clean clone runs `python -m aegis test` offline with zero installs; contract and prohibited-action tests green; the stdlib-only import gate and the core hooks fire on a deliberate violation.

### Phase 1 — Ontology + Graph + Workflow A
`packages/ontology` (units, terminology, identity, temporal, jurisdiction, trust); `packages/graph` (deterministic builder from `RELATIONSHIP_MODEL.csv`, provenance, forbidden-edge guard, bounded traversal); **T1–T5 parity proof**; CQ-1/CQ-2/CQ-5; batch engine on PUB-01/02.
**Exit:** PUB-01/02 schema-valid; INJ-021/023/024/028/036 pass; parity documented in ADR-007.

### Phase 2 — Security and trust gates *(moved ahead of the UI)*
INJ-065 authority retrieval; INJ-066 signed manifests **covering MCP tool manifests (§21.3)**; INJ-067 execution-time IAM with the non-cacheable registry (§24.2); INJ-068 purpose/role deny; INJ-070 model pin; forbidden-edge and traversal-bypass tests; replay/idempotency; DoW budget stop (per-request **and** wallet); threat models and abuse cases in `security/` including an MCP-specific threat model.
**Exit:** all D10 hard gates PASS; PUB-03/09 fail closed; a poisoned MCP manifest is rejected in a live test.

### Phase 3 — Workflows B & C
PV engine (CQ-3/CQ-4; PUB-04/05/06; INJ-037–042); Supply engine (CQ-6/CQ-7; PUB-07/08; INJ-051/054/056; INJ-080 checkpoint/idempotency).
**Exit:** all three workflows green via CLI.

### Phase 4 — Agent orchestration (LangGraph) + continuity
`OrchestratorPort` + stdlib runner first, then the LangGraph adapter (§20): bounded steps via `recursion_limit`, checkpointer with `durability="sync"`, `interrupt()`/`Command(resume=...)` for human approval, allow-listed read tools, kill switch, rollback; InferencePort stub; **parity suite** stdlib ↔ LangGraph; trajectory graders; `ai_disabled` exercised in CI; outage/recovery suites (INJ-069/079/080/082).
**Exit:** both runners produce byte-identical schema-valid packs; interrupt/resume and checkpoint-freshness tests pass; continuity threshold met.

### Phase 5 — Human-review console
`apps/web` Jinja templates + vendored HTMX, served by `python -m aegis serve`. Assessment uses the stdlib HTTP server; FastAPI is optional (`requirements-ui.txt`). Four core screens first (`/workflows/batch|pv|supply`, `/evidence/{id}`); secondary `/`, `/gates`, `/injects`. Forced acknowledgement is enforced by what the server renders and re-checked on POST. Graph/ontology explorers remain later. CLI parity retained: every pack the console shows is obtainable from `python -m aegis run`.
**Exit (this sitting):** live HTMX console on the four core screens; acknowledge gate holds on direct HTTP; assessment tests remain zero-install. Playwright/axe remain optional (NFR-14 still asserted by markup tests).

### Phase 6 — Evaluation, performance and FinOps
`evals/` datasets, graders, runner and thresholds (§25); adversarial corpus (closes R-2201) and subgroup suite; trajectory evals; human-review panel executed once against the rubric (closes R-2202); `CachePort` with memo/file tiers plus the Redis adapter and the non-cacheable registry (§24.2); token/step/wallet budgets and the **cost-per-successful-task calculator** (§24.4, closes PUB-14 / R-2301).
**Exit:** PUB-14 reports a real number; cache-parity and DoW thresholds green; adversarial and subgroup thresholds met.

### Phase 7 — Inject fan-out, compliance and evidence
Remaining `TC-INJ-###` across D01/D02/D03/D07/D09/D12/D13 including `T-ARTEFACT` doc-lints; `compliance/control-map.csv` completed with `T-GOV` tripwires (§23.3); regression suite; SLO/observability/backup/retirement (§13); quality gates with §9.5 thresholds; `STRUCTURE_MANIFEST.json`; bridge export B-1…B-6.
**Exit:** zero `NOT_RUN`; thresholds met; every compliance obligation resolves to a passing test; `check_submission_structure.py --final` passes with the snapshot.

### Phase 8 — Defence
Scripted happy / edge / attack / outage / recovery / manual demos; claim–argument–evidence narrative; residual risks; go / conditional-go / pivot / pause / stop recommendation.

---

## 17. Per-sitting ritual

1. One task; work in the new repo (bridge exports excepted).
2. Map evidence authority → write failing tests → implement → review output against the contract.
3. Run targeted tests, then the suite.
4. Update the inject coverage row, the traceability matrix and — where a compliance obligation moved — `compliance/control-map.csv`. The AI-change record is written automatically by the session hooks (§22.4); review it rather than compose it.
5. Stop.

---

## 18. Success criteria

| Criterion | Measure |
|---|---|
| Separation | Product code only in `aegis-sdd`; challenge hashes unchanged |
| Zero-install core | `assessment` runs on stdlib alone; static-analysis gate enforces it |
| KG governance | ADR-007 supersedes D-205 with T1–T5 parity evidence |
| Ontology honesty | Zero silent unit/terminology/identity merges |
| Graph safety | Forbidden edges unwritable; provenance on 100% of nodes/edges |
| Three workflows | PUB fixtures → schema-valid packs; prohibitions fail closed |
| All 84 injects | No `NOT_RUN`; no hard gate deferred |
| UI | Consumes packs only; a11y, forced-ack and RTL pass; CLI parity |
| Thresholds | §9.5 gates measured and enforced |
| DoD coverage | GxP boundary, brownfield/rollback/decommissioning, ops/SLO, traceability, risk all documented |
| Agentic framework | LangGraph runs the workflows in `ui`/`cloud` with byte-parity to the stdlib runner; zero installs still required for assessment |
| Tool protocol | MCP used at build time and (optionally) at runtime, read-only, allow-listed, hash-pinned; a poisoned manifest is provably rejected |
| Dev-time governance | Cursor hooks generate an AI-change record per session; hooks are documented as dev controls only |
| Compliance | Every EU AI Act and ISO 42001 obligation in `control-map.csv` resolves to a passing test; all artefact-19 §7 change triggers have live tripwires |
| Performance & cost | Cache-parity holds, p95 within SLO, per-request and wallet budgets enforced, cost per successful task published (PUB-14 no longer `not_implemented`) |
| Evaluation | Deterministic gates only; adversarial and subgroup corpora exist and pass; judge scores recorded but non-gating |
| FDE bridge | Artefacts reconciled, manifest hashed, `--final` passes |

---

## 19. Open decisions (defaults apply if silent)

| # | Decision | Default |
|---|---|---|
| 1 | Repo name/location | `d:\Capstone\PharmaRepo-Agentic\aegis-sdd` |
| 2 | Graph implementation | **Plain-Python property graph** rebuilt per run (`networkx` only behind `GraphPort`) |
| 2a | Graph **storage** | **No database.** Cosmos DB for Gremlin is an optional `cloud`-mode adapter, never required for a graded result (§33) |
| 2b | Agent count | **Six runtime agent roles** (§32). A seventh requires an ADR |
| 3 | Ontology formalism | Versioned vocab + shape validation; no OWL reasoner |
| 4 | API framework | **FastAPI** on CPython 3.11–3.13, in `advisory`/`ui`/`cloud`. Never required to produce a pack — the CLI does that with stdlib alone |
| 5 | Bridge cadence | Snapshot + artefact reconciliation at each defence tag |
| 6 | Agent framework | **LangGraph** in `ui`/`cloud`; stdlib runner in `assessment` |
| 7 | LangGraph checkpointer | `SqliteSaver` locally (file, offline); Redis checkpointer only in `cloud`; **references only, no PHI** (§20.4) |
| 8 | Cache backend | In-process memo (assessment) → file cache (ui) → Redis (cloud). Redis is never required to produce a pack |
| 9 | Runtime MCP exposure | **Off by default.** Read-only client in `ui`/`cloud`; the AEGIS MCP *server* is a demo-only, read-only surface |
| 10 | LLM-as-judge | Enabled for reporting, **never** wired to a release gate |
| 11 | Compliance posture | Retain artefact 19's advisory / non-high-risk claim, now defended by tripwires rather than prose |
| 12 | **Model provider** | **Azure OpenAI**, narrative only, behind `InferencePort` and the kill switch (§34) |
| 13 | **Azure authentication** | **Entra ID managed identity** via `DefaultAzureCredential`. Key auth only for local development, from a secret store |
| 14 | **Model version** | Pinned explicitly; floating aliases are forbidden. Version recorded in every evidence record |
| 15 | **Abuse-monitoring retention** | Either the Limited Access exemption is held, or only pseudonymised content is sent. Decision recorded in `compliance/eu-ai-act/` and re-checked at deployment |
| 16 | **LLM reproducibility** | Record-and-replay cassettes keyed by prompt hash. Live calls only in `advisory`; tests and evals always replay |
| 17 | **Evidence store** | Append-only, content-addressed, hash-chained files (§35). Azure Blob with an immutability policy in `cloud`. No database is ever the system of record |
| 18 | **Prompt-log retention** | 90 days, per `data/retention_rules.csv`, unless an evidence or legal hold applies |

---

## 20. Agent orchestration — LangGraph (BS-24, BS-25)

### 20.1 Why a port, and why LangGraph sits behind it

The assessed path must install nothing and run offline; LangGraph is a third-party package. Both statements can hold only if the framework is an **adapter**, not the architecture.

```
packages/orchestrator/port.py        OrchestratorPort  (stdlib)
packages/orchestrator/deterministic.py  stdlib runner — the assessed path, authoritative
services/integration/langgraph/      LangGraphOrchestrator — ui/cloud
```

`OrchestratorPort.run(request) -> Pack` is the whole contract. The deterministic runner executes the same node sequence as a plain function pipeline. **Neither runner contains domain logic** — nodes call `packages/domain` engines, which remain the source of truth (§1, decision 2).

ADR-008 records this choice and its rejected alternatives (framework in the core; hand-rolled agent loop everywhere; CrewAI/AutoGen).

### 20.2 Graph topology

Identical in both runners; LangGraph expresses it as a `StateGraph`:

| Node | Agent (§32) | Responsibility | Deterministic? |
|---|---|---|---|
| `admit` | kernel, **not an agent** | AuthZ re-check, purpose, budget admission, idempotency key | Yes |
| `plan` | AG-1 Supervisor | Select workflow A/B/C and the bounded step list | Yes |
| `retrieve` | AG-2 Evidence retrieval | Read-only source adapters, trust tagging | Yes (cacheable) |
| `project_graph` | AG-2 Evidence retrieval | Bounded KG projection with provenance | Yes (cacheable) |
| `reconcile` | AG-3 / AG-4 / AG-5 | Engine A/B/C — contradictions, gaps, abstentions | Yes (cacheable) |
| `annotate` | AG-3 / AG-4 / AG-5 | Optional inference, annotations only, kill-switchable | No — off by default |
| `approve` | AG-1 Supervisor | `interrupt()` for human acknowledgement / approval path | Human |
| `package` | AG-6 Review packager | Human-review pack assembly, evidence hashing | Yes |
| `validate_emit` | kernel, **not an agent** | Contract validation, audit append, FinOps record | Yes |

State is a `TypedDict` of **references** (record ids, hashes, decisions) — see §20.4.

### 20.3 Human-in-the-loop is a first-class graph primitive

LangGraph's `interrupt()` pauses the graph at `approve` and surfaces a payload; the run resumes with `Command(resume={...})` on the same `thread_id`. This gives the plan's human-review requirements a real mechanism instead of a UI convention:

| Requirement | Mechanism |
|---|---|
| Forced evidence acknowledgement before "ready for review" (INJ-071) | `approve` interrupt cannot be bypassed; resume payload carries reviewer id, role and the acknowledged evidence ids |
| Supply allocation stays a human decision (INJ-056) | Approval path is an interrupt; the graph has **no** node that allocates |
| Contested batch evidence (INJ-021/028) | Interrupt payload lists contradictions and gaps verbatim |
| Checkpoint-corruption re-confirmation (INJ-080) | Stale or hash-mismatched checkpoint forces a fresh interrupt, never a silent resume |

Resume events are audit records, **not** electronic signatures (§11 stands unchanged).

### 20.4 Checkpoints — durability, freshness and data policy

Checkpointing is what makes the agent resumable, and it is also a new data store. Both facts are governed:

| Control | Rule |
|---|---|
| Durability | `durability="sync"` — state persisted before each step, so a crash cannot lose or duplicate a step. Performance cost accepted; this is a regulated workflow |
| Backend | `SqliteSaver` on local disk (`ui`, offline-safe); Redis checkpointer only in `cloud` |
| **No PHI in state** | Checkpoint state holds record ids, hashes, ontology decisions and budget counters — never PV narrative text or patient attributes. A privacy test scans persisted state against a personal-data pattern set and fails the build on a hit (INJ-060/062) |
| Residency | Checkpoint store region is pinned and asserted at startup; a mismatch fails closed (INJ-064) |
| Retention | TTL bounded and documented; a DSR restriction marks the thread non-resumable rather than deleting a GxP-relevant trace (INJ-061) |
| Freshness | `thread_id` bound to the idempotency key; checkpoint age and hash validated before resume; stale or tampered → human confirm (INJ-080) |
| Replay | Resuming a completed thread returns the original pack; it never re-executes side effects (there are none by design) |

### 20.5 Bounded execution

`recursion_limit` caps graph steps per run; the kernel's own step, token and wallet budgets sit above it (§24.3) so a limit cannot be raised in config without failing the budget test. Tool access is an allow-list of read-only tools resolved through the trust gate (§21.3). Excessive agency, unbounded loops and denial-of-wallet (INJ-076) are therefore bounded in two independent places.

### 20.6 Parity is the safety property

The LangGraph adapter earns its place only by proving it changes nothing:

- `tests/orchestration/test_parity.py` runs PUB-01…15 through both runners and asserts **byte-identical** packs after normalising `request_id` and timestamps.
- Any divergence is a defect in the adapter, never a reason to update the expected pack (R-09).
- CI runs the deterministic runner on every commit and the parity suite whenever `requirements-agent.txt` or the adapter changes.

### 20.7 Injects this addresses

INJ-056 (approval path), 065/066 (tool boundary at the graph edge), 067 (admit-node re-check), 069/079/082 (runner swap = continuity), 071 (forced acknowledgement), 076 (step/token bounds), 080 (checkpoint freshness, idempotent replay), 081 (trajectory regression on model swap).

---

## 21. MCP — Model Context Protocol (BS-26)

### 21.1 Two uses, deliberately kept apart

| Use | Where | Status |
|---|---|---|
| **Build-time**: Cursor talks to MCP servers (documentation, data inspection) to accelerate development | Developer IDE, `.cursor/mcp.json` | Encouraged; produces no product behaviour |
| **Runtime**: AEGIS consumes external tools over MCP, and optionally exposes its own read-only tools | `services/integration/mcp/`, `ui`/`cloud` only | Off by default; behind the trust gate |

Conflating them is how a convenience becomes an attack path, so the assurance case states the split explicitly.

### 21.2 Build-time configuration

`.cursor/mcp.json` declares the servers used while building (documentation lookup for LangGraph, FastAPI and HTMX, read-only inspection of local synthetic data). Rules: no server may hold credentials to a real system; no server writes to the challenge package; MCP calls made during a build session are logged by the `beforeMCPExecution` hook into the AI-change record (§22.2). ADR-010 records the server list and its justification.

### 21.3 Runtime MCP is exactly the INJ-066 threat surface

An MCP server supplies tool **names, descriptions, input schemas and results** — all attacker-influenced text that reaches the model. The challenge already models this as tool-manifest poisoning (INJ-066) and prompt injection (INJ-065). Runtime MCP therefore passes the same gate as any other tool:

| Control | Rule |
|---|---|
| Registration | A server and its tools must appear in the approved catalog with a **signed manifest and pinned hash**; unsigned or drifted → denied, run continues without that tool |
| Capability class | **Read-only tools only.** Any tool whose schema implies a write, disposition, allocation, submission or deletion is rejected at registration, not at call time |
| Descriptions are data | Tool descriptions and results are wrapped as untrusted content and can never become instructions — the same rule as an untrusted document node (§5.4) |
| Result handling | Results are evidence candidates requiring source, authority, effective time and hash; unattributable results are dropped, not summarised |
| Authorisation | Every call re-checks user, purpose and entitlement at execution time; no cached decision (INJ-067) |
| Budget | MCP calls consume the same step/token budget; a chatty server hits the DoW stop (INJ-076) |
| Egress | Server allow-list; no arbitrary URLs; denied entirely in `assessment`/`ai_disabled` |
| Failure | Fail closed and abstain — degrade the answer, never the guarantees |

`tests/security/test_mcp_trust.py` asserts each row, including a deliberately poisoned manifest and a tool description carrying an injected instruction.

### 21.4 Optional AEGIS MCP server

A demo-only server exposing `get_evidence_pack`, `get_evidence_item`, `explain_abstention`, `get_inject_coverage` — read-only, entitlement-checked, no mutating verbs. It exists to show interoperability; nothing in scoring depends on it, and it is disabled in `assessment`.

---

## 22. Cursor hooks and AI-assisted change control (BS-27)

### 22.1 Boundary statement — read this before citing a hook as a control

Cursor hooks execute in the **developer's IDE around agent events**. They are software-development controls. They are **not** product runtime controls, they are absent in production, and the assurance case must never present a hook as the reason a regulated action is denied — `policy_guard` and the kernel gates do that. What hooks legitimately provide is **evidence that the AI-assisted build itself was governed**, which is precisely what ISO 42001 lifecycle control and EU AI Act record-keeping ask for.

### 22.2 Hook set (project hooks in `.cursor/hooks.json`)

| Event | Purpose | Fail mode |
|---|---|---|
| `sessionStart` | Open an AI-change record: session id, model, branch, runtime mode | Fail open |
| `beforeSubmitPrompt` | Scan the prompt for secrets, credentials and personal-data patterns before it leaves the machine | **`failClosed: true`** |
| `beforeReadFile` | Block reads of `.env`, `security/secrets/`, any real credential path | **`failClosed: true`** |
| `afterFileEdit` | Enforce the core import ban (§4 rule 5), regulated-schema shape, and formatting on the edited file | **`failClosed: true`** |
| `beforeShellExecution` | Deny writes into the challenge package, deny network commands while in `assessment`, deny destructive git operations | **`failClosed: true`** |
| `beforeMCPExecution` | Allow-list MCP servers and log every call with arguments hash | **`failClosed: true`** |
| `postToolUse` | Append tool usage to the session record | Fail open |
| `stop` | Finalise the AI-change record and remind that the coverage row and traceability matrix need updating | Fail open |

Guardrails that must hold regardless of the IDE are duplicated as CI checks — the hook gives fast feedback, CI gives the guarantee.

### 22.3 Implementation notes

- Hook scripts are **Python** (`python .cursor/hooks/<name>.py`), not bash, because the team develops on Windows and `jq`/bash cannot be assumed. Python is already a hard prerequisite of this project.
- Contract: read JSON on stdin, emit only the fields the event supports (`permission`, `user_message`, `agent_message`, `updated_input`, `additional_context`), exit `0` to allow, exit `2` to block.
- Safety-critical hooks set `failClosed: true` so a crashed hook blocks rather than silently permits — the same deny-by-default posture as the product.
- Each hook has a unit test with a recorded stdin payload, so hook logic is testable rather than folklore.

### 22.4 Evidence output

Every session writes `evidence/ai-assisted-changes/<date>-<session>.json`: prompts (redacted), model identity, files touched, tools and MCP servers invoked, hook denials, tests run and the resulting commit. This is the artefact the ISO 42001 lifecycle table (§23.4) and the change-control authority K-005 expect, produced automatically instead of remembered.

---

## 23. EU AI Act and ISO/IEC 42001 as executable controls (BS-31)

### 23.1 Inherited position — do not re-litigate it

Challenge artefacts 19 and 20 already establish the posture, and this build adopts it unchanged: advisory system, deployer lens, human Decide authority retained, autonomous high-risk decisioning excluded by design, no conformity assessment claimed. v3.2 adds the missing half — **enforcement**. Artefact 19 §7 lists the triggers that invalidate the claim, and until now nothing detected them.

### 23.2 EU AI Act obligation register — `compliance/eu-ai-act/`

| Obligation theme | Implementation in this build | Verified by |
|---|---|---|
| AI literacy / instructions for use | `docs/product/intended-use.md`; UI explains what the system does and does not decide | `T-ARTEFACT` doc-lint |
| Human oversight | `approve` interrupt (§20.3), forced acknowledgement, contestability, kill switch | `T-UX`, `T-TRAJ` |
| Transparency to users | Persistent "AI-assisted, advisory only" notice; annotations labelled as model output and visually separated from evidence | Playwright presence test |
| Record-keeping / logging | Append-only hash-linked audit; every abstention, denial and resume logged | `T-BEHAV` audit assertions |
| Accuracy, robustness, security | Evaluation subsystem (§25) + security suite | §9.5 thresholds |
| Risk management | §14 register + artefacts 16–18 | Review + doc-lint |
| Technical documentation | `docs/architecture`, ADRs, traceability matrix | Traceability validator |
| Data governance | Provenance, authority, effective dating, residency, purpose limitation | `T-ONT`, `T-GATE` |
| Incident handling | `ops/runbooks/incident.md`, kill switch, evidence preservation | `T-RESIL` |

### 23.3 Tripwires — the part that was missing

`compliance/tripwires/` holds executable checks, run by `tests/compliance/` as `T-GOV`, one per artefact-19 §7 change trigger:

| Trigger from artefact 19 §7 | Tripwire |
|---|---|
| A write tool that could set disposition, allocate or finalise PV is introduced | Scan the tool catalog, MCP registrations and API routes for mutating capability; **any hit fails the build** and prints "EU AI Act applicability claim invalidated — re-run artefact 19" |
| Forced human review or contestability removed | Assert the `approve` interrupt exists on every workflow and that the UI acknowledgement gate is present |
| Model substituted without change control | Assert every model id in config resolves to a registry entry with a pinned hash and a recorded eval regression run (INJ-070/081) |
| Deployment outside the analysed jurisdiction | Assert configured region against the residency policy |
| Prohibited-action deny-list weakened | Diff the deny-list against the signed baseline; any shrink fails |
| Grader or threshold silently weakened | Diff `evals/thresholds.yaml` against the baseline; a loosened hard gate requires an approved exception record (artefact 20 §4) |

A compliance claim that no longer holds now breaks the build, which is the only version of compliance that survives a busy sprint.

### 23.4 ISO/IEC 42001 AIMS mapping — `compliance/iso42001/`

| AIMS area | Where it lives in this repo |
|---|---|
| Context, scope, interested parties (cl. 4) | `docs/governance/aims-scope.md`, artefact 19 §1–2 |
| Leadership, AI policy (cl. 5) | `docs/governance/ai-policy.md` — deterministic-first, no transfer of Decide authority |
| Planning, AI risk and impact assessment (cl. 6) | §14 register, artefacts 16–18, inject-driven threat model |
| Support, competence, documented information (cl. 7) | `docs/engineering/`, templates, evidence tree |
| Operation — lifecycle controls (cl. 8) | K-005 change classes: model · prompt · retrieval · schema · tool · evaluator, each with required evidence before release |
| Performance evaluation (cl. 9) | §25 evals, §13 SLOs, §9.5 thresholds |
| Improvement (cl. 10) | Failed gates become fixtures; incident records feed the register |
| Data, system and third-party controls (Annex A themes) | Provenance and ontology rules (§5), tool/model trust (§21.3), SBOM and vendor concentration (§4 rule 6) |

Change-class enforcement is mechanical: a diff touching a prompt, schema, tool manifest, model pin or grader without the corresponding evidence file fails `tests/compliance/test_change_classes.py`.

### 23.5 `compliance/control-map.csv`

Columns: `obligation_id, framework, obligation, control, module, test_id, evidence_path, status`. Validated like the traceability matrix (§10) — an obligation with no test, or a test with no evidence path, fails the build. This is what turns "we considered the EU AI Act and ISO 42001" into something an assessor can execute.

---

## 24. Performance, caching and token economics (BS-28, BS-29)

### 24.1 Performance objectives

| Metric | Target |
|---|---|
| p95 batch pack (assessment fixtures) | < 5 s |
| p95 API response (`ui`) | < 1.5 s cached, < 5 s cold |
| Graph traversal | ≤ 4 hops default, hard cap 6 |
| Cache hit rate on repeat fixture runs | ≥ 80% (reported, not gating) |
| Determinism | 3 consecutive runs byte-identical (§9.5) |

Measured by `tests/performance/`, recorded to `evidence/operations/`. Performance work may never trade away determinism or a gate.

### 24.2 Cache design — and the set that must never be cached

Three tiers behind one `CachePort`: **L0** in-process memoisation of pure functions (stdlib, available in `assessment`), **L1** content-addressed file cache under `out/cache/` (`ui`), **L2** Redis (`cloud` only, adapter in `services/integration/redis/`). LangGraph node-level `CachePolicy(ttl=…)` may be applied to deterministic nodes (`retrieve`, `project_graph`, `reconcile`) and to nothing else.

Cache keys are composite and versioned:

```
sha256(payload_hash | code_version | ontology_version | terminology_version |
       relationship_model_hash | as_of_date | runtime_mode)
```

so a terminology update (MedDRA 27.1 → 28.0) or an ontology change invalidates by construction rather than by remembering to purge.

**Non-cacheable registry — enforced in code, not by convention.** Artefact 23 §4 records that entitlement and consent caches already caused safety and privacy failures here; INJ-067 is that failure. The following may never enter any tier: authorisation and entitlement decisions, consent and purpose checks, residency decisions, DSR/legal-hold state, kill-switch and runtime-mode state, model integrity verdicts, checkpoint freshness verdicts, anything containing personal data. `packages/cache` raises on a key in a protected namespace, and `tests/security/test_cache_boundaries.py` proves it.

Two more rules: superseded or newly effective evidence purges the affected namespace before the next run, and **cache-on must equal cache-off** byte-for-byte (§9.5) — a cache that changes an answer is a defect, not an optimisation.

### 24.3 Token and step budgets

| Layer | Control | Inject |
|---|---|---|
| Per request | `MAX_TOKENS_PER_REQUEST = 50 000` (carried over from the existing gate that denies the 980 000-token SEC-2 loop) | 076 |
| Per run | Max steps, max tool calls, max traversal hops; `recursion_limit` beneath them | 076 |
| **Cumulative wallet** | Daily and monthly token/cost ceilings with soft alert and hard stop — the gap artefact 23 §3 records as missing | 076 |
| Price change | Detect a rate change against the recorded price card and raise a FinOps alert rather than absorbing it silently | 075 |
| Concentration | Report capability-by-vendor concentration in the FinOps record | 078 |

Hitting a budget produces an honest partial pack with an abstention and a budget-stop reason. It never produces a truncated answer presented as complete.

### 24.4 Cost per successful task — closing PUB-14

Artefact 23 §6 defines the formula and artefact 22 records PUB-14 as `not_implemented` with gap R-2301. `packages/finops` implements it:

```
cost_per_successful_task =
    (inference_token_cost + allocated_observability + human_review_loaded_cost)
    / successful_tasks
```

`successful_tasks` is **never** the request count — the artefact-23 baseline is 1110/1900 and 2800/4200, so counting requests would overstate success by roughly 40%. Because `assessment` runs offline with no reviewer, success has two definitions and the record says which one it used (AMB-06):

| Basis | Definition | Used in |
|---|---|---|
| `reviewer_accepted` | Schema-valid pack, `authorization.decision = allow`, accepted by a named reviewer role | `ui` / `cloud`, human-panel runs |
| `offline_proxy` | Schema-valid pack, `authorization.decision = allow`, **zero blocking gaps and zero unresolved hard-gate denials** | `assessment` / `ai_disabled` |

Human review is costed at the loaded staff rates rather than the $0 the cost model carries, and is labelled `modelled` (reviewer minutes × rate) rather than `observed` until a panel has run — so the TCO stops understating itself (R-2302) without pretending to a measurement nobody took. Every graded run emits `evidence/operations/finops/<run_id>.json` including `success_basis`, the human-review cost basis and the avoided-inference count, which in `assessment` is 100% and makes the deterministic path's near-zero inference cost an explicit, defensible result.

### 24.5 Routing

Avoided inference first; then the local small model within its validated scope; the large model only when justified and available. **No silent fallback** to an unverified or unpinned model — a failed integrity check abstains (INJ-070, and the observed primary-endpoint outage in the challenge data).

---

## 25. Evaluation system (BS-30)

### 25.1 Levels

| Level | Suite | Gating |
|---|---|---|
| L0 | Contract / schema conformance | **Gate** |
| L1 | Property graders (§9.2) — conflict preserved, abstention correct, no prohibited field | **Gate** |
| L2 | Scenario evals — PUB-01…15 and the 84 `TC-INJ-###` | **Gate** |
| L3 | Adversarial / red-team corpus | **Gate** |
| L4 | Subgroup and language fidelity | **Gate** |
| L5 | Agent trajectory evals | **Gate** |
| L6 | Regression and model-substitution drift | **Gate** |
| **L6a** | **Advice grounding and output-guard behaviour** (§25.9) | **Gate** |
| L7 | Human-review panel | Reported; blocks the *pilot* claim, not the build |
| L8 | LLM-as-judge on explanation quality | **Never gates** (§25.5) |

`python -m aegis evaluate` runs L0–L6a offline with zero installs; L7 is a scored human exercise; L8 requires `cloud`.

**Evals never call Azure.** L6a replays cassettes (§34.5), so the eval suite is deterministic, free and runnable on a clean machine with no credentials. A live-call suite exists, runs on demand, reports variance and is **never** a gate. An evaluation that needs a network and a bill is an evaluation that quietly stops being run.

### 25.2 Datasets

`evals/datasets/` holds scenario cases (from the hash-verified fixtures), adversarial cases, subgroup slices and frozen regression packs. Each case is a JSON record with `case_id, workflow, inputs, expected_behaviours[], forbidden_behaviours[], inject_ids[], rationale`. Because fixtures ship no answer keys, cases assert **behaviour**, never a golden string.

### 25.3 Adversarial corpus — closes R-2201

At least 30 cases, authored as data, covering: instruction text embedded in SOPs and CoAs (INJ-065); poisoned, unsigned and hash-drifted tool manifests including MCP (INJ-066); revoked-entitlement replay (INJ-067); exfiltration attempts via traversal, citation text and error messages (INJ-068); unpinned model substitution (INJ-070); token floods (INJ-076); contradictory-authority documents designed to trigger a premature resolution; and unit/terminology traps designed to elicit a silent conversion (INJ-024/039). Threshold: **zero successful injections, zero poisoned-tool executions**, and every case must produce either a correct refusal or an abstention with a reason.

### 25.4 Trajectory evals (`T-TRAJ`)

Output-only grading cannot see an agent that reached a right answer through an illegal path. Over the LangGraph run log:

| Metric | Threshold |
|---|---|
| Illegal tool calls (not allow-listed, or write-capable) | 0 |
| Steps per workflow | ≤ configured limit; median tracked for drift |
| Required approval interrupts raised | 100% |
| Resume without a valid reviewer identity | 0 |
| Budget adherence | 100% |
| Redundant retrieval rate | Reported (cost signal) |
| Path determinism | Same input → same node sequence |

### 25.5 LLM-as-judge policy

A judge may score explanation clarity and citation helpfulness, and its scores are published. It may **not** decide pass/fail for any gate, and a test over `evals/thresholds.yaml` asserts no gate references a judge metric. Rationale: a non-deterministic grader on a regulated release gate would be unvalidatable and would break the offline reproducibility the whole plan rests on.

### 25.6 Human-review panel — closes R-2202

Artefact 22 §4 defines the rubric but never scored it. One scored session per defence tag: reviewers in role (QP, safety physician, supply governance) work real packs; measured on evidence completeness surfaced, contradictions noticed, prohibited language spotted, abstention clarity, and time to decision. Results, including disagreements, go to `evals/human-panel/`. A rubric that has never been run against a human is an assumption, not evidence.

### 25.7 Regression and drift

Every graded pack is frozen into `evals/datasets/regression/`. Any change to a model, prompt, schema, tool, grader or the orchestrator re-runs the frozen set. A new `fail`, or a silent `not_implemented → pass` conversion, blocks the merge — the rule artefact 22 §7 already states, now enforced. Model substitution additionally requires L4 subgroup re-run and L5 trajectory comparison (INJ-081).

### 25.8 Advice evaluation — L6a (added with §34)

The other levels evaluate what the system *computes*. L6a evaluates what it *says*, and it is deterministic because the guard is deterministic — no judge is involved in any threshold here.

| Metric | Threshold | Why it gates |
|---|---|---|
| Regulated-field isolation — advisory pack equals offline pack minus annotations | **15/15 fixtures byte-identical** | If this ever fails, generated text has reached a regulated field and every other guarantee collapses |
| Numeric groundedness — every number, date and identifier present verbatim in the pack | **0 unsupported** | The dominant hallucination mode in this domain |
| Citation closure — every reference resolves in the pack | **0 unresolvable** | Invented sources are worse than no sources |
| Prohibited language in generated text | **0** | The deny-list applies to prose exactly as to fields |
| Abstention preservation — advice never narrates past an abstention | **0 violations** | Confidence the evidence does not support |
| Guard rejection rate | Reported, with reasons by check | A rising rate is an early signal of prompt or model drift |
| Refusal quality — where the pack abstains, the advice says so plainly | Reported | Measures whether abstention is *communicated*, not just emitted |
| Advice replay determinism | **3 runs byte-identical** | Makes the whole level reproducible |

Guard rejection rate and refusal quality are reported rather than gated on purpose: a rejection is the guard doing its job, so gating on a low rate would create pressure to weaken the guard.

A prompt-template change re-runs L6a and L6 (§25.7). Prompts are versioned artefacts, so a prompt edit is a change with an evaluation, not a text tweak.

### 25.9 Outputs

`evidence/evaluation/` receives `results.json` (per case: id, input hash, result, gate outcome, reviewer role, evidence path), `scorecard.md` in the artefact-22 format so the challenge scorecard can be regenerated rather than retyped, `trajectories/`, and `thresholds_applied.json` recording which gate versions ran. The bridge (§3.3 B-3) pushes the refreshed scorecard back into the challenge package.

---

## 26. Ownership and per-phase accountability

The challenge artefacts already assign six roles; the build plan never used them, so phases had no owner and change classes had no named approver. Individual names remain pending (A-001 in the business case) — the **roles** are binding regardless.

| Role | Owns | Approves (per artefact 20 §4 change classes) |
|---|---|---|
| Product / value lead | §30.4 cut line, scope, UI priorities | Prompt changes |
| GxP / quality lead | §11 records boundary, workflow A acceptance, EU AI Act posture | Model, retrieval, evaluator changes |
| Security / privacy lead | §21 trust gates, §24.2 cache boundaries, threat models | Tool and prompt changes |
| Architecture / integration lead | §20 orchestration, §4 dependency policy, ADRs | Model, schema, tool changes |
| Evaluation / reliability lead | §25 evals, §9.5 thresholds, §13 SLOs | Schema and evaluator changes |
| Domain lead | §5 ontology and graph, §29 matching rules | Retrieval corpus changes |

Two approvers are required for anything touching a hard gate, and the evaluator class requires GxP co-approval so thresholds cannot be weakened by the person whose work they gate.

### 26.1 These are not the product's roles (BS-45)

Three populations carry the word "role" in this build and conflating any two of them is a governance failure, so the counts are stated together and kept disjoint by construction.

| Population | Count | Defined in | Holds runtime entitlement |
|---|---|---|---|
| **Runtime roles** — who the product serves | **7** | `01_specs/registers/roles_and_entitlements.md` | Yes — visibility and interrupts |
| **Accountability roles** — who owns the build | **6** | The table above | **No** |
| **Build-time Cursor agents** | **3** | §32.4 | **No** |

The seven runtime roles are the five in `01_specs/product/scope.md` §6 plus `auditor` and `unblinding_authority`, both of which the feature specs already required — FR-008 §1 and FR-014 name an auditor, BR-138 routes potential-unblinding findings to an unblinding authority — while neither was declared anywhere. Declaring them is not an addition of scope; it is writing down what the specs were already assuming.

The register also closes a gap of the same class as the inject gap. FR-005 step 4 and BR-046 require sensitive segments to be gated by role, but the package supplies only segment → access group (`sensitive_segments.csv`) and user → role (`users_entitlements.csv`). The **role → access group edge does not exist in the data**, so the gate had no table behind it and could not have been implemented as specified. It is now a declared Unknown, AMB-15, with a deny-by-default matrix owned by the security/privacy lead — not an invented mapping presented as policy.

**No role is an administrator.** There is no entitlement level at which the FR-005 gates stop applying, because a role that could disable them would be the single change most capable of invalidating the EU AI Act applicability claim (§23.3).

**Timeboxing.** Each phase carries a declared timebox and a review at its exit criteria. If a phase overruns its box by more than half, the §30.4 drop order is applied at that review rather than at the end — the point of a cut line is that it is used early enough to matter.

---

## 27. Ambiguity closure register (BS-33…BS-38)

Each entry is closed with a decision, not deferred. Anything genuinely unresolvable is recorded as a declared Unknown with an owner in `01_specs/registers/spec_ambiguities.md`.

| ID | Ambiguity | Decision | Rationale | Verified by |
|---|---|---|---|---|
| **AMB-01** | 7 fixtures require `advisory_nonexecuting`; no such schema ships | Author `packages/contracts/internal/advisory_nonexecuting.schema.json` from the **invariant core the three regulated schemas share** — `request_id, workflow, as_of, authorization{user,purpose,checked_at,decision}, evidence[], contradictions[], gaps[], abstentions[], human_review, execution_status="not_executed", audit` — plus `scenario_id`, a closed workflow enum **derived from the feature set**, `findings[]`, `gate_outcome`, optional `metrics`. `additionalProperties: false`. Marked **team-authored, not challenge-authoritative**; it may add obligations, never relax one. The enum holds **eight** values: the seven fixture scenarios plus `regulatory`, which FR-012 needs and no fixture supplies (§36.5) | The four challenge schemas cannot cover security/reliability/privacy/integration/agent/finops/clinical/regulatory scenarios, and inventing an open object would forfeit closed-schema safety | `tests/contract/test_advisory_contract.py` — all 7 fixtures validate; `tests/contract/test_contract_representability.py` — every feature declaring the contract has an enum value; prohibited-field deny-list applies identically |
| **AMB-02** | What exactly does `integrity.sha256` hash? | The **source artefact hash as published by the package** — the fixture's `evidence[].sha256`, cross-checked against `FILE_HASHES.csv`. Never a recomputed digest of a transformed row. `record_id` locates the row inside that artefact; `audit.hash_scope` records `source_artifact` | A per-row hash is unverifiable against anything in the package, so it would look rigorous and prove nothing | Contract test + a negative test asserting a recomputed hash is rejected |
| **AMB-03** | Where do `retrieved_at` and `checked_at` come from? | From `authorized_context.as_of`, never the wall clock. `request_id` = `"REQ-" + sha256(scenario_id · as_of · input_hash · code_version)[:16]` | `evidence_item.retrieved_at` is required; sampling the clock makes byte-identical runs impossible, which would sink the headline reproducibility claim | Determinism test with no exclusions |
| **AMB-04** | Serialisation and ordering unspecified | §28 | Two implementers would otherwise produce different bytes from identical logic | `tests/unit/test_canonical_json.py` |
| **AMB-05** | Confidence-gated matching had policy but no numbers | §29 | `spec-driven-delivery` forbids "validate confidence" without a number or a declared Unknown | Per-rule unit tests with boundary cases |
| **AMB-06** | Cost per successful task undefined offline | Two named bases, `reviewer_accepted` and `offline_proxy`, recorded in the FinOps artefact (§24.4) | Assessment has no reviewer, so the graded mode had no definition of the metric it must report | PUB-14 emits a value with `success_basis` |
| **AMB-07** | Parity scope vs inference | Parity claimed with inference **disabled**; with inference on, everything except `human_review.annotations` (§9.5) | A sampling model can never be byte-reproducible; the claim needed a boundary | Parity suite in both configurations |
| **AMB-08** | Interpreter unpinned | CPython ≥ 3.11, < 3.14 (§4 rule 4a) | Determinism and stdlib behaviour are version-bound | `python -m aegis setup` refuses outside the range |
| **AMB-09** | Fixture copy set hand-listed | Derived from fixture `evidence_references` and re-derived in CI (§3.2) | A missed CSV surfaces as a mid-implementation failure instead of a build failure | Copy-set diff check |
| **AMB-10** | No delivery cut line | Minimum defensible submission and drop order (§30.4) | Without it, time pressure cuts scoreable work first | Phase review checklist |

---

## 28. Determinism and canonicalisation rules (BS-34)

"Three consecutive runs byte-identical" is only achievable if these rules are implemented from the first commit; retrofitting them is expensive.

| Rule | Requirement |
|---|---|
| Canonical JSON | `json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`, UTF-8, LF line endings, single trailing newline |
| Array ordering | Every emitted array has a declared sort key with an explicit tiebreaker — `evidence` by `(source, record_id)`; `contradictions` by `(topic, source, record_id)`; `gaps` by `(gap_type, subject_id)`; `abstentions` by `(reason_code, subject_id)`. No array may depend on input file order |
| No set iteration | Sets may be used internally but never iterated into output; convert with an explicit `sorted()` |
| Generated timestamps | Derived from `as_of` (AMB-03), formatted ISO-8601 UTC with `Z` |
| **Source timestamps** | Reproduced **verbatim**, preserving the source's precision and timezone marking. Never reformatted, never widened, never silently converted — a missing timezone stays missing and drives `timezone_unknown` (INJ-018) |
| Numbers | Money and measured quantities are strings with the source's scale; binary floats are banned in packs. Ratios computed for FinOps use `decimal.Decimal` with a declared rounding mode |
| Identifiers | Derived by hash from content (AMB-03). `uuid4`, `random` and `time.time()` are banned in `packages/` and blocked by the static-analysis gate |
| Hashing | SHA-256 over raw bytes as read; no normalisation before hashing |
| Locale and environment | No dependence on `LANG`, `TZ`, filesystem ordering or `PYTHONHASHSEED`; CI runs one job with a deliberately hostile locale and timezone to prove it |
| Audit block | The in-pack `audit` object is deterministic (derived ids, content hashes, counts). Wall-clock run telemetry lives in `evidence/operations/`, outside the pack |

---

## 29. Matching, linkage and confidence thresholds (BS-35)

The system proposes; a human disposes. That policy is unchanged — what follows is the missing specification of *how* candidates are proposed, with the strategy order fixed and every threshold either numeric or a declared Unknown.

### 29.1 Identity resolution — deterministic tiers, no fuzzy matching

| Tier | Rule | Verdict |
|---|---|---|
| 1 | Same identifier scheme, same value, same org namespace | `SAME` |
| 2 | Linked by a mapping record with `status = approved` and effective at `as_of` | `SAME_BY_MAPPING` — must cite `mapping_id` |
| 3 | Connected by a declared edge in `RELATIONSHIP_MODEL.csv` | `RELATED` — never `SAME` |
| 4 | String similarity | **Not used for identity at all.** Similarity may only propose a review candidate |

A mapping whose status is `proposed`, `draft` or `superseded` yields `IdentityConflict` plus an abstention, never an equivalence (INJ-045). Identical local codes under different org prefixes are distinct by construction (INJ-005/008).

### 29.2 ICSR duplicate candidates (INJ-037)

Strategy order is fixed: exact worldwide-unique-id → composite key match → nothing else.

Composite key fields: patient identifier or initials · date of birth, or age bucket where DOB is absent · sex · suspect product · reaction preferred term · onset date within a **±7-day** window. Score is the **count of matching fields out of six** — not a probability.

| Score | Behaviour |
|---|---|
| 6, or exact worldwide-unique-id match | `duplicate_candidate_high` |
| 4–5 | `duplicate_candidate` |
| 3 | `duplicate_candidate_weak`, surfaced only with the matched fields listed |
| ≤ 2 | Not surfaced |

No score merges anything, at any threshold. Every candidate carries the matched and mismatched fields so a reviewer can disagree. **The ±7 days and the 4/3 cut points are team-set POC defaults, not validated PV business rules** — recorded as a declared Unknown owned by the safety physician role in `spec_ambiguities.md`.

### 29.3 Cross-domain linkage — complaint ↔ batch ↔ ICSR (INJ-043)

Link only on a shared batch or lot identifier, or a Tier-2 approved mapping, with events within a **±30-day** default window. Anything weaker emits an abstention with reason code `unconfirmed_link` — reusing the vocabulary the existing scorecard already applies to PUB-11 — rather than a speculative association. Window and reason code are configuration, surfaced in the pack.

### 29.4 Recall scope and bounded traversal (INJ-058)

Breadth-first from the seed, default depth 4 and hard cap 6. When the frontier is truncated the pack sets `traversal_incomplete: true`, lists the unexplored frontier node ids and raises an abstention. Completeness of recall scope is **never** asserted.

### 29.5 Where a number is deliberately absent

Unit comparison (INJ-024), terminology equivalence across MedDRA versions (INJ-039) and expectedness (INJ-040) have **no threshold by design**: either an approved mapping applies or the system abstains. A tolerance here would be a silent conversion, which the ontology rules prohibit outright.

### 29.6 Checklist compliance

`01_specs/registers/matching_confidence_checklist.md` records, per confidence-gated feature: strategy priority order, numeric thresholds or declared Unknown with owner, rejection behaviour below threshold, and dedup/quantity rules — the four items the method requires.

---

## 30. Specification layer, review gates and delivery cut line (BS-32, BS-36, BS-37, BS-38)

### 30.1 This plan stops being the build input

From v3.3 the plan is the **index and the rationale**. Implementation reads specs. Layout, authored under `submission/AgenticApp/` now and migrated to `{NEW_REPO}/docs/` and `{NEW_REPO}/specs/` at Phase 0:

```
submission/AgenticApp/
├── 00_plan/MASTER_BUILD_PLAN.md      ← this document (index, decisions, rationale)
├── 01_specs/
│   ├── README.md                     ← spec ID scheme, layer rules, review gates
│   ├── product/scope.md              ← problem, in/out of scope, AP-1…AP-n principles
│   ├── features/FEATURE_INDEX.md     ← FR register with status
│   ├── features/FR-0NN_*.md          ← one feature per file
│   ├── api/api_contracts.md          ← contract rules, error envelope, module rules
│   ├── api/advisory_nonexecuting.schema.json
│   ├── data/data_model.md            ← ontology entities, graph node/edge types
│   ├── registers/business_rules_register.md
│   ├── registers/acceptance_criteria_register.md
│   ├── registers/spec_ambiguities.md
│   ├── registers/matching_confidence_checklist.md
│   └── testing/ac_test_plan.md       ← AC → test task → type → status
└── 02_tasks/
    ├── task_index.md
    └── task-0NN_*.md                 ← Goal · Specs to load · Out of scope · Steps · Acceptance checks · Done when
```

### 30.2 ID scheme and the traceability chain

`AP-n` architecture principle · `FR-0NN` feature · `BR-0NN` business rule · `AC-FR0NN-NN` acceptance criterion · `TASK-0NN` · `TC-INJ-###` inject test · `AMB-NN` ambiguity · `REQ-*` the §10 requirement classes.

The chain that must hold end to end: **AP → FR → BR → AC → TASK → test → evidence path**. The §10 validator is extended to audit orphans in both directions and to flag the classes the method calls out: a feature with no AC, a business rule with no verifying AC or threshold, an AC with no test task, a matching rule with no number or declared Unknown, an error or security rule with no AC. No unmarked orphans — each is fixed now, assumed with a revisit date, or open-blocked.

### 30.3 Review gates

| Gate | Rule |
|---|---|
| Spec quality review | Second pair of eyes per feature spec against the checklist in `01_specs/README.md` |
| Architecture review | Must be `pass` or `conditional` before API contracts and the data model lock. ADR-007…010 are inputs |
| Structural reopen | Must be `cleared` before tasks are cut. A task written while an ambiguity affecting it is open is marked `blocked` and not started |
| Drift | Architecture drift produces an ADR and, if material, a reopen — never a silent merge |
| PoC vs production | Every component is labelled in `poc_vs_production.md`. The existing `submission/src/*.py` stubs are labelled **throwaway scaffolding** and are not migrated |

### 30.4 Minimum defensible submission and drop order

If time collapses, this is what must exist to defend the work — and the order in which everything else is dropped.

**Must ship (the cut line):** hash-verified fixtures and copy manifest · kernel with authZ, canonical serialisation and real evidence hashing · the four challenge contracts plus `advisory_nonexecuting` · Workflow A end to end on PUB-01/02/03 · every D10 hard gate at 100% · `ai_disabled` continuity · the six CLI commands · evidence export with honest coverage including `DEFERRED(reason)` · the bridge back to the challenge package.

**Drop order when time runs short:** L8 judge evals → Redis and the `cloud` mode → runtime MCP → the graph and ontology explorer screens → the LangGraph adapter (the stdlib runner is authoritative, so this costs nothing scoreable) → the console beyond the three workflow screens → the KG projection itself, falling back to the relational register under R-01.

Nothing in that list is a hard gate, a contract, a workflow engine or an evidence guarantee — those are never dropped. A partial submission that is honest about `DEFERRED` scores; a broad one that quietly fails a hard gate does not.

### 30.5 The six-stage spec-first lifecycle (BS-39)

Structure alone is not spec-driven development. Every capability moves through six stages, each with a named output and an exit gate. A stage may not be skipped, and work does not start in a later stage while an earlier gate is red.

| # | Stage | What happens here | Output | Exit gate |
|---|---|---|---|---|
| **1** | **Define the spec** | Capture the requirement, constraints, business rules and acceptance criteria in a testable form | `01_specs/features/FR-0NN` at **v1.0**, plus rows in the BR and AC registers | Spec quality checklist passes; every threshold is numeric or a declared Unknown with an owner |
| **2** | **Validate and align** | Review with the accountable roles (§26) — is it complete, consistent and worth building? | **Approved spec** — status and reviewer recorded in the file header | Second-pair-of-eyes review recorded; ambiguities either closed in §27 or registered with an owner |
| **3** | **Design from the spec** | Architecture placement first, then contracts and data model | ADR where a decision is material · `api/api_contracts.md` · `data/data_model.md` | Architecture review `pass` or `conditional`; contracts lock only after it |
| **4** | **Implement to the spec** | Build strictly to the design. **No scope creep** — a good idea that is not in the spec goes back to stage 1 | Working build, one `TASK-0NN` at a time with specs-to-load | Structural reopen `cleared`; the stdlib, determinism and deny-list gates pass |
| **5** | **Test against the spec** | Verify every acceptance criterion, not the implementation's own assumptions | Tested and verified — `ac_test_plan.md` statuses, `evidence/tests/`, eval results | §9.5 release thresholds met; no AC silently skipped or deferred on a hard gate |
| **6** | **Evolve the spec** | Feed results back. The spec changes first, then the code | **Spec vNext** with a version bump and a change record | Change class approved per artefact 20 §4; regression suite green; drift produces an ADR, never a silent merge |

**The four principles, and what enforces each here**

| Principle | Enforcement in this build |
|---|---|
| Clarity before code | No task may be cut against an unauthored feature (`01_specs/README.md`); tasks name their specs-to-load |
| The spec is the source of truth | Where plan and spec disagree, the spec wins and the plan is corrected. Traceability validator audits `AP → FR → BR → AC → TASK → test → evidence` **and** `inject → BR → AC`, in both directions |
| Coverage is proven, not asserted | The **inject-coverage gate** (TASK-001 step 8) fails the build if any inject lacks a rule and a criterion. A §15 row, a dimension owner or a sentence in a register is not coverage |
| Alignment is explicit | Stage 2 review by the accountable role, recorded in the file — not assumed from silence |
| Testable by design | An acceptance criterion that a machine cannot check is rejected at stage 1. "Appropriate", "reasonable" and "as needed" are not acceptance criteria |

**Loop discipline.** Stage 6 returns to stage 1 for the next increment; it does not return to stage 4. Learning that arrives during implementation — and it will — is written into the spec before it is written into the code. That single rule is what keeps the spec authoritative twelve weeks from now rather than becoming an archaeological record of what someone once intended.

---

## 31. Nine-layer platform architecture and control ownership (BS-40)

AEGIS is an application, but it operates inside an enterprise AI platform whose controls sit at layer boundaries. This section names all nine layers, states what AEGIS puts there, and — importantly — where AEGIS deliberately implements only part of the reference model.

| # | Layer | AEGIS component | Controls at this layer | Where specified |
|---|---|---|---|---|
| **1** | User / workforce | The seven runtime roles: QP, safety physician, supply governance board, quality reviewer, CISO/DPO, auditor, unblinding authority | Identity · entitlement · consent · domain role model · location and jurisdiction | §26.1, `01_specs/registers/roles_and_entitlements.md`; INJ-067, 060, 064 |
| **2** | AI access, request intake, model routing | Runtime mode selector, request admission, model registry and router | Use-case classification by workflow · risk tiering · approved model catalog with hash pins · routing policy (avoided inference → local SLM → large, never a silent fallback) · geography and licensing gates · usage, cost and audit logging | §4, §24.5; INJ-070, 075, 078 |
| **3** | Application / agent | The six agents in §32 | Agent approval · role-based access · model-risk class per agent · human-in-the-loop policy · **capability boundary per agent** | §32 |
| **4** | Orchestration, tool use, policy decision | LangGraph graph or the deterministic runner | Tool permissions allow-list · runtime policy decision, deny by default · action approval via `interrupt()` · data-in/data-out controls · prompt-injection checks · content-safety checks | §20, §21.3; INJ-065, 066, 067, 076 |
| **5** | MCP / connector | `services/integration/mcp/`, source adapters | MCP server approval · connector allow-list · controlled ingestion · rate management · safe-usage policy · **data residency** · tool-call audit · connector trust verification | §21; INJ-064, 066 |
| **6** | Enterprise systems and data | Read-only adapters over exports and fixtures | Data access control · secrets protection · **data lineage = provenance on every node and edge** · encryption in transit and at rest (cloud) · secure connectors · data and model confidentiality | §5.4, §12; INJ-029, 036, 064 |
| **7** | Validation, review and evidence gate | Contract validator, deny-list grader, test and eval suites, forced human acknowledgement | Output quality · **evidence packaging** · security validation · static analysis · change management · version compliance · regulatory linkage · audit-trail retention | §9, §23, §25 |
| **8** | Output, action and release | Pack emission, evidence export, FDE bridge | Release evidence · audit trail · rollback window · published artifacts · post-release monitoring · approved deployment | §3.3, §9.5, §12 |
| **9** | Observability, feedback, improvement | SLI collection, FinOps records, eval regression, drift checks | Telemetry · audit evidence · **model drift** · risk calibration · feedback intake · continuous tuning | §13, §24, §25.7; INJ-081 |

### 31.1 Where AEGIS implements only half a layer — deliberately

The reference model's connector lane offers create, update, replace, delete, trigger and transaction operations, and its release layer performs deployment actions. **AEGIS implements the read half and stops.**

| Reference capability | AEGIS position |
|---|---|
| CRUD, transactions, trigger/ops connectors | **Read connections only.** No write connector exists in the catalog, and registering one fails the compliance tripwire (§23.3) |
| Approval-based routing to a write action | The approval path is produced as *content* for a human; the system performs no action after approval |
| Layer 8 "business action" | Performed by a human in a system of record, outside AEGIS. The system's output is the last thing it does |
| Self-heal / auto-retry / fine-tune loops at layer 9 | Feedback becomes fixtures and specs, reviewed by a human. There is no automatic model or behaviour change |

This is the difference between an advisory system and an autonomous one, expressed as missing capability rather than as policy text. Absent capability cannot be misconfigured.

### 31.2 Layer control ownership

Each layer has one accountable role from §26: layers 1 and 6 to the security/privacy lead; 2 and 4 to the architecture lead; 3 to the architecture lead with GxP co-approval on model-risk class; 5 to the security lead; 7 and 9 to the evaluation lead; 8 to the product lead with GxP sign-off. A layer with no named owner is a finding at the phase review.

---

## 32. Agent roster and capability boundaries (BS-41)

**Answer: six runtime agent roles.** The number is fixed by design and adding a seventh requires an ADR — an unbounded agent population is the most common way a governed system loses its boundary.

### 32.1 The six

| ID | Agent | Responsibility | May call a model | Tools | HITL |
|---|---|---|---|---|---|
| **AG-1** | Supervisor | Selects the workflow, holds the bounded step list, enforces budgets and checkpoints, raises and resumes interrupts | **No** — the step list per workflow is fixed and deterministic | None directly | Owns every interrupt |
| **AG-2** | Evidence retrieval | Selects read-only sources, tags trust status, attaches provenance and hashes | **No** | Source adapters, allow-listed read MCP tools | — |
| **AG-3** | Batch reconciliation (A) | Invokes engine A, assembles contradictions, gaps, abstentions, readiness | Annotations only | Graph, ontology | Forced acknowledgement |
| **AG-4** | PV intake (B) | Invokes engine B — extract, normalise within ontology limits, cluster candidates, cite | Annotations only, within `ai_use_boundaries.csv` | Ontology, terminology | Safety physician review |
| **AG-5** | Supply options (C) | Invokes engine C, assembles draft options with constraints and approval paths | Annotations only | Graph | Approval path interrupt |
| **AG-6** | Review packager | Assembles the human-review pack, enforces forced acknowledgement, validates the contract before emission | **No** | None | Owns the acknowledgement record |

In `assessment` and `ai_disabled`, all six roles execute as plain deterministic functions with no model call and no agency — the same nodes, the same order, the same bytes (§20.6). The agent count does not change between modes; the autonomy does.

### 32.2 What is deliberately *not* an agent

Authorisation and entitlement checks · tool and model trust verification · the prohibited-language deny-list · contract validation · budget and wallet enforcement · cache boundary enforcement · audit writing · compliance tripwires.

These are deterministic kernel code. **A guard implemented as an agent is a guard you cannot certify** — it would introduce a probabilistic path into exactly the controls that must fail closed, and it would make INJ-065 (prompt injection) a route to disabling the gate rather than merely being detected by it.

### 32.3 Capability boundary — enforced, not documented

Each agent declares, in `packages/config/agents.yaml`: permitted tools, maximum steps, maximum tokens, whether inference is permitted, which interrupts it must raise, and its model-risk class. The kernel enforces the declaration at execution time; an agent attempting a tool outside its list is denied and the attempt is audited. Trajectory evals (§25.4) assert zero out-of-boundary calls, so a boundary that erodes fails the build rather than the review.

### 32.4 Build-time agents — separate population, not shipped

Three Cursor-side roles support development and are governed by the hooks in §22: a spec author/reviewer, an implementation agent working one `TASK-0NN` at a time, and a verification agent that runs suites and drafts evidence. They never run in the product, hold no runtime entitlement, and are recorded in `evidence/ai-assisted-changes/` rather than in any pack.

---

## 33. Knowledge graph storage decision (BS-42)

**Answer: an in-process property graph rebuilt deterministically from source on every run. Not Cosmos DB for Gremlin, not Neo4j — with Cosmos Gremlin available as an optional `cloud`-mode adapter behind `GraphPort` if a managed-graph demo is wanted.**

### 33.1 Why the projection is not a database

AP-8 states the graph is a read-only projection, never a system of record. That is not a performance decision, it is the control that keeps the graph from becoming a second, unauditable copy of regulated evidence. A persistent graph store contradicts it in four ways at once: it holds state between runs, it needs its own residency and retention policy, it can drift from source, and it becomes something a reviewer must trust without being able to re-derive it.

Rebuilding from CSV each run means the graph can always be reproduced exactly from evidence that is itself hash-verified. That property is worth more here than any query performance a managed service could offer.

### 33.2 The options, judged against this system

| Option | Verdict | Reasoning |
|---|---|---|
| **Plain-Python property graph** — dataclasses, adjacency dicts, bounded BFS/DFS | **Chosen** | Zero install (AP-5), deterministic ordering under our control (§28), inspectable in a debugger, trivially re-derived, and comfortably sized for fixture-scale data — hundreds of rows per dataset, not billions of vertices |
| `networkx` | Optional adapter behind `GraphPort`; not used by the assessed path | Adds an install for algorithms we do not need at this scale |
| RDF / OWL export (`rdflib`, Oxigraph) | Export format only | Useful for interchange and for the ontology story; a reasoner inferring regulated facts is explicitly out of scope (§5.2) |
| **Azure Cosmos DB for Gremlin** | `cloud` mode only, never required for scoring | Genuinely capable and not deprecated, but see §33.3 |
| Neo4j / AuraDB | Same class as Cosmos; no advantage here | Would add a second vendor without changing any answer the system gives |
| Microsoft Fabric Graph | Noted for the roadmap | Microsoft now points OLAP-style graph work and Gremlin migrations here; relevant only if the graph ever outgrows a per-run projection |

### 33.3 If Cosmos Gremlin is used in `cloud` mode, these constraints are real

Verified against current Microsoft documentation: traversals are cancelled at a **30-second timeout**; exceeding provisioned throughput returns **429 throttling**, which would make traversal behaviour depend on billing state rather than on evidence; **fluent/bytecode API calls are unsupported**, so queries are string-built and the newest Gremlin drivers are not usable — Microsoft recommends the 3.4.x driver line; and Microsoft directs OLAP graph scenarios to Fabric rather than to this API.

On top of those, three constraints come from our own rules: traversal result ordering must be made explicit or determinism (§28) breaks; the store's region must be pinned and asserted, or INJ-064 residency is live; and it concentrates another capability on one vendor, which is the exact risk INJ-078 models.

So the adapter, if built, is a demonstration of portability — that `GraphPort` is real — and never a dependency of any graded result. `T-KG` tests must pass identically against the in-process graph and any adapter, or the adapter is disabled.

### 33.4 What would change this decision

Graph size beyond roughly 10⁶ edges, or a requirement for cross-run persistent graph state, or multi-tenant concurrent traversal at production scale. None of these apply to the challenge data or to the POC, and if one arrives it is an ADR, not a quiet migration.

---

## 34. Azure OpenAI as the advisory model layer (BS-43)

### 34.1 What changed, and the one thing that did not

The product now **gives advice in natural language, generated by Azure OpenAI**, as its normal user-facing behaviour. A new `advisory` mode is the default for the deployed application.

What did **not** change: the deterministic engines remain the source of truth (AP-1). The model writes *about* a pack that has already been computed. It does not compute, decide, retrieve, choose a step or resolve a contradiction. Concretely — if the model were removed, every finding, contradiction, gap, abstention, readiness state and gate outcome would be **byte-identical**. Only the prose would be absent.

This is not caution for its own sake. Three hard requirements make it unavoidable:

| Requirement | Source | Consequence |
|---|---|---|
| AI-disabled continuity for every mandatory workflow | DoD §5, INJ-082, PUB-10 | The product must work with inference off, so inference cannot be load-bearing |
| Identical inputs produce identical bytes | AP-12, NFR-01 | A sampled token stream cannot sit anywhere on the path to a regulated field |
| `pv_intake` tolerates **zero hours** of AI outage | PUB-10 evidence | If advice were required, a PV outage would stop PV work |

So `assessment` stays offline and stdlib-only. That is what gets graded, and it is also the honest answer to "what happens when Azure is unavailable".

### 34.2 What the advice may and may not contain

The model receives the **finished pack** — nothing else. It never sees raw source records, never holds a retrieval tool, and never sees a document the deterministic layer did not already admit as evidence.

| The advice may | The advice may not |
|---|---|
| Explain what the evidence shows, in plain language | State or imply a disposition, causality, eligibility, allocation or recall decision |
| Explain **why** a contradiction matters to this reviewer | Resolve the contradiction, or indicate which side is right |
| Name what is missing and what would close the gap | Assert the missing thing, or estimate it |
| Suggest **questions to ask** and review steps to take | Recommend an action on stock, a batch, a case or a subject |
| Restate a number that is already in the pack | Introduce a number, date, identifier or unit that is not in the pack |
| Say plainly that it cannot help | Fill silence with plausible text |

### 34.3 The output guard — five checks, all deterministic

Generated text is untrusted until it passes every check. A failure discards the text; it is never repaired, and the pack is still delivered without narrative.

| # | Check | Rejects |
|---|---|---|
| **G-1** | Deny-list over rendered text (`packages/contracts/deny_list.json`) | Any disposition or execution statement |
| **G-2** | **Citation closure** — every `evidence_ref` in the advice exists in the pack | Invented sources |
| **G-3** | **Numeric closure** — every number, date and identifier in the advice appears verbatim in the pack | The dominant hallucination mode in this domain |
| **G-4** | Structured-output schema validation, `additionalProperties: false` | Shape drift |
| **G-5** | Abstention preservation — advice cannot narrate past an abstention the engine raised | Confidence the evidence does not support |

G-3 is the strongest control here and the cheapest to run. In a regulated pack, a fabricated number is far more dangerous than a fabricated sentence, and unlike a sentence it is trivially checkable.

### 34.4 Governance of the Azure connection

| Control | Position |
|---|---|
| Authentication | **Microsoft Entra ID with managed identity** via `DefaultAzureCredential`. No API key in code, `.env`, logs or evidence. Key auth is permitted only for local development, from a secret store |
| Deployment pinning | Deployment name, **explicit model version** (never a floating alias) and `api-version` are configuration, and all three are recorded in every evidence record |
| Residency | The endpoint region is checked against the data's residency requirement **before the call**, by the same rule as BR-045. A residency mismatch blocks the call rather than degrading gracefully |
| **Abuse-monitoring retention** | Azure OpenAI retains prompts for human abuse review by default. For any prompt that could carry personal data this is a **processing decision, not a platform detail** — the deployment must either hold the Limited Access exemption from abuse monitoring, or carry only pseudonymised content (BR-012a). The choice is recorded in `compliance/eu-ai-act/` and re-checked at deployment |
| Content filtering | Azure content filters stay enabled; filter categories and severities returned per call are stored as evidence. Our deny-list runs *in addition*, never instead |
| Minimisation before send | Pseudonymisation and purpose filtering run **before** the prompt is built, so the model receives the minimum the purpose requires |
| Budgets | Token, step and wallet ceilings from FR-007 apply. Exhaustion produces a budget-stop abstention, not a shortened answer |
| Kill switch | Disables inference without disabling the product, and does not depend on the inference path to work (BR-075) |
| Prompt versioning | Prompt templates are versioned artefacts with hashes; a prompt change is a change-controlled event with its own evaluation run |

**Configuration slots.** Credentials and endpoint details are supplied by the product owner and are settings, never code. `.env.example` carries the **names only**:

`AZURE_OPENAI_ENDPOINT` · `AZURE_OPENAI_DEPLOYMENT` · `AZURE_OPENAI_API_VERSION` · `AZURE_OPENAI_MODEL_VERSION` · `AZURE_OPENAI_REGION` · `AZURE_CLIENT_ID` (managed identity) · `AEGIS_LLM_ENABLED`.

There is deliberately **no default** for any of them, and no `AZURE_OPENAI_API_KEY` slot outside local development. An unset endpoint, deployment, version or region is treated as a residency failure, so the system makes no call, names the missing setting and still delivers the pack (AC-FR013-19, AMB-14). Defaulting a region would be the quiet way to send regulated data somewhere nobody chose.

### 34.5 Reproducibility despite a non-deterministic model

`temperature=0` and a fixed `seed` reduce variance; Azure guarantees neither. So determinism is achieved structurally instead:

1. Regulated fields never touch the model, so NFR-01 holds regardless of what the model emits.
2. Advice is **recorded and replayed**. Every interaction is stored in a cassette keyed by the SHA-256 of the rendered prompt plus the deployment and model version. Tests and evals replay cassettes and are therefore deterministic; only `advisory` mode calls Azure live.
3. `system_fingerprint`, model version and `api-version` are recorded per call, so a change in Azure's serving stack is visible in evidence rather than mysterious.
4. A live-call test suite runs on demand, is never a release gate, and reports variance rather than asserting equality.

### 34.6 Failure behaviour

| Failure | Behaviour |
|---|---|
| Azure unreachable, throttled or timing out | Pack is delivered without narrative, with a stated reason. Never a queued retry storm |
| Output guard rejects | Text discarded, rejection recorded with the failing check, pack delivered |
| Content filter triggers | Recorded as evidence; no attempt to re-prompt around the filter |
| Residency or consent check fails | Call never made; the reason is stated in the pack |
| Budget exhausted | Budget-stop abstention |

Every one of these degrades to the offline behaviour, which is exactly why the offline path is kept working rather than kept as a formality.

### 34.7 Injects this addresses

064 residency of inference endpoints · 065 injection reaching a model · 070 model supply-chain and manifest integrity · 075 price shock on a real meter · 076 denial of wallet · 078 vendor concentration, now a live Azure dependency named in the risk register · 079 regional outage · 081 model substitution regression · 082 AI-disabled continuity.

---

## 35. Evidence store (BS-44)

### 35.1 Position

Evidence is the deliverable. If a pack cannot be reproduced and defended six months later, the system has not done its job. The store is therefore **append-only, content-addressed and tamper-evident** — not a table that can be updated.

### 35.2 What is stored, per request

| Record | Contents |
|---|---|
| `request` | `request_id`, `scenario_id`, `as_of`, user, purpose, authorisation decision and its inputs, runtime mode, code version |
| `inputs` | Source artefact paths with SHA-256, and the copy-set manifest hash |
| `pack` | The emitted pack, canonical bytes, with its own hash |
| `llm` *(advisory mode only)* | Prompt template id and hash, rendered prompt, response, deployment, **model version**, `api-version`, `system_fingerprint`, token counts, cost, content-filter results, guard outcomes |
| `guard` | Each of G-1…G-5 with pass or fail and the reason |
| `decisions` | Every abstention, denial, gap and contradiction with its reason code |
| `review` | Reviewer identity, evidence items opened, acknowledgement or contest, timestamps |
| `outcome` | Exactly one per request. Terminal disposition from a closed set of nine — three deliberate (`completed`, `abstained`, `denied`), six failures (`budget_exhausted`, `source_unavailable`, `contract_invalid`, `guard_failed`, `timeout`, `internal_error`). Written even when no pack was emitted (BR-142) |
| `audit` | The event chain, each entry carrying the hash of the previous entry |

`outcome` is deliberately not folded into `decisions`. `decisions` records what the system chose *on purpose* — abstentions, denials, gaps, contradictions — and abstention correctness is a headline metric measured from it. A request that consumed budget and produced nothing is a different event, and recording the two in one place would make the metric unreadable. The distinction also gives FR-007 BR-057 the per-request disposition it needs to keep failed requests in the denominator of cost per successful task; in the package baseline 2,190 of 6,100 requests fall into that category with no recorded reason (`03_lean_dmaic/dmaic_plan.md` §2.2).

### 35.3 Integrity

Records are chained: each carries `prev_hash`, so removing or altering one breaks verification for everything after it. `python -m aegis verify-evidence` walks the chain and reports the first break. Tamper-evidence is the achievable property here; tamper-*proofing* would require infrastructure this project does not have, and claiming it would be dishonest.

### 35.4 Where it lives

| Mode | Store | Rationale |
|---|---|---|
| `assessment`, `ai_disabled` | `evidence/` on the filesystem — JSONL plus content-addressed blobs | Zero install, offline, inspectable by a grader with a text editor |
| `advisory`, `ui` | Same layout, plus a local index for retrieval | Same artefacts; the index is derived and disposable |
| `cloud` | **Azure Blob Storage with an immutability policy** (time-based retention plus legal hold), same layout | WORM at the platform level; the container is the system of record, not a database |

The layout is identical across modes, so cloud storage is a destination rather than a different design. Nothing is stored only in a database: an index may be rebuilt from the store, never the reverse.

### 35.5 Retention — and the rule that applies to us

`data/retention_rules.csv` states that **AI prompt logs are deleted after 90 days unless under evidence hold**. That rule governs our own prompt logs, not merely the records the system reasons about. The store therefore implements:

- Clinical source and ICSR records — retained, never expired by this system.
- LLM prompt and response records — expire at 90 days **unless** an evidence hold or legal hold applies.
- A legal hold blocks expiry and is checked at expiry time, live, never from cache (AP-9).
- Expiry is recorded as an event in the chain, so a deletion is itself evidence.

A system that reasons about retention while ignoring its own retention obligation would fail its first inspection question.

### 35.6 Retrieval

`python -m aegis evidence --request-id REQ-...` returns the full chain for one request, and the console links every claim to its record. An inspection-style request — "show me everything behind this pack, including what the model was told" — is answerable in one command. That is the acceptance test for this section.

---

## 36. Supersession

| Version | Status |
|---|---|
| v1 — product inside `submission/` | Superseded |
| v2 — separate repo, Taipy, no KG | Superseded |
| v3 — Next.js + KG, DoD gaps | Superseded |
| v3.1 — DoD-complete, no agent framework or compliance automation | Superseded |
| v3.2 — capability-complete, not spec-ready | Superseded |
| v3.3 — spec-ready, no lifecycle stages, layer controls, agent roster or graph-store decision | Superseded |
| v3.4 — lifecycle and roster complete; five spec artefacts missing, `specs/` and `tasks/` undefined, pseudonymisation uncovered | Superseded |
| v3.5 — complete spec set, but offline-only: no model layer, no evidence store | Superseded |
| v3.6 — model layer and evidence store complete; console still required a Node runtime | Superseded |
| **v3.7 — this document** | **Active** — index only; authoritative build inputs are `01_specs/` and `02_tasks/` |

### 36.1 Final-pass findings, closed in v3.5

Recorded because a plan that claims completeness should show what the completeness check found.

| # | Finding | Severity | Fix |
|---|---|---|---|
| 1 | §30.1, `01_specs/README.md` and TASK-001 all wrote artefacts into `{NEW_REPO}/specs/` and `{NEW_REPO}/tasks/`, which §2 never defined | Would have broken the structure manifest on the first commit | Both directories added to §2 |
| 2 | DoD §4 names **pseudonymisation**; no rule, criterion or test existed anywhere | A named DoD clause with zero coverage | BR-012a, AC-FR002-13, `tests/security/test_pseudonymisation.py` |
| 3 | §30.3 required `poc_vs_production.md`; it was never authored | Unlabelled prototypes drift into production claims | Authored — every component labelled, `submission/src/*.py` marked throwaway |
| 4 | No data model and no state-transition spec, both core technical-design contracts | Ontology and lifecycle rules lived only in prose | `data/data_model.md`, `data/state_transitions.md` authored |
| 5 | NFRs scattered across §13, §24 and §9.5 with no measurable register | Unmeasurable non-functional claims | `nfrs.md` — 20 requirements at v3.5, each with a measurement; 26 today after the model and evidence-store additions |
| 6 | Title line still read v3.2 while the header table read v3.4 | Version ambiguity in a controlled document | Corrected |
| 7 | PUB-12 was filed under continuity, but it reconciles LIMS v1 against v2 with an unapproved unit mapping | The spec would not have matched the fixture | **FR-011** authored |
| 8 | Dimension D07 — injects 045 to 050 — had no owning feature | Behaviour would have been built without being specified | **FR-012** authored |
| 9 | Feature index cited inject IDs that did not match `data/injects.json` — 070, 081, 009 among them | Traceability rows pointing at the wrong requirement | All IDs verified against the source and corrected |

### 36.2 The v3.7 console change

One decision, recorded because it changes the deployment and the dependency surface even though it changes no requirement.

| Aspect | v3.6 | v3.7 |
|---|---|---|
| Console stack | Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui | Jinja + HTMX + Tailwind, served by FastAPI |
| Runtimes to deploy | Python **and** Node | Python only |
| Lockfiles and SBOMs | Two | One |
| BR-065, BR-069, BR-070a enforcement | Server-side by discipline | Server-side by construction (§6.1) |
| Features, business rules, acceptance criteria, tasks | 14 / 128 / 177 / 35 | 14 / 128 / 177 / 35 — **unchanged by the console decision**; the counts move only in §36.3 below |

Nothing in `01_specs/` named a framework, which is why the count is unchanged and why the change was cheap to make at this point. FR-008 gains one clarification — that the enabled acknowledge control must be absent from the server response, not merely disabled in the browser — which strengthens an existing criterion rather than adding a new one.

The honest cost: the React components in `submission/dashboard` no longer port, so the console is built from scratch. That reuse was worth less than it appeared, because §6.1 already forbade porting the mock layer and every screen binds to a pack shape that did not exist in the old dashboard.

### 36.3 The v3.7 inject-coverage closure

A validation pass scanned the registers rather than re-reading their claims, and found that **"all 84 injects map to a feature" was true only at dimension level.** Nineteen injects had an owner and a `TC-INJ` row with a test class in §15, but no business rule and no acceptance criterion. Since §15 lives in this document and this document is explicitly an index (§30), those nineteen behaviours would have been built from a table cell rather than from a spec — which is precisely the failure mode the spec-first lifecycle exists to prevent.

| Aspect | Before | After |
|---|---|---|
| Injects named by a rule and a criterion | 65 of 84 | **81 of 84**, plus 3 artefact obligations with artefact tests |
| Business rules | 128 | **145** (BR-125…BR-141) |
| Acceptance criteria | 177 | **203** |
| Features, tasks | 14 / 35 | 14 / 35 — unchanged; every new rule landed in a feature that already existed |

Sixteen were behavioural gaps inside existing features: FR-010 owned clinical trial integrity but never specified potential unblinding, adjudication backlog or site risk; FR-004 owned evidence integrity but not assay drift, local-code collision, manipulation concerns or CAPA recurrence; FR-003 owned supply but not excipient substitution or customs mismatch. The most serious was **inject 016, potential unblinding** — now BR-138, which treats treatment allocation as absent for every role and additionally detects *inferential* unblinding from combinations of otherwise permitted fields.

Three were genuine artefact obligations with no product behaviour, and they are verified by artefact tests rather than forced into business rules a product cannot enforce. Inject 004 moved the other way: §15 classed patent-cliff urgency as an artefact matter, but urgency invariance is executable, so BR-135 now requires a byte-identical pack under maximum stated urgency.

The lesson worth carrying: **ownership is not coverage.** And a lesson written into a register is not a control, so the scan that found the gap became the **inject-coverage gate** in TASK-001 step 8 — it reads `data/injects.json`, scans both registers, and fails the build naming any inject without a rule and a criterion. Three artefact obligations sit on a closed allow-list; adding a fourth entry fails the gate rather than silencing it. The traceability validator's audited chain gained `inject → BR → AC` so the two agree, and §9.5 now separates the **specification** threshold, enforced from the first commit, from the **execution** threshold measured at release.

That separation is the substantive fix. The old release gate checked only that 84 tests ran and passed, which a test written from a one-line §15 summary would satisfy while the behaviour was never specified. Checking specification completeness in Phase 0 and execution results in Phase 7 closes the window between them.

### 36.4 The v3.8 role-model closure

Asked how governance handles roles, the plan could answer for the build but not for the product. §26 named six accountability roles and §32 fixed six runtime agents, but **the people the system serves were never specified**: `scope.md` §6 listed five business roles while the feature specs used seven, and no file said what any of them could see.

Underneath that was the sharper defect. FR-005 step 4 and BR-046 require sensitive segments to be gated by role, and the package supplies segment → access group (`sensitive_segments.csv`) and user → role (`users_entitlements.csv`) — but **not the edge between them**. BR-046 was a gate with no table, the same defect class as a confidence rule with no number (§29), and it could not have been implemented as written. Whoever built it would have invented a mapping and called it policy.

`01_specs/registers/roles_and_entitlements.md` now carries the seven roles, the deny-by-default entitlement matrix, the canonicalisation table that resolves `qualified_person` against `EU Qualified Person` without fuzzy matching, and the segregation-of-duties constraints. The missing edge is recorded honestly as **AMB-15**, a declared Unknown owned by the security/privacy lead, rather than presented as a decision the package supports. No counts moved: BR-046 was bound to the matrix rather than replaced, so the rule and criterion totals are unchanged and the inject-coverage gate still passes.

Two structural points came out of it. `auditor` satisfies **no** interrupt in any workflow — an auditor who could acknowledge would be reviewing their own oversight — and preparer and acknowledger are positions in a request rather than roles, because a permanently-granted acknowledger role would defeat BR-070a entirely.

### 36.5 The advisory contract could not represent FR-012

Asked whether covering injects inside three workflows was the right approach rather than adding a fourth, the answer was yes — and checking it found that the mechanism the approach depends on had a hole.

Injects outside A, B and C are answered by an `advisory_nonexecuting` pack instead of a workflow pack. Its `workflow` field is **required**, its enum is **closed**, and the object is `additionalProperties: false`. The enum was built with one value per public advisory fixture: `security` and `privacy` (PUB-09, PUB-11), `reliability` (PUB-10), `integration` (PUB-12), `agent` (PUB-13), `finops` (PUB-14), `clinical` (PUB-15).

FR-012 declares that contract and has **no public fixture**. It was authored in v3.5 to adopt the orphaned D07 injects, and nobody extended the enum — so the feature carrying injects 045 to 050 could not emit a legal pack, and AC-FR012-01 was unsatisfiable as written. The enum was **fixture-shaped where it needed to be spec-shaped**, which is the same error as judging inject coverage by dimension ownership (§36.3).

The fix is one value, `regulatory`, plus `tests/contract/test_contract_representability.py` in TASK-004, which parses the `Contract` header of every feature and fails if a declared contract cannot represent it. A fourth workflow engine was considered and rejected: FR-012 is regulatory *context* for A, B and C with no engine, no state machine and no execution path of its own, so an engine would add three parity proofs and a fixture set to serve six injects that a schema value serves.

**The general lesson, third time it has appeared:** an artefact derived from the evidence you happen to have will silently exclude the things you specified later. Derive it from the spec set, and check the derivation in the build.

### 36.6 Modularity was designed but not enforced

Asked whether the app is modular and whether the plan follows through, the design held up and the enforcement did not.

The structure is sound: thirteen stdlib-only core modules, every third-party adapter confined to `services/integration/`, four ports making LangGraph, Redis, Azure OpenAI and the graph store swappable, and a one-way dependency rule that is the reason `assessment` can run with zero installs while `cloud` runs the same nodes through managed services. That part needed no change.

But of the six module rules, only MR-4 had a gate. MR-2 said in its own text that a violation "fails review". MR-5 and MR-6 had no check at all — and **MR-5 is the rule that keeps classification out of orchestrator nodes**, which is what the determinism and parity claims rest on. Risk R-10 names that erosion precisely and offered a design review as the mitigation, which is not a control that survives a deadline.

Nothing checked direction *within* `packages/` either. The one-way rule governs the core's outer boundary and says nothing about its interior, so `ontology` importing `domain` would have inverted the dependency and passed cleanly, as would a cycle.

Worse, the one gate that existed was worded to fail on "any import outside the standard library", which rejects `from packages.ontology import units` — every legitimate internal import. The realistic outcome is not that someone reports the spec as wrong; it is that the first developer it blocks loosens it, and the only enforced module rule gets weaker on day one.

§4a now declares the six-tier layering, and TASK-001 step 9 adds a module boundary gate covering layering, cycles, MR-5, MR-6 and test-support isolation. MR-5 and MR-6 use the literal-construction technique FR-004 already applies to `EvidenceItem`, so it is a proven pattern in this codebase rather than a new one. `api_contracts.md` §6 now records, per rule, whether it is enforced by a gate, structurally, or by review — because a convention labelled as a control is how a boundary quietly stops existing.

---

## 37. Lean DMAIC — Measure-first, then freeze (Prompt 09)

The full registers live in `03_lean_dmaic/` and are the Improve spine for this plan. This section is an index, not a second copy.

| Artefact | Path |
|---|---|
| Lens roll-up | `03_lean_dmaic/lens_rollup.md` |
| DMAIC plan | `03_lean_dmaic/dmaic_plan.md` |
| DOWNTIME waste | `03_lean_dmaic/waste_register_downtime.md` |
| AI-specific waste | `03_lean_dmaic/waste_register_ai_specific.md` |
| Build constraints | `03_lean_dmaic/build_constraints_from_lean.md` |
| Structural reopen | `03_lean_dmaic/structural_reopen.md` |

**Mode is Measure-first, not optional.** Package baselines exist (`model_usage.csv`, `cost_model.csv`, `staff_rates.csv`) and they disagree with the design: inference is costed at $184k/month, human review at $0, and 2,190 of 6,100 requests (35.9%) produced no successful task with no recorded reason. Prompt 09 therefore forbids agent scale-out, extra retrieval and new advisory surface ahead of instrumentation.

**What this changes in the build, in order:**

1. **Stop specifying features.** FR-001 through stage 2, then TASK-008/009, before any new rule or criterion (`02_tasks/task_index.md` Lean freeze).
2. **Instrument before efficiency.** Reviewer minutes at `staff_rates.csv` (TASK-026); one `outcome` record per request (BR-142, TASK-033).
3. **Gate subgroup spread.** NFR-27 / §9.5 — aggregate pass with a failing slice is a fail (TASK-027).
4. **Do not remove forced review.** That cost is a control (INJ-001), not a waste.

Structural reopen item 1 (the `outcome` record) is closed. ADR-001…011 remain a TASK-001 deliverable, not a reason to write more spec. Gate: `cleared` to start Phase 0; `blocked` for any further feature authoring until MF-1 lands.
