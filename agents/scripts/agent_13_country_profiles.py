#!/usr/bin/env python3
"""
Agent 13 — Country Profile Synthesizer
Generates investor-focused narrative sections for Tier 1+2 countries.
Run ID: 2026-W11 | Date: 2026-03-10
"""

import json
import os
from datetime import datetime
from collections import defaultdict

BASE = "/home/pietro/stratoterra"
DATA_DIR = os.path.join(BASE, "data")
STAGING_DIR = os.path.join(BASE, "staging")

RUN_ID = "2026-W11"
GEN_DATE = "2026-03-10T06:00:00Z"
REFERENCE_DATE = "2026-03-10"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def fmt_pct(val):
    """Format percentage value."""
    if val is None:
        return "n/a"
    return f"{val:.1f}%"


def fmt_usd(val):
    """Format USD value in human-readable form."""
    if val is None:
        return "n/a"
    if abs(val) >= 1e12:
        return f"${val/1e12:.1f}T"
    if abs(val) >= 1e9:
        return f"${val/1e9:.1f}B"
    if abs(val) >= 1e6:
        return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


def fmt_score(val):
    """Format 0-1 score."""
    if val is None:
        return "n/a"
    return f"{val:.3f}"


def get_value(section, key, default=None):
    """Safely extract a value from a country data section."""
    if section is None:
        return default
    item = section.get(key, {})
    if isinstance(item, dict):
        return item.get("value", default)
    return item if item is not None else default


def get_trend(section, key, default="n/a"):
    """Safely extract a trend from a country data section."""
    if section is None:
        return default
    item = section.get(key, {})
    if isinstance(item, dict):
        return item.get("trend", default)
    return default


def trend_label(trend):
    """Convert trend code to human-readable label."""
    labels = {
        "strong_growth": "rising sharply",
        "growth": "rising",
        "stable": "stable",
        "decrease": "declining",
        "strong_decrease": "declining sharply",
    }
    return labels.get(trend, trend if trend else "stable")


def classify_country(alerts_by_severity, trend_data):
    """Classify country as crisis/event-heavy/stable for template selection."""
    n_critical = len(alerts_by_severity.get("critical", []))
    n_warning = len(alerts_by_severity.get("warning", []))

    if n_critical > 0:
        return "crisis"
    if n_warning > 0:
        return "event_heavy"
    return "stable"


def build_alerts_index(alert_data):
    """Build per-country alert lookup from alert_index.json."""
    country_alerts = defaultdict(lambda: {"critical": [], "warning": [], "watch": []})
    for a in alert_data.get("alerts", []):
        cc = a.get("country_code", "")
        sev = a.get("severity", "")
        if cc and sev in ("critical", "warning", "watch"):
            country_alerts[cc][sev].append(a)
    return country_alerts


def build_trends_index(trend_data):
    """Build per-country trend lookup from trend_estimates."""
    country_trends = defaultdict(list)
    for est in trend_data.get("estimates", []):
        cc = est.get("country_code", "")
        if cc:
            country_trends[cc].append(est)
    return country_trends


def build_events_index(events_data):
    """Build per-country event lookup from news_events."""
    country_events = defaultdict(list)
    for evt in events_data.get("events", []):
        # Associate with all countries involved
        for cc in evt.get("countries_involved", []):
            country_events[cc].append(evt)
        # Also associate with primary_country
        pc = evt.get("primary_country")
        if pc and pc not in evt.get("countries_involved", []):
            country_events[pc].append(evt)
    return country_events


def get_key_macro(country_data):
    """Extract key macroeconomic indicators."""
    macro = country_data.get("macroeconomic", {})
    return {
        "gdp_growth": get_value(macro, "gdp_real_growth_pct"),
        "gdp_growth_trend": get_trend(macro, "gdp_real_growth_pct"),
        "inflation": get_value(macro, "inflation_cpi_pct"),
        "inflation_trend": get_trend(macro, "inflation_cpi_pct"),
        "unemployment": get_value(macro, "unemployment_rate_pct"),
        "debt_gdp": get_value(macro, "govt_debt_pct_gdp"),
        "debt_trend": get_trend(macro, "govt_debt_pct_gdp"),
        "current_account": get_value(macro, "current_account_pct_gdp"),
        "ca_trend": get_trend(macro, "current_account_pct_gdp"),
        "policy_rate": get_value(macro, "central_bank_policy_rate_pct"),
        "credit_rating": get_value(macro, "sovereign_credit_rating"),
        "gdp_nominal": get_value(macro, "gdp_nominal_usd"),
        "gdp_per_capita": get_value(macro, "gdp_per_capita_usd"),
        "fx_reserves": get_value(macro, "fx_reserves_usd"),
        "gdp_forecast": get_value(macro, "gdp_growth_forecast_2026_pct"),
    }


def get_key_derived(country_data):
    """Extract derived metrics."""
    derived = country_data.get("derived", {})
    return {
        "investment_risk": get_value(derived, "overall_investment_risk_score"),
        "investment_risk_trend": get_trend(derived, "overall_investment_risk_score"),
        "chokepoint_exposure": get_value(derived, "supply_chain_chokepoint_exposure"),
        "political_risk_premium": get_value(derived, "political_risk_premium_bps"),
        "energy_independence": get_value(derived, "energy_independence_index"),
        "resource_self_sufficiency": get_value(derived, "resource_self_sufficiency_index"),
        "composite_power": get_value(derived, "composite_national_power_index"),
        "market_accessibility": get_value(derived, "market_accessibility_score"),
        "political_stability_trend": get_value(derived, "political_stability_trend"),
        "trade_openness_trend": get_value(derived, "trade_openness_trend"),
    }


def build_executive_summary(country_name, cc, macro, derived, alerts_by_sev, events, trends, country_class):
    """Build the executive summary (3-5 sentences)."""

    parts = []

    # Lead with crisis/critical alerts if present
    critical_alerts = alerts_by_sev.get("critical", [])
    warning_alerts = alerts_by_sev.get("warning", [])

    if country_class == "crisis":
        # Lead with the most severe issue
        crisis_headlines = [a["headline"] for a in critical_alerts[:2]]
        parts.append(f"{country_name} faces critical-level risks this week: {'; '.join(crisis_headlines)}.")

    # Key events this week
    high_impact_events = [e for e in events if e.get("severity") in ("transformative", "major")]
    if high_impact_events and country_class != "crisis":
        top_evt = high_impact_events[0]
        parts.append(f"{top_evt['headline']}.")

    # Macro snapshot
    gdp_g = macro["gdp_growth"]
    infl = macro["inflation"]
    gdp_trend = macro["gdp_growth_trend"]
    infl_trend = macro["inflation_trend"]

    if gdp_g is not None:
        gdp_str = f"GDP growth at {fmt_pct(gdp_g)} ({trend_label(gdp_trend)})"
    else:
        gdp_str = f"GDP growth trend {trend_label(gdp_trend)}"

    if infl is not None:
        infl_str = f"inflation at {fmt_pct(infl)} ({trend_label(infl_trend)})"
    else:
        infl_str = f"inflation {trend_label(infl_trend)}"

    parts.append(f"{gdp_str}, {infl_str}.")

    # Chokepoint / energy exposure
    choke = derived.get("chokepoint_exposure")
    if choke is not None and choke > 0.5:
        parts.append(
            f"Supply chain chokepoint exposure is critically elevated at {fmt_score(choke)} amid the Strait of Hormuz crisis."
        )

    # Political risk premium if notable
    prp = derived.get("political_risk_premium")
    if prp is not None and prp > 300:
        parts.append(f"Political risk premium stands at {int(prp)} bps, signaling elevated sovereign risk.")

    # Investment risk
    inv_risk = derived.get("investment_risk")
    inv_trend = derived.get("investment_risk_trend")
    if inv_risk is not None:
        if inv_risk > 0.5:
            parts.append(f"Overall investment risk is elevated at {fmt_score(inv_risk)} and {trend_label(inv_trend)}.")
        elif inv_trend in ("decrease", "strong_decrease"):
            parts.append(f"Investment risk score at {fmt_score(inv_risk)}, trending {trend_label(inv_trend)}.")

    # Warning alerts if no crisis
    if country_class == "event_heavy" and not parts:
        warn_headlines = [a["headline"] for a in warning_alerts[:2]]
        parts.append(f"Active warnings: {'; '.join(warn_headlines)}.")

    # For stable countries with no events, give brief overview
    if country_class == "stable" and len(parts) <= 1:
        energy = derived.get("energy_independence")
        if energy is not None:
            parts.append(
                f"Energy independence index at {fmt_score(energy)}. "
                f"The economy remains broadly stable with no major disruptions this week."
            )
        else:
            parts.append("The economy remains broadly stable with no major disruptions this week.")

    return " ".join(parts[:5])  # Cap at 5 sentences


def build_key_changes(country_name, cc, events, trends, alerts_by_sev):
    """Build list of key changes this week."""
    changes = []

    # From high-impact events
    seen_headlines = set()
    for evt in events:
        if evt.get("severity") in ("transformative", "major"):
            headline = evt.get("headline", "")
            if headline and headline not in seen_headlines:
                changes.append(headline)
                seen_headlines.add(headline)

    # From trend changes (non-stable)
    notable_trends = []
    for t in trends:
        if t.get("trend") in ("strong_growth", "strong_decrease", "growth", "decrease"):
            factor = t.get("factor", "")
            trend_val = t.get("trend", "")
            reasoning = t.get("reasoning", "")
            # Only include the most impactful trends
            if factor in (
                "gdp_real_growth_pct",
                "inflation_cpi_pct",
                "political_stability",
                "overall_investment_risk_score",
            ):
                label = factor.replace("_", " ").replace("pct", "%").title()
                notable_trends.append(f"{label}: {trend_label(trend_val)}")

    # From alerts
    for a in alerts_by_sev.get("critical", []):
        h = a.get("headline", "")
        if h and h not in seen_headlines:
            changes.append(h)
            seen_headlines.add(h)

    for a in alerts_by_sev.get("warning", [])[:3]:
        h = a.get("headline", "")
        if h and h not in seen_headlines:
            changes.append(h)
            seen_headlines.add(h)

    # Add notable trends if not already covered
    for nt in notable_trends:
        if nt not in seen_headlines:
            changes.append(nt)

    # Deduplicate and cap
    return changes[:8]


def build_outlook(country_name, cc, macro, derived, trends, country_class):
    """Build 2-3 sentence outlook."""
    parts = []

    gdp_trend = macro["gdp_growth_trend"]
    infl_trend = macro["inflation_trend"]
    debt_trend = macro["debt_trend"]
    pol_stab = derived.get("political_stability_trend")

    if country_class == "crisis":
        parts.append(
            f"Near-term outlook for {country_name} is highly uncertain given active crisis conditions."
        )
        # Find trend reasoning for investment risk
        for t in trends:
            if t.get("factor") == "overall_investment_risk_score":
                parts.append(t.get("investor_implication", ""))
                break
    else:
        # GDP trajectory
        if gdp_trend in ("strong_decrease", "decrease"):
            parts.append(f"GDP growth is on a downward trajectory.")
        elif gdp_trend in ("strong_growth", "growth"):
            parts.append(f"GDP growth momentum remains positive.")
        else:
            parts.append(f"GDP growth outlook is broadly stable.")

        # Inflation and policy
        if infl_trend in ("growth", "strong_growth"):
            parts.append(
                f"Inflation is {trend_label(infl_trend)}, likely constraining monetary easing."
            )
        elif infl_trend in ("decrease", "strong_decrease"):
            parts.append(
                f"Inflation is {trend_label(infl_trend)}, potentially opening space for monetary easing."
            )

    # Political stability
    if pol_stab in ("decrease", "strong_decrease"):
        parts.append(f"Political stability is {trend_label(pol_stab)}, adding to investor uncertainty.")
    elif pol_stab in ("growth", "strong_growth"):
        parts.append(f"Political stability is improving, supporting investor confidence.")

    # Debt trajectory
    if debt_trend in ("growth", "strong_growth"):
        fiscal_note = f"Fiscal trajectory warrants monitoring as government debt is {trend_label(debt_trend)}."
        if len(parts) < 3:
            parts.append(fiscal_note)

    return " ".join(parts[:3])


def build_investor_implications(country_name, cc, macro, derived, trends, events, country_class):
    """Build 2-3 sentence investor implications."""
    parts = []

    inv_risk = derived.get("investment_risk")
    choke = derived.get("chokepoint_exposure")
    energy_ind = derived.get("energy_independence")
    prp = derived.get("political_risk_premium")
    market_access = derived.get("market_accessibility")

    if country_class == "crisis":
        if inv_risk is not None and inv_risk > 0.5:
            parts.append(
                f"Investment risk is critically elevated at {fmt_score(inv_risk)}. "
                f"Defensive positioning or risk reduction recommended."
            )
        else:
            parts.append(
                "Active crisis conditions warrant heightened caution and defensive positioning."
            )

    # Chokepoint exposure implications
    if choke is not None and choke > 0.5:
        parts.append(
            f"Extreme supply chain chokepoint exposure ({fmt_score(choke)}) "
            f"creates acute risk for trade-dependent sectors."
        )

    # Energy exposure
    if energy_ind is not None:
        if energy_ind < 0.3:
            parts.append(
                f"Low energy independence ({fmt_score(energy_ind)}) makes the economy vulnerable to the oil price shock."
            )
        elif energy_ind > 0.8:
            parts.append(
                f"High energy independence ({fmt_score(energy_ind)}) provides a buffer against the oil price shock."
            )

    # Market accessibility
    if market_access is not None and market_access > 0.7 and country_class != "crisis":
        parts.append(f"Market accessibility score of {fmt_score(market_access)} supports capital flows.")

    # Risk premium
    if prp is not None and prp > 500 and country_class != "crisis":
        parts.append(
            f"Elevated political risk premium ({int(prp)} bps) suggests caution on sovereign exposure."
        )

    # Get investor implications from trends
    for t in trends:
        if t.get("factor") == "overall_investment_risk_score":
            impl = t.get("investor_implication", "")
            if impl and len(parts) < 3:
                parts.append(impl)
            break

    # Fallback for stable countries
    if not parts:
        if inv_risk is not None:
            if inv_risk < 0.3:
                parts.append(
                    f"Investment risk remains low at {fmt_score(inv_risk)}. "
                    f"{country_name} continues to offer a favorable risk-reward profile."
                )
            else:
                parts.append(
                    f"Investment risk at {fmt_score(inv_risk)} is moderate. "
                    f"Monitor macro trends for positioning adjustments."
                )
        else:
            parts.append(f"Monitor evolving macro conditions for positioning adjustments.")

    return " ".join(parts[:3])


def build_data_quality_note(country_data, macro, derived, trends, cc):
    """Build data quality note."""
    issues = []

    # Check confidence levels
    macro_section = country_data.get("macroeconomic", {})
    low_conf_factors = []
    for key, val in macro_section.items():
        if isinstance(val, dict) and val.get("confidence") is not None:
            if val["confidence"] < 0.5:
                low_conf_factors.append(key)

    if low_conf_factors:
        issues.append(
            f"Low confidence on {len(low_conf_factors)} macro indicator(s): "
            f"{', '.join(low_conf_factors[:3])}."
        )

    # Check for missing key data
    missing = []
    for key in ["gdp_real_growth_pct", "inflation_cpi_pct", "unemployment_rate_pct"]:
        val = get_value(macro_section, key)
        if val is None:
            missing.append(key.replace("_", " "))
    if missing:
        issues.append(f"Missing data: {', '.join(missing)}.")

    # Check trend coverage
    trend_factors = [t.get("factor") for t in trends]
    if len(trend_factors) < 5:
        issues.append(f"Limited trend coverage ({len(trend_factors)} factors estimated).")

    # Check staleness
    last_updated = country_data.get("last_updated", "")
    if last_updated and "2026-03-10" not in last_updated and "2026-03-09" not in last_updated:
        issues.append(f"Some data may be from a prior week (last updated: {last_updated}).")

    if not issues:
        return "Data quality is within acceptable parameters for this update cycle. All key indicators have adequate source coverage."

    return " ".join(issues)


def generate_narrative(country_data, cc, country_name, alerts_by_sev, trends, events):
    """Generate the complete narrative object for a country."""
    macro = get_key_macro(country_data)
    derived = get_key_derived(country_data)
    country_class = classify_country(alerts_by_sev, trends)

    narrative = {
        "ai_generated": True,
        "generated_at": GEN_DATE,
        "run_id": RUN_ID,
        "executive_summary": build_executive_summary(
            country_name, cc, macro, derived, alerts_by_sev, events, trends, country_class
        ),
        "key_changes_this_week": build_key_changes(
            country_name, cc, events, trends, alerts_by_sev
        ),
        "outlook": build_outlook(
            country_name, cc, macro, derived, trends, country_class
        ),
        "investor_implications": build_investor_implications(
            country_name, cc, macro, derived, trends, events, country_class
        ),
        "data_quality_note": build_data_quality_note(
            country_data, macro, derived, trends, cc
        ),
    }

    return narrative


def main():
    print(f"=== Agent 13: Country Profile Synthesizer ===")
    print(f"Run ID: {RUN_ID} | Date: {REFERENCE_DATE}")
    print()

    # Load inputs
    print("Loading inputs...")
    country_list = load_json(os.path.join(DATA_DIR, "indices", "country_list.json"))
    alert_index = load_json(os.path.join(DATA_DIR, "indices", "alert_index.json"))
    trend_estimates = load_json(
        os.path.join(STAGING_DIR, "trends", "trend_estimates_2026-03-10.json")
    )
    news_events = load_json(
        os.path.join(STAGING_DIR, "raw_collected", "news_events_2026-03-10.json")
    )

    # Build indexes
    alerts_index = build_alerts_index(alert_index)
    trends_index = build_trends_index(trend_estimates)
    events_index = build_events_index(news_events)

    # Get Tier 1 + Tier 2 countries
    tiers = country_list.get("tiers", {})
    target_countries = []
    for tier_key in ("tier_1", "tier_2"):
        tier_data = tiers.get(tier_key, {})
        for c in tier_data.get("countries", []):
            target_countries.append((c["code"], c["name"], tier_key))

    print(f"Target countries: {len(target_countries)} (Tier 1 + Tier 2)")
    print()

    # Process each country
    success_count = 0
    error_count = 0
    crisis_countries = []
    event_heavy_countries = []
    stable_countries = []

    for cc, name, tier in target_countries:
        country_file = os.path.join(DATA_DIR, "countries", f"{cc}.json")

        if not os.path.exists(country_file):
            print(f"  SKIP {cc} ({name}): file not found")
            error_count += 1
            continue

        try:
            country_data = load_json(country_file)

            alerts_by_sev = alerts_index.get(cc, {"critical": [], "warning": [], "watch": []})
            trends = trends_index.get(cc, [])
            events = events_index.get(cc, [])

            # Classify
            country_class = classify_country(alerts_by_sev, trends)
            if country_class == "crisis":
                crisis_countries.append(cc)
            elif country_class == "event_heavy":
                event_heavy_countries.append(cc)
            else:
                stable_countries.append(cc)

            # Generate narrative
            narrative = generate_narrative(
                country_data, cc, name, alerts_by_sev, trends, events
            )

            # Update country data
            country_data["narrative"] = narrative

            # Save
            save_json(country_file, country_data)

            n_alerts = (
                len(alerts_by_sev.get("critical", []))
                + len(alerts_by_sev.get("warning", []))
                + len(alerts_by_sev.get("watch", []))
            )
            n_events = len(events)
            n_trends = len(trends)

            print(
                f"  OK   {cc} ({name}): {country_class} | "
                f"{n_alerts} alerts, {n_events} events, {n_trends} trends | "
                f"{len(narrative['key_changes_this_week'])} changes"
            )
            success_count += 1

        except Exception as e:
            print(f"  ERR  {cc} ({name}): {e}")
            error_count += 1

    # Summary
    print()
    print("=" * 60)
    print(f"RESULTS: {success_count} narratives generated, {error_count} errors")
    print(f"  Crisis countries ({len(crisis_countries)}): {', '.join(crisis_countries)}")
    print(f"  Event-heavy countries ({len(event_heavy_countries)}): {', '.join(event_heavy_countries)}")
    print(f"  Stable countries ({len(stable_countries)}): {', '.join(stable_countries)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
