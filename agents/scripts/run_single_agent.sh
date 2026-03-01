#!/usr/bin/env bash
# =============================================================================
# Stratoterra Single Agent Runner
# Usage: ./agents/scripts/run_single_agent.sh <agent_number>
#
# Prints the agent prompt (with env vars substituted) and logs the start
# to run_log.json. Use this to re-run a specific agent after a failure.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${CYAN}[INFO]${RESET}  $*"; }
error() { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
fatal() { error "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
  echo "Usage: $0 <agent_number>"
  echo ""
  echo "Agent numbers and names:"
  echo "  01  Official Statistics Gatherer"
  echo "  02  Financial Data Gatherer"
  echo "  03  News & Events Gatherer"
  echo "  04  Trade & Sanctions Gatherer"
  echo "  05  Military & Conflict Gatherer"
  echo "  06  Political & Regulatory Gatherer"
  echo "  07  Fact Extractor & Structurer"
  echo "  08  Cross-Validator & Anomaly Detector"
  echo "  09  Data Integrator"
  echo "  10  Trend Estimator"
  echo "  11  Derived Metrics Calculator"
  echo "  12  Alert Generator"
  echo "  13  Country Profile Synthesizer"
  echo "  14  Weekly Briefing Generator"
  echo "  15  Data Quality Reporter"
  echo "  16  Archive & Commit Preparer"
  exit 1
}

# ---------------------------------------------------------------------------
# Agent number to prompt file mapping
# ---------------------------------------------------------------------------
get_prompt_file() {
  local num="$1"
  case "${num}" in
    01|1)  echo "agent_01_official_stats.md" ;;
    02|2)  echo "agent_02_financial_data.md" ;;
    03|3)  echo "agent_03_news_events.md" ;;
    04|4)  echo "agent_04_trade_sanctions.md" ;;
    05|5)  echo "agent_05_military_conflict.md" ;;
    06|6)  echo "agent_06_political_regulatory.md" ;;
    07|7)  echo "agent_07_processor.md" ;;
    08|8)  echo "agent_08_validator.md" ;;
    09|9)  echo "agent_09_integrator.md" ;;
    10)    echo "agent_10_trends.md" ;;
    11)    echo "agent_11_derived_metrics.md" ;;
    12)    echo "agent_12_alerts.md" ;;
    13)    echo "agent_13_narratives.md" ;;
    14)    echo "agent_14_briefing.md" ;;
    15)    echo "agent_15_quality.md" ;;
    16)    echo "agent_16_archive_commit.md" ;;
    *)     echo "" ;;
  esac
}

get_agent_id() {
  local num="$1"
  printf "agent_%02d" "${num}" 2>/dev/null || echo "agent_${num}"
}

get_config_file() {
  local num="$1"
  case "${num}" in
    01|1)  echo "agent_01_official_stats.json" ;;
    02|2)  echo "agent_02_financial_data.json" ;;
    03|3)  echo "agent_03_news_events.json" ;;
    04|4)  echo "agent_04_trade_sanctions.json" ;;
    05|5)  echo "agent_05_military_conflict.json" ;;
    06|6)  echo "agent_06_political_regulatory.json" ;;
    07|7)  echo "agent_07_processor.json" ;;
    08|8)  echo "agent_08_validator.json" ;;
    09|9)  echo "agent_09_integrator.json" ;;
    10)    echo "agent_10_trends.json" ;;
    11)    echo "agent_11_derived_metrics.json" ;;
    12)    echo "agent_12_alerts.json" ;;
    13)    echo "agent_13_narratives.json" ;;
    14)    echo "agent_14_briefing.json" ;;
    15)    echo "agent_15_quality.json" ;;
    16)    echo "agent_16_archive.json" ;;
    *)     echo "" ;;
  esac
}

# ---------------------------------------------------------------------------
# Substitute template variables in prompt file
# ---------------------------------------------------------------------------
render_prompt() {
  local prompt_file="$1"
  local content
  content=$(cat "${prompt_file}")

  content="${content//\{RUN_ID\}/${RUN_ID}}"
  content="${content//\{CURRENT_DATE\}/${CURRENT_DATE}}"
  content="${content//\{DATE\}/${CURRENT_DATE}}"
  content="${content//\{YEAR\}/${YEAR}}"
  content="${content//\{WEEK_NUMBER\}/${WEEK_NUMBER}}"
  content="${content//\{ISO_TIMESTAMP\}/${ISO_TIMESTAMP}}"

  echo "${content}"
}

# ---------------------------------------------------------------------------
# Log agent start to run_log.json
# ---------------------------------------------------------------------------
log_agent_start() {
  local agent_id="$1"
  local run_log="${PROJECT_ROOT}/staging/run_log.json"

  if [[ ! -f "${run_log}" ]]; then
    info "run_log.json not found, creating it"
    cat > "${run_log}" <<EOF
{
  "run_id": "${RUN_ID}",
  "started_at": "${ISO_TIMESTAMP}",
  "status": "in_progress",
  "agents": []
}
EOF
  fi

  info "Logged ${agent_id} start to staging/run_log.json"

  # Append a start record if jq is available
  if command -v jq &>/dev/null; then
    local tmp
    tmp=$(mktemp)
    jq --arg id "${agent_id}" \
       --arg ts "${ISO_TIMESTAMP}" \
       '.agents += [{"agent_id": $id, "status": "started", "started_at": $ts}]' \
       "${run_log}" > "${tmp}" && mv "${tmp}" "${run_log}"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  local agent_num="${1:-}"
  if [[ -z "${agent_num}" ]]; then
    usage
  fi

  # Set up environment variables
  CURRENT_DATE="$(date -u +%Y-%m-%d)"
  YEAR="$(date -u +%Y)"
  WEEK_NUMBER="$(date -u +%V)"
  RUN_ID="${YEAR}-W${WEEK_NUMBER}"
  ISO_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # Load .env if present
  local env_file="${PROJECT_ROOT}/.env"
  if [[ -f "${env_file}" ]]; then
    set -o allexport
    # shellcheck disable=SC1090
    source "${env_file}"
    set +o allexport
  fi

  local prompt_filename
  prompt_filename=$(get_prompt_file "${agent_num}")
  if [[ -z "${prompt_filename}" ]]; then
    fatal "Unknown agent number: ${agent_num}. Use 01-16."
  fi

  local prompt_path="${PROJECT_ROOT}/agents/prompts/${prompt_filename}"
  if [[ ! -f "${prompt_path}" ]]; then
    fatal "Prompt file not found: ${prompt_path}"
  fi

  local config_filename
  config_filename=$(get_config_file "${agent_num}")
  local config_path="${PROJECT_ROOT}/agents/config/${config_filename}"

  local agent_id
  agent_id=$(get_agent_id "${agent_num}")

  echo ""
  echo -e "${BOLD}${CYAN}Stratoterra — Single Agent Runner${RESET}"
  echo -e "Agent:     ${BOLD}${agent_id}${RESET} (${prompt_filename})"
  echo -e "Run ID:    ${BOLD}${RUN_ID}${RESET}"
  echo -e "Date:      ${CURRENT_DATE}"
  echo ""

  # Show config summary if available
  if [[ -f "${config_path}" ]] && command -v jq &>/dev/null; then
    local name phase timeout
    name=$(jq -r '.name' "${config_path}" 2>/dev/null || echo "unknown")
    phase=$(jq -r '.phase_name' "${config_path}" 2>/dev/null || echo "unknown")
    timeout=$(jq -r '.timeout_minutes' "${config_path}" 2>/dev/null || echo "unknown")
    echo -e "Name:      ${name}"
    echo -e "Phase:     ${phase}"
    echo -e "Timeout:   ${timeout} minutes"
    echo ""
  fi

  log_agent_start "${agent_id}"

  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${YELLOW}Paste the following prompt into your Claude Code MAX session:${RESET}"
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""

  render_prompt "${prompt_path}"

  echo ""
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""
  info "After the agent completes, validate outputs with:"
  echo "  ./agents/scripts/validate_staging.sh <phase_number>"
}

main "$@"
