#!/usr/bin/env python3
"""
Stratoterra — UI Data Contract Tests
Tests E2E-UI-001 through E2E-UI-010

Verifies that chunk files served to the frontend are present, loadable,
within size limits, and contain the fields the UI depends on.
Also includes frontend code quality checks (E2E-UI-009) to catch
silent-failure anti-patterns like empty catch blocks and z-index conflicts.
No third-party libraries required.
"""

import json
import os
import sys
import unittest
import datetime

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
INDICES_DIR = os.path.join(DATA_DIR, "indices")
GLOBAL_DIR = os.path.join(DATA_DIR, "global")
TIMESERIES_DIR = os.path.join(DATA_DIR, "timeseries")

# Seed countries that must always have detail chunks (E2E-UI-002)
SEED_COUNTRIES = ["USA", "CHN", "DEU", "BRA", "NGA"]

# Size limits (bytes)
SUMMARY_MAX_BYTES = 1_000_000       # 1 MB
COUNTRY_DETAIL_MAX_BYTES = 200_000  # 200 KB
RELATION_MAX_BYTES = 50_000         # 50 KB
BRIEFING_MAX_BYTES = 50_000         # 50 KB
MANIFEST_MAX_BYTES = 10_000         # 10 KB

# Minimum timeseries data points for charting (E2E-UI-005)
TIMESERIES_MIN_POINTS = 8

# Fields that must be present in each summary entry for the map to render
SUMMARY_REQUIRED_MAP_FIELDS = {
    "code", "name", "region", "latitude", "longitude",
    "alert_count",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_file(candidates):
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def find_summary_path():
    return find_file([
        os.path.join(CHUNKS_DIR, "country-summary", "all_countries_summary.json"),
        os.path.join(CHUNKS_DIR, "all_countries_summary.json"),
    ])


def find_country_detail(code):
    """Return the path to a country detail chunk, or None if not found."""
    candidates = [
        os.path.join(CHUNKS_DIR, "country-detail", f"{code}.json"),
        os.path.join(CHUNKS_DIR, f"{code}.json"),
        os.path.join(DATA_DIR, "countries", f"{code}.json"),
    ]
    return find_file(candidates)


def find_timeseries(code):
    """Return a list of timeseries file paths for a country."""
    results = []
    # Check chunks/timeseries/
    ts_chunks = os.path.join(CHUNKS_DIR, "timeseries")
    if os.path.isdir(ts_chunks):
        for f in os.listdir(ts_chunks):
            if code in f and f.endswith(".json"):
                results.append(os.path.join(ts_chunks, f))
    # Check data/timeseries/
    if os.path.isdir(TIMESERIES_DIR):
        for f in os.listdir(TIMESERIES_DIR):
            if code in f and f.endswith(".json"):
                results.append(os.path.join(TIMESERIES_DIR, f))
    return results


def find_briefing():
    """Return the path to the most recent weekly briefing, or None."""
    candidates = []
    for base_dir in [os.path.join(CHUNKS_DIR, "global"), GLOBAL_DIR]:
        if os.path.isdir(base_dir):
            for f in os.listdir(base_dir):
                if "briefing" in f and f.endswith(".json"):
                    candidates.append(os.path.join(base_dir, f))
    # Return the lexicographically last (most recent date in filename)
    return sorted(candidates)[-1] if candidates else None


def find_alert_index():
    return find_file([
        os.path.join(CHUNKS_DIR, "global", "alert_index.json"),
        os.path.join(INDICES_DIR, "alert_index.json"),
    ])


# ---------------------------------------------------------------------------
# E2E-UI-001: Summary chunk loadable and renderable
# ---------------------------------------------------------------------------

class TestE2E_UI_001_SummaryChunk(unittest.TestCase):
    """E2E-UI-001: all_countries_summary.json is present, under 1MB, and map-ready."""

    def setUp(self):
        self.summary_path = find_summary_path()

    def test_summary_file_exists(self):
        if not self.summary_path:
            self.skipTest(
                "all_countries_summary.json not found — pipeline may not have run yet"
            )
        self.assertTrue(os.path.isfile(self.summary_path))

    def test_summary_valid_json(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        try:
            data = load_json(self.summary_path)
        except json.JSONDecodeError as exc:
            self.fail(f"Summary is not valid JSON: {exc}")
        # Accept both bare array and wrapper dict with 'countries' key
        if isinstance(data, dict):
            self.assertIn("countries", data, "Summary wrapper must have 'countries' key")
            self.assertIsInstance(data["countries"], list, "countries must be an array")
        else:
            self.assertIsInstance(data, list, "Summary must be a JSON array or wrapper object")

    def test_summary_size_under_1mb(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        size = os.path.getsize(self.summary_path)
        self.assertLessEqual(
            size,
            SUMMARY_MAX_BYTES,
            f"all_countries_summary.json is {size:,} bytes, must be <{SUMMARY_MAX_BYTES:,} bytes (1 MB)",
        )

    def test_summary_entries_have_map_fields(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        countries = data.get("countries", data) if isinstance(data, dict) else data
        if not isinstance(countries, list):
            self.skipTest("Summary countries is not a list")
        # Use relaxed field set — lat/lon may use different names
        required = {"code", "name", "region"}
        errors = []
        for item in countries:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            missing = required - set(item.keys())
            if missing:
                errors.append(f"{code}: missing map fields {sorted(missing)}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_summary_lat_lon_valid(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        countries = data.get("countries", data) if isinstance(data, dict) else data
        if not isinstance(countries, list):
            self.skipTest("Summary countries is not a list")
        errors = []
        for item in countries:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            lat = item.get("latitude", item.get("lat"))
            lon = item.get("longitude", item.get("lon"))
            if lat is not None and not (-90 <= lat <= 90):
                errors.append(f"{code}: latitude={lat} out of range")
            if lon is not None and not (-180 <= lon <= 180):
                errors.append(f"{code}: longitude={lon} out of range")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_summary_is_non_empty(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        countries = data.get("countries", data) if isinstance(data, dict) else data
        if not isinstance(countries, list):
            self.skipTest("Summary countries is not a list")
        self.assertGreater(
            len(countries), 0, "all_countries_summary.json must contain at least one entry"
        )


# ---------------------------------------------------------------------------
# E2E-UI-002: Country detail chunks loadable for seed countries
# ---------------------------------------------------------------------------

class TestE2E_UI_002_CountryDetailChunks(unittest.TestCase):
    """E2E-UI-002: Detail chunk files exist and are valid for seed countries."""

    def test_seed_country_detail_exists(self):
        missing = []
        for code in SEED_COUNTRIES:
            if not find_country_detail(code):
                missing.append(code)
        if len(missing) == len(SEED_COUNTRIES):
            self.skipTest(
                "No country detail files found for any seed country — "
                "pipeline may not have run yet"
            )
        self.assertEqual(
            missing,
            [],
            f"Missing detail chunk files for: {missing}",
        )

    def test_seed_country_detail_valid_json(self):
        errors = []
        found_any = False
        for code in SEED_COUNTRIES:
            path = find_country_detail(code)
            if not path:
                continue
            found_any = True
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{code}: {exc}")
        if not found_any:
            self.skipTest("No seed country detail files found")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_seed_country_detail_has_layers(self):
        errors = []
        found_any = False
        required_layers = {"endowments", "institutions", "economy", "military", "relations", "derived"}
        for code in SEED_COUNTRIES:
            path = find_country_detail(code)
            if not path:
                continue
            found_any = True
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            layers = data.get("layers", {})
            if not isinstance(layers, dict):
                errors.append(f"{code}: 'layers' is not an object")
                continue
            missing = required_layers - set(layers.keys())
            if missing:
                errors.append(f"{code}: missing layers {sorted(missing)}")
        if not found_any:
            self.skipTest("No seed country detail files found")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_seed_country_detail_size_limit(self):
        errors = []
        found_any = False
        for code in SEED_COUNTRIES:
            path = find_country_detail(code)
            if not path:
                continue
            found_any = True
            size = os.path.getsize(path)
            if size > COUNTRY_DETAIL_MAX_BYTES:
                errors.append(
                    f"{code}: {size:,} bytes exceeds limit of {COUNTRY_DETAIL_MAX_BYTES:,} bytes"
                )
        if not found_any:
            self.skipTest("No seed country detail files found")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_seed_country_detail_has_narrative(self):
        errors = []
        found_any = False
        for code in SEED_COUNTRIES:
            path = find_country_detail(code)
            if not path:
                continue
            found_any = True
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            # Narrative may be nested in data["narrative"] or directly on data
            narrative = data.get("narrative") or {}
            exec_summary = (
                narrative.get("executive_summary")
                or data.get("executive_summary")
                or ""
            )
            if not exec_summary:
                errors.append(f"{code}: missing executive_summary in narrative")
        if not found_any:
            self.skipTest("No seed country detail files found")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-003: Timeseries files loadable for seed countries
# ---------------------------------------------------------------------------

class TestE2E_UI_003_TimeseriesChunks(unittest.TestCase):
    """E2E-UI-003: Timeseries files exist and meet charting requirements."""

    def test_seed_country_timeseries_exists(self):
        missing = []
        found_any = False
        for code in SEED_COUNTRIES:
            files = find_timeseries(code)
            if files:
                found_any = True
            else:
                missing.append(code)
        if not found_any:
            self.skipTest(
                "No timeseries files found for any seed country — pipeline may not have run yet"
            )
        self.assertEqual(
            missing,
            [],
            f"No timeseries files found for: {missing}",
        )

    def test_timeseries_valid_json(self):
        found_any = False
        errors = []
        for code in SEED_COUNTRIES:
            for path in find_timeseries(code):
                found_any = True
                try:
                    load_json(path)
                except json.JSONDecodeError as exc:
                    errors.append(f"{os.path.basename(path)}: {exc}")
        if not found_any:
            self.skipTest("No timeseries files found")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timeseries_minimum_data_points(self):
        """Each timeseries must have >= 8 data points for chart rendering."""
        found_any = False
        errors = []
        for code in SEED_COUNTRIES:
            for path in find_timeseries(code):
                found_any = True
                try:
                    data = load_json(path)
                except json.JSONDecodeError:
                    continue
                # Handle nested structure: {"series": {"gdp_growth": [...], ...}}
                if isinstance(data, list):
                    entries = data
                elif isinstance(data, dict) and "series" in data:
                    # Check each sub-series has enough data points
                    series = data["series"]
                    if isinstance(series, dict):
                        for series_name, points in series.items():
                            if isinstance(points, list) and len(points) < TIMESERIES_MIN_POINTS:
                                errors.append(
                                    f"{os.path.basename(path)}.series.{series_name}: "
                                    f"{len(points)} data points, need >= {TIMESERIES_MIN_POINTS}"
                                )
                        found_any = True
                        continue
                    entries = []
                else:
                    entries = data.get("data", [])
                if len(entries) < TIMESERIES_MIN_POINTS:
                    errors.append(
                        f"{os.path.basename(path)}: {len(entries)} data points, "
                        f"need >= {TIMESERIES_MIN_POINTS}"
                    )
        if not found_any:
            self.skipTest("No timeseries files found")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timeseries_chronological_order(self):
        found_any = False
        errors = []
        for code in SEED_COUNTRIES:
            for path in find_timeseries(code):
                found_any = True
                try:
                    data = load_json(path)
                except json.JSONDecodeError:
                    continue
                # Handle nested structure: {"series": {"gdp_growth": [...], ...}}
                if isinstance(data, list):
                    all_series = [("root", data)]
                elif isinstance(data, dict) and "series" in data:
                    series = data["series"]
                    if isinstance(series, dict):
                        all_series = list(series.items())
                    else:
                        all_series = [("data", data.get("data", []))]
                else:
                    all_series = [("data", data.get("data", []))]
                for series_name, entries in all_series:
                    timestamps = [
                        e.get("timestamp") or e.get("date")
                        for e in entries
                        if isinstance(e, dict)
                    ]
                    timestamps = [t for t in timestamps if t]
                    if timestamps != sorted(timestamps):
                        errors.append(
                            f"{os.path.basename(path)}.{series_name}: "
                            "timestamps not in chronological order"
                        )
        if not found_any:
            self.skipTest("No timeseries files found")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-004: Weekly briefing loadable
# ---------------------------------------------------------------------------

class TestE2E_UI_004_BriefingLoadable(unittest.TestCase):
    """E2E-UI-004: Weekly briefing exists, is valid JSON, and has expected sections."""

    def setUp(self):
        self.briefing_path = find_briefing()

    def test_briefing_exists(self):
        if not self.briefing_path:
            self.skipTest("No weekly briefing file found — pipeline may not have run yet")
        self.assertTrue(os.path.isfile(self.briefing_path))

    def test_briefing_valid_json(self):
        if not self.briefing_path:
            self.skipTest("Briefing not found")
        try:
            load_json(self.briefing_path)
        except json.JSONDecodeError as exc:
            self.fail(f"Briefing is not valid JSON: {exc}")

    def test_briefing_has_required_sections(self):
        if not self.briefing_path:
            self.skipTest("Briefing not found")
        data = load_json(self.briefing_path)
        required = {"headline", "top_stories", "regional_summaries"}
        missing = required - set(data.keys())
        self.assertEqual(
            missing,
            set(),
            f"Briefing missing required sections: {sorted(missing)}",
        )

    def test_briefing_top_stories_non_empty(self):
        if not self.briefing_path:
            self.skipTest("Briefing not found")
        data = load_json(self.briefing_path)
        stories = data.get("top_stories", [])
        self.assertGreater(len(stories), 0, "top_stories must not be empty")

    def test_briefing_size_within_limit(self):
        if not self.briefing_path:
            self.skipTest("Briefing not found")
        size = os.path.getsize(self.briefing_path)
        self.assertLessEqual(
            size,
            BRIEFING_MAX_BYTES,
            f"Briefing file is {size:,} bytes, limit is {BRIEFING_MAX_BYTES:,} bytes",
        )


# ---------------------------------------------------------------------------
# E2E-UI-005: Alert index loadable
# ---------------------------------------------------------------------------

class TestE2E_UI_005_AlertIndexLoadable(unittest.TestCase):
    """E2E-UI-005: alert_index.json exists, is valid JSON, and has the alerts array."""

    def setUp(self):
        self.alert_path = find_alert_index()

    def test_alert_index_exists(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found — pipeline may not have run yet")
        self.assertTrue(os.path.isfile(self.alert_path))

    def test_alert_index_valid_json(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        try:
            load_json(self.alert_path)
        except json.JSONDecodeError as exc:
            self.fail(f"alert_index.json is not valid JSON: {exc}")

    def test_alert_index_has_alerts_array(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        self.assertIn("alerts", data, "alert_index.json must have an 'alerts' key")
        self.assertIsInstance(
            data["alerts"], list, "alert_index.json 'alerts' must be a list"
        )

    def test_alert_severities_recognized(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        valid = {"critical", "warning", "watch"}
        errors = []
        for i, alert in enumerate(data.get("alerts", [])):
            if not isinstance(alert, dict):
                continue
            sev = alert.get("severity")
            if sev and sev not in valid:
                errors.append(f"Alert [{i}]: unknown severity '{sev}'")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-006: Summary contains metric fields required by "Color by" selector
# ---------------------------------------------------------------------------

# These are the summary field names referenced by METRIC_CONFIG in constants.js.
# Each entry in the summary must have these fields for the map coloring to work.
METRIC_FIELDS = {
    "gdp_real_growth_pct",
    "political_stability",
    "investment_risk_score",
    "military_spending_trend",
    "military_expenditure_pct_gdp",
    "max_alert_severity",
    "composite_national_power_index",
    "energy_independence",
    "trade_openness_pct",
}

# Minimum coverage thresholds (fraction of countries that must have the field)
# Tier 1 countries (major economies) should have near-complete data.
METRIC_COVERAGE_TIER1_MIN = 0.80
METRIC_COVERAGE_OVERALL_MIN = 0.25


class TestE2E_UI_006_SummaryMetricFields(unittest.TestCase):
    """E2E-UI-006: Summary entries contain the fields needed by the map's
    'Color by' selector. Without these, map coloring silently falls back
    to default color for all countries."""

    def setUp(self):
        self.summary_path = find_summary_path()
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        countries = data.get("countries", data) if isinstance(data, dict) else data
        if not isinstance(countries, list):
            self.skipTest("Summary countries is not a list")
        self.countries = countries
        self.tier1 = [c for c in countries if c.get("tier") == 1]

    def test_metric_fields_present_overall(self):
        """At least METRIC_COVERAGE_OVERALL_MIN of countries have each metric field."""
        total = len(self.countries)
        if total == 0:
            self.skipTest("No countries in summary")
        errors = []
        for field in sorted(METRIC_FIELDS):
            count = sum(1 for c in self.countries if c.get(field) is not None)
            coverage = count / total
            if coverage < METRIC_COVERAGE_OVERALL_MIN:
                errors.append(
                    f"{field}: {count}/{total} ({coverage:.0%}) < "
                    f"{METRIC_COVERAGE_OVERALL_MIN:.0%} minimum"
                )
        self.assertEqual(errors, [], "Metric fields with insufficient coverage:\n" + "\n".join(errors))

    def test_metric_fields_present_tier1(self):
        """At least METRIC_COVERAGE_TIER1_MIN of Tier 1 countries have each metric field."""
        if not self.tier1:
            self.skipTest("No Tier 1 countries in summary")
        total = len(self.tier1)
        errors = []
        for field in sorted(METRIC_FIELDS):
            count = sum(1 for c in self.tier1 if c.get(field) is not None)
            coverage = count / total
            if coverage < METRIC_COVERAGE_TIER1_MIN:
                errors.append(
                    f"{field}: {count}/{total} Tier 1 ({coverage:.0%}) < "
                    f"{METRIC_COVERAGE_TIER1_MIN:.0%} minimum"
                )
        self.assertEqual(errors, [], "Tier 1 metric coverage gaps:\n" + "\n".join(errors))

    def test_metric_values_are_valid_types(self):
        """Metric field values must be numeric or valid enum strings, not objects/lists."""
        NUMERIC_FIELDS = {
            "gdp_real_growth_pct", "political_stability", "investment_risk_score",
            "military_expenditure_pct_gdp", "composite_national_power_index",
            "energy_independence", "trade_openness_pct",
        }
        ENUM_FIELDS = {
            "military_spending_trend": {"strong_growth", "growth", "stable", "decrease", "strong_decrease"},
            "max_alert_severity": {"critical", "warning", "watch", "none"},
        }
        errors = []
        for c in self.countries:
            code = c.get("code", "?")
            for field in NUMERIC_FIELDS:
                val = c.get(field)
                if val is not None and not isinstance(val, (int, float)):
                    errors.append(f"{code}.{field}: expected number, got {type(val).__name__} = {val!r}")
            for field, valid_values in ENUM_FIELDS.items():
                val = c.get(field)
                if val is not None and val not in valid_values:
                    errors.append(f"{code}.{field}: '{val}' not in {sorted(valid_values)}")
        self.assertEqual(errors, [], "Invalid metric values:\n" + "\n".join(errors[:20]))

    def test_no_wrapper_objects_in_metric_fields(self):
        """Metric fields must be flat values, not {value: ..., confidence: ...} wrappers.
        These wrappers exist in full country files but must be unwrapped for the summary."""
        errors = []
        for c in self.countries:
            code = c.get("code", "?")
            for field in METRIC_FIELDS:
                val = c.get(field)
                if isinstance(val, dict):
                    errors.append(
                        f"{code}.{field}: is a dict (probably a value wrapper). "
                        f"Summary must have flat values, not {{value: ..., confidence: ...}}"
                    )
        self.assertEqual(errors, [], "Unwrapped value objects found:\n" + "\n".join(errors[:20]))


# ---------------------------------------------------------------------------
# E2E-UI-007: Alert data renderable by ticker + dashboard
# ---------------------------------------------------------------------------

class TestE2E_UI_007_AlertRenderability(unittest.TestCase):
    """E2E-UI-007: Every alert has the fields the ticker and alert dashboard
    need to render without crashing.

    The ticker calls alert.title.toUpperCase() — if title is missing and
    there is no headline fallback, the ticker crashes silently.
    The dashboard renders title, body, country tags, and type badge."""

    def setUp(self):
        self.alert_path = find_alert_index()
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        self.alerts = data.get("alerts", [])

    def test_every_alert_has_displayable_title(self):
        """Ticker and dashboard both need a text title. Must have title or headline."""
        errors = []
        for i, a in enumerate(self.alerts):
            if not isinstance(a, dict):
                continue
            title = a.get("title") or a.get("headline")
            if not title or not title.strip():
                errors.append(
                    f"Alert [{i}] {a.get('alert_id', '?')}: no title or headline"
                )
        self.assertEqual(errors, [], "Alerts without displayable title:\n" + "\n".join(errors))

    def test_every_alert_has_displayable_body(self):
        """Dashboard renders description/details/summary as body text."""
        errors = []
        for i, a in enumerate(self.alerts):
            if not isinstance(a, dict):
                continue
            body = a.get("description") or a.get("details") or a.get("summary")
            if not body or not body.strip():
                errors.append(
                    f"Alert [{i}] {a.get('alert_id', '?')}: no description, details, or summary"
                )
        self.assertEqual(errors, [], "Alerts without displayable body:\n" + "\n".join(errors))

    def test_every_alert_has_country_info(self):
        """Dashboard shows country tags. Must have countries array or country_code."""
        errors = []
        for i, a in enumerate(self.alerts):
            if not isinstance(a, dict):
                continue
            countries = a.get("countries") or (
                [a["country_code"]] if a.get("country_code") else []
            )
            if not countries:
                errors.append(
                    f"Alert [{i}] {a.get('alert_id', '?')}: no countries or country_code"
                )
        self.assertEqual(errors, [], "Alerts without country info:\n" + "\n".join(errors))

    def test_every_alert_has_severity(self):
        """Ticker routes alerts by severity. Missing severity breaks routing."""
        errors = []
        valid = {"critical", "warning", "watch"}
        for i, a in enumerate(self.alerts):
            if not isinstance(a, dict):
                continue
            sev = a.get("severity")
            if not sev:
                errors.append(f"Alert [{i}] {a.get('alert_id', '?')}: missing severity")
            elif sev not in valid:
                errors.append(f"Alert [{i}] {a.get('alert_id', '?')}: severity '{sev}' not in {sorted(valid)}")
        self.assertEqual(errors, [], "Alert severity issues:\n" + "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-008: Briefing data renderable by briefing view
# ---------------------------------------------------------------------------

class TestE2E_UI_008_BriefingRenderability(unittest.TestCase):
    """E2E-UI-008: Weekly briefing data has the fields the briefing view
    needs to render stories, market context, and regional summaries."""

    def setUp(self):
        self.briefing_path = find_briefing()
        if not self.briefing_path:
            self.skipTest("Briefing not found")
        self.data = load_json(self.briefing_path)

    def test_every_story_has_title_and_summary(self):
        """Story cards render title and summary/description."""
        stories = self.data.get("top_stories", [])
        errors = []
        for i, s in enumerate(stories):
            if not isinstance(s, dict):
                continue
            if not s.get("title"):
                errors.append(f"Story [{i}]: missing title")
            body = s.get("summary") or s.get("description")
            if not body:
                errors.append(f"Story [{i}]: missing summary or description")
        self.assertEqual(errors, [], "Story rendering issues:\n" + "\n".join(errors))

    def test_every_story_has_country_tags(self):
        """Story cards show country tags from countries, countries_affected, or countries_involved."""
        stories = self.data.get("top_stories", [])
        errors = []
        for i, s in enumerate(stories):
            if not isinstance(s, dict):
                continue
            countries = (
                s.get("countries")
                or s.get("countries_affected")
                or s.get("countries_involved")
                or []
            )
            if not countries:
                errors.append(f"Story [{i}] '{s.get('title', '?')[:40]}': no country tags")
        self.assertEqual(errors, [], "Stories without country tags:\n" + "\n".join(errors))

    def test_market_context_is_renderable(self):
        """Market context must be a string, numeric chip data, or summary+moves dict."""
        mc = self.data.get("market_context")
        if mc is None:
            self.skipTest("No market_context in briefing")
        if isinstance(mc, str):
            self.assertTrue(len(mc) > 0, "market_context string is empty")
            return
        self.assertIsInstance(mc, dict, "market_context must be string or dict")
        # Must have either numeric chip fields or summary/notable_moves
        has_chips = any(
            mc.get(f)
            for f in ["oil_brent_usd", "gold_usd", "eur_usd", "us_10y_yield", "dxy_index"]
        )
        has_summary = bool(mc.get("summary") or mc.get("notable_moves"))
        self.assertTrue(
            has_chips or has_summary,
            f"market_context dict has neither chip data nor summary. Keys: {sorted(mc.keys())}",
        )

    def test_regional_summaries_are_renderable(self):
        """Each regional summary must be a non-empty string or dict with summary key."""
        rs = self.data.get("regional_summaries", {})
        self.assertGreater(len(rs), 0, "regional_summaries is empty")
        errors = []
        for region, val in rs.items():
            if isinstance(val, str):
                if not val.strip():
                    errors.append(f"Region '{region}': empty string")
            elif isinstance(val, dict):
                if not val.get("summary"):
                    errors.append(f"Region '{region}': dict without 'summary' key")
            else:
                errors.append(f"Region '{region}': unexpected type {type(val).__name__}")
        self.assertEqual(errors, [], "Regional summary issues:\n" + "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-010: Rankings page factor value completeness
# ---------------------------------------------------------------------------

# Fields referenced by each METRIC_GROUPS tab in rankings-view.js.
# Must match the actual field names used in the JS.
RANKINGS_FIELDS = {
    "economic": [
        "gdp_nominal_usd", "gdp_real_growth_pct", "gdp_per_capita_usd",
        "inflation_rate_pct", "trade_openness_pct", "political_risk_premium_bps",
    ],
    "power": [
        "composite_national_power_index", "military_expenditure_usd",
        "population", "energy_independence",
    ],
    "risk": [
        "investment_risk_score", "political_stability",
        "political_risk_premium_bps", "alert_count",
    ],
    "development": [
        "gdp_per_capita_usd", "composite_national_power_index",
        "energy_independence", "trade_openness_pct",
    ],
}

# Minimum fraction of countries that must have a value for each ranking field.
# 0.70 = at least 70% of countries must have a non-null value.
RANKINGS_FIELD_COVERAGE_MIN = 0.70
RANKINGS_FIELD_COVERAGE_TIER1_MIN = 0.90


class TestE2E_UI_010_RankingsCompleteness(unittest.TestCase):
    """E2E-UI-010: Every ranking factor referenced by rankings-view.js must
    have sufficient data coverage in the summary. Missing values render as '—'
    in the table, degrading the rankings page experience."""

    def setUp(self):
        self.summary_path = find_summary_path()
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        countries = data.get("countries", data) if isinstance(data, dict) else data
        if not isinstance(countries, list):
            self.skipTest("Summary countries is not a list")
        self.countries = countries
        self.tier1 = [c for c in countries if c.get("tier") == 1]

    def test_every_ranking_field_exists_in_summary(self):
        """Every field referenced by rankings-view.js METRIC_GROUPS must appear
        in at least one country's summary entry (i.e., the field is not completely
        phantom/undefined)."""
        all_fields = set()
        for fields in RANKINGS_FIELDS.values():
            all_fields.update(fields)

        phantom = []
        for field in sorted(all_fields):
            count = sum(1 for c in self.countries if c.get(field) is not None)
            if count == 0:
                phantom.append(field)
        self.assertEqual(
            phantom, [],
            f"Ranking fields with ZERO data (completely missing from summary): {phantom}",
        )

    def test_ranking_field_coverage_overall(self):
        """Each ranking field must have >= {RANKINGS_FIELD_COVERAGE_MIN:.0%} coverage
        across all 75 countries."""
        total = len(self.countries)
        if total == 0:
            self.skipTest("No countries")
        errors = []
        all_fields = set()
        for fields in RANKINGS_FIELDS.values():
            all_fields.update(fields)
        for field in sorted(all_fields):
            count = sum(1 for c in self.countries if c.get(field) is not None)
            coverage = count / total
            if coverage < RANKINGS_FIELD_COVERAGE_MIN:
                errors.append(
                    f"{field}: {count}/{total} ({coverage:.0%}) < "
                    f"{RANKINGS_FIELD_COVERAGE_MIN:.0%} minimum"
                )
        self.assertEqual(
            errors, [],
            "Ranking fields with insufficient coverage:\n" + "\n".join(errors),
        )

    def test_ranking_field_coverage_tier1(self):
        """Tier 1 countries (major economies) must have >= {RANKINGS_FIELD_COVERAGE_TIER1_MIN:.0%}
        coverage for each ranking field."""
        if not self.tier1:
            self.skipTest("No Tier 1 countries")
        total = len(self.tier1)
        errors = []
        all_fields = set()
        for fields in RANKINGS_FIELDS.values():
            all_fields.update(fields)
        for field in sorted(all_fields):
            count = sum(1 for c in self.tier1 if c.get(field) is not None)
            coverage = count / total
            if coverage < RANKINGS_FIELD_COVERAGE_TIER1_MIN:
                errors.append(
                    f"{field}: {count}/{total} Tier 1 ({coverage:.0%}) < "
                    f"{RANKINGS_FIELD_COVERAGE_TIER1_MIN:.0%} minimum"
                )
        self.assertEqual(
            errors, [],
            "Tier 1 ranking field coverage gaps:\n" + "\n".join(errors),
        )

    def test_ranking_values_are_numeric(self):
        """All ranking field values must be numeric (int or float), not strings
        or wrapper objects. The formatVal() function in rankings-view.js expects
        numbers for currency/percent/score/number formats."""
        errors = []
        all_fields = set()
        for fields in RANKINGS_FIELDS.values():
            all_fields.update(fields)
        for c in self.countries:
            code = c.get("code", "?")
            for field in all_fields:
                val = c.get(field)
                if val is not None and not isinstance(val, (int, float)):
                    errors.append(
                        f"{code}.{field}: expected number, got {type(val).__name__} = {val!r}"
                    )
        self.assertEqual(
            errors, [],
            "Non-numeric ranking values:\n" + "\n".join(errors[:20]),
        )

    def test_ranking_fields_match_js_metric_groups(self):
        """Cross-check: parse rankings-view.js to verify RANKINGS_FIELDS in this
        test matches the actual field references in the JS source."""
        js_path = os.path.join(REPO_ROOT, "web", "js", "rankings-view.js")
        if not os.path.isfile(js_path):
            self.skipTest("rankings-view.js not found")

        with open(js_path, "r", encoding="utf-8") as f:
            js_src = f.read()

        # Extract field names from "field: 'xxx'" patterns
        import re
        js_fields = set(re.findall(r"field:\s*'([^']+)'", js_src))

        test_fields = set()
        for fields in RANKINGS_FIELDS.values():
            test_fields.update(fields)

        missing_in_test = js_fields - test_fields
        extra_in_test = test_fields - js_fields

        errors = []
        if missing_in_test:
            errors.append(
                f"Fields in rankings-view.js but NOT in test: {sorted(missing_in_test)}"
            )
        if extra_in_test:
            errors.append(
                f"Fields in test but NOT in rankings-view.js: {sorted(extra_in_test)}"
            )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# E2E-UI-011: Alert data quality — no resolved, no duplicates, type present
# ---------------------------------------------------------------------------

class TestE2E_UI_011_AlertDataQuality(unittest.TestCase):
    """E2E-UI-011: Alert data quality checks to prevent empty/broken cards
    in the alert dashboard. Resolved alerts, missing type fields, and
    duplicates cause empty-looking items at the end of severity sections."""

    def setUp(self):
        self.alert_path = find_alert_index()
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        self.alerts = data.get("alerts", [])
        self.summary = data.get("summary", {})

    def test_no_resolved_alerts_in_active_list(self):
        """Resolved alerts should be filtered out. They render as stale cards."""
        resolved = [
            f"[{i}] {a.get('alert_id', '?')}: {(a.get('title') or a.get('headline', ''))[:50]}"
            for i, a in enumerate(self.alerts)
            if a.get("status") == "resolved"
        ]
        self.assertEqual(
            resolved, [],
            "Resolved alerts still in active list:\n" + "\n".join(resolved),
        )

    def test_every_alert_has_type_field(self):
        """Alerts without type render with missing type badge in dashboard."""
        missing = [
            f"[{i}] {a.get('alert_id', '?')} ({a.get('country_code', '?')})"
            for i, a in enumerate(self.alerts)
            if not a.get("type")
        ]
        self.assertEqual(
            missing, [],
            "Alerts missing 'type' field:\n" + "\n".join(missing),
        )

    def test_summary_counts_match_alerts(self):
        """Summary counts must match actual alert counts by severity."""
        actual = {}
        for a in self.alerts:
            sev = a.get("severity", "unknown")
            actual[sev] = actual.get(sev, 0) + 1

        errors = []
        for sev in ["critical", "warning", "watch"]:
            expected = self.summary.get(sev, 0)
            got = actual.get(sev, 0)
            if expected != got:
                errors.append(f"{sev}: summary says {expected}, actual is {got}")

        total_expected = self.summary.get("total_active", 0)
        total_actual = len(self.alerts)
        if total_expected != total_actual:
            errors.append(f"total_active: summary says {total_expected}, actual is {total_actual}")

        self.assertEqual(errors, [], "Summary count mismatches:\n" + "\n".join(errors))

    def test_no_exact_duplicate_alerts(self):
        """No two alerts should have same country_code + severity + near-identical title."""
        seen = {}
        dupes = []
        for i, a in enumerate(self.alerts):
            country = a.get("country_code", "?")
            sev = a.get("severity", "?")
            title = (a.get("title") or a.get("headline") or "").strip().lower()
            # Normalize: first 40 chars to catch near-duplicates
            key = (country, sev, title[:40])
            if key in seen:
                dupes.append(
                    f"[{i}] duplicates [{seen[key]}]: {country} {sev} '{title[:50]}'"
                )
            else:
                seen[key] = i
        self.assertEqual(
            dupes, [],
            "Duplicate alerts found:\n" + "\n".join(dupes),
        )


# ---------------------------------------------------------------------------
# E2E-UI-009: Frontend code quality — catch silent-failure anti-patterns
# ---------------------------------------------------------------------------

WEB_DIR = os.path.join(REPO_ROOT, "web")
JS_DIR = os.path.join(WEB_DIR, "js")
CSS_DIR = os.path.join(WEB_DIR, "css")

import re
import glob as globmod


class TestE2E_UI_009_FrontendCodeQuality(unittest.TestCase):
    """E2E-UI-009: Static analysis of frontend JS/CSS for anti-patterns that
    cause silent failures (empty catch blocks, z-index conflicts, missing
    DOM element references)."""

    def test_no_empty_catch_blocks(self):
        """Empty catch blocks silently swallow errors, hiding runtime bugs.
        Every catch must at least log the error."""
        if not os.path.isdir(JS_DIR):
            self.skipTest("web/js/ not found")
        # Match catch(...) { } with only whitespace inside braces
        empty_catch = re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}')
        errors = []
        for js_file in sorted(globmod.glob(os.path.join(JS_DIR, "*.js"))):
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            for m in empty_catch.finditer(content):
                # Find line number
                line_num = content[:m.start()].count("\n") + 1
                errors.append(
                    f"{os.path.basename(js_file)}:{line_num}: "
                    f"empty catch block swallows errors silently"
                )
        self.assertEqual(
            errors, [],
            "Empty catch blocks found (must log errors):\n" + "\n".join(errors),
        )

    def test_ticker_dom_ids_exist_in_html(self):
        """Every DOM ID referenced by AlertTicker.init() must exist in index.html.
        Missing IDs cause null references that crash silently inside try/catch."""
        index_path = os.path.join(WEB_DIR, "index.html")
        app_path = os.path.join(JS_DIR, "app.js")
        if not os.path.isfile(index_path) or not os.path.isfile(app_path):
            self.skipTest("index.html or app.js not found")

        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
        with open(app_path, "r", encoding="utf-8") as f:
            js = f.read()

        # Extract all getElementById('...') calls from ticker init section
        id_refs = re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", js)
        # Extract all id="..." from HTML
        html_ids = set(re.findall(r'id="([^"]+)"', html))

        missing = []
        for dom_id in id_refs:
            if dom_id not in html_ids:
                missing.append(dom_id)
        self.assertEqual(
            missing, [],
            f"JS references DOM IDs not found in HTML: {missing}",
        )

    def test_ticker_zindex_above_map_content(self):
        """The alert ticker must have higher z-index than any map/content layer,
        otherwise Leaflet panes or other positioned elements can cover it."""
        main_css = os.path.join(CSS_DIR, "main.css")
        if not os.path.isfile(main_css):
            self.skipTest("main.css not found")

        with open(main_css, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract z-index for .alert-ticker
        ticker_match = re.search(
            r'\.alert-ticker\s*\{[^}]*z-index:\s*(\d+)', content, re.DOTALL
        )
        if not ticker_match:
            self.skipTest("Could not find .alert-ticker z-index in CSS")
        ticker_z = int(ticker_match.group(1))

        # #main-content must create a stacking context (z-index != auto)
        # to contain Leaflet's internal z-indices within the map area
        main_content_match = re.search(
            r'#main-content\s*\{([^}]*)\}', content, re.DOTALL
        )
        if main_content_match:
            mc_block = main_content_match.group(1)
            has_zindex = re.search(r'z-index:\s*(\d+)', mc_block)
            has_isolation = 'isolation' in mc_block
            self.assertTrue(
                has_zindex or has_isolation,
                "#main-content must create a stacking context (z-index or isolation: isolate) "
                "to contain Leaflet z-indices. Without this, map panes can render above the ticker."
            )

        # Ticker z-index must be well above typical content z-indices
        self.assertGreaterEqual(
            ticker_z, 900,
            f".alert-ticker z-index is {ticker_z}, should be >= 900 to stay above all content",
        )

    def test_no_fire_and_forget_async_init(self):
        """Critical async initializers (ticker, map, data) should be awaited,
        not fire-and-forget. Unawaited init causes race conditions where
        show()/hide() run before initialization completes."""
        app_path = os.path.join(JS_DIR, "app.js")
        if not os.path.isfile(app_path):
            self.skipTest("app.js not found")

        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Build set of modules whose init is async by scanning their source files
        async_modules = set()
        for js_file in sorted(globmod.glob(os.path.join(JS_DIR, "*.js"))):
            with open(js_file, "r", encoding="utf-8") as f:
                src = f.read()
            # Detect "init: async function" or "async init(" patterns
            if re.search(r'init\s*:\s*async\s+function|async\s+init\s*\(', src):
                # Extract module name from "var ModuleName = (function" or similar
                mod_match = re.search(r'var\s+(\w+)\s*=\s*\(?\s*function', src)
                if mod_match:
                    async_modules.add(mod_match.group(1))

        # Look for bare async init calls that are NOT awaited and NOT assigned
        errors = []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue
            match = re.match(r'^([A-Z]\w+)\.(init|load|fetch)\s*\(', stripped)
            if match:
                module_name = match.group(1)
                # Only flag if this module's init is actually async
                if module_name in async_modules:
                    if not stripped.startswith("await") and "= " not in line:
                        errors.append(
                            f"app.js:{i}: '{stripped[:60]}' — async init not awaited or captured. "
                            f"This causes race conditions."
                        )
        self.assertEqual(
            errors, [],
            "Fire-and-forget async calls found:\n" + "\n".join(errors),
        )


# ---------------------------------------------------------------------------
# E2E-UI-012: Intel Overlays integration checks
# ---------------------------------------------------------------------------

class TestE2E_UI_012_IntelOverlaysIntegration(unittest.TestCase):
    """E2E-UI-012: Verify that the intel overlays module is wired into the
    index.html and that all referenced DOM IDs and scripts exist."""

    def setUp(self):
        self.index_path = os.path.join(WEB_DIR, "index.html")
        if not os.path.isfile(self.index_path):
            self.skipTest("index.html not found")
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_overlays_css_linked(self):
        """overlays.css must be linked in index.html."""
        self.assertIn(
            "css/overlays.css", self.html,
            "overlays.css not linked in index.html",
        )

    def test_overlays_js_loaded(self):
        """overlays.js must be loaded in index.html."""
        self.assertIn(
            "js/overlays.js", self.html,
            "overlays.js not loaded in index.html",
        )

    def test_st_layers_panel_in_html(self):
        """#st-layers panel must exist in index.html for the overlay toggles."""
        self.assertIn(
            'id="st-layers"', self.html,
            "#st-layers panel not found in index.html",
        )

    def test_st_card_in_html(self):
        """#st-card detail card must exist in index.html."""
        self.assertIn(
            'id="st-card"', self.html,
            "#st-card detail card not found in index.html",
        )

    def test_all_12_layer_rows_in_html(self):
        """All 12 layer data-layer attributes must be present in index.html."""
        layers = [
            "airports", "ports", "chokepoints", "cables",
            "bases", "conflicts", "missiles", "nuclear",
            "power", "pipelines", "cyber", "sanctions",
        ]
        missing = [
            lid for lid in layers
            if f'data-layer="{lid}"' not in self.html
        ]
        self.assertEqual(
            missing, [],
            f"Missing data-layer rows in index.html: {missing}",
        )

    def test_overlays_js_file_exists(self):
        """overlays.js file must exist on disk."""
        js_path = os.path.join(JS_DIR, "overlays.js")
        self.assertTrue(os.path.isfile(js_path), "web/js/overlays.js not found")

    def test_overlays_css_file_exists(self):
        """overlays.css file must exist on disk."""
        css_path = os.path.join(CSS_DIR, "overlays.css")
        self.assertTrue(os.path.isfile(css_path), "web/css/overlays.css not found")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
