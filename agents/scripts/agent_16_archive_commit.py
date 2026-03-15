#!/usr/bin/env python3
"""Agent 16 — Archive & Commit Preparer

Creates archive snapshot, generates UI-optimized chunk files,
builds manifest, and updates the run log.
Does NOT execute any git commands.

Usage:
    python3 agents/scripts/agent_16_archive_commit.py                # auto-detect run_id
    python3 agents/scripts/agent_16_archive_commit.py --run-id 2026-W11
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
COUNTRIES_DIR = DATA_DIR / "countries"
GLOBAL_DIR = DATA_DIR / "global"
INDICES_DIR = DATA_DIR / "indices"
METADATA_DIR = DATA_DIR / "metadata"
CHUNKS_DIR = DATA_DIR / "chunks"
STAGING_DIR = PROJECT_ROOT / "staging"
ARCHIVE_DIR = PROJECT_ROOT / "archive"

NOW = datetime.now(timezone.utc)
_iso = NOW.isocalendar()
RUN_ID = f"{_iso.year}-W{_iso.week:02d}"
NOW = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")

# Country centroid coordinates (ISO3 -> [lat, lon])
COUNTRY_COORDS = {
    "AGO": [-12.37, 17.54], "ARE": [23.42, 53.85], "ARG": [-38.42, -63.62],
    "AUS": [-25.27, 133.78], "AZE": [40.14, 47.58], "BGD": [23.68, 90.36],
    "BGR": [42.73, 25.49], "BRA": [-14.24, -51.93], "CAN": [56.13, -106.35],
    "CHE": [46.82, 8.23], "CHL": [-35.68, -71.54], "CHN": [35.86, 104.20],
    "CIV": [7.54, -5.55], "COD": [-4.04, 21.76], "COL": [4.57, -74.30],
    "CZE": [49.82, 15.47], "DEU": [51.17, 10.45], "EGY": [26.82, 30.80],
    "ESP": [40.46, -3.75], "ETH": [9.15, 40.49], "FIN": [61.92, 25.75],
    "FRA": [46.23, 2.21], "GBR": [55.38, -3.44], "GEO": [42.32, 43.36],
    "GHA": [7.95, -1.02], "GRC": [39.07, 21.82], "HRV": [45.10, 15.20],
    "HUN": [47.16, 19.50], "IDN": [-0.79, 113.92], "IND": [20.59, 78.96],
    "IRL": [53.41, -8.24], "IRN": [32.43, 53.69], "IRQ": [33.22, 43.68],
    "ISR": [31.05, 34.85], "ITA": [41.87, 12.57], "JOR": [30.59, 36.24],
    "JPN": [36.20, 138.25], "KAZ": [48.02, 66.92], "KEN": [-0.02, 37.91],
    "KOR": [35.91, 127.77], "KWT": [29.31, 47.48], "LBY": [26.34, 17.23],
    "LKA": [7.87, 80.77], "MAR": [31.79, -7.09], "MEX": [23.63, -102.55],
    "MMR": [21.91, 95.96], "MOZ": [-18.67, 35.53], "MYS": [4.21, 101.98],
    "NGA": [9.08, 8.68], "NLD": [52.13, 5.29], "NOR": [60.47, 8.47],
    "NZL": [-40.90, 174.89], "OMN": [21.47, 55.98], "PAK": [30.38, 69.35],
    "PER": [-9.19, -75.02], "PHL": [12.88, 121.77], "POL": [51.92, 19.15],
    "PRT": [39.40, -8.22], "QAT": [25.35, 51.18], "ROU": [45.94, 24.97],
    "RUS": [61.52, 105.32], "SAU": [23.89, 45.08], "SEN": [14.50, -14.45],
    "SGP": [1.35, 103.82], "SRB": [44.02, 21.01], "SWE": [60.13, 18.64],
    "THA": [15.87, 100.99], "TUR": [38.96, 35.24], "TWN": [23.70, 120.96],
    "TZA": [-6.37, 34.89], "UKR": [48.38, 31.17], "USA": [37.09, -95.71],
    "UZB": [41.38, 64.59], "VNM": [14.06, 108.28], "ZAF": [-30.56, 22.94],
}


def load_json(path):
    """Load a JSON file, return None on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, FileNotFoundError) as e:
        print(f"  Warning: could not load {path}: {e}", file=sys.stderr)
        return None


def save_json(path, data):
    """Write JSON with 2-space indent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def extract_value(obj, default=None):
    """Extract a value from a factor object (handles both {value: X} and raw X)."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get("value", default)
    return obj


def get_nested(data, *keys, default=None):
    """Safely traverse nested dicts."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


# ===========================================================================
# Step 1: Archive Snapshot
# ===========================================================================
def step_1_archive():
    print("=== Step 1: Archive Snapshot ===")
    archive_path = ARCHIVE_DIR / RUN_ID
    archive_path.mkdir(parents=True, exist_ok=True)

    src = METADATA_DIR / "last_update.json"
    dst = archive_path / "last_update_snapshot.json"
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  Copied last_update.json -> {dst}")
    else:
        print(f"  Warning: {src} not found, creating stub")
        save_json(dst, {"run_id": RUN_ID, "note": "last_update.json missing at archive time"})

    return str(archive_path)


# ===========================================================================
# Step 2: Generate Country Summary Chunk
# ===========================================================================
def step_2_country_summary():
    print("\n=== Step 2: Country Summary Chunk ===")

    # Load supporting data
    country_list = load_json(INDICES_DIR / "country_list.json") or {}
    alert_index = load_json(INDICES_DIR / "alert_index.json") or {}

    # Build tier lookup from country_list
    tier_lookup = {}
    for tier_key in ("tier_1", "tier_2", "tier_3"):
        tier_data = country_list.get("tiers", {}).get(tier_key, {})
        tier_num = int(tier_key.split("_")[1])
        for c in tier_data.get("countries", []):
            tier_lookup[c["code"]] = tier_num

    # Build alert lookup: country_code -> {count, max_severity}
    SEVERITY_ORDER = {"critical": 3, "warning": 2, "watch": 1, "none": 0}
    alert_lookup = {}
    for alert in alert_index.get("alerts", []):
        codes = alert.get("countries", [])
        cc = alert.get("country_code")
        if cc and cc not in codes:
            codes.append(cc)
        sev = alert.get("severity", "watch")
        for code in codes:
            if code not in alert_lookup:
                alert_lookup[code] = {"count": 0, "max_severity": "none"}
            alert_lookup[code]["count"] += 1
            if SEVERITY_ORDER.get(sev, 0) > SEVERITY_ORDER.get(alert_lookup[code]["max_severity"], 0):
                alert_lookup[code]["max_severity"] = sev

    # Process each country file
    country_files = sorted(COUNTRIES_DIR.glob("*.json"))
    summaries = []

    for cf in country_files:
        code = cf.stem
        data = load_json(cf)
        if not data:
            continue

        name = data.get("country_name") or data.get("name") or code
        tier = data.get("tier") or tier_lookup.get(code, 0)

        # Coordinates
        coords = COUNTRY_COORDS.get(code, [0, 0])
        lat, lon = coords[0], coords[1]

        # Derived metrics (check both top-level 'derived' and 'layers.derived')
        derived = data.get("derived", {})
        layers_derived = get_nested(data, "layers", "derived", default={})

        cnpi = extract_value(derived.get("composite_national_power_index"), None)
        if cnpi is None:
            cnpi = layers_derived.get("composite_national_power_index")

        oir = extract_value(derived.get("overall_investment_risk_score"), None)
        if oir is None:
            oir = layers_derived.get("overall_investment_risk_score")

        # Political stability: check institutions section
        pss = extract_value(get_nested(data, "institutions", "wgi_political_stability"))
        if pss is None:
            pss = get_nested(data, "layers", "institutions", "wgi_political_stability")

        # Macroeconomic
        gdp_nominal = extract_value(get_nested(data, "macroeconomic", "gdp_nominal_usd"))
        gdp_growth = extract_value(get_nested(data, "macroeconomic", "gdp_real_growth_pct"))
        gdp_per_capita = extract_value(get_nested(data, "macroeconomic", "gdp_per_capita_usd"))
        inflation = extract_value(get_nested(data, "macroeconomic", "inflation_cpi_pct"))
        population = extract_value(get_nested(data, "demographic", "population_total"))

        # More derived
        energy_ind = extract_value(derived.get("energy_independence_index"))
        if energy_ind is None:
            energy_ind = layers_derived.get("energy_independence_index")

        pol_risk_bps = extract_value(derived.get("political_risk_premium_bps"))
        if pol_risk_bps is None:
            pol_risk_bps = layers_derived.get("political_risk_premium_bps")

        chokepoint = extract_value(derived.get("supply_chain_chokepoint_exposure"))
        if chokepoint is None:
            chokepoint = layers_derived.get("supply_chain_chokepoint_exposure")

        # Alerts
        alert_info = alert_lookup.get(code, {"count": 0, "max_severity": "none"})

        # Narrative headline (first sentence of executive_summary in narrative section)
        narrative_headline = None
        exec_summary = get_nested(data, "narrative", "executive_summary")
        if exec_summary and isinstance(exec_summary, str):
            # Take up to first period+space, or first 200 chars
            period_idx = exec_summary.find(". ")
            if period_idx > 0:
                narrative_headline = exec_summary[:period_idx + 1]
            else:
                narrative_headline = exec_summary[:200]

        # Military
        military = data.get("military", {})
        mil_exp_usd = extract_value(get_nested(data, "military", "military_expenditure_usd"))
        mil_exp_pct = extract_value(get_nested(data, "military", "military_expenditure_pct_gdp"))
        mil_trend_obj = military.get("military_expenditure_trend", {})
        mil_trend = extract_value(mil_trend_obj) if mil_trend_obj else None

        # Trade openness
        trade_openness = extract_value(get_nested(data, "economy", "trade_openness_pct"))

        # Political stability (raw 0-1 for map coloring)
        pol_stability_raw = pss
        if pol_stability_raw is not None and isinstance(pol_stability_raw, (int, float)):
            # WGI range is roughly -2.5 to +2.5, normalize to 0-1
            pol_stability_raw = max(0.0, min(1.0, (pol_stability_raw + 2.5) / 5.0))

        # Active flags count
        active_flags = get_nested(data, "metadata", "active_flags", default=[])
        flags_count = len(active_flags) if isinstance(active_flags, list) else 0

        last_updated = data.get("last_updated", NOW)

        summary = {
            "code": code,
            "name": name,
            "tier": tier,
            "region": data.get("region", "unknown"),
            "lat": lat,
            "lon": lon,
            "composite_national_power_index": cnpi,
            "overall_investment_risk_score": oir,
            "political_stability_score": pss,
            "gdp_nominal_usd": gdp_nominal,
            "gdp_real_growth_pct": gdp_growth,
            "gdp_per_capita_usd": gdp_per_capita,
            "inflation_rate_pct": inflation,
            "population": population,
            "energy_independence": energy_ind,
            "political_risk_premium_bps": pol_risk_bps,
            "supply_chain_chokepoint_exposure": chokepoint,
            "military_expenditure_usd": mil_exp_usd,
            "military_expenditure_pct_gdp": mil_exp_pct,
            "military_spending_trend": mil_trend,
            "political_stability": pol_stability_raw,
            "trade_openness_pct": trade_openness,
            "active_flags_count": flags_count,
            "alert_count": alert_info["count"],
            "max_alert_severity": alert_info["max_severity"],
            "narrative_headline": narrative_headline,
            "last_updated": last_updated,
            "investment_risk_score": oir,  # alias for backward compat
        }
        summaries.append(summary)

    output = {
        "generated_at": NOW,
        "run_id": RUN_ID,
        "countries": summaries
    }

    out_path = CHUNKS_DIR / "country-summary" / "all_countries_summary.json"
    save_json(out_path, output)
    print(f"  Generated summary for {len(summaries)} countries -> {out_path}")
    return len(summaries)


# ===========================================================================
# Step 3: Country Detail Chunks
# ===========================================================================
def step_3_country_detail():
    print("\n=== Step 3: Country Detail Chunks ===")
    detail_dir = CHUNKS_DIR / "country-detail"
    detail_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for cf in sorted(COUNTRIES_DIR.glob("*.json")):
        code = cf.stem
        dst = detail_dir / f"{code}.json"
        shutil.copy2(cf, dst)
        count += 1

    print(f"  Copied {count} country detail chunks -> {detail_dir}")
    return count


# ===========================================================================
# Step 4: Global Chunks
# ===========================================================================
def step_4_global_chunks():
    print("\n=== Step 4: Global Chunks ===")
    global_chunks_dir = CHUNKS_DIR / "global"
    global_chunks_dir.mkdir(parents=True, exist_ok=True)

    copied = []

    # Weekly briefing: find latest
    briefing_files = sorted(GLOBAL_DIR.glob("weekly_briefing_*.json"), reverse=True)
    if briefing_files:
        src = briefing_files[0]
        dst = global_chunks_dir / "weekly_briefing.json"
        shutil.copy2(src, dst)
        copied.append(f"weekly_briefing ({src.name})")
        print(f"  Copied {src.name} -> weekly_briefing.json")
    else:
        print("  Warning: no weekly_briefing file found")

    # Alert index
    alert_src = INDICES_DIR / "alert_index.json"
    if alert_src.exists():
        shutil.copy2(alert_src, global_chunks_dir / "alert_index.json")
        copied.append("alert_index")
        print(f"  Copied alert_index.json")
    else:
        print("  Warning: alert_index.json not found")

    # Event feed
    event_src = GLOBAL_DIR / "event_feed.json"
    if event_src.exists():
        shutil.copy2(event_src, global_chunks_dir / "event_feed.json")
        copied.append("event_feed")
        print(f"  Copied event_feed.json")
    else:
        print("  Warning: event_feed.json not found")

    # Global rankings
    rankings_src = GLOBAL_DIR / "global_rankings.json"
    if rankings_src.exists():
        shutil.copy2(rankings_src, global_chunks_dir / "global_rankings.json")
        copied.append("global_rankings")
        print(f"  Copied global_rankings.json")
    else:
        print("  Warning: global_rankings.json not found")

    print(f"  Global chunks: {len(copied)} files copied")
    return copied


# ===========================================================================
# Step 5: Article Chunks
# ===========================================================================
def step_5_article_chunks():
    print("\n=== Step 5: Article Chunks ===")
    build_script = PROJECT_ROOT / "agents" / "scripts" / "build_article_index.py"
    if build_script.exists():
        print(f"  Running {build_script}...")
        result = subprocess.run(
            [sys.executable, str(build_script)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"    {line}")
        if result.returncode != 0:
            print(f"  Warning: build_article_index.py exited with code {result.returncode}")
            if result.stderr:
                print(f"    stderr: {result.stderr.strip()}")
        return result.returncode == 0
    else:
        print("  build_article_index.py not found — skipping")
        return False


# ===========================================================================
# Step 6: Manifest
# ===========================================================================
def step_6_manifest(summary_count, detail_count, global_files):
    print("\n=== Step 6: Write Manifest ===")

    # Count files in each chunk subdirectory
    counts = {}
    for sub in CHUNKS_DIR.iterdir():
        if sub.is_dir():
            file_count = sum(1 for f in sub.rglob("*.json"))
            counts[sub.name] = file_count

    manifest = {
        "generated_at": NOW,
        "run_id": RUN_ID,
        "files": {
            "all_countries_summary": {
                "path": "data/chunks/country-summary/all_countries_summary.json",
                "countries": summary_count,
            },
            "country_detail": {
                "count": detail_count,
            },
            "weekly_briefing": {
                "last_modified": NOW,
            },
            "alert_index": {
                "last_modified": NOW,
            },
        },
        "chunks": {
            "country_summary": {
                "file": "country-summary/all_countries_summary.json",
                "country_count": summary_count,
            },
            "country_detail": {
                "directory": "country-detail/",
                "file_count": detail_count,
            },
            "global": {
                "directory": "global/",
                "files": global_files,
            },
        },
        "directory_file_counts": counts,
        "total_chunk_files": sum(counts.values()),
    }

    out_path = CHUNKS_DIR / "manifest.json"
    save_json(out_path, manifest)
    print(f"  Manifest written -> {out_path}")
    print(f"  Total chunk files: {manifest['total_chunk_files']}")
    return manifest


# ===========================================================================
# Step 7: Update Run Log
# ===========================================================================
def step_7_update_run_log(manifest):
    print("\n=== Step 7: Update Run Log ===")
    run_log_path = STAGING_DIR / "run_log.json"
    run_log = load_json(run_log_path) or {}

    # Add or update agent_16 entry
    agents = run_log.get("agents", [])

    # Check if agent_16 already recorded in the agents list
    a16_found = False
    for agent in agents:
        if agent.get("agent_id") == "agent_16":
            agent["status"] = "completed"
            agent["completed_at"] = NOW
            agent["notes"] = (
                f"Archive snapshot created. "
                f"{manifest['chunks']['country_summary']['country_count']} country summaries, "
                f"{manifest['chunks']['country_detail']['file_count']} country detail chunks, "
                f"{manifest['total_chunk_files']} total chunk files."
            )
            a16_found = True
            break

    if not a16_found:
        agents.append({
            "agent_id": "agent_16",
            "name": "archive_commit_preparer",
            "status": "completed",
            "started_at": NOW,
            "completed_at": NOW,
            "notes": (
                f"Archive snapshot created. "
                f"{manifest['chunks']['country_summary']['country_count']} country summaries, "
                f"{manifest['chunks']['country_detail']['file_count']} country detail chunks, "
                f"{manifest['total_chunk_files']} total chunk files."
            )
        })
        run_log["agents"] = agents

    # Also add top-level agent_16 field for quick access
    run_log["agent_16"] = {
        "status": "SUCCESS",
        "started_at": NOW,
        "completed_at": NOW,
        "archive_path": f"archive/{RUN_ID}/",
        "summary_countries": manifest["chunks"]["country_summary"]["country_count"],
        "detail_countries": manifest["chunks"]["country_detail"]["file_count"],
        "total_chunk_files": manifest["total_chunk_files"],
    }

    # Update overall status
    run_log["status"] = "completed"
    run_log["completed_at"] = NOW

    save_json(run_log_path, run_log)
    print(f"  Run log updated -> {run_log_path}")


# ===========================================================================
# Main
# ===========================================================================
def main():
    global RUN_ID
    parser = argparse.ArgumentParser(description="Agent 16 — Archive & Commit Preparer")
    parser.add_argument("--run-id", help="Run ID (e.g. 2026-W11). Default: auto from date.")
    args = parser.parse_args()
    if args.run_id:
        RUN_ID = args.run_id

    print(f"Agent 16 — Archive & Commit Preparer")
    print(f"Run ID: {RUN_ID} | Timestamp: {NOW}")
    print(f"Project root: {PROJECT_ROOT}")
    print("=" * 60)

    # Ensure chunk directories exist
    for subdir in ["country-summary", "country-detail", "global", "global/articles",
                    "relations", "timeseries", "supranational"]:
        (CHUNKS_DIR / subdir).mkdir(parents=True, exist_ok=True)

    archive_path = step_1_archive()
    summary_count = step_2_country_summary()
    detail_count = step_3_country_detail()
    global_files = step_4_global_chunks()
    step_5_article_chunks()
    manifest = step_6_manifest(summary_count, detail_count, global_files)
    step_7_update_run_log(manifest)

    print("\n" + "=" * 60)
    print("Agent 16 complete. Summary:")
    print(f"  Archive:         {archive_path}")
    print(f"  Country summary: {summary_count} countries")
    print(f"  Country detail:  {detail_count} files")
    print(f"  Global chunks:   {len(global_files)} files")
    print(f"  Total chunks:    {manifest['total_chunk_files']} files")
    print(f"  Status:          SUCCESS")
    print("\nNo git commands executed. Files are ready for commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
