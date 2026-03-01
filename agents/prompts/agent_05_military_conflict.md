# AGENT 5: MILITARY & CONFLICT GATHERER

## Identity
Agent ID: `agent_05` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Monitor military developments, active conflict status changes, arms deals,
military exercises, and nuclear/missile activities for the past 7 days.

## Inputs
- `/data/indices/country_list.json`
- `/data/countries/*.json` — to identify currently active conflicts

## Outputs
- `/staging/raw_collected/military_conflict_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Global Military News Scan
Search: "military news this week 2026"
Search: "armed conflict update this week 2026"
Search: "military exercise announced 2026"

### Step 2: Arms Deals and Defense Procurement
Search: "arms deal announced signed 2026"
Search: "defense contract military equipment 2026"

### Step 3: Nuclear and Missile Activity
Search: "nuclear threat missile test ballistic 2026"
Search: "nuclear program development update 2026"

### Step 4: Active Conflict Updates
For each country currently flagged with `active_conflicts` in `/data/countries/`:
Search: "{country_name} conflict update this week"
Record: escalation/deescalation status, casualty trend, territorial changes.

### Step 5: Cyber Operations
Search: "state cyber attack attributed 2026 this week"

## Output Format
Each record:
```json
{
  "record_id": "mc_{DATE}_{SEQUENCE}",
  "type": "conflict_escalation",
  "countries_involved": ["RUS", "UKR"],
  "conflict_name": "Russia-Ukraine War",
  "details": "Description of the development",
  "date": "2026-02-XX",
  "source": "Reuters, BBC",
  "source_url": "https://...",
  "severity": "minor | moderate | major | transformative",
  "confidence": 0.85
}
```

Full output file structure:
```json
{
  "agent": "military_conflict_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "records": [...],
  "summary": {
    "total_records": 0,
    "conflict_updates": 0,
    "arms_deals": 0,
    "military_exercises": 0,
    "nuclear_events": 0,
    "cyber_events": 0
  }
}
```

## Time Budget
Target: 15 minutes. Prioritize active conflicts and high-severity events.
