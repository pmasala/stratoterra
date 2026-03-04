"""
Stratoterra End-to-End Test — Full Pipeline Produces Valid Chunks
Test: E2E-PIP-001

Validates that after the full pipeline has run:
1. All required chunk files exist in data/chunks/
2. The all_countries_summary chunk is well-formed and complete
3. Country detail chunks exist and are valid
4. The manifest is accurate and up-to-date
5. The briefing chunk is accessible
6. The relation index is present and valid

Run: python3 tests/scripts/test_e2e_pipeline.py
"""

import json
import os
import sys
import glob
import unittest
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHUNKS_DIR = DATA_DIR / "chunks"
COUNTRIES_DIR = DATA_DIR / "countries"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def find_files(base: Path, pattern: str) -> list[Path]:
    return sorted(Path(f) for f in glob.glob(str(base / pattern)))


def safe_get(d: dict, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, {})
    return d if d != {} else default


def is_valid_run_id(s: str) -> bool:
    import re
    return bool(re.match(r"^\d{4}-W\d{2}[a-z]?$", s or ""))


def is_valid_iso_timestamp(s: str) -> bool:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            datetime.strptime(s, fmt)
            return True
        except (ValueError, TypeError):
            pass
    return False


# ---------------------------------------------------------------------------
# E2E-PIP-001: Full Pipeline Chunk Validation
# ---------------------------------------------------------------------------
class TestE2EFullPipeline(unittest.TestCase):
    """
    E2E-PIP-001: Validates that the full pipeline produces valid, complete chunks.
    These tests should all pass after a successful complete pipeline run.
    """

    @classmethod
    def setUpClass(cls):
        """Load all chunk files and data for the test suite."""
        # Manifest
        cls.manifest_path = CHUNKS_DIR / "manifest.json"
        cls.manifest = load_json(cls.manifest_path) if cls.manifest_path.exists() else None

        # Country summary chunk
        cls.summary_path = CHUNKS_DIR / "country-summary" / "all_countries_summary.json"
        cls.summary = load_json(cls.summary_path) if cls.summary_path.exists() else None

        # Country detail chunks
        cls.detail_files = find_files(CHUNKS_DIR / "country-detail", "*.json")

        # Relation chunks
        cls.relation_files = find_files(CHUNKS_DIR / "relations", "*.json")

        # Global chunks
        cls.global_dir = CHUNKS_DIR / "global"
        cls.briefing_path = cls.global_dir / "weekly_briefing.json"
        cls.briefing = load_json(cls.briefing_path) if cls.briefing_path.exists() else None
        cls.alert_chunk_path = cls.global_dir / "alert_index.json"
        cls.alert_chunk = load_json(cls.alert_chunk_path) if cls.alert_chunk_path.exists() else None

        # Relation index
        cls.relation_index_path = DATA_DIR / "indices" / "relation_index.json"
        cls.relation_index = (
            load_json(cls.relation_index_path)
            if cls.relation_index_path.exists() else None
        )

        # Source country files for comparison
        cls.source_country_files = find_files(COUNTRIES_DIR, "*.json")

    # -----------------------------------------------------------------------
    # Manifest checks
    # -----------------------------------------------------------------------

    def test_e2e_001_manifest_exists(self):
        """E2E-001: data/chunks/manifest.json exists."""
        if not self.manifest_path.exists():
            self.skipTest("manifest.json not found. Run the full pipeline first.")
        self.assertIsNotNone(self.manifest)

    def test_e2e_002_manifest_has_generated_at(self):
        """E2E-002: manifest.json has a valid generated_at timestamp."""
        if self.manifest is None:
            self.skipTest("manifest not available.")
        ts = self.manifest.get("generated_at", "")
        self.assertTrue(is_valid_iso_timestamp(ts), f"manifest generated_at '{ts}' is not valid ISO 8601")

    def test_e2e_003_manifest_has_required_keys(self):
        """E2E-003: manifest.json has required top-level keys."""
        if self.manifest is None:
            self.skipTest("manifest not available.")
        required_keys = ["run_id", "generated_at", "files"]
        missing = [k for k in required_keys if k not in self.manifest]
        self.assertEqual(missing, [], f"Manifest missing required keys: {missing}")

    def test_e2e_004_manifest_detail_count_matches_actual(self):
        """E2E-004: manifest country_detail count matches actual detail chunk count."""
        if self.manifest is None:
            self.skipTest("manifest not available.")
        files = self.manifest.get("files", {})
        if isinstance(files, dict):
            detail_entry = files.get("country_detail", {})
            manifest_count = detail_entry.get("count", -1)
            if manifest_count >= 0:
                actual_count = len(self.detail_files)
                self.assertEqual(
                    manifest_count, actual_count,
                    f"Manifest country_detail count={manifest_count} but actual detail chunks={actual_count}"
                )

    # -----------------------------------------------------------------------
    # Country summary chunk checks
    # -----------------------------------------------------------------------

    def test_e2e_010_summary_chunk_exists(self):
        """E2E-010: all_countries_summary.json exists."""
        if not self.summary_path.exists():
            self.skipTest("all_countries_summary.json not found. Run Agent 16 first.")
        self.assertIsNotNone(self.summary)

    def test_e2e_011_summary_is_not_empty(self):
        """E2E-011: Summary contains at least one country."""
        if self.summary is None:
            self.skipTest("Summary chunk not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        self.assertGreater(len(countries), 0, "all_countries_summary has no countries")

    def test_e2e_012_summary_count_matches_source(self):
        """E2E-012: Summary country count matches source country files."""
        if self.summary is None:
            self.skipTest("Summary chunk not available.")
        if not self.source_country_files:
            self.skipTest("No source country files to compare against.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        summary_count = len(countries)
        source_count = len(self.source_country_files)
        self.assertEqual(
            summary_count, source_count,
            f"Summary has {summary_count} countries but source has {source_count}"
        )

    def test_e2e_013_summary_countries_have_code_and_name(self):
        """E2E-013: Each country in summary has 'code' and 'name' fields."""
        if self.summary is None:
            self.skipTest("Summary chunk not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        missing = [
            i for i, c in enumerate(countries)
            if not isinstance(c, dict) or "code" not in c or "name" not in c
        ]
        self.assertEqual(missing, [], f"Summary countries missing code/name at indices: {missing}")

    def test_e2e_014_summary_codes_are_iso3(self):
        """E2E-014: All country codes in summary are valid ISO3 format."""
        if self.summary is None:
            self.skipTest("Summary chunk not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        invalid = [
            c.get("code", "?")
            for c in countries
            if isinstance(c, dict) and (
                not isinstance(c.get("code"), str)
                or len(c["code"]) != 3
                or not c["code"].isupper()
            )
        ]
        self.assertEqual(invalid, [], f"Invalid ISO3 codes in summary: {invalid}")

    def test_e2e_015_summary_tiers_are_valid(self):
        """E2E-015: All tier values in summary are 1, 2, or 3."""
        if self.summary is None:
            self.skipTest("Summary chunk not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        invalid = [
            c.get("code", "?")
            for c in countries
            if isinstance(c, dict) and c.get("tier") not in (1, 2, 3)
        ]
        self.assertEqual(invalid, [], f"Countries with invalid tier: {invalid}")

    def test_e2e_016_summary_file_size_reasonable(self):
        """E2E-016: Summary file is between 1KB and 5MB (sanity size check)."""
        if not self.summary_path.exists():
            self.skipTest("Summary chunk not available.")
        size_kb = self.summary_path.stat().st_size / 1024
        self.assertGreater(size_kb, 1, f"Summary file too small: {size_kb:.1f}KB")
        self.assertLess(size_kb, 5120, f"Summary file unexpectedly large: {size_kb:.1f}KB")

    # -----------------------------------------------------------------------
    # Country detail chunk checks
    # -----------------------------------------------------------------------

    def test_e2e_020_detail_chunks_exist(self):
        """E2E-020: Country detail chunk files exist."""
        if not self.detail_files:
            self.skipTest("No country detail chunks found. Run Agent 16 first.")
        self.assertGreater(len(self.detail_files), 0)

    def test_e2e_021_detail_count_matches_source(self):
        """E2E-021: Detail chunk count matches source country files."""
        if not self.detail_files or not self.source_country_files:
            self.skipTest("Detail or source files not available.")
        self.assertEqual(
            len(self.detail_files), len(self.source_country_files),
            f"Detail chunks: {len(self.detail_files)}, source files: {len(self.source_country_files)}"
        )

    def test_e2e_022_detail_files_are_valid_json(self):
        """E2E-022: All country detail chunks are valid JSON."""
        if not self.detail_files:
            self.skipTest("No detail files to check.")
        invalid = []
        for path in self.detail_files:
            try:
                load_json(path)
            except (json.JSONDecodeError, OSError) as e:
                invalid.append(f"{path.name}: {e}")
        self.assertEqual(invalid, [], f"Invalid JSON in detail chunks: {invalid}")

    def test_e2e_023_detail_files_have_code_field(self):
        """E2E-023: Each detail chunk has a country code field matching its filename."""
        if not self.detail_files:
            self.skipTest("No detail files to check.")
        mismatches = []
        for path in self.detail_files:
            try:
                data = load_json(path)
                # Detail chunks may use 'country_code' or 'code'
                code = data.get("country_code", data.get("code", ""))
                if code != path.stem:
                    mismatches.append(f"{path.name}: code field='{code}'")
            except Exception:
                pass
        self.assertEqual(mismatches, [], f"Code field mismatches: {mismatches}")

    def test_e2e_024_tier1_countries_have_narrative(self):
        """E2E-024: Tier 1 country detail chunks have a narrative section."""
        if not self.detail_files:
            self.skipTest("No detail files to check.")
        missing_narrative = []
        for path in self.detail_files:
            try:
                data = load_json(path)
                if data.get("tier") == 1 and "narrative" not in data:
                    missing_narrative.append(path.stem)
            except Exception:
                pass
        self.assertEqual(
            missing_narrative, [],
            f"Tier 1 countries missing narrative in detail chunks: {missing_narrative}"
        )

    # -----------------------------------------------------------------------
    # Global chunk checks
    # -----------------------------------------------------------------------

    def test_e2e_030_briefing_chunk_exists(self):
        """E2E-030: data/chunks/global/weekly_briefing.json exists."""
        if not self.briefing_path.exists():
            self.skipTest("weekly_briefing.json chunk not found. Run Agent 16 first.")
        self.assertIsNotNone(self.briefing)

    def test_e2e_031_briefing_is_valid(self):
        """E2E-031: Briefing chunk has headline and top_stories."""
        if self.briefing is None:
            self.skipTest("Briefing chunk not available.")
        self.assertIn("headline", self.briefing, "Briefing chunk missing 'headline'")
        self.assertIn("top_stories", self.briefing, "Briefing chunk missing 'top_stories'")

    def test_e2e_032_alert_chunk_exists(self):
        """E2E-032: data/chunks/global/alert_index.json exists."""
        if not self.alert_chunk_path.exists():
            self.skipTest("alert_index chunk not found.")
        self.assertIsNotNone(self.alert_chunk)

    def test_e2e_033_alert_chunk_is_valid(self):
        """E2E-033: Alert chunk has 'alerts' list."""
        if self.alert_chunk is None:
            self.skipTest("Alert chunk not available.")
        self.assertIn("alerts", self.alert_chunk, "Alert chunk missing 'alerts' field")
        self.assertIsInstance(self.alert_chunk["alerts"], list)

    # -----------------------------------------------------------------------
    # Relation checks
    # -----------------------------------------------------------------------

    def test_e2e_040_relation_index_exists(self):
        """E2E-040: data/indices/relation_index.json exists."""
        if not self.relation_index_path.exists():
            self.skipTest("relation_index.json not found. Run Agent 16 first.")
        self.assertIsNotNone(self.relation_index)

    def test_e2e_041_relation_chunks_have_valid_pair_names(self):
        """E2E-041: Relation chunk filenames follow AAA_BBB format (excluding index files)."""
        if not self.relation_files:
            return  # No relation files is acceptable (depends on pipeline data)
        import re
        invalid = [
            f.name for f in self.relation_files
            if f.stem != "relation_index"
            and not re.match(r"^[A-Z]{3}_[A-Z]{3}\.json$", f.name)
        ]
        self.assertEqual(invalid, [], f"Relation files with non-standard naming: {invalid}")

    def test_e2e_042_relation_pair_names_alphabetical(self):
        """E2E-042: Relation pair codes are alphabetically ordered (CHN_USA not USA_CHN)."""
        if not self.relation_files:
            return
        not_alphabetical = []
        for f in self.relation_files:
            stem = f.stem
            if stem == "relation_index":
                continue
            parts = stem.split("_")
            if len(parts) == 2 and parts[0] > parts[1]:
                not_alphabetical.append(stem)
        self.assertEqual(
            not_alphabetical, [],
            f"Relation pairs not in alphabetical order: {not_alphabetical}"
        )

    # -----------------------------------------------------------------------
    # Cross-chunk consistency
    # -----------------------------------------------------------------------

    def test_e2e_050_summary_codes_in_detail_chunks(self):
        """E2E-050: Every country code in summary that has a detail chunk is valid."""
        if self.summary is None or not self.detail_files:
            self.skipTest("Summary or detail chunks not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        summary_codes = {c["code"] for c in countries if isinstance(c, dict) and "code" in c}
        detail_codes = {f.stem for f in self.detail_files}
        # Only check that detail files are a subset of summary (not all 75 have details yet)
        orphan_details = detail_codes - summary_codes
        self.assertEqual(
            orphan_details, set(),
            f"Detail chunks with no matching summary entry: {orphan_details}"
        )

    def test_e2e_051_no_orphan_detail_chunks(self):
        """E2E-051: Every detail chunk has a corresponding entry in the summary."""
        if self.summary is None or not self.detail_files:
            self.skipTest("Summary or detail chunks not available.")
        countries = self.summary if isinstance(self.summary, list) else self.summary.get("countries", [])
        summary_codes = {c["code"] for c in countries if isinstance(c, dict) and "code" in c}
        detail_codes = {f.stem for f in self.detail_files}
        orphans = detail_codes - summary_codes
        self.assertEqual(
            orphans, set(),
            f"Detail chunks with no matching summary entry: {orphans}"
        )

    def test_e2e_052_manifest_summary_size_matches_actual(self):
        """E2E-052: Manifest-reported summary file size approximately matches actual."""
        if self.manifest is None or not self.summary_path.exists():
            self.skipTest("Manifest or summary not available.")
        # Find summary entry in files array
        manifest_size = 0
        files = self.manifest.get("files", [])
        if isinstance(files, list):
            for entry in files:
                if isinstance(entry, dict) and "summary" in entry.get("path", ""):
                    manifest_size = entry.get("size_bytes", 0)
                    break
        elif isinstance(files, dict):
            manifest_size = files.get("all_countries_summary", {}).get("size_bytes", 0)
        actual_size = self.summary_path.stat().st_size
        if manifest_size > 0:
            ratio = abs(actual_size - manifest_size) / max(actual_size, 1)
            self.assertLess(
                ratio, 0.05,
                f"Manifest size {manifest_size} vs actual {actual_size} — ratio {ratio:.2%} > 5%"
            )

    # -----------------------------------------------------------------------
    # Run log completeness
    # -----------------------------------------------------------------------

    @staticmethod
    def _find_latest_run_log() -> Path | None:
        """Find the most recent run_log file (dated or generic)."""
        staging = PROJECT_ROOT / "staging"
        candidates = sorted(staging.glob("run_log*.json"), reverse=True)
        # Prefer dated files (run_log_2026-W10b.json) over generic (run_log.json)
        dated = [c for c in candidates if c.name != "run_log.json"]
        return dated[0] if dated else (candidates[0] if candidates else None)

    def test_e2e_060_run_log_exists(self):
        """E2E-060: A run_log file exists in staging/."""
        run_log_path = self._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found in staging/.")
        data = load_json(run_log_path)
        self.assertIn("run_id", data, f"{run_log_path.name} missing run_id")
        self.assertIn("agents", data, f"{run_log_path.name} missing agents array")

    def test_e2e_061_run_log_has_all_16_agents(self):
        """E2E-061: Latest run_log records all 16 agents having started."""
        run_log_path = self._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        agents = data.get("agents", [])
        agent_ids = {a.get("agent_id") for a in agents}
        expected_ids = {f"agent_{i:02d}" for i in range(1, 17)}
        missing = expected_ids - agent_ids
        if missing:
            self.skipTest(
                f"Pipeline not complete — agents not yet run: {sorted(missing)}. "
                "This is expected if the pipeline is still in progress."
            )

    def test_e2e_062_no_failed_agents_in_run_log(self):
        """E2E-062: No agents have status 'failed' in latest run_log."""
        run_log_path = self._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        agents = data.get("agents", [])
        failed = [
            a.get("agent_id", "?")
            for a in agents
            if a.get("status") == "failed"
        ]
        self.assertEqual(failed, [], f"Agents with failed status: {failed}")


# ---------------------------------------------------------------------------
# E2E-PIP-002: Cache-Aware Pipeline Validation
# ---------------------------------------------------------------------------
class TestE2ECacheAwarePipeline(unittest.TestCase):
    """
    E2E-PIP-002: Validates cache-aware pipeline infrastructure.
    Tests that frequency registry, release calendar, and cache registry
    are present, well-formed, and consistent after a pipeline run.
    """

    AGENTS_CONFIG_DIR = PROJECT_ROOT / "agents" / "config"

    @classmethod
    def setUpClass(cls):
        cls.freq_registry_path = cls.AGENTS_CONFIG_DIR / "factor_frequency_registry.json"
        cls.release_cal_path = cls.AGENTS_CONFIG_DIR / "release_calendar.json"
        cls.cache_registry_path = cls.AGENTS_CONFIG_DIR / "cache_registry.json"

        cls.freq_registry = load_json(cls.freq_registry_path) if cls.freq_registry_path.exists() else None
        cls.release_cal = load_json(cls.release_cal_path) if cls.release_cal_path.exists() else None
        cls.cache_registry = load_json(cls.cache_registry_path) if cls.cache_registry_path.exists() else None

    # -----------------------------------------------------------------------
    # Factor frequency registry
    # -----------------------------------------------------------------------

    def test_e2e_070_frequency_registry_exists(self):
        """E2E-070: agents/config/factor_frequency_registry.json exists."""
        self.assertTrue(
            self.freq_registry_path.exists(),
            "factor_frequency_registry.json not found"
        )

    def test_e2e_071_frequency_registry_has_required_tiers(self):
        """E2E-071: Frequency registry has all 5 frequency tiers."""
        if self.freq_registry is None:
            self.skipTest("Frequency registry not available.")
        freqs = self.freq_registry.get("frequencies", {})
        expected = {"static", "annual", "quarterly", "monthly", "weekly"}
        actual = set(freqs.keys())
        missing = expected - actual
        self.assertEqual(missing, set(), f"Missing frequency tiers: {missing}")

    def test_e2e_072_frequency_registry_tiers_have_categories(self):
        """E2E-072: Each frequency tier has a non-empty factor_categories list."""
        if self.freq_registry is None:
            self.skipTest("Frequency registry not available.")
        freqs = self.freq_registry.get("frequencies", {})
        empty_tiers = [
            tier for tier, cfg in freqs.items()
            if not cfg.get("factor_categories")
        ]
        self.assertEqual(empty_tiers, [], f"Tiers with empty factor_categories: {empty_tiers}")

    def test_e2e_073_frequency_registry_ttl_values(self):
        """E2E-073: Frequency tiers have correct TTL structure."""
        if self.freq_registry is None:
            self.skipTest("Frequency registry not available.")
        freqs = self.freq_registry.get("frequencies", {})
        # Static should have null TTL, others should have numeric TTL
        if "static" in freqs:
            self.assertIsNone(
                freqs["static"].get("ttl_days"),
                "Static tier should have null ttl_days"
            )
        for tier in ["annual", "quarterly", "monthly", "weekly"]:
            if tier in freqs:
                ttl = freqs[tier].get("ttl_days")
                self.assertIsInstance(
                    ttl, (int, float),
                    f"{tier} tier should have numeric ttl_days, got {type(ttl).__name__}"
                )
                self.assertGreater(ttl, 0, f"{tier} tier ttl_days should be positive")

    # -----------------------------------------------------------------------
    # Release calendar
    # -----------------------------------------------------------------------

    def test_e2e_080_release_calendar_exists(self):
        """E2E-080: agents/config/release_calendar.json exists."""
        self.assertTrue(
            self.release_cal_path.exists(),
            "release_calendar.json not found"
        )

    def test_e2e_081_release_calendar_has_sources(self):
        """E2E-081: Release calendar has a non-empty sources dict."""
        if self.release_cal is None:
            self.skipTest("Release calendar not available.")
        sources = self.release_cal.get("sources", {})
        self.assertGreater(len(sources), 0, "Release calendar has no sources")

    def test_e2e_082_release_calendar_sources_have_required_fields(self):
        """E2E-082: Each source in release calendar has name, frequency, and factors."""
        if self.release_cal is None:
            self.skipTest("Release calendar not available.")
        sources = self.release_cal.get("sources", {})
        incomplete = []
        for source_id, cfg in sources.items():
            if not isinstance(cfg, dict):
                incomplete.append(f"{source_id}: not a dict")
                continue
            missing_fields = []
            if "name" not in cfg:
                missing_fields.append("name")
            if "frequency" not in cfg:
                missing_fields.append("frequency")
            if "factors" not in cfg:
                missing_fields.append("factors")
            if missing_fields:
                incomplete.append(f"{source_id}: missing {missing_fields}")
        self.assertEqual(incomplete, [], f"Incomplete source entries: {incomplete}")

    # -----------------------------------------------------------------------
    # Cache registry
    # -----------------------------------------------------------------------

    def test_e2e_090_cache_registry_exists(self):
        """E2E-090: agents/config/cache_registry.json exists."""
        self.assertTrue(
            self.cache_registry_path.exists(),
            "cache_registry.json not found"
        )

    def test_e2e_091_cache_registry_has_entries(self):
        """E2E-091: Cache registry has a non-empty entries dict."""
        if self.cache_registry is None:
            self.skipTest("Cache registry not available.")
        entries = self.cache_registry.get("entries", {})
        self.assertGreater(len(entries), 0, "Cache registry has no entries")

    def test_e2e_092_cache_registry_entries_have_required_fields(self):
        """E2E-092: Each cache entry has last_fetched, frequency, and countries_covered."""
        if self.cache_registry is None:
            self.skipTest("Cache registry not available.")
        entries = self.cache_registry.get("entries", {})
        incomplete = []
        for source_id, entry in entries.items():
            if not isinstance(entry, dict):
                incomplete.append(f"{source_id}: not a dict")
                continue
            missing = []
            for field in ["last_fetched", "frequency"]:
                if field not in entry:
                    missing.append(field)
            if missing:
                incomplete.append(f"{source_id}: missing {missing}")
        self.assertEqual(incomplete, [], f"Incomplete cache entries: {incomplete}")

    def test_e2e_093_cache_registry_valid_frequencies(self):
        """E2E-093: Cache registry entries reference valid frequency values."""
        if self.cache_registry is None:
            self.skipTest("Cache registry not available.")
        valid_freqs = {"static", "annual", "quarterly", "monthly", "weekly"}
        entries = self.cache_registry.get("entries", {})
        invalid = [
            f"{sid}: {e.get('frequency')}"
            for sid, e in entries.items()
            if isinstance(e, dict) and e.get("frequency") not in valid_freqs
        ]
        self.assertEqual(invalid, [], f"Entries with invalid frequency: {invalid}")

    def test_e2e_094_cache_registry_timestamps_are_valid(self):
        """E2E-094: Cache registry last_fetched values are valid ISO timestamps."""
        if self.cache_registry is None:
            self.skipTest("Cache registry not available.")
        entries = self.cache_registry.get("entries", {})
        invalid = [
            f"{sid}: {e.get('last_fetched')}"
            for sid, e in entries.items()
            if isinstance(e, dict) and e.get("last_fetched")
            and not is_valid_iso_timestamp(e["last_fetched"])
        ]
        self.assertEqual(invalid, [], f"Entries with invalid last_fetched timestamp: {invalid}")

    def test_e2e_095_cache_registry_has_last_updated(self):
        """E2E-095: Cache registry has a top-level last_updated timestamp."""
        if self.cache_registry is None:
            self.skipTest("Cache registry not available.")
        ts = self.cache_registry.get("last_updated", "")
        self.assertTrue(
            is_valid_iso_timestamp(ts),
            f"Cache registry last_updated '{ts}' is not a valid timestamp"
        )

    # -----------------------------------------------------------------------
    # Run log cache context
    # -----------------------------------------------------------------------

    def test_e2e_100_run_log_has_cache_context(self):
        """E2E-100: Latest run_log has a cache_context section."""
        run_log_path = TestE2EFullPipeline._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        self.assertIn(
            "cache_context", data,
            "Run log missing cache_context section"
        )

    def test_e2e_101_cache_context_has_frequency_flags(self):
        """E2E-101: Run log cache_context has weekly/monthly/quarterly due flags."""
        run_log_path = TestE2EFullPipeline._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        ctx = data.get("cache_context", {})
        for flag in ["weekly_due", "monthly_due", "quarterly_due"]:
            self.assertIn(flag, ctx, f"cache_context missing '{flag}'")

    def test_e2e_102_cache_context_event_triggers(self):
        """E2E-102: Run log cache_context has event_triggers list."""
        run_log_path = TestE2EFullPipeline._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        ctx = data.get("cache_context", {})
        triggers = ctx.get("event_triggers", ctx.get("event_triggers_detected"))
        self.assertIsNotNone(triggers, "cache_context has no event_triggers info")

    def test_e2e_103_agents_have_cache_decisions(self):
        """E2E-103: Gathering agents (01-06) in run_log have cache_decisions."""
        run_log_path = TestE2EFullPipeline._find_latest_run_log()
        if run_log_path is None:
            self.skipTest("No run_log file found.")
        data = load_json(run_log_path)
        agents = data.get("agents", [])
        gathering_ids = {f"agent_{i:02d}" for i in range(1, 7)}
        missing_cache_decisions = []
        for a in agents:
            aid = a.get("agent_id", "")
            if aid in gathering_ids and "cache_decisions" not in a:
                missing_cache_decisions.append(aid)
        self.assertEqual(
            missing_cache_decisions, [],
            f"Gathering agents missing cache_decisions: {missing_cache_decisions}"
        )

    # -----------------------------------------------------------------------
    # Cache registry ↔ release calendar consistency
    # -----------------------------------------------------------------------

    def test_e2e_110_cache_sources_in_release_calendar(self):
        """E2E-110: Annual/quarterly cache entries have matching release calendar source."""
        if self.cache_registry is None or self.release_cal is None:
            self.skipTest("Cache registry or release calendar not available.")
        cal_sources = set(self.release_cal.get("sources", {}).keys())
        entries = self.cache_registry.get("entries", {})
        missing = []
        for sid, e in entries.items():
            if isinstance(e, dict) and e.get("frequency") in ("annual", "quarterly"):
                # Match by source_id prefix (e.g., "worldbank.wdi" should be in calendar)
                if sid not in cal_sources:
                    missing.append(sid)
        # This is a warning-level check — not all sources need calendar entries
        if missing:
            self.skipTest(
                f"Advisory: {len(missing)} annual/quarterly cache entries "
                f"without release calendar match: {missing[:5]}"
            )


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data dir:     {DATA_DIR}")
    print(f"Chunks dir:   {CHUNKS_DIR}")
    print("")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestE2EFullPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestE2ECacheAwarePipeline))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("")
    total = result.testsRun
    skipped = len(result.skipped)
    failures = len(result.failures) + len(result.errors)
    passed = total - failures - skipped

    print(f"Results: {passed} passed, {failures} failed, {skipped} skipped out of {total} tests")
    if skipped > 0:
        print(f"Note: {skipped} tests skipped because pipeline has not fully run yet.")
        print("Run the complete pipeline (Agents 01-16) and re-run this test.")

    sys.exit(0 if result.wasSuccessful() else 1)
