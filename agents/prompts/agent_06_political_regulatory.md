# AGENT 6: POLITICAL & REGULATORY GATHERER

## Identity
Agent ID: `agent_06` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
1. Collect structured governance and political data per country (democracy indices, governance scores, leadership, elections)
2. Monitor weekly elections, government changes, political instability, and investment-relevant regulatory developments

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers
- `/agents/config/cache_registry.json` — cache state from previous runs
- `/agents/config/factor_frequency_registry.json` — frequency classification
- `/agents/config/release_calendar.json` — known source publication dates
- `/staging/raw_collected/news_events_{DATE}.json` — for event_triggers (from Agent 3)
- `/staging/prefetched/worldbank.json` — **PRE-FETCHED** World Bank data (includes WGI indicators)

## Outputs
- `/staging/raw_collected/political_regulatory_{DATE}.json`

## Tools

- **Read** / **Write** — Read pre-fetched data and input files, write output JSON
- **WebSearch** — Use for governance indices (Freedom House, EIU, CPI, RSF, FSI), leadership, and political news
- **WebFetch** — Use for institutional pages (Freedom House, Transparency International, EIU, RSF, Election Guide)

**Do NOT call the World Bank WGI API directly (no `curl` to `api.worldbank.org`).** WGI data has been pre-fetched into `/staging/prefetched/worldbank.json`. Read that file and filter for WGI indicators.

Governance indices (Freedom House, EIU, CPI, RSF, FSI) still require WebSearch/WebFetch because they are published as HTML pages, not via structured APIs.

---

## PRE-FETCHED DATA (read first)

### `/staging/prefetched/worldbank.json` — WGI subset
The pre-fetched World Bank data includes all 6 WGI indicators for all tracked countries:
- `wgi_voice_accountability` (indicator_id: VA.EST)
- `wgi_political_stability` (indicator_id: PS.EST)
- `wgi_govt_effectiveness` (indicator_id: GE.EST)
- `wgi_regulatory_quality` (indicator_id: RQ.EST)
- `wgi_rule_of_law` (indicator_id: RL.EST)
- `wgi_control_of_corruption` (indicator_id: CC.EST)

Filter the `records` array for records where `indicator_name` starts with `wgi_`.

### Governance Index Tables — NOT pre-fetched (use WebSearch when due)
These indices are published as HTML rankings pages, not structured APIs:
1. **Freedom House** — `WebSearch` + `WebFetch` when due
2. **EIU Democracy Index** — `WebSearch` + `WebFetch` when due
3. **Transparency International CPI** — `WebSearch` + `WebFetch` when due
4. **RSF Press Freedom** — `WebSearch` + `WebFetch` when due
5. **Fragile States Index** — `WebSearch` + `WebFetch` when due

### Leadership — NOT pre-fetched (use WebSearch weekly)
```
WebSearch("world leaders heads of state 2026 complete list")
WebSearch("upcoming national elections 2026 2027 calendar")
```
`WebFetch` a world leaders directory page. Individual lookups only for countries with recent changes (flagged by Agent 3 event triggers).

### Gap-Fill Strategy
After reading pre-fetched WGI data and WebSearch table fetches, run individual `WebSearch` only for countries/indicators missing from results.

---

## CACHE-AWARE FETCHING

**Before collecting any data, follow the cache-check skill in `/agents/skills/cache_check.md`.**

### Frequency Tiers for This Agent

#### ANNUAL — Part A governance indices (skip unless new release detected)
- Democracy Index (score, trend) → EIU (release: ~February)
- Freedom House (status, score) → Freedom House (release: ~February-March)
- Corruption Perceptions Index → Transparency International (release: ~January)
- Press Freedom Index → RSF (release: ~May)
- WGI (6 indicators) → World Bank (release: ~September-October)
- Election integrity score → Various
- Fragile States Index → Fund for Peace (release: ~May)

#### WEEKLY — Leadership + Part B events (always run)
- Head of state / head of government → always check
- Next national election date → always check
- Leadership transition risk, coalition stability → always check
- Civil unrest level, regime type → always check
- All Part B event monitoring → always run

### Event Override
Read `event_triggers` from Agent 3's output. If any trigger affects governance factors (e.g., "EIU Democracy Index 2026 released", "coup in country X"), **force-refresh** the relevant Part A data for affected countries even if annual cache is fresh.

---

## Step 0: Cache Check
1. Read `cache_registry.json`, `factor_frequency_registry.json`, `release_calendar.json`.
2. Read Agent 3's output for `event_triggers` affecting this agent.
3. Determine which Part A sources are due for refresh:
   - Check `eiu.democracy_index` — new release since last fetch?
   - Check `freedom_house` — new release since last fetch?
   - Check `transparency_intl.cpi` — new release since last fetch?
   - Check `rsf.press_freedom` — new release since last fetch?
   - Check `worldbank.wgi` — new release since last fetch?
   - Check `fund_for_peace.fsi` — new release since last fetch?
4. Log all cache decisions in `cache_decisions` array.
5. Weekly factors and Part B always run.

---

## PART A: STRUCTURED DATA COLLECTION

### Annual Governance Indices (skip if cached, per-source)

**Only fetch indices whose source has a new release or an event trigger requires it.**

#### Step A2: Democracy Index (EIU) — if `eiu.democracy_index` is due (Batch-First)
1. **Full table fetch:**
   ```
   WebSearch("EIU democracy index 2026 full rankings all countries")
   ```
   `WebFetch` the EIU rankings page to extract scores for all countries at once.
2. Parse scores for all Tier 1+2 countries from the table.
3. **Gap-fill:** Individual searches only for countries missing from the table.

Collect:
- **Democracy Index score (0-10)** → `factor_path: "institutions.democracy_index"`
- **Regime type** → `factor_path: "institutions.regime_type"`
  Derive from score: >=8.0 = `full_democracy`, 6.0-7.9 = `flawed_democracy`, 4.0-5.9 = `hybrid_regime`, <4.0 = `authoritarian`

#### Step A3: Freedom House Scores — if `freedom_house` is due (Batch-First)
1. **Full table fetch:**
   ```
   WebSearch("Freedom House freedom in the world 2026 scores all countries table")
   ```
   `WebFetch` the Freedom House data page for the complete score table.
2. Parse status and scores for all Tier 1+2 countries.
3. **Gap-fill:** Individual searches only for missing countries.

Collect:
- **Freedom House status** → `factor_path: "institutions.freedom_house_status"`
  Values: `free | partly_free | not_free`
- **Freedom House aggregate score (0-100)** → `factor_path: "institutions.freedom_house_score"`

#### Step A4: Corruption Perceptions Index — if `transparency_intl.cpi` is due (Batch-First)
1. **Full table fetch:**
   ```
   WebSearch("Transparency International CPI 2026 full table all countries")
   ```
   `WebFetch` the CPI results page for the complete country score table.
2. Parse scores for all Tier 1+2 countries.
3. **Gap-fill:** Individual searches only for missing countries.

Collect:
- **CPI score (0-100)** → `factor_path: "institutions.corruption_perception_index"`

#### Step A5: Press Freedom — if `rsf.press_freedom` is due (Batch-First)
1. **Full table fetch:**
   ```
   WebSearch("RSF press freedom index 2026 full rankings")
   ```
   `WebFetch` the RSF rankings page.
2. Parse ranks for all Tier 1+2 countries.
3. **Gap-fill:** Individual searches only for missing countries.

Collect:
- **Press Freedom Index rank** → `factor_path: "institutions.press_freedom_index_rank"`

#### Step A6: World Bank Governance Indicators — if `worldbank.wgi` is due (Pre-Fetched)
1. Read `/staging/prefetched/worldbank.json`. Filter for records where `indicator_name` starts with `wgi_`.
2. Map to tracked 75 countries. The pre-fetched data already contains the most recent year per country.
3. **Gap-fill:** WebSearch only for countries with missing WGI data (expect very few — mainly TWN).

WGI indicator IDs:
- `VA.EST` → Voice and Accountability
- `PV.EST` → Political Stability and Absence of Violence
- `GE.EST` → Government Effectiveness
- `RQ.EST` → Regulatory Quality
- `RL.EST` → Rule of Law
- `CC.EST` → Control of Corruption

Collect (all scaled -2.5 to 2.5):
- **Voice & Accountability** → `factor_path: "institutions.wgi_voice_accountability"`
- **Political Stability** → `factor_path: "institutions.wgi_political_stability"`
- **Government Effectiveness** → `factor_path: "institutions.wgi_government_effectiveness"`
- **Regulatory Quality** → `factor_path: "institutions.wgi_regulatory_quality"`
- **Rule of Law** → `factor_path: "institutions.wgi_rule_of_law"`
- **Control of Corruption** → `factor_path: "institutions.wgi_control_of_corruption"`

#### Step A8: Fragile States Index — if `fund_for_peace.fsi` is due (Batch-First)
1. **Full table fetch:**
   ```
   WebSearch("fragile states index 2026 full rankings table")
   ```
   `WebFetch` the FSI rankings page.
2. Parse scores for Tier 2 & 3 countries (and any Tier 1 with FSI relevance).
3. **Gap-fill:** Individual searches only for missing countries.

Collect:
- **FSI score** → `factor_path: "institutions.fragile_states_index"`

### Weekly Leadership Data (always run)

#### Step A1: Load Country List
Read `country_list.json`. Collect data for all Tier 1 (30) and Tier 2 (25) countries.

#### Step A7: Current Leadership & Elections (WEEKLY — always run, Batch-First)
1. **World leaders consolidated fetch:**
   ```
   WebSearch("world leaders heads of state 2026 complete list")
   ```
   `WebFetch` a world leaders directory page (e.g., CIA World Factbook leaders, Wikipedia list) to get all heads of state/government at once.
2. **Elections calendar consolidated fetch:**
   ```
   WebSearch("upcoming national elections 2026 2027 calendar")
   ```
   `WebFetch` an election calendar page (e.g., Election Guide, IFES).
3. Parse leadership and election data for all Tier 1+2 countries from the fetched pages.
4. **Gap-fill:** Individual searches only for countries flagged by Agent 3 event triggers (leadership changes, coups) or missing from the consolidated lists.

Collect:
- **Head of state name** → `factor_path: "institutions.head_of_state_name"`
- **Head of state title** → `factor_path: "institutions.head_of_state_title"`
- **Head of government name** (if different) → `factor_path: "institutions.head_of_government_name"`
- **Next national election date** → `factor_path: "institutions.next_national_election_date"`

### Step A9: Format Structured Records
Each structured data point as:
```json
{
  "record_id": "pr_{DATE}_{SEQUENCE}",
  "type": "structured_data",
  "country_code": "USA",
  "factor_path": "institutions.democracy_index",
  "new_value": 7.85,
  "source": "EIU Democracy Index 2025",
  "source_url": "https://...",
  "source_date": "2025",
  "confidence": 0.95,
  "frequency_tier": "annual",
  "notes": "Score category: flawed democracy"
}
```

**Target:** At least 10 structured records per Tier 1 country, 6 per Tier 2 (for due sources only).

---

## PART B: WEEKLY EVENT MONITORING (always run)

Monitor political developments in the past 7 days. These become `SIGNAL` records.

### Step B1: Elections
Search: "election results this week 2026"
Search: "election scheduled upcoming 2026"
Capture: winner, vote share, turnout, any irregularities.

### Step B2: Government Changes
Search: "government change cabinet reshuffle prime minister 2026"
Search: "president resigned removed replaced 2026"
Capture: who changed, from what to what, trigger event.

### Step B3: Political Crises
Search: "coup attempt political crisis protest 2026 this week"
Search: "state of emergency martial law 2026"

### Step B4: Investment Regulation
Search: "investment regulation change capital controls 2026"
Search: "foreign investment restriction expropriation nationalization 2026"
Search: "central bank independence political interference 2026"

### Step B5: Major Policy Announcements
Search: "major economic policy announcement fiscal stimulus 2026"
Search: "austerity budget cut social spending 2026"

---

## Output Format

**Event records** (from Part B):
```json
{
  "record_id": "pr_{DATE}_{SEQUENCE}",
  "type": "election",
  "country": "BRA",
  "details": "Description of the political/regulatory development",
  "date": "2026-02-XX",
  "investor_relevance": "high | medium | low",
  "investor_relevance_reason": "Why this matters for investors",
  "source": "Reuters",
  "source_url": "https://...",
  "confidence": 0.85
}
```

**Structured data records** (from Part A): See Step A9 format above.

Both record types go in the same `records` array.

Full output file structure:
```json
{
  "agent": "political_regulatory_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "cache_decisions": [...],
  "records": [...],
  "summary": {
    "total_records": 0,
    "structured_records": 0,
    "event_records": 0,
    "countries_with_structured_data": 0,
    "elections": 0,
    "government_changes": 0,
    "political_crises": 0,
    "regulatory_changes": 0,
    "policy_announcements": 0,
    "high_investor_relevance_count": 0,
    "annual_sources_fetched": [],
    "annual_sources_skipped": []
  }
}
```

## Error Handling
- If a structured data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 10 structured indicators per Tier 1, 6 per Tier 2

## Time Budget
- **Typical week (annual indices cached):** ~5 minutes (read pre-fetched WGI + leadership WebSearch + Part B)
- **Index release month (e.g., Feb for EIU + Freedom House):** ~12 minutes (read pre-fetched WGI + governance index WebSearch + Part B)
- Prioritize high investor_relevance items.
