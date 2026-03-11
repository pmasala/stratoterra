#!/usr/bin/env python3
"""
Agent 08 — Cross-Validator & Anomaly Detector
Validates factor updates from Agent 07 before integration into /data.
Run ID: 2026-W11 | Date: 2026-03-10
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter

# ── Configuration ──────────────────────────────────────────────────────────

BASE_DIR = "/home/pietro/stratoterra"
INPUT_FILE = f"{BASE_DIR}/staging/processed/factor_updates_2026-03-10.json"
COUNTRY_DIR = f"{BASE_DIR}/data/countries"
OUTPUT_FILE = f"{BASE_DIR}/staging/validated/validated_updates_2026-03-10.json"
ESCALATION_FILE = f"{BASE_DIR}/staging/validated/escalation_report_2026-03-10.json"

# ── Plausibility ranges per factor path ────────────────────────────────────

PLAUSIBILITY_RANGES = {
    # Macroeconomic
    "economy.macroeconomic.gdp_nominal_usd": (1e8, 40e12),           # $100M to $40T
    "economy.macroeconomic.gdp_per_capita_usd": (200, 150_000),
    "economy.macroeconomic.gdp_ppp_usd": (1e9, 40e12),
    "economy.macroeconomic.gdp_real_growth_rate_pct": (-30, 30),
    "economy.macroeconomic.inflation_rate_cpi_pct": (-10, 1000),
    "economy.macroeconomic.unemployment_rate_pct": (0, 60),
    "economy.macroeconomic.current_account_balance_pct_gdp": (-40, 40),
    "economy.macroeconomic.fiscal_balance_pct_gdp": (-40, 40),
    "economy.macroeconomic.public_debt_pct_gdp": (0, 300),
    "economy.macroeconomic.foreign_exchange_reserves_usd": (0, 10e12),
    "economy.macroeconomic.total_exports_usd": (0, 5e12),
    "economy.macroeconomic.total_imports_usd": (0, 5e12),
    "economy.macroeconomic.fdi_inflows_usd": (-200e9, 600e9),
    "economy.macroeconomic.gini_coefficient": (20, 70),

    # Central bank & markets
    "macroeconomic.central_bank_policy_rate_pct": (-2, 100),
    "macroeconomic.sovereign_bond_yield_10yr_pct": (-2, 50),
    "macroeconomic.equity_index": (10, 200_000),
    "macroeconomic.exchange_rate_vs_usd": (0.0001, 5_000_000),  # Iranian rial ~964K/USD

    # Demographics
    "endowments.demographics.population_total": (50_000, 2e9),
    "endowments.demographics.population_growth_rate_pct": (-5, 10),
    "endowments.demographics.life_expectancy_years": (40, 95),
    "endowments.demographics.urban_population_pct": (5, 100),
    "endowments.demographics.labor_force_participation_pct": (20, 95),
    "endowments.demographics.health_expenditure_pct_gdp": (1, 25),
    "endowments.demographics.literacy_rate_pct": (10, 100),

    # Capability
    "economy.capability.electricity_access_pct": (0, 100),
    "economy.capability.internet_users_pct": (0, 100),

    # WGI scores — range [-2.5, 2.5]
    "institutions.wgi_voice_accountability": (-2.5, 2.5),
    "institutions.wgi_political_stability": (-2.5, 2.5),
    "institutions.wgi_government_effectiveness": (-2.5, 2.5),
    "institutions.wgi_regulatory_quality": (-2.5, 2.5),
    "institutions.wgi_rule_of_law": (-2.5, 2.5),
    "institutions.wgi_control_of_corruption": (-2.5, 2.5),
    "institutions.political.wgi_voice_accountability": (-2.5, 2.5),
    "institutions.political.wgi_political_stability": (-2.5, 2.5),
    "institutions.political.wgi_government_effectiveness": (-2.5, 2.5),
    "institutions.political.wgi_regulatory_quality": (-2.5, 2.5),
    "institutions.political.wgi_rule_of_law": (-2.5, 2.5),
    "institutions.political.wgi_control_of_corruption": (-2.5, 2.5),

    # Commodities (USD)
    "commodity.brent_crude": (5, 300),
    "commodity.wti_crude": (5, 300),
    "commodity.natural_gas_henry_hub": (0.5, 30),
    "commodity.gold": (500, 10_000),
    "commodity.silver": (5, 200),
    "commodity.copper": (1, 20),
    "commodity.iron_ore": (20, 400),
    "commodity.lithium_carbonate": (1, 100),
    "commodity.wheat": (100, 1500),
    "commodity.corn": (80, 1000),
    "commodity.soybeans": (100, 2000),
}

# Typical weekly change magnitudes (used for 3× anomaly detection)
TYPICAL_WEEKLY_CHANGE = {
    "economy.macroeconomic.gdp_nominal_usd": 0.02,             # ~2% max normal
    "economy.macroeconomic.gdp_per_capita_usd": 0.02,
    "economy.macroeconomic.gdp_ppp_usd": 0.02,
    "economy.macroeconomic.gdp_real_growth_rate_pct": 0.5,     # absolute pp
    "economy.macroeconomic.inflation_rate_cpi_pct": 0.5,
    "economy.macroeconomic.unemployment_rate_pct": 0.3,
    "economy.macroeconomic.current_account_balance_pct_gdp": 1.0,
    "economy.macroeconomic.fiscal_balance_pct_gdp": 1.0,
    "economy.macroeconomic.public_debt_pct_gdp": 2.0,
    "economy.macroeconomic.foreign_exchange_reserves_usd": 0.05,
    "economy.macroeconomic.total_exports_usd": 0.05,
    "economy.macroeconomic.total_imports_usd": 0.05,
    "economy.macroeconomic.fdi_inflows_usd": 0.5,
    "economy.macroeconomic.gini_coefficient": 1.0,
    "macroeconomic.central_bank_policy_rate_pct": 0.5,         # absolute pp
    "macroeconomic.sovereign_bond_yield_10yr_pct": 0.5,
    "macroeconomic.equity_index": 0.05,                        # 5%
    "macroeconomic.exchange_rate_vs_usd": 0.05,                # 5%
    "endowments.demographics.population_total": 0.005,
    "endowments.demographics.population_growth_rate_pct": 0.1,
    "endowments.demographics.life_expectancy_years": 0.5,
    "endowments.demographics.urban_population_pct": 0.5,
    "endowments.demographics.labor_force_participation_pct": 0.5,
    "endowments.demographics.health_expenditure_pct_gdp": 0.5,
    "endowments.demographics.literacy_rate_pct": 1.0,
    "economy.capability.electricity_access_pct": 1.0,
    "economy.capability.internet_users_pct": 1.0,
    "commodity.brent_crude": 0.10,
    "commodity.wti_crude": 0.10,
    "commodity.natural_gas_henry_hub": 0.10,
    "commodity.gold": 0.05,
    "commodity.silver": 0.08,
    "commodity.copper": 0.06,
    "commodity.iron_ore": 0.08,
    "commodity.lithium_carbonate": 0.10,
    "commodity.wheat": 0.06,
    "commodity.corn": 0.06,
    "commodity.soybeans": 0.06,
}

# Factors that use absolute change (pp) rather than % change for magnitude check
ABSOLUTE_CHANGE_FACTORS = {
    "economy.macroeconomic.gdp_real_growth_rate_pct",
    "economy.macroeconomic.inflation_rate_cpi_pct",
    "economy.macroeconomic.unemployment_rate_pct",
    "economy.macroeconomic.current_account_balance_pct_gdp",
    "economy.macroeconomic.fiscal_balance_pct_gdp",
    "economy.macroeconomic.public_debt_pct_gdp",
    "economy.macroeconomic.gini_coefficient",
    "macroeconomic.central_bank_policy_rate_pct",
    "macroeconomic.sovereign_bond_yield_10yr_pct",
    "endowments.demographics.life_expectancy_years",
    "endowments.demographics.urban_population_pct",
    "endowments.demographics.labor_force_participation_pct",
    "endowments.demographics.health_expenditure_pct_gdp",
    "endowments.demographics.population_growth_rate_pct",
    "endowments.demographics.literacy_rate_pct",
    "economy.capability.electricity_access_pct",
    "economy.capability.internet_users_pct",
}

# WGI factors also use absolute change
for wgi_path in [p for p in PLAUSIBILITY_RANGES if "wgi_" in p]:
    ABSOLUTE_CHANGE_FACTORS.add(wgi_path)
    TYPICAL_WEEKLY_CHANGE[wgi_path] = 0.15  # WGI changes are small

# High-impact escalation triggers
ESCALATION_FACTOR_KEYWORDS = [
    "sovereign_credit_rating",
    "head_of_state",
    "nuclear",
    "under_international_sanctions",
]

# ── Mapping from update factor_path to country JSON field ──────────────────

FACTOR_PATH_TO_COUNTRY_FIELD = {
    "economy.macroeconomic.gdp_nominal_usd": ("macroeconomic", "gdp_nominal_usd"),
    "economy.macroeconomic.gdp_per_capita_usd": ("macroeconomic", "gdp_per_capita_usd"),
    "economy.macroeconomic.gdp_ppp_usd": None,  # not always present
    "economy.macroeconomic.gdp_real_growth_rate_pct": ("macroeconomic", "gdp_real_growth_pct"),
    "economy.macroeconomic.inflation_rate_cpi_pct": ("macroeconomic", "inflation_cpi_pct"),
    "economy.macroeconomic.unemployment_rate_pct": ("macroeconomic", "unemployment_rate_pct"),
    "economy.macroeconomic.current_account_balance_pct_gdp": ("macroeconomic", "current_account_pct_gdp"),
    "economy.macroeconomic.fiscal_balance_pct_gdp": None,  # not always present
    "economy.macroeconomic.public_debt_pct_gdp": ("macroeconomic", "govt_debt_pct_gdp"),
    "economy.macroeconomic.foreign_exchange_reserves_usd": ("macroeconomic", "fx_reserves_usd"),
    "economy.macroeconomic.total_exports_usd": ("macroeconomic", "total_exports_usd"),
    "economy.macroeconomic.total_imports_usd": ("macroeconomic", "total_imports_usd"),
    "economy.macroeconomic.fdi_inflows_usd": None,
    "economy.macroeconomic.gini_coefficient": None,
    "macroeconomic.central_bank_policy_rate_pct": ("macroeconomic", "central_bank_policy_rate_pct"),
    "macroeconomic.sovereign_bond_yield_10yr_pct": ("macroeconomic", "sovereign_bond_yield_10yr_pct"),
    "macroeconomic.equity_index": ("macroeconomic", "equity_index_level"),
    "macroeconomic.exchange_rate_vs_usd": None,  # country code mismatch (EUR etc.)
    "endowments.demographics.population_total": ("demographic", "population_total"),
    "endowments.demographics.population_growth_rate_pct": ("demographic", "population_growth_pct"),
    "endowments.demographics.life_expectancy_years": ("demographic", "life_expectancy"),
    "endowments.demographics.urban_population_pct": None,
    "endowments.demographics.labor_force_participation_pct": None,
    "endowments.demographics.health_expenditure_pct_gdp": None,
    "endowments.demographics.literacy_rate_pct": None,
    "economy.capability.electricity_access_pct": None,
    "economy.capability.internet_users_pct": None,
}

# WGI fields map to institutions section
for wgi in ["voice_accountability", "political_stability", "government_effectiveness",
            "regulatory_quality", "rule_of_law", "control_of_corruption"]:
    FACTOR_PATH_TO_COUNTRY_FIELD[f"institutions.wgi_{wgi}"] = ("institutions", f"wgi_{wgi}")
    FACTOR_PATH_TO_COUNTRY_FIELD[f"institutions.political.wgi_{wgi}"] = ("institutions", f"wgi_{wgi}")


def load_country_data():
    """Load all country JSON files into a dict keyed by ISO3."""
    countries = {}
    for fname in os.listdir(COUNTRY_DIR):
        if not fname.endswith(".json"):
            continue
        iso3 = fname.replace(".json", "")
        try:
            with open(os.path.join(COUNTRY_DIR, fname)) as f:
                countries[iso3] = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  WARNING: Could not load {fname}: {e}", file=sys.stderr)
    return countries


def get_current_value(country_data, factor_path, country_code):
    """Look up the current value for a factor in the country data.
    Returns (value, found) tuple."""

    # Check the explicit mapping first
    mapping = FACTOR_PATH_TO_COUNTRY_FIELD.get(factor_path)
    if mapping is None:
        # Try to navigate the factor_path as nested keys in the country data
        # e.g., "economy.macroeconomic.gdp_ppp_usd" → layers.economy? or economy?
        parts = factor_path.split(".")
        # Try direct path in country data
        node = country_data
        for part in parts:
            if isinstance(node, dict):
                if part in node:
                    node = node[part]
                else:
                    return None, False
            else:
                return None, False
        if isinstance(node, dict) and "value" in node:
            return node["value"], True
        return node, True

    section, field = mapping
    if section not in country_data:
        return None, False
    sec = country_data[section]
    if field not in sec:
        return None, False
    entry = sec[field]
    if isinstance(entry, dict) and "value" in entry:
        return entry["value"], True
    return entry, True


def compute_change(old_val, new_val, factor_path):
    """Compute change between old and new value.
    Returns (change_pct, abs_change, change_type) where change_type is 'pct' or 'abs'."""

    if old_val is None or new_val is None:
        return None, None, None
    if not isinstance(old_val, (int, float)) or not isinstance(new_val, (int, float)):
        return None, None, None

    abs_change = new_val - old_val

    if factor_path in ABSOLUTE_CHANGE_FACTORS:
        return None, abs_change, "abs"

    # Percentage change
    if old_val == 0:
        if new_val == 0:
            return 0.0, 0.0, "pct"
        return None, abs_change, "abs"  # can't compute pct from zero base

    pct_change = ((new_val - old_val) / abs(old_val)) * 100
    return pct_change, abs_change, "pct"


def check_plausibility(new_val, factor_path):
    """Check if value falls within plausible range. Returns (passed, note)."""
    if not isinstance(new_val, (int, float)):
        return True, ""  # skip non-numeric values

    bounds = PLAUSIBILITY_RANGES.get(factor_path)
    if bounds is None:
        return True, ""  # no range defined, pass

    lo, hi = bounds
    if new_val < lo or new_val > hi:
        return False, f"Value {new_val} outside plausible range [{lo}, {hi}]"
    return True, ""


def check_magnitude(old_val, new_val, factor_path):
    """Check if change exceeds 3× typical weekly change. Returns (passed, is_anomalous, note)."""
    if old_val is None or new_val is None:
        return True, False, ""
    if not isinstance(old_val, (int, float)) or not isinstance(new_val, (int, float)):
        return True, False, ""

    typical = TYPICAL_WEEKLY_CHANGE.get(factor_path)
    if typical is None:
        return True, False, ""

    if factor_path in ABSOLUTE_CHANGE_FACTORS:
        actual_change = abs(new_val - old_val)
        threshold = 3 * typical
        if actual_change > threshold:
            return True, True, f"Absolute change {actual_change:.4f} exceeds 3× typical ({typical}) = {threshold}"
    else:
        if old_val == 0:
            return True, False, ""
        pct_change = abs((new_val - old_val) / old_val)
        threshold = 3 * typical
        if pct_change > threshold:
            return True, True, f"Change {pct_change*100:.1f}% exceeds 3× typical ({typical*100:.1f}%) = {threshold*100:.1f}%"

    return True, False, ""


def should_escalate(update, old_val, new_val, factor_path, confidence):
    """Determine if this update should be escalated for human/agent-17 review."""
    reasons = []

    # Low confidence
    if confidence is not None and confidence < 0.4:
        reasons.append(f"Low confidence ({confidence})")

    # High-impact factor keywords
    for kw in ESCALATION_FACTOR_KEYWORDS:
        if kw in factor_path:
            if old_val is not None and new_val != old_val:
                reasons.append(f"High-impact factor change: {factor_path}")
            break

    # GDP swing > 3 percentage points
    if factor_path == "economy.macroeconomic.gdp_real_growth_rate_pct":
        if old_val is not None and isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            if abs(new_val - old_val) > 3.0:
                reasons.append(f"GDP growth swing > 3pp: {old_val} → {new_val}")

    # Conflict status change — handled via event triggers, not factor updates

    return reasons


def validate_update(update, idx, country_data_map, event_country_codes):
    """Validate a single factor update. Returns validated record."""

    country_code = update.get("country_code", "")
    factor_path = update.get("factor_path", "")
    new_val = update.get("new_value")
    confidence = update.get("confidence")
    source_agent = update.get("agent_source", "")
    notes_in = update.get("notes", "")

    # Prepare result
    result = {
        "update_id": f"upd_{idx:04d}",
        "country_code": country_code,
        "factor_path": factor_path,
        "new_value": new_val,
        "previous_value": None,
        "change_pct": None,
        "confidence": confidence,
        "source_agent": source_agent,
        "checks_passed": [],
        "checks_failed": [],
        "notes": "",
        "verdict": "ACCEPT",
    }

    all_notes = []

    # Skip non-numeric / dict / complex values — accept with note
    if isinstance(new_val, (dict, list)):
        result["verdict"] = "ACCEPT_WITH_NOTE"
        result["notes"] = "Complex (dict/list) value — plausibility check skipped"
        result["checks_passed"] = ["type_complex"]
        return result

    # Skip GLOBAL and non-country codes for country lookup
    is_country = country_code not in ("GLOBAL", "EUR", "HKG") and country_code in country_data_map
    old_val = None
    found = False

    if is_country:
        cdata = country_data_map[country_code]
        old_val, found = get_current_value(cdata, factor_path, country_code)
        result["previous_value"] = old_val

    # ── Check 1: Plausibility ──
    plaus_ok, plaus_note = check_plausibility(new_val, factor_path)
    if plaus_ok:
        result["checks_passed"].append("plausibility")
    else:
        result["checks_failed"].append("plausibility")
        all_notes.append(plaus_note)

    # ── Check 2: Magnitude ──
    if found and old_val is not None:
        mag_ok, is_anomalous, mag_note = check_magnitude(old_val, new_val, factor_path)
        if not is_anomalous:
            result["checks_passed"].append("magnitude")
        else:
            result["checks_passed"].append("magnitude_anomalous")
            all_notes.append(mag_note)
    else:
        result["checks_passed"].append("magnitude_no_baseline")

    # ── Check 3: Compute change_pct ──
    if found and old_val is not None and isinstance(new_val, (int, float)) and isinstance(old_val, (int, float)):
        pct_change, abs_change, change_type = compute_change(old_val, new_val, factor_path)
        if change_type == "pct" and pct_change is not None:
            result["change_pct"] = round(pct_change, 4)
        elif change_type == "abs" and abs_change is not None:
            result["change_pct"] = round(abs_change, 4)  # For absolute factors, store the pp change

    # ── Check 4: Consistency (alternative source & cross-check) ──
    consistency_checked = False

    # 4a. Check alternative_sources if present
    alt_sources = update.get("alternative_sources", [])
    if alt_sources and isinstance(new_val, (int, float)):
        for alt in alt_sources:
            alt_val = alt.get("value")
            if alt_val is not None and isinstance(alt_val, (int, float)) and alt_val != 0:
                disagree_pct = abs(new_val - alt_val) / abs(alt_val) * 100
                if disagree_pct > 20:
                    result["checks_passed"].append("consistency_alt_disagree")
                    all_notes.append(
                        f"Alternative source ({alt.get('source','?')}) disagrees: "
                        f"{alt_val} vs primary {new_val} ({disagree_pct:.1f}% diff)"
                    )
                    consistency_checked = True
                    break
        if not consistency_checked:
            result["checks_passed"].append("consistency_alt_agree")
            consistency_checked = True

    # 4b. Check weekly_change_pct from source vs our computed change
    if not consistency_checked:
        weekly_change = update.get("weekly_change_pct")
        if weekly_change is not None and result["change_pct"] is not None:
            if abs(result["change_pct"]) > 0 and abs(weekly_change) > 0:
                ratio = abs(result["change_pct"]) / abs(weekly_change) if weekly_change != 0 else float('inf')
                if 0.5 < ratio < 2.0:
                    result["checks_passed"].append("consistency")
                else:
                    result["checks_passed"].append("consistency_minor_discrepancy")
                    all_notes.append(f"Weekly change from source ({weekly_change}%) vs computed ({result['change_pct']:.2f}%)")
            else:
                result["checks_passed"].append("consistency")
            consistency_checked = True

    if not consistency_checked:
        result["checks_passed"].append("consistency_no_alt")

    # ── Determine verdict ──

    # REJECT: fails plausibility
    if "plausibility" in result["checks_failed"]:
        result["verdict"] = "REJECT"
        result["notes"] = "; ".join(all_notes)
        return result

    # ESCALATE checks
    escalation_reasons = should_escalate(update, old_val, new_val, factor_path, confidence)
    if escalation_reasons:
        result["verdict"] = "ESCALATE"
        all_notes.extend(escalation_reasons)
        result["notes"] = "; ".join(all_notes)
        return result

    # FLAG: anomalous magnitude but plausible (especially if event-driven)
    if "magnitude_anomalous" in result["checks_passed"]:
        # If the country is involved in known events, flag instead of escalate
        if country_code in event_country_codes:
            result["verdict"] = "FLAG"
            all_notes.append(f"Event context: {country_code} has active event triggers")
        else:
            result["verdict"] = "FLAG"
        result["notes"] = "; ".join(all_notes)
        return result

    # ACCEPT_WITH_NOTE: minor concerns
    if all_notes:
        result["verdict"] = "ACCEPT_WITH_NOTE"
        result["notes"] = "; ".join(all_notes)
        return result

    # ACCEPT: all checks pass
    result["verdict"] = "ACCEPT"
    return result


def main():
    print("=" * 70)
    print("Agent 08 — Cross-Validator & Anomaly Detector")
    print(f"Run ID: 2026-W11 | Date: 2026-03-10")
    print("=" * 70)

    # ── Load input ──
    print("\n[1/5] Loading factor updates...")
    with open(INPUT_FILE) as f:
        input_data = json.load(f)

    factor_updates = input_data.get("factor_updates", [])
    event_signals = input_data.get("event_signals", [])
    event_triggers = input_data.get("event_triggers", [])
    print(f"  Loaded {len(factor_updates)} factor updates")
    print(f"  Loaded {len(event_signals)} event signals")
    print(f"  Loaded {len(event_triggers)} event triggers")

    # ── Load country data ──
    print("\n[2/5] Loading current country data...")
    country_data = load_country_data()
    print(f"  Loaded {len(country_data)} country files")

    # ── Build event-involved country set ──
    event_country_codes = set()
    for sig in event_signals:
        for cc in sig.get("countries_involved", []):
            event_country_codes.add(cc)
        pc = sig.get("primary_country")
        if pc:
            event_country_codes.add(pc)
    for trig in event_triggers:
        for cc in trig.get("affected_countries", []):
            event_country_codes.add(cc)
    print(f"  {len(event_country_codes)} countries have active events")

    # ── Validate each update ──
    print("\n[3/5] Validating factor updates...")
    validated = []
    verdict_counts = Counter()

    for idx, update in enumerate(factor_updates, start=1):
        result = validate_update(update, idx, country_data, event_country_codes)
        validated.append(result)
        verdict_counts[result["verdict"]] += 1

    # ── Build output ──
    print("\n[4/5] Writing output files...")
    summary = {
        "total": len(validated),
        "accept": verdict_counts.get("ACCEPT", 0),
        "accept_with_note": verdict_counts.get("ACCEPT_WITH_NOTE", 0),
        "flag": verdict_counts.get("FLAG", 0),
        "reject": verdict_counts.get("REJECT", 0),
        "escalate": verdict_counts.get("ESCALATE", 0),
    }

    output = {
        "validation_date": "2026-03-10",
        "run_id": "2026-W11",
        "validated_updates": validated,
        "event_signals": event_signals,
        "event_triggers": event_triggers,
        "summary": summary,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Written: {OUTPUT_FILE}")

    # ── Escalation report ──
    escalations = [v for v in validated if v["verdict"] == "ESCALATE"]
    if escalations:
        escalation_report = {
            "report_date": "2026-03-10",
            "run_id": "2026-W11",
            "total_escalations": len(escalations),
            "escalations": escalations,
        }
        with open(ESCALATION_FILE, "w") as f:
            json.dump(escalation_report, f, indent=2)
        print(f"  Written: {ESCALATION_FILE}")
    else:
        print(f"  No escalations — skipping escalation report")

    # ── Summary ──
    print("\n[5/5] Validation Summary")
    print("=" * 50)
    print(f"  Total updates:      {summary['total']}")
    print(f"  ACCEPT:             {summary['accept']}")
    print(f"  ACCEPT_WITH_NOTE:   {summary['accept_with_note']}")
    print(f"  FLAG:               {summary['flag']}")
    print(f"  REJECT:             {summary['reject']}")
    print(f"  ESCALATE:           {summary['escalate']}")
    print("=" * 50)

    # Show flagged and escalated details
    if verdict_counts.get("FLAG", 0) > 0:
        print(f"\n  --- FLAGGED ({verdict_counts['FLAG']}) ---")
        for v in validated:
            if v["verdict"] == "FLAG":
                print(f"    {v['country_code']}.{v['factor_path']}: {v['previous_value']} → {v['new_value']}")
                print(f"      {v['notes']}")

    if verdict_counts.get("REJECT", 0) > 0:
        print(f"\n  --- REJECTED ({verdict_counts['REJECT']}) ---")
        for v in validated:
            if v["verdict"] == "REJECT":
                print(f"    {v['country_code']}.{v['factor_path']}: {v['new_value']}")
                print(f"      {v['notes']}")

    if verdict_counts.get("ESCALATE", 0) > 0:
        print(f"\n  --- ESCALATED ({verdict_counts['ESCALATE']}) ---")
        for v in validated:
            if v["verdict"] == "ESCALATE":
                print(f"    {v['country_code']}.{v['factor_path']}: {v['previous_value']} → {v['new_value']} (conf={v['confidence']})")
                print(f"      {v['notes']}")

    print("\nAgent 08 complete.")
    return 0 if summary["reject"] == 0 or summary["reject"] < summary["total"] * 0.05 else 1


if __name__ == "__main__":
    sys.exit(main())
