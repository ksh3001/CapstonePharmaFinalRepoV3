# Developer guide

**Question this file answers:** how a contributor changes this repository without breaking an FDE gate.

## Interpreter and setup

CPython ≥ 3.11 and < 3.14. From the repo root:

```text
python -m aegis setup
python -m aegis test
```

Console extras (optional): `python -m pip install -r requirements-ui.txt`.

Load only the specs listed on the task you are executing (`tasks/`). Specs win over the plan.

## Hard rules (also in `CONTRIBUTING.md`)

1. No third-party import under `packages/`.
2. Do not construct `Contradiction`, `Gap`, or `Abstention` outside `packages/domain`.
3. Do not call `write_audit` outside `packages/kernel`.
4. Derive times from `as_of`. No `datetime.now`, `time.time`, `uuid4`, or `random` in `packages/`.
5. Do not modify challenge-package evidence. Copy through `scripts/build_fixture_copyset.py`.
6. Do not implement a prohibited action (disposition, eligibility, stock-movement, recall, signature).

## Gates that fail the build

| Gate | What it checks |
|---|---|
| Stdlib | `packages/` imports |
| Module boundaries | Layering, MR-5, MR-6 |
| Inject coverage | Every inject has a BR and an AC (or the closed 001–003 allow-list) |
| Traceability | `specs/registers/traceability.csv` — generated, do not hand-author a second matrix |
| Nondeterminism | Forbidden clocks and RNG in `packages/` |
| Compliance tripwires | Artefact 19 §7 triggers in `compliance/tripwires/evaluate.py` |
| Change-class baseline | Protected files in `compliance/iso42001/change-class-baseline.json` |

If you edit a protected file (deny-list, thresholds, MCP tools, system prompt, Azure adapter, graders), update the baseline hash **and** record the reason in `compliance/iso42001/exceptions.md` when the change is an exception rather than a hash refresh.

## Tests

`python -m aegis test` discovers `tests/**/test_*.py` and `quality/static-analysis/test_*.py`. Write the failing test from the acceptance criterion first.

## Documentation standard

New `docs/` files answer one question. Artefact files that close an inject start with **Inject** and **Obligation**, cite a spec or BR, and do not leave unfinished markers. Register the file in `docs/README.md`.
