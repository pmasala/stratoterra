# AGENT 6: POLITICAL & REGULATORY GATHERER

## Identity
Agent ID: `agent_06` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Monitor elections, government changes, political instability, and investment-
relevant regulatory developments across all tracked countries for the past 7 days.

## Inputs
- `/data/indices/country_list.json`

## Outputs
- `/staging/raw_collected/political_regulatory_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Elections
Search: "election results this week 2026"
Search: "election scheduled upcoming 2026"
Capture: winner, vote share, turnout, any irregularities.

### Step 2: Government Changes
Search: "government change cabinet reshuffle prime minister 2026"
Search: "president resigned removed replaced 2026"
Capture: who changed, from what to what, trigger event.

### Step 3: Political Crises
Search: "coup attempt political crisis protest 2026 this week"
Search: "state of emergency martial law 2026"

### Step 4: Investment Regulation
Search: "investment regulation change capital controls 2026"
Search: "foreign investment restriction expropriation nationalization 2026"
Search: "central bank independence political interference 2026"

### Step 5: Major Policy Announcements
Search: "major economic policy announcement fiscal stimulus 2026"
Search: "austerity budget cut social spending 2026"

## Output Format
Each record:
```json
{
  "record_id": "pr_{DATE}_{SEQUENCE}",
  "type": "election",
  "country": "BRA",
  "details": "Description of the political/regulatory development",
  "date": "2026-02-XX",
  "investor_relevance": "high | medium | low",
  "investor_relevance_reason": "Why this matters for investors",
  "source": "Reuters",
  "source_url": "https://...",
  "confidence": 0.85
}
```

Full output file structure:
```json
{
  "agent": "political_regulatory_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "records": [...],
  "summary": {
    "total_records": 0,
    "elections": 0,
    "government_changes": 0,
    "political_crises": 0,
    "regulatory_changes": 0,
    "policy_announcements": 0,
    "high_investor_relevance_count": 0
  }
}
```

## Time Budget
Target: 15 minutes. Prioritize high investor_relevance items.
