#!/usr/bin/env python3
"""
Agent 09: Data Integrator
Merges validated factor updates into /data/countries/*.json and global data.
Run ID: 2026-W10, Date: 2026-03-04
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = "/home/pietro/stratoterra"
DATE = "2026-03-04"
VALIDATED_FILE = f"{PROJECT_ROOT}/staging/validated/validated_updates_{DATE}.json"
FACTOR_UPDATES_FILE = f"{PROJECT_ROOT}/staging/processed/factor_updates_{DATE}.json"
COUNTRIES_DIR = f"{PROJECT_ROOT}/data/countries"
METADATA_DIR = f"{PROJECT_ROOT}/data/metadata"
GLOBAL_DIR = f"{PROJECT_ROOT}/data/global"
CACHE_REGISTRY = f"{PROJECT_ROOT}/agents/config/cache_registry.json"
RUN_LOG_FILE = f"{PROJECT_ROOT}/staging/run_log.json"

RUN_ID = "2026-W10"
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ACCEPTED_VERDICTS = {"ACCEPT", "ACCEPT_WITH_NOTE", "FLAG"}

# Mapping from factor_update paths to country file keys
FACTOR_PATH_MAP = {
    "economy.macroeconomic.exchange_rate_vs_usd": ("macroeconomic", "exchange_rate_vs_usd"),
    "economy.macroeconomic.sovereign_bond_yield_10yr": ("macroeconomic", "sovereign_bond_yield_10yr_pct"),
    "economy.macroeconomic.equity_index": ("macroeconomic", "equity_index_level"),
    "economy.macroeconomic.central_bank_policy_rate_pct": ("macroeconomic", "central_bank_policy_rate_pct"),
    "institutions.political.head_of_state": ("institutions", "head_of_state"),
    "institutions.political.leadership_transition_risk": ("institutions", "leadership_transition_risk"),
    "institutions.political.civil_unrest_level": ("institutions", "civil_unrest_level"),
    "institutions.political.head_of_government": ("institutions", "head_of_government"),
}

# Commodity paths for global data file
COMMODITY_PATH_MAP = {
    "economy.commodity_prices.brent_crude_usd_bbl": "commodity_price.brent_crude_usd_bbl",
    "economy.commodity_prices.wti_crude_usd_bbl": "commodity_price.wti_crude_usd_bbl",
    "economy.commodity_prices.natural_gas_usd_mmbtu": "commodity_price.natural_gas_henry_hub_usd_mmbtu",
    "economy.commodity_prices.gold_usd_oz": "commodity_price.gold_usd_oz",
    "economy.commodity_prices.silver_usd_oz": "commodity_price.silver_usd_oz",
    "economy.commodity_prices.copper_usd_lb": "commodity_price.copper_usd_lb",
    "economy.commodity_prices.iron_ore_usd_tonne": "commodity_price.iron_ore_usd_tonne",
}


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def update_factor(country_data, section, key, value, confidence):
    """Update a factor in the country data file."""
    if section not in country_data:
        country_data[section] = {}

    # Special handling for head_of_state (stores as plain strings)
    if key == "head_of_state" and isinstance(value, dict):
        name = value.get("name", "")
        title = value.get("title", "")
        status = value.get("status", "")
        country_data[section]["head_of_state_name"] = name
        country_data[section]["head_of_state_title"] = f"{title} ({status})" if status else title
        return True

    # Special handling for head_of_government
    if key == "head_of_government" and isinstance(value, dict):
        name = value.get("name", "")
        title = value.get("title", "")
        country_data[section]["head_of_government_name"] = name
        country_data[section]["head_of_government_title"] = title
        return True

    # Special handling for equity_index (extract level from complex object)
    if key == "equity_index_level" and isinstance(value, dict):
        level = value.get("level", value)
        weekly_change = value.get("weekly_change_pct")
        country_data[section]["equity_index_level"] = {
            "value": level,
            "confidence": confidence,
            "last_updated": TIMESTAMP,
            "source": "agent_pipeline",
            "run_id": RUN_ID,
        }
        if weekly_change is not None:
            country_data[section]["equity_index_daily_change_pct"] = {
                "value": weekly_change,
                "confidence": confidence,
                "last_updated": TIMESTAMP,
                "source": "agent_pipeline",
                "run_id": RUN_ID,
            }
        return True

    # Standard factor update
    if key in country_data[section] and isinstance(country_data[section][key], dict) and "value" in country_data[section][key]:
        country_data[section][key]["value"] = value
        country_data[section][key]["confidence"] = confidence
        country_data[section][key]["last_updated"] = TIMESTAMP
        country_data[section][key]["source"] = "agent_pipeline"
        country_data[section][key]["run_id"] = RUN_ID
    else:
        country_data[section][key] = {
            "value": value,
            "confidence": confidence,
            "last_updated": TIMESTAMP,
            "source": "agent_pipeline",
            "run_id": RUN_ID,
        }
    return True


def update_layers(country_data, section, key, value):
    """Update the layers section which mirrors factor data in flat format."""
    layers = country_data.get("layers", {})
    layer_map = {
        "macroeconomic": "economy",
        "institutions": "institutions",
        "military": "military",
    }
    layer_name = layer_map.get(section)
    if not layer_name or layer_name not in layers:
        return

    if key == "equity_index_level" and isinstance(value, dict):
        layers[layer_name]["equity_index_level"] = value.get("level", value)
        if "weekly_change_pct" in value:
            layers[layer_name]["equity_index_daily_change_pct"] = value["weekly_change_pct"]
    elif key == "head_of_state" and isinstance(value, dict):
        layers[layer_name]["head_of_state_name"] = value.get("name", "")
        layers[layer_name]["head_of_state_title"] = value.get("title", "")
    elif key == "head_of_government" and isinstance(value, dict):
        layers[layer_name]["head_of_government_name"] = value.get("name", "")
    else:
        # Use the mapped key name for layers
        leaf_key = key
        if isinstance(value, (int, float, str, bool)):
            layers[layer_name][leaf_key] = value


def main():
    print(f"=== Agent 09: Data Integrator ===")
    print(f"Run ID: {RUN_ID}")
    print(f"Date: {DATE}")
    print(f"Timestamp: {TIMESTAMP}")
    print()

    # Load validated updates and factor updates
    validated = load_json(VALIDATED_FILE)
    factor_data = load_json(FACTOR_UPDATES_FILE)

    all_validated = validated["validated_updates"]
    factor_updates = {u["update_id"]: u for u in factor_data["factor_updates"]}

    # Filter to accepted verdicts
    accepted = [u for u in all_validated if u["verdict"] in ACCEPTED_VERDICTS]
    rejected = [u for u in all_validated if u["verdict"] not in ACCEPTED_VERDICTS]
    print(f"Total validated: {len(all_validated)}")
    print(f"To integrate: {len(accepted)}")
    print(f"Rejected/skipped: {len(rejected)}")
    print()

    # Merge validated with factor_updates to get full metadata
    merged = []
    for v in accepted:
        uid = v["update_id"]
        fu = factor_updates.get(uid, {})
        merged.append({
            "update_id": uid,
            "verdict": v["verdict"],
            "new_value": v["new_value"],
            "notes": v.get("notes", ""),
            "country_code": fu.get("country_code"),
            "factor_path": fu.get("factor_path", ""),
            "confidence": fu.get("confidence", 0.9),
            "target": fu.get("target", "country"),
        })

    # Separate country vs global updates
    country_updates = [m for m in merged if m["target"] == "country" and m["country_code"]]
    global_updates = [m for m in merged if m["target"] == "global"]

    print(f"Country updates: {len(country_updates)}")
    print(f"Global updates: {len(global_updates)}")
    print()

    # Group by country
    by_country = defaultdict(list)
    for u in country_updates:
        by_country[u["country_code"]].append(u)

    countries_updated = set()
    factors_updated = 0
    flags_added = 0
    errors = []

    # Process each country
    for cc in sorted(by_country.keys()):
        country_file = os.path.join(COUNTRIES_DIR, f"{cc}.json")
        if not os.path.exists(country_file):
            msg = f"WARN: No country file for {cc}, skipping {len(by_country[cc])} updates"
            print(msg)
            errors.append(msg)
            continue

        try:
            country_data = load_json(country_file)
        except Exception as e:
            msg = f"ERROR: Failed to read {country_file}: {e}"
            print(msg)
            errors.append(msg)
            continue

        cc_factors = 0
        cc_flags = 0

        for upd in by_country[cc]:
            factor_path = upd["factor_path"]
            new_value = upd["new_value"]
            confidence = upd["confidence"]
            verdict = upd["verdict"]

            # Map factor path to country file structure
            mapping = FACTOR_PATH_MAP.get(factor_path)
            if not mapping:
                msg = f"WARN: No mapping for factor_path '{factor_path}' (update {upd['update_id']})"
                print(msg)
                errors.append(msg)
                continue

            section, key = mapping

            # Apply update
            update_factor(country_data, section, key, new_value, confidence)
            update_layers(country_data, section, key, new_value)
            cc_factors += 1

            # Handle FLAG: add to active_flags
            if verdict == "FLAG":
                if "metadata" not in country_data:
                    country_data["metadata"] = {"active_flags": []}
                if "active_flags" not in country_data.get("metadata", {}):
                    country_data["metadata"]["active_flags"] = []
                country_data["metadata"]["active_flags"].append({
                    "factor": factor_path,
                    "reason": upd.get("notes", "Flagged by validator"),
                    "new_value": new_value,
                    "flagged_at": TIMESTAMP,
                    "run_id": RUN_ID,
                })
                cc_flags += 1

        # Update top-level metadata
        country_data["last_updated"] = TIMESTAMP
        country_data["run_id"] = RUN_ID

        try:
            save_json(country_file, country_data)
            countries_updated.add(cc)
            factors_updated += cc_factors
            flags_added += cc_flags
            print(f"  {cc}: {cc_factors} factors updated" + (f", {cc_flags} flags" if cc_flags else ""))
        except Exception as e:
            msg = f"ERROR: Failed to write {country_file}: {e}"
            print(msg)
            errors.append(msg)

    # Process global (commodity) updates
    global_file = os.path.join(GLOBAL_DIR, f"global_data_{RUN_ID}.json")
    if os.path.exists(global_file):
        global_data = load_json(global_file)
    else:
        # Base on previous global file
        prev_global = os.path.join(GLOBAL_DIR, "global_data_2026-W09.json")
        if os.path.exists(prev_global):
            global_data = load_json(prev_global)
            global_data["run_id"] = RUN_ID
            global_data["date"] = DATE
        else:
            global_data = {"run_id": RUN_ID, "date": DATE, "generated_at": TIMESTAMP, "data": {}}

    global_data["generated_at"] = TIMESTAMP
    global_factors = 0
    global_flags = 0

    for upd in global_updates:
        factor_path = upd["factor_path"]
        new_value = upd["new_value"]
        confidence = upd["confidence"]
        verdict = upd["verdict"]

        global_key = COMMODITY_PATH_MAP.get(factor_path)
        if not global_key:
            msg = f"WARN: No global mapping for '{factor_path}' (update {upd['update_id']})"
            print(msg)
            errors.append(msg)
            continue

        global_data["data"][global_key] = {
            "value": new_value,
            "confidence": confidence,
            "last_updated": TIMESTAMP,
            "source": "agent_pipeline",
            "run_id": RUN_ID,
        }
        global_factors += 1

        if verdict == "FLAG":
            if "flags" not in global_data:
                global_data["flags"] = []
            global_data["flags"].append({
                "factor": global_key,
                "reason": upd.get("notes", "Flagged"),
                "value": new_value,
                "flagged_at": TIMESTAMP,
            })
            global_flags += 1

    save_json(global_file, global_data)
    print(f"\n  Global: {global_factors} commodity prices updated" + (f", {global_flags} flags" if global_flags else ""))

    print()
    print(f"=== Integration Summary ===")
    print(f"Countries updated: {len(countries_updated)}")
    print(f"Country factors integrated: {factors_updated}")
    print(f"Global factors integrated: {global_factors}")
    print(f"Flags added: {flags_added + global_flags}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print()

    # Write /data/metadata/last_update.json
    os.makedirs(METADATA_DIR, exist_ok=True)
    last_update = {
        "last_run_id": RUN_ID,
        "last_run_completed_at": TIMESTAMP,
        "countries_updated": len(countries_updated),
        "relations_updated": 0,
        "total_factors_updated": factors_updated + global_factors,
    }
    save_json(os.path.join(METADATA_DIR, "last_update.json"), last_update)
    print(f"Wrote last_update.json")

    # Append to /data/metadata/update_log.json
    update_log_path = os.path.join(METADATA_DIR, "update_log.json")
    if os.path.exists(update_log_path):
        update_log = load_json(update_log_path)
        if not isinstance(update_log, list):
            update_log = [update_log]
    else:
        update_log = []

    update_log.append({
        "run_id": f"{RUN_ID}c",
        "completed_at": TIMESTAMP,
        "date": DATE,
        "countries_updated": len(countries_updated),
        "relations_updated": 0,
        "updates_accepted": len([u for u in accepted if u["verdict"] == "ACCEPT"]),
        "updates_accepted_with_note": len([u for u in accepted if u["verdict"] == "ACCEPT_WITH_NOTE"]),
        "updates_flagged": len([u for u in accepted if u["verdict"] == "FLAG"]),
        "updates_rejected": len(rejected),
        "global_updates": global_factors,
        "errors": len(errors),
    })
    save_json(update_log_path, update_log)
    print(f"Wrote update_log.json")

    # Update cache registry
    try:
        cache_reg = load_json(CACHE_REGISTRY)
        # Update financial_markets entry (weekly data was fetched)
        if "financial_markets" in cache_reg:
            cache_reg["financial_markets"]["last_fetched"] = TIMESTAMP
        cache_reg["last_updated"] = TIMESTAMP
        save_json(CACHE_REGISTRY, cache_reg)
        print(f"Updated cache_registry.json")
    except Exception as e:
        msg = f"WARN: Failed to update cache registry: {e}"
        print(msg)
        errors.append(msg)

    # Update run_log.json
    run_log = load_json(RUN_LOG_FILE)
    run_log["agents"].append({
        "agent_id": "agent_09",
        "name": "Data Integrator",
        "status": "completed",
        "started_at": TIMESTAMP,
        "completed_at": TIMESTAMP,
        "countries_updated": len(countries_updated),
        "factors_integrated": factors_updated,
        "global_factors_integrated": global_factors,
        "flags_added": flags_added + global_flags,
        "errors": len(errors),
        "error_details": errors if errors else None,
        "notes": f"Integrated {factors_updated} country + {global_factors} global updates across {len(countries_updated)} countries. {flags_added + global_flags} flags.",
    })
    save_json(RUN_LOG_FILE, run_log)
    print(f"Updated run_log.json")

    print(f"\n=== Agent 09 Complete ===")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
