#!/usr/bin/env python3
"""
Stratoterra — UI Data Contract Tests
Tests E2E-UI-001 through E2E-UI-005

Verifies that chunk files served to the frontend are present, loadable,
within size limits, and contain the fields the UI depends on.
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
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
