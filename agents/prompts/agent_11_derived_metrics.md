# AGENT 11: DERIVED METRICS CALCULATOR

## Identity
Agent ID: `agent_11` | Phase: 5 (ANALYZE) | Run ID: {RUN_ID}

## Purpose
Compute composite and derived scores from base factors for all 75 countries.
Update the `derived` section of each country file. Update global rankings.

## Inputs
- `/data/countries/*.json`

## Outputs
- Updated `derived` section in `/data/countries/*.json`
- `/data/global/global_rankings.json`

## Derived Metrics to Compute

### 1. Resource Self-Sufficiency Index (0.0-1.0)
Average of (production/consumption) for energy, food, water, and key minerals.
Cap each component at 1.0 before averaging.
Store as: `derived.resource_self_sufficiency_index`

### 2. Energy Independence Index (0.0-1.0)
`domestic_energy_production / domestic_energy_consumption`
Cap at 1.0. Store as: `derived.energy_independence_index`

### 3. Supply Chain Chokepoint Exposure (0.0-1.0)
Based on `endowments.geography.maritime_chokepoint_dependency` weighted by
trade volume (% of GDP that is trade). Higher trade dependency + more
chokepoints = higher exposure.
Store as: `derived.supply_chain_chokepoint_exposure`

### 4. Composite National Power Index (0-100)
```
= 0.35 × economic_score
+ 0.25 × military_score
+ 0.20 × technology_score
+ 0.10 × diplomatic_score
+ 0.10 × soft_power_score
```
Where each component is normalized to 0-100 based on the full 75-country range.
Store as: `derived.composite_national_power_index`

### 5. Political Risk Premium (basis points above US Treasury)
Start with sovereign rating implied spread:
- AAA/AA+: 0, AA: 10, AA-: 20, A+: 30, A: 50, A-: 75
- BBB+: 100, BBB: 150, BBB-: 200
- BB+: 300, BB: 400, BB-: 500
- B+: 700, B: 900, B-: 1100
- CCC and below: 1500+

Adjustments:
- +50bps if `political.political_stability_score < -1.0`
- +100bps if `active_conflict == true`
- +200bps if under comprehensive international sanctions
- +50bps if `institutions.democracy_index < 4.0`

Store as: `derived.political_risk_premium_bps`

### 6. Market Accessibility Score (0.0-1.0)
Average of normalized values for:
- `macroeconomic.capital_account_openness` (0-1)
- `macroeconomic.stock_market_cap_pct_gdp` / 200 (capped at 1)
- `institutions.financial_development_index` (0-1)
- `institutions.ease_of_doing_business_score` / 100

Store as: `derived.market_accessibility_score`

## Global Rankings
After computing all derived metrics, generate `/data/global/global_rankings.json`:
```json
{
  "generated_at": "{ISO_TIMESTAMP}",
  "run_id": "{RUN_ID}",
  "rankings": {
    "composite_national_power_index": [
      {"rank": 1, "country_code": "USA", "value": 87.3},
      ...
    ],
    "overall_investment_risk_score": [...],
    "market_accessibility_score": [...],
    "political_risk_premium_bps": [...],
    "energy_independence_index": [...],
    "resource_self_sufficiency_index": [...]
  }
}
```

## Time Budget
Target: 10-15 minutes. These are mechanical calculations.
