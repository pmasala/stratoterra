# AGENT 9: DATA INTEGRATOR

## Identity
Agent ID: `agent_09` | Phase: 4 (INTEGRATE) | Run ID: {RUN_ID}

## Purpose
Merge all validated updates (ACCEPT, ACCEPT_WITH_NOTE, FLAG) into the main
`/data/` store. Skip REJECT and unresolved ESCALATE items.

## Prerequisite
Human review of any escalations from Agent 8 must be complete before this agent runs.

## Inputs
- `/staging/validated/validated_updates_{DATE}.json`
- `/staging/processed/factor_updates_{DATE}.json` (for `event_triggers` passthrough)
- `/data/countries/*.json`
- `/data/relations/*.json`
- `/data/timeseries/*.json`
- `/agents/config/cache_registry.json` — current cache state

## Outputs
- Updated `/data/countries/*.json`
- Updated `/data/relations/*.json`
- Updated `/data/timeseries/*.json`
- `/data/metadata/last_update.json`
- `/data/metadata/update_log.json`
- Updated `/agents/config/cache_registry.json` — refreshed cache timestamps

## Step-by-Step Instructions

### Step 1: Read Validated Updates
Load `/staging/validated/validated_updates_{DATE}.json`.
Filter to only: ACCEPT, ACCEPT_WITH_NOTE, FLAG verdicts.
Ignore: REJECT, unresolved ESCALATE.

### Step 2: For Each Accepted Update
1. Read current `/data/countries/{code}.json` (or relation/supranational file)
2. Navigate to the `factor_path` within that file
3. Append the current value to `/data/timeseries/{code}_{factor_category}.json` with a timestamp
4. Write the new value to the factor path
5. Update `last_updated` timestamp on that factor
6. Update `confidence` score
7. If verdict == `FLAG`: add an entry to the country's `metadata.active_flags` array

### Step 3: Update Relation Files
For bilateral updates: apply same process to `/data/relations/{PAIR}.json`.
Pair codes are alphabetically ordered (e.g., `CHN_USA`, not `USA_CHN`).

### Step 4: Update Metadata Files
Update `/data/metadata/last_update.json`:
```json
{
  "last_run_id": "{RUN_ID}",
  "last_run_completed_at": "{ISO_TIMESTAMP}",
  "countries_updated": N,
  "relations_updated": N,
  "total_factors_updated": N
}
```

Append to `/data/metadata/update_log.json`:
```json
{
  "run_id": "{RUN_ID}",
  "completed_at": "{ISO_TIMESTAMP}",
  "countries_updated": N,
  "relations_updated": N,
  "updates_accepted": N,
  "updates_flagged": N,
  "updates_rejected": N
}
```

### Step 5: Update Cache Registry

After successful integration, update `/agents/config/cache_registry.json` to reflect what was actually fetched and integrated this run.

1. Read the current `cache_registry.json`.
2. For each data source that was fetched this run (identified from `cache_decisions` arrays in the Phase 1 agent outputs and the `source_name` fields in validated updates):
   - Create or update the entry with:
     - `last_fetched`: current ISO timestamp
     - `source_release_date`: from `release_calendar.json` if applicable
     - `frequency`: the source's frequency tier
     - `next_due`: computed based on frequency (last_fetched + ttl_days, or next release date)
     - `countries_covered`: count of countries with data from this source
     - `records`: count of records integrated from this source
3. For event-triggered refreshes (from `event_triggers` in the processed updates), update the relevant entries even though they wouldn't normally be due.
4. Set `cache_registry.last_updated` to current ISO timestamp.
5. Write the updated `cache_registry.json`.

Example entry after update:
```json
{
  "worldbank.wgi": {
    "last_fetched": "2026-03-01T10:00:00Z",
    "source_release_date": "2025-09-15",
    "frequency": "annual",
    "next_due": "2026-09-15",
    "countries_covered": 55,
    "records": 330
  }
}
```

### Step 6: Log Completion
Log to `staging/run_log.json`: records integrated, cache entries updated, any errors encountered.

## Important Rules
- Never delete existing data — only update specific factor fields
- Always preserve previous values in timeseries before overwriting
- If a file read or write fails: stop, log the error, do not continue
- Always update cache_registry.json — this is critical for downstream pipeline efficiency

## Time Budget
Target: 5-10 minutes.
