# PoC vs production labelling

**Question this file answers:** which parts of this build are meant to survive, and which are honestly disposable. Unlabelled prototype code becomes production code by accident; that is the failure this file prevents.

Three labels only.

- **Production-intent** — built to the full quality bar: specs, tests, gates, evidence. Would ship.
- **Demonstrator** — real and working, but scoped to fixtures. Correct behaviour, not production scale, hardening or operability.
- **Throwaway scaffolding** — exists to prove a path or unblock a demo. **Must not be migrated.**

| Component | Label | Reasoning |
|---|---|---|
| `packages/domain` engines A/B/C | Production-intent | The deterministic source of truth; everything else defers to it |
| `packages/kernel` (authZ, budgets, canonical JSON, kill switch) | Production-intent | The controls are the product |
| `packages/contracts` + deny-list | Production-intent | Regulated output boundary |
| `packages/ontology` | Production-intent | Abstention correctness depends on it |
| `packages/graph` | Demonstrator | Correct and bounded, but in-process and fixture-scale (§33). Cosmos Gremlin adapter would be the production path |
| `packages/orchestrator` stdlib runner | Production-intent | It is the continuity path, not a stand-in |
| `services/integration/langgraph` | Demonstrator | Proven at parity on fixtures; no production deployment topology |
| `services/integration/redis` | Demonstrator | Correctness proven by parity; no HA, eviction tuning or failover design |
| `services/integration/mcp` | Demonstrator | Read-only, allow-listed, mode-gated |
| `services/integration/inference` (Azure OpenAI) | Demonstrator | Managed identity, pinned version and full governance are production-intent in design, but there is no production quota model, no multi-region strategy and no load testing at scale |
| `packages/advice` (prompts + guard G-1…G-5) | Production-intent | The guard is the control that makes generated text safe to show; it is held to the same bar as the gates |
| `packages/evidence_store` | Production-intent | Evidence is the deliverable. A demonstrator evidence store would make every other claim unverifiable |
| `services/integration/evidence_store` (Azure Blob WORM) | Demonstrator | Correct layout and immutability policy, but no lifecycle management, geo-redundancy or restore rehearsal |
| `services/api` | Demonstrator | Correct contracts; no rate limiting, tenancy or production auth integration |
| `apps/web` server-rendered console (Jinja + HTMX) | Demonstrator | Four core screens live via `python -m aegis serve`. FastAPI is optional transport. Not a full operator product |
| `evals/` graders | Production-intent | Release gating depends on them |
| `compliance/` tripwires | Production-intent | An unexecutable compliance claim is worse than none |
| `infra/`, `deploy/` | Throwaway scaffolding | Structure and local environment only; no cloud provisioning is claimed |
| `services/worker` | Not built | Deferred with no stub, so nothing pretends to exist |
| **Existing `submission/src/*.py` stubs** | **Throwaway scaffolding** | Hardcoded stubs written to make the Taipy UI import cleanly. **Explicitly not migrated** into the new repository. They are the clearest example of why this file exists |
| Existing Taipy UI | Superseded | Replaced by `apps/web`. Superseded because Taipy owns the rendering model, which puts WCAG 2.2 AA, RTL and payload-level entitlement out of reach — not because it looks dated. Retained in the old repo as history |

## Rules

A component may be promoted from Demonstrator to Production-intent only by satisfying the full bar and recording the change here with a date. Nothing is silently promoted, and no component is labelled Production-intent in advance of the evidence.

Release notes, the defence and the readiness recommendation all quote these labels verbatim. Claiming production readiness for a Demonstrator is a defence failure, not a presentation choice.
