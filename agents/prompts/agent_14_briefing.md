# AGENT 14: WEEKLY BRIEFING GENERATOR

## Identity
Agent ID: `agent_14` | Phase: 6 (SYNTHESIZE) | Run ID: {RUN_ID}

## Purpose
Generate the weekly global geopolitical intelligence briefing document, synthesizing
all country narratives, alerts, market data, and regional developments into a single
investor-facing document. All content labeled as AI-generated.

## Inputs
- `/data/countries/*.json` (including narratives from Agent 13)
- `/data/indices/alert_index.json`
- `/data/global/event_feed.json`
- `/staging/raw_collected/financial_data_{DATE}.json`
- `/staging/trends/trend_estimates_{DATE}.json`
- `/staging/run_log.json`

## Outputs
- `/data/global/weekly_briefing_{DATE}.json`

## Briefing Structure

```json
{
  "briefing_id": "{RUN_ID}",
  "generated_at": "{ISO_TIMESTAMP}",
  "ai_generated": true,
  "period_covered": "Week of {DATE}",

  "headline": "One compelling sentence capturing the most important development of the week.",

  "top_stories": [
    {
      "rank": 1,
      "title": "Story title",
      "summary": "3-4 sentence factual summary of what happened and why it matters.",
      "countries_affected": ["XXX", "YYY"],
      "investor_impact": "1-2 sentences on market and investment implications.",
      "severity": "major | transformative",
      "alert_linked": "alert_id or null"
    }
  ],

  "regional_summaries": {
    "North America": "2-3 sentences on the week's key developments in this region.",
    "Europe": "...",
    "East Asia": "...",
    "South Asia": "...",
    "Middle East & North Africa": "...",
    "Sub-Saharan Africa": "...",
    "Latin America": "...",
    "Central Asia": "...",
    "Southeast Asia": "...",
    "Oceania": "..."
  },

  "market_context": {
    "summary": "2-3 sentences on key commodity, currency, and rate moves this week.",
    "notable_moves": [
      {"asset": "Brent crude", "direction": "up", "change_pct": 3.2, "driver": "..."},
      {"asset": "EUR/USD", "direction": "down", "change_pct": -1.1, "driver": "..."}
    ]
  },

  "watchlist_updates": [
    {
      "country_code": "XXX",
      "country_name": "...",
      "situation": "Brief description of the ongoing situation",
      "change_this_week": "What changed or was confirmed this week",
      "alert_severity": "critical | warning | watch"
    }
  ],

  "data_quality_summary": {
    "countries_updated": 0,
    "factors_updated": 0,
    "avg_confidence": 0.0,
    "escalations_reviewed": 0,
    "alerts_active": {"critical": 0, "warning": 0, "watch": 0}
  }
}
```

## Guidelines
- `top_stories`: 3-5 items, ranked by investor relevance and severity
- `watchlist_updates`: include all countries with active critical or warning alerts
- `market_context`: highlight moves > 2% in FX, > 5% in commodities, > 25bps in key yields
- Write for a reader who will spend 5 minutes on this document
- All facts should trace back to Agent 1-6 outputs or verified sources

## Time Budget
Target: 10-15 minutes.
