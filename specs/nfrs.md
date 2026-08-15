# Non-functional requirements

**Question this file answers:** what must be true of the system regardless of which feature is running, with a number attached to each claim.

Every row is measured somewhere and reported to `evidence/`. A row without a measurement is a defect in this file.

| ID | Requirement | Target | Measured by |
|---|---|---|---|
| **NFR-01** | Determinism | 3 consecutive runs byte-identical, **no excluded fields** | `tests/regression/test_byte_identical.py` |
| **NFR-02** | Zero-install assessed path | `assessment` runs on CPython 3.11–3.13 stdlib alone | Clean-clone CI job, no network |
| **NFR-03** | Offline operation | No socket opened in `assessment` or `ai_disabled` | Network-denied CI job |
| **NFR-04** | Batch pack latency | p95 < 5 s on assessment fixtures | `tests/performance/` |
| **NFR-05** | API latency (`ui`) | p95 < 1.5 s cached, < 5 s cold | `tests/performance/` |
| **NFR-06** | Graph traversal bound | ≤ 4 hops default, hard cap 6 | `tests/integration/test_bounded_traversal.py` |
| **NFR-07** | Per-request token ceiling | 50 000; exceeded → budget stop, not truncation | `tests/security/` |
| **NFR-08** | Cumulative wallet | Daily and monthly ceilings with soft alert and hard stop | `tests/performance/` |
| **NFR-09** | Cache correctness | Cache-on output identical to cache-off; zero authZ/consent keys in any namespace | `tests/security/test_cache_boundaries.py` |
| **NFR-10** | Schema validity | 100% of emitted packs validate before leaving the service | Contract suite |
| **NFR-11** | Evidence provenance | 100% of cited facts carry a valid sha256 and `source_preserved: true` | Contract suite |
| **NFR-12** | Continuity | 100% of workflows produce packs with inference disabled | `tests/resilience/` |
| **NFR-13** | Orchestrator parity | LangGraph and stdlib runners byte-identical with inference off | `tests/orchestration/test_parity.py` |
| **NFR-14** | Accessibility | 0 axe critical/serious findings; 100% keyboard reachability on the 4 core screens | `tests/e2e/` |
| **NFR-15** | Internationalisation | RTL Arabic renders correctly; Hindi renders correctly; locale never changes a computed value | `tests/e2e/`, NFR-01 hostile-locale job |
| **NFR-16** | Auditability | Every abstention, denial, resume and acknowledgement recorded with a reason | Audit assertions |
| **NFR-17** | Recoverability | System state rebuildable from CSV + code; evidence directory is the durable artefact | `tests/resilience/` restore test |
| **NFR-18** | Capacity | Sized to fixture scale — hundreds of rows per dataset; limits documented, not assumed | `tests/performance/` |
| **NFR-19** | Secret hygiene | No secret, credential or personal datum in code, logs, fixtures, packs or docs | Secret scan in CI + `beforeSubmitPrompt` hook |
| **NFR-20** | Supply-chain integrity | Every optional dependency pinned and present in `security/sbom/` | Build gate |
| **NFR-21** | Advice reproducibility | Cassette replay byte-identical across 3 runs; **zero live calls** in tests and evals | `tests/regression/test_advice_replay.py` |
| **NFR-22** | Advice groundedness | 100% of numbers, dates and identifiers in advice present verbatim in the pack; 0 unsupported claims | `evals/graders/deterministic/groundedness.py` |
| **NFR-23** | Advisory latency | p95 < 8 s end to end including generation; the pack itself still meets NFR-04 | `tests/performance/` |
| **NFR-24** | Regulated-field isolation | Pack in `advisory` mode byte-identical to `assessment` once annotations are removed, on 15/15 fixtures | `tests/orchestration/test_advisory_parity.py` |
| **NFR-25** | Evidence completeness | 100% of requests produce a verifiable chain; 0 requests proceed without one | `tests/integration/test_evidence_chain.py` |
| **NFR-26** | Evidence integrity | Any single-byte alteration detected, first break reported | `tests/security/test_chain_tamper.py` |
| **NFR-27** | Subgroup spread | Advisory-mode model metrics: AUROC spread across named cohorts ≤ **0.15**; entity F1 spread across named languages ≤ **0.15**. Aggregate pass with a failing slice is a fail | `evals/datasets/subgroup/`; `evals/thresholds.yaml` `subgroup_spread` |

## Trade-off rules

Performance work may never weaken NFR-01, NFR-09, NFR-10 or NFR-11. Where latency and determinism conflict, determinism wins and the latency target is renegotiated as an ADR — not silently missed.

Narrative is the first thing sacrificed under any pressure — latency, cost, outage or guard failure. NFR-23 may be missed without a release block; NFR-24 may not be missed at all, because the moment generated text can move a regulated field, every other guarantee in this table becomes unprovable.
