# Direct SMTCoq theory certificates

The November 10 extraction adds `EunoiaTheory` and its complete correctness
proofs, plus `TheoryEntry` in the checked certificate cache. All 133 Rocq proof
and Eunoia signature files match upstream core
`910425da6e2f8ba059ed217c26cb9491fb3fb3ba` byte for byte.

Truth, exact premise reuse, equality transitivity (including reflexivity and
symmetry), congruence, and Micromega arithmetic call SMTCoq's existing verified
small checkers directly. Supported steps avoid allocating and executing a local
clause machine. The full signature-generated source checker still validates
every source step, actual premise/conclusion bindings and scopes. Every cache
entry is checked, including unused entries; referenced clauses must match in
exact order. Default true-clause failures are rejected explicitly.

The 37 new proof and mutation examples cover direct theory checking, incorrect
endpoints and argument equalities, changed arithmetic coefficients and premises,
bounds, source-invalid steps after conflict, invalid semantic certificates
after conflict, and shared/unused invalid cache entries. No axioms or admitted
proofs are introduced; the inherited SMTCoq UInt63/proof-irrelevance baseline
remains.

The component manifest adds six separately labeled cases: direct transitivity,
congruence and arithmetic, complete source checking with a shared primitive,
and two corruption controls. Run them without any solver or native producer:

```sh
python3 -B benchmarks/run.py --output /tmp/eunoia-theory-components \
  --repeats 100 --rounds 3 --timeout 30 --kernel-timeout 900 \
  --case transitivity --case congruence --case linear_scaling \
  --case checked_shared_primitive \
  --case unused_invalid_primitive_entry_rejected \
  --case invalid_primitive_after_conflict_rejected
```

Component timing is distinct from the upstream public-tactic comparison. The
upstream producer selects theory operations from actual clauses and formulas,
without hardcoded CPC rule names, and retains the verified local fallback.
Its direct producer and backend are outside this standalone repository.

## Validation

The complete install/regression suite, 238-target assumption audit, and six fresh
component proofs with independent recursive kernel replay passed. The component
probe used one repeat and one round during concurrent verification; it establishes
validity and standalone operation, without a comparative timing claim.
[Exact validation artifact](theory-certificates-validation-2026-11-10.json).
