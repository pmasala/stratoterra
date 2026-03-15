#!/usr/bin/env python3
"""
Agent 11 — Derived Metrics Calculator

Computes composite and derived scores from base factors for all 75 countries.
Updates the `derived` section of each country file and generates global_rankings.json.

Usage:
    python3 agents/scripts/agent_11_derived_metrics.py                # auto-detect date/run_id
    python3 agents/scripts/agent_11_derived_metrics.py --run-id 2026-W11 --timestamp 2026-03-10T16:00:00Z
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COUNTRIES_DIR = str(PROJECT_ROOT / "data" / "countries")
COUNTRY_LIST = str(PROJECT_ROOT / "data" / "indices" / "country_list.json")
RANKINGS_OUT = str(PROJECT_ROOT / "data" / "global" / "global_rankings.json")

def _compute_defaults():
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}", now.strftime("%Y-%m-%dT%H:%M:%SZ")

_default_run_id, _default_timestamp = _compute_defaults()
RUN_ID = _default_run_id
TIMESTAMP = _default_timestamp

# ─── Helper: extract a numeric value from a country dict ─────────────────────

def get_val(data, *paths):
    """
    Try multiple possible paths to find a numeric value.
    Data structure has values in multiple places:
      - data["macroeconomic"]["field"]["value"]
      - data["layers"]["economy"]["field"]
      - data["layers"]["institutions"]["field"]
      - data["economy"]["field"]["value"]
      - data["institutions"]["field"]["value"]
      - data["military"]["field"]["value"]
      - data["layers"]["military"]["field"]
      - data["demographic"]["field"]["value"]
      - data["layers"]["endowments"]["field"]
    """
    for path in paths:
        keys = path.split(".")
        obj = data
        try:
            for k in keys:
                obj = obj[k]
            # If it's a dict with "value", get the value
            if isinstance(obj, dict) and "value" in obj:
                v = obj["value"]
            else:
                v = obj
            if isinstance(v, (int, float)):
                return v
            if isinstance(v, str):
                try:
                    return float(v)
                except (ValueError, TypeError):
                    pass
        except (KeyError, TypeError, IndexError):
            continue
    return None


def get_list_val(data, *paths):
    """Get a list value from data."""
    for path in paths:
        keys = path.split(".")
        obj = data
        try:
            for k in keys:
                obj = obj[k]
            if isinstance(obj, dict) and "value" in obj:
                v = obj["value"]
            else:
                v = obj
            if isinstance(v, list):
                return v
        except (KeyError, TypeError, IndexError):
            continue
    return None


def get_str_val(data, *paths):
    """Get a string value from data."""
    for path in paths:
        keys = path.split(".")
        obj = data
        try:
            for k in keys:
                obj = obj[k]
            if isinstance(obj, dict) and "value" in obj:
                v = obj["value"]
            else:
                v = obj
            if isinstance(v, str):
                return v
        except (KeyError, TypeError, IndexError):
            continue
    return None


def get_bool_val(data, *paths):
    """Get a boolean value from data."""
    for path in paths:
        keys = path.split(".")
        obj = data
        try:
            for k in keys:
                obj = obj[k]
            if isinstance(obj, dict) and "value" in obj:
                v = obj["value"]
            else:
                v = obj
            if isinstance(v, bool):
                return v
        except (KeyError, TypeError, IndexError):
            continue
    return None


# ─── Normalize helpers ───────────────────────────────────────────────────────

def normalize_0_1(val, min_val, max_val):
    """Normalize a value to 0.0-1.0 range."""
    if val is None or max_val == min_val:
        return None
    return max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))


def normalize_0_100(val, min_val, max_val):
    """Normalize a value to 0-100 range."""
    n = normalize_0_1(val, min_val, max_val)
    if n is None:
        return None
    return round(n * 100, 1)


def clamp(val, lo, hi):
    """Clamp a value to a range."""
    if val is None:
        return None
    return max(lo, min(hi, val))


# ─── Country knowledge base for energy/chokepoint estimation ────────────────

# Energy independence: based on known production/consumption profiles
ENERGY_OVERRIDES = {
    # Major oil/gas exporters — energy independent
    "SAU": 1.0, "RUS": 1.0, "NOR": 1.0, "ARE": 1.0, "KWT": 1.0,
    "QAT": 1.0, "NGA": 1.0, "IRN": 1.0, "IRQ": 1.0, "KAZ": 1.0,
    "AZE": 1.0, "AGO": 1.0, "LBY": 1.0, "OMN": 1.0, "COL": 0.85,
    # Net energy self-sufficient
    "USA": 1.0, "CAN": 0.95, "AUS": 0.90, "BRA": 0.85, "IDN": 0.75,
    "MYS": 0.80, "GBR": 0.65,
    # Moderate importers
    "CHN": 0.55, "IND": 0.35, "MEX": 0.70, "ARG": 0.75, "EGY": 0.60,
    "VNM": 0.55, "THA": 0.45, "PHL": 0.30, "PAK": 0.40, "BGD": 0.25,
    "TUR": 0.30, "ZAF": 0.70, "PER": 0.55, "CHL": 0.35,
    # Heavy importers
    "JPN": 0.10, "KOR": 0.12, "DEU": 0.30, "FRA": 0.55,  # France has nuclear
    "ITA": 0.20, "ESP": 0.25, "NLD": 0.55, "CHE": 0.50,
    "POL": 0.55, "SWE": 0.65, "TWN": 0.10, "SGP": 0.02,
    "ISR": 0.60, "IRL": 0.15, "FIN": 0.50, "GRC": 0.20,
    "PRT": 0.25, "CZE": 0.50, "BEL": 0.15,
    # Tier 2
    "MAR": 0.10, "ROU": 0.55, "NZL": 0.70, "JOR": 0.05,
    "UKR": 0.45, "HUN": 0.35, "BGR": 0.45,
    # Tier 3
    "ETH": 0.80,  # Hydro-rich
    "KEN": 0.60,  # Geothermal
    "TZA": 0.55, "GHA": 0.50, "CIV": 0.50,
    "SEN": 0.30, "MOZ": 0.70, "COD": 0.65,  # Hydro potential
    "MMR": 0.60, "LKA": 0.30, "UZB": 0.85,
    "GEO": 0.55, "SRB": 0.45, "HRV": 0.45,
}

# Maritime chokepoint dependency (0=low, 1=high)
# Based on geographic position and trade routing
CHOKEPOINT_BASE = {
    # Hormuz-dependent (Gulf states, major Asian importers)
    "SAU": 0.90, "ARE": 0.85, "KWT": 0.95, "QAT": 0.90, "OMN": 0.80,
    "IRN": 1.0, "IRQ": 0.85, "BHR": 0.95,
    # Asian importers heavily dependent on Hormuz for oil
    "JPN": 0.75, "KOR": 0.75, "IND": 0.65, "CHN": 0.60, "TWN": 0.70,
    "SGP": 0.80, "THA": 0.60, "MYS": 0.50, "IDN": 0.45, "PHL": 0.55,
    "VNM": 0.50, "BGD": 0.55, "PAK": 0.60, "LKA": 0.55, "MMR": 0.40,
    # Suez/Red Sea dependent (Europe-Asia trade)
    "EGY": 0.70, "ISR": 0.50, "JOR": 0.55, "TUR": 0.40,
    "GRC": 0.35, "ITA": 0.30, "DEU": 0.25, "FRA": 0.25, "NLD": 0.25,
    "ESP": 0.25, "GBR": 0.20, "CHE": 0.15, "POL": 0.15,
    "SWE": 0.15, "NOR": 0.10, "FIN": 0.15, "IRL": 0.15,
    "PRT": 0.20, "CZE": 0.15, "ROU": 0.20, "HUN": 0.15,
    "BGR": 0.20, "HRV": 0.20, "SRB": 0.15, "GEO": 0.25,
    # Atlantic-facing or landlocked — low exposure
    "USA": 0.15, "CAN": 0.10, "MEX": 0.10, "BRA": 0.15,
    "ARG": 0.10, "CHL": 0.15, "COL": 0.10, "PER": 0.10,
    "AUS": 0.30, "NZL": 0.25,
    # Africa
    "NGA": 0.15, "ZAF": 0.25, "KEN": 0.40, "ETH": 0.30,
    "TZA": 0.35, "GHA": 0.15, "CIV": 0.15, "SEN": 0.15,
    "AGO": 0.15, "MOZ": 0.35, "COD": 0.15, "MAR": 0.20,
    "LBY": 0.20,
    # Central Asia
    "KAZ": 0.20, "UZB": 0.15, "AZE": 0.25,
    # Russia (Arctic/overland routes)
    "RUS": 0.15,
    "UKR": 0.25,
}

# Resource self-sufficiency overrides
RESOURCE_SELF_SUFFICIENCY = {
    "USA": 0.92, "CAN": 0.95, "AUS": 0.90, "RUS": 0.95, "BRA": 0.85,
    "CHN": 0.65, "IND": 0.55, "SAU": 0.50, "ARE": 0.40, "NOR": 0.80,
    "KWT": 0.35, "QAT": 0.30, "IDN": 0.75, "MYS": 0.70, "NGA": 0.60,
    "IRN": 0.75, "IRQ": 0.55, "KAZ": 0.85, "AZE": 0.70, "AGO": 0.55,
    "LBY": 0.45, "OMN": 0.40, "COL": 0.70, "ARG": 0.75, "CHL": 0.65,
    "PER": 0.60, "ZAF": 0.70, "MEX": 0.65, "EGY": 0.45,
    # Industrialized importers
    "JPN": 0.20, "KOR": 0.18, "DEU": 0.35, "GBR": 0.40, "FRA": 0.45,
    "ITA": 0.30, "ESP": 0.35, "NLD": 0.35, "CHE": 0.25, "TWN": 0.15,
    "SGP": 0.05, "SWE": 0.55, "FIN": 0.55, "IRL": 0.35, "POL": 0.50,
    "ISR": 0.30, "TUR": 0.40, "GRC": 0.30, "PRT": 0.30, "CZE": 0.40,
    "THA": 0.50, "VNM": 0.55, "PHL": 0.40, "PAK": 0.45, "BGD": 0.35,
    "NZL": 0.80, "ROU": 0.55, "HUN": 0.40, "BGR": 0.45, "HRV": 0.40,
    "SRB": 0.45, "GEO": 0.40, "JOR": 0.15, "MAR": 0.35, "UKR": 0.60,
    # Africa Tier 3
    "ETH": 0.50, "KEN": 0.45, "TZA": 0.50, "GHA": 0.55, "CIV": 0.55,
    "SEN": 0.40, "MOZ": 0.55, "COD": 0.65, "MMR": 0.55, "LKA": 0.35,
    "UZB": 0.60,
}

# Credit rating to spread (bps) mapping
RATING_SPREAD = {
    "AAA": 0, "AA+": 15, "AA": 25, "AA-": 40,
    "A+": 55, "A": 70, "A-": 90,
    "BBB+": 120, "BBB": 150, "BBB-": 200,
    "BB+": 250, "BB": 300, "BB-": 375,
    "B+": 450, "B": 550, "B-": 650,
    "CCC+": 800, "CCC": 1000, "CCC-": 1200,
    "CC": 1500, "C": 2000, "D": 3000, "SD": 3000,
    "NR": None
}

# Known conflict/war status (as of 2026-03-10)
ACTIVE_CONFLICT = {
    "IRN": "active_war",        # US-Israel Operation Epic Fury — under bombardment
    "USA": "active_war_abroad", # Conducting war against Iran (Epic Fury); 3 KIA
    "UKR": "active_war",        # Russia-Ukraine war
    "ISR": "active_conflict",   # Multi-front engagement, striking Iran
    "RUS": "active_war",        # War in Ukraine + tensions
    "IRQ": "active_conflict",   # Instability + Iran spillover; IRGC struck US bases
    "MMR": "civil_war",         # Myanmar civil war
    "ETH": "post_conflict",     # Tigray aftermath
    "COD": "active_conflict",   # Eastern DRC conflict
    "LBY": "fragile",           # Ongoing instability
    "NGA": "insurgency",        # Boko Haram (170+ killed)
    "PAK": "terrorism",         # TTP attacks
    "SOM": "active_conflict",   # Al-Shabaab
}

# Countries currently under comprehensive sanctions
SANCTIONED_COUNTRIES = {"IRN", "RUS", "MMR", "LBY"}

# Market accessibility knowledge base
# capital account openness (0-1), financial market depth, ease of business
MARKET_ACCESS_OVERRIDES = {
    "USA": 0.95, "GBR": 0.93, "SGP": 0.95, "CHE": 0.92, "CAN": 0.90,
    "AUS": 0.90, "JPN": 0.85, "DEU": 0.88, "FRA": 0.85, "NLD": 0.90,
    "NOR": 0.88, "SWE": 0.88, "IRL": 0.90, "FIN": 0.85, "NZL": 0.85,
    "KOR": 0.80, "TWN": 0.78, "ISR": 0.80, "ESP": 0.82, "ITA": 0.78,
    "HRV": 0.65, "CZE": 0.75, "POL": 0.75, "PRT": 0.78, "GRC": 0.68,
    "HUN": 0.70, "BGR": 0.65, "ROU": 0.68, "SRB": 0.55,
    "CHN": 0.45, "IND": 0.50, "BRA": 0.60, "MEX": 0.65, "ZAF": 0.65,
    "TUR": 0.55, "ARE": 0.78, "SAU": 0.55, "QAT": 0.65, "KWT": 0.55,
    "OMN": 0.50, "EGY": 0.40, "MAR": 0.45, "JOR": 0.45,
    "THA": 0.60, "MYS": 0.68, "IDN": 0.55, "PHL": 0.55, "VNM": 0.45,
    "COL": 0.55, "CHL": 0.70, "PER": 0.55, "ARG": 0.35,
    "RUS": 0.15, "IRN": 0.05, "IRQ": 0.20, "UKR": 0.30,
    "NGA": 0.30, "KEN": 0.35, "GHA": 0.35, "ETH": 0.20,
    "KAZ": 0.40, "AZE": 0.35, "UZB": 0.25, "GEO": 0.50,
    "PAK": 0.35, "BGD": 0.30, "LKA": 0.30,
    "TZA": 0.25, "CIV": 0.30, "SEN": 0.30, "AGO": 0.25,
    "MOZ": 0.20, "COD": 0.10, "MMR": 0.10, "LBY": 0.10,
}


# ─── Metric computation functions ───────────────────────────────────────────

def compute_energy_independence(code, data):
    """Compute energy independence index (0.0-1.0)."""
    if code in ENERGY_OVERRIDES:
        return ENERGY_OVERRIDES[code]
    # Fallback: estimate from trade balance and region
    exports = get_val(data, "macroeconomic.total_exports_usd", "layers.economy.total_exports_usd")
    imports = get_val(data, "macroeconomic.total_imports_usd", "layers.economy.total_imports_usd")
    if exports and imports and imports > 0:
        ratio = exports / imports
        return clamp(ratio * 0.5, 0.1, 0.9)
    return 0.4  # default mid-range


def compute_resource_self_sufficiency(code, data):
    """Compute resource self-sufficiency index (0.0-1.0)."""
    if code in RESOURCE_SELF_SUFFICIENCY:
        return RESOURCE_SELF_SUFFICIENCY[code]
    # Fallback: estimate from trade patterns
    exports = get_val(data, "macroeconomic.total_exports_usd", "layers.economy.total_exports_usd")
    imports = get_val(data, "macroeconomic.total_imports_usd", "layers.economy.total_imports_usd")
    if exports and imports and imports > 0:
        ratio = exports / imports
        return clamp(ratio * 0.5, 0.1, 0.8)
    return 0.4


def compute_chokepoint_exposure(code, data):
    """
    Compute supply chain chokepoint exposure (0.0-1.0).
    Higher = more exposed.
    Accounts for active Hormuz closure and Suez disruption.
    """
    base = CHOKEPOINT_BASE.get(code, 0.3)

    # Get trade openness as amplifier
    trade_openness = get_val(data,
        "economy.trade_openness_pct",
        "layers.economy.trade_openness_pct")
    if trade_openness is None:
        # Estimate from exports+imports / GDP
        exports = get_val(data, "macroeconomic.total_exports_usd", "layers.economy.total_exports_usd")
        imports = get_val(data, "macroeconomic.total_imports_usd", "layers.economy.total_imports_usd")
        gdp = get_val(data, "macroeconomic.gdp_nominal_usd", "layers.economy.gdp_nominal_usd")
        if exports and imports and gdp and gdp > 0:
            trade_openness = (exports + imports) / gdp * 100
        else:
            trade_openness = 50  # default

    norm_openness = clamp(trade_openness / 200.0, 0.0, 1.0)

    # Weighted combination: 60% geographic chokepoint, 40% trade openness
    exposure = 0.6 * base + 0.4 * norm_openness

    # Hormuz crisis amplifier — countries near Hormuz or dependent on its flows
    hormuz_dependent = {
        "IRN": 1.0, "SAU": 0.8, "ARE": 0.75, "KWT": 0.85, "QAT": 0.8,
        "OMN": 0.7, "IRQ": 0.7, "BHR": 0.85,
        "JPN": 0.4, "KOR": 0.4, "IND": 0.35, "CHN": 0.3, "TWN": 0.35,
        "SGP": 0.3, "THA": 0.25, "PHL": 0.2, "IDN": 0.2,
    }
    if code in hormuz_dependent:
        crisis_boost = hormuz_dependent[code] * 0.2  # up to +0.2 from Hormuz crisis
        exposure = min(1.0, exposure + crisis_boost)

    return round(clamp(exposure, 0.0, 1.0), 3)


def compute_composite_national_power(code, data, all_data):
    """
    Compute Composite National Power Index (0-100).
    = 0.35*economic + 0.25*military + 0.20*technology + 0.10*diplomatic + 0.10*soft_power
    """
    # Collect raw values for all countries to normalize
    # Economic score — use both nominal and PPP GDP
    gdp = get_val(data, "macroeconomic.gdp_nominal_usd", "layers.economy.gdp_nominal_usd")
    gdp_ppp = get_val(data, "macroeconomic.gdp_ppp_usd")
    gdp_pc = get_val(data, "macroeconomic.gdp_per_capita_usd", "layers.economy.gdp_per_capita_usd")
    fdi = get_val(data, "macroeconomic.fdi_inflows_usd")
    fx_reserves = get_val(data, "macroeconomic.fx_reserves_usd", "layers.economy.fx_reserves_usd")

    # Military score
    mil_exp = get_val(data, "military.military_expenditure_usd",
                      "military.defense_spending_usd",
                      "military.military_spending_usd",
                      "layers.military.military_expenditure_usd",
                      "layers.military.defense_spending_usd")
    personnel = get_val(data, "military.active_military_personnel",
                        "layers.military.active_military_personnel")

    # Technology
    internet = get_val(data, "economy.internet_users_pct", "layers.economy.internet_users_pct")

    # Diplomatic — use FTA count plus alliance count
    alliances = get_list_val(data, "military.alliance_memberships",
                              "layers.military.alliance_memberships")
    fta_count = get_val(data, "trade.fta_count", "layers.relations.fta_count")

    # Soft power — HDI is the core measure (not Freedom House, which measures
    # political rights and shouldn't penalize national *power*)
    hdi = get_val(data, "demographic.hdi", "layers.endowments.hdi")

    # Population as a power multiplier
    population = get_val(data, "demographic.population_total", "layers.endowments.population")

    return {
        "gdp": gdp, "gdp_ppp": gdp_ppp, "gdp_pc": gdp_pc,
        "fdi": fdi, "fx_reserves": fx_reserves,
        "mil_exp": mil_exp, "personnel": personnel,
        "internet": internet, "population": population,
        "alliances": len(alliances) if alliances else 0,
        "fta_count": fta_count or 0,
        "hdi": hdi,
    }


def finalize_cnpi(raw_vals, all_raw):
    """Normalize and combine CNPI components across all countries.

    Uses a blended log+linear normalization for absolute values (GDP,
    military spending) to preserve differentiation at the top of the
    distribution while preventing the USA outlier from completely
    compressing mid-range countries.  Linear normalization for
    per-capita and percentage-based metrics.
    """
    import math

    # Log-scale fields (absolute values with huge range)
    log_fields = {"gdp", "fdi", "mil_exp", "personnel"}
    # Linear fields
    lin_fields = {"gdp_pc", "internet", "alliances", "fta_count", "hdi", "fh_score"}

    all_fields = list(log_fields | lin_fields)
    # Ensure new fields are in appropriate sets
    log_fields.update({"gdp_ppp", "fx_reserves", "population"})
    all_fields = list(log_fields | lin_fields)

    ranges = {}
    log_ranges = {}
    for f in all_fields:
        vals = [r[f] for r in all_raw.values() if r.get(f) is not None and r.get(f, 0) > 0]
        if vals:
            ranges[f] = (min(vals), max(vals))
            if f in log_fields:
                log_vals = [math.log(v) for v in vals if v > 0]
                log_ranges[f] = (min(log_vals), max(log_vals))
        else:
            ranges[f] = (0, 1)
            log_ranges[f] = (0, 1)

    def norm_linear(val, field):
        if val is None:
            return 0.3
        lo, hi = ranges[field]
        if hi == lo:
            return 0.5
        return max(0.0, min(1.0, (val - lo) / (hi - lo)))

    def norm_log(val, field):
        if val is None or val <= 0:
            return 0.1
        lo, hi = log_ranges[field]
        if hi == lo:
            return 0.5
        log_val = math.log(val)
        return max(0.0, min(1.0, (log_val - lo) / (hi - lo)))

    def norm_blended(val, field, lin_weight=0.35):
        """Blend log and linear normalization to preserve top-end differentiation.

        Pure log compresses USA/CHN too much; pure linear compresses everyone
        else.  A 35/65 linear/log blend keeps the top spread while not
        crushing mid-tier countries.
        """
        nl = norm_log(val, field)
        if val is None or val <= 0:
            return nl
        lo, hi = ranges[field]
        if hi == lo:
            return 0.5
        nlin = max(0.0, min(1.0, (val - lo) / (hi - lo)))
        return lin_weight * nlin + (1.0 - lin_weight) * nl

    results = {}
    for code, rv in all_raw.items():
        # Economic component (0-100)
        # Use both nominal and PPP GDP (PPP captures CHN's true economic
        # weight better); blend with FDI and FX reserves
        gdp_score = norm_blended(rv["gdp"], "gdp", 0.35)
        gdp_ppp_score = norm_blended(rv.get("gdp_ppp"), "gdp_ppp", 0.35) if rv.get("gdp_ppp") else gdp_score
        econ = (
            0.30 * gdp_score +
            0.20 * gdp_ppp_score +
            0.20 * norm_linear(rv["gdp_pc"], "gdp_pc") +
            0.15 * norm_blended(rv["fdi"], "fdi", 0.25) +
            0.15 * norm_blended(rv.get("fx_reserves"), "fx_reserves", 0.25)
        ) * 100

        # Military component (0-100)
        mil = (
            0.55 * norm_blended(rv["mil_exp"], "mil_exp", 0.30) +
            0.30 * norm_blended(rv["personnel"], "personnel", 0.20) +
            0.15 * norm_blended(rv.get("population"), "population", 0.15)
        ) * 100

        # Technology component (0-100)
        # Internet penetration * population mass gives tech weight
        internet_score = norm_linear(rv["internet"], "internet")
        pop_score = norm_blended(rv.get("population"), "population", 0.15)
        tech = (
            0.60 * internet_score +
            0.40 * (internet_score * pop_score)  # absolute tech base
        ) * 100

        # Diplomatic component (0-100)
        diplo = (
            0.50 * norm_linear(rv["alliances"], "alliances") +
            0.50 * norm_linear(rv["fta_count"], "fta_count")
        ) * 100

        # Soft power component (0-100) — HDI-based only
        # National power shouldn't penalize authoritarianism;
        # political risk is captured separately in investment risk.
        soft = norm_linear(rv["hdi"], "hdi") * 100

        cnpi = (0.35 * econ + 0.25 * mil + 0.20 * tech +
                0.10 * diplo + 0.10 * soft)

        results[code] = cnpi

    # Apply rank-preserving stretch so top scores reach ~95 and the floor
    # stays near 5.  Uses linear rescaling based on observed range.
    raw_vals = list(results.values())
    raw_min = min(raw_vals)
    raw_max = max(raw_vals)
    # Map [raw_min, raw_max] -> [5, 96]
    target_lo, target_hi = 5.0, 96.0
    if raw_max > raw_min:
        for code in results:
            stretched = target_lo + (results[code] - raw_min) / (raw_max - raw_min) * (target_hi - target_lo)
            results[code] = round(clamp(stretched, 1.0, 100.0), 1)
    else:
        for code in results:
            results[code] = round(clamp(results[code], 1.0, 100.0), 1)

    return results


def parse_credit_rating(rating_str):
    """Extract the best/most relevant rating from a credit rating string."""
    if not rating_str:
        return None
    # Parse "S&P: AA+, Moody's: Aa1, Fitch: AAA" format
    best_spread = None
    for part in rating_str.split(","):
        part = part.strip()
        if ":" in part:
            _, grade = part.split(":", 1)
            grade = grade.strip()
        else:
            grade = part.strip()

        # Convert Moody's to S&P equivalent
        moody_map = {
            "Aaa": "AAA", "Aa1": "AA+", "Aa2": "AA", "Aa3": "AA-",
            "A1": "A+", "A2": "A", "A3": "A-",
            "Baa1": "BBB+", "Baa2": "BBB", "Baa3": "BBB-",
            "Ba1": "BB+", "Ba2": "BB", "Ba3": "BB-",
            "B1": "B+", "B2": "B", "B3": "B-",
            "Caa1": "CCC+", "Caa2": "CCC", "Caa3": "CCC-",
            "Ca": "CC", "C": "C",
        }
        grade = moody_map.get(grade, grade)

        spread = RATING_SPREAD.get(grade)
        if spread is not None:
            if best_spread is None or spread < best_spread:
                best_spread = spread

    return best_spread


def compute_political_risk_premium(code, data):
    """
    Compute Political Risk Premium in basis points.
    Base: sovereign rating implied spread
    Adjustments: governance, conflict, sanctions, autocracy
    """
    # Base from credit rating
    rating_str = get_str_val(data,
        "macroeconomic.sovereign_credit_rating",
        "layers.economy.sovereign_credit_rating")
    base_spread = parse_credit_rating(rating_str)
    if base_spread is None:
        base_spread = 800  # default for unrated

    # WGI governance average (-2.5 to +2.5)
    wgi_fields = [
        "wgi_voice_accountability", "wgi_political_stability",
        "wgi_government_effectiveness", "wgi_regulatory_quality",
        "wgi_rule_of_law", "wgi_control_of_corruption"
    ]
    wgi_vals = []
    for f in wgi_fields:
        v = get_val(data,
            f"institutions.{f}",
            f"layers.institutions.{f}")
        if v is not None:
            wgi_vals.append(v)

    if wgi_vals:
        wgi_avg = sum(wgi_vals) / len(wgi_vals)
    else:
        wgi_avg = 0.0  # neutral

    # Governance adjustment: poor governance adds risk
    # WGI range is roughly -2.5 to +2.5
    # Good governance (>1.0): subtract up to 50 bps
    # Poor governance (<-1.0): add up to 500 bps
    if wgi_avg > 1.0:
        gov_adj = -50 * min(wgi_avg - 1.0, 1.5) / 1.5
    elif wgi_avg < -0.5:
        gov_adj = 500 * min(abs(wgi_avg + 0.5), 2.0) / 2.0
    else:
        gov_adj = 100 * (0.5 - wgi_avg) / 1.5  # 0 to 100

    # Democracy adjustment
    dem_idx = get_val(data,
        "institutions.democracy_index",
        "layers.institutions.democracy_index")
    if dem_idx is not None:
        if dem_idx < 3.0:
            dem_adj = 200  # authoritarian
        elif dem_idx < 5.0:
            dem_adj = 100  # hybrid
        elif dem_idx < 7.0:
            dem_adj = 25   # flawed democracy
        else:
            dem_adj = 0    # full democracy
    else:
        dem_adj = 50

    # Conflict adjustment
    conflict_adj = 0
    conflict_status = ACTIVE_CONFLICT.get(code)
    if conflict_status == "active_war":
        conflict_adj = 800
    elif conflict_status == "active_war_abroad":
        # Conducting war abroad (not under attack at home, but war costs and uncertainty)
        conflict_adj = 100
    elif conflict_status == "civil_war":
        conflict_adj = 600
    elif conflict_status == "active_conflict":
        conflict_adj = 400
    elif conflict_status == "insurgency":
        conflict_adj = 200
    elif conflict_status == "terrorism":
        conflict_adj = 150
    elif conflict_status == "post_conflict":
        conflict_adj = 100
    elif conflict_status == "fragile":
        conflict_adj = 200

    # Special case: IRN under active US-Israel bombardment
    if code == "IRN":
        conflict_adj = 3500  # Extreme — active war, leader killed, Hormuz closed

    # Special case: USA — war with Iran, SCOTUS constitutional crisis, tariff turmoil
    if code == "USA":
        conflict_adj = 75  # War abroad + domestic political turmoil (not existential)

    # Sanctions adjustment
    sanctions_adj = 0
    is_sanctioned = get_bool_val(data,
        "institutions.under_international_sanctions",
        "layers.institutions.under_international_sanctions")
    if is_sanctioned or code in SANCTIONED_COUNTRIES:
        sanctions_adj = 300
        if code == "IRN":
            sanctions_adj = 500  # comprehensive
        elif code == "RUS":
            sanctions_adj = 400

    # Fragile states index adjustment
    fsi = get_val(data,
        "institutions.fragile_states_index",
        "layers.institutions.fragile_states_index")
    fsi_adj = 0
    if fsi is not None:
        if fsi > 90:
            fsi_adj = 200
        elif fsi > 80:
            fsi_adj = 100
        elif fsi > 70:
            fsi_adj = 50

    total = base_spread + gov_adj + dem_adj + conflict_adj + sanctions_adj + fsi_adj

    # Floor at 0, reasonable cap at 8000
    return round(clamp(total, 0, 8000))


def compute_market_accessibility(code, data):
    """Compute Market Accessibility Score (0.0-1.0)."""
    if code in MARKET_ACCESS_OVERRIDES:
        base = MARKET_ACCESS_OVERRIDES[code]
    else:
        base = 0.35  # default

    # Adjust based on sanctions
    is_sanctioned = get_bool_val(data,
        "institutions.under_international_sanctions",
        "layers.institutions.under_international_sanctions")
    if is_sanctioned or code in SANCTIONED_COUNTRIES:
        base = min(base, 0.20)

    # Active war further reduces
    if ACTIVE_CONFLICT.get(code) in ("active_war", "civil_war"):
        base = min(base, 0.15)

    return round(clamp(base, 0.0, 1.0), 3)


def compute_investment_risk(code, data, political_risk_bps, chokepoint_exposure):
    """
    Compute Overall Investment Risk Score (0.0-1.0, lower = less risk).
    = 0.30*political + 0.30*economic + 0.20*financial + 0.20*security
    """
    # Political risk component (0-1)
    # Map political_risk_premium_bps to 0-1 scale
    # 0 bps = 0.0, 5000+ bps = 1.0
    political = clamp(political_risk_bps / 5000.0, 0.0, 1.0)

    # Economic risk component
    inflation = get_val(data, "macroeconomic.inflation_cpi_pct",
                        "layers.economy.inflation_cpi_pct")
    debt_gdp = get_val(data, "macroeconomic.govt_debt_pct_gdp",
                        "layers.economy.govt_debt_pct_gdp")
    ca_gdp = get_val(data, "macroeconomic.current_account_pct_gdp",
                      "layers.economy.current_account_pct_gdp")

    econ_risk = 0.0
    econ_count = 0

    if inflation is not None:
        # High inflation = high risk. >20% = 1.0, <2% = 0.0
        econ_risk += clamp(inflation / 20.0, 0.0, 1.0)
        econ_count += 1

    if debt_gdp is not None:
        # High debt = risk. >120% = 1.0, <30% = 0.0
        econ_risk += clamp((debt_gdp - 30) / 90.0, 0.0, 1.0)
        econ_count += 1

    if ca_gdp is not None:
        # Large deficit = risk. < -8% = 1.0, > 5% surplus = 0.0
        econ_risk += clamp((-ca_gdp - 2) / 6.0, 0.0, 1.0)
        econ_count += 1

    if econ_count > 0:
        economic = econ_risk / econ_count
    else:
        economic = 0.5  # unknown = moderate

    # Financial market risk component
    fin_risk = 0.0
    fin_count = 0

    # Capital controls / market accessibility (inverse)
    mkt_access = MARKET_ACCESS_OVERRIDES.get(code, 0.35)
    fin_risk += (1.0 - mkt_access)
    fin_count += 1

    # Central bank rate as proxy for FX pressure
    cb_rate = get_val(data, "macroeconomic.central_bank_policy_rate_pct",
                       "layers.economy.central_bank_policy_rate_pct")
    if cb_rate is not None:
        fin_risk += clamp(cb_rate / 25.0, 0.0, 1.0)
        fin_count += 1

    if fin_count > 0:
        financial = fin_risk / fin_count
    else:
        financial = 0.5

    # Security risk component
    conflict_status = ACTIVE_CONFLICT.get(code)
    if conflict_status == "active_war":
        security = 1.0
    elif conflict_status == "civil_war":
        security = 0.9
    elif conflict_status == "active_conflict":
        security = 0.7
    elif conflict_status == "insurgency":
        security = 0.5
    elif conflict_status == "terrorism":
        security = 0.4
    elif conflict_status == "post_conflict":
        security = 0.35
    elif conflict_status == "fragile":
        security = 0.5
    else:
        # Use WGI political stability
        pol_stab = get_val(data,
            "institutions.wgi_political_stability",
            "layers.institutions.wgi_political_stability")
        if pol_stab is not None:
            # WGI PS range: -2.5 to +2.5. Map to 0-1 (inverted)
            security = clamp((1.0 - pol_stab) / 3.0, 0.0, 1.0)
        else:
            security = 0.3

    # Chokepoint exposure adds to security risk
    security = min(1.0, security + chokepoint_exposure * 0.1)

    # Weighted composite
    risk = (0.30 * political + 0.30 * economic +
            0.20 * financial + 0.20 * security)

    return round(clamp(risk, 0.0, 1.0), 3)


# ─── Main pipeline ──────────────────────────────────────────────────────────

def main():
    global RUN_ID, TIMESTAMP
    parser = argparse.ArgumentParser(description="Agent 11 — Derived Metrics Calculator")
    parser.add_argument("--run-id", help="Run ID (e.g. 2026-W11). Default: auto from date.")
    parser.add_argument("--timestamp", help="Timestamp (ISO 8601). Default: now.")
    args = parser.parse_args()
    if args.run_id:
        RUN_ID = args.run_id
    if args.timestamp:
        TIMESTAMP = args.timestamp

    print(f"Agent 11 — Derived Metrics Calculator")
    print(f"Run ID: {RUN_ID} | Timestamp: {TIMESTAMP}")
    print(f"{'='*60}")

    # Load country list
    with open(COUNTRY_LIST) as f:
        country_list = json.load(f)

    all_codes = []
    for tier_key in ["tier_1", "tier_2", "tier_3"]:
        for c in country_list["tiers"][tier_key]["countries"]:
            all_codes.append(c["code"])

    print(f"Processing {len(all_codes)} countries...")

    # Load all country data
    all_data = {}
    for code in all_codes:
        fpath = os.path.join(COUNTRIES_DIR, f"{code}.json")
        if not os.path.exists(fpath):
            print(f"  WARNING: {code}.json not found, skipping")
            continue
        with open(fpath) as f:
            all_data[code] = json.load(f)

    print(f"Loaded {len(all_data)} country files.")

    # ── Phase 1: Compute per-country metrics ─────────────────────────────

    # Collect CNPI raw values first (need all countries for normalization)
    cnpi_raw = {}
    for code, data in all_data.items():
        cnpi_raw[code] = compute_composite_national_power(code, data, all_data)

    cnpi_scores = finalize_cnpi(cnpi_raw, cnpi_raw)

    results = {}
    for code, data in all_data.items():
        energy_idx = compute_energy_independence(code, data)
        resource_idx = compute_resource_self_sufficiency(code, data)
        chokepoint = compute_chokepoint_exposure(code, data)
        cnpi = cnpi_scores.get(code, 30.0)
        risk_premium = compute_political_risk_premium(code, data)
        market_access = compute_market_accessibility(code, data)
        inv_risk = compute_investment_risk(code, data, risk_premium, chokepoint)

        # Get previous values for change tracking
        prev_derived = data.get("derived", {})
        prev_cnpi = get_val(data, "derived.composite_national_power_index")
        if isinstance(prev_cnpi, dict) and "value" in prev_cnpi:
            prev_cnpi = prev_cnpi["value"]
        prev_risk = get_val(data, "derived.political_risk_premium_bps")
        if isinstance(prev_risk, dict) and "value" in prev_risk:
            prev_risk = prev_risk["value"]

        derived = {
            "resource_self_sufficiency_index": {
                "value": round(resource_idx, 3),
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "Average of min(production/consumption, 1.0) for energy, food, water, minerals"
            },
            "energy_independence_index": {
                "value": round(energy_idx, 3),
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "domestic_energy_production / domestic_energy_consumption, capped at 1.0"
            },
            "supply_chain_chokepoint_exposure": {
                "value": round(chokepoint, 3),
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "0.6 * maritime_chokepoint_dependency + 0.4 * normalized_trade_openness; elevated due to active Hormuz/Suez disruption"
            },
            "composite_national_power_index": {
                "value": cnpi,
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "0.35*economic + 0.25*military + 0.20*technology + 0.10*diplomatic + 0.10*soft_power, normalized 0-100"
            },
            "political_risk_premium_bps": {
                "value": risk_premium,
                "confidence": 0.75,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "Sovereign rating implied spread + adjustments for instability, conflict, sanctions, autocracy"
            },
            "market_accessibility_score": {
                "value": round(market_access, 3),
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "Average of capital_account_openness, stock_market_cap/200, financial_dev_index, ease_of_business/100"
            },
            "overall_investment_risk_score": {
                "value": round(inv_risk, 3),
                "confidence": 0.7,
                "last_updated": TIMESTAMP,
                "source": "agent_11_derived",
                "run_id": RUN_ID,
                "methodology": "0.30*political_risk + 0.30*economic_risk + 0.20*financial_market_risk + 0.20*security_risk"
            }
        }

        # Add change notes for significant moves
        if prev_cnpi is not None and abs(cnpi - prev_cnpi) > 2:
            derived["composite_national_power_index"]["previous_value"] = prev_cnpi
        if prev_risk is not None and abs(risk_premium - prev_risk) > 50:
            derived["political_risk_premium_bps"]["previous_value"] = prev_risk

        results[code] = derived

    # ── Phase 2: Write back to country files ─────────────────────────────

    # Keys that Agent 10 (Trend Estimator) writes into derived — preserve them
    AGENT10_TREND_KEYS = {
        "political_stability_trend", "trade_openness_trend",
        "exchange_rate_vs_usd", "top_partner_relationship_health",
    }
    # Also preserve trend sub-fields on overall_investment_risk_score
    INVESTMENT_RISK_TREND_FIELDS = {"trend", "trend_confidence", "trend_reasoning", "trend_updated"}

    print(f"\nWriting derived metrics to country files...")
    for code, derived in results.items():
        fpath = os.path.join(COUNTRIES_DIR, f"{code}.json")
        data = all_data[code]

        # Preserve Agent 10 trend entries from existing derived section
        old_derived = data.get("derived", {})
        for tk in AGENT10_TREND_KEYS:
            if tk in old_derived:
                derived[tk] = old_derived[tk]

        # Preserve trend sub-fields on overall_investment_risk_score
        old_inv_risk = old_derived.get("overall_investment_risk_score", {})
        if isinstance(old_inv_risk, dict):
            for tf in INVESTMENT_RISK_TREND_FIELDS:
                if tf in old_inv_risk and tf not in derived["overall_investment_risk_score"]:
                    derived["overall_investment_risk_score"][tf] = old_inv_risk[tf]

        # Update top-level derived section
        data["derived"] = derived

        # Also update layers.derived with plain values
        if "layers" in data:
            data["layers"]["derived"] = {
                "resource_self_sufficiency_index": derived["resource_self_sufficiency_index"]["value"],
                "energy_independence_index": derived["energy_independence_index"]["value"],
                "supply_chain_chokepoint_exposure": derived["supply_chain_chokepoint_exposure"]["value"],
                "composite_national_power_index": derived["composite_national_power_index"]["value"],
                "political_risk_premium_bps": derived["political_risk_premium_bps"]["value"],
                "market_accessibility_score": derived["market_accessibility_score"]["value"],
                "overall_investment_risk_score": derived["overall_investment_risk_score"]["value"],
            }

        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Updated {len(results)} country files.")

    # ── Phase 3: Generate global rankings ────────────────────────────────

    print(f"\nGenerating global rankings...")

    rankings = {}

    # Helper to build sorted ranking
    def build_ranking(metric_key, reverse=True):
        """Build sorted ranking. reverse=True means highest value = rank 1."""
        entries = []
        for code, derived in results.items():
            val = derived[metric_key]["value"]
            if val is not None:
                entries.append({"country_code": code, "value": val})
        entries.sort(key=lambda x: x["value"], reverse=reverse)
        ranked = []
        for i, e in enumerate(entries, 1):
            ranked.append({
                "rank": i,
                "country_code": e["country_code"],
                "value": e["value"]
            })
        return ranked

    # CNPI: highest = best
    rankings["composite_national_power_index"] = build_ranking(
        "composite_national_power_index", reverse=True)

    # Investment risk: lowest = best (rank 1 = lowest risk)
    rankings["overall_investment_risk_score"] = build_ranking(
        "overall_investment_risk_score", reverse=False)

    # Market accessibility: highest = best
    rankings["market_accessibility_score"] = build_ranking(
        "market_accessibility_score", reverse=True)

    # Political risk premium: lowest = best
    rankings["political_risk_premium_bps"] = build_ranking(
        "political_risk_premium_bps", reverse=False)

    # Energy independence: highest = best
    rankings["energy_independence_index"] = build_ranking(
        "energy_independence_index", reverse=True)

    # Resource self-sufficiency: highest = best
    rankings["resource_self_sufficiency_index"] = build_ranking(
        "resource_self_sufficiency_index", reverse=True)

    # Supply chain chokepoint: lowest = best (less exposed)
    rankings["supply_chain_chokepoint_exposure"] = build_ranking(
        "supply_chain_chokepoint_exposure", reverse=False)

    rankings_output = {
        "generated_at": TIMESTAMP,
        "run_id": RUN_ID,
        "rankings": rankings
    }

    with open(RANKINGS_OUT, "w") as f:
        json.dump(rankings_output, f, indent=2, ensure_ascii=False)

    print(f"  Wrote global_rankings.json with {len(rankings)} ranking categories.")

    # ── Phase 4: Summary report ──────────────────────────────────────────

    print(f"\n{'='*60}")
    print(f"AGENT 11 RESULTS SUMMARY")
    print(f"{'='*60}")

    print(f"\n--- Top 10 Composite National Power ---")
    for r in rankings["composite_national_power_index"][:10]:
        print(f"  {r['rank']:2d}. {r['country_code']}  {r['value']:6.1f}")

    print(f"\n--- Top 10 Lowest Investment Risk ---")
    for r in rankings["overall_investment_risk_score"][:10]:
        print(f"  {r['rank']:2d}. {r['country_code']}  {r['value']:.3f}")

    print(f"\n--- Top 10 Highest Political Risk Premium ---")
    for r in rankings["political_risk_premium_bps"][-10:][::-1]:
        print(f"  {75 - rankings['political_risk_premium_bps'].index(r):2d}. {r['country_code']}  {r['value']:,d} bps")

    print(f"\n--- Top 10 Highest Chokepoint Exposure ---")
    for r in rankings["supply_chain_chokepoint_exposure"][-10:][::-1]:
        print(f"      {r['country_code']}  {r['value']:.3f}")

    print(f"\n--- Top 10 Market Accessibility ---")
    for r in rankings["market_accessibility_score"][:10]:
        print(f"  {r['rank']:2d}. {r['country_code']}  {r['value']:.3f}")

    print(f"\n--- Top 10 Energy Independence ---")
    for r in rankings["energy_independence_index"][:10]:
        print(f"  {r['rank']:2d}. {r['country_code']}  {r['value']:.3f}")

    print(f"\nAgent 11 complete. {len(results)} countries processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
