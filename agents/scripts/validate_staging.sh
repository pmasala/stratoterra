#!/usr/bin/env bash
# =============================================================================
# Stratoterra Staging Validator
# Usage: ./agents/scripts/validate_staging.sh <phase_number>
#
# Validates that expected staging files exist after each pipeline phase.
# Phase numbers: 1 (Gather), 2 (Process), 3 (Validate), 4 (Integrate),
#                5 (Analyze), 6 (Synthesize), 7 (Finalize)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

pass()  { echo -e "  ${GREEN}[PASS]${RESET} $*"; }
fail()  { echo -e "  ${RED}[FAIL]${RESET} $*"; FAILURES=$((FAILURES + 1)); }
warn()  { echo -e "  ${YELLOW}[WARN]${RESET} $*"; }
info()  { echo -e "  ${BOLD}[INFO]${RESET} $*"; }

FAILURES=0

# ---------------------------------------------------------------------------
# Date detection
# ---------------------------------------------------------------------------
DATE="${CURRENT_DATE:-$(date -u +%Y-%m-%d)}"

# ---------------------------------------------------------------------------
# File existence check helper
# ---------------------------------------------------------------------------
check_file() {
  local label="$1"
  local filepath="$2"
  local full_path="${PROJECT_ROOT}/${filepath}"

  if [[ -f "${full_path}" ]]; then
    local size
    size=$(du -h "${full_path}" 2>/dev/null | cut -f1 || echo "?")
    pass "${label} (${size})"
  else
    # Try glob for date-templated files
    local pattern="${full_path/\{DATE\}/*}"
    local found
    found=$(ls "${pattern}" 2>/dev/null | head -1 || true)
    if [[ -n "${found}" ]]; then
      local size
      size=$(du -h "${found}" 2>/dev/null | cut -f1 || echo "?")
      pass "${label} → $(basename "${found}") (${size})"
    else
      fail "${label}: not found at ${filepath}"
    fi
  fi
}

# ---------------------------------------------------------------------------
# Check minimum file size (non-empty)
# ---------------------------------------------------------------------------
check_file_nonempty() {
  local label="$1"
  local filepath="$2"
  local full_path="${PROJECT_ROOT}/${filepath}"

  # Resolve glob
  local pattern="${full_path/\{DATE\}/*}"
  local found
  found=$(ls "${pattern}" 2>/dev/null | head -1 || true)
  if [[ -z "${found}" ]]; then
    found="${full_path}"
  fi

  if [[ -f "${found}" ]]; then
    local size_bytes
    size_bytes=$(wc -c < "${found}" 2>/dev/null || echo 0)
    if [[ "${size_bytes}" -gt 10 ]]; then
      pass "${label} (non-empty, ${size_bytes} bytes)"
    else
      fail "${label}: file exists but appears empty (${size_bytes} bytes)"
    fi
  else
    fail "${label}: not found"
  fi
}

# ---------------------------------------------------------------------------
# Phase validation functions
# ---------------------------------------------------------------------------

validate_phase_1() {
  echo -e "\n${BOLD}Phase 1 — GATHER: Checking raw_collected files${RESET}"
  check_file_nonempty "Agent 01 output (official_stats)" "staging/raw_collected/official_stats_${DATE}.json"
  check_file_nonempty "Agent 02 output (financial_data)" "staging/raw_collected/financial_data_${DATE}.json"
  check_file_nonempty "Agent 03 output (news_events)"   "staging/raw_collected/news_events_${DATE}.json"
  check_file_nonempty "Agent 04 output (trade_sanctions)" "staging/raw_collected/trade_sanctions_${DATE}.json"
  check_file_nonempty "Agent 05 output (military_conflict)" "staging/raw_collected/military_conflict_${DATE}.json"
  check_file_nonempty "Agent 06 output (political_regulatory)" "staging/raw_collected/political_regulatory_${DATE}.json"
}

validate_phase_2() {
  echo -e "\n${BOLD}Phase 2 — PROCESS: Checking processed files${RESET}"
  check_file_nonempty "Agent 07 output (factor_updates)" "staging/processed/factor_updates_${DATE}.json"
}

validate_phase_3() {
  echo -e "\n${BOLD}Phase 3 — VALIDATE: Checking validated files${RESET}"
  check_file_nonempty "Agent 08 output (validated_updates)" "staging/validated/validated_updates_${DATE}.json"
  # escalation_report is optional (only if there are escalations)
  if ls "${PROJECT_ROOT}/staging/validated/escalation_report_"*.json 2>/dev/null | head -1 | grep -q .; then
    pass "Agent 08 escalation_report: present"
  else
    warn "Agent 08 escalation_report: not present (no escalations, or check manually)"
  fi
}

validate_phase_4() {
  echo -e "\n${BOLD}Phase 4 — INTEGRATE: Checking /data/ was updated${RESET}"
  check_file_nonempty "last_update.json" "data/metadata/last_update.json"
  check_file_nonempty "update_log.json"  "data/metadata/update_log.json"
  # Check that at least one country file exists
  local country_count
  country_count=$(ls "${PROJECT_ROOT}/data/countries/"*.json 2>/dev/null | wc -l || echo 0)
  if [[ "${country_count}" -gt 0 ]]; then
    pass "Country files in /data/countries/ (${country_count} files)"
  else
    fail "No country files found in /data/countries/"
  fi
}

validate_phase_5() {
  echo -e "\n${BOLD}Phase 5 — ANALYZE: Checking analysis outputs${RESET}"
  check_file_nonempty "Agent 10 output (trend_estimates)" "staging/trends/trend_estimates_${DATE}.json"
  check_file_nonempty "Agent 11 output (global_rankings)" "data/global/global_rankings.json"
  check_file_nonempty "Agent 12 output (alert_index)"    "data/indices/alert_index.json"
  check_file_nonempty "Agent 12 output (event_feed)"     "data/global/event_feed.json"
}

validate_phase_6() {
  echo -e "\n${BOLD}Phase 6 — SYNTHESIZE: Checking narrative and briefing${RESET}"
  check_file_nonempty "Agent 14 output (weekly_briefing)" "data/global/weekly_briefing_${DATE}.json"
  # Spot-check a few country files for narrative section presence
  local sample_country
  sample_country=$(ls "${PROJECT_ROOT}/data/countries/"*.json 2>/dev/null | head -1 || true)
  if [[ -n "${sample_country}" ]] && command -v python3 &>/dev/null; then
    if python3 -c "import json,sys; d=json.load(open('${sample_country}')); assert 'narrative' in d" 2>/dev/null; then
      pass "Country narrative section present in $(basename "${sample_country}")"
    else
      warn "Could not verify narrative section in sample country file"
    fi
  fi
}

validate_phase_7() {
  echo -e "\n${BOLD}Phase 7 — FINALIZE: Checking quality report and chunks${RESET}"
  check_file_nonempty "Agent 15 output (quality_report)" "data/metadata/quality_report_${DATE}.json"
  check_file_nonempty "Agent 16 output (chunks manifest)" "data/chunks/manifest.json"
  check_file_nonempty "Agent 16 output (all_countries_summary)" "data/chunks/country-summary/all_countries_summary.json"
  check_file_nonempty "Agent 16 output (relation_index)" "data/indices/relation_index.json"
  # Check archive snapshot
  if ls "${PROJECT_ROOT}/archive/"*/last_update_snapshot.json 2>/dev/null | head -1 | grep -q .; then
    pass "Archive snapshot present"
  else
    warn "No archive snapshot found (Agent 16 may not have run yet)"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
usage() {
  echo "Usage: $0 <phase_number>"
  echo ""
  echo "Phase numbers:"
  echo "  1  Gather       — Agents 01-06 raw_collected output"
  echo "  2  Process      — Agent 07 processed output"
  echo "  3  Validate     — Agent 08 validated output"
  echo "  4  Integrate    — Agent 09 /data/ updates"
  echo "  5  Analyze      — Agents 10-12 analysis output"
  echo "  6  Synthesize   — Agents 13-14 narrative and briefing"
  echo "  7  Finalize     — Agents 15-16 quality report and chunks"
  echo "  all             — Run all phase checks"
  exit 1
}

main() {
  local phase="${1:-}"
  if [[ -z "${phase}" ]]; then
    usage
  fi

  echo ""
  echo -e "${BOLD}Stratoterra Staging Validator${RESET}"
  echo "Date: ${DATE}"
  echo "Project root: ${PROJECT_ROOT}"

  case "${phase}" in
    1)   validate_phase_1 ;;
    2)   validate_phase_2 ;;
    3)   validate_phase_3 ;;
    4)   validate_phase_4 ;;
    5)   validate_phase_5 ;;
    6)   validate_phase_6 ;;
    7)   validate_phase_7 ;;
    all)
      validate_phase_1
      validate_phase_2
      validate_phase_3
      validate_phase_4
      validate_phase_5
      validate_phase_6
      validate_phase_7
      ;;
    *)   usage ;;
  esac

  echo ""
  if [[ "${FAILURES}" -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}All checks passed.${RESET}"
    exit 0
  else
    echo -e "${RED}${BOLD}${FAILURES} check(s) failed.${RESET}"
    exit 1
  fi
}

main "$@"
