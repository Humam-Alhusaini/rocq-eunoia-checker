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

## Helper-cache synchronization, 2026-11-04

The current synchronization tracks upstream `46c954b8c07dcc71c8bdacf6516656c104aeeda6`.
All 93 proof/signature files in the provenance manifest match that revision
byte for byte. The generic cache proves exact reference-computation refinement;
all hint entries are validated, including unused ones. The source producer is
checked against 32 captured CPC fixtures without invoking a solver.

The new standalone helper benchmark runner passed a complete smoke run with
fresh closed proofs and independent kernel checking. Its concurrent smoke
timings are validation diagnostics and are not published as performance data.
The older semantic/source samples above retain their original checkpoint and
should not be attributed to this synchronization.

The synchronized standalone snapshot passed `make build`, `make test`, and its
51-target assumption audit. A separate idle-machine component run at
`f9a50f3` passed all three alternating-order rounds, with four fresh closed
proofs and an independent kernel check per round. Median VM times for 3,000
full source-rule calls were 3.516 s for reference evaluation and 2.312 s for
validated sharing; corresponding `Qed` medians were 3.663 s and 2.286 s.
Candidate collection is outside those component timers. These values are not
full-trace, tactic, solver or cross-prover comparisons. The main tactic's
matched experiment found helper mining slower overall and left it optional.

[Exact component timings and source hashes](helper-cache-component-2026-11-04.json)
retain this sample separately from the older semantic/source measurements.

## Indexed evaluator synchronization

The next synchronized snapshot tracks upstream
`f8f7b360f1cf1e44f7e04ca0b3cd765c05cab145`: all 99 proof/signature files
match their recorded upstream hashes. It adds the optional, proved program-name
trie and exact indexed-evaluator refinements. `make build`, `make test`, and the
64-target assumption audit passed, including all 32 indexed CPC captures.
The isolated profiler additionally compiled fresh `uf1` and `lia1` replays
with `--interpreter indexed --repeats 1 --rounds 1` and independently checked
their kernels. These concurrent smoke timings are not performance claims.

The main tactic's matched indexed experiment found a slowdown and kept this
option disabled. This synchronization provides a separately measurable checker
implementation; it does not assert an end-to-end improvement. The older helper
component report above remains tied to its own `f9a50f3` checkpoint.

## Signature-specialized evaluator synchronization

The snapshot synchronized from upstream
`f1ef28e1fd1a0faa88fe712307fea66db228c43b` contains 107 proof/signature files
matching their recorded hashes exactly. It adds expression specialization,
structural fuel layers, generated helper compilation, and surface/full-checker
refinements. The generic proofs are closed; the inherited SMTCoq assumption
baseline is unchanged.

`make build`, `make test`, and the expanded 79-target assumption audit passed.
All 32 captured CPC traces are replayed through the specialized source evaluator.
The isolated profiler supports `--interpreter staged`; a fresh `uf1`/`lia1`
smoke run with one repeat and one round passed all eight timing phases and its
independent kernel check. These concurrent validation timings are not published
as performance evidence. Full-tactic comparisons remain a separate upstream
experiment; the specialized path is optional.

```sh
python3 tools/eunoia-runtime-profile/profile.py --interpreter staged \
  --fixture uf1 --fixture lia1 --repeats 1 --rounds 1 \
  --output /tmp/eunoia-staged-smoke
```

The upstream matched tactic experiment at `f1ef28e` preserved all successes and
rejections but was slower overall: 39.226 s specialized versus 33.420 s
reference over two seven-case rounds per path. The specialization remains off
by default upstream. The independent profiler exposes it for measurement; its
helper-loop gains are not a full-tactic speedup.

## Direct helper compilation synchronization

This snapshot tracks upstream `67cc9a31a069f1ad8a0b8cb3a4cd70e031fe3c75`.
All 116 proof/signature files match their recorded upstream hashes. The
signature compiler emits 58 guarded helpers plus one proved reference fallback
under its case-count resource policy, with flat, scoped and shared checker
adapters. Rule coverage remains 87 selected rules and 59 helpers.

The build and regression suite passed. The complete assumption audit explicitly
includes the 31 new direct-runtime targets and passed all **110 targets**. An
initial 79-target report omitted that new selection and is not used as complete
validation of this snapshot. All 32 captured source traces replay through the
direct evaluator, and fresh `uf1`/`lia1` profiler proofs passed independent
kernel checking with `--interpreter direct --repeats 1 --rounds 1`.

The repeated-rule runner is separate from both captured-source and complete
semantic-checker benchmarks. It includes typing, surface conversion, evaluation,
and separately reported `Qed`; it invokes no solver or native certificate
search. Concurrent smoke measurements are validation diagnostics only, not
published performance comparisons.

Both new entry points passed their smoke checks with fresh artifacts: the
actual-trace profiler produced eight timing rows and passed its kernel check;
the complete repeated-rule runner produced all eight VM/`Qed` rows for one
round, four closed proofs, and an independent kernel check. These checks ran
alongside other validation, so their timings are retained only as diagnostics.

A separate frozen run at `b961527` passed all three alternating-order rounds:
four fresh closed proofs and an independent kernel check per round, yielding
24 VM/`Qed` timing rows. For 3,000 complete rule calls, median VM times were
3.630 s reference and 3.383 s direct; `Qed` medians were 3.731 s and 3.301 s.
These VM/`Qed` figures measure source-rule computation, not the complete tactic.
A Python compiler check ran between measured rounds during kernel verification;
independent-check wall times are not presented as performance comparisons.
Upstream's full tactic remained slower with direct compilation enabled.

[Exact component rows and source hashes](direct-helper-component-2026-11-04.json)
retain the sample independently of later canonicalization experiments.

## Indexed signature aliases (2026-11-05)

This snapshot tracks upstream `14c2dd8beb03005ad0fdda3e31c879df7887d9e3`.
All 117 bundled proof and signature files match that commit byte for byte; the
previous extraction manifest is archived as `provenance/extraction-67cc9a3.json`.
`EoRename.refinement` and the two generated pointwise correctness lemmas prove
that precomputed alias indexes preserve the original renaming computation.
Every source evaluator uses the same generated conversion functions.

`make build`, `make test`, and the expanded **113-target** assumption audit
passed, including all 48 compiler tests and the generated source replay suite.
The new renaming proofs are closed; semantic theorem assumptions remain within
the inherited baseline. No new theory support is claimed by this optimization.

A fresh reference-interpreter `uf1`/`lia1` smoke run produced all eight expected
timing phases and passed its independent kernel check. It ran concurrently
with other validation, so these timings are diagnostics, not performance data.

## Definitionally equal term comparison (2026-11-05)

This snapshot tracks upstream `983c85a` across the same 117 proof and
signature files. Application equality branches on its function comparison,
avoiding the argument comparison after a mismatch. The new pointwise refinement
theorem is proved by `reflexivity` against the original recursive definition.
Existing equality-specification proofs retain their statements and use an
explicit conjunction view during rewriting.

`make build`, `make test`, and the complete **114-target** assumption audit
passed. The new equality refinement is closed. A fresh reference `uf1`/`lia1`
source smoke run produced all eight expected timing phases and passed its
independent kernel check. These validation runs overlapped with main-repository
validation; their timings are diagnostics and do not establish a speedup.
