# Contributing

FDE build rules. Specs in `specs/` are authoritative. The plan is rationale. `docs/README.md` is the documentation register.

## Before you write code

1. Load only the specs listed on the task you are executing (`tasks/`).
2. Write the failing test first, from the acceptance criterion.
3. Interpreter: CPython ≥ 3.11 and < 3.14.
4. Lean freeze: no new feature specs, business rules, or acceptance criteria until FR-001 stage 2. Phase 0 is not frozen.

```text
python -m aegis setup
python -m aegis test
```

Optional console extras: `python -m pip install -r requirements-ui.txt`. How to run the app: root `README.md`. How to change code: `docs/engineering/developer-guide.md`.

## Hard rules

1. Do not add a third-party import under `packages/`. The stdlib import gate will fail the build.
2. Do not construct `Contradiction`, `Gap`, or `Abstention` outside `packages/domain`.
3. Do not call the audit writer outside `packages/kernel`.
4. Do not use `uuid4`, `random`, `time.time`, or `datetime.now` under `packages/`. Derive times from `as_of`.
5. Do not modify challenge-package files. Copy through `scripts/build_fixture_copyset.py`.
6. Do not implement autonomous batch disposition, PV decisions, eligibility, stock movement, quality-status change, or recall initiation.
7. Do not commit `.env` or secrets.

## Documentation

New `docs/` files answer one question (FDE layering). Artefacts that close an inject start with **Inject** and **Obligation**, cite a spec, and do not leave unfinished markers. Add a row to `docs/README.md`.

## Protected change classes

Edits to the deny-list, eval thresholds, MCP tool catalog, Azure adapter, advice brief, or deterministic graders must refresh `compliance/iso42001/change-class-baseline.json`. An exception is recorded in `compliance/iso42001/exceptions.md`.
