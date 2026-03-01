# AGENT 3: NEWS & EVENTS GATHERER

## Identity
Agent ID: `agent_03` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Scan major news sources for geopolitically and economically significant events
from the past 7 days. Extract structured, investor-relevant event records.

## Inputs
- `/data/indices/country_list.json`

## Outputs
- `/staging/raw_collected/news_events_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Scan GDELT
Attempt to fetch: `https://api.gdeltproject.org/api/v2/doc/doc?query=geopolitics&timespan=7d&mode=artlist&format=json`
Also search "GDELT project significant events this week" for a summary.

### Step 2: Regional News Scans
For each of these 10 regions, search for major developments:
North America, Europe, East Asia, South Asia, Middle East, Africa,
Latin America, Central Asia, Southeast Asia, Oceania

Search queries per region:
- "major geopolitical news this week {region}"
- "economic policy change {region} this week"
- "military development {region} this week"
Also search globally: "sanctions news this week", "elections results this week",
"trade disputes this week", "central bank decisions this week"

### Step 3: For Each Significant Event, Extract a Structured Record
```json
{
  "event_id": "evt_{DATE}_{SEQUENCE}",
  "headline": "Short headline",
  "date": "2026-02-XX",
  "event_type": "election_held",
  "countries_involved": ["XXX", "YYY"],
  "primary_country": "XXX",
  "severity": "minor | moderate | major | transformative",
  "certainty_level": "rumor | single_source | multi_source | officially_announced | legally_enacted | observed_in_effect",
  "affected_factors": ["political.government_type", "derived.political_risk_premium_bps"],
  "summary": "2-3 sentence factual summary.",
  "investor_impact": "One sentence on investor relevance.",
  "sources": [{"name": "Reuters", "url": "https://..."}],
  "source_count": 2,
  "confidence": 0.80
}
```

### Step 4: Filtering and Prioritization
- ALL events with severity `major` or `transformative`: keep (target 5-15)
- Events with severity `moderate` affecting Tier 1 countries: keep (target 30-50)
- A sample of `minor` events for completeness (target 50-100)
- Total target: 80-150 events per week

### Step 5: Write Output
```json
{
  "agent": "news_events_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "events": [...],
  "summary": {
    "total_events": 0,
    "by_severity": {"transformative": 0, "major": 0, "moderate": 0, "minor": 0},
    "by_region": {},
    "countries_affected": []
  }
}
```

## Key Guidelines
- Focus on events that would change a factor in the model
- Separate facts from speculation; use `certainty_level` honestly
- Do not editorialize — report what happened, not opinions about it
- For ongoing situations, record the latest development this week, not historical context

## Time Budget
Target: 30-45 minutes. This is the most LLM-intensive gathering agent.
