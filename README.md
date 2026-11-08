# Rocq Eunoia Checker

A standalone extraction of SMTRocq's signature-generated Eunoia/CPC checker,
with benchmarks that do not invoke an SMT solver, the SMTCoq tactic, or native
certificate search. Extracted from [SMTRocq PR #2](https://github.com/Humam-Alhusaini/SMTRocq/pull/2)
initially at `0613ce2b18315b811ed8d19b9a7820e206ffec0f`, now synchronized with
the checkpoint recorded in [the upstream manifest](provenance/upstream.json).

The repository includes the generated rule interpreter, strict CPC reader,
checked trace/scoping machinery, semantic certificate gates, proofs, fixtures,
signature compiler, and required SMTCoq theory sources. All 131 current Rocq proof and Eunoia signature files match that upstream
checkpoint byte for byte. Their hashes are in
[provenance/upstream.json](provenance/upstream.json); the original extraction
record remains in [provenance/extraction-0613ce2b.json](provenance/extraction-0613ce2b.json).
The initial 115 relevant commits
retain their authorship, with rewritten commit IDs mapped in
[provenance/commit-map.tsv](provenance/commit-map.tsv).

The verified signature-program index is also included and tested against the
reference evaluator; it remains an experimental tactic path upstream.

The generic checked-helper cache and its reference-refinement proofs are included;
its collection and validation tests use captured CPC data, with no solver invocation.

The direct local certificate gate and its correctness theorem are included.
It derives an exact clause from exact premises using the existing SMTCoq
operations; complete source/scoping checks still run. Upstream keeps candidate
search experimental because a matched comparison did not establish a broad
performance gain. [Details](docs/eunoia/direct-certificates.md).

## Build and test

Requires Linux/POSIX, OCaml, Rocq **9.2 or later**, its matching standard library,
Dune **3.21 or later**, and Python **3.9 or later**. Rocq 9.2 / OCaml 4.14.2 /
Dune 3.21.1 were tested. No Trakt, cvc5, veriT, CVC4, ZChaff, installed SMTCoq,
or SMTCoq OCaml plugin is required.

In an existing opam switch:

```sh
opam install . --deps-only --with-test
make build
make test
python3 -B tools/check-assumptions.py --output /tmp/eunoia-assumptions
```

The generator follows the pinned signature's include graph: 87 selected rules
and 59 helpers; 522 other rules reject. Tests cover deterministic regeneration,
48 compiler tests, 111 reader cases, positive and corrupted certificates,
scope/liveness controls, captured proof replays, and independent kernel checks.
`make test` includes the full generated-runtime validation; its outputs remain
in temporary directories. Set `EUNOIA_KEEP_TEST_DIR=1` to retain them.

For an isolated prebuilt toolchain, the image used by CI is pinned by digest:

```sh
docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=/work" -w /work \
  --entrypoint /bin/bash \
  ghcr.io/rocq-trakt/rocq@sha256:21d9edc7a97aabe15577ae442854c2a03cc81097ff7b5fa899d8d6fe62d05c68 \
  -lc 'make build && make test'
```

The image contains additional packages, but this project's build does not link
against Trakt or the SMTCoq tactic plugin. A wrapper that executes arbitrary
commands can be selected with `EUNOIA_ENV=/absolute/path/to/wrapper`; otherwise
tools use the current PATH via `tools/rocq-env`.

## Benchmark independently

Keep the semantic and source-computation measurement layers separate.

**Semantic certificate checking:**

```sh
python3 -B benchmarks/run.py --output results/semantic --repeats 100 --rounds 3
python3 -B benchmarks/report.py results/semantic/summary.json
```

This builds first, then uses fresh Rocq compiler processes to evaluate fixed,
preconstructed certificates: complete scoped checker calls, local UF and LIA
certificates, and rejection controls. The default ten cases come from unchanged
upstream regressions. Each case must compute its exact expected result, finish
`Qed`, produce a fresh `.vo`, pass its assumption audit, and pass an independent
recursive `rocq check`. False results for corrupted inputs are labeled rejection
controls, not successful positive proofs. Select examples with repeatable
`--case NAME`; see [benchmarks/cases.json](benchmarks/cases.json).

**Generated source-rule computation:**

```sh
python3 -B tools/eunoia-runtime-profile/profile.py \
  --output /tmp/eunoia-source --repeats 20 --rounds 3
```

This replays 29 original/reduced UF/LIA solver captures through generated source
computation, retaining hashes, step counts, timings, assumption checks and kernel
checks. It is **not semantic proof acceptance**: its test type queries and roots
are computation inputs. `--interpreter indexed` selects the proved program-name index on the same
captured computation workload; the default remains `reference`. This source
comparison is separate from full tactic performance.
Integer-cast capture regressions additionally run in
`make test`; the profiler's default 29-capture corpus excludes those three.

The optional checked-helper sharing component has a separate runner:

```sh
python3 -B benchmarks/helper_cache.py --output /tmp/eunoia-helpers --rounds 3
```

It compares 1,000 and 3,000 complete `arith_poly_norm` source-rule calls with
reference evaluation and validated sharing. Cache validation and surface
conversion are inside the VM measurements; candidate collection occurs before
timing. Each positive theorem needs `Qed`, a fresh `.vo`, empty assumptions and
independent kernel checking. This synthetic repeated-rule component does not
measure a full proof trace or predict end-to-end tactic performance.

The runners retain raw logs, generated measurement sources, tool versions,
source hashes, exit statuses and JSON summaries. VM evaluation, proof-producing
reduction, reflexivity and `Qed` have separate timing boundaries; process wall
time and independent kernel checks are outside those VM measurements. Very
small timings may round to zero; increase repeats and use several rounds on an
idle machine. Results directories must be new to prevent stale artifact reuse.

These microbenchmarks isolate checking costs. They do not measure solver time,
certificate production/search, tactic preprocessing, or end-to-end performance
against Lean-SMT, Logos or Sledgehammer. A fair comparison needs matching inputs,
acceptance requirements, timing boundaries, versions and machine resources.

## Library boundary and trust

`EunoiaScopedAdapter.checker` consumes authoritative typed tables, root terms,
root claims, a scoped trace, and local semantic witnesses. Its correctness theorem
connects successful checking to the existing SMTCoq interpretation. Generated
`CpcGenerated.derive` computes rule conclusions from signature data; its result
alone cannot authorize a semantic inference.

The public Rocq namespaces remain `SMTCoq.*` to preserve the original proofs and
make future upstream integration straightforward. These sources are bundled;
there is no external SMTCoq dependency. Because namespaces overlap, do not load
both separately installed copies in the same Rocq session.

The OCaml reader parses CPC syntax, but **there is no general `verify file.cpc`
semantic CLI** in this extraction. Checking raw cvc5 output end to end still
requires constructing authoritative tables and local certificates; that producer
and the public tactic remain in SMTRocq. The semantic benchmark supplies fixed
certificates directly, isolating the checked library from production/search.

No proof body or axiom was added during extraction. The source-computation
proofs are closed under the global context. Semantic correctness retains the
upstream primitive-integer and proof-irrelevance assumption baseline, listed in
[docs/eunoia/baseline-assumptions.txt](docs/eunoia/baseline-assumptions.txt).
Bundled compatibility sources also contain existing declarations such as
`PArray.array_ext`; its presence does not mean a measured theorem depends on it.
The benchmark audits actual theorem dependencies and rejects names outside the
baseline. This repository does not claim axiom-free semantic checking.

See [tools/eunoia/INTERFACE.md](tools/eunoia/INTERFACE.md) for the generated/runtime
boundary. The tested scope is a bounded UF/LIA fragment; purification, Boolean
constant arguments, and Real/cast intermediates retain the upstream limitations.

## License and provenance

SMTCoq-derived code retains its CeCILL-C license and copyright notices; see
[LICENSE](LICENSE). Pinned cvc5 Eunoia signatures retain their own upstream notices
and provenance under `tools/eunoia/signatures`. Historical validation documents
describe the original SMTRocq environment; use the commands above for this repo.

The signature-specialized helper evaluator is included with exact computation
refinement proofs and all 32 captured source replays. See upstream measurements
before interpreting component timings as tactic improvements.

Direct signature compilation is included with proved reference fallbacks and
flat, scoped, and shared checker adapters. Its source profiler and repeated-rule
runner are separate from tactic measurements.

For the repeated complete source-rule diagnostic:

```sh
python3 benchmarks/direct_helpers.py --output /tmp/eunoia-direct-rules --rounds 3
```

It alternates ordering between fresh rounds, compares reference and direct
execution at 1,000 and 3,000 calls, and records VM and `Qed` separately. Every
round requires closed proofs and an independent kernel check. These are source
computation costs, separate from the complete semantic checker and tactic.
Use `--interpreter direct` in the actual-trace source profiler for captured CPC
workloads instead of repeated copies of one rule input.

Signature alias conversion now uses precomputed indexes with closed pointwise
refinement proofs. The source rules and supported fragment are unchanged.

Source-term application equality now short-circuits after an unequal function
subtree, with a closed definitional-refinement proof. Matched upstream tactic
timings tracked control variation and do not establish an additional tactic
speedup. See [validation](docs/validation.md) for the standalone checks.

The extraction includes all 59 compiled helpers with modular case proofs, and
87 individually proved rule implementations for proof-specific registries.
These are experimental execution paths; upstream tactic comparisons have not
established a speedup. Standalone source timings remain distinct from tactic timings.

To time the compiled rule registry on captured source proofs, use
`python3 tools/eunoia-runtime-profile/profile.py --interpreter specialized --output /tmp/eunoia-specialized-source`. Each fixture selects its own used-rule registry.
This measures source replay, with no solver or tactic invocation.

The indexed model encoder reuses the bundled SMTCoq atom/formula tables to
compute Eunoia encodings once. `EunoiaModelDagCheck.checker_refinement` proves
that the complete checker returns exactly the original result for every input;
generated source rules, bindings, scopes and semantic gates remain checked.
The fixed benchmark also includes scoped shared/inline examples and corruption
controls from this checker. These small standalone fixtures validate the
measurement path; upstream tactic improvements are reported separately.
