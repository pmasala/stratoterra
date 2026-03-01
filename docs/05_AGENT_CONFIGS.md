# Geopolitical Intelligence Model — Agent Configuration Files

**Version:** 1.0-draft
**Date:** 2026-03-01
**Status:** Design Phase
**Depends on:** `01_FACTOR_MODEL_SPEC.md`, `02_AGENT_ARCHITECTURE.md`

---

## Overview

This document contains the actual prompt/configuration for each agent that you will use with Claude Code MAX. Each agent is a structured prompt that tells Claude Code exactly what to do, what files to read, what to produce, and how to handle errors.

**Usage pattern:**
1. Open Claude Code MAX session
2. Paste or reference the orchestrator prompt
3. The orchestrator runs agents sequentially
4. You review escalations and quality report
5. Approve final commit

---

## Master Orchestrator

This is the top-level prompt you give Claude Code to start the weekly run.

```markdown
# WEEKLY GEOPOLITICAL MODEL UPDATE — ORCHESTRATOR

You are the orchestrator for the Geopolitical Intelligence Model weekly update.
Today's date: {CURRENT_DATE}
Run ID: {YEAR}-W{WEEK_NUMBER}

## Your task

Execute the weekly update pipeline by running each agent in sequence.
For each agent:
1. Read the agent's configuration (below or in /agents/config/)
2. Execute the agent's task
3. Validate the agent's output
4. Log the result to /staging/run_log.json
5. Proceed to the next agent

## Pipeline sequence

Phase 1 — DATA GATHERING:
  Agent 1: Official Statistics Gatherer
  Agent 2: Financial Data Gatherer
  Agent 3: News & Events Gatherer
  Agent 4: Trade & Sanctions Gatherer
  Agent 5: Military & Conflict Gatherer
  Agent 6: Political & Regulatory Gatherer

Phase 2 — PROCESSING:
  Agent 7: Fact Extractor & Structurer

Phase 3 — VALIDATION:
  Agent 8: Cross-Validator & Anomaly Detector

Phase 4 — INTEGRATION:
  Agent 9: Data Integrator

Phase 5 — ANALYSIS:
  Agent 10: Trend Estimator
  Agent 11: Derived Metrics Calculator
  Agent 12: Alert Generator

Phase 6 — SYNTHESIS:
  Agent 13: Country Profile Synthesizer
  Agent 14: Weekly Briefing Generator

Phase 7 — FINALIZATION:
  Agent 15: Data Quality Reporter
  Agent 16: Archive & Commit Preparer

## Run log format

Initialize /staging/run_log.json at start:
{
  "run_id": "{YEAR}-W{WEEK}",
  "started_at": "{ISO_TIMESTAMP}",
  "status": "in_progress",
  "agents": []
}

After each agent, append:
{
  "agent_id": "...",
  "status": "completed" | "failed" | "completed_with_warnings",
  "started_at": "...",
  "completed_at": "...",
  "records_processed": N,
  "errors": N,
  "warnings": N,
  "output_files": ["..."],
  "notes": "..."
}

## Error handling

If an agent fails:
1. Log the failure in run_log.json
2. STOP the pipeline
3. Report the error clearly
4. Save all staging files so far
5. Suggest fix and ask if I want to retry or skip

## Human review points

After Agent 8 (Validator): If there are ESCALATED items, PAUSE and present
them to me for review. Wait for my decisions before proceeding to Agent 9.

After Agent 15 (Quality Report): Present the quality summary and any
critical issues. Wait for my acknowledgment before Agent 16.

## Important notes

- All API calls must respect rate limits
- Use web_search and web_fetch tools for data gathering
- Write all intermediate outputs to /staging/
- Write final outputs to /data/
- Do not modify /data/ until Agent 9 (after validation)
- Keep detailed logs — every decision should be traceable

## Begin

Start with Agent 1. Let's go.
```

---

## Agent 1: Official Statistics Gatherer

```markdown
# AGENT 1: OFFICIAL STATISTICS GATHERER

## Identity
Agent ID: official_stats_gatherer
Phase: 1 (Data Gathering)
Run ID: {RUN_ID}

## Purpose
Collect updated official statistics from international data sources
for all tracked countries. Focus on macroeconomic, demographic, trade,
and development indicators.

## Inputs
- Read /data/indices/country_list.json for the list of countries to process
- Read /data/metadata/last_update.json to know what was last collected

## Outputs
- Write to /staging/raw_collected/official_stats_{DATE}.json

## Instructions

### Step 1: Load country list
Read country_list.json. Get the list of all country codes (ISO alpha-3).
Organize into Tier 1 (30), Tier 2 (25), Tier 3 (20).

### Step 2: For each Tier 1-2 country, collect the following indicators

Use web_search and web_fetch to find current values for:

MACROECONOMIC (source: search "World Bank {indicator} {country} {year}",
or search "{country} GDP 2025", "{country} inflation rate 2025", etc.):
- GDP nominal USD
- GDP real growth rate %
- GDP per capita USD
- Inflation rate CPI %
- Unemployment rate %
- Government debt % GDP
- Current account balance % GDP
- Total exports USD
- Total imports USD
- Foreign exchange reserves USD
- Central bank policy rate %
- Sovereign credit rating (Moody's, S&P, Fitch)

DEMOGRAPHIC (source: search "World Bank population {country}"):
- Population total
- Population growth rate
- Median age
- Life expectancy
- HDI score

TRADE (for top trade relationships):
- Top 5 export partners and % shares
- Top 5 import partners and % shares
- Top 5 export products and % shares
- Top 5 import products and % shares

### Step 3: For Tier 3 countries
Collect only: GDP, population, inflation rate, political stability score.
Minimal coverage is acceptable.

### Step 4: Format output

For each data point collected, create a record:
{
  "country_code": "USA",
  "factor_path": "macroeconomic.gdp_nominal_usd",
  "new_value": 28500000000000,
  "source": "World Bank / IMF WEO",
  "source_url": "https://...",
  "source_date": "2025-12-31",
  "confidence": 0.90,
  "notes": ""
}

### Step 5: Write output file

Write all records to /staging/raw_collected/official_stats_{DATE}.json
Include a summary section with counts.

### Error handling
- If a search returns no useful data for a country+indicator: skip it,
  log in the "skipped" array with reason
- If you get rate-limited: wait 30 seconds and retry
- Target: collect at least 10 indicators per Tier 1 country

### Time budget
Target: 15-30 minutes for this agent.
Do not spend more than 1 minute searching for a single data point.
If it's not easily findable, skip and move on.
```

---

## Agent 2: Financial Data Gatherer

```markdown
# AGENT 2: FINANCIAL DATA GATHERER

## Identity
Agent ID: financial_data_gatherer
Phase: 1 (Data Gathering)
Run ID: {RUN_ID}

## Purpose
Collect current financial market data for all tracked countries:
exchange rates, bond yields, stock indices, commodity prices.

## Inputs
- /data/indices/country_list.json

## Outputs
- /staging/raw_collected/financial_data_{DATE}.json

## Instructions

### Step 1: Exchange rates
Search for current exchange rates for all Tier 1-2 currencies vs USD.
Use web_search: "exchange rate {currency} to USD today"
Collect: current rate, 1-week change %, 1-month change %

Key currencies: EUR, GBP, JPY, CNY, INR, BRL, RUB, KRW, AUD, CAD,
CHF, SEK, NOK, MXN, IDR, TRY, ZAR, SAR, AED, THB, MYR, SGD,
TWD, PLN, ILS, PHP, VND, COP, ARS, CLP, EGP, NGN, PKR, BDT,
KZT, UAH, RON, CZK, HUF

### Step 2: Sovereign bond yields
Search for "10 year government bond yield {country}"
Collect for Tier 1 countries (30): current yield, 1-week change

### Step 3: Stock market indices
Search for current levels of:
- S&P 500 (USA), FTSE 100 (GBR), DAX (DEU), CAC 40 (FRA),
  Nikkei 225 (JPN), Shanghai Composite (CHN), Hang Seng (HKG),
  KOSPI (KOR), BSE Sensex (IND), Bovespa (BRA), ASX 200 (AUS),
  TSX (CAN), MOEX (RUS), JSE Top 40 (ZAF)
Collect: current level, 1-week change %

### Step 4: Commodity prices
Search for current prices:
- Brent crude oil ($/barrel)
- WTI crude oil ($/barrel)
- Natural gas Henry Hub ($/MMBtu)
- Gold ($/oz)
- Silver ($/oz)
- Copper ($/tonne)
- Iron ore ($/tonne)
- Lithium carbonate ($/tonne)
- Wheat ($/bushel)
- Corn ($/bushel)
- Soybeans ($/bushel)
Collect: current price, 1-week change %, 1-month change %

### Step 5: Central bank rates
Search for latest policy rates for Tier 1 central banks.
Note any rate decisions made in the past week.

### Step 6: Sovereign credit ratings
Search for "sovereign credit rating changes this week"
Only record if there was an actual change since last run.

### Output format
Same record structure as Agent 1. Each data point:
{
  "country_code": "USA",
  "factor_path": "macroeconomic.exchange_rate_vs_usd",
  "new_value": 1.0,
  "market_timestamp": "2026-03-01T16:00:00Z",
  "weekly_change_pct": 0.0,
  "source": "...",
  "confidence": 0.95,
  "volatility_flag": false
}

Flag volatility_flag = true if weekly change > 3% for FX or > 50bps for yields.

### Time budget
Target: 10-20 minutes.
```

---

## Agent 3: News & Events Gatherer

```markdown
# AGENT 3: NEWS & EVENTS GATHERER

## Identity
Agent ID: news_events_gatherer
Phase: 1 (Data Gathering)
Run ID: {RUN_ID}

## Purpose
Scan major news sources for geopolitically and economically significant
events from the past 7 days. Extract structured event records.

## Inputs
- /data/indices/country_list.json

## Outputs
- /staging/raw_collected/news_events_{DATE}.json

## Instructions

### Step 1: Scan GDELT (primary source)
Search: "GDELT project significant events this week"
Also try: web_fetch "https://api.gdeltproject.org/api/v2/doc/doc?query=geopolitics&timespan=7d&mode=artlist&format=json"
Extract the most significant global events from the past 7 days.

### Step 2: Scan major news wire services
For each region, search for major news:
- "major geopolitical news this week {region}"
- "economic policy changes this week"
- "military developments this week"
- "sanctions news this week"
- "elections this week"
- "trade disputes this week"
- "central bank decisions this week"

Regions: North America, Europe, East Asia, South Asia, Middle East,
Africa, Latin America, Central Asia, Southeast Asia

### Step 3: For each significant event found

Classify and extract:
{
  "event_id": "evt_{DATE}_{SEQUENCE}",
  "headline": "Short headline",
  "date": "2026-02-XX",
  "event_type": "(from taxonomy: election_held, trade_policy_change,
    military_deployment, sanctions_imposed, etc.)",
  "countries_involved": ["XXX", "YYY"],
  "primary_country": "XXX",
  "severity": "minor | moderate | major | transformative",
  "certainty_level": "rumor | single_source | multi_source |
    officially_announced | legally_enacted | observed_in_effect",
  "affected_factors": [
    "list of factor paths this event might affect"
  ],
  "summary": "2-3 sentence summary",
  "investor_impact": "1 sentence on what this means for investors",
  "sources": [{"name": "...", "url": "..."}],
  "source_count": N,
  "confidence": 0.X
}

### Step 4: Prioritize and filter

- Keep ALL events with severity >= "major" (aim for 5-15 per week)
- Keep events with severity = "moderate" if they affect Tier 1 countries
  (aim for 30-50 per week)
- Keep a sample of "minor" events for completeness (aim for 50-100)
- Total target: 80-150 events per week

### Step 5: Write output
Compile all events into the output file with summary statistics.

### Important guidance
- Be thorough but efficient. Don't deep-dive every story.
- Focus on events that would matter to an investor.
- For each event, think: "Would this change a factor in our model?"
- Separate facts from speculation. Use certainty_level honestly.
- Do not editorialize. Report what happened, not what you think about it.

### Time budget
Target: 30-45 minutes. This is the most LLM-intensive gathering agent.
```

---

## Agent 4-6: Specialized Gatherers

```markdown
# AGENT 4: TRADE & SANCTIONS GATHERER

Agent ID: trade_sanctions_gatherer
Phase: 1 | Run ID: {RUN_ID}

## Purpose
Monitor trade and sanctions changes for the past week.

## Instructions
1. Search: "new sanctions imposed this week 2026"
2. Search: "trade agreement signed this week 2026"
3. Search: "WTO dispute settlement new cases 2026"
4. Search: "tariff changes this week"
5. Search: "supply chain disruption {Suez/Panama/Malacca/Hormuz}"

For each finding, create a record with:
- type: sanction_change | trade_agreement | wto_dispute | tariff_change | supply_chain_disruption
- countries_involved
- details
- source and URL
- date
- severity and confidence

Output: /staging/raw_collected/trade_sanctions_{DATE}.json
Time budget: 15 minutes

---

# AGENT 5: MILITARY & CONFLICT GATHERER

Agent ID: military_conflict_gatherer
Phase: 1 | Run ID: {RUN_ID}

## Purpose
Monitor military and conflict developments for the past week.

## Instructions
1. Search: "military news this week 2026"
2. Search: "armed conflict update this week"
3. Search: "military exercise announced 2026"
4. Search: "arms deal announced 2026"
5. Search: "nuclear threat missile test 2026"
6. For known active conflicts (check /data for countries with active_conflicts):
   Search: "{conflict_name} latest update"

For each finding, create a record with:
- type: conflict_escalation | conflict_deescalation | military_exercise |
  arms_deal | deployment | nuclear_activity | cyber_attack
- countries_involved
- details
- source and URL
- severity and confidence

Output: /staging/raw_collected/military_conflict_{DATE}.json
Time budget: 15 minutes

---

# AGENT 6: POLITICAL & REGULATORY GATHERER

Agent ID: political_regulatory_gatherer
Phase: 1 | Run ID: {RUN_ID}

## Purpose
Monitor political changes, elections, and regulatory developments.

## Instructions
1. Search: "elections this week results 2026"
2. Search: "government change cabinet reshuffle 2026"
3. Search: "major policy announcement this week"
4. Search: "coup protest political crisis 2026"
5. Search: "investment regulation change 2026"
6. Search: "capital controls foreign investment restriction 2026"

For each finding, create a record:
- type: election | government_change | policy_shift | unrest | regulation_change
- country
- details
- investor_relevance: high | medium | low
- source and URL
- confidence

Output: /staging/raw_collected/political_regulatory_{DATE}.json
Time budget: 15 minutes
```

---

## Agent 7: Fact Extractor & Structurer

```markdown
# AGENT 7: FACT EXTRACTOR & STRUCTURER

Agent ID: fact_extractor
Phase: 2 (Processing)
Run ID: {RUN_ID}

## Purpose
Transform all raw collected data into structured factor updates
mapped to the schema defined in 01_FACTOR_MODEL_SPEC.md.

## Inputs
Read ALL files in /staging/raw_collected/ from this run:
- official_stats_{DATE}.json
- financial_data_{DATE}.json
- news_events_{DATE}.json
- trade_sanctions_{DATE}.json
- military_conflict_{DATE}.json
- political_regulatory_{DATE}.json

Also read the factor model schema from /docs/01_FACTOR_MODEL_SPEC.md

## Outputs
- /staging/processed/factor_updates_{DATE}.json

## Instructions

### Step 1: Load all raw data
Read each gathering agent's output file.
Count total records across all files.

### Step 2: For each record, determine if it updates a factor

DIRECT FACTOR UPDATES (records from Agents 1, 2):
- These are quantitative data points that directly map to schema factors
- Map each to its factor_path (e.g., "macroeconomic.gdp_nominal_usd")
- Set confidence based on source type:
  - Official API / World Bank / IMF: 0.85-0.95
  - Financial market data: 0.90-0.95
  - Web-scraped official page: 0.70-0.85
  - News-extracted: 0.50-0.70

EVENT-TO-FACTOR MAPPING (records from Agents 3-6):
- Not all events update factors. Classify each event:

  a) DIRECT_UPDATE: Event definitively changes a factor value
     Examples:
     - "Country X raises tariffs to 25%" → update trade.tariff
     - "New PM appointed" → update political.head_of_government
     - "Central bank raises rate to 5%" → update macroeconomic.central_bank_policy_rate_pct
     - "Sanctions imposed" → update political.sanctions array
     Only for certainty_level >= "officially_announced"

  b) SIGNAL: Event suggests a trend but doesn't change a specific value
     Examples:
     - "Protests continue in Country X" → signal for political_stability trend
     - "Trade tensions escalate" → signal for bilateral relation trend
     - "Military exercises near border" → signal for military_readiness
     These go to the event_signals array for the Trend Estimator

  c) IRRELEVANT: Event doesn't affect our model
     Log and skip

### Step 3: Normalize values
- All monetary values to USD
- Use exchange rates from Agent 2 output for conversion
- All percentages to consistent format (0-100 or 0-1 as schema specifies)
- Dates to ISO 8601

### Step 4: Handle duplicates and conflicts
- If the same factor_path + country has updates from multiple sources:
  - Use the highest-confidence source
  - Note the alternative values in a "alternatives" field
  - If values differ by > 20%: flag for validation

### Step 5: Write output

{
  "processing_date": "{DATE}",
  "agent": "fact_extractor",
  "factor_updates": [
    {
      "update_id": "upd_{SEQUENCE}",
      "target": "country" | "relation" | "supranational",
      "country_code": "USA",        // or null for relations
      "relation_id": null,           // or "USA_CHN" for relations
      "factor_path": "macroeconomic.gdp_real_growth_rate_pct",
      "new_value": 2.3,
      "previous_value": null,        // Will be filled by validator
      "source_agent": "official_stats_gatherer",
      "source_name": "World Bank",
      "source_url": "...",
      "source_date": "2025-12-31",
      "confidence": 0.92,
      "anomaly_flag": false,
      "conflict_flag": false,
      "alternatives": [],
      "notes": ""
    }
  ],
  "event_signals": [
    {
      "event_id": "evt_...",
      "affected_countries": ["USA", "CHN"],
      "affected_factors": ["relations.USA_CHN.trade.tension_index"],
      "signal_direction": "negative",
      "signal_strength": 0.7,
      "description": "Escalation in trade rhetoric between US and China"
    }
  ],
  "unmapped_records": [
    // Records that couldn't be mapped to any factor
  ],
  "summary": {
    "total_input_records": N,
    "direct_updates": N,
    "event_signals": N,
    "unmapped": N,
    "conflicts_detected": N
  }
}

### Time budget
Target: 20-30 minutes
```

---

## Agent 8: Cross-Validator

```markdown
# AGENT 8: CROSS-VALIDATOR & ANOMALY DETECTOR

Agent ID: validator
Phase: 3 (Validation)
Run ID: {RUN_ID}

## Purpose
Validate every proposed factor update before it enters the main data store.
Protect data integrity. Flag anomalies. Escalate uncertain changes.

## Inputs
- /staging/processed/factor_updates_{DATE}.json
- /data/countries/*.json (current values)
- /data/timeseries/*.json (historical values if available)

## Outputs
- /staging/validated/validated_updates_{DATE}.json
- /staging/validated/escalation_report_{DATE}.json (if any ESCALATE items)

## Instructions

### For each proposed update in factor_updates:

1. LOAD CURRENT VALUE
   Read the current value of this factor from /data/countries/{code}.json
   Set previous_value in the update record.

2. PLAUSIBILITY CHECK
   Apply range checks based on factor type:
   - GDP growth: [-30%, +30%]
   - Inflation: [-10%, 1000%]
   - Population: change < 2% per quarter
   - Military personnel: change < 20% per quarter
   - Exchange rates: weekly change < 30%
   - All indices: within their defined ranges
   - All percentages: [0, 100] or [0, 1] as appropriate

   If out of range → REJECT with reason

3. CHANGE MAGNITUDE CHECK
   Compute absolute and percentage change from current value.
   If change > 3× the typical quarterly change for this factor type:
   → FLAG as anomaly (but don't reject)

4. CROSS-SOURCE CHECK
   If this update has alternatives (from Step 4 of Agent 7):
   - If alternatives agree within 10%: proceed with highest-confidence
   - If alternatives disagree > 20%: FLAG with note

5. INTERNAL CONSISTENCY CHECK
   Where applicable:
   - If GDP composition is being updated: verify sum ≈ 100%
   - If trade data updated: verify export/import consistency
   - If military data: verify counts are non-negative integers

6. ASSIGN VERDICT
   - ACCEPT: passes all checks, change is normal
   - ACCEPT_WITH_NOTE: passes but has minor concerns (note them)
   - FLAG: anomalous but plausible, integrate with visual flag in UI
   - REJECT: fails plausibility or internal consistency
   - ESCALATE: high-impact change with uncertainty

   ESCALATE criteria (any of these):
   - Sovereign credit rating change
   - Leadership change (new head of state/government)
   - New sanctions or sanctions lifted
   - GDP growth change > 3 percentage points
   - Military conflict status change
   - Nuclear status change
   - Any update with confidence < 0.4 that would significantly
     change the country profile

### Output format

{
  "validation_date": "{DATE}",
  "validated_updates": [
    {
      "update_id": "upd_001",
      "verdict": "ACCEPT",
      "previous_value": 2.1,
      "new_value": 2.3,
      "change_pct": 9.5,
      "checks_passed": ["plausibility", "magnitude", "consistency"],
      "notes": ""
    },
    {
      "update_id": "upd_042",
      "verdict": "ESCALATE",
      "previous_value": "stable",
      "new_value": "BBB-",
      "reason": "Sovereign credit downgrade detected from single source.
                 Confidence 0.65. Needs human verification.",
      "recommended_action": "Search for corroboration from rating agencies"
    }
  ],
  "summary": {
    "total": N,
    "accept": N,
    "accept_with_note": N,
    "flag": N,
    "reject": N,
    "escalate": N
  }
}

### ESCALATION REPORT
If there are any ESCALATE items, write a separate escalation report:
/staging/validated/escalation_report_{DATE}.json

Present each escalation clearly:
- What changed?
- Why is it uncertain?
- What are the sources?
- What is the recommended action?
- Options: ACCEPT / REJECT / INVESTIGATE FURTHER

⚠️ PAUSE HERE and present escalations to the human operator.
Wait for decisions before proceeding.

### Time budget
Target: 15-20 minutes
```

---

## Agent 9-16: Remaining Agents

```markdown
# AGENT 9: DATA INTEGRATOR

Agent ID: data_integrator
Phase: 4 (Integration) | Run ID: {RUN_ID}

## Purpose
Merge all ACCEPTED and FLAGGED updates into /data/.

## Instructions
1. Read /staging/validated/validated_updates_{DATE}.json
2. For each update with verdict ACCEPT, ACCEPT_WITH_NOTE, or FLAG:
   a. Read /data/countries/{code}.json
   b. Navigate to factor_path
   c. Save current value to /data/timeseries/{code}_{factor_category}.json
   d. Write new value
   e. Update last_updated timestamp on that factor
   f. Update confidence score
   g. If verdict == FLAG: add to metadata.active_flags array
3. For relation updates: same process on /data/relations/{pair}.json
4. Update /data/metadata/last_update.json with current timestamps
5. Update /data/metadata/update_log.json with change summary

Time budget: 5-10 minutes

---

# AGENT 10: TREND ESTIMATOR

Agent ID: trend_estimator
Phase: 5 (Analysis) | Run ID: {RUN_ID}

## Purpose
Produce quarterly trend estimates for key factors of each Tier 1-2 country.

## Inputs
- /data/countries/*.json (just updated by Agent 9)
- /staging/processed/factor_updates_{DATE}.json (event_signals)
- /staging/raw_collected/news_events_{DATE}.json

## Output
- /staging/trends/trend_estimates_{DATE}.json
- Update trend fields in /data/countries/*.json

## Instructions

For each Tier 1-2 country (55 countries), estimate trends for these factors:
1. GDP real growth rate
2. Inflation rate
3. Current account balance
4. Public debt trajectory
5. Political stability
6. Military expenditure
7. Trade openness
8. FDI inflows
9. Currency strength
10. Overall investment risk
11. Top bilateral relationship health (top trading partner)

For each factor × country:

STEP A: Look at current value and any available historical values.
Determine quantitative direction.

STEP B: Look at event_signals from Agent 7 and news events from Agent 3
that affect this country or factor. Determine qualitative signal.

STEP C: Combine into a trend assessment:

{
  "country_code": "TUR",
  "factor_path": "macroeconomic.inflation_rate_cpi_pct",
  "current_value": 45.2,
  "trend": "decrease",
  "confidence": 0.65,
  "reasoning": "Turkey's inflation has been declining from its 85% peak
    in late 2024, supported by aggressive monetary tightening. The central
    bank maintained high rates this quarter. However, the pace of decline
    is slowing, and fiscal pressures from earthquake reconstruction spending
    pose upside risk to inflation.",
  "supporting_evidence": [
    "Central bank held rate at 47.5% at February meeting",
    "Monthly CPI data showing deceleration trend",
    "IMF forecast projects 30% by year-end"
  ],
  "counter_arguments": [
    "Fiscal expansion could reignite price pressures",
    "Lira depreciation adding to import costs"
  ],
  "investor_implication": "Turkish fixed income may offer value as
    disinflation continues, but currency risk remains elevated."
}

Total estimates: ~605 (55 countries × 11 factors)

Be efficient. For stable, uneventful countries, the reasoning can be brief.
Focus depth on countries with significant changes this week.

Time budget: 30-45 minutes

---

# AGENT 11: DERIVED METRICS CALCULATOR

Agent ID: derived_metrics_calculator
Phase: 5 | Run ID: {RUN_ID}

## Purpose
Compute composite and derived scores from base factors.

## Instructions
For each country, compute and write to the "derived" section:

1. resource_self_sufficiency_index (0-1):
   Average of (production/consumption) for energy, food, water, key minerals
   Cap each component at 1.0

2. energy_independence_index (0-1):
   Domestic energy production / domestic energy consumption

3. supply_chain_chokepoint_exposure (0-1):
   Based on maritime_chokepoint_dependency and trade volumes

4. composite_national_power_index (0-100):
   = 35% × economic_score + 25% × military_score +
     20% × technology_score + 10% × diplomatic_score + 10% × soft_power
   Where each component is normalized to 0-100

5. political_risk_premium (basis points):
   Start with: sovereign rating → base spread
   Adjust: +50bps if political_stability < -1.0
   Adjust: +100bps if active conflict
   Adjust: +200bps if under comprehensive sanctions
   Adjust: +50bps if democracy_index < 4.0

6. market_accessibility_score (0-1):
   Based on: capital_account_openness, stock_market_cap,
   financial_development_index, ease_of_doing_business

7. Update global_rankings.json with all countries ranked by key metrics

Time budget: 10-15 minutes

---

# AGENT 12: ALERT GENERATOR

Agent ID: alert_generator
Phase: 5 | Run ID: {RUN_ID}

## Instructions
1. Read /data/indices/alert_index.json (previous alerts)
2. Scan all updated country data for threshold breaches:

CRITICAL triggers:
- default_probability > 0.5
- currency_crisis_probability > 0.7
- active conflict escalated to "high"
- coup or unconstitutional leadership change
- comprehensive sanctions imposed
- expropriation of foreign assets

WARNING triggers:
- credit rating downgrade
- political_stability trend = strong_decrease
- GDP trend = strong_decrease (2+ quarters)
- inflation > 50%
- reserves < 3 months imports
- election within 30 days in unstable country

WATCH triggers:
- Any trend direction reversal
- New targeted sanctions
- Policy shift announcement
- Leadership change
- Major protests

3. For existing alerts: update status (ongoing/escalated/deescalated/resolved)
4. Write updated alert_index.json
5. Write updated event_feed.json

Time budget: 10 minutes

---

# AGENT 13: COUNTRY PROFILE SYNTHESIZER

Agent ID: profile_synthesizer
Phase: 6 | Run ID: {RUN_ID}

## Instructions
For each Tier 1-2 country (55 countries):

Read the country's full data file and this week's events.
Generate a narrative section:

{
  "narrative": {
    "generated_at": "{TIMESTAMP}",
    "executive_summary": "3-5 sentences. Current state, key headline,
      what an investor should know first.",
    "key_changes_this_week": [
      "Bullet point 1",
      "Bullet point 2"
    ],
    "outlook": "2-3 sentences on trajectory. Key risks and opportunities.",
    "investor_implications": "2-3 sentences. Asset class implications,
      positioning suggestions, risk flags.",
    "data_quality_note": "Note any significant data gaps or
      low-confidence factors."
  }
}

Guidelines:
- Be concise and factual, not sensational
- Lead with what changed, not background
- If nothing significant changed: say so briefly
- For countries with active alerts: reference them
- Write for a sophisticated investor, not a general audience

Time budget: 20-30 minutes (batch process, ~30 seconds per country)

---

# AGENT 14: WEEKLY BRIEFING GENERATOR

Agent ID: briefing_generator
Phase: 6 | Run ID: {RUN_ID}

## Instructions
Generate /data/global/weekly_briefing_{DATE}.json

Read: all country narratives, alert_index, event_feed, financial data

Produce:
1. headline: One compelling sentence summarizing the week
2. top_stories: 3-5 most important developments, each with title,
   summary (3-4 sentences), countries affected, investor impact
3. regional_summaries: 2-3 sentences per region (10 regions)
4. market_context: key commodity/currency/rate moves
5. watchlist_updates: ongoing situations with changes
6. data_quality_summary: high-level stats on this week's update

Write in clear, professional language. Investor audience.

Time budget: 10-15 minutes

---

# AGENT 15: DATA QUALITY REPORTER

Agent ID: quality_reporter
Phase: 7 | Run ID: {RUN_ID}

## Instructions
Generate /data/metadata/quality_report_{DATE}.json

1. COVERAGE: For each country, count non-null factors / total expected factors
   Report: Tier 1 avg, Tier 2 avg, Tier 3 avg
   Flag any Tier 1 country below 80%

2. STALENESS: List factors older than their expected update frequency
   Sort by priority (Tier 1 > Tier 2 > Tier 3)

3. CONFIDENCE: Average confidence per country and per layer
   Flag anything below 0.3

4. VALIDATION: Summarize accept/reject/escalate ratios from Agent 8

5. AGENT PERFORMANCE: Duration and record counts from run_log.json

6. RECOMMENDATIONS: Suggest actions for next week
   "Investigate source X which returned errors"
   "Country Y has degraded coverage"
   "Consider adding source Z for better coverage"

⚠️ PAUSE and present quality summary to human operator.

Time budget: 5 minutes

---

# AGENT 16: ARCHIVE & COMMIT PREPARER

Agent ID: archive_commit
Phase: 7 | Run ID: {RUN_ID}

## Instructions
1. Create /archive/{RUN_ID}/ directory
2. Copy current /data/metadata/last_update.json to archive
   (lightweight snapshot — full data is in git history)
3. Clean /staging/raw_collected/ (delete files)
4. Keep /staging/validated/ and /staging/trends/ for reference
5. Update /data/chunks/manifest.json with current file sizes and dates
6. Generate chunked versions of data for the web UI:
   - /data/chunks/country-summary/all_countries_summary.json
     (extract minimal fields from each country for map rendering)
   - Ensure all country-detail chunks are up to date
   - Update relation_index.json with latest composite scores
7. Prepare git commit message:

   "Weekly update {RUN_ID}

   Countries updated: {N}
   Relations updated: {N}
   New alerts: {N critical}, {N warning}, {N watch}
   Coverage: {pct}% avg across Tier 1
   Quality: {confidence_avg} avg confidence

   Top changes:
   - {change_1}
   - {change_2}
   - {change_3}"

8. Print the commit message for human to review and execute:
   git add -A && git commit -m "..." && git push

Time budget: 5 minutes
```

---

## Environment Setup

Before first run, ensure the project structure exists:

```bash
#!/bin/bash
# /agents/scripts/setup_project.sh

mkdir -p /geopolitical-model/{agents/{config,prompts,scripts},data/{countries,relations,supranational,indices,timeseries,metadata,global,chunks/{country-summary,country-detail,relations,timeseries,global,supranational}},staging/{raw_collected,processed,validated,trends},web/{js,css,assets},archive,docs,tests/{fixtures/{mock_sources,expected_outputs,seed_data},schemas,scripts,reports}}

# Initialize metadata files
echo '{"schema_version": "1.0", "last_full_run": null}' > /geopolitical-model/data/metadata/schema_version.json
echo '{}' > /geopolitical-model/data/metadata/last_update.json
echo '[]' > /geopolitical-model/data/metadata/update_log.json
echo '{"alerts": []}' > /geopolitical-model/data/indices/alert_index.json
echo '{"keys": [], "last_modified": null}' > /geopolitical-model/data/chunks/manifest.json

echo "Project structure initialized."
```
