/* ==========================================================================
   Stratoterra — Internationalization (i18n) Module
   Supports: English (en), Italian (it)
   ========================================================================== */

var I18n = (function() {
  'use strict';

  var currentLang = 'en';
  var listeners = [];

  var translations = {
    en: {
      // Page title & brand
      'page.title': 'Stratoterra — Geopolitical Intelligence',
      'logo.aria': 'Stratoterra — home',

      // Navigation
      'nav.map': 'Map',
      'nav.stories': 'Stories',
      'nav.alerts': 'Alerts',
      'nav.rankings': 'Rankings',
      'nav.compare': 'Compare',

      // Search
      'search.placeholder': 'Search country...',
      'search.aria': 'Search countries',

      // Metric selectors
      'metric.color_by': 'Color by:',
      'metric.alert_severity': 'Alert Severity',
      'metric.gdp_growth': 'GDP Growth',
      'metric.political_stability': 'Political Stability',
      'metric.political_stability_short': 'Stability',
      'metric.investment_risk': 'Investment Risk',
      'metric.investment_risk_short': 'Inv. Risk',
      'metric.military_spend_trend': 'Military Spend Trend',
      'metric.military_spend_short': 'Mil. Spend',
      'metric.military_spend_pct_gdp': 'Military Spend (% GDP)',
      'metric.military_spend_pct_gdp_short': 'Mil. % GDP',
      'metric.national_power_index': 'National Power Index',
      'metric.power_index_short': 'Power Index',
      'metric.energy_independence': 'Energy Independence',
      'metric.energy_independence_short': 'Energy Ind.',
      'metric.trade_openness': 'Trade Openness',
      'metric.trade_openness_short': 'Trade Open.',
      'metric.gdp_growth_pct': 'GDP Growth (%)',
      'metric.trade_openness_pct': 'Trade Openness (%)',

      // Overlay selectors
      'overlay.label': 'Overlay:',
      'overlay.none': 'None',
      'overlay.no_overlay': 'No Overlay',
      'overlay.eu': 'European Union',
      'overlay.nato': 'NATO',
      'overlay.brics': 'BRICS',
      'overlay.asean': 'ASEAN',
      'overlay.opec': 'OPEC',
      'overlay.g7': 'G7',
      'overlay.g20': 'G20',

      // Intel overlays
      'intel.title': 'Intel Overlays',
      'intel.group_air': 'Air & Maritime',
      'intel.group_military': 'Military',
      'intel.group_infra': 'Infrastructure',
      'intel.group_humanitarian': 'Humanitarian',
      'intel.airports': 'Major Airports',
      'intel.ports': 'Strategic Ports',
      'intel.chokepoints': 'Sea Chokepoints',
      'intel.cables': 'Submarine Cables',
      'intel.bases': 'Military Bases',
      'intel.conflicts': 'Conflict Zones',
      'intel.missiles': 'Missile Coverage',
      'intel.nuclear': 'Nuclear Sites',
      'intel.power_stations': 'Power Stations',
      'intel.pipelines': 'Oil & Gas Pipelines',
      'intel.cyber': 'Cyber Operations',
      'intel.sanctions': 'Active Sanctions',

      // Overlay detail card labels
      'card.airport': 'AIRPORT',
      'card.iata_code': 'IATA code',
      'card.passenger_traffic': 'Passenger traffic',
      'card.strategic_port': 'STRATEGIC PORT',
      'card.country': 'Country',
      'card.capacity': 'Capacity',
      'card.military_base': 'MILITARY BASE',
      'card.nation': 'Nation',
      'card.facility': 'Facility',
      'card.personnel': 'Personnel',
      'card.conflict_zone': 'CONFLICT ZONE',
      'card.intensity': 'Intensity',
      'card.since': 'Since',
      'card.type': 'Type',
      'card.casualties': 'Casualties',
      'card.power_station': 'POWER STATION',
      'card.output': 'Output',
      'card.decommissioned': 'Decommissioned',
      'card.nuclear_site': 'NUCLEAR SITE',
      'card.missile_coverage': 'MISSILE COVERAGE',
      'card.system': 'System',
      'card.range': 'Range',
      'card.sea_chokepoint': 'SEA CHOKEPOINT',
      'card.daily_flow': 'Daily flow',
      'card.risk_level': 'Risk level',
      'card.submarine_cable': 'SUBMARINE CABLE',
      'card.operator': 'Operator',
      'card.status': 'Status',
      'card.active': 'Active',
      'card.pipeline': 'PIPELINE',
      'card.product': 'Product',
      'card.from': 'From',
      'card.to': 'To',
      'card.cyber_ops': 'CYBER OPERATIONS',
      'card.origin': 'Origin',
      'card.target': 'Target',
      'card.severity': 'Severity',
      'card.sanctions': 'ACTIVE SANCTIONS',
      'card.issuing_body': 'Issuing body',
      'card.in_force_since': 'In force since',

      // Trend labels
      'trend.strong_growth': 'Strong Growth',
      'trend.growth': 'Growth',
      'trend.stable': 'Stable',
      'trend.decrease': 'Decrease',
      'trend.strong_decrease': 'Strong Decrease',

      // Alert severity
      'severity.critical': 'Critical',
      'severity.warning': 'Warning',
      'severity.watch': 'Watch',
      'severity.none': 'None',

      // Regions
      'region.north_america': 'North America',
      'region.latin_america': 'Latin America',
      'region.europe': 'Europe',
      'region.middle_east': 'Middle East',
      'region.sub_saharan_africa': 'Sub-Saharan Africa',
      'region.south_asia': 'South Asia',
      'region.east_asia': 'East Asia',
      'region.southeast_asia': 'Southeast Asia',
      'region.central_asia': 'Central Asia',
      'region.oceania': 'Oceania',

      // Tier labels
      'tier.1': 'Tier 1 — Major',
      'tier.2': 'Tier 2 — Regional',
      'tier.3': 'Tier 3 — Frontier',

      // Country panel
      'panel.back': '← Back',
      'panel.no_data': 'Detailed data not yet available for {name}.',
      'panel.tab_endowments': 'Endowments',
      'panel.tab_institutions': 'Institutions',
      'panel.tab_economy': 'Economy',
      'panel.tab_military': 'Military',
      'panel.tab_relations': 'Relations',
      'panel.tab_derived': 'Derived',
      'panel.executive_summary': 'Executive Summary',
      'panel.key_changes': 'Key Changes This Week',
      'panel.outlook': 'Outlook',
      'panel.investor_implications': 'Investor Implications',
      'panel.active_alerts': 'Active Alerts',
      'panel.data_quality': 'Data Quality',
      'panel.sources': 'Sources',
      'panel.confidence': 'Confidence',
      'panel.trend': 'Trend',
      'panel.value': 'Value',
      'panel.prev_value': 'Previous',
      'panel.change': 'Change',
      'panel.last_updated': 'Last updated',
      'panel.composite_score': 'Composite Score',
      'panel.volume': 'Volume',

      // Map tooltip
      'tooltip.no_data': 'No data available',
      'tooltip.gdp': 'GDP',
      'tooltip.risk': 'Risk',
      'tooltip.alert': 'alert',
      'tooltip.alerts': 'alerts',

      // Briefing view
      'briefing.back_to_stories': '← Back to Stories',
      'briefing.ai_generated': 'AI-Generated',
      'briefing.countries': 'Countries:',
      'briefing.sources': 'Sources',
      'briefing.accessed': 'accessed',
      'briefing.article_not_found': 'Article not found',
      'briefing.article_load_error': 'This article could not be loaded.',
      'briefing.stories_unavailable': 'Stories unavailable',
      'briefing.stories_not_generated': 'Daily stories have not been generated yet.',
      'briefing.market_context': 'Market Context',
      'briefing.top_stories': 'Top Stories',
      'briefing.regional_roundup': 'Regional Roundup',
      'briefing.investor_action': 'Investor action:',

      // Alert dashboard
      'alerts.dashboard': 'Alert Dashboard',
      'alerts.all_regions': 'All Regions',
      'alerts.all_types': 'All Types',
      'alerts.no_alerts': 'No alerts for today.',
      'alerts.unavailable': 'Alerts unavailable',
      'alerts.not_generated': 'Alert data has not been generated yet.',
      'alerts.action': 'Action:',

      // Rankings view
      'rankings.title': 'Global Rankings',
      'rankings.group_economic': 'Economic',
      'rankings.group_power': 'Power',
      'rankings.group_risk': 'Risk',
      'rankings.group_development': 'Development',
      'rankings.all_regions': 'All Regions',
      'rankings.all_tiers': 'All Tiers',
      'rankings.tier_1': 'Tier 1',
      'rankings.tier_2': 'Tier 2',
      'rankings.tier_3': 'Tier 3',
      'rankings.countries': 'countries',
      'rankings.col_rank': '#',
      'rankings.col_country': 'Country',
      'rankings.col_region': 'Region',
      'rankings.col_gdp': 'GDP',
      'rankings.col_growth': 'Growth %',
      'rankings.col_gdp_cap': 'GDP/Cap',
      'rankings.col_inflation': 'Inflation %',
      'rankings.col_trade_open': 'Trade Open %',
      'rankings.col_risk_prem': 'Risk Prem (bps)',
      'rankings.col_overall': 'Overall',
      'rankings.col_mil_spend': 'Mil Spend',
      'rankings.col_population': 'Population',
      'rankings.col_energy_ind': 'Energy Ind.',
      'rankings.col_inv_risk': 'Inv. Risk',
      'rankings.col_pol_stability': 'Pol. Stability',
      'rankings.col_alerts': 'Alerts',
      'rankings.col_power_index': 'Power Index',
      'rankings.col_energy': 'Energy',
      'rankings.col_trade_pct': 'Trade %',

      // Comparison tool
      'compare.title': 'Country Comparison',
      'compare.add_country': 'Add country... ({n} remaining)',
      'compare.min_countries': 'Select at least 2 countries to compare (up to 5).',
      'compare.mode_table': 'Table',
      'compare.mode_radar': 'Radar Chart',
      'compare.col_metric': 'Metric',
      'compare.gdp': 'GDP',
      'compare.gdp_growth': 'GDP Growth',
      'compare.gdp_capita': 'GDP/Capita',
      'compare.population': 'Population',
      'compare.inflation': 'Inflation',
      'compare.political_stability': 'Political Stability',
      'compare.investment_risk': 'Investment Risk',
      'compare.military_spending': 'Military Spending',
      'compare.economic_complexity': 'Economic Complexity',
      'compare.energy_independence': 'Energy Independence',
      'compare.trade_openness': 'Trade Openness',
      'compare.overall_score': 'Overall Score',
      'compare.alerts': 'Alerts',
      'compare.radar_economic': 'Economic',
      'compare.radar_military': 'Military',
      'compare.radar_technology': 'Technology',
      'compare.radar_stability': 'Stability',
      'compare.radar_openness': 'Openness',
      'compare.radar_energy': 'Energy',

      // Relation explorer
      'relations.title': 'Relation Explorer',
      'relations.network_graph': 'Network Graph',
      'relations.bilateral_detail': 'Bilateral Detail',
      'relations.back_network': '← Network',
      'relations.center_country': 'Center country: ',
      'relations.select': 'Select...',
      'relations.select_pair': 'Select pair: ',
      'relations.no_selection': 'Select a country or pair to explore relationships.',
      'relations.no_data': 'No relation data available for {country}. Relations will appear after pipeline generates bilateral data.',
      'relations.bilateral_unavailable': 'Bilateral detail not available for {pair}.',
      'relations.d3_not_loaded': 'D3.js not loaded.',
      'relations.dim_trade': 'Trade',
      'relations.dim_diplomatic': 'Diplomatic',
      'relations.dim_military': 'Military',
      'relations.dim_financial': 'Financial',
      'relations.dim_energy': 'Energy',
      'relations.dim_scientific': 'Scientific',

      // Footer & meta
      'footer.last_updated': 'Last updated:',
      'footer.not_available': 'Not yet available',
      'disclaimer': 'AI-generated geopolitical analysis for informational purposes only. Not financial advice.',
      'disclaimer.methodology': 'Methodology',

      // Ticker
      'ticker.critical': 'CRITICAL',
      'ticker.watch': 'WATCH',

      // Metric format labels
      'format.none': 'None',
      'format.watch': 'Watch',
      'format.warning': 'Warning',
      'format.critical': 'Critical',
      'format.strong': '↗ Strong',
      'format.growth': '↗ Growth',
      'format.decline': '↘ Decline',
      'format.strong_decline': '⬇ Strong Decline',

      // Legend
      'legend.low': 'Low',
      'legend.high': 'High',
      'legend.decline': 'Decline',
      'legend.growth': 'Growth',

      // Date labels
      'date.today': 'Today',
      'date.yesterday': 'Yesterday',
      'date.days_ago': '{n}d ago',
      'date.weeks_ago': '{n}w ago',
      'date.months_ago': '{n}mo ago',

      // Language selector
      'lang.label': 'Language',
      'lang.en': 'English',
      'lang.it': 'Italiano'
    },

    it: {
      // Page title & brand
      'page.title': 'Stratoterra — Intelligence Geopolitica',
      'logo.aria': 'Stratoterra — home',

      // Navigation
      'nav.map': 'Mappa',
      'nav.stories': 'Articoli',
      'nav.alerts': 'Allerte',
      'nav.rankings': 'Classifiche',
      'nav.compare': 'Confronta',

      // Search
      'search.placeholder': 'Cerca paese...',
      'search.aria': 'Cerca paesi',

      // Metric selectors
      'metric.color_by': 'Colora per:',
      'metric.alert_severity': 'Gravità Allerta',
      'metric.gdp_growth': 'Crescita PIL',
      'metric.political_stability': 'Stabilità Politica',
      'metric.political_stability_short': 'Stabilità',
      'metric.investment_risk': 'Rischio Investimento',
      'metric.investment_risk_short': 'Rischio Inv.',
      'metric.military_spend_trend': 'Trend Spesa Militare',
      'metric.military_spend_short': 'Spesa Mil.',
      'metric.military_spend_pct_gdp': 'Spesa Militare (% PIL)',
      'metric.military_spend_pct_gdp_short': 'Mil. % PIL',
      'metric.national_power_index': 'Indice Potenza Nazionale',
      'metric.power_index_short': 'Indice Potenza',
      'metric.energy_independence': 'Indipendenza Energetica',
      'metric.energy_independence_short': 'Indip. Energ.',
      'metric.trade_openness': 'Apertura Commerciale',
      'metric.trade_openness_short': 'Apert. Comm.',
      'metric.gdp_growth_pct': 'Crescita PIL (%)',
      'metric.trade_openness_pct': 'Apertura Commerciale (%)',

      // Overlay selectors
      'overlay.label': 'Sovrapposizione:',
      'overlay.none': 'Nessuna',
      'overlay.no_overlay': 'Nessuna Sovrapposizione',
      'overlay.eu': 'Unione Europea',
      'overlay.nato': 'NATO',
      'overlay.brics': 'BRICS',
      'overlay.asean': 'ASEAN',
      'overlay.opec': 'OPEC',
      'overlay.g7': 'G7',
      'overlay.g20': 'G20',

      // Intel overlays
      'intel.title': 'Sovrapposizioni Intelligence',
      'intel.group_air': 'Aereo e Marittimo',
      'intel.group_military': 'Militare',
      'intel.group_infra': 'Infrastrutture',
      'intel.group_humanitarian': 'Umanitario',
      'intel.airports': 'Aeroporti Principali',
      'intel.ports': 'Porti Strategici',
      'intel.chokepoints': 'Stretti Marittimi',
      'intel.cables': 'Cavi Sottomarini',
      'intel.bases': 'Basi Militari',
      'intel.conflicts': 'Zone di Conflitto',
      'intel.missiles': 'Copertura Missilistica',
      'intel.nuclear': 'Siti Nucleari',
      'intel.power_stations': 'Centrali Elettriche',
      'intel.pipelines': 'Oleodotti e Gasdotti',
      'intel.cyber': 'Operazioni Cyber',
      'intel.sanctions': 'Sanzioni Attive',

      // Overlay detail card labels
      'card.airport': 'AEROPORTO',
      'card.iata_code': 'Codice IATA',
      'card.passenger_traffic': 'Traffico passeggeri',
      'card.strategic_port': 'PORTO STRATEGICO',
      'card.country': 'Paese',
      'card.capacity': 'Capacità',
      'card.military_base': 'BASE MILITARE',
      'card.nation': 'Nazione',
      'card.facility': 'Struttura',
      'card.personnel': 'Personale',
      'card.conflict_zone': 'ZONA DI CONFLITTO',
      'card.intensity': 'Intensità',
      'card.since': 'Dal',
      'card.type': 'Tipo',
      'card.casualties': 'Vittime',
      'card.power_station': 'CENTRALE ELETTRICA',
      'card.output': 'Potenza',
      'card.decommissioned': 'Dismessa',
      'card.nuclear_site': 'SITO NUCLEARE',
      'card.missile_coverage': 'COPERTURA MISSILISTICA',
      'card.system': 'Sistema',
      'card.range': 'Raggio',
      'card.sea_chokepoint': 'STRETTO MARITTIMO',
      'card.daily_flow': 'Flusso giornaliero',
      'card.risk_level': 'Livello di rischio',
      'card.submarine_cable': 'CAVO SOTTOMARINO',
      'card.operator': 'Operatore',
      'card.status': 'Stato',
      'card.active': 'Attivo',
      'card.pipeline': 'OLEODOTTO/GASDOTTO',
      'card.product': 'Prodotto',
      'card.from': 'Da',
      'card.to': 'A',
      'card.cyber_ops': 'OPERAZIONI CYBER',
      'card.origin': 'Origine',
      'card.target': 'Obiettivo',
      'card.severity': 'Gravità',
      'card.sanctions': 'SANZIONI ATTIVE',
      'card.issuing_body': 'Ente emittente',
      'card.in_force_since': 'In vigore dal',

      // Trend labels
      'trend.strong_growth': 'Forte Crescita',
      'trend.growth': 'Crescita',
      'trend.stable': 'Stabile',
      'trend.decrease': 'Calo',
      'trend.strong_decrease': 'Forte Calo',

      // Alert severity
      'severity.critical': 'Critico',
      'severity.warning': 'Avviso',
      'severity.watch': 'Osservazione',
      'severity.none': 'Nessuno',

      // Regions
      'region.north_america': 'Nord America',
      'region.latin_america': 'America Latina',
      'region.europe': 'Europa',
      'region.middle_east': 'Medio Oriente',
      'region.sub_saharan_africa': 'Africa Subsahariana',
      'region.south_asia': 'Asia Meridionale',
      'region.east_asia': 'Asia Orientale',
      'region.southeast_asia': 'Sud-est Asiatico',
      'region.central_asia': 'Asia Centrale',
      'region.oceania': 'Oceania',

      // Tier labels
      'tier.1': 'Livello 1 — Principali',
      'tier.2': 'Livello 2 — Regionali',
      'tier.3': 'Livello 3 — Frontiera',

      // Country panel
      'panel.back': '← Indietro',
      'panel.no_data': 'Dati dettagliati non ancora disponibili per {name}.',
      'panel.tab_endowments': 'Dotazioni',
      'panel.tab_institutions': 'Istituzioni',
      'panel.tab_economy': 'Economia',
      'panel.tab_military': 'Militare',
      'panel.tab_relations': 'Relazioni',
      'panel.tab_derived': 'Derivati',
      'panel.executive_summary': 'Sintesi Esecutiva',
      'panel.key_changes': 'Cambiamenti Chiave Questa Settimana',
      'panel.outlook': 'Prospettive',
      'panel.investor_implications': 'Implicazioni per gli Investitori',
      'panel.active_alerts': 'Allerte Attive',
      'panel.data_quality': 'Qualità dei Dati',
      'panel.sources': 'Fonti',
      'panel.confidence': 'Affidabilità',
      'panel.trend': 'Tendenza',
      'panel.value': 'Valore',
      'panel.prev_value': 'Precedente',
      'panel.change': 'Variazione',
      'panel.last_updated': 'Ultimo aggiornamento',
      'panel.composite_score': 'Punteggio Composito',
      'panel.volume': 'Volume',

      // Map tooltip
      'tooltip.no_data': 'Dati non disponibili',
      'tooltip.gdp': 'PIL',
      'tooltip.risk': 'Rischio',
      'tooltip.alert': 'allerta',
      'tooltip.alerts': 'allerte',

      // Briefing view
      'briefing.back_to_stories': '← Torna agli Articoli',
      'briefing.ai_generated': 'Generato dall\'IA',
      'briefing.countries': 'Paesi:',
      'briefing.sources': 'Fonti',
      'briefing.accessed': 'consultato',
      'briefing.article_not_found': 'Articolo non trovato',
      'briefing.article_load_error': 'Impossibile caricare questo articolo.',
      'briefing.stories_unavailable': 'Articoli non disponibili',
      'briefing.stories_not_generated': 'Gli articoli giornalieri non sono ancora stati generati.',
      'briefing.market_context': 'Contesto di Mercato',
      'briefing.top_stories': 'Notizie Principali',
      'briefing.regional_roundup': 'Rassegna Regionale',
      'briefing.investor_action': 'Azione investitore:',

      // Alert dashboard
      'alerts.dashboard': 'Pannello Allerte',
      'alerts.all_regions': 'Tutte le Regioni',
      'alerts.all_types': 'Tutti i Tipi',
      'alerts.no_alerts': 'Nessuna allerta per oggi.',
      'alerts.unavailable': 'Allerte non disponibili',
      'alerts.not_generated': 'I dati delle allerte non sono ancora stati generati.',
      'alerts.action': 'Azione:',

      // Rankings view
      'rankings.title': 'Classifiche Globali',
      'rankings.group_economic': 'Economico',
      'rankings.group_power': 'Potenza',
      'rankings.group_risk': 'Rischio',
      'rankings.group_development': 'Sviluppo',
      'rankings.all_regions': 'Tutte le Regioni',
      'rankings.all_tiers': 'Tutti i Livelli',
      'rankings.tier_1': 'Livello 1',
      'rankings.tier_2': 'Livello 2',
      'rankings.tier_3': 'Livello 3',
      'rankings.countries': 'paesi',
      'rankings.col_rank': '#',
      'rankings.col_country': 'Paese',
      'rankings.col_region': 'Regione',
      'rankings.col_gdp': 'PIL',
      'rankings.col_growth': 'Crescita %',
      'rankings.col_gdp_cap': 'PIL/Cap',
      'rankings.col_inflation': 'Inflazione %',
      'rankings.col_trade_open': 'Apert. Comm. %',
      'rankings.col_risk_prem': 'Premio Rischio (bps)',
      'rankings.col_overall': 'Complessivo',
      'rankings.col_mil_spend': 'Spesa Mil.',
      'rankings.col_population': 'Popolazione',
      'rankings.col_energy_ind': 'Indip. Energ.',
      'rankings.col_inv_risk': 'Rischio Inv.',
      'rankings.col_pol_stability': 'Stab. Politica',
      'rankings.col_alerts': 'Allerte',
      'rankings.col_power_index': 'Indice Potenza',
      'rankings.col_energy': 'Energia',
      'rankings.col_trade_pct': 'Comm. %',

      // Comparison tool
      'compare.title': 'Confronto Paesi',
      'compare.add_country': 'Aggiungi paese... ({n} rimanenti)',
      'compare.min_countries': 'Seleziona almeno 2 paesi da confrontare (massimo 5).',
      'compare.mode_table': 'Tabella',
      'compare.mode_radar': 'Grafico Radar',
      'compare.col_metric': 'Metrica',
      'compare.gdp': 'PIL',
      'compare.gdp_growth': 'Crescita PIL',
      'compare.gdp_capita': 'PIL/Capita',
      'compare.population': 'Popolazione',
      'compare.inflation': 'Inflazione',
      'compare.political_stability': 'Stabilità Politica',
      'compare.investment_risk': 'Rischio Investimento',
      'compare.military_spending': 'Spesa Militare',
      'compare.economic_complexity': 'Complessità Economica',
      'compare.energy_independence': 'Indipendenza Energetica',
      'compare.trade_openness': 'Apertura Commerciale',
      'compare.overall_score': 'Punteggio Complessivo',
      'compare.alerts': 'Allerte',
      'compare.radar_economic': 'Economico',
      'compare.radar_military': 'Militare',
      'compare.radar_technology': 'Tecnologia',
      'compare.radar_stability': 'Stabilità',
      'compare.radar_openness': 'Apertura',
      'compare.radar_energy': 'Energia',

      // Relation explorer
      'relations.title': 'Esplora Relazioni',
      'relations.network_graph': 'Grafico Rete',
      'relations.bilateral_detail': 'Dettaglio Bilaterale',
      'relations.back_network': '← Rete',
      'relations.center_country': 'Paese centrale: ',
      'relations.select': 'Seleziona...',
      'relations.select_pair': 'Seleziona coppia: ',
      'relations.no_selection': 'Seleziona un paese o una coppia per esplorare le relazioni.',
      'relations.no_data': 'Dati relazionali non disponibili per {country}. Le relazioni appariranno dopo che il pipeline avrà generato i dati bilaterali.',
      'relations.bilateral_unavailable': 'Dettaglio bilaterale non disponibile per {pair}.',
      'relations.d3_not_loaded': 'D3.js non caricato.',
      'relations.dim_trade': 'Commercio',
      'relations.dim_diplomatic': 'Diplomatico',
      'relations.dim_military': 'Militare',
      'relations.dim_financial': 'Finanziario',
      'relations.dim_energy': 'Energia',
      'relations.dim_scientific': 'Scientifico',

      // Footer & meta
      'footer.last_updated': 'Ultimo aggiornamento:',
      'footer.not_available': 'Non ancora disponibile',
      'disclaimer': 'Analisi geopolitica generata dall\'IA solo a scopo informativo. Non costituisce consulenza finanziaria.',
      'disclaimer.methodology': 'Metodologia',

      // Ticker
      'ticker.critical': 'CRITICO',
      'ticker.watch': 'OSSERVAZIONE',

      // Metric format labels
      'format.none': 'Nessuno',
      'format.watch': 'Osservazione',
      'format.warning': 'Avviso',
      'format.critical': 'Critico',
      'format.strong': '↗ Forte',
      'format.growth': '↗ Crescita',
      'format.decline': '↘ Calo',
      'format.strong_decline': '⬇ Forte Calo',

      // Legend
      'legend.low': 'Basso',
      'legend.high': 'Alto',
      'legend.decline': 'Calo',
      'legend.growth': 'Crescita',

      // Date labels
      'date.today': 'Oggi',
      'date.yesterday': 'Ieri',
      'date.days_ago': '{n}g fa',
      'date.weeks_ago': '{n}s fa',
      'date.months_ago': '{n}m fa',

      // Language selector
      'lang.label': 'Lingua',
      'lang.en': 'English',
      'lang.it': 'Italiano'
    }
  };

  // Supported languages list
  var SUPPORTED_LANGUAGES = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'it', label: 'Italiano', flag: '🇮🇹' }
  ];

  /**
   * Get translation for a key, with optional parameter substitution.
   * @param {string} key - Translation key (e.g., 'nav.map')
   * @param {object} [params] - Optional parameters for interpolation (e.g., {name: 'Italy'})
   * @returns {string} Translated string, or the key if not found
   */
  function t(key, params) {
    var dict = translations[currentLang] || translations.en;
    var str = dict[key];
    if (str == null) {
      // Fallback to English
      str = translations.en[key];
    }
    if (str == null) return key;
    if (params) {
      Object.keys(params).forEach(function(k) {
        str = str.replace(new RegExp('\\{' + k + '\\}', 'g'), params[k]);
      });
    }
    return str;
  }

  /**
   * Get the current language code
   */
  function getLang() {
    return currentLang;
  }

  /**
   * Set the current language and notify listeners
   */
  function setLang(lang) {
    if (!translations[lang]) return;
    if (lang === currentLang) return;
    currentLang = lang;
    try {
      localStorage.setItem('stratoterra-lang', lang);
    } catch (e) { /* storage unavailable */ }
    document.documentElement.lang = lang;
    notifyListeners();
  }

  /**
   * Register a listener for language changes
   */
  function onChange(fn) {
    listeners.push(fn);
  }

  function notifyListeners() {
    listeners.forEach(function(fn) {
      try { fn(currentLang); } catch (e) { console.error('[I18n] Listener error:', e); }
    });
  }

  /**
   * Get the locale string for date formatting
   */
  function getLocale() {
    return currentLang === 'it' ? 'it-IT' : 'en-US';
  }

  /**
   * Update all static HTML elements that have data-i18n attributes
   */
  function updateDOM() {
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
      var key = el.getAttribute('data-i18n');
      var translated = t(key);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = translated;
      } else {
        el.textContent = translated;
      }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
      el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(function(el) {
      el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria-label')));
    });
    document.querySelectorAll('[data-i18n-title]').forEach(function(el) {
      el.title = t(el.getAttribute('data-i18n-title'));
    });
    // Update page title
    document.title = t('page.title');
  }

  /**
   * Get list of supported languages
   */
  function getSupportedLanguages() {
    return SUPPORTED_LANGUAGES;
  }

  // Initialize from localStorage or browser preference
  function init() {
    var saved = null;
    try { saved = localStorage.getItem('stratoterra-lang'); } catch (e) {}
    if (saved && translations[saved]) {
      currentLang = saved;
    } else {
      // Check browser language
      var browserLang = (navigator.language || navigator.userLanguage || 'en').slice(0, 2).toLowerCase();
      if (translations[browserLang]) {
        currentLang = browserLang;
      }
    }
    document.documentElement.lang = currentLang;
  }

  // Auto-initialize
  init();

  return {
    t: t,
    getLang: getLang,
    setLang: setLang,
    getLocale: getLocale,
    onChange: onChange,
    updateDOM: updateDOM,
    getSupportedLanguages: getSupportedLanguages,
    SUPPORTED_LANGUAGES: SUPPORTED_LANGUAGES
  };
})();
