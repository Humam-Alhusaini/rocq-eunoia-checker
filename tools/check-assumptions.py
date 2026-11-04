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
        "EunoiaScopedAdapter": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
        "EunoiaLocal": ["execute_valid", "run_valid", "gate_correct"],
        "EunoiaTactic": ["checker_correct", "checker_b_correct", "checker_eq_correct"],
    }.items():
        prefix = "SMTCoq.checker.eunoia." + module
        command += ["--import", prefix]
        for theorem in theorems:
            command += ["--theorem", prefix + "." + module + "." + theorem]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
