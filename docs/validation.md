# Extraction validation (2026-11-04)

Upstream: SMTRocq `0613ce2b18315b811ed8d19b9a7820e206ffec0f`.
All 80 retained proof/signature files match the upstream bytes in
`provenance/upstream.json`. No checker proof or semantic definition was edited.

Locally executed checks:

- `dune build --ignore-promoted-rules -j 3 @install`: passed.
- `dune runtest --ignore-promoted-rules -j 3`: passed, including 47 generator
  tests, 111 parser regressions, static semantic/mutation/scoping proofs,
  deterministic regeneration, captured source replays and independent checks.
- Five benchmark measurement/report regression tests: passed.
- Nine semantic correctness theorem assumption audits: passed against the
  inherited 52-name baseline. No axiom-free claim is made for semantic checking.
- `opam lint rocq-eunoia-checker.opam`: passed.
- Semantic benchmark: ten cases, two rounds, 50 repeated evaluations per case;
  20 fresh compiled proofs, successful assumption audits, and all 20 checked
  in a separate recursive `rocq check` invocation.
- Generated source benchmark: original UF4 and LIA1 captures, ten repeated
  evaluations, one round, closed assumption reports and a recursive kernel check.
  This is a diagnostic subset; the full source-replay regression runs above.

Toolchain: Rocq 9.2, OCaml 4.14.2, Dune 3.21.1. No solver or public tactic was
invoked. The first complete test run was followed by targeted harness fixes;
failed intermediate measurement directories are retained locally and are not
summarized as successful runs.

Raw logs and JSON remain in the development checkout under ignored `results/`.
CI produces independent benchmark artifacts; local validation does not establish
that a remote CI run passed. Use the README commands to reproduce the checks.

A short shared-machine sample (median repeated-evaluation CPU seconds, including
VM invocation and comparison overhead) follows. These are microbenchmarks, not
a cross-prover performance result. Millisecond timer granularity makes short
individual proof-phase measurements imprecise; use more rounds for comparisons.

| Case | Layer | CPU seconds / evaluation |
| --- | --- | ---: |
| checked_single_scope | complete-scoped-checker | 0.023550 |
| checked_nested_scopes | complete-scoped-checker | 0.035860 |
| checked_boolean_goal | complete-scoped-checker | 0.025650 |
| checked_equality_goal | complete-scoped-checker | 0.027380 |
| low_fuel_rejects | rejection-control | 0.013850 |
| scaling_accepted | local-LIA-certificate | 0.000500 |
| missing_certificate_rejected | rejection-control | 0.000560 |
| changed_coefficient_rejected | rejection-control | 0.000810 |
| transitivity_clause | local-UF-certificate | 0.000570 |
| congruence_clause | local-UF-certificate | 0.000590 |
