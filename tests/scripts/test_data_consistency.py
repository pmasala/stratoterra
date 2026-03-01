#!/usr/bin/env python3
"""
Stratoterra — Data Consistency Tests
Tests IT-CON-001 through IT-CON-008

Verifies cross-file integrity: country lists match files on disk, relation
pairs are canonically ordered, alert countries exist, etc.
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
COUNTRIES_DIR = os.path.join(DATA_DIR, "countries")
RELATIONS_DIR = os.path.join(DATA_DIR, "relations")
GLOBAL_DIR = os.path.join(DATA_DIR, "global")
TIMESERIES_DIR = os.path.join(DATA_DIR, "timeseries")
SUPRANATIONAL_DIR = os.path.join(DATA_DIR, "supranational")

COUNTRY_LIST_PATH = os.path.join(INDICES_DIR, "country_list.json")
RELATION_INDEX_PATH = os.path.join(INDICES_DIR, "relation_index.json")
ALERT_INDEX_PATH = os.path.join(INDICES_DIR, "alert_index.json")
RANKINGS_PATH = os.path.join(GLOBAL_DIR, "global_rankings.json")

SUMMARY_PATHS = [
    os.path.join(CHUNKS_DIR, "country-summary", "all_countries_summary.json"),
    os.path.join(CHUNKS_DIR, "all_countries_summary.json"),
]

EXPECTED_COUNTRY_COUNT = 75


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


def glob_json_files(directory):
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".json")
    )


def load_country_list():
    """Load country_list.json and return set of ISO codes."""
    if not os.path.isfile(COUNTRY_LIST_PATH):
        return None
    data = load_json(COUNTRY_LIST_PATH)
    # Support both a plain array of codes and an array of objects with a 'code' field
    if isinstance(data, list):
        codes = set()
        for item in data:
            if isinstance(item, str):
                codes.add(item)
            elif isinstance(item, dict):
                code = item.get("code") or item.get("iso3") or item.get("iso_code")
                if code:
                    codes.add(code)
        return codes
    if isinstance(data, dict):
        # Could be {"countries": [...]}
        for key in ("countries", "data", "items"):
            if key in data and isinstance(data[key], list):
                return load_country_list_from_array(data[key])
    return None


def load_country_list_from_array(arr):
    codes = set()
    for item in arr:
        if isinstance(item, str):
            codes.add(item)
        elif isinstance(item, dict):
            code = item.get("code") or item.get("iso3") or item.get("iso_code")
            if code:
                codes.add(code)
    return codes


def load_summary():
    path = find_file(SUMMARY_PATHS)
    if not path:
        return None
    data = load_json(path)
    return data if isinstance(data, list) else None


# ---------------------------------------------------------------------------
# IT-CON-001: Country list and country files match
# ---------------------------------------------------------------------------

class TestIT_CON_001_CountryListMatchesFiles(unittest.TestCase):
    """IT-CON-001: country_list.json entries have matching files and vice versa."""

    def setUp(self):
        self.country_codes_from_list = load_country_list()
        self.country_files = glob_json_files(COUNTRIES_DIR)
        self.codes_from_files = {
            os.path.basename(f).replace(".json", "") for f in self.country_files
        }

    def test_country_list_exists(self):
        if not os.path.isfile(COUNTRY_LIST_PATH):
            self.skipTest(f"country_list.json not found at {COUNTRY_LIST_PATH}")

    def test_every_list_entry_has_file(self):
        if self.country_codes_from_list is None:
            self.skipTest("country_list.json not found or unparseable")
        if not self.country_files:
            self.skipTest("No country files found — pipeline may not have run yet")
        missing_files = self.country_codes_from_list - self.codes_from_files
        self.assertEqual(
            missing_files,
            set(),
            f"Countries in country_list.json without a .json file: {sorted(missing_files)}",
        )

    def test_every_file_is_in_list(self):
        if self.country_codes_from_list is None:
            self.skipTest("country_list.json not found or unparseable")
        if not self.country_files:
            self.skipTest("No country files found — pipeline may not have run yet")
        orphaned = self.codes_from_files - self.country_codes_from_list
        self.assertEqual(
            orphaned,
            set(),
            f"Country files not listed in country_list.json: {sorted(orphaned)}",
        )


# ---------------------------------------------------------------------------
# IT-CON-002: Summary has exactly 75 entries and codes match country_list
# ---------------------------------------------------------------------------

class TestIT_CON_002_SummaryCountAndCodes(unittest.TestCase):
    """IT-CON-002: Summary has exactly 75 entries and codes align with country_list."""

    def setUp(self):
        self.summary = load_summary()
        self.country_codes_from_list = load_country_list()

    def test_summary_has_75_entries(self):
        if self.summary is None:
            self.skipTest("all_countries_summary.json not found or not a list")
        self.assertEqual(
            len(self.summary),
            EXPECTED_COUNTRY_COUNT,
            f"Expected {EXPECTED_COUNTRY_COUNT} countries in summary, got {len(self.summary)}",
        )

    def test_summary_codes_match_country_list(self):
        if self.summary is None:
            self.skipTest("all_countries_summary.json not found")
        if self.country_codes_from_list is None:
            self.skipTest("country_list.json not found")
        summary_codes = {item.get("code") for item in self.summary if isinstance(item, dict)}
        extra_in_summary = summary_codes - self.country_codes_from_list
        missing_from_summary = self.country_codes_from_list - summary_codes
        errors = []
        if extra_in_summary:
            errors.append(f"Codes in summary but not in country_list: {sorted(extra_in_summary)}")
        if missing_from_summary:
            errors.append(f"Codes in country_list but missing from summary: {sorted(missing_from_summary)}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_summary_codes_are_unique(self):
        if self.summary is None:
            self.skipTest("all_countries_summary.json not found")
        codes = [item.get("code") for item in self.summary if isinstance(item, dict)]
        duplicates = [c for c in codes if codes.count(c) > 1]
        self.assertEqual(
            list(set(duplicates)),
            [],
            f"Duplicate country codes in summary: {sorted(set(duplicates))}",
        )


# ---------------------------------------------------------------------------
# IT-CON-003: All country detail files have matching summary entries
# ---------------------------------------------------------------------------

class TestIT_CON_003_DetailFilesHaveSummaryEntries(unittest.TestCase):
    """IT-CON-003: Each country detail file has a corresponding entry in the summary."""

    def setUp(self):
        self.summary = load_summary()
        self.country_files = glob_json_files(COUNTRIES_DIR)

    def test_detail_files_in_summary(self):
        if self.summary is None:
            self.skipTest("all_countries_summary.json not found")
        if not self.country_files:
            self.skipTest("No country detail files found")
        summary_codes = {item.get("code") for item in self.summary if isinstance(item, dict)}
        missing = []
        for path in self.country_files:
            code = os.path.basename(path).replace(".json", "")
            if code not in summary_codes:
                missing.append(code)
        self.assertEqual(
            missing,
            [],
            f"Country files without summary entry: {missing}",
        )


# ---------------------------------------------------------------------------
# IT-CON-004: Relation pairs are alphabetically ordered
# ---------------------------------------------------------------------------

class TestIT_CON_004_RelationPairOrdering(unittest.TestCase):
    """IT-CON-004: All relation files and index entries use alphabetical pair ordering."""

    def setUp(self):
        self.relation_files = glob_json_files(RELATIONS_DIR)

    def test_relation_filenames_ordered(self):
        if not self.relation_files:
            self.skipTest("No relation files found")
        errors = []
        for path in self.relation_files:
            fname = os.path.basename(path).replace(".json", "")
            parts = fname.split("_")
            if len(parts) == 2:
                a, b = parts
                if a >= b:
                    errors.append(
                        f"Filename '{fname}.json': '{a}' is not alphabetically before '{b}'"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_relation_file_contents_ordered(self):
        if not self.relation_files:
            self.skipTest("No relation files found")
        errors = []
        for path in self.relation_files:
            try:
                data = load_json(path)
            except (json.JSONDecodeError, OSError):
                continue
            a = data.get("country_a", "")
            b = data.get("country_b", "")
            if a and b and a >= b:
                errors.append(
                    f"{os.path.basename(path)}: country_a='{a}' must sort before country_b='{b}'"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_relation_index_entries_ordered(self):
        if not os.path.isfile(RELATION_INDEX_PATH):
            self.skipTest("relation_index.json not found")
        try:
            data = load_json(RELATION_INDEX_PATH)
        except (json.JSONDecodeError, OSError):
            self.skipTest("relation_index.json could not be parsed")
        relations = data if isinstance(data, list) else data.get("relations", [])
        errors = []
        for entry in relations:
            if not isinstance(entry, dict):
                continue
            pair = entry.get("pair", "")
            parts = pair.split("_")
            if len(parts) == 2 and parts[0] >= parts[1]:
                errors.append(f"relation_index.json: pair '{pair}' not in alpha order")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# IT-CON-005: Alert countries exist in country list
# ---------------------------------------------------------------------------

class TestIT_CON_005_AlertCountriesValid(unittest.TestCase):
    """IT-CON-005: All countries referenced in alerts exist in country_list.json."""

    def setUp(self):
        self.country_codes = load_country_list()

    def test_alert_countries_in_list(self):
        if not os.path.isfile(ALERT_INDEX_PATH):
            self.skipTest("alert_index.json not found")
        if self.country_codes is None:
            self.skipTest("country_list.json not found")
        try:
            data = load_json(ALERT_INDEX_PATH)
        except (json.JSONDecodeError, OSError):
            self.skipTest("alert_index.json could not be parsed")
        errors = []
        for i, alert in enumerate(data.get("alerts", [])):
            if not isinstance(alert, dict):
                continue
            for country_field in ("countries", "countries_affected"):
                for code in alert.get(country_field, []):
                    if code not in self.country_codes:
                        errors.append(
                            f"Alert [{i}] '{alert.get('title', '')}': "
                            f"references unknown country '{code}'"
                        )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# IT-CON-006: Rankings reference valid metric fields and are ordered
# ---------------------------------------------------------------------------

class TestIT_CON_006_RankingsConsistency(unittest.TestCase):
    """IT-CON-006: Rankings in global_rankings.json are correctly ordered and reference valid countries."""

    def setUp(self):
        self.country_codes = load_country_list()

    def test_rankings_exist(self):
        if not os.path.isfile(RANKINGS_PATH):
            self.skipTest("global_rankings.json not found")

    def test_rankings_valid_json(self):
        if not os.path.isfile(RANKINGS_PATH):
            self.skipTest("global_rankings.json not found")
        try:
            load_json(RANKINGS_PATH)
        except json.JSONDecodeError as exc:
            self.fail(f"global_rankings.json is invalid JSON: {exc}")

    def test_rankings_country_codes_valid(self):
        if not os.path.isfile(RANKINGS_PATH):
            self.skipTest("global_rankings.json not found")
        if self.country_codes is None:
            self.skipTest("country_list.json not found")
        data = load_json(RANKINGS_PATH)
        errors = []
        # Rankings may be a dict of metric_name -> list of {code, value, rank}
        rankings = data if isinstance(data, dict) else {}
        for metric, entries in rankings.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                code = entry.get("code") or entry.get("country_code")
                if code and code not in self.country_codes:
                    errors.append(
                        f"Rankings metric '{metric}': unknown country code '{code}'"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_rankings_no_duplicate_rank_positions(self):
        if not os.path.isfile(RANKINGS_PATH):
            self.skipTest("global_rankings.json not found")
        data = load_json(RANKINGS_PATH)
        errors = []
        rankings = data if isinstance(data, dict) else {}
        for metric, entries in rankings.items():
            if not isinstance(entries, list):
                continue
            ranks = [e.get("rank") for e in entries if isinstance(e, dict) and e.get("rank") is not None]
            if len(ranks) != len(set(ranks)):
                errors.append(f"Rankings metric '{metric}': duplicate rank positions found")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# IT-CON-007: Relation index and files are mutually consistent
# ---------------------------------------------------------------------------

class TestIT_CON_007_RelationIndexAndFilesMatch(unittest.TestCase):
    """IT-CON-007: relation_index.json and /data/relations/ files are consistent."""

    def setUp(self):
        self.relation_files = glob_json_files(RELATIONS_DIR)
        self.pairs_from_files = {
            os.path.basename(f).replace(".json", "") for f in self.relation_files
        }

    def test_index_entries_have_files(self):
        if not os.path.isfile(RELATION_INDEX_PATH):
            self.skipTest("relation_index.json not found")
        if not self.relation_files:
            self.skipTest("No relation files found")
        data = load_json(RELATION_INDEX_PATH)
        relations = data if isinstance(data, list) else data.get("relations", [])
        missing = []
        for entry in relations:
            if not isinstance(entry, dict):
                continue
            pair = entry.get("pair", "")
            if pair and pair not in self.pairs_from_files:
                missing.append(pair)
        self.assertEqual(
            missing,
            [],
            f"Pairs in relation_index.json with no file on disk: {missing}",
        )

    def test_relation_files_are_in_index(self):
        if not os.path.isfile(RELATION_INDEX_PATH):
            self.skipTest("relation_index.json not found")
        if not self.relation_files:
            self.skipTest("No relation files found")
        data = load_json(RELATION_INDEX_PATH)
        relations = data if isinstance(data, list) else data.get("relations", [])
        indexed_pairs = {
            e.get("pair") for e in relations if isinstance(e, dict) and e.get("pair")
        }
        orphaned = self.pairs_from_files - indexed_pairs
        self.assertEqual(
            orphaned,
            set(),
            f"Relation files not listed in relation_index.json: {sorted(orphaned)}",
        )


# ---------------------------------------------------------------------------
# IT-CON-008: Chunk manifest accuracy
# ---------------------------------------------------------------------------

class TestIT_CON_008_ChunkManifestAccuracy(unittest.TestCase):
    """IT-CON-008: manifest.json accurately reflects files on disk."""

    MANIFEST_PATH = os.path.join(CHUNKS_DIR, "manifest.json")

    def test_manifest_files_exist(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        data = load_json(self.MANIFEST_PATH)
        missing = []
        for entry in data.get("files", []):
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path", "")
            abs_path = os.path.join(CHUNKS_DIR, rel)
            if not os.path.isfile(abs_path):
                missing.append(rel)
        self.assertEqual(
            missing,
            [],
            f"Files listed in manifest.json but not found on disk:\n" + "\n".join(missing),
        )

    def test_manifest_size_accuracy(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        data = load_json(self.MANIFEST_PATH)
        tolerance_bytes = 1024  # 1 KB tolerance
        errors = []
        for entry in data.get("files", []):
            if not isinstance(entry, dict):
                continue
            rel = entry.get("path", "")
            declared_size = entry.get("size_bytes")
            if declared_size is None:
                continue
            abs_path = os.path.join(CHUNKS_DIR, rel)
            if not os.path.isfile(abs_path):
                continue
            actual_size = os.path.getsize(abs_path)
            if abs(actual_size - declared_size) > tolerance_bytes:
                errors.append(
                    f"{rel}: declared {declared_size}B, actual {actual_size}B "
                    f"(delta {abs(actual_size - declared_size)}B)"
                )
        self.assertEqual(
            errors,
            [],
            f"Manifest size discrepancies (tolerance {tolerance_bytes}B):\n"
            + "\n".join(errors),
        )

    def test_manifest_summary_chunk_country_count(self):
        if not os.path.isfile(self.MANIFEST_PATH):
            self.skipTest("manifest.json not found")
        data = load_json(self.MANIFEST_PATH)
        summary_info = data.get("summary_chunk", {})
        if not summary_info:
            return  # optional field, no failure
        count = summary_info.get("country_count")
        if count is not None:
            self.assertEqual(
                count,
                EXPECTED_COUNTRY_COUNT,
                f"manifest.json summary_chunk.country_count={count}, "
                f"expected {EXPECTED_COUNTRY_COUNT}",
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
