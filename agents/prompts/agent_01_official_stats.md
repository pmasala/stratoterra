# AGENT 1: OFFICIAL STATISTICS GATHERER

## Identity
Agent ID: `agent_01` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Collect updated macroeconomic, demographic, and trade statistics from official
international sources for all 75 tracked countries.

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers
- `/data/metadata/last_update.json` — what was last collected and when
- `/agents/config/cache_registry.json` — cache state from previous runs
- `/agents/config/factor_frequency_registry.json` — frequency classification
- `/agents/config/release_calendar.json` — known source publication dates

## Outputs
- `/staging/raw_collected/official_stats_{DATE}.json`

## Tools

- **WebSearch** — Use to discover current values (e.g., `WebSearch("World Bank GDP USA 2025")`)
- **WebFetch** — Use to extract data from specific pages (e.g., Trading Economics country pages)
- **Bash** with `curl` — Use for structured JSON APIs:
  - World Bank: `curl "https://api.worldbank.org/v2/country/{ISO2}/indicator/{ID}?format=json&date=2024:2025"`
  - IMF WEO: `curl "https://www.imf.org/external/datamapper/api/v1/{indicator}/{ISO3}"`
- **Read** / **Write** — Read input files, write output JSON

No API keys are required. All sources are public.

---

## CACHE-AWARE FETCHING

**Before collecting any data, follow the cache-check skill in `/agents/skills/cache_check.md`.**

This agent's data is split across multiple frequency tiers. On a typical week, you will SKIP most categories and only fetch weekly/monthly data that is due.

### Frequency Tiers for This Agent

#### MONTHLY (fetch if ≥30 days since last fetch)
- Inflation rate CPI % → World Bank, national stats
- Core inflation % → National stats
- Unemployment rate % → National stats, ILO
- Youth unemployment rate % → National stats
- Central bank policy rate % → Central bank sites
- Money supply M2 growth % → IMF IFS, central banks
- Real interest rate % → IMF IFS

#### QUARTERLY (fetch if ≥90 days since last fetch)
- GDP nominal USD, GDP PPP USD, GDP per capita → World Bank, IMF WEO
- GDP real growth rate % → IMF WEO
- Fiscal balance % GDP, public debt % GDP → IMF
- Current account balance % GDP → IMF
- Trade balance USD, total exports/imports USD → World Bank, IMF
- FDI inflows/outflows USD → World Bank
- Foreign exchange reserves USD → IMF IFS
- Gold reserves → IMF IFS

#### ANNUAL (fetch only when new release detected in release_calendar)
- Demographics (population, median age, life expectancy, HDI, etc.) → World Bank, UNDP
- Governance indices (WGI) → World Bank WGI
- GDP composition (agriculture/industry/services) → World Bank
- External debt metrics → World Bank
- Inequality (Gini, income shares, poverty rates) → World Bank
- Economic complexity, innovation index, human capital → Harvard Atlas, WIPO, UNESCO
- Infrastructure, energy data → World Bank LPI, EIA
- Natural resources (non-energy) → USGS

#### STATIC (skip entirely unless event trigger)
- Geography, climate classification, cultural factors → Already seeded

---

## Step-by-Step Instructions

### Step 0: Cache Check
1. Read `cache_registry.json`, `factor_frequency_registry.json`, and `release_calendar.json`.
2. For each frequency tier above, determine which blocks are DUE for refresh.
3. Log your cache decisions in a `cache_decisions` array (see cache_check.md for format).
4. **Skip any block that is not due.** Proceed only with due blocks.

### Step 1: Load Country List
Read `country_list.json`. Organize countries into Tier 1 (30), Tier 2 (25), Tier 3 (20).

### Step 2: Collect Due Data — Tier 1 & 2 Countries
For each country, collect ONLY the indicators in frequency blocks that are due this run.

**If MONTHLY block is due:**
- Inflation rate CPI % (latest available)
- Unemployment rate %
- Central bank policy rate %

**If QUARTERLY block is due:**
- GDP nominal USD (search: "World Bank GDP {country} 2025" or IMF WEO)
- GDP real growth rate % (IMF forecast)
- GDP per capita USD
- Government debt % of GDP
- Current account balance % of GDP
- Total exports USD and total imports USD
- Foreign exchange reserves USD

**If ANNUAL block is due (specific source has new release):**
- Demographics: Population total, population growth rate %, median age, life expectancy, HDI
- Governance: WGI indicators (6 scores)
- Other annual indicators as listed above

**If NO blocks are due:** Log that all data is cached and skip to Step 5.

### Step 3: Collect Tier 3 Countries
Collect only due-frequency indicators: GDP, population, inflation rate, political stability score.
Minimal coverage is acceptable for Tier 3.

### Step 4: Format Each Data Point
```json
{
  "country_code": "USA",
  "factor_path": "macroeconomic.gdp_nominal_usd",
  "new_value": 28500000000000,
  "source": "World Bank / IMF WEO",
  "source_url": "https://...",
  "source_date": "2025-12-31",
  "confidence": 0.90,
  "frequency_tier": "quarterly",
  "notes": ""
}
```

### Step 5: Write Output File
```json
{
  "agent": "official_stats_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "cache_decisions": [
    {
      "source": "worldbank.wgi",
      "factor_category": "institutions.political.wgi_*",
      "frequency": "annual",
      "action": "skipped",
      "reason": "cached — no new release since last fetch",
      "last_fetched": "2026-02-15T10:00:00Z",
      "next_due": "2026-09-15"
    }
  ],
  "records": [...],
  "skipped": [
    {"country_code": "...", "factor_path": "...", "reason": "..."}
  ],
  "summary": {
    "total_records": 0,
    "countries_covered": 0,
    "tier_1_avg_indicators": 0,
    "tier_2_avg_indicators": 0,
    "tier_3_avg_indicators": 0,
    "blocks_fetched": [],
    "blocks_skipped": []
  }
}
```

## Error Handling
- If a data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 12 indicators per Tier 1, 8 per Tier 2, 4 per Tier 3 (for due blocks only)

## Time Budget
- **Typical week (no blocks due):** 2-5 minutes (cache check + logging only)
- **Month boundary (monthly block due):** 8-12 minutes
- **Quarter boundary (quarterly block due):** 15-20 minutes
- **Annual release week:** 20-30 minutes (full fetch for that source)
