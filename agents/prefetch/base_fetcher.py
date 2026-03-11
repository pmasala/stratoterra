"""
Base fetcher with retry, caching, and fallback logic.

All source-specific fetch scripts inherit from BaseFetcher.
"""

import json
import logging
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("prefetch")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREFETCHED_DIR = PROJECT_ROOT / "staging" / "prefetched"
CACHE_DIR = PROJECT_ROOT / "staging" / "prefetch_cache"
COUNTRY_LIST_PATH = PROJECT_ROOT / "data" / "indices" / "country_list.json"


def load_country_list() -> dict:
    """Load and return the country list with tier groupings."""
    with open(COUNTRY_LIST_PATH) as f:
        return json.load(f)


def get_all_country_codes() -> list[str]:
    """Return flat list of all 75 ISO3 country codes."""
    data = load_country_list()
    codes = []
    for tier in data["tiers"].values():
        codes.extend(c["code"] for c in tier["countries"])
    return codes


def get_countries_by_tier() -> dict[str, list[dict]]:
    """Return {tier_1: [...], tier_2: [...], tier_3: [...]}."""
    data = load_country_list()
    return {k: v["countries"] for k, v in data["tiers"].items()}


# ISO3 -> ISO2 mapping for World Bank API (which uses ISO2).
# Covers all 75 tracked countries.
ISO3_TO_ISO2 = {
    "USA": "US", "CHN": "CN", "JPN": "JP", "DEU": "DE", "GBR": "GB",
    "FRA": "FR", "IND": "IN", "ITA": "IT", "CAN": "CA", "KOR": "KR",
    "RUS": "RU", "BRA": "BR", "AUS": "AU", "ESP": "ES", "MEX": "MX",
    "IDN": "ID", "NLD": "NL", "SAU": "SA", "TUR": "TR", "CHE": "CH",
    "POL": "PL", "SWE": "SE", "NOR": "NO", "ISR": "IL", "ARE": "AE",
    "SGP": "SG", "TWN": "TW", "THA": "TH", "MYS": "MY", "ZAF": "ZA",
    "NGA": "NG", "EGY": "EG", "PAK": "PK", "BGD": "BD", "VNM": "VN",
    "PHL": "PH", "COL": "CO", "ARG": "AR", "CHL": "CL", "PER": "PE",
    "IRN": "IR", "IRQ": "IQ", "KAZ": "KZ", "UKR": "UA", "ROU": "RO",
    "CZE": "CZ", "GRC": "GR", "PRT": "PT", "FIN": "FI", "IRL": "IE",
    "NZL": "NZ", "QAT": "QA", "KWT": "KW", "OMN": "OM", "MAR": "MA",
    "ETH": "ET", "KEN": "KE", "TZA": "TZ", "GHA": "GH", "CIV": "CI",
    "SEN": "SN", "AGO": "AO", "MOZ": "MZ", "COD": "CD", "MMR": "MM",
    "LKA": "LK", "UZB": "UZ", "AZE": "AZ", "GEO": "GE", "SRB": "RS",
    "HUN": "HU", "BGR": "BG", "HRV": "HR", "JOR": "JO", "LBY": "LY",
}

ISO2_TO_ISO3 = {v: k for k, v in ISO3_TO_ISO2.items()}


class BaseFetcher:
    """Base class for all prefetch scripts."""

    source_id: str = "base"
    output_filename: str = "base.json"

    def __init__(self):
        self.session = self._build_session()
        self.errors: list[dict] = []
        self.stats = {"requests_made": 0, "requests_failed": 0, "cache_hits": 0}
        self.run_timestamp = datetime.now(timezone.utc).isoformat()

    def _build_session(self) -> requests.Session:
        """Build a requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": "Stratoterra/1.0 (geopolitical-intelligence; research)",
            "Accept": "application/json",
        })
        return session

    def get(self, url: str, params: dict | None = None,
            timeout: int = 30) -> requests.Response | None:
        """Make a GET request with error handling."""
        self.stats["requests_made"] += 1
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            self.stats["requests_failed"] += 1
            self.errors.append({
                "url": url,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            logger.warning("Request failed: %s — %s", url[:120], e)
            return None

    def get_json(self, url: str, params: dict | None = None,
                 timeout: int = 30) -> Any | None:
        """Make a GET request and return parsed JSON."""
        resp = self.get(url, params=params, timeout=timeout)
        if resp is None:
            return None
        try:
            return resp.json()
        except ValueError:
            logger.warning("Invalid JSON from %s", url[:120])
            return None

    def save_output(self, data: dict) -> Path:
        """Save the output JSON to staging/prefetched/."""
        PREFETCHED_DIR.mkdir(parents=True, exist_ok=True)
        output_path = PREFETCHED_DIR / self.output_filename
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Wrote %s", output_path)
        return output_path

    def update_cache(self, data: dict) -> None:
        """Copy successful output to the cache directory for fallback."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = CACHE_DIR / self.output_filename
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_cache(self) -> dict | None:
        """Load the last successful output from cache."""
        cache_path = CACHE_DIR / self.output_filename
        if cache_path.exists():
            self.stats["cache_hits"] += 1
            with open(cache_path) as f:
                return json.load(f)
        return None

    def build_envelope(self, records: list[dict],
                       skipped: list[dict] | None = None,
                       extra: dict | None = None) -> dict:
        """Build the standard output envelope."""
        envelope = {
            "source_id": self.source_id,
            "fetched_at": self.run_timestamp,
            "records": records,
            "skipped": skipped or [],
            "errors": self.errors,
            "stats": self.stats,
        }
        if extra:
            envelope.update(extra)
        return envelope

    def run(self) -> dict:
        """Override in subclass. Must return the output dict."""
        raise NotImplementedError

    def execute(self) -> dict:
        """Run the fetcher with fallback to cache on failure."""
        logger.info("Starting %s fetcher", self.source_id)
        start = time.monotonic()
        try:
            result = self.run()
            elapsed = time.monotonic() - start
            result["stats"]["elapsed_seconds"] = round(elapsed, 1)

            # If we got meaningful data, update cache
            if result.get("records") and len(result["records"]) > 0:
                self.update_cache(result)
                logger.info(
                    "%s: %d records in %.1fs",
                    self.source_id, len(result["records"]), elapsed,
                )
            else:
                logger.warning("%s: 0 records, checking cache fallback", self.source_id)
                cached = self.load_cache()
                if cached:
                    cached["_fallback"] = True
                    cached["_fallback_reason"] = "Live fetch returned 0 records"
                    cached["_original_errors"] = self.errors
                    result = cached

            self.save_output(result)
            return result

        except Exception as e:
            elapsed = time.monotonic() - start
            logger.error("%s failed after %.1fs: %s", self.source_id, elapsed, e)
            cached = self.load_cache()
            if cached:
                cached["_fallback"] = True
                cached["_fallback_reason"] = str(e)
                self.save_output(cached)
                return cached
            # No cache — write an error envelope
            err_result = self.build_envelope([], extra={
                "_error": str(e),
                "stats": {**self.stats, "elapsed_seconds": round(elapsed, 1)},
            })
            self.save_output(err_result)
            return err_result
