# AGENT 4: TRADE & SANCTIONS GATHERER

## Identity
Agent ID: `agent_04` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
1. Collect structured trade and sanctions data per country (trade partners, tariffs, FTAs, sanctions status)
2. Monitor weekly changes in trade policy, sanctions regimes, WTO disputes, tariffs, and supply chain disruptions

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers
- `/data/metadata/last_update.json` — what was last collected and when
- `/agents/config/cache_registry.json` — cache state from previous runs
- `/agents/config/factor_frequency_registry.json` — frequency classification
- `/agents/config/release_calendar.json` — known source publication dates
- `/staging/raw_collected/news_events_{DATE}.json` — for event_triggers (from Agent 3)
- `/staging/prefetched/comtrade.json` — **PRE-FETCHED** UN Comtrade bilateral trade data (if available)

## Outputs
- `/staging/raw_collected/trade_sanctions_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched data and input files, write output JSON
- **WebSearch** — Use for sanctions lookups, WTO disputes, tariff data, and trade news
- **WebFetch** — Use for specific pages (OFAC SDN list, WTO dispute pages, EU sanctions map)

**Do NOT call the UN Comtrade API directly (no `curl` to `comtradeapi.un.org`).** Trade data has been pre-fetched into `/staging/prefetched/comtrade.json` if a Comtrade API key was configured. Read that file first. If the file is empty or missing, fall back to WebSearch for trade partner data.

---

## PRE-FETCHED DATA (read first)

### `/staging/prefetched/comtrade.json` (if available)
Contains bilateral trade records for Tier 1 and Tier 2 countries:
- Top 10 export partners per country with USD values and % shares
- Top 10 import partners per country with USD values and % shares
Each record: `{country_code, partner_code, flow, value_usd, pct_of_total, indicator_name, year}`

### How to use
1. Read the file. If `records` is empty or file doesn't exist, fall back to WebSearch for Part A Step A2.
2. Group records by `country_code` and `flow` (export/import).
3. Take top 5 per country for the output format.

### Sanctions, tariffs, WTO — NOT pre-fetched
These require WebSearch because they come from HTML pages, not structured APIs:
- OFAC sanctions list
- EU sanctions map
- WTO tariff profiles
- WTO dispute settlement

### Gap-Fill Strategy
After reading pre-fetched Comtrade data, run `WebSearch` only for:
- Countries missing from the Comtrade data
- Sanctions data (always WebSearch — changes frequently)
- Tariff rates and FTA lists (WebSearch table fetches)

---

## CACHE-AWARE FETCHING

**Before collecting any data, follow the cache-check skill in `/agents/skills/cache_check.md`.**

### Frequency Tiers for This Agent

#### QUARTERLY — Part A structured data (skip if <90 days since last fetch)
- Top export/import partners with % shares → UN Comtrade
- Top export/import products with % shares → UN Comtrade
- Average applied tariff rate % → WTO
- Trade openness (trade/GDP %) → World Bank
- Active FTA list and count → WTO, bilateral sources

#### WEEKLY — Part B event monitoring (always run)
- Sanctions status (OFAC, EU, UN) → always scan
- Sanctions changes, trade agreements, WTO disputes, tariff changes, chokepoint disruptions

### Event Override
Read `event_triggers` from Agent 3's output. If any trigger affects trade/sanctions factors (e.g., "new sanctions imposed on X", "major trade agreement signed"), **force-refresh** the relevant Part A data for affected countries even if quarterly cache is fresh.

---

## Step 0: Cache Check
1. Read `cache_registry.json`, `factor_frequency_registry.json`, `release_calendar.json`.
2. Read Agent 3's output for `event_triggers` affecting this agent.
3. Determine if Part A (quarterly structured data) is due for refresh.
4. Log all cache decisions in `cache_decisions` array.
5. Part B (weekly events) always runs.

---

## PART A: STRUCTURED DATA COLLECTION (QUARTERLY — skip if cached)

**Only run this section if quarterly data is due (≥90 days since last fetch) or event-triggered.**

Collect per-country factor values. These become `DIRECT_UPDATE` records that populate the factor model.

### Step A1: Load Country List
Read `country_list.json`. Collect structured data for all Tier 1 (30) and Tier 2 (25) countries.

### Step A2: Bilateral Trade Data (Pre-Fetched + Gap-Fill)
1. Read `/staging/prefetched/comtrade.json`. If the file exists and has records:
   - Group by `country_code` and `flow` (export/import).
   - Take top 5 partners per country per flow direction.
   - Map to the output format (see Step A6).
2. If the file is empty or missing, fall back to consolidated WebSearch:
   ```
   WebSearch("{country} top trading partners exports imports 2025")
   ```
3. **Gap-fill:** For countries missing from pre-fetched Comtrade results, use consolidated searches:
   ```
   WebSearch("{country} top trading partners exports imports 2025")
   ```

Collect:
- **Top 5 export partners** with % shares → `factor_path: "economy.top_export_partners"`
- **Top 5 import partners** with % shares → `factor_path: "economy.top_import_partners"`
- **Top 5 export products** with % shares → `factor_path: "economy.top_export_products"`
- **Top 5 import products** with % shares → `factor_path: "economy.top_import_products"`

### Step A3: Tariff & Trade Openness (Batch-First)
1. **WTO tariff table:**
   ```
   WebSearch("WTO average applied tariff rates by country 2025 table")
   ```
   `WebFetch` the WTO tariff profiles page to extract rates for all countries at once.
2. **Trade openness** — available from World Bank batch API (Agent 1 may have fetched this; check staging). Otherwise:
   ```
   WebSearch("trade to GDP ratio by country 2025 table")
   ```
3. **Gap-fill:** Individual searches only for countries missing from table results.

Collect:
- **Average applied tariff rate %** → `factor_path: "economy.avg_applied_tariff_pct"`
- **Trade openness (trade/GDP %)** → `factor_path: "economy.trade_openness_pct"`

### Step A4: Free Trade Agreements
1. **Consolidated search:**
   ```
   WebSearch("free trade agreements by country complete list 2025 2026")
   ```
   `WebFetch` a comprehensive FTA database page (WTO RTA database or similar).
2. **Gap-fill:** Individual searches for countries not found in the consolidated list.

Collect:
- **List of active FTAs** → `factor_path: "trade.free_trade_agreements"`
- **FTA count** → `factor_path: "trade.fta_count"`

### Step A5: Sanctions Status (Batch-First)
Instead of per-country sanctions lookups, fetch complete sanctions lists:
1. **OFAC (one fetch):** `WebSearch("OFAC sanctioned countries programs list 2026")` → `WebFetch` the page.
2. **EU (one fetch):** `WebSearch("EU sanctions map current restrictive measures 2026")` → `WebFetch` the page.
3. **UN (one fetch):** `WebSearch("UN Security Council sanctions committees active 2026")` → `WebFetch` the page.
4. Match sanctioned countries against the 75 tracked countries. Set sanctions details for each match.

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
  "frequency_tier": "quarterly",
  "notes": ""
}
```

**Target:** At least 6 structured records per Tier 1 country, 4 per Tier 2.

---

## PART B: WEEKLY EVENT MONITORING (always run)

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
  "cache_decisions": [...],
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
    "chokepoint_events": 0,
    "part_a_status": "fetched | skipped_cached | partial_event_override",
    "part_b_status": "fetched"
  }
}
```

## Error Handling
- If a structured data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 6 structured indicators per Tier 1, 4 per Tier 2

## Time Budget
- **Typical week (Part A cached):** ~8 minutes (Part B only)
- **Quarter boundary (Part A due):** ~12 minutes (read pre-fetched Comtrade + sanctions WebSearch + Part B)
