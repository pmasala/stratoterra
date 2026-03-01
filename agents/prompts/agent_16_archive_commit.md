# AGENT 16: ARCHIVE & COMMIT PREPARER

## Identity
Agent ID: `agent_16` | Phase: 7 (FINALIZE) | Run ID: {RUN_ID}

## Prerequisite
Human operator must have acknowledged the quality report from Agent 15.

## Purpose
Create an archive snapshot, generate UI-optimized chunk files, clean staging
directories, and prepare the git commit message for human review and execution.

## Inputs
- `/data/countries/*.json`
- `/data/relations/*.json`
- `/data/indices/*.json`
- `/data/global/*.json`
- `/data/metadata/quality_report_{DATE}.json`
- `/staging/run_log.json`

## Outputs
- `/archive/{RUN_ID}/last_update_snapshot.json`
- `/data/chunks/country-summary/all_countries_summary.json`
- `/data/chunks/country-detail/{code}.json` (one per country)
- `/data/chunks/relations/{PAIR}.json` (one per tracked pair)
- `/data/chunks/global/weekly_briefing.json`
- `/data/chunks/global/alert_index.json`
- `/data/chunks/manifest.json`
- `/data/indices/relation_index.json`

## Steps

### Step 1: Create Archive Snapshot
```
mkdir -p /archive/{RUN_ID}/
```
Copy `/data/metadata/last_update.json` to `/archive/{RUN_ID}/last_update_snapshot.json`.
This is a lightweight reference; full historical data lives in git.

### Step 2: Clean Staging
Delete all files in `/staging/raw_collected/`.
Keep: `/staging/validated/`, `/staging/trends/`, `/staging/run_log.json`.

### Step 3: Generate Country Summary Chunk
Read all `/data/countries/*.json`. For each country, extract minimal fields:
`code, name, tier, lat, lon, composite_national_power_index,
overall_investment_risk_score, political_stability_score, gdp_nominal_usd,
gdp_real_growth_rate_pct, active_alerts_count, top_alert_severity,
narrative_headline (first sentence of executive_summary), last_updated`

Write to `/data/chunks/country-summary/all_countries_summary.json`.
Target size: ~500KB. This file is loaded on initial page load.

### Step 4: Generate Country Detail Chunks
For each country, copy the full country JSON to:
`/data/chunks/country-detail/{code}.json`
These are loaded on-demand when a user clicks a country.

### Step 5: Generate Relation Chunks
For each bilateral pair in `/data/relations/`, copy to:
`/data/chunks/relations/{PAIR}.json`

### Step 6: Generate Global Chunks
Copy `/data/global/weekly_briefing_{DATE}.json` → `/data/chunks/global/weekly_briefing.json`
Copy `/data/indices/alert_index.json` → `/data/chunks/global/alert_index.json`

### Step 7: Update Manifest
Write `/data/chunks/manifest.json`:
```json
{
  "generated_at": "{ISO_TIMESTAMP}",
  "run_id": "{RUN_ID}",
  "files": {
    "all_countries_summary": {
      "path": "data/chunks/country-summary/all_countries_summary.json",
      "size_bytes": 0,
      "countries": 75,
      "last_modified": "{ISO_TIMESTAMP}"
    },
    "country_detail": {"count": 75, "last_modified": "{ISO_TIMESTAMP}"},
    "relations": {"count": 0, "last_modified": "{ISO_TIMESTAMP}"},
    "weekly_briefing": {"last_modified": "{ISO_TIMESTAMP}"}
  }
}
```

### Step 8: Update Relation Index
Rebuild `/data/indices/relation_index.json` with updated composite scores
for all bilateral pairs.

### Step 9: Prepare Git Commit Message
Read from quality report and run log to fill in the template.
Print the following for the human to review and execute:

```
git add -A && git commit -m "Weekly update {RUN_ID}

Countries updated: {N}
Relations updated: {N}
New alerts: {N_critical} critical, {N_warning} warning, {N_watch} watch
Coverage: {pct}% avg across Tier 1
Quality: {confidence_avg} avg confidence

Top changes:
- {change_1}
- {change_2}
- {change_3}"

git push origin main
```

**Do NOT execute the git commands.** Present them to the human for review.

## Time Budget
Target: 5 minutes.
