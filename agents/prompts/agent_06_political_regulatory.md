# AGENT 6: POLITICAL & REGULATORY GATHERER

## Identity
Agent ID: `agent_06` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
1. Collect structured governance and political data per country (democracy indices, governance scores, leadership, elections)
2. Monitor weekly elections, government changes, political instability, and investment-relevant regulatory developments

## Inputs
- `/data/indices/country_list.json` — list of country codes and tiers

## Outputs
- `/staging/raw_collected/political_regulatory_{DATE}.json`

## Tools

- **WebSearch** — Use for discovering current governance data and political news
- **WebFetch** — Use for institutional pages (Freedom House, Transparency International, EIU, RSF, Election Guide)
- **Bash** with `curl` — Use for World Bank WGI API:
  `curl "https://api.worldbank.org/v2/country/{ISO2}/indicator/{WGI_ID}?format=json&date=2023:2025"`
- **Read** / **Write** — Read input files, write output JSON

No API keys are required.

---

## PART A: STRUCTURED DATA COLLECTION

Collect per-country governance and political factor values. These become `DIRECT_UPDATE` records.

### Step A1: Load Country List
Read `country_list.json`. Collect structured data for all Tier 1 (30) and Tier 2 (25) countries.

### Step A2: Democracy Index (EIU)
For each Tier 1 & 2 country:
- Search: `"EIU Democracy Index {country} 2025 score"` or `"Economist Intelligence Unit democracy index {country}"`

Collect:
- **Democracy Index score (0-10)** → `factor_path: "institutions.democracy_index"`
- **Regime type** → `factor_path: "institutions.regime_type"`
  Derive from score: ≥8.0 = `full_democracy`, 6.0-7.9 = `flawed_democracy`, 4.0-5.9 = `hybrid_regime`, <4.0 = `authoritarian`

### Step A3: Freedom House Scores
For each Tier 1 & 2 country:
- Search: `"Freedom House {country} 2025 freedom score"` or `"Freedom in the World {country} 2025"`
- Alternative: WebFetch `https://freedomhouse.org/countries/freedom-world/scores`

Collect:
- **Freedom House status** → `factor_path: "institutions.freedom_house_status"`
  Values: `free | partly_free | not_free`
- **Freedom House aggregate score (0-100)** → `factor_path: "institutions.freedom_house_score"`

### Step A4: Corruption Perceptions Index (Transparency International)
For each Tier 1 & 2 country:
- Search: `"Transparency International CPI {country} 2025 score"` or `"corruption perceptions index {country} 2025"`

Collect:
- **CPI score (0-100)** → `factor_path: "institutions.corruption_perception_index"`

### Step A5: Press Freedom (RSF)
For each Tier 1 & 2 country:
- Search: `"RSF press freedom index {country} 2025 rank"` or `"Reporters Without Borders {country} ranking"`

Collect:
- **Press Freedom Index rank** → `factor_path: "institutions.press_freedom_index_rank"`

### Step A6: World Bank Governance Indicators (WGI)
For each Tier 1 & 2 country, use WebSearch or the World Bank API:
- Search: `"World Bank governance indicators {country} 2024"` or `"WGI {country} political stability rule of law"`
- API: `curl "https://api.worldbank.org/v2/country/{ISO2}/indicator/PV.EST?format=json&date=2022:2025"`

WGI indicator IDs:
- `VA.EST` → Voice and Accountability
- `PS.EST` → Political Stability (also called `PV.EST`)
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

### Step A7: Current Leadership & Elections
For each Tier 1 & 2 country:
- Search: `"{country} current head of state president prime minister 2026"`
- Search: `"{country} next national election date"`

Collect:
- **Head of state name** → `factor_path: "institutions.head_of_state_name"`
- **Head of state title** → `factor_path: "institutions.head_of_state_title"`
- **Head of government name** (if different) → `factor_path: "institutions.head_of_government_name"`
- **Next national election date** → `factor_path: "institutions.next_national_election_date"`

### Step A8: Fragile States Index (Fund for Peace)
For Tier 2 & 3 countries (and any Tier 1 with FSI relevance):
- Search: `"Fragile States Index {country} 2025 score"` or `"Fund for Peace fragile states {country}"`

Collect:
- **FSI score** → `factor_path: "institutions.fragile_states_index"`

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
  "notes": "Score category: flawed democracy"
}
```

**Target:** At least 10 structured records per Tier 1 country, 6 per Tier 2.

---

## PART B: WEEKLY EVENT MONITORING

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
    "high_investor_relevance_count": 0
  }
}
```

## Error Handling
- If a structured data point is not found after one search: skip it, log in `skipped`
- If rate-limited: wait 30 seconds and retry once
- Target: at least 10 structured indicators per Tier 1, 6 per Tier 2

## Time Budget
Target: 25 minutes total. Part A: ~13 min. Part B: ~12 min. Prioritize high investor_relevance items.
