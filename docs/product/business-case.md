# Business case — cycle time without weakening Quality

**Inject:** INJ-001 (board compression target).  
**Obligation:** any cycle-time benefit is modelled together with the Quality authority it must not weaken. A stated benefit that assumes reduced review is rejected.

## Board pressure

The challenge board asks for a reduction in end-to-end release lead time without changing registered specifications. That pressure is a scenario, not a product objective. AEGIS does not take a compression target as a reason to skip a gate, collapse a contradiction, or let a model decide.

## What the product actually shortens

The scarce cost in the three workflows is expert time spent *assembling* evidence (MES, LIMS, QMS, safety sources, supply constraints). The product shortens time **to a reviewable evidence pack**: provenance, contradictions, gaps, and abstentions, ready for a human. It does not shorten independent Quality review, Qualified Person judgement, safety medical review, or supply-governance approval.

`specs/product/scope.md` states the bound: the cost of a wrong judgement is patient harm or regulatory exposure, so the answer cannot be an automation that decides faster.

## Quality authority that must not weaken

| Role | Remains the decision-maker | Product must not do |
|---|---|---|
| EU Qualified Person | Batch release | Disposition or release |
| Safety physician | Causality, seriousness, reportability | Final PV conclusions |
| Supply governance board | Allocation and shipment | Reserve, allocate, or ship |
| Quality reviewer | Disposition | Change quality status |

These exclusions are permanent (`specs/product/scope.md` §4). A benefit claim that assumes fewer reviewers, a shorter QP review, or a waived GxP gate is **rejected**. Cycle-time benefit and Quality authority are modelled together, or the claim is not a benefit of this product.

## Stop if the claim drifts

Plan §14 R-08: any disposition, eligibility, or allocation feature is rejected by the policy gate and by design review. That is the executable form of this artefact.
