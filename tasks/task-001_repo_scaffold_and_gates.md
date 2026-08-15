# TASK-001 — Repo scaffold, structure manifest and build gates

**Goal:** create the new repository skeleton so that every later task lands in a place that already exists, and so the constraints everything else depends on — stdlib-only core, a pinned interpreter, determinism and complete inject coverage — are enforced from the first commit rather than asserted later.

## Specs to load

`00_plan/MASTER_BUILD_PLAN.md` §2 (structure), §4 (runtime modes and dependency policy) · `01_specs/README.md` · `01_specs/product/scope.md` (AP-5, AP-11) · `01_specs/registers/traceability_gap_audit.md` §3 (the allow-list and why it exists).

Nothing else. Do not read the feature specs for this task.

## Out of scope

Any domain logic. Any workflow engine. Any dependency install. The Cursor hooks and `mcp.json` (TASK-001b, cut separately once the repo exists).

## Steps

1. Create `aegis-sdd` at the location in plan §19 decision 1, outside the challenge package.
2. Create the directory tree from plan §2 exactly, with `.gitkeep` in otherwise empty directories.
3. Write root files: `README.md`, `REPO_MAP.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `.env.example` (names only), `LICENSE`, `.gitignore`.
4. Generate `STRUCTURE_MANIFEST.json` from the tree — generated, never hand-edited.
5. Implement the **stdlib import gate** in `quality/static-analysis/`: walk `packages/`, parse each module with `ast`, and fail on any import that is neither the standard library nor another `packages/*` module. Intra-core imports are legitimate and must pass — a gate that rejects `from packages.ontology import units` inside `packages/domain` would be loosened by the first person it blocked, which is worse than not having it. Report a third-party hit against the deny-list `langgraph, langchain, redis, mcp, fastapi, jinja2, httpx, requests, networkx, rdflib, openai, azure` so the message names the offending dependency.
6. Implement the **interpreter guard**: refuse to run outside CPython ≥ 3.11, < 3.14, with a clear message naming the detected version.
7. Implement the **banned-nondeterminism gate**: fail if `packages/` references `uuid4`, `random`, `time.time`, or `datetime.now`.
8. Implement the **inject-coverage gate** in `quality/static-analysis/inject_coverage_gate.py`. It reads every inject ID from `data/injects.json`, scans the inject column of `specs/registers/business_rules_register.md` and `specs/registers/acceptance_criteria_register.md`, and fails the build naming any inject not carried by **at least one business rule and one acceptance criterion**. Exempt only the IDs in `quality/static-analysis/inject_coverage_allowlist.json`, which is a closed list of three artefact obligations — `001`, `002`, `003` — each with the artefact path and the artefact test that verifies it. The gate additionally fails if the allow-list contains an ID not in that set, so widening the exemption is a reviewed change rather than a quiet one, and if the registers cite an inject ID absent from `data/injects.json`.
9. Implement the **module boundary gate** in `quality/static-analysis/module_boundaries.py`, enforcing plan §4a from the same AST walk as step 5:
   - **Layering** — each module's tier is read from a declared map; an import running upward a tier fails, naming both modules.
   - **Cycles** — build the intra-`packages` import graph and fail on any cycle at any depth, printing the cycle.
   - **MR-5** — a literal construction of `Contradiction`, `Gap` or `Abstention` outside `packages/domain` fails, mirroring the `EvidenceItem` check FR-004 already requires.
   - **MR-6** — a call to the audit writer from outside `packages/kernel` fails.
   - **Test isolation** — `packages/test-support` imported from anything but `tests/` fails.
10. Extend the **traceability validator** so its audited chain is `AP → FR → BR → AC → TASK → test → evidence` **and** `inject → BR → AC`. `traceability.csv` already carries an `inject_id` column; the validator must assert completeness over it rather than merely permit it.
11. Copy the plan into `plans/active/`, `01_specs/` into `specs/` and `02_tasks/` into `tasks/` — all three defined in plan §2.

## Acceptance checks

- The tree matches plan §2; `STRUCTURE_MANIFEST.json` regenerates identically on a second run.
- Adding `import requests` to any module under `packages/` fails the gate, with the offending file and line named.
- A normal intra-core import such as `from packages.ontology import units` inside `packages/domain` **passes** — the gate does not block legitimate composition.
- `packages/ontology` importing `packages/domain` fails the layering check, naming both modules and their tiers.
- An import cycle between any two core modules fails, printing the cycle.
- Constructing a `Contradiction`, `Gap` or `Abstention` outside `packages/domain` fails (MR-5); calling the audit writer outside `packages/kernel` fails (MR-6).
- Importing `packages/test-support` from a non-test module fails.
- Adding `uuid4()` to a module under `packages/` fails the nondeterminism gate.
- Running under Python 3.10 exits non-zero with the version message; running under 3.11 and 3.12 succeeds.
- Deleting any business rule that is the sole carrier of an inject fails the inject-coverage gate, naming that inject.
- Adding a fourth ID to the allow-list fails the gate rather than suppressing a finding.
- The gate passes today at 81 of 81 behavioural injects plus the three allow-listed artefact obligations.
- No file contains a credential, token or real hostname.

## Test expectations

`quality/static-analysis/test_no_third_party.py` — positive and negative cases, including a deliberately violating fixture module.
`quality/static-analysis/test_inject_coverage_gate.py` — passes on the current registers; fails on a register with a rule removed; fails on a widened allow-list; fails on a register citing a nonexistent inject ID.
`quality/static-analysis/test_module_boundaries.py` — a legal intra-core import passes; an upward import, a cycle, an out-of-package `Contradiction` construction, an out-of-kernel audit write and a non-test `test-support` import each fail, and each names what it found.
`tests/unit/test_setup_guard.py` — version boundary cases.
`tests/unit/test_structure_manifest.py` — regeneration is stable.

## Done when

A clean clone runs the gates offline with zero installs, all five gate tests pass, and `git status` shows no untracked generated files.

## Why the inject-coverage gate is in Phase 0

The v3.7 audit found nineteen injects that were owned by a dimension and listed in plan §15 but named by no rule and no criterion (`01_specs/registers/traceability_gap_audit.md` §3). The existing controls would not have caught it: the release gate checks execution results in Phase 7, and the `stop` hook only reminds, fail-open. Nothing structural prevented the recurrence, so the check that found the gap is made permanent here rather than left as a sentence in a register. This is AP-11 applied to the spec set itself.
