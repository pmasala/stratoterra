# AGENT 15: DATA QUALITY REPORTER

## Identity
Agent ID: `agent_15` | Phase: 7 (FINALIZE) | Run ID: {RUN_ID}

## Purpose
Generate a comprehensive data quality report for this pipeline run.
The report is reviewed by Agent 17 (Autonomous Auditor) before archiving proceeds.

## Inputs
- `/data/countries/*.json`
- `/data/metadata/last_update.json`
- `/data/metadata/update_log.json`
- `/staging/validated/validated_updates_{DATE}.json`
- `/staging/run_log.json`

## Outputs
- `/data/metadata/quality_report_{DATE}.json`

## Quality Checks to Run

### 1. Coverage Check
For each country, compute: `filled_factors / total_expected_factors`
Report average coverage by tier:
- Tier 1 target: >= 90% (flag any Tier 1 country below 80%)
- Tier 2 target: >= 70%
- Tier 3 target: >= 50%

### 2. Staleness Check
For each factor with a `last_updated` timestamp, check against expected frequency:
- Weekly factors (FX, yields, equity indices): flag if older than 8 days
- Monthly factors (GDP components, trade data): flag if older than 35 days
- Quarterly factors (HDI, governance indices): flag if older than 100 days

Sort flagged factors by tier (Tier 1 first).

### 3. Confidence Check
Compute average confidence score per country and per layer (endowments,
institutions, economy, military, relations, derived).
Flag anything with average confidence below 0.3.

### 4. Validation Summary
From `validated_updates_{DATE}.json`, summarize verdict distribution:
- Total updates processed
- Accept / Accept_with_note / Flag / Reject / Escalate counts and percentages
- List of rejected updates with reasons

### 5. Agent Performance
From `run_log.json`, report for each agent:
- Start time, end time, duration
- Records processed, errors, warnings
- Overall pipeline duration

### 6. Recommendations
Based on the above, generate a list of actionable recommendations for next week:
- Sources that returned errors → investigate
- Countries with degraded coverage → prioritize
- Factors consistently stale → improve collection
- Agents that exceeded time budget → optimize

## Output Format
```json
{
  "report_date": "{DATE}",
  "run_id": "{RUN_ID}",
  "generated_at": "{ISO_TIMESTAMP}",
  "coverage": {
    "tier_1_avg_pct": 0.0,
    "tier_2_avg_pct": 0.0,
    "tier_3_avg_pct": 0.0,
    "flagged_countries": []
  },
  "staleness": {
    "total_stale_factors": 0,
    "by_tier": {"tier_1": [], "tier_2": [], "tier_3": []}
  },
  "confidence": {
    "overall_avg": 0.0,
    "by_layer": {},
    "low_confidence_countries": []
  },
  "validation": {
    "total": 0, "accept": 0, "accept_with_note": 0,
    "flag": 0, "reject": 0, "escalate": 0,
    "rejected_details": []
  },
  "agent_performance": [...],
  "recommendations": [
    {"priority": "high", "action": "...", "reason": "..."}
  ]
}
```

## Automated Quality Review
Agent 17 (Autonomous Auditor) will review this quality report and decide GO/CONDITIONAL_GO/NO_GO
before Agent 16 runs. Do not pause — proceed to output the report and complete.

## Time Budget
Target: 5 minutes to generate the report.
