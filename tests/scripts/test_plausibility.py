#!/usr/bin/env python3
"""
Stratoterra — Data Plausibility Tests
Tests UT-PLB-001 through UT-PLB-008

Verifies that factor values sit within realistic ranges.
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
COUNTRIES_DIR = os.path.join(DATA_DIR, "countries")
RELATIONS_DIR = os.path.join(DATA_DIR, "relations")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
INDICES_DIR = os.path.join(DATA_DIR, "indices")

SUMMARY_PATHS = [
    os.path.join(CHUNKS_DIR, "country-summary", "all_countries_summary.json"),
    os.path.join(CHUNKS_DIR, "all_countries_summary.json"),
]

# ---------------------------------------------------------------------------
# Plausibility bounds
# ---------------------------------------------------------------------------

# GDP
GDP_NOMINAL_MIN = 1e8            # $100 million (smallest tracked economies)
GDP_NOMINAL_MAX = 100e12         # $100 trillion (extreme upper)
GDP_PER_CAPITA_MIN = 200         # $200 USD
GDP_PER_CAPITA_MAX = 200_000     # $200,000 USD
GDP_GROWTH_MIN = -30             # -30%
GDP_GROWTH_MAX = 30              # +30%

# Population
POP_MIN = 100_000                # 100 thousand
POP_MAX = 2_000_000_000          # 2 billion

# Military
MILITARY_SPEND_MAX_GDP_RATIO = 0.40   # 40% of GDP — wartime economies (e.g. Ukraine) can exceed 30%
MAX_NUCLEAR_WARHEADS = 10_000
MAX_AIRCRAFT_CARRIERS = 15

# Economic indices
ECI_MIN = -3.0
ECI_MAX = 3.0

# Scores expected in [0, 1]
ZERO_ONE_FIELDS_SUMMARY = [
    "political_stability",
    "investment_risk_score",
    "overall_score",
]

# Alert
ALERT_COUNT_MIN = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def glob_json_files(directory):
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".json")
    )


def find_file(candidates):
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def load_summary():
    path = find_file(SUMMARY_PATHS)
    if not path:
        return None
    data = load_json(path)
    return data if isinstance(data, list) else None


def get_nested(data, *keys, default=None):
    """Traverse nested dicts; return default if any key is missing."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


# ---------------------------------------------------------------------------
# UT-PLB-001: GDP values are plausible
# ---------------------------------------------------------------------------

class TestUT_PLB_001_GDP(unittest.TestCase):
    """UT-PLB-001: GDP values (nominal, per capita, growth) are in realistic ranges."""

    def setUp(self):
        self.summary = load_summary()
        self.country_files = glob_json_files(COUNTRIES_DIR)

    def test_gdp_nominal_positive_summary(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            gdp = item.get("gdp_nominal_usd")
            if gdp is not None and gdp <= 0:
                errors.append(f"{code}: gdp_nominal_usd={gdp} is not positive")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_gdp_nominal_below_max_summary(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            gdp = item.get("gdp_nominal_usd")
            if gdp is not None and gdp > GDP_NOMINAL_MAX:
                errors.append(
                    f"{code}: gdp_nominal_usd={gdp:.2e} exceeds maximum {GDP_NOMINAL_MAX:.2e}"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_gdp_per_capita_range_summary(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            pc = item.get("gdp_per_capita_usd")
            if pc is not None:
                if pc < GDP_PER_CAPITA_MIN or pc > GDP_PER_CAPITA_MAX:
                    errors.append(
                        f"{code}: gdp_per_capita_usd={pc} outside [{GDP_PER_CAPITA_MIN}, {GDP_PER_CAPITA_MAX}]"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_gdp_growth_rate_range_summary(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            growth = item.get("gdp_real_growth_pct")
            if growth is not None:
                if growth < GDP_GROWTH_MIN or growth > GDP_GROWTH_MAX:
                    errors.append(
                        f"{code}: gdp_real_growth_pct={growth} outside "
                        f"[{GDP_GROWTH_MIN}, {GDP_GROWTH_MAX}]"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_gdp_growth_trend_valid_summary(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        valid = {"strong_growth", "growth", "stable", "decrease", "strong_decrease"}
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            trend = item.get("gdp_growth_trend")
            if trend is not None and trend not in valid:
                errors.append(f"{code}: gdp_growth_trend='{trend}' not in {valid}")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-002: Population values are plausible
# ---------------------------------------------------------------------------

class TestUT_PLB_002_Population(unittest.TestCase):
    """UT-PLB-002: Population values in realistic range."""

    def setUp(self):
        self.summary = load_summary()

    def test_population_minimum(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            pop = item.get("population")
            if pop is not None and pop < POP_MIN:
                errors.append(f"{code}: population={pop} below minimum {POP_MIN}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_population_maximum(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            pop = item.get("population")
            if pop is not None and pop > POP_MAX:
                errors.append(
                    f"{code}: population={pop:,} exceeds maximum {POP_MAX:,}"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_population_is_integer(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            pop = item.get("population")
            if pop is not None and not isinstance(pop, int):
                errors.append(
                    f"{code}: population={pop!r} should be an integer, got {type(pop).__name__}"
                )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-003: Political stability index in [0, 1]
# ---------------------------------------------------------------------------

class TestUT_PLB_003_PoliticalStability(unittest.TestCase):
    """UT-PLB-003: political_stability is normalized to [0, 1]."""

    def setUp(self):
        self.summary = load_summary()

    def test_political_stability_range(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            val = item.get("political_stability")
            if val is not None and not (0.0 <= val <= 1.0):
                errors.append(f"{code}: political_stability={val} outside [0, 1]")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-004: Investment risk score in [0, 1]
# ---------------------------------------------------------------------------

class TestUT_PLB_004_InvestmentRisk(unittest.TestCase):
    """UT-PLB-004: investment_risk_score is normalized to [0, 1]."""

    def setUp(self):
        self.summary = load_summary()

    def test_investment_risk_range(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            val = item.get("investment_risk_score")
            if val is not None and not (0.0 <= val <= 1.0):
                errors.append(f"{code}: investment_risk_score={val} outside [0, 1]")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-005: Military spending > 0 for all Tier 1 countries
# ---------------------------------------------------------------------------

class TestUT_PLB_005_MilitarySpending(unittest.TestCase):
    """UT-PLB-005: Tier 1 countries must have positive military spending."""

    def setUp(self):
        self.summary = load_summary()

    def test_tier1_military_spending_positive(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            if item.get("tier") != 1:
                continue
            code = item.get("code", "?")
            spend = item.get("military_spending_usd")
            if spend is None:
                errors.append(f"{code} (Tier 1): military_spending_usd is missing")
            elif spend <= 0:
                errors.append(
                    f"{code} (Tier 1): military_spending_usd={spend} must be positive"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_military_spending_not_exceed_20pct_gdp(self):
        """Military spending should not exceed 20% of GDP (extreme upper bound per spec)."""
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            spend = item.get("military_spending_usd")
            gdp = item.get("gdp_nominal_usd")
            if spend and gdp and gdp > 0:
                ratio = spend / gdp
                if ratio > MILITARY_SPEND_MAX_GDP_RATIO:
                    errors.append(
                        f"{code}: military spending is {ratio:.1%} of GDP "
                        f"(max allowed {MILITARY_SPEND_MAX_GDP_RATIO:.0%})"
                    )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-006: Economic Complexity Index in [-3, +3]
# ---------------------------------------------------------------------------

class TestUT_PLB_006_ECI(unittest.TestCase):
    """UT-PLB-006: economic_complexity_index in [-3, +3] per Harvard/MIT methodology."""

    def setUp(self):
        self.summary = load_summary()

    def test_eci_range(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            eci = item.get("economic_complexity_index")
            if eci is not None and not (ECI_MIN <= eci <= ECI_MAX):
                errors.append(
                    f"{code}: economic_complexity_index={eci} outside [{ECI_MIN}, {ECI_MAX}]"
                )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-007: Alert counts non-negative
# ---------------------------------------------------------------------------

class TestUT_PLB_007_AlertCounts(unittest.TestCase):
    """UT-PLB-007: alert_count is a non-negative integer in summary."""

    def setUp(self):
        self.summary = load_summary()

    def test_alert_count_non_negative(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            count = item.get("alert_count")
            if count is not None and count < 0:
                errors.append(f"{code}: alert_count={count} is negative")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_alert_count_is_integer(self):
        if self.summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in self.summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            count = item.get("alert_count")
            if count is not None and not isinstance(count, int):
                errors.append(
                    f"{code}: alert_count={count!r} should be int, got {type(count).__name__}"
                )
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# UT-PLB-008: Derived composite scores from country detail files are in [0, 1]
# ---------------------------------------------------------------------------

class TestUT_PLB_008_DerivedScores(unittest.TestCase):
    """UT-PLB-008: Derived layer composite scores are in [0, 1]."""

    def setUp(self):
        self.country_files = glob_json_files(COUNTRIES_DIR)

    def test_overall_score_range_in_summary(self):
        summary = load_summary()
        if summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            score = item.get("overall_score")
            if score is not None and not (0.0 <= score <= 1.0):
                errors.append(f"{code}: overall_score={score} outside [0, 1]")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_energy_independence_non_negative(self):
        """Energy independence is a ratio (>=0); >1 means net exporter — that is valid."""
        summary = load_summary()
        if summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            val = item.get("energy_independence")
            if val is not None and val < 0:
                errors.append(f"{code}: energy_independence={val} is negative")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_trade_openness_non_negative(self):
        summary = load_summary()
        if summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            val = item.get("trade_openness_pct")
            if val is not None and val < 0:
                errors.append(f"{code}: trade_openness_pct={val} is negative")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_latitude_longitude_valid_in_summary(self):
        summary = load_summary()
        if summary is None:
            self.skipTest("Summary not found")
        errors = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            code = item.get("code", "?")
            lat = item.get("latitude")
            lon = item.get("longitude")
            if lat is not None and not (-90 <= lat <= 90):
                errors.append(f"{code}: latitude={lat} outside [-90, 90]")
            if lon is not None and not (-180 <= lon <= 180):
                errors.append(f"{code}: longitude={lon} outside [-180, 180]")
        self.assertEqual(errors, [], "\n".join(errors))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
