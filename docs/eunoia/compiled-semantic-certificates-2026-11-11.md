# Compiled semantic certificates

`EunoiaCertificate` exposes a small verified certificate checker using the same
SMTCoq interpretation, concrete local/theory gates and scoped trace machine as
the strict CPC backend. Its soundness theorems prove inconsistency of the actual
root clauses and provide Boolean/equality goal wrappers.

This checker certifies an SMT theorem, not conformance of a source CPC proof.
The original signature-generated checkers remain available and unchanged.
An upstream untrusted compiler translates CVC5 proofs into these certificates;
the compiler and public `smtrocq` tactic are not dependencies of this repository.

Every submitted semantic step, all cache entries including unused entries,
actual ordered root claims, typed tables, scope discharge, fresh destinations,
live reads, bounds and the final conflict are checked. A producer may submit a
shorter derivation, but cannot bypass certificate checking. The standalone
fixtures include satisfiable roots with an attempted leak of a local conflict.

The new tests contain seventeen proved examples, including soundness, two
accepted Boolean certificates and fourteen rejection controls. Sixteen of them
are separately labeled in `benchmarks/cases.json` for independent component
measurement. All proof/signature files are byte-identical to the upstream core
recorded in [the manifest](../../provenance/upstream.json).

```sh
make build
make test
python3 -B tools/check-assumptions.py --output /tmp/eunoia-compiled-audit
python3 -B benchmarks/run.py --skip-build --output /tmp/eunoia-compiled \
  --case scoped_refutation --case invalid_unused_entry \
  --case satisfiable_roots_cannot_import_local_conflict --repeats 100 --rounds 3
```

Component runs exclude the solver, tactic, preprocessing and native certificate
search. They do not establish full-tactic performance. No new axiom or admitted
proof is introduced; the inherited UInt63/proof-irrelevance baseline remains.

The final build, 259-target audit and all sixteen fresh component/kernel replays
passed. [Exact validation](compiled-semantic-validation-2026-11-11.json) records
commands, hashes and assumption sets. Timings from this concurrent validation
are not comparative measurements.
