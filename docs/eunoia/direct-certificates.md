# Direct local certificates (experimental)

`EunoiaLocalDirect` checks a derivation of the exact conclusion clause from the
exact ordered premise clauses. It reuses `EunoiaLocal.witness`, its root loader,
and its strict SMTCoq command executor. The record's `conflict` field identifies
the output clause in this mode. The original refutation gate instead loads the
premises and negated conclusion, then checks an empty clause.

`gate_correct` proves that an accepted direct certificate establishes the
conclusion from the premises under SMTCoq's existing interpretation. The gate
checks the final clause, all roots, bounds, fresh outputs and every command,
including unused commands after the requested output was derived. Unsupported
operations cannot succeed through SMTCoq's true-clause fallback.

`EunoiaMemo.Direct` selects this gate for a source occurrence. The existing
`Inline` and `Cached` constructors retain their meanings. Direct certificates
are checked inline; the legacy semantic cache still validates all its entries,
including unused ones. Full generated CPC evaluation, exact source bindings,
roots, scope discharge and steps after a conflict remain checked.

Set `EUNOIA_DIRECT_CERTIFICATES=1` to try bounded direct derivations in the public
tactic. Failed searches fall back to the original refutation search. Candidate
search and slicing are untrusted: slicing only removes unused local search
commands before submission, never CPC source steps. The gate checks every
submitted command. The default remains the original producer while comparative
performance is evaluated. This option is separate from
`EUNOIA_DIRECT_PROGRAMS`, which selects compiled signature helper execution.

The eleven fixed Rocq examples exercise exact premise identity, a changed
conclusion, missing/extra premises, explicit truth, an invalid unused command,
a true-clause fallback, output bounds, a complete generated scoped proof,
an unsupported source step after conflict, and semantic soundness.

No axioms or admissions are added. Correctness inherits SMTCoq's existing UInt63
and proof-irrelevance baseline.

Validation and timing results are recorded in
[the upstream November 8 checkpoint](https://github.com/Humam-Alhusaini/SMTRocq/blob/smtrocq/cvc5-eunoia/docs/eunoia/direct-certificates-2026-11-08.md).

In this extraction, candidate search is not included. Benchmark the fixed full
source-checker fixture and its rejection controls independently:

```sh
python3 -B benchmarks/run.py --output /tmp/eunoia-direct \
  --case complete_generated_source_checker_accepts \
  --case altered_conclusion_rejected \
  --case invalid_unused_command_rejected \
  --case invalid_true_fallback_rejected \
  --timeout 30 --kernel-timeout 900
```

The compiler and recursive kernel deadlines are separate and recorded per
command. These component timings do not include a solver or native tactic.
