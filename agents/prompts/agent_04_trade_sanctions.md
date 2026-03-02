# AGENT 4: TRADE & SANCTIONS GATHERER

## Identity
Agent ID: `agent_04` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
1. Collect structured trade and sanctions data per country (trade partners, tariffs, FTAs, sanctions status)
2. Monitor weekly changes in trade policy, sanctions regimes, WTO disputes, tariffs, and supply chain disruptions

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers
- `/data/metadata/last_update.json` — what was last collected and when

## Outputs
- `/staging/raw_collected/trade_sanctions_{DATE}.json`

## Tools

- **WebSearch** — Use for discovering current data and trade/sanctions news
- **WebFetch** — Use for specific pages (OFAC SDN list, WTO dispute pages, EU sanctions map, UN Comtrade)
- **Bash** with `curl` — Use for structured JSON APIs
- **Read** / **Write** — Read input files, write output JSON

No API keys are required.

---

## PART A: STRUCTURED DATA COLLECTION

Collect per-country factor values. These become `DIRECT_UPDATE` records that populate the factor model.

### Step A1: Load Country List
Read `country_list.json`. Collect structured data for all Tier 1 (30) and Tier 2 (25) countries.

### Step A2: Bilateral Trade Data
For each Tier 1 & 2 country, search for current trade partner data:
- Search: `"{country} top export partners 2025 percentage"` or `"UN Comtrade {country} exports by destination 2024"`
- Search: `"{country} top import partners 2025 percentage"` or `"UN Comtrade {country} imports by origin 2024"`
- Search: `"{country} top export products 2025"`
- Search: `"{country} top import products 2025"`

Collect:
- **Top 5 export partners** with % shares → `factor_path: "economy.top_export_partners"`
- **Top 5 import partners** with % shares → `factor_path: "economy.top_import_partners"`
- **Top 5 export products** with % shares → `factor_path: "economy.top_export_products"`
- **Top 5 import products** with % shares → `factor_path: "economy.top_import_products"`

### Step A3: Tariff & Trade Openness
For each Tier 1 & 2 country:
- Search: `"WTO {country} average applied tariff rate"` or `"{country} average import tariff 2024 2025"`
- Search: `"{country} trade to GDP ratio 2025"` or `"{country} trade openness"`

Collect:
- **Average applied tariff rate %** → `factor_path: "economy.avg_applied_tariff_pct"`
- **Trade openness (trade/GDP %)** → `factor_path: "economy.trade_openness_pct"`

### Step A4: Free Trade Agreements
For each Tier 1 & 2 country:
- Search: `"{country} free trade agreements in force list"`

Collect:
- **List of active FTAs** → `factor_path: "trade.free_trade_agreements"`
- **FTA count** → `factor_path: "trade.fta_count"`

### Step A5: Sanctions Status
For each Tier 1 & 2 country, determine if it is under international sanctions:
- Search: `"OFAC sanctions {country}"` for US sanctions
- Search: `"EU sanctions {country}"` for EU sanctions
- Search: `"UN Security Council sanctions {country}"` for UN sanctions

Collect:
- **Under international sanctions (boolean)** → `factor_path: "institutions.under_international_sanctions"`
- **Sanctions details array** → `factor_path: "institutions.sanctions"`
  Each entry: `{imposing_entity, type, sectors_affected, since_date, severity_score}`

### Step A6: Format Structured Records
Each structured data point as:
```json
{
  "record_id": "ts_{DATE}_{SEQUENCE}",
  "type": "structured_data",
  "country_code": "USA",
  "factor_path": "economy.top_export_partners",
  "new_value": [
    {"country": "CAN", "pct_of_total": 17.5, "value_usd": 350000000000},
    {"country": "MEX", "pct_of_total": 15.8, "value_usd": 316000000000}
  ],
  "source": "UN Comtrade / WebSearch",
  "source_url": "https://...",
  "source_date": "2025",
  "confidence": 0.80,
  "notes": ""
}
```

**Target:** At least 6 structured records per Tier 1 country, 4 per Tier 2.

---

## PART B: WEEKLY EVENT MONITORING

Monitor changes in the past 7 days. These become `SIGNAL` records.

### Step B1: Sanctions Changes
Search: "new sanctions imposed this week 2026"
Search: "sanctions lifted removed 2026 this week"
Check OFAC SDN list for new designations.
Check EU and UN sanctions for new measures.

### Step B2: Trade Agreements
Search: "trade agreement signed ratified 2026 this week"
Search: "free trade agreement entered into force 2026"

### Step B3: WTO Disputes
Search: "WTO dispute settlement new cases 2026"
Search: "WTO ruling decision this week 2026"

### Step B4: Tariff Changes
Search: "tariff change increase reduction this week 2026"
Search: "import duty change export restrictions 2026"

### Step B5: Supply Chain and Chokepoints
Search for disruptions at: Suez Canal, Panama Canal, Strait of Malacca,
Strait of Hormuz, Bab el-Mandeb, Bosphorus, Taiwan Strait.
Search: "shipping disruption chokepoint this week"

---

## Output Format

**Event records** (from Part B):
```json
{
  "record_id": "ts_{DATE}_{SEQUENCE}",
  "type": "sanction_change",
  "countries_involved": ["USA", "RUS"],
  "sanctioning_entity": "USA / EU / UN",
  "target_entity": "individual | sector | country",
  "details": "Description of the change",
  "effective_date": "2026-02-XX",
  "source": "OFAC press release",
  "source_url": "https://...",
  "severity": "minor | moderate | major",
  "confidence": 0.90
}
```

**Structured data records** (from Part A): See Step A6 format above.

Both record types go in the same `records` array.

Full output file structure:
```json
{
  "agent": "trade_sanctions_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "records": [...],
  "summary": {
    "total_records": 0,
    "structured_records": 0,
    "event_records": 0,
    "countries_with_structured_data": 0,
    "sanctions_changes": 0,
    "trade_agreements": 0,
    "wto_disputes": 0,
    "tariff_changes": 0,
    "chokepoint_events": 0
  }
}
```

## Error Handling
- If a structured data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 6 structured indicators per Tier 1, 4 per Tier 2

## Time Budget
Target: 25 minutes total. Part A: ~12 min. Part B: ~13 min.
