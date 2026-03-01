# Geopolitical Intelligence Model — Agent Architecture

**Version:** 1.0-draft
**Date:** 2026-03-01
**Status:** Design Phase
**Depends on:** `01_FACTOR_MODEL_SPEC.md`

---

## Architecture Overview

### Operating Model

```
┌─────────────────────────────────────────────────────────┐
│                   WEEKLY UPDATE CYCLE                     │
│                                                           │
│  Human triggers Claude Code MAX session                   │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │  ORCHESTRATOR    │ Reads update_plan.json              │
│  │  (Master Agent)  │ Dispatches sub-agents sequentially  │
│  └────────┬────────┘                                     │
│           │                                               │
│     ┌─────┼─────┬──────┬──────┬──────┐                   │
│     ▼     ▼     ▼      ▼      ▼      ▼                   │
│   [T1]  [T2]  [T3]   [T4]   [T5]   [T6]                │
│   Data  Data  Data   Proc.  Valid. Synth.                │
│   Gatherers          essors  ators                        │
│     │     │     │      │      │      │                   │
│     └─────┴─────┴──────┴──────┴──────┘                   │
│                    │                                      │
│                    ▼                                      │
│            /data (JSON files)                             │
│            Updated in git repo                            │
│                    │                                      │
│                    ▼                                      │
│            Static Web UI                                  │
│            (reads /data, renders map)                     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **No live backend.** The web UI is a static site (HTML/JS/CSS) that reads JSON data files. All intelligence is pre-computed.

2. **Weekly batch processing.** You trigger a Claude Code MAX session that runs the full agent pipeline. Output: updated JSON files committed to the data repository.

3. **Sequential agent execution.** Claude Code runs agents one at a time in a defined order. Each agent reads inputs (previous agent outputs + existing data), performs its task, writes outputs.

4. **File-based communication.** Agents communicate through the filesystem. No message queues, no databases — just JSON files in a defined directory structure.

5. **Git as audit trail.** Every weekly run commits changes with a timestamped message. Git diff shows exactly what changed and when.

6. **Idempotent agents.** Each agent can be re-run safely. If a run fails partway, you restart from the failed agent, not from scratch.

---

## Directory Structure

```
/geopolitical-model
├── /agents                          # Agent scripts and configs
│   ├── /config
│   │   ├── orchestrator.md          # Master run plan
│   │   ├── agent_official_stats.md  # Config for each agent
│   │   ├── agent_news_events.md
│   │   ├── agent_financial.md
│   │   ├── agent_trade_sanctions.md
│   │   ├── agent_military_conflict.md
│   │   ├── agent_political.md
│   │   ├── agent_processor.md
│   │   ├── agent_validator.md
│   │   ├── agent_trend_estimator.md
│   │   ├── agent_synthesizer.md
│   │   └── agent_alert_generator.md
│   ├── /prompts                     # Reusable prompt templates
│   │   ├── extraction_prompt.md
│   │   ├── validation_prompt.md
│   │   ├── trend_estimation_prompt.md
│   │   └── synthesis_prompt.md
│   └── /scripts                     # Shell scripts for orchestration
│       ├── run_weekly_update.sh
│       ├── run_single_agent.sh
│       └── validate_data.sh
│
├── /data                            # THE MODEL (output of agents)
│   ├── /countries
│   │   ├── USA.json
│   │   ├── CHN.json
│   │   └── ...
│   ├── /relations
│   │   ├── USA_CHN.json
│   │   └── ...
│   ├── /supranational
│   ├── /indices
│   ├── /timeseries
│   ├── /metadata
│   └── /global
│
├── /staging                         # Intermediate agent outputs
│   ├── /raw_collected               # Raw data from gatherer agents
│   ├── /processed                   # Structured data from processor
│   ├── /validated                   # Data after validation
│   ├── /trends                      # Trend estimations
│   └── /run_log.json               # Current run progress and status
│
├── /web                             # Static web UI
│   ├── index.html
│   ├── /js
│   ├── /css
│   └── /assets
│
├── /archive                         # Historical snapshots
│   ├── /2026-Q1-W01
│   ├── /2026-Q1-W02
│   └── ...
│
└── /docs                            # Project documentation
    ├── 01_FACTOR_MODEL_SPEC.md
    ├── 02_AGENT_ARCHITECTURE.md
    ├── 03_REQUIREMENTS.md
    ├── 04_TEST_PLAN.md
    └── ...
```

---

## Agent Definitions

### Execution Order

The weekly update runs agents in this exact sequence:

```
Phase 1: DATA GATHERING (can potentially run in parallel)
  1. Agent: Official Statistics Gatherer
  2. Agent: Financial Data Gatherer
  3. Agent: News & Events Gatherer
  4. Agent: Trade & Sanctions Gatherer
  5. Agent: Military & Conflict Gatherer
  6. Agent: Political & Regulatory Gatherer

Phase 2: PROCESSING
  7. Agent: Fact Extractor & Structurer

Phase 3: VALIDATION
  8. Agent: Cross-Validation & Anomaly Detection

Phase 4: INTEGRATION
  9. Agent: Data Integrator (merges validated data into /data)

Phase 5: ANALYSIS
  10. Agent: Trend Estimator
  11. Agent: Derived Metrics Calculator
  12. Agent: Alert Generator

Phase 6: SYNTHESIS
  13. Agent: Country Profile Synthesizer
  14. Agent: Weekly Briefing Generator

Phase 7: FINALIZATION
  15. Agent: Data Quality Report Generator
  16. Agent: Archive & Commit
```

---

### Agent 1: Official Statistics Gatherer

```yaml
agent_id: official_stats_gatherer
phase: 1_gathering
priority: 1

purpose: >
  Collect updated official statistics from authoritative international
  and national sources. Focus on macroeconomic indicators, demographics,
  trade statistics, and development indices.

input_files:
  - /data/metadata/data_sources.json       # Registry of API endpoints and URLs
  - /data/indices/country_list.json        # Which countries to update
  - /data/metadata/last_update.json        # What was last collected and when

output_files:
  - /staging/raw_collected/official_stats_{date}.json

data_sources:
  primary:
    - name: World Bank Open Data API
      url: https://api.worldbank.org/v2/
      indicators:
        - NY.GDP.MKTP.CD          # GDP current USD
        - NY.GDP.MKTP.KD.ZG       # GDP growth rate
        - NY.GDP.PCAP.CD          # GDP per capita
        - FP.CPI.TOTL.ZG         # Inflation CPI
        - BN.CAB.XOKA.GD.ZS      # Current account % GDP
        - GC.DOD.TOTL.GD.ZS      # Central govt debt % GDP
        - SL.UEM.TOTL.ZS         # Unemployment rate
        - SP.POP.TOTL             # Population
        - SP.DYN.LE00.IN         # Life expectancy
        - SE.ADT.LITR.ZS         # Literacy rate
        # ... (full list in data_sources.json)
      rate_limit: 50 requests/minute
      auth: none

    - name: IMF World Economic Outlook
      url: https://www.imf.org/external/datamapper/api/
      data: GDP forecasts, inflation forecasts, fiscal balances
      update_cadence: biannual (April, October)
      auth: none

    - name: UN Comtrade
      url: https://comtradeapi.un.org/
      data: Bilateral trade flows by HS code
      rate_limit: 100 requests/hour (with API key)
      auth: api_key

    - name: World Bank WGI
      url: https://info.worldbank.org/governance/wgi/
      data: Governance indicators (6 dimensions)
      update_cadence: annual

    - name: UNDP Human Development Reports
      url: https://hdr.undp.org/data-center/
      data: HDI, GII, IHDI
      update_cadence: annual

  secondary:
    - name: CIA World Factbook
      url: https://www.cia.gov/the-world-factbook/
      data: Country overviews, geography, demographics
      method: web_scraping
      note: Backup source for cross-validation

    - name: National statistics offices
      method: web_fetch per country
      note: For Tier 1 countries, check national stats office directly

collection_strategy: |
  1. Check last_update.json for each indicator × country combination
  2. Skip if data was updated within expected cadence (e.g., skip monthly GDP if last checked 2 weeks ago)
  3. For each due update:
     a. Query primary API
     b. Parse response into standardized format
     c. Compare with previous value
     d. Flag if change exceeds expected range (>2 standard deviations from trend)
  4. Write all collected data to staging with source attribution

output_format: |
  {
    "collection_date": "2026-03-01T12:00:00Z",
    "agent": "official_stats_gatherer",
    "records": [
      {
        "country_code": "USA",
        "factor_path": "macroeconomic.gdp_nominal_usd",
        "new_value": 28500000000000,
        "previous_value": 27900000000000,
        "source": "World Bank API",
        "source_url": "https://api.worldbank.org/v2/...",
        "source_date": "2025-12-31",
        "confidence": 0.95,
        "change_pct": 2.15,
        "flag": null
      },
      ...
    ],
    "errors": [],
    "skipped": [],
    "summary": {
      "total_queries": 450,
      "successful": 438,
      "failed": 3,
      "skipped_not_due": 9,
      "new_data_points": 312,
      "flagged_anomalies": 5
    }
  }

error_handling: |
  - API timeout: retry 3 times with exponential backoff
  - API error 4xx: log and skip, flag for manual review
  - API error 5xx: retry 3 times, then skip and flag
  - Unexpected data format: log raw response, skip, flag
  - Missing country: log, continue with others

estimated_duration: 15-30 minutes
estimated_api_calls: 300-500 per run
```

---

### Agent 2: Financial Data Gatherer

```yaml
agent_id: financial_data_gatherer
phase: 1_gathering
priority: 2

purpose: >
  Collect current financial market data: exchange rates, sovereign bond yields,
  credit default swaps, stock market indices, commodity prices, and
  central bank policy rates.

input_files:
  - /data/indices/country_list.json
  - /data/metadata/last_update.json

output_files:
  - /staging/raw_collected/financial_data_{date}.json

data_sources:
  primary:
    - name: Free financial APIs
      candidates:
        - Yahoo Finance (via web_fetch)
        - ExchangeRate-API (free tier)
        - Alpha Vantage (free tier, 5/min)
      data: Exchange rates, stock indices

    - name: Trading Economics (web_fetch)
      url: https://tradingeconomics.com/
      data: >
        Bond yields, CDS spreads, policy rates, credit ratings,
        economic indicators with historical data
      method: web_fetch + extraction
      note: Primary source for sovereign credit ratings and policy rates

    - name: Central bank websites
      method: web_fetch per major central bank
      data: Policy rate decisions, minutes summaries
      countries: Tier 1 only

    - name: CBOE / market data
      data: VIX, currency volatility indices
      method: web_fetch

  secondary:
    - name: BIS Statistics
      url: https://www.bis.org/statistics/
      data: Cross-border banking, FX turnover, debt securities

collection_strategy: |
  1. Fetch current exchange rates for all Tier 1-2 currencies vs USD
  2. Fetch sovereign bond yields (10Y benchmark) for Tier 1-2
  3. Fetch stock market index levels and weekly change for Tier 1
  4. Fetch latest central bank policy rate for Tier 1-2
  5. Fetch sovereign credit ratings (check for changes since last run)
  6. Fetch commodity prices (oil, gas, gold, copper, lithium, wheat, etc.)
  7. Compute week-over-week changes
  8. Flag significant moves (>2% weekly change in FX, >50bps in yields)

output_format: |
  Same structure as Agent 1 output, with additional fields:
  - "market_timestamp": when the market data was captured
  - "weekly_change_pct": computed change from previous week
  - "monthly_change_pct": computed change from 4 weeks ago
  - "volatility_flag": boolean if move is unusual

estimated_duration: 10-20 minutes
```

---

### Agent 3: News & Events Gatherer

```yaml
agent_id: news_events_gatherer
phase: 1_gathering
priority: 3

purpose: >
  Scan news sources for geopolitically and economically significant events
  that occurred in the past week. Extract structured event records with
  country attribution, event type, severity, and relevance scoring.

input_files:
  - /data/indices/country_list.json
  - /data/metadata/last_update.json
  - /staging/raw_collected/previous_events.json    # To avoid duplicates

output_files:
  - /staging/raw_collected/news_events_{date}.json

data_sources:
  primary:
    - name: GDELT Project
      url: https://api.gdeltproject.org/
      data: >
        Global event database. Pre-extracted events from worldwide news.
        CAMEO-coded event types. Updated every 15 minutes.
      method: API query
      query_strategy: >
        Query by country for Tier 1-2 countries.
        Filter for event types: military actions, diplomatic events,
        economic actions, political changes, natural disasters,
        social unrest, sanctions, elections.
      note: >
        GDELT is the backbone. It provides structured events
        already extracted from news. We use this FIRST, then
        supplement with direct news reading.

    - name: ACLED
      url: https://acleddata.com/
      data: Armed conflict events, protests, riots, political violence
      method: API query
      auth: api_key (free for research)
      note: Authoritative for conflict events

    - name: RSS feeds from major wire services
      feeds:
        - Reuters World News
        - AP News International
        - Al Jazeera
        - BBC World
        - SCMP (Asia focus)
        - Africa News
      method: web_fetch RSS → parse → filter relevant articles
      strategy: >
        Fetch headlines + summaries. Use LLM to classify relevance
        to geopolitical model. Only fetch full article for
        highly relevant stories.

  secondary:
    - name: Government press releases
      method: web_fetch key government sites for Tier 1 countries
      focus: >
        Foreign ministry statements, central bank announcements,
        trade policy announcements, sanctions announcements
    - name: Think tank publications
      feeds:
        - CSIS
        - Brookings
        - IISS
        - Chatham House
        - Carnegie Endowment
      method: web_fetch weekly publications pages

collection_strategy: |
  1. Query GDELT for past 7 days, all Tier 1-2 countries
     - Filter: Goldstein scale > |5| (significant events)
     - Extract: actor1, actor2, event_type, date, tone, source_url
  2. Query ACLED for past 7 days, all countries with known conflicts
  3. Fetch RSS feeds, extract headlines + summaries for past 7 days
  4. For each news item, use LLM to:
     a. Classify: is this relevant to our factor model? (yes/no/maybe)
     b. If yes: extract structured event record (see format below)
     c. Rate severity: minor / moderate / major / transformative
     d. Identify affected factors: which parts of the model does this impact?
     e. Identify affected countries (may be multiple)
  5. Deduplicate: same event reported by multiple sources → merge
  6. For top 20 most significant events, fetch full article via web_fetch
     and extract detailed analysis

output_format: |
  {
    "collection_date": "2026-03-01",
    "agent": "news_events_gatherer",
    "events": [
      {
        "event_id": "evt_20260225_001",
        "headline": "Country X announces 25% tariff on Country Y goods",
        "date": "2026-02-25",
        "event_type": "trade_policy_change",
        "cameo_code": "0231",
        "countries_involved": ["XXX", "YYY"],
        "primary_country": "XXX",
        "actors": [
          {"name": "Ministry of Trade, Country X", "role": "initiator"},
          {"name": "Country Y", "role": "target"}
        ],
        "severity": "major",
        "certainty_level": "officially_announced",
        "affected_factors": [
          "relations.XXX_YYY.trade.avg_tariff",
          "macroeconomic.XXX.trade_balance",
          "derived.XXX.trade_policy_orientation"
        ],
        "summary": "...",
        "detailed_analysis": "...",
        "sources": [
          {"name": "Reuters", "url": "...", "date": "2026-02-25"},
          {"name": "GDELT", "event_id": "..."}
        ],
        "source_count": 5,
        "tone_score": -3.5,
        "relevance_score": 0.92,
        "investor_impact_assessment": "...",
        "confidence": 0.85
      },
      ...
    ],
    "summary": {
      "total_events_scanned": 12500,
      "relevant_events_extracted": 180,
      "events_by_severity": {
        "transformative": 0,
        "major": 8,
        "moderate": 45,
        "minor": 127
      },
      "events_by_region": {...},
      "top_themes_this_week": [...]
    }
  }

event_type_taxonomy: |
  POLITICAL:
    - election_held
    - election_announced
    - government_formed
    - government_collapsed
    - leader_change
    - coup_attempt
    - constitutional_change
    - policy_announcement
    - legislation_passed
    - judicial_ruling
  DIPLOMATIC:
    - summit_meeting
    - treaty_signed
    - treaty_withdrawn
    - ambassador_recalled
    - diplomatic_expulsion
    - recognition_change
    - mediation_attempt
    - international_organization_action
  MILITARY:
    - military_deployment
    - military_exercise
    - border_incident
    - armed_conflict_escalation
    - armed_conflict_deescalation
    - ceasefire
    - arms_deal
    - nuclear_test_or_threat
    - cyber_attack_attributed
  ECONOMIC:
    - trade_policy_change
    - sanctions_imposed
    - sanctions_lifted
    - central_bank_decision
    - sovereign_rating_change
    - major_deal_or_acquisition
    - debt_default_or_restructuring
    - currency_crisis
    - nationalization_or_expropriation
    - infrastructure_project_announced
  SOCIAL:
    - mass_protest
    - civil_unrest
    - humanitarian_crisis
    - refugee_movement
    - pandemic_outbreak
    - natural_disaster
    - terrorist_attack
  RESOURCE:
    - resource_discovery
    - production_disruption
    - export_restriction
    - commodity_price_shock
    - energy_infrastructure_change
    - water_dispute

certainty_levels: |
  - rumor_speculation          # Unverified reports
  - single_source_report       # One credible source
  - multi_source_confirmed     # Multiple independent sources
  - officially_announced       # Government/official statement
  - legally_enacted            # Law passed, treaty signed
  - observed_in_effect         # Measurable in data

estimated_duration: 30-60 minutes (LLM-intensive)
```

---

### Agent 4: Trade & Sanctions Gatherer

```yaml
agent_id: trade_sanctions_gatherer
phase: 1_gathering
priority: 4

purpose: >
  Monitor changes in trade relationships, sanctions regimes, trade agreements,
  and supply chain disruptions. Update bilateral trade data.

input_files:
  - /data/relations/                       # Existing bilateral data
  - /data/indices/relation_index.json
  - /data/metadata/last_update.json

output_files:
  - /staging/raw_collected/trade_sanctions_{date}.json

data_sources:
  - UN Comtrade (quarterly trade data)
  - OFAC Sanctions List (US)
  - EU Sanctions Map
  - UN Security Council Sanctions
  - WTO dispute settlement updates
  - Trade agreement repositories (UNCTAD, WTO RTA database)
  - Shipping data: MarineTraffic / VesselFinder (free tier, summary level)

collection_strategy: |
  1. Check for new sanctions actions (OFAC, EU, UN) since last run
  2. Check WTO for new dispute filings or rulings
  3. Check for new trade agreements signed or entered into force
  4. For Tier 1 bilateral pairs: update trade flow data if new quarter available
  5. Monitor shipping disruption reports (chokepoint status)
  6. Extract structured records for all changes

estimated_duration: 15-25 minutes
```

---

### Agent 5: Military & Conflict Gatherer

```yaml
agent_id: military_conflict_gatherer
phase: 1_gathering
priority: 5

purpose: >
  Monitor changes in military posture, conflict intensity, arms transfers,
  military exercises, and defense spending announcements.

input_files:
  - /data/countries/*/military section
  - /data/metadata/last_update.json

output_files:
  - /staging/raw_collected/military_conflict_{date}.json

data_sources:
  - SIPRI Military Expenditure Database (annual, check for updates)
  - SIPRI Arms Transfer Database
  - ACLED (already queried by news agent, but extract military-specific events)
  - IISS Military Balance (annual publication, check for new edition)
  - Global Firepower (web_fetch country pages for Tier 1)
  - Defense ministry press releases (Tier 1 countries)
  - NATO communiques
  - OSINT sources: Janes, Defense News headlines

collection_strategy: |
  1. Check SIPRI for database updates
  2. Extract military-specific events from ACLED data
  3. Check defense news headlines for major procurement, deployment changes
  4. For active conflicts: update intensity assessments
  5. Check for military exercise announcements
  6. Check for nuclear/missile test activity
  7. Update arms transfer records if new data available

estimated_duration: 15-20 minutes
```

---

### Agent 6: Political & Regulatory Gatherer

```yaml
agent_id: political_regulatory_gatherer
phase: 1_gathering
priority: 6

purpose: >
  Monitor political changes: elections, government changes, policy shifts,
  regulatory changes, and institutional developments.

input_files:
  - /data/countries/*/political section
  - /data/metadata/last_update.json

output_files:
  - /staging/raw_collected/political_regulatory_{date}.json

data_sources:
  - Election Guide (electionguide.org) — upcoming and recent elections
  - Freedom House — annual updates
  - EIU Democracy Index — annual
  - Transparency International CPI — annual
  - Varieties of Democracy (V-Dem) — annual
  - Government websites for Tier 1 countries (policy announcements)
  - Regulatory change trackers

collection_strategy: |
  1. Check election calendar: any elections in past week or next 4 weeks?
  2. Check for government changes (new PM, cabinet reshuffles)
  3. Check for major policy announcements (Tier 1 countries)
  4. Check for index updates (Freedom House, EIU, TI — annual, but check)
  5. Monitor for constitutional changes, coup attempts, state of emergency
  6. Check for regulatory changes affecting foreign investment

estimated_duration: 15-20 minutes
```

---

### Agent 7: Fact Extractor & Structurer

```yaml
agent_id: fact_extractor
phase: 2_processing
priority: 7

purpose: >
  Take all raw collected data from Phase 1 agents and transform into
  structured factor updates. Map each data point to the correct location
  in the factor model schema. Resolve format inconsistencies.

input_files:
  - /staging/raw_collected/official_stats_{date}.json
  - /staging/raw_collected/financial_data_{date}.json
  - /staging/raw_collected/news_events_{date}.json
  - /staging/raw_collected/trade_sanctions_{date}.json
  - /staging/raw_collected/military_conflict_{date}.json
  - /staging/raw_collected/political_regulatory_{date}.json
  - /docs/01_FACTOR_MODEL_SPEC.md          # Schema reference

output_files:
  - /staging/processed/factor_updates_{date}.json

processing_logic: |
  For each raw record from gathering agents:

  1. IDENTIFY target factor:
     - Map the data point to a specific factor_path in the schema
     - e.g., "World Bank GDP indicator" → "macroeconomic.gdp_nominal_usd"
     - If a data point doesn't map to any factor, log and skip

  2. NORMALIZE value:
     - Convert units to schema standard (all monetary to USD, etc.)
     - Handle currency conversions using latest FX rates
     - Handle different fiscal year definitions
     - Resolve conflicting date formats

  3. COMPARE with existing:
     - Load current value from /data/countries/{code}.json
     - Compute change (absolute and percentage)
     - Flag if change is statistically unusual

  4. ASSIGN confidence:
     - Source reliability × corroboration count × data recency
     - Official API data from World Bank: base confidence 0.90
     - News-extracted data: base confidence 0.50-0.70
     - Single-source unverified: base confidence 0.20-0.40

  5. For NEWS EVENTS specifically:
     - Determine if the event should update a factor value
       or just be logged as a supporting event for trend estimation
     - Only events at certainty_level >= "officially_announced"
       should directly update factor values
     - Lower certainty events go to trend estimation as signals

  6. Handle BILATERAL RELATIONS:
     - Events involving two countries → update relation record
     - Map event type to relation sub-dimension
     - e.g., "sanctions imposed" → relation.trade.sanctions_a_on_b = true

output_format: |
  {
    "processing_date": "2026-03-01",
    "agent": "fact_extractor",
    "factor_updates": [
      {
        "update_id": "upd_001",
        "target": "country",
        "country_code": "USA",
        "factor_path": "macroeconomic.gdp_real_growth_rate_pct",
        "new_value": 2.3,
        "previous_value": 2.1,
        "change_absolute": 0.2,
        "change_pct": 9.5,
        "unit": "percent",
        "source_agent": "official_stats_gatherer",
        "source_name": "World Bank API",
        "source_url": "...",
        "source_date": "2025-12-31",
        "confidence": 0.93,
        "anomaly_flag": false,
        "requires_validation": false,
        "notes": ""
      },
      ...
    ],
    "relation_updates": [...],
    "event_signals": [
      // Events that don't directly update factors but inform trends
      {
        "event_id": "evt_...",
        "affected_countries": ["USA", "CHN"],
        "affected_factors": ["relations.USA_CHN.trade.*"],
        "signal_direction": "negative",
        "signal_strength": 0.7,
        "description": "..."
      }
    ],
    "unmapped_data": [...],   // Data that couldn't be mapped to schema
    "summary": {
      "total_input_records": 1250,
      "mapped_successfully": 1180,
      "unmapped": 70,
      "factor_updates_produced": 890,
      "relation_updates_produced": 120,
      "event_signals_produced": 45,
      "anomalies_flagged": 12
    }
  }

estimated_duration: 20-30 minutes
```

---

### Agent 8: Cross-Validation & Anomaly Detection

```yaml
agent_id: validator
phase: 3_validation
priority: 8

purpose: >
  Validate all proposed factor updates before they are integrated.
  Check for anomalies, contradictions, and data quality issues.
  Produce a validation report with accept/reject/flag recommendations.

input_files:
  - /staging/processed/factor_updates_{date}.json
  - /data/countries/                       # Current factor values
  - /data/timeseries/                      # Historical trends

output_files:
  - /staging/validated/validated_updates_{date}.json
  - /staging/validated/validation_report_{date}.json

validation_rules: |
  RULE 1: Plausibility Check
    - GDP growth rate: must be between -30% and +30%
    - Population: must not change >2% in one quarter
    - Military personnel: must not change >20% in one quarter
    - Exchange rate: flag if weekly change > 15%
    - Any percentage: must be 0-100
    - Any index 0-1: must be 0-1
    For each factor, define plausible ranges and max change rates

  RULE 2: Cross-Source Consistency
    - If same factor updated by multiple agents with different values:
      - If values within 5%: use highest-confidence source
      - If values diverge >5%: flag for review, use official source
    - If news reports contradict official data:
      - Official data prevails for current values
      - News event logged as signal for trend estimation

  RULE 3: Temporal Consistency
    - Load last 4 quarters from timeseries
    - Compute trend
    - If new value deviates >3 std dev from trend: flag as anomaly
    - Anomalies are not rejected, just flagged

  RULE 4: Internal Consistency
    - GDP composition must sum to ~100%
    - Export + domestic consumption <= production (for resources)
    - Debt ratios must be consistent with absolute values
    - Bilateral trade: A's exports to B ≈ B's imports from A

  RULE 5: Staleness Check
    - If a factor hasn't been updated in >2x its expected frequency:
      flag as potentially stale
    - E.g., if a quarterly indicator hasn't updated in 8 months

validation_output: |
  Each proposed update gets a verdict:
  - ACCEPT: passes all rules, auto-integrate
  - ACCEPT_WITH_NOTE: passes but has minor concerns
  - FLAG: anomalous but plausible, auto-integrate but mark in report
  - REJECT: fails plausibility or internal consistency
  - ESCALATE: requires human judgment (you review during the run)

  Decision distribution target:
  - ACCEPT: ~70% of updates
  - ACCEPT_WITH_NOTE: ~15%
  - FLAG: ~10%
  - REJECT: ~3%
  - ESCALATE: ~2%

escalation_protocol: |
  When an update is marked ESCALATE:
  1. Agent writes clear explanation of the concern
  2. Presents the data with sources
  3. Asks you (the human) to decide: accept, reject, or investigate further
  4. Your decision is logged for future learning

  Examples of ESCALATE scenarios:
  - Major leadership change reported by news but not official sources
  - Dramatic economic indicator change with single source
  - Conflict escalation claims from social media only
  - Sanctions changes that would significantly alter country profile

estimated_duration: 15-20 minutes
```

---

### Agent 9: Data Integrator

```yaml
agent_id: data_integrator
phase: 4_integration
priority: 9

purpose: >
  Take all validated and accepted updates and merge them into the
  main /data directory. Update timeseries. Maintain data versioning.

input_files:
  - /staging/validated/validated_updates_{date}.json
  - /data/                                 # Current model state

output_files:
  - /data/countries/*.json                 # Updated country files
  - /data/relations/*.json                 # Updated relation files
  - /data/timeseries/*.json               # Appended time series
  - /data/metadata/last_update.json       # Updated timestamps
  - /data/metadata/update_log.json        # What changed this run

integration_logic: |
  1. For each ACCEPTED or FLAGGED update:
     a. Read target JSON file
     b. Navigate to factor_path
     c. Record previous value in timeseries
     d. Write new value
     e. Update last_updated timestamp
     f. Update confidence score
     g. If FLAGGED, add to metadata.flags array

  2. For relation updates:
     a. Load or create relation file
     b. Update relevant sub-dimension
     c. Recompute composite scores (cooperation_index, etc.)

  3. Update indices:
     a. Regenerate global_rankings.json
     b. Update alert_index.json
     c. Update resource_index.json cross-references

  4. Timeseries management:
     a. Append new values with timestamps
     b. Keep last 20 quarters (5 years) of quarterly data
     c. Keep last 52 weeks of weekly data
     d. Archive older data to /archive

  5. Generate update_log entry:
     {
       "run_date": "2026-03-01",
       "updates_applied": 850,
       "countries_updated": 65,
       "relations_updated": 45,
       "flags_active": 12,
       "previous_snapshot": "/archive/2026-Q1-W08",
       "changes_summary": {...}
     }

estimated_duration: 5-10 minutes
```

---

### Agent 10: Trend Estimator

```yaml
agent_id: trend_estimator
phase: 5_analysis
priority: 10

purpose: >
  For each key factor of each Tier 1-2 country, produce a quarterly
  trend estimate (strong_growth → strong_decrease) with reasoning,
  confidence, and supporting evidence.

input_files:
  - /data/countries/*.json                 # Current values + historical
  - /data/timeseries/*.json               # Historical trends
  - /staging/raw_collected/news_events_{date}.json  # Recent events
  - /staging/processed/factor_updates_{date}.json   # Event signals

output_files:
  - /staging/trends/trend_estimates_{date}.json

factors_to_estimate: |
  For each Tier 1-2 country, estimate trends for:
  - GDP real growth rate
  - Inflation rate
  - Current account balance
  - Public debt trajectory
  - Political stability
  - Military expenditure trend
  - Trade openness trend
  - FDI inflow trend
  - Currency strength trend
  - Overall country risk trajectory
  - Key bilateral relationship trajectories (top 5 partners)

  Total: ~55 countries × ~11 factors = ~605 trend estimates

estimation_methodology: |

  For each factor × country:

  1. QUANTITATIVE SIGNAL:
     - Load last 8 quarterly values (or weekly for financial data)
     - Compute simple trend (linear regression slope)
     - Compute momentum (acceleration/deceleration)
     - Map to trend categories:
       slope > +2σ → strong_growth
       slope > +1σ → growth
       |slope| < 1σ → stable
       slope < -1σ → decrease
       slope < -2σ → strong_decrease

  2. QUALITATIVE SIGNAL:
     - Review event signals from this week
     - Consider policy announcements, political changes
     - Consider external shocks (sanctions, commodity prices)
     - Use LLM to assess: "Given these events, should the
       quantitative trend estimate be modified?"

  3. COMBINE:
     - If quantitative and qualitative agree: high confidence
     - If they disagree: moderate confidence, explain divergence
     - Weight recent events more heavily for fast-moving situations

  4. GENERATE REASONING:
     - Write 2-3 sentence explanation for each trend estimate
     - List top 3 supporting evidence points
     - List top 1-2 counter-arguments or risks to the estimate
     - This reasoning is displayed to users in the UI

prompt_template: |
  You are analyzing the trend for {factor_name} in {country_name}.

  Current value: {current_value}
  Historical values (last 8 quarters):
  {historical_values}

  Recent events affecting this factor:
  {relevant_events}

  Current global context:
  {global_context_summary}

  Based on the quantitative trend and recent events, provide:
  1. Trend estimate: strong_growth | growth | stable | decrease | strong_decrease
  2. Confidence: 0.0 to 1.0
  3. Reasoning: 2-3 sentences explaining your assessment
  4. Supporting evidence: top 3 data points or events
  5. Counter-arguments: what could invalidate this trend?
  6. Investor implication: one sentence on what this means for investors

  Respond in JSON format.

estimated_duration: 30-45 minutes (LLM-intensive, many inference calls)
```

---

### Agent 11: Derived Metrics Calculator

```yaml
agent_id: derived_metrics_calculator
phase: 5_analysis
priority: 11

purpose: >
  Compute all derived metrics from Layer 6 of the factor model.
  These are composite scores calculated from Layers 1-5 data.

input_files:
  - /data/countries/*.json
  - /data/relations/*.json
  - /data/supranational/*.json

output_files:
  - Updates derived_metrics section in each /data/countries/{code}.json
  - /data/global/global_rankings.json

computation_formulas: |

  resource_self_sufficiency_index:
    For each critical resource (energy, food, water, key minerals):
      sufficiency = min(1, domestic_production / domestic_consumption)
    Weighted average across resources, weighted by strategic criticality

  energy_independence_index:
    = domestic_energy_production / domestic_energy_consumption
    Capped at 1.0

  food_independence_index:
    = (domestic_food_production + food_reserves) /
      domestic_food_consumption
    Weighted by caloric contribution of main food categories

  supply_chain_chokepoint_exposure:
    = weighted sum of (trade_volume_through_chokepoint / total_trade)
    for each maritime chokepoint the country depends on
    Weighted by chokepoint disruption probability

  composite_national_power_index:
    = 0.35 × economic_power + 0.25 × military_power +
      0.20 × technological_capability + 0.10 × diplomatic_reach +
      0.10 × soft_power
    Each component is a normalized composite of relevant factors

  political_risk_premium_bps:
    Base rate from sovereign credit rating
    + adjustments for: political stability, conflict,
      sanctions, policy orientation, institutional quality
    Calibrated against actual CDS spreads where available

  currency_crisis_probability_12m:
    Logistic model based on:
    - Reserve adequacy (months of imports)
    - Current account deficit
    - External debt / exports
    - Exchange rate overvaluation proxy
    - Political stability
    - Capital account openness
    Historical calibration against past currency crises

  Each derived metric must include:
  - computed_value
  - computation_timestamp
  - input_factor_versions (which data points fed into this)
  - confidence (derived from confidence of input factors)

estimated_duration: 10-15 minutes
```

---

### Agent 12: Alert Generator

```yaml
agent_id: alert_generator
phase: 5_analysis
priority: 12

purpose: >
  Scan the updated model for conditions that warrant investor alerts.
  Generate structured alerts with severity, affected assets, and
  recommended monitoring actions.

input_files:
  - /data/countries/*.json (with updated trends and derived metrics)
  - /staging/raw_collected/news_events_{date}.json
  - /data/indices/alert_index.json         # Previous alerts

output_files:
  - /data/indices/alert_index.json         # Updated alerts
  - /data/global/event_feed.json           # Updated event feed

alert_triggers: |

  CRITICAL (immediate investor attention):
  - Sovereign default probability > 0.5
  - Currency crisis probability > 0.7
  - Active armed conflict escalation
  - Coup or unconstitutional government change
  - Comprehensive sanctions imposed by US or EU
  - Nationalization/expropriation of foreign assets
  - Capital controls imposed

  WARNING (monitor closely):
  - Sovereign rating downgrade
  - Political stability trend = strong_decrease
  - GDP trend = strong_decrease for 2+ consecutive quarters
  - Inflation > 50% (hyperinflation territory)
  - Reserves < 3 months of imports
  - Major trade partner relationship → hostile
  - Military mobilization or large-scale exercises near border
  - Election within 30 days in unstable country

  WATCH (be aware):
  - Any trend changing direction (growth → decrease or vice versa)
  - New sanctions (even targeted)
  - Significant policy shift announcement
  - Leadership change
  - Major protest movement
  - New trade dispute filed
  - Commodity price shock affecting key export

  Each alert includes:
  - severity: critical | warning | watch
  - title: one-line summary
  - description: 2-3 sentences
  - countries_affected: string[]
  - factors_affected: string[]
  - first_detected: timestamp
  - status: new | ongoing | escalated | deescalated | resolved
  - investor_action: string (e.g., "Review exposure to X")
  - related_events: string[] (event_ids)

alert_lifecycle: |
  - NEW: first time this condition is detected
  - ONGOING: condition persists from previous week
  - ESCALATED: severity increased since last week
  - DEESCALATED: severity decreased
  - RESOLVED: condition no longer present
  Alerts older than 12 weeks with no change → archive

estimated_duration: 10-15 minutes
```

---

### Agent 13: Country Profile Synthesizer

```yaml
agent_id: profile_synthesizer
phase: 6_synthesis
priority: 13

purpose: >
  Generate human-readable narrative summaries for each country profile.
  These are displayed in the UI when a user clicks on a country.

input_files:
  - /data/countries/*.json
  - /staging/trends/trend_estimates_{date}.json
  - /data/indices/alert_index.json

output_files:
  - Adds/updates "narrative" section in each /data/countries/{code}.json

output_content: |
  For each Tier 1-2 country, generate:

  1. EXECUTIVE SUMMARY (3-5 sentences):
     Current state overview. What's the headline story for this country
     right now? What should an investor know first?

  2. KEY CHANGES THIS WEEK (bullet points):
     What changed in the past week? Only include notable changes.

  3. OUTLOOK (2-3 sentences):
     Where is this country heading based on trend estimates?
     What are the key risks and opportunities?

  4. INVESTOR IMPLICATIONS (2-3 sentences):
     What does this mean for someone allocating capital?

  Format: Markdown-compatible text stored in the country JSON.

  Example:
  {
    "narrative": {
      "generated_at": "2026-03-01T15:00:00Z",
      "executive_summary": "Turkey continues to face...",
      "key_changes_this_week": [
        "Central bank raised policy rate by 250bps to 47.5%",
        "Lira depreciated 3.2% against USD"
      ],
      "outlook": "The tightening cycle appears to be...",
      "investor_implications": "Fixed income investors should...",
      "data_quality_note": "3 factors flagged as uncertain this week"
    }
  }

estimated_duration: 20-30 minutes (one LLM call per country, ~55 countries)
```

---

### Agent 14: Weekly Briefing Generator

```yaml
agent_id: briefing_generator
phase: 6_synthesis
priority: 14

purpose: >
  Generate a weekly global briefing document summarizing the most
  important changes across all countries and regions. Displayed
  as the "This Week" landing page in the UI.

input_files:
  - /data/global/event_feed.json
  - /data/indices/alert_index.json
  - /staging/trends/trend_estimates_{date}.json
  - All country narratives

output_files:
  - /data/global/weekly_briefing_{date}.json

content_structure: |
  {
    "briefing_date": "2026-03-01",
    "period": "2026-02-22 to 2026-03-01",

    "headline": "One-line global summary",

    "top_stories": [
      // 3-5 most significant developments this week
      {
        "title": "...",
        "summary": "3-4 sentences",
        "countries": [...],
        "investor_impact": "...",
        "severity": "...",
        "related_alert_ids": [...]
      }
    ],

    "regional_summaries": {
      "north_america": "2-3 sentences",
      "europe": "...",
      "east_asia": "...",
      "south_asia": "...",
      "middle_east_north_africa": "...",
      "sub_saharan_africa": "...",
      "latin_america": "...",
      "central_asia": "...",
      "southeast_asia": "...",
      "oceania": "..."
    },

    "market_context": {
      "key_commodity_moves": [...],
      "key_currency_moves": [...],
      "key_rate_decisions": [...],
      "risk_sentiment": "risk_on | neutral | risk_off"
    },

    "watchlist_updates": [
      // Changes to ongoing situations worth monitoring
    ],

    "data_quality_summary": {
      "countries_updated": 65,
      "factors_updated": 890,
      "validation_flags": 12,
      "escalations_resolved": 3,
      "data_freshness_concerns": [...]
    }
  }

estimated_duration: 10-15 minutes
```

---

### Agent 15: Data Quality Report

```yaml
agent_id: quality_reporter
phase: 7_finalization
priority: 15

purpose: >
  Generate a comprehensive quality report for the entire weekly run.
  Identifies data gaps, stale factors, validation concerns, and
  coverage metrics. This is your operational dashboard.

input_files:
  - /staging/run_log.json
  - /staging/validated/validation_report_{date}.json
  - /data/metadata/last_update.json
  - /data/countries/*.json

output_files:
  - /data/metadata/quality_report_{date}.json

report_contents: |
  1. COVERAGE MATRIX:
     For each country × layer, what percentage of factors have
     been updated within expected frequency?
     Flag: any Tier 1 country with coverage < 80%

  2. STALENESS REPORT:
     List all factors that are overdue for update
     Sorted by staleness severity

  3. CONFIDENCE DISTRIBUTION:
     Histogram of confidence scores across all active factors
     Flag: any factor with confidence < 0.3

  4. VALIDATION SUMMARY:
     Acceptance rate, rejection rate, escalation rate
     List of all flagged anomalies with resolution status

  5. SOURCE HEALTH:
     For each data source: was it reachable? Did it return valid data?
     Response times and error rates

  6. AGENT PERFORMANCE:
     Duration of each agent
     Error count per agent
     Data points processed per agent

  7. RECOMMENDATIONS:
     "These 5 factors need manual investigation"
     "These 3 sources appear to be down/changed"
     "Consider adding source X for better coverage of Y"

estimated_duration: 5 minutes
```

---

### Agent 16: Archive & Commit

```yaml
agent_id: archive_commit
phase: 7_finalization
priority: 16

purpose: >
  Create a snapshot of the current model state, archive the previous
  version, clean up staging, and prepare a git commit.

input_files:
  - /data/ (entire directory)
  - /staging/ (entire directory)

actions: |
  1. Copy current /data to /archive/{year}-Q{quarter}-W{week}
  2. Clean /staging (remove raw and processed files, keep reports)
  3. Update /data/metadata/schema_version.json
  4. Generate git commit message summarizing changes
  5. Stage all changed files
  6. Output commit message for human review before committing

commit_message_template: |
  Weekly update {date}

  Countries updated: {count}
  Relations updated: {count}
  Alerts: {new_critical} critical, {new_warning} warnings
  Data quality: {coverage_pct}% coverage, {confidence_avg} avg confidence

  Key changes:
  - {top_change_1}
  - {top_change_2}
  - {top_change_3}

estimated_duration: 2-5 minutes
```

---

## Total Weekly Run Estimate

```
Phase 1 (Gathering):    60-120 minutes
Phase 2 (Processing):   20-30 minutes
Phase 3 (Validation):   15-20 minutes
Phase 4 (Integration):  5-10 minutes
Phase 5 (Analysis):     50-75 minutes
Phase 6 (Synthesis):    30-45 minutes
Phase 7 (Finalization): 7-10 minutes
─────────────────────────────────────
TOTAL:                  ~3-5 hours per weekly run
```

With Claude Code MAX, this should be feasible in a single session. The most time-intensive parts are the LLM-based analysis (trend estimation, synthesis) and the web fetching (news, financial data).

---

## Error Recovery

```
If a run fails at Agent N:

1. Check /staging/run_log.json for last successful agent
2. Fix the issue (missing source, API error, data format change)
3. Re-run from Agent N onwards:
   ./scripts/run_single_agent.sh {agent_id}
   (Subsequent agents will pick up from where the pipeline left off)

If an entire run is corrupted:
1. Restore from /archive/{previous_week}
2. Re-run the entire pipeline

Run log format:
{
  "run_id": "2026-W09",
  "started_at": "2026-03-01T10:00:00Z",
  "agents": [
    {
      "agent_id": "official_stats_gatherer",
      "status": "completed",
      "started_at": "...",
      "completed_at": "...",
      "records_processed": 438,
      "errors": 3,
      "output_file": "..."
    },
    ...
  ],
  "current_agent": "validator",
  "overall_status": "in_progress"
}
```

---

## Security Considerations

- **No API keys in agent config files.** Store API keys in environment variables or a .env file excluded from git.
- **Web fetching respects robots.txt.** Agents should check and honor robots.txt.
- **Rate limiting.** Each agent config specifies rate limits for its sources. Agents must respect them.
- **No PII collection.** The model tracks countries and institutions, never individuals (except heads of state names, which are public).
- **Data licensing.** Track which sources have usage restrictions. Flag any data that cannot be publicly displayed.

---

## Next Documents

- `03_REQUIREMENTS.md` — Functional and non-functional requirements
- `04_TEST_PLAN.md` — Unit and end-to-end test specifications
- `05_AGENT_CONFIGS.md` — Ready-to-use Claude Code agent prompt files
- `06_WEB_UI_SPEC.md` — Frontend specification
- `07_DATA_SOURCES.md` — Complete data source registry with API details
