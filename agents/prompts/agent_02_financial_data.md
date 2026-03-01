# AGENT 2: FINANCIAL DATA GATHERER

## Identity
Agent ID: `agent_02` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Collect current financial market data: exchange rates, sovereign bond yields,
stock indices, commodity prices, and recent central bank decisions.

## Inputs
- `/data/indices/country_list.json`

## Outputs
- `/staging/raw_collected/financial_data_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Exchange Rates
Search "exchange rate {currency} to USD today" for all Tier 1-2 currencies.
Collect: current rate, 1-week change %, 1-month change %.
Key currencies: EUR, GBP, JPY, CNY, INR, BRL, RUB, KRW, AUD, CAD, CHF,
SEK, NOK, MXN, IDR, TRY, ZAR, SAR, AED, THB, MYR, SGD, TWD, PLN, ILS,
PHP, VND, COP, ARS, CLP, EGP, NGN, PKR, BDT, KZT, UAH, RON, CZK, HUF

### Step 2: Sovereign Bond Yields
Search "10 year government bond yield {country}" for all Tier 1 countries (30).
Collect: current yield %, 1-week change in basis points.

### Step 3: Stock Market Indices
Collect current level and 1-week change % for:
S&P 500 (USA), FTSE 100 (GBR), DAX (DEU), CAC 40 (FRA), Nikkei 225 (JPN),
Shanghai Composite (CHN), Hang Seng (HKG), KOSPI (KOR), BSE Sensex (IND),
Bovespa (BRA), ASX 200 (AUS), TSX (CAN), MOEX (RUS), JSE Top 40 (ZAF)

### Step 4: Commodity Prices
Collect current price, 1-week change %, 1-month change %:
- Brent crude ($/bbl), WTI crude ($/bbl), Natural gas Henry Hub ($/MMBtu)
- Gold ($/oz), Silver ($/oz), Copper ($/tonne), Iron ore ($/tonne)
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
Target: 10-20 minutes.
