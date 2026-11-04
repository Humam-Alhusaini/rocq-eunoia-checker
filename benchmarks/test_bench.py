import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checker_bench", HERE / "run.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
report_spec = importlib.util.spec_from_file_location("checker_report", HERE / "report.py")
report = importlib.util.module_from_spec(report_spec)
report_spec.loader.exec_module(report)


class MeasurementTests(unittest.TestCase):
    def test_actual_rocq_timing_formats(self):
        for prefix in ("Finished", "Completed successfully"):
            log = "\n".join([
                "BENCH repeated_vm", f"{prefix} transaction in 1. secs (0.9u,0.1s) (successful)",
                "BENCH proof_vm", f"{prefix} transaction in 0.2 secs (0.1u,0.s)",
                "BENCH reflexivity", f"{prefix} transaction in 0. secs (0.u,0.s)",
                f"{prefix} transaction in 0.01 secs (0.01u,0.s)"])
            result = bench.timings(log, 10)
            self.assertEqual(result["repeated_vm"]["cpu_s_per_evaluation"], 0.1)
            self.assertEqual(result["qed"]["evaluations"], 1)

    def test_missing_qed_is_not_a_successful_measurement(self):
        with self.assertRaises(ValueError):
            bench.timings("BENCH repeated_vm\nFinished transaction in 1. secs (1.u,0.s)", 1)

    def test_duplicate_phase_is_rejected(self):
        with self.assertRaises(ValueError):
            bench.timings("BENCH proof_vm\nFinished transaction in 1. secs (1.u,0.s)\n" * 2, 1)

    def test_failed_or_unchecked_run_has_no_table(self):
        for passed, checked in ((False, 1), (True, 0)):
            with self.assertRaises(ValueError):
                report.report(dict(rounds=1, cases=[{}], results=[{}], commands=[],
                                   passed=passed, kernel_checked_results=checked))

    def test_cases_are_existing_positive_and_rejection_examples(self):
        cases = json.loads((HERE / "cases.json").read_text())
        self.assertEqual(len({c["example"] for c in cases}), len(cases))
        for case in cases:
            expression, expected = bench.proposition(case)
            self.assertTrue(expression.strip())
            if case["layer"] == "rejection-control":
                self.assertEqual(expected.strip(), "false")


if __name__ == "__main__":
    unittest.main()
