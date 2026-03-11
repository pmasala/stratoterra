#!/usr/bin/env python3
"""
Agent 09 — Data Integrator
Run ID: 2026-W11, Date: 2026-03-10

Merges validated updates into /data/ country files and updates metadata.
"""
import json
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict, Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
VALIDATED_PATH = os.path.join(BASE_DIR, "staging/validated/validated_updates_2026-03-10.json")
COUNTRIES_DIR = os.path.join(BASE_DIR, "data/countries")
GLOBAL_DIR = os.path.join(BASE_DIR, "data/global")
METADATA_DIR = os.path.join(BASE_DIR, "data/metadata")
CACHE_REGISTRY_PATH = os.path.join(BASE_DIR, "agents/config/cache_registry.json")

RUN_ID = "2026-W11"
RUN_DATE = "2026-03-10"
TIMESTAMP = "2026-03-10T00:00:00Z"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Accepted verdicts (skip REJECT)
ACCEPTED_VERDICTS = {"ACCEPT", "ACCEPT_WITH_NOTE", "FLAG"}

# ---- Path Mapping ----
# Validated update factor_paths use full schema notation:
#   economy.macroeconomic.X  -> country_data["macroeconomic"][mapped_X]
#   economy.capability.X     -> country_data["economy"][mapped_X] (or create subsection)
#   endowments.demographics.X -> country_data["demographic"][mapped_X]
#   institutions.political.X -> country_data["institutions"][mapped_X]
#   institutions.X           -> country_data["institutions"][X]
#   macroeconomic.X          -> country_data["macroeconomic"][X]
#   military.X               -> country_data["military"][mapped_X]

# Factor name remappings (validated name -> actual name in country JSON)
FACTOR_NAME_MAP = {
    # economy.macroeconomic renames
    "gdp_real_growth_rate_pct": "gdp_real_growth_pct",
    "inflation_rate_cpi_pct": "inflation_cpi_pct",
    "public_debt_pct_gdp": "govt_debt_pct_gdp",
    "current_account_balance_pct_gdp": "current_account_pct_gdp",
    "foreign_exchange_reserves_usd": "fx_reserves_usd",
    "fdi_inflows_usd": "fdi_inflows_usd",
    "fiscal_balance_pct_gdp": "fiscal_balance_pct_gdp",
    "gdp_ppp_usd": "gdp_ppp_usd",
    "gini_coefficient": "gini_coefficient",
    "equity_index": "equity_index_level",
    "exchange_rate_vs_usd": "exchange_rate_vs_usd",
    # endowments.demographics renames
    "life_expectancy_years": "life_expectancy",
    "population_growth_rate_pct": "population_growth_pct",
    "health_expenditure_pct_gdp": "health_expenditure_pct_gdp",
    "labor_force_participation_pct": "labor_force_participation_pct",
    "literacy_rate_pct": "literacy_rate_pct",
    "urban_population_pct": "urban_population_pct",
    # economy.capability
    "electricity_access_pct": "electricity_access_pct",
    "internet_users_pct": "internet_users_pct",
    # military renames
    "arms_exports_global_share": "arms_exports_global_share",
    "arms_imports_global_share": "arms_imports_global_share",
}


def resolve_path(factor_path):
    """
    Resolve a validated factor_path to (section, key) in country JSON.

    Returns (section_path_list, factor_key) or None if path is for GLOBAL/non-country data.
    """
    parts = factor_path.split(".")

    if parts[0] == "commodity":
        # GLOBAL commodity data — not stored in country files
        return None

    if parts[0] == "military" and parts[1] in ("arms_transfers_global", "arms_imports_by_region"):
        # GLOBAL military aggregate data
        return None

    # economy.macroeconomic.X -> macroeconomic.mapped_X
    if len(parts) == 3 and parts[0] == "economy" and parts[1] == "macroeconomic":
        key = FACTOR_NAME_MAP.get(parts[2], parts[2])
        return (["macroeconomic"], key)

    # economy.capability.X -> stored in economy section as a direct factor
    if len(parts) == 3 and parts[0] == "economy" and parts[1] == "capability":
        key = FACTOR_NAME_MAP.get(parts[2], parts[2])
        return (["economy"], key)

    # endowments.demographics.X -> demographic.mapped_X
    if len(parts) == 3 and parts[0] == "endowments" and parts[1] == "demographics":
        key = FACTOR_NAME_MAP.get(parts[2], parts[2])
        return (["demographic"], key)

    # institutions.political.X -> institutions.mapped_X
    if len(parts) == 3 and parts[0] == "institutions" and parts[1] == "political":
        key = FACTOR_NAME_MAP.get(parts[2], parts[2])
        return (["institutions"], key)

    # institutions.X -> institutions.X
    if len(parts) == 2 and parts[0] == "institutions":
        key = FACTOR_NAME_MAP.get(parts[1], parts[1])
        return (["institutions"], key)

    # macroeconomic.X -> macroeconomic.mapped_X
    if len(parts) == 2 and parts[0] == "macroeconomic":
        key = FACTOR_NAME_MAP.get(parts[1], parts[1])
        return (["macroeconomic"], key)

    # military.X -> military.mapped_X
    if len(parts) == 2 and parts[0] == "military":
        key = FACTOR_NAME_MAP.get(parts[1], parts[1])
        return (["military"], key)

    # Fallback: try direct path
    if len(parts) == 2:
        key = FACTOR_NAME_MAP.get(parts[1], parts[1])
        return ([parts[0]], key)

    print(f"  WARNING: Unrecognized factor_path pattern: {factor_path}")
    return None


def update_factor(country_data, section_path, factor_key, update):
    """
    Navigate to the section and update/create the factor entry.
    Returns True if successful.
    """
    # Navigate to the section, creating if necessary
    node = country_data
    for segment in section_path:
        if segment not in node:
            node[segment] = {}
        node = node[segment]

    # Build the new factor value
    existing = node.get(factor_key)
    if isinstance(existing, dict) and "value" in existing:
        # Update in place, preserving any extra fields like trend
        existing["value"] = update["new_value"]
        existing["confidence"] = update["confidence"]
        existing["last_updated"] = TIMESTAMP
        existing["source"] = "agent_pipeline"
        existing["run_id"] = RUN_ID
    else:
        # Create new entry
        node[factor_key] = {
            "value": update["new_value"],
            "confidence": update["confidence"],
            "last_updated": TIMESTAMP,
            "source": "agent_pipeline",
            "run_id": RUN_ID,
        }

    return True


def add_flag(country_data, update):
    """Add a flag entry to metadata.active_flags."""
    if "metadata" not in country_data:
        country_data["metadata"] = {}
    if "active_flags" not in country_data["metadata"]:
        country_data["metadata"]["active_flags"] = []

    flag_entry = {
        "factor_path": update["factor_path"],
        "value": update["new_value"],
        "reason": update.get("notes", ""),
        "flagged_at": TIMESTAMP,
        "run_id": RUN_ID,
    }
    country_data["metadata"]["active_flags"].append(flag_entry)


def update_global_data(global_updates):
    """Update global data file with commodity and aggregate military data."""
    # Create new global data file for this week
    global_file = os.path.join(GLOBAL_DIR, f"global_data_{RUN_ID}.json")

    # Start from previous week's data if it exists
    prev_file = os.path.join(GLOBAL_DIR, "global_data_2026-W10.json")
    if os.path.exists(prev_file):
        with open(prev_file, "r") as f:
            global_data = json.load(f)
    else:
        global_data = {
            "run_id": RUN_ID,
            "date": RUN_DATE,
            "generated_at": NOW_ISO,
            "data": {},
            "flags": [],
        }

    # Update metadata
    global_data["run_id"] = RUN_ID
    global_data["date"] = RUN_DATE
    global_data["generated_at"] = NOW_ISO

    # Commodity name to global_data key mapping
    COMMODITY_KEY_MAP = {
        "brent_crude": "commodity_price.brent_crude_usd_bbl",
        "wti_crude": "commodity_price.wti_crude_usd_bbl",
        "natural_gas_henry_hub": "commodity_price.natural_gas_henry_hub_usd_mmbtu",
        "gold": "commodity_price.gold_usd_oz",
        "silver": "commodity_price.silver_usd_oz",
        "copper": "commodity_price.copper_usd_tonne",
        "iron_ore": "commodity_price.iron_ore_usd_tonne",
        "lithium_carbonate": "commodity_price.lithium_carbonate_usd_tonne",
        "wheat": "commodity_price.wheat_usd_bushel",
        "corn": "commodity_price.corn_usd_bushel",
        "soybeans": "commodity_price.soybeans_usd_bushel",
    }

    commodity_count = 0
    military_global_count = 0

    for upd in global_updates:
        path = upd["factor_path"]
        parts = path.split(".")

        if parts[0] == "commodity" and parts[1] in COMMODITY_KEY_MAP:
            gkey = COMMODITY_KEY_MAP[parts[1]]
            if gkey in global_data["data"]:
                global_data["data"][gkey]["value"] = upd["new_value"]
                global_data["data"][gkey]["confidence"] = upd["confidence"]
                global_data["data"][gkey]["last_updated"] = TIMESTAMP
                global_data["data"][gkey]["run_id"] = RUN_ID
            else:
                global_data["data"][gkey] = {
                    "value": upd["new_value"],
                    "confidence": upd["confidence"],
                    "last_updated": TIMESTAMP,
                    "source": "agent_pipeline",
                    "run_id": RUN_ID,
                }
            commodity_count += 1

        elif parts[0] == "military":
            # Store global military aggregate data
            gkey = f"military.{parts[1]}"
            global_data["data"][gkey] = {
                "value": upd["new_value"],
                "confidence": upd["confidence"],
                "last_updated": TIMESTAMP,
                "source": "agent_pipeline",
                "run_id": RUN_ID,
            }
            military_global_count += 1

    with open(global_file, "w") as f:
        json.dump(global_data, f, indent=2)

    return commodity_count, military_global_count


def main():
    print(f"Agent 09 — Data Integrator")
    print(f"Run ID: {RUN_ID}")
    print(f"Date: {RUN_DATE}")
    print(f"Timestamp: {NOW_ISO}")
    print()

    # 1. Read validated updates
    print("Reading validated updates...")
    with open(VALIDATED_PATH, "r") as f:
        validated = json.load(f)

    all_updates = validated["validated_updates"]
    print(f"  Total updates: {len(all_updates)}")

    # 2. Filter by verdict
    accepted = [u for u in all_updates if u["verdict"] in ACCEPTED_VERDICTS]
    rejected = [u for u in all_updates if u["verdict"] == "REJECT"]
    print(f"  Accepted: {len(accepted)} (ACCEPT: {sum(1 for u in accepted if u['verdict']=='ACCEPT')}, "
          f"ACCEPT_WITH_NOTE: {sum(1 for u in accepted if u['verdict']=='ACCEPT_WITH_NOTE')}, "
          f"FLAG: {sum(1 for u in accepted if u['verdict']=='FLAG')})")
    print(f"  Rejected: {len(rejected)}")
    if rejected:
        for r in rejected:
            print(f"    REJECT: {r['country_code']}.{r['factor_path']} = {r['new_value']}")
    print()

    # 3. Separate GLOBAL vs country updates
    global_updates = [u for u in accepted if u["country_code"] == "GLOBAL"]
    country_updates = [u for u in accepted if u["country_code"] != "GLOBAL"]

    print(f"  GLOBAL updates: {len(global_updates)}")
    print(f"  Country updates: {len(country_updates)}")
    print()

    # 4. Process GLOBAL updates
    if global_updates:
        print("Processing GLOBAL updates...")
        commodity_count, mil_global_count = update_global_data(global_updates)
        print(f"  Commodity prices updated: {commodity_count}")
        print(f"  Military global aggregates updated: {mil_global_count}")
        print(f"  Wrote: data/global/global_data_{RUN_ID}.json")
        print()

    # 5. Group country updates by country_code
    by_country = defaultdict(list)
    for u in country_updates:
        by_country[u["country_code"]].append(u)

    print(f"Countries to update: {len(by_country)}")
    print()

    # 6. Process each country
    stats = {
        "countries_updated": 0,
        "factors_updated": 0,
        "factors_created": 0,
        "flags_added": 0,
        "skipped_global": len(global_updates),
        "skipped_unresolvable": 0,
        "errors": [],
    }

    verdict_counts = Counter()

    for cc in sorted(by_country.keys()):
        updates = by_country[cc]
        country_file = os.path.join(COUNTRIES_DIR, f"{cc}.json")

        if not os.path.exists(country_file):
            print(f"  WARNING: Country file not found: {cc}.json — skipping {len(updates)} updates")
            stats["errors"].append(f"Missing country file: {cc}.json")
            continue

        with open(country_file, "r") as f:
            country_data = json.load(f)

        factors_written = 0
        factors_new = 0
        flags = 0

        for upd in updates:
            resolved = resolve_path(upd["factor_path"])
            if resolved is None:
                stats["skipped_unresolvable"] += 1
                continue

            section_path, factor_key = resolved

            # Check if this is a new or existing factor
            node = country_data
            is_new = True
            try:
                for seg in section_path:
                    node = node[seg]
                if factor_key in node:
                    is_new = False
            except (KeyError, TypeError):
                pass

            success = update_factor(country_data, section_path, factor_key, upd)
            if success:
                factors_written += 1
                verdict_counts[upd["verdict"]] += 1
                if is_new:
                    factors_new += 1

                # Handle FLAG verdict
                if upd["verdict"] == "FLAG":
                    add_flag(country_data, upd)
                    flags += 1

        # Update country-level metadata
        country_data["last_updated"] = TIMESTAMP
        country_data["run_id"] = RUN_ID
        if "metadata" in country_data:
            country_data["metadata"]["update_count"] = country_data["metadata"].get("update_count", 0) + factors_written

        # Write back
        with open(country_file, "w") as f:
            json.dump(country_data, f, indent=2)

        stats["countries_updated"] += 1
        stats["factors_updated"] += factors_written
        stats["factors_created"] += factors_new
        stats["flags_added"] += flags

        status = f"  {cc}: {factors_written} factors updated"
        if factors_new > 0:
            status += f" ({factors_new} new)"
        if flags > 0:
            status += f", {flags} flags"
        print(status)

    print()
    print("=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    print(f"  Countries updated:      {stats['countries_updated']}")
    print(f"  Total factors updated:   {stats['factors_updated']}")
    print(f"  New factors created:     {stats['factors_created']}")
    print(f"  Flags added:             {stats['flags_added']}")
    print(f"  GLOBAL updates written:  {stats['skipped_global']}")
    print(f"  Unresolvable paths:      {stats['skipped_unresolvable']}")
    print(f"  Verdicts: {dict(verdict_counts)}")
    if stats["errors"]:
        print(f"  Errors: {stats['errors']}")
    print()

    # 7. Update last_update.json
    print("Updating metadata/last_update.json...")
    last_update = {
        "last_run_id": RUN_ID,
        "last_run_completed_at": NOW_ISO,
        "countries_updated": stats["countries_updated"],
        "relations_updated": 0,
        "total_factors_updated": stats["factors_updated"],
    }
    with open(os.path.join(METADATA_DIR, "last_update.json"), "w") as f:
        json.dump(last_update, f, indent=2)
    print("  Done.")

    # 8. Append to update_log.json
    print("Appending to metadata/update_log.json...")
    log_path = os.path.join(METADATA_DIR, "update_log.json")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            update_log = json.load(f)
    else:
        update_log = []

    log_entry = {
        "run_id": RUN_ID,
        "completed_at": NOW_ISO,
        "date": RUN_DATE,
        "countries_updated": stats["countries_updated"],
        "relations_updated": 0,
        "updates_accepted": verdict_counts.get("ACCEPT", 0),
        "updates_accepted_with_note": verdict_counts.get("ACCEPT_WITH_NOTE", 0),
        "updates_flagged": verdict_counts.get("FLAG", 0),
        "updates_rejected": len(rejected),
        "global_updates": len(global_updates),
        "new_factors_created": stats["factors_created"],
        "errors": len(stats["errors"]),
    }
    update_log.append(log_entry)

    with open(log_path, "w") as f:
        json.dump(update_log, f, indent=2)
    print("  Done.")

    # 9. Update cache_registry.json
    print("Updating cache_registry.json...")
    with open(CACHE_REGISTRY_PATH, "r") as f:
        cache = json.load(f)

    # Update financial_markets (weekly data refreshed)
    if "financial_markets" in cache["entries"]:
        cache["entries"]["financial_markets"]["last_fetched"] = NOW_ISO
        cache["entries"]["financial_markets"]["next_due"] = "2026-03-17"

    # Update sipri.arms_transfers (was due today, data fetched)
    if "sipri.arms_transfers" in cache["entries"]:
        cache["entries"]["sipri.arms_transfers"]["last_fetched"] = NOW_ISO
        cache["entries"]["sipri.arms_transfers"]["next_due"] = "2027-03-10"

    cache["last_updated"] = NOW_ISO

    with open(CACHE_REGISTRY_PATH, "w") as f:
        json.dump(cache, f, indent=2)
    print("  Done.")

    # 10. Update run_log.json
    print("Updating staging/run_log.json...")
    run_log_path = os.path.join(BASE_DIR, "staging/run_log.json")
    if os.path.exists(run_log_path):
        with open(run_log_path, "r") as f:
            run_log = json.load(f)
    else:
        run_log = {}

    run_log["agent_09"] = {
        "status": "SUCCESS",
        "started_at": NOW_ISO,
        "completed_at": NOW_ISO,
        "countries_updated": stats["countries_updated"],
        "factors_updated": stats["factors_updated"],
        "flags_added": stats["flags_added"],
        "global_updates": len(global_updates),
        "rejected": len(rejected),
    }

    with open(run_log_path, "w") as f:
        json.dump(run_log, f, indent=2)
    print("  Done.")

    print()
    print(f"Agent 09 complete. {stats['factors_updated']} factors integrated across {stats['countries_updated']} countries.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
