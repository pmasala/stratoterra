# AGENT 12: ALERT GENERATOR

## Identity
Agent ID: `agent_12` | Phase: 5 (ANALYZE) | Run ID: {RUN_ID}

## Purpose
Scan all updated country data for threshold breaches. Generate new alerts and
update existing alert statuses. Write the alert index and event feed.

## Inputs
- `/data/indices/alert_index.json` (existing alerts)
- `/data/countries/*.json` (just updated)
- `/staging/trends/trend_estimates_{DATE}.json`

## Outputs
- `/data/indices/alert_index.json` (updated)
- `/data/global/event_feed.json` (updated)

## Step 1: Load Existing Alerts
Read all existing alerts from `alert_index.json`. Note their current status.

## Step 2: Scan for New Alert Triggers

**CRITICAL triggers:**
- `derived.default_probability > 0.5`
- `derived.currency_crisis_probability > 0.7`
- Active conflict escalated to severity `high`
- Coup or unconstitutional leadership change (from Agent 6 data)
- Comprehensive sanctions newly imposed
- Expropriation of foreign assets

**WARNING triggers:**
- Sovereign credit rating downgrade
- `political.political_stability_score` trend = `strong_decrease`
- GDP trend = `strong_decrease` for 2+ consecutive periods
- `macroeconomic.inflation_rate_cpi_pct > 50`
- FX reserves < 3 months of imports
- Election within 30 days in country with `political_stability_score < -1.0`

**WATCH triggers:**
- Any trend direction reversal (was growth, now decrease)
- New targeted sanctions (not comprehensive)
- Major policy shift announcement
- Leadership change (non-coup)
- Major protests (severity >= `major` from Agent 3)
- Chokepoint disruption affecting tracked country's key trade routes

## Step 3: Update Alert Lifecycle
For each existing alert, update its status:
- `new` → `ongoing` if condition persists
- `ongoing` → `escalated` if severity increased
- `ongoing` or `escalated` → `deescalated` if severity decreased
- Any → `resolved` if triggering condition no longer exists

## Alert Record Format
```json
{
  "alert_id": "alert_{DATE}_{SEQUENCE}",
  "severity": "critical | warning | watch",
  "country_code": "ARG",
  "status": "new | ongoing | escalated | deescalated | resolved",
  "trigger": "default_probability > 0.5",
  "headline": "Argentina default probability elevated above 50%",
  "details": "2-3 sentence description of the situation and its investor relevance.",
  "first_triggered": "{ISO_TIMESTAMP}",
  "last_updated": "{ISO_TIMESTAMP}",
  "affected_factors": ["derived.default_probability"],
  "run_id": "{RUN_ID}"
}
```

## Output Files

`/data/indices/alert_index.json`:
```json
{
  "last_updated": "{ISO_TIMESTAMP}",
  "run_id": "{RUN_ID}",
  "summary": {"critical": 0, "warning": 0, "watch": 0, "total_active": 0},
  "alerts": [...]
}
```

`/data/global/event_feed.json`: sorted list of all new and updated events
from this run, for display in the UI feed panel.

## Time Budget
Target: 10 minutes.
