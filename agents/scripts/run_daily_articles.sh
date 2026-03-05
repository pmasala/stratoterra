#!/usr/bin/env bash
# =============================================================================
# Stratoterra — Daily Article Generator
# Lightweight daily pipeline: runs Agent 18 to generate articles from the
# latest weekly briefing, builds article index chunk, and commits.
#
# On weekly pipeline days, Agent 18 runs as part of the full pipeline.
# On other days, run this script standalone (~20-30 min).
#
# Usage:
#   ./agents/scripts/run_daily_articles.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

TODAY=$(date -u +%Y-%m-%d)
echo "=== Stratoterra Daily Article Generator ==="
echo "Date: $TODAY"
echo ""

# --- Find latest weekly briefing ---
LATEST_BRIEFING=$(ls -t data/global/weekly_briefing_*.json 2>/dev/null | head -1)
if [ -z "$LATEST_BRIEFING" ]; then
    echo "ERROR: No weekly briefing found in data/global/"
    echo "Run the weekly pipeline first to generate a briefing."
    exit 1
fi
echo "Using briefing: $LATEST_BRIEFING"

# --- Ensure output directories exist ---
mkdir -p data/global/articles
mkdir -p data/chunks/global/articles

# --- Run Agent 18 (Article Writer) ---
echo ""
echo "--- Running Agent 18: Article Writer ---"
claude --dangerously-skip-permissions agents/prompts/agent_18_article_writer.md

# --- Build article index chunk ---
echo ""
echo "--- Building article index ---"
python3 agents/scripts/build_article_index.py

# --- Git commit ---
echo ""
echo "--- Committing articles ---"
ARTICLE_COUNT=$(ls data/global/articles/article_${TODAY}_*.json 2>/dev/null | grep -cv "index" || echo "0")
if [ "$ARTICLE_COUNT" -gt 0 ]; then
    git add data/global/articles/ data/chunks/global/
    git commit -m "Daily articles $TODAY: $ARTICLE_COUNT articles generated

AI-generated articles from latest weekly briefing.
Source: $LATEST_BRIEFING"
    git push origin main
    echo ""
    echo "=== Done: $ARTICLE_COUNT articles published ==="
else
    echo "No new articles generated for $TODAY."
fi
