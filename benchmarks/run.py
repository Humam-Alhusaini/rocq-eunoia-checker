#!/usr/bin/env python3
"""Benchmark fixed source/semantic certificates, without a solver, tactic, or search."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import signal
import statistics
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
TIMING = re.compile(r"(?:Finished|Completed)(?: (?:successfully|failing))? transaction in "
                    r"([0-9.]+) secs? \(([0-9.]+)u,([0-9.]+)s\)")
PHASES = ("repeated_vm", "proof_vm", "reflexivity", "qed")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proposition(case):
    path = ROOT / "theories/checker/eunoia" / (case["module"] + ".v")
    match = re.search(r"^\s*Example " + re.escape(case["example"]) + r"\s*:\s*(.*?)\.\s*Proof\.",
                      path.read_text(), re.M | re.S)
    if not match:
        raise ValueError(f"missing existing example: {case['example']}")
    # New checker fixtures need not put spaces around their final Boolean
    # equality. Retain the existing non-Boolean fixture syntax as well.
    equality = re.fullmatch(r"(.*)\s*=\s*(true|false)\s*", match[1], re.S)
    if equality is not None:
        return equality[1], equality[2]
    expression, expected = match[1].rsplit(" = ", 1)
    return expression, expected


def source(case, repeats, audit):
    expression, expected = proposition(case)
    return f'''Module BenchScope.
From Stdlib Require Import List String Bool Uint63 ZArith ZMicromega RingMicromega EnvRing.
From SMTCoq.utils Require Import PArray.
From SMTCoq.checker.fol Require Import State Terms.
From SMTCoq.checker Require Import MainChecker.
From SMTCoq.checker.small_checker.euf Require Import EUF.
From SMTCoq.checker.eunoia Require Import EunoiaScopedAdapter EunoiaLia EunoiaScope EunoiaMemo EunoiaTheory {case["module"]}.
Import Atom EunoiaLia.
Import ListNotations.
Import SMTCoq.checker.eunoia.{case["module"]}{"." + case["scope"] if case["scope"] else ""}.
Local Open Scope uint63_scope.
Local Open Scope array_scope.
Local Open Scope string_scope.
Example measured : ({expression}) = ({expected}).
Proof.
  idtac "BENCH repeated_vm".
  Time do {repeats} (let actual := eval vm_compute in ({expression}) in
    let expected := eval vm_compute in ({expected}) in constr_eq actual expected).
  idtac "BENCH proof_vm". Time vm_compute.
  idtac "BENCH reflexivity". Time reflexivity.
Time Qed.
End BenchScope.
Redirect "{audit.as_posix()}" Print Assumptions BenchScope.measured.
'''


def timings(log, repeats):
    result, phase = {}, None
    for line in log.splitlines():
        if line.startswith("BENCH "):
            phase = line.split()[1]
        match = TIMING.search(line)
        if match and phase:
            if phase in result:
                raise ValueError(f"duplicate timing phase {phase}")
            wall, user, system = map(float, match.groups())
            count = repeats if phase == "repeated_vm" else 1
            result[phase] = dict(wall_s=wall, user_s=user, system_s=system,
                                 evaluations=count, cpu_s_per_evaluation=(user + system) / count)
            phase = "qed" if phase == "reflexivity" else None
    if set(result) != set(PHASES):
        raise ValueError(f"incomplete timing output: {sorted(result)}")
    return result


def loadpaths():
    flags = []
    for path in sorted((ROOT / "theories").rglob("dune")):
        match = re.search(r"\(name\s+(SMTCoq[\w.]*)\)", path.read_text())
        if match:
            flags += ["-Q", str(ROOT / "_build/default" / path.parent.relative_to(ROOT)), match[1]]
    return flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new artifact directory")
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=30, help="whole-compiler deadline per measured case")
    parser.add_argument("--build-timeout", type=int, default=300)
    parser.add_argument("--kernel-timeout", type=int, default=900, help="separate recursive kernel-check deadline")
    parser.add_argument("--case", action="append", help="existing example name; repeatable")
    parser.add_argument("--env", type=Path, default=Path(os.environ.get("EUNOIA_ENV", ROOT / "tools/rocq-env")))
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    if min(args.repeats, args.rounds, args.jobs, args.timeout, args.build_timeout, args.kernel_timeout) < 1:
        parser.error("counts and timeout must be positive")
    out = args.output.resolve()
    if out.exists() or '"' in str(out) or "\n" in str(out):
        parser.error("--output must be a new directory without quotes or newlines")
    cases = json.loads((HERE / "cases.json").read_text())
    if args.case:
        unknown = set(args.case) - {c["example"] for c in cases}
        if unknown:
            parser.error(f"unknown cases: {sorted(unknown)}")
        cases = [c for c in cases if c["example"] in args.case]
    out.mkdir(parents=True)
    env = str(args.env.resolve())
    summary = dict(passed=False, scope="fixed checker inputs; per-case source/semantic layers; no solver/tactic/search",
                   repeats=args.repeats, rounds=args.rounds, cases=cases,
                   platform=platform.platform(), cpu_count=os.cpu_count(), commands=[], results=[],
                   git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   git_status=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                   source_hashes={str(p.relative_to(ROOT)): digest(p) for base in ("theories", "benchmarks")
                                  for p in (ROOT / base).rglob("*") if p.suffix in (".v", ".py", ".json")})
    cgroup = Path("/sys/fs/cgroup/cpu.max")
    summary["cpu_max"] = cgroup.read_text().strip() if cgroup.exists() else None

    def save():
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    def run(argv, stem, cwd=out, timeout=None):
        timeout = args.timeout if timeout is None else timeout
        start = time.monotonic()
        with (out / (stem + ".log")).open("w") as log:
            proc = subprocess.Popen(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                proc.wait(timeout=timeout)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                code = 124
            except BaseException:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                raise
        summary["commands"].append(dict(argv=argv, cwd=str(cwd), exit_code=code,
                                        wall_s=time.monotonic() - start, timeout_s=timeout, log=stem + ".log"))
        save()
        if code:
            raise RuntimeError(f"{stem}: exit {code}; see {out / (stem + '.log')}")
        return (out / (stem + ".log")).read_text()

    try:
        summary["version"] = run([env, "rocq", "--version"], "version").strip()
        if not args.skip_build:
            run([env, "dune", "build", "--ignore-promoted-rules", f"-j{args.jobs}", "@install"], "build", ROOT, timeout=args.build_timeout)
        spec = importlib.util.spec_from_file_location("audit", ROOT / "tools/audit-eunoia-assumptions.py")
        audit_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit_module)
        baseline = set((ROOT / "docs/eunoia/baseline-assumptions.txt").read_text().split())
        flags = loadpaths()
        checked_modules = []
        for round_number in range(args.rounds):
            for index, case in enumerate(cases if round_number % 2 == 0 else list(reversed(cases))):
                name = f"Bench{round_number}_{index}"
                audit = out / (name + "-assumptions")
                path = out / (name + ".v")
                path.write_text(source(case, args.repeats, audit))
                log = run([env, "rocq", "compile", "-q", *flags, "-Q", str(out), "StandaloneBench", path.name], name)
                if not path.with_suffix(".vo").is_file():
                    raise RuntimeError("compiler did not produce a fresh .vo")
                dependencies = audit_module.assumptions(audit.with_suffix(".out").read_text())
                if dependencies - baseline:
                    raise RuntimeError(f"unexpected assumptions: {sorted(dependencies - baseline)}")
                checked_modules.append("StandaloneBench." + name)
                summary["results"].append(dict(case=case["example"], layer=case["layer"], round=round_number,
                                               timings=timings(log, args.repeats), assumptions=sorted(dependencies),
                                               source_sha256=digest(path), vo_sha256=digest(path.with_suffix(".vo"))))
                save()
        # One independent recursive kernel process checks every measured module.
        # Its imported theory closure is checked once, rather than per case.
        run([env, "rocq", "check", "-silent", *flags, "-Q", str(out), "StandaloneBench",
             *checked_modules], "kernel", timeout=args.kernel_timeout)
        summary["kernel_checked_results"] = len(checked_modules)
        summary["medians_cpu_s"] = {
            case["example"]: {phase: statistics.median(r["timings"][phase]["cpu_s_per_evaluation"]
                for r in summary["results"] if r["case"] == case["example"]) for phase in PHASES}
            for case in cases}
        summary["passed"] = True
        save()
        print(out / "summary.json")
    except Exception as error:
        summary["error"] = str(error)
        save()
        raise


if __name__ == "__main__":
    main()
