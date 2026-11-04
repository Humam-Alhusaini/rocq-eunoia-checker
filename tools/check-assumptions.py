#!/usr/bin/env python3
"""Audit the semantic correctness boundary against the inherited baseline."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bench", ROOT / "benchmarks/run.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    command = [sys.executable, "-B", str(ROOT / "tools/audit-eunoia-assumptions.py"),
               "--build-loadpaths", "--output-dir", str(args.output.resolve())]
    flags = bench.loadpaths()
    for index in range(0, len(flags), 3):
        command += ["--loadpath", flags[index + 1], flags[index + 2]]
    for module, theorems in {
        "EunoiaHelperCache": ["checker_refinement", "checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EoCheckedMemo": ["key_eqb_equivalence", "evaluate_cached_refinement", "validate_entries_sound", "checked_evaluate_correct"],
        "EoRuleMemo": ["run_rule_cached_refinement", "run_surface_cached_refinement"],
        "EunoiaMemo": ["gate_correct", "checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaAdapter": ["memo_encoding_refinement", "cached_eval_with_refinement", "prepared_eval_with_refinement"],
        "EunoiaIntegerEmbedding": ["normalize_ordinary", "fraction_eq_cross", "fraction_le_cross",
          "fraction_lt_cross", "floor_integer", "fraction_add", "fraction_mul", "fraction_neg"],
        "EunoiaDivision": ["positive_laws", "negative_laws", "zero_laws", "positive_division_shift",
          "positive_modulo_shift", "negative_division_shift", "negative_modulo_shift", "nested_positive_positive",
          "nested_negative_positive", "eqb_swap", "quotient_value", "remainder_value",
          "boolean_eq_true", "boolean_true_eq"],
        "EunoiaScopedAdapter": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaLocal": ["execute_valid", "run_valid", "gate_correct"],
        "EunoiaTactic": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
    }.items():
        prefix = "SMTCoq.checker.eunoia." + module
        command += ["--import", prefix]
        for theorem in theorems:
            command += ["--theorem", prefix + "." + module + "." + theorem]
    module = "SMTCoq.checker.eunoia.CpcMemo"
    command += ["--import", module]
    for theorem in ("validate_context_sound", "derive_context_cached_refinement", "derive_checked_correct"):
        command += ["--theorem", module + "." + theorem]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
