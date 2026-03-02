# AGENT 7: FACT EXTRACTOR & STRUCTURER

## Identity
Agent ID: `agent_07` | Phase: 2 (PROCESS) | Run ID: {RUN_ID}

## Purpose
Transform all raw collected data from Phase 1 into structured factor updates
mapped to the canonical schema in `docs/01_FACTOR_MODEL_SPEC.md`.

## Inputs
- `/staging/raw_collected/official_stats_{DATE}.json`
- `/staging/raw_collected/financial_data_{DATE}.json`
- `/staging/raw_collected/news_events_{DATE}.json`
- `/staging/raw_collected/trade_sanctions_{DATE}.json`
- `/staging/raw_collected/military_conflict_{DATE}.json`
- `/staging/raw_collected/political_regulatory_{DATE}.json`
- `/docs/01_FACTOR_MODEL_SPEC.md` (for factor path reference)

## Outputs
- `/staging/processed/factor_updates_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Load and Count All Raw Data
Read all six Phase 1 output files. Count total records.

### Step 2: Classify Direct Factor Updates (Agents 1 & 2 records)
For quantitative records, map to the exact `factor_path` from the spec.
Assign confidence based on source:
- Official API (World Bank, IMF): 0.85-0.95
- Financial market data: 0.90-0.95
- Web-scraped official page: 0.70-0.85
- News-extracted value: 0.50-0.70

### Step 2b: Process Structured Data Records (Agents 4-6)
Agents 4, 5, and 6 produce two types of records:
- **`type: "structured_data"`** — Pre-structured factor updates with explicit `factor_path` and `new_value`. Treat these exactly like Agent 1 & 2 records (Step 2). They already have the correct schema mapping — pass them through as `DIRECT_UPDATE` entries in `factor_updates`.
- **Event records** (all other `type` values) — Process these in Step 3 below.

To identify structured data records: check for `"type": "structured_data"` OR the presence of both `factor_path` and `new_value` fields.

### Step 3: Classify Event Records (Agents 3-6)
For records from Agents 3-6 that are NOT `structured_data` (i.e., event records without `factor_path`), classify each as one of:
- **DIRECT_UPDATE**: certainty_level >= `officially_announced` AND maps to a specific factor. Example: "Central bank raises rate to 5%" → update `macroeconomic.central_bank_policy_rate_pct`.
- **SIGNAL**: Suggests trend direction but no specific value. Goes to `event_signals` array.
- **IRRELEVANT**: No model factor affected. Log and skip.

### Step 4: Normalize Values
- Convert all monetary values to USD using exchange rates from Agent 2
- Standardize percentages (0-100 for display, 0.0-1.0 for indices as per spec)
- Convert all dates to ISO 8601

### Step 5: Handle Duplicates and Conflicts
- If same factor_path + country has multiple sources: use highest-confidence
- Note alternatives in `alternatives` field
- If values differ > 20%: set `conflict_flag = true`

### Step 6: Write Output
```json
{
  "processing_date": "{DATE}",
  "agent": "fact_extractor",
  "run_id": "{RUN_ID}",
  "factor_updates": [
    {
      "update_id": "upd_001",
      "target": "country",
      "country_code": "TUR",
      "relation_id": null,
      "factor_path": "macroeconomic.inflation_rate_cpi_pct",
      "new_value": 45.2,
      "previous_value": null,
      "source_agent": "official_stats_gatherer",
      "source_name": "World Bank",
      "source_url": "https://...",
      "source_date": "2026-01-31",
      "confidence": 0.92,
      "anomaly_flag": false,
      "conflict_flag": false,
      "alternatives": [],
      "notes": ""
    }
  ],
  "event_signals": [
    {
      "event_id": "evt_2026-03-01_001",
      "affected_countries": ["USA", "CHN"],
      "affected_factors": ["relations.CHN_USA.trade.tension_index"],
      "signal_direction": "negative",
      "signal_strength": 0.7,
      "description": "Escalation in trade rhetoric"
    }
  ],
  "unmapped_records": [],
  "summary": {
    "total_input_records": 0,
    "direct_updates": 0,
    "event_signals": 0,
    "unmapped": 0,
    "conflicts_detected": 0
  }
}
```

## Time Budget
Target: 20-30 minutes.
