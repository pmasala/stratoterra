#!/usr/bin/env python3
"""
Stratoterra — Master Test Runner
Discovers all test_*.py modules under tests/scripts/, runs them via unittest,
and writes a JSON report to tests/reports/test_report_{date}.json.

Usage:
    python tests/scripts/run_all_tests.py
    python tests/scripts/run_all_tests.py --output /path/to/report.json
    python tests/scripts/run_all_tests.py --verbose
"""

import json
import os
import sys
import unittest
import datetime
import argparse
import importlib.util
import traceback
import io

# ---------------------------------------------------------------------------
# Path setup — ensure repo root is on sys.path so test modules can import helpers
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "tests", "scripts")
REPORTS_DIR = os.path.join(REPO_ROOT, "tests", "reports")

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


# ---------------------------------------------------------------------------
# Test discovery
# ---------------------------------------------------------------------------

def discover_test_modules():
    """Return sorted list of test_*.py file paths in the scripts directory."""
    modules = []
    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if fname.startswith("test_") and fname.endswith(".py"):
            modules.append(os.path.join(SCRIPTS_DIR, fname))
    return modules


def load_module_from_path(path):
    """Dynamically load a Python module from a file path."""
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Result collection
# ---------------------------------------------------------------------------

class DetailedTextResult(unittest.TextTestResult):
    """Extended result that captures per-test detail for the JSON report."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_details = []

    def startTest(self, test):
        super().startTest(test)
        self._current_start = datetime.datetime.utcnow()

    def _record(self, test, status, message=""):
        elapsed = (
            (datetime.datetime.utcnow() - self._current_start).total_seconds()
            if hasattr(self, "_current_start")
            else 0.0
        )
        self.test_details.append({
            "test_id": test.id(),
            "class": type(test).__name__,
            "method": test._testMethodName,
            "description": test.shortDescription() or "",
            "status": status,
            "message": message,
            "elapsed_seconds": round(elapsed, 3),
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        msg = self._exc_info_to_string(err, test)
        self._record(test, "FAIL", msg)

    def addError(self, test, err):
        super().addError(test, err)
        msg = self._exc_info_to_string(err, test)
        self._record(test, "ERROR", msg)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._record(test, "EXPECTED_FAILURE")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._record(test, "UNEXPECTED_SUCCESS")


# ---------------------------------------------------------------------------
# Module-level runner
# ---------------------------------------------------------------------------

def run_module(path, verbosity=1):
    """
    Load and run all tests in a single module file.
    Returns (suite_result, test_detail_list, module_error_str_or_None).
    """
    module_name = os.path.splitext(os.path.basename(path))[0]

    # Load module
    try:
        module = load_module_from_path(path)
    except Exception:
        tb = traceback.format_exc()
        return None, [], tb

    # Build suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)

    # Run with capturing output
    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=verbosity,
        resultclass=DetailedTextResult,
    )
    result = runner.run(suite)
    return result, result.test_details, None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(module_runs, run_start, run_end):
    """
    Build the JSON-serializable report dict.

    module_runs: list of {
        "module": filename,
        "result": unittest.TestResult or None,
        "details": list of per-test dicts,
        "load_error": str or None,
    }
    """
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    all_failures = []

    module_summaries = []
    all_test_details = []

    for run in module_runs:
        module_name = run["module"]
        result = run["result"]
        load_error = run["load_error"]
        details = run["details"]

        if load_error:
            module_summaries.append({
                "module": module_name,
                "status": "LOAD_ERROR",
                "load_error": load_error,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
            })
            all_failures.append({
                "module": module_name,
                "type": "LOAD_ERROR",
                "message": load_error,
            })
            continue

        m_passed = sum(1 for d in details if d["status"] == "PASS")
        m_failed = sum(1 for d in details if d["status"] == "FAIL")
        m_errors = sum(1 for d in details if d["status"] == "ERROR")
        m_skipped = sum(1 for d in details if d["status"] == "SKIP")
        m_run = result.testsRun if result else 0

        total_tests += m_run
        total_passed += m_passed
        total_failed += m_failed
        total_errors += m_errors
        total_skipped += m_skipped

        for d in details:
            if d["status"] in ("FAIL", "ERROR"):
                all_failures.append({
                    "module": module_name,
                    "test": d["test_id"],
                    "type": d["status"],
                    "message": d["message"],
                })

        module_status = (
            "PASS" if (m_failed == 0 and m_errors == 0) else "FAIL"
        )
        module_summaries.append({
            "module": module_name,
            "status": module_status,
            "tests_run": m_run,
            "passed": m_passed,
            "failed": m_failed,
            "errors": m_errors,
            "skipped": m_skipped,
        })

        for d in details:
            d["module"] = module_name
        all_test_details.extend(details)

    overall_status = "PASS" if (total_failed == 0 and total_errors == 0) else "FAIL"

    return {
        "schema_version": "1.0",
        "run_start": run_start.isoformat() + "Z",
        "run_end": run_end.isoformat() + "Z",
        "elapsed_seconds": round((run_end - run_start).total_seconds(), 2),
        "overall_status": overall_status,
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "skipped": total_skipped,
            "modules_run": len(module_runs),
        },
        "failures": all_failures,
        "modules": module_summaries,
        "test_details": all_test_details,
    }


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_summary(report):
    s = report["summary"]
    status = report["overall_status"]
    status_label = "PASSED" if status == "PASS" else "FAILED"
    bar = "=" * 65

    print(bar)
    print(f"  Stratoterra Test Suite — {status_label}")
    print(bar)
    print(f"  Run started : {report['run_start']}")
    print(f"  Elapsed     : {report['elapsed_seconds']}s")
    print(f"  Total tests : {s['total_tests']}")
    print(f"  Passed      : {s['passed']}")
    print(f"  Failed      : {s['failed']}")
    print(f"  Errors      : {s['errors']}")
    print(f"  Skipped     : {s['skipped']}")
    print(bar)

    # Per-module table
    print(f"  {'MODULE':<45} {'STATUS':<8} {'PASS':>5} {'FAIL':>5} {'ERR':>5} {'SKIP':>5}")
    print(f"  {'-'*45} {'-'*8} {'-'*5} {'-'*5} {'-'*5} {'-'*5}")
    for m in report["modules"]:
        print(
            f"  {m['module']:<45} {m['status']:<8} "
            f"{m['passed']:>5} {m['failed']:>5} {m['errors']:>5} {m['skipped']:>5}"
        )

    if report["failures"]:
        print()
        print("  FAILURES / ERRORS:")
        print("  " + "-" * 63)
        for f in report["failures"]:
            label = f.get("test") or f.get("module")
            print(f"  [{f['type']}] {label}")
            # Print first 5 lines of the message
            lines = f["message"].strip().splitlines()[:5]
            for line in lines:
                print(f"    {line}")
            if len(f["message"].strip().splitlines()) > 5:
                print("    ... (see report file for full details)")

    print(bar)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Stratoterra master test runner",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path for the JSON report (default: tests/reports/test_report_{date}.json)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose test output",
    )
    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1

    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Determine output path
    today = datetime.date.today().isoformat()
    output_path = args.output or os.path.join(
        REPORTS_DIR, f"test_report_{today}.json"
    )

    # Discover modules
    module_paths = discover_test_modules()
    if not module_paths:
        print("[ERROR] No test_*.py modules found in", SCRIPTS_DIR)
        sys.exit(2)

    print(f"Discovered {len(module_paths)} test module(s):")
    for p in module_paths:
        print(f"  {os.path.basename(p)}")
    print()

    run_start = datetime.datetime.utcnow()

    module_runs = []
    for path in module_paths:
        module_name = os.path.basename(path)
        if args.verbose:
            print(f"--- Running {module_name} ---")
        result, details, load_error = run_module(path, verbosity=verbosity)
        module_runs.append({
            "module": module_name,
            "result": result,
            "details": details,
            "load_error": load_error,
        })

    run_end = datetime.datetime.utcnow()

    # Build report
    report = build_report(module_runs, run_start, run_end)

    # Write report
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    # Print summary
    print_summary(report)
    print(f"Full report written to: {output_path}")
    print()

    # Exit code: 0 = all passed, 1 = failures exist, 2 = runner error
    sys.exit(0 if report["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
