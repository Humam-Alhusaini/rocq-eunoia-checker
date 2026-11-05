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
        "EunoiaProgramIndexFlat": ["flat_step_ext", "flat_run_ext", "flat_checker_ext", "checker_refinement", "checker_correct", "checker_b_refinement", "checker_b_correct", "checker_eq_refinement", "checker_eq_correct"],
        "EunoiaProgramIndexScoped": ["checker_refinement", "checker_correct", "checker_b_refinement", "checker_b_correct", "checker_eq_refinement", "checker_eq_correct"],
        "EoRename": ["refinement"],
        'EoDirect': ['compile_refinement', 'run_program_correct', 'call_compiled_correct'],
        'CpcDirect': ['dispatch_correct'],
        'CpcDirectEntry': ['choose_correct', 'dispatch_correct'],
        'CpcDirectEval': ['evaluate_correct'],
        'CpcDirectRules': ['run_rule_correct', 'run_surface_correct', 'derive_context_correct'],
        'EunoiaDirect': ['checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        'EunoiaDirectFlat': ['flat_step_ext', 'flat_run_ext', 'flat_checker_ext', 'checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        'EunoiaDirectScoped': ['checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        'EoStaged': ['compile_refinement'],
        'EoFuelLayers': ['fetch_make', 'make_correct'],
        'EoCompiledPrograms': ['execute_correct'],
        'CpcStaged': ['execute_correct'],
        'CpcStagedEval': ['evaluate_correct'],
        'CpcStagedRules': ['run_rule_correct', 'run_surface_correct', 'derive_prepared_correct'],
        'EunoiaStaged': ['checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        "EunoiaProgramIndex": ["checker_refinement", "checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EoNameIndex": ["lookup_insert", "lookup_from_list"],
        "EoIndexed": ["evaluate_indexed_refinement", "run_rule_refinement", "run_surface_refinement"],
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
    module = "SMTCoq.checker.eunoia.CpcIndexed"
    command += ["--import", module]
    for theorem in ("program_lookup_correct", "derive_context_with_index_refinement",
                    "derive_indexed_refinement", "derive_assuming_indexed_refinement"):
        command += ["--theorem", module + "." + theorem]
    command += ["--import", "SMTCoq.checker.eunoia.CpcGenerated",
                "--theorem", "SMTCoq.checker.eunoia.CpcGenerated.cpc_canonicalize_correct",
                "--theorem", "SMTCoq.checker.eunoia.CpcGenerated.cpc_surface_correct"]
    command += ["--import", "SMTCoq.checker.eunoia.EoSyntax",
                "--theorem", "SMTCoq.checker.eunoia.EoSyntax.term_eqb_refinement"]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
