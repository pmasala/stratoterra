#!/usr/bin/env python3
"""
Update country JSON files with trend estimates from Agent 10, 2026-W11.
Maps trend factors to the correct paths in country JSON files.
"""

import json
import os

BASE = "/home/pietro/stratoterra"
TRENDS_FILE = f"{BASE}/staging/trends/trend_estimates_2026-03-10.json"
DATA_DIR = f"{BASE}/data/countries"

with open(TRENDS_FILE) as f:
    trends = json.load(f)

# Map factor names to JSON paths
FACTOR_MAP = {
    "gdp_real_growth_pct": ("macroeconomic", "gdp_real_growth_pct"),
    "inflation_cpi_pct": ("macroeconomic", "inflation_cpi_pct"),
    "current_account_pct_gdp": ("macroeconomic", "current_account_pct_gdp"),
    "govt_debt_pct_gdp": ("macroeconomic", "govt_debt_pct_gdp"),
    "military_expenditure_pct_gdp": ("military", "military_expenditure_pct_gdp"),
    "trade_openness_pct": ("macroeconomic", "trade_openness_pct"),
    "fdi_net_inflows_usd": ("macroeconomic", "fdi_inflows_usd"),
    "exchange_rate_vs_usd": ("macroeconomic", "exchange_rate_vs_usd"),
    "overall_investment_risk_score": ("derived", "overall_investment_risk_score"),
    "political_stability": ("derived", "political_stability_trend"),
    "top_partner_relationship_health": ("derived", "top_partner_relationship_health"),
}

# Alternate field names to try
ALT_FIELDS = {
    ("macroeconomic", "inflation_cpi_pct"): [("macroeconomic", "inflation_rate_cpi_pct")],
    ("macroeconomic", "gdp_real_growth_pct"): [("macroeconomic", "gdp_growth_pct")],
    ("macroeconomic", "govt_debt_pct_gdp"): [("macroeconomic", "public_debt_pct_gdp")],
    ("macroeconomic", "fdi_inflows_usd"): [("macroeconomic", "fdi_net_inflows_usd")],
    ("military", "military_expenditure_pct_gdp"): [("military", "military_spending_pct_gdp")],
}

updated_count = 0
country_count = 0
skipped = []

# Group estimates by country
from collections import defaultdict
by_country = defaultdict(list)
for est in trends["estimates"]:
    by_country[est["country_code"]].append(est)

for code, ests in sorted(by_country.items()):
    fpath = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(fpath):
        skipped.append(code)
        continue

    with open(fpath) as f:
        cdata = json.load(f)

    country_updated = False

    for est in ests:
        factor = est["factor"]
        if factor not in FACTOR_MAP:
            continue

        section, key = FACTOR_MAP[factor]

        # Find the right section/key - try primary then alternates
        target_section = section
        target_key = key

        # Check if the primary path exists
        if section not in cdata:
            cdata[section] = {}

        # For factors that map to existing fields, update in-place
        found = False
        if section in cdata and key in cdata[section]:
            found = True
        else:
            # Try alternate field names
            for alt_section, alt_key in ALT_FIELDS.get((section, key), []):
                if alt_section in cdata and alt_key in cdata[alt_section]:
                    target_section = alt_section
                    target_key = alt_key
                    found = True
                    break

        if found and isinstance(cdata[target_section][target_key], dict) and "value" in cdata[target_section][target_key]:
            # Update existing field with trend data
            cdata[target_section][target_key]["trend"] = est["trend"]
            cdata[target_section][target_key]["trend_confidence"] = est["confidence"]
            cdata[target_section][target_key]["trend_reasoning"] = est["reasoning"]
            cdata[target_section][target_key]["trend_updated"] = "2026-03-10T12:00:00Z"
            updated_count += 1
            country_updated = True
        elif factor in ("political_stability", "top_partner_relationship_health", "overall_investment_risk_score",
                        "exchange_rate_vs_usd", "trade_openness_pct"):
            # For derived/synthetic factors, create/update in derived section
            if "derived" not in cdata:
                cdata["derived"] = {}

            field_name = factor + "_trend" if factor in ("political_stability",) else factor
            if factor == "trade_openness_pct":
                field_name = "trade_openness_trend"

            cdata["derived"][field_name] = {
                "value": est["trend"],
                "confidence": est["confidence"],
                "reasoning": est["reasoning"],
                "last_updated": "2026-03-10T12:00:00Z",
                "source": "agent_10_trend_estimator",
                "run_id": "2026-W11"
            }
            updated_count += 1
            country_updated = True
        else:
            # Field doesn't exist yet as a structured object; create it
            if target_section not in cdata:
                cdata[target_section] = {}
            cdata[target_section][target_key] = {
                "value": est["current_value"],
                "trend": est["trend"],
                "trend_confidence": est["confidence"],
                "trend_reasoning": est["reasoning"],
                "trend_updated": "2026-03-10T12:00:00Z",
                "confidence": est["confidence"],
                "last_updated": "2026-03-10T12:00:00Z",
                "source": "agent_10_trend_estimator",
                "run_id": "2026-W11"
            }
            updated_count += 1
            country_updated = True

    if country_updated:
        country_count += 1
        with open(fpath, "w") as f:
            json.dump(cdata, f, indent=2)

print(f"Updated {updated_count} trend fields across {country_count} country files")
if skipped:
    print(f"Skipped (no JSON file): {skipped}")
