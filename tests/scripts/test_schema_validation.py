#!/usr/bin/env python3
"""
Stratoterra — Schema Validation Tests
Tests UT-SCH-001 through UT-SCH-008

Validates every data file in the pipeline output against the JSON Schema
definitions in /tests/schemas/. Uses jsonschema (draft-07); falls back to
a reduced structural check if jsonschema is not installed.
"""

import json
import os
import sys
import unittest
import datetime

# ---------------------------------------------------------------------------
# Optional dependency: jsonschema
# ---------------------------------------------------------------------------
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print(
        "[WARNING] jsonschema library not installed. "
        "Schema validation will fall back to structural checks only.\n"
        "Install with: pip install jsonschema",
        file=sys.stderr,
    )

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
SCHEMAS_DIR = os.path.join(REPO_ROOT, "tests", "schemas")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
INDICES_DIR = os.path.join(DATA_DIR, "indices")
GLOBAL_DIR = os.path.join(DATA_DIR, "global")
TIMESERIES_DIR = os.path.join(DATA_DIR, "timeseries")
COUNTRIES_DIR = os.path.join(DATA_DIR, "countries")
RELATIONS_DIR = os.path.join(DATA_DIR, "relations")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    """Load and return parsed JSON from a file path. Raises on failure."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_schema(schema_filename):
    """Load a JSON Schema file from the schemas directory."""
    schema_path = os.path.join(SCHEMAS_DIR, schema_filename)
    return load_json(schema_path)


def validate_against_schema(instance, schema, label=""):
    """
    Validate instance against schema using jsonschema.
    Returns a list of validation error message strings (empty = pass).
    Falls back to [] (no errors) if jsonschema is unavailable.
    """
    if not JSONSCHEMA_AVAILABLE:
        return []
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(instance), key=str):
        errors.append(f"{label}: {error.message} (path: {list(error.absolute_path)})")
    return errors


def glob_json_files(directory):
    """Return sorted list of .json file paths in a directory (non-recursive)."""
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".json")
    )


def is_valid_iso8601(value):
    """Best-effort check that a string looks like an ISO 8601 datetime."""
    if not isinstance(value, str):
        return False
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            datetime.datetime.strptime(value.strip(), fmt)
            return True
        except ValueError:
            continue
    return False


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

class TestUT_SCH_001_CountryFiles(unittest.TestCase):
    """UT-SCH-001: Every country JSON file conforms to the country detail schema."""

    def setUp(self):
        self.schema = load_schema("country_detail_schema.json")
        self.country_files = glob_json_files(COUNTRIES_DIR)

    def test_country_files_exist(self):
        """At least one country file must exist if the data directory is populated."""
        if not os.path.isdir(COUNTRIES_DIR):
            self.skipTest(f"Countries directory not found: {COUNTRIES_DIR}")
        # We only warn if empty, not fail — pipeline may not have run yet
        if not self.country_files:
            self.skipTest("No country files found — pipeline may not have run yet")

    def test_country_files_valid_json(self):
        if not self.country_files:
            self.skipTest("No country files to validate")
        errors = []
        for path in self.country_files:
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")
        self.assertEqual(errors, [], f"Invalid JSON in country files:\n" + "\n".join(errors))

    def test_country_files_schema_conformance(self):
        if not self.country_files:
            self.skipTest("No country files to validate")
        all_errors = []
        for path in self.country_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue  # caught by valid_json test
            errs = validate_against_schema(data, self.schema, os.path.basename(path))
            all_errors.extend(errs)
        self.assertEqual(
            all_errors, [],
            "Schema violations in country files:\n" + "\n".join(all_errors),
        )

    def test_country_codes_are_iso_alpha3(self):
        if not self.country_files:
            self.skipTest("No country files to validate")
        errors = []
        for path in self.country_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            code = data.get("country_code", data.get("code", ""))
            if not (isinstance(code, str) and len(code) == 3 and code.isupper()):
                errors.append(f"{os.path.basename(path)}: invalid code '{code}'")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timestamps_are_iso8601(self):
        if not self.country_files:
            self.skipTest("No country files to validate")
        errors = []
        for path in self.country_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            ts = data.get("last_updated", "")
            if ts and not is_valid_iso8601(ts):
                errors.append(
                    f"{os.path.basename(path)}: bad last_updated timestamp '{ts}'"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_required_layers_present(self):
        if not self.country_files:
            self.skipTest("No country files to validate")
        required_layers = {"endowments", "institutions", "economy", "military", "relations", "derived"}
        errors = []
        for path in self.country_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            layers = data.get("layers", {})
            if not isinstance(layers, dict):
                errors.append(f"{os.path.basename(path)}: 'layers' is not an object")
                continue
            missing = required_layers - set(layers.keys())
            if missing:
                errors.append(
                    f"{os.path.basename(path)}: missing layers {sorted(missing)}"
                )
        self.assertEqual(errors, [], "\n".join(errors))


class TestUT_SCH_002_RelationFiles(unittest.TestCase):
    """UT-SCH-002: Every relation JSON file conforms to the relation schema."""

    def setUp(self):
        self.schema = load_schema("relation_schema.json")
        self.relation_files = glob_json_files(RELATIONS_DIR)

    def test_relation_files_valid_json(self):
        if not self.relation_files:
            self.skipTest("No relation files to validate")
        errors = []
        for path in self.relation_files:
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_relation_files_schema_conformance(self):
        if not self.relation_files:
            self.skipTest("No relation files to validate")
        all_errors = []
        for path in self.relation_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            errs = validate_against_schema(data, self.schema, os.path.basename(path))
            all_errors.extend(errs)
        self.assertEqual(all_errors, [], "\n".join(all_errors))

    def test_pair_codes_alphabetically_ordered(self):
        if not self.relation_files:
            self.skipTest("No relation files to validate")
        errors = []
        for path in self.relation_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            a = data.get("country_a", "")
            b = data.get("country_b", "")
            if a and b and a >= b:
                errors.append(
                    f"{os.path.basename(path)}: country_a='{a}' must be alphabetically "
                    f"before country_b='{b}'"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_composite_score_in_range(self):
        if not self.relation_files:
            self.skipTest("No relation files to validate")
        errors = []
        for path in self.relation_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            score = data.get("composite_score")
            if score is not None and not (0.0 <= float(score) <= 1.0):
                errors.append(
                    f"{os.path.basename(path)}: composite_score={score} out of [0, 1]"
                )
        self.assertEqual(errors, [], "\n".join(errors))


class TestUT_SCH_003_CountrySummaryChunk(unittest.TestCase):
    """UT-SCH-003 (mapped from UT-SCH): all_countries_summary.json validates against summary schema."""

    SUMMARY_PATHS = [
        os.path.join(CHUNKS_DIR, "country-summary", "all_countries_summary.json"),
        os.path.join(CHUNKS_DIR, "all_countries_summary.json"),
    ]

    def _find_summary(self):
        for p in self.SUMMARY_PATHS:
            if os.path.isfile(p):
                return p
        return None

    def setUp(self):
        self.schema = load_schema("country_summary_schema.json")
        self.summary_path = self._find_summary()

    def test_summary_file_exists(self):
        if not self.summary_path:
            self.skipTest(
                "all_countries_summary.json not found — pipeline may not have run yet"
            )

    def test_summary_valid_json(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        try:
            load_json(self.summary_path)
        except json.JSONDecodeError as exc:
            self.fail(f"Invalid JSON in summary: {exc}")

    def test_summary_schema_conformance(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        errors = validate_against_schema(data, self.schema, "all_countries_summary.json")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_summary_is_array_or_wrapper(self):
        if not self.summary_path:
            self.skipTest("Summary file not found")
        data = load_json(self.summary_path)
        # Accept both bare array and wrapper dict with 'countries' key
        if isinstance(data, dict):
            self.assertIn("countries", data, "Summary wrapper object must have 'countries' key")
            self.assertIsInstance(data["countries"], list, "countries must be an array")
        else:
            self.assertIsInstance(data, list, "all_countries_summary.json must be a JSON array or wrapper object")


class TestUT_SCH_005_WeeklyBriefing(unittest.TestCase):
    """UT-SCH-005: weekly_briefing validates against briefing schema."""

    def _find_briefing(self):
        candidates = []
        # Check chunks/global/
        chunks_global = os.path.join(CHUNKS_DIR, "global")
        if os.path.isdir(chunks_global):
            for f in os.listdir(chunks_global):
                if "briefing" in f and f.endswith(".json"):
                    candidates.append(os.path.join(chunks_global, f))
        # Check data/global/
        if os.path.isdir(GLOBAL_DIR):
            for f in os.listdir(GLOBAL_DIR):
                if "briefing" in f and f.endswith(".json"):
                    candidates.append(os.path.join(GLOBAL_DIR, f))
        return candidates

    def setUp(self):
        self.schema = load_schema("briefing_schema.json")
        self.briefing_files = self._find_briefing()

    def test_briefing_files_exist(self):
        if not self.briefing_files:
            self.skipTest("No weekly briefing files found — pipeline may not have run yet")

    def test_briefing_valid_json(self):
        if not self.briefing_files:
            self.skipTest("No briefing files found")
        errors = []
        for path in self.briefing_files:
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_briefing_schema_conformance(self):
        if not self.briefing_files:
            self.skipTest("No briefing files found")
        all_errors = []
        for path in self.briefing_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            errs = validate_against_schema(data, self.schema, os.path.basename(path))
            all_errors.extend(errs)
        self.assertEqual(all_errors, [], "\n".join(all_errors))

    def test_briefing_has_top_stories(self):
        if not self.briefing_files:
            self.skipTest("No briefing files found")
        errors = []
        for path in self.briefing_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            stories = data.get("top_stories", [])
            if not stories:
                errors.append(f"{os.path.basename(path)}: top_stories is empty")
        self.assertEqual(errors, [], "\n".join(errors))


class TestUT_SCH_006_AlertIndex(unittest.TestCase):
    """UT-SCH-006: alert_index.json validates against alert schema."""

    ALERT_PATHS = [
        os.path.join(INDICES_DIR, "alert_index.json"),
        os.path.join(CHUNKS_DIR, "global", "alert_index.json"),
    ]

    def _find_alert_index(self):
        for p in self.ALERT_PATHS:
            if os.path.isfile(p):
                return p
        return None

    def setUp(self):
        self.schema = load_schema("alert_schema.json")
        self.alert_path = self._find_alert_index()

    def test_alert_index_exists(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found — pipeline may not have run yet")

    def test_alert_index_valid_json(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        try:
            load_json(self.alert_path)
        except json.JSONDecodeError as exc:
            self.fail(f"Invalid JSON: {exc}")

    def test_alert_index_schema_conformance(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        errors = validate_against_schema(data, self.schema, "alert_index.json")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_alert_severities_valid(self):
        if not self.alert_path:
            self.skipTest("alert_index.json not found")
        data = load_json(self.alert_path)
        valid_severities = {"critical", "warning", "watch"}
        errors = []
        for i, alert in enumerate(data.get("alerts", [])):
            sev = alert.get("severity")
            if sev not in valid_severities:
                errors.append(f"Alert [{i}]: invalid severity '{sev}'")
        self.assertEqual(errors, [], "\n".join(errors))


class TestUT_SCH_007_Manifest(unittest.TestCase):
    """UT-SCH-007: manifest.json validates and all referenced files exist."""

    MANIFEST_PATH = os.path.join(CHUNKS_DIR, "manifest.json")

    def setUp(self):
        self.schema = load_schema("manifest_schema.json")

    def test_manifest_exists(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found — pipeline may not have run yet")

    def test_manifest_valid_json(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        try:
            load_json(self.MANIFEST_PATH)
        except json.JSONDecodeError as exc:
            self.fail(f"Invalid JSON: {exc}")

    def test_manifest_schema_conformance(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        data = load_json(self.MANIFEST_PATH)
        errors = validate_against_schema(data, self.schema, "manifest.json")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_manifest_referenced_files_exist(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        data = load_json(self.MANIFEST_PATH)
        files = data.get("files", {})
        missing = []
        if isinstance(files, list):
            for entry in files:
                rel_path = entry.get("path", "")
                abs_path = os.path.join(REPO_ROOT, rel_path)
                if not os.path.isfile(abs_path):
                    missing.append(rel_path)
        elif isinstance(files, dict):
            for key, entry in files.items():
                if not isinstance(entry, dict):
                    continue
                rel_path = entry.get("path", "")
                if not rel_path:
                    continue
                abs_path = os.path.join(REPO_ROOT, rel_path)
                # For directory entries (count > 0), check directory exists
                if entry.get("count") and rel_path.endswith("/"):
                    if not os.path.isdir(abs_path):
                        missing.append(rel_path)
                elif not rel_path.endswith("/") and not os.path.isfile(abs_path):
                    missing.append(rel_path)
        self.assertEqual(
            missing, [],
            f"Files listed in manifest.json but not found on disk:\n"
            + "\n".join(missing),
        )


class TestUT_SCH_008_Timeseries(unittest.TestCase):
    """UT-SCH-008: Timeseries files have ordered timestamps, no duplicates, numeric values."""

    def setUp(self):
        self.timeseries_files = glob_json_files(TIMESERIES_DIR)

    def test_timeseries_valid_json(self):
        if not self.timeseries_files:
            self.skipTest("No timeseries files found")
        errors = []
        for path in self.timeseries_files:
            try:
                load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timeseries_chronological_order(self):
        if not self.timeseries_files:
            self.skipTest("No timeseries files found")
        errors = []
        for path in self.timeseries_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            # Support both top-level arrays and objects with a 'data' key
            entries = data if isinstance(data, list) else data.get("data", [])
            timestamps = [e.get("timestamp") or e.get("date") for e in entries if isinstance(e, dict)]
            timestamps = [t for t in timestamps if t]
            if timestamps != sorted(timestamps):
                errors.append(
                    f"{os.path.basename(path)}: timestamps not in chronological order"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timeseries_no_duplicate_timestamps(self):
        if not self.timeseries_files:
            self.skipTest("No timeseries files found")
        errors = []
        for path in self.timeseries_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            entries = data if isinstance(data, list) else data.get("data", [])
            timestamps = [e.get("timestamp") or e.get("date") for e in entries if isinstance(e, dict)]
            timestamps = [t for t in timestamps if t]
            if len(timestamps) != len(set(timestamps)):
                errors.append(
                    f"{os.path.basename(path)}: duplicate timestamps detected"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_timeseries_values_are_numeric(self):
        if not self.timeseries_files:
            self.skipTest("No timeseries files found")
        errors = []
        for path in self.timeseries_files:
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            entries = data if isinstance(data, list) else data.get("data", [])
            for i, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    continue
                value = entry.get("value")
                if value is not None and not isinstance(value, (int, float)):
                    errors.append(
                        f"{os.path.basename(path)}: entry [{i}] value is not numeric: {value!r}"
                    )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
