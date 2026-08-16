# Intended use

**Question this file answers:** what the product is for, who may use it, and what it must never decide.

AEGIS is an advisory, human-in-the-loop evidence console for three workflows: batch evidence, PV intake, and supply / cold-chain. Deterministic engines assemble a reviewable pack. A qualified human decides outside this system.

## Who it is for

EU Qualified Person, safety physician, supply governance, quality reviewer, CISO / DPO, auditor, and unblinding-authority roles as named in `specs/registers/roles_and_entitlements.md`. Entitlement changes visibility. It never grants the console authority to act in a system of record.

## What it does

- Retrieve evidence with provenance
- Surface contradictions, gaps, and abstentions with equal prominence
- Record acknowledgement, contest, and follow-up notes on an append-only evidence chain
- Optionally add a labelled model restatement in `advisory` mode

## What it does not do

It does not decide batch disposition, PV causality or reportability, clinical eligibility, stock-movement, quality-status change, recall, regulatory submission, or electronic signature. Those exclusions are permanent (`specs/product/scope.md` §4).

## How to use it

1. Assume an identity in the header.
2. Open a catalog pack and read findings, contradictions, gaps, and abstentions together.
3. Open every critical evidence item. Acknowledgement stays unavailable until they are opened.
4. On Status, record the action taken. That note is stored on the evidence chain.
5. Use the in-console user guide (question-mark icon) for page-level screenshots.

The console is instructions for use for reviewers. This file is the product statement those screens implement.
