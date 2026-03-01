#!/usr/bin/env bash
# =============================================================================
# Stratoterra Weekly Pipeline Entry Point
# Usage: ./agents/scripts/run_weekly_update.sh
#
# This script validates prerequisites, sets up the environment, initializes
# the run log, and prints the banner before launching the pipeline.
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

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
fatal()   { error "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
print_banner() {
  echo ""
  echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}${CYAN}║         STRATOTERRA WEEKLY PIPELINE                         ║${RESET}"
  echo -e "${BOLD}${CYAN}║         Geopolitical Intelligence Model Update               ║${RESET}"
  echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
  echo ""
  echo -e "  Run ID:   ${BOLD}${RUN_ID}${RESET}"
  echo -e "  Date:     ${BOLD}${CURRENT_DATE}${RESET}"
  echo -e "  Root:     ${PROJECT_ROOT}"
  echo ""
}

# ---------------------------------------------------------------------------
# Compute run identifiers
# ---------------------------------------------------------------------------
CURRENT_DATE="$(date -u +%Y-%m-%d)"
YEAR="$(date -u +%Y)"
WEEK_NUMBER="$(date -u +%V)"
RUN_ID="${YEAR}-W${WEEK_NUMBER}"
ISO_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

export CURRENT_DATE YEAR WEEK_NUMBER RUN_ID ISO_TIMESTAMP

# ---------------------------------------------------------------------------
# Check for .env file and load it
# ---------------------------------------------------------------------------
check_env_file() {
  local env_file="${PROJECT_ROOT}/.env"
  if [[ ! -f "${env_file}" ]]; then
    warn ".env file not found at ${env_file}"
    warn "Copy .env.example to .env and fill in your API keys."
    warn "Proceeding without API keys — some data collection may fail."
    return
  fi

  info "Loading environment from .env"
  # shellcheck disable=SC1090
  set -o allexport
  source "${env_file}"
  set +o allexport
  success "Environment loaded"
}

# ---------------------------------------------------------------------------
# Check required tools
# ---------------------------------------------------------------------------
check_prerequisites() {
  info "Checking prerequisites..."
  local missing=0

  for cmd in python3 git jq curl; do
    if command -v "${cmd}" &>/dev/null; then
      success "${cmd} found"
    else
      warn "${cmd} not found (some features may be limited)"
    fi
  done

  # Check project structure
  for dir in \
    "${PROJECT_ROOT}/data/indices" \
    "${PROJECT_ROOT}/data/countries" \
    "${PROJECT_ROOT}/data/metadata" \
    "${PROJECT_ROOT}/agents/config" \
    "${PROJECT_ROOT}/agents/prompts"; do
    if [[ -d "${dir}" ]]; then
      success "Directory exists: ${dir#${PROJECT_ROOT}/}"
    else
      error "Missing directory: ${dir#${PROJECT_ROOT}/}"
      missing=1
    fi
  done

  # Check required data files
  if [[ ! -f "${PROJECT_ROOT}/data/indices/country_list.json" ]]; then
    warn "country_list.json not found — Agent 1 will fail without it"
    warn "Initialize with setup_project.sh or create data/indices/country_list.json"
  else
    success "country_list.json found"
  fi

  if [[ "${missing}" -eq 1 ]]; then
    fatal "Missing required directories. Run setup_project.sh first."
  fi
}

# ---------------------------------------------------------------------------
# Create staging directories
# ---------------------------------------------------------------------------
create_staging_dirs() {
  info "Creating staging directories for run ${RUN_ID}..."
  mkdir -p \
    "${PROJECT_ROOT}/staging/raw_collected" \
    "${PROJECT_ROOT}/staging/processed" \
    "${PROJECT_ROOT}/staging/validated" \
    "${PROJECT_ROOT}/staging/trends"
  success "Staging directories ready"
}

# ---------------------------------------------------------------------------
# Initialize run log
# ---------------------------------------------------------------------------
initialize_run_log() {
  local run_log="${PROJECT_ROOT}/staging/run_log.json"
  info "Initializing run log at staging/run_log.json"

  cat > "${run_log}" <<EOF
{
  "run_id": "${RUN_ID}",
  "started_at": "${ISO_TIMESTAMP}",
  "status": "started",
  "current_date": "${CURRENT_DATE}",
  "project_root": "${PROJECT_ROOT}",
  "agents": []
}
EOF
  success "Run log initialized"
}

# ---------------------------------------------------------------------------
# Print pipeline summary
# ---------------------------------------------------------------------------
print_pipeline_summary() {
  echo ""
  echo -e "${BOLD}Pipeline Phases:${RESET}"
  echo "  Phase 1 — GATHER      (Agents 01-06)   60-120 min"
  echo "  Phase 2 — PROCESS     (Agent  07)       20-30 min"
  echo "  Phase 3 — VALIDATE    (Agent  08)       15-20 min  ← Human review"
  echo "  Phase 4 — INTEGRATE   (Agent  09)        5-10 min"
  echo "  Phase 5 — ANALYZE     (Agents 10-12)    50-75 min"
  echo "  Phase 6 — SYNTHESIZE  (Agents 13-14)    30-45 min"
  echo "  Phase 7 — FINALIZE    (Agents 15-16)     7-10 min  ← Human review"
  echo ""
  echo -e "${YELLOW}Human review points:${RESET}"
  echo "  After Agent 08: Review escalated validation items (~30 min)"
  echo "  After Agent 15: Review quality report (~15 min)"
  echo ""
  echo -e "${BOLD}To run a single agent:${RESET}"
  echo "  ./agents/scripts/run_single_agent.sh <agent_number>"
  echo ""
  echo -e "${BOLD}Prompt files are in:${RESET}"
  echo "  agents/prompts/"
  echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  check_env_file
  check_prerequisites
  create_staging_dirs
  initialize_run_log
  print_banner
  print_pipeline_summary

  echo -e "${GREEN}${BOLD}Pipeline environment ready.${RESET}"
  echo ""
  echo "Next step: Open a Claude Code MAX session and paste the orchestrator prompt:"
  echo "  agents/prompts/orchestrator.md"
  echo ""
  echo "Run ID: ${RUN_ID}"
  echo "Started: ${ISO_TIMESTAMP}"
}

main "$@"
