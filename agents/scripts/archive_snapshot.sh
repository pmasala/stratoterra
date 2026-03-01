#!/usr/bin/env bash
# =============================================================================
# Stratoterra Archive Snapshot Creator
# Usage: ./agents/scripts/archive_snapshot.sh [RUN_ID]
#
# Creates a lightweight archive snapshot in archive/{RUN_ID}/.
# The snapshot contains metadata; full data history lives in git.
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
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
fatal()   { error "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Determine Run ID
# ---------------------------------------------------------------------------
CURRENT_DATE="$(date -u +%Y-%m-%d)"
YEAR="$(date -u +%Y)"
WEEK_NUMBER="$(date -u +%V)"
ISO_TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ -n "${1:-}" ]]; then
  RUN_ID="$1"
  info "Using provided Run ID: ${RUN_ID}"
else
  RUN_ID="${YEAR}-W${WEEK_NUMBER}"
  info "Using computed Run ID: ${RUN_ID}"
fi

ARCHIVE_DIR="${PROJECT_ROOT}/archive/${RUN_ID}"

# ---------------------------------------------------------------------------
# Create archive directory
# ---------------------------------------------------------------------------
create_archive_dir() {
  if [[ -d "${ARCHIVE_DIR}" ]]; then
    warn "Archive directory already exists: archive/${RUN_ID}/"
    read -rp "Overwrite? [y/N]: " confirm
    if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
      info "Aborted."
      exit 0
    fi
  fi
  mkdir -p "${ARCHIVE_DIR}"
  success "Created archive/${RUN_ID}/"
}

# ---------------------------------------------------------------------------
# Copy metadata snapshot
# ---------------------------------------------------------------------------
copy_metadata() {
  local src="${PROJECT_ROOT}/data/metadata/last_update.json"
  local dst="${ARCHIVE_DIR}/last_update_snapshot.json"

  if [[ -f "${src}" ]]; then
    cp "${src}" "${dst}"
    success "Copied last_update.json → archive/${RUN_ID}/last_update_snapshot.json"
  else
    warn "data/metadata/last_update.json not found, creating placeholder"
    cat > "${dst}" <<EOF
{
  "note": "last_update.json was not found at archive time",
  "run_id": "${RUN_ID}",
  "archived_at": "${ISO_TIMESTAMP}"
}
EOF
  fi
}

# ---------------------------------------------------------------------------
# Copy quality report if it exists
# ---------------------------------------------------------------------------
copy_quality_report() {
  local src
  src=$(ls "${PROJECT_ROOT}/data/metadata/quality_report_"*.json 2>/dev/null | sort | tail -1 || true)
  if [[ -n "${src}" ]]; then
    cp "${src}" "${ARCHIVE_DIR}/quality_report_snapshot.json"
    success "Copied quality report → archive/${RUN_ID}/quality_report_snapshot.json"
  else
    warn "No quality report found, skipping"
  fi
}

# ---------------------------------------------------------------------------
# Copy run log
# ---------------------------------------------------------------------------
copy_run_log() {
  local src="${PROJECT_ROOT}/staging/run_log.json"
  if [[ -f "${src}" ]]; then
    cp "${src}" "${ARCHIVE_DIR}/run_log_snapshot.json"
    success "Copied run_log.json → archive/${RUN_ID}/run_log_snapshot.json"
  else
    warn "staging/run_log.json not found, skipping"
  fi
}

# ---------------------------------------------------------------------------
# Copy alert index snapshot
# ---------------------------------------------------------------------------
copy_alert_index() {
  local src="${PROJECT_ROOT}/data/indices/alert_index.json"
  if [[ -f "${src}" ]]; then
    cp "${src}" "${ARCHIVE_DIR}/alert_index_snapshot.json"
    success "Copied alert_index.json → archive/${RUN_ID}/alert_index_snapshot.json"
  else
    warn "data/indices/alert_index.json not found, skipping"
  fi
}

# ---------------------------------------------------------------------------
# Write archive manifest
# ---------------------------------------------------------------------------
write_archive_manifest() {
  local manifest="${ARCHIVE_DIR}/archive_manifest.json"

  # Count countries and relations
  local country_count
  country_count=$(ls "${PROJECT_ROOT}/data/countries/"*.json 2>/dev/null | wc -l || echo 0)
  local relation_count
  relation_count=$(ls "${PROJECT_ROOT}/data/relations/"*.json 2>/dev/null | wc -l || echo 0)

  # Get git commit hash if in a git repo
  local git_hash="none"
  if command -v git &>/dev/null && git -C "${PROJECT_ROOT}" rev-parse HEAD &>/dev/null 2>&1; then
    git_hash=$(git -C "${PROJECT_ROOT}" rev-parse --short HEAD 2>/dev/null || echo "none")
  fi

  cat > "${manifest}" <<EOF
{
  "run_id": "${RUN_ID}",
  "archived_at": "${ISO_TIMESTAMP}",
  "current_date": "${CURRENT_DATE}",
  "git_commit": "${git_hash}",
  "data_coverage": {
    "country_files": ${country_count},
    "relation_files": ${relation_count}
  },
  "files_in_archive": [
    "last_update_snapshot.json",
    "quality_report_snapshot.json",
    "run_log_snapshot.json",
    "alert_index_snapshot.json",
    "archive_manifest.json"
  ],
  "note": "Full data history is preserved in git. This archive contains metadata snapshots only."
}
EOF
  success "Wrote archive_manifest.json"
}

# ---------------------------------------------------------------------------
# Clean staging raw_collected
# ---------------------------------------------------------------------------
clean_staging() {
  local raw_dir="${PROJECT_ROOT}/staging/raw_collected"
  if [[ -d "${raw_dir}" ]]; then
    local file_count
    file_count=$(ls "${raw_dir}"/*.json 2>/dev/null | wc -l || echo 0)
    if [[ "${file_count}" -gt 0 ]]; then
      info "Cleaning staging/raw_collected/ (${file_count} files)..."
      rm -f "${raw_dir}"/*.json
      success "staging/raw_collected/ cleaned"
    else
      info "staging/raw_collected/ already empty"
    fi
  fi
  info "Keeping staging/validated/, staging/trends/, staging/run_log.json"
}

# ---------------------------------------------------------------------------
# Print archive summary
# ---------------------------------------------------------------------------
print_summary() {
  echo ""
  echo -e "${BOLD}Archive Summary${RESET}"
  echo "  Run ID:     ${RUN_ID}"
  echo "  Location:   archive/${RUN_ID}/"
  echo ""
  ls -lh "${ARCHIVE_DIR}/" 2>/dev/null || true
  echo ""
  success "Archive snapshot complete."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  echo ""
  echo -e "${BOLD}${CYAN}Stratoterra Archive Snapshot Creator${RESET}"
  echo "Run ID:       ${RUN_ID}"
  echo "Archive path: ${ARCHIVE_DIR}"
  echo ""

  create_archive_dir
  copy_metadata
  copy_quality_report
  copy_run_log
  copy_alert_index
  write_archive_manifest
  clean_staging
  print_summary
}

main "$@"
