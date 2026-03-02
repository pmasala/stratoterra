#!/usr/bin/env python3
"""
Agent 09: Data Integrator
Merges validated factor updates into /data/countries/*.json
Run ID: 2026-W10, Date: 2026-03-02
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = "/home/pietro/stratoterra"
VALIDATED_FILE = f"{PROJECT_ROOT}/staging/validated/validated_updates_2026-03-02.json"
COUNTRIES_DIR = f"{PROJECT_ROOT}/data/countries"
METADATA_DIR = f"{PROJECT_ROOT}/data/metadata"
RUN_LOG_FILE = f"{PROJECT_ROOT}/staging/run_log.json"

RUN_ID = "2026-W10"
TIMESTAMP = "2026-03-02T12:05:00Z"
ACCEPTED_VERDICTS = {"ACCEPT", "ACCEPT_WITH_NOTE", "FLAG", "ESCALATE"}

# Mapping from validated update factor_path keys to existing country JSON keys
# When the update uses a different name than the country file
KEY_ALIASES = {
    "macroeconomic.inflation_rate_cpi_pct": "macroeconomic.inflation_cpi_pct",
    "macroeconomic.foreign_reserves_usd": "macroeconomic.fx_reserves_usd",
    "macroeconomic.central_bank_rate_pct": "macroeconomic.central_bank_policy_rate_pct",
    "macroeconomic.policy_rate_pct": "macroeconomic.central_bank_policy_rate_pct",
}


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def set_nested(d, path_parts, value_obj):
    """Set a nested value in a dict, creating intermediate dicts as needed.
    value_obj is a dict with 'value', 'confidence', etc."""
    current = d
    for part in path_parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            # Overwrite non-dict with dict if we need nesting
            current[part] = {}
        current = current[part]

    key = path_parts[-1]
    if key in current and isinstance(current[key], dict) and "value" in current[key]:
        # Update existing factor entry
        current[key]["value"] = value_obj["value"]
        current[key]["confidence"] = value_obj["confidence"]
        current[key]["last_updated"] = TIMESTAMP
        current[key]["source"] = "agent_pipeline"
        current[key]["run_id"] = RUN_ID
    else:
        # Create new factor entry
        current[key] = {
            "value": value_obj["value"],
            "confidence": value_obj["confidence"],
            "last_updated": TIMESTAMP,
            "source": "agent_pipeline",
            "run_id": RUN_ID,
        }


def update_layers(country_data, section, key, value):
    """Update the layers section which mirrors factor data in flat format."""
    layers = country_data.get("layers", {})
    layer_map = {
        "macroeconomic": "economy",
        "demographic": "endowments",
        "institutions": "institutions",
        "military": "military",
        "trade": "relations",
        "economy": "economy",
    }
    layer_name = layer_map.get(section)
    if layer_name and layer_name in layers:
        # For nested keys like commodity_price.gold, use the leaf key
        layers[layer_name][key] = value


def resolve_factor_path(factor_path):
    """Resolve a factor_path, applying aliases and returning (section, key_parts)."""
    resolved = KEY_ALIASES.get(factor_path, factor_path)
    parts = resolved.split(".")
    section = parts[0]
    key_parts = parts[1:]
    return section, key_parts, parts


def main():
    print(f"=== Agent 09: Data Integrator ===")
    print(f"Run ID: {RUN_ID}")
    print(f"Timestamp: {TIMESTAMP}")
    print()

    # Load validated updates
    validated = load_json(VALIDATED_FILE)
    all_updates = validated["validated_updates"]
    print(f"Total validated updates loaded: {len(all_updates)}")

    # Filter to accepted verdicts (human approved all escalations)
    updates = [u for u in all_updates if u["verdict"] in ACCEPTED_VERDICTS]
    rejected = [u for u in all_updates if u["verdict"] not in ACCEPTED_VERDICTS]
    print(f"Updates to integrate: {len(updates)}")
    print(f"Rejected/skipped: {len(rejected)}")
    print()

    # Group updates by country
    by_country = defaultdict(list)
    for u in updates:
        by_country[u["country_code"]].append(u)

    countries_updated = set()
    factors_updated = 0
    flags_added = 0
    errors = []
    new_fields_created = 0

    # Process each country
    country_codes = sorted(by_country.keys())
    print(f"Countries to update: {len(country_codes)}")

    for cc in country_codes:
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

        cc_updates = by_country[cc]
        cc_factors = 0
        cc_flags = 0

        for upd in cc_updates:
            factor_path = upd["factor_path"]
            new_value = upd["new_value"]
            confidence = upd["confidence"]
            verdict = upd["verdict"]

            section, key_parts, full_parts = resolve_factor_path(factor_path)

            # Build value object
            value_obj = {
                "value": new_value,
                "confidence": confidence,
            }

            # Set the value in the country data
            set_nested(country_data, full_parts if factor_path not in KEY_ALIASES else KEY_ALIASES[factor_path].split("."), value_obj)
            cc_factors += 1

            # Update layers section (flat mirror)
            if len(key_parts) == 1:
                update_layers(country_data, section, key_parts[0], new_value)

            # Handle FLAG verdict: add to active_flags
            if verdict == "FLAG":
                if "metadata" not in country_data:
                    country_data["metadata"] = {"active_flags": []}
                if "active_flags" not in country_data["metadata"]:
                    country_data["metadata"]["active_flags"] = []
                country_data["metadata"]["active_flags"].append({
                    "factor": factor_path,
                    "reason": upd.get("notes", "Flagged by validator"),
                    "previous_value": upd.get("previous_value"),
                    "new_value": new_value,
                    "flagged_at": TIMESTAMP,
                    "run_id": RUN_ID,
                })
                cc_flags += 1

        # Update top-level metadata
        country_data["last_updated"] = TIMESTAMP
        country_data["run_id"] = RUN_ID
        if "metadata" in country_data:
            country_data["metadata"]["update_count"] = country_data["metadata"].get("update_count", 0) + cc_factors

        # Save
        try:
            save_json(country_file, country_data)
            countries_updated.add(cc)
            factors_updated += cc_factors
            flags_added += cc_flags
        except Exception as e:
            msg = f"ERROR: Failed to write {country_file}: {e}"
            print(msg)
            errors.append(msg)

    print()
    print(f"=== Integration Summary ===")
    print(f"Countries updated: {len(countries_updated)}")
    print(f"Factors integrated: {factors_updated}")
    print(f"Flags added: {flags_added}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print()

    # Create metadata directory if needed
    os.makedirs(METADATA_DIR, exist_ok=True)

    # Write /data/metadata/last_update.json
    last_update = {
        "last_run_id": RUN_ID,
        "last_run_completed_at": TIMESTAMP,
        "countries_updated": len(countries_updated),
        "relations_updated": 0,
        "total_factors_updated": factors_updated,
    }
    save_json(os.path.join(METADATA_DIR, "last_update.json"), last_update)
    print(f"Wrote {METADATA_DIR}/last_update.json")

    # Write /data/metadata/update_log.json
    update_log_path = os.path.join(METADATA_DIR, "update_log.json")
    if os.path.exists(update_log_path):
        update_log = load_json(update_log_path)
        if not isinstance(update_log, list):
            update_log = [update_log]
    else:
        update_log = []

    update_log.append({
        "run_id": RUN_ID,
        "completed_at": TIMESTAMP,
        "countries_updated": len(countries_updated),
        "relations_updated": 0,
        "updates_accepted": len([u for u in updates if u["verdict"] == "ACCEPT"]),
        "updates_accepted_with_note": len([u for u in updates if u["verdict"] == "ACCEPT_WITH_NOTE"]),
        "updates_flagged": len([u for u in updates if u["verdict"] == "FLAG"]),
        "updates_escalated_accepted": len([u for u in updates if u["verdict"] == "ESCALATE"]),
        "updates_rejected": len(rejected),
        "errors": len(errors),
        "fx_convention_note": "EUR-zone, GBP, AUD FX rates normalized to local/USD convention (previously stored as USD/local). All exchange_rate_vs_usd values now consistently represent units of local currency per 1 USD.",
    })
    save_json(update_log_path, update_log)
    print(f"Wrote {update_log_path}")

    # Update run_log.json
    run_log = load_json(RUN_LOG_FILE)
    run_log["agents"].append({
        "agent_id": "agent_09",
        "agent_name": "Data Integrator",
        "phase": "INTEGRATE",
        "status": "completed",
        "started_at": "2026-03-02T12:00:00Z",
        "completed_at": TIMESTAMP,
        "countries_updated": len(countries_updated),
        "relations_updated": 0,
        "factors_integrated": factors_updated,
        "flags_added": flags_added,
        "errors": len(errors),
        "error_details": errors if errors else None,
        "notes": f"Integrated {factors_updated} factor updates across {len(countries_updated)} countries. {flags_added} flags added. All 25 escalated items accepted per human review. FX rates for EUR-zone/GBP/AUD normalized to local/USD convention. No relation or timeseries updates in this run (no relation data in validated updates).",
    })
    save_json(RUN_LOG_FILE, run_log)
    print(f"Updated {RUN_LOG_FILE}")

    print()
    print(f"=== Agent 09 Complete ===")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
