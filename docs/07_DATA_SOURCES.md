# Geopolitical Intelligence Model — Data Source Registry

**Version:** 1.1
**Date:** 2026-03-14
**Status:** Active
**Depends on:** `01_FACTOR_MODEL_SPEC.md`, `02_AGENT_ARCHITECTURE.md`

---

## Overview

This document catalogs every data source the agent pipeline uses. Each source includes: access method, API details, rate limits, cost, licensing, reliability assessment, and which factors it feeds.

Sources are rated:
- **Reliability:** ⭐⭐⭐ (excellent) to ⭐ (unreliable)
- **Cost:** 💰 Free, 💰💰 Freemium, 💰💰💰 Paid

---

## 1. Official Statistics Sources

### 1.1 World Bank Open Data API

```yaml
source_id: worldbank
name: World Bank Open Data
url: https://api.worldbank.org/v2/
method: REST API (JSON)
auth: None required
rate_limit: 50 requests/minute (soft limit)
cost: 💰 Free
license: Creative Commons Attribution 4.0 (CC-BY 4.0)
attribution_required: Yes — "Source: World Bank"
reliability: ⭐⭐⭐
update_cadence: Most indicators annual, some quarterly
coverage: 200+ countries, 1,600+ indicators
used_by_agent: Agent 1 (Official Stats Gatherer)

key_indicators:
  macroeconomic:
    - NY.GDP.MKTP.CD          # GDP current USD
    - NY.GDP.MKTP.KD.ZG       # GDP growth annual %
    - NY.GDP.PCAP.CD          # GDP per capita current USD
    - NY.GDP.MKTP.PP.CD       # GDP PPP current USD
    - FP.CPI.TOTL.ZG         # Inflation consumer prices annual %
    - GC.DOD.TOTL.GD.ZS      # Central government debt % GDP
    - BN.CAB.XOKA.GD.ZS      # Current account balance % GDP
    - NE.EXP.GNFS.CD         # Exports of goods and services
    - NE.IMP.GNFS.CD         # Imports of goods and services
    - BX.KLT.DINV.CD.WD      # FDI net inflows
    - FR.INR.DPST             # Deposit interest rate
    - FI.RES.TOTL.CD         # Total reserves including gold

  demographic:
    - SP.POP.TOTL             # Population total
    - SP.POP.GROW             # Population growth annual %
    - SP.DYN.LE00.IN         # Life expectancy at birth
    - SP.URB.TOTL.IN.ZS      # Urban population %
    - SL.UEM.TOTL.ZS         # Unemployment total %
    - SL.TLF.CACT.ZS         # Labor force participation rate
    - SE.ADT.LITR.ZS         # Literacy rate
    - SH.XPD.CHEX.GD.ZS     # Health expenditure % GDP
    - SP.DYN.IMRT.IN         # Infant mortality per 1000

  development:
    - SI.POV.GINI             # Gini index
    - SI.POV.DDAY             # Poverty headcount $2.15/day
    - HD.HCI.OVRL             # Human Capital Index

  governance:
    # World Governance Indicators (WGI) — separate dataset
    - VA.EST                  # Voice and Accountability
    - PS.EST                  # Political Stability
    - GE.EST                  # Government Effectiveness
    - RQ.EST                  # Regulatory Quality
    - RL.EST                  # Rule of Law
    - CC.EST                  # Control of Corruption

  infrastructure:
    - EG.ELC.ACCS.ZS         # Electricity access %
    - IT.NET.USER.ZS         # Internet users %
    - LP.LPI.OVRL.XQ         # Logistics Performance Index

example_api_call: |
  https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD
  ?format=json&date=2023:2025&per_page=5

notes: |
  - Most data has 1-2 year lag (2025 data available in mid-2026)
  - Some indicators update quarterly (GDP growth, inflation)
  - WGI updates annually
  - Best single source for standardized cross-country comparison
```

### 1.2 IMF Data

```yaml
source_id: imf
name: International Monetary Fund
urls:
  - https://www.imf.org/external/datamapper/api/        # DataMapper API
  - https://data.imf.org/api/                            # Data portal
method: REST API + web_fetch for publications
auth: None for most endpoints
rate_limit: Moderate (undocumented, ~100/hour appears safe)
cost: 💰 Free
license: Open access with attribution
reliability: ⭐⭐⭐
update_cadence: WEO biannual (April, October); IFS monthly
used_by_agent: Agent 1

key_datasets:
  - World Economic Outlook (WEO)
    # GDP forecasts, inflation forecasts, unemployment, fiscal balance
    # Updated April and October each year
  - International Financial Statistics (IFS)
    # Exchange rates, reserves, monetary aggregates
    # Updated monthly
  - Direction of Trade Statistics (DOTS)
    # Bilateral trade flows
    # Updated quarterly
  - Financial Development Index
    # Financial system depth, access, efficiency
    # Updated annually
  - Balance of Payments
    # Current account, capital flows
    # Updated quarterly

notes: |
  - WEO is essential for GDP growth forecasts
  - IFS complements World Bank with more frequent monetary data
  - DOTS valuable for bilateral trade flow validation
```

### 1.3 UN Data Sources

```yaml
source_id: un_comtrade
name: UN Comtrade
url: https://comtradeapi.un.org/
method: REST API
auth: API key required (free registration)
rate_limit: 100 requests/hour (free tier), 250/hour (premium)
cost: 💰 Free (basic), 💰💰 Premium ($50/month for higher limits)
license: Open access
reliability: ⭐⭐⭐
update_cadence: Monthly/quarterly depending on reporting country
used_by_agent: Agent 1, Agent 4

data_provided:
  - Bilateral trade flows by HS code
  - Import/export values and quantities
  - Top trade products and partners
  - Trade balance calculations

notes: |
  - THE authoritative source for detailed bilateral trade data
  - Free tier sufficient for weekly updates (batch queries)
  - Some countries report with 3-6 month delay
  - Use for: bilateral trade in relations layer,
    top export/import products and partners

---

source_id: undp
name: UNDP Human Development Reports
url: https://hdr.undp.org/data-center/
method: web_fetch + data download
auth: None
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual
used_by_agent: Agent 1

data_provided:
  - Human Development Index (HDI)
  - Gender Inequality Index (GII)
  - Inequality-adjusted HDI (IHDI)
  - Multidimensional Poverty Index
```

---

## 2. Financial Data Sources

### 2.1 Exchange Rates & Market Data

```yaml
source_id: exchangerate_api
name: ExchangeRate-API
url: https://v6.exchangerate-api.com/v6/
method: REST API
auth: API key (free tier available)
rate_limit: 1,500 requests/month (free)
cost: 💰 Free tier sufficient
reliability: ⭐⭐⭐
update_cadence: Daily
used_by_agent: Agent 2

data_provided:
  - Currency exchange rates vs USD (150+ currencies)
  - Historical rates

notes: |
  - Free tier provides 1,500 requests/month
  - At 40 currencies × 4 weeks = 160 requests/month — well within limit
  - Alternative free source: https://open.er-api.com/

---

source_id: trading_economics
name: Trading Economics
url: https://tradingeconomics.com/
method: web_fetch (no free API)
auth: None for web scraping; API is paid ($49/month+)
rate_limit: Be respectful with web_fetch (5-10 pages per session)
cost: 💰 Free (web_fetch), 💰💰💰 Paid (API)
license: Data viewable online; redistribution restricted
reliability: ⭐⭐⭐
update_cadence: Real-time to weekly depending on indicator
used_by_agent: Agent 2

data_provided:
  - Government bond yields (10Y, 2Y, 5Y)
  - Central bank policy rates
  - Sovereign credit ratings (Moody's, S&P, Fitch)
  - Stock market indices
  - Commodity prices
  - Economic indicators with forecasts
  - CDS spreads

strategy: |
  - Use web_search to find Trading Economics pages for specific data points
  - web_fetch to extract the current value
  - Do NOT bulk-scrape; fetch specific country/indicator pages
  - Example: search "trading economics USA 10 year bond yield"
  - Alternative: Yahoo Finance for stock indices and FX

notes: |
  - Best single source for sovereign bond yields and credit ratings
  - Web scraping approach may break if page layout changes
  - Have fallback queries prepared
```

### 2.2 Commodity Prices

```yaml
source_id: commodity_search
name: Commodity Price Search (multiple sources)
method: web_search
cost: 💰 Free
reliability: ⭐⭐ (depends on search results)
used_by_agent: Agent 2

collection_strategy: |
  For each commodity, search:
  "current {commodity} price per {unit} {month} {year}"

  Commodities and units:
  - Brent crude oil ($/barrel)
  - WTI crude oil ($/barrel)
  - Natural gas Henry Hub ($/MMBtu)
  - Natural gas TTF Europe ($/MWh)
  - Gold ($/troy oz)
  - Silver ($/troy oz)
  - Copper ($/metric tonne)
  - Iron ore ($/dry metric tonne)
  - Lithium carbonate ($/metric tonne)
  - Aluminum ($/metric tonne)
  - Nickel ($/metric tonne)
  - Wheat ($/bushel)
  - Corn ($/bushel)
  - Soybeans ($/bushel)
  - Rice ($/cwt)
  - Coffee ($/lb)
  - Uranium ($/lb)

  Cross-reference with at least 2 results for each.
```

---

## 3. Geopolitical Event Sources

### 3.1 GDELT Project

```yaml
source_id: gdelt
name: GDELT Project (Global Database of Events, Language, and Tone)
url: https://api.gdeltproject.org/api/v2/
method: REST API
auth: None
rate_limit: Generous (thousands of queries/day)
cost: 💰 Free
license: Open access
reliability: ⭐⭐⭐
update_cadence: Every 15 minutes
used_by_agent: Agent 3

api_endpoints:
  doc_api: |
    https://api.gdeltproject.org/api/v2/doc/doc
    ?query={search_term}
    &timespan=7d
    &mode=artlist
    &format=json
    &maxrecords=250

  geo_api: |
    https://api.gdeltproject.org/api/v2/geo/geo
    ?query={country}
    &timespan=7d
    &format=GeoJSON

data_provided:
  - Global news events extracted and coded
  - CAMEO event codes (who did what to whom)
  - Goldstein scale (cooperation-conflict score)
  - Geographic coordinates
  - Tone analysis
  - Source articles

query_strategy: |
  1. Query for high-Goldstein events (|Goldstein| > 5) in past 7 days
  2. Query by country for each Tier 1-2 country
  3. Query by theme: MILITARY, SANCTIONS, TRADE, ELECTION, PROTEST
  4. Deduplicate across queries

notes: |
  - GDELT is the single most valuable source for the News agent
  - Pre-processes news so you don't need to read every article
  - Goldstein scale: -10 (military attack) to +10 (major cooperation)
  - CAMEO codes map to our event_type taxonomy
  - Volume: typically 200,000+ events/day globally
  - Agent 3 should filter aggressively for relevance
```

### 3.2 ACLED (Armed Conflict Location & Event Data)

```yaml
source_id: acled
name: ACLED
url: https://acleddata.com/
api_url: https://api.acleddata.com/acled/read/
method: REST API
auth: API key (free registration required)
rate_limit: Reasonable (undocumented, ~500 requests/day)
cost: 💰 Free for research and non-commercial
license: Attribution required, non-commercial use
reliability: ⭐⭐⭐
update_cadence: Weekly
used_by_agent: Agent 3, Agent 5

data_provided:
  - Armed conflict events (battles, explosions, violence against civilians)
  - Protests and riots
  - Strategic developments
  - Actor information (government, rebel groups, militias)
  - Fatality estimates
  - Geographic coordinates

api_example: |
  https://api.acleddata.com/acled/read/
  ?event_date=2026-02-22|2026-03-01
  &event_date_where=BETWEEN
  &country=Nigeria|Ukraine|Myanmar
  &limit=500

notes: |
  - Most authoritative source for conflict and political violence data
  - Essential for Agent 5 (Military & Conflict)
  - Weekly updates align perfectly with our pipeline cadence
  - Covers: Africa, Middle East, South/Southeast Asia, Europe, Americas
  - Each event has precise geographic coding
```

### 3.3 News Wire Services (RSS)

```yaml
source_id: news_rss
name: Major News RSS Feeds
method: web_fetch RSS feeds
cost: 💰 Free
reliability: ⭐⭐ (variable quality, need filtering)
used_by_agent: Agent 3

feeds:
  - name: Reuters World
    url: https://www.reutersagency.com/feed/
    focus: Global
    quality: ⭐⭐⭐

  - name: AP News International
    url: https://apnews.com/
    method: web_fetch homepage + search
    focus: Global
    quality: ⭐⭐⭐

  - name: Al Jazeera
    url: https://www.aljazeera.com/xml/rss/all.xml
    focus: Middle East, developing world
    quality: ⭐⭐⭐

  - name: BBC World
    url: https://feeds.bbci.co.uk/news/world/rss.xml
    focus: Global
    quality: ⭐⭐⭐

  - name: SCMP (South China Morning Post)
    url: https://www.scmp.com/rss
    focus: China, East Asia
    quality: ⭐⭐⭐

  - name: Africa News
    url: https://www.africanews.com/
    method: web_fetch
    focus: Africa
    quality: ⭐⭐

  - name: Nikkei Asia
    url: https://asia.nikkei.com/
    method: web_fetch
    focus: Asia economics
    quality: ⭐⭐⭐

strategy: |
  - Don't read every article. Fetch headlines and summaries only.
  - Use LLM to classify relevance (geopolitical model relevant? yes/no)
  - Only web_fetch full article for events classified as "major"
  - Cross-reference with GDELT to avoid duplication
```

---

## 4. Military & Security Sources

### 4.1 SIPRI

```yaml
source_id: sipri
name: Stockholm International Peace Research Institute
url: https://www.sipri.org/databases
method: web_fetch (databases are downloadable, some via API)
auth: None
cost: 💰 Free
license: Open access with attribution
reliability: ⭐⭐⭐
update_cadence: Annual (military expenditure), continuous (arms transfers)
used_by_agent: Agent 5

databases:
  - name: Military Expenditure Database
    url: https://milex.sipri.org/sipri_milex
    data: Military spending in USD and % GDP for 170+ countries
    update: Annual (April release)

  - name: Arms Transfers Database
    url: https://armstrade.sipri.org/armstrade/
    data: International arms transfers (supplier, recipient, system type)
    update: Annual (March release)

  - name: Arms Industry Database
    data: Top 100 arms-producing companies
    update: Annual (December release)

notes: |
  - THE authoritative source for military spending data
  - Arms transfer data maps directly to our bilateral military relations
  - Annual updates mean this data is only refreshed once per year
  - Between updates, use news-based signals for military spending changes
```

### 4.2 Global Firepower

```yaml
source_id: globalfirepower
name: Global Firepower Index
url: https://www.globalfirepower.com/
method: web_fetch country pages
auth: None
cost: 💰 Free
license: Public information, attribution recommended
reliability: ⭐⭐ (aggregated from multiple sources, methodology not fully transparent)
update_cadence: Annual
used_by_agent: Agent 5

data_provided:
  - Military personnel counts (active, reserve, paramilitary)
  - Equipment inventories (tanks, aircraft, naval vessels)
  - Defense budget
  - Geographic factors (coastline, shared borders)
  - Power index ranking

strategy: |
  web_search "globalfirepower {country}" for each Tier 1-2 country
  Extract: personnel, major equipment categories, budget
  Use as secondary source; cross-validate with SIPRI for spending

notes: |
  - Equipment counts should be treated as estimates (confidence 0.5-0.7)
  - Some data may be outdated for rapidly changing situations
  - Good starting point but not authoritative for fine-grained analysis
```

---

## 5. Political & Governance Sources

### 5.1 Indices and Rankings

```yaml
source_id: eiu_democracy
name: Economist Intelligence Unit — Democracy Index
url: https://www.eiu.com/n/campaigns/democracy-index/
method: web_search + web_fetch (annual report)
cost: 💰 Free (summary data published in report)
reliability: ⭐⭐⭐
update_cadence: Annual (January/February)
used_by_agent: Agent 6

data: Democracy index score (0-10) and category for 167 countries

---

source_id: transparency_intl
name: Transparency International — Corruption Perceptions Index
url: https://www.transparency.org/cpi
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (January)
used_by_agent: Agent 6

data: CPI score (0-100) and rank for 180 countries

---

source_id: freedom_house
name: Freedom House — Freedom in the World
url: https://freedomhouse.org/countries/freedom-world/scores
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (February/March)
used_by_agent: Agent 6

data: Freedom status (Free/Partly Free/Not Free), aggregate score (0-100),
political rights and civil liberties sub-scores for 195 countries

---

source_id: rsf_press
name: Reporters Without Borders — Press Freedom Index
url: https://rsf.org/en/ranking
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (May)
used_by_agent: Agent 6

data: Press freedom score and rank for 180 countries

---

source_id: fragile_states
name: Fund for Peace — Fragile States Index
url: https://fragilestatesindex.org/
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (May)
used_by_agent: Agent 6

data: 12 indicators of state fragility, composite score, rank

---

source_id: wipo_gii
name: WIPO — Global Innovation Index
url: https://www.wipo.int/global_innovation_index/
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (September)
used_by_agent: Agent 1

data: Innovation score and rank for 130+ countries

---

source_id: harvard_atlas
name: Harvard Atlas of Economic Complexity
url: https://atlas.cid.harvard.edu/
api: https://atlas.cid.harvard.edu/api/
method: API + web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual
used_by_agent: Agent 1

data: Economic Complexity Index (ECI), product space, export diversification
```

### 5.2 Election and Leadership Data

```yaml
source_id: electionguide
name: Election Guide (IFES)
url: https://www.electionguide.org/
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Continuous (event-driven)
used_by_agent: Agent 6

data: |
  - Upcoming election dates worldwide
  - Recent election results
  - Election type (presidential, parliamentary, referendum)
  - Incumbents and challengers

notes: |
  Essential for tracking election_approaching alerts
  and leadership_transition_risk assessment
```

---

## 6. Resource and Energy Sources

```yaml
source_id: eia
name: US Energy Information Administration
url: https://www.eia.gov/opendata/
api: https://api.eia.gov/v2/
method: REST API
auth: API key (free registration)
rate_limit: Generous
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Monthly/annual depending on dataset
used_by_agent: Agent 1

data_provided:
  - Oil production/consumption by country
  - Natural gas production/consumption
  - Coal production/consumption
  - Electricity generation by source
  - Renewable energy capacity
  - Energy trade flows

---

source_id: usgs_minerals
name: US Geological Survey — Mineral Commodity Summaries
url: https://www.usgs.gov/centers/national-minerals-information-center
method: web_fetch annual reports
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Annual (January)
used_by_agent: Agent 1

data_provided:
  - Production and reserves for 90+ mineral commodities
  - Country-level breakdown
  - Import sources and dependencies
  - Price trends

notes: |
  Essential for our natural resources layer
  Critical minerals data (lithium, cobalt, rare earths) here

---

source_id: opec
name: OPEC Monthly Oil Market Report
url: https://www.opec.org/opec_web/en/publications/338.htm
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Monthly
used_by_agent: Agent 1

data_provided:
  - Oil production by OPEC+ members
  - Demand forecasts
  - Supply analysis
```

---

## 7. Trade and Sanctions Sources

```yaml
source_id: ofac
name: US OFAC Sanctions List
url: https://sanctionssearch.ofac.treas.gov/
method: web_fetch + search
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Continuous (event-driven, typically weekly updates)
used_by_agent: Agent 4

data_provided:
  - Sanctioned countries (comprehensive sanctions programs)
  - Sanctioned entities and individuals
  - Sectoral sanctions details

---

source_id: eu_sanctions
name: EU Sanctions Map
url: https://www.sanctionsmap.eu/
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Continuous
used_by_agent: Agent 4

data_provided:
  - EU restrictive measures by country
  - Types of sanctions (arms embargo, financial, travel ban)

---

source_id: wto_disputes
name: WTO Dispute Settlement
url: https://www.wto.org/english/tratop_e/dispu_e/dispu_e.htm
method: web_fetch
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Continuous
used_by_agent: Agent 4

data_provided:
  - Active trade disputes between countries
  - Dispute status and rulings
  - Affected products/sectors
```

---

## 8. Cultural and Institutional Sources

```yaml
source_id: hofstede
name: Hofstede Insights — Cultural Dimensions
url: https://www.hofstede-insights.com/country-comparison-tool
method: web_fetch
cost: 💰 Free (basic scores publicly available)
reliability: ⭐⭐ (methodology debated, but widely used)
update_cadence: Rarely changes (static for most purposes)
used_by_agent: Agent 1 (initial load only)

data_provided:
  - 6 cultural dimensions per country
  - Power Distance, Individualism, Masculinity,
    Uncertainty Avoidance, Long-Term Orientation, Indulgence

---

source_id: wvs
name: World Values Survey
url: https://www.worldvaluessurvey.org/
method: web_fetch / data download
cost: 💰 Free
reliability: ⭐⭐⭐
update_cadence: Every 5 years (Wave 7: 2017-2022, Wave 8: upcoming)
used_by_agent: Agent 1 (initial load only)

data_provided:
  - Values and beliefs across 100+ countries
  - Trust, tolerance, political attitudes
  - Traditional vs secular values
  - Survival vs self-expression values
```

---

## 9. Think Tank and Analysis Sources

```yaml
source_id: think_tanks
name: Major Think Tank Publications
method: web_fetch weekly publications pages
cost: 💰 Free (most publications freely available)
reliability: ⭐⭐ to ⭐⭐⭐ (varies by source)
used_by_agent: Agent 3 (News & Events)

sources:
  - name: CSIS (Center for Strategic and International Studies)
    url: https://www.csis.org/
    focus: US foreign policy, Asia, defense

  - name: Brookings Institution
    url: https://www.brookings.edu/
    focus: US policy, global economy

  - name: IISS (International Institute for Strategic Studies)
    url: https://www.iiss.org/
    focus: Military balance, strategic security
    note: Publishes "The Military Balance" — essential reference for Agent 5

  - name: Chatham House (Royal Institute of International Affairs)
    url: https://www.chathamhouse.org/
    focus: Global governance, regions

  - name: Carnegie Endowment for International Peace
    url: https://carnegieendowment.org/
    focus: Democracy, international order

  - name: Council on Foreign Relations
    url: https://www.cfr.org/
    focus: US foreign policy, global conflicts

  - name: RAND Corporation
    url: https://www.rand.org/
    focus: Defense, security, policy analysis

  - name: European Council on Foreign Relations (ECFR)
    url: https://ecfr.eu/
    focus: European foreign policy

strategy: |
  - NOT used for raw data extraction
  - Used for contextual analysis to inform trend estimates
  - Check weekly for major new publications/assessments
  - Particularly valuable during crises for expert analysis
```

---

## 10. Source Priority Matrix

When multiple sources provide the same data point:

| Factor Category | Primary Source | Secondary Source | Tertiary Source |
|---|---|---|---|
| GDP, growth, inflation | World Bank | IMF WEO | Trading Economics |
| Population, demographics | World Bank | UN Population Division | CIA Factbook |
| Trade flows (bilateral) | UN Comtrade | IMF DOTS | Trading Economics |
| Exchange rates | ExchangeRate-API | Trading Economics | Yahoo Finance |
| Bond yields | Trading Economics | Central bank sites | Financial news |
| Credit ratings | Trading Economics | Rating agency sites | News search |
| Military spending | SIPRI | Global Firepower | News search |
| Military equipment | Global Firepower | IISS Military Balance | SIPRI |
| Conflict events | ACLED | GDELT | News search |
| Political events | GDELT + News | Election Guide | Think tanks |
| Governance indices | Freedom House, EIU, TI | World Bank WGI | — |
| Energy data | EIA | OPEC (oil) | World Bank |
| Mineral resources | USGS | National geological surveys | — |
| Economic complexity | Harvard Atlas | — | — |
| Cultural dimensions | Hofstede | World Values Survey | — |
| Sanctions | OFAC (US), EU Sanctions Map | UN SC Resolutions | News |

---

## 11. Cost Summary

| Source | Monthly Cost | Annual Cost |
|---|---|---|
| World Bank API | Free | Free |
| IMF Data | Free | Free |
| UN Comtrade (free tier) | Free | Free |
| UNDP | Free | Free |
| ExchangeRate-API (free) | Free | Free |
| Trading Economics | Free (web) | Free |
| GDELT | Free | Free |
| ACLED | Free | Free |
| SIPRI | Free | Free |
| Global Firepower | Free | Free |
| EIA | Free | Free |
| USGS | Free | Free |
| News RSS | Free | Free |
| All governance indices | Free | Free |
| **TOTAL** | **$0** | **$0** |

All sources used are free or have free tiers sufficient for our weekly update cadence. If higher API limits are needed in the future, UN Comtrade premium ($50/month) would be the first upgrade.

---

## 12. Source Health Monitoring

Agent 15 (Quality Reporter) tracks source health each run:

```json
{
  "source_health": [
    {
      "source_id": "worldbank",
      "last_successful_query": "2026-03-01T12:00:00Z",
      "last_failed_query": null,
      "success_rate_last_4_weeks": 1.0,
      "avg_response_time_ms": 450,
      "status": "healthy"
    },
    {
      "source_id": "trading_economics",
      "last_successful_query": "2026-03-01T12:15:00Z",
      "last_failed_query": "2026-02-22T12:20:00Z",
      "success_rate_last_4_weeks": 0.85,
      "avg_response_time_ms": 2100,
      "status": "degraded",
      "note": "Page layout changed, extraction partially failing"
    }
  ]
}
```

When a source degrades:
1. Flag in quality report
2. Attempt alternative sources
3. If no alternative: mark affected factors as lower confidence
4. Investigate and fix extraction logic before next run

---

## 13. Pre-Fetch System Integration

Several data sources have been automated via deterministic Python scripts in `agents/prefetch/`. These run before the pipeline (or via GitHub Actions cron) and cache structured data in `staging/prefetched/`.

| Source | Pre-fetch Script | API Key Required | Notes |
|---|---|---|---|
| World Bank | `fetch_worldbank.py` | No | 18 indicators; only one indicator per API call; WGI Political Stability = `PV.EST` (not PS.EST); TWN (Taiwan) missing from WB — expected |
| IMF | `fetch_imf.py` | No | Country-filtered URLs return 403 — must fetch all countries and filter locally; `GGX_NGDP` returns no data |
| GDELT | `fetch_gdelt.py` | No | Thematic queries get 429'd without 5s delays between them; Geo API unreliable (404s) |
| FX/Commodities | `fetch_fx_commodities.py` | No | metals.live has TLS SNI issue (`TLSV1_UNRECOGNIZED_NAME`); commodity prices gap-filled by agents |
| ACLED | `fetch_acled.py` | Yes (free) | Set `ACLED_API_KEY` and `ACLED_EMAIL` in `.env` |
| EIA | `fetch_eia.py` | Yes (free) | Set `EIA_API_KEY` in `.env` |
| Comtrade | `fetch_comtrade.py` | Yes (free) | Set `COMTRADE_API_KEY` in `.env` |

**Runner:** `./agents/scripts/run_prefetch.sh [all|--no-key|<source>]`
**CI/CD:** `.github/workflows/prefetch.yml` — runs every Sunday at 06:00 UTC
**Output:** `staging/prefetched/*.json` (committed), `staging/prefetch_cache/` (gitignored fallback)
