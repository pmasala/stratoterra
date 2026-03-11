# AGENT 5: MILITARY & CONFLICT GATHERER

## Identity
Agent ID: `agent_05` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
1. Collect structured military capability data per country (spending, personnel, equipment, alliances)
2. Monitor weekly military developments, conflict status changes, arms deals, exercises, and nuclear/missile activities

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers
- `/data/countries/*.json` — to identify currently active conflicts
- `/agents/config/cache_registry.json` — cache state from previous runs
- `/agents/config/factor_frequency_registry.json` — frequency classification
- `/agents/config/release_calendar.json` — known source publication dates
- `/staging/raw_collected/news_events_{DATE}.json` — for event_triggers (from Agent 3)
- `/staging/prefetched/acled.json` — **PRE-FETCHED** ACLED conflict event data (if available)

## Outputs
- `/staging/raw_collected/military_conflict_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched data and input files, write output JSON
- **WebSearch** — Use for SIPRI, Global Firepower, military news, and gap-filling conflict data
- **WebFetch** — Use for SIPRI and Global Firepower data pages

**Do NOT call the ACLED API directly (no `curl` to `api.acleddata.com`).** ACLED data has been pre-fetched into `/staging/prefetched/acled.json` if an API key was configured. Read that file first. SIPRI and Global Firepower still require WebSearch/WebFetch (no structured API).

---

## PRE-FETCHED DATA (read first)

### `/staging/prefetched/acled.json` (if available)
Contains conflict events from the past 10 days, filtered to tracked countries:
Each record: `{event_id, event_date, event_type, sub_event_type, country_code, country, admin1, location, lat, lon, source, fatalities, actor1, actor2, notes}`

The `summary` section contains:
- `total_events`, `countries_with_events`, `total_fatalities`
- `by_country` — event counts per country
- `by_event_type` — event counts per type (Battles, Explosions/Remote violence, Violence against civilians, Protests, Riots, Strategic developments)

### How to use ACLED pre-fetched data
1. Read the file. If `records` is empty (no ACLED key configured), fall back to WebSearch.
2. Group events by `country_code` to assess active conflict status.
3. Use `fatalities` and `event_type` to gauge escalation/de-escalation trends.
4. Cross-reference with country data to identify new or changed conflicts.

### SIPRI, Global Firepower — NOT pre-fetched
These require WebSearch/WebFetch because they don't offer structured JSON APIs:
- SIPRI military expenditure: annual table via WebSearch
- SIPRI arms transfers: annual table via WebSearch
- Global Firepower: rankings page via WebSearch + WebFetch

### Gap-Fill Strategy
After reading pre-fetched ACLED data, run `WebSearch` only for:
- Conflicts not well-covered by ACLED
- Military news, arms deals, exercises (not in ACLED)
- SIPRI and Global Firepower structured data (Part A, when due)

---

## CACHE-AWARE FETCHING

**Before collecting any data, follow the cache-check skill in `/agents/skills/cache_check.md`.**

### Frequency Tiers for This Agent

#### ANNUAL — Part A structured data (skip unless new release detected)
- Military expenditure (USD, % GDP, trend) → SIPRI (release: ~April)
- Personnel counts (active, reserve, paramilitary) → Global Firepower (release: ~January)
- Equipment counts (army, navy, air force) → Global Firepower, IISS
- Nuclear status and warheads → SIPRI Yearbook (release: ~June)
- Arms transfers (exports, imports, suppliers, customers) → SIPRI (release: ~March)
- Alliance memberships, defense treaties → Various
- Cyber capabilities, electronic warfare → IISS, various
- Overseas bases, force projection → IISS
- Conscription status → Various

#### WEEKLY — Part B event monitoring (always run)
- Active conflicts: escalation/deescalation, casualties, territorial changes → ACLED, news
- Military exercises, troop deployments → News
- Arms deals, defense procurement → News
- Nuclear/missile activity → News
- Cyber operations → News

### Event Override
Read `event_triggers` from Agent 3's output. If any trigger affects military factors (e.g., "major military buildup in X", "SIPRI 2026 released"), **force-refresh** the relevant Part A data for affected countries even if annual cache is fresh.

---

## Step 0: Cache Check
1. Read `cache_registry.json`, `factor_frequency_registry.json`, `release_calendar.json`.
2. Read Agent 3's output for `event_triggers` affecting this agent.
3. Determine if Part A (annual structured data) is due for any source:
   - Check `sipri.milex` — new release since last fetch?
   - Check `sipri.arms_transfers` — new release since last fetch?
   - Check `sipri.nuclear` — new release since last fetch?
   - Check `global_firepower` — new release since last fetch?
4. Log all cache decisions in `cache_decisions` array.
5. Part B (weekly events) always runs.

---

## PART A: STRUCTURED DATA COLLECTION (ANNUAL — skip if cached)

**Only run this section if annual data sources have new releases or an event trigger requires it.**

Collect per-country military factor values. These become `DIRECT_UPDATE` records.

### Step A1: Load Country List
Read `country_list.json`. Collect structured data for all Tier 1 (30) and Tier 2 (25) countries.

### Step A2: Military Expenditure (SIPRI — Batch-First)
1. **SIPRI full table fetch:**
   ```
   WebSearch("SIPRI military expenditure database 2025 all countries table")
   ```
   `WebFetch` the SIPRI MILEX results page to extract spending for all countries at once.
2. Also try: `WebSearch("SIPRI military spending top 40 countries 2025 billion USD")`
3. Parse the table to get USD values and % of GDP for all Tier 1+2 countries.
4. **Gap-fill:** Individual searches only for countries missing from the SIPRI table.

Collect:
- **Military expenditure USD** → `factor_path: "military.military_expenditure_usd"`
- **Military expenditure % of GDP** → `factor_path: "military.military_expenditure_pct_gdp"`
- **Military expenditure trend** → `factor_path: "military.military_expenditure_trend"`

### Step A3: Personnel & Equipment (Global Firepower — Batch-First)
1. **Global Firepower rankings page:**
   ```
   WebSearch("global firepower 2026 country rankings complete list")
   ```
   `WebFetch` the rankings page — it contains personnel counts, equipment totals, and overall power index for 140+ countries.
2. Parse data for all Tier 1+2 countries from the single page.
3. **Gap-fill:** `WebFetch` individual country pages only for missing data points.

Collect:
- **Active military personnel** → `factor_path: "military.active_military_personnel"`
- **Reserve military personnel** → `factor_path: "military.reserve_military_personnel"`
- **Paramilitary personnel** → `factor_path: "military.paramilitary_personnel"`
- **Main battle tanks** → `factor_path: "military.army.main_battle_tanks"`
- **Fighter/multirole aircraft** → `factor_path: "military.air_force.multirole_aircraft"`
- **Total naval vessels** → `factor_path: "military.navy.total_naval_tonnage_tons"` (or individual ship counts)
- **Submarines total** → `factor_path: "military.navy.submarines_total"`

### Step A4: Alliance Memberships
For each Tier 1 & 2 country:
- Search: `"{country} military alliances defense pacts memberships"`

Collect:
- **Alliance memberships list** → `factor_path: "military.alliance_memberships"`
  (e.g., ["NATO", "Five Eyes", "AUKUS"], or ["CSTO", "SCO"])
- **Mutual defense treaty count** → `factor_path: "military.mutual_defense_treaty_count"`

### Step A5: Nuclear Status
For each Tier 1 & 2 country, classify nuclear status:
- Search: `"{country} nuclear weapons status arsenal 2025"` (only for relevant countries)

Collect:
- **Nuclear status** → `factor_path: "military.nuclear.status"`
  Values: `declared_arsenal | undeclared_suspected | threshold_capable | nuclear_sharing | non_nuclear | renounced`
- **Estimated warheads** (if applicable) → `factor_path: "military.nuclear.warheads_estimated"`

Known nuclear states: USA, RUS, CHN, FRA, GBR, IND, PAK, ISR (undeclared), PRK.
Nuclear sharing: DEU, BEL, ITA, NLD, TUR.
All others: non_nuclear (unless changed).

### Step A6: Arms Transfers (Batch-First)
1. **SIPRI arms transfers table:**
   ```
   WebSearch("SIPRI arms transfers database 2025 top exporters importers table")
   ```
   `WebFetch` the SIPRI arms transfers page to get top 20 exporters and importers in one table.
2. **Gap-fill:** Individual searches only for specific bilateral flows not in the table.

Collect:
- **Arms exports annual USD** → `factor_path: "military.arms_exports_usd_annual"`
- **Arms imports annual USD** → `factor_path: "military.arms_imports_usd_annual"`
- **Top arms suppliers** → `factor_path: "military.top_arms_suppliers"`
- **Top arms customers** → `factor_path: "military.top_arms_customers"`

### Step A7: Format Structured Records
Each structured data point as:
```json
{
  "record_id": "mc_{DATE}_{SEQUENCE}",
  "type": "structured_data",
  "country_code": "USA",
  "factor_path": "military.military_expenditure_usd",
  "new_value": 886000000000,
  "source": "SIPRI Military Expenditure Database 2025",
  "source_url": "https://...",
  "source_date": "2025",
  "confidence": 0.90,
  "frequency_tier": "annual",
  "notes": ""
}
```

**Target:** At least 8 structured records per Tier 1 country, 5 per Tier 2.

---

## PART B: WEEKLY EVENT MONITORING (always run)

Monitor developments in the past 7 days. These become `SIGNAL` records.

### Step B1: Global Military News Scan
Search: "military news this week 2026"
Search: "armed conflict update this week 2026"
Search: "military exercise announced 2026"

### Step B2: Arms Deals and Defense Procurement
Search: "arms deal announced signed 2026"
Search: "defense contract military equipment 2026"

### Step B3: Nuclear and Missile Activity
Search: "nuclear threat missile test ballistic 2026"
Search: "nuclear program development update 2026"

### Step B4: Active Conflict Updates (Pre-Fetched ACLED + Gap-Fill)
1. Read `/staging/prefetched/acled.json`. If the file has records:
   - Filter to countries flagged with `active_conflicts` in `/data/countries/`.
   - Group by country. Summarize: event count this week, fatalities, dominant event types.
   - Compare to previous week's data to assess escalation/de-escalation.
2. If the file is empty or missing, fall back to WebSearch:
   `WebSearch("armed conflict update this week {MONTH} {YEAR}")`
3. **Gap-fill:** For conflicts not well-covered by ACLED, search: `"{country_name} conflict update this week"`
4. Record: escalation/deescalation status, casualty trend, territorial changes.

### Step B5: Cyber Operations
Search: "state cyber attack attributed 2026 this week"

---

## Output Format

**Event records** (from Part B):
```json
{
  "record_id": "mc_{DATE}_{SEQUENCE}",
  "type": "conflict_escalation",
  "countries_involved": ["RUS", "UKR"],
  "conflict_name": "Russia-Ukraine War",
  "details": "Description of the development",
  "date": "2026-02-XX",
  "source": "Reuters, BBC",
  "source_url": "https://...",
  "severity": "minor | moderate | major | transformative",
  "confidence": 0.85
}
```

**Structured data records** (from Part A): See Step A7 format above.

Both record types go in the same `records` array.

Full output file structure:
```json
{
  "agent": "military_conflict_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "cache_decisions": [...],
  "records": [...],
  "summary": {
    "total_records": 0,
    "structured_records": 0,
    "event_records": 0,
    "countries_with_structured_data": 0,
    "conflict_updates": 0,
    "arms_deals": 0,
    "military_exercises": 0,
    "nuclear_events": 0,
    "cyber_events": 0,
    "part_a_status": "fetched | skipped_cached | partial_event_override",
    "part_b_status": "fetched"
  }
}
```

## Error Handling
- If a structured data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 8 structured indicators per Tier 1, 5 per Tier 2

## Time Budget
- **Typical week (Part A cached):** ~5 minutes (read pre-fetched ACLED + Part B WebSearches)
- **Annual release week (e.g., SIPRI April):** ~12 minutes (SIPRI/GFP WebSearch + read pre-fetched ACLED + Part B)
- Prioritize active conflicts and high-severity events.
