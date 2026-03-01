#!/usr/bin/env bash
# =============================================================================
# Stratoterra Chunk Generator
# Usage: ./agents/scripts/generate_chunks.sh
#
# Reads country and relation files from /data/ and generates UI-optimized
# chunk files in /data/chunks/. Run this manually or as part of Agent 16.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
fatal()   { error "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------
check_prereqs() {
  if ! command -v python3 &>/dev/null; then
    fatal "python3 is required but not found."
  fi
}

# ---------------------------------------------------------------------------
# Python chunk generation script (inline)
# ---------------------------------------------------------------------------
run_chunk_generator() {
  local iso_timestamp
  iso_timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  python3 - "${PROJECT_ROOT}" "${iso_timestamp}" <<'PYEOF'
import sys
import json
import os
import glob
from pathlib import Path

project_root = sys.argv[1]
iso_timestamp = sys.argv[2]

data_dir    = Path(project_root) / "data"
chunks_dir  = data_dir / "chunks"
country_dir = data_dir / "countries"
relation_dir = data_dir / "relations"

# Ensure output directories exist
(chunks_dir / "country-summary").mkdir(parents=True, exist_ok=True)
(chunks_dir / "country-detail").mkdir(parents=True, exist_ok=True)
(chunks_dir / "relations").mkdir(parents=True, exist_ok=True)
(chunks_dir / "global").mkdir(parents=True, exist_ok=True)
(chunks_dir / "supranational").mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 1. Generate all_countries_summary.json
# -------------------------------------------------------------------------
print("[INFO]  Generating country summary chunk...")

SUMMARY_FIELDS = [
    "code", "name", "tier", "lat", "lon",
]

DERIVED_FIELDS = {
    "composite_national_power_index":  ["derived", "composite_national_power_index"],
    "overall_investment_risk_score":   ["derived", "overall_investment_risk_score"],
    "political_stability_score":       ["political", "political_stability_score"],
    "gdp_nominal_usd":                 ["macroeconomic", "gdp_nominal_usd"],
    "gdp_real_growth_rate_pct":        ["macroeconomic", "gdp_real_growth_rate_pct"],
    "last_updated":                    ["metadata", "last_updated"],
}

def safe_get(d, *keys, default=None):
    """Navigate nested dict, return default if any key is missing."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, {})
    return d if d != {} else default

summaries = []
country_files = sorted(glob.glob(str(country_dir / "*.json")))

for filepath in country_files:
    try:
        with open(filepath) as f:
            country = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN]  Skipping {filepath}: {e}")
        continue

    summary = {}
    # Top-level fields
    for field in SUMMARY_FIELDS:
        if field in country:
            summary[field] = country[field]

    # Nested derived fields
    for target_key, path in DERIVED_FIELDS.items():
        val = safe_get(country, *path)
        if val is not None:
            summary[target_key] = val

    # Alert summary
    alerts = country.get("metadata", {}).get("active_alerts", [])
    summary["active_alerts_count"] = len(alerts)
    severities = {"critical": 3, "warning": 2, "watch": 1}
    if alerts:
        top = max(alerts, key=lambda a: severities.get(a.get("severity", "watch"), 0))
        summary["top_alert_severity"] = top.get("severity", "watch")
    else:
        summary["top_alert_severity"] = None

    # Narrative headline (first sentence of executive_summary)
    narrative = country.get("narrative", {})
    exec_summary = narrative.get("executive_summary", "")
    if exec_summary:
        headline = exec_summary.split(".")[0].strip() + "."
        summary["narrative_headline"] = headline
    else:
        summary["narrative_headline"] = None

    summaries.append(summary)

output = {
    "generated_at": iso_timestamp,
    "total_countries": len(summaries),
    "countries": summaries
}

summary_path = chunks_dir / "country-summary" / "all_countries_summary.json"
with open(summary_path, "w") as f:
    json.dump(output, f, indent=2)

size_kb = summary_path.stat().st_size / 1024
print(f"[OK]    all_countries_summary.json written ({len(summaries)} countries, {size_kb:.1f}KB)")

# -------------------------------------------------------------------------
# 2. Generate per-country detail chunks
# -------------------------------------------------------------------------
print("[INFO]  Generating country detail chunks...")
detail_count = 0
for filepath in country_files:
    try:
        with open(filepath) as f:
            country = json.load(f)
    except (json.JSONDecodeError, OSError):
        continue
    code = country.get("code", Path(filepath).stem)
    dest = chunks_dir / "country-detail" / f"{code}.json"
    with open(dest, "w") as f:
        json.dump(country, f, indent=2)
    detail_count += 1

print(f"[OK]    {detail_count} country detail chunks written")

# -------------------------------------------------------------------------
# 3. Generate relation chunks
# -------------------------------------------------------------------------
print("[INFO]  Generating relation chunks...")
relation_files = sorted(glob.glob(str(relation_dir / "*.json")))
relation_count = 0
for filepath in relation_files:
    try:
        with open(filepath) as f:
            rel = json.load(f)
    except (json.JSONDecodeError, OSError):
        continue
    pair = Path(filepath).stem
    dest = chunks_dir / "relations" / f"{pair}.json"
    with open(dest, "w") as f:
        json.dump(rel, f, indent=2)
    relation_count += 1

print(f"[OK]    {relation_count} relation chunks written")

# -------------------------------------------------------------------------
# 4. Copy global files
# -------------------------------------------------------------------------
print("[INFO]  Copying global files to chunks/global/...")
global_dir = data_dir / "global"
if global_dir.exists():
    for src in global_dir.glob("*.json"):
        # Use latest weekly_briefing if multiple exist
        dest_name = src.name
        if dest_name.startswith("weekly_briefing_"):
            dest_name = "weekly_briefing.json"
        dest = chunks_dir / "global" / dest_name
        with open(src) as f:
            content = json.load(f)
        with open(dest, "w") as f:
            json.dump(content, f, indent=2)
    print(f"[OK]    Global files copied")

# Also copy alert_index
alert_index_src = data_dir / "indices" / "alert_index.json"
if alert_index_src.exists():
    with open(alert_index_src) as f:
        content = json.load(f)
    with open(chunks_dir / "global" / "alert_index.json", "w") as f:
        json.dump(content, f, indent=2)
    print("[OK]    alert_index.json copied to chunks/global/")

# -------------------------------------------------------------------------
# 5. Write manifest
# -------------------------------------------------------------------------
print("[INFO]  Writing chunks/manifest.json...")

def dir_count(path):
    return len(list(path.glob("*.json"))) if path.exists() else 0

summary_size = (chunks_dir / "country-summary" / "all_countries_summary.json").stat().st_size \
    if (chunks_dir / "country-summary" / "all_countries_summary.json").exists() else 0

manifest = {
    "generated_at": iso_timestamp,
    "files": {
        "all_countries_summary": {
            "path": "data/chunks/country-summary/all_countries_summary.json",
            "size_bytes": summary_size,
            "countries": len(summaries),
            "last_modified": iso_timestamp
        },
        "country_detail": {
            "count": dir_count(chunks_dir / "country-detail"),
            "path": "data/chunks/country-detail/",
            "last_modified": iso_timestamp
        },
        "relations": {
            "count": dir_count(chunks_dir / "relations"),
            "path": "data/chunks/relations/",
            "last_modified": iso_timestamp
        },
        "global": {
            "count": dir_count(chunks_dir / "global"),
            "path": "data/chunks/global/",
            "last_modified": iso_timestamp
        }
    }
}

with open(chunks_dir / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("[OK]    manifest.json written")
print(f"\n[INFO]  Chunk generation complete.")
print(f"        Countries: {len(summaries)}")
print(f"        Relations: {relation_count}")
print(f"        Summary size: {summary_size/1024:.1f}KB")
PYEOF
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  echo ""
  echo -e "${BOLD}${CYAN}Stratoterra Chunk Generator${RESET}"
  echo "Project root: ${PROJECT_ROOT}"
  echo ""

  check_prereqs

  local country_count
  country_count=$(ls "${PROJECT_ROOT}/data/countries/"*.json 2>/dev/null | wc -l || echo 0)

  if [[ "${country_count}" -eq 0 ]]; then
    error "No country files found in data/countries/. Run the pipeline first."
    echo "If this is a fresh install, generate seed data or run Agents 01-09 first."
    exit 1
  fi

  info "Found ${country_count} country files"
  run_chunk_generator

  echo ""
  success "Done. Chunks written to data/chunks/"
}

main "$@"
