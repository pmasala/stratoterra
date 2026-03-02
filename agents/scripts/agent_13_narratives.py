#!/usr/bin/env python3
"""
Agent 13: Country Profile Synthesizer
Run ID: 2026-W10, Date: 2026-03-02

Generates investor-focused narrative summaries for each country.
Updates the narrative section of each country file with:
- executive_summary
- key_changes_this_week
- outlook
- investor_implications
- data_quality_note

Tier 1 (30 countries): Detailed narratives
Tier 2 (25 countries): Moderate detail
Tier 3 (20 countries): Brief summaries
"""

import json
import os
import sys
from datetime import datetime

BASE = "/home/pietro/stratoterra"
DATA_DIR = f"{BASE}/data/countries"
TRENDS_FILE = f"{BASE}/staging/trends/trend_estimates_2026-03-02.json"
ALERTS_FILE = f"{BASE}/data/indices/alert_index.json"
COUNTRY_LIST_FILE = f"{BASE}/data/indices/country_list.json"

RUN_ID = "2026-W10"
GENERATED_AT = "2026-03-02T18:00:00Z"


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def get_country_trends(trends_data, code):
    """Extract all trend estimates for a given country code."""
    return [e for e in trends_data.get("estimates", []) if e.get("country_code") == code]


def get_country_alerts(alerts_data, code):
    """Extract all alerts for a given country code."""
    result = []
    for alert in alerts_data.get("alerts", []):
        if alert.get("country_code") == code or code in alert.get("countries", []):
            result.append(alert)
    return result


def get_macro_value(country_data, key, default=None):
    """Safely extract a macroeconomic value."""
    macro = country_data.get("macroeconomic", {})
    field = macro.get(key, {})
    if isinstance(field, dict):
        return field.get("value", default)
    return default


def get_derived_value(country_data, key, default=None):
    """Safely extract a derived value."""
    derived = country_data.get("derived", {})
    field = derived.get(key, {})
    if isinstance(field, dict):
        return field.get("value", default)
    return default


def get_layers_value(country_data, layer, key, default=None):
    """Safely extract a value from layers."""
    layers = country_data.get("layers", {})
    layer_data = layers.get(layer, {})
    if isinstance(layer_data, dict):
        val = layer_data.get(key, default)
        return val
    return default


def fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val}%"


def fmt_usd_b(val):
    if val is None:
        return "N/A"
    return f"${val/1e9:.1f}B"


def summarize_trends(trends):
    """Create a compact summary of trend directions."""
    summary = {}
    for t in trends:
        factor = t.get("factor_path", "")
        short = factor.split(".")[-1] if "." in factor else factor
        summary[short] = {
            "trend": t.get("trend", "N/A"),
            "confidence": t.get("confidence", 0),
            "reasoning": t.get("reasoning", ""),
            "investor_implication": t.get("investor_implication", ""),
            "current_value": t.get("current_value")
        }
    return summary


# ============================================================
# NARRATIVE GENERATORS PER COUNTRY
# These are organized by country code for high-impact countries,
# with fallback generators for tier-based processing.
# ============================================================

KEY_EVENTS = {
    "iran_strikes": "US-Israeli Operation Epic Fury struck 1,000+ targets in Iran on Feb 28, killing Supreme Leader Khamenei.",
    "hormuz_closure": "Strait of Hormuz effectively closed to commercial shipping following IRGC retaliation on Mar 1.",
    "irgc_retaliation": "IRGC retaliated against 27 US bases across Gulf region on Mar 1.",
    "scotus_ieepa": "US Supreme Court struck down IEEPA tariffs 6-3 on Feb 20; Trump imposed Section 122 tariffs.",
    "china_japan_sanctions": "China sanctioned 50 Japanese companies with rare earth export controls on Feb 25.",
    "pakistan_war": "Pakistan declared open war on Afghanistan on Feb 27 with airstrikes on Kabul and Kandahar.",
    "argentina_reform": "Argentina Senate approved landmark labor reform (42-28 vote) on Feb 27.",
    "korea_yoon": "South Korea sentenced ex-President Yoon to life for insurrection on Feb 19.",
    "indonesia_deal": "US-Indonesia signed $33 billion trade agreement on Feb 19.",
    "hezbollah_ceasefire": "Hezbollah broke November 2024 ceasefire, firing rockets at northern Israel on Mar 1.",
    "gold_surge": "Gold surged past $5,300/oz amid global market turmoil.",
    "thailand_pm": "Thailand PM Anutin formed coalition government on Feb 13.",
}


def generate_narrative_usa(country_data, trends, alerts):
    ts = summarize_trends(trends)
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The US faces a convergence of military, trade, and constitutional crises this week. "
            "Operation Epic Fury struck 1,000+ targets in Iran, killing Supreme Leader Khamenei -- the largest US military operation since Iraq 2003. "
            "Three US soldiers were killed in IRGC retaliation at Kuwait. The Strait of Hormuz closure sent oil prices surging and Dow futures dropped 517 points. "
            "Simultaneously, the SCOTUS struck down IEEPA tariffs 6-3, forcing a pivot to Section 122 with 10-15% global tariffs for 150 days. "
            "Additional tariffs on China (20% cumulative) and Canada/Mexico (25%) take effect March 4. "
            "Recession probability jumped from 25-30% to 40-50%. The Fed holds at 3.50-3.75% with stagflation risk constraining future rate cuts."
        ),
        "key_changes_this_week": [
            "US-Israeli strikes hit 1,000+ Iran targets; 3 US soldiers killed in Kuwait; IRGC retaliates against 27 US bases (Feb 28-Mar 1, transformative)",
            "SCOTUS struck down IEEPA tariffs 6-3; Trump pivoted to Section 122 with 15% global tariff (Feb 20, transformative)",
            "Strait of Hormuz effectively closed; oil prices surge to $80-90+ range; gold past $5,300/oz (Mar 1)",
            "Additional 10% China tariff (20% total) and 25% Canada/Mexico tariffs effective March 4",
            "Recession probability surged from 25-30% to 40-50%; S&P 500 posted largest monthly decline in a year",
            "New START treaty expired without extension; global nuclear arms control framework collapsed"
        ],
        "outlook": (
            "The US faces a potential stagflation scenario: oil price shock from Hormuz disruption pushes inflation higher while recession probability rises on trade disruption and consumer confidence deterioration. "
            "The constitutional crisis over trade policy creates legal uncertainty for hundreds of billions in tariff collections, with companies suing for $134B+ in refunds. "
            "March FOMC (17-18) is a key decision point -- the Fed faces a dilemma between supporting growth and containing inflation. "
            "Trump-Xi summit planned for March 30 could either escalate or de-escalate China trade tensions. "
            "Iran military operations continue with no ceasefire in sight, adding persistent defense spending and oil supply risk."
        ),
        "investor_implications": (
            "Defensive positioning warranted: overweight Treasuries (10Y at 3.96%), gold ($5,300+), energy, and defense contractors (Lockheed, Raytheon, Northrop). "
            "Underweight consumer discretionary, airlines, and trade-exposed manufacturers. "
            "The $200B+ tariff refund question creates contingent fiscal liability. "
            "Monitor VIX at Monday open and March FOMC for rate path signals. "
            "Section 122 tariffs limited to 150 days create a policy cliff in July that will require resolution."
        ),
        "data_quality_note": "US macro data is high quality (confidence 0.85-0.95). Recession probability estimates are analyst consensus, not official forecasts. Market data is pre-Monday-open and may shift significantly."
    }


def generate_narrative_chn(country_data, trends, alerts):
    ts = summarize_trends(trends)
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "China faces mounting pressure on multiple fronts this week. GDP growth decelerating from 4.8% to 4.2% forecast amid US tariff escalation to 20% cumulative. "
            "In a sharp escalation, China sanctioned 50 Japanese companies and imposed rare earth export controls on Feb 25 in response to PM Takaichi's Taiwan defense comments -- the worst China-Japan bilateral moment in decades. "
            "CPI at 0% signals persistent deflation risk. NPC opens March 5 with economic targets and stimulus signals expected. "
            "China positioned as neutral on Iran conflict but called UNSC emergency session. "
            "PBOC cut FX forward reserve ratio from 20% to 0% to manage yuan."
        ),
        "key_changes_this_week": [
            "China sanctioned 50 Japanese companies with rare earth export controls and dual-use goods restrictions (Feb 25, major)",
            "US imposed additional 10% tariff on China (20% total) effective March 4 (major)",
            "PBOC cut FX forward reserve ratio from 20% to 0% to slow yuan appreciation (moderate)",
            "NPC opens March 5 -- annual economic growth targets and stimulus measures expected",
            "China called UNSC emergency session over Iran strikes; positioned as neutral mediator",
            "CPI at 0% with deflation risk persisting; property sector weak"
        ],
        "outlook": (
            "China's growth trajectory is modestly decelerating but manageable through fiscal stimulus. "
            "The Japan sanctions escalation opens a new front in China's geopolitical confrontation that could fragment East Asian supply chains. "
            "NPC announcements March 5 will set policy tone -- expect a GDP target of 4.5-5.0% with fiscal expansion. "
            "The Hormuz crisis provides China leverage as an alternative energy partner for Iran but also raises import costs. "
            "Trump-Xi summit March 30 is the key bilateral event to watch."
        ),
        "investor_implications": (
            "Chinese equities face cross-currents: tariff headwinds vs potential NPC stimulus announcements. "
            "CNY management signals tolerance for modest depreciation. "
            "Japan-China sanctions create winners (domestic rare earth substitution plays) and losers (Japan-dependent supply chains). "
            "Monitor semiconductor sector for tech decoupling escalation. "
            "Defensive positioning in stimulus-linked sectors (infrastructure, SOEs) over private consumer-facing firms."
        ),
        "data_quality_note": "China macro data carries standard reliability caveats. CPI and GDP figures from IMF/World Bank. PBOC actions officially confirmed. Japan sanctions details confirmed by both governments."
    }


def generate_narrative_jpn(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Japan faces a dual shock this week: energy vulnerability and a severe deterioration in China relations. "
            "China sanctioned 50 Japanese companies with rare earth export controls on Feb 25 following PM Takaichi's Taiwan defense comments -- the worst bilateral moment in decades. "
            "Japan's energy independence at only 10% makes it acutely exposed to the Hormuz closure and oil price surge. "
            "The LDP supermajority from the Feb 8 snap election enables constitutional revision and defense spending at a record $58B. "
            "GDP trend is decreasing as manufacturing faces supply chain disruption."
        ),
        "key_changes_this_week": [
            "China sanctioned 50 Japanese companies with rare earth export controls (Feb 25, major)",
            "Strait of Hormuz closure critically threatens energy imports (energy independence: 10%) (Mar 1)",
            "LDP supermajority from Feb 8 snap election enables constitutional revision agenda",
            "Defense spending at strong_growth trajectory reaching $58B",
            "Japan-China relations at worst point in decades; Tokyo issued formal protest",
            "GDP trend shifting to decrease amid supply chain disruption"
        ],
        "outlook": (
            "Japan's near-term outlook is challenged by the convergence of energy vulnerability and China-Japan geopolitical deterioration. "
            "The rare earth export controls threaten high-tech manufacturing supply chains that could take 12-18 months to diversify. "
            "The defense spending increase and constitutional revision agenda signal a structural shift in Japan's security posture. "
            "BOJ policy normalization may slow if growth headwinds intensify. "
            "Resolution of China-Japan tensions depends on whether sanctions remain retaliatory or become structural."
        ),
        "investor_implications": (
            "Japanese equities face headwinds from energy costs and China supply chain disruption. "
            "Defense and domestic rare earth substitution stocks are direct beneficiaries. "
            "Yen may weaken on terms-of-trade deterioration from oil prices. "
            "Avoid Japan-China exposed manufacturing (autos, electronics) until sanctions scope clarifies. "
            "JGB yields may be capped if BOJ delays tightening on growth concerns."
        ),
        "data_quality_note": "Japan macro data is high quality. Energy independence figure is well-established. China sanctions details confirmed by both governments. LDP election results are official."
    }


def generate_narrative_deu(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Germany's fragile recovery faces external headwinds from oil price surge and trade fragmentation risks. "
            "GDP at 0.2% with a growth trend to 0.9% forecast, but the Hormuz closure threatens energy costs (energy independence: 30%). "
            "China's sanctions on Japan and broader trade decoupling signals risk for Germany's export-dependent model. "
            "EU-US trade deal postponed amid tariff uncertainty. The EU-Mercosur Partnership Agreement provides a positive counterweight."
        ),
        "key_changes_this_week": [
            "Hormuz closure drives oil price surge; Germany energy independence at 30% (Mar 1)",
            "China-Japan sanctions escalation signals broader trade fragmentation risk for exporters",
            "EU-US trade deal postponed amid SCOTUS tariff ruling uncertainty",
            "EU-Mercosur Partnership Agreement signed -- largest FTA ever (Jan 17)",
            "GDP trend growth (0.2% to 0.9%) but fragile amid external shocks"
        ],
        "outlook": (
            "Germany's recovery trajectory depends on energy costs and trade stability. "
            "The oil price surge adds 0.2-0.4pp to inflation and compresses margins for energy-intensive manufacturers. "
            "China-Japan escalation is a warning signal for broader East Asian trade fragmentation that would hurt German auto and machinery exports. "
            "EU fiscal rules and defense spending requirements compete for fiscal space. "
            "The new Merz government's industrial policy will be tested by these cross-currents."
        ),
        "investor_implications": (
            "German equities sensitive to energy costs and China trade flows. "
            "Overweight defense-exposed firms benefiting from EU rearmament. "
            "Underweight auto sector on China-Japan contagion risk and trade fragmentation. "
            "Bund yields may compress on flight-to-safety flows. "
            "EUR/USD could face pressure if ECB signals concern over growth."
        ),
        "data_quality_note": "German macro data is high quality. Energy independence and trade data from official EU sources. GDP forecast reflects IMF projections."
    }


def generate_narrative_gbr(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The UK navigates the global crisis from a relatively insulated position. "
            "GDP growth at 1.3% with stable trend. Energy independence at 0.65 provides partial buffer against oil price surge. "
            "The UK's North Sea production benefits from higher oil prices. "
            "No direct tariff escalation with the US this week, providing relief versus Canada/Mexico/China. "
            "Inflation at 2.6% may tick higher on energy pass-through."
        ),
        "key_changes_this_week": [
            "Hormuz closure drives global oil price surge; UK partially buffered by North Sea production",
            "No direct US tariff escalation affecting UK this week",
            "Inflation at 2.6% may face upward pressure from energy costs",
            "UK joined UNSC discussions on Iran strikes; diplomatic positioning moderate"
        ],
        "outlook": (
            "The UK is relatively well-positioned compared to energy-dependent peers. "
            "North Sea revenues benefit from oil price surge while partial energy independence limits cost pass-through. "
            "BOE rate path may shift hawkish if energy-driven inflation persists. "
            "Trade diversification post-Brexit continues with no major US tariff threats in the near term."
        ),
        "investor_implications": (
            "UK energy sector (Shell, BP) benefits from oil price surge. "
            "Gilts may face modest pressure if BOE signals delayed cuts. "
            "FTSE 100 outperforms continental Europe on energy weighting. "
            "Sterling relatively stable; monitor for safe-haven flows."
        ),
        "data_quality_note": "UK macro data is high quality. Energy independence figure from official statistics."
    }


def generate_narrative_fra(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "France navigates geopolitical turbulence with GDP growth at 0.8% and stable trend. "
            "France called for a UNSC emergency session over Iran strikes, positioning itself as a multilateral voice. "
            "Nuclear energy provides energy independence advantage (0.5) relative to peers. "
            "EU-Mercosur agreement provides trade diversification. Inflation at 2.3% remains contained."
        ),
        "key_changes_this_week": [
            "France co-led UNSC emergency session call over Iran strikes (Mar 1)",
            "Hormuz closure adds energy cost pressure; nuclear advantage provides partial buffer",
            "EU-Mercosur Partnership Agreement signed (Jan 17) -- trade diversification positive",
            "GDP stable at 0.8% with contained inflation at 2.3%"
        ],
        "outlook": (
            "France's nuclear energy base provides structural advantage in the current oil shock. "
            "Diplomatic activism on Iran may enhance France's multilateral standing. "
            "EU defense spending increase benefits French defense industry (Thales, Dassault, MBDA). "
            "Fiscal consolidation remains a challenge with elevated debt levels."
        ),
        "investor_implications": (
            "French defense stocks benefit from EU rearmament and regional instability. "
            "Nuclear energy advantage limits inflation pass-through vs fossil-dependent peers. "
            "OAT-Bund spread stable; French fiscal trajectory under monitoring. "
            "CAC 40 resilient relative to energy-dependent indices."
        ),
        "data_quality_note": "French macro data is high quality from EU official sources."
    }


def generate_narrative_ind(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "India faces significant oil shock exposure as the largest economy most dependent on Gulf energy imports. "
            "Importing approximately 85% of its oil needs via Hormuz-affected routes, the closure threatens inflation (CPI trending from 2.8% to 4%) and the current account deficit. "
            "The rupee is under depreciation pressure at 91.42/USD. "
            "GDP trend is decreasing from 6.6% to 6.2% but India remains the fastest-growing major economy. "
            "Government faces a choice between fuel subsidies and fiscal consolidation."
        ),
        "key_changes_this_week": [
            "Hormuz closure critically threatens India's oil imports (85% import dependency) (Mar 1, major)",
            "CPI inflation trending from 2.8% to 4% on energy pass-through",
            "Rupee under depreciation pressure at 91.42/USD",
            "GDP trend decreasing from 6.6% to 6.2% forecast",
            "Current account deficit widening on higher oil import bill"
        ],
        "outlook": (
            "India's growth premium faces near-term compression from the oil shock. "
            "If Hormuz remains closed for more than 2-4 weeks, inflation could exceed 5% and force RBI to pause rate normalization. "
            "Fiscal impact of fuel subsidies could add 0.5-0.8% of GDP to the deficit. "
            "India's non-alignment diplomacy allows it to potentially source discounted Russian oil, providing partial offset. "
            "The medium-term structural growth story (demographics, digital infrastructure, manufacturing shift) remains intact."
        ),
        "investor_implications": (
            "Overweight Indian IT services (USD earners, energy-agnostic) and underweight energy-intensive industrials. "
            "INR hedge recommended given depreciation pressure. "
            "Indian government bonds face yield pressure on inflation and fiscal concerns. "
            "Monitor RBI statements for any emergency rate action. "
            "India remains a structural overweight but tactical caution warranted."
        ),
        "data_quality_note": "India macro data is moderate-to-high quality. Oil import dependency is well-documented. GDP and inflation figures from RBI and IMF sources."
    }


def generate_narrative_ita(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Italy faces moderate headwinds from the oil price surge with GDP at 0.6% and low energy independence. "
            "The Hormuz closure adds inflation pressure atop a fragile recovery. "
            "EU-Mercosur agreement provides trade diversification. "
            "Government debt at elevated levels constrains fiscal response to energy shock."
        ),
        "key_changes_this_week": [
            "Hormuz closure drives oil price surge; Italy energy-dependent (Mar 1)",
            "EU-Mercosur Partnership Agreement signed -- positive for trade (Jan 17)",
            "GDP at 0.6% with fragile recovery amid external headwinds"
        ],
        "outlook": (
            "Italy's recovery is the most vulnerable among major EU economies to an energy price shock. "
            "BTP-Bund spread may widen if growth falters. "
            "ECB rate cuts would support Italian sovereign debt dynamics. "
            "Structural reform momentum under Meloni provides positive backdrop if external shocks contained."
        ),
        "investor_implications": (
            "BTPs face spread widening risk if oil shock persists. "
            "Italian bank stocks sensitive to growth outlook and sovereign spread. "
            "Defense sector benefits from EU rearmament. "
            "Underweight Italian cyclicals exposed to energy costs."
        ),
        "data_quality_note": "Italian macro data is high quality from EU/ECB sources."
    }


def generate_narrative_can(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Canada faces a dual dynamic: 25% US tariffs effective March 4 threaten trade flows while higher oil prices benefit the energy sector. "
            "GDP trend growth from 1.2% to 1.5% shows resilience. "
            "USMCA exemptions provide partial tariff shield. "
            "The Canada-US bilateral relationship is under significant strain amid broader US trade policy disruption."
        ),
        "key_changes_this_week": [
            "25% US tariffs effective March 4; USMCA exemptions until April (major)",
            "Oil price surge benefits Canadian energy sector (Western Canada Select)",
            "Canada-US bilateral relationship under strain from tariff escalation",
            "GDP trend growth (1.2% to 1.5%) showing resilience"
        ],
        "outlook": (
            "Canada's near-term outlook depends on tariff duration and oil price trajectory. "
            "Energy sector windfall partially offsets tariff drag. "
            "USMCA exemption period until April provides a negotiation window. "
            "BOC may cut rates if tariff impact materializes on growth. "
            "Political pressure to diversify trade beyond US dependency intensifies."
        ),
        "investor_implications": (
            "Canadian energy producers (Suncor, CNRL) benefit from oil surge. "
            "Tariff-exposed manufacturers (autos, lumber) face margin compression. "
            "CAD supported by oil prices but pressured by trade uncertainty. "
            "Canadian government bonds may rally on BOC easing expectations."
        ),
        "data_quality_note": "Canadian macro data is high quality. Tariff details from official US/Canadian government sources."
    }


def generate_narrative_kor(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "South Korea navigates post-Yoon political stabilization alongside external energy and security headwinds. "
            "Ex-President Yoon was sentenced to life for insurrection on Feb 19, closing a turbulent political chapter. "
            "The Lee government is stabilizing institutions. Energy independence at 15% makes Korea highly exposed to the Hormuz closure. "
            "Semiconductor cycle recovery provides a growth offset. North Korea's hypersonic missile test adds regional security concerns."
        ),
        "key_changes_this_week": [
            "Ex-President Yoon sentenced to life for insurrection (Feb 19, major)",
            "Lee government political stabilization trend positive",
            "Energy independence at 15% -- highly exposed to Hormuz oil disruption (Mar 1)",
            "Semiconductor recovery supports growth trajectory",
            "North Korea tested hypersonic missiles; regional security deteriorated"
        ],
        "outlook": (
            "Korea's political normalization is a structural positive, offsetting energy vulnerability in the near term. "
            "Semiconductor exports remain the key growth driver -- Samsung, SK Hynix benefit from AI demand cycle. "
            "If oil prices remain elevated, BOK may delay rate cuts to contain imported inflation. "
            "China-Japan sanctions signal broader East Asian trade fragmentation risk relevant to Korea's supply chains."
        ),
        "investor_implications": (
            "Korean semiconductor names (Samsung, SK Hynix) remain conviction overweights on AI cycle. "
            "Energy cost pass-through pressures Korean industrial margins. "
            "KRW may weaken on terms-of-trade deterioration. "
            "KOSPI provides tactical entry on any Hormuz-driven selloff if semiconductor fundamentals hold."
        ),
        "data_quality_note": "South Korea macro data is high quality. Political events are officially confirmed. Energy independence figure from IEA data."
    }


def generate_narrative_rus(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Russia's war economy faces increasing strain in Year 5 of the Ukraine conflict. "
            "GDP at 0.6% with a decrease trend, inflation at 9%, and central bank rate at 21% constraining the civilian economy. "
            "Defense spending consumes 7.1% of GDP. Russia launched a record 1,720+ drones in late February, while Ukraine's Flamingo missiles struck Russian Caspian oil infrastructure. "
            "Kadyrov's health deterioration adds Chechnya succession uncertainty. "
            "Comprehensive Western sanctions remain in place with NR credit rating."
        ),
        "key_changes_this_week": [
            "Record 1,720+ drones launched at Ukraine in late February (Feb 28)",
            "Ukraine's Flamingo missiles struck Caspian oil infrastructure -- new vulnerability",
            "GDP at 0.6% with decrease trend; civilian economy under 21% rate squeeze",
            "Kadyrov health deterioration adds Chechnya succession uncertainty",
            "New START treaty expired -- nuclear arms control framework collapsed"
        ],
        "outlook": (
            "Russia's war economy trajectory is unsustainable beyond 2027 at current resource burn rates. "
            "Caspian oil infrastructure vulnerability is a new strategic concern as Ukraine's strike range extends. "
            "The combination of high interest rates, sanctions, and war spending creates cumulative economic deterioration. "
            "A Chechnya succession crisis could compound security challenges. "
            "No diplomatic offramp visible in the near term."
        ),
        "investor_implications": (
            "Russia remains effectively uninvestable for Western capital under comprehensive sanctions. "
            "Oil price surge benefits Russian revenue but Hormuz disruption may not help given Russia's own export routes. "
            "Ruble stability is artificial given capital controls. "
            "Secondary sanctions risk applies to any entity with Russian exposure."
        ),
        "data_quality_note": "Russia macro data carries significant reliability caveats under wartime conditions. GDP and inflation figures are IMF estimates. Military data from OSINT sources. NR credit rating from all three agencies."
    }


def generate_narrative_bra(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Brazil benefits from several positive developments: the EU-Mercosur Partnership Agreement signed January 17 is the largest FTA ever, covering 780 million people. "
            "GDP growth at 2.4% with stable trend. The Selic rate at 13.25% remains elevated but inflation is contained. "
            "Brazil's agricultural commodity exports benefit from trade rerouting dynamics. "
            "Energy self-sufficiency provides buffer against Hormuz disruption."
        ),
        "key_changes_this_week": [
            "EU-Mercosur Partnership Agreement signed -- largest FTA in history (Jan 17, major)",
            "Oil price surge benefits Petrobras and pre-salt production",
            "GDP at 2.4% with stable trend; inflation contained",
            "Brazil positioned diplomatically as neutral on Iran conflict"
        ],
        "outlook": (
            "Brazil is among the best-positioned emerging markets for the current global environment. "
            "Energy self-sufficiency, agricultural export strength, and EU-Mercosur trade opening provide structural tailwinds. "
            "The BCB Selic rate trajectory is key -- rate cuts depend on continued inflation deceleration. "
            "Political stability under Lula II is adequate for investor confidence."
        ),
        "investor_implications": (
            "Brazilian equities attractive on relative valuation vs EM peers. "
            "Petrobras benefits from oil surge. Agricultural exporters benefit from trade diversification. "
            "BRL may strengthen on commodity tailwinds. "
            "Brazilian government bonds offer attractive real yields at current Selic levels."
        ),
        "data_quality_note": "Brazil macro data is high quality from BCB and IBGE. EU-Mercosur details from official EU sources."
    }


def generate_narrative_aus(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Australia benefits from commodity exposure and energy self-sufficiency in the current crisis environment. "
            "LNG exports benefit from Hormuz-driven price surge as alternative supply. "
            "GDP growth at 1.8% with stable trend. China slowdown is the primary growth risk given Australia's export concentration. "
            "AUKUS defense partnership strengthened by regional security deterioration."
        ),
        "key_changes_this_week": [
            "Hormuz closure benefits Australian LNG as alternative supply source (Mar 1)",
            "China slowdown (4.8% to 4.2%) creates demand headwinds for commodities",
            "AUKUS alliance relevance increases amid regional security deterioration",
            "GDP at 1.8% with stable trend; RBA rate path unchanged"
        ],
        "outlook": (
            "Australia benefits as an alternative energy supplier during the Hormuz disruption. "
            "LNG and coal exports command premium pricing. "
            "China demand deceleration is the key risk -- iron ore and base metals prices may diverge from energy. "
            "RBA likely holds rates steady amid mixed external signals."
        ),
        "investor_implications": (
            "Australian LNG producers (Woodside, Santos) benefit from Hormuz supply disruption. "
            "Iron ore names (BHP, Rio Tinto) face China demand headwinds. "
            "AUD may strengthen on energy export earnings. "
            "ASX resources outperform broader market in this environment."
        ),
        "data_quality_note": "Australian macro data is high quality from ABS and RBA. Energy production figures from official sources."
    }


def generate_narrative_esp(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Spain's PM Sanchez condemned the US-Israeli strikes on Iran as a breach of international law, aligning Spain with the multilateral criticism camp. "
            "GDP growth at 2.3% -- outperforming the Eurozone. Tourism and services drive growth. "
            "Energy dependence creates vulnerability to the oil price surge. "
            "EU-Mercosur agreement benefits Spanish exports to Latin America."
        ),
        "key_changes_this_week": [
            "PM Sanchez condemned Iran strikes as breach of international law (Mar 1)",
            "Oil price surge adds inflation risk to energy-dependent economy",
            "GDP at 2.3% -- Eurozone outperformance continues",
            "EU-Mercosur agreement benefits Spanish Latin American trade links"
        ],
        "outlook": (
            "Spain's growth momentum is the strongest in the Eurozone but vulnerable to energy costs. "
            "Tourism season approaching -- any escalation affecting global travel patterns would impact GDP. "
            "Diplomatic positioning may create friction with US on trade negotiations."
        ),
        "investor_implications": (
            "Spanish bonds outperform periphery peers on growth differential. "
            "Tourism and hospitality stocks face event risk from regional instability. "
            "Underweight energy-intensive Spanish industrials. "
            "IBEX 35 remains Eurozone outperformer on fundamentals."
        ),
        "data_quality_note": "Spanish macro data is high quality from INE and ECB sources."
    }


def generate_narrative_mex(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Mexico faces 25% US tariffs effective March 4, the most significant trade policy shock since NAFTA renegotiation. "
            "Auto imports exempted until April; USMCA coverage provides partial shield. "
            "GDP trend growth from 1.0% to 1.5% remains positive. "
            "Oil price surge benefits Pemex and fiscal revenue. "
            "Judicial reform continues to erode rule-of-law perceptions among foreign investors."
        ),
        "key_changes_this_week": [
            "25% US tariffs effective March 4; auto/USMCA exemptions until April (major)",
            "Oil price surge benefits Pemex fiscal position",
            "GDP trend growth (1.0% to 1.5%) showing resilience",
            "Judicial reform continues undermining investment climate",
            "Peso under pressure from tariff uncertainty"
        ],
        "outlook": (
            "Mexico's near-term trajectory depends on tariff duration and USMCA exemption scope. "
            "Oil revenue windfall provides fiscal buffer. "
            "The April deadline for auto/USMCA exemptions creates a policy cliff. "
            "Judicial reform impact on FDI is a medium-term structural concern. "
            "Nearshoring thesis faces test from tariff uncertainty."
        ),
        "investor_implications": (
            "MXN under pressure -- hedge recommended for USD-reporting investors. "
            "Pemex benefits from oil surge but structural challenges remain. "
            "Nearshoring beneficiaries (industrial REITs, logistics) face tariff uncertainty. "
            "Mexican government bonds may rally on Banxico easing if growth weakens."
        ),
        "data_quality_note": "Mexico macro data is moderate-to-high quality. Tariff details from official US/Mexican government sources."
    }


def generate_narrative_idn(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Indonesia secured a significant strategic win with a $33 billion US trade agreement signed Feb 19, positioning it as a key US partner in Southeast Asia. "
            "GDP stable at 4.9%. FDI trend growth reflecting improved investment climate. "
            "However, the SCOTUS IEEPA ruling questions the enforceability of executive trade deals. "
            "Oil price surge adds moderate cost pressure as a net energy importer."
        ),
        "key_changes_this_week": [
            "US-Indonesia signed $33 billion trade agreement (Feb 19, major)",
            "FDI trend growth as investment climate improves",
            "GDP stable at 4.9% with solid fundamentals",
            "SCOTUS IEEPA ruling creates uncertainty for executive trade agreements",
            "Oil price surge adds moderate import cost pressure"
        ],
        "outlook": (
            "Indonesia's positioning as a US strategic partner in the China competition dynamic is a multi-year positive. "
            "The $33B deal encompasses nickel processing, digital economy, and infrastructure. "
            "Resource nationalism risk remains a concern for mining investors. "
            "GDP growth sustained near 5% with broad-based drivers."
        ),
        "investor_implications": (
            "Indonesian nickel and mining stocks benefit from US supply chain diversification. "
            "Rupiah may strengthen on FDI inflows. "
            "JCI index presents compelling EM value. "
            "Monitor implementation of $33B deal for sector-specific opportunities."
        ),
        "data_quality_note": "Indonesia macro data is moderate quality. Trade agreement details from official sources. GDP and FDI figures from BI and BPS."
    }


def generate_narrative_irn(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Iran is in the most severe crisis since the 1979 revolution. US-Israeli Operation Epic Fury struck 1,000+ targets on Feb 28, killing Supreme Leader Khamenei. "
            "IRGC retaliated against 27 US bases and Gulf states on Mar 1, closing the Strait of Hormuz. "
            "The economy faces collapse: GDP strong_decrease, inflation at 42.4% approaching hyperinflation, "
            "currency in freefall, trade completely disrupted. Political succession crisis with no clear heir during 40-day mourning. "
            "Iran is effectively uninvestable across all asset classes."
        ),
        "key_changes_this_week": [
            "US-Israeli strikes hit 1,000+ targets; Supreme Leader Khamenei killed (Feb 28, transformative)",
            "IRGC retaliated against 27 US bases and Gulf states; Strait of Hormuz closed (Mar 1, transformative)",
            "Succession crisis with no clear heir; IRGC consolidating control during mourning period",
            "Inflation at 42.4% approaching hyperinflation threshold; currency collapse accelerating",
            "Strong_decrease trends across GDP, trade, FDI, current account, political stability",
            "Nuclear infrastructure targeted in strikes"
        ],
        "outlook": (
            "Iran faces state collapse risk in the near-to-medium term. "
            "IRGC control may stabilize security apparatus but cannot address economic collapse. "
            "Succession outcome (hardliner vs pragmatist) will determine whether Iran escalates further or seeks negotiated de-escalation. "
            "Hormuz closure duration is the key variable for global energy markets. "
            "No diplomatic resolution visible in the near term."
        ),
        "investor_implications": (
            "Iran is completely uninvestable. All existing exposures face total loss risk. "
            "Secondary sanctions apply to any entity transacting with Iran. "
            "The primary investment implication is the Hormuz closure's impact on global energy prices and Gulf state sovereigns. "
            "Iran crisis duration is the single most important variable for global commodity markets in Q1-Q2 2026."
        ),
        "data_quality_note": "Iran economic data is very low confidence under current conditions. Pre-crisis figures from IMF may no longer reflect reality. Military situation assessment from OSINT and news sources. CRITICAL: 2 active critical alerts."
    }


def generate_narrative_sau(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Saudi Arabia faces a paradoxical position: oil price surge benefits revenue but Hormuz closure (52% chokepoint exposure) physically blocks export routes. "
            "IRGC attacks on regional US bases include Saudi-proximate installations. "
            "Political stability trend is decreasing as the Kingdom navigates between US alliance obligations and Iranian retaliation risk. "
            "Vision 2030 diversification projects face disruption from regional instability. "
            "GDP trend is decreasing despite the oil price windfall."
        ),
        "key_changes_this_week": [
            "Strait of Hormuz closure at 70% traffic collapse; 52% Saudi chokepoint exposure (Mar 1, critical)",
            "IRGC attacks on regional US bases near Saudi territory (Mar 1)",
            "Political stability trend decrease as Kingdom navigates US-Iran tensions",
            "GDP trend decrease despite oil price surge due to export route disruption",
            "Vision 2030 projects face regional instability headwinds"
        ],
        "outlook": (
            "Saudi Arabia's near-term outlook hinges on Hormuz reopening timeline and Iranian retaliation scope. "
            "Alternative pipeline capacity (East-West Pipeline to Yanbu on Red Sea) can partially offset Hormuz closure but at reduced volume. "
            "If conflict extends beyond 4-6 weeks, Vision 2030 FDI commitments face cancellation risk. "
            "The Aramco IPO tranche that was being considered is likely shelved."
        ),
        "investor_implications": (
            "Aramco: paradoxically negative as export routes are blocked despite higher prices. "
            "Saudi sovereign bonds face spread widening on regional risk. "
            "NEOM and entertainment giga-projects face timeline delays. "
            "Overweight Saudi pipeline/logistics infrastructure that can redirect flows to Red Sea."
        ),
        "data_quality_note": "Saudi macro data is moderate quality. Oil export route details from industry sources. Chokepoint exposure calculated from trade flow data. CRITICAL alert active."
    }


def generate_narrative_isr(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Israel faces a three-front war following the most significant military escalation in decades. "
            "Hezbollah broke the November 2024 ceasefire on Mar 1, reopening the northern front. "
            "IRGC launched retaliatory strikes including a missile hitting West Jerusalem. "
            "Military spending at 8.8% of GDP (2nd highest globally). Government debt trend strong_growth. "
            "Budget deadline March 31 could trigger government dissolution. "
            "Political stability at -1.46 with multiple critical alerts active."
        ),
        "key_changes_this_week": [
            "Hezbollah broke ceasefire, fired rockets at northern Israel (Mar 1, major)",
            "IRGC retaliatory strike hit road in West Jerusalem (Mar 1, transformative)",
            "Israel now faces three-front war: Gaza, Lebanon, Iran",
            "Military spending at 8.8% of GDP; debt trend strong_growth",
            "Budget deadline March 31 could trigger government dissolution",
            "Political stability at -1.46 with critical alert upgraded"
        ],
        "outlook": (
            "Israel's security and fiscal situation has deteriorated critically. "
            "A three-front war (Gaza, Lebanon, Iran) strains military capacity and fiscal resources simultaneously. "
            "Budget deadline March 31 creates political crisis risk on top of security crisis. "
            "Tech sector resilience is being tested by reservist call-ups and investor risk aversion. "
            "US support is assured but the scope of conflict is unprecedented for Israel since 1973."
        ),
        "investor_implications": (
            "Israeli equities face severe downside risk. TA-35 likely gap down Monday. "
            "Shekel depreciation accelerating under multi-front conflict stress. "
            "Israeli government bonds face sell-off on fiscal deterioration and credit rating downgrade risk. "
            "Tech sector (TASE-listed and US-listed Israeli firms) face talent retention challenges from reservist mobilization. "
            "Defense stocks are the only sector with positive positioning."
        ),
        "data_quality_note": "Israel macro data is moderate quality under wartime conditions. Military spending and conflict data from official and OSINT sources. CRITICAL: Multiple critical/warning alerts active."
    }


def generate_narrative_are(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The UAE faces its worst security crisis in modern history. IRGC struck Al Dhafra Air Base and launched missiles at Dubai and Abu Dhabi on Mar 1. "
            "Aviation severely disrupted with 7,700+ delays and 2,280 cancellations. "
            "Strait of Hormuz closure blocks oil and LNG exports (76% chokepoint exposure -- highest among Gulf states). "
            "Tourism and financial services severely impacted. UAE closed its Tehran embassy. "
            "All major trend indicators show strong_decrease: current account, trade openness, FDI, while investment risk shows strong_growth."
        ),
        "key_changes_this_week": [
            "IRGC struck Al Dhafra Air Base; missiles hit Dubai and Abu Dhabi (Mar 1, transformative/critical)",
            "Aviation disrupted: 7,700+ delays, 2,280 cancellations (Mar 1)",
            "Strait of Hormuz closure: 76% chokepoint exposure -- highest in Gulf (Mar 1, critical)",
            "UAE closed Tehran embassy (Mar 1)",
            "Strong_decrease across current account, trade, FDI; strong_growth in investment risk"
        ],
        "outlook": (
            "The UAE's hub economy model is acutely vulnerable to military conflict and Hormuz closure. "
            "Dubai's position as a global aviation, tourism, and financial hub faces existential stress if conflict persists beyond weeks. "
            "Abu Dhabi's oil wealth provides a fiscal buffer but cannot offset export route disruption. "
            "FDI and tourism recovery will lag security normalization by 6-12 months."
        ),
        "investor_implications": (
            "UAE equities face severe re-rating risk. DFM and ADX likely gap down. "
            "Dubai real estate faces foreign buyer withdrawal. "
            "Abu Dhabi sovereign wealth fund (ADIA, Mubadala) portfolios provide ultimate backstop but near-term disruption is severe. "
            "Emirates and Etihad airline operations severely curtailed. "
            "Any exposure to UAE should be hedged or reduced."
        ),
        "data_quality_note": "UAE macro data is moderate quality. Aviation disruption data from FlightAware. Military events from official UAE statements and OSINT. CRITICAL alert active."
    }


def generate_narrative_sgp(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Singapore's trade-dependent economy faces headwinds from global shipping disruption following the Hormuz crisis. "
            "Current account at 17.54% of GDP highlights extreme trade dependence. "
            "GDP trend decreasing from 2.2% to 1.8%. Trade openness trend decrease as re-routing costs rise. "
            "Political stability at 1.42 -- highest in the dataset -- provides institutional buffer. "
            "Singapore benefits as a relative safe haven in Southeast Asia."
        ),
        "key_changes_this_week": [
            "Hormuz crisis increases re-routing costs for Middle East-Asia trade flows (Mar 1)",
            "GDP trend decrease from 2.2% to 1.8% on trade disruption",
            "Trade openness trend decrease as shipping costs rise",
            "Political stability at 1.42 (highest in dataset) provides institutional buffer"
        ],
        "outlook": (
            "Singapore faces second-order effects from the Hormuz crisis through trade flow disruption rather than direct energy exposure. "
            "Bunkering and ship servicing revenues may increase from rerouted traffic. "
            "Singapore dollar remains a regional safe-haven currency. "
            "Financial services sector relatively insulated from physical trade disruption."
        ),
        "investor_implications": (
            "STI may underperform on trade disruption concerns but Singapore's safe-haven premium limits downside. "
            "Singapore REITs (S-REITs) face mixed signals from logistics sector disruption. "
            "DBS, OCBC, UOB banks benefit from flight-to-quality deposit flows. "
            "SGD supported by safe-haven status."
        ),
        "data_quality_note": "Singapore macro data is high quality from MAS and SingStat sources. Watch-level alert active."
    }


def generate_narrative_twn(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Taiwan faces elevated risk from the convergence of extreme energy vulnerability and cross-strait tensions. "
            "Energy independence at only 5% -- the lowest in the dataset -- makes Taiwan critically exposed to the Hormuz closure. "
            "GDP trend decreasing from 3.7% to 2.1%. Chokepoint exposure at 0.69. "
            "China's sanctions on Japan following PM Takaichi's Taiwan defense comments signal deteriorating regional security. "
            "China conducted blockade simulation exercises and PLA drone flew through Taiwanese airspace."
        ),
        "key_changes_this_week": [
            "Energy independence at 5% -- most vulnerable to Hormuz closure (Mar 1, critical for Taiwan)",
            "China blockade simulation exercises and PLA drone airspace violation (ongoing)",
            "China-Japan sanctions escalated following PM Takaichi's Taiwan defense remarks (Feb 25)",
            "GDP trend decreasing from 3.7% to 2.1%",
            "Chokepoint exposure at 0.69 -- among highest in dataset"
        ],
        "outlook": (
            "Taiwan's risk premium is structurally elevated by cross-strait tensions compounded by the current global instability. "
            "China's willingness to sanction Japan over Taiwan-related comments signals hardening of position. "
            "Energy vulnerability is Taiwan's Achilles heel in any blockade scenario. "
            "TSMC and semiconductor sector provide strategic relevance that motivates US/Japan support. "
            "Any further China-Japan-Taiwan escalation would be transformative for global tech supply chains."
        ),
        "investor_implications": (
            "TSMC remains systemically important but Taiwan risk premium should be priced in. "
            "TAIEX faces downside on energy costs and cross-strait risk. "
            "TWD under depreciation pressure. "
            "Any China blockade scenario (however unlikely near-term) would be catastrophic for global semiconductor supply. "
            "Diversification of TSMC exposure to Arizona/Japan fabs is the key risk mitigant."
        ),
        "data_quality_note": "Taiwan macro data is high quality. Energy independence figure well-established. Cross-strait military activities from OSINT. Warning-level alert active."
    }


def generate_narrative_tur(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Turkey navigates dual pressures: 34.9% inflation with aggressive monetary tightening (47.5% rate) alongside regional instability from the Iran crisis. "
            "Istanbul mayor Imamoglu imprisoned, signaling continued opposition suppression. "
            "Turkey is positioned as a potential mediator in the Iran conflict given relationships with all parties. "
            "GDP growth at 3.0% shows resilience despite monetary tightening. "
            "Erdogan succession dynamics emerging as a medium-term theme."
        ),
        "key_changes_this_week": [
            "Iran crisis adds regional risk proximity; Turkey positioned as potential mediator (Mar 1)",
            "Inflation at 34.9% with decrease trend (positive) from peak",
            "Central bank rate at 47.5% -- among highest globally",
            "Istanbul mayor Imamoglu imprisoned; opposition suppression continues",
            "Erdogan succession dynamics emerging as political theme"
        ],
        "outlook": (
            "Turkey's disinflation trajectory is the key positive theme but is being tested by oil price surge. "
            "The Iran crisis creates both risks (energy costs, regional instability) and opportunities (mediator role, trade rerouting). "
            "CBRT may need to hold rates longer than expected if energy-driven inflation persists. "
            "Political risk remains elevated with opposition suppression."
        ),
        "investor_implications": (
            "Turkish lira carry trade attractive at 47.5% rate but event risk elevated. "
            "Istanbul bourse may benefit from mediator positioning and oil transit revenue. "
            "Turkish bank stocks priced for disinflation -- any reversal would be painful. "
            "Underweight consumer-facing sectors exposed to inflation persistence."
        ),
        "data_quality_note": "Turkey macro data is moderate quality. Inflation and rate data from CBRT. Political events confirmed by multiple sources. Warning-level alert active."
    }


def generate_narrative_che(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Switzerland benefits from its traditional safe-haven status amid global turmoil. "
            "GDP growth stable. CHF appreciating on flight-to-safety flows. "
            "Gold surge past $5,300/oz benefits Swiss banking and gold refining sectors. "
            "Swiss neutrality limits direct exposure to geopolitical conflicts."
        ),
        "key_changes_this_week": [
            "CHF appreciating on global safe-haven flows (Mar 1)",
            "Gold at $5,300+ benefits Swiss banking and refining sectors",
            "Swiss neutrality limits direct geopolitical exposure",
            "GDP stable with contained inflation"
        ],
        "outlook": (
            "Switzerland is among the best-positioned economies for the current crisis environment. "
            "Safe-haven inflows support the franc and financial sector. "
            "SNB may need to manage CHF appreciation to protect export competitiveness. "
            "Swiss pharmaceutical and technology sectors relatively insulated from geopolitical disruption."
        ),
        "investor_implications": (
            "Swiss franc long positions benefit from crisis environment. "
            "Swiss banks (UBS, Credit Suisse) benefit from wealth management inflows. "
            "SMI outperforms European peers on defensive characteristics. "
            "Swiss gold refiners (Valcambi, PAMP) benefit from $5,300+ gold."
        ),
        "data_quality_note": "Swiss macro data is high quality from SNB and FSO sources."
    }


def generate_narrative_pol(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Poland's economy grows at 3.2% with moderate inflation. "
            "NATO's eastern flank posture strengthens with EU defense spending increase. "
            "Poland benefits from nearshoring flows redirected from more volatile EM markets. "
            "Energy dependence creates vulnerability to oil price surge."
        ),
        "key_changes_this_week": [
            "Hormuz crisis adds energy cost pressure to energy-dependent economy",
            "NATO eastern flank posture strengthens amid global security deterioration",
            "GDP at 3.2% -- among strongest in EU",
            "Nearshoring flows benefit from trade redirection dynamics"
        ],
        "outlook": (
            "Poland remains an EU growth leader with structural advantages from nearshoring and EU fund absorption. "
            "Defense spending increase creates domestic demand stimulus. "
            "Energy transition investments partially offset oil dependence over time. "
            "NBP rate path depends on inflation trajectory."
        ),
        "investor_implications": (
            "Polish equities offer EU growth exposure at reasonable valuations. "
            "WIG 20 benefits from EU fund flows and nearshoring. "
            "PLN may face pressure from energy import costs. "
            "Polish defense sector benefits from NATO spending increase."
        ),
        "data_quality_note": "Polish macro data is high quality from GUS and NBP sources."
    }


def generate_narrative_swe(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Sweden's economy recovers with GDP growth improving. "
            "NATO membership strengthens security positioning in the current threat environment. "
            "Defense spending increasing. "
            "Limited direct exposure to Hormuz crisis but second-order trade effects apply."
        ),
        "key_changes_this_week": [
            "NATO membership provides security positioning amid global instability",
            "Defense spending trajectory increasing",
            "Limited direct Hormuz exposure but trade effects present",
            "GDP recovery continuing"
        ],
        "outlook": (
            "Sweden's economic recovery is supported by housing market stabilization and export recovery. "
            "NATO membership resolved a structural security gap. "
            "Riksbank rate path may be adjusted if oil-driven inflation emerges."
        ),
        "investor_implications": (
            "Swedish equities offer Nordic growth exposure. "
            "Saab and Ericsson benefit from defense spending and security themes. "
            "SEK may weaken on terms-of-trade impact from energy costs. "
            "Swedish housing market stabilization supports bank valuations."
        ),
        "data_quality_note": "Swedish macro data is high quality from SCB and Riksbank sources."
    }


def generate_narrative_nor(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Norway is a primary beneficiary of the Hormuz closure as Europe's largest gas supplier and a major oil producer. "
            "Energy exports surge in value as global prices spike. "
            "Government Pension Fund Global provides immense fiscal buffer. "
            "NATO membership and Arctic positioning strengthen security relevance."
        ),
        "key_changes_this_week": [
            "Hormuz closure benefits Norwegian oil and gas exports as alternative supply (Mar 1)",
            "Energy export revenue surging on price spikes",
            "GPFG sovereign wealth provides fiscal buffer",
            "NATO membership strengthens security positioning"
        ],
        "outlook": (
            "Norway is among the largest beneficiaries of the current crisis environment. "
            "European energy dependence on Norwegian supply increases pricing power. "
            "Norges Bank may face appreciation pressure on NOK. "
            "Sovereign wealth fund insulates fiscal position from any domestic shock."
        ),
        "investor_implications": (
            "Equinor is a direct beneficiary of European energy premium. "
            "NOK likely to strengthen on energy earnings. "
            "Norwegian sovereign bonds are among the safest globally. "
            "OBX index benefits from energy and maritime logistics exposure."
        ),
        "data_quality_note": "Norwegian macro data is high quality from SSB and Norges Bank sources."
    }


def generate_narrative_nld(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The Netherlands faces moderate headwinds from global trade disruption given its role as a major European logistics hub. "
            "Rotterdam port traffic may be affected by shipping rerouting. "
            "ASML remains systemically important in the semiconductor supply chain amid tech decoupling dynamics. "
            "GDP growth stable. Dutch fiscal position strong."
        ),
        "key_changes_this_week": [
            "Global shipping rerouting may affect Rotterdam port traffic",
            "ASML exposure to China-Japan-Taiwan semiconductor tensions",
            "Trade disruption from Hormuz crisis affects European logistics flows",
            "GDP stable with strong fiscal position"
        ],
        "outlook": (
            "The Netherlands faces second-order effects from trade disruption through its logistics hub function. "
            "ASML remains a key beneficiary of semiconductor investment but faces geopolitical exposure. "
            "Dutch gas transition from Groningen continues."
        ),
        "investor_implications": (
            "ASML is the key Netherlands exposure -- beneficiary of semiconductor investment but geopolitical risk applies. "
            "Dutch logistics stocks face mixed signals from trade rerouting. "
            "AEX index sensitive to global trade flows."
        ),
        "data_quality_note": "Netherlands macro data is high quality from CBS and DNB sources."
    }


def generate_narrative_mys(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Malaysia benefits as a net energy exporter from the oil price surge while maintaining semiconductor manufacturing diversification attractiveness. "
            "GDP growth stable. Petronas and palm oil exports benefit from commodity price strength. "
            "China-Japan tensions may redirect supply chain investment toward ASEAN including Malaysia."
        ),
        "key_changes_this_week": [
            "Oil price surge benefits Malaysia as net energy exporter (Mar 1)",
            "Semiconductor supply chain diversification benefits Malaysia positioning",
            "China-Japan tensions may redirect investment to ASEAN",
            "GDP growth stable with solid fundamentals"
        ],
        "outlook": (
            "Malaysia is well-positioned as an energy exporter with semiconductor manufacturing diversification appeal. "
            "Petronas benefits from oil surge. Palm oil exports benefit from commodity tailwinds. "
            "China-ASEAN trade links provide growth stability."
        ),
        "investor_implications": (
            "Petronas-linked equities benefit from energy prices. "
            "Malaysian semiconductor assembly/test (OSAT) firms benefit from supply chain diversification. "
            "MYR supported by energy export earnings. "
            "KLCI attractive on relative EM valuation."
        ),
        "data_quality_note": "Malaysia macro data is moderate-to-high quality from BNM and DOS sources."
    }


def generate_narrative_tha(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Thailand is in political transition with PM Anutin forming a new coalition government on Feb 13. "
            "Policy direction under the new government remains to be defined. "
            "Tourism recovery is the key growth driver but faces event risk from regional instability. "
            "GDP growth moderate. Oil price surge adds import cost pressure."
        ),
        "key_changes_this_week": [
            "PM Anutin formed new coalition government (Feb 13, moderate)",
            "Tourism recovery faces event risk from regional instability",
            "Oil price surge adds import cost pressure",
            "Political transition period with policy direction unclear"
        ],
        "outlook": (
            "Thailand's near-term trajectory depends on new government policy signals. "
            "Tourism season is the primary growth lever -- any travel disruption from regional conflict is a downside risk. "
            "BOT rate path may be influenced by energy-driven inflation."
        ),
        "investor_implications": (
            "Thai tourism and hospitality stocks face mixed signals. "
            "SET index may be range-bound during political transition. "
            "THB under moderate pressure from energy imports. "
            "Monitor new government's economic policy announcements."
        ),
        "data_quality_note": "Thailand macro data is moderate quality from BOT and NESDC sources. Watch-level alert active."
    }


def generate_narrative_zaf(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "South Africa faces mixed signals: oil price surge adds import costs but commodity exports (gold, platinum, coal) benefit from price strength. "
            "Gold at $5,300+ is highly positive for South African mining revenue. "
            "GDP growth remains sluggish with structural load-shedding challenges. "
            "GNU coalition provides political stability."
        ),
        "key_changes_this_week": [
            "Gold surge to $5,300+ benefits South African mining sector significantly",
            "Oil price surge adds import cost pressure",
            "Commodity export revenue boosted by global crisis dynamics",
            "GNU coalition maintains political stability"
        ],
        "outlook": (
            "South Africa's gold and platinum mining sectors are direct beneficiaries of the crisis environment. "
            "Structural challenges (load-shedding, unemployment) persist. "
            "SARB rate path depends on inflation trajectory amid commodity price cross-currents. "
            "GNU coalition stability tested by policy implementation."
        ),
        "investor_implications": (
            "South African gold miners (AngloGold, Gold Fields, Harmony) are conviction overweights at $5,300+ gold. "
            "Platinum group metals benefit from supply disruption dynamics. "
            "ZAR may strengthen on mining export earnings. "
            "JSE resources index outperforms broader market."
        ),
        "data_quality_note": "South Africa macro data is moderate quality from SARB and StatsSA sources."
    }


def generate_narrative_pak(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Pakistan is in crisis on multiple fronts: declared open war on Afghanistan on Feb 27 with airstrikes on Kabul and Kandahar, "
            "while 20 people were killed in domestic protests over US-Israeli strikes on Iran. "
            "Political stability at -1.93 -- among the worst in the dataset. "
            "GDP trend strong_decrease, inflation strong_growth, debt strong_growth. "
            "Sovereign credit at CCC+/Caa1. "
            "A nuclear-armed nation in active conflict with deteriorating fiscal position."
        ),
        "key_changes_this_week": [
            "Pakistan declared open war on Afghanistan with airstrikes on Kabul and Kandahar (Feb 27, transformative)",
            "20 killed in domestic protests over Iran strikes (Mar 1)",
            "Political stability at -1.93 (strong_decrease) -- near worst in dataset",
            "GDP trend strong_decrease; inflation trend strong_growth; debt trend strong_growth",
            "Sovereign credit at CCC+/Caa1; fiscal position deteriorating rapidly"
        ],
        "outlook": (
            "Pakistan faces compounding crises: active war, domestic unrest, fiscal deterioration, and regional instability from the Iran conflict. "
            "IMF program compliance at severe risk if war spending expands. "
            "Nuclear dimension adds global escalation risk. "
            "No diplomatic resolution with Afghanistan visible. "
            "Political stability may deteriorate further if protests spread."
        ),
        "investor_implications": (
            "Pakistan is effectively uninvestable at current risk levels. "
            "Sovereign bonds face distressed pricing. "
            "KSE-100 faces severe downside. "
            "Rupee under extreme pressure. "
            "Any existing exposure should be reduced to zero where possible."
        ),
        "data_quality_note": "Pakistan macro data is low-to-moderate quality under current crisis conditions. Political and military events from official statements and news sources. CRITICAL alert active."
    }


def generate_narrative_arg(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Argentina delivers a landmark positive development: the Senate approved major labor reform (42-28 vote) on Feb 27, advancing Milei's economic restructuring agenda. "
            "Monthly inflation decelerated dramatically to 2.9% from a peak above 25%. "
            "Annual CPI at 41.3% still elevated but the trajectory is sharply positive. "
            "GDP at 4.5% with stable trend. "
            "Sovereign credit remains CCC+/Caa1 but the reform trajectory is improving."
        ),
        "key_changes_this_week": [
            "Senate approved landmark labor reform (42-28 vote) on Feb 27 (major, positive)",
            "Monthly inflation decelerated to 2.9% from peak of 25%+ (positive trajectory)",
            "GDP at 4.5% with stable trend showing recovery",
            "Political stability improving under Milei reform agenda",
            "Sovereign credit remains CCC+/Caa1 but outlook improving"
        ],
        "outlook": (
            "Argentina's reform trajectory under Milei is the most positive structural story among frontier markets. "
            "Labor reform passage removes a key structural impediment to formal employment. "
            "If monthly inflation continues below 3%, annual rate will fall below 20% by H2 2026. "
            "FDI recovery depends on sustained reform implementation and credit rating upgrade."
        ),
        "investor_implications": (
            "Argentine sovereign bonds offer high-yield opportunity on reform thesis -- but CCC+ credit requires conviction. "
            "Merval index pricing in reform optimism. "
            "ARS stabilization depends on continued disinflation. "
            "Vaca Muerta energy assets benefit from oil price surge. "
            "This is a high-conviction, high-risk structural turnaround trade."
        ),
        "data_quality_note": "Argentina macro data is moderate quality. Monthly inflation from INDEC. Senate vote officially confirmed. Sovereign credit from all three agencies. Warning-level alert active (inflation) plus watch-level alert (positive reform)."
    }


def generate_narrative_ukr(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ukraine's war enters its 5th year with mixed military developments. "
            "The southern counteroffensive recaptured 300+ sq km. Flamingo missiles struck a Russian ICBM factory and Caspian oil infrastructure -- demonstrating expanding strike capability. "
            "Russia launched a record 1,720+ drones in late February. "
            "GDP at 2% growth trend shows remarkable resilience. IMF $8.1B loan approved anchoring a $136.5B international support package. "
            "Sovereign credit at CC/Ca with 2,250 bps risk premium."
        ),
        "key_changes_this_week": [
            "Southern counteroffensive recaptured 300+ sq km (Feb, major)",
            "Flamingo missiles struck Russian ICBM factory and Caspian oil infrastructure (major)",
            "Russia launched record 1,720+ drones at Ukraine in late February",
            "IMF $8.1B loan approved anchoring $136.5B support package",
            "GDP at 2% growth trend showing wartime resilience",
            "Sovereign credit at CC/Ca with 2,250 bps risk premium"
        ],
        "outlook": (
            "Ukraine's military capability is demonstrably expanding while the economy shows war-adjusted resilience. "
            "Flamingo missile capability targeting Russian energy infrastructure is strategically significant. "
            "IMF support package provides fiscal lifeline through 2026. "
            "Any ceasefire/negotiation scenario remains distant but Ukraine's improved military position strengthens negotiating leverage. "
            "Reconstruction opportunity remains the long-term investment thesis."
        ),
        "investor_implications": (
            "Ukraine sovereign bonds trade at deep distress levels -- any ceasefire trigger would produce outsized returns. "
            "Current investment is speculative and requires conflict resolution conviction. "
            "Ukrainian agricultural assets have value in any post-conflict scenario. "
            "International reconstruction commitments ($136.5B+) represent future opportunity pipeline."
        ),
        "data_quality_note": "Ukraine economic data is low-to-moderate quality under wartime conditions. Military developments from Ukrainian MOD and OSINT. IMF figures official. CRITICAL alert active."
    }


def generate_narrative_qat(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Qatar is under direct Iranian attack. IRGC struck Al Udeid Air Base. "
            "Strait of Hormuz closure blocks Qatar's LNG exports (66% chokepoint exposure). "
            "Current account trend strong_decrease from 17.29%. "
            "GDP growth outlook severely downgraded from pre-crisis 6.1% forecast. "
            "North Field LNG expansion timeline at risk. "
            "Qatar is caught between hosting the primary US military base in the Gulf and proximity to Iran."
        ),
        "key_changes_this_week": [
            "IRGC struck Al Udeid Air Base in Qatar (Mar 1, critical/transformative)",
            "Hormuz closure blocks LNG exports -- 66% chokepoint exposure (Mar 1, critical)",
            "GDP outlook severely downgraded from 6.1% forecast",
            "North Field LNG expansion timeline at risk",
            "Current account trend strong_decrease from 17.29%"
        ],
        "outlook": (
            "Qatar's LNG-dependent economy faces existential disruption from Hormuz closure. "
            "North Field expansion -- the largest single energy project globally -- faces delay risk. "
            "Qatar's diplomatic agility (historically mediating between rivals) may prove valuable but Al Udeid targeting limits neutrality options."
        ),
        "investor_implications": (
            "QatarEnergy and LNG project investments face force majeure conditions. "
            "QSE index faces severe repricing. "
            "Qatari sovereign bonds may widen but sovereign wealth (QIA) provides strong backstop. "
            "Any LNG offtake agreements face supply disruption clauses."
        ),
        "data_quality_note": "Qatar macro data is moderate quality. Military events from official statements. Chokepoint exposure calculated from trade flow data. CRITICAL alert active."
    }


def generate_narrative_kwt(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Kuwait is under direct Iranian attack. IRGC struck Ali Al Salem Air Base. "
            "Hormuz closure blocks oil exports (64% chokepoint exposure). "
            "Low debt (7.3%) provides fiscal buffer but oil revenue disruption threatens the budget. "
            "GDP outlook severely downgraded from pre-crisis 3.9% forecast."
        ),
        "key_changes_this_week": [
            "IRGC struck Ali Al Salem Air Base in Kuwait (Mar 1, critical/transformative)",
            "Hormuz closure blocks oil exports -- 64% chokepoint exposure (Mar 1, critical)",
            "GDP outlook severely downgraded from 3.9% forecast",
            "Low debt (7.3%) provides fiscal buffer"
        ],
        "outlook": (
            "Kuwait's oil-dependent economy faces severe disruption from Hormuz closure. "
            "Fiscal reserves (Kuwait Investment Authority) provide significant buffer. "
            "Low debt position means Kuwait can weather the crisis longer than peers. "
            "Recovery depends on Hormuz reopening timeline."
        ),
        "investor_implications": (
            "Kuwait equity market faces severe repricing. "
            "KIA sovereign wealth provides ultimate backstop. "
            "Kuwaiti sovereign bonds face spread widening but strong fiscal position limits credit risk. "
            "Oil export revenue loss is temporary if conflict resolves."
        ),
        "data_quality_note": "Kuwait macro data is moderate quality. Military events from official statements. CRITICAL alert active."
    }


def generate_narrative_omn(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Oman is critically exposed to the Strait of Hormuz closure with 62% chokepoint exposure. "
            "Oil exports severely disrupted in what is the most severe global energy supply disruption in decades. "
            "Unlike UAE/Qatar/Kuwait, Oman was not directly targeted by IRGC strikes but geographic proximity to Hormuz makes it the most physically affected."
        ),
        "key_changes_this_week": [
            "Strait of Hormuz 70% traffic collapse -- 62% Oman chokepoint exposure (Mar 1, critical)",
            "Oil exports severely disrupted",
            "No direct IRGC strikes on Oman but geographic proximity critical"
        ],
        "outlook": (
            "Oman's economy is directly tied to Hormuz passage for oil exports. "
            "Fiscal reserves are limited relative to wealthier Gulf peers. "
            "Oman's historically neutral diplomatic posture with Iran may provide some protection from direct targeting. "
            "Recovery tied directly to Hormuz reopening."
        ),
        "investor_implications": (
            "Oman sovereign bonds face significant spread widening. "
            "Oil export revenue disruption is severe. "
            "Muscat Securities Market faces repricing. "
            "Oman's fiscal position more vulnerable than Kuwait/Qatar due to smaller reserves."
        ),
        "data_quality_note": "Oman macro data is moderate quality. Chokepoint exposure calculated from trade data. CRITICAL alert active."
    }


# ============================================================
# TIER 2 NARRATIVE GENERATORS (moderate detail)
# ============================================================

def generate_narrative_nga(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Nigeria faces a security crisis with the Boko Haram massacre killing 170+, compounded by 23% inflation and NLC labor protests. "
            "Sovereign credit at CCC+/Caa1. Oil price surge benefits revenue but security and governance challenges persist."
        ),
        "key_changes_this_week": [
            "Boko Haram massacre killed 170+ (major security event)",
            "Inflation at 23% with CCC+/Caa1 credit rating",
            "NLC conducting protests over economic conditions",
            "Oil price surge benefits fiscal revenue"
        ],
        "outlook": "Security deterioration and inflation persistence challenge Nigeria's reform trajectory. Oil revenue windfall provides fiscal cushion but structural challenges remain. Presidential reform agenda faces implementation headwinds.",
        "investor_implications": "Nigerian equities and bonds carry elevated risk at CCC+ credit. Naira volatility expected. Oil-linked revenue is the key positive. Avoid non-oil sectors.",
        "data_quality_note": "Nigeria macro data is moderate quality. Warning-level alert active."
    }


def generate_narrative_egy(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Egypt faces second-order effects from the Iran-Gulf crisis through Suez Canal traffic disruption and oil import costs. "
            "Regional instability weighs on tourism. "
            "GDP growth moderate with IMF program providing fiscal anchor."
        ),
        "key_changes_this_week": [
            "Suez Canal traffic potentially affected by regional shipping rerouting",
            "Oil import costs increase on price surge",
            "Regional instability affects tourism outlook",
            "IMF program provides fiscal anchor"
        ],
        "outlook": "Egypt's Suez Canal revenues and tourism face headwinds from regional instability. IMF program compliance is the key fiscal discipline mechanism. EGP management under central bank scrutiny.",
        "investor_implications": "Egyptian government bonds priced with IMF support backstop. Tourism stocks face regional event risk. Suez Canal revenue may fluctuate with rerouting patterns.",
        "data_quality_note": "Egypt macro data is moderate quality. IMF program data is official."
    }


def generate_narrative_phl(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Philippines faces a governance crisis from the Marcos flood control corruption scandal. "
            "House Speaker and Senate President stepped down. Third Trillion Peso March protest held. "
            "Marcos-Duterte alliance shattered. FDI trend at risk from political instability."
        ),
        "key_changes_this_week": [
            "Marcos corruption scandal deepens; legislative leadership forced out (major)",
            "Third Trillion Peso March protest (ongoing political crisis)",
            "Marcos-Duterte alliance shattered",
            "FDI at risk from governance deterioration"
        ],
        "outlook": "Philippines political crisis has no clear resolution. Legislative paralysis threatens reform implementation. FDI recovery depends on governance stabilization. BPO sector provides economic resilience.",
        "investor_implications": "PSEi faces governance discount. BPO/services sector resilient to political turbulence. PHP under pressure. Philippine government bonds may widen on political risk.",
        "data_quality_note": "Philippines macro data is moderate quality. Political events from official sources. Warning-level alert active."
    }


def generate_narrative_col(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Colombia benefits from oil price surge as a net energy exporter. "
            "GDP growth moderate. Oil revenue supports fiscal position. "
            "Petro government reform agenda continues. Regional instability limited to Central American migration flows."
        ),
        "key_changes_this_week": [
            "Oil price surge benefits Colombian energy revenue",
            "GDP growth moderate with stable fundamentals",
            "Petro government reform agenda continues"
        ],
        "outlook": "Colombia's energy exporter status provides a near-term positive. Fiscal reform implementation under Petro is the key medium-term variable. Security situation stable.",
        "investor_implications": "Ecopetrol benefits from oil prices. Colombian sovereign bonds moderate risk. COP supported by energy exports.",
        "data_quality_note": "Colombia macro data is moderate quality from BanRep and DANE."
    }


def generate_narrative_chl(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Chile's copper exports benefit from supply chain disruption dynamics and green energy transition demand. "
            "GDP growth stable. Constitutional reform process continuing. "
            "Limited direct exposure to Hormuz crisis but oil import costs add inflation pressure."
        ),
        "key_changes_this_week": [
            "Copper prices supported by supply chain disruption dynamics",
            "Oil import costs increase on Hormuz disruption",
            "GDP growth stable; inflation contained"
        ],
        "outlook": "Chile's copper exposure is structurally positive for the green energy transition. BCCh rate path provides monetary policy flexibility. Political stability improving post-constitutional reform period.",
        "investor_implications": "Chilean copper miners benefit from structural demand. CLP supported by copper. Chilean sovereign bonds are investment-grade stable. SQM and lithium exposure adds battery metals upside.",
        "data_quality_note": "Chile macro data is high quality from BCCh and INE."
    }


def generate_narrative_per(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Peru installed its 9th president in a decade (Balcazar), with presidential elections scheduled April 12. "
            "Political instability is chronic. Mining sector remains the economic backbone. "
            "Oil import costs add modest pressure."
        ),
        "key_changes_this_week": [
            "Balcazar installed as 9th president in a decade (ongoing instability)",
            "Presidential elections scheduled April 12",
            "Mining and investment environment uncertain"
        ],
        "outlook": "Peru's chronic political instability is the key risk. April 12 elections will set the next political cycle. Mining sector (copper, gold, silver) provides economic resilience regardless of political leadership.",
        "investor_implications": "Peruvian mining exposure (Southern Copper, Buenaventura) attractive on gold surge. PEN relatively stable. Political uncertainty warrants caution on non-mining sectors.",
        "data_quality_note": "Peru macro data is moderate quality. Political events confirmed. Watch-level alert active."
    }


def generate_narrative_bgd(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Bangladesh completes a major democratic transition with BNP winning a landslide (209 seats) in the Feb 12 election -- the first post-Hasina vote. "
            "Business optimism improving. Energy independence at 0.4 creates oil surge vulnerability. "
            "Garment export sector provides economic base."
        ),
        "key_changes_this_week": [
            "BNP won landslide (209 seats) in Feb 12 election (major, positive transition)",
            "Business optimism improving under new government",
            "Energy independence at 0.4 -- exposed to oil surge",
            "Garment export sector provides economic stability"
        ],
        "outlook": "Bangladesh's democratic transition is positive for governance and FDI. BNP government's economic policy signals will be key. Garment sector resilience provides base-case stability.",
        "investor_implications": "Bangladeshi garment exporters benefit from stable demand. Democratic transition positive for long-term FDI. Energy costs a near-term headwind.",
        "data_quality_note": "Bangladesh macro data is moderate quality. Election results official. Watch-level alert active."
    }


def generate_narrative_vnm(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Vietnam continues to benefit from manufacturing supply chain diversification out of China. "
            "GDP growth strong. FDI inflows sustained. "
            "Oil import costs add modest pressure. "
            "US-China trade tensions generally benefit Vietnam's positioning."
        ),
        "key_changes_this_week": [
            "Manufacturing FDI inflows continue from China diversification",
            "GDP growth strong with export momentum",
            "Oil price surge adds modest import cost pressure",
            "US-China tariff escalation benefits Vietnam positioning"
        ],
        "outlook": "Vietnam's structural story as a China+1 manufacturing destination remains intact and is reinforced by China-Japan sanctions escalation. FDI pipeline robust. Energy costs the main headwind.",
        "investor_implications": "Vietnamese equities offer EM manufacturing exposure. VN-Index attractive on growth trajectory. VND relatively stable. Electronics and textile exporters benefit from supply chain shift.",
        "data_quality_note": "Vietnam macro data is moderate quality from GSO and SBV."
    }


def generate_narrative_irq(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Iraq is critically exposed to the Strait of Hormuz closure with 51% chokepoint exposure. "
            "Oil exports severely disrupted -- Iraq's fiscal position is highly dependent on oil revenue. "
            "The Iran conflict creates additional security concerns given Iran's influence over Iraqi politics and militias."
        ),
        "key_changes_this_week": [
            "Hormuz closure at 70% traffic collapse -- 51% Iraq chokepoint exposure (Mar 1, critical)",
            "Oil exports severely disrupted; fiscal position at risk",
            "Iran conflict creates additional security concerns via militia proxy networks"
        ],
        "outlook": "Iraq's economy is existentially dependent on oil export routes through Hormuz. Alternative pipelines to Turkey provide partial but insufficient offset. Political stability at risk from Iranian militia influence.",
        "investor_implications": "Iraq sovereign bonds face severe repricing. Oil-dependent fiscal position under extreme stress. Avoid Iraqi exposure until Hormuz situation resolves.",
        "data_quality_note": "Iraq macro data is low-to-moderate quality. Chokepoint exposure calculated from trade data. CRITICAL alert active."
    }


def generate_narrative_kaz(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Kazakhstan benefits from oil price surge as a major energy exporter with export routes not dependent on Hormuz. "
            "CPC pipeline to Black Sea and China pipeline provide alternative routes. "
            "GDP growth moderate. Balanced diplomacy between Russia, China, and the West."
        ),
        "key_changes_this_week": [
            "Oil price surge benefits Kazakhstan energy revenue",
            "Export routes (CPC pipeline) not dependent on Hormuz",
            "Balanced diplomacy positioning maintained"
        ],
        "outlook": "Kazakhstan's energy export revenue benefits from crisis pricing while export routes avoid Hormuz dependency. Balanced multi-vector diplomacy provides geopolitical flexibility.",
        "investor_implications": "Kazakh energy equities benefit from oil prices. KZT supported by energy earnings. KASE index offers frontier energy exposure. CPC pipeline reliability is key risk factor.",
        "data_quality_note": "Kazakhstan macro data is moderate quality from NBK and stat.gov.kz."
    }


def generate_narrative_rou(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Romania's economy grows solidly within the EU framework. "
            "NATO eastern flank positioning strengthens security relevance. "
            "Oil price surge adds energy cost pressure. "
            "EU fund absorption supports growth."
        ),
        "key_changes_this_week": [
            "NATO eastern flank posture strengthened amid global instability",
            "Oil price surge adds energy cost pressure",
            "EU fund absorption continues supporting growth"
        ],
        "outlook": "Romania's EU integration and NATO membership provide structural advantages. Energy costs are the near-term headwind. Defense spending increase creates fiscal demand.",
        "investor_implications": "BET index offers EU convergence exposure. Romanian government bonds at reasonable yields. RON relatively stable within EU framework.",
        "data_quality_note": "Romania macro data is moderate quality from BNR and INS sources."
    }


def generate_narrative_cze(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Czech Republic's export-oriented economy faces headwinds from trade fragmentation and oil price surge. "
            "GDP recovery continuing. "
            "Auto sector exposure to broader trade tensions. "
            "EU/NATO membership provides institutional stability."
        ),
        "key_changes_this_week": [
            "Trade fragmentation headwinds for export-oriented economy",
            "Oil price surge adds energy costs",
            "GDP recovery continuing",
            "EU/NATO membership provides institutional stability"
        ],
        "outlook": "Czech economy depends on European auto sector and industrial demand. China-Japan sanctions signal broader supply chain fragmentation risk. CNB rate path provides flexibility.",
        "investor_implications": "PX index sensitive to European industrial cycle. CZK relatively stable. Czech auto sector suppliers face broader trade uncertainty.",
        "data_quality_note": "Czech macro data is high quality from CNB and CZSO sources."
    }


def generate_narrative_grc(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Greece benefits from tourism growth and EU recovery funds. "
            "GDP growth improving. Shipping sector faces mixed signals from Hormuz rerouting. "
            "Greek shipping operators may benefit from higher freight rates."
        ),
        "key_changes_this_week": [
            "Shipping sector faces mixed signals from Hormuz rerouting",
            "Tourism growth positive but regional instability adds event risk",
            "GDP improving with EU recovery fund support"
        ],
        "outlook": "Greece's shipping industry is a net beneficiary of higher freight rates. Tourism season approaching with regional instability as the key risk. Fiscal position continues improving under EU framework.",
        "investor_implications": "Greek shipping stocks benefit from freight rate surge. Athens General Index offers EU peripheral recovery exposure. Greek tourism stocks face event risk.",
        "data_quality_note": "Greece macro data is moderate-to-high quality from ELSTAT and BOG."
    }


def generate_narrative_prt(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Portugal's economy grows steadily with tourism and tech sector support. "
            "Limited direct exposure to Hormuz crisis. "
            "EU-Mercosur agreement benefits Portuguese-speaking trade links with Brazil."
        ),
        "key_changes_this_week": [
            "EU-Mercosur agreement benefits Portuguese-Brazilian trade links",
            "Limited direct Hormuz exposure",
            "GDP growth steady with tourism support"
        ],
        "outlook": "Portugal's growth trajectory supported by tourism, tech sector, and EU fund absorption. EU-Mercosur opens enhanced Brazil trade channel. Fiscal position improving.",
        "investor_implications": "PSI index offers Iberian growth exposure. Portuguese government bonds at reasonable spreads. Tourism sector faces modest regional event risk.",
        "data_quality_note": "Portugal macro data is high quality from INE and BdP sources."
    }


def generate_narrative_fin(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Finland's economy faces moderate headwinds from the global environment. "
            "NATO membership strengthens security positioning near Russia. "
            "Technology sector (Nokia) provides growth base. "
            "Limited direct Hormuz exposure."
        ),
        "key_changes_this_week": [
            "NATO membership provides security stability near Russia",
            "Global trade disruption adds modest headwinds",
            "Technology sector provides growth base"
        ],
        "outlook": "Finland benefits from NATO security umbrella and technology sector resilience. Defense spending increase supports domestic demand. Russia border proximity remains structural risk factor.",
        "investor_implications": "Helsinki exchange offers Nordic tech and defense exposure. Finnish government bonds are safe-haven quality. Nokia benefits from 5G/defense communication demand.",
        "data_quality_note": "Finland macro data is high quality from Statistics Finland and BOF."
    }


def generate_narrative_irl(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ireland's tech-heavy economy faces mixed signals from global crisis. "
            "MNC tax base provides fiscal strength. "
            "Limited direct Hormuz exposure. "
            "Housing and cost-of-living challenges persist domestically."
        ),
        "key_changes_this_week": [
            "Global tech sector faces mixed signals from geopolitical disruption",
            "MNC tax revenue continues supporting fiscal position",
            "Limited direct Hormuz exposure"
        ],
        "outlook": "Ireland's MNC-driven economy is relatively insulated from direct crisis effects. Tech sector may face volatility from trade fragmentation. EU single market access remains structural advantage.",
        "investor_implications": "ISEQ index dominated by MNC dynamics. Irish government bonds at tight spreads. Tech MNC headquarters provide tax base resilience.",
        "data_quality_note": "Ireland macro data is high quality from CSO and CBI sources."
    }


def generate_narrative_nzl(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "New Zealand's agricultural export economy faces moderate impact from global trade disruption. "
            "GDP growth stable. China demand deceleration is the key risk given export concentration. "
            "Five Eyes membership maintains intelligence sharing. "
            "Limited direct Hormuz exposure."
        ),
        "key_changes_this_week": [
            "China demand deceleration creates export headwinds",
            "Limited direct Hormuz exposure",
            "GDP growth stable with contained inflation"
        ],
        "outlook": "New Zealand's agricultural exports face China demand risk. RBNZ rate path may adjust to external conditions. Housing market dynamics domestic focus.",
        "investor_implications": "NZX offers agricultural and dairy sector exposure. NZD under modest pressure from China demand concerns. NZ government bonds safe-haven quality.",
        "data_quality_note": "New Zealand macro data is high quality from StatsNZ and RBNZ."
    }


def generate_narrative_mar(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Morocco benefits from its position as a manufacturing and logistics hub for Europe and Africa. "
            "Automotive and phosphate sectors provide diversified export base. "
            "Limited direct Hormuz exposure but oil import costs add pressure. "
            "Political stability maintained under monarchy."
        ),
        "key_changes_this_week": [
            "Oil import costs increase from Hormuz crisis",
            "Manufacturing export base provides economic stability",
            "Phosphate exports benefit from agricultural input demand"
        ],
        "outlook": "Morocco's diversified economy and EU proximity provide structural advantages. Automotive sector benefits from nearshoring to Europe. Phosphate exports benefit from global food security concerns.",
        "investor_implications": "MASI index offers North Africa/Europe bridge exposure. Moroccan sovereign bonds at moderate yields. OCP phosphate benefits from food security demand.",
        "data_quality_note": "Morocco macro data is moderate quality from HCP and BAM."
    }


# ============================================================
# TIER 3 NARRATIVE GENERATORS (brief summaries)
# ============================================================

def generate_tier3_narrative(country_data, trends, alerts, code, name):
    """Generate brief Tier 3 narrative."""
    alert_texts = []
    for a in alerts:
        alert_texts.append(f"{a['severity'].upper()}: {a.get('headline', a.get('title', 'Alert'))}")

    trend_summary = []
    for t in trends:
        factor = t.get("factor_path", "").split(".")[-1]
        trend_summary.append(f"{factor}: {t.get('trend', 'N/A')}")

    gdp = get_macro_value(country_data, "gdp_real_growth_pct")
    inflation = get_macro_value(country_data, "inflation_cpi_pct")
    credit = get_macro_value(country_data, "sovereign_credit_rating", "N/A")

    has_alerts = len(alerts) > 0
    has_critical = any(a.get("severity") == "critical" for a in alerts)

    if has_critical:
        quality_note = f"Tier 3 country with basic coverage. {len(alerts)} active alert(s) including critical."
    elif has_alerts:
        quality_note = f"Tier 3 country with basic coverage. {len(alerts)} active alert(s)."
    else:
        quality_note = "Tier 3 country with basic coverage only."

    exec_summary = f"{name}: GDP growth at {fmt_pct(gdp)}, inflation at {fmt_pct(inflation)}, credit rating {credit}."
    if alert_texts:
        exec_summary += " " + " ".join(alert_texts[:2]) + "."

    changes = []
    if alert_texts:
        for at in alert_texts[:3]:
            changes.append(at)
    if not changes:
        changes = ["No significant changes this week"]

    outlook = f"{name} outlook requires monitoring. "
    if has_critical:
        outlook += "Critical-level alerts warrant close attention. "
    outlook += "Oil price surge affects all energy importers."

    implications = "Frontier market risk applies. "
    if has_critical:
        implications += "Elevated risk -- reduce exposure where possible."
    else:
        implications += "Monitor for developments relevant to sector exposure."

    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": exec_summary,
        "key_changes_this_week": changes,
        "outlook": outlook,
        "investor_implications": implications,
        "data_quality_note": quality_note
    }


# Special Tier 3 narratives for countries with critical alerts
def generate_narrative_eth(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ethiopia is in selective default (SD/Ca/RD) with a 2,700 bps political risk premium. "
            "TPLF-government clashes have resumed, threatening the Pretoria peace agreement. "
            "Elections scheduled June 1, 2026 in a fraught environment with TPLF legal status revoked. "
            "GDP growth at 7.2% appears strong but is distorted by low base effects and data quality concerns."
        ),
        "key_changes_this_week": [
            "TPLF-government clashes resumed -- Tigray conflict risk (major)",
            "Sovereign credit at selective default (SD/Ca/RD)",
            "Elections scheduled June 1, 2026 -- TPLF legal status revoked",
            "Political risk premium at 2,700 bps"
        ],
        "outlook": "Ethiopia faces rising conflict risk ahead of June elections. Debt restructuring remains incomplete. Telecom privatization (Safaricom entry) provides one positive structural story.",
        "investor_implications": "Ethiopia is effectively uninvestable at selective default. Avoid all exposure. Monitor debt restructuring progress for eventual recovery opportunity.",
        "data_quality_note": "Ethiopia macro data is low quality. Selective default credit rating. CRITICAL alert active."
    }


def generate_narrative_mmr(country_data, trends, alerts):
    return {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Myanmar is effectively a failed state. The military junta controls only 21% of territory, five years after the coup. "
            "GDP growth at -2.7%. Inflation at 31%. Political risk premium at 2,000 bps. "
            "No legitimate government, no functioning economy."
        ),
        "key_changes_this_week": [
            "Military controls only 21% of territory (ongoing civil war)",
            "GDP contracting at -2.7%; inflation at 31%",
            "Political risk premium at 2,000 bps"
        ],
        "outlook": "Myanmar has no visible path to stability. Resistance forces control majority of territory. Humanitarian crisis deepening. No international engagement pathway under junta.",
        "investor_implications": "Myanmar is completely uninvestable. Total write-off for any existing exposure. No recovery pathway visible.",
        "data_quality_note": "Myanmar macro data is extremely low quality under civil war conditions. CRITICAL alert active."
    }


# ============================================================
# DISPATCH TABLE
# ============================================================

CUSTOM_GENERATORS = {
    # Tier 1 - detailed
    "USA": generate_narrative_usa,
    "CHN": generate_narrative_chn,
    "JPN": generate_narrative_jpn,
    "DEU": generate_narrative_deu,
    "GBR": generate_narrative_gbr,
    "FRA": generate_narrative_fra,
    "IND": generate_narrative_ind,
    "ITA": generate_narrative_ita,
    "CAN": generate_narrative_can,
    "KOR": generate_narrative_kor,
    "RUS": generate_narrative_rus,
    "BRA": generate_narrative_bra,
    "AUS": generate_narrative_aus,
    "ESP": generate_narrative_esp,
    "MEX": generate_narrative_mex,
    "IDN": generate_narrative_idn,
    "NLD": generate_narrative_nld,
    "SAU": generate_narrative_sau,
    "TUR": generate_narrative_tur,
    "CHE": generate_narrative_che,
    "POL": generate_narrative_pol,
    "SWE": generate_narrative_swe,
    "NOR": generate_narrative_nor,
    "ISR": generate_narrative_isr,
    "ARE": generate_narrative_are,
    "SGP": generate_narrative_sgp,
    "TWN": generate_narrative_twn,
    "THA": generate_narrative_tha,
    "MYS": generate_narrative_mys,
    "ZAF": generate_narrative_zaf,
    # Tier 2 - moderate detail
    "IRN": generate_narrative_irn,
    "PAK": generate_narrative_pak,
    "ARG": generate_narrative_arg,
    "UKR": generate_narrative_ukr,
    "QAT": generate_narrative_qat,
    "KWT": generate_narrative_kwt,
    "OMN": generate_narrative_omn,
    "NGA": generate_narrative_nga,
    "EGY": generate_narrative_egy,
    "PHL": generate_narrative_phl,
    "BGD": generate_narrative_bgd,
    "VNM": generate_narrative_vnm,
    "COL": generate_narrative_col,
    "CHL": generate_narrative_chl,
    "PER": generate_narrative_per,
    "IRQ": generate_narrative_irq,
    "KAZ": generate_narrative_kaz,
    "ROU": generate_narrative_rou,
    "CZE": generate_narrative_cze,
    "GRC": generate_narrative_grc,
    "PRT": generate_narrative_prt,
    "FIN": generate_narrative_fin,
    "IRL": generate_narrative_irl,
    "NZL": generate_narrative_nzl,
    "MAR": generate_narrative_mar,
    # Tier 3 - special (critical alerts)
    "ETH": generate_narrative_eth,
    "MMR": generate_narrative_mmr,
}


def main():
    print("=" * 60)
    print("AGENT 13: Country Profile Synthesizer")
    print(f"Run ID: {RUN_ID} | Date: 2026-03-02")
    print("=" * 60)

    # Load input data
    print("\nLoading input data...")
    country_list = load_json(COUNTRY_LIST_FILE)
    alerts_data = load_json(ALERTS_FILE)

    # Load trends (large file, read in parts)
    print("Loading trend estimates...")
    trends_data = load_json(TRENDS_FILE)

    # Build complete country list with tiers
    all_countries = []
    for tier_key, tier_data in country_list["tiers"].items():
        tier_num = int(tier_key.split("_")[1])
        for c in tier_data["countries"]:
            all_countries.append({
                "code": c["code"],
                "name": c["name"],
                "region": c["region"],
                "tier": tier_num
            })

    print(f"Processing {len(all_countries)} countries...")
    print(f"  Tier 1: {sum(1 for c in all_countries if c['tier'] == 1)} countries (detailed)")
    print(f"  Tier 2: {sum(1 for c in all_countries if c['tier'] == 2)} countries (moderate)")
    print(f"  Tier 3: {sum(1 for c in all_countries if c['tier'] == 3)} countries (brief)")

    processed = 0
    errors = []

    for country in all_countries:
        code = country["code"]
        name = country["name"]
        tier = country["tier"]

        country_file = os.path.join(DATA_DIR, f"{code}.json")

        if not os.path.exists(country_file):
            errors.append(f"{code}: file not found at {country_file}")
            continue

        try:
            country_data = load_json(country_file)
            country_trends = get_country_trends(trends_data, code)
            country_alerts = get_country_alerts(alerts_data, code)

            # Generate narrative
            if code in CUSTOM_GENERATORS:
                narrative = CUSTOM_GENERATORS[code](country_data, country_trends, country_alerts)
            else:
                # Tier 3 fallback
                narrative = generate_tier3_narrative(country_data, country_trends, country_alerts, code, name)

            # Update the country file
            country_data["narrative"] = narrative

            # Also update top-level convenience fields
            country_data["code"] = code
            country_data["name"] = name
            if "executive_summary" in narrative:
                country_data["executive_summary"] = narrative["executive_summary"]
            if "key_changes_this_week" in narrative:
                country_data["key_changes"] = narrative["key_changes_this_week"]
            if "outlook" in narrative:
                country_data["outlook"] = narrative["outlook"]
            if "investor_implications" in narrative:
                country_data["investor_implications"] = narrative["investor_implications"]

            # Update active_alerts convenience field
            active_alerts = []
            for a in country_alerts:
                active_alerts.append({
                    "severity": a.get("severity"),
                    "title": a.get("title", a.get("headline")),
                    "description": a.get("description", a.get("details"))
                })
            if active_alerts:
                country_data["active_alerts"] = active_alerts

            save_json(country_file, country_data)
            processed += 1

            tier_label = {1: "TIER1", 2: "TIER2", 3: "TIER3"}[tier]
            alert_count = len(country_alerts)
            trend_count = len(country_trends)
            print(f"  [{tier_label}] {code} ({name}): narrative updated | {alert_count} alerts | {trend_count} trends")

        except Exception as e:
            errors.append(f"{code}: {str(e)}")
            print(f"  ERROR {code}: {str(e)}")

    # Summary
    print("\n" + "=" * 60)
    print(f"AGENT 13 COMPLETE")
    print(f"  Processed: {processed}/{len(all_countries)} countries")
    print(f"  Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

    # Update run log
    run_log_path = os.path.join(BASE, "staging", "run_log.json")
    if os.path.exists(run_log_path):
        try:
            run_log = load_json(run_log_path)
        except:
            run_log = {}
    else:
        run_log = {}

    run_log["agent_13"] = {
        "status": "completed" if not errors else "completed_with_errors",
        "completed_at": GENERATED_AT,
        "run_id": RUN_ID,
        "countries_processed": processed,
        "countries_total": len(all_countries),
        "errors": errors
    }
    save_json(run_log_path, run_log)

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
