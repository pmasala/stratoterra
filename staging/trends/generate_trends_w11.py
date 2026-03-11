#!/usr/bin/env python3
"""
Agent 10 — Trend Estimator for 2026-W11 (2026-03-10)
Generates trend estimates for 11 key factors across Tier 1 (30) + Tier 2 (25) countries.

Key events this week:
1. US-Iran War Day 10+ — Hormuz mined, oil $116+, 140 US troops injured
2. European market crash ~6% across major indices
3. G7 SPR release signaled
4. SIPRI 2026 — global arms transfers +9.2%, Europe top importing region
5. Argentina recession -1.3% (Milei shock therapy)
6. Central bank super week coming March 16-19
"""

import json
import os
from datetime import datetime

BASE = "/home/pietro/stratoterra"
DATA_DIR = f"{BASE}/data/countries"
OUTPUT_FILE = f"{BASE}/staging/trends/trend_estimates_2026-03-10.json"

# Load country list
with open(f"{BASE}/data/indices/country_list.json") as f:
    country_list = json.load(f)

tier1_countries = [c["code"] for c in country_list["tiers"]["tier_1"]["countries"]]
tier2_countries = [c["code"] for c in country_list["tiers"]["tier_2"]["countries"]]
all_countries = tier1_countries + tier2_countries

country_names = {}
country_regions = {}
country_tiers = {}
for c in country_list["tiers"]["tier_1"]["countries"]:
    country_names[c["code"]] = c["name"]
    country_regions[c["code"]] = c["region"]
    country_tiers[c["code"]] = 1
for c in country_list["tiers"]["tier_2"]["countries"]:
    country_names[c["code"]] = c["name"]
    country_regions[c["code"]] = c["region"]
    country_tiers[c["code"]] = 2

# ===== CLASSIFICATION GROUPS =====

# Countries directly in the war zone
WAR_ZONE = {"IRN", "ISR"}

# Gulf states affected by Hormuz closure
HORMUZ_AFFECTED_GULF = {"SAU", "ARE", "KWT", "QAT", "OMN", "IRQ"}

# Oil importers heavily dependent on Hormuz
HEAVY_OIL_IMPORTERS_HORMUZ = {"JPN", "KOR", "IND", "TWN", "THA", "BGD", "PAK", "PHL"}

# European oil importers (not Hormuz-critical but affected by price)
EUROPEAN_OIL_IMPORTERS = {"DEU", "FRA", "GBR", "ITA", "ESP", "NLD", "POL", "SWE",
                          "CHE", "CZE", "ROU", "GRC", "PRT", "FIN", "IRL", "TUR"}

# Oil/commodity exporters NOT Hormuz-dependent (beneficiaries)
OIL_EXPORTERS_SAFE = {"NOR", "RUS", "BRA", "CAN", "NGA", "KAZ", "COL", "AUS"}

# Argentina special case — recession + Milei reforms
# Mexico special case — El Mencho killed, tariff impacts
# China special case — Two Sessions, tech push, relatively insulated
# Ukraine special case — ongoing war, EU funding

# Defense spending growth countries (NATO 2%, war impacts)
NATO_DEFENSE_GROWTH = {"USA", "GBR", "FRA", "DEU", "POL", "NOR", "CAN", "ITA", "ESP",
                       "NLD", "CZE", "ROU", "GRC", "PRT", "FIN", "SWE"}

# ===== LOAD COUNTRY DATA =====
country_data = {}
for code in all_countries:
    fpath = os.path.join(DATA_DIR, f"{code}.json")
    if os.path.exists(fpath):
        with open(fpath) as f:
            country_data[code] = json.load(f)

def get_value(cdata, section, key):
    """Extract a numeric value from country data."""
    if section in cdata and key in cdata[section]:
        v = cdata[section][key]
        if isinstance(v, dict) and "value" in v:
            val = v["value"]
            if isinstance(val, (int, float)):
                return val
        elif isinstance(v, (int, float)):
            return v
    return None

def get_nested_value(cdata, *keys):
    """Navigate nested dict."""
    obj = cdata
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return None
    if isinstance(obj, dict) and "value" in obj:
        val = obj["value"]
        if isinstance(val, (int, float)):
            return val
    return obj if isinstance(obj, (int, float)) else None


NOW = "2026-03-10T12:00:00Z"

estimates = []
trend_counts = {"strong_growth": 0, "growth": 0, "stable": 0, "decrease": 0, "strong_decrease": 0}

def add_estimate(code, factor, current_val, trend, confidence, reasoning, evidence, counter, implication):
    """Add a trend estimate."""
    trend_counts[trend] += 1
    estimates.append({
        "country_code": code,
        "factor": factor,
        "current_value": current_val,
        "trend": trend,
        "confidence": confidence,
        "reasoning": reasoning,
        "supporting_evidence": evidence,
        "counter_arguments": counter,
        "investor_implication": implication,
        "ai_generated": True,
        "generated_at": NOW
    })


# ===== GENERATE ESTIMATES PER COUNTRY =====

for code in all_countries:
    cdata = country_data.get(code, {})
    name = country_names.get(code, code)
    region = country_regions.get(code, "unknown")

    # Extract current values
    gdp_nominal = get_value(cdata, "macroeconomic", "gdp_nominal_usd")
    gdp_growth = get_value(cdata, "macroeconomic", "gdp_real_growth_pct")
    inflation = get_value(cdata, "macroeconomic", "inflation_cpi_pct")
    ca_gdp = get_value(cdata, "macroeconomic", "current_account_pct_gdp")
    debt_gdp = get_value(cdata, "macroeconomic", "govt_debt_pct_gdp")
    mil_pct = get_value(cdata, "military", "military_expenditure_pct_gdp")
    fdi = get_value(cdata, "macroeconomic", "fdi_inflows_usd")
    exports = get_value(cdata, "macroeconomic", "total_exports_usd")
    imports = get_value(cdata, "macroeconomic", "total_imports_usd")

    # Try alternate field names for some factors
    if gdp_growth is None:
        gdp_growth = get_value(cdata, "macroeconomic", "gdp_growth_pct")
    if inflation is None:
        inflation = get_value(cdata, "macroeconomic", "inflation_rate_cpi_pct")
    if debt_gdp is None:
        debt_gdp = get_value(cdata, "macroeconomic", "public_debt_pct_gdp")
    if mil_pct is None:
        mil_pct = get_nested_value(cdata, "military", "military_spending_pct_gdp")
    if mil_pct is None:
        mil_pct = get_nested_value(cdata, "military", "defense_spending_pct_gdp")
    # Compute mil_pct from absolute spending if still missing
    if mil_pct is None and gdp_nominal and gdp_nominal > 0:
        mil_usd = get_value(cdata, "military", "military_expenditure_usd")
        if mil_usd is None:
            mil_usd = get_value(cdata, "military", "military_spending_usd")
        if mil_usd is None:
            mil_usd = get_value(cdata, "military", "defense_spending_usd")
        if mil_usd is not None:
            mil_pct = round((mil_usd / gdp_nominal) * 100, 2)
    if fdi is None:
        fdi = get_value(cdata, "macroeconomic", "fdi_net_inflows_usd")

    # Compute trade openness if we have the data
    trade_openness = None
    if exports and imports and gdp_nominal and gdp_nominal > 0:
        trade_openness = ((exports + imports) / gdp_nominal) * 100

    # ===== 1. GDP REAL GROWTH =====
    if gdp_growth is not None:
        if code in WAR_ZONE:
            if code == "IRN":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "strong_decrease", 0.95,
                    "War Day 10+ with escalating intensity. Infrastructure destruction accelerating. Hormuz mined, halting oil exports (~70% of revenue). Kurdish ground invasion opens new front. GDP trajectory: deep contraction -15% to -20% annualized.",
                    ["Operation Epic Fury entering most intense phase per Pentagon", "Hormuz now physically mined, not just blockaded", "Tehran under sustained bombing; internet shut down"],
                    ["Domestic oil consumption sustains some economic activity", "War mobilization spending may inflate nominal GDP"],
                    "Iran GDP in catastrophic freefall. Uninvestable across all timeframes.")
            else:  # ISR
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "strong_decrease", 0.90,
                    "Active war with Iran/Hezbollah. Hezbollah escalation from Lebanon. Military mobilization consuming resources. Tech sector disrupted. But US military support and domestic resilience partially offset.",
                    ["Multi-front conflict: Iran strikes + Hezbollah escalation from Lebanon", "Reserve mobilization pulling workers from economy", "Regional conflict expanding beyond initial scope"],
                    ["US providing massive military support", "Israeli tech/defense sector benefits from war economy"],
                    "Israeli growth severely impacted by multi-front war. Defense-adjacent sectors only bright spot.")
        elif code in HORMUZ_AFFECTED_GULF:
            if code in {"SAU", "ARE"}:
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "strong_decrease", 0.88,
                    f"Hormuz mine-laying by IRGC blocks primary oil export route. Oil revenue disruption severe despite high prices. {name} has limited pipeline alternatives. Defense spending surge adds fiscal pressure.",
                    ["Hormuz physically mined, US Navy cannot provide escorts", "VLCC insurance withdrawn; tanker traffic halted", "IRGC declared Tehran will decide when war ends"],
                    ["High oil prices mean per-barrel revenue is extreme once exports resume", "Strategic petroleum reserves provide temporary buffer", "Pipeline alternatives (East-West Pipeline for SAU) partially mitigate"],
                    f"{name} GDP faces severe contraction from export channel disruption despite high headline oil prices.")
            elif code == "IRQ":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "strong_decrease", 0.85,
                    "Iraq caught between US operations and Iranian influence. Kurdish invasion of Iran from Iraqi Kurdistan threatens sovereignty. Oil exports via Hormuz disrupted. Internal security deteriorating.",
                    ["Kurdish forces using Iraqi territory to invade Iran with US air support", "Iraqi oil exports partially routed through Hormuz", "Internal militia dynamics complicated by Iran war"],
                    ["Basra-Ceyhan pipeline provides alternative export route", "High oil prices benefit eventual export resumption"],
                    "Iraq GDP severely disrupted by proxy conflict dynamics and export channel closure.")
            else:  # KWT, QAT, OMN
                severity = "strong_decrease" if code in {"KWT", "QAT"} else "decrease"
                conf = 0.88 if code in {"KWT", "QAT"} else 0.82
                pipeline_note = "No pipeline alternative to Hormuz" if code == "KWT" else ("LNG exports completely blocked" if code == "QAT" else "Limited Hormuz dependency but regional disruption severe")
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, severity, conf,
                    f"{name} GDP under severe pressure from Hormuz disruption. {pipeline_note}. High energy prices cannot be monetized while export channels are blocked.",
                    ["Hormuz mine-laying eliminates maritime export capability", f"{pipeline_note}", "Regional conflict creating investor flight"],
                    ["Sovereign wealth funds provide fiscal buffer", "High energy prices benefit once exports resume"],
                    f"{name} facing GDP contraction until Hormuz reopens. Sovereign wealth reserves key to resilience.")
        elif code in HEAVY_OIL_IMPORTERS_HORMUZ:
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.82,
                f"{name} heavily dependent on Gulf oil transiting Hormuz. Oil at $116/bbl adds 1-2pp to import bill as % of GDP. Manufacturing and transport sectors hit hardest. G7 SPR release provides partial temporary relief.",
                [f"Brent crude surged 25% to $116.50/bbl in single week", f"{name} receives significant share of oil imports via Hormuz", "Asian LNG prices surging as Qatari supply disrupted"],
                ["G7 coordinated SPR release could cap prices temporarily", "Energy efficiency improvements reduce per-unit impact", "Alternative suppliers (non-Gulf) ramping up"],
                f"{name} GDP growth revised down 0.5-1.0pp on oil shock. Energy-intensive sectors most vulnerable.")
        elif code in EUROPEAN_OIL_IMPORTERS:
            # European markets crashed ~6%
            trend_val = "decrease"
            conf = 0.78
            extra = ""
            if code == "DEU":
                extra = " VW slashing 50,000 jobs adds structural pressure."
                conf = 0.85
            elif code == "TUR":
                extra = " Turkey navigating between NATO membership and regional relationships. Turkic coordination tested."
                conf = 0.75
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, trend_val, conf,
                f"{name} facing GDP headwinds from oil shock ($116/bbl Brent) and European market crash (~6% drops across indices). Energy costs rising sharply.{extra}",
                ["European equity markets crashed ~6% this week", "Oil prices surged 25% adding to energy import bills", "EU nuclear energy policy 'blunder' acknowledged"],
                ["G7 SPR release may cap oil prices", "ECB likely to respond with accommodative policy", "European defense spending creating industrial stimulus"],
                f"{name} GDP growth revised down 0.3-0.7pp. Stagflation risks rising across Europe.")
        elif code in OIL_EXPORTERS_SAFE:
            if code == "RUS":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.75,
                    "Russia benefits from oil price surge to $116/bbl. Shadow fleet oil transfers in Gulf of Oman expand market share. War economy continues to drive GDP. Possible intelligence sharing with Iran complicates Western relations.",
                    ["Ship-to-ship oil transfer caught in Gulf of Oman", "Oil prices at $116/bbl boost revenue despite sanctions", "SIPRI: arms exports collapsed 64% but war economy sustains domestic production"],
                    ["Sanctions limit price realization", "US warned of consequences if Russia aids Iran", "Ukraine retaking territory raises military costs"],
                    "Russian GDP benefits from oil windfall despite sanctions. Shadow economy expanding.")
            elif code == "NOR":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.82,
                    "Norway as North Sea oil/gas producer is primary beneficiary of Hormuz disruption. Non-Hormuz export routes secure. Energy windfall boosts fiscal position significantly.",
                    ["Brent at $116/bbl — massive windfall for Norwegian production", "North Sea supply routes completely unaffected by Gulf conflict", "European scramble for non-Gulf energy sources benefits Norway directly"],
                    ["Dutch disease risk from energy windfall", "Global recession could ultimately reduce demand"],
                    "Norway GDP growth accelerates on energy windfall. Government Pension Fund inflows surge.")
            elif code == "CAN":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.72,
                    "Canada benefits from oil price surge but faces US tariff headwinds (25% on goods). Ontario budget planning tariff relief. Trump trade tensions persist. Net effect roughly neutral.",
                    ["Oil exports benefit from $116/bbl Brent", "Ontario budget March 26 includes tariff relief for workers", "Trump's 25% tariff on Canadian goods dampens trade"],
                    ["Energy windfall partially offsets tariff drag", "Canadian dollar appreciation helps consumers"],
                    "Canada GDP roughly stable as oil windfall offsets tariff drag. Watch US-Canada trade dynamics.")
            elif code == "BRA":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.78,
                    "Brazil as net oil exporter benefits from price surge. Geographically insulated from Gulf conflict. Pre-salt production boosting export revenues. Commodity basket (iron, soy, oil) all elevated.",
                    ["Net oil exporter with non-Hormuz export routes", "Commodity prices elevated across the board", "Geographically remote from conflict zone"],
                    ["BRL appreciation could hurt non-commodity exports", "Global recession risk if oil shock persists"],
                    "Brazil GDP growth supported by commodity windfall. Petrobras and mining sectors primary beneficiaries.")
            elif code == "NGA":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.72,
                    "Nigeria benefits from oil price surge to $116/bbl. Non-Hormuz Atlantic coast exports secure. However, domestic refining challenges and Dangote refinery ramp-up complicate picture.",
                    ["Oil prices at record levels benefit Nigerian revenues", "Atlantic coast export routes unaffected", "Dangote refinery reducing fuel import dependence"],
                    ["Oil production capacity constraints limit upside", "Security challenges in Niger Delta persist", "Naira instability dampens domestic growth"],
                    "Nigeria GDP growth lifted by oil windfall. Fiscal position improves but structural challenges remain.")
            elif code == "AUS":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.78,
                    "Australia benefits as LNG premium surges from Qatari supply disruption. Gold at record highs boosts mining revenues. AUD at best levels since 2023. Commodity currency safe haven flows.",
                    ["Australian dollar at highest since 2023", "LNG premium as Qatari supply disrupted", "Gold mining windfall at $5,195/oz"],
                    ["AUD strength pressures non-commodity exporters", "China demand uncertainty clouds outlook"],
                    "Australia GDP growth accelerates on LNG/gold windfall. Mining sector leads.")
            elif code == "COL":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.70,
                    "Colombia benefits from oil exports but Petro's leftist coalition gaining congressional power raises policy uncertainty. Energy transition agenda may limit oil sector expansion. Congressional election results strengthen reform agenda.",
                    ["Oil price surge benefits Colombian exports", "Petro coalition won most congressional seats", "Conservative opposition Paloma Valencia gaining presidential traction"],
                    ["Petro energy transition policies may constrain oil investment", "Peso under pressure from interventionist policy concerns"],
                    "Colombia GDP stable as oil windfall offset by policy uncertainty. Watch Petro reform agenda implementation.")
            elif code == "KAZ":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.80,
                    "Kazakhstan benefits from oil price surge via CPC pipeline (not Hormuz-dependent). Turkic States coordination tested but economic fundamentals improving on energy windfall.",
                    ["CPC pipeline to Black Sea not Hormuz-dependent", "Oil prices at $116/bbl boost fiscal revenues", "OTS foreign ministers meeting shows diplomatic engagement"],
                    ["Russian influence constrains foreign policy options", "Central Asian infrastructure bottlenecks limit export expansion"],
                    "Kazakhstan GDP growth boosted by oil windfall. CPC pipeline route is key strategic advantage.")
        elif code == "ARG":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.80,
                "Argentina GDP -1.3% under Milei's shock therapy. However, becoming net energy exporter for first time via Vaca Muerta — particularly valuable as Gulf crisis drives prices higher. Milei courting Wall Street. Mixed signals.",
                ["GDP contracted -1.3% (Milei shock therapy recession)", "Net energy exports achieved for first time — Vaca Muerta production surge", "Milei Wall Street roadshow attracting foreign investment interest"],
                ["Energy export windfall could offset recession depth", "Structural reforms may yield medium-term growth", "Argentina bonds rallying on reform credibility"],
                "Argentina in recession but energy exporter status provides partial offset. Contrarian opportunity for risk-tolerant investors.")
        elif code == "MEX":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.75,
                "Mexico faces headwinds from 25% US tariffs and oil price impact on import costs. El Mencho (CJNG) killing creates short-term cartel violence risk but long-term security positive. USMCA trade disrupted.",
                ["Trump 25% tariff on Mexican goods", "El Mencho killed — CJNG power vacuum may trigger violence", "Oil price surge increases import costs despite being net exporter"],
                ["El Mencho killing positive for long-term security", "Near-shoring trend benefits Mexican manufacturing", "Oil exports benefit from higher prices"],
                "Mexico GDP under mild pressure from tariffs and short-term security risks. Near-shoring thesis intact longer-term.")
        elif code == "CHN":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.75,
                "China relatively insulated from Hormuz crisis — diversified oil imports, SPR reserves, Russian pipeline supply. Two Sessions tech/AI push signals continued growth focus. But 10% additional US tariff and oil price surge create headwinds.",
                ["Two Sessions vowed tech self-reliance and AI acceleration", "Diversified oil supply (Russia, Central Asia, Africa)", "Arms imports dropped 72% reflecting domestic production capability"],
                ["10% additional US tariff effective March 4 creates trade drag", "Oil price surge adds to import costs", "Property sector still in correction"],
                "China GDP stable at ~5% target. Tech sector acceleration offsets trade and energy headwinds.")
        elif code == "UKR":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.68,
                "Ukraine retaking territory as Russia's buffer zone strategy falters. EU €90B transfer bypassing Hungary provides critical funding. ArcelorMittal Kryvyi Rih operating at a loss signals industrial stress. Peace talks proposed but skepticism high.",
                ["Ukraine retook territory; Russian buffer zone strategy faltering", "EU transferred €90B bypassing Hungary's veto", "US proposed fresh trilateral peace talks — Zelensky confirmed"],
                ["ArcelorMittal steel plant operating at a loss", "Energy costs remain extreme", "World attention pivoting away to Iran war"],
                "Ukraine GDP stabilizing with EU support but industrial base severely damaged. Peace dividend potential if talks progress.")
        elif code == "SGP":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.72,
                "Singapore as trade hub faces disruption from Hormuz closure affecting global shipping routes. Oil price surge impacts refining margins. Asian trade flows rerouting. Financial center safe haven flows partially offset.",
                ["Global trade disruption from Hormuz closure", "Oil price surge affects refining hub operations", "Asian shipping rerouting through longer routes"],
                ["Safe haven financial flows benefit SGP", "Shipping/logistics sector profits from disruption premium"],
                "Singapore GDP growth slows on trade disruption. Financial services sector resilient.")
        elif code == "TWN":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.75,
                "Taiwan heavily dependent on imported energy via Hormuz. Oil shock adds costs to semiconductor manufacturing. Global demand uncertainty clouds tech export outlook.",
                ["Heavy Hormuz oil import dependency", "Semiconductor energy costs rising", "Global demand uncertainty from conflict"],
                ["Semiconductor demand for AI remains robust", "TSMC pricing power partially offsets cost increases"],
                "Taiwan GDP growth moderated by energy costs. Semiconductor sector provides resilience.")
        elif code in {"THA", "MYS", "IDN"}:
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.72,
                f"{name} facing oil shock headwinds as net energy importer. Manufacturing competitiveness eroded by higher input costs. Tourism recovery continues but energy costs weigh on airlines.",
                ["Oil prices surged 25% adding to import costs", "Manufacturing input costs rising", "Asian economic growth outlook deteriorating"],
                ["Domestic demand relatively resilient", "Tourism sector continues recovery", "Central bank policy space available"],
                f"{name} GDP growth revised down 0.3-0.5pp on oil shock. Consumer sectors relatively sheltered.")
        elif code == "ZAF":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.75,
                "South Africa facing unprecedented marine gas oil prices from Gulf disruption. Mining sector benefits from gold windfall but energy costs erode broader economy. Load-shedding risk increases with fuel costs.",
                ["MGO prices at unprecedented highs", "Rand under pressure from terms-of-trade deterioration", "Gold mining windfall partially offsets"],
                ["Gold exports benefit from $5,195/oz prices", "Mining sector provides GDP floor"],
                "South Africa GDP growth under pressure from energy costs. Gold sector is sole bright spot.")
        elif code == "EGY":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.78,
                "Egypt faces severe oil import cost pressure and Suez Canal revenue uncertainty. Tourism disrupted by regional conflict. IMF program constrained. Food import costs rising.",
                ["Oil import bill surging at $116/bbl", "Regional conflict proximity disrupts tourism", "Wheat prices rising affecting food imports"],
                ["Suez Canal traffic may increase from Hormuz rerouting", "IMF program provides fiscal anchor"],
                "Egypt GDP growth revised down sharply. Balance of payments pressure intensifying.")
        elif code in {"VNM", "PHL", "BGD", "PAK"}:
            severity = "decrease"
            if code == "PAK":
                severity = "decrease"
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, severity, 0.72,
                f"{name} faces oil shock headwinds as major energy importer. Remittance flows from Gulf states at risk. Manufacturing export competitiveness eroded by input costs.",
                ["Oil prices surged 25% to $116/bbl", "Gulf worker remittances at risk from regional instability", "Manufacturing input costs rising globally"],
                ["Domestic demand relatively resilient", "Some trade diversion benefits possible"],
                f"{name} GDP growth revised down 0.3-0.5pp. Gulf remittance channel is key vulnerability.")
        elif code in {"CHL", "PER"}:
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.70,
                f"{name} relatively insulated from Gulf crisis. Copper/mineral demand supports exports. Critical mineral supply chain importance growing (UN: demand could triple by 2030).",
                ["Critical mineral demand growing — UN says could triple by 2030", "Geographically remote from conflict", "Copper prices elevated"],
                ["Global recession risk could reduce commodity demand", "Oil import costs rising"],
                f"{name} GDP stable. Critical mineral thesis strengthening long-term.")
        elif code in {"CZE", "ROU", "GRC", "PRT", "FIN", "IRL"}:
            if code == "GRC":
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "growth", 0.72,
                    "Greece's shipping fleet benefits from longer rerouted tanker voyages around Africa. Maritime revenue windfall partially offsets oil import costs. Tourism sector at risk from regional instability.",
                    ["Greek shipping fleet profits from longer routes", "Tanker day rates at record highs", "Rerouting around Africa adds voyage days"],
                    ["Tourism could be impacted by Mediterranean security concerns", "Oil import costs rising"],
                    "Greece GDP boosted by shipping windfall. Unique beneficiary of trade rerouting.")
            else:
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease" if code != "IRL" else "stable", 0.70,
                    f"{name} faces European-wide headwinds from oil shock and market crash. Energy costs rising sharply. Defense spending increasing under NATO commitments.",
                    ["European equity markets crashed ~6%", "Oil prices surged to $116/bbl", "NATO defense spending commitments increasing"],
                    ["ECB accommodation expected", "Defense spending creates industrial stimulus"],
                    f"{name} GDP growth moderated by European-wide headwinds. NATO defense orders provide partial offset.")
        elif code == "NZL":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "decrease", 0.70,
                "New Zealand faces bleak economic outlook. Health Minister retirement signals government instability. Air NZ viability questioned. Oil shock adds to import costs.",
                ["Health Minister Shane Reti retiring — government instability", "Air NZ future questioned amid economic challenges", "Oil import costs rising"],
                ["Commodity exports (dairy, wool) provide buffer", "Geographic isolation limits direct conflict exposure"],
                "New Zealand GDP growth decelerating. Government stability and Air NZ viability key watches.")
        elif code == "MAR":
            add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.68,
                "Morocco relatively insulated from Gulf crisis compared to other MENA states. Phosphate exports benefit from rising agricultural input demand. Tourism faces some regional risk.",
                ["Phosphate exports benefit from food security concerns", "Geographic distance from Gulf conflict", "Renewable energy investments reducing oil dependency"],
                ["Tourism could be impacted by MENA instability", "Oil import costs still rising"],
                "Morocco GDP stable with phosphate export support. Less exposed than Gulf neighbors.")
        else:
            # Default for any remaining countries
            if gdp_growth is not None:
                add_estimate(code, "gdp_real_growth_pct", gdp_growth, "stable", 0.60,
                    f"{name} faces indirect headwinds from global oil shock but no direct exposure to Gulf conflict. GDP growth trajectory broadly unchanged from prior week.",
                    ["Global oil prices elevated at $116/bbl", "No direct Gulf conflict exposure", "Regional economic dynamics broadly stable"],
                    ["Oil price shock may ease with G7 SPR release", "Domestic demand provides buffer"],
                    f"{name} GDP growth broadly stable with modest downward revision from energy costs.")

    # ===== 2. INFLATION CPI =====
    if inflation is not None:
        if code == "IRN":
            add_estimate(code, "inflation_cpi_pct", inflation, "strong_growth", 0.92,
                "Hyperinflation trajectory. War Day 10+ with intensifying bombing. Currency collapse, supply chains destroyed, panic hoarding. Internet shutdown prevents price transparency. CPI likely 50%+ and accelerating.",
                ["Rial in freefall on parallel markets", "Import channels severed by mining of Hormuz", "Tehran under sustained bombing — supply chains destroyed"],
                ["Government price controls could suppress official CPI", "Demand destruction from economic collapse partially offsets"],
                "Iran headed for hyperinflation. Rial-denominated assets worthless.")
        elif code in HORMUZ_AFFECTED_GULF:
            add_estimate(code, "inflation_cpi_pct", inflation, "growth", 0.78,
                f"{name} facing import cost pressure from disrupted supply chains. Energy subsidies buffer consumers but fiscal cost rising. Food import costs increasing as Gulf shipping disrupted.",
                ["Supply chain disruption from Hormuz closure", "Food import costs rising", "Regional uncertainty driving precautionary stockpiling"],
                ["Government subsidies cap consumer prices", "SWFs provide fiscal buffer for subsidy maintenance"],
                f"{name} inflation rising on supply disruption but government subsidies provide buffer.")
        elif code in HEAVY_OIL_IMPORTERS_HORMUZ:
            add_estimate(code, "inflation_cpi_pct", inflation, "growth", 0.82,
                f"{name} facing inflation pressure from oil at $116/bbl. Energy costs feeding through to transportation, manufacturing, and food prices. Central bank faces stagflation dilemma.",
                ["Brent crude surged 25% to $116.50/bbl", "Transportation and manufacturing input costs surging", "Food prices rising on higher logistics costs"],
                ["Central banks may tighten to contain expectations", "G7 SPR release could provide temporary relief"],
                f"{name} inflation rising 0.5-1.0pp from oil shock pass-through. Central bank response is key variable.")
        elif code in EUROPEAN_OIL_IMPORTERS:
            add_estimate(code, "inflation_cpi_pct", inflation, "growth", 0.78,
                f"{name} facing inflation uptick from oil shock feeding through energy, transport, and goods prices. EU admitted 'nuclear blunder' on energy policy. ECB faces stagflation dilemma ahead of March policy meeting.",
                ["Oil prices surged 25% — feeding through to consumer prices", "European energy costs rising sharply", "EU energy policy rethink underway"],
                ["ECB may tighten to contain inflation expectations", "Energy tax cuts being discussed to reduce consumer impact"],
                f"{name} inflation rising 0.3-0.7pp from oil shock. ECB response at next meeting is key catalyst.")
        elif code in OIL_EXPORTERS_SAFE:
            if code == "NGA":
                add_estimate(code, "inflation_cpi_pct", inflation, "growth", 0.75,
                    "Nigeria inflation elevated. Oil price windfall improves fiscal position but Naira instability and import dependency keep consumer prices rising.",
                    ["Naira volatility continues", "Food import costs rising globally", "Oil windfall improves government revenue but not consumer prices"],
                    ["Dangote refinery may reduce fuel import costs", "CBN tightening cycle ongoing"],
                    "Nigeria inflation remains elevated. Oil windfall benefits government coffers, not consumer prices.")
            else:
                trend_val = "stable"
                note = f"{name} as oil exporter benefits from price surge. Domestic inflation contained by energy self-sufficiency. Imported goods inflation the main pressure point."
                if code == "RUS":
                    trend_val = "growth"
                    note = "Russia facing inflation from war economy overheating and sanctions-driven import substitution. Oil windfall partially offsets through stronger fiscal position."
                add_estimate(code, "inflation_cpi_pct", inflation, trend_val, 0.72,
                    note,
                    ["Oil price surge benefits exporters' fiscal position", "Domestic energy costs stable", "Import costs rising globally"],
                    ["Global goods inflation could affect imports", "Currency moves affect import prices"],
                    f"{name} inflation relatively contained. Energy self-sufficiency provides buffer.")
        elif code == "ARG":
            add_estimate(code, "inflation_cpi_pct", inflation, "decrease", 0.78,
                "Argentina inflation decelerating under Milei shock therapy despite still extreme levels. Monthly rates declining. Fiscal austerity and monetary tightening taking effect. Energy exporter status reduces oil shock pass-through.",
                ["Monthly inflation rates declining under Milei austerity", "Fiscal balance improving", "Net energy exporter status buffers oil shock"],
                ["Recession-driven demand destruction may be temporary", "Social pressures could force policy reversal"],
                "Argentina inflation trend improving despite high absolute level. Milei reform credibility key to continued progress.")
        elif code == "CHN":
            add_estimate(code, "inflation_cpi_pct", inflation, "stable", 0.72,
                "China facing near-zero/deflationary pressures from weak domestic demand and property sector correction. Oil price surge partially offsets but PBoC maintaining accommodative stance. Two Sessions signal stimulus continuation.",
                ["Domestic demand weak; property correction ongoing", "Oil price surge adds cost-push pressure", "PBoC maintaining accommodative monetary policy"],
                ["Stimulus measures could boost demand-pull inflation", "Tech sector investment may create pockets of demand"],
                "China inflation near zero. Deflation risk persists despite oil shock. PBoC has ample policy space.")
        else:
            # Default: most countries face mild inflation pressure from oil
            add_estimate(code, "inflation_cpi_pct", inflation, "growth", 0.68,
                f"{name} facing mild inflation pressure from global oil price surge to $116/bbl feeding through energy and transport costs.",
                ["Brent crude surged 25% to $116.50/bbl", "Global transport costs rising", "Food prices affected by logistics costs"],
                ["Central banks may tighten preemptively", "G7 SPR release could cap oil prices"],
                f"{name} inflation rising modestly from oil shock. Central bank response and energy subsidy policies determine magnitude.")

    # ===== 3. CURRENT ACCOUNT % GDP =====
    if ca_gdp is not None:
        if code == "IRN":
            add_estimate(code, "current_account_pct_gdp", ca_gdp, "strong_decrease", 0.94,
                "Oil export revenue eliminated by Hormuz mine-laying. Current account swinging deeply negative. Military imports continue via overland routes but export capacity near zero. Day 10+ of war.",
                ["Hormuz physically mined — not just blockaded", "Oil exports (~70% of revenue) completely halted", "Internet shutdown indicates economic paralysis"],
                ["Some overland trade via Turkey/Pakistan continues", "War-era barter arrangements may develop"],
                "Iran current account in catastrophic deficit. External payments capacity destroyed.")
        elif code in HORMUZ_AFFECTED_GULF:
            trend = "strong_decrease" if code in {"KWT", "QAT"} else "decrease"
            add_estimate(code, "current_account_pct_gdp", ca_gdp, trend, 0.85,
                f"{name} current account deteriorating as Hormuz disruption blocks energy exports. High oil/gas prices cannot be monetized. Import costs rising. SWF drawdowns support consumption.",
                [f"Hormuz mine-laying blocks {name}'s primary export route", "VLCC insurance withdrawn", "Import costs rising from disrupted supply chains"],
                ["Pipeline alternatives (where available) provide partial relief", "SWF assets provide external buffer"],
                f"{name} current account surplus evaporating. Export channel disruption key issue.")
        elif code in HEAVY_OIL_IMPORTERS_HORMUZ:
            add_estimate(code, "current_account_pct_gdp", ca_gdp, "decrease", 0.80,
                f"{name} current account worsening from oil import bill surge at $116/bbl. Energy import costs adding 1-2pp to deficit. Trade balance deteriorating.",
                ["Oil import costs surged with Brent at $116/bbl", f"{name} dependent on Gulf oil", "Trade balance deteriorating on energy costs"],
                ["Export demand for non-energy goods may hold", "Currency depreciation improves competitiveness"],
                f"{name} current account deficit widening. Energy import bill is primary driver.")
        elif code in OIL_EXPORTERS_SAFE:
            add_estimate(code, "current_account_pct_gdp", ca_gdp, "growth", 0.78,
                f"{name} current account improving as oil/commodity prices surge and non-Hormuz export routes remain secure. Trade surplus widening.",
                ["Oil/commodity prices at multi-year highs", "Non-Hormuz export routes fully operational", "Terms of trade improving dramatically"],
                ["Global demand may weaken if oil shock persists", "Currency appreciation may erode non-commodity trade"],
                f"{name} current account surplus expanding on commodity windfall.")
        elif code == "USA":
            add_estimate(code, "current_account_pct_gdp", ca_gdp, "stable", 0.68,
                "US current account roughly stable. Energy self-sufficiency buffers oil shock impact. Tariffs (15% Section 122) reduce imports. But war costs add to transfers. Safe-haven dollar inflows support.",
                ["US energy self-sufficient — domestic production covers consumption", "15% Section 122 tariffs reduce imports", "Safe-haven capital inflows support dollar"],
                ["War costs adding to external transfers", "Tariff refund litigation ($175B) creates fiscal uncertainty"],
                "US current account stable. Competing forces roughly offsetting.")
        else:
            # Default: most importers see CA deterioration from oil
            is_exporter = code in OIL_EXPORTERS_SAFE
            trend = "growth" if is_exporter else "decrease"
            add_estimate(code, "current_account_pct_gdp", ca_gdp, trend, 0.65,
                f"{name} current account {'improving on commodity windfall' if is_exporter else 'deteriorating from higher oil import costs at $116/bbl'}.",
                [f"Oil prices surged 25% to $116/bbl", f"{'Commodity exports benefit from price surge' if is_exporter else 'Energy import bill rising sharply'}"],
                ["G7 SPR release may cap oil prices", "Currency adjustments provide partial offset"],
                f"{name} current account {'surplus expanding' if is_exporter else 'deficit widening'} from energy price dynamics.")

    # ===== 4. GOVT DEBT % GDP =====
    if debt_gdp is not None:
        if code == "IRN":
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "strong_growth", 0.85,
                "Iran debt-to-GDP ratio exploding as GDP collapses and emergency war spending surges. Nominal debt metrics meaningless given currency collapse. Real fiscal position catastrophic.",
                ["GDP in freefall", "Emergency war spending escalating", "Revenue from oil exports eliminated"],
                ["Low pre-war nominal debt ratio", "Money printing replaces borrowing in wartime"],
                "Iran fiscal position destroyed. Debt metrics unreliable given economic collapse.")
        elif code in (WAR_ZONE - {"IRN"}):  # ISR
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "growth", 0.82,
                "Israel debt rising from multi-front war spending. Reserve mobilization costs. US support offsets some burden but fiscal trajectory deteriorating.",
                ["Multi-front military operations consuming resources", "Reserve mobilization pulling from productive economy", "Defense supplementals required"],
                ["US military aid significant", "Strong pre-war fiscal position", "High-tech economy generates tax revenue"],
                "Israel debt trajectory worsening. War duration is key determinant of fiscal impact.")
        elif code == "USA":
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "growth", 0.82,
                "US debt rising from war spending (Operation Epic Fury) plus potential $175B tariff refund liability from SCOTUS ruling. Defense supplementals likely. Higher rates increase debt service. No fiscal consolidation visible.",
                ["War costs escalating — 'most intense phase' promised", "$175B tariff refund lawsuits create contingent liability", "Fed rates at 3.625% increase debt service costs"],
                ["Economic growth generates revenue", "Dollar reserve status provides financing advantage"],
                "US debt trajectory concerning. War costs plus tariff refund liability add fiscal pressure.")
        elif code in HORMUZ_AFFECTED_GULF:
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "growth", 0.75,
                f"{name} debt ratio rising as revenue drops from export disruption while spending (defense, subsidies) increases. SWF drawdowns buffer but deplete reserves.",
                ["Revenue from energy exports disrupted", "Defense spending increasing", "Consumer subsidies maintained despite revenue loss"],
                ["SWFs provide massive fiscal buffer", "Low pre-crisis debt levels"],
                f"{name} debt rising from revenue shortfall. SWF resilience key to fiscal stability.")
        elif code in OIL_EXPORTERS_SAFE:
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "decrease", 0.72,
                f"{name} debt ratio improving as oil/commodity windfall boosts government revenue. Fiscal surplus expanding or deficit narrowing.",
                ["Energy revenue surge from oil at $116/bbl", "Non-Hormuz export routes secure", "Fiscal position strengthening"],
                ["Pressure to increase spending on military/subsidies", "Windfall may be temporary"],
                f"{name} debt ratio improving on energy windfall. Fiscal discipline key to lasting benefit.")
        else:
            # Most countries: debt growing from higher costs and lower growth
            add_estimate(code, "govt_debt_pct_gdp", debt_gdp, "growth", 0.68,
                f"{name} debt ratio rising modestly as oil shock reduces growth and increases government energy costs/subsidies. Interest rates remain elevated.",
                ["Oil shock reduces growth, lowering tax revenue", "Energy subsidies/transfers increase spending", "Interest rates remain elevated globally"],
                ["Fiscal consolidation measures possible", "Growth could surprise to upside"],
                f"{name} debt trajectory worsening modestly. Fiscal space narrowing across most economies.")

    # ===== 5. POLITICAL STABILITY (WGI) =====
    # Try to find political stability score
    pol_stab = get_nested_value(cdata, "institutions", "wgi_political_stability")
    if pol_stab is None:
        pol_stab = get_nested_value(cdata, "political", "political_stability_score")
    if pol_stab is None:
        pol_stab = get_nested_value(cdata, "institutions", "political_stability_score")
    if pol_stab is None:
        pol_stab = get_nested_value(cdata, "derived", "political_risk_premium_bps")

    # Use a synthetic value for political stability based on context
    if code == "IRN":
        add_estimate(code, "political_stability", pol_stab, "strong_decrease", 0.95,
            "Iran political stability collapsed. Supreme Leader killed Feb 28. Capital under sustained bombing. Internet shut down. Kurdish invasion from west. IRGC claims control but governance paralyzed. State approaching collapse.",
            ["Supreme Leader Khamenei killed", "Tehran under sustained US-Israeli bombing", "Kurdish ground forces invading from west with US air support"],
            ["IRGC chain of command may maintain some control", "Historical resilience of Iranian state institutions"],
            "Iran political stability near zero. State integrity at risk. Regime survival uncertain.")
    elif code == "ISR":
        add_estimate(code, "political_stability", pol_stab, "strong_decrease", 0.88,
            "Israel facing multi-front war with extended duration. Hezbollah escalating from Lebanon. Society under war strain. National unity government but reserves mobilization creating economic friction.",
            ["Multi-front war: Iran + Hezbollah + proxy forces", "Hezbollah 'reckless war' endangering Lebanon and Israel", "International condemnation of civilian casualties growing"],
            ["National unity in wartime", "Strong institutional resilience", "US support provides security backstop"],
            "Israel political stability severely tested by extended multi-front conflict.")
    elif code in HORMUZ_AFFECTED_GULF:
        add_estimate(code, "political_stability", pol_stab, "decrease", 0.78,
            f"{name} political stability declining from Gulf conflict proximity. Economic disruption from Hormuz closure creating internal pressure. Security concerns elevated.",
            ["Hormuz disruption threatens economic model", "Regional conflict proximity", "Population anxiety from nearby military operations"],
            ["Strong security apparatus", "Regime legitimacy from economic distribution"],
            f"{name} political stability under pressure from regional conflict and economic disruption.")
    elif code == "USA":
        add_estimate(code, "political_stability", pol_stab, "decrease", 0.80,
            "US political stability declining. War with Iran has no clear endpoint. DHS Secretary fired. $175B tariff refund SCOTUS crisis. 5 recession warning signs identified. Midterm mood favoring Democrats. Rand Paul warns of 'disastrous' midterms.",
            ["War expanding — boots on ground 'not ruled out'", "DHS Secretary Noem fired mid-war", "SCOTUS tariff crisis plus $175B refund liability", "Midterm polls favor Democrats; GOP in 'course correction mode'"],
            ["Institutional resilience remains strong", "Economy still generating jobs"],
            "US political stability declining on war, constitutional, and fiscal fronts simultaneously.")
    elif code == "UKR":
        add_estimate(code, "political_stability", pol_stab, "stable", 0.65,
            "Ukraine political stability steady. Territory retaken. EU €90B funding secured. Peace talks proposed. But world attention shifting to Iran reduces leverage.",
            ["Territory being retaken", "€90B EU funding secured", "Fresh peace talks proposed"],
            ["World attention shifting to Iran", "ArcelorMittal losses signal industrial decay"],
            "Ukraine political stability holding with EU support. Peace talks offer cautious optimism.")
    elif code == "COL":
        add_estimate(code, "political_stability", pol_stab, "stable", 0.70,
            "Colombia political dynamics shifting. Petro coalition won congressional majority. Opposition candidate Paloma Valencia gaining. Democratic transitions proceeding normally.",
            ["Petro coalition won most congressional seats", "Opposition gaining presidential traction", "Democratic process functioning"],
            ["Petro reform agenda could create social friction", "Drug trafficking violence continues"],
            "Colombia political stability adequate. Congressional result strengthens Petro but opposition rising.")
    elif code == "MEX":
        add_estimate(code, "political_stability", pol_stab, "stable", 0.72,
            "Mexico political stability mixed. El Mencho killing is major security milestone but CJNG power vacuum risks short-term violence. US tariff tensions persist. Institutional continuity under Sheinbaum.",
            ["El Mencho (CJNG leader) killed — major cartel disruption", "CJNG power vacuum may trigger turf wars", "US-Mexico trade tensions continue"],
            ["Sheinbaum government maintaining stability", "Military institutions performing effectively"],
            "Mexico political stability neutral. El Mencho killing positive long-term, risky short-term.")
    elif code in EUROPEAN_OIL_IMPORTERS:
        if code == "DEU":
            add_estimate(code, "political_stability", pol_stab, "decrease", 0.75,
                "Germany political stability weakening. VW slashing 50,000 jobs — largest in German auto history. EU admitted 'nuclear blunder' on energy. European markets crashed 6%. Industrial competitiveness crisis deepening.",
                ["VW 50,000 job cuts — worst in German auto history", "European market crash ~6%", "Energy policy failure acknowledged"],
                ["Coalition government stable", "NATO defense spending creating industrial demand"],
                "Germany political stability under pressure from industrial decline and energy crisis.")
        elif code == "GBR":
            add_estimate(code, "political_stability", pol_stab, "stable", 0.70,
                "UK political stability adequate. Starmer leaked memo controversy over Scotland/Wales override powers. HMS Dragon deploying to Gulf. Energy costs rising but managed.",
                ["HMS Dragon deploying to Gulf — UK military commitment", "Leaked memo on devolved government powers", "UK-China tensions from Jimmy Lai case"],
                ["Starmer government has strong parliamentary majority", "Institutional resilience"],
                "UK political stability stable. Devolution tensions and Gulf deployment manageable.")
        elif code == "TUR":
            add_estimate(code, "political_stability", pol_stab, "decrease", 0.72,
                "Turkey facing complex balancing act between NATO membership and regional relationships. Turkic States coordination tested. Kurdish proxy war in Iran creates domestic concerns. NATO obligations conflict with regional interests.",
                ["NATO member while maintaining Iran relationships", "Kurdish invasion of Iran concerns Turkey", "OTS foreign ministers meeting tested Turkic coordination"],
                ["Erdogan experienced at managing competing pressures", "Turkey's geographic importance gives leverage"],
                "Turkey political stability declining on conflicting alliance pressures and Kurdish proxy concerns.")
        else:
            add_estimate(code, "political_stability", pol_stab, "stable", 0.65,
                f"{name} political stability broadly maintained. European-wide stress from oil shock and market crash creates background pressure but institutions holding.",
                ["European markets crashed ~6%", "Energy costs rising", "NATO defense commitments increasing"],
                ["Strong institutional frameworks", "EU solidarity provides support"],
                f"{name} political stability adequate despite external pressures.")
    else:
        if pol_stab is not None or code in all_countries:
            add_estimate(code, "political_stability", pol_stab, "stable", 0.60,
                f"{name} political stability broadly unchanged this week. Global oil shock creates background economic pressure but no direct political triggers.",
                ["No major domestic political events", "Global oil shock creates economic pressure", "Regional dynamics broadly stable"],
                ["External shocks could crystallize latent tensions", "Fiscal pressure from oil costs may constrain policy"],
                f"{name} political stability holding. Monitor for fiscal pressure pass-through to social stability.")

    # ===== 6. MILITARY EXPENDITURE % GDP =====
    # All branches produce an estimate (use mil_pct which may be None for current_value)
    if code in WAR_ZONE:
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "strong_growth", 0.92,
            f"{name} military spending surging due to active war. Emergency defense spending eclipsing all other budget priorities. {'Operation Epic Fury and Roaring Lion consuming massive resources.' if code == 'ISR' else 'Total mobilization spending.'}",
            ["Active war requiring maximum military resources", "SIPRI: global arms transfers up 9.2%", "Emergency defense supplementals inevitable"],
            ["GDP contraction inflates ratio even without spending increase", "International aid offsets some cost"],
            f"{name} military spending as % of GDP surging. War economy dominant.")
    elif code in HORMUZ_AFFECTED_GULF:
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.80,
            f"{name} increasing defense spending in response to Gulf conflict. Regional arms race accelerating. SIPRI data shows Middle East arms imports up despite recent decline.",
            ["Gulf conflict driving defense spending increase", "SIPRI 2026: global arms transfers +9.2%", "Regional security environment deteriorating"],
            ["Fiscal constraints from revenue disruption", "US providing security umbrella"],
            f"{name} defense spending rising. Regional arms race dynamics intensifying.")
    elif code in NATO_DEFENSE_GROWTH:
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.82,
            f"{name} defense spending growing under NATO 2% commitment. SIPRI: European arms imports up 210%. All 32 NATO members now at 2% GDP target. US arms exports up 27% — Europe now top recipient region.",
            ["NATO all 32 members now at 2% GDP target", "SIPRI: European arms imports surged 210%", "US supplied 58% of NATO European imports"],
            ["Fiscal constraints may slow pace", "Public opinion varies on defense vs. social spending"],
            f"{name} defense spending on structural uptrend. NATO commitments and SIPRI data confirm long-term growth.")
    elif code == "CHN":
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.78,
            "China continuing military modernization. Arms imports dropped 72% reflecting domestic production capability. Two Sessions signaled continued tech/defense focus. PLA budget expected to increase 7-8%.",
            ["SIPRI: China arms imports -72% (domestic production)", "Two Sessions tech self-reliance push includes defense", "PLA modernization on track"],
            ["GDP growth slowing modestly", "Fiscal priorities competing with stimulus needs"],
            "China defense spending growing steadily. Domestic production replacing imports — self-sufficiency improving.")
    elif code == "IND":
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.78,
            "India defense spending increasing. SIPRI: world's 2nd largest arms importer. Reducing Russian dependence (40% from 51%). China investment curbs easing signals complex strategic recalibration.",
            ["SIPRI: India world's 2nd largest arms importer", "Russian share of imports declining (40% from 51%)", "Easing Chinese investment curbs signals strategic flexibility"],
            ["Fiscal deficit constraints", "Competing development spending priorities"],
            "India defense spending growth stable. Arms supply diversification away from Russia accelerating.")
    elif code == "PAK":
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.75,
            "Pakistan defense spending increasing. SIPRI: arms imports grew 66% with China supplying 80%. India rivalry drives continued military investment.",
            ["SIPRI: Pakistan arms imports +66%", "China supplies 80% of Pakistani arms", "India rivalry sustains spending pressure"],
            ["IMF fiscal conditions constrain spending", "Economic crisis limits budget flexibility"],
            "Pakistan defense spending growing despite fiscal constraints. China as primary arms supplier deepening dependency.")
    elif code == "UKR":
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "strong_growth", 0.88,
            "Ukraine defense spending at extreme levels. SIPRI: world's largest arms importer (9.7% global share, up from 0.1%). EU €90B transfer sustains military effort. Territory being retaken.",
            ["SIPRI: Ukraine world's largest arms importer — 9.7% share", "EU €90B transfer secured", "Active counteroffensive retaking territory"],
            ["GDP so depleted that ratio is inflated", "International aid bears most actual cost"],
            "Ukraine defense spending at wartime maximum. Externally funded but commitment demonstrated.")
    elif code == "RUS":
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "growth", 0.80,
            "Russia maintaining high military spending for Ukraine war. Arms export collapse (-64% to 6.8% share) redirected to domestic use. War economy sustains GDP but crowds out civilian spending.",
            ["SIPRI: Russian arms exports collapsed -64%", "War economy requiring sustained high spending", "Domestic arms production replacing lost export capacity"],
            ["Economic strain from sustained war spending", "Sanctions limiting technology access"],
            "Russia military spending elevated by war. Arms export collapse reflects redirected production to domestic use.")
    else:
        add_estimate(code, "military_expenditure_pct_gdp", mil_pct, "stable", 0.62,
            f"{name} defense spending broadly stable. SIPRI global arms transfers +9.2% reflects broad rearmament trend but {name} not at center of current conflict dynamics.",
            ["SIPRI: global arms transfers +9.2%", "Regional security environment stable", "No direct military engagement"],
            ["Fiscal constraints may limit increases", "Domestic spending priorities compete"],
            f"{name} defense spending stable. Global rearmament trend provides modest upward bias.")

    # ===== 7. TRADE OPENNESS =====
    if trade_openness is not None:
        if code in WAR_ZONE | HORMUZ_AFFECTED_GULF:
            add_estimate(code, "trade_openness_pct", round(trade_openness, 1), "strong_decrease" if code in WAR_ZONE else "decrease", 0.82,
                f"{name} trade openness collapsing as Hormuz disruption blocks maritime trade. Both exports and imports severely disrupted. Overland routes insufficient to replace sea trade.",
                ["Hormuz mine-laying blocks maritime trade", "VLCC insurance withdrawn", "Supply chains disrupted"],
                ["Overland trade routes (where available) partially compensate", "Trade will resume when hostilities cease"],
                f"{name} trade openness declining sharply. Maritime commerce effectively halted.")
        elif code in HEAVY_OIL_IMPORTERS_HORMUZ:
            add_estimate(code, "trade_openness_pct", round(trade_openness, 1), "decrease", 0.72,
                f"{name} trade openness declining as oil shock disrupts trade patterns. Higher import costs reduce trade volumes. Supply chain rerouting underway but costly.",
                ["Oil shock disrupting trade patterns", "Asian shipping rerouting around Africa", "Import costs rising from energy and logistics"],
                ["Trade diversion to non-Gulf suppliers", "IATA: air cargo supported $157B in frontloaded trade"],
                f"{name} trade openness modestly declining. Shipping disruption and cost increases reduce trade intensity.")
        else:
            add_estimate(code, "trade_openness_pct", round(trade_openness, 1) if trade_openness else None, "stable", 0.60,
                f"{name} trade openness broadly stable. Global trade disruption from Hormuz primarily affects Gulf-dependent routes. Some trade rerouting benefits alternative routes.",
                ["Global trade disruption mainly Gulf-focused", "Alternative trade routes operational", "Trade frontloading effect from 2025 now unwinding"],
                ["Trade rerouting could benefit non-Gulf routes", "G7 coordination supports trade stability"],
                f"{name} trade openness stable with modest headwinds from global disruption.")

    # ===== 8. FDI NET INFLOWS =====
    if fdi is not None:
        if code in WAR_ZONE:
            add_estimate(code, "fdi_net_inflows_usd", fdi, "strong_decrease", 0.90,
                f"{name} FDI flows halted by active war. International investors withdrawing. Capital flight accelerating. No new investment possible under current conditions.",
                ["Active war destroying investment environment", "International sanctions/isolation", "Infrastructure destruction"],
                ["Post-war reconstruction will attract investment eventually", "Resource endowment remains"],
                f"{name} FDI effectively zero. Capital flight dominant.")
        elif code in HORMUZ_AFFECTED_GULF:
            add_estimate(code, "fdi_net_inflows_usd", fdi, "decrease", 0.78,
                f"{name} FDI declining as Gulf conflict creates uncertainty. International investors reassessing regional risk. Vision 2030-type diversification plans delayed.",
                ["Regional conflict uncertainty deters investment", "Risk premiums elevated for all Gulf states", "Project delays as international partners reassess"],
                ["SWFs continue domestic investment programs", "Conflict is expected to be temporary", "High oil prices make energy investment attractive long-term"],
                f"{name} FDI declining on conflict uncertainty. Long-term investment thesis intact if conflict resolves.")
        elif code == "USA":
            add_estimate(code, "fdi_net_inflows_usd", fdi, "stable", 0.70,
                "US FDI inflows broadly stable. War creating uncertainty but safe-haven status supports. SCOTUS tariff ruling creates trade policy uncertainty. Defense sector attracting investment.",
                ["Safe-haven status attracts capital in crisis", "Defense sector investment surge", "SCOTUS tariff ruling creates policy uncertainty"],
                ["$175B tariff refund liability deters some investors", "War costs add fiscal uncertainty"],
                "US FDI stable. Safe-haven flows offset war and policy uncertainty.")
        elif code in {"IND"}:
            add_estimate(code, "fdi_net_inflows_usd", fdi, "growth", 0.72,
                "India FDI potentially improving as China investment curbs eased. Gulf worker/remittance disruption partially offset by India's attractiveness as manufacturing alternative. Modi government actively courting investment.",
                ["India easing Chinese investment restrictions", "Manufacturing diversification from China benefiting India", "Gulf disruption creates some investment relocation"],
                ["Gulf remittance disruption creates economic headwinds", "Oil costs impact manufacturing competitiveness"],
                "India FDI trending up on China curb easing and manufacturing diversification.")
        elif code == "ARG":
            add_estimate(code, "fdi_net_inflows_usd", fdi, "growth", 0.72,
                "Argentina FDI improving as Milei reforms attract Wall Street attention. Net energy exporter status particularly attractive during Gulf crisis. Vaca Muerta investment accelerating.",
                ["Milei Wall Street roadshow attracting interest", "Net energy exporter status — first time", "Vaca Muerta shale production surging"],
                ["Recession creates near-term economic risk", "Reform sustainability uncertain", "Capital controls still in place"],
                "Argentina FDI improving on reform credibility and energy exporter thesis. Vaca Muerta is key draw.")
        else:
            # Default: mild negative from global uncertainty
            add_estimate(code, "fdi_net_inflows_usd", fdi, "stable", 0.58,
                f"{name} FDI broadly stable with mild downward pressure from global uncertainty. Gulf conflict creating risk-off sentiment across emerging markets.",
                ["Global risk-off sentiment from Gulf conflict", "Capital flight to safe havens", "Regional dynamics broadly unchanged"],
                ["Investment diversification from conflict zones benefits neutral countries", "Low valuations attract contrarian capital"],
                f"{name} FDI stable. Global risk-off sentiment creates mild headwind.")
    else:
        # No FDI data available — still generate an estimate with None value
        add_estimate(code, "fdi_net_inflows_usd", None, "stable", 0.50,
            f"{name} FDI data not available. Trend assumed stable given no direct conflict exposure and no country-specific FDI signals this week.",
            ["No FDI data available for trend comparison", "Global risk-off sentiment from Gulf conflict"],
            ["Investment diversification may benefit neutral countries"],
            f"{name} FDI trend indeterminate. No data for quantitative assessment.")

    # ===== 9. EXCHANGE RATE VS USD =====
    # Trend direction: growth = appreciation vs USD, decrease = depreciation
    if code in WAR_ZONE:
        add_estimate(code, "exchange_rate_vs_usd", None, "strong_decrease", 0.92,
            f"{name} currency in freefall against USD. War, sanctions, and economic collapse driving capital flight. Parallel market rates diverging from official.",
            ["Active war destroying confidence", "Capital flight accelerating", "Parallel market divergence extreme"],
            ["Capital controls limit official rate moves", "Some informal support from allies"],
            f"{name} currency collapsing. USD strength adds to pressure.")
    elif code in HORMUZ_AFFECTED_GULF:
        # Most Gulf currencies are pegged to USD
        add_estimate(code, "exchange_rate_vs_usd", None, "stable", 0.80,
            f"{name} currency pegged to USD. Peg under pressure from fiscal strain but central bank defending. FX reserves adequate for now.",
            ["Currency peg to USD maintained", "Central bank defending aggressively", "SWF reserves provide buffer"],
            ["Revenue disruption threatens long-term peg viability", "Speculative pressure building"],
            f"{name} currency peg holding for now. Watch FX reserve depletion rate.")
    elif code == "AUS":
        add_estimate(code, "exchange_rate_vs_usd", None, "growth", 0.78,
            "Australian dollar at best levels since 2023. Rising commodity prices, hawkish RBA, China stimulus, and safe-haven commodity currency flows all supporting AUD.",
            ["AUD at highest since 2023", "Commodity prices elevated (LNG, gold, iron ore)", "Safe-haven commodity currency flows"],
            ["Global risk-off could reverse flows", "China demand uncertainty"],
            "AUD strengthening on commodity windfall. Benefits consumers but pressures exporters.")
    elif code in OIL_EXPORTERS_SAFE:
        if code == "RUS":
            add_estimate(code, "exchange_rate_vs_usd", None, "growth", 0.68,
                "Ruble modestly strengthening on oil windfall at $116/bbl. Capital controls maintaining stability. Shadow economy complicates assessment.",
                ["Oil revenue surge at $116/bbl", "Capital controls maintaining stability", "Ship-to-ship transfers expanding revenue channels"],
                ["Sanctions limit price realization", "War costs draining reserves"],
                "Ruble modestly supported by oil windfall despite sanctions.")
        elif code in {"NOR", "CAN"}:
            add_estimate(code, "exchange_rate_vs_usd", None, "growth", 0.72,
                f"{name} currency strengthening as commodity exporter benefiting from oil/energy price surge. Safe-haven and commodity flows both supportive.",
                ["Oil/commodity price surge", "Non-Hormuz export routes secure", "Commodity currency demand rising"],
                ["US dollar strength from safe-haven demand offsets", "Central bank may resist appreciation"],
                f"{name} currency modestly appreciating on energy windfall.")
        else:
            add_estimate(code, "exchange_rate_vs_usd", None, "stable", 0.62,
                f"{name} currency stable to modestly stronger on commodity exports. Oil windfall supports but USD safe-haven demand provides counterweight.",
                ["Commodity export revenue rising", "USD safe-haven demand strong"],
                ["Central bank intervention possible", "Regional dynamics may limit gains"],
                f"{name} currency stable with modest positive bias from commodity windfall.")
    elif code in HEAVY_OIL_IMPORTERS_HORMUZ | {"EGY", "PAK", "BGD"}:
        add_estimate(code, "exchange_rate_vs_usd", None, "decrease", 0.78,
            f"{name} currency under pressure from widening trade deficit due to oil shock. Terms of trade deteriorating. Central bank may need to intervene.",
            ["Oil import bill surging at $116/bbl", "Trade deficit widening", "Capital flight to safe-haven USD"],
            ["Central bank reserves provide buffer", "FX intervention possible"],
            f"{name} currency depreciating on terms-of-trade deterioration from oil shock.")
    elif code == "CHN":
        add_estimate(code, "exchange_rate_vs_usd", None, "stable", 0.72,
            "CNY broadly stable. PBoC managing controlled depreciation. Oil costs offset by trade surplus. Capital controls effective. Two Sessions signals stability priority.",
            ["PBoC managing exchange rate actively", "Trade surplus provides support", "Capital controls effective"],
            ["Deflationary pressures could weaken", "US tariffs reduce export revenue"],
            "CNY stable under PBoC management. No disorderly moves expected.")
    elif code == "ARG":
        add_estimate(code, "exchange_rate_vs_usd", None, "growth", 0.70,
            "Argentine peso stabilizing under Milei reforms. Crawling peg regime reducing gap between official and parallel rates. Energy exporter status provides fundamental support.",
            ["Milei reforms reducing parallel market gap", "Net energy exporter for first time", "Wall Street engagement improving confidence"],
            ["Recession weighing on fundamentals", "Capital controls still limiting flows"],
            "Argentine peso improving on reform credibility. Gap between official and parallel rates narrowing.")
    elif code in EUROPEAN_OIL_IMPORTERS:
        add_estimate(code, "exchange_rate_vs_usd", None, "decrease", 0.68,
            f"{'EUR' if region == 'europe' else f'{name} currency'} under mild pressure from European market crash and energy import costs. USD safe-haven demand dominant. ECB policy response key variable.",
            ["European markets crashed ~6%", "USD safe-haven demand elevated", "Energy import costs rising"],
            ["ECB may raise rates to defend currency", "European current account still positive overall"],
            f"{name} currency mildly depreciating vs USD. European-wide energy and market stress weighing.")
    else:
        add_estimate(code, "exchange_rate_vs_usd", None, "stable", 0.55,
            f"{name} currency broadly stable against USD. No direct conflict exposure. Global risk-off sentiment creates mild depreciation pressure against safe-haven dollar.",
            ["USD safe-haven demand elevated", "No direct conflict exposure", "Regional dynamics stable"],
            ["Central bank intervention provides stability", "Fundamentals broadly unchanged"],
            f"{name} currency stable with mild depreciation bias from USD safe-haven demand.")

    # ===== 10. OVERALL INVESTMENT RISK SCORE =====
    risk_score = get_nested_value(cdata, "derived", "political_risk_premium_bps")
    if risk_score is None:
        risk_score = get_nested_value(cdata, "derived", "overall_investment_risk_score")

    if code in WAR_ZONE:
        add_estimate(code, "overall_investment_risk_score", risk_score, "strong_decrease", 0.95,
            f"{name} investment risk at maximum. Active war, infrastructure destruction, and economic collapse make all investment uninvestable. Risk premium off the charts.",
            ["Active war Day 10+", "Infrastructure being destroyed", "Economy in freefall"],
            ["Post-war reconstruction opportunity eventually", "Resource base intact"],
            f"{name} uninvestable. Maximum risk across all dimensions.")
    elif code in HORMUZ_AFFECTED_GULF:
        add_estimate(code, "overall_investment_risk_score", risk_score, "decrease", 0.82,
            f"{name} investment risk elevated significantly. Hormuz disruption blocks primary economic activity. SWF reserves buffer but not indefinitely. Conflict duration is key uncertainty.",
            ["Hormuz closure blocks primary revenue stream", "Regional conflict proximity", "VLCC insurance withdrawn"],
            ["SWFs provide substantial buffer", "Conflict expected to be temporary", "High energy prices benefit eventual recovery"],
            f"{name} investment risk elevated. Underweight until Hormuz reopens.")
    elif code == "USA":
        add_estimate(code, "overall_investment_risk_score", risk_score, "decrease", 0.78,
            "US investment risk rising but from a strong base. War costs, SCOTUS tariff crisis, recession warning signs, and bond market stress all add to risk. But US remains core allocation on institutional strength.",
            ["5 recession warning signs identified", "Bond market basis trade unwinding — $1T+ at risk", "War costs escalating with no endpoint", "Dow fell 800+ points"],
            ["Institutional resilience", "Energy self-sufficiency", "Dollar reserve status"],
            "US investment risk rising but remains investable. Defensive positioning warranted: Treasuries, gold, defense, energy.")
    elif code in HEAVY_OIL_IMPORTERS_HORMUZ:
        add_estimate(code, "overall_investment_risk_score", risk_score, "decrease", 0.78,
            f"{name} investment risk rising from oil shock exposure and energy supply vulnerability. Current account pressure and inflation risks compound.",
            ["Heavy Hormuz oil import dependency", "Inflation rising from energy costs", "Current account pressure increasing"],
            ["G7 SPR release provides temporary buffer", "Strong institutional frameworks", "Diversification of energy sources underway"],
            f"{name} investment risk elevated. Energy dependency is key vulnerability.")
    elif code in OIL_EXPORTERS_SAFE:
        add_estimate(code, "overall_investment_risk_score", risk_score, "growth", 0.72,
            f"{name} investment risk improving as oil/commodity windfall boosts fiscal position and economic growth. Non-Hormuz export routes provide strategic advantage.",
            ["Oil/commodity prices at multi-year highs", "Non-Hormuz routes secure", "Fiscal position improving"],
            ["Windfall may be temporary if conflict resolves", "Resource curse dynamics"],
            f"{name} investment risk improving. Energy windfall creates opportunistic entry points.")
    elif code in EUROPEAN_OIL_IMPORTERS:
        add_estimate(code, "overall_investment_risk_score", risk_score, "decrease", 0.72,
            f"{name} investment risk modestly elevated from European market crash, oil shock, and defense spending reallocation. But institutional strength provides resilience.",
            ["European markets crashed ~6%", "Oil shock raising costs", "Defense spending crowding out other investment"],
            ["Strong institutional frameworks", "ECB policy support expected", "NATO defense orders create industrial demand"],
            f"{name} investment risk modestly elevated. European-wide energy and market stress weighing.")
    else:
        add_estimate(code, "overall_investment_risk_score", risk_score, "stable", 0.58,
            f"{name} investment risk broadly unchanged. Global oil shock creates background pressure but no direct exposure to Gulf conflict. Fundamentals stable.",
            ["No direct conflict exposure", "Global risk-off sentiment mild impact", "Domestic fundamentals stable"],
            ["Spillover effects from global recession risk", "Capital flows to safe havens"],
            f"{name} investment risk stable. Monitor for second-order effects from global energy crisis.")

    # ===== 11. RELATIONSHIP HEALTH SCORE (TOP PARTNER) =====
    if code in WAR_ZONE:
        if code == "IRN":
            add_estimate(code, "top_partner_relationship_health", None, "strong_decrease", 0.92,
                "Iran's key bilateral relationships in crisis. At war with USA/Israel. Russia providing covert support but relationship asymmetric. China maintaining distance. No major partner providing effective assistance.",
                ["Active war with US and Israel", "Russia caught in ship-to-ship oil transfers but not openly supporting", "US warned Russia against providing Iran intelligence"],
                ["Russia-Iran energy ties deepening through shadow fleet", "China maintaining some economic engagement"],
                "Iran isolated diplomatically. Russia only significant partner but support limited and covert.")
        else:  # ISR
            add_estimate(code, "top_partner_relationship_health", None, "growth", 0.78,
                "Israel-US relationship strengthened by joint military operations. Operation Roaring Lion demonstrates deep operational integration. But international condemnation of civilian casualties could strain.",
                ["Joint US-Israeli military operations (Operation Epic Fury/Roaring Lion)", "US providing air support for operations", "Deep military cooperation"],
                ["International condemnation of civilian casualties", "Humanitarian concerns growing"],
                "Israel-US relationship at operational peak during wartime. Post-war dynamics may shift.")
    elif code == "USA":
        add_estimate(code, "top_partner_relationship_health", None, "decrease", 0.72,
            "US bilateral relationships strained across multiple fronts. EU split on Iran war support. Trump trade tensions with Canada, China. Russia intelligence-sharing concerns. But G7 coordinating on SPR release shows cooperation.",
            ["EU leaders split on US-Israeli war against Iran", "25% tariffs on Canada; 10% additional on China", "US warned Russia on Iran intelligence", "G7 coordinating SPR release"],
            ["G7 coordination demonstrates alliance value", "NATO defense spending alignment"],
            "US bilateral relationships under strain from war and trade policy simultaneously. G7 coordination a positive signal.")
    elif code in HORMUZ_AFFECTED_GULF:
        add_estimate(code, "top_partner_relationship_health", None, "decrease", 0.72,
            f"{name} relationship health with key partners declining as Gulf conflict strains alliances. US unable to provide Hormuz escorts. Regional cooperation tested.",
            ["US Navy told ships Hormuz escorts 'not possible for now'", "Regional alliance dynamics shifting", "Economic disruption straining trade partnerships"],
            ["Long-term US security commitment", "GCC coordination mechanisms active"],
            f"{name} partner relationships under stress from conflict. US inability to escort Hormuz traffic damages credibility.")
    elif code in {"CHN"}:
        add_estimate(code, "top_partner_relationship_health", None, "stable", 0.68,
            "China-US relationship stable at low level. Additional 10% tariff adds friction but no new escalation. India easing China investment curbs signals broader engagement. Two Sessions confirms strategic direction.",
            ["10% additional US tariff — incremental not transformative", "India easing Chinese investment restrictions", "Arms imports -72% reflects reduced dependency on partners"],
            ["Trump-Xi dynamics unpredictable", "Decoupling trend continuing"],
            "China bilateral relationships stable. India opening positive. US friction continues but not escalating.")
    elif code == "IND":
        add_estimate(code, "top_partner_relationship_health", None, "growth", 0.72,
            "India bilateral relationships improving. Easing Chinese investment curbs signals strategic flexibility. US alignment on Iran provides diplomatic capital. But Gulf disruption threatens remittance and worker safety.",
            ["India easing Chinese investment restrictions", "Gulf conflict disrupts Indian worker safety and remittances", "Reducing Russian arms dependency (40% from 51%)"],
            ["Gulf worker crisis could strain Gulf state relations", "$40M cargo stranded at ports"],
            "India bilateral relationships cautiously improving. China opening and arms diversification positive trends.")
    elif code == "UKR":
        add_estimate(code, "top_partner_relationship_health", None, "growth", 0.75,
            "Ukraine-EU relationship strengthened by €90B transfer bypassing Hungary. Fresh US peace talks proposed. EU institutional precedent set for overriding single-member vetoes.",
            ["EU €90B transfer bypassing Hungary — institutional precedent", "US proposed fresh trilateral peace talks", "EU-Hungary relations strained over Ukraine"],
            ["US attention shifting to Iran may reduce leverage", "Hungary-Ukraine tensions escalating"],
            "Ukraine partner relationships improving. EU funding secured. Peace talks offer hope.")
    elif code == "GBR":
        add_estimate(code, "top_partner_relationship_health", None, "stable", 0.68,
            "UK bilateral relationships stable. HMS Dragon deploying to Gulf shows US alignment. UK-China tensions from Jimmy Lai case. GBP/EUR dynamics reflect economic positioning.",
            ["HMS Dragon deploying to Gulf — US alliance commitment", "Jimmy Lai case straining UK-China relations", "GBP/EUR forex dynamics stable"],
            ["UK-China tensions could escalate", "Brexit trade adjustments ongoing"],
            "UK partner relationships stable. Gulf deployment demonstrates US alignment.")
    else:
        add_estimate(code, "top_partner_relationship_health", None, "stable", 0.55,
            f"{name} key bilateral relationships broadly unchanged this week. Global focus on Gulf conflict reduces attention on other bilateral dynamics.",
            ["Global attention focused on Gulf conflict", "No major bilateral events for {name}", "Regional dynamics stable"],
            ["Spillover from Gulf conflict could affect partnerships", "Geopolitical realignment ongoing globally"],
            f"{name} partner relationships stable. Global crisis creates background uncertainty.")


# ===== BUILD OUTPUT =====
output = {
    "agent": "trend_estimator",
    "run_id": "2026-W11",
    "estimation_date": "2026-03-10",
    "ai_generated": True,
    "schema_version": "1.0",
    "document_type": "trend_estimates",
    "summary": {
        "run_id": "2026-W11",
        "generated_at": NOW,
        "pipeline_agent": "Agent 10 (Trend Estimator)",
        "reference_date": "2026-03-10",
        "total_estimates": len(estimates),
        "countries_covered": len(set(e["country_code"] for e in estimates)),
        "by_trend_label": trend_counts,
        "trend_distribution": trend_counts,
        "impact_groups": {
            "high_impact": {
                "countries": ["IRN", "ISR", "USA", "SAU", "ARE", "KWT", "QAT", "IRQ"],
                "count": 8,
                "factors_per_country": 11
            },
            "moderate_impact": {
                "countries": ["DEU", "GBR", "FRA", "JPN", "KOR", "IND", "RUS", "TUR",
                             "BRA", "AUS", "CAN", "NOR", "NGA", "EGY", "UKR", "CHN",
                             "MEX", "ARG", "PAK", "OMN", "IDN", "ZAF", "POL"],
                "count": 23,
                "factors_per_country": "5-11"
            },
            "low_impact": {
                "countries": ["CHE", "SGP", "TWN", "THA", "MYS", "SWE", "ITA", "ESP",
                             "NLD", "CZE", "ROU", "GRC", "PRT", "FIN", "IRL", "NZL",
                             "CHL", "PER", "COL", "VNM", "PHL", "BGD", "KAZ", "MAR"],
                "count": 24,
                "factors_per_country": "5-11"
            }
        },
        "key_themes": [
            "Iran war Day 10+ — Hormuz mined, 140 US troops injured, Kurdish ground invasion, boots on ground 'not ruled out'",
            "Brent crude surged 25% to $116.50/bbl — gold at $5,195.60 — Dow fell 800+ points",
            "G7 finance ministers signal coordinated SPR release — temporary relief expected",
            "Hormuz physically mined by IRGC — US Navy unable to provide escorts — mine clearance could take months",
            "European markets crashed ~6% — VW slashing 50,000 jobs — EU admitted 'nuclear blunder' on energy",
            "SIPRI 2026: global arms transfers +9.2% — Europe now top importing region for first time since 1960s — US arms exports +27%",
            "Bond market stress — leveraged basis trade ($1T+) unwinding — recalls March 2020 Treasury seizure",
            "Argentina recession -1.3% but becoming net energy exporter — Milei courting Wall Street",
            "Central bank super week coming March 16-19 — stagflation dilemma globally",
            "India easing Chinese investment curbs — strategic recalibration underway"
        ],
        "top_risk_deteriorations": [
            {"country": "IRN", "reason": "War Day 10+ — Hormuz mined — Kurdish invasion — economy in freefall — state approaching collapse"},
            {"country": "ISR", "reason": "Multi-front war: Iran + Hezbollah escalation — international condemnation growing"},
            {"country": "KWT", "reason": "No pipeline alternative to Hormuz — near-total economic paralysis"},
            {"country": "QAT", "reason": "World's largest LNG exporter completely offline — Hormuz mines block all maritime trade"},
            {"country": "USA", "reason": "War escalation + SCOTUS tariff crisis + 5 recession warnings + bond market stress + Dow -800"},
            {"country": "DEU", "reason": "VW 50,000 job cuts + European market crash + energy policy crisis"}
        ],
        "top_beneficiaries": [
            {"country": "NOR", "reason": "North Sea producer — non-Hormuz routes — energy windfall at $116/bbl"},
            {"country": "AUS", "reason": "LNG premium from Qatari disruption — gold mining windfall — AUD at 2023 highs"},
            {"country": "BRA", "reason": "Net oil exporter — geographically insulated — commodity basket elevated"},
            {"country": "KAZ", "reason": "CPC pipeline not Hormuz-dependent — oil windfall"},
            {"country": "GRC", "reason": "Shipping fleet profits from longer rerouted tanker voyages — day rates at records"},
            {"country": "ARG", "reason": "Net energy exporter for first time — Vaca Muerta — Milei reform credibility rising"}
        ],
        "ai_disclosure": "All trend estimates are AI-generated based on publicly available information as of 2026-03-10. These are probabilistic estimates subject to uncertainty and should be validated against primary sources. Confidence scores reflect estimated reliability.",
        "next_agent": "Agent 11 (Derived Metrics Calculator)"
    },
    "estimates": estimates
}

# Write output
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(f"Generated {len(estimates)} trend estimates for {len(set(e['country_code'] for e in estimates))} countries")
print(f"Trend distribution: {trend_counts}")
print(f"Output written to {OUTPUT_FILE}")
