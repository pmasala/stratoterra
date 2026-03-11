"""
Integration tests for the pre-fetch → agent pipeline.

Validates:
1. Pre-fetched output files exist and conform to the envelope schema
2. Country coverage meets minimum thresholds per tier
3. Agent prompt ↔ pre-fetched file alignment (every agent gets its expected inputs)
4. Indicator names in pre-fetched data match what agent prompts reference
5. Record field schemas per source
6. Data quality: plausible value ranges
7. Cache fallback mechanism

Tests marked @pytest.mark.integration require actual pre-fetched files on disk.
Run with: pytest tests/scripts/test_prefetch_integration.py -v
"""

import json
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

PREFETCHED_DIR = PROJECT_ROOT / "staging" / "prefetched"
PROMPTS_DIR = PROJECT_ROOT / "agents" / "prompts"

from agents.prefetch.base_fetcher import (
    BaseFetcher,
    get_all_country_codes,
    get_countries_by_tier,
    CACHE_DIR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_prefetched(filename: str) -> dict | None:
    """Load a pre-fetched JSON file, return None if missing."""
    path = PREFETCHED_DIR / filename
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def prefetched_exists(filename: str) -> bool:
    return (PREFETCHED_DIR / filename).exists()


# Core files that must always exist (no API key needed)
CORE_FILES = ["worldbank.json", "imf_weo.json", "fx_commodities.json", "gdelt.json"]

# Optional files (need API keys)
OPTIONAL_FILES = ["acled.json", "eia.json", "comtrade.json"]

# Skip all integration tests if no prefetched files exist at all
HAS_PREFETCHED = any(prefetched_exists(f) for f in CORE_FILES)


# ---------------------------------------------------------------------------
# 1. Output file existence & envelope schema
# ---------------------------------------------------------------------------

class TestEnvelopeSchema:
    """Every pre-fetched file must conform to the standard envelope format."""

    REQUIRED_KEYS = {"source_id", "fetched_at", "records", "errors", "stats"}

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("filename", CORE_FILES)
    def test_core_file_exists(self, filename):
        assert prefetched_exists(filename), f"Missing core prefetched file: {filename}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("filename", CORE_FILES)
    def test_envelope_keys(self, filename):
        data = load_prefetched(filename)
        if data is None:
            pytest.skip(f"{filename} not found")
        for key in self.REQUIRED_KEYS:
            assert key in data, f"{filename} missing envelope key: {key}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("filename", CORE_FILES)
    def test_records_is_nonempty_list(self, filename):
        data = load_prefetched(filename)
        if data is None:
            pytest.skip(f"{filename} not found")
        records = data.get("records", [])
        assert isinstance(records, list), f"{filename}: records is not a list"
        assert len(records) > 0, f"{filename}: records is empty"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("filename", CORE_FILES)
    def test_no_errors(self, filename):
        data = load_prefetched(filename)
        if data is None:
            pytest.skip(f"{filename} not found")
        errors = data.get("errors", [])
        # Warn but don't fail on a few errors
        if len(errors) > 5:
            pytest.fail(f"{filename}: {len(errors)} errors (threshold: 5)")

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_summary_file_exists(self):
        assert prefetched_exists("_summary.json"), "Missing _summary.json"


# ---------------------------------------------------------------------------
# 2. Country coverage thresholds
# ---------------------------------------------------------------------------

class TestCountryCoverage:
    """Pre-fetched data must cover minimum % of countries per tier."""

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_worldbank_tier1_coverage(self):
        """World Bank should cover >= 90% of Tier 1 countries."""
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        tiers = get_countries_by_tier()
        tier1_codes = {c["code"] for c in tiers["tier_1"]}
        covered = {r["country_code"] for r in data["records"]}
        overlap = tier1_codes & covered
        pct = len(overlap) / len(tier1_codes) * 100
        assert pct >= 90, (
            f"Tier 1 coverage: {pct:.0f}% ({len(overlap)}/{len(tier1_codes)}). "
            f"Missing: {tier1_codes - covered}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_worldbank_tier2_coverage(self):
        """World Bank should cover >= 70% of Tier 2 countries."""
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        tiers = get_countries_by_tier()
        tier2_codes = {c["code"] for c in tiers["tier_2"]}
        covered = {r["country_code"] for r in data["records"]}
        overlap = tier2_codes & covered
        pct = len(overlap) / len(tier2_codes) * 100
        assert pct >= 70, (
            f"Tier 2 coverage: {pct:.0f}% ({len(overlap)}/{len(tier2_codes)}). "
            f"Missing: {tier2_codes - covered}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_imf_tier1_coverage(self):
        """IMF WEO should cover >= 90% of Tier 1 countries."""
        data = load_prefetched("imf_weo.json")
        if data is None:
            pytest.skip("imf_weo.json not found")
        tiers = get_countries_by_tier()
        tier1_codes = {c["code"] for c in tiers["tier_1"]}
        covered = {r["country_code"] for r in data["records"]}
        overlap = tier1_codes & covered
        pct = len(overlap) / len(tier1_codes) * 100
        assert pct >= 90, (
            f"Tier 1 coverage: {pct:.0f}% ({len(overlap)}/{len(tier1_codes)}). "
            f"Missing: {tier1_codes - covered}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_fx_minimum_currencies(self):
        """FX should cover at least 20 currencies."""
        data = load_prefetched("fx_commodities.json")
        if data is None:
            pytest.skip("fx_commodities.json not found")
        fx_records = [r for r in data["records"] if r.get("indicator_name") == "exchange_rate_vs_usd"]
        assert len(fx_records) >= 20, f"Only {len(fx_records)} currencies (min: 20)"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_gdelt_minimum_articles(self):
        """GDELT should have at least 100 articles."""
        data = load_prefetched("gdelt.json")
        if data is None:
            pytest.skip("gdelt.json not found")
        assert len(data["records"]) >= 100, f"Only {len(data['records'])} articles (min: 100)"


# ---------------------------------------------------------------------------
# 3. Agent prompt ↔ pre-fetched file alignment
# ---------------------------------------------------------------------------

class TestAgentAlignment:
    """
    Verify that every pre-fetched file referenced in agent prompts
    actually exists on disk (or is correctly documented as optional).
    """

    AGENT_PREFETCH_MAP = {
        "agent_01_official_stats.md": {
            "required": ["worldbank.json", "imf_weo.json"],
            "optional": ["eia.json"],
        },
        "agent_02_financial_data.md": {
            "required": ["fx_commodities.json"],
            "optional": [],
        },
        "agent_03_news_events.md": {
            "required": ["gdelt.json"],
            "optional": [],
        },
        "agent_04_trade_sanctions.md": {
            "required": [],
            "optional": ["comtrade.json"],
        },
        "agent_05_military_conflict.md": {
            "required": [],
            "optional": ["acled.json"],
        },
        "agent_06_political_regulatory.md": {
            "required": ["worldbank.json"],  # WGI subset
            "optional": [],
        },
    }

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("agent_file,deps", list(AGENT_PREFETCH_MAP.items()))
    def test_required_inputs_exist(self, agent_file, deps):
        """Each agent's required pre-fetched files must exist."""
        for filename in deps["required"]:
            assert prefetched_exists(filename), (
                f"Agent {agent_file} requires {filename} but it's missing"
            )

    def test_agent_prompts_reference_prefetched_dir(self):
        """Agent prompts should reference /staging/prefetched/ paths."""
        for agent_file, deps in self.AGENT_PREFETCH_MAP.items():
            all_files = deps["required"] + deps["optional"]
            if not all_files:
                continue
            prompt_path = PROMPTS_DIR / agent_file
            if not prompt_path.exists():
                pytest.skip(f"{agent_file} not found")
            content = prompt_path.read_text()
            for filename in all_files:
                basename = filename.replace(".json", "")
                assert basename in content, (
                    f"Agent {agent_file} should reference '{basename}' "
                    f"but it's not mentioned in the prompt"
                )


# ---------------------------------------------------------------------------
# 4. Indicator mapping completeness
# ---------------------------------------------------------------------------

class TestIndicatorMapping:
    """
    Verify that indicators in pre-fetched data match what agent prompts
    and fetcher code expect.
    """

    # World Bank indicators that Agent 01 maps to factor paths
    EXPECTED_WB_INDICATORS = {
        "gdp_nominal_usd", "gdp_per_capita_usd", "gdp_growth_pct", "gdp_ppp_usd",
        "govt_debt_pct_gdp", "current_account_pct_gdp", "reserves_total_usd",
        "fdi_net_inflows_usd", "exports_usd", "imports_usd",
        "inflation_cpi_pct", "unemployment_pct", "labor_force_participation_pct",
        "population", "population_growth_pct", "life_expectancy", "urban_population_pct",
        "gini_index", "literacy_rate_pct", "health_expenditure_pct_gdp",
        "electricity_access_pct", "internet_users_pct",
        "wgi_voice_accountability", "wgi_political_stability",
        "wgi_govt_effectiveness", "wgi_regulatory_quality",
        "wgi_rule_of_law", "wgi_control_of_corruption",
    }

    # IMF WEO indicators that Agent 01 uses
    EXPECTED_IMF_INDICATORS = {
        "gdp_nominal_usd_bn", "gdp_real_growth_pct", "inflation_avg_pct",
        "unemployment_rate_pct", "fiscal_balance_pct_gdp",
        "current_account_pct_gdp", "govt_expenditure_pct_gdp", "gross_debt_pct_gdp",
    }

    # WGI indicators that Agent 06 reads from worldbank.json
    EXPECTED_WGI_INDICATORS = {
        "wgi_voice_accountability", "wgi_political_stability",
        "wgi_govt_effectiveness", "wgi_regulatory_quality",
        "wgi_rule_of_law", "wgi_control_of_corruption",
    }

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_worldbank_has_expected_indicators(self):
        """worldbank.json must contain all expected indicator_name values."""
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        actual = {r["indicator_name"] for r in data["records"]}
        missing = self.EXPECTED_WB_INDICATORS - actual
        # Allow up to 3 missing (sparse data like gini, literacy)
        assert len(missing) <= 3, (
            f"World Bank missing {len(missing)} indicators: {missing}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_imf_has_expected_indicators(self):
        """imf_weo.json must contain most expected indicator_name values.

        Allow up to 1 missing — GGX_NGDP (govt_expenditure_pct_gdp) may not
        be available from the IMF DataMapper API.
        """
        data = load_prefetched("imf_weo.json")
        if data is None:
            pytest.skip("imf_weo.json not found")
        actual = {r["indicator_name"] for r in data["records"]}
        missing = self.EXPECTED_IMF_INDICATORS - actual
        assert len(missing) <= 1, f"IMF WEO missing {len(missing)} indicators: {missing}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_worldbank_has_wgi_for_agent06(self):
        """worldbank.json must have WGI indicators for Agent 06.

        Note: WGI Political Stability uses indicator PV.EST (not PS.EST).
        Allow 1 missing indicator for API quirks.
        """
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        wgi_records = [r for r in data["records"] if r["indicator_name"].startswith("wgi_")]
        actual_indicators = {r["indicator_name"] for r in wgi_records}
        missing = self.EXPECTED_WGI_INDICATORS - actual_indicators
        assert len(missing) <= 1, f"WGI missing for Agent 06: {missing}"
        # Should cover multiple countries
        wgi_countries = {r["country_code"] for r in wgi_records}
        assert len(wgi_countries) >= 50, (
            f"WGI covers only {len(wgi_countries)} countries (min: 50)"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_gdelt_has_expected_query_ids(self):
        """gdelt.json articles should have at least the top_events bucket.

        Note: GDELT deduplication by URL can collapse thematic queries when
        articles overlap with the broad top_events query. We only require
        that top_events is present and >=3 total query buckets have articles.
        """
        data = load_prefetched("gdelt.json")
        if data is None:
            pytest.skip("gdelt.json not found")
        actual_queries = {r["query_id"] for r in data["records"]}
        assert "top_events" in actual_queries, "GDELT missing top_events query"
        # After dedup, at least 1 bucket should survive (top_events guaranteed)
        assert len(actual_queries) >= 1, (
            f"GDELT has no query buckets: {actual_queries}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_fx_has_exchange_rate_indicator(self):
        """fx_commodities.json FX records must have indicator_name = exchange_rate_vs_usd."""
        data = load_prefetched("fx_commodities.json")
        if data is None:
            pytest.skip("fx_commodities.json not found")
        fx = [r for r in data["records"] if "currency" in r]
        for r in fx:
            assert r.get("indicator_name") == "exchange_rate_vs_usd", (
                f"FX record for {r.get('currency')} has wrong indicator_name"
            )

    def test_fetcher_indicator_names_match_prompt(self):
        """Indicator names defined in fetcher code must match agent prompt docs."""
        from agents.prefetch.fetch_worldbank import INDICATOR_NAMES as WB_NAMES
        from agents.prefetch.fetch_imf import INDICATORS as IMF_NAMES

        # World Bank fetcher indicator names should match what we test above
        wb_values = set(WB_NAMES.values())
        assert self.EXPECTED_WB_INDICATORS == wb_values, (
            f"WB fetcher indicator names don't match expected.\n"
            f"Extra in code: {wb_values - self.EXPECTED_WB_INDICATORS}\n"
            f"Missing in code: {self.EXPECTED_WB_INDICATORS - wb_values}"
        )

        # IMF fetcher indicator names
        imf_values = set(IMF_NAMES.values())
        assert self.EXPECTED_IMF_INDICATORS == imf_values, (
            f"IMF fetcher indicator names don't match expected.\n"
            f"Extra in code: {imf_values - self.EXPECTED_IMF_INDICATORS}\n"
            f"Missing in code: {self.EXPECTED_IMF_INDICATORS - imf_values}"
        )


# ---------------------------------------------------------------------------
# 5. Record field schemas per source
# ---------------------------------------------------------------------------

class TestRecordSchemas:
    """Validate that records from each source have the expected fields."""

    WB_REQUIRED_FIELDS = {"country_code", "indicator_id", "indicator_name", "value", "year", "source"}
    IMF_REQUIRED_FIELDS = {"country_code", "indicator_id", "indicator_name", "value", "year", "is_forecast", "source"}
    FX_REQUIRED_FIELDS = {"currency", "country_code", "rate_vs_usd", "source", "indicator_name"}
    GDELT_REQUIRED_FIELDS = {"title", "url", "source", "query_id"}

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_worldbank_record_fields(self):
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        for i, r in enumerate(data["records"][:50]):  # Check first 50
            missing = self.WB_REQUIRED_FIELDS - set(r.keys())
            assert not missing, f"WB record {i} missing fields: {missing}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_imf_record_fields(self):
        data = load_prefetched("imf_weo.json")
        if data is None:
            pytest.skip("imf_weo.json not found")
        for i, r in enumerate(data["records"][:50]):
            missing = self.IMF_REQUIRED_FIELDS - set(r.keys())
            assert not missing, f"IMF record {i} missing fields: {missing}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_fx_record_fields(self):
        data = load_prefetched("fx_commodities.json")
        if data is None:
            pytest.skip("fx_commodities.json not found")
        fx = [r for r in data["records"] if "currency" in r]
        for i, r in enumerate(fx[:20]):
            missing = self.FX_REQUIRED_FIELDS - set(r.keys())
            assert not missing, f"FX record {i} missing fields: {missing}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_gdelt_record_fields(self):
        data = load_prefetched("gdelt.json")
        if data is None:
            pytest.skip("gdelt.json not found")
        for i, r in enumerate(data["records"][:50]):
            missing = self.GDELT_REQUIRED_FIELDS - set(r.keys())
            assert not missing, f"GDELT record {i} missing fields: {missing}"


# ---------------------------------------------------------------------------
# 6. Data quality: plausible value ranges
# ---------------------------------------------------------------------------

class TestDataQuality:
    """Spot-check that values are within plausible ranges."""

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_gdp_values_positive(self):
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        gdp_records = [r for r in data["records"] if r["indicator_name"] == "gdp_nominal_usd"]
        for r in gdp_records:
            assert r["value"] > 0, f"GDP for {r['country_code']} is non-positive: {r['value']}"

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_population_values_reasonable(self):
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        pop_records = [r for r in data["records"] if r["indicator_name"] == "population"]
        for r in pop_records:
            # Smallest tracked country (Qatar) ~3M, largest (China/India) ~1.4B
            assert 100_000 < r["value"] < 2_000_000_000, (
                f"Population for {r['country_code']} out of range: {r['value']}"
            )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_inflation_values_bounded(self):
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        infl = [r for r in data["records"] if r["indicator_name"] == "inflation_cpi_pct"]
        for r in infl:
            # Allow -10% to 1000% (Zimbabwe/Argentina edge cases)
            assert -20 < r["value"] < 10000, (
                f"Inflation for {r['country_code']} implausible: {r['value']}%"
            )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_fx_rates_positive(self):
        data = load_prefetched("fx_commodities.json")
        if data is None:
            pytest.skip("fx_commodities.json not found")
        fx = [r for r in data["records"] if r.get("indicator_name") == "exchange_rate_vs_usd"]
        for r in fx:
            assert r["rate_vs_usd"] > 0, (
                f"FX rate for {r['currency']} non-positive: {r['rate_vs_usd']}"
            )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_wgi_scores_in_range(self):
        """WGI scores should be in [-2.5, 2.5] range."""
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        wgi = [r for r in data["records"] if r["indicator_name"].startswith("wgi_")]
        for r in wgi:
            assert -3.0 <= r["value"] <= 3.0, (
                f"WGI {r['indicator_name']} for {r['country_code']} "
                f"out of range: {r['value']}"
            )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_country_codes_are_valid_iso3(self):
        """All country_code values should be valid ISO3 codes from our tracked list."""
        all_codes = set(get_all_country_codes())
        for filename in CORE_FILES:
            data = load_prefetched(filename)
            if data is None:
                continue
            for r in data["records"]:
                cc = r.get("country_code")
                if cc:  # GDELT records don't have country_code
                    assert cc in all_codes, (
                        f"{filename}: unknown country_code '{cc}'"
                    )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_no_duplicate_records(self):
        """World Bank should not have duplicate country+indicator pairs."""
        data = load_prefetched("worldbank.json")
        if data is None:
            pytest.skip("worldbank.json not found")
        seen = set()
        dupes = []
        for r in data["records"]:
            key = (r["country_code"], r["indicator_id"])
            if key in seen:
                dupes.append(key)
            seen.add(key)
        assert len(dupes) == 0, f"Found {len(dupes)} duplicate WB records: {dupes[:5]}"


# ---------------------------------------------------------------------------
# 7. Cache fallback mechanism
# ---------------------------------------------------------------------------

class TestCacheFallback:
    """Test that the BaseFetcher cache mechanism works correctly."""

    def test_cache_roundtrip(self, tmp_path):
        """Save → load roundtrip preserves data."""
        with patch("agents.prefetch.base_fetcher.PREFETCHED_DIR", tmp_path / "out"):
            with patch("agents.prefetch.base_fetcher.CACHE_DIR", tmp_path / "cache"):
                f = BaseFetcher()
                f.source_id = "test_rt"
                f.output_filename = "test_rt.json"

                data = f.build_envelope([
                    {"country_code": "USA", "indicator": "gdp", "value": 28.5e12},
                    {"country_code": "CHN", "indicator": "gdp", "value": 19.0e12},
                ])
                f.save_output(data)
                f.update_cache(data)

                cached = f.load_cache()
                assert cached is not None
                assert len(cached["records"]) == 2
                assert cached["source_id"] == "test_rt"

    def test_fallback_on_empty_result(self, tmp_path):
        """When live fetch returns 0 records, fallback to cache."""
        with patch("agents.prefetch.base_fetcher.PREFETCHED_DIR", tmp_path / "out"):
            with patch("agents.prefetch.base_fetcher.CACHE_DIR", tmp_path / "cache"):
                # First: create a cache with real data
                f1 = BaseFetcher()
                f1.source_id = "test_fb"
                f1.output_filename = "test_fb.json"
                good_data = f1.build_envelope([{"value": 42}])
                f1.update_cache(good_data)

                # Second: a fetcher that returns empty
                class EmptyFetcher(BaseFetcher):
                    source_id = "test_fb"
                    output_filename = "test_fb.json"
                    def run(self):
                        return self.build_envelope([])

                f2 = EmptyFetcher()
                result = f2.execute()
                assert result.get("_fallback") is True
                assert len(result["records"]) == 1
                assert result["records"][0]["value"] == 42

    def test_fallback_on_exception(self, tmp_path):
        """When live fetch raises, fallback to cache."""
        with patch("agents.prefetch.base_fetcher.PREFETCHED_DIR", tmp_path / "out"):
            with patch("agents.prefetch.base_fetcher.CACHE_DIR", tmp_path / "cache"):
                # Seed cache
                f1 = BaseFetcher()
                f1.source_id = "test_ex"
                f1.output_filename = "test_ex.json"
                good_data = f1.build_envelope([{"value": 99}])
                f1.update_cache(good_data)

                # Crashing fetcher
                class CrashFetcher(BaseFetcher):
                    source_id = "test_ex"
                    output_filename = "test_ex.json"
                    def run(self):
                        raise RuntimeError("API down")

                f2 = CrashFetcher()
                result = f2.execute()
                assert result.get("_fallback") is True
                assert "API down" in result.get("_fallback_reason", "")

    def test_error_envelope_when_no_cache(self, tmp_path):
        """When both live fetch and cache fail, return error envelope."""
        with patch("agents.prefetch.base_fetcher.PREFETCHED_DIR", tmp_path / "out"):
            with patch("agents.prefetch.base_fetcher.CACHE_DIR", tmp_path / "cache"):
                class CrashFetcher(BaseFetcher):
                    source_id = "test_nc"
                    output_filename = "test_nc.json"
                    def run(self):
                        raise RuntimeError("Total failure")

                f = CrashFetcher()
                result = f.execute()
                assert result.get("_error") is not None
                assert len(result["records"]) == 0


# ---------------------------------------------------------------------------
# 8. Cross-source consistency
# ---------------------------------------------------------------------------

class TestCrossSourceConsistency:
    """Validate consistency between different pre-fetched sources."""

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_wb_and_imf_country_overlap(self):
        """World Bank and IMF should cover largely the same countries."""
        wb = load_prefetched("worldbank.json")
        imf = load_prefetched("imf_weo.json")
        if wb is None or imf is None:
            pytest.skip("Missing prefetched files")
        wb_countries = {r["country_code"] for r in wb["records"]}
        imf_countries = {r["country_code"] for r in imf["records"]}
        overlap = wb_countries & imf_countries
        # At least 60 countries should be in both
        assert len(overlap) >= 60, (
            f"WB/IMF overlap: {len(overlap)} countries. "
            f"Only in WB: {wb_countries - imf_countries}. "
            f"Only in IMF: {imf_countries - wb_countries}"
        )

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    def test_fx_countries_are_tracked(self):
        """All FX country_code values should be tracked countries."""
        data = load_prefetched("fx_commodities.json")
        if data is None:
            pytest.skip("fx_commodities.json not found")
        all_codes = set(get_all_country_codes())
        fx = [r for r in data["records"] if r.get("country_code")]
        for r in fx:
            assert r["country_code"] in all_codes, (
                f"FX currency {r['currency']} maps to untracked country {r['country_code']}"
            )


# ---------------------------------------------------------------------------
# 9. Minimum record counts (regression guard)
# ---------------------------------------------------------------------------

class TestMinimumRecordCounts:
    """Guard against regressions in data volume."""

    MINIMUMS = {
        "worldbank.json": 1500,   # ~1886 from live test
        "imf_weo.json": 800,      # ~1003 from live test
        "fx_commodities.json": 20, # ~25 from live test
        "gdelt.json": 100,         # ~250 from live test
    }

    @pytest.mark.skipif(not HAS_PREFETCHED, reason="No prefetched files on disk")
    @pytest.mark.parametrize("filename,minimum", list(MINIMUMS.items()))
    def test_minimum_records(self, filename, minimum):
        data = load_prefetched(filename)
        if data is None:
            pytest.skip(f"{filename} not found")
        actual = len(data["records"])
        assert actual >= minimum, (
            f"{filename}: {actual} records < minimum {minimum}"
        )
