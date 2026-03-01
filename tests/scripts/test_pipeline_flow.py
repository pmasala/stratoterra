"""
Stratoterra Integration Tests — Pipeline Flow Validation
Tests: IT-FLW-001 through IT-FLW-006

Validates that the staging directory contains expected files in the correct
patterns after each pipeline phase, and that data flows correctly between phases.

Run: python3 tests/scripts/test_pipeline_flow.py
"""

import json
import os
import sys
import glob
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
STAGING_DIR = PROJECT_ROOT / "staging"
DATA_DIR = PROJECT_ROOT / "data"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_files(base: Path, pattern: str) -> list[Path]:
    """Find all files matching a glob pattern under base."""
    return sorted(Path(f) for f in glob.glob(str(base / pattern)))


def most_recent(files: list[Path]) -> Path | None:
    """Return the most recently modified file from a list."""
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def is_valid_iso_timestamp(s: str) -> bool:
    """Check if a string is a valid ISO 8601 timestamp."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            datetime.strptime(s, fmt)
            return True
        except (ValueError, TypeError):
            continue
    return False


def is_valid_run_id(s: str) -> bool:
    """Check if run_id matches YYYY-WNN format."""
    import re
    return bool(s and re.match(r"^\d{4}-W\d{2}$", s))


# ---------------------------------------------------------------------------
# IT-FLW-001: Phase 1 Staging Files Exist
# ---------------------------------------------------------------------------
class TestPhase1GatherFiles(unittest.TestCase):
    """IT-FLW-001: Phase 1 output files exist in staging/raw_collected/."""

    EXPECTED_PATTERNS = [
        ("official_stats", "raw_collected/official_stats_*.json"),
        ("financial_data", "raw_collected/financial_data_*.json"),
        ("news_events",    "raw_collected/news_events_*.json"),
        ("trade_sanctions","raw_collected/trade_sanctions_*.json"),
        ("military_conflict","raw_collected/military_conflict_*.json"),
        ("political_regulatory","raw_collected/political_regulatory_*.json"),
    ]

    def _check_phase1_file(self, label: str, pattern: str):
        """Helper to check a Phase 1 file exists and is non-empty."""
        files = find_files(STAGING_DIR, pattern)
        if not files:
            self.skipTest(f"{label}: file not found ({pattern}). Run Phase 1 agents first.")
        latest = most_recent(files)
        size = latest.stat().st_size
        self.assertGreater(size, 50, f"{label}: file exists but is nearly empty ({size} bytes)")

    def test_official_stats_exists(self):
        """IT-FLW-001a: Agent 01 output file exists."""
        self._check_phase1_file("official_stats", "raw_collected/official_stats_*.json")

    def test_financial_data_exists(self):
        """IT-FLW-001b: Agent 02 output file exists."""
        self._check_phase1_file("financial_data", "raw_collected/financial_data_*.json")

    def test_news_events_exists(self):
        """IT-FLW-001c: Agent 03 output file exists."""
        self._check_phase1_file("news_events", "raw_collected/news_events_*.json")

    def test_trade_sanctions_exists(self):
        """IT-FLW-001d: Agent 04 output file exists."""
        self._check_phase1_file("trade_sanctions", "raw_collected/trade_sanctions_*.json")

    def test_military_conflict_exists(self):
        """IT-FLW-001e: Agent 05 output file exists."""
        self._check_phase1_file("military_conflict", "raw_collected/military_conflict_*.json")

    def test_political_regulatory_exists(self):
        """IT-FLW-001f: Agent 06 output file exists."""
        self._check_phase1_file("political_regulatory", "raw_collected/political_regulatory_*.json")

    def test_run_ids_are_consistent(self):
        """IT-FLW-001g: All Phase 1 files share the same run_id."""
        run_ids = set()
        for label, pattern in self.EXPECTED_PATTERNS:
            files = find_files(STAGING_DIR, pattern)
            if not files:
                continue
            try:
                data = load_json(most_recent(files))
                if "run_id" in data:
                    run_ids.add(data["run_id"])
            except Exception:
                pass

        if len(run_ids) > 1:
            self.fail(f"Inconsistent run_ids across Phase 1 files: {run_ids}")

    def test_all_phase1_dates_match(self):
        """IT-FLW-001h: All Phase 1 collection dates match."""
        dates = set()
        for label, pattern in self.EXPECTED_PATTERNS:
            files = find_files(STAGING_DIR, pattern)
            if not files:
                continue
            try:
                data = load_json(most_recent(files))
                date = data.get("collection_date") or data.get("processing_date")
                if date:
                    dates.add(date)
            except Exception:
                pass

        if len(dates) > 1:
            # Allow dates within 1 day (pipeline can span midnight)
            date_objects = []
            for d in dates:
                try:
                    date_objects.append(datetime.strptime(d, "%Y-%m-%d"))
                except ValueError:
                    pass
            if date_objects:
                span = (max(date_objects) - min(date_objects)).days
                self.assertLessEqual(span, 1, f"Phase 1 dates span more than 1 day: {dates}")


# ---------------------------------------------------------------------------
# IT-FLW-002: Phase 2 Staging File Exists
# ---------------------------------------------------------------------------
class TestPhase2ProcessFile(unittest.TestCase):
    """IT-FLW-002: Phase 2 output file exists and references Phase 1 records."""

    @classmethod
    def setUpClass(cls):
        files = find_files(STAGING_DIR, "processed/factor_updates_*.json")
        cls.actual_path = most_recent(files) if files else None
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 07 output not found. Run agents 01-07 first.")

    def test_factor_updates_file_exists(self):
        """IT-FLW-002a: factor_updates file exists and is non-empty."""
        self.assertGreater(
            self.actual_path.stat().st_size, 100,
            "factor_updates file is nearly empty"
        )

    def test_factor_updates_references_phase1(self):
        """IT-FLW-002b: factor_updates summary shows input records > 0."""
        summary = self.actual.get("summary", {})
        total = summary.get("total_input_records", 0)
        self.assertGreater(total, 0, "total_input_records should be > 0 after Phase 1")

    def test_run_id_valid_format(self):
        """IT-FLW-002c: run_id in factor_updates is valid."""
        run_id = self.actual.get("run_id", "")
        self.assertTrue(is_valid_run_id(run_id), f"run_id '{run_id}' not in YYYY-WNN format")

    def test_factor_updates_not_empty(self):
        """IT-FLW-002d: factor_updates list is not empty."""
        updates = self.actual.get("factor_updates", [])
        self.assertGreater(len(updates), 0, "factor_updates should contain at least one update")


# ---------------------------------------------------------------------------
# IT-FLW-003: Phase 3 Validation Files Exist
# ---------------------------------------------------------------------------
class TestPhase3ValidationFiles(unittest.TestCase):
    """IT-FLW-003: Phase 3 output files exist and verdicts are valid."""

    VALID_VERDICTS = {"ACCEPT", "ACCEPT_WITH_NOTE", "FLAG", "REJECT", "ESCALATE"}

    @classmethod
    def setUpClass(cls):
        files = find_files(STAGING_DIR, "validated/validated_updates_*.json")
        cls.actual_path = most_recent(files) if files else None
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 08 output not found. Run agents 01-08 first.")

    def test_validated_updates_exists(self):
        """IT-FLW-003a: validated_updates file exists."""
        self.assertIsNotNone(self.actual_path)
        self.assertGreater(self.actual_path.stat().st_size, 50)

    def test_all_verdicts_valid(self):
        """IT-FLW-003b: All verdict values are in the allowed set."""
        updates = self.actual.get("validated_updates", [])
        invalid = [
            f"update_id={u.get('update_id')}: verdict='{u.get('verdict')}'"
            for u in updates
            if u.get("verdict") not in self.VALID_VERDICTS
        ]
        self.assertEqual(invalid, [], f"Invalid verdict values: {invalid}")

    def test_summary_present(self):
        """IT-FLW-003c: validation summary section is present."""
        summary = self.actual.get("summary", {})
        self.assertIn("total", summary, "summary.total is required")
        self.assertIn("escalate", summary, "summary.escalate is required")

    def test_reject_count_reasonable(self):
        """IT-FLW-003d: Rejection rate < 50% (sanity check)."""
        summary = self.actual.get("summary", {})
        total = summary.get("total", 0)
        rejected = summary.get("reject", 0)
        if total > 0:
            rejection_rate = rejected / total
            self.assertLess(
                rejection_rate, 0.5,
                f"Rejection rate {rejection_rate:.0%} is suspiciously high — check Agent 07 quality"
            )

    def test_escalation_report_if_escalations(self):
        """IT-FLW-003e: If escalations exist, escalation_report file should also exist."""
        summary = self.actual.get("summary", {})
        escalate_count = summary.get("escalate", 0)
        if escalate_count > 0:
            esc_files = find_files(STAGING_DIR, "validated/escalation_report_*.json")
            self.assertGreater(
                len(esc_files), 0,
                f"{escalate_count} escalations noted in summary but escalation_report not found"
            )


# ---------------------------------------------------------------------------
# IT-FLW-004: Phase 4 Integration into /data/
# ---------------------------------------------------------------------------
class TestPhase4Integration(unittest.TestCase):
    """IT-FLW-004: Agent 09 successfully updates /data/ directory."""

    @classmethod
    def setUpClass(cls):
        cls.last_update_path = DATA_DIR / "metadata" / "last_update.json"
        cls.last_update = load_json(cls.last_update_path) if cls.last_update_path.exists() else None
        cls.country_files = find_files(DATA_DIR / "countries", "*.json")

    def test_last_update_exists(self):
        """IT-FLW-004a: data/metadata/last_update.json exists."""
        if not self.last_update_path.exists():
            self.skipTest("last_update.json not found. Run agents 01-09 first.")
        self.assertIsNotNone(self.last_update)

    def test_last_update_has_run_id(self):
        """IT-FLW-004b: last_update.json contains a valid run_id."""
        if self.last_update is None:
            self.skipTest("last_update.json not available.")
        run_id = self.last_update.get("last_run_id")
        if run_id is None:
            self.skipTest("last_run_id is null — pipeline has not run yet.")
        self.assertTrue(is_valid_run_id(run_id), f"last_run_id '{run_id}' not in YYYY-WNN format")

    def test_country_files_exist(self):
        """IT-FLW-004c: At least one country file exists in data/countries/."""
        if not self.country_files:
            self.skipTest("No country files found. Run agents 01-09 first.")
        self.assertGreater(len(self.country_files), 0)

    def test_country_file_structure(self):
        """IT-FLW-004d: Sample country file has expected top-level keys."""
        if not self.country_files:
            self.skipTest("No country files found.")
        sample = load_json(self.country_files[0])
        expected_keys = ["code", "name", "tier"]
        for k in expected_keys:
            self.assertIn(k, sample, f"Country file missing '{k}' field")

    def test_country_codes_are_iso3(self):
        """IT-FLW-004e: Country filenames match ISO3 format (ABC.json)."""
        invalid = [
            f.name for f in self.country_files
            if not (len(f.stem) == 3 and f.stem.isupper())
        ]
        self.assertEqual(invalid, [], f"Non-ISO3 country filenames: {invalid}")

    def test_update_log_exists(self):
        """IT-FLW-004f: data/metadata/update_log.json exists."""
        update_log = DATA_DIR / "metadata" / "update_log.json"
        if not update_log.exists():
            self.skipTest("update_log.json not found.")
        data = load_json(update_log)
        self.assertIsInstance(data, list, "update_log.json should be a list")


# ---------------------------------------------------------------------------
# IT-FLW-005: Phase 5 Analysis Files
# ---------------------------------------------------------------------------
class TestPhase5Analysis(unittest.TestCase):
    """IT-FLW-005: Phase 5 analysis outputs exist and are consistent."""

    @classmethod
    def setUpClass(cls):
        trend_files = find_files(STAGING_DIR, "trends/trend_estimates_*.json")
        cls.trends_path = most_recent(trend_files) if trend_files else None
        cls.trends = load_json(cls.trends_path) if cls.trends_path else None

        cls.alert_index_path = DATA_DIR / "indices" / "alert_index.json"
        cls.alert_index = load_json(cls.alert_index_path) if cls.alert_index_path.exists() else None

        cls.rankings_path = DATA_DIR / "global" / "global_rankings.json"
        cls.rankings = load_json(cls.rankings_path) if cls.rankings_path.exists() else None

    def test_trend_estimates_exist(self):
        """IT-FLW-005a: Trend estimates file exists."""
        if self.trends is None:
            self.skipTest("Trend estimates not found. Run agents 01-10 first.")
        self.assertGreater(len(self.trends.get("estimates", [])), 0)

    def test_alert_index_exists(self):
        """IT-FLW-005b: alert_index.json exists in data/indices/."""
        if not self.alert_index_path.exists():
            self.skipTest("alert_index.json not found. Run agents 01-12 first.")
        self.assertIsNotNone(self.alert_index)

    def test_alert_index_structure(self):
        """IT-FLW-005c: alert_index.json has required structure."""
        if self.alert_index is None:
            self.skipTest("alert_index not available.")
        self.assertIn("alerts", self.alert_index, "alert_index missing 'alerts' field")
        self.assertIsInstance(self.alert_index["alerts"], list)

    def test_alert_severities_valid(self):
        """IT-FLW-005d: All alerts have valid severity values."""
        if self.alert_index is None:
            self.skipTest("alert_index not available.")
        valid_severities = {"critical", "warning", "watch"}
        alerts = self.alert_index.get("alerts", [])
        invalid = [
            a.get("alert_id", "?")
            for a in alerts
            if a.get("severity") not in valid_severities
        ]
        self.assertEqual(invalid, [], f"Alerts with invalid severity: {invalid}")

    def test_global_rankings_exist(self):
        """IT-FLW-005e: global_rankings.json exists in data/global/."""
        if not self.rankings_path.exists():
            self.skipTest("global_rankings.json not found. Run agents 01-11 first.")
        self.assertIsNotNone(self.rankings)

    def test_trend_ai_generated_flag(self):
        """IT-FLW-005f: Trend estimates have ai_generated=True."""
        if self.trends is None:
            self.skipTest("Trend estimates not available.")
        self.assertTrue(
            self.trends.get("ai_generated"),
            "trend_estimates must have ai_generated=True"
        )


# ---------------------------------------------------------------------------
# IT-FLW-006: Phase 6 Narrative and Briefing
# ---------------------------------------------------------------------------
class TestPhase6Synthesis(unittest.TestCase):
    """IT-FLW-006: Phase 6 narrative and briefing outputs are present."""

    @classmethod
    def setUpClass(cls):
        briefing_files = find_files(DATA_DIR / "global", "weekly_briefing_*.json")
        cls.briefing_path = most_recent(briefing_files) if briefing_files else None
        cls.briefing = load_json(cls.briefing_path) if cls.briefing_path else None

        cls.country_files = find_files(DATA_DIR / "countries", "*.json")

    def test_weekly_briefing_exists(self):
        """IT-FLW-006a: weekly_briefing file exists in data/global/."""
        if self.briefing is None:
            self.skipTest("weekly_briefing not found. Run agents 01-14 first.")
        self.assertIsNotNone(self.briefing)

    def test_briefing_has_headline(self):
        """IT-FLW-006b: Briefing has a non-empty headline."""
        if self.briefing is None:
            self.skipTest("weekly_briefing not available.")
        headline = self.briefing.get("headline", "")
        self.assertGreater(len(headline.strip()), 10, "Briefing headline is too short")

    def test_briefing_ai_generated(self):
        """IT-FLW-006c: Briefing is labeled as AI-generated."""
        if self.briefing is None:
            self.skipTest("weekly_briefing not available.")
        self.assertTrue(self.briefing.get("ai_generated"), "Briefing must have ai_generated=True")

    def test_country_narratives_present(self):
        """IT-FLW-006d: A sample of Tier 1 country files have narrative sections."""
        if not self.country_files:
            self.skipTest("No country files found.")
        # Check up to 5 country files for narrative presence
        sample = self.country_files[:5]
        missing_narrative = []
        for path in sample:
            try:
                data = load_json(path)
                tier = data.get("tier", 3)
                if tier == 1 and "narrative" not in data:
                    missing_narrative.append(path.stem)
            except Exception:
                pass

        self.assertEqual(
            missing_narrative, [],
            f"Tier 1 countries missing narrative sections: {missing_narrative}"
        )

    def test_briefing_has_regional_summaries(self):
        """IT-FLW-006e: Briefing contains regional_summaries."""
        if self.briefing is None:
            self.skipTest("weekly_briefing not available.")
        summaries = self.briefing.get("regional_summaries", {})
        self.assertGreater(len(summaries), 0, "Briefing has no regional_summaries")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Staging dir:  {STAGING_DIR}")
    print(f"Data dir:     {DATA_DIR}")
    print("")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for cls in [
        TestPhase1GatherFiles,
        TestPhase2ProcessFile,
        TestPhase3ValidationFiles,
        TestPhase4Integration,
        TestPhase5Analysis,
        TestPhase6Synthesis,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
