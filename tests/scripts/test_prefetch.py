"""
Tests for the pre-fetch infrastructure and individual fetchers.

Tests are split into:
- Unit tests (no network, mock responses) — always run
- Integration tests (live API calls) — marked with @pytest.mark.integration
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.prefetch.base_fetcher import (
    BaseFetcher,
    ISO3_TO_ISO2,
    ISO2_TO_ISO3,
    get_all_country_codes,
    get_countries_by_tier,
    load_country_list,
    PREFETCHED_DIR,
    CACHE_DIR,
)


# ---------------------------------------------------------------------------
# Base infrastructure tests
# ---------------------------------------------------------------------------

class TestCountryHelpers:
    def test_load_country_list(self):
        data = load_country_list()
        assert data["total_countries"] == 75
        assert "tiers" in data

    def test_get_all_country_codes(self):
        codes = get_all_country_codes()
        assert len(codes) == 75
        assert "USA" in codes
        assert "CHN" in codes
        assert "LBY" in codes  # last tier 3

    def test_get_countries_by_tier(self):
        tiers = get_countries_by_tier()
        assert len(tiers["tier_1"]) == 30
        assert len(tiers["tier_2"]) == 25
        assert len(tiers["tier_3"]) == 20

    def test_iso3_to_iso2_coverage(self):
        """Every tracked country must have an ISO2 mapping."""
        codes = get_all_country_codes()
        for code in codes:
            assert code in ISO3_TO_ISO2, f"Missing ISO2 mapping for {code}"

    def test_iso2_to_iso3_roundtrip(self):
        """ISO2 -> ISO3 roundtrip must work for all entries."""
        for iso3, iso2 in ISO3_TO_ISO2.items():
            assert ISO2_TO_ISO3[iso2] == iso3


class TestBaseFetcher:
    def test_build_envelope(self):
        f = BaseFetcher()
        f.source_id = "test"
        env = f.build_envelope([{"a": 1}], skipped=[{"b": 2}])
        assert env["source_id"] == "test"
        assert len(env["records"]) == 1
        assert len(env["skipped"]) == 1
        assert "fetched_at" in env
        assert "stats" in env

    def test_session_has_retry(self):
        f = BaseFetcher()
        adapter = f.session.get_adapter("https://example.com")
        assert adapter.max_retries.total == 3

    def test_save_and_load_cache(self, tmp_path, monkeypatch):
        monkeypatch.setattr("agents.prefetch.base_fetcher.PREFETCHED_DIR", tmp_path / "out")
        monkeypatch.setattr("agents.prefetch.base_fetcher.CACHE_DIR", tmp_path / "cache")

        f = BaseFetcher()
        f.source_id = "test"
        f.output_filename = "test.json"

        data = {"source_id": "test", "records": [{"x": 1}]}
        f.save_output(data)
        f.update_cache(data)

        cached = f.load_cache()
        assert cached is not None
        assert cached["records"][0]["x"] == 1


# ---------------------------------------------------------------------------
# World Bank fetcher tests
# ---------------------------------------------------------------------------

class TestWorldBankFetcher:
    def _make_wb_response(self, entries):
        """Create a mock World Bank API response."""
        return [
            {"page": 1, "pages": 1, "per_page": 1000, "total": len(entries)},
            entries,
        ]

    @patch("agents.prefetch.fetch_worldbank.WorldBankFetcher.get_json")
    def test_parses_indicator_data(self, mock_get):
        from agents.prefetch.fetch_worldbank import WorldBankFetcher

        mock_get.return_value = self._make_wb_response([
            {
                "indicator": {"id": "NY.GDP.MKTP.CD"},
                "country": {"id": "US"},
                "countryiso3code": "USA",
                "value": 28500000000000,
                "date": "2025",
            },
            {
                "indicator": {"id": "NY.GDP.MKTP.CD"},
                "country": {"id": "CN"},
                "countryiso3code": "CHN",
                "value": 19000000000000,
                "date": "2025",
            },
        ])

        fetcher = WorldBankFetcher()
        records = fetcher._fetch_single_indicator(["US", "CN"], "NY.GDP.MKTP.CD")
        assert len(records) == 2
        assert records[0]["country_code"] == "USA"
        assert records[0]["indicator_name"] == "gdp_nominal_usd"

    @patch("agents.prefetch.fetch_worldbank.WorldBankFetcher.get_json")
    def test_skips_untracked_countries(self, mock_get):
        from agents.prefetch.fetch_worldbank import WorldBankFetcher

        mock_get.return_value = self._make_wb_response([
            {
                "indicator": {"id": "NY.GDP.MKTP.CD"},
                "country": {"id": "ZZ"},
                "countryiso3code": "ZZZ",
                "value": 100,
                "date": "2025",
            },
        ])

        fetcher = WorldBankFetcher()
        records = fetcher._fetch_single_indicator(["ZZ"], "NY.GDP.MKTP.CD")
        assert len(records) == 0

    @patch("agents.prefetch.fetch_worldbank.WorldBankFetcher.get_json")
    def test_skips_null_values(self, mock_get):
        from agents.prefetch.fetch_worldbank import WorldBankFetcher

        mock_get.return_value = self._make_wb_response([
            {
                "indicator": {"id": "NY.GDP.MKTP.CD"},
                "country": {"id": "US"},
                "countryiso3code": "USA",
                "value": None,
                "date": "2025",
            },
        ])

        fetcher = WorldBankFetcher()
        records = fetcher._fetch_single_indicator(["US"], "NY.GDP.MKTP.CD")
        assert len(records) == 0


# ---------------------------------------------------------------------------
# IMF fetcher tests
# ---------------------------------------------------------------------------

class TestIMFFetcher:
    @patch("agents.prefetch.fetch_imf.IMFFetcher.get_json")
    def test_parses_weo_data(self, mock_get):
        from agents.prefetch.fetch_imf import IMFFetcher

        mock_get.return_value = {
            "values": {
                "NGDP_RPCH": {
                    "USA": {"2024": "2.5", "2025": "2.1", "2026": "1.8"},
                    "CHN": {"2024": "4.8", "2025": "4.5"},
                    "ZZZ": {"2024": "1.0"},  # untracked, should be filtered
                }
            }
        }

        fetcher = IMFFetcher()
        records = fetcher._fetch_indicator("NGDP_RPCH", ["USA", "CHN"])
        assert len(records) >= 4  # Multiple years for USA + CHN
        assert not any(r["country_code"] == "ZZZ" for r in records)
        usa_records = [r for r in records if r["country_code"] == "USA"]
        assert any(r["is_forecast"] for r in usa_records)


# ---------------------------------------------------------------------------
# GDELT fetcher tests
# ---------------------------------------------------------------------------

class TestGDELTFetcher:
    @patch("agents.prefetch.fetch_gdelt.GDELTFetcher.get_json")
    def test_parses_doc_api(self, mock_get):
        from agents.prefetch.fetch_gdelt import GDELTFetcher

        mock_get.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "url": "https://example.com/1",
                    "domain": "example.com",
                    "language": "English",
                    "seendate": "20260310T120000Z",
                },
            ]
        }

        fetcher = GDELTFetcher()
        records = fetcher._fetch_doc_query({
            "id": "test",
            "query": "test",
            "maxrecords": 10,
        })
        assert len(records) == 1
        assert records[0]["title"] == "Test Article"

    @patch("agents.prefetch.fetch_gdelt.GDELTFetcher.get_json")
    def test_deduplicates_by_url(self, mock_get):
        from agents.prefetch.fetch_gdelt import GDELTFetcher

        mock_get.return_value = {
            "articles": [
                {"title": "A", "url": "https://example.com/1", "domain": "x", "language": "en", "seendate": ""},
                {"title": "B", "url": "https://example.com/1", "domain": "x", "language": "en", "seendate": ""},
                {"title": "C", "url": "https://example.com/2", "domain": "x", "language": "en", "seendate": ""},
            ]
        }

        fetcher = GDELTFetcher()
        # Simulate run which deduplicates
        # We need to call the internal method multiple times with same data
        r1 = fetcher._fetch_doc_query({"id": "t1", "query": "q"})
        r2 = fetcher._fetch_doc_query({"id": "t2", "query": "q"})
        all_records = r1 + r2
        seen = set()
        deduped = []
        for r in all_records:
            if r["url"] not in seen:
                seen.add(r["url"])
                deduped.append(r)
        assert len(deduped) == 2


# ---------------------------------------------------------------------------
# FX fetcher tests
# ---------------------------------------------------------------------------

class TestFXFetcher:
    @patch("agents.prefetch.fetch_fx_commodities.FXCommoditiesFetcher.get_json")
    def test_parses_frankfurter(self, mock_get):
        from agents.prefetch.fetch_fx_commodities import FXCommoditiesFetcher

        mock_get.return_value = {
            "base": "USD",
            "date": "2026-03-10",
            "rates": {
                "EUR": 0.92, "GBP": 0.79, "JPY": 148.5,
                "BRL": 5.85, "INR": 83.2,
            }
        }

        fetcher = FXCommoditiesFetcher()
        records = fetcher._fetch_fx_frankfurter()
        assert len(records) >= 4
        eur = next(r for r in records if r["currency"] == "EUR")
        assert eur["rate_vs_usd"] == 0.92
        assert eur["country_code"] == "DEU"


# ---------------------------------------------------------------------------
# Output schema validation
# ---------------------------------------------------------------------------

class TestOutputSchema:
    """Verify all fetcher outputs conform to the expected envelope schema."""

    REQUIRED_ENVELOPE_KEYS = {"source_id", "fetched_at", "records", "errors", "stats"}

    def test_envelope_has_required_keys(self):
        f = BaseFetcher()
        f.source_id = "test"
        env = f.build_envelope([])
        for key in self.REQUIRED_ENVELOPE_KEYS:
            assert key in env, f"Missing key: {key}"

    def test_records_is_list(self):
        f = BaseFetcher()
        f.source_id = "test"
        env = f.build_envelope([{"a": 1}])
        assert isinstance(env["records"], list)

    def test_errors_is_list(self):
        f = BaseFetcher()
        f.source_id = "test"
        env = f.build_envelope([])
        assert isinstance(env["errors"], list)
