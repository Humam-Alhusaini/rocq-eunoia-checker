#!/usr/bin/env python3
"""Audit the semantic correctness boundary against the inherited baseline."""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bench", ROOT / "benchmarks/run.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900,
                        help="independent audit deadline in seconds")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("timeout must be positive")
    command = [sys.executable, "-B", str(ROOT / "tools/audit-eunoia-assumptions.py"),
               "--build-loadpaths", "--output-dir", str(args.output.resolve())]
    flags = bench.loadpaths()
    for index in range(0, len(flags), 3):
        command += ["--loadpath", flags[index + 1], flags[index + 2]]
    for module, theorems in {
        "EoModelDagCache": ["run_correct", "compile_correct", "cached_correct"],
        "EunoiaModelDag": ["body_reference", "prepare_valid", "encode_literal_cached_correct", "encoding_entries_refinement"],
        "EunoiaModelDagCheck": ["checker_refinement", "checker_correct", "checker_b_refinement", "checker_b_correct", "checker_eq_refinement", "checker_eq_correct"],
        'EoSpecialized': ['prepare_one_correct', 'prepare_one_ext', 'find_key', 'run_using_correct', 'run_surface_correct', 'derive_context_correct'],
        'EunoiaSpecialized': ['checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        'EunoiaSpecializedFlat': ['flat_step_ext', 'flat_run_ext', 'flat_checker_ext', 'checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
        'EunoiaSpecializedScoped': ['checker_refinement', 'checker_correct', 'checker_b_refinement', 'checker_b_correct', 'checker_eq_refinement', 'checker_eq_correct'],
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
        "EunoiaCertificate": ["checker_tables", "checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaMemo": ["gate_correct", "checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaAdapter": ["memo_encoding_refinement", "cached_eval_with_refinement", "prepared_eval_with_refinement"],
        "EunoiaIntegerEmbedding": ["normalize_ordinary", "fraction_eq_cross", "fraction_le_cross",
          "fraction_lt_cross", "floor_integer", "fraction_add", "fraction_mul", "fraction_neg"],
        "EunoiaIntegerFacts": ["abs_laws", "min_laws", "max_laws", "sign_laws",
          "symbolic_positive_modulo", "symbolic_negative_modulo", "symbolic_zero_division",
          "known_quotient_divisor", "known_remainder_divisor"],
        "EunoiaDivision": ["positive_laws", "negative_laws", "zero_laws", "positive_division_shift",
          "positive_modulo_shift", "negative_division_shift", "negative_modulo_shift", "nested_positive_positive",
          "nested_negative_positive", "eqb_swap", "quotient_value", "remainder_value",
          "boolean_eq_true", "boolean_true_eq"],
        "EunoiaScopedAdapter": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaLocal": ["execute_valid", "run_valid", "gate_correct", "array_clause_valid", "execute_array_binding"],
        "EunoiaLocalDirect": ["gate_correct"],
        "EunoiaTheory": ["units_exact", "units_valid", "negations_false",
                         "implication_correct", "checked_clause_correct",
                         "global_gate_correct", "gate_correct"],
        "EunoiaTactic": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
    }.items():
        prefix = "SMTCoq.checker.eunoia." + module
        command += ["--import", prefix]
        for theorem in theorems:
            command += ["--theorem", prefix + "." + module + "." + theorem]
    for test_module in ("EunoiaArrayTests", "EunoiaModelDagTests", "EunoiaLocalDirectTests", "EunoiaTheoryTests", "EunoiaCertificateTests"):
        module = "SMTCoq.checker.eunoia." + test_module
        command += ["--import", module]
        for theorem in re.findall(r"^\s*(?:Example|Theorem|Lemma)\s+(\w+)",
                (ROOT / "theories/checker/eunoia" / (test_module + ".v")).read_text(), re.M):
            command += ["--theorem", module + ("." + test_module if test_module in ("EunoiaArrayTests", "EunoiaLocalDirectTests", "EunoiaTheoryTests", "EunoiaCertificateTests") else "") + "." + theorem]
    module = "SMTCoq.checker.eunoia.CpcSpecialized"
    command += ["--import", module]
    command += ["--theorem", module + ".CpcSpecialized.rules_correct"]
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
    command += ["--import", "SMTCoq.utils.PArray", "--theorem", "SMTCoq.utils.PArray.IntOrderedType.compare_gt"]
    proc = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    try:
        code = proc.wait(timeout=args.timeout)
    except BaseException:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
        raise
    if code:
        raise subprocess.CalledProcessError(code, command)


if __name__ == "__main__":
    main()
