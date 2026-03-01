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
- `/data/countries/*.json`
- `/data/relations/*.json`
- `/data/timeseries/*.json`

## Outputs
- Updated `/data/countries/*.json`
- Updated `/data/relations/*.json`
- Updated `/data/timeseries/*.json`
- `/data/metadata/last_update.json`
- `/data/metadata/update_log.json`

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

### Step 5: Log Completion
Log to `staging/run_log.json`: records integrated, any errors encountered.

## Important Rules
- Never delete existing data — only update specific factor fields
- Always preserve previous values in timeseries before overwriting
- If a file read or write fails: stop, log the error, do not continue

## Time Budget
Target: 5-10 minutes.
