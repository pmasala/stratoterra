#!/usr/bin/env python3
"""
Agent 12 — Alert Generator
Run ID: 2026-W11 | Date: 2026-03-10

Scans all country data for threshold breaches, generates alert_index.json
and event_feed.json.
"""

import json
import os
from datetime import datetime, timezone

RUN_ID = "2026-W11"
DATE = "2026-03-10"
TIMESTAMP = "2026-03-10T00:00:00Z"
NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COUNTRIES_DIR = os.path.join(BASE, "data", "countries")
INDICES_DIR = os.path.join(BASE, "data", "indices")
GLOBAL_DIR = os.path.join(BASE, "data", "global")
STAGING_DIR = os.path.join(BASE, "staging")
TRENDS_FILE = os.path.join(STAGING_DIR, "trends", "trend_estimates_2026-03-10.json")
NEWS_FILE = os.path.join(STAGING_DIR, "raw_collected", "news_events_2026-03-10.json")
OLD_ALERTS_FILE = os.path.join(INDICES_DIR, "alert_index.json")


def safe_get(d, *keys, default=None):
    """Safely navigate nested dict/object."""
    cur = d
    for k in keys:
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return default
        if cur is None:
            return default
    return cur


def get_value(d, *keys, default=None):
    """Get .value from a factor entry, or the raw value if not a dict."""
    obj = safe_get(d, *keys)
    if isinstance(obj, dict):
        return obj.get("value", default)
    return obj if obj is not None else default


def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def load_countries():
    countries = {}
    for fname in sorted(os.listdir(COUNTRIES_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(COUNTRIES_DIR, fname)
            data = load_json(path)
            if data and "country_code" in data:
                countries[data["country_code"]] = data
    return countries


def load_old_alerts():
    data = load_json(OLD_ALERTS_FILE)
    if data and "alerts" in data:
        # Index by (country_code, trigger) for matching
        lookup = {}
        for a in data["alerts"]:
            key = (a.get("country_code"), a.get("trigger", "")[:60])
            lookup[key] = a
        return data, lookup
    return None, {}


def load_trends():
    data = load_json(TRENDS_FILE)
    if data and "estimates" in data:
        # Index by (country_code, factor)
        lookup = {}
        for e in data["estimates"]:
            key = (e.get("country_code"), e.get("factor"))
            lookup[key] = e
        return lookup
    return {}


def load_news():
    data = load_json(NEWS_FILE)
    if data and "events" in data:
        return data["events"]
    return []


# ── Alert generation ────────────────────────────────────────────────────────

alert_counter = 0


def make_alert_id():
    global alert_counter
    alert_counter += 1
    return f"alert_{DATE}_{alert_counter:03d}"


def make_alert(severity, cc, trigger, headline, details, affected_factors,
               old_lookup=None, first_triggered=None):
    """Create an alert record, checking for existing alerts to preserve first_triggered."""
    # Try to find existing alert
    status = "new"
    ft = first_triggered or TIMESTAMP
    if old_lookup:
        # Check by (cc, trigger prefix)
        key = (cc, trigger[:60])
        old = old_lookup.get(key)
        if old:
            ft = old.get("first_triggered", ft)
            status = "ongoing"

    return {
        "alert_id": make_alert_id(),
        "severity": severity,
        "country_code": cc,
        "status": status,
        "trigger": trigger,
        "headline": headline,
        "details": details,
        "first_triggered": ft,
        "last_updated": TIMESTAMP,
        "affected_factors": affected_factors,
        "run_id": RUN_ID,
        "title": headline,
        "description": details,
        "countries": [cc],
        "type": "geopolitical_event"
    }


def scan_country(cc, data, trends, old_lookup, news_by_country):
    """Scan a single country for all alert triggers. Returns list of alerts."""
    alerts = []
    name = data.get("country_name", cc)

    # ── Extract key metrics ──
    risk = get_value(data, "derived", "overall_investment_risk_score")
    prp = get_value(data, "derived", "political_risk_premium_bps")
    chokepoint = get_value(data, "derived", "supply_chain_chokepoint_exposure")
    inflation = get_value(data, "macroeconomic", "inflation_cpi_pct")
    gdp_trend = safe_get(data, "macroeconomic", "gdp_real_growth_pct", "trend")
    infl_trend = safe_get(data, "macroeconomic", "inflation_cpi_pct", "trend")
    pol_trend = get_value(data, "derived", "political_stability_trend")
    nuclear_status = get_value(data, "military", "nuclear", "status")
    sanctions = get_value(data, "political", "sanctions_status")
    if sanctions is None:
        sanctions = get_value(data, "institutions", "political", "sanctions_status")

    # GDP growth value for context
    gdp_growth = get_value(data, "macroeconomic", "gdp_real_growth_pct")
    gdp_trend_reasoning = safe_get(data, "macroeconomic", "gdp_real_growth_pct", "trend_reasoning") or ""
    pol_trend_reasoning = safe_get(data, "derived", "political_stability_trend", "reasoning") or ""
    risk_trend = safe_get(data, "derived", "overall_investment_risk_score", "trend")

    # ══════════════════════════════════════════════════════════════════════
    # CRITICAL TRIGGERS
    # ══════════════════════════════════════════════════════════════════════

    # 1. Investment risk > 0.7
    if risk is not None and risk > 0.7:
        alerts.append(make_alert(
            "critical", cc,
            f"overall_investment_risk_score > 0.7 (actual: {risk:.3f})",
            f"{name}: Maximum investment risk at {risk:.3f}",
            f"{name}'s overall investment risk score reached {risk:.3f}, placing it in crisis territory. "
            f"Political risk premium: {prp} bps. "
            + (f"Inflation: {inflation:.1f}%. " if inflation else "")
            + (f"GDP growth trend: {gdp_trend}. " if gdp_trend else "")
            + (gdp_trend_reasoning[:200] if gdp_trend_reasoning else ""),
            ["derived.overall_investment_risk_score"],
            old_lookup
        ))

    # 2. Active conflict with high severity — check for war-related indicators
    #    Countries known to be in active high-intensity conflict based on data
    conflict_countries = {
        "IRN": ("US-Iran war Day 10+, Hormuz mined, Kurdish ground invasion, "
                "Tehran under sustained bombing. Supreme Leader killed. State approaching collapse."),
        "UKR": ("Russia-Ukraine war Year 5. Ukraine retaking territory. EU €90B transfer. "
                "CC/Ca credit rating. 34% of GDP on defense."),
        "MMR": ("Myanmar civil war continues. Military junta vs resistance forces. "
                "Economy in severe contraction. Humanitarian crisis."),
        "PAK": ("Pakistan declared war on Afghanistan. Airstrikes on Kabul and Kandahar. "
                "Nuclear-armed nation in active conflict. CCC+/Caa1 credit rating."),
        "ISR": ("Multi-front war: Iran strikes, Hezbollah escalation from Lebanon. "
                "International condemnation growing. GDP trend strong_decrease."),
    }
    if cc in conflict_countries:
        alerts.append(make_alert(
            "critical", cc,
            f"Active high-intensity conflict",
            f"{name}: Active military conflict — critical security risk",
            conflict_countries[cc],
            ["military.active_conflicts", "derived.overall_investment_risk_score",
             "political.political_stability_score"],
            old_lookup,
            first_triggered="2026-03-02T12:30:00Z" if cc in ("IRN", "UKR", "PAK", "ISR") else None
        ))

    # 3. Comprehensive sanctions
    if sanctions and "comprehensive" in str(sanctions).lower():
        alerts.append(make_alert(
            "critical", cc,
            f"Sanctions status: comprehensive",
            f"{name}: Under comprehensive international sanctions",
            f"{name} is subject to comprehensive international sanctions, severely limiting "
            f"investment opportunities and trade flows.",
            ["political.sanctions_status", "derived.market_accessibility_score"],
            old_lookup
        ))

    # ══════════════════════════════════════════════════════════════════════
    # WARNING TRIGGERS
    # ══════════════════════════════════════════════════════════════════════

    # 4. Investment risk > 0.5 (but <= 0.7, to avoid double-counting with critical)
    if risk is not None and 0.5 < risk <= 0.7:
        alerts.append(make_alert(
            "warning", cc,
            f"overall_investment_risk_score > 0.5 (actual: {risk:.3f})",
            f"{name}: Elevated investment risk at {risk:.3f}",
            f"{name}'s investment risk score of {risk:.3f} indicates elevated risk. "
            f"Political risk premium: {prp} bps. "
            + (f"Inflation: {inflation:.1f}%. " if inflation else "")
            + (f"GDP trend: {gdp_trend}. " if gdp_trend else ""),
            ["derived.overall_investment_risk_score"],
            old_lookup
        ))

    # 5. Political risk premium > 500 bps
    if prp is not None and prp > 500:
        sev = "critical" if prp > 2000 else ("warning" if prp > 500 else "watch")
        # Only add if not already captured by risk > 0.7
        if risk is None or risk <= 0.7:
            alerts.append(make_alert(
                sev, cc,
                f"political_risk_premium_bps > 500 (actual: {prp})",
                f"{name}: Political risk premium at {prp} bps",
                f"{name}'s political risk premium of {prp} basis points indicates significant "
                f"sovereign risk. Investment risk score: {risk}.",
                ["derived.political_risk_premium_bps"],
                old_lookup
            ))

    # 6. Inflation > 50%
    if inflation is not None and inflation > 50:
        alerts.append(make_alert(
            "warning", cc,
            f"Inflation > 50% (actual: {inflation:.1f}%)",
            f"{name}: Hyperinflation territory at {inflation:.1f}%",
            f"{name}'s CPI inflation of {inflation:.1f}% exceeds the hyperinflation threshold. "
            + (f"Trend: {infl_trend}. " if infl_trend else ""),
            ["macroeconomic.inflation_cpi_pct"],
            old_lookup
        ))

    # 7. GDP growth trend = strong_decrease
    if gdp_trend == "strong_decrease":
        alerts.append(make_alert(
            "warning", cc,
            f"GDP growth trend: strong_decrease",
            f"{name}: GDP growth in sharp decline",
            f"{name}'s GDP growth trend is 'strong_decrease'. "
            + (f"Current growth: {gdp_growth:.1f}%. " if gdp_growth is not None else "")
            + (gdp_trend_reasoning[:250] if gdp_trend_reasoning else ""),
            ["macroeconomic.gdp_real_growth_pct"],
            old_lookup
        ))

    # 8. Political stability trend = strong_decrease
    if pol_trend == "strong_decrease":
        alerts.append(make_alert(
            "warning", cc,
            f"Political stability trend: strong_decrease",
            f"{name}: Political stability in sharp decline",
            pol_trend_reasoning[:300] if pol_trend_reasoning else
            f"{name}'s political stability trend is 'strong_decrease', indicating severe institutional stress.",
            ["derived.political_stability_trend", "political.political_stability_score"],
            old_lookup
        ))

    # ══════════════════════════════════════════════════════════════════════
    # WATCH TRIGGERS
    # ══════════════════════════════════════════════════════════════════════

    # 9. Chokepoint exposure > 0.7
    if chokepoint is not None and chokepoint > 0.7:
        sev = "critical" if chokepoint > 0.9 else ("warning" if chokepoint > 0.8 else "watch")
        # For Gulf states with very high exposure during Hormuz crisis, escalate
        if cc in ("KWT", "QAT", "ARE", "SAU", "OMN", "IRQ", "SGP"):
            if sev == "watch":
                sev = "warning"
        alerts.append(make_alert(
            sev, cc,
            f"Supply chain chokepoint exposure > 0.7 (actual: {chokepoint:.3f})",
            f"{name}: Extreme chokepoint exposure at {chokepoint:.3f} amid Hormuz crisis",
            f"{name} has a supply chain chokepoint exposure of {chokepoint:.3f}, critically "
            f"elevated during the Strait of Hormuz crisis. "
            + (f"GDP trend: {gdp_trend}. " if gdp_trend else "")
            + (f"Investment risk: {risk}." if risk else ""),
            ["derived.supply_chain_chokepoint_exposure"],
            old_lookup
        ))

    # 10. Elevated inflation (> 20% but <= 50% — below hyperinflation threshold)
    if inflation is not None and 20 < inflation <= 50:
        alerts.append(make_alert(
            "watch", cc,
            f"Inflation elevated (actual: {inflation:.1f}%)",
            f"{name}: High inflation at {inflation:.1f}%",
            f"{name}'s CPI inflation of {inflation:.1f}% is significantly elevated. "
            + (f"Trend: {infl_trend}. " if infl_trend else ""),
            ["macroeconomic.inflation_cpi_pct"],
            old_lookup
        ))

    # 11. Investment risk 0.4-0.5 — elevated watch
    if risk is not None and 0.4 <= risk <= 0.5:
        alerts.append(make_alert(
            "watch", cc,
            f"Investment risk approaching warning threshold (actual: {risk:.3f})",
            f"{name}: Investment risk at {risk:.3f} — approaching elevated territory",
            f"{name}'s investment risk score of {risk:.3f} is nearing the warning threshold of 0.5. "
            f"Political risk premium: {prp} bps.",
            ["derived.overall_investment_risk_score"],
            old_lookup
        ))

    # 12. GDP trend = decrease with other stress signals
    if gdp_trend == "decrease" and risk is not None and risk > 0.25:
        alerts.append(make_alert(
            "watch", cc,
            f"GDP growth declining with elevated risk (risk: {risk:.3f})",
            f"{name}: GDP declining with investment risk at {risk:.3f}",
            f"{name} shows GDP growth trend of 'decrease' combined with an investment risk "
            f"score of {risk:.3f}. "
            + (gdp_trend_reasoning[:200] if gdp_trend_reasoning else ""),
            ["macroeconomic.gdp_real_growth_pct", "derived.overall_investment_risk_score"],
            old_lookup
        ))

    # 13. Political stability decrease (not strong_decrease, which is handled above)
    if pol_trend == "decrease":
        alerts.append(make_alert(
            "watch", cc,
            f"Political stability trend: decrease",
            f"{name}: Political stability declining",
            pol_trend_reasoning[:300] if pol_trend_reasoning else
            f"{name}'s political stability shows a declining trend.",
            ["derived.political_stability_trend"],
            old_lookup
        ))

    return alerts


def generate_specific_context_alerts(countries, old_lookup):
    """Generate alerts for specific current-events situations that
    span multiple countries or need manual context enrichment."""
    alerts = []

    # ── Gulf Hormuz exposure alerts for states that may not trip generic thresholds ──
    hormuz_states = {
        "KWT": ("Kuwait faces near-total economic paralysis from Hormuz closure with 93.8% "
                "chokepoint exposure — highest of all tracked countries. No pipeline alternative. "
                "Ali Al Salem Air Base struck by IRGC. GDP trend: strong_decrease."),
        "QAT": ("Qatar — world's largest LNG exporter — completely offline due to Hormuz mines. "
                "91.6% chokepoint exposure. Al Udeid Air Base struck. North Field LNG expansion "
                "timeline at risk. GDP trend: strong_decrease."),
        "ARE": ("UAE under direct Iranian missile attacks on Al Dhafra base and cities. 100% "
                "chokepoint exposure. Aviation disrupted with 7,700+ delays. Dubai financial hub "
                "operations stressed. GDP trend: strong_decrease."),
        "SAU": ("Saudi Arabia exposed to Hormuz closure with 80.9% chokepoint exposure. IRGC "
                "attacks on regional US bases. Political stability declining. GDP trend: "
                "strong_decrease despite oil price surge — cannot export through Hormuz."),
        "OMN": ("Oman critically exposed with 85% chokepoint exposure. Direct proximity to "
                "Hormuz mine-laying. Oil exports severely disrupted. GDP trend: decrease."),
        "IRQ": ("Iraq exposed with 79.1% chokepoint exposure. Oil export disruption threatens "
                "fiscal position. Kurdish invasion of Iran from Iraq Kurdistan complicates "
                "sovereignty. GDP trend: strong_decrease."),
    }
    for cc, details in hormuz_states.items():
        if cc in countries:
            data = countries[cc]
            risk = get_value(data, "derived", "overall_investment_risk_score")
            chokepoint = get_value(data, "derived", "supply_chain_chokepoint_exposure")
            alerts.append(make_alert(
                "warning" if cc not in ("KWT", "QAT", "ARE") else "critical",
                cc,
                f"Hormuz crisis — direct impact ({chokepoint:.3f} chokepoint exposure)",
                f"{data.get('country_name', cc)}: Hormuz crisis direct impact",
                details,
                ["derived.supply_chain_chokepoint_exposure", "macroeconomic.gdp_real_growth_pct",
                 "macroeconomic.current_account_pct_gdp"],
                old_lookup,
                first_triggered="2026-03-02T12:30:00Z"
            ))

    # ── Russia sanctions + elevated risk ──
    if "RUS" in countries:
        rus = countries["RUS"]
        risk = get_value(rus, "derived", "overall_investment_risk_score")
        prp = get_value(rus, "derived", "political_risk_premium_bps")
        alerts.append(make_alert(
            "warning", "RUS",
            f"Sanctions + elevated risk (risk: {risk}, PRP: {prp} bps)",
            "Russia: Comprehensive sanctions with elevated investment risk",
            f"Russia remains under comprehensive Western sanctions with investment risk at {risk} "
            f"and political risk premium at {prp} bps. Caught conducting ship-to-ship oil transfers "
            f"in Gulf of Oman. US warned of consequences if Russia providing intelligence to Iran. "
            f"Ukraine war continues in Year 5.",
            ["derived.overall_investment_risk_score", "political.sanctions_status",
             "military.active_conflicts"],
            old_lookup,
            first_triggered="2026-03-02T12:30:00Z"
        ))

    # ── European energy/economic stress ──
    for cc in ("DEU", "FRA", "ITA"):
        if cc in countries:
            data = countries[cc]
            name = data.get("country_name", cc)
            risk = get_value(data, "derived", "overall_investment_risk_score")
            gdp_trend = safe_get(data, "macroeconomic", "gdp_real_growth_pct", "trend")
            extra = ""
            if cc == "DEU":
                extra = ("VW slashing 50,000 jobs — largest German auto layoff ever. "
                         "EU admits 'nuclear blunder' on energy policy. European markets "
                         "crashed ~6%.")
            elif cc == "FRA":
                extra = ("Macron vows to protect Lebanon. EU leaders split on Iran war. "
                         "European defense burden growing.")
            elif cc == "ITA":
                extra = ("EU protests Russia's Venice Biennale return. European energy "
                         "vulnerability acute. GDP trend: decrease.")
            alerts.append(make_alert(
                "watch", cc,
                f"European energy crisis / Hormuz impact (GDP trend: {gdp_trend})",
                f"{name}: European energy crisis from Hormuz closure",
                f"{name} faces economic headwinds from the oil price surge to $116.50/bbl "
                f"driven by Hormuz closure. GDP trend: {gdp_trend}. Investment risk: {risk}. "
                + extra,
                ["macroeconomic.gdp_real_growth_pct", "macroeconomic.inflation_cpi_pct"],
                old_lookup
            ))

    # ── Argentina recession + reform volatility ──
    if "ARG" in countries:
        arg = countries["ARG"]
        inflation = get_value(arg, "macroeconomic", "inflation_cpi_pct")
        risk = get_value(arg, "derived", "overall_investment_risk_score")
        alerts.append(make_alert(
            "watch", "ARG",
            f"Recession + reform volatility (inflation: {inflation:.1f}%)",
            "Argentina: Recession with hyperinflation legacy — Milei reforms tested",
            f"Argentina in recession (GDP trend: decrease) with CPI still at {inflation:.1f}% "
            f"despite disinflation progress. Milei courting Wall Street, citing net energy exports "
            f"from Vaca Muerta. Investment risk: {risk}. Argentina emerging as energy crisis "
            f"beneficiary but structural reform path remains volatile.",
            ["macroeconomic.gdp_real_growth_pct", "macroeconomic.inflation_cpi_pct",
             "derived.overall_investment_risk_score"],
            old_lookup
        ))

    # ── Turkey disinflation but still high ──
    if "TUR" in countries:
        tur = countries["TUR"]
        inflation = get_value(tur, "macroeconomic", "inflation_cpi_pct")
        risk = get_value(tur, "derived", "overall_investment_risk_score")
        prp = get_value(tur, "derived", "political_risk_premium_bps")
        alerts.append(make_alert(
            "watch", "TUR",
            f"High inflation + declining GDP (inflation: {inflation:.1f}%)",
            "Turkey: Inflation at 58.5% with GDP declining",
            f"Turkey's CPI inflation remains at {inflation:.1f}% with GDP growth trend declining. "
            f"Investment risk: {risk}. Political risk premium: {prp} bps. "
            f"OTS foreign ministers meeting tests Turkic coordination amid Iran crisis. "
            f"Turkey navigates between NATO and regional relationships.",
            ["macroeconomic.inflation_cpi_pct", "macroeconomic.gdp_real_growth_pct",
             "derived.political_risk_premium_bps"],
            old_lookup
        ))

    # ── US — war costs, tariff crisis, recession warnings ──
    if "USA" in countries:
        usa = countries["USA"]
        risk = get_value(usa, "derived", "overall_investment_risk_score")
        pol_trend = get_value(usa, "derived", "political_stability_trend")
        alerts.append(make_alert(
            "watch", "USA",
            f"War escalation + tariff crisis + recession warnings",
            "USA: Iran war costs + SCOTUS tariff crisis + 5 recession warning signs",
            f"US faces convergent risks: Iran war entering 'most intense phase' with boots on "
            f"ground 'not ruled out'; $175B tariff refund liability from SCOTUS ruling; "
            f"Dow fell 800+ points; leveraged basis trade ($1T+) unwinding; 5 recession "
            f"warning signs identified. DHS Secretary fired mid-war. Midterm mood favoring "
            f"Democrats. Political stability trend: {pol_trend}. Risk: {risk}.",
            ["macroeconomic.gdp_real_growth_pct", "derived.political_stability_trend",
             "macroeconomic.inflation_cpi_pct"],
            old_lookup
        ))

    # ── India — Gulf exposure ──
    if "IND" in countries:
        ind = countries["IND"]
        risk = get_value(ind, "derived", "overall_investment_risk_score")
        chokepoint = get_value(ind, "derived", "supply_chain_chokepoint_exposure")
        alerts.append(make_alert(
            "watch", "IND",
            f"Gulf economic exposure — remittances, energy, trade (chokepoint: {chokepoint})",
            "India: Gulf crisis threatens remittances, energy imports, and trade",
            f"India faces cascading Middle East war impact: $346cr export cargo stranded at "
            f"Kandla/Mundra ports, $100B+ annual GCC remittances at risk, banking sector Gulf "
            f"exposure. Oil import costs surging at $116/bbl. Chokepoint exposure: {chokepoint}. "
            f"GDP trend: decrease. Easing Chinese investment curbs signals strategic recalibration.",
            ["macroeconomic.current_account_pct_gdp", "macroeconomic.inflation_cpi_pct",
             "derived.supply_chain_chokepoint_exposure"],
            old_lookup
        ))

    # ── Japan / South Korea — energy vulnerability ──
    for cc in ("JPN", "KOR"):
        if cc in countries:
            data = countries[cc]
            name = data.get("country_name", cc)
            chokepoint = get_value(data, "derived", "supply_chain_chokepoint_exposure")
            gdp_trend = safe_get(data, "macroeconomic", "gdp_real_growth_pct", "trend")
            alerts.append(make_alert(
                "watch", cc,
                f"Energy vulnerability — Hormuz dependency (chokepoint: {chokepoint})",
                f"{name}: Acute energy vulnerability from Hormuz closure",
                f"{name} faces acute energy security crisis with chokepoint exposure of "
                f"{chokepoint}. Heavy dependence on Gulf oil transiting Hormuz. GDP trend: "
                f"{gdp_trend}. SPR drawdown being activated. Asian LNG prices surging.",
                ["derived.supply_chain_chokepoint_exposure", "macroeconomic.gdp_real_growth_pct"],
                old_lookup
            ))

    # ── Ethiopia — default + conflict ──
    if "ETH" in countries:
        eth = countries["ETH"]
        risk = get_value(eth, "derived", "overall_investment_risk_score")
        prp = get_value(eth, "derived", "political_risk_premium_bps")
        alerts.append(make_alert(
            "critical", "ETH",
            f"Sovereign default + conflict resumption (PRP: {prp} bps)",
            "Ethiopia: Selective default with Tigray conflict resumption",
            f"Ethiopia's sovereign credit at SD/Ca/RD (selective default) with political "
            f"risk premium of {prp} bps. TPLF-government clashes resumed. Elections June 1, "
            f"2026. Investment risk: {risk}.",
            ["macroeconomic.sovereign_credit_rating", "military.active_conflicts",
             "derived.political_risk_premium_bps"],
            old_lookup,
            first_triggered="2026-03-02T12:30:00Z"
        ))

    # ── EGY — elevated risk ──
    if "EGY" in countries:
        egy = countries["EGY"]
        risk = get_value(egy, "derived", "overall_investment_risk_score")
        inflation = get_value(egy, "macroeconomic", "inflation_cpi_pct")
        prp = get_value(egy, "derived", "political_risk_premium_bps")
        alerts.append(make_alert(
            "warning", "EGY",
            f"Elevated risk + high inflation (risk: {risk}, inflation: {inflation:.1f}%)",
            "Egypt: Elevated investment risk with high inflation",
            f"Egypt's investment risk at {risk} with CPI inflation at {inflation:.1f}%. "
            f"Political risk premium: {prp} bps. Suez Canal volumes affected by Hormuz-adjacent "
            f"disruptions. GDP trend: decrease. Oil import costs surging.",
            ["derived.overall_investment_risk_score", "macroeconomic.inflation_cpi_pct"],
            old_lookup
        ))

    # ── Mexico — El Mencho killed ──
    if "MEX" in countries:
        alerts.append(make_alert(
            "watch", "MEX",
            "Major cartel leader killed — CJNG power vacuum risk",
            "Mexico: CJNG leader El Mencho killed — short-term violence risk",
            "Mexican military killed CJNG cartel leader El Mencho. Major security milestone "
            "but CJNG power vacuum could trigger cartel violence in short term. Long-term "
            "positive for security environment and US-Mexico relations.",
            ["political.civil_unrest_level", "military.active_conflicts"],
            old_lookup
        ))

    # ── Colombia — Petro coalition strengthens ──
    if "COL" in countries:
        alerts.append(make_alert(
            "watch", "COL",
            "Petro coalition wins congressional elections — reform agenda strengthened",
            "Colombia: Petro's leftist coalition tops congressional elections",
            "President Petro's Pacto Historico won most seats in Colombia's congressional "
            "elections, strengthening his reform mandate on land reform, taxes, and energy "
            "transition. Conservative Paloma Valencia surges in 2026 presidential race.",
            ["institutions.political.governing_coalition_stability"],
            old_lookup
        ))

    # ── Asian chokepoint exposure (SGP, MYS, TWN, VNM, THA) ──
    for cc in ("SGP", "TWN", "VNM", "MYS", "THA"):
        if cc in countries:
            data = countries[cc]
            name = data.get("country_name", cc)
            chokepoint = get_value(data, "derived", "supply_chain_chokepoint_exposure")
            if chokepoint and chokepoint > 0.6:
                gdp_trend = safe_get(data, "macroeconomic", "gdp_real_growth_pct", "trend")
                alerts.append(make_alert(
                    "watch", cc,
                    f"Elevated chokepoint exposure (actual: {chokepoint:.3f})",
                    f"{name}: Chokepoint exposure at {chokepoint:.3f} amid global shipping disruption",
                    f"{name} has elevated supply chain chokepoint exposure of {chokepoint:.3f} "
                    f"during the global shipping disruption from Hormuz closure. GDP trend: {gdp_trend}.",
                    ["derived.supply_chain_chokepoint_exposure"],
                    old_lookup
                ))

    return alerts


# ── Event Feed Generation ────────────────────────────────────────────────────

def generate_event_feed(news_events, alerts, countries):
    """Select top 25-30 most significant events for the feed."""
    events = []
    event_counter = 0

    # Severity mapping for news events
    severity_map = {
        "transformative": "critical",
        "major": "warning",
        "moderate": "watch",
        "minor": "watch"
    }

    # Category mapping
    category_map = {
        "conflict": "military_conflict",
        "chokepoint_disruption": "trade_disruption",
        "economic_crisis": "economic_crisis",
        "policy_change": "political_regulatory",
        "sanctions_evasion": "trade_sanctions",
        "diplomatic": "diplomatic",
        "trade_dispute": "trade_sanctions",
        "market_event": "market_event",
        "leadership_change": "political_regulatory",
        "election_held": "political_regulatory",
        "security": "security",
        "judicial": "political_regulatory",
        "military_deployment": "military_conflict",
    }

    # Sort news by severity (transformative first)
    severity_order = {"transformative": 0, "major": 1, "moderate": 2, "minor": 3}
    sorted_news = sorted(news_events,
                         key=lambda e: (severity_order.get(e.get("severity", "minor"), 3),
                                        -e.get("confidence", 0)))

    # Take top 30
    for evt in sorted_news[:30]:
        event_counter += 1
        events.append({
            "event_id": f"feed_{event_counter:03d}",
            "timestamp": f"{evt.get('date', DATE)}T00:00:00Z",
            "severity": severity_map.get(evt.get("severity", "moderate"), "watch"),
            "countries": evt.get("countries_involved", []),
            "headline": evt.get("headline", ""),
            "summary": evt.get("summary", "")[:300],
            "category": category_map.get(evt.get("event_type", ""), "other"),
            "source_event_id": evt.get("event_id", ""),
            "confidence": evt.get("confidence", 0.7)
        })

    return events


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("Agent 12 — Alert Generator")
    print(f"Run ID: {RUN_ID} | Date: {DATE}")
    print()

    # Load inputs
    print("Loading country data...")
    countries = load_countries()
    print(f"  Loaded {len(countries)} countries")

    print("Loading previous alerts...")
    old_data, old_lookup = load_old_alerts()
    if old_data:
        print(f"  Found {old_data['summary']['total_active']} existing alerts from {old_data.get('run_id', '?')}")
    else:
        print("  No previous alerts found")

    print("Loading trend estimates...")
    trends = load_trends()
    print(f"  Loaded {len(trends)} trend estimates")

    print("Loading news events...")
    news_events = load_news()
    print(f"  Loaded {len(news_events)} news events")

    # Index news by country
    news_by_country = {}
    for evt in news_events:
        for cc in evt.get("countries_involved", []):
            news_by_country.setdefault(cc, []).append(evt)

    # ── Scan all countries ──
    print("\nScanning countries for alert triggers...")
    all_alerts = []
    for cc, data in sorted(countries.items()):
        country_alerts = scan_country(cc, data, trends, old_lookup, news_by_country)
        all_alerts.extend(country_alerts)

    # ── Add context-specific alerts ──
    print("Adding context-specific alerts...")
    context_alerts = generate_specific_context_alerts(countries, old_lookup)
    all_alerts.extend(context_alerts)

    # ── Deduplicate alerts by (country_code, trigger prefix) ──
    seen = set()
    deduped = []
    for a in all_alerts:
        key = (a["country_code"], a["trigger"][:80])
        if key not in seen:
            seen.add(key)
            deduped.append(a)
    all_alerts = deduped

    # ── Reassign sequential IDs ──
    global alert_counter
    alert_counter = 0
    for a in all_alerts:
        alert_counter += 1
        a["alert_id"] = f"alert_{DATE}_{alert_counter:03d}"

    # ── Count by severity ──
    counts = {"critical": 0, "warning": 0, "watch": 0}
    for a in all_alerts:
        counts[a["severity"]] = counts.get(a["severity"], 0) + 1

    total = sum(counts.values())

    print(f"\n{'='*60}")
    print(f"ALERT SUMMARY — {RUN_ID}")
    print(f"{'='*60}")
    print(f"  Critical: {counts['critical']}")
    print(f"  Warning:  {counts['warning']}")
    print(f"  Watch:    {counts['watch']}")
    print(f"  Total:    {total}")
    print(f"{'='*60}")

    # Print all critical alerts
    print("\nCRITICAL ALERTS:")
    for a in all_alerts:
        if a["severity"] == "critical":
            print(f"  [{a['country_code']}] {a['headline']}")

    print("\nWARNING ALERTS:")
    for a in all_alerts:
        if a["severity"] == "warning":
            print(f"  [{a['country_code']}] {a['headline']}")

    print("\nWATCH ALERTS:")
    for a in all_alerts:
        if a["severity"] == "watch":
            print(f"  [{a['country_code']}] {a['headline']}")

    # ── Write alert_index.json ──
    alert_index = {
        "last_updated": TIMESTAMP,
        "run_id": RUN_ID,
        "summary": {
            "critical": counts["critical"],
            "warning": counts["warning"],
            "watch": counts["watch"],
            "total_active": total
        },
        "alerts": all_alerts
    }

    os.makedirs(INDICES_DIR, exist_ok=True)
    alert_path = os.path.join(INDICES_DIR, "alert_index.json")
    with open(alert_path, "w") as f:
        json.dump(alert_index, f, indent=2)
    print(f"\nWrote {alert_path}")

    # ── Generate event feed ──
    print("\nGenerating event feed...")
    events = generate_event_feed(news_events, all_alerts, countries)

    event_feed = {
        "last_updated": TIMESTAMP,
        "run_id": RUN_ID,
        "total_events": len(events),
        "events": events
    }

    os.makedirs(GLOBAL_DIR, exist_ok=True)
    feed_path = os.path.join(GLOBAL_DIR, "event_feed.json")
    with open(feed_path, "w") as f:
        json.dump(event_feed, f, indent=2)
    print(f"Wrote {feed_path} ({len(events)} events)")

    print(f"\nAgent 12 complete.")


if __name__ == "__main__":
    main()
