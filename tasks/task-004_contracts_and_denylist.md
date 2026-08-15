# TASK-004 — Contract package, advisory contract and deny-list

**Goal:** make every one of the fifteen fixtures validatable, including the seven that reference a contract the challenge package does not ship, make every *feature* that declares a contract able to emit one, and make prohibited output impossible to emit unnoticed.

## Specs to load

`01_specs/api/api_contracts.md` (whole file) · `01_specs/api/advisory_nonexecuting.schema.json` · AMB-01 in plan §27 · `01_specs/product/scope.md` §4 (out of scope, permanently) · the `Contract` header row of every file in `01_specs/features/`.

## Out of scope

Producing packs. Any engine logic. The UI.

## Steps

1. Copy the four challenge schemas into `packages/contracts/regulated/` unmodified; hash-verify them and fail the build if any differs from `FILE_HASHES.csv`.
2. Install `advisory_nonexecuting.schema.json` into `packages/contracts/internal/`, keeping the `description` that marks it team-authored.
3. Implement a stdlib JSON Schema validator sufficient for draft 2020-12 as used by these five schemas — `type`, `required`, `enum`, `const`, `properties`, `items`, `$ref`, `additionalProperties: false`, `minLength`, `minItems`, `pattern`. No third-party dependency (AP-5).
4. Implement contract resolution: read `response_contract` from the fixture and select the schema. `"advisory_nonexecuting"` maps to the internal contract; a `*.schema.json` value maps to the regulated one; an unknown value is an error, never a default.
5. Author `packages/contracts/deny_list.json` with the categories in `api_contracts.md` §4, plus its baseline hash.
6. Implement the deny-list grader over **rendered strings at any depth**, not field names.
7. Implement the invariant assertions that apply to every contract: `execution_status == "not_executed"`; `no_side_effects == true` where the contract has it; every evidence item carrying a well-formed hash and `source_preserved: true`.
8. Implement the **contract representability check**: parse the `Contract` header row of every file in `specs/features/`, and for each feature declaring `advisory_nonexecuting`, assert its declared `workflow` value exists in the schema enum. Fail naming the feature and the missing value. The enum is derived from the **feature** set, not the fixture set — building it from fixtures is what left FR-012 unable to emit a valid pack (`api_contracts.md` §2).

## Acceptance checks

- All fifteen fixtures resolve to a contract; none falls through to a default.
- Every feature declaring `advisory_nonexecuting` has an enum value; adding a fifteenth feature with a new scenario type and no enum value fails the build, naming it.
- A pack containing "approved for release" in a nested free-text field is rejected by the grader.
- Removing a required property from a pack fails validation with the property named.
- Adding an undeclared property fails validation — closure is enforced, not assumed.
- Shrinking `deny_list.json` fails the baseline-hash check.
- The validator imports nothing outside the standard library.

## Test expectations

`tests/contract/test_advisory_contract.py` — the seven advisory fixtures validate (AMB-01).
`tests/contract/test_contract_representability.py` — every feature declaring the advisory contract has an enum value; a feature with an unlisted value fails, naming it.
`tests/contract/test_invariants.py` — AC-FR001-02, AC-FR003-02.
`tests/security/test_prohibited_language.py` — AC-FR001-03, AC-FR002-02, AC-FR003-03, with nested and rendered-string cases.

## Done when

Every fixture has a resolvable contract, the deny-list cannot be weakened silently, and the contract layer runs offline with zero installs.
