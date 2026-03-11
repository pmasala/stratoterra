#!/usr/bin/env bash
# Run pre-fetch scripts locally.
# Usage:
#   ./agents/scripts/run_prefetch.sh              # All sources
#   ./agents/scripts/run_prefetch.sh worldbank     # Specific source
#   ./agents/scripts/run_prefetch.sh --no-key      # Skip sources needing API keys

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Load .env if present
if [ -f .env ]; then
    echo "Loading .env..."
    set -a
    source .env
    set +a
fi

# Ensure output directories exist
mkdir -p staging/prefetched staging/prefetch_cache

echo "=== Stratoterra Pre-Fetch ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

python3 -m agents.prefetch.run_all "$@"

echo ""
echo "Output: staging/prefetched/"
echo "Cache:  staging/prefetch_cache/"
