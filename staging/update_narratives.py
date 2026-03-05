#!/usr/bin/env python3
"""Agent 13: Country Profile Synthesizer - Generate narratives for Tier 1 and Tier 2 countries."""

import json
import os
from datetime import datetime

DATA_DIR = "/home/pietro/stratoterra/data/countries"
GENERATED_AT = "2026-03-04T18:30:00Z"
RUN_ID = "2026-W10"

# All narratives keyed by country code
NARRATIVES = {
    # ===================== HIGH PRIORITY (full narrative) =====================

    "IRN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Iran is under active US-Israeli military bombardment on Day 5 of Operation Epic Fury/Roaring Lion. Supreme Leader Khamenei was killed on Feb 28 and no constitutional succession mechanism has been activated, leaving the IRGC governing via an interim council. The Strait of Hormuz is effectively closed to commercial traffic, eliminating Iran's primary export route and approximately 70% of government revenue. The economy is in freefall with GDP on a -10% to -15% annualized trajectory, inflation at 42.4% approaching hyperinflation, and the rial collapsing on parallel markets.",
        "key_changes_this_week": [
            "Supreme Leader Khamenei killed in initial strikes (Feb 28) -- leadership vacuum with no succession activated",
            "Strait of Hormuz closed by IRGC retaliation, severing Iran's primary export route",
            "IRGC struck 27 US bases across 9 countries in retaliatory campaign",
            "Nuclear facilities including Natanz severely damaged across 1,000+ target strikes",
            "Currency in freefall; inflation trajectory toward hyperinflation (42.4% and accelerating)",
            "Political risk premium raised to 5,200 bps -- highest in tracked universe"
        ],
        "outlook": "Near-term trajectory is catastrophic. Active military operations will continue for weeks per US statements. IRGC factional infighting likely as leadership vacuum persists. Hormuz closure duration is the single most consequential variable for global energy markets. No diplomatic pathway is visible. State collapse scenario is non-trivial.",
        "investor_implications": "Iran is completely uninvestable across all asset classes and timeframes. All existing exposures should be written to zero. Secondary sanctions apply to any entity transacting with Iranian counterparties. The primary investor concern is indirect: Hormuz closure effects on Gulf sovereign creditworthiness, global energy prices, and Asian supply chains.",
        "data_quality_note": "All Iran economic data is extremely low confidence under active conflict. Pre-crisis IMF figures no longer reflect conditions. Military assessments from OSINT only. Maximum political risk premium active."
    },

    "ISR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Israel is conducting multi-front military operations against Iran (Operation Roaring Lion), Hezbollah in Lebanon (ceasefire collapsed Mar 1), and ongoing Gaza operations. Military spending has surged to 8.8% of GDP, second-highest globally. The economy faces headwinds from reserve mobilization and tourism collapse, but US military aid and a resilient tech sector provide offsets. The shekel is weakening in orderly fashion with Bank of Israel defending using reserves. A March 31 budget deadline could trigger government dissolution if not met.",
        "key_changes_this_week": [
            "Launched joint strikes on Iran with US -- Operation Roaring Lion ongoing since Feb 28",
            "Hezbollah broke November 2024 ceasefire on Mar 1, opening northern front with rocket attacks",
            "IRGC retaliatory missile hit road in West Jerusalem -- first direct Iranian strike on Israeli soil",
            "Military spending surged to 8.8% of GDP; defense sector booming",
            "US-Israel alliance deepened significantly through joint operations",
            "Budget deadline Mar 31 could trigger government dissolution"
        ],
        "outlook": "Multi-front war will strain the economy but is unlikely to cause collapse given US financial and military backstop. Defense spending will remain elevated. Tech sector fundamentals are intact but FDI decisions are paused. Political stability depends on war outcomes and budget resolution by March 31.",
        "investor_implications": "Elevated risk but investable for risk-tolerant investors with a 2+ year horizon. Defense sector is a strong overweight. Tech sector FDI pause likely temporary -- fundamentals intact for post-conflict recovery. Shekel depreciation orderly, not disorderly. Government bonds under pressure from fiscal expansion but not crisis-level given US backing.",
        "data_quality_note": "Military situation rapidly evolving. Economic data lags conflict developments. Budget projections uncertain given wartime supplementals."
    },

    "USA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "The United States is prosecuting Operation Epic Fury against Iran while navigating a constitutional crisis over trade policy. SCOTUS struck down IEEPA tariffs 6-3 on Feb 20, forcing a shift to 15% Section 122 surcharges (effective immediately) plus 10% additional on China (Mar 4). The oil shock from Hormuz closure is pushing inflation higher (Brent +36% YTD, gasoline up 12 cents/gallon in one day). The Fed is on hold at 3.50-3.75% facing a stagflation dilemma. Texas and North Carolina primaries on Mar 3 showed anti-incumbent sentiment as midterm season begins.",
        "key_changes_this_week": [
            "Launched Operation Epic Fury on Iran (Feb 28) -- strikes to continue for weeks per Trump",
            "SCOTUS struck down IEEPA tariffs 6-3; 15% Section 122 surcharge imposed; 10% additional on China Mar 4",
            "Brent crude +36% YTD; gasoline spiked 12 cents/gallon in one day -- largest in 4 years",
            "Companies suing for $134B+ in tariff refunds following SCOTUS ruling",
            "Texas and North Carolina primaries show anti-incumbent sentiment (Mar 3)",
            "New START treaty expired without extension -- nuclear arms control framework collapsed"
        ],
        "outlook": "GDP growth faces mild headwinds from oil shock and tariff uncertainty, but recession is not the base case given labor market strength and domestic energy production. Inflation re-acceleration is the primary risk, likely keeping the Fed on hold through mid-2026. Political uncertainty elevated across trade policy, war, and midterms.",
        "investor_implications": "US remains core portfolio allocation despite elevated risk. Short duration fixed income preferred given inflation risk. Defense sector (LMT, RTX, NOC) positioned for multi-year growth. Energy producers benefit from oil price surge. Dollar strength benefits importers but hurts EM borrowers and US exporters. $134B tariff refund litigation creates corporate uncertainty.",
        "data_quality_note": "Economic data solid. Trade policy framework in flux following SCOTUS ruling. War cost estimates preliminary."
    },

    "KOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "South Korea suffered its worst equity market day in history on Mar 4, with KOSPI plunging 12.1%. Samsung fell 12% and SK Hynix 10%. The crash exposed Korea's critical vulnerability: 70% of oil imports transit the now-closed Strait of Hormuz. The political risk premium doubled from 60 to 120 bps. The won is under heavy depreciation pressure. Supply chain chokepoint exposure has been raised to 0.88, among the highest for any developed economy. BOK emergency measures are under review.",
        "key_changes_this_week": [
            "KOSPI crashed 12.1% on Mar 4 -- worst single-day decline in history",
            "Samsung Electronics -12%, SK Hynix -10% in single session",
            "Political risk premium doubled from 60 to 120 bps",
            "Supply chain chokepoint exposure raised to 0.88 reflecting Hormuz dependency",
            "Won under heavy depreciation pressure; BOK emergency measures under review",
            "70% oil import dependency via Hormuz exposed as critical structural vulnerability"
        ],
        "outlook": "Recession risk has risen sharply. Korea's structural energy dependency on Middle East oil creates an acute near-term vulnerability that strategic petroleum reserves can only partially mitigate. Semiconductor export demand adds additional uncertainty. The government will likely deploy fiscal stimulus but constrained by already elevated bond yields (10yr at 3.65%).",
        "investor_implications": "Korean assets face significant near-term headwinds. KOSPI recovery depends on Hormuz resolution timeline. Semiconductor sector fundamentals intact but sentiment-driven selling may continue. Won depreciation creates opportunities for USD-based investors if Hormuz reopens. Energy security reform will be a structural investment theme. Current account deterioration acute due to surging oil import bill.",
        "data_quality_note": "Market data real-time. Energy dependency calculations based on trade flow data. Strategic petroleum reserve drawdown timeline uncertain."
    },

    "JPN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Japan faces a dual shock: oil prices surging from Hormuz closure (Japan imports ~90% of energy) and China's rare earth export ban targeting 50 Japanese companies. The Nikkei fell 3.6%. PM Takaichi's LDP secured a supermajority (352/465 seats), providing the strongest political mandate in decades for defense expansion toward 2% GDP. Japan-China relations are at their worst point in decades following Takaichi's Taiwan defense comments. The yen weakened to 157.64 amid safe-haven dollar flows.",
        "key_changes_this_week": [
            "Nikkei 225 fell 3.6% on Iran crisis and China sanctions spillover",
            "China banned rare earth and dual-use exports to Japan -- 50 companies sanctioned (effective Jan 6)",
            "PM Takaichi LDP won supermajority with 352/465 lower house seats (Feb 9 election)",
            "Defense spending trajectory to 2% GDP accelerated with strong mandate",
            "Japan-China relations at worst point in decades -- Tokyo issued formal protest",
            "Yen weakened to 157.64; energy import bill surging on oil shock"
        ],
        "outlook": "Political stability has improved significantly with the Takaichi supermajority, but economic headwinds are intensifying. Energy shock and rare earth supply disruption will pressure manufacturing margins and GDP growth. Defense spending growth is now a structural multi-year trend. BOJ rate normalization path is complicated by the energy shock. Watch for BOJ intervention near 160 yen.",
        "investor_implications": "Japan remains a core developed-market allocation. Defense industrials are a strong overweight given supermajority mandate. Rare earth diversification companies benefit from China ban. Energy-intensive manufacturers face margin pressure. Yen weakness creates hedging considerations for foreign investors. Semiconductor investment (TSMC fabs) continues as structural positive.",
        "data_quality_note": "Economic data solid. Rare earth supply chain impact still being quantified. Defense budget details pending Diet approval."
    },

    "SAU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Saudi Arabia faces an existential challenge to its economic model as Hormuz closure blocks approximately 90% of oil export routes. Despite Brent surging to $82.76, the Kingdom cannot deliver most of its production to market -- the East-West pipeline provides only 5M bpd capacity. IRGC struck Saudi-proximate US military installations. Vision 2030 timelines are disrupted. The riyal peg is holding with substantial reserves but prolonged closure would test sustainability.",
        "key_changes_this_week": [
            "Hormuz closure blocks ~90% of Saudi oil export routes despite $82.76 Brent price",
            "East-West pipeline capacity of 5M bpd only partially offsets Hormuz blockage",
            "IRGC attacks struck bases on or near Saudi territory",
            "Vision 2030 investment timelines disrupted by regional war",
            "Political stability strained by proximity to conflict and economic model risk",
            "US-Saudi partnership deepened significantly through shared Iran threat"
        ],
        "outlook": "The near-term economic outlook has deteriorated sharply despite high oil prices. Volume collapse from Hormuz closure means revenues decline even as prices rise. Fiscal reserves and sovereign wealth provide a substantial buffer but not indefinite. Resolution of Hormuz crisis is critical. Vision 2030 diversification thesis gains urgency as oil export vulnerability is exposed.",
        "investor_implications": "Saudi sovereign risk elevated but manageable given low debt (26% GDP) and massive reserves. Riyal peg stable near-term but watch for stress signals if crisis extends past Q2. Vision 2030 project delays likely but long-term thesis intact. FDI pipeline paused pending conflict resolution. Defense spending justified and increasing.",
        "data_quality_note": "Oil export volume data uncertain during Hormuz crisis. East-West pipeline utilization estimates approximate. Fiscal reserve drawdown pace unclear."
    },

    "ARE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "The UAE is under direct Iranian missile attack -- IRGC struck Al Dhafra Air Base and launched missiles at Dubai and Abu Dhabi. Aviation has been severely disrupted with 7,700+ delays and 2,280 cancellations. Hormuz closure blocks oil and LNG exports (76% chokepoint exposure), though Fujairah terminal outside the strait provides some flexibility. The UAE closed its Tehran embassy. Despite the crisis, the UAE's diversified economy and substantial sovereign wealth reserves position it as the most resilient Gulf state.",
        "key_changes_this_week": [
            "IRGC struck Al Dhafra Air Base with missiles; Dubai and Abu Dhabi targeted",
            "7,700+ flight delays and 2,280 cancellations from aviation disruption",
            "UAE closed Tehran embassy -- diplomatic relations severed",
            "Hormuz closure blocks 76% of trade routes; Fujairah provides partial alternative",
            "Tourism and financial services sectors severely impacted by regional instability",
            "FDI and trade openness trends shifted to decrease/strong_decrease"
        ],
        "outlook": "The UAE is better positioned than Gulf peers to weather the crisis thanks to economic diversification, Fujairah export alternative, and ADIA sovereign wealth. However, direct missile strikes on territory represent an unprecedented escalation. Expat flight risk is the primary domestic concern. Recovery will be faster than peers once Hormuz reopens given institutional strength and trade hub infrastructure.",
        "investor_implications": "UAE remains the most investable Gulf state with a diversification premium over peers. Dirham peg is stable with massive reserves. Real estate and tourism face near-term headwinds from conflict proximity but structural demand intact. FDI pause likely temporary. Abu Dhabi sovereign credit remains investment-grade despite crisis.",
        "data_quality_note": "Aviation disruption data real-time. Trade flow estimates uncertain during Hormuz closure. Expat demographic movements not yet quantified."
    },

    "CHN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "China faces a decelerating economy (GDP trend from 4.8% to 4.2%) compounded by escalating trade conflicts on two fronts. An additional 10% US tariff takes effect Mar 4, while China itself sanctioned 50 Japanese companies and imposed rare earth export controls in response to PM Takaichi's Taiwan remarks. CPI is at 0% signaling deflation risk. FDI inflows continue to decline. The NPC opens Mar 5 to set economic direction. Oil import costs are rising from Hormuz disruption but China is diversifying away from Gulf sources.",
        "key_changes_this_week": [
            "Additional 10% US tariff on China effective Mar 4 on top of existing duties",
            "China sanctioned 50 Japanese companies and imposed rare earth export ban",
            "GDP growth decelerating from 4.8% to 4.2% trend with deflation risk (CPI 0%)",
            "FDI trend decrease as foreign investment continues to withdraw",
            "NPC opening Mar 5 -- key policy direction for economic stimulus expected",
            "Oil import supply chain disrupted by Hormuz closure; diversifying away from Gulf"
        ],
        "outlook": "Growth deceleration continues as trade fragmentation intensifies on multiple fronts. The NPC will likely signal additional stimulus measures. Rare earth weaponization against Japan marks a significant escalation in China's willingness to use economic coercion, potentially inviting counter-measures. Deflation risk is the most underappreciated macro vulnerability. US tariff trajectory creates persistent headwind.",
        "investor_implications": "China growth deceleration warrants caution on cyclical sectors. NPC stimulus measures may provide selective upside. Rare earth producers benefit from supply restriction premium. Onshore consumer plays are more insulated than export-dependent sectors. Yuan under modest pressure but PBOC has tools to manage depreciation. Bond market offers value given deflationary backdrop.",
        "data_quality_note": "GDP data subject to revision. CPI methodology questions persist. Trade flow data increasingly fragmented by sanctions and controls."
    },

    "DEU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Germany faces renewed energy cost pressure from the Hormuz oil shock (DAX -4.1%) while shouldering an increasing share of Ukraine defense funding as the sole European funder after US aid suspension. Defense spending has surged 12.6%, meeting NATO's 2% GDP target. GDP growth remains anemic at 0.5% with manufacturing under pressure from rising energy costs and global trade contraction. The ECB is on hold despite growth weakness, caught in the same stagflation dilemma as other central banks.",
        "key_changes_this_week": [
            "DAX fell 4.1% on Iran crisis and energy cost fears",
            "Oil shock raising energy costs for manufacturing-heavy economy (30% energy independence)",
            "Defense spending surged 12.6%, meeting NATO 2% GDP target for first time",
            "Europe now sole funder of Ukraine defense after US aid suspension",
            "ECB on hold despite growth weakness -- stagflation dilemma deepening",
            "EU-US trade deal postponed amid tariff uncertainty"
        ],
        "outlook": "Germany navigates multiple structural challenges: energy transition costs, defense spending expansion, and Ukraine burden-sharing. The Merz government has political capital from its honeymoon period and cross-party defense consensus. Manufacturing recession risk is rising from energy costs. Defense industry (Rheinmetall) is a structural growth story. The 5% NATO spending target by 2035 signals a decade-long defense spending uptrend.",
        "investor_implications": "Germany remains a core European allocation despite headwinds. Defense industrials are a structural overweight. Energy-intensive manufacturers face margin compression. Bunds may benefit from ECB hold and flight-to-quality within eurozone. Infrastructure investment fund provides medium-term fiscal stimulus. Export sector faces headwinds from US tariffs and China slowdown.",
        "data_quality_note": "Economic data reliable. Defense spending projections based on NATO commitments. Ukraine funding burden estimates evolving."
    },

    "GBR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "The UK equity market sold off with FTSE -3.44% as the Iran crisis drives oil-related inflation fears. Gilt yields rose to 4.30%, tightening financial conditions. The Starmer government faces mounting economic challenges including the oil shock, higher gilt yields, and divided public opinion on the US-Israel operations. Military spending exceeds NATO's 2% target with Royal Navy assets deployed in the Gulf. The Bank of England faces a difficult growth-inflation tradeoff with CPI at 2.8% trending higher.",
        "key_changes_this_week": [
            "FTSE 100 fell 3.44% on Iran crisis selloff",
            "Gilt yields rose to 4.30% tightening financial conditions",
            "Oil shock driving inflation re-acceleration risk (CPI 2.8% trending higher)",
            "Military spending exceeds NATO 2% with Royal Navy Gulf deployment",
            "BOE faces stagflation dilemma -- rate cuts likely delayed",
            "Anti-war sentiment growing domestically over Iran operations"
        ],
        "outlook": "UK faces stagflation risk as oil-driven inflation meets slowing growth. BOE will likely hold rates, prolonging tight financial conditions. Defense spending growth is secured as a structural theme. Brexit-related trade friction continues to limit upside. Political stability is adequate but under pressure from multiple crises.",
        "investor_implications": "UK equities offer value after selloff for long-horizon investors. Gilt yields at 4.30% attractive for income but inflation risk persists. Sterling under modest pressure vs dollar. Defense sector benefits from NATO commitment. Financial sector faces headwinds from higher-for-longer rates and economic uncertainty.",
        "data_quality_note": "Economic data reliable. BOE policy guidance evolving with oil shock. Defense deployment costs not fully disclosed."
    },

    "RUS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Russia's war economy shows increasing strain in its fifth year. GDP growth has slowed to 0.6% with 9% inflation and a central bank rate at 21% that is crushing civilian economic activity. Defense spending consumes 7.1% of GDP. The military launched a record 1,720+ drones in late February while Ukraine's Flamingo missiles struck Russian Caspian oil infrastructure. Kadyrov's health deterioration adds Chechnya succession uncertainty. Comprehensive Western sanctions continue with no resolution in sight.",
        "key_changes_this_week": [
            "Record 1,720+ drones launched in late February escalation",
            "Ukraine struck Russian Caspian oil infrastructure with Flamingo missiles",
            "GDP trend decrease (0.6%) with inflation at 9% and central bank rate at 21%",
            "Defense spending at 7.1% of GDP straining civilian economy",
            "Kadyrov health deterioration adds Chechnya succession risk",
            "NR credit rating; comprehensive Western sanctions persist"
        ],
        "outlook": "War economy model is unsustainable at current intensity. 21% interest rates are destroying civilian investment. Ukraine's ability to strike oil infrastructure creates a new strategic vulnerability. Kadyrov succession could destabilize North Caucasus. No ceasefire negotiations visible. Oil price surge provides some revenue relief but export routes partially constrained by sanctions.",
        "investor_implications": "Russia remains uninvestable for Western capital due to comprehensive sanctions and NR credit rating. Ruble stability depends on oil revenue and capital controls. Defense sector dominates economic activity. Civilian sector contracting under 21% rates. Secondary sanctions risk applies to any intermediary transactions. Long-term reconstruction opportunity exists post-conflict but timeline unknown.",
        "data_quality_note": "Russian economic data increasingly unreliable. Defense spending likely understated. Casualty and military equipment data from OSINT with significant uncertainty."
    },

    "UKR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Ukraine's war enters its fifth year with CC/Ca credit rating and 2,250 bps political risk premium, but GDP shows resilient 2% growth. Ukrainian forces gained territory in February, pushing back Russian advances in Zaporizhzhia. Flamingo missiles successfully struck Russian Caspian oil infrastructure. Europe is now the sole defense funder after US aid suspension, with Ukraine requesting $60B for 2026. IMF $8.1B loan anchors a $136.5B international support package.",
        "key_changes_this_week": [
            "Ukrainian forces gained territory in Zaporizhzhia in February advances",
            "Flamingo missiles struck Russian Caspian oil infrastructure -- new strategic capability",
            "Russia launched record 1,720+ drones in late February escalation",
            "Europe now sole defense funder after US aid suspension; $60B requested for 2026",
            "IMF $8.1B loan anchoring $136.5B support package",
            "GDP growth at 2% showing economic resilience despite ongoing war"
        ],
        "outlook": "Ukraine's military position has modestly improved with territorial gains and new strike capabilities. Economic resilience at 2% GDP growth is notable. However, dependence on European funding creates vulnerability if EU political dynamics shift. War continues with no ceasefire in sight. Reconstruction opportunity is massive but requires conflict resolution.",
        "investor_implications": "Ukraine sovereign bonds trade at deep distress levels reflecting CC/Ca rating. Reconstruction theme is the primary investment case but requires ceasefire. IMF program provides institutional anchor. Agricultural sector is the most resilient economic segment. Hryvnia managed by NBU with limited market access. Risk-tolerant investors may find value in deeply discounted sovereign paper with long time horizons.",
        "data_quality_note": "Economic data surprisingly robust given wartime conditions. IMF monitoring provides validation. Military situation from OSINT. European funding commitments subject to political risk."
    },

    "PAK": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Pakistan declared open war on Afghanistan on Feb 27, launching airstrikes on Kabul and Kandahar. This nuclear-armed nation simultaneously faces protests over Iran strikes (20 killed), sovereign credit at CCC+/Caa1, and a deteriorating fiscal position. GDP trend is strong_decrease with inflation surging and debt growing rapidly. Political stability has collapsed to -1.93 with compounding domestic instability from the Afghanistan conflict and public unrest.",
        "key_changes_this_week": [
            "Declared open war on Afghanistan -- airstrikes on Kabul and Kandahar (Feb 27)",
            "20 killed in domestic protests over Iran strikes compounding instability",
            "Political stability collapsed to -1.93 (strong_decrease)",
            "GDP trend strong_decrease; inflation strong_growth; debt strong_growth",
            "Sovereign credit at CCC+/Caa1 -- fiscal position deteriorating rapidly",
            "Nuclear-armed nation now in active conflict with deteriorating governance"
        ],
        "outlook": "Pakistan faces a convergence of crises: active war on Afghanistan, domestic unrest, fiscal deterioration, and regional spillover from Iran conflict. The military-civilian governance dynamic is under extreme strain. IMF program compliance at risk. Nuclear status adds systemic geopolitical risk. No stabilization pathway is visible in the near term.",
        "investor_implications": "Pakistan sovereign risk at extreme levels. CCC+/Caa1 rating reflects near-default fiscal trajectory. War spending will accelerate debt accumulation. FDI frozen. Rupee under significant pressure. Investors should minimize all Pakistan exposure. CPEC infrastructure investments under operational risk from conflict zones.",
        "data_quality_note": "Economic data lagging rapidly evolving military and political situation. IMF program metrics may be outdated. Conflict casualty data uncertain."
    },

    "LBN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Lebanon's fragile recovery has been shattered by Hezbollah's decision to break the November 2024 ceasefire on Mar 1, firing missiles and drones into Israel. This reopens the devastating southern front atop Lebanon's existing economic collapse. The country was already in selective default with GDP contraction, hyperinflation, and institutional breakdown. Hezbollah's entry into the Iran-Israel war makes Lebanon a direct conflict zone again with catastrophic humanitarian and economic consequences.",
        "key_changes_this_week": [
            "Hezbollah broke November 2024 ceasefire on Mar 1 -- fired missiles and drones into Israel",
            "Southern Lebanon reopened as active war front in Iran-Israel conflict",
            "Existing economic collapse compounded by new military escalation",
            "Selective default status unchanged -- recovery timeline pushed out indefinitely",
            "Humanitarian crisis deepening with new displacement from southern border",
            "Country effectively a proxy battleground in US-Israel vs Iran conflict"
        ],
        "outlook": "Catastrophic. Lebanon faces the worst possible scenario: renewed high-intensity conflict layered on top of unresolved economic collapse. Reconstruction and recovery timelines are pushed out by years. Political dysfunction prevents any effective crisis response. The country is entirely dependent on international humanitarian aid.",
        "investor_implications": "Lebanon is uninvestable. Sovereign bonds in default with recovery values negligible in current scenario. Banking sector frozen. Real economy destroyed. No asset class offers acceptable risk-return. The conflict will deepen existing losses for any remaining creditors.",
        "data_quality_note": "Lebanon economic data is extremely unreliable given institutional collapse. Conflict situation from real-time OSINT. No credible fiscal or monetary data available."
    },

    # ===================== MEDIUM PRIORITY (3-4 sentences) =====================

    "FRA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "France faces renewed inflationary pressure from the oil shock as the Iran crisis disrupts energy supply chains. The CAC 40 sold off with European peers. Defense spending meets NATO 2% and France bears increased Ukraine defense burden as sole European funder alongside Germany. Macron's political position remains contested domestically but France's independent nuclear deterrent and military projection capability maintain strategic relevance.",
        "key_changes_this_week": [
            "European equity selloff from Iran crisis hitting CAC 40",
            "Oil shock driving inflation re-acceleration risk",
            "NATO 2% defense spending target met; increased Ukraine funding burden",
            "ECB on hold complicating growth outlook"
        ],
        "outlook": "Growth faces energy cost headwinds while defense spending provides partial fiscal offset. ECB hold prolongs tight conditions. France's military role in European security architecture is increasing.",
        "investor_implications": "French equities offer value post-selloff. Defense sector (Thales, Dassault) benefits from NATO spending surge. OAT spreads stable. Consumer sector faces oil-driven margin pressure.",
        "data_quality_note": "Data reliable. ECB policy guidance evolving."
    },

    "ITA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Italy faces headwinds from the oil shock given high energy import dependency and elevated public debt (140%+ GDP). European equity selloff impacted the FTSE MIB. NATO 2% defense spending target adds fiscal pressure. ECB hold limits monetary policy flexibility. However, tourism recovery and EU recovery fund disbursements provide partial offsets.",
        "key_changes_this_week": [
            "European equity selloff from Iran crisis",
            "Oil shock raising energy costs for import-dependent economy",
            "NATO 2% defense target adding fiscal pressure on high-debt economy",
            "ECB on hold limiting policy flexibility"
        ],
        "outlook": "Italy navigates between energy shock headwinds and structural reform benefits from EU recovery fund. Fiscal sustainability remains the key long-term vulnerability. BTP spread risk could re-emerge if oil shock persists.",
        "investor_implications": "BTP spreads warrant monitoring. Energy cost pressure on manufacturing. Tourism sector relatively resilient. Defense spending growth benefits Italian defense firms.",
        "data_quality_note": "Data reliable."
    },

    "IND": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "India faces significant headwinds from the oil shock as a major energy importer dependent on Middle East supplies. The Hormuz closure directly impacts India's oil and LNG import routes. However, India's diversified economy, strong domestic demand, and willingness to purchase discounted Russian oil provide partial buffers. The rupee is under pressure from energy import costs and safe-haven dollar demand.",
        "key_changes_this_week": [
            "Oil shock raising energy import costs significantly -- Hormuz dependency elevated",
            "Rupee under pressure from energy costs and dollar strength",
            "RBI faces inflation-growth tradeoff from oil price surge",
            "Diversified supply sources (Russian oil discounts) provide partial buffer"
        ],
        "outlook": "GDP growth trajectory moderating from energy cost headwinds but India remains among the fastest-growing large economies. Current account deficit will widen. RBI likely on hold. Domestic consumption story intact.",
        "investor_implications": "India growth premium narrows on energy shock but structural story intact. IT services sector insulated from oil shock. Current account deficit widening warrants rupee hedging. Domestic consumption plays preferred over energy-intensive industry.",
        "data_quality_note": "Data reliable. Oil import costs evolving rapidly."
    },

    "BRA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Brazil is a primary beneficiary of the Hormuz crisis as a net oil exporter with geographically insulated Atlantic export routes. Oil price surge boosts Petrobras revenue and fiscal position. Real strength from commodity tailwinds. Brazil is positioned as an alternative supplier for Asian buyers seeking non-Hormuz oil sources.",
        "key_changes_this_week": [
            "Net oil exporter benefiting from oil price surge (Brent +36% YTD)",
            "Atlantic export routes fully insulated from Hormuz closure",
            "Petrobras revenue outlook improved significantly",
            "Positioned as alternative oil supplier for Asian markets"
        ],
        "outlook": "Brazil is one of the few large economies benefiting from current geopolitical dynamics. Oil revenue windfall could reduce fiscal deficit pressure. Agricultural exports also benefit from supply chain rerouting. The key risk is domestic political noise around fiscal policy.",
        "investor_implications": "Brazil is an overweight candidate in current environment. Petrobras benefits directly from oil price surge. Real supported by commodity tailwinds. Fixed income offers high real yields. Risk: domestic fiscal policy uncertainty could limit benefit realization.",
        "data_quality_note": "Data reliable. Oil production and export data current."
    },

    "TUR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Turkey faces dual pressures from 34.9% inflation amid an aggressive 47.5% central bank rate and proximity to the Iran conflict. Istanbul mayor Imamoglu's imprisonment signals deepening opposition suppression. However, Turkey is positioning as a potential mediator in the Iran crisis and Erdogan succession dynamics are emerging. Oil price surge adds import cost pressure but transit fees for alternative routes could benefit.",
        "key_changes_this_week": [
            "Inflation at 34.9% with central bank rate at 47.5% aggressively targeting disinflation",
            "Istanbul mayor Imamoglu imprisoned -- opposition suppression deepening",
            "Regional proximity to Iran conflict elevating risk premium",
            "Potential mediator role in Iran crisis could enhance diplomatic standing"
        ],
        "outlook": "Disinflation trend is the key positive. Political risk from opposition crackdown is the key negative. Turkey's geographic position makes it both vulnerable to and potentially a beneficiary of the regional crisis. Erdogan succession dynamics will dominate medium-term political outlook.",
        "investor_implications": "Lira carry trade attractive at 47.5% but political risk elevated. Disinflation momentum is positive if sustained. Equity valuations cheap but governance discount warranted. Sovereign credit under pressure from political risk.",
        "data_quality_note": "Inflation methodology questions persist. Political risk assessment evolving."
    },

    "MEX": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Mexico faces 25% US tariffs effective Mar 4 with auto imports exempted until April. USMCA coverage provides partial shield. GDP trend shows growth (1% to 1.5%) resilience. Oil price surge benefits Pemex. The judicial reform undermining rule of law continues to deter foreign investment. Peso under pressure from tariff uncertainty.",
        "key_changes_this_week": [
            "25% US tariffs effective Mar 4; auto imports exempted until April",
            "USMCA coverage provides partial exemption shield",
            "Oil price surge benefiting Pemex revenue",
            "Judicial reform continues to undermine investment confidence"
        ],
        "outlook": "Near-term tariff shock is manageable given USMCA exemptions but creates uncertainty. Nearshoring thesis faces headwinds from judicial reform concerns. Oil revenue provides fiscal buffer. Resolution of tariff framework is critical for investment outlook.",
        "investor_implications": "Mexican assets face tariff-driven volatility. Peso hedging recommended. Nearshoring plays require clarity on judicial reform impact. Pemex benefits from oil surge but operational challenges persist.",
        "data_quality_note": "Trade data evolving rapidly with tariff changes. Judicial reform impact on FDI being quantified."
    },

    "IDN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Indonesia faces moderate headwinds from the oil shock as a net energy importer with some domestic production offset. The rupiah is under pressure from safe-haven dollar demand. Domestic consumption story remains intact. Indonesia benefits from supply chain diversification trends as companies reduce China concentration.",
        "key_changes_this_week": [
            "Oil shock raising energy import costs moderately",
            "Rupiah under pressure from dollar strength",
            "Supply chain diversification beneficiary as firms reduce China exposure",
            "Domestic consumption fundamentals intact"
        ],
        "outlook": "Indonesia's large domestic economy provides resilience against external shocks. Oil price impact is moderate given partial domestic production. Supply chain diversification from China benefits Indonesian manufacturing. Growth trajectory modestly lower but intact.",
        "investor_implications": "Indonesia offers defensive positioning in Southeast Asia. Domestic consumption plays preferred. Commodity exposure (palm oil, nickel) provides diversification. Rupiah hedging recommended.",
        "data_quality_note": "Data reliable."
    },

    "ZAF": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "South Africa announced a landmark R1 trillion (~$62B) infrastructure plan over three years, with the 2026 budget marking the first time in 17 years that debt is stabilizing and deficit narrowing. Gold price surge to $5,413/oz benefits South Africa's mining sector significantly. The rand should benefit from both commodity tailwinds and improved fiscal signaling.",
        "key_changes_this_week": [
            "R1 trillion infrastructure plan announced over 3 years in 2026 budget",
            "First time in 17 years debt stabilizing and deficit narrowing",
            "Gold at $5,413/oz record benefits mining sector significantly",
            "Fiscal improvement signal positive for sovereign creditworthiness"
        ],
        "outlook": "South Africa's fiscal trajectory has meaningfully improved. Gold windfall provides revenue upside. Infrastructure spending should boost growth. Loadshedding improvements continue. The key risk is implementation capacity and ANC coalition dynamics.",
        "investor_implications": "South African assets offer improving risk-reward. Gold miners benefit from record prices. Rand supported by commodity tailwinds and fiscal improvement. Government bonds attractive on improving fiscal trajectory. Infrastructure-linked equities positioned for multi-year spending cycle.",
        "data_quality_note": "Budget data from official government announcements. Infrastructure implementation track record historically weak."
    },

    "POL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Poland continues its defense spending expansion, now among NATO's highest spenders relative to GDP. The Ukraine front-line proximity maintains elevated security spending. Oil shock adds inflationary pressure but Poland's energy diversification (Baltic Pipe, LNG) reduces vulnerability versus 2022. EU fund disbursements continue supporting growth.",
        "key_changes_this_week": [
            "NATO 2% defense target met with Poland exceeding at ~4% GDP",
            "Oil shock adds moderate inflationary pressure",
            "Energy diversification (Baltic Pipe, LNG) reduces Hormuz vulnerability",
            "EU fund disbursements supporting growth"
        ],
        "outlook": "Poland is a structural defense spending beneficiary and NATO front-line state. Economic fundamentals remain solid with EU convergence support. Energy diversification from Russian/ME dependency continues.",
        "investor_implications": "Polish defense sector benefits from NATO spending surge. PLN stable within EU convergence framework. Government bonds offer carry. Energy security investments are a multi-year theme.",
        "data_quality_note": "Data reliable."
    },

    "AUS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Australia is a beneficiary of the Hormuz crisis as an LNG exporter with prices surging on Qatari supply disruption, and a gold producer benefiting from record $5,413/oz prices. The Australian dollar should benefit from commodity tailwinds. Defense spending is increasing in line with AUKUS commitments and regional security concerns from China-Japan tensions.",
        "key_changes_this_week": [
            "LNG export premiums surging as Qatari supply disrupted by Hormuz closure",
            "Gold mining sector benefits from record $5,413/oz prices",
            "Defense spending increasing under AUKUS commitments",
            "Regional security concerns elevated by China-Japan sanctions escalation"
        ],
        "outlook": "Australia is well-positioned as a commodity beneficiary of current geopolitical dynamics. LNG and gold provide dual revenue tailwinds. AUKUS defense integration continues. China trade relations remain the key structural risk.",
        "investor_implications": "Australian resource sector is a strong overweight. LNG producers benefit from Qatari disruption premium. Gold miners at record profitability. AUD supported by commodity tailwinds. Defense industrials benefit from AUKUS spending.",
        "data_quality_note": "Data reliable. LNG pricing evolving rapidly."
    },

    "CAN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Canada faces 25% US tariffs effective Mar 4 but benefits from oil price surge as a major energy exporter. GDP trend shows growth (1.2% to 1.5%) resilience. USMCA exemptions provide partial tariff shield. The Canada-US bilateral relationship is under significant strain. Energy sector is the clear beneficiary as non-Hormuz Atlantic/Pacific routes provide secure export channels.",
        "key_changes_this_week": [
            "25% US tariffs effective Mar 4; USMCA exemptions provide partial shield",
            "Energy sector benefits from oil price surge with secure export routes",
            "Canada-US bilateral relationship under significant strain",
            "GDP showing resilience at 1.2-1.5% growth trajectory"
        ],
        "outlook": "Energy windfall partially offsets tariff headwinds. Canada's secure oil export infrastructure (not Hormuz-dependent) positions it as a premium supplier. US relationship strain is the key political risk. BOC likely on hold given mixed macro signals.",
        "investor_implications": "Canadian energy sector is an overweight. CAD supported by oil prices. Banks face moderate headwinds from trade uncertainty. Government bonds offer quality. Tariff resolution critical for non-energy sectors.",
        "data_quality_note": "Data reliable. Tariff impact estimates preliminary."
    },

    "NOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Norway is the primary European beneficiary of the Hormuz crisis as a North Sea oil and gas producer with non-Hormuz export routes. Energy revenues are surging, boosting the sovereign wealth fund (Government Pension Fund Global). European demand for Norwegian gas is increasing as LNG supply from Qatar is disrupted. The krone should benefit from energy tailwinds.",
        "key_changes_this_week": [
            "North Sea oil and gas revenues surging on Brent +36% YTD",
            "Non-Hormuz export routes provide secure energy delivery to Europe",
            "Sovereign wealth fund benefiting from energy windfall",
            "European gas demand shifting to Norwegian supply as Qatari LNG disrupted"
        ],
        "outlook": "Norway is structurally positioned to benefit from prolonged energy disruption. Sovereign wealth fund accumulation accelerates. European energy dependency on Norwegian supply deepens. Defense spending meets NATO 2% target.",
        "investor_implications": "Norwegian energy sector is a strong overweight. NOK benefits from energy tailwinds. Sovereign wealth fund growth accelerates. Equinor and peers positioned for multi-quarter earnings beats.",
        "data_quality_note": "Data reliable. Energy production and pricing data current."
    },

    "KWT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Kuwait is critically exposed to the Hormuz closure with no pipeline alternative for oil exports -- near-total oil dependency on the Strait. IRGC struck Ali Al Salem Air Base directly. Low debt (7.3% GDP) provides a fiscal buffer but oil revenue disruption threatens the budget. GDP outlook has been severely downgraded from pre-crisis 3.9% forecast.",
        "key_changes_this_week": [
            "IRGC struck Ali Al Salem Air Base on Kuwaiti territory",
            "Hormuz closure blocks near-total oil export capacity -- no pipeline alternative",
            "GDP outlook severely downgraded from pre-crisis 3.9%",
            "Low debt (7.3% GDP) provides fiscal buffer but revenue disrupted"
        ],
        "outlook": "Kuwait faces the worst relative impact among Gulf states due to no pipeline alternative. Resolution of Hormuz crisis is existential for Kuwaiti fiscal sustainability. Sovereign wealth reserves provide a multi-year buffer.",
        "investor_implications": "Kuwaiti assets under severe stress from Hormuz dependency. Sovereign credit stable near-term given reserves but medium-term vulnerable. FDI and growth outlook entirely dependent on Hormuz reopening timeline.",
        "data_quality_note": "Oil export data uncertain during Hormuz closure."
    },

    "QAT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Qatar faces direct military attack (IRGC struck Al Udeid Air Base) and Hormuz closure blocking LNG exports (66% chokepoint exposure). As the world's largest LNG exporter, Qatar's inability to ship gas has global implications for energy markets. The North Field LNG expansion timeline is at risk. Current account trend has shifted to strong_decrease from a pre-crisis 17.29% surplus. GDP growth outlook severely downgraded from 6.1%.",
        "key_changes_this_week": [
            "IRGC struck Al Udeid Air Base -- direct military attack on Qatari territory",
            "Hormuz closure blocks LNG exports -- world's largest LNG exporter offline",
            "Current account trending strong_decrease from 17.29% surplus",
            "North Field LNG expansion timeline at risk from conflict"
        ],
        "outlook": "Qatar is caught between hosting a major US military base (Al Udeid) and geographic proximity to Iran. LNG export disruption has global energy implications. Fiscal reserves provide buffer but revenue collapse is severe. Resolution of Hormuz crisis critical.",
        "investor_implications": "Qatari LNG assets face near-term disruption. Sovereign credit resilient given reserves but revenue pressure acute. European gas buyers seeking alternative supply sources. Post-crisis, Qatar's LNG position strengthens as supply security becomes premium.",
        "data_quality_note": "LNG shipping data disrupted. Export volume estimates uncertain."
    },

    "OMN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Oman is critically exposed to the Hormuz closure with 62% supply chain chokepoint exposure. Oil exports are severely disrupted in what is the most severe global energy supply disruption in decades. Oman's fiscal position is more precarious than wealthier Gulf peers given smaller sovereign reserves.",
        "key_changes_this_week": [
            "Hormuz closure with 62% chokepoint exposure severely disrupts oil exports",
            "Oil revenue disrupted despite price surge -- volume collapse dominates",
            "Smaller fiscal reserves than Gulf peers reduce buffer capacity",
            "Most severe global energy supply disruption in decades affecting Omani economy"
        ],
        "outlook": "Oman is highly vulnerable to prolonged Hormuz closure given smaller reserves relative to Saudi Arabia and UAE. Fiscal consolidation progress of recent years at risk. Diversification efforts remain early-stage.",
        "investor_implications": "Omani sovereign risk elevated. Bond spreads likely widening. Revenue disruption threatens fiscal trajectory improvements. Investors should reduce Oman fixed income exposure pending Hormuz resolution.",
        "data_quality_note": "Oil export data uncertain during Hormuz closure."
    },

    "IRQ": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Iraq faces critical Hormuz chokepoint exposure at 51%, with oil exports severely disrupted. Iraq's fiscal position is almost entirely dependent on oil revenue. The country's position between Iran and US-allied Gulf states creates additional political complexity. Oil export infrastructure through Turkey (Kirkuk-Ceyhan pipeline) provides a partial alternative but capacity is limited.",
        "key_changes_this_week": [
            "Hormuz closure blocks 51% of supply chain chokepoint exposure",
            "Oil revenue severely disrupted -- fiscal position highly oil-dependent",
            "Geographic position between warring parties creates political complexity",
            "Kirkuk-Ceyhan pipeline provides limited export alternative"
        ],
        "outlook": "Iraq's fiscal sustainability is directly tied to oil export volumes. Hormuz closure creates acute near-term fiscal pressure. Turkey pipeline provides partial alternative. Political positioning between Iran and US is increasingly difficult.",
        "investor_implications": "Iraqi sovereign risk elevated from oil revenue disruption. Bond spreads likely widening. KRG oil exports via Turkey pipeline are the primary functioning revenue stream. Political risk premium elevated.",
        "data_quality_note": "Oil export data fragmented. Fiscal data lagging."
    },

    "JOR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Jordan is caught in the crossfire of the Iran-Israel conflict with IRGC strikes hitting targets in the region. As a net energy importer, Jordan faces higher oil costs without the resource wealth of Gulf neighbors. US aid and IMF support provide fiscal anchors. Refugee burden from Syria continues. Political stability is strained by regional tensions and domestic sentiment over the conflict.",
        "key_changes_this_week": [
            "Regional conflict proximity elevating risk premium",
            "Oil shock raising energy import costs for resource-poor economy",
            "IRGC strikes in region affecting security environment",
            "US aid and IMF support provide fiscal stability anchors"
        ],
        "outlook": "Jordan navigates a difficult position as a US ally in a region at war. Energy costs and refugee burden strain the budget. US aid dependency deepens. Stability depends on conflict not spilling over into Jordanian territory.",
        "investor_implications": "Jordanian sovereign risk modestly elevated by proximity to conflict. US aid dependency is a credit positive given alliance strength. Eurobonds may face spread widening. Tourism revenue at risk from regional instability.",
        "data_quality_note": "Data reliable. Security situation evolving."
    },

    "EGY": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Egypt faces dual headwinds from oil price surge (as a net importer) and continued Red Sea/Suez Canal disruption reducing transit revenue. However, Egypt is geographically positioned to benefit from rerouted shipping that avoids Hormuz and uses Suez as an alternative. LNG import costs rising. The IMF program provides fiscal anchor. Domestic political situation stable under Sisi.",
        "key_changes_this_week": [
            "Oil price surge raising energy import costs",
            "Suez Canal may benefit from Hormuz avoidance rerouting",
            "Red Sea disruption from Houthis persists affecting transit revenue",
            "IMF program provides fiscal stability anchor"
        ],
        "outlook": "Egypt's position is mixed: oil costs rise but Suez transit could benefit from Hormuz avoidance. IMF program discipline improves medium-term outlook. Pound stabilization continues. Tourism faces headwinds from regional instability.",
        "investor_implications": "Egyptian pound-denominated assets offer high yields with IMF backstop. Suez transit revenue outlook depends on Hormuz vs Red Sea dynamics. Sovereign bonds offer carry but currency risk persists.",
        "data_quality_note": "Data reliable. Suez transit revenue estimates evolving with routing changes."
    },

    # ===================== LOW PRIORITY (2-3 sentences) =====================

    "CHE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Switzerland benefits from safe-haven flows with the franc strengthening amid global risk-off. Gold price surge benefits Swiss refineries and financial sector. No significant domestic changes this week beyond Iran crisis spillover through financial markets.",
        "key_changes_this_week": [
            "Swiss franc strengthening on safe-haven demand",
            "Gold price surge benefits financial sector and refineries"
        ],
        "outlook": "Switzerland well-insulated from geopolitical crisis. Safe-haven premium intact. SNB policy accommodative.",
        "investor_implications": "CHF strength benefits domestic purchasing power but hurts exporters. Swiss gold and financial sector benefiting from risk-off environment.",
        "data_quality_note": "Data reliable."
    },

    "SGP": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Singapore faces moderate headwinds from Hormuz-driven trade disruption as a shipping hub but benefits from increased bunkering and trade rerouting activity. No significant domestic changes this week. Financial sector benefits from safe-haven capital flows into Asian financial centers.",
        "key_changes_this_week": [
            "Trade rerouting from Hormuz adds bunkering and logistics activity",
            "Financial sector benefits from safe-haven Asian capital flows"
        ],
        "outlook": "Singapore's position as a trade and financial hub provides resilience. Shipping rerouting creates near-term disruption but also opportunity.",
        "investor_implications": "Singapore REITs and financial sector relatively defensive. Shipping-related companies benefit from rerouting. SGD stable.",
        "data_quality_note": "Data reliable."
    },

    "TWN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Taiwan is the most energy-vulnerable economy in the dataset with only 5% energy independence. Hormuz closure directly impacts energy imports. GDP trend has decreased from 3.7% to 2.1%. The China-Japan sanctions escalation signals broader regional security deterioration that is directly relevant to cross-strait dynamics. TSMC operations continue normally.",
        "key_changes_this_week": [
            "Energy independence at 5% -- most vulnerable to Hormuz closure in dataset",
            "GDP trend decreased from 3.7% to 2.1%",
            "China-Japan escalation signals broader regional security risk",
            "Chokepoint exposure at 0.69"
        ],
        "outlook": "Taiwan's energy vulnerability is acute. Cross-strait risk elevated by China-Japan deterioration. TSMC strategic importance provides implicit security guarantee but does not eliminate risk.",
        "investor_implications": "TSMC remains core semiconductor allocation but energy and cross-strait risk warrant hedging. TWD under pressure from energy costs and regional risk premium.",
        "data_quality_note": "Data reliable. Cross-strait risk assessment evolving."
    },

    "THA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Thailand faces moderate headwinds from oil price surge as a net energy importer. Tourism revenue remains strong. No significant domestic political changes this week. Baht under modest pressure from dollar strength and energy costs.",
        "key_changes_this_week": [
            "Oil price surge raising energy import costs moderately",
            "Tourism sector continues strong performance"
        ],
        "outlook": "Thailand's domestic economy provides resilience. Tourism recovery continues. Oil shock is the primary near-term headwind.",
        "investor_implications": "Thai tourism and domestic consumption plays remain attractive. Energy import costs warrant monitoring. Baht hedging recommended for foreign investors.",
        "data_quality_note": "Data reliable."
    },

    "MYS": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Malaysia benefits modestly from the oil price surge as a net energy exporter (oil and LNG). Petronas revenues improve. No significant domestic changes this week. Ringgit relatively stable given commodity support.",
        "key_changes_this_week": [
            "Oil and LNG price surge benefits Petronas and fiscal position",
            "Ringgit supported by commodity tailwinds"
        ],
        "outlook": "Malaysia's energy export position provides cushion. Semiconductor supply chain role adds structural relevance. Domestic politics stable.",
        "investor_implications": "Malaysian energy sector benefits from price surge. Ringgit supported by oil. Semiconductor-linked plays attractive.",
        "data_quality_note": "Data reliable."
    },

    "SWE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Sweden meets NATO 2% defense spending target, a historic shift. Oil shock adds moderate inflationary pressure. No significant domestic changes this week beyond European-wide Iran crisis spillover. Defense sector benefits from NATO spending surge.",
        "key_changes_this_week": [
            "NATO 2% defense spending target met -- historic for Sweden",
            "European equity selloff from Iran crisis"
        ],
        "outlook": "Sweden's defense spending shift is structural. Economy faces moderate energy cost headwinds. Krona stable within European context.",
        "investor_implications": "Swedish defense industrials (Saab) benefit from NATO spending surge. Krona stable. No major positioning changes needed.",
        "data_quality_note": "Data reliable."
    },

    "NGA": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Nigeria faces a security crisis (Boko Haram massacre killed 170+), 23% inflation, and NLC labor protests. Sovereign credit at CCC+/Caa1. Oil price surge benefits export revenue but domestic refining capacity constraints limit pass-through. Naira under continued pressure.",
        "key_changes_this_week": [
            "Boko Haram massacre killed 170+ -- security crisis deepening",
            "Inflation at 23% with NLC protests compounding instability",
            "Oil price surge benefits export revenue but limited domestic pass-through"
        ],
        "outlook": "Nigeria's security and inflation challenges persist. Oil revenue provides fiscal buffer but governance and infrastructure constraints limit development impact.",
        "investor_implications": "Nigerian sovereign risk elevated. Oil revenue benefit offset by security and governance concerns. Naira weakness likely to persist. Selective energy sector exposure only.",
        "data_quality_note": "Security and economic data from multiple sources with moderate confidence."
    },

    "KAZ": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Kazakhstan is a beneficiary of the Hormuz crisis with CPC pipeline exports to the Black Sea not Hormuz-dependent. Oil price surge provides significant revenue windfall. Tenge supported by energy tailwinds. No significant domestic political changes.",
        "key_changes_this_week": [
            "Oil price windfall from non-Hormuz CPC pipeline exports",
            "Tenge supported by energy revenue tailwinds"
        ],
        "outlook": "Kazakhstan positioned as premium oil supplier via CPC pipeline. Revenue windfall improves fiscal position. Russian transit dependency is the key infrastructure risk.",
        "investor_implications": "Kazakh energy assets benefit from oil price surge and Hormuz avoidance premium. Tenge stable. Sovereign credit improving.",
        "data_quality_note": "Data reliable."
    },

    "AZE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Azerbaijan benefits from the Hormuz crisis with BTC (Baku-Tbilisi-Ceyhan) pipeline exports to the Mediterranean secure and not Hormuz-dependent. Oil and gas revenue windfall significant. No significant domestic changes.",
        "key_changes_this_week": [
            "BTC pipeline to Mediterranean provides secure export route",
            "Oil and gas revenue windfall from Hormuz avoidance premium"
        ],
        "outlook": "Azerbaijan positioned as alternative energy supplier for European markets. BTC pipeline route secure. Revenue windfall improves fiscal position.",
        "investor_implications": "Azerbaijani energy assets benefit from oil price surge and secure export routes. Manat stable. SOCAR and related assets attractive.",
        "data_quality_note": "Data reliable."
    },

    "ARG": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Argentina shows significant improvement under Milei reforms. Annual CPI at 41.3% but monthly inflation has decelerated dramatically to 2.9%. Senate approved landmark labor reform 42-28 on Feb 27. Political stability improving. Sovereign credit remains CCC+/Caa1 but trajectory is positive. Oil price surge benefits Vaca Muerta production.",
        "key_changes_this_week": [
            "Monthly inflation decelerated to 2.9% -- dramatic improvement",
            "Senate approved landmark labor reform 42-28 (Feb 27)",
            "Oil price surge benefits Vaca Muerta shale production"
        ],
        "outlook": "Argentina's reform trajectory is the most positive emerging market story in 2026. Disinflation momentum is strong. Structural reforms advancing. Credit upgrade cycle beginning.",
        "investor_implications": "Argentina is an upgrade candidate. Sovereign bonds offer significant spread compression potential. Vaca Muerta energy assets benefit from oil surge. Peso stabilizing under reform program.",
        "data_quality_note": "Inflation methodology questions persist. Reform implementation track record being established."
    },

    "CHL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Chile faces moderate headwinds from the oil shock as a net energy importer but copper prices are supported by supply chain concerns. No significant domestic changes this week. Lithium sector continues to attract investment.",
        "key_changes_this_week": [
            "Oil shock adds moderate energy cost headwinds",
            "Copper and lithium sectors provide structural support"
        ],
        "outlook": "Chile's commodity exposure provides mixed impact. Copper/lithium positive, oil negative. Institutional strength intact.",
        "investor_implications": "Chilean copper miners benefit from supply chain diversification trends. Lithium sector remains strategic. Peso relatively stable.",
        "data_quality_note": "Data reliable."
    },

    "COL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Colombia benefits modestly from oil price surge as a net exporter. Ecopetrol revenues improve. No significant domestic political changes this week. Peso relatively stable with commodity support.",
        "key_changes_this_week": [
            "Oil price surge benefits Ecopetrol revenue",
            "Peso supported by commodity tailwinds"
        ],
        "outlook": "Colombia's energy export position provides moderate benefit. Domestic political dynamics around Petro government are the key risk variable.",
        "investor_implications": "Colombian energy sector benefits from oil surge. Peso supported. Sovereign bonds offer carry.",
        "data_quality_note": "Data reliable."
    },

    "PER": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Peru faces moderate headwinds from oil price surge as a net importer. Copper and gold mining sectors benefit from commodity price strength. No significant domestic changes this week.",
        "key_changes_this_week": [
            "Oil price surge adds energy cost headwinds",
            "Gold at $5,413/oz benefits mining sector"
        ],
        "outlook": "Peru's mining sector provides resilience. Gold windfall particularly significant. Political stability relatively stable.",
        "investor_implications": "Peruvian gold miners benefit from record prices. Copper sector offers strategic commodity exposure. Sol relatively stable.",
        "data_quality_note": "Data reliable."
    },

    "PHL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "The Philippines faces a governance crisis from the Marcos flood control corruption scandal. House Speaker and Senate President stepped down. Third Trillion Peso March protest occurred. The Marcos-Duterte alliance has shattered. Oil price surge adds energy cost pressure as a net importer. Peso under pressure.",
        "key_changes_this_week": [
            "Marcos corruption scandal -- House Speaker and Senate President stepped down",
            "Third Trillion Peso March protest",
            "Marcos-Duterte alliance shattered"
        ],
        "outlook": "Political instability is the dominant risk. Governance crisis could deter FDI. BPO sector provides some economic resilience. Oil costs add headwind.",
        "investor_implications": "Philippines political risk elevated. FDI outlook deteriorating on governance concerns. BPO sector relatively insulated. Peso hedging recommended.",
        "data_quality_note": "Political situation evolving rapidly."
    },

    "VNM": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Vietnam faces moderate headwinds from oil price surge but benefits from supply chain diversification trends as companies continue to reduce China concentration. No significant domestic changes this week. Manufacturing sector continues to attract FDI.",
        "key_changes_this_week": [
            "Oil shock adds moderate energy cost headwinds",
            "Supply chain diversification from China continues to benefit FDI"
        ],
        "outlook": "Vietnam's manufacturing FDI pipeline remains strong. Oil cost headwinds are manageable. Growth trajectory intact.",
        "investor_implications": "Vietnam manufacturing plays remain attractive as China+1 beneficiary. FDI pipeline strong. Dong stable.",
        "data_quality_note": "Data reliable."
    },

    "BGD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Bangladesh faces headwinds from oil price surge as a net energy importer with limited fiscal buffers. Garment export sector remains the economic backbone. No significant domestic changes this week beyond oil shock transmission.",
        "key_changes_this_week": [
            "Oil shock raising energy import costs",
            "Garment export sector continues as economic anchor"
        ],
        "outlook": "Bangladesh's energy vulnerability creates near-term fiscal pressure. Garment sector provides export resilience. IMF program provides policy anchor.",
        "investor_implications": "Bangladesh sovereign risk modestly elevated by energy costs. Garment sector FDI intact. Taka under pressure.",
        "data_quality_note": "Data reliability moderate."
    },

    "GRC": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Greece is a surprise beneficiary of the Hormuz crisis as its shipping fleet profits from longer rerouted tanker voyages. Greek-owned tanker companies see elevated charter rates. Oil shock adds domestic energy cost pressure but shipping revenue windfall is significant. Tourism prospects for 2026 intact.",
        "key_changes_this_week": [
            "Greek shipping fleet profits from rerouted tanker voyages and all-time high VLCC rates",
            "Oil price surge adds domestic energy cost pressure"
        ],
        "outlook": "Greece's shipping sector windfall is material. Tourism season prospects intact. Fiscal trajectory continues improving. NATO 2% defense spending met.",
        "investor_implications": "Greek shipping companies benefit from extended voyages and elevated rates. Tourism and shipping dual tailwind. Greek bonds continue tightening vs periphery.",
        "data_quality_note": "Data reliable. Shipping revenue estimates from VLCC rate data."
    },

    "ESP": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "Spain faces moderate headwinds from the oil shock as a net energy importer. European equity selloff impacts IBEX. Tourism sector remains the key growth driver. No significant domestic changes this week beyond European-wide Iran crisis spillover.",
        "key_changes_this_week": [
            "European equity selloff from Iran crisis",
            "Oil shock adds energy cost pressure"
        ],
        "outlook": "Spain's tourism-driven growth provides resilience. Energy costs are the primary headwind. ECB hold limits policy flexibility.",
        "investor_implications": "Spanish tourism sector defensive. IBEX offers value post-selloff. Energy cost pressure on industrial sector.",
        "data_quality_note": "Data reliable."
    },

    "NLD": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "The Netherlands faces moderate headwinds from the oil shock and global trade contraction given its open, trade-dependent economy. ASML and semiconductor supply chain implications from China-Japan rare earth tensions add uncertainty. NATO 2% defense spending met. No significant domestic changes this week.",
        "key_changes_this_week": [
            "Trade-dependent economy exposed to global trade contraction",
            "ASML faces uncertainty from China-Japan rare earth tensions",
            "NATO 2% defense spending target met"
        ],
        "outlook": "Netherlands' open economy is sensitive to global trade dynamics. ASML strategic importance provides investment anchor. Defense spending growth structural.",
        "investor_implications": "ASML remains strategic semiconductor holding. Trade-dependent sectors face headwinds. Dutch bonds offer quality within eurozone.",
        "data_quality_note": "Data reliable."
    },

    "BEL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Belgium faces European-wide headwinds from oil shock and global trade contraction. NATO/EU institutional presence provides stability anchor. Defense spending meets 2% target.",
        "key_changes_this_week": [
            "European equity selloff from Iran crisis",
            "NATO 2% defense spending target met"
        ],
        "outlook": "Belgium stable within EU framework. No significant deviation from European trends.",
        "investor_implications": "Belgian OLOs offer quality within eurozone. No major positioning changes needed.",
        "data_quality_note": "Data reliable."
    },

    "ROU": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Romania benefits from NATO front-line state spending and EU fund disbursements. Oil shock adds moderate inflationary pressure. Defense spending above 2% GDP reflects proximity to Ukraine conflict.",
        "key_changes_this_week": [
            "NATO defense spending above 2% GDP maintained",
            "EU fund disbursements supporting growth"
        ],
        "outlook": "Romania's EU convergence story intact. Defense spending structural given Ukraine proximity. Energy diversification ongoing.",
        "investor_implications": "Romanian government bonds offer attractive yields within EU convergence framework. Leu relatively stable.",
        "data_quality_note": "Data reliable."
    },

    "CZE": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Czech Republic faces European-wide headwinds from oil shock affecting its export-oriented manufacturing economy. NATO 2% defense spending met. CNB policy navigating inflation-growth balance.",
        "key_changes_this_week": [
            "Oil shock adds energy cost pressure on manufacturing",
            "NATO 2% defense spending target met"
        ],
        "outlook": "Czech manufacturing sector faces energy cost headwinds. EU integration provides stability. Defense spending growth structural.",
        "investor_implications": "Czech koruna stable. Government bonds offer quality within CEE. Manufacturing sector faces near-term headwinds.",
        "data_quality_note": "Data reliable."
    },
}

# Additional Tier 2 countries not in tasks above that need narratives
# PRT, FIN, IRL, NZL, MAR need narratives too

ADDITIONAL_NARRATIVES = {
    "PRT": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Portugal faces European-wide headwinds from oil shock. Tourism sector remains strong. Fiscal trajectory continues improving. NATO 2% defense spending target progressing.",
        "key_changes_this_week": [
            "European equity selloff from Iran crisis",
            "Oil shock adds moderate energy cost pressure"
        ],
        "outlook": "Portugal's tourism and tech sectors provide growth resilience. Fiscal trajectory positive. EU convergence continues.",
        "investor_implications": "Portuguese government bonds continue tightening vs periphery. Tourism sector defensive.",
        "data_quality_note": "Data reliable."
    },

    "FIN": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Finland faces European-wide headwinds from oil shock. NATO membership continues to enhance security posture. Russia border management stable. Defense spending above 2% GDP.",
        "key_changes_this_week": [
            "NATO defense spending above 2% maintained",
            "Oil shock adds moderate energy cost pressure"
        ],
        "outlook": "Finland's NATO integration continues strengthening security. Economy faces energy cost headwinds but institutional strength provides resilience.",
        "investor_implications": "Finnish government bonds offer Nordic quality. Defense spending growth structural.",
        "data_quality_note": "Data reliable."
    },

    "IRL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Ireland's multinational-driven economy faces moderate headwinds from global trade contraction but tech sector presence provides resilience. Corporate tax regime continues attracting FDI.",
        "key_changes_this_week": [
            "Global trade contraction adds moderate headwinds",
            "Tech sector multinational presence provides economic anchor"
        ],
        "outlook": "Ireland's multinational tax base provides fiscal resilience. Tech sector employment stable. EU membership provides framework stability.",
        "investor_implications": "Irish government bonds offer quality within eurozone. Tech sector employment anchor stable.",
        "data_quality_note": "Data reliable."
    },

    "NZL": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. New Zealand is geographically insulated from Middle East crisis. Dairy and agricultural exports stable. NZD under modest pressure from global risk-off. RBNZ policy accommodative.",
        "key_changes_this_week": [
            "Geographic insulation from Middle East crisis",
            "NZD under modest pressure from global risk-off"
        ],
        "outlook": "New Zealand's geographic isolation provides natural hedge against Middle East crisis. Agricultural exports stable. Housing market correction ongoing.",
        "investor_implications": "NZD offers value if risk-off reverses. Agricultural sector defensive. Government bonds offer quality.",
        "data_quality_note": "Data reliable."
    },

    "MAR": {
        "ai_generated": True,
        "generated_at": GENERATED_AT,
        "run_id": RUN_ID,
        "executive_summary": "No significant country-specific changes this week. Morocco faces headwinds from oil price surge as a net energy importer. Renewable energy investments provide medium-term hedge. OCP phosphate exports stable.",
        "key_changes_this_week": [
            "Oil price surge adds energy import cost pressure",
            "Phosphate exports stable providing revenue support"
        ],
        "outlook": "Morocco's renewable energy transition provides medium-term resilience. Phosphate revenue stable. EU trade corridor functioning.",
        "investor_implications": "Moroccan sovereign risk stable. Phosphate sector benefits from food security concerns. Dirham stable under managed float.",
        "data_quality_note": "Data reliable."
    },
}

NARRATIVES.update(ADDITIONAL_NARRATIVES)


def update_country_file(code, narrative):
    """Update a single country JSON file with the new narrative."""
    filepath = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} does not exist")
        return False

    with open(filepath, 'r') as f:
        data = json.load(f)

    data['narrative'] = narrative

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"OK: {code} ({filepath})")
    return True


def main():
    success = 0
    fail = 0
    skip = 0

    for code, narrative in NARRATIVES.items():
        filepath = os.path.join(DATA_DIR, f"{code}.json")
        if not os.path.exists(filepath):
            print(f"SKIP: {code} -- no file at {filepath}")
            skip += 1
            continue
        if update_country_file(code, narrative):
            success += 1
        else:
            fail += 1

    print(f"\nDone: {success} updated, {fail} failed, {skip} skipped")
    print(f"Total Tier 1+2 countries processed: {success}")


if __name__ == "__main__":
    main()
