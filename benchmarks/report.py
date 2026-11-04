#!/usr/bin/env python3
"""Print median per-evaluation CPU times from a successful semantic run."""
import argparse
import json
from pathlib import Path


def report(summary):
    expected = summary["rounds"] * len(summary["cases"])
    if (not summary.get("passed") or len(summary["results"]) != expected or
            summary.get("kernel_checked_results") != expected or
            any(c["exit_code"] for c in summary["commands"])):
        raise ValueError("incomplete or failed run; no benchmark table produced")
    lines = ["Median CPU seconds per evaluation; solver/search excluded.", "",
             "| Case | Layer | VM check | Proof VM | Qed |",
             "| --- | --- | ---: | ---: | ---: |"]
    for case in summary["cases"]:
        times = summary["medians_cpu_s"][case["example"]]
        lines.append(f"| {case['example']} | {case['layer']} | "
                     f"{times['repeated_vm']:.6f} | {times['proof_vm']:.6f} | {times['qed']:.6f} |")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    print(report(json.loads(args.summary.read_text())))
