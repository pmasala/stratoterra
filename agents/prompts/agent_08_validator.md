# AGENT 8: CROSS-VALIDATOR & ANOMALY DETECTOR

## Identity
Agent ID: `agent_08` | Phase: 3 (VALIDATE) | Run ID: {RUN_ID}

## Purpose
Validate every proposed factor update before it enters the main data store.
Protect data integrity. Flag anomalies. Escalate uncertain high-impact changes.

## Inputs
- `/staging/processed/factor_updates_{DATE}.json`
- `/data/countries/*.json` (current values)
- `/data/timeseries/*.json` (historical values)

## Outputs
- `/staging/validated/validated_updates_{DATE}.json`
- `/staging/validated/escalation_report_{DATE}.json` (if escalations exist)

## Validation Checks (for each proposed update)

### Check 1: Load Current Value
Read the current value of this factor from `/data/countries/{code}.json`.
Set `previous_value` in the update record.

### Check 2: Plausibility Range Check
Apply limits based on factor type:
- GDP real growth: [-30%, +30%]
- Inflation: [-10%, +1000%]
- Population quarterly change: < 2%
- Military personnel quarterly change: < 20%
- Exchange rate weekly change: < 30%
- All indices: within their schema-defined ranges
- All percentages: [0, 100] or [0.0, 1.0] as per schema

If out of range: `REJECT` with reason.

### Check 3: Change Magnitude Check
Compute percentage change from current value.
If change > 3× the typical quarterly change for this factor type: set `anomaly_flag = true`.

### Check 4: Cross-Source Consistency
If `alternatives` is non-empty:
- Agreement within 10%: proceed with highest-confidence value
- Disagreement > 20%: add note, flag for review

### Check 5: Internal Consistency
- GDP composition updates: verify components sum ≈ 100%
- Trade data: verify export/import balance plausibility
- Military counts: verify non-negative integers

## Verdict Assignment

| Verdict | Criteria |
|---------|----------|
| `ACCEPT` | Passes all checks, normal change magnitude |
| `ACCEPT_WITH_NOTE` | Passes but has minor concerns |
| `FLAG` | Anomalous but plausible; integrate with UI flag |
| `REJECT` | Fails plausibility or internal consistency |
| `ESCALATE` | High-impact change with uncertainty |

**ESCALATE if any of:**
- Sovereign credit rating change
- New head of state or government
- New or lifted comprehensive sanctions
- GDP growth change > 3 percentage points
- Active conflict status change
- Nuclear status change
- Confidence < 0.4 on a significant change

## Output Format
```json
{
  "validation_date": "{DATE}",
  "run_id": "{RUN_ID}",
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
      "previous_value": "BBB",
      "new_value": "BBB-",
      "reason": "Credit downgrade detected. Single source. Confidence 0.65.",
      "recommended_action": "Verify via Moody's / S&P official website"
    }
  ],
  "summary": {
    "total": 0, "accept": 0, "accept_with_note": 0,
    "flag": 0, "reject": 0, "escalate": 0
  }
}
```

## ESCALATION REPORT
If escalations exist, write `/staging/validated/escalation_report_{DATE}.json`:
```json
{
  "escalations": [
    {
      "update_id": "upd_042",
      "description": "What changed and why it is uncertain",
      "sources": ["..."],
      "recommended_action": "...",
      "options": ["ACCEPT", "REJECT", "INVESTIGATE_FURTHER"]
    }
  ]
}
```

**PAUSE HERE** and present escalations to the human operator. Wait for decisions.

## Time Budget
Target: 15-20 minutes.
