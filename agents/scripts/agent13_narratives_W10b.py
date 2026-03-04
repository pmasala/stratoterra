#!/usr/bin/env python3
"""
Agent 13 — Country Profile Synthesizer
Run ID: 2026-W10b
Date: 2026-03-03
Generates investor-focused narrative sections for Tier 1 and Tier 2 countries.
"""

import json
import os

DATA_DIR = "/home/pietro/stratoterra/data/countries/"
GENERATED_AT = "2026-03-03T22:50:00Z"
RUN_ID = "2026-W10b"

# ---------------------------------------------------------------------------
# NARRATIVE DEFINITIONS
# ---------------------------------------------------------------------------

NARRATIVES = {

    # -----------------------------------------------------------------------
    # CRITICAL COUNTRIES — Full Depth
    # -----------------------------------------------------------------------

    "IRN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Iran faces an existential crisis unlike any since the 1979 revolution. "
            "US-Israeli Operation Epic Fury struck 504 sites across 1,039 sorties on Feb 28, "
            "killing Supreme Leader Khamenei and destroying nuclear facilities including Natanz. "
            "The IRGC has closed the Strait of Hormuz in direct retaliation, severing roughly 20% of global oil supply. "
            "An interim three-person governing council is attempting to manage succession under active military pressure, "
            "with no historical precedent for this scenario. Political risk premium on all Iran-linked assets is at maximum."
        ),
        "key_changes_this_week": [
            "Supreme Leader Khamenei killed in Operation Epic Fury strikes (Feb 28, transformative)",
            "Strait of Hormuz closed by IRGC in retaliation, blocking ~20% of global oil supply",
            "Nuclear facilities including Natanz struck and severely damaged across 504 target sites",
            "787+ casualties reported; 27 US military bases in region hit by IRGC counter-strikes",
            "Interim three-person governing council formed; Assembly of Experts convened under emergency",
            "Iranian currency in freefall; inflation trajectory toward hyperinflation (42.4% pre-crisis)",
        ],
        "outlook": (
            "The near-term trajectory is catastrophic. Succession via the Assembly of Experts has no precedent "
            "under active military bombardment, and IRGC institutional control may fracture across factional lines. "
            "Hormuz closure duration — days, weeks, or months — is the single most consequential variable for "
            "global energy markets in Q1-Q2 2026. No diplomatic pathway is visible; military escalation risk remains high."
        ),
        "investor_implications": (
            "Iran assets are completely uninvestable; all remaining exposures should be written off as total losses. "
            "Secondary sanctions apply to any entity transacting with Iranian counterparties. "
            "The primary investor implication is indirect: the Hormuz closure's cascading effect on Gulf sovereign "
            "creditworthiness, global energy prices, and supply-chain disruption across Asia."
        ),
        "data_quality_note": (
            "Iran economic and military data is very low confidence under active conflict. Pre-crisis IMF figures no longer "
            "reflect ground conditions. Military situation assessed from OSINT and open-source news. "
            "CRITICAL: Maximum political risk premium active."
        ),
    },

    "USA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The United States simultaneously launched the largest military operation since Iraq 2003 and navigated "
            "a domestic constitutional rupture. Operation Epic Fury struck 1,039 targets in Iran with US-Israeli forces; "
            "three US soldiers were killed in IRGC retaliatory strikes. The Supreme Court struck down IEEPA tariff authority "
            "6-3, forcing a pivot to Section 122 with a 15% global tariff capped at 150 days. "
            "Markets sold off sharply (S&P -0.78%, Dow -2.1%), and recession probability rose to 40-50%. "
            "Nationwide 'No Kings' protests are planned for March 28, adding a domestic political dimension."
        ),
        "key_changes_this_week": [
            "Operation Epic Fury launched against Iran; 3 US soldiers KIA in IRGC retaliation (Feb 28-Mar 1, transformative)",
            "SCOTUS struck down IEEPA tariff authority 6-3; Section 122 15% global tariff enacted for 150 days",
            "Additional 20% cumulative China tariffs and 25% Canada/Mexico tariffs effective March 4",
            "Recession probability surged from 25-30% to 40-50%; S&P posted largest monthly decline in a year",
            "No Kings protests planned nationwide March 28; midterm primary season begun",
            "Strait of Hormuz closure driving oil surge; stagflation risk elevated",
        ],
        "outlook": (
            "The US faces a potential stagflation scenario: the Hormuz oil shock pushes inflation higher while "
            "trade disruption and consumer confidence deterioration raise recession risk. "
            "The 150-day Section 122 tariff clock creates a policy cliff in July requiring legislative resolution. "
            "The March FOMC (17-18) is a critical inflection point; the Fed is trapped between containing energy-driven "
            "inflation and supporting a slowing economy."
        ),
        "investor_implications": (
            "Defensive positioning is warranted: overweight Treasuries (10Y at 3.96% on flight-to-safety), "
            "gold ($5,155+), energy sector, and defense contractors (Lockheed, Raytheon, Northrop). "
            "Underweight consumer discretionary, airlines, and trade-exposed manufacturers. "
            "Monitor VIX at market open and March FOMC for rate path signals; the 150-day tariff cliff in July "
            "is the next major policy discontinuity."
        ),
        "data_quality_note": (
            "US macro data is high confidence (0.85-0.95). Recession probability estimates are analyst consensus, "
            "not official forecasts. Market data reflects pre-week-open conditions and may shift materially."
        ),
    },

    "ISR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Israel is fighting simultaneous wars on two fronts for the first time since 1973. "
            "Operation Roaring Lion, the Israeli air component of the joint US-Israeli strikes on Iran, is ongoing. "
            "Hezbollah broke its ceasefire by launching rockets into northern Israel in solidarity with Iran; "
            "Israel responded with strikes on Beirut killing 52+ and has deployed ground forces into south Lebanon. "
            "IRGC retaliatory strikes have hit Israeli targets directly. The economy faces severe strain from "
            "defense mobilization, tourism collapse, and insurance repricing across all Israeli asset classes."
        ),
        "key_changes_this_week": [
            "Operation Roaring Lion: Israeli air strikes on Iran as part of joint US-Israeli operation (Feb 28)",
            "Hezbollah broke ceasefire; rockets launched at northern Israel; Israeli strikes killed 52+ in Beirut",
            "Israeli ground forces deployed into south Lebanon; second front opened",
            "IRGC retaliatory strikes hit Israeli targets directly",
            "ILS under depreciation pressure; Tel Aviv Stock Exchange in high volatility",
            "Defense spending surge; reservist mobilization at scale impacting labor supply",
        ],
        "outlook": (
            "Extended multi-front conflict strains the Israeli economy and military simultaneously. "
            "Defense spending will surge further, adding to fiscal pressure already elevated from Gaza operations. "
            "The diplomatic path to ceasefire on either front is unclear, with Hezbollah's political future "
            "in Lebanon complicated by the Lebanese cabinet's historic vote to ban Hezbollah military activities."
        ),
        "investor_implications": (
            "A meaningful war premium is now priced into all Israeli assets. The ILS will face continued depreciation "
            "pressure as defense outlays surge and foreign investor risk appetite falls. "
            "The Tel Aviv Stock Exchange is volatile; defense sector names are the sole beneficiaries. "
            "TA-35 and TA-125 exposure should be reduced until a credible de-escalation pathway emerges."
        ),
        "data_quality_note": (
            "Military situation data from OSINT and open-source news. Economic impact estimates are preliminary. "
            "Casualty figures may understate actual toll. CRITICAL: Multiple active alerts."
        ),
    },

    "SAU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Saudi Arabia is caught directly in the Iran-US crossfire with severe economic consequences. "
            "Iranian drones struck the US Embassy in Riyadh in a retaliatory salvo targeting Gulf US partners. "
            "The Hormuz closure has idled Ras Tanura and Ju'aymah terminals, blocking the vast majority of Saudi crude exports "
            "and triggering a Fitch warning on sovereign rating risk. "
            "Saudi Aramco VLCC freight rates surged 94% as tankers scramble for alternative routing. "
            "The East-West Pipeline (5 mbpd capacity) provides partial relief via Yanbu on the Red Sea coast, "
            "but Red Sea Houthi activity constrains that exit too."
        ),
        "key_changes_this_week": [
            "Iranian drones struck US Embassy in Riyadh; Saudi air defenses engaged",
            "Hormuz closure blocked majority of Saudi crude exports; Ras Tanura and Ju'aymah terminals idled",
            "VLCC freight rates surged 94% on rerouting demand",
            "Fitch warned on Saudi sovereign rating; bond spreads widening",
            "East-West Pipeline (5 mbpd) activated as partial export alternative via Yanbu",
            "Oil price surge partially offsets volume loss; net revenue impact negative due to export blockage",
        ],
        "outlook": (
            "Economic damage accumulates with each day Hormuz remains closed. "
            "The East-West Pipeline provides a partial lifeline but cannot fully compensate for blocked Gulf terminal exports. "
            "If Hormuz closure extends beyond two weeks, Saudi Arabia faces a meaningful sovereign fiscal shortfall "
            "despite its substantial sovereign wealth buffer ($940B+ ARAMCO + PIF). "
            "Vision 2030 diversification projects face delays as capital allocation priorities shift."
        ),
        "investor_implications": (
            "Saudi Aramco investors face significant near-term downside as export volumes are constrained even while "
            "oil prices surge — a paradoxical outcome that compresses realized revenue. "
            "Saudi sovereign bond spreads are widening; Fitch's rating warning is a credible near-term risk. "
            "PIF-linked assets and Vision 2030 project bonds carry elevated execution risk. "
            "Monitor Hormuz reopening timeline as the primary catalyst for SAR-denominated asset recovery."
        ),
        "data_quality_note": (
            "Saudi export volume estimates are based on terminal operational reports and shipping data. "
            "Fiscal impact calculations use pre-crisis oil revenue baselines. CRITICAL: Multiple active alerts."
        ),
    },

    "PAK": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Pakistan faces a dual existential crisis: open conventional war with Afghanistan following "
            "Operation Ghazab Lil Haq (strikes on 46 locations across the border), and severe domestic sectarian "
            "violence triggered by Khamenei's assassination. "
            "The military has been deployed under Article 245 across Gilgit-Baltistan and major urban centers. "
            "Curfews, communications blackouts, and at least 24-26 protest deaths mark the worst domestic instability "
            "in years, arriving simultaneously with a hot border conflict."
        ),
        "key_changes_this_week": [
            "Operation Ghazab Lil Haq: Pakistan struck 46 locations in Afghanistan, escalating to open war",
            "Article 245 military deployment across Gilgit-Baltistan and major cities",
            "Domestic sectarian violence following Khamenei assassination; 24-26 killed in protests",
            "Communications blackout imposed in conflict-adjacent regions",
            "Curfews declared in multiple urban centers",
            "IMF program compliance at risk as fiscal discipline faces military spending surge",
        ],
        "outlook": (
            "The two-front crisis — external war and domestic instability — strains Pakistan's already fragile economy "
            "at a moment of IMF-mandated reform. If military spending surges beyond IMF program parameters, "
            "the $7B Extended Fund Facility could be suspended, triggering a sovereign liquidity crisis. "
            "Pakistan's nuclear posture vis-a-vis Afghanistan is a wildcard that markets will price with extreme caution."
        ),
        "investor_implications": (
            "PKR faces severe depreciation pressure; sovereign bonds are in distressed territory. "
            "FDI inflows will freeze until military situation stabilizes. "
            "CPEC corridor security is at direct risk from Afghan border conflict. "
            "Eurobond holders should monitor IMF program status as the key sovereign solvency indicator."
        ),
        "data_quality_note": (
            "Conflict data from OSINT; communications blackout limits ground-truth verification. "
            "Economic impact estimates are preliminary. CRITICAL: Multiple active alerts. High uncertainty."
        ),
    },

    "KOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "South Korea suffered its worst single-day equity market crash since April 2024, with KOSPI falling "
            "7.24% and circuit breakers triggered. The dual shock of Iran crisis risk-off sentiment and "
            "North Korea's deployment of KN-25 600mm multiple rocket systems to frontline positions drove "
            "both financial and geopolitical risk repricing. "
            "South Korea imports approximately 88% of its oil, with a substantial share transiting Hormuz, "
            "creating severe energy cost exposure. Bond yields rose and the KRW weakened as foreign capital fled."
        ),
        "key_changes_this_week": [
            "KOSPI fell 7.24% — worst single-day decline since April 2024; circuit breakers triggered",
            "North Korea deployed KN-25 600mm MRLs to frontline positions; military tension elevated",
            "Freedom Shield 26 exercise scheduled March 9-19; US-ROK military posture review",
            "Hormuz closure threatens South Korea's oil import supply chain (88% import dependency)",
            "KRW under depreciation pressure; BOK intervention signals",
            "Bond yields rose on risk repricing; Samsung/SK Hynix supply chains under monitoring",
        ],
        "outlook": (
            "South Korea's heavy structural exposure to both Hormuz oil imports and global trade volumes makes it "
            "one of the most macro-vulnerable developed economies in this crisis. "
            "The Bank of Korea may intervene to stabilize KRW, but rate cuts are constrained by energy-driven inflation. "
            "If North Korea perceives US military attention as diverted to the Middle East, "
            "the risk of opportunistic provocation increases materially."
        ),
        "investor_implications": (
            "Korean equities are oversold on panic selling but structural risks remain elevated — "
            "do not interpret the KOSPI crash as a pure buying opportunity. "
            "Samsung Electronics and SK Hynix supply chain exposure (Taiwan Strait + Hormuz) warrants monitoring. "
            "Korea sovereign CDS spreads are widening; KTBs (Korean Treasury Bonds) offer relative value on "
            "BOK support expectation but carry geopolitical tail risk."
        ),
        "data_quality_note": (
            "Market data is intraday and may not fully reflect final settlement. "
            "North Korean military deployment data from ROK Joint Chiefs of Staff reporting. Moderate-high confidence."
        ),
    },

    "CHN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "China's unprecedented military purge deepened this week with nine additional PLA lawmakers removed, "
            "bringing the total to 100+ officers purged since 2022. Top general Zhang Youxia (CMC Vice Chairman) "
            "and Joint Staff chief Liu Zhenli are under investigation — leaving only one general besides Xi on the CMC. "
            "An unverified coup attempt report circulated in intelligence channels. "
            "Externally, a $11.1B Taiwan arms sale remains stalled ahead of the planned Trump-Xi summit, "
            "while Chinese markets sold off on combined domestic political risk and Iran crisis risk-off."
        ),
        "key_changes_this_week": [
            "9 more PLA lawmakers removed; Zhang Youxia and Liu Zhenli under investigation (100+ total purged)",
            "Unverified coup attempt report in intelligence channels — unconfirmed but market-moving",
            "$11.1B Taiwan arms sale stalled ahead of Trump-Xi summit",
            "CSI 300 under pressure; political risk underpriced by markets",
            "Two Sessions (NPC/CPPCC) opening week: stimulus signals awaited",
            "PLA institutional reliability uncertain; Taiwan Strait risk assessment requires revision",
        ],
        "outlook": (
            "The PLA purge creates genuine uncertainty about Chinese military command coherence, "
            "which paradoxically both reduces and increases Taiwan Strait risk — reduced offensive capability "
            "but also reduced deterrent credibility. "
            "The Trump-Xi summit (planned late March) is a pivotal event; the $11.1B arms sale stall suggests "
            "both sides are managing pre-summit optics. "
            "Two Sessions economic stimulus signals will be the primary near-term market catalyst."
        ),
        "investor_implications": (
            "CSI 300 and Hong Kong-listed China equities carry unpriced political risk. "
            "The purge's scale — eliminating nearly all independent military leadership — is historically "
            "unusual and warrants a political risk premium not yet reflected in valuations. "
            "Two Sessions stimulus packages could provide a near-term positive catalyst; "
            "monitor PBOC liquidity injections and fiscal deficit targets as sentiment anchors."
        ),
        "data_quality_note": (
            "PLA purge data from official Chinese state media releases; coup attempt report unverified. "
            "Market data is high confidence. Taiwan arms sale status from US DoD and Congressional reporting."
        ),
    },

    "ARE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The UAE took direct military hits this week as the IRGC struck Al Minhad Air Base, "
            "a major US military facility on Emirati soil, in retaliatory strikes against Gulf US partners. "
            "Jebel Ali Port — the world's 9th largest container port handling 15.5 million TEUs — is effectively "
            "cut off from global ocean trade by the dual closure of the Strait of Hormuz and Red Sea Houthi interdiction. "
            "Over 7,700 flights were disrupted across UAE airspace. The Abu Dhabi-to-Fujairah pipeline "
            "(approximately 1.5 mbpd capacity) provides a partial crude export alternative bypassing Hormuz."
        ),
        "key_changes_this_week": [
            "Al Minhad Air Base struck by IRGC; US military facility on UAE soil hit directly",
            "Jebel Ali Port (15.5M TEU) cut off by dual Hormuz/Red Sea closure",
            "7,700+ flights disrupted across UAE airspace from military operations",
            "Abu Dhabi-to-Fujairah pipeline (~1.5 mbpd) activated as Hormuz bypass",
            "Dubai tourism and MICE sector severely impacted by regional conflict risk",
            "UAE safe-haven status within Gulf undermined by direct strike on Emirati territory",
        ],
        "outlook": (
            "The UAE's economic model — built on being a regional trade, logistics, and financial hub — "
            "is directly challenged when Jebel Ali is isolated and regional conflict strikes Emirati territory. "
            "Abu Dhabi's oil revenues are partially protected by the Fujairah bypass pipeline, "
            "but the non-oil economy (tourism, re-exports, financial services) faces acute near-term disruption. "
            "Conflict duration is the primary driver of economic damage accumulation."
        ),
        "investor_implications": (
            "Dubai real estate and tourism-linked REITs and equities face near-term headwinds as "
            "conference cancellations and tourist risk aversion materialize. "
            "ADNOC export revenues are partially insulated via Fujairah but not fully. "
            "UAE sovereign bonds (ADIB, Abu Dhabi sovereign) retain investment grade but spreads will widen. "
            "The UAE dirham peg to USD is secure given ADIA reserve levels, limiting FX risk."
        ),
        "data_quality_note": (
            "Flight disruption data from Eurocontrol and airline reporting. Port data from DP World operational reports. "
            "Military strike assessment from OSINT. CRITICAL: Multiple active alerts."
        ),
    },

    "KWT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Kuwait is among the hardest-hit Gulf states in the Iran crisis. "
            "Ali al-Salem Air Base was struck by Iran in retaliatory salvos; "
            "in a separate incident, Kuwaiti air defenses accidentally shot down three US fighter jets, "
            "creating a significant diplomatic complication within the US-Gulf coalition. "
            "Kuwait's oil exports are completely blocked by the Hormuz closure, with no pipeline alternative "
            "unlike Saudi Arabia or the UAE. Revenue loss is estimated at approximately $2.5 billion per month."
        ),
        "key_changes_this_week": [
            "Ali al-Salem Air Base struck by Iranian IRGC retaliatory salvos",
            "Kuwaiti air defenses accidentally shot down 3 US fighter jets — significant diplomatic incident",
            "Oil exports completely halted by Hormuz closure; no pipeline bypass available",
            "Estimated $2.5B/month revenue loss from export blockage",
            "Kuwait Investment Authority (KIA) drawdown accelerating to fund domestic fiscal gap",
            "KWD peg to USD basket maintained but sovereign fiscal buffer under stress",
        ],
        "outlook": (
            "Kuwait's complete export dependence on Hormuz — with no bypass pipeline — means revenue loss "
            "scales linearly with closure duration. "
            "The KIA sovereign wealth fund ($900B+) provides a substantial buffer, but sustained drawdown "
            "accelerates if closure extends beyond weeks. "
            "The friendly-fire incident with US forces creates political strain within the coalition at a critical moment."
        ),
        "investor_implications": (
            "Kuwait Investment Authority may accelerate liquidation of foreign equity and fixed income positions "
            "to fund domestic fiscal needs, creating potential selling pressure in global markets. "
            "Kuwaiti sovereign bonds retain investment-grade status but spreads are widening meaningfully. "
            "The KWD peg is secure given KIA reserves; no FX risk, but credit spread risk is real and growing."
        ),
        "data_quality_note": (
            "Revenue loss estimates based on pre-crisis export volumes. Friendly-fire incident confirmed by "
            "US CENTCOM and Kuwaiti MoD. KIA drawdown figures are estimates; official disclosures are quarterly."
        ),
    },

    "QAT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Qatar faces a uniquely severe export crisis: its LNG terminal infrastructure at Ras Laffan "
            "is rendered economically inaccessible by the Hormuz closure, blocking approximately 20% of global "
            "LNG supply originating from Qatar. Al Udeid Air Base — the largest US military base in the Middle East — "
            "is directly threatened by IRGC retaliatory strike planning. "
            "Unlike crude oil producers with some pipeline alternatives, Qatar has no overland LNG export pathway, "
            "making the revenue loss immediate and complete while Hormuz remains closed."
        ),
        "key_changes_this_week": [
            "Hormuz closure blocked Qatar LNG exports (~20% of global LNG supply); no pipeline alternative exists",
            "Al Udeid Air Base (largest US base in Middle East) under direct threat from IRGC strike planning",
            "QatarEnergy LNG contracts face potential force majeure claims from buyers",
            "LNG spot prices surging globally as Qatari supply disrupted",
            "QAR peg to USD maintained; sovereign fiscal buffer substantial but revenues in freefall",
            "Diplomatic role as mediator (Hamas talks) potentially compromised by active conflict positioning",
        ],
        "outlook": (
            "Qatar's revenue collapse is immediate and total while Hormuz remains closed — a fundamentally "
            "different vulnerability profile from diversified economies. "
            "The force majeure legal exposure on long-term LNG contracts could result in contractual disputes "
            "with European and Asian buyers worth billions. "
            "Qatar's diplomatic positioning as a regional mediator may be strained by its hosting of Al Udeid, "
            "which is an active target in the current conflict."
        ),
        "investor_implications": (
            "QatarEnergy bonds and equity (including listed affiliates) carry acute near-term risk from "
            "revenue disruption and force majeure litigation exposure. "
            "Qatar sovereign bonds are investment-grade and well-buffered by QIA's $475B+ in assets, "
            "but spreads will widen materially if closure extends. "
            "LNG spot price surge benefits Qatar structurally once Hormuz reopens, "
            "creating a potential strong recovery trade on any de-escalation signal."
        ),
        "data_quality_note": (
            "LNG export volume data from Kpler shipping analytics. Al Udeid threat assessment from OSINT. "
            "Force majeure exposure is estimated; contract terms are confidential. CRITICAL: Multiple active alerts."
        ),
    },

    "LBN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Lebanon has been plunged back into active conflict as Hezbollah broke its November 2024 ceasefire "
            "to launch rockets at northern Israel in solidarity with Iran. "
            "Israel responded with strikes on Beirut killing 52+ and deployed ground forces into south Lebanon. "
            "In a historic and politically extraordinary move, the Lebanese cabinet voted to formally ban "
            "Hezbollah's military activities — a decision that directly challenges the group's political legitimacy "
            "but whose enforceability is deeply uncertain given Hezbollah's state-within-a-state structure."
        ),
        "key_changes_this_week": [
            "Hezbollah broke November 2024 ceasefire; launched rockets at northern Israel in solidarity with Iran",
            "Israeli strikes on Beirut killed 52+; Israeli ground forces entered south Lebanon",
            "Lebanese cabinet voted to ban Hezbollah military activities — historic but enforceability uncertain",
            "IRGC leverage over Hezbollah in question following Khamenei's death",
            "Lebanese pound under renewed pressure; banking sector freeze deepening",
            "Economic recovery program — only beginning after years of collapse — derailed",
        ],
        "outlook": (
            "Lebanon's institutional capacity to confront Hezbollah militarily is essentially zero, "
            "making the cabinet ban a political statement rather than an operational constraint. "
            "The death of Khamenei may actually weaken Hezbollah's strategic direction, "
            "potentially creating an opening for a negotiated stand-down, but this remains speculative. "
            "Economic recovery is fully derailed; any reconstruction financing will require complete conflict resolution."
        ),
        "investor_implications": (
            "Lebanese Eurobonds remain in default and any remaining exposure should be exited or written off. "
            "The conflict re-escalation eliminates any near-term prospect of IMF program negotiation, "
            "which was the precondition for debt restructuring and economic normalization. "
            "No investable Lebanese assets exist until conflict terminates and political settlement is reached."
        ),
        "data_quality_note": (
            "Casualty figures from Lebanese Health Ministry and IDF reporting; may diverge. "
            "Political data (cabinet vote) from Lebanese Parliament official records. "
            "CRITICAL: Conflict active; data reliability degraded."
        ),
    },

    "RUS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Russia-Ukraine war continues into its fourth year with Ukraine achieving its best territorial performance "
            "since the Kursk incursion — gaining more territory than it lost in February. "
            "The EU's 20th sanctions package has been delayed over a dispute on the maritime services ban, "
            "giving Russia a temporary reprieve on financial pressure. "
            "A general license issued for Lukoil divestiture may signal an emerging Western asset exit pathway "
            "for companies holding Russian energy interests. "
            "Russian military losses continue to mount (1.27M total per Ukrainian General Staff claims) "
            "while the MOEX holds roughly flat (-0.19%) and the ruble trades at 77.72."
        ),
        "key_changes_this_week": [
            "Ukraine gained more territory than lost in February — best performance since Kursk incursion",
            "EU 20th sanctions package delayed over maritime services ban dispute",
            "General license issued for Lukoil divestiture; potential Western asset exit pathway",
            "MOEX flat (-0.19%); ruble at 77.72/USD — relative stability amid global volatility",
            "Russian military losses mounting (~1.27M total per Ukrainian General Staff claims)",
            "Iran crisis creates indirect risk: Russia-Iran military cooperation axis under pressure from Khamenei death",
        ],
        "outlook": (
            "The Russian economy has demonstrated more resilience than many forecasters predicted, "
            "supported by high defense spending, import substitution, and energy revenues rerouted to Asia. "
            "However, sanctions are tightening incrementally with each EU package, and military attrition "
            "is accelerating at unsustainable rates. "
            "The Iran crisis may remove a key military supplier and diplomatic partner, "
            "potentially weakening Russia's strategic position over the medium term."
        ),
        "investor_implications": (
            "Russian assets remain broadly sanctioned and inaccessible to Western investors. "
            "The Lukoil general license is a potential exit mechanism for trapped capital — "
            "monitor for additional licenses that could allow more orderly divestiture. "
            "MOEX stability and ruble resilience should not be interpreted as investment signals; "
            "they reflect capital controls, not genuine market equilibrium."
        ),
        "data_quality_note": (
            "Ukrainian territorial gain data from ISW (Institute for the Study of War). "
            "Casualty figures are Ukrainian General Staff claims and are not independently verified. "
            "Russian economic data has a known reporting quality issue. Confidence: moderate."
        ),
    },

    "UKR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ukraine achieved its strongest territorial performance since the Kursk incursion, "
            "gaining more ground than it lost across the February reporting period. "
            "The IMF approved an $8.1 billion four-year loan, anchoring a broader $136.5 billion international "
            "support package that significantly strengthens Ukraine's fiscal position. "
            "Geneva talks with the United States are ongoing, with diplomatic momentum building "
            "around a potential negotiated framework for the first time since early 2022."
        ),
        "key_changes_this_week": [
            "Ukraine gained more territory than lost in February — best performance since Kursk incursion",
            "IMF approved $8.1B four-year loan; $136.5B international support package anchored",
            "Geneva diplomatic talks with US ongoing; negotiated framework discussions advancing",
            "Energy infrastructure remains vulnerable to Russian missile and drone strikes",
            "Reconstruction investment pipeline growing; international development bank commitments rising",
            "Military momentum on eastern front favorable but northern pressure points remain contested",
        ],
        "outlook": (
            "Ukraine's military momentum is positive but fragile; energy infrastructure strikes during winter "
            "create civilian vulnerability that constrains offensive operational tempo. "
            "The IMF loan backstop significantly strengthens Ukraine's ability to maintain budget discipline "
            "while simultaneously funding defense. "
            "Geneva talks represent the most credible diplomatic progress in years; a ceasefire framework "
            "in the next 60-90 days is a plausible but not certain scenario."
        ),
        "investor_implications": (
            "Ukraine sovereign bonds are trading at recovery values, pricing in a growing probability "
            "of successful debt restructuring under IMF auspices. "
            "Reconstruction opportunities are accumulating; early-mover advantage accrues to entities "
            "establishing presence in sectors like energy, infrastructure, and agriculture. "
            "IMF backstop materially strengthens the fiscal anchor underpinning any investment thesis."
        ),
        "data_quality_note": (
            "Territorial data from ISW. IMF loan figures from official IMF press release. "
            "Geneva talks status from US State Department and Ukrainian foreign ministry. Confidence: high."
        ),
    },

    # -----------------------------------------------------------------------
    # MODERATE COUNTRIES — 3-4 sentences
    # -----------------------------------------------------------------------

    "DEU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Energy-importing Germany faces a significant oil and gas price shock from the dual Hormuz/Suez "
            "chokepoint crisis, arriving on top of ongoing supply chain disruption. "
            "The DAX fell 3.54% — among the worst European performances — reflecting Germany's acute "
            "manufacturing and export exposure to global trade disruption. "
            "Defense spending surged to $107 billion (+18%), the largest single-year increase in modern German history, "
            "representing a structural fiscal shift. Stagflation risk is elevated as energy costs rise while "
            "industrial output contracts."
        ),
        "key_changes_this_week": [
            "DAX fell 3.54%; equity market reflecting manufacturing and trade exposure",
            "Defense spending surge to $107B (+18%) — historic structural fiscal shift",
            "Oil price shock from dual Hormuz/Suez closure elevating energy cost for industry",
            "Stagflation risk elevated: energy-driven inflation plus slowing growth",
            "US Section 122 tariffs create additional export market headwind",
        ],
        "outlook": (
            "Germany's structural vulnerability to energy price shocks and trade disruption remains unresolved. "
            "Defense spending surge will provide a domestic demand offset but not immediately enough to compensate "
            "for manufacturing output contraction. ECB rate path will be critical."
        ),
        "investor_implications": (
            "DAX exposure warrants caution; overweight defense (Rheinmetall, Hensoldt) and underweight "
            "automotive exporters and chemical sector. German Bunds remain a safe-haven asset with yield "
            "compression expected on risk-off flows."
        ),
        "data_quality_note": None,
    },

    "FRA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "France's CAC 40 fell 1.95% as the oil price shock and Iran crisis risk-off sentiment hit "
            "European markets. Defense Minister Lecornu led a cabinet reshuffle that signals continued "
            "defense-forward posture from the Macron government. "
            "The EU-US trade deal framework is threatened by US Section 122 tariffs, creating export market "
            "uncertainty for French luxury goods, aerospace, and agriculture. "
            "European defense spending increase, with France as a leading contributor, provides a domestic demand offset."
        ),
        "key_changes_this_week": [
            "CAC 40 fell 1.95% on Iran crisis risk-off and oil shock",
            "Cabinet reshuffle led by Defense Minister Lecornu; defense posture reinforced",
            "EU-US trade deal threatened by Section 122 tariff regime",
            "Defense spending increasing as part of European 12.6% surge",
            "Energy shock from dual chokepoint closure adding to inflation pressure",
        ],
        "outlook": (
            "France's economic outlook is mixed: defense spending provides a structural growth driver, "
            "but energy price shock and trade uncertainty weigh on consumer and business confidence. "
            "ECB decisions will be the primary macro policy anchor."
        ),
        "investor_implications": (
            "CAC 40 exposure should be tilted toward defense (Thales, Dassault) and away from "
            "luxury goods exporters facing US tariff headwinds. OAT spreads over Bunds remain manageable."
        ),
        "data_quality_note": None,
    },

    "GBR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The FTSE 100 showed notable resilience, falling only 0.04%, reflecting its large-cap energy "
            "and mining weighting which benefits from commodity price surges. "
            "The Bank of England voted 5-4 to hold rates — the slimmest majority, signaling a dovish tilt "
            "that could accelerate rate cuts if energy-driven inflation moderates. "
            "Energy costs are rising from the oil shock. The FCA regulatory easing package (April 2026) "
            "provides a positive structural backdrop for UK financial services."
        ),
        "key_changes_this_week": [
            "FTSE 100 fell only 0.04% — outperforming European peers on energy/mining weighting",
            "BoE voted 5-4 to hold rates; dovish tilt signal with potential early rate cut",
            "Energy costs rising from Hormuz/Suez closure oil shock",
            "FCA regulatory easing package effective April 2026 — positive for financial services",
            "Defense spending growth continuing; UK contributing to European surge",
        ],
        "outlook": (
            "UK is relatively better-positioned than continental European peers in this crisis, "
            "with North Sea energy production providing partial domestic insulation and FTSE energy "
            "sector providing portfolio offset. BoE rate cuts are the key near-term macro catalyst."
        ),
        "investor_implications": (
            "FTSE 100 energy and mining names (Shell, BP, Rio Tinto, BHP) are beneficiaries of commodity surge. "
            "Gilts offer moderate safe-haven appeal. GBP at modest risk from growth slowdown but supported "
            "by North Sea energy terms-of-trade improvement."
        ),
        "data_quality_note": None,
    },

    "JPN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Japan's Nikkei fell 3.06% as the country's 88% oil import dependency makes it structurally "
            "one of the most exposed developed economies to a Hormuz closure. "
            "The Bank of Japan held rates at 0.75% at its latest meeting, resisting pressure to tighten "
            "further as energy-driven inflation complicates the rate path. "
            "The yen is strengthening on safe-haven flows, providing partial import cost offset but compressing "
            "export sector earnings for Japan's critical manufacturing exporters."
        ),
        "key_changes_this_week": [
            "Nikkei fell 3.06%; oil import vulnerability to Hormuz closure driving risk-off selling",
            "BoJ held at 0.75%; energy inflation complicating rate normalization path",
            "JPY strengthening on safe-haven flows; yen carry trade partially unwinding",
            "88% oil import dependency creates severe energy cost exposure to Hormuz closure duration",
            "Export sector earnings compressed by JPY appreciation",
        ],
        "outlook": (
            "Japan's energy import vulnerability is structural and cannot be quickly resolved. "
            "If Hormuz closure extends, Japan faces both energy cost shocks and potential supply shortfalls "
            "that could trigger government strategic reserve releases and emergency procurement at spot prices. "
            "BoJ is effectively trapped: cannot tighten into an energy shock, but inflation rising."
        ),
        "investor_implications": (
            "Nikkei is under pressure; underweight energy-intensive Japanese manufacturers (steel, chemicals, autos). "
            "JGBs benefit from domestic safe-haven flows. JPY long positions are performing; "
            "watch for BoJ intervention signals if yen appreciation becomes disorderly."
        ),
        "data_quality_note": None,
    },

    "IND": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "India's Sensex fell a modest 0.44%, outperforming most Asian peers, reflecting India's growing "
            "economic diversification and the positive near-term signal from a US-India trade deal "
            "implementation at an 18% tariff rate — significantly below the Section 122 global 15% floor "
            "after bilateral negotiations. "
            "The Pakistan-Afghanistan open war on India's western border creates security externalities "
            "that will require monitoring, particularly regarding CPEC disruption and border stability. "
            "India has committed to stop purchasing Russian oil as part of its US alignment, "
            "raising near-term import cost concerns."
        ),
        "key_changes_this_week": [
            "Sensex fell only 0.44% — outperforming Asian peers; relative resilience",
            "US-India trade deal implementation at 18% preferential tariff rate",
            "Agreement to stop buying Russian oil; near-term import cost headwind",
            "Pakistan-Afghanistan war on western border creates regional security externalities",
            "Oil import costs surging from Hormuz closure; India heavily import-dependent",
            "Rupee under modest pressure; RBI monitoring capital flows",
        ],
        "outlook": (
            "India's structural growth story remains intact but near-term headwinds from oil import costs "
            "and regional conflict proximity are real. The US trade deal is a significant long-term positive "
            "for export-oriented sectors. RBI will need to balance inflation (energy) against growth support."
        ),
        "investor_implications": (
            "India remains one of the more attractive EM investment destinations despite near-term noise. "
            "IT services, pharmaceuticals, and domestic consumption names are preferred. "
            "Energy-importing sectors face margin pressure. INR moderate depreciation risk from oil import surge."
        ),
        "data_quality_note": None,
    },

    "BRA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Brazil's Bovespa rose 0.83% — one of the few major equity markets to post gains this week — "
            "reflecting Brazil's position as a net oil exporter that benefits directly from oil price surges. "
            "Brazilian real (BRL) showed relative stability as commodity terms-of-trade improved. "
            "The central bank's credibility has been maintained through consistent inflation-targeting "
            "communication, anchoring fixed income despite global volatility."
        ),
        "key_changes_this_week": [
            "Bovespa +0.83% — rare positive in global risk-off; net oil exporter beneficiary",
            "BRL relatively stable on improved commodity terms-of-trade",
            "Oil price surge benefits Petrobras and Brazilian E&P sector",
            "Central bank credibility intact; SELIC rate path unchanged",
            "Agri-commodity prices also elevated; broad commodity exporter benefit",
        ],
        "outlook": (
            "Brazil's commodity exporter status provides genuine insulation in an oil-shock environment. "
            "Political risk from Lula government fiscal policy remains a medium-term concern, "
            "but near-term macro tailwinds are supportive. Monitor fiscal deficit trajectory."
        ),
        "investor_implications": (
            "Brazilian equities are relatively attractive in a commodity-surge environment. "
            "Petrobras and agri-exporters (JBS, BRF) are beneficiaries. "
            "BRL may appreciate modestly on commodity flows; Treasuries (NTN-B) offer inflation-linked protection."
        ),
        "data_quality_note": None,
    },

    "TUR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Turkey's lira sits at 43.97/USD as the country navigates its Middle East proximity with a "
            "characteristically multi-directional foreign policy stance. "
            "Elevated inflation remains the dominant domestic challenge, constraining the CBRT's policy flexibility. "
            "The dual chokepoint crisis may paradoxically benefit Turkey: Bosphorus transit volumes could rise "
            "as shipping seeks alternative routes, and Turkey's energy hub ambitions gain relevance as "
            "Hormuz supply chains reorganize."
        ),
        "key_changes_this_week": [
            "TRY at 43.97/USD; inflation remains elevated, constraining CBRT",
            "Middle East conflict proximity creates regional risk premium on Turkish assets",
            "Bosphorus transit volumes may increase as shipping routes reorganize around closed straits",
            "Turkey energy hub positioning gains relevance from Hormuz/Suez dual closure",
            "Defense sector (Baykar, Aselsan) benefits from European and regional defense spending surge",
        ],
        "outlook": (
            "Turkey's structural inflation problem persists, but the geopolitical environment creates "
            "opportunities for Ankara's transactional foreign policy. "
            "Energy transit revenues and defense exports could provide economic positives. "
            "CBRT independence and rate decisions remain the key near-term risk variable."
        ),
        "investor_implications": (
            "Turkish lira remains structurally at risk; avoid unhedged TRY exposure. "
            "Eurobond holders should monitor inflation and current account data. "
            "Defense and aerospace sector equity (Baykar unlisted, Aselsan listed) benefits from regional demand surge."
        ),
        "data_quality_note": None,
    },

    "EGY": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Egypt faces a dual crisis compounding its already fragile fiscal position: "
            "the Suez Canal remains effectively closed due to Houthi interdiction, "
            "putting approximately $800 million per month in canal transit revenues at risk; "
            "simultaneously, Egypt's status as an oil importer means the global price surge adds to "
            "its import cost burden. "
            "The Egyptian pound sits at 49.88/USD as IMF program implementation continues. "
            "Sudan refugee influx remains a significant fiscal and social pressure."
        ),
        "key_changes_this_week": [
            "Suez Canal effectively closed (Houthi interdiction); ~$800M/month transit revenue at risk",
            "Oil import costs surging on global price shock",
            "EGP at 49.88/USD; IMF program implementation ongoing",
            "Sudan refugee influx continues; fiscal and social pressure",
            "Tourism sector partially insulated from Suez closure but affected by regional conflict risk",
        ],
        "outlook": (
            "Egypt's IMF program provides a fiscal anchor but cannot fully offset the dual shock of "
            "Suez revenue loss and oil import cost increase. "
            "Suez Canal reopening is the critical catalyst; every week of closure is approximately $200M in lost revenue."
        ),
        "investor_implications": (
            "Egyptian Eurobonds carry elevated risk; spreads have widened materially. "
            "IMF program compliance is the key sovereign solvency signal. "
            "EGP further depreciation is possible if fiscal gap widens; monitor FX reserves monthly data."
        ),
        "data_quality_note": None,
    },

    "NGA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Nigeria is a net oil exporter and benefits structurally from the global price surge, "
            "but its extremely limited refining capacity means it cannot fully capture the windfall — "
            "Nigeria paradoxically imports refined petroleum products even as it exports crude. "
            "The naira sits at 1,372/USD as the central bank manages post-unification FX pressure. "
            "Security conditions in the Niger Delta and northeastern Nigeria are stable "
            "but warrant continuous monitoring for any deterioration linked to global instability."
        ),
        "key_changes_this_week": [
            "Oil price surge positive for export revenues; limited by refining capacity constraint",
            "NGN at 1,372/USD; CBN managing post-FX unification pressures",
            "Refined petroleum import costs also rising despite crude export windfall",
            "Security situation stable but regional monitoring warranted",
            "Fiscal space improving modestly from higher crude benchmark revenue",
        ],
        "outlook": (
            "Nigeria's oil windfall is real but structurally limited by refining and infrastructure constraints. "
            "Dangote Refinery ramp-up progress is the key domestic catalyst for improved commodity capture. "
            "FX stability and inflation management remain primary near-term risks."
        ),
        "investor_implications": (
            "Nigerian Eurobonds benefit modestly from improved fiscal outlook on higher oil prices. "
            "NGN stabilization expected if FX reserves rebuild on windfall. "
            "Monitor Dangote Refinery output as game-changer for refined product import dependency."
        ),
        "data_quality_note": None,
    },

    "IDN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Indonesia's rupiah sits at 16,868/USD as the country navigates its dual exposure: "
            "as a net oil importer it faces rising energy costs from the Hormuz shock, "
            "but its status as the world's leading nickel exporter means it benefits from the broader "
            "commodity price rally driven by global supply chain disruption. "
            "Political stability under President Prabowo is maintained; no significant domestic events this week."
        ),
        "key_changes_this_week": [
            "IDR at 16,868/USD; moderate depreciation pressure from oil import cost shock",
            "Nickel exports benefit from commodity rally on global supply chain disruption",
            "Net oil importer: energy cost headwind from Hormuz closure and oil price surge",
            "Political stability maintained under Prabowo government",
            "EV battery supply chain positioning providing structural tailwind for nickel sector",
        ],
        "outlook": (
            "Indonesia's net commodity export position provides a partial hedge against the oil shock. "
            "The nickel-to-EV supply chain positioning is a strong medium-term structural positive. "
            "BI (Bank Indonesia) is managing IDR carefully; rate policy unchanged."
        ),
        "investor_implications": (
            "Indonesian equities offer selective opportunity in mining and nickel processing sectors. "
            "IDR modest depreciation risk; hedging recommended for US dollar-based investors. "
            "Sovereign bonds (SBN) benefit from BI support and remain investment grade."
        ),
        "data_quality_note": None,
    },

    "ZAF": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "South Africa is a relative beneficiary of the global crisis environment: gold above $5,155 per ounce "
            "is a major positive for its mining sector, which contributes significantly to export revenues and JSE market cap. "
            "The JSE is near record highs, driven by gold and platinum group metals (PGMs) repricing. "
            "The rand sits at 15.92/USD — relatively stable — and improving electricity supply (reduced load-shedding) "
            "supports the domestic economic recovery narrative."
        ),
        "key_changes_this_week": [
            "Gold above $5,155/oz — major positive for mining sector and JSE",
            "JSE near record highs; gold and PGM miners outperforming",
            "ZAR at 15.92/USD — relatively stable despite global risk-off",
            "Load-shedding improvement supporting domestic economic recovery",
            "PGM prices also elevated on global supply chain disruption premium",
        ],
        "outlook": (
            "South Africa's commodity exporter profile is well-suited to the current crisis environment. "
            "Sustained gold above $5,000 would be transformative for fiscal revenues and mining investment. "
            "Domestic political risks from GNU (Government of National Unity) stability remain but are manageable."
        ),
        "investor_implications": (
            "JSE gold miners (Gold Fields, AngloGold Ashanti, Harmony) are strong buys in this environment. "
            "ZAR has rare upside potential from gold windfall improving current account. "
            "SA sovereign bonds offer attractive real yields; GNU political stability is the key risk variable."
        ),
        "data_quality_note": None,
    },

    "POL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Poland's zloty sits at 3.62/EUR as the country continues its robust defense spending expansion "
            "and NATO integration deepening. NATO Cold Response exercise is underway, and Poland remains "
            "among the highest defense spenders as a share of GDP in the alliance. "
            "EU energy shock from the dual chokepoint closure is partly managed through Poland's post-2022 "
            "diversification away from Russian energy — Norwegian LNG and Baltic interconnectors provide alternatives."
        ),
        "key_changes_this_week": [
            "PLN at 3.62/EUR; macro stability maintained",
            "NATO Cold Response exercise underway; defense posture elevated",
            "Defense spending growth continuing as part of European 12.6% surge",
            "EU energy shock managed via diversified sources (Norwegian LNG, Baltic interconnectors)",
            "Ukraine war proximity remains the primary tail risk; monitoring eastern border",
        ],
        "outlook": (
            "Poland is a relative safe-haven within the EU given its energy diversification and "
            "strong NATO integration. Defense spending surge supports domestic industrial capacity. "
            "Ukraine war duration remains the primary geopolitical risk for Polish assets."
        ),
        "investor_implications": (
            "Polish equities offer defensive quality in European context. Defense suppliers and "
            "domestic consumption names preferred. PLN is relatively stable; POLGBs (Polish government bonds) "
            "offer attractive yields with moderate risk."
        ),
        "data_quality_note": None,
    },

    "AUS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Australia's ASX 200 fell 0.5%, underperforming its net commodity exporter fundamentals "
            "as global risk-off sentiment dominated. Australia stands to benefit indirectly from the Gulf "
            "LNG supply disruption: Australian LNG producers (Woodside, Santos) are natural beneficiaries "
            "as Qatari and Gulf supplies are constrained by Hormuz closure. "
            "Iron ore prices remain stable, supporting the major mining sector."
        ),
        "key_changes_this_week": [
            "ASX 200 fell 0.5%; global risk-off overriding commodity export positive",
            "LNG export opportunity from Gulf supply disruption; Woodside and Santos beneficiaries",
            "Iron ore prices stable; mining sector broadly supported",
            "AUD under modest pressure from risk-off flows despite commodity tailwind",
            "RBA rate path unchanged; inflation trajectory moderating",
        ],
        "outlook": (
            "Australia's commodity export profile positions it well for a sustained high-energy-price environment. "
            "LNG demand from Japan, Korea, and China as they seek Hormuz-alternative supplies could provide "
            "a significant near-term revenue uplift. Trade relationship management with China remains important."
        ),
        "investor_implications": (
            "ASX LNG producers (Woodside, Santos) and gold miners are near-term outperformers. "
            "AUD may strengthen on terms-of-trade improvement as global oil and LNG prices rise. "
            "Australian government bonds (ACGBs) offer safe-haven characteristics with solid credit quality."
        ),
        "data_quality_note": None,
    },

    "CAN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Canada is navigating a bilateral trade war with the United States while benefiting from the "
            "global oil price surge as a major exporter. Ottawa announced 25% retaliatory tariffs on $30B "
            "in US goods effective March 4 — the most significant trade retaliation since CUSMA renegotiation. "
            "Prime Minister Carney's government commands 61% approval, providing political capital for the trade standoff. "
            "Canadian oil sands producers benefit directly from WTI price surge driven by Hormuz closure."
        ),
        "key_changes_this_week": [
            "25% retaliatory tariffs on $30B US goods announced effective March 4",
            "PM Carney government at 61% approval; strong political mandate for trade standoff",
            "Oil exports benefit from WTI price surge from Hormuz closure",
            "CAD under modest pressure from US trade uncertainty",
            "Energy sector (Suncor, Canadian Natural Resources) outperforming",
        ],
        "outlook": (
            "Canada's trade war with the US is a significant headwind for integrated supply chains, "
            "but the energy sector windfall partially offsets economic impact. "
            "CUSMA/USMCA renegotiation pressure will define the medium-term trade relationship."
        ),
        "investor_implications": (
            "Canadian energy producers are strong buys on oil price surge; "
            "trade-exposed manufacturing and auto sector names warrant caution. "
            "CAD modest depreciation risk from trade uncertainty but energy terms-of-trade provide floor. "
            "CanGovt bonds offer safe-haven quality; spreads over UST remain tight."
        ),
        "data_quality_note": None,
    },

    "MEX": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Mexico's peso sits at 17.24/USD as nearshoring momentum continues to attract manufacturing FDI "
            "from companies seeking US-adjacent production capacity. "
            "USMCA/CUSMA exemptions partially protect Mexico from the Section 122 tariff regime, "
            "creating a competitive advantage relative to Asian and European exporters. "
            "US trade policy uncertainty remains the primary risk; any deterioration in USMCA terms "
            "would significantly impact Mexico's manufacturing export thesis."
        ),
        "key_changes_this_week": [
            "MXN at 17.24/USD; relative stability amid US tariff turbulence",
            "USMCA exemptions providing competitive advantage vs. Asian/European exporters",
            "Nearshoring FDI momentum continuing; manufacturing investment pipeline healthy",
            "US-Mexico tariff 25% threat remains contingent; Canada tariffs triggered March 4",
            "Banxico rate path monitoring; inflation moderating but vigilance required",
        ],
        "outlook": (
            "Mexico's nearshoring story remains structurally intact. USMCA framework provides the critical "
            "legal foundation for manufacturing investment. "
            "Political risk from Claudia Sheinbaum government's economic policy signals warrants monitoring."
        ),
        "investor_implications": (
            "Mexico is a relative outperformer among EM given USMCA insulation and nearshoring tailwind. "
            "MXN offers positive carry with moderate downside risk. "
            "Real estate (FIBRAS) and industrial REITs near US border are structural beneficiaries."
        ),
        "data_quality_note": None,
    },

    # -----------------------------------------------------------------------
    # LOW-IMPACT TIER 1 COUNTRIES
    # -----------------------------------------------------------------------

    "CHE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Switzerland is a primary beneficiary of global risk-off sentiment: CHF is strengthening against "
            "most major currencies as investors seek safe-haven assets, gold held at Swiss vaults is surging "
            "past $5,155, and Swiss financial institutions benefit from elevated wealth management inflows. "
            "No significant country-specific events this week; Switzerland's primary exposure is indirect "
            "through global trade disruption impacts on its export-oriented precision manufacturing and pharma sectors."
        ),
        "key_changes_this_week": [
            "CHF strengthening on safe-haven flows; SNB monitoring for excessive appreciation",
            "Gold above $5,155 benefits Swiss financial sector and commodity trading hubs (Geneva, Zurich)",
            "No significant domestic events; global risk environment dominated by Iran conflict",
            "Export sector faces CHF appreciation headwind",
        ],
        "outlook": (
            "Switzerland's safe-haven status insulates it from the worst of the global storm. "
            "SNB may intervene if CHF appreciation becomes disorderly and threatens export competitiveness."
        ),
        "investor_implications": (
            "CHF and Swiss franc-denominated assets are classic safe-haven buys. "
            "Swiss equities (Nestle, Novartis, Roche) offer defensive quality with CHF appreciation upside for USD investors."
        ),
        "data_quality_note": None,
    },

    "SWE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Sweden sees no significant country-specific events this week beyond participating in the broader "
            "European defense spending surge. Defense sector companies (Saab, BAE Sweden operations) benefit from "
            "increased NATO procurement as Europe targets 12.6% defense spending growth. "
            "Global risk environment dominated by Iran conflict and dual chokepoint crisis; "
            "Sweden's energy diversification reduces direct Hormuz vulnerability."
        ),
        "key_changes_this_week": [
            "Defense spending growth; Saab and defense contractors benefit from European surge",
            "No significant domestic events this week",
            "Global risk environment dominated by Iran conflict",
            "SEK modest weakness on risk-off flows; Riksbank monitoring",
        ],
        "outlook": "Sweden's NATO integration and defense industrial base position it well for the elevated security spending environment. Economic outlook stable.",
        "investor_implications": "Saab AB is a direct beneficiary of European defense surge. OMX Stockholm offers defensive quality. SEK has modest downside but fundamentals are sound.",
        "data_quality_note": None,
    },

    "NOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Norway is a significant beneficiary of the global energy price surge: as Western Europe's "
            "largest oil and gas producer, elevated Brent prices directly benefit Equinor and Norwegian "
            "sovereign wealth fund (GPFG) revenues. The NOK may strengthen on improved energy terms-of-trade. "
            "Norway faces no direct military or geopolitical exposure to the Iran crisis."
        ),
        "key_changes_this_week": [
            "Oil and gas price surge directly benefits Norwegian sovereign revenues and Equinor",
            "GPFG (Oil Fund) portfolio values shifting on equity sell-off but NOK energy terms-of-trade improving",
            "No significant domestic events; global risk environment dominated by Iran conflict",
            "NOK strengthening modestly on energy export windfall",
        ],
        "outlook": "Sustained high energy prices are structurally positive for Norway's fiscal position. GPFG mark-to-market losses from equity sell-off are offset by energy revenue gains.",
        "investor_implications": "NOK and Norwegian government bonds are safe and income-generating. Equinor is a direct beneficiary of oil price surge.",
        "data_quality_note": None,
    },

    "NLD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "The Netherlands faces significant indirect exposure through Rotterdam Port — Europe's largest — "
            "which will see disrupted inbound oil and LNG flows from the dual chokepoint crisis. "
            "ASML, the critical semiconductor lithography monopoly, is largely insulated from the Iran "
            "crisis directly but faces ongoing geopolitical pressure from US-China chip restrictions. "
            "No significant domestic political events this week."
        ),
        "key_changes_this_week": [
            "Rotterdam Port facing disrupted oil and LNG inbound flows from dual chokepoint crisis",
            "ASML monitoring US-China chip restriction developments; no new restrictions this week",
            "Global risk environment dominated by Iran conflict and dual chokepoint crisis",
            "AEX index down in line with European peers",
        ],
        "outlook": "Netherlands' port-dependent economy is more exposed than average to supply chain disruption. Energy cost shock feeds into Dutch industrial and residential costs.",
        "investor_implications": "ASML remains the premier investment thesis in European tech; cyclical industrials face headwinds. Amsterdam-listed financials may see safe-haven demand.",
        "data_quality_note": None,
    },

    "ESP": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Spain has no significant country-specific events this week. "
            "The global risk environment dominated by Iran conflict and dual chokepoint crisis weighs on "
            "Spanish equities, but Spain's relatively high renewable energy penetration provides modest insulation "
            "from the oil price shock. Tourism sector — a key GDP driver — may see bookings shift "
            "from Middle East destinations toward Southern Europe."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring global Iran conflict impact",
            "IBEX 35 declining in line with European peers",
            "Renewable energy penetration providing partial oil price insulation",
            "Tourism booking shifts from Middle East to Spain possible near-term positive",
        ],
        "outlook": "Spain's economic recovery continues with renewable energy as a structural positive. European energy shock creates headwinds but Spain is less exposed than Germany or Netherlands.",
        "investor_implications": "Spanish equities and Bonos (sovereign bonds) track broader European sentiment. Iberdrola and renewable energy names benefit from high energy price environment.",
        "data_quality_note": None,
    },

    "ITA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Italy has no significant country-specific events this week. "
            "As a major energy importer heavily dependent on Mediterranean gas pipeline flows and LNG, "
            "Italy faces meaningful energy cost exposure from the dual chokepoint crisis. "
            "BTP-Bund spreads are widening modestly on risk-off sentiment. "
            "Defense spending is increasing as part of the European NATO commitment surge."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring European energy shock impact",
            "BTP-Bund spreads widening on risk-off; fiscal credibility monitoring",
            "Energy import cost exposure from Hormuz/Suez dual closure",
            "Defense spending increasing as part of European NATO commitment",
        ],
        "outlook": "Italy's fiscal position remains a medium-term concern; ECB backstop is critical. Energy shock creates stagflation risk for the Italian economy.",
        "investor_implications": "BTPs carry elevated spread risk; ECB PEPP reinvestment signals are the key support mechanism. Italian equities defensive in energy and financials.",
        "data_quality_note": None,
    },

    "SGP": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Singapore faces significant trade disruption risk as a global entrepot hub: "
            "the dual Hormuz/Suez closure and shipping route reorganization will affect transshipment "
            "volumes through its port (world's 2nd largest container port). "
            "Singapore's status as a financial center may attract capital flight from more conflict-exposed "
            "regional hubs including Dubai. SGD is well-supported by MAS intervention capacity."
        ),
        "key_changes_this_week": [
            "Port of Singapore faces shipping route reorganization from dual chokepoint closure",
            "Financial hub capital inflows potentially accelerating from Dubai conflict disruption",
            "STI (Straits Times Index) declining on regional risk-off sentiment",
            "SGD well-supported by MAS; safe-haven within Southeast Asia",
        ],
        "outlook": "Singapore's diversified financial and logistics model provides resilience. Capital inflows from regional instability are a structural positive for asset management and private banking.",
        "investor_implications": "SGD is a safe-haven within Asia EM; SGS (Singapore Government Securities) offer quality fixed income. DBS, OCBC, UOB benefit from elevated interest margins.",
        "data_quality_note": None,
    },

    "TWN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Taiwan is monitoring the China military purge situation carefully — the elimination of independent "
            "PLA leadership could either reduce near-term Taiwan Strait risk (degraded offensive planning capability) "
            "or increase it (Xi direct control with less institutional constraint). "
            "TSMC and the semiconductor supply chain face indirect exposure from global shipping disruption. "
            "The stalled $11.1B US arms sale ahead of Trump-Xi summit creates a near-term defense supply uncertainty."
        ),
        "key_changes_this_week": [
            "China military purge (100+ officers) creates Taiwan Strait risk reassessment need",
            "$11.1B US arms sale stalled ahead of Trump-Xi summit",
            "TSMC supply chain monitoring from global shipping disruption",
            "TAIEX under pressure from regional risk-off sentiment",
            "TWD holding relative to Asian peers; CBC monitoring",
        ],
        "outlook": "Taiwan Strait risk requires active reassessment given PLA leadership disruption. TSMC's strategic importance continues to provide a form of geopolitical insurance. Arms sale stall is a near-term concern.",
        "investor_implications": "TSMC ADR and TAIEX exposure should factor in elevated tail risk. Semiconductor supply chain monitoring warranted. TWD has modest depreciation risk.",
        "data_quality_note": None,
    },

    "MYS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Malaysia has no significant country-specific events this week. "
            "As a net energy exporter (oil and LNG), Malaysia benefits from the global price surge, "
            "supporting Petronas revenues and the fiscal position. "
            "Global risk environment dominated by Iran conflict and dual chokepoint crisis; "
            "Malacca Strait shipping volumes may increase as alternative routing expands."
        ),
        "key_changes_this_week": [
            "Oil and LNG price surge benefits Petronas and Malaysian fiscal revenues",
            "Malacca Strait alternative routing may increase transit volumes",
            "No significant domestic events; global risk environment dominant",
            "MYR holding; BNM monitoring capital flows",
        ],
        "outlook": "Malaysia's net energy exporter status provides fiscal insulation. Semiconductor and electronics export exposure to global trade disruption warrants monitoring.",
        "investor_implications": "Malaysian equities benefit from energy price tailwind. MYR has modest upside potential from energy terms-of-trade improvement. MGS (Malaysian Government Securities) are investment grade.",
        "data_quality_note": None,
    },

    "THA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Thailand has no significant country-specific events this week. "
            "As a net oil importer, Thailand faces energy cost headwinds from the Hormuz closure oil price surge. "
            "Tourism sector — a major GDP contributor — may see some demand shift from conflict-adjacent "
            "Middle Eastern destinations. THB is under modest depreciation pressure from risk-off flows."
        ),
        "key_changes_this_week": [
            "Oil import costs rising from Hormuz closure; energy cost headwind",
            "Tourism sector may benefit from demand shift away from Middle East destinations",
            "THB under modest depreciation pressure",
            "No significant domestic political events this week",
        ],
        "outlook": "Thailand's energy import dependency creates near-term headwinds. Tourism recovery remains the key domestic growth driver. BOT (Bank of Thailand) rate policy unchanged.",
        "investor_implications": "Thai equities face near-term pressure from oil shock. SET index tracking broader Asian risk-off. Tourism and hospitality names may recover faster than industrials.",
        "data_quality_note": None,
    },

    # -----------------------------------------------------------------------
    # LOW-IMPACT TIER 2 COUNTRIES
    # -----------------------------------------------------------------------

    "ARG": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Argentina has no significant country-specific events this week. "
            "The global risk environment is dominated by the Iran conflict and dual chokepoint crisis. "
            "Argentina's commodity export position (soybeans, corn, beef) provides modest insulation. "
            "IMF program implementation under Milei government continues; peso stability is the primary domestic focus."
        ),
        "key_changes_this_week": [
            "No significant domestic events; global risk environment dominant",
            "Commodity export prices (soybeans, corn) elevated on global disruption",
            "IMF program implementation continues under Milei government",
            "ARS stability monitoring; blue-dollar spread narrowing trend",
        ],
        "outlook": "Argentina's IMF program trajectory and peso stabilization are the key investment variables. Commodity export tailwind is modest but positive.",
        "investor_implications": "Argentine sovereign bonds remain speculative grade; Milei program credibility is the key catalyst. ARS-denominated exposure should remain hedged.",
        "data_quality_note": None,
    },

    "BGD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Bangladesh completed a historic democratic transition with BNP winning a landslide (209 seats) "
            "in the February 12 election — the first post-Hasina vote. Business optimism is improving under "
            "the new government. The oil price surge from Hormuz closure creates a headwind given "
            "Bangladesh's energy import dependency. Garment export sector provides the economic base."
        ),
        "key_changes_this_week": [
            "BNP won landslide election (209 seats); democratic transition completing",
            "Business optimism improving under new government",
            "Energy import cost headwind from oil price surge",
            "Garment sector stable; export orders maintaining",
        ],
        "outlook": "Democratic transition is positive for governance and FDI. BNP economic policy signals will be key. Energy import costs are a near-term headwind.",
        "investor_implications": "Bangladeshi garment exporters are a selective opportunity. Democratic transition positive for long-term FDI; energy costs a near-term headwind. BDT stability monitoring.",
        "data_quality_note": None,
    },

    "CHL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Chile has no significant country-specific events this week. "
            "The global risk environment is dominated by the Iran conflict. "
            "Chile's copper exports benefit from elevated commodity prices on global supply chain disruption. "
            "Lithium sector continues its structural growth trajectory; Codelco and SQM monitoring."
        ),
        "key_changes_this_week": [
            "Copper prices elevated on global supply chain disruption; positive for export revenues",
            "Lithium sector structural growth continuing",
            "No significant domestic events; global risk environment dominant",
            "CLP relatively stable; BCCH monitoring",
        ],
        "outlook": "Chile's copper and lithium export profile provides structural tailwinds. Fiscal position improving on commodity revenues. Political stability maintained.",
        "investor_implications": "Chilean equities (Codelco related, SQM, Antofagasta) benefit from copper price surge. CLP has upside potential from commodity terms-of-trade improvement.",
        "data_quality_note": None,
    },

    "COL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Colombia has no significant country-specific events this week. "
            "As an oil exporter, Colombia benefits from the global price surge to a modest degree, "
            "though Ecopetrol's production constraints limit full capture. "
            "Global risk environment dominated by Iran conflict and dual chokepoint crisis."
        ),
        "key_changes_this_week": [
            "Oil price surge modestly positive for Ecopetrol and fiscal revenues",
            "No significant domestic events; global risk environment dominant",
            "COP holding; BanRep monitoring",
            "Security situation in coca-producing regions stable",
        ],
        "outlook": "Colombia's oil export tailwind is real but constrained by production capacity. Fiscal position and peso stability are key monitoring variables.",
        "investor_implications": "Ecopetrol is a modest beneficiary of oil surge. Colombian TES bonds offer EM yield with moderate risk. COP has limited upside from oil given production constraints.",
        "data_quality_note": None,
    },

    "CZE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Czech Republic has no significant country-specific events this week. "
            "The global risk environment dominated by Iran conflict affects Czech equities via European risk-off sentiment. "
            "Defense spending is increasing as part of NATO/EU commitments. "
            "CZK is relatively stable within the European context."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring European energy shock",
            "Defense spending increasing per NATO commitments",
            "CZK stable; CNB rate policy monitoring",
            "European risk-off sentiment affecting PX index",
        ],
        "outlook": "Czech Republic's EU membership and diversified energy supply post-2022 provide resilience. Defense sector investment is a structural positive.",
        "investor_implications": "Czech equities and government bonds are investment grade with moderate risk. Defense sector exposure is a thematic positive.",
        "data_quality_note": None,
    },

    "FIN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Finland has no significant country-specific events this week. "
            "As a NATO member with a long border with Russia, Finland's security posture is elevated. "
            "Defense spending is increasing significantly as part of the European surge. "
            "Finnish energy diversification post-2022 reduces direct Hormuz closure vulnerability."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring European and Russia-adjacent risks",
            "Defense spending surge; NATO posture elevated",
            "Energy diversification reducing Hormuz vulnerability",
            "OMXH25 tracking European risk-off sentiment",
        ],
        "outlook": "Finland's NATO integration and Russia border monitoring create elevated but manageable security overhead. Economy stable; defense sector a structural positive.",
        "investor_implications": "Finnish government bonds (FGBs) are investment grade. Defense and security sector equities benefit from spending surge. EUR-denominated exposure standard.",
        "data_quality_note": None,
    },

    "GRC": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Greece has no significant country-specific events this week. "
            "As a major shipping nation, Greece's shipping sector is navigating significant route disruptions "
            "from dual chokepoint crisis — Greek-owned vessels represent ~20% of global tonnage. "
            "Some routes are now commanding premium freight rates; Greek shipowners benefit on earnings."
        ),
        "key_changes_this_week": [
            "Greek-owned shipping fleet benefiting from elevated freight rates from route disruptions",
            "Suez/Hormuz closure creating rerouting premium for vessel operators",
            "No significant domestic political events",
            "ATHEX tracking European risk-off sentiment",
        ],
        "outlook": "Greece's shipping sector is a structural beneficiary of freight rate surges from chokepoint crises. Domestic economy stable; tourism sector monitoring Middle East conflict impact on bookings.",
        "investor_implications": "Greek shipping equities (Costamare, Star Bulk, Navios) are direct beneficiaries of freight rate surge. Greek government bonds (GGBs) have compressed to investment-grade-adjacent spreads.",
        "data_quality_note": None,
    },

    "IRL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ireland has no significant country-specific events this week. "
            "The global risk environment dominated by Iran conflict and dual chokepoint crisis. "
            "Ireland's pharma and tech export economy is largely insulated from direct energy shock but "
            "faces US tariff uncertainty given large US multinational presence (Apple, Google, Meta EU operations)."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring US tariff impacts on multinational structures",
            "Section 122 tariffs create indirect risk for US multinationals with Irish operations",
            "Energy costs rising modestly from European shock",
            "ISEQ tracking European risk-off sentiment",
        ],
        "outlook": "Ireland's multinational-dependent economy is sensitive to US trade policy. Fiscal position very strong from corporate tax revenues. Housing market continues to be a structural challenge.",
        "investor_implications": "Irish government bonds (ICGBs) are investment grade. Multinational FDI concentration creates tail risk from US tax or tariff policy changes.",
        "data_quality_note": None,
    },

    "PRT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Portugal has no significant country-specific events this week. "
            "The global risk environment dominated by Iran conflict. "
            "Portugal's high renewable energy penetration provides insulation from oil price shocks. "
            "Tourism sector may benefit modestly from demand diversion away from Middle East destinations."
        ),
        "key_changes_this_week": [
            "No significant domestic events; global risk environment dominant",
            "High renewable energy penetration limiting oil shock exposure",
            "Tourism demand diversion from Middle East possible near-term positive",
            "PSI tracking European risk-off",
        ],
        "outlook": "Portugal's fiscal consolidation and renewable energy leadership are structural positives. Tourism-driven growth continues. ECB rate decisions are the primary external policy driver.",
        "investor_implications": "Portuguese OTs (government bonds) are investment grade with improving fundamentals. Tourism and renewable energy equities are selective opportunities.",
        "data_quality_note": None,
    },

    "IRQ": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Iraq faces direct collateral exposure from the Iran conflict: as a country with close Iranian "
            "political and military ties, US strikes targeting Iran-linked assets create spillover risk. "
            "Iraq's oil export infrastructure — centered on Basra terminals — is adjacent to the Hormuz closure zone. "
            "Basra Heavy crude exports may face shipping disruption even if terminals remain operational. "
            "No specific domestic events this week beyond conflict adjacency monitoring."
        ),
        "key_changes_this_week": [
            "Iran conflict creating spillover risk for Iraq given Iran-linked political/military ties",
            "Basra terminal oil exports affected by Hormuz closure shipping disruption",
            "PMF (Iran-linked militias) activity monitoring; potential for US strikes on Iraqi soil",
            "IQD at 1,310/USD; CBi intervention maintaining stability",
        ],
        "outlook": "Iraq's political-military relationship with Iran creates significant tail risk from continued US military operations. Oil export disruption is an economic blow despite high prices.",
        "investor_implications": "Iraq sovereign exposure is highly speculative. Oil sector investment requires geopolitical risk premium significantly above pre-crisis levels.",
        "data_quality_note": None,
    },

    "JOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Jordan has no significant country-specific events this week but faces significant regional spillover "
            "from the Iran crisis and Lebanese conflict escalation. "
            "Jordan hosts large Palestinian and Syrian refugee populations; regional instability "
            "creates additional refugee pressure and fiscal stress. "
            "Jordan's peace treaty with Israel creates a sensitive diplomatic position."
        ),
        "key_changes_this_week": [
            "Regional instability escalating; Lebanon and Iran conflicts creating refugee pressure risk",
            "Jordan's peace treaty with Israel creates diplomatic complexity",
            "Energy import costs rising; Jordan is highly oil-import dependent",
            "JOD peg to USD maintained; CBJ reserves monitoring",
        ],
        "outlook": "Jordan's fiscal position is strained by regional instability and energy import costs. IMF support and Gulf aid are critical fiscal stabilizers.",
        "investor_implications": "Jordan sovereign bonds carry elevated regional risk premium. JOD peg is well-supported but foreign aid dependency is a structural vulnerability.",
        "data_quality_note": None,
    },

    "KAZ": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Kazakhstan has no significant country-specific events this week. "
            "As a major oil exporter (CPC pipeline to Black Sea), Kazakhstan benefits from elevated oil prices. "
            "The Russia-Ukraine war continues to complicate CPC pipeline transit logistics. "
            "Global risk environment dominated by Iran conflict."
        ),
        "key_changes_this_week": [
            "Oil price surge positive for Kazakhstani export revenues and fiscal position",
            "CPC pipeline transit continuing; Russia-Ukraine war creates logistics complexity",
            "No significant domestic events",
            "KZT relatively stable; NBK managing exchange rate",
        ],
        "outlook": "Kazakhstan's oil export windfall is positive for fiscal position. Diversification away from CPC pipeline via Caspian and China routes is a medium-term priority.",
        "investor_implications": "Kazakhstan sovereign bonds benefit from improved fiscal outlook. Tengiz and Kashagan field output is key variable for investor returns.",
        "data_quality_note": None,
    },

    "MAR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Morocco has no significant country-specific events this week. "
            "The global risk environment dominated by Iran conflict. "
            "Morocco is positioned as a nearshoring hub for European manufacturing, "
            "a structural benefit as European companies seek supply chain diversification. "
            "Energy import dependency creates headwind from oil price surge."
        ),
        "key_changes_this_week": [
            "No significant domestic events; global risk environment dominant",
            "Nearshoring FDI momentum continuing; European supply chain diversification beneficiary",
            "Energy import costs rising from oil price shock",
            "MAD stable; BAM maintaining exchange rate policy",
        ],
        "outlook": "Morocco's European nearshoring positioning and phosphate exports provide structural positives. Energy import costs are the primary near-term headwind.",
        "investor_implications": "Moroccan sovereign bonds are investment grade with improving fundamentals. OCP (phosphate) equity exposure benefits from elevated fertilizer prices.",
        "data_quality_note": None,
    },

    "NZL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "New Zealand has no significant country-specific events this week. "
            "Geographic distance from conflict zones provides insulation. "
            "As an agricultural exporter, NZ benefits modestly from elevated global commodity prices. "
            "Energy import dependency creates a modest headwind from oil price surge. "
            "NZD under modest risk-off depreciation pressure."
        ),
        "key_changes_this_week": [
            "No significant domestic events; monitoring global risk environment",
            "Agricultural export prices elevated on global supply disruption",
            "Energy import costs rising modestly",
            "NZD under risk-off depreciation pressure",
        ],
        "outlook": "New Zealand's geographic insulation is a structural positive in this environment. RBNZ rate path is the primary domestic policy variable.",
        "investor_implications": "NZGBs offer investment-grade fixed income. NZD has modest downside risk from risk-off flows. Agricultural sector equity provides commodity tailwind.",
        "data_quality_note": None,
    },

    "OMN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Oman occupies a uniquely precarious position: as a Gulf state bordering Iran and flanking the "
            "Strait of Hormuz, Oman's Duqm port and LNG facilities are caught in the conflict zone. "
            "Oman has historically maintained better relations with Iran than other Gulf states, "
            "which may provide some protection but also creates complex diplomatic positioning with the US-led coalition. "
            "Oil export revenues are blocked by Hormuz closure like other Gulf producers."
        ),
        "key_changes_this_week": [
            "Hormuz closure blocking Omani oil and LNG exports; direct revenue impact",
            "Oman's Iran diplomatic ties create complex positioning within US-led coalition",
            "Duqm port potentially affected by conflict adjacency",
            "OMR peg to USD maintained; CBO reserves monitoring",
        ],
        "outlook": "Oman's Hormuz adjacency creates both revenue disruption and direct security exposure. Iran relationship is an unusual diplomatic card. Sovereign rating under pressure if closure extends.",
        "investor_implications": "Omani sovereign bonds carry elevated risk from Hormuz exposure and Iran adjacency. Monitor for any diplomatic role Oman might play in Iran negotiations.",
        "data_quality_note": None,
    },

    "PER": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Peru has no significant country-specific events this week. "
            "As a major copper and gold exporter, Peru benefits from elevated commodity prices — "
            "particularly gold above $5,155/oz which is a major positive for Las Bambas, Cerro Verde, "
            "and Yanacocha operations. "
            "Global risk environment dominated by Iran conflict; no direct Peru exposure."
        ),
        "key_changes_this_week": [
            "Gold above $5,155 major positive for Peruvian mining sector",
            "Copper prices elevated on global supply disruption; positive for Cerro Verde and Las Bambas",
            "No significant domestic events; global risk environment dominant",
            "PEN stable; BCRP monitoring",
        ],
        "outlook": "Peru's mining export profile provides genuine tailwind in a commodity surge environment. Political stability under Boluarte government is maintained but remains fragile.",
        "investor_implications": "Peruvian mining equities (Southern Copper, Buenaventura) benefit from dual gold/copper surge. PEN has modest upside from commodity terms-of-trade improvement.",
        "data_quality_note": None,
    },

    "PHL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Philippines has no significant country-specific events this week. "
            "As a net oil importer with significant remittance inflows from overseas Filipino workers "
            "(including those in the Gulf), the Hormuz crisis creates a dual pressure: "
            "rising energy costs and potential disruption to OFW remittance flows from Gulf states. "
            "South China Sea territorial disputes remain an ongoing background risk."
        ),
        "key_changes_this_week": [
            "OFW remittance flows from Gulf states at risk from Iran conflict disruption",
            "Oil import costs rising from Hormuz closure; energy cost headwind",
            "No significant domestic events",
            "PHP under modest depreciation pressure; BSP monitoring",
        ],
        "outlook": "Philippines' OFW remittance vulnerability to Gulf conflict is a meaningful risk. Energy import costs create near-term fiscal pressure. South China Sea monitoring ongoing.",
        "investor_implications": "Philippine sovereign bonds and PSEi face near-term pressure from OFW risk and energy costs. BSP has capacity to support PHP if needed. Remittance data will be a key leading indicator.",
        "data_quality_note": None,
    },

    "ROU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Romania has no significant country-specific events this week. "
            "As a NATO member and EU state bordering Ukraine, Romania's security posture is elevated. "
            "Romania is a modest oil and gas producer, providing partial energy independence. "
            "Defense spending is increasing per NATO commitments as part of the European surge."
        ),
        "key_changes_this_week": [
            "No significant domestic events; Ukraine war proximity monitoring",
            "Defense spending increasing per NATO commitments",
            "Domestic oil and gas production providing partial energy independence",
            "RON relatively stable; NBR rate policy unchanged",
        ],
        "outlook": "Romania's NATO integration and partial energy self-sufficiency provide resilience. Ukraine war proximity creates persistent security overhead but no direct escalation.",
        "investor_implications": "Romanian government bonds (RONGBs) are investment grade with moderate risk. Defense sector investment is a thematic positive. RON monitoring vs EUR.",
        "data_quality_note": None,
    },

    "VNM": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Vietnam has no significant country-specific events this week. "
            "As a major electronics and manufacturing exporter, Vietnam benefits from US-China trade diversion "
            "and nearshoring trends. Energy import costs from oil price surge are a modest headwind. "
            "Global risk environment dominated by Iran conflict; Vietnam has no direct exposure."
        ),
        "key_changes_this_week": [
            "No significant domestic events; global risk environment dominant",
            "Manufacturing and electronics export positioning benefits from US-China diversion",
            "Energy import costs rising modestly from oil price shock",
            "VND stable; SBV managing exchange rate",
        ],
        "outlook": "Vietnam's manufacturing export positioning as a China alternative is a strong structural positive. FDI inflows from Samsung, Intel, and others continue. Energy import costs are the primary headwind.",
        "investor_implications": "Vietnamese equities offer EM growth exposure with nearshoring tailwind. VND is managed; monitor SBV FX policy. Ho Chi Minh City Stock Exchange tracking regional risk-off.",
        "data_quality_note": None,
    },

    # -----------------------------------------------------------------------
    # TIER 3 COUNTRIES — Brief narratives (all included for completeness)
    # -----------------------------------------------------------------------

    "AZE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Azerbaijan has no significant country-specific events this week. "
            "As a Caspian oil and gas producer with pipeline connectivity to Europe (BTC, TANAP), "
            "Azerbaijan benefits from elevated energy prices and increased European demand for "
            "non-Russian, non-Gulf energy supplies."
        ),
        "key_changes_this_week": [
            "Caspian oil production benefiting from price surge and European demand diversification",
            "BTC and TANAP pipeline flows supporting European energy security",
            "No significant domestic events",
        ],
        "outlook": "Azerbaijan's energy export position is strategically valuable given global supply disruptions. Nagorno-Karabakh post-conflict consolidation continues.",
        "investor_implications": "SOCAR bonds and Azerbaijani sovereign exposure benefit from energy windfall. AZN peg stable.",
        "data_quality_note": None,
    },

    "BGD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Bangladesh completed a major democratic transition with BNP winning a landslide (209 seats) "
            "in the February 12 election. Business optimism is improving. "
            "Energy import costs are rising from the Hormuz oil price shock. "
            "Garment export sector provides the economic base for stability."
        ),
        "key_changes_this_week": [
            "BNP landslide election victory (209 seats); democratic transition completing",
            "Energy import cost headwind from oil price surge",
            "Business optimism improving under new government",
        ],
        "outlook": "Democratic transition positive for governance and FDI. Energy costs are a near-term headwind. Garment sector resilience provides base-case stability.",
        "investor_implications": "Garment sector exporters offer selective opportunity. BDT monitoring; energy costs create inflationary pressure.",
        "data_quality_note": None,
    },

    "ETH": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Ethiopia has no significant country-specific events this week beyond the ongoing internal "
            "security situation in Amhara and Tigray regions. "
            "Global risk environment dominated by Iran conflict. "
            "Ethiopia's domestic political and humanitarian challenges remain the primary investor focus."
        ),
        "key_changes_this_week": [
            "No significant new events; internal security monitoring continues",
            "Global risk environment dominated by Iran conflict",
            "ETB under continued depreciation pressure",
        ],
        "outlook": "Ethiopia's peace process and economic reform under IMF program remain the key variables. Security situation in regions requires monitoring.",
        "investor_implications": "Ethiopia sovereign bonds are in restructuring; avoid new exposure. Telecom sector (Ethio Telecom) is the primary investable asset.",
        "data_quality_note": None,
    },

    "COD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Democratic Republic of Congo has no significant country-specific events this week. "
            "Eastern DRC security situation — including M23 and FDLR activity — remains a persistent challenge. "
            "Global risk environment dominated by Iran conflict. "
            "Critical mineral exports (cobalt, coltan) benefit from elevated commodity prices."
        ),
        "key_changes_this_week": [
            "Critical mineral prices (cobalt, coltan) elevated from global supply disruption",
            "Eastern DRC security situation ongoing; M23 monitoring",
            "No significant new political events",
        ],
        "outlook": "DRC's critical mineral wealth is strategically important for EV supply chains. Security situation in east is the primary risk to mining operations and investment.",
        "investor_implications": "Mining sector exposure (Glencore, CMOC) benefits from commodity prices but carries security and governance risk. DRC sovereign bonds are speculative grade.",
        "data_quality_note": None,
    },

    "MMR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Myanmar (Burma) has no significant country-specific events this week beyond the ongoing "
            "civil conflict between the military junta and resistance forces. "
            "Global risk environment dominated by Iran conflict. "
            "Myanmar remains broadly uninvestable under military rule with active sanctions."
        ),
        "key_changes_this_week": [
            "Civil conflict ongoing; junta vs. resistance forces monitoring",
            "No significant change in international sanctions status",
            "No significant domestic events beyond conflict monitoring",
        ],
        "outlook": "Myanmar remains in a prolonged political and military conflict with no near-term resolution pathway. Economy severely contracted under junta rule.",
        "investor_implications": "Myanmar is broadly uninvestable under current sanctions and conflict conditions. No actionable investor thesis.",
        "data_quality_note": None,
    },

    "SDN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": (
            "Sudan has no significant country-specific events this week beyond the ongoing civil war "
            "between SAF and RSF forces, which has created one of the world's worst humanitarian crises. "
            "Global risk environment dominated by Iran conflict. "
            "Sudan remains in active conflict and is broadly uninvestable."
        ),
        "key_changes_this_week": [
            "Civil war (SAF vs. RSF) ongoing; humanitarian crisis deepening",
            "No significant change in international engagement",
            "Sudan remains broadly uninvestable",
        ],
        "outlook": "Sudan's civil war has no near-term resolution pathway. Humanitarian crisis continues to worsen. No investor pathway until conflict terminates.",
        "investor_implications": "Sudan is uninvestable. No actionable thesis. Monitor for ceasefire agreements as potential catalyst for eventual reconstruction investment.",
        "data_quality_note": None,
    },

}

# Default narrative for countries not explicitly defined above
DEFAULT_NARRATIVE_TEMPLATE = {
    "ai_generated": True,
    "generated_at": GENERATED_AT,
    "run_id": RUN_ID,
    "executive_summary": (
        "No significant country-specific events this week. "
        "The global risk environment is dominated by the Iran conflict and dual chokepoint crisis "
        "(Strait of Hormuz closed by IRGC + Red Sea Houthi interdiction of Suez). "
        "Oil prices surged 7-8%, global equities sold off broadly, and gold reached $5,155/oz. "
        "This country's investment thesis should be assessed primarily through the lens of "
        "its commodity export/import position, trade dependencies on Gulf states, and "
        "exposure to global risk-off sentiment."
    ),
    "key_changes_this_week": [
        "No significant country-specific events this week",
        "Global risk environment dominated by Iran conflict and dual Hormuz/Suez chokepoint crisis",
        "Oil +7-8%, gold $5,155, global equity sell-off — monitoring indirect exposure",
    ],
    "outlook": (
        "Outlook contingent on Iran conflict duration and Hormuz reopening timeline. "
        "Domestic fundamentals unchanged; global risk environment is the dominant variable this week."
    ),
    "investor_implications": (
        "Investors should assess this country's indirect exposure to the Iran crisis through "
        "energy import costs, trade route disruption, and global risk-off capital flows. "
        "No country-specific positioning changes recommended this week."
    ),
    "data_quality_note": None,
}


def update_country_narrative(code: str, data: dict, narrative: dict) -> dict:
    """Update the narrative section of a country's data dict."""
    data["narrative"] = narrative
    data["last_updated"] = "2026-03-03T22:50:00Z"
    data["run_id"] = RUN_ID
    return data


def main():
    updated = []
    skipped = []
    errors = []

    country_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")])

    for fname in country_files:
        code = fname.replace(".json", "")
        fpath = os.path.join(DATA_DIR, fname)

        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            tier = data.get("tier")

            # Only update Tier 1 and Tier 2
            if tier not in (1, 2):
                skipped.append((code, f"Tier {tier} — skipped"))
                continue

            # Get the appropriate narrative
            if code in NARRATIVES:
                narrative = NARRATIVES[code]
            else:
                # Use default template, customized with country name
                narrative = dict(DEFAULT_NARRATIVE_TEMPLATE)

            # Remove None data_quality_note
            if narrative.get("data_quality_note") is None:
                narrative.pop("data_quality_note", None)

            data = update_country_narrative(code, data, narrative)

            with open(fpath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write("\n")

            updated.append((code, tier, "custom" if code in NARRATIVES else "default"))

        except Exception as e:
            errors.append((code, str(e)))

    # Summary
    print("=" * 70)
    print(f"Agent 13 — Country Profile Synthesizer — Run {RUN_ID}")
    print("=" * 70)
    print(f"\nUpdated {len(updated)} countries (Tier 1 + Tier 2):")
    for code, tier, ntype in updated:
        marker = "[CUSTOM]" if ntype == "custom" else "[DEFAULT]"
        print(f"  {marker} {code} (Tier {tier})")

    print(f"\nSkipped {len(skipped)} countries (Tier 3 — not in scope):")
    for code, reason in skipped:
        print(f"  {code}: {reason}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for code, err in errors:
            print(f"  {code}: {err}")
    else:
        print("\nNo errors.")

    print("\n" + "=" * 70)
    print("Agent 13 complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
