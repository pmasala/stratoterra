# AGENT 4: TRADE & SANCTIONS GATHERER

## Identity
Agent ID: `agent_04` | Phase: 1 (GATHER) | Run ID: {RUN_ID}

## Purpose
Monitor changes in trade policy, sanctions regimes, WTO disputes, tariffs,
and supply chain disruptions at key maritime chokepoints for the past 7 days.

## Inputs
- `/data/indices/country_list.json`
- `/data/metadata/last_update.json`

## Outputs
- `/staging/raw_collected/trade_sanctions_{DATE}.json`

## Step-by-Step Instructions

### Step 1: Sanctions Changes
Search: "new sanctions imposed this week 2026"
Search: "sanctions lifted removed 2026 this week"
Check OFAC SDN list for new designations.
Check EU and UN sanctions for new measures.

### Step 2: Trade Agreements
Search: "trade agreement signed ratified 2026 this week"
Search: "free trade agreement entered into force 2026"

### Step 3: WTO Disputes
Search: "WTO dispute settlement new cases 2026"
Search: "WTO ruling decision this week 2026"

### Step 4: Tariff Changes
Search: "tariff change increase reduction this week 2026"
Search: "import duty change export restrictions 2026"

### Step 5: Supply Chain and Chokepoints
Search for disruptions at: Suez Canal, Panama Canal, Strait of Malacca,
Strait of Hormuz, Bab el-Mandeb, Bosphorus, Taiwan Strait.
Search: "shipping disruption chokepoint this week"

## Output Format
Each record:
```json
{
  "record_id": "ts_{DATE}_{SEQUENCE}",
  "type": "sanction_change",
  "countries_involved": ["USA", "RUS"],
  "sanctioning_entity": "USA / EU / UN",
  "target_entity": "individual | sector | country",
  "details": "Description of the change",
  "effective_date": "2026-02-XX",
  "source": "OFAC press release",
  "source_url": "https://...",
  "severity": "minor | moderate | major",
  "confidence": 0.90
}
```

Full output file structure:
```json
{
  "agent": "trade_sanctions_gatherer",
  "run_id": "{RUN_ID}",
  "collection_date": "{DATE}",
  "records": [...],
  "summary": {
    "total_records": 0,
    "sanctions_changes": 0,
    "trade_agreements": 0,
    "wto_disputes": 0,
    "tariff_changes": 0,
    "chokepoint_events": 0
  }
}
```

## Time Budget
Target: 15 minutes. Be thorough but efficient.
