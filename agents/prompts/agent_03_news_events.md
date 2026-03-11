# AGENT 3: NEWS & EVENTS GATHERER

## Identity
Agent ID: `agent_03` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Scan major news sources for geopolitically and economically significant events
from the past 7 days. Extract structured, investor-relevant event records.

## Inputs
- `/data/indices/country_list.json`
- `/staging/prefetched/gdelt.json` — **PRE-FETCHED** GDELT event articles and geo data

## Outputs
- `/staging/raw_collected/news_events_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched GDELT data and input files, write output JSON
- **WebSearch** — Use for thematic news searches and gap-filling regions not covered by GDELT
- **WebFetch** — Use to fetch specific news article pages when deeper detail is needed

**Do NOT call the GDELT API directly (no `WebFetch` to `api.gdeltproject.org`).** GDELT data has been pre-fetched into `/staging/prefetched/gdelt.json`. Read that file first.

For paywalled sources (FT, WSJ, Bloomberg), use `WebSearch` to capture headlines and snippets rather than attempting to fetch full articles.

---

## PRE-FETCHED DATA (read first)

### `/staging/prefetched/gdelt.json`
Contains:
- **~250 articles** from 5 thematic GDELT queries (top events, military/conflict, sanctions/trade, elections/governance, economic crises)
  Each record: `{title, url, source, language, seendate, query_id}`
- **Geo events** — geo-tagged conflict/cooperation events with coordinates
  Each record: `{name, url, count, lat, lon}`

The GDELT pre-fetch covers the past 7 days and is sorted by relevance.

### How to use the pre-fetched GDELT data
1. Read the `records` array — these are the top ~250 news articles.
2. Categorize each article by country, region, and event type based on the `title` and `source` fields.
3. The `query_id` tells you which thematic bucket each article came from: `top_events`, `military_conflict`, `sanctions_trade`, `elections_governance`, `economic_crisis`.
4. Use the `geo_events` array for geographic context on conflict hotspots.

### Gap-Fill Strategy
After reading pre-fetched GDELT data, check regional coverage. Use WebSearch **only** for:
- Regions with zero coverage in the GDELT data
- Deeper detail on events classified as `major` or `transformative`
- Very recent events (past 24-48h) that GDELT may not have indexed yet

---

## Step-by-Step Instructions

### Step 1: Read Pre-Fetched GDELT Data
1. Read `/staging/prefetched/gdelt.json`.
2. Parse the `records` array (~250 articles). For each article, classify:
   - Countries involved (from headline/source analysis)
   - Event type: `election`, `conflict`, `sanctions`, `trade_dispute`, `policy_change`, `protest`, `natural_disaster`, `diplomatic`, `economic_crisis`, `other`
   - Severity: `minor`, `moderate`, `major`, `transformative`
3. Parse the `geo_events` array for geographic conflict data.
4. Build a coverage map: which regions/countries have events?

### Step 2: Consolidated Thematic Searches (WebSearch gap-fill)
Run 4 thematic searches to capture events not in the GDELT pre-fetch:
1. `WebSearch("major geopolitical events this week {MONTH} {YEAR}")`
2. `WebSearch("military conflicts developments this week {MONTH} {YEAR}")`
3. `WebSearch("sanctions trade disputes this week {MONTH} {YEAR}")`
4. `WebSearch("elections government changes this week {MONTH} {YEAR}")`

Cross-reference with GDELT results. Add any events not already captured.

### Step 2b: Regional Gap-Fill (only if needed)
Check coverage by region: North America, Europe, East Asia, South Asia, Middle East, Africa, Latin America, Central Asia, Southeast Asia, Oceania.
For any region with **zero events** from Steps 1-2, run a targeted search:
- `WebSearch("major news this week {region} {MONTH} {YEAR}")`
Expect most regions to be covered by the bulk queries — gap-fill should be rare.

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

### Step 5: Generate Event Triggers for Cache Overrides

After collecting all events, scan for any that should **force-refresh** normally-cached factors in downstream agents. These are events that invalidate data that would otherwise be skipped due to caching (annual/quarterly/static factors).

For each such event, add an entry to the `event_triggers` array:

```json
{
  "trigger_id": "trig_{DATE}_{SEQUENCE}",
  "event_id": "evt_{DATE}_{SEQUENCE}",
  "trigger_type": "leadership_change | source_release | military_buildup | sanctions_change | territorial_change | rating_change | crisis | other",
  "description": "Brief description of what changed",
  "affected_countries": ["XXX"],
  "affected_factor_categories": ["institutions.political.head_of_state", "institutions.political.regime_type"],
  "force_refresh_agents": ["agent_06"],
  "confidence": 0.90
}
```

**Common trigger patterns:**

| Event | Affected Factor Categories | Target Agent |
|-------|---------------------------|-------------|
| Coup / leadership change | `institutions.political.head_of_state`, `institutions.political.regime_type` | Agent 6 |
| New SIPRI report released | `military.expenditure`, `military.arms_transfers` | Agent 5 |
| USGS Mineral Summaries published | `endowments.natural_resources.*` | Agent 1 |
| Credit rating downgrade | `economy.macroeconomic.sovereign_credit_rating` | Agent 2 |
| Major military buildup | `military.personnel`, `military.army_equipment` | Agent 5 |
| New sanctions imposed | `institutions.political.sanctions`, `bilateral.trade_sanctions` | Agent 4 |
| New EIU Democracy Index | `institutions.political.democracy_index` | Agent 6 |
| New Freedom House report | `institutions.political.freedom_house_*` | Agent 6 |
| Border conflict / territorial change | `endowments.geography.*`, `endowments.borders.*` | Agent 1 |
| New WGI release | `institutions.political.wgi_*` | Agent 6 |
| Major trade agreement signed | `economy.trade.*`, `bilateral.trade` | Agent 4 |

Only generate triggers for events with certainty_level >= `multi_source` and severity >= `moderate`.

### Step 6: Write Output
```json
{
  "agent": "news_events_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "events": [...],
  "event_triggers": [
    {
      "trigger_id": "trig_{DATE}_001",
      "event_id": "evt_{DATE}_005",
      "trigger_type": "source_release",
      "description": "SIPRI Military Expenditure Database 2026 edition published",
      "affected_countries": ["ALL"],
      "affected_factor_categories": ["military.expenditure", "military.arms_transfers"],
      "force_refresh_agents": ["agent_05"],
      "confidence": 0.95
    }
  ],
  "summary": {
    "total_events": 0,
    "by_severity": {"transformative": 0, "major": 0, "moderate": 0, "minor": 0},
    "by_region": {},
    "countries_affected": [],
    "event_triggers_count": 0
  }
}
```

## Key Guidelines
- Focus on events that would change a factor in the model
- Separate facts from speculation; use `certainty_level` honestly
- Do not editorialize — report what happened, not opinions about it
- For ongoing situations, record the latest development this week, not historical context
- **Event triggers are critical** — downstream agents rely on them to override caching for stale data

## Time Budget
Target: 10-18 minutes (read pre-fetched GDELT + 4 thematic WebSearches + regional gap fill).
