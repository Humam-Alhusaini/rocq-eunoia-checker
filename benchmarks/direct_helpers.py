#!/usr/bin/env python3
"""Measure complete source-rule calls through reference and direct helpers.

No solver, tactic or certificate search; typing, surface conversion, evaluation
and Qed are measured, with fresh closed proofs and independent kernel checks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.get("EUNOIA_ENV", str(ROOT / "tools/rocq-env"))
MODULES = ('EoSyntax', 'EoRuntime', 'EoArithmetic', 'EoOrder', 'EoNameIndex', 'EoRename', 'CpcGenerated', 'EoCheckedMemo', 'EoRuleMemo', 'CpcMemo', 'EoMemoCollector', 'EoDirect', 'CpcDirect', 'CpcDirectEntry', 'CpcDirectEval', 'CpcDirectRules', 'TraceReplay', 'LiaTraceReplay')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=600)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents or args.rounds < 1 or args.timeout <= 0:
        parser.error("choose a new external output directory and positive rounds/timeout")
    out.mkdir(parents=True)
    flags = ["-Q", ".", "SMTCoq.checker.eunoia"]
    summary = dict(passed=False, layer="complete source-rule component; no solver or certificate search",
                   git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   git_status=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                   runner_sha256=digest(Path(__file__)), modules={}, commands=[], timings=[])

    def save():
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    def run(name, command):
        started = time.monotonic()
        with (out / (name + ".log")).open("w") as log:
            try:
                result = subprocess.run([ENV, *command], cwd=out, text=True, stdout=log,
                                        stderr=subprocess.STDOUT, timeout=args.timeout)
                code, timed_out = result.returncode, False
            except subprocess.TimeoutExpired:
                code, timed_out = 124, True
        summary["commands"].append(dict(name=name, argv=[ENV, *command], exit_code=code,
                                        timeout=timed_out, process_wall_s=time.monotonic() - started))
        save()
        if code:
            raise RuntimeError(name + " failed; inspect " + str(out / (name + ".log")))
        return (out / (name + ".log")).read_text()

    try:
        run("version", ["rocq", "--version"])
        for module in MODULES:
            base = "tools/eunoia/tests" if module in ("TraceReplay", "LiaTraceReplay") else "theories/checker/eunoia"
            source = ROOT / base / (module + ".v")
            shutil.copy2(source, out / source.name)
            summary["modules"][module] = digest(source)
            run(module, ["rocq", "compile", "-q", *flags, module + ".v"])
        template = ROOT / "tools/eunoia/tests/DirectHelpersBench.v"
        summary["template_sha256"] = digest(template)
        prefix, *blocks = template.read_text().split("\nGoal ")
        assert len(blocks) == 4
        for round_number in range(args.rounds):
            source = prefix
            ordered = blocks if round_number % 2 == 0 else list(reversed(blocks))
            for block in ordered:
                count = re.match(r"expected (\d+)", block)[1]
                mode = "reference" if "(reference" in block else "direct"
                label = mode + "_" + count
                block = block.replace("Proof. Time vm_compute.",
                                      'Proof. idtac "PROFILE ' + label + ' vm". Time vm_compute.')
                block = block.replace("reflexivity. Time Qed.",
                                      'idtac "PROFILE ' + label + ' qed". reflexivity. Time Qed.')
                source += "\nExample " + label + " : " + block + "\nPrint Assumptions " + label + ".\n"
            module = "DirectProfile" + str(round_number)
            (out / (module + ".v")).write_text(source)
            log = run(module, ["rocq", "compile", "-q", *flags, module + ".v"])
            if log.count("Closed under the global context") != 4 or not (out / (module + ".vo")).is_file():
                raise RuntimeError("missing fresh proof artifact or nonempty theorem assumptions")
            label = None
            for line in log.splitlines():
                if line.startswith("PROFILE "):
                    _, case, phase = line.split()
                    label = case, phase
                match = re.match(r"Finished transaction in ([\d.]+) secs", line)
                if match and label:
                    summary["timings"].append(dict(round=round_number, case=label[0], phase=label[1],
                                                   wall_s=float(match[1])))
                    label = None
            if len(summary["timings"]) != 8 * (round_number + 1):
                raise RuntimeError("missing or unparsed VM/Qed timing")
            run(module + "-kernel", ["rocq", "check", "-silent", *flags,
                                     "SMTCoq.checker.eunoia." + module])
        summary["passed"] = True
    finally:
        save()
    print(out / "summary.json")


if __name__ == "__main__":
    main()
