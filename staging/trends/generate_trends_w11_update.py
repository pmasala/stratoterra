#!/usr/bin/env python3
"""
Agent 10 (Trend Estimator) — 2026-W11 Update (2026-03-14)
Generates quarterly trend estimates for 11 factors across 55 Tier 1+2 countries.
Updates country JSON files and writes staging/trends/trend_estimates_2026-03-14.json
"""

import json
import os
from datetime import datetime
from copy import deepcopy

BASE = "/home/pietro/stratoterra"
DATA_DIR = os.path.join(BASE, "data/countries")
STAGING_DIR = os.path.join(BASE, "staging/trends")
OUTPUT_FILE = os.path.join(STAGING_DIR, "trend_estimates_2026-03-14.json")
TIMESTAMP = "2026-03-14T00:00:00Z"

# All 55 Tier 1 + Tier 2 countries
TIER1 = [
    "USA", "CHN", "JPN", "DEU", "GBR", "IND", "FRA", "ITA", "CAN", "KOR",
    "AUS", "BRA", "RUS", "MEX", "ESP", "IDN", "NLD", "SAU", "TUR", "CHE",
    "POL", "SWE", "NOR", "ISR", "ARE", "SGP", "IRL", "ZAF", "TWN", "THA"
]
TIER2 = [
    "ARG", "CHL", "COL", "PER", "EGY", "NGA", "KEN", "MAR", "GHA", "PAK",
    "BGD", "VNM", "MYS", "PHL", "KAZ", "UZB", "UKR", "IRN", "IRQ", "QAT",
    "KWT", "OMN", "CZE", "ROU", "HUN"
]
ALL_COUNTRIES = TIER1 + TIER2

# Countries significantly affected by this week's events
HIGH_IMPACT = {"IRN", "ISR", "USA", "SAU", "ARE", "KWT", "QAT", "IRQ"}
MODERATE_IMPACT = {
    "DEU", "GBR", "FRA", "JPN", "KOR", "IND", "RUS", "TUR", "BRA", "AUS",
    "CAN", "NOR", "NGA", "EGY", "UKR", "CHN", "MEX", "ARG", "PAK", "OMN",
    "IDN", "ZAF", "POL", "LBN"
}

# Oil exporters (benefit from high prices, unless Hormuz-blocked)
OIL_EXPORTERS_NON_HORMUZ = {"USA", "CAN", "NOR", "BRA", "NGA", "ARG", "COL", "GHA", "KAZ", "AZE", "RUS"}
OIL_EXPORTERS_HORMUZ = {"SAU", "ARE", "KWT", "QAT", "OMN", "IRQ", "IRN"}
OIL_IMPORTERS_HEAVY = {"JPN", "KOR", "IND", "DEU", "GBR", "FRA", "ITA", "ESP", "TUR", "THA", "PAK", "BGD", "EGY", "ZAF", "PHL"}

# ============================================================
# TREND ESTIMATION LOGIC
# ============================================================

def get_country_profile(code):
    """Load country JSON and extract relevant values."""
    path = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        data = json.load(f)

    macro = data.get("macroeconomic", {})
    military = data.get("military", {})
    derived = data.get("derived", {})
    institutions = data.get("institutions", {})

    def get_val(section, key):
        item = section.get(key, {})
        if isinstance(item, dict):
            return item.get("value")
        return item

    return {
        "code": code,
        "name": data.get("country_name", code),
        "tier": data.get("tier", 3),
        "region": data.get("region", ""),
        "gdp_growth": get_val(macro, "gdp_real_growth_pct"),
        "inflation": get_val(macro, "inflation_cpi_pct"),
        "current_account": get_val(macro, "current_account_pct_gdp"),
        "govt_debt": get_val(macro, "govt_debt_pct_gdp"),
        "exchange_rate": get_val(macro, "exchange_rate_vs_usd"),
        "bond_yield": get_val(macro, "sovereign_bond_yield_10yr_pct"),
        "policy_rate": get_val(macro, "central_bank_policy_rate_pct"),
        "mil_pct_gdp": get_val(military, "military_expenditure_pct_gdp"),
        "cnpi": get_val(derived, "composite_national_power_index"),
        "risk_score": get_val(derived, "overall_investment_risk_score"),
        "pol_stability": get_val(institutions, "wgi_political_stability"),
        "data": data
    }


def estimate_trends(profile):
    """Generate 11 trend estimates for a country based on current context."""
    code = profile["code"]
    estimates = []

    # Determine country context
    is_war_zone = code in {"IRN", "ISR"}
    is_hormuz_blocked = code in OIL_EXPORTERS_HORMUZ
    is_oil_exporter_safe = code in OIL_EXPORTERS_NON_HORMUZ
    is_oil_importer = code in OIL_IMPORTERS_HEAVY
    is_high_impact = code in HIGH_IMPACT
    is_conflict_active = code in {"UKR", "RUS", "IRN", "ISR"}

    # ---- 1. GDP REAL GROWTH ----
    gdp_val = profile["gdp_growth"]
    if code == "IRN":
        gdp_trend = "strong_decrease"
        gdp_conf = 0.95
        gdp_reason = "War entering third week with 6,000+ targets struck. Infrastructure destruction accelerating. Hormuz mined, halting oil exports (~70% of revenue). New Supreme Leader Mojtaba Khamenei defiant. GDP trajectory: deep contraction -15% to -25% annualized."
        gdp_evidence = ["6,000+ targets struck by US-Israel coalition", "1,348 civilians killed, 17,000+ injured", "Strait of Hormuz effectively closed by IRGC mines", "New Supreme Leader vows continued resistance"]
        gdp_counter = ["Iranian resilience and war economy adaptation"]
        gdp_investor = "Iran economy in freefall. No investable assets remain accessible."
    elif code == "ISR":
        gdp_trend = "strong_decrease"
        gdp_conf = 0.90
        gdp_reason = "Multi-front war expanding. Lebanon operations dramatically escalated — 680+ killed, 800,000 displaced, IDF advancing past Litani River. Hezbollah retaliatory strikes on northern Israel. War costs mounting."
        gdp_evidence = ["Lebanon war expansion — 680+ killed", "IDF pushing past Litani to Zahrani River", "Hezbollah retaliation for Khamenei killing", "Military reserves mobilized"]
        gdp_counter = ["US military support and aid packages", "Tech sector partially insulated"]
        gdp_investor = "Israel GDP contraction deepening as multi-front war expands. Defense stocks only beneficiary."
    elif code == "SAU":
        gdp_trend = "strong_decrease"
        gdp_conf = 0.88
        gdp_reason = "Hormuz blockade remains effective — new Supreme Leader vows 'not a litre of oil' will pass. Oil revenue disruption catastrophic despite $100+ prices. Limited pipeline alternatives cannot substitute maritime capacity."
        gdp_evidence = ["Hormuz declared 'closed' by IRGC on March 4", "New Supreme Leader maintains blockade pledge", "Three more commercial ships struck this week", "US Navy escorts 'not ready' per Treasury Sec Bessent"]
        gdp_counter = ["East-West pipeline to Red Sea provides some outlet", "SWF reserves buffer fiscal impact"]
        gdp_investor = "Saudi GDP contraction inevitable as export revenue blocked. Vision 2030 timeline severely impacted."
    elif code == "KWT":
        gdp_trend = "strong_decrease"
        gdp_conf = 0.92
        gdp_reason = "Kuwait has no pipeline alternative to Hormuz. Near-total economic paralysis as maritime trade blocked. Oil revenue effectively zero. Economy dependent on 90%+ oil exports."
        gdp_evidence = ["No non-Hormuz export routes", "90%+ fiscal dependence on oil", "Hormuz mines prevent tanker passage"]
        gdp_counter = ["SWF reserves provide fiscal buffer"]
        gdp_investor = "Kuwait GDP in severe contraction. Most exposed Gulf state to Hormuz closure."
    elif code == "QAT":
        gdp_trend = "strong_decrease"
        gdp_conf = 0.90
        gdp_reason = "World's largest LNG exporter completely offline. Qatar F-15QA fighters now in direct combat — intercepted Iranian bombers targeting US base. Economy paralyzed by Hormuz closure."
        gdp_evidence = ["LNG exports blocked by Hormuz mines", "Qatar jets intercepted Iranian bombers near US base", "All maritime trade suspended"]
        gdp_counter = ["Massive SWF and fiscal reserves"]
        gdp_investor = "Qatar LNG revenue eliminated. Direct military engagement adds security premium."
    elif is_hormuz_blocked:  # IRQ, OMN, ARE
        gdp_trend = "strong_decrease"
        gdp_conf = 0.85
        gdp_reason = f"Hormuz blockade severely disrupting oil exports. {profile['name']} export revenue sharply curtailed. Limited alternative export routes."
        gdp_evidence = ["Hormuz mines block maritime oil trade", "Oil revenue dominant fiscal source"]
        gdp_counter = ["Some pipeline alternatives may partially offset", "IEA strategic reserve release"]
        gdp_investor = f"{profile['name']} GDP under severe pressure from Hormuz disruption."
    elif code == "USA":
        gdp_trend = "stable"
        gdp_conf = 0.68
        gdp_reason = "US GDP stable but facing cross-currents. Energy self-sufficiency provides buffer, but Iran war costs, Section 301 trade escalation against 76 trading partners, and oil shock consumer impact create headwinds. February CPI benign but forward-looking indicators deteriorating. 5 recession warning signs flagged."
        gdp_evidence = ["Energy self-sufficiency buffers oil shock", "Section 301 investigations (16 overcapacity + 60 forced labor)", "Gas prices at $3.63/gal — 22-month high", "5 recession warning signs identified", "War spending adding to fiscal pressure"]
        gdp_counter = ["Consumer spending resilient so far", "Strong labor market provides support"]
        gdp_investor = "US GDP stable but recession risk rising from war costs and trade escalation."
    elif is_oil_exporter_safe:
        if code == "RUS":
            gdp_trend = "growth"
            gdp_conf = 0.78
            gdp_reason = "Russia emerging as major beneficiary of Iran war. Oil above $100/bbl boosting revenue. Iranian oil off market increases Russian pricing power. War economy continues to drive GDP. Shadow fleet expanding in Gulf of Oman."
            gdp_evidence = ["Oil windfall at $100+/bbl", "Iranian competition eliminated from market", "War economy spending sustains GDP", "Shadow fleet oil transfers expanding"]
            gdp_counter = ["Western sanctions limit full monetization", "War costs in Ukraine continue to drain resources"]
            gdp_investor = "Russia revenue windfall from oil. Best macro position since pre-2022 sanctions."
        elif code == "NOR":
            gdp_trend = "growth"
            gdp_conf = 0.78
            gdp_reason = "Norway's North Sea production benefits from $100+ oil without Hormuz exposure. Energy windfall boosting fiscal position. European energy dependency on Norwegian gas increasing."
            gdp_evidence = ["Non-Hormuz production routes", "European gas demand redirecting to Norway", "Oil at $100+/bbl"]
            gdp_counter = ["Global recession risk could reduce demand", "Section 301 investigation announced"]
            gdp_investor = "Norway fiscal windfall. European energy reorientation favors Norwegian assets."
        elif code == "BRA":
            gdp_trend = "growth"
            gdp_conf = 0.78
            gdp_reason = "Brazil as net oil exporter benefits from price surge. Pre-salt production boosting export revenues. Geographically insulated from Gulf conflict. Commodity basket (iron, soy, oil) all elevated."
            gdp_evidence = ["Net oil exporter status", "Pre-salt production at record levels", "Commodity basket elevated"]
            gdp_counter = ["Global demand slowdown could offset", "High domestic interest rates constrain growth"]
            gdp_investor = "Brazil benefiting from commodity windfall. Oil exporter premium intact."
        elif code == "CAN":
            gdp_trend = "growth"
            gdp_conf = 0.72
            gdp_reason = "Canada benefits from oil/gas windfall at $100+ prices. Non-Hormuz production routes. But US Section 301 trade investigations and tariff tensions create headwinds."
            gdp_evidence = ["Oil sands revenue surge", "Non-Hormuz export routes", "LNG export capacity expanding"]
            gdp_counter = ["US trade tensions and Section 301 investigations", "Housing market fragility"]
            gdp_investor = "Canada oil windfall offset by US trade policy uncertainty."
        elif code == "NGA":
            gdp_trend = "growth"
            gdp_conf = 0.72
            gdp_reason = "Nigeria benefits from oil price surge to $100+/bbl. Atlantic coast exports not affected by Hormuz. Dangote refinery ramp-up adds domestic refining capacity."
            gdp_evidence = ["Atlantic coast exports secure", "Oil at $100+/bbl", "Dangote refinery adding capacity"]
            gdp_counter = ["Domestic refining challenges persist", "Naira instability"]
            gdp_investor = "Nigeria oil windfall positive for GDP but currency risk persists."
        elif code == "ARG":
            gdp_trend = "stable"
            gdp_conf = 0.72
            gdp_reason = "Argentina GDP negative under Milei shock therapy but becoming net energy exporter via Vaca Muerta — valuable as Gulf crisis drives oil prices higher. Mixed signals as structural reform pain offsets energy windfall."
            gdp_evidence = ["Vaca Muerta net energy exports", "Oil windfall at $100+/bbl", "Milei reform credibility rising"]
            gdp_counter = ["GDP still negative at -1.3%", "Shock therapy creating domestic demand weakness"]
            gdp_investor = "Argentina GDP bottoming. Energy exporter transition provides medium-term upside."
        else:
            gdp_trend = "growth"
            gdp_conf = 0.68
            gdp_reason = f"{profile['name']} benefits from non-Hormuz oil/commodity exports at elevated prices."
            gdp_evidence = ["Non-Hormuz export routes", "Oil/commodity prices elevated"]
            gdp_counter = ["Global demand slowdown risk"]
            gdp_investor = f"{profile['name']} benefits from commodity windfall."
    elif is_oil_importer:
        if code == "DEU":
            gdp_trend = "decrease"
            gdp_conf = 0.85
            gdp_reason = "Germany facing continued GDP headwinds from oil shock. Section 301 investigations add new trade risk. VW job cuts (50,000) deepening industrial recession. Energy costs rising. Stagflation scenario forming."
            gdp_evidence = ["Oil at $100+/bbl", "Section 301 investigation targeting Germany", "VW slashing 50,000 jobs", "European markets in correction"]
            gdp_counter = ["ECB policy response could provide relief", "Infrastructure spending plans"]
            gdp_investor = "Germany industrial recession deepening. Auto sector under dual pressure from energy costs and trade risk."
        elif code == "JPN":
            gdp_trend = "decrease"
            gdp_conf = 0.85
            gdp_reason = "Japan heavily dependent on Gulf oil transiting Hormuz. Oil at $100+/bbl with IEA 400M barrel SPR release providing only partial relief. North Korea fired 10 ballistic missiles, adding security costs. Section 301 investigation adds trade risk."
            gdp_evidence = ["Gulf oil dependency via Hormuz", "DPRK fired 10 missiles during Freedom Shield", "IEA SPR release only partially offsets supply loss", "Section 301 investigation targeting Japan"]
            gdp_counter = ["SPR release provides temporary relief", "Yen weakness supports exporters"]
            gdp_investor = "Japan GDP under dual pressure from energy shock and NE Asia security deterioration."
        elif code == "KOR":
            gdp_trend = "decrease"
            gdp_conf = 0.82
            gdp_reason = "South Korea vulnerable to oil shock and elevated security costs. DPRK fired 10 ballistic missiles during Freedom Shield exercises. US military stretched across Middle East and Korea theaters simultaneously. Section 301 investigation adds trade headwind."
            gdp_evidence = ["DPRK 10-missile salvo — largest single launch", "Oil dependency via Hormuz routes", "US-ROK Freedom Shield exercise (18,000 troops)", "Section 301 investigation targeting Korea"]
            gdp_counter = ["Strong export manufacturing base", "DPRK provocations typically short-lived"]
            gdp_investor = "South Korea facing dual threat: energy costs plus elevated DPRK tensions."
        elif code == "IND":
            gdp_trend = "decrease"
            gdp_conf = 0.82
            gdp_reason = "India heavily dependent on Gulf oil. Oil at $100+/bbl adding 1-2pp to import bill. Section 301 investigation on both overcapacity and forced labor adds trade uncertainty. Stranded Iranian sailors creating diplomatic tension."
            gdp_evidence = ["Heavy Gulf oil dependency", "Oil at $100+/bbl", "Section 301 investigations targeting India", "Stranded Iranian sailors diplomatic issue"]
            gdp_counter = ["Diversifying oil sources including Russian crude", "Strong domestic consumption base"]
            gdp_investor = "India growth trajectory downgraded by energy shock. Trade policy uncertainty from US adds risk."
        elif code == "TUR":
            gdp_trend = "decrease"
            gdp_conf = 0.78
            gdp_reason = "Turkey facing oil shock pressure with 100% energy import dependency. Regional instability from Iran war spilling over. NATO obligations pull in competing directions. Section 301 investigations are not directly targeting Turkey but regional trade disruption affects supply chains."
            gdp_evidence = ["100% oil import dependency", "Regional instability spillover", "Inflation already at 58.5%"]
            gdp_counter = ["Tourism resilience", "Central bank tightening cycle showing results"]
            gdp_investor = "Turkey GDP under pressure from oil costs and regional instability."
        elif code == "PAK":
            gdp_trend = "decrease"
            gdp_conf = 0.82
            gdp_reason = "Pakistan heavily dependent on Gulf oil transiting Hormuz. Oil at $100+/bbl devastating for already fragile economy. IMF program constrains fiscal response. Neighboring Iran conflict creates refugee and security pressure."
            gdp_evidence = ["Heavy Gulf oil dependency via Hormuz", "IMF program constraints", "Iran conflict proximity creates spillover risk"]
            gdp_counter = ["IMF disbursements continue", "Remittance flows from Gulf relatively stable"]
            gdp_investor = "Pakistan most vulnerable to Hormuz disruption among large economies."
        elif code == "EGY":
            gdp_trend = "decrease"
            gdp_conf = 0.82
            gdp_reason = "Egypt facing severe oil import cost pressure, Suez Canal revenue uncertainty, and tourism disruption from regional conflict. Food import costs rising. IMF program constrains fiscal response."
            gdp_evidence = ["Heavy oil import dependency", "Suez Canal revenue at risk from conflict", "Tourism disrupted by Middle East war", "Food import costs rising"]
            gdp_counter = ["IMF program provides some stability", "Gas production partially offsets oil imports"]
            gdp_investor = "Egypt GDP under triple pressure: oil costs, Suez uncertainty, and tourism disruption."
        else:
            gdp_trend = "decrease"
            gdp_conf = 0.72
            gdp_reason = f"{profile['name']} facing GDP headwinds from oil shock at $100+/bbl. Energy costs rising for oil-importing economy."
            gdp_evidence = ["Oil at $100+/bbl", "Energy import costs rising"]
            gdp_counter = ["G7 SPR release provides partial relief"]
            gdp_investor = f"{profile['name']} GDP under pressure from energy costs."
    elif code == "UKR":
        gdp_trend = "stable"
        gdp_conf = 0.68
        gdp_reason = "Ukraine GDP stable amid frozen conflict. Peace talks '90% complete' but stalled. Russia launched large-scale drone/missile barrage killing 10+ in Kharkiv. Zelenskiy engaging Saudi Arabia diplomatically. EU funding flowing via non-Hungary channels."
        gdp_evidence = ["Peace talks stalled at '90% complete'", "Russia large-scale drone/missile attacks continue", "EU funding flowing", "Zelenskiy-MBS diplomatic call"]
        gdp_counter = ["Infrastructure damage accumulating", "War costs unsustainable without foreign aid"]
        gdp_investor = "Ukraine GDP stable but fragile. Reconstruction opportunity contingent on peace."
    elif code == "CHN":
        gdp_trend = "stable"
        gdp_conf = 0.72
        gdp_reason = "China relatively insulated from Hormuz crisis via diversified oil imports and Russian pipeline supply. But Section 301 overcapacity investigations across 21 sectors plus forced labor probe against 60 countries create major new trade headwinds. Oil price surge adds modest cost pressure."
        gdp_evidence = ["Section 301 overcapacity investigation targeting China", "Section 301 forced labor investigation (60 countries)", "Diversified oil supply routes", "Russian pipeline imports buffer Hormuz risk"]
        gdp_counter = ["Two Sessions stimulus signals", "Tech/AI investment push", "SPR reserves adequate"]
        gdp_investor = "China growth stable but Section 301 trade escalation poses medium-term headwind."
    elif code == "SGP":
        gdp_trend = "stable"
        gdp_conf = 0.68
        gdp_reason = "Singapore benefits from trade rerouting away from Hormuz but Section 301 overcapacity investigation adds trade uncertainty. Financial hub gains from geopolitical hedging."
        gdp_evidence = ["Trade rerouting benefits", "Section 301 investigation targeting Singapore", "Financial hub premium"]
        gdp_counter = ["Global trade slowdown risk", "Regional uncertainty from DPRK missiles"]
        gdp_investor = "Singapore GDP stable. Financial hub gains offset trade policy uncertainty."
    elif code == "VNM":
        gdp_trend = "stable"
        gdp_conf = 0.68
        gdp_reason = "Vietnam general election March 15 ensures political continuity. Section 301 investigations create trade headwind. Oil import costs rising but manufacturing base resilient."
        gdp_evidence = ["General election for continuity — 73.5M voters", "Section 301 investigation targeting Vietnam", "Manufacturing base attracting supply chain shifts"]
        gdp_counter = ["Political stability supports business confidence", "FDI inflows remain strong"]
        gdp_investor = "Vietnam GDP stable. Election provides political continuity."
    else:
        gdp_trend = "stable"
        gdp_conf = 0.60
        gdp_reason = f"{profile['name']} GDP broadly stable. No direct exposure to Gulf conflict. Global oil shock creates mild headwinds."
        gdp_evidence = ["No direct Gulf conflict exposure", "Global oil prices elevated"]
        gdp_counter = ["Regional economic dynamics provide buffer"]
        gdp_investor = f"{profile['name']} GDP stable with modest energy cost pressure."

    estimates.append(make_estimate(code, "macroeconomic.gdp_real_growth_pct", gdp_val, gdp_trend, gdp_conf, gdp_reason, gdp_evidence, gdp_counter, gdp_investor))

    # ---- 2. INFLATION CPI ----
    inf_val = profile["inflation"]
    if code == "IRN":
        inf_trend, inf_conf = "strong_growth", 0.95
        inf_reason = "Hyperinflation accelerating. War entering third week. Currency collapse, supply chains destroyed, panic hoarding. New Supreme Leader's defiance ensures continued economic collapse."
        inf_evidence = ["War entering week 3", "Currency in freefall", "Supply chains destroyed"]
        inf_counter = ["Price controls may slow measured inflation"]
        inf_investor = "Iran hyperinflation. No investable monetary policy."
    elif code == "ARG":
        inf_trend, inf_conf = "decrease", 0.78
        inf_reason = "Argentina inflation decelerating under Milei shock therapy despite still extreme levels (220%). Monthly rates declining. Energy exporter status reduces oil shock pass-through."
        inf_evidence = ["Monthly CPI rates declining", "Fiscal austerity taking effect", "Energy exporter status buffers oil shock"]
        inf_counter = ["Still at 220% annual rate", "Peso depreciation creates imported inflation"]
        inf_investor = "Argentina inflation decelerating. Key Milei credibility metric."
    elif code == "TUR":
        inf_trend, inf_conf = "growth", 0.78
        inf_reason = "Turkey inflation (58.5%) pressured higher by oil shock feeding through energy, transport, and food prices. Central bank's ultra-tight policy (47.5%) struggling against commodity cost push."
        inf_evidence = ["Oil shock cost pass-through", "58.5% base already elevated", "Regional supply chain disruptions"]
        inf_counter = ["Central bank at 47.5% maintaining tight stance", "Lira stabilization efforts"]
        inf_investor = "Turkey inflation re-accelerating. Central bank credibility at stake."
    elif code == "USA":
        inf_trend, inf_conf = "growth", 0.75
        inf_reason = "US February CPI steady at 2.4% but pre-dates Iran war oil shock. Gas prices at $3.63/gal (22-month high). March/April readings will capture $100+ oil pass-through. IEA 400M barrel SPR release provides partial but insufficient offset."
        inf_evidence = ["Feb CPI 2.4% — backward-looking", "Gas at $3.63/gal, 22-month high", "IEA 400M barrel SPR release — largest ever", "Oil above $100/bbl feeding through"]
        inf_counter = ["SPR release may cap oil prices temporarily", "Fed on hold dampens demand-pull"]
        inf_investor = "US inflation re-accelerating from energy shock. Fed rate cut path delayed."
    elif is_oil_importer:
        inf_trend, inf_conf = "growth", 0.78
        inf_reason = f"{profile['name']} facing inflation pressure from oil at $100+/bbl feeding through energy, transport, and food prices. IEA 400M barrel SPR release provides only partial relief."
        inf_evidence = ["Oil at $100+/bbl", "IEA 400M barrel SPR release — largest in history", "Energy costs feeding through to consumer prices"]
        inf_counter = ["SPR release may cap energy prices temporarily", "Central bank tightening response"]
        inf_investor = f"{profile['name']} inflation rising from energy cost pass-through."
    elif is_oil_exporter_safe:
        if code == "RUS":
            inf_trend, inf_conf = "growth", 0.72
            inf_reason = "Russia inflation from war economy overheating continues. Labor market at 2.1% unemployment (historic low). Oil windfall partially offsets through stronger fiscal position but wartime demand push persists."
            inf_evidence = ["War economy overheating", "2.1% unemployment — record low", "Import substitution driving costs"]
            inf_counter = ["Oil windfall improves fiscal position", "21% policy rate restrictive"]
            inf_investor = "Russia inflation persistent from war economy dynamics."
        elif code == "NGA":
            inf_trend, inf_conf = "growth", 0.72
            inf_reason = "Nigeria inflation elevated at 33%. Oil windfall improves fiscal position but Naira instability and import dependency keep consumer prices rising."
            inf_evidence = ["Naira instability", "Import dependency for consumer goods", "33% base rate"]
            inf_counter = ["Oil revenue improves fiscal capacity", "Dangote refinery reduces fuel imports"]
            inf_investor = "Nigeria inflation elevated. Oil windfall doesn't reach consumers."
        else:
            inf_trend, inf_conf = "stable", 0.65
            inf_reason = f"{profile['name']} inflation broadly stable as oil exporter status shields from energy cost pass-through."
            inf_evidence = ["Energy exporter status", "Domestic fuel price controls"]
            inf_counter = ["Imported goods inflation from global supply chain disruption"]
            inf_investor = f"{profile['name']} inflation contained by energy self-sufficiency."
    elif is_hormuz_blocked:
        inf_trend, inf_conf = "strong_growth", 0.85
        inf_reason = f"{profile['name']} facing severe supply chain disruption from Hormuz blockade. Import costs surging. Essential goods supply constrained."
        inf_evidence = ["Hormuz blockade disrupting all maritime trade", "Import costs surging", "Food and essential goods supply constrained"]
        inf_counter = ["Government subsidies and price controls"]
        inf_investor = f"{profile['name']} inflation surging from trade disruption."
    elif code == "ISR":
        inf_trend, inf_conf = "growth", 0.78
        inf_reason = "Israel inflation rising from wartime supply disruptions, import cost pressure from oil shock, and Lebanon operations expanding. Military mobilization creates labor market distortions."
        inf_evidence = ["Wartime supply disruptions", "Lebanon operations escalating", "Oil import costs rising", "Military mobilization"]
        inf_counter = ["Tech sector deflation in some categories"]
        inf_investor = "Israel inflation rising from war disruption."
    elif code == "UKR":
        inf_trend, inf_conf = "growth", 0.68
        inf_reason = "Ukraine inflation under moderate upward pressure from oil shock and continued wartime supply disruptions. EU funding helps stabilize but Russian attacks on infrastructure increase costs."
        inf_evidence = ["Oil shock pass-through", "Russian attacks on infrastructure", "Wartime supply disruptions"]
        inf_counter = ["EU aid stabilizes economy", "Central bank credibility"]
        inf_investor = "Ukraine inflation elevated by war dynamics."
    else:
        inf_trend, inf_conf = "stable", 0.60
        inf_reason = f"{profile['name']} inflation broadly stable with modest upward pressure from global oil prices."
        inf_evidence = ["Global oil prices elevated", "Limited direct Hormuz exposure"]
        inf_counter = ["Central bank policy response", "Energy subsidies"]
        inf_investor = f"{profile['name']} inflation stable with mild upward bias."

    estimates.append(make_estimate(code, "macroeconomic.inflation_cpi_pct", inf_val, inf_trend, inf_conf, inf_reason, inf_evidence, inf_counter, inf_investor))

    # ---- 3. CURRENT ACCOUNT ----
    ca_val = profile["current_account"]
    if code == "IRN":
        ca_trend, ca_conf = "strong_decrease", 0.94
        ca_reason = "Oil export revenue eliminated by Hormuz mine-laying and US bombing. Current account swinging deeply negative. Import costs surging via overland routes."
        ca_evidence = ["Oil exports halted", "Trade routes blocked", "Currency collapse"]
        ca_counter = ["Overland trade with Iraq/Turkey continues"]
        ca_inv = "Iran current account catastrophic."
    elif is_hormuz_blocked:
        ca_trend, ca_conf = "strong_decrease", 0.88
        ca_reason = f"{profile['name']} current account severely impacted by Hormuz blockade. Oil/gas export revenue sharply curtailed. Import costs rising from alternative routes."
        ca_evidence = ["Hormuz blockade cutting exports", "Maritime trade suspended"]
        ca_counter = ["Pipeline alternatives for some exports", "SWF drawdowns"]
        ca_inv = f"{profile['name']} current account severely deteriorating."
    elif code == "USA":
        ca_trend, ca_conf = "stable", 0.68
        ca_reason = "US current account roughly stable. Energy self-sufficiency buffers oil shock. Section 301 investigations (16 overcapacity + 60 forced labor) could reduce imports medium-term. War costs add to transfers. Safe-haven dollar inflows support."
        ca_evidence = ["Energy self-sufficient", "Section 301 investigations launched", "Safe-haven capital inflows"]
        ca_counter = ["War costs adding to external transfers", "Tariff refund litigation"]
        ca_inv = "US current account stable. Competing forces offsetting."
    elif is_oil_exporter_safe:
        ca_trend, ca_conf = "growth", 0.75
        ca_reason = f"{profile['name']} current account improving as oil/commodity prices surge and non-Hormuz export routes remain secure. Trade surplus widening."
        ca_evidence = ["Non-Hormuz export routes", "Oil/commodity prices elevated"]
        ca_counter = ["Import costs rising globally"]
        ca_inv = f"{profile['name']} current account improving on commodity windfall."
    elif is_oil_importer and code in {"JPN", "KOR", "IND", "PAK"}:
        ca_trend, ca_conf = "decrease", 0.82
        ca_reason = f"{profile['name']} current account worsening from oil import bill surge at $100+/bbl. Energy import costs adding 1-2pp to deficit."
        ca_evidence = ["Oil import bill surging", "Hormuz disruption increasing costs"]
        ca_counter = ["Export volumes may partially offset", "SPR release provides temporary relief"]
        ca_inv = f"{profile['name']} current account deteriorating from energy costs."
    else:
        ca_trend, ca_conf = "decrease", 0.62
        ca_reason = f"{profile['name']} current account under modest pressure from higher energy import costs."
        ca_evidence = ["Oil import costs rising"]
        ca_counter = ["Trade balance partially offset by other factors"]
        ca_inv = f"{profile['name']} current account mildly deteriorating."

    estimates.append(make_estimate(code, "macroeconomic.current_account_pct_gdp", ca_val, ca_trend, ca_conf, ca_reason, ca_evidence, ca_counter, ca_inv))

    # ---- 4. GOVT DEBT ----
    debt_val = profile["govt_debt"]
    if code == "IRN":
        debt_trend, debt_conf = "strong_growth", 0.88
        debt_reason = "Iran debt-to-GDP ratio exploding as GDP collapses and emergency war spending surges. Nominal debt metrics meaningless given currency collapse."
        debt_evidence = ["GDP in freefall", "Emergency war spending", "Currency collapse"]
        debt_counter = ["Debt statistics unreliable in war conditions"]
        debt_inv = "Iran fiscal position catastrophic."
    elif code == "USA":
        debt_trend, debt_conf = "growth", 0.85
        debt_reason = "US debt rising from war spending (Operation Epic Fury) entering third week. Senate failed to pass war powers resolution — no legislative check on spending. $175B tariff refund SCOTUS liability. GOP House majority razor-thin at 217-214 after Kiley exit. Defense supplementals inevitable."
        debt_evidence = ["War spending unchecked after failed war powers vote", "GOP majority narrows to 217-214", "$175B tariff refund liability", "Defense spending supplementals expected"]
        debt_counter = ["Economic growth generates revenue", "Dollar reserve status provides financing advantage"]
        debt_inv = "US debt trajectory accelerating. War costs plus political constraints on fiscal policy."
    elif is_hormuz_blocked:
        debt_trend, debt_conf = "strong_growth", 0.82
        debt_reason = f"{profile['name']} debt ratio rising sharply as revenue drops from export disruption while defense and subsidy spending increases."
        debt_evidence = ["Export revenue collapsed", "Defense spending surge", "Subsidies required"]
        debt_counter = ["SWF drawdowns buffer fiscal position"]
        debt_inv = f"{profile['name']} fiscal position deteriorating rapidly."
    elif is_oil_exporter_safe:
        if code == "RUS":
            debt_trend, debt_conf = "decrease", 0.72
            debt_reason = "Russia debt ratio improving as oil windfall boosts government revenue. Fiscal surplus expanding. Low base (18.5%) provides comfort."
            debt_evidence = ["Oil windfall", "Low debt base", "Fiscal surplus"]
            debt_counter = ["War costs in Ukraine", "Sanctions limit fiscal flexibility"]
            debt_inv = "Russia fiscal position improving on oil windfall."
        else:
            debt_trend, debt_conf = "decrease", 0.68
            debt_reason = f"{profile['name']} debt ratio improving as commodity windfall boosts government revenue."
            debt_evidence = ["Commodity revenue surge", "Fiscal surplus expanding"]
            debt_counter = ["Spending pressures", "Global uncertainty"]
            debt_inv = f"{profile['name']} fiscal position improving."
    elif code == "ISR":
        debt_trend, debt_conf = "strong_growth", 0.85
        debt_reason = "Israel debt rising sharply from multi-front war spending. Lebanon operations dramatically expanded. Reserve mobilization and reconstruction costs mounting. US aid partially offsets."
        debt_evidence = ["Multi-front war (Iran + Lebanon)", "Reserve mobilization", "Lebanon expansion — 680+ killed"]
        debt_counter = ["US military and financial support"]
        debt_inv = "Israel debt trajectory steep. War duration key variable."
    else:
        debt_trend, debt_conf = "growth", 0.65
        debt_reason = f"{profile['name']} debt ratio rising modestly as oil shock reduces growth and increases government energy costs/subsidies."
        debt_evidence = ["Lower growth reduces revenue", "Energy subsidies increase spending"]
        debt_counter = ["Fiscal consolidation efforts", "Growth recovery potential"]
        debt_inv = f"{profile['name']} debt rising modestly."

    estimates.append(make_estimate(code, "macroeconomic.govt_debt_pct_gdp", debt_val, debt_trend, debt_conf, debt_reason, debt_evidence, debt_counter, debt_inv))

    # ---- 5. EXCHANGE RATE VS USD ----
    fx_val = profile["exchange_rate"]
    if code == "IRN":
        fx_trend, fx_conf = "strong_decrease", 0.95
        fx_reason = "Iran rial in freefall. War, Hormuz closure, export halt driving currency collapse. Parallel market diverging from official rate."
        fx_evidence = ["War entering week 3", "Export revenue zero", "Capital flight"]
        fx_counter = ["Capital controls limit outflows"]
        fx_inv = "Iran currency worthless for investment purposes."
    elif code == "ISR":
        fx_trend, fx_conf = "decrease", 0.82
        fx_reason = "Shekel under pressure from war expansion into Lebanon. Geopolitical risk premium elevated. BoI defending but war costs mounting."
        fx_evidence = ["Multi-front war expansion", "Capital outflow pressure", "War spending"]
        fx_counter = ["BoI intervention capacity", "US support packages"]
        fx_inv = "Shekel weakening. War duration determines trajectory."
    elif code == "SAU":
        fx_trend, fx_conf = "stable", 0.75
        fx_reason = "SAR peg to USD maintained. Central bank defending despite fiscal strain from Hormuz blockade. FX reserves ($464B) adequate for medium-term peg defense."
        fx_evidence = ["Dollar peg maintained", "FX reserves at $464B"]
        fx_counter = ["Revenue disruption creates depletion risk", "Peg defense costly"]
        fx_inv = "SAR peg holding but under growing stress."
    elif code == "USA":
        fx_trend, fx_conf = "stable", 0.80
        fx_reason = "USD strengthening as safe-haven during Middle East war. DXY at multi-month highs. War and global risk-off supporting dollar demand."
        fx_evidence = ["Safe-haven demand", "War-driven capital flows", "DXY at highs"]
        fx_counter = ["War costs and fiscal expansion long-term negative", "Fed rate cut expectations"]
        fx_inv = "USD strong on safe-haven demand."
    elif code == "RUS":
        fx_trend, fx_conf = "growth", 0.68
        fx_reason = "Ruble modestly strengthening on oil windfall at $100+/bbl. Capital controls maintaining stability. Oil revenue exceeding expectations."
        fx_evidence = ["Oil windfall", "Capital controls effective"]
        fx_counter = ["Sanctions limit convertibility", "Shadow economy distortions"]
        fx_inv = "Ruble strengthening but limited investability."
    elif is_hormuz_blocked and code != "SAU":
        fx_trend, fx_conf = "decrease", 0.78
        fx_reason = f"{profile['name']} currency under pressure from revenue collapse due to Hormuz blockade."
        fx_evidence = ["Export revenue collapsed", "Import costs rising"]
        fx_counter = ["FX reserves provide buffer", "USD peg defense if applicable"]
        fx_inv = f"{profile['name']} currency weakening."
    elif is_oil_exporter_safe:
        fx_trend, fx_conf = "growth", 0.62
        fx_reason = f"{profile['name']} currency supported by commodity export windfall. Oil/gas revenue boosting external position."
        fx_evidence = ["Commodity windfall", "Trade surplus"]
        fx_counter = ["USD safe-haven demand provides counterweight"]
        fx_inv = f"{profile['name']} currency supported by exports."
    elif is_oil_importer and code in {"JPN", "IND", "KOR", "PAK", "EGY", "TUR", "BGD"}:
        fx_trend, fx_conf = "decrease", 0.75
        fx_reason = f"{profile['name']} currency under pressure from widening trade deficit due to oil shock. Terms of trade deteriorating."
        fx_evidence = ["Oil import costs rising", "Trade deficit widening", "USD safe-haven demand"]
        fx_counter = ["Central bank intervention capacity", "Export diversification"]
        fx_inv = f"{profile['name']} currency weakening on trade deficit."
    else:
        fx_trend, fx_conf = "stable", 0.55
        fx_reason = f"{profile['name']} currency broadly stable against USD. No direct conflict exposure."
        fx_evidence = ["No direct conflict exposure"]
        fx_counter = ["Global risk-off sentiment creates mild depreciation pressure"]
        fx_inv = f"{profile['name']} currency stable."

    estimates.append(make_estimate(code, "macroeconomic.exchange_rate_vs_usd", fx_val, fx_trend, fx_conf, fx_reason, fx_evidence, fx_counter, fx_inv))

    # ---- 6. SOVEREIGN BOND YIELD 10YR ----
    bond_val = profile["bond_yield"]
    if code == "IRN":
        bond_trend, bond_conf = "strong_growth", 0.90
        bond_reason = "Iran sovereign bonds effectively untradeable. Default risk near certainty. No functioning bond market during active war."
        bond_evidence = ["Active war", "Economy collapsed", "No market access"]
        bond_counter = []
        bond_inv = "Iran bonds in default territory."
    elif code == "USA":
        bond_trend, bond_conf = "growth", 0.72
        bond_reason = "US 10yr yields rising on war spending, inflation expectations from oil shock, and fiscal uncertainty from $175B tariff refund liability. Bond market stress from leveraged basis trade ($1T+) echoes March 2020."
        bond_evidence = ["War spending increasing supply", "Inflation expectations rising", "Bond market stress from basis trade unwind"]
        bond_counter = ["Safe-haven demand compresses yields", "Fed could intervene if market dysfunctional"]
        bond_inv = "US yields rising. Bond market stress elevated."
    elif code == "ISR":
        bond_trend, bond_conf = "growth", 0.82
        bond_reason = "Israel bond yields rising on war risk premium and expanded Lebanon operations. Credit downgrades possible if war extends."
        bond_evidence = ["Multi-front war", "Fiscal deterioration", "Credit downgrade risk"]
        bond_counter = ["US support packages", "BoI intervention"]
        bond_inv = "Israel bonds under pressure. Watch for rating actions."
    elif is_hormuz_blocked:
        bond_trend, bond_conf = "strong_growth", 0.80
        bond_reason = f"{profile['name']} bond yields surging on revenue collapse and fiscal deterioration from Hormuz blockade."
        bond_evidence = ["Revenue collapse", "Fiscal stress"]
        bond_counter = ["SWF support"]
        bond_inv = f"{profile['name']} bond yields rising sharply."
    elif is_oil_exporter_safe:
        bond_trend, bond_conf = "decrease", 0.62
        bond_reason = f"{profile['name']} bond yields stable to declining on improved fiscal position from commodity windfall."
        bond_evidence = ["Fiscal improvement", "Revenue windfall"]
        bond_counter = ["Global rate environment"]
        bond_inv = f"{profile['name']} bonds stable."
    else:
        if is_oil_importer:
            bond_trend, bond_conf = "growth", 0.65
            bond_reason = f"{profile['name']} bond yields rising modestly on inflation expectations from oil shock."
            bond_evidence = ["Inflation expectations rising", "Fiscal pressure from energy costs"]
            bond_counter = ["Central bank credibility", "Flight to quality dynamics"]
            bond_inv = f"{profile['name']} yields modestly higher."
        else:
            bond_trend, bond_conf = "stable", 0.55
            bond_reason = f"{profile['name']} bond yields broadly stable."
            bond_evidence = ["No direct conflict exposure"]
            bond_counter = ["Global rate movements"]
            bond_inv = f"{profile['name']} yields stable."

    estimates.append(make_estimate(code, "macroeconomic.sovereign_bond_yield_10yr_pct", bond_val, bond_trend, bond_conf, bond_reason, bond_evidence, bond_counter, bond_inv))

    # ---- 7. CENTRAL BANK POLICY RATE ----
    rate_val = profile["policy_rate"]
    if code == "IRN":
        rate_trend, rate_conf = "growth", 0.75
        rate_reason = "Iran central bank policy rate irrelevant in war conditions. Monetary policy transmission destroyed."
        rate_evidence = ["War economy", "Currency collapse"]
        rate_counter = []
        rate_inv = "Iran monetary policy non-functional."
    elif code == "USA":
        rate_trend, rate_conf = "stable", 0.78
        rate_reason = "Fed on hold at 3.625%. February CPI steady at 2.4% pre-war but March/April readings will capture oil shock. Central bank super week March 16-19 — stagflation dilemma limits rate cuts. War uncertainty keeps Fed cautious."
        rate_evidence = ["Feb CPI 2.4% — backward-looking", "Central bank super week March 16-19", "Stagflation dilemma"]
        rate_counter = ["Recession warnings could force cuts", "Financial stability concerns"]
        rate_inv = "Fed on hold. Rate cut path delayed by energy inflation."
    elif code in {"DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "AUT", "FIN", "IRL", "PRT", "GRC"}:
        rate_trend, rate_conf = "stable", 0.72
        rate_reason = "ECB facing stagflation dilemma. Oil shock pushes inflation higher while growth weakens. March policy meeting critical. Belgium general strike highlights wage-price spiral risk."
        rate_evidence = ["ECB stagflation dilemma", "March policy meeting upcoming", "Belgium general strike — wage pressure signal"]
        rate_counter = ["Growth weakness could force dovish tilt"]
        rate_inv = "ECB on hold. Stagflation makes policy direction unclear."
    elif code == "GBR":
        rate_trend, rate_conf = "stable", 0.72
        rate_reason = "BoE on hold at 3.75%. Oil shock inflation pass-through delays easing cycle. Pro-Palestine protests and domestic political pressure adding complexity."
        rate_evidence = ["Oil shock delaying rate cuts", "UK inflation already elevated at 3.27%"]
        rate_counter = ["Growth weakness could force easing"]
        rate_inv = "BoE on hold. Rate cuts delayed by energy inflation."
    elif code == "JPN":
        rate_trend, rate_conf = "stable", 0.72
        rate_reason = "BoJ on hold at 0.75%. Oil shock complicates normalization path. Yen weakness from energy import costs could force intervention. DPRK missile threat adds uncertainty."
        rate_evidence = ["Oil shock complicating policy", "Yen weakness", "DPRK 10-missile salvo"]
        rate_counter = ["Inflation above target supports normalization case"]
        rate_inv = "BoJ in holding pattern. Too many cross-currents."
    elif code == "TUR":
        rate_trend, rate_conf = "stable", 0.72
        rate_reason = "TCMB maintaining ultra-tight 47.5% rate. Oil shock re-accelerating inflation undermines easing case. Regional instability adds risk premium."
        rate_evidence = ["47.5% rate maintained", "Oil shock re-acceleration", "Regional instability"]
        rate_counter = ["Inflation was decelerating before oil shock"]
        rate_inv = "Turkey easing cycle on hold. Oil shock delays pivot."
    elif code == "RUS":
        rate_trend, rate_conf = "stable", 0.68
        rate_reason = "CBR at 21%. Oil windfall improves fiscal position but war economy overheating continues. No room to ease despite growth."
        rate_evidence = ["21% rate maintained", "War economy overheating", "Oil windfall"]
        rate_counter = ["Inflation pressure may require further tightening"]
        rate_inv = "Russia rates unchanged. War economy limits policy options."
    else:
        rate_trend, rate_conf = "stable", 0.60
        rate_reason = f"{profile['name']} policy rate broadly stable. Central bank balancing growth and inflation concerns amid global uncertainty."
        rate_evidence = ["Global uncertainty", "Oil shock pass-through concerns"]
        rate_counter = ["Growth concerns could prompt easing"]
        rate_inv = f"{profile['name']} rates on hold."

    estimates.append(make_estimate(code, "macroeconomic.central_bank_policy_rate_pct", rate_val, rate_trend, rate_conf, rate_reason, rate_evidence, rate_counter, rate_inv))

    # ---- 8. COMPOSITE NATIONAL POWER INDEX ----
    cnpi_val = profile["cnpi"]
    if code == "IRN":
        cnpi_trend, cnpi_conf = "strong_decrease", 0.92
        cnpi_reason = "Iran national power collapsing. Military infrastructure being destroyed. Economy in freefall. Supreme Leader killed and replaced. International isolation deepening."
        cnpi_evidence = ["6,000+ targets struck", "Former Supreme Leader killed", "Economy collapsed"]
        cnpi_counter = ["Nuclear program partially intact", "Proxy network still functioning"]
        cnpi_inv = "Iran national power in historic decline."
    elif code == "USA":
        cnpi_trend, cnpi_conf = "stable", 0.72
        cnpi_reason = "US national power stable but stretched across multiple theaters. Iran war entering third week. Freedom Shield exercise in Korea while DPRK fires 10 missiles. Shield of Americas alliance launched with 15 Latin American nations. Section 301 investigations demonstrate trade leverage."
        cnpi_evidence = ["Multi-theater military deployment", "Shield of Americas alliance (15 nations)", "Section 301 investigations (76 trading partners)", "DPRK missile response to Freedom Shield"]
        cnpi_counter = ["Military stretched across theaters", "Domestic political divisions", "War powers vote failure"]
        cnpi_inv = "US power projection tested but alliance-building continues."
    elif code == "ISR":
        cnpi_trend, cnpi_conf = "decrease", 0.82
        cnpi_reason = "Israel national power declining as multi-front war expands. Lebanon operations dramatically escalated. International condemnation growing. Military resources stretched."
        cnpi_evidence = ["Lebanon expansion — 680+ killed", "Multi-front operations", "International criticism intensifying"]
        cnpi_counter = ["US military support", "Technological superiority"]
        cnpi_inv = "Israel power declining from multi-front war strain."
    elif code == "RUS":
        cnpi_trend, cnpi_conf = "growth", 0.68
        cnpi_reason = "Russia national power rising relatively as US stretched across theaters. Oil windfall strengthens economic base. Strategic position improves with Iran war diverting Western attention. Peace talks stalled at 90% — Russia maintaining leverage."
        cnpi_evidence = ["US stretched across theaters", "Oil windfall", "Peace talks stalled favoring Russia", "Shadow fleet expansion"]
        cnpi_counter = ["Sanctions remain in place", "Ukraine war costs continue"]
        cnpi_inv = "Russia relative power improving amid US distraction."
    elif code == "FRA":
        cnpi_trend, cnpi_conf = "growth", 0.68
        cnpi_reason = "France asserting independent strategic role. Announced unprecedented 10-warship deployment to reopen Hormuz. Charles de Gaulle carrier deploying. European defense leadership emerging."
        cnpi_evidence = ["10-warship deployment announced", "Charles de Gaulle carrier deploying", "Independent Hormuz strategy", "European defense leadership"]
        cnpi_counter = ["Deployment costs strain budget", "Operational risks"]
        cnpi_inv = "France projecting increased power in Gulf. Defense stocks benefiting."
    elif is_hormuz_blocked:
        cnpi_trend, cnpi_conf = "strong_decrease", 0.80
        cnpi_reason = f"{profile['name']} national power declining sharply from Hormuz blockade. Economic base undermined. Military response limited."
        cnpi_evidence = ["Economic paralysis", "Hormuz blockade"]
        cnpi_counter = ["Alliance partnerships provide support"]
        cnpi_inv = f"{profile['name']} national power declining."
    elif code == "CHN":
        cnpi_trend, cnpi_conf = "stable", 0.72
        cnpi_reason = "China national power stable. US distracted by Iran war provides strategic window. But Section 301 investigations (overcapacity + forced labor) across 21 sectors represent major new trade confrontation. Two Sessions tech/AI push continues."
        cnpi_evidence = ["US distracted by Middle East", "Section 301 trade confrontation", "Tech/AI investment push"]
        cnpi_counter = ["Trade escalation risk from Section 301", "Demographic headwinds"]
        cnpi_inv = "China power stable. US distraction creates strategic window."
    else:
        cnpi_trend, cnpi_conf = "stable", 0.55
        cnpi_reason = f"{profile['name']} national power broadly stable. No significant structural changes this week."
        cnpi_evidence = ["No major changes"]
        cnpi_counter = ["Global power dynamics shifting"]
        cnpi_inv = f"{profile['name']} national power unchanged."

    estimates.append(make_estimate(code, "derived.composite_national_power_index", cnpi_val, cnpi_trend, cnpi_conf, cnpi_reason, cnpi_evidence, cnpi_counter, cnpi_inv))

    # ---- 9. OVERALL INVESTMENT RISK SCORE ----
    risk_val = profile["risk_score"]
    if code == "IRN":
        risk_trend, risk_conf = "strong_growth", 0.95
        risk_reason = "Iran investment risk at maximum. Active war, economy collapsed, assets frozen, Hormuz mined. No investable opportunities."
        risk_evidence = ["Active war", "Economy collapsed", "Assets frozen"]
        risk_counter = []
        risk_inv = "Iran uninvestable."
    elif code == "ISR":
        risk_trend, risk_conf = "growth", 0.85
        risk_reason = "Israel investment risk rising as war expands into Lebanon. 680+ killed, 800,000 displaced. Hezbollah retaliation on northern Israel. Tech sector disrupted. War duration uncertain."
        risk_evidence = ["Lebanon war expansion", "Hezbollah retaliation", "Multi-front conflict"]
        risk_counter = ["US support packages", "Strong institutional base"]
        risk_inv = "Israel risk elevated. Selective tech opportunities but war duration unknown."
    elif code == "USA":
        risk_trend, risk_conf = "growth", 0.78
        risk_reason = "US investment risk rising from war costs, bond market stress, Section 301 trade escalation, and political fragility (217-214 House majority). Senate failed to constrain war spending. 5 recession warning signs. But institutional strength provides floor."
        risk_evidence = ["War costs unchecked", "Bond market basis trade stress", "Section 301 escalation (76 partners)", "House majority at 217-214"]
        risk_counter = ["Deep capital markets", "Dollar reserve status", "Institutional resilience"]
        risk_inv = "US risk rising but from strong base. War duration key variable."
    elif is_hormuz_blocked:
        risk_trend, risk_conf = "strong_growth", 0.88
        risk_reason = f"{profile['name']} investment risk at extreme levels from Hormuz blockade. Revenue collapsed. Fiscal position deteriorating."
        risk_evidence = ["Hormuz blockade", "Revenue collapse"]
        risk_counter = ["SWF reserves buffer"]
        risk_inv = f"{profile['name']} investment risk extremely elevated."
    elif is_oil_exporter_safe:
        risk_trend, risk_conf = "decrease", 0.65
        risk_reason = f"{profile['name']} investment risk improving on commodity windfall. Fiscal position strengthening. Non-Hormuz export routes secure."
        risk_evidence = ["Commodity windfall", "Fiscal improvement"]
        risk_counter = ["Global recession risk", "Trade policy uncertainty"]
        risk_inv = f"{profile['name']} risk declining on commodity strength."
    elif code == "UKR":
        risk_trend, risk_conf = "stable", 0.60
        risk_reason = "Ukraine investment risk unchanged. Peace talks stalled. Active combat continues with large-scale Russian attacks. Reconstruction opportunity depends on peace."
        risk_evidence = ["Peace talks stalled at 90%", "Russian attacks continue", "EU funding flowing"]
        risk_counter = ["Peace could unlock reconstruction boom"]
        risk_inv = "Ukraine risk high but stable. Peace talks key catalyst."
    elif code == "EGY":
        risk_trend, risk_conf = "growth", 0.75
        risk_reason = "Egypt investment risk rising from oil import shock, Suez Canal uncertainty, and regional conflict proximity. IMF program constrains fiscal response."
        risk_evidence = ["Oil import costs surging", "Suez Canal revenue risk", "Tourism disrupted"]
        risk_counter = ["IMF backstop", "Remittance flows stable"]
        risk_inv = "Egypt risk rising. Triple pressure from oil, Suez, and tourism."
    elif code == "KOR":
        risk_trend, risk_conf = "growth", 0.72
        risk_reason = "South Korea investment risk elevated by DPRK 10-missile salvo and US military being stretched across multiple theaters. Section 301 investigation adds trade risk."
        risk_evidence = ["DPRK 10-missile salvo", "US military stretched", "Section 301 investigation"]
        risk_counter = ["Strong institutions", "Alliance commitment"]
        risk_inv = "Korea risk elevated from DPRK provocation and trade uncertainty."
    else:
        if is_oil_importer:
            risk_trend, risk_conf = "growth", 0.62
            risk_reason = f"{profile['name']} investment risk modestly elevated from oil shock and global uncertainty."
            risk_evidence = ["Oil costs rising", "Global uncertainty elevated"]
            risk_counter = ["Institutional stability", "Policy response capacity"]
            risk_inv = f"{profile['name']} risk mildly elevated."
        else:
            risk_trend, risk_conf = "stable", 0.55
            risk_reason = f"{profile['name']} investment risk broadly unchanged."
            risk_evidence = ["No significant structural changes"]
            risk_counter = ["Global risk environment uncertain"]
            risk_inv = f"{profile['name']} risk stable."

    # Note: higher risk_score = worse, so "growth" in risk_score means deterioration
    estimates.append(make_estimate(code, "derived.overall_investment_risk_score", risk_val, risk_trend, risk_conf, risk_reason, risk_evidence, risk_counter, risk_inv))

    # ---- 10. MILITARY EXPENDITURE PCT GDP ----
    mil_val = profile["mil_pct_gdp"]
    if code == "IRN":
        mil_trend, mil_conf = "strong_growth", 0.90
        mil_reason = "Iran military expenditure as % GDP surging as GDP collapses and war spending maximized. Total mobilization underway."
        mil_evidence = ["Total war mobilization", "GDP collapsing", "Emergency military spending"]
        mil_counter = []
        mil_inv = "Iran defense spending unsustainable."
    elif code == "ISR":
        mil_trend, mil_conf = "strong_growth", 0.88
        mil_reason = "Israel military spending surging as war expands to Lebanon. IDF operations across multiple fronts. Reserve mobilization costs. US aid supplements but domestic spending rising sharply."
        mil_evidence = ["Lebanon war expansion", "Multi-front operations", "Reserve mobilization"]
        mil_counter = ["US military aid offsets some costs"]
        mil_inv = "Israel defense spending trajectory steep."
    elif code == "USA":
        mil_trend, mil_conf = "growth", 0.85
        mil_reason = "US defense spending growing from Iran war (Operation Epic Fury) now entering third week. Freedom Shield exercise in Korea with 18,000 troops. Shield of Americas alliance with 15 Latin American nations. SIPRI: global arms transfers +9.2%, US exports +27%."
        mil_evidence = ["Iran war third week", "Freedom Shield 18,000 troops", "Shield of Americas alliance", "SIPRI: US arms exports +27%"]
        mil_counter = ["Sequestration constraints", "Fiscal sustainability questions"]
        mil_inv = "US defense spending accelerating. Defense stocks benefiting."
    elif code == "FRA":
        mil_trend, mil_conf = "growth", 0.78
        mil_reason = "France announcing unprecedented 10-warship naval deployment to Hormuz. Charles de Gaulle carrier, 8 frigates, 2 amphibious carriers. Major defense spending increase signaled."
        mil_evidence = ["10-warship deployment", "Charles de Gaulle carrier", "2 frigates for Operation Aspides"]
        mil_counter = ["Budget constraints"]
        mil_inv = "France defense spending increasing. NATO burden-sharing shift."
    elif code == "RUS":
        mil_trend, mil_conf = "growth", 0.78
        mil_reason = "Russia military spending elevated from Ukraine war. Large-scale drone/missile barrages continue against Ukraine (10+ killed in Kharkiv). War economy driving defense spending as % GDP higher."
        mil_evidence = ["Ukraine war ongoing", "Large-scale attacks continue", "War economy"]
        mil_counter = ["Oil windfall funds spending without debt"]
        mil_inv = "Russia defense spending high but funded by oil windfall."
    elif code in {"DEU", "GBR", "POL", "NOR", "SWE", "FIN", "CAN", "AUS"}:
        mil_trend, mil_conf = "growth", 0.72
        mil_reason = f"{profile['name']} defense spending growing under NATO commitments. SIPRI: European arms imports up 210%. All 32 NATO members now at 2% GDP target."
        mil_evidence = ["NATO 2% commitment", "SIPRI: European arms imports +210%", "Global threat environment"]
        mil_counter = ["Fiscal constraints"]
        mil_inv = f"{profile['name']} defense spending trend up."
    elif is_hormuz_blocked:
        mil_trend, mil_conf = "strong_growth", 0.80
        mil_reason = f"{profile['name']} defense spending surging in response to direct military threat from Hormuz conflict. GDP decline increases ratio further."
        mil_evidence = ["Direct military threat", "GDP declining"]
        mil_counter = ["International military support"]
        mil_inv = f"{profile['name']} defense spending forced higher."
    elif code == "UKR":
        mil_trend, mil_conf = "growth", 0.72
        mil_reason = "Ukraine defense spending elevated from ongoing war. Large Russian attacks continue. Peace talks stalled. Military spending as % GDP among highest globally."
        mil_evidence = ["Active war", "Russian attacks continue", "Peace talks stalled"]
        mil_counter = ["Western military aid reduces domestic burden"]
        mil_inv = "Ukraine defense spending high. Western aid critical."
    else:
        mil_trend, mil_conf = "stable", 0.58
        mil_reason = f"{profile['name']} military spending broadly stable relative to GDP."
        mil_evidence = ["No significant threat change"]
        mil_counter = ["Global threat environment evolving"]
        mil_inv = f"{profile['name']} defense spending unchanged."

    estimates.append(make_estimate(code, "military.military_expenditure_pct_gdp", mil_val, mil_trend, mil_conf, mil_reason, mil_evidence, mil_counter, mil_inv))

    # ---- 11. POLITICAL STABILITY ----
    pol_val = profile["pol_stability"]
    if code == "IRN":
        pol_trend, pol_conf = "strong_decrease", 0.95
        pol_reason = "Iran political stability collapsing. Former Supreme Leader killed. New Supreme Leader Mojtaba Khamenei installed under extreme duress. Active war with foreign powers. 1,348 civilians killed, 17,000+ injured. Regime survival in question."
        pol_evidence = ["Supreme Leader succession under war", "1,348 civilians killed", "Foreign military strikes on territory", "Hormuz blockade strangling economy"]
        pol_counter = ["Regime historically resilient under external pressure"]
        pol_inv = "Iran political stability at historic low. Regime change scenario non-trivial."
    elif code == "ISR":
        pol_trend, pol_conf = "decrease", 0.82
        pol_reason = "Israel political stability declining. War expansion into Lebanon highly divisive. International condemnation growing. Domestic debate over war aims intensifying."
        pol_evidence = ["Lebanon war expansion", "International condemnation", "Domestic divisions"]
        pol_counter = ["Rally-around-flag effect", "US support"]
        pol_inv = "Israel political stability weakening under war strain."
    elif code == "USA":
        pol_trend, pol_conf = "decrease", 0.82
        pol_reason = "US political stability declining. War with Iran has no congressional authorization — war powers vote failed. GOP House majority razor-thin at 217-214 after Kiley exit to independent. DHS Secretary fired. $175B tariff refund SCOTUS crisis. Rand Paul warns of 'disastrous' midterms."
        pol_evidence = ["War powers vote failed — no congressional authorization", "GOP majority 217-214 after Kiley exit", "DHS Secretary fired", "$175B SCOTUS tariff refund crisis"]
        pol_counter = ["Institutional resilience", "Two-party system stability"]
        pol_inv = "US political stability declining. War and fiscal crises testing governance."
    elif code == "BEL":
        pol_trend, pol_conf = "decrease", 0.72
        pol_reason = "Belgium political stability shaken by 24-hour general strike. All flights cancelled at Brussels and Charleroi airports. 650+ flights cancelled, 95,000 travelers displaced. Pension and wage reforms politically contentious."
        pol_evidence = ["24-hour general strike", "All flights cancelled", "Union militancy", "Pension reform dispute"]
        pol_counter = ["Strike was orderly and time-limited"]
        pol_inv = "Belgium political instability. EU institutional hub disrupted."
    elif code == "VNM":
        pol_trend, pol_conf = "stable", 0.78
        pol_reason = "Vietnam political stability maintained through general election. 73.5 million voters electing 500 National Assembly members. One-party system ensures continuity."
        pol_evidence = ["General election March 15", "One-party continuity", "864 candidates for 500 seats"]
        pol_counter = ["Section 301 investigation creates external pressure"]
        pol_inv = "Vietnam political stability assured by election."
    elif code == "DNK":
        pol_trend, pol_conf = "stable", 0.65
        pol_reason = "Denmark snap election called for March 24. Frederiksen capitalizing on Greenland standoff with Trump. Social Democrats leading polls but coalition math uncertain."
        pol_evidence = ["Snap election March 24", "Greenland standoff driving politics", "Coalition uncertainty"]
        pol_counter = ["Democratic process orderly", "Defense consensus across parties"]
        pol_inv = "Denmark political transition underway. Election adds short-term uncertainty."
    elif code == "RUS":
        pol_trend, pol_conf = "stable", 0.65
        pol_reason = "Russia political stability maintained under Putin. Oil windfall strengthens regime. US distracted by Iran war. Peace talks stalled — Russia maintaining advantageous position. No domestic challenge to regime."
        pol_evidence = ["Oil windfall strengthens regime", "US distracted", "Peace talks favor Russia"]
        pol_counter = ["War casualties accumulating", "Sanctions long-term impact"]
        pol_inv = "Russia political stability maintained. Regime position strong."
    elif code == "UKR":
        pol_trend, pol_conf = "stable", 0.62
        pol_reason = "Ukraine political stability maintained despite ongoing war. Zelenskiy engaging Saudi Arabia diplomatically. EU funding flowing via non-Hungary channels. Peace talks stalled but not collapsed."
        pol_evidence = ["Zelenskiy diplomatic engagement", "EU funding secured", "Peace talks ongoing"]
        pol_counter = ["War fatigue", "Russian large-scale attacks continue"]
        pol_inv = "Ukraine political stability fragile but holding."
    elif is_hormuz_blocked:
        pol_trend, pol_conf = "decrease", 0.75
        pol_reason = f"{profile['name']} political stability under pressure from economic crisis caused by Hormuz blockade. Social contract strained."
        pol_evidence = ["Economic crisis from Hormuz", "Revenue collapse"]
        pol_counter = ["Regime resilience", "Security apparatus"]
        pol_inv = f"{profile['name']} political stability declining."
    else:
        pol_trend, pol_conf = "stable", 0.55
        pol_reason = f"{profile['name']} political stability broadly unchanged. No major domestic political disruptions this week."
        pol_evidence = ["No significant domestic disruptions"]
        pol_counter = ["Global uncertainty creates indirect pressure"]
        pol_inv = f"{profile['name']} political stability maintained."

    estimates.append(make_estimate(code, "institutions.political_stability_score", pol_val, pol_trend, pol_conf, pol_reason, pol_evidence, pol_counter, pol_inv))

    return estimates


def make_estimate(country, factor_path, current_value, trend, confidence, reasoning, evidence, counter, investor_imp):
    return {
        "country_code": country,
        "factor_path": factor_path,
        "current_value": current_value,
        "trend": trend,
        "confidence": confidence,
        "reasoning": reasoning,
        "supporting_evidence": evidence,
        "counter_arguments": counter,
        "investor_implication": investor_imp,
        "ai_generated": True,
        "generated_at": TIMESTAMP
    }


def update_country_file(code, estimates):
    """Update trend fields in a country JSON file."""
    path = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(path):
        return False

    with open(path, 'r') as f:
        data = json.load(f)

    macro = data.get("macroeconomic", {})
    military = data.get("military", {})
    derived = data.get("derived", {})

    factor_map = {
        "macroeconomic.gdp_real_growth_pct": ("macroeconomic", "gdp_real_growth_pct"),
        "macroeconomic.inflation_cpi_pct": ("macroeconomic", "inflation_cpi_pct"),
        "macroeconomic.current_account_pct_gdp": ("macroeconomic", "current_account_pct_gdp"),
        "macroeconomic.govt_debt_pct_gdp": ("macroeconomic", "govt_debt_pct_gdp"),
        "macroeconomic.exchange_rate_vs_usd": ("macroeconomic", "exchange_rate_vs_usd"),
        "macroeconomic.sovereign_bond_yield_10yr_pct": ("macroeconomic", "sovereign_bond_yield_10yr_pct"),
        "macroeconomic.central_bank_policy_rate_pct": ("macroeconomic", "central_bank_policy_rate_pct"),
        "derived.composite_national_power_index": ("derived", "composite_national_power_index"),
        "derived.overall_investment_risk_score": ("derived", "overall_investment_risk_score"),
        "military.military_expenditure_pct_gdp": ("military", "military_expenditure_pct_gdp"),
    }

    for est in estimates:
        fp = est["factor_path"]

        # Handle political stability separately (it's a derived trend field)
        if fp == "institutions.political_stability_score":
            if "derived" not in data:
                data["derived"] = {}
            data["derived"]["political_stability_trend"] = {
                "value": est["trend"],
                "confidence": est["confidence"],
                "reasoning": est["reasoning"],
                "last_updated": TIMESTAMP,
                "source": "agent_10_trend_estimator",
                "run_id": "2026-W11"
            }
            continue

        if fp not in factor_map:
            continue

        section_name, field_name = factor_map[fp]
        section = data.get(section_name, {})
        field = section.get(field_name, {})

        if isinstance(field, dict) and "value" in field:
            # Detailed field format — add trend directly
            field["trend"] = est["trend"]
            field["trend_confidence"] = est["confidence"]
            field["trend_reasoning"] = est["reasoning"]
            field["trend_updated"] = TIMESTAMP
            section[field_name] = field
        elif isinstance(field, dict):
            # May be a complex field without value key — add trend
            field["trend"] = est["trend"]
            field["trend_confidence"] = est["confidence"]
            field["trend_reasoning"] = est["reasoning"]
            field["trend_updated"] = TIMESTAMP
            section[field_name] = field

        data[section_name] = section

    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return True


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    all_estimates = []
    countries_updated = 0
    countries_read = set()

    # Countries to read and update (key countries + high/moderate impact)
    countries_to_update = set(ALL_COUNTRIES)  # Update all

    # Generate estimates for all 55 countries
    for code in ALL_COUNTRIES:
        profile = get_country_profile(code)
        if not profile:
            print(f"  SKIP {code}: file not found")
            continue

        countries_read.add(code)
        estimates = estimate_trends(profile)
        all_estimates.extend(estimates)

        # Update country files
        if update_country_file(code, estimates):
            countries_updated += 1
            print(f"  OK {code}: {len(estimates)} estimates, file updated")
        else:
            print(f"  WARN {code}: {len(estimates)} estimates, file NOT updated")

    # Count by trend label
    trend_counts = {"strong_growth": 0, "growth": 0, "stable": 0, "decrease": 0, "strong_decrease": 0}
    for est in all_estimates:
        trend_counts[est["trend"]] = trend_counts.get(est["trend"], 0) + 1

    # Build output
    output = {
        "agent": "trend_estimator",
        "run_id": "2026-W11",
        "estimation_date": "2026-03-14",
        "ai_generated": True,
        "schema_version": "1.0",
        "document_type": "trend_estimates",
        "summary": {
            "run_id": "2026-W11",
            "generated_at": TIMESTAMP,
            "pipeline_agent": "Agent 10 (Trend Estimator)",
            "reference_date": "2026-03-14",
            "total_estimates": len(all_estimates),
            "countries_covered": len(countries_read),
            "by_trend_label": trend_counts,
            "trend_distribution": trend_counts,
            "impact_groups": {
                "high_impact": {
                    "countries": sorted(list(HIGH_IMPACT)),
                    "count": len(HIGH_IMPACT),
                    "factors_per_country": 11
                },
                "moderate_impact": {
                    "countries": sorted(list(MODERATE_IMPACT & set(ALL_COUNTRIES))),
                    "count": len(MODERATE_IMPACT & set(ALL_COUNTRIES)),
                    "factors_per_country": "5-11"
                },
                "low_impact": {
                    "countries": sorted(list(set(ALL_COUNTRIES) - HIGH_IMPACT - MODERATE_IMPACT)),
                    "count": len(set(ALL_COUNTRIES) - HIGH_IMPACT - MODERATE_IMPACT),
                    "factors_per_country": "5-11"
                }
            },
            "key_themes": [
                "Iran war entering third week — 6,000+ targets struck, 1,348 civilians killed, new Supreme Leader Mojtaba Khamenei vows continued resistance",
                "Strait of Hormuz remains mined and effectively closed — IEA approves historic 400M barrel SPR release",
                "Oil above $100/bbl — US gas at $3.63/gal (22-month high) — inflation pass-through expected March/April",
                "Israel expands Lebanon operations dramatically — 680+ killed, 800,000 displaced, IDF past Litani River",
                "USTR launches dual Section 301 investigations: overcapacity (16 economies, 21 sectors) + forced labor (60 countries)",
                "North Korea fires 10 ballistic missiles during US-Korea Freedom Shield exercise (18,000 troops)",
                "France announces unprecedented 10-warship deployment to Hormuz region",
                "Russia-Ukraine peace talks stalled at '90% complete' — Russia benefits from oil windfall",
                "Belgium paralyzed by 24-hour general strike — all flights cancelled",
                "Trump launches Shield of Americas alliance with 15 Latin American nations; recognizes Venezuela's Rodriguez"
            ],
            "top_risk_deteriorations": [
                {"country": "IRN", "reason": "War week 3 — 6,000+ targets struck — Mojtaba Khamenei installed — economy in freefall"},
                {"country": "ISR", "reason": "Lebanon war expansion — 680+ killed — multi-front conflict deepening"},
                {"country": "KWT", "reason": "No pipeline alternative to Hormuz — near-total economic paralysis continues"},
                {"country": "QAT", "reason": "World's largest LNG exporter offline — jets in direct combat with Iranian bombers"},
                {"country": "USA", "reason": "War week 3 + Section 301 escalation + 217-214 House margin + bond stress"},
                {"country": "KOR", "reason": "DPRK 10-missile salvo + Section 301 + US military stretched"}
            ],
            "top_beneficiaries": [
                {"country": "RUS", "reason": "Oil windfall + US distracted + peace talks stalled in Russia's favor"},
                {"country": "NOR", "reason": "North Sea producer — non-Hormuz — European gas demand redirecting"},
                {"country": "BRA", "reason": "Net oil exporter — geographically insulated — commodity basket elevated"},
                {"country": "FRA", "reason": "Asserting defense leadership — 10-warship deployment to Hormuz"},
                {"country": "NGA", "reason": "Atlantic coast oil exports secure — $100+ oil windfall"},
                {"country": "ARG", "reason": "Net energy exporter via Vaca Muerta — Milei reform credibility rising"}
            ],
            "ai_disclosure": "All trend estimates are AI-generated based on publicly available information as of 2026-03-14. These are probabilistic estimates subject to uncertainty and should be validated against primary sources. Confidence scores reflect estimated reliability.",
            "next_agent": "Agent 11 (Derived Metrics Calculator)"
        },
        "estimates": all_estimates
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Agent 10 (Trend Estimator) — 2026-W11 Update Complete")
    print(f"{'='*60}")
    print(f"Total estimates: {len(all_estimates)}")
    print(f"Countries covered: {len(countries_read)}")
    print(f"Countries updated: {countries_updated}")
    print(f"Trend distribution: {trend_counts}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
