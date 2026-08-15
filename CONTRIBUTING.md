# Contributing

1. Load only the specs listed on the task you are executing.
2. Write the failing test first, from the acceptance criterion.
3. Do not add a third-party import under `packages/`. The stdlib import gate will fail the build.
4. Do not construct `Contradiction`, `Gap`, or `Abstention` outside `packages/domain`.
5. Do not call the audit writer outside `packages/kernel`.
6. Do not use `uuid4`, `random`, `time.time`, or `datetime.now` under `packages/`. Derive times from `as_of`.
7. Do not modify challenge-package files. Copy through `scripts/build_fixture_copyset.py`.
8. Do not implement autonomous batch disposition, PV decisions, eligibility, stock movement, quality-status change, or recall initiation.
9. Interpreter: CPython ≥ 3.11, < 3.14.
10. Lean freeze: no new feature specs, business rules, or acceptance criteria until FR-001 stage 2. Phase 0 is not frozen.
