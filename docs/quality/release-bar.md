# Release bar

**Question this file answers:** what must be true before a tag or a defence demo is called successful.

These are the plan §9.5 / §13 measures that this repository can actually execute. They are not an SLO contract with a live estate.

## Must be green

| Check | Bar |
|---|---|
| `python -m aegis setup` | Interpreter pin, copy-set, structure manifest, static gates |
| `python -m aegis test` | Full suite; a failure or error fails the run |
| Schema validity | Every graded pack validates against the closed contracts |
| Prohibited emissions | Deny-list and no-action inventory stay intact |
| Determinism | Assessment packs are byte-identical across repeats (excluded fields listed in `evals/thresholds.yaml`) |
| Subgroup spread | `subgroup_spread_max` must not exceed the frozen baseline |
| Continuity | `ai_disabled` / `assessment` still emit a schema-valid pack |
| Tripwires | `tests/compliance/test_tripwires.py` |

## Explicitly not the bar

- Model accuracy leadership
- Automation rate
- A live multi-region Azure estate
- EU AI Act conformity assessment or ISO/IEC 42001 certification

## If a hard gate is red

Stop feature work (plan §14 R-02). Do not loosen `evals/thresholds.yaml` to go green. A loosened hard gate is itself a tripwire failure.
