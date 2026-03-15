#!/usr/bin/env python3
"""
Agent 15 — Data Quality Reporter

Generates a comprehensive data quality report by analyzing:
1. Coverage: filled fields per country, grouped by tier
2. Staleness: factors not updated within expected frequency
3. Confidence: average confidence scores per country and per layer
4. Validation: verdict breakdown from validated_updates
5. Agent performance: from run_log.json
6. Recommendations: based on findings

Usage:
    python3 agents/scripts/agent_15_quality_report.py                # auto-detect date/run_id
    python3 agents/scripts/agent_15_quality_report.py --date 2026-03-14 --run-id 2026-W11
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
COUNTRIES_DIR = DATA_DIR / "countries"
STAGING_DIR = PROJECT_ROOT / "staging"

# Staleness thresholds
WEEKLY_STALE_DAYS = 8
MONTHLY_STALE_DAYS = 35

# Sections to analyze for coverage
DATA_SECTIONS = [
    "macroeconomic",
    "demographic",
    "political",
    "military",
    "trade",
    "derived",
    "economy",
    "institutions",
]

# Factors considered "weekly" (should be updated every run)
WEEKLY_FACTORS = {
    "gdp_nominal_usd", "gdp_real_growth_pct", "gdp_per_capita_usd",
    "inflation_cpi_pct", "unemployment_rate_pct", "current_account_pct_gdp",
    "govt_debt_pct_gdp", "fx_reserves_usd", "total_exports_usd",
    "total_imports_usd", "exchange_rate_vs_usd", "sovereign_bond_yield_10yr_pct",
    "equity_index_level", "central_bank_policy_rate_pct",
    "composite_national_power_index", "overall_investment_risk_score",
    "political_risk_premium_bps",
    "government_bond_yield_10y", "central_bank_rate",
}

# Layer mapping for sections
LAYER_MAP = {
    "macroeconomic": "economy",
    "economy": "economy",
    "trade": "economy",
    "demographic": "endowments",
    "institutions": "institutions",
    "political": "institutions",
    "military": "military",
    "derived": "derived",
}

# Metadata/non-data keys to skip at the top level
SKIP_KEYS = {
    "country_code", "country_name", "tier", "region",
    "last_updated", "run_id", "code", "name",
    "executive_summary", "key_changes", "outlook",
    "investor_implications", "active_alerts", "layers", "metadata",
}


def compute_run_id(dt: datetime) -> str:
    """Compute ISO week-based run ID from a datetime."""
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def load_json(path):
    """Load a JSON file, returning None on failure."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  WARNING: Could not load {path}: {e}", file=sys.stderr)
        return None


def count_leaf_factors(obj, depth=0):
    """
    Recursively count leaf factor nodes.
    A leaf factor is a dict that has a 'value' key (the standard factor format).
    Returns (filled_count, total_count, confidence_values, factor_details).
    """
    filled = 0
    total = 0
    confidences = []
    details = []

    if not isinstance(obj, dict):
        return filled, total, confidences, details

    if "value" in obj and ("confidence" in obj or "last_updated" in obj or "source" in obj):
        total += 1
        val = obj["value"]
        is_filled = val is not None and val != "" and val != [] and val != {}
        if is_filled:
            filled += 1
        conf = obj.get("confidence")
        if isinstance(conf, (int, float)):
            confidences.append(conf)
        details.append({
            "confidence": conf,
            "last_updated": obj.get("last_updated"),
        })
        return filled, total, confidences, details

    for key, child in obj.items():
        if isinstance(child, dict):
            f, t, c, d = count_leaf_factors(child, depth + 1)
            filled += f
            total += t
            confidences.extend(c)
            for dd in d:
                dd["factor_name"] = dd.get("factor_name", key)
            details.extend(d)

    return filled, total, confidences, details


def check_staleness(factor_details, section_name, country_code, now):
    """Check for stale factors in a section. Returns list of stale factor info."""
    stale = []
    for d in factor_details:
        lu = d.get("last_updated")
        fname = d.get("factor_name", "unknown")
        if not lu:
            continue
        try:
            lu_dt = datetime.fromisoformat(lu.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        age_days = (now - lu_dt).days

        is_weekly = fname in WEEKLY_FACTORS
        if is_weekly and age_days > WEEKLY_STALE_DAYS:
            stale.append({
                "country": country_code,
                "section": section_name,
                "factor": fname,
                "last_updated": lu,
                "age_days": age_days,
                "expected_frequency": "weekly",
                "threshold_days": WEEKLY_STALE_DAYS,
            })
        elif not is_weekly and age_days > MONTHLY_STALE_DAYS:
            stale.append({
                "country": country_code,
                "section": section_name,
                "factor": fname,
                "last_updated": lu,
                "age_days": age_days,
                "expected_frequency": "monthly",
                "threshold_days": MONTHLY_STALE_DAYS,
            })

    return stale


def analyze_country(country_data, country_code, now):
    """Analyze a single country file for coverage, confidence, and staleness."""
    total_filled = 0
    total_fields = 0
    all_confidences = []
    layer_confidences = defaultdict(list)
    all_stale = []

    for section in DATA_SECTIONS:
        section_data = country_data.get(section, {})
        if not isinstance(section_data, dict):
            continue
        f, t, c, details = count_leaf_factors(section_data)
        total_filled += f
        total_fields += t
        all_confidences.extend(c)

        layer = LAYER_MAP.get(section, section)
        layer_confidences[layer].extend(c)

        stale = check_staleness(details, section, country_code, now)
        all_stale.extend(stale)

    narrative = country_data.get("narrative", {})
    if isinstance(narrative, dict):
        narrative_fields = [
            "executive_summary", "key_changes_this_week", "outlook",
            "investor_implications", "data_quality_note"
        ]
        for nf in narrative_fields:
            total_fields += 1
            val = narrative.get(nf)
            if val and val != "":
                total_filled += 1

    coverage_pct = (total_filled / total_fields * 100) if total_fields > 0 else 0
    avg_confidence = (sum(all_confidences) / len(all_confidences)) if all_confidences else 0

    return {
        "filled": total_filled,
        "total": total_fields,
        "coverage_pct": round(coverage_pct, 1),
        "avg_confidence": round(avg_confidence, 3),
        "confidence_count": len(all_confidences),
        "layer_confidences": dict(layer_confidences),
        "stale_factors": all_stale,
    }


def build_tier_map(country_list):
    """Build code -> tier mapping from country_list.json."""
    tier_map = {}
    for tier_key, tier_data in country_list.get("tiers", {}).items():
        tier_num = int(tier_key.split("_")[1])
        for c in tier_data.get("countries", []):
            tier_map[c["code"]] = tier_num
    return tier_map


def analyze_validation(validated_path):
    """Analyze the validated_updates file for verdict breakdown."""
    data = load_json(validated_path)
    if not data:
        return {
            "total": 0, "accept": 0, "accept_with_note": 0,
            "flag": 0, "reject": 0, "escalate": 0,
            "reject_rate_pct": 0, "rejected_details": [],
            "flagged_details": [],
        }

    updates = data.get("validated_updates", [])
    summary = data.get("summary", {})
    verdicts = Counter(u.get("verdict", "UNKNOWN") for u in updates)

    rejected_details = []
    flagged_details = []
    for u in updates:
        if u.get("verdict") == "REJECT":
            rejected_details.append({
                "country": u.get("country_code", ""),
                "factor": u.get("factor_path", ""),
                "new_value": u.get("new_value"),
                "previous_value": u.get("previous_value"),
                "reason": u.get("notes", ""),
            })
        elif u.get("verdict") == "FLAG":
            flagged_details.append({
                "country": u.get("country_code", ""),
                "factor": u.get("factor_path", ""),
                "new_value": u.get("new_value"),
                "previous_value": u.get("previous_value"),
                "change_pct": u.get("change_pct"),
                "reason": u.get("notes", ""),
            })

    total = len(updates)
    reject_count = verdicts.get("REJECT", 0)

    return {
        "total": summary.get("total", total),
        "accept": verdicts.get("ACCEPT", 0),
        "accept_with_note": verdicts.get("ACCEPT_WITH_NOTE", 0),
        "flag": verdicts.get("FLAG", 0),
        "reject": reject_count,
        "escalate": summary.get("escalate", verdicts.get("ESCALATE", 0)),
        "reject_rate_pct": round(reject_count / total * 100, 2) if total > 0 else 0,
        "rejected_details": rejected_details,
        "flagged_details": flagged_details,
    }


def analyze_agents(run_log):
    """Extract agent performance from run_log.json."""
    agents_list = run_log.get("agents", [])
    performance = []
    for a in agents_list:
        entry = {
            "agent_id": a.get("agent_id", ""),
            "name": a.get("name", ""),
            "status": a.get("status", "unknown"),
            "records_produced": a.get("records_produced", 0),
            "notes": a.get("notes", ""),
        }
        if "duration_seconds" in a:
            entry["duration_seconds"] = a["duration_seconds"]
        performance.append(entry)

    a9 = run_log.get("agent_09")
    if a9:
        performance.append({
            "agent_id": "agent_09",
            "name": "data_integrator",
            "status": a9.get("status", "unknown"),
            "countries_updated": a9.get("countries_updated", 0),
            "factors_updated": a9.get("factors_updated", 0),
            "flags_added": a9.get("flags_added", 0),
            "rejected": a9.get("rejected", 0),
        })

    return performance


def generate_recommendations(coverage, staleness, confidence, validation, agent_perf, country_results):
    """Generate actionable recommendations based on findings."""
    recs = []

    if coverage["tier_1_avg_pct"] < 90:
        recs.append(f"COVERAGE: Tier 1 average coverage at {coverage['tier_1_avg_pct']}% — below 90% target. Prioritize filling gaps in major economy files.")
    if coverage["tier_2_avg_pct"] < 70:
        recs.append(f"COVERAGE: Tier 2 average coverage at {coverage['tier_2_avg_pct']}% — below 70% target. Focus on regional player data completion.")
    if coverage["tier_3_avg_pct"] < 50:
        recs.append(f"COVERAGE: Tier 3 average coverage at {coverage['tier_3_avg_pct']}% — below 50% target. Basic data needed for frontier countries.")
    if coverage.get("tier_1_countries_below_80"):
        codes = [c["code"] for c in coverage["tier_1_countries_below_80"]]
        recs.append(f"COVERAGE: Tier 1 countries below 80%: {', '.join(codes)}. These need immediate data remediation.")

    total_stale = staleness["total_stale_factors"]
    if total_stale > 0:
        weekly_stale = sum(1 for f in staleness.get("all_stale", []) if f.get("expected_frequency") == "weekly")
        monthly_stale = total_stale - weekly_stale
        if weekly_stale > 0:
            recs.append(f"STALENESS: {weekly_stale} weekly-frequency factors are older than {WEEKLY_STALE_DAYS} days. Review gathering agent data freshness.")
        if monthly_stale > 0:
            recs.append(f"STALENESS: {monthly_stale} monthly-frequency factors are older than {MONTHLY_STALE_DAYS} days.")

    if confidence["overall_avg"] < 0.5:
        recs.append(f"CONFIDENCE: Overall average confidence at {confidence['overall_avg']:.3f} — consider adding more corroborating sources.")
    if confidence["low_confidence_countries"]:
        codes = [c["code"] for c in confidence["low_confidence_countries"]]
        recs.append(f"CONFIDENCE: Low-confidence countries (<0.5): {', '.join(codes)}. Cross-validate with additional sources.")

    if validation["reject"] > 5:
        recs.append(f"VALIDATION: {validation['reject']} rejected updates — review source data quality for affected factors.")
    if validation["flag"] > 0:
        flagged_summary = []
        for fd in validation.get("flagged_details", []):
            flagged_summary.append(f"{fd['country']}/{fd['factor'].split('.')[-1]}")
        recs.append(f"VALIDATION: {validation['flag']} flagged updates ({', '.join(flagged_summary)}). Review for data accuracy.")
    if validation.get("escalate", 0) > 20:
        recs.append(f"VALIDATION: {validation['escalate']} escalations — exceeds target of <=20. Tighten gathering agent thresholds.")

    for a in agent_perf:
        if a.get("status") not in ("completed", "SUCCESS", "in_progress"):
            recs.append(f"AGENT: {a.get('agent_id', '?')} ({a.get('name', '?')}) status: {a.get('status', '?')} — investigate failure.")

    empty_political = sum(1 for r in country_results.values() if r.get("_political_empty"))
    if empty_political > 0:
        recs.append(f"DATA GAP: {empty_political} countries have empty 'political' sections (data is in 'institutions' section instead). Consider deprecating the 'political' top-level key or migrating data.")

    if not recs:
        recs.append("All quality metrics within acceptable thresholds. No immediate action required.")

    return recs


def find_validated_updates(staging_dir, report_date):
    """Find the validated_updates file, trying exact date then most recent."""
    exact = staging_dir / "validated" / f"validated_updates_{report_date}.json"
    if exact.exists():
        return exact
    # Fall back to most recent
    validated_dir = staging_dir / "validated"
    if validated_dir.exists():
        candidates = sorted(validated_dir.glob("validated_updates_*.json"), reverse=True)
        if candidates:
            return candidates[0]
    return exact  # will produce a warning when load_json fails


def main():
    parser = argparse.ArgumentParser(description="Agent 15 — Data Quality Reporter")
    parser.add_argument("--date", help="Report date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--run-id", help="Run ID (e.g. 2026-W11). Default: auto from date.")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    report_date = args.date or now.strftime("%Y-%m-%d")
    run_id = args.run_id or compute_run_id(now)

    # Parse the report date for staleness checks
    report_dt = datetime.fromisoformat(report_date + "T23:59:59+00:00")

    print(f"Agent 15 — Data Quality Reporter")
    print(f"Run: {run_id} | Date: {report_date}")
    print("=" * 60)

    # Load supporting files
    country_list = load_json(DATA_DIR / "indices" / "country_list.json")
    run_log = load_json(STAGING_DIR / "run_log.json")
    validated_path = find_validated_updates(STAGING_DIR, report_date)

    if not country_list:
        print("ERROR: Cannot load country_list.json", file=sys.stderr)
        sys.exit(1)

    tier_map = build_tier_map(country_list)

    # 1. Coverage & Confidence & Staleness
    print("\n[1/5] Analyzing coverage, confidence, and staleness...")
    country_results = {}
    tier_stats = defaultdict(list)
    tier_confidence = defaultdict(list)
    global_layer_confidences = defaultdict(list)
    all_stale_factors = []

    country_files = sorted(COUNTRIES_DIR.glob("*.json"))
    for cf in country_files:
        code = cf.stem
        data = load_json(cf)
        if not data:
            continue

        result = analyze_country(data, code, report_dt)
        pol = data.get("political", {})
        result["_political_empty"] = not pol or pol == {}
        country_results[code] = result

        tier = tier_map.get(code, 0)
        if tier > 0:
            tier_stats[tier].append(result["coverage_pct"])
            tier_confidence[tier].append(result["avg_confidence"])

        for layer, confs in result["layer_confidences"].items():
            global_layer_confidences[layer].extend(confs)

        all_stale_factors.extend(result["stale_factors"])

    tier_1_avg = round(sum(tier_stats.get(1, [])) / len(tier_stats.get(1, [1])), 1) if tier_stats.get(1) else 0
    tier_2_avg = round(sum(tier_stats.get(2, [])) / len(tier_stats.get(2, [1])), 1) if tier_stats.get(2) else 0
    tier_3_avg = round(sum(tier_stats.get(3, [])) / len(tier_stats.get(3, [1])), 1) if tier_stats.get(3) else 0

    tier_1_below_80 = []
    for code, tier in tier_map.items():
        if tier == 1 and code in country_results:
            if country_results[code]["coverage_pct"] < 80:
                tier_1_below_80.append({
                    "code": code,
                    "coverage_pct": country_results[code]["coverage_pct"],
                    "filled": country_results[code]["filled"],
                    "total": country_results[code]["total"],
                })

    flagged_countries = []
    tier_targets = {1: 90, 2: 70, 3: 50}
    for code, tier in tier_map.items():
        if code in country_results:
            target = tier_targets.get(tier, 50)
            if country_results[code]["coverage_pct"] < target:
                flagged_countries.append({
                    "code": code,
                    "tier": tier,
                    "coverage_pct": country_results[code]["coverage_pct"],
                    "target_pct": target,
                })

    print(f"  Tier 1 avg coverage: {tier_1_avg}%  (target >=90%)")
    print(f"  Tier 2 avg coverage: {tier_2_avg}%  (target >=70%)")
    print(f"  Tier 3 avg coverage: {tier_3_avg}%  (target >=50%)")
    print(f"  Tier 1 countries below 80%: {len(tier_1_below_80)}")
    print(f"  Countries below tier target: {len(flagged_countries)}")

    # 2. Staleness
    print(f"\n[2/5] Checking data staleness...")
    stale_by_tier = defaultdict(list)
    for sf in all_stale_factors:
        cc = sf["country"]
        tier = tier_map.get(cc, 0)
        tier_key = f"tier_{tier}" if tier > 0 else "untiered"
        stale_by_tier[tier_key].append(f"{cc}.{sf['factor']} ({sf['age_days']}d)")

    print(f"  Total stale factors: {len(all_stale_factors)}")
    for tk in sorted(stale_by_tier.keys()):
        print(f"    {tk}: {len(stale_by_tier[tk])} stale factors")

    # 3. Confidence
    all_conf = [country_results[c]["avg_confidence"] for c in country_results if country_results[c]["confidence_count"] > 0]
    overall_avg_conf = round(sum(all_conf) / len(all_conf), 3) if all_conf else 0

    by_layer = {}
    for layer, confs in sorted(global_layer_confidences.items()):
        if confs:
            by_layer[layer] = round(sum(confs) / len(confs), 3)

    low_conf_countries = []
    for code in country_results:
        r = country_results[code]
        if r["confidence_count"] > 0 and r["avg_confidence"] < 0.5:
            low_conf_countries.append({
                "code": code,
                "avg_confidence": r["avg_confidence"],
            })

    print(f"\n  Overall avg confidence: {overall_avg_conf}")
    for layer, avg in by_layer.items():
        print(f"    {layer}: {avg}")
    print(f"  Countries with avg confidence < 0.5: {len(low_conf_countries)}")

    # 4. Validation
    print("\n[3/5] Analyzing validation results...")
    validation = analyze_validation(validated_path)
    print(f"  Total validated: {validation['total']}")
    print(f"  ACCEPT: {validation['accept']}, ACCEPT_WITH_NOTE: {validation['accept_with_note']}")
    print(f"  FLAG: {validation['flag']}, REJECT: {validation['reject']}, ESCALATE: {validation['escalate']}")
    print(f"  Reject rate: {validation['reject_rate_pct']}%")

    # 5. Agent Performance
    print("\n[4/5] Analyzing agent performance...")
    agent_perf = analyze_agents(run_log) if run_log else []
    if agent_perf:
        for a in agent_perf:
            status_str = a.get("status", "?")
            records = a.get("records_produced", a.get("factors_updated", "?"))
            print(f"  {a.get('agent_id', '?'):12s} | {a.get('name', '?'):30s} | {status_str:12s} | records: {records}")
    else:
        print("  No agent entries in run_log (run still in progress or agents field empty).")

    # 6. Recommendations
    print("\n[5/5] Generating recommendations...")
    coverage_section = {
        "tier_1_avg_pct": tier_1_avg,
        "tier_2_avg_pct": tier_2_avg,
        "tier_3_avg_pct": tier_3_avg,
        "tier_1_target_pct": 90,
        "tier_2_target_pct": 70,
        "tier_3_target_pct": 50,
        "tier_1_countries_below_80": tier_1_below_80,
        "flagged_countries": flagged_countries,
        "countries_analyzed": len(country_results),
    }

    staleness_section = {
        "total_stale_factors": len(all_stale_factors),
        "by_tier": {tk: stale_by_tier[tk] for tk in sorted(stale_by_tier.keys())},
        "all_stale": all_stale_factors,
    }

    confidence_section = {
        "overall_avg": overall_avg_conf,
        "by_layer": by_layer,
        "tier_1_avg": round(sum(tier_confidence.get(1, [])) / len(tier_confidence.get(1, [1])), 3) if tier_confidence.get(1) else 0,
        "tier_2_avg": round(sum(tier_confidence.get(2, [])) / len(tier_confidence.get(2, [1])), 3) if tier_confidence.get(2) else 0,
        "tier_3_avg": round(sum(tier_confidence.get(3, [])) / len(tier_confidence.get(3, [1])), 3) if tier_confidence.get(3) else 0,
        "low_confidence_countries": low_conf_countries,
    }

    recs = generate_recommendations(
        coverage_section, staleness_section, confidence_section,
        validation, agent_perf, country_results,
    )
    for i, r in enumerate(recs, 1):
        print(f"  {i}. {r}")

    # Build final report
    print("\n[6/6] Writing quality report...")

    country_detail = {}
    for code in sorted(country_results.keys()):
        r = country_results[code]
        country_detail[code] = {
            "filled": r["filled"],
            "total": r["total"],
            "coverage_pct": r["coverage_pct"],
            "avg_confidence": r["avg_confidence"],
            "tier": tier_map.get(code, 0),
        }

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    staleness_report = {
        "total_stale_factors": len(all_stale_factors),
        "by_tier": {},
    }
    for tier_num in [1, 2, 3]:
        tk = f"tier_{tier_num}"
        entries = stale_by_tier.get(tk, [])
        staleness_report["by_tier"][tk] = entries[:20]
        if len(entries) > 20:
            staleness_report["by_tier"][tk].append(f"... and {len(entries) - 20} more")

    report = {
        "report_date": report_date,
        "run_id": run_id,
        "generated_at": generated_at,
        "coverage": {
            "tier_1_avg_pct": tier_1_avg,
            "tier_2_avg_pct": tier_2_avg,
            "tier_3_avg_pct": tier_3_avg,
            "tier_1_target_pct": 90,
            "tier_2_target_pct": 70,
            "tier_3_target_pct": 50,
            "tier_1_countries_below_80": sorted(tier_1_below_80, key=lambda x: x["coverage_pct"]),
            "flagged_countries": sorted(flagged_countries, key=lambda x: x["coverage_pct"]),
            "countries_analyzed": len(country_results),
            "country_detail": country_detail,
        },
        "staleness": staleness_report,
        "confidence": confidence_section,
        "validation": {
            "total": validation["total"],
            "accept": validation["accept"],
            "accept_with_note": validation["accept_with_note"],
            "flag": validation["flag"],
            "reject": validation["reject"],
            "escalate": validation["escalate"],
            "reject_rate_pct": validation["reject_rate_pct"],
            "rejected_details": validation["rejected_details"],
            "flagged_details": validation["flagged_details"],
        },
        "agent_performance": agent_perf,
        "recommendations": recs,
    }

    # Determine overall verdict
    tier_1_ok = tier_1_avg >= 90
    tier_2_ok = tier_2_avg >= 70
    tier_3_ok = tier_3_avg >= 50
    all_agents_ok = len(agent_perf) == 0 or all(
        a.get("status") in ("completed", "SUCCESS", "in_progress") for a in agent_perf
    )
    reject_rate_ok = validation["reject_rate_pct"] < 5

    if tier_1_ok and tier_2_ok and tier_3_ok and all_agents_ok and reject_rate_ok:
        verdict = "GO"
    elif all_agents_ok and reject_rate_ok:
        verdict = "CONDITIONAL_GO"
    else:
        verdict = "NO_GO"

    report["overall_verdict"] = verdict

    output_path = DATA_DIR / "metadata" / f"quality_report_{report_date}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n  Report written to: {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("QUALITY REPORT SUMMARY")
    print("=" * 60)
    print(f"  Coverage:   T1={tier_1_avg}%  T2={tier_2_avg}%  T3={tier_3_avg}%")
    print(f"  Staleness:  {len(all_stale_factors)} stale factors")
    print(f"  Confidence: Overall={overall_avg_conf}  Low-conf countries={len(low_conf_countries)}")
    print(f"  Validation: {validation['total']} updates — {validation['accept']} accepted, {validation['reject']} rejected, {validation['flag']} flagged, {validation['escalate']} escalated")
    if agent_perf:
        print(f"  Agents:     {sum(1 for a in agent_perf if a.get('status') in ('completed','SUCCESS'))}/{len(agent_perf)} completed successfully")
    else:
        print(f"  Agents:     Run in progress (no agent entries logged yet)")
    print(f"  Recommendations: {len(recs)}")
    print(f"\n  OVERALL VERDICT: {verdict}")

    print(f"\nAgent 15 complete.")
    return verdict


if __name__ == "__main__":
    verdict = main()
    sys.exit(0 if verdict in ("GO", "CONDITIONAL_GO") else 1)
