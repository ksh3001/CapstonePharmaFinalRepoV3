# No-AI baseline — compared explicitly, including when it wins

**Inject:** INJ-003 (no-AI challenge).  
**Obligation:** the no-AI baseline is stated and compared explicitly, including the case where it wins.

## The challenge

A process-excellence claim in the package is that workflow redesign and master-data repair could deliver most of the value without generative AI. That claim is in scope for this artefact. It is not dismissed.

## What “no AI” already is in AEGIS

Deterministic engines in `packages/` are the source of truth (AP-1). They retrieve evidence, detect contradictions and gaps, abstain with reasons, and deny prohibited actions. They do not call a model.

Runtime modes `assessment` and `ai_disabled` run the same nodes as plain functions with inference off. The regulated fields of the fifteen public fixtures are required to be byte-identical with the model on or off (AC-FR013-01). The console and the CLI can both produce a pack without Azure OpenAI.

Generative AI exists only in FR-013: advisory annotations on `human_review`, never on a regulated field.

## When the no-AI baseline wins

The no-AI path wins — and is the required path — when any of the following is true:

- the work is evidence assembly, contradiction detection, unit comparison, identity, privacy, or a hard gate (the engines already do this)
- the model is unavailable, unpinned, out of residency, or over budget
- a reviewer would be slower checking prose than reading the structured pack
- the claim to be proven is a schema-valid pack offline (DoD §3, NFR-03)

In those cases adding a model cannot improve the scored outcome and can only add cost, attack surface (INJ-065/066/070/076), and vendor concentration (INJ-078). The product keeps the no-AI path as the assessed default rather than as a fallback brochure.

## When advisory text is allowed to exist

Only as labelled annotation, after the engines have already produced the pack, and only in `advisory` / `ui` / `cloud`. If the annotation and the pack disagree, the pack wins. If inference is off, nothing is missing from the regulated result.

## Stop/pivot (plan §14)

R-01: if the knowledge-graph projection adds no value over the relational baseline, retire graph features — the engines remain.  
R-10: if domain logic starts living in graph nodes, the module-boundary gate fails the build.  
Stop criteria: hard-gate injects not at 100% PASS, or no workflow producing a schema-valid pack offline.

Those thresholds are the comparison the board asked for: the no-AI baseline is executable today; generative AI is optional prose on top of it.
