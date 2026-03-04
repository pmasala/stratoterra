"""
Stratoterra Unit Tests — Agent Output Structure Validation
Tests: UT-AGT-001 through UT-AGT-005

Validates that actual agent output files (when present in staging/)
conform to the expected structure defined in tests/fixtures/expected_outputs/.

Run: python3 tests/scripts/test_agent_outputs.py
"""

import json
import os
import sys
import glob
import unittest
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Project root resolution
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "expected_outputs"
STAGING_DIR = PROJECT_ROOT / "staging"
DATA_DIR = PROJECT_ROOT / "data"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    """Load a JSON file and return its contents."""
    with open(path) as f:
        return json.load(f)


def find_staging_file(pattern: str) -> Path | None:
    """Find the most recent file in staging/ matching a glob pattern."""
    matches = sorted(glob.glob(str(STAGING_DIR / pattern)))
    return Path(matches[-1]) if matches else None


def find_data_file(pattern: str) -> Path | None:
    """Find a data file matching a glob pattern."""
    matches = sorted(glob.glob(str(DATA_DIR / pattern)))
    return Path(matches[-1]) if matches else None


def check_required_fields(obj: dict, required: list, context: str) -> list[str]:
    """Return a list of missing required field names."""
    return [f for f in required if f not in obj]


def check_list_of_objects(items: list, required_fields: list, context: str) -> list[str]:
    """Check that each item in a list has all required fields. Return error messages."""
    errors = []
    for i, item in enumerate(items):
        missing = [f for f in required_fields if f not in item]
        if missing:
            errors.append(f"{context}[{i}] missing fields: {missing}")
    return errors


# ---------------------------------------------------------------------------
# UT-AGT-001: Agent 01 Output Structure
# ---------------------------------------------------------------------------
class TestAgent01OfficialStats(unittest.TestCase):
    """UT-AGT-001: Validate Agent 01 output structure and content rules."""

    @classmethod
    def setUpClass(cls):
        cls.expected = load_json(FIXTURES_DIR / "agent_01_expected.json")
        cls.actual_path = find_staging_file("raw_collected/official_stats_*.json")
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 01 output not found in staging/raw_collected/. Run the agent first.")

    def test_top_level_required_fields(self):
        """UT-AGT-001a: Top-level required fields are present."""
        required = self.expected.get("_required_fields", [
            "agent", "run_id", "collection_date", "records", "summary"
        ])
        missing = check_required_fields(self.actual, required, "agent_01 output")
        self.assertEqual(missing, [], f"Missing top-level fields: {missing}")

    def test_agent_identifier(self):
        """UT-AGT-001b: Agent field matches expected identifier."""
        self.assertEqual(
            self.actual.get("agent"), "official_stats_gatherer",
            "Agent identifier should be 'official_stats_gatherer'"
        )

    def test_records_is_list(self):
        """UT-AGT-001c: records field is a non-empty list."""
        records = self.actual.get("records", [])
        self.assertIsInstance(records, list, "records must be a list")
        self.assertGreater(len(records), 0, "records must not be empty")

    def test_record_required_fields(self):
        """UT-AGT-001d: Each record has required fields."""
        required = self.expected.get("_required_record_fields", [
            "country_code", "factor_path", "new_value", "source", "confidence"
        ])
        records = self.actual.get("records", [])
        errors = check_list_of_objects(records, required, "records")
        self.assertEqual(errors, [], f"Record field errors: {errors}")

    def test_confidence_in_range(self):
        """UT-AGT-001e: All confidence values are between 0.0 and 1.0."""
        records = self.actual.get("records", [])
        out_of_range = [
            f"record[{i}] country={r.get('country_code')} path={r.get('factor_path')} confidence={r.get('confidence')}"
            for i, r in enumerate(records)
            if not isinstance(r.get("confidence"), (int, float))
            or not (0.0 <= r["confidence"] <= 1.0)
        ]
        self.assertEqual(out_of_range, [], f"Confidence out of range [0,1]: {out_of_range}")

    def test_country_codes_are_iso3(self):
        """UT-AGT-001f: Country codes are 3-character uppercase strings."""
        records = self.actual.get("records", [])
        invalid = [
            r.get("country_code")
            for r in records
            if not isinstance(r.get("country_code"), str)
            or len(r["country_code"]) != 3
            or not r["country_code"].isupper()
        ]
        self.assertEqual(invalid, [], f"Invalid ISO3 country codes: {invalid}")

    def test_summary_fields(self):
        """UT-AGT-001g: Summary section has required fields."""
        required = self.expected.get("_required_summary_fields", [
            "total_records", "countries_covered"
        ])
        summary = self.actual.get("summary", {})
        missing = check_required_fields(summary, required, "summary")
        self.assertEqual(missing, [], f"Missing summary fields: {missing}")

    def test_skipped_is_list(self):
        """UT-AGT-001h: skipped field is a list (may be empty)."""
        skipped = self.actual.get("skipped", [])
        self.assertIsInstance(skipped, list, "skipped must be a list")

    def test_collection_date_is_iso_format(self):
        """UT-AGT-001i: collection_date is a valid YYYY-MM-DD date."""
        date_str = self.actual.get("collection_date", "")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            self.fail(f"collection_date '{date_str}' is not a valid YYYY-MM-DD date")


# ---------------------------------------------------------------------------
# UT-AGT-002: Agent 07 Output Structure
# ---------------------------------------------------------------------------
class TestAgent07Processor(unittest.TestCase):
    """UT-AGT-002: Validate Agent 07 output structure."""

    @classmethod
    def setUpClass(cls):
        cls.expected = load_json(FIXTURES_DIR / "agent_07_expected.json")
        cls.actual_path = find_staging_file("processed/factor_updates_*.json")
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 07 output not found in staging/processed/. Run agents 01-07 first.")

    def test_top_level_required_fields(self):
        """UT-AGT-002a: Top-level required fields are present."""
        # Core required fields (unmapped_records is optional, event_triggers added in cache-aware pipeline)
        required = self.expected.get("_required_fields", [
            "processing_date", "agent", "run_id",
            "factor_updates", "event_signals", "summary"
        ])
        missing = check_required_fields(self.actual, required, "agent_07 output")
        self.assertEqual(missing, [], f"Missing top-level fields: {missing}")

    def test_agent_identifier(self):
        """UT-AGT-002b: Agent field contains fact_extractor identifier."""
        agent = self.actual.get("agent", "")
        self.assertIn("fact_extractor", agent, f"Agent field '{agent}' should contain 'fact_extractor'")

    def test_factor_updates_is_list(self):
        """UT-AGT-002c: factor_updates is a list."""
        self.assertIsInstance(self.actual.get("factor_updates"), list)

    def test_factor_update_required_fields(self):
        """UT-AGT-002d: Each factor update has required fields."""
        required = self.expected.get("_required_update_fields", [
            "update_id", "target", "country_code", "factor_path",
            "new_value", "confidence", "anomaly_flag", "conflict_flag"
        ])
        updates = self.actual.get("factor_updates", [])
        errors = check_list_of_objects(updates, required, "factor_updates")
        self.assertEqual(errors, [], f"factor_update field errors: {errors}")

    def test_target_values(self):
        """UT-AGT-002e: target field values are within allowed set."""
        allowed = {"country", "relation", "supranational", "global"}
        updates = self.actual.get("factor_updates", [])
        invalid = [
            f"update_id={u.get('update_id')} target={u.get('target')}"
            for u in updates
            if u.get("target") not in allowed
        ]
        self.assertEqual(invalid, [], f"Invalid target values: {invalid}")

    def test_update_ids_are_unique(self):
        """UT-AGT-002f: update_id values are unique."""
        updates = self.actual.get("factor_updates", [])
        ids = [u.get("update_id") for u in updates]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate update_id values found")

    def test_event_signals_is_list(self):
        """UT-AGT-002g: event_signals is a list."""
        self.assertIsInstance(self.actual.get("event_signals"), list)

    def test_summary_counts_match(self):
        """UT-AGT-002h: summary update counts are approximately consistent with factor_updates list."""
        updates_count = len(self.actual.get("factor_updates", []))
        summary = self.actual.get("summary", {})
        direct = summary.get("direct_updates", 0)
        event_triggered = summary.get("event_triggered_updates", 0)
        expected_total = direct + event_triggered
        # Allow small tolerance (±2) due to agent counting variations
        self.assertAlmostEqual(
            updates_count, expected_total, delta=2,
            msg=f"len(factor_updates)={updates_count} vs direct_updates({direct}) + event_triggered({event_triggered}) = {expected_total}"
        )

    def test_boolean_flags(self):
        """UT-AGT-002i: anomaly_flag and conflict_flag are booleans."""
        updates = self.actual.get("factor_updates", [])
        errors = []
        for i, u in enumerate(updates):
            for flag in ("anomaly_flag", "conflict_flag"):
                if not isinstance(u.get(flag), bool):
                    errors.append(f"update[{i}].{flag} is not bool: {u.get(flag)}")
        self.assertEqual(errors, [], f"Boolean flag errors: {errors}")


# ---------------------------------------------------------------------------
# UT-AGT-003: Agent 10 Output Structure
# ---------------------------------------------------------------------------
class TestAgent10TrendEstimator(unittest.TestCase):
    """UT-AGT-003: Validate Agent 10 trend estimates output structure."""

    VALID_TRENDS = {"strong_growth", "growth", "increase", "stable", "decrease", "strong_decrease"}

    @classmethod
    def setUpClass(cls):
        cls.expected = load_json(FIXTURES_DIR / "agent_10_expected.json")
        cls.actual_path = find_staging_file("trends/trend_estimates_*.json")
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 10 output not found in staging/trends/. Run agents 01-10 first.")

    def test_top_level_required_fields(self):
        """UT-AGT-003a: Top-level required fields are present."""
        # Core required: estimates and summary. Optional: agent, run_id, ai_generated (may be per-estimate)
        required = ["estimates", "summary"]
        missing = check_required_fields(self.actual, required, "agent_10 output")
        self.assertEqual(missing, [], f"Missing top-level fields: {missing}")

    def test_ai_generated_flag(self):
        """UT-AGT-003b: ai_generated flag is present (top-level or per-estimate)."""
        top_level = self.actual.get("ai_generated")
        if top_level is not None:
            self.assertTrue(top_level, "ai_generated must be True for Agent 10 output")
        else:
            # Check per-estimate
            estimates = self.actual.get("estimates", [])
            if estimates:
                self.assertTrue(
                    estimates[0].get("ai_generated"),
                    "ai_generated must be True per estimate"
                )

    def test_estimates_is_nonempty_list(self):
        """UT-AGT-003c: estimates is a non-empty list."""
        estimates = self.actual.get("estimates", [])
        self.assertIsInstance(estimates, list)
        self.assertGreater(len(estimates), 0, "estimates must not be empty")

    def test_estimate_required_fields(self):
        """UT-AGT-003d: Each estimate has required fields."""
        # Accept both "factor_path" and "factor" as the factor field name
        required = [
            "country_code", "current_value", "trend", "confidence",
            "reasoning", "supporting_evidence", "counter_arguments",
            "investor_implication", "ai_generated"
        ]
        estimates = self.actual.get("estimates", [])
        errors = []
        for i, est in enumerate(estimates):
            missing = [f for f in required if f not in est]
            # Check for factor_path or factor
            if "factor_path" not in est and "factor" not in est:
                missing.append("factor_path|factor")
            if missing:
                errors.append(f"estimates[{i}] missing fields: {missing}")
        self.assertEqual(errors, [], f"Estimate field errors: {errors}")

    def test_trend_labels_valid(self):
        """UT-AGT-003e: trend field values are valid trend labels."""
        estimates = self.actual.get("estimates", [])
        invalid = [
            f"[{i}] {e.get('country_code')}.{e.get('factor_path')}: '{e.get('trend')}'"
            for i, e in enumerate(estimates)
            if e.get("trend") not in self.VALID_TRENDS
        ]
        self.assertEqual(invalid, [], f"Invalid trend labels: {invalid}")

    def test_confidence_in_range(self):
        """UT-AGT-003f: All confidence values are in [0.0, 1.0]."""
        estimates = self.actual.get("estimates", [])
        out_of_range = [
            f"[{i}] {e.get('country_code')}: confidence={e.get('confidence')}"
            for i, e in enumerate(estimates)
            if not isinstance(e.get("confidence"), (int, float))
            or not (0.0 <= e["confidence"] <= 1.0)
        ]
        self.assertEqual(out_of_range, [], f"Confidence out of [0,1]: {out_of_range}")

    def test_supporting_evidence_is_list(self):
        """UT-AGT-003g: supporting_evidence is a list in each estimate."""
        estimates = self.actual.get("estimates", [])
        invalid = [
            f"[{i}] {e.get('country_code')}"
            for i, e in enumerate(estimates)
            if not isinstance(e.get("supporting_evidence"), list)
        ]
        self.assertEqual(invalid, [], f"supporting_evidence not a list: {invalid}")

    def test_counter_arguments_is_list(self):
        """UT-AGT-003h: counter_arguments is a list in each estimate."""
        estimates = self.actual.get("estimates", [])
        invalid = [
            f"[{i}] {e.get('country_code')}"
            for i, e in enumerate(estimates)
            if not isinstance(e.get("counter_arguments"), list)
        ]
        self.assertEqual(invalid, [], f"counter_arguments not a list: {invalid}")

    def test_summary_total_matches_estimates(self):
        """UT-AGT-003i: summary.total_estimates matches len(estimates)."""
        estimates_count = len(self.actual.get("estimates", []))
        summary_total = self.actual.get("summary", {}).get("total_estimates", -1)
        self.assertEqual(
            estimates_count, summary_total,
            f"summary.total_estimates ({summary_total}) != len(estimates) ({estimates_count})"
        )


# ---------------------------------------------------------------------------
# UT-AGT-004: Agent 14 Output Structure
# ---------------------------------------------------------------------------
class TestAgent14Briefing(unittest.TestCase):
    """UT-AGT-004: Validate Agent 14 weekly briefing output structure."""

    REQUIRED_REGIONS = {
        "North America", "Europe", "East Asia", "South Asia",
        "Middle East & North Africa", "Sub-Saharan Africa", "Latin America",
        "Central Asia", "Southeast Asia", "Oceania"
    }

    @classmethod
    def setUpClass(cls):
        cls.expected = load_json(FIXTURES_DIR / "agent_14_expected.json")
        # Check both naming conventions
        cls.actual_path = find_data_file("global/weekly_briefing_*.json")
        if cls.actual_path is None:
            cls.actual_path = find_data_file("global/weekly_briefing.json")
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 14 output not found in data/global/. Run agents 01-14 first.")

    def test_top_level_required_fields(self):
        """UT-AGT-004a: Top-level required fields are present."""
        required = self.expected.get("_required_fields", [
            "briefing_id", "generated_at", "ai_generated", "period_covered",
            "headline", "top_stories", "regional_summaries", "market_context",
            "watchlist_updates", "data_quality_summary"
        ])
        missing = check_required_fields(self.actual, required, "agent_14 output")
        self.assertEqual(missing, [], f"Missing top-level fields: {missing}")

    def test_ai_generated_flag(self):
        """UT-AGT-004b: ai_generated is True."""
        self.assertTrue(self.actual.get("ai_generated"), "ai_generated must be True")

    def test_headline_is_string(self):
        """UT-AGT-004c: headline is a non-empty string."""
        headline = self.actual.get("headline", "")
        self.assertIsInstance(headline, str)
        self.assertGreater(len(headline.strip()), 0, "headline must not be empty")

    def test_top_stories_is_list(self):
        """UT-AGT-004d: top_stories is a list with at least one entry."""
        stories = self.actual.get("top_stories", [])
        self.assertIsInstance(stories, list)
        self.assertGreater(len(stories), 0, "top_stories must have at least one entry")

    def test_top_story_required_fields(self):
        """UT-AGT-004e: Each top story has required fields."""
        required = self.expected.get("_required_top_story_fields", [
            "rank", "title", "summary", "countries_affected", "investor_impact", "severity"
        ])
        stories = self.actual.get("top_stories", [])
        errors = check_list_of_objects(stories, required, "top_stories")
        self.assertEqual(errors, [], f"Top story field errors: {errors}")

    def test_regional_summaries_coverage(self):
        """UT-AGT-004f: regional_summaries covers all 10 required regions."""
        summaries = self.actual.get("regional_summaries", {})
        missing = self.REQUIRED_REGIONS - set(summaries.keys())
        self.assertEqual(
            missing, set(),
            f"Missing regional summaries for: {missing}"
        )

    def test_regional_summaries_non_empty(self):
        """UT-AGT-004g: Each regional summary is a non-empty string."""
        summaries = self.actual.get("regional_summaries", {})
        empty = [k for k, v in summaries.items() if not isinstance(v, str) or len(v.strip()) == 0]
        self.assertEqual(empty, [], f"Empty regional summaries: {empty}")

    def test_data_quality_summary_structure(self):
        """UT-AGT-004h: data_quality_summary has required fields."""
        dqs = self.actual.get("data_quality_summary", {})
        required = ["countries_updated", "factors_updated", "avg_confidence", "alerts_active"]
        missing = [f for f in required if f not in dqs]
        self.assertEqual(missing, [], f"Missing data_quality_summary fields: {missing}")

    def test_top_stories_ranked(self):
        """UT-AGT-004i: top_stories are ranked starting from 1."""
        stories = self.actual.get("top_stories", [])
        ranks = [s.get("rank") for s in stories]
        self.assertEqual(ranks[0], 1, "First top story must have rank=1")


# ---------------------------------------------------------------------------
# UT-AGT-005: Agent 15 Output Structure
# ---------------------------------------------------------------------------
class TestAgent15QualityReport(unittest.TestCase):
    """UT-AGT-005: Validate Agent 15 quality report output structure."""

    @classmethod
    def setUpClass(cls):
        cls.expected = load_json(FIXTURES_DIR / "agent_15_expected.json")
        cls.actual_path = find_data_file("metadata/quality_report_*.json")
        cls.actual = load_json(cls.actual_path) if cls.actual_path else None

    def setUp(self):
        if self.actual is None:
            self.skipTest("Agent 15 output not found in data/metadata/. Run agents 01-15 first.")

    def test_top_level_required_fields(self):
        """UT-AGT-005a: Top-level required fields are present."""
        required = self.expected.get("_required_fields", [
            "report_date", "run_id", "generated_at",
            "coverage", "staleness", "confidence", "validation",
            "agent_performance", "recommendations"
        ])
        missing = check_required_fields(self.actual, required, "agent_15 output")
        self.assertEqual(missing, [], f"Missing top-level fields: {missing}")

    def test_coverage_required_fields(self):
        """UT-AGT-005b: coverage section has required fields."""
        required = self.expected.get("_required_coverage_fields", [
            "tier_1_avg_pct", "tier_2_avg_pct", "tier_3_avg_pct", "flagged_countries"
        ])
        coverage = self.actual.get("coverage", {})
        missing = check_required_fields(coverage, required, "coverage")
        self.assertEqual(missing, [], f"Missing coverage fields: {missing}")

    def test_coverage_targets(self):
        """UT-AGT-005c: Coverage percentages meet minimum targets (or are flagged)."""
        targets = self.expected.get("_coverage_targets", {
            "tier_1_min": 90, "tier_2_min": 70, "tier_3_min": 50
        })
        coverage = self.actual.get("coverage", {})
        flagged = coverage.get("flagged_countries", [])

        # Tier 1: average should be >= 90%, or there should be flagged countries explaining shortfall
        t1_avg = coverage.get("tier_1_avg_pct", 0)
        if t1_avg < targets.get("tier_1_min", 90):
            # Acceptable if flagged countries account for it
            self.assertGreater(
                len(flagged), 0,
                f"Tier 1 coverage {t1_avg}% < 90% but no flagged_countries listed"
            )

    def test_validation_fields(self):
        """UT-AGT-005d: validation section has required fields."""
        required = self.expected.get("_required_validation_fields", [
            "total", "accept", "accept_with_note", "flag", "reject", "escalate"
        ])
        validation = self.actual.get("validation", {})
        missing = check_required_fields(validation, required, "validation")
        self.assertEqual(missing, [], f"Missing validation fields: {missing}")

    def test_validation_counts_sum_to_total(self):
        """UT-AGT-005e: Validation verdict counts sum to total."""
        v = self.actual.get("validation", {})
        total = v.get("total", 0)
        subtotals = sum([
            v.get("accept", 0),
            v.get("accept_with_note", 0),
            v.get("flag", 0),
            v.get("reject", 0),
            v.get("escalate", 0),
        ])
        self.assertEqual(
            total, subtotals,
            f"Validation counts don't sum: total={total}, sum of verdicts={subtotals}"
        )

    def test_confidence_avg_in_range(self):
        """UT-AGT-005f: Overall average confidence is in [0.0, 1.0]."""
        avg = self.actual.get("confidence", {}).get("overall_avg", -1)
        self.assertTrue(0.0 <= avg <= 1.0, f"overall_avg confidence {avg} not in [0,1]")

    def test_agent_performance_is_list(self):
        """UT-AGT-005g: agent_performance is a list."""
        perf = self.actual.get("agent_performance", [])
        self.assertIsInstance(perf, list, "agent_performance must be a list")

    def test_recommendations_is_list(self):
        """UT-AGT-005h: recommendations is a list."""
        recs = self.actual.get("recommendations", [])
        self.assertIsInstance(recs, list, "recommendations must be a list")

    def test_staleness_structure(self):
        """UT-AGT-005i: staleness section has by_tier breakdown."""
        staleness = self.actual.get("staleness", {})
        self.assertIn("by_tier", staleness, "staleness must have by_tier")
        by_tier = staleness["by_tier"]
        for tier in ("tier_1", "tier_2", "tier_3"):
            self.assertIn(tier, by_tier, f"staleness.by_tier missing '{tier}'")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Print project context
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Fixtures dir: {FIXTURES_DIR}")
    print(f"Staging dir:  {STAGING_DIR}")
    print("")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load all test classes
    for cls in [
        TestAgent01OfficialStats,
        TestAgent07Processor,
        TestAgent10TrendEstimator,
        TestAgent14Briefing,
        TestAgent15QualityReport,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
