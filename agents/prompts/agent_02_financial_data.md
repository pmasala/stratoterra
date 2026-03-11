# AGENT 2: FINANCIAL DATA GATHERER

## Identity
Agent ID: `agent_02` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Collect current financial market data: exchange rates, sovereign bond yields,
stock indices, commodity prices, and recent central bank decisions.

**Cache policy:** All data collected by this agent is WEEKLY frequency — no caching
or skip logic applies. Every data point is refreshed every pipeline run.

## Inputs
- `/data/indices/country_list.json`
- `/staging/prefetched/fx_commodities.json` — **PRE-FETCHED** exchange rates and commodity prices

## Outputs
- `/staging/raw_collected/financial_data_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched data and input files, write output JSON
- **WebSearch** — Use for bond yields, stock indices, credit ratings, and gap-filling FX/commodity data
- **WebFetch** — Use to extract data from financial data pages (Trading Economics, investing.com)

**Do NOT call FX or commodity APIs directly.** Exchange rates and metals prices have been pre-fetched into `/staging/prefetched/fx_commodities.json`. Read that file first, then use WebSearch only for data not covered.

---

## PRE-FETCHED DATA (read first)

### `/staging/prefetched/fx_commodities.json`
Contains:
- **Exchange rates** (~25-30 currencies vs USD) from Frankfurter/ExchangeRate-API
  Each record: `{currency, country_code, rate_vs_usd, source, indicator_name}`
- **Commodity prices** (gold, silver, platinum, palladium) from metals.live API
  Each record: `{commodity, price_usd, unit, source, indicator_name}`

**Currencies NOT covered by the pre-fetch** (Frankfurter uses ECB data, which excludes some):
VND, NGN, PKR, BDT, KZT, UAH, ARS, IRR — gap-fill these via WebSearch.

**Commodities NOT covered by the pre-fetch** (only metals available via free API):
Oil (Brent, WTI), natural gas, copper, iron ore, lithium, wheat, corn, soybeans — gap-fill via WebSearch.

### Gap-Fill Strategy
1. Read pre-fetched data first.
2. Identify currencies and commodities missing from the pre-fetched file.
3. Use consolidated WebSearch table fetches (one search for all missing FX, one for all missing commodities).
4. Individual WebSearch only for stubborn gaps.

---

## Step-by-Step Instructions

### Step 1: Exchange Rates (Pre-Fetched + Gap-Fill)
1. Read `/staging/prefetched/fx_commodities.json`. Extract all `indicator_name: "exchange_rate_vs_usd"` records.
2. Map each to the output format with `factor_path: "macroeconomic.exchange_rate_vs_usd"`.
3. Identify which of these 39 currencies are missing from the pre-fetched data:
   EUR, GBP, JPY, CNY, INR, BRL, RUB, KRW, AUD, CAD, CHF,
   SEK, NOK, MXN, IDR, TRY, ZAR, SAR, AED, THB, MYR, SGD, TWD, PLN, ILS,
   PHP, VND, COP, ARS, CLP, EGP, NGN, PKR, BDT, KZT, UAH, RON, CZK, HUF
4. **Gap-fill missing currencies only:** `WebSearch("exchange rate {currency} to USD today")` for each missing one.
5. For weekly change %: `WebSearch("major currency exchange rates weekly change {MONTH} {YEAR}")` (one consolidated search).

### Step 2: Sovereign Bond Yields (WebSearch — no pre-fetched source)
1. **Table fetch:** `WebSearch("government bond yields 10 year all countries today table")`
2. `WebFetch` the result page (WorldGovernmentBonds.com or similar).
3. Extract yields for all Tier 1 countries (30) from the table.
4. **Gap-fill:** Individual searches only for countries missing from the table.
5. Collect: current yield %, 1-week change in basis points.

### Step 3: Stock Market Indices (Batch-First)
1. **Table fetch:** `WebSearch("world stock market indices today performance")`
2. `WebFetch` to extract all major index values.
3. **Gap-fill:** Individual searches for any missing indices.
4. Collect current level and 1-week change % for:
   S&P 500 (USA), FTSE 100 (GBR), DAX (DEU), CAC 40 (FRA), Nikkei 225 (JPN),
   Shanghai Composite (CHN), Hang Seng (HKG), KOSPI (KOR), BSE Sensex (IND),
   Bovespa (BRA), ASX 200 (AUS), TSX (CAN), MOEX (RUS), JSE Top 40 (ZAF)

### Step 4: Commodity Prices (Pre-Fetched Metals + WebSearch for Others)
1. Read `/staging/prefetched/fx_commodities.json`. Extract all commodity records (gold, silver, platinum, palladium already available).
2. **Gap-fill remaining commodities via one consolidated search:**
   `WebSearch("commodity prices today oil gas copper iron wheat corn soybeans lithium")`
   `WebFetch` a commodity overview page (e.g., Trading Economics commodities page).
3. **Individual gap-fill** only for commodities still missing.
4. Collect current price, 1-week change %, 1-month change %:
   - Brent crude ($/bbl), WTI crude ($/bbl), Natural gas Henry Hub ($/MMBtu)
   - Gold ($/oz) ← pre-fetched, Silver ($/oz) ← pre-fetched, Copper ($/tonne), Iron ore ($/tonne)
   - Lithium carbonate ($/tonne), Wheat ($/bushel), Corn ($/bushel), Soybeans ($/bushel)

### Step 5: Central Bank Rate Decisions
Search for policy rate decisions from Tier 1 central banks in the past week.
Record only if there was an actual change or surprise decision.

### Step 6: Sovereign Credit Rating Changes
Search "sovereign credit rating changes this week". Record only actual changes.

## Output Format
```json
{
  "agent": "financial_data_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "exchange_rates": [...],
  "bond_yields": [...],
  "equity_indices": [...],
  "commodities": [...],
  "central_bank_decisions": [...],
  "rating_changes": [...]
}
```

Each record:
```json
{
  "country_code": "DEU",
  "factor_path": "macroeconomic.sovereign_bond_yield_10yr_pct",
  "new_value": 2.45,
  "market_timestamp": "2026-03-01T16:00:00Z",
  "weekly_change_pct": -0.8,
  "weekly_change_bps": null,
  "source": "Trading Economics",
  "confidence": 0.95,
  "volatility_flag": false
}
```

Set `volatility_flag = true` if weekly FX change > 3% or yield change > 50bps.

## Time Budget
Target: 3-7 minutes (read pre-fetched FX/metals + WebSearch for bonds/indices/energy commodities + gap fill).
