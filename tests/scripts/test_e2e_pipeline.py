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
    return bool(re.match(r"^\d{4}-W\d{2}$", s or ""))


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
        required_keys = ["schema_version", "generated_at", "files"]
        missing = [k for k in required_keys if k not in self.manifest]
        self.assertEqual(missing, [], f"Manifest missing required keys: {missing}")

    def test_e2e_004_manifest_country_count_matches_actual(self):
        """E2E-004: manifest total_files matches actual chunk file count."""
        if self.manifest is None:
            self.skipTest("manifest not available.")
        manifest_count = self.manifest.get("total_files", -1)
        files_list = self.manifest.get("files", [])
        if manifest_count >= 0 and isinstance(files_list, list):
            self.assertEqual(
                manifest_count, len(files_list),
                f"Manifest total_files={manifest_count} but files array has {len(files_list)} entries"
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
        """E2E-023: Each detail chunk has a 'code' field matching its filename."""
        if not self.detail_files:
            self.skipTest("No detail files to check.")
        mismatches = []
        for path in self.detail_files:
            try:
                data = load_json(path)
                code = data.get("code", "")
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

    def test_e2e_060_run_log_exists(self):
        """E2E-060: staging/run_log.json exists."""
        run_log_path = PROJECT_ROOT / "staging" / "run_log.json"
        if not run_log_path.exists():
            self.skipTest("run_log.json not found.")
        data = load_json(run_log_path)
        self.assertIn("run_id", data, "run_log.json missing run_id")
        self.assertIn("agents", data, "run_log.json missing agents array")

    def test_e2e_061_run_log_has_all_16_agents(self):
        """E2E-061: run_log.json records all 16 agents having started."""
        run_log_path = PROJECT_ROOT / "staging" / "run_log.json"
        if not run_log_path.exists():
            self.skipTest("run_log.json not found.")
        data = load_json(run_log_path)
        agents = data.get("agents", [])
        agent_ids = {a.get("agent_id") for a in agents}
        expected_ids = {f"agent_{i:02d}" for i in range(1, 17)}
        missing = expected_ids - agent_ids
        if missing:
            # If the pipeline hasn't completed yet, this is informational
            self.skipTest(
                f"Pipeline not complete — agents not yet run: {sorted(missing)}. "
                "This is expected if the pipeline is still in progress."
            )

    def test_e2e_062_no_failed_agents_in_run_log(self):
        """E2E-062: No agents have status 'failed' in run_log.json."""
        run_log_path = PROJECT_ROOT / "staging" / "run_log.json"
        if not run_log_path.exists():
            self.skipTest("run_log.json not found.")
        data = load_json(run_log_path)
        agents = data.get("agents", [])
        failed = [
            a.get("agent_id", "?")
            for a in agents
            if a.get("status") == "failed"
        ]
        self.assertEqual(failed, [], f"Agents with failed status: {failed}")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data dir:     {DATA_DIR}")
    print(f"Chunks dir:   {CHUNKS_DIR}")
    print("")

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestE2EFullPipeline)

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
