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
- `/staging/prefetched/worldbank.json` — **PRE-FETCHED** World Bank data (all indicators, all countries)
- `/staging/prefetched/imf_weo.json` — **PRE-FETCHED** IMF WEO forecasts (all indicators, all countries)
- `/staging/prefetched/eia.json` — **PRE-FETCHED** EIA energy data (if available)

## Outputs
- `/staging/raw_collected/official_stats_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched data and input files, write output JSON
- **WebSearch** — Use ONLY for gap-filling data not found in pre-fetched files
- **WebFetch** — Use ONLY when WebSearch points to a specific page for gap-fill data

**Do NOT call any APIs directly (no `curl`, no `WebFetch` to API endpoints).** All structured API data has been pre-fetched by Python scripts into `/staging/prefetched/`. Your job is to read, validate, map to factor paths, and gap-fill.

---

## PRE-FETCHED DATA (read these first)

The following files contain structured data already fetched from APIs by deterministic Python scripts. **Read these files before doing anything else.**

### `/staging/prefetched/worldbank.json`
Contains ~1,900 records covering 74 countries across 27 indicators:
- GDP group: `gdp_nominal_usd`, `gdp_per_capita_usd`, `gdp_growth_pct`, `gdp_ppp_usd`
- Fiscal: `govt_debt_pct_gdp`, `current_account_pct_gdp`, `reserves_total_usd`, `fdi_net_inflows_usd`
- Trade: `exports_usd`, `imports_usd`
- Labor: `inflation_cpi_pct`, `unemployment_pct`, `labor_force_participation_pct`
- Demographics: `population`, `population_growth_pct`, `life_expectancy`, `urban_population_pct`
- Development: `gini_index`, `literacy_rate_pct`, `health_expenditure_pct_gdp`
- Infrastructure: `electricity_access_pct`, `internet_users_pct`
- WGI (6 indicators): `wgi_voice_accountability`, `wgi_political_stability`, `wgi_govt_effectiveness`, `wgi_regulatory_quality`, `wgi_rule_of_law`, `wgi_control_of_corruption`

Each record has: `country_code`, `indicator_id`, `indicator_name`, `value`, `year`, `source`.

### `/staging/prefetched/imf_weo.json`
Contains ~1,000 records with IMF WEO forecasts:
- `gdp_nominal_usd_bn`, `gdp_real_growth_pct`, `inflation_avg_pct`, `unemployment_rate_pct`
- `fiscal_balance_pct_gdp`, `current_account_pct_gdp`, `govt_expenditure_pct_gdp`, `gross_debt_pct_gdp`

Records include `is_forecast: true` for future years — use these for trend estimates.

### `/staging/prefetched/eia.json` (if available)
Contains energy production/consumption data: oil, gas, coal, electricity by country.

### Gap-Fill Strategy

After reading pre-fetched data, identify countries or indicators with missing values. Run `WebSearch` queries **only** for these gaps. Expect gaps mainly for:
- Taiwan (TWN) — not in World Bank data
- Recently revised indicators
- Tier 3 countries with sparse coverage
- Indicators not covered by the pre-fetch scripts (e.g., HDI, economic complexity, central bank policy rates)

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

### Step 1: Load Pre-Fetched Data + Country List
1. Read `country_list.json`. Organize countries into Tier 1 (30), Tier 2 (25), Tier 3 (20).
2. Read `/staging/prefetched/worldbank.json` — this contains ~1,900 records already fetched from the World Bank API.
3. Read `/staging/prefetched/imf_weo.json` — this contains ~1,000 records already fetched from the IMF WEO API.
4. Read `/staging/prefetched/eia.json` if it exists — contains energy production/consumption data.
5. Index the pre-fetched data by `country_code` + `indicator_name` for fast lookup.

### Step 2: Map Pre-Fetched Data to Factor Paths
For each due frequency block, extract relevant records from the pre-fetched data and map them to the output format:

**Mapping from pre-fetched `indicator_name` → `factor_path`:**
- `gdp_nominal_usd` → `macroeconomic.gdp_nominal_usd`
- `gdp_per_capita_usd` → `macroeconomic.gdp_per_capita_usd`
- `gdp_growth_pct` → `macroeconomic.gdp_real_growth_rate_pct` (cross-check with IMF `gdp_real_growth_pct`)
- `gdp_ppp_usd` → `macroeconomic.gdp_ppp_usd`
- `inflation_cpi_pct` → `macroeconomic.inflation_rate_cpi_pct`
- `unemployment_pct` → `macroeconomic.unemployment_rate_pct`
- `govt_debt_pct_gdp` → `macroeconomic.public_debt_pct_gdp`
- `current_account_pct_gdp` → `macroeconomic.current_account_balance_pct_gdp`
- `reserves_total_usd` → `macroeconomic.foreign_exchange_reserves_usd`
- `fdi_net_inflows_usd` → `macroeconomic.fdi_inflows_usd`
- `exports_usd` → `macroeconomic.total_exports_usd`
- `imports_usd` → `macroeconomic.total_imports_usd`
- `population` → `demographics.population_total`
- `population_growth_pct` → `demographics.population_growth_rate_pct`
- `life_expectancy` → `demographics.life_expectancy_years`
- `urban_population_pct` → `demographics.urban_population_pct`
- `gini_index` → `demographics.gini_index`
- `wgi_*` → `institutions.political.wgi_*` (6 WGI indicators)

For IMF WEO forecast data (`is_forecast: true`), include it with a note indicating it's a forecast.

Set `confidence: 0.95` for World Bank data, `confidence: 0.90` for IMF WEO data.

### Step 3: Gap-Fill via WebSearch (only for missing data)
After mapping pre-fetched data, identify gaps:
1. **Taiwan (TWN)** — always missing from World Bank. Search: `WebSearch("Taiwan GDP population inflation 2025")`
2. **Central bank policy rates** — not in pre-fetched data. Use a consolidated search:
   ```
   WebSearch("central bank interest rates by country 2026 complete table")
   ```
3. **HDI, economic complexity, innovation index** — not in pre-fetched data. Individual searches only if annual block is due.
4. **Any Tier 1 or Tier 2 country with <4 indicators** from pre-fetched data — run targeted `WebSearch`.
5. Minimal coverage gap-fill for Tier 3 countries.

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
- **Typical week (no blocks due):** 1-2 minutes (cache check + read pre-fetched + logging)
- **Month boundary (monthly block due):** 3-5 minutes (read pre-fetched + map + gap fill)
- **Quarter boundary (quarterly block due):** 4-7 minutes (read pre-fetched + map + gap fill)
- **Annual release week:** 5-10 minutes (read pre-fetched + map + additional WebSearch gap fill)
