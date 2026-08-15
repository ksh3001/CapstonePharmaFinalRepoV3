# Success metrics — named conflicts, no single objective

**Inject:** INJ-002 (conflicting success metrics).  
**Obligation:** conflicting success metrics are surfaced as a conflict with the trade-off named. No single metric is presented as the objective.

## The conflict (named)

Manufacturing is rewarded for throughput. Quality is rewarded for deviation containment. Supply is rewarded for service level. Clinical is rewarded for database-lock speed. Those four incentives cannot be collapsed into one score without hiding who loses.

AEGIS does not pick a winner. It surfaces the conflict and keeps the trade-off visible so a human with authority can judge.

## Product measures (not a substitute objective)

From `specs/product/scope.md` §7, the product is judged on:

- cycle time to a **reviewable** evidence pack
- proportion of contradictions surfaced rather than missed
- abstention correctness
- zero prohibited outputs
- reviewer trust from the human panel
- cost per successful task, including human-review time

These are a balanced set. None of them is *the* objective. Throughput, service level, and lock speed are stakeholder metrics the pack may cite as evidence of pressure; they are not optimisation targets for the engines.

## Explicitly not a success measure

- model accuracy leadership
- automation rate
- any single KPI that would justify skipping a gate

A dashboard, annotation, or advisory sentence that presents one of those as the product objective is a defect against this artefact and against BR-007 / BR-064 (the console computes no business rule and must not offer a prohibited action).

## Trade-off the product will not hide

Faster assembly that misses a contradiction is a failure, even if cycle time looks better. An abstention that keeps Quality authority intact is a success, even if it looks slower than a confident wrong pack.
