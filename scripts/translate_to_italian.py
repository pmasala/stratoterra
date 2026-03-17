#!/usr/bin/env python3
"""
Translate country-detail JSON files from English to Italian.
Translates all text fields while preserving numeric values, dates, codes,
JSON structure, and source values.
"""

import json
import os
import re
import copy

DATA_DIR = "/home/user/stratoterra/data/chunks/country-detail"

COUNTRIES = [
    "AGO", "ARE", "ARG", "AUS", "AZE", "BGD", "BGR", "BRA", "CAN", "CHE",
    "CHL", "CHN", "CIV", "COD", "COL", "CZE", "DEU", "EGY", "ESP", "ETH",
    "FIN", "FRA", "GBR", "GEO", "GHA"
]

# Country names EN -> IT
COUNTRY_NAMES = {
    "Angola": "Angola",
    "United Arab Emirates": "Emirati Arabi Uniti",
    "Argentina": "Argentina",
    "Australia": "Australia",
    "Azerbaijan": "Azerbaigian",
    "Bangladesh": "Bangladesh",
    "Bulgaria": "Bulgaria",
    "Brazil": "Brasile",
    "Canada": "Canada",
    "Switzerland": "Svizzera",
    "Chile": "Cile",
    "China": "Cina",
    "Côte d'Ivoire": "Costa d'Avorio",
    "Cote d'Ivoire": "Costa d'Avorio",
    "Democratic Republic of the Congo": "Repubblica Democratica del Congo",
    "DR Congo": "RD Congo",
    "Colombia": "Colombia",
    "Czech Republic": "Repubblica Ceca",
    "Czechia": "Cechia",
    "Germany": "Germania",
    "Egypt": "Egitto",
    "Spain": "Spagna",
    "Ethiopia": "Etiopia",
    "Finland": "Finlandia",
    "France": "Francia",
    "United Kingdom": "Regno Unito",
    "Georgia": "Georgia",
    "Ghana": "Ghana",
    # Other country names that may appear in text
    "United States": "Stati Uniti",
    "Russia": "Russia",
    "Japan": "Giappone",
    "India": "India",
    "South Korea": "Corea del Sud",
    "North Korea": "Corea del Nord",
    "Turkey": "Turchia",
    "Iran": "Iran",
    "Iraq": "Iraq",
    "Saudi Arabia": "Arabia Saudita",
    "Israel": "Israele",
    "South Africa": "Sudafrica",
    "Nigeria": "Nigeria",
    "Mexico": "Messico",
    "Indonesia": "Indonesia",
    "Poland": "Polonia",
    "Netherlands": "Paesi Bassi",
    "Belgium": "Belgio",
    "Sweden": "Svezia",
    "Norway": "Norvegia",
    "Denmark": "Danimarca",
    "Austria": "Austria",
    "Ireland": "Irlanda",
    "Italy": "Italia",
    "Portugal": "Portogallo",
    "Greece": "Grecia",
    "Romania": "Romania",
    "Hungary": "Ungheria",
    "Ukraine": "Ucraina",
    "Pakistan": "Pakistan",
    "Thailand": "Tailandia",
    "Vietnam": "Vietnam",
    "Philippines": "Filippine",
    "Malaysia": "Malesia",
    "Singapore": "Singapore",
    "Taiwan": "Taiwan",
    "New Zealand": "Nuova Zelanda",
    "Peru": "Peru",
    "Venezuela": "Venezuela",
    "Ecuador": "Ecuador",
    "Bolivia": "Bolivia",
    "Paraguay": "Paraguay",
    "Uruguay": "Uruguay",
    "Cuba": "Cuba",
    "Morocco": "Marocco",
    "Tunisia": "Tunisia",
    "Algeria": "Algeria",
    "Libya": "Libia",
    "Kenya": "Kenya",
    "Tanzania": "Tanzania",
    "Mozambique": "Mozambico",
    "Qatar": "Qatar",
    "Kuwait": "Kuwait",
    "Oman": "Oman",
    "Bahrain": "Bahrein",
    "Jordan": "Giordania",
    "Lebanon": "Libano",
    "Syria": "Siria",
    "Yemen": "Yemen",
    "Afghanistan": "Afghanistan",
    "Myanmar": "Myanmar",
    "Sri Lanka": "Sri Lanka",
    "Nepal": "Nepal",
    "Cambodia": "Cambogia",
}

# Acronyms to preserve (never translate)
PRESERVE_ACRONYMS = {
    "NATO", "EU", "BRICS", "ASEAN", "OPEC", "G7", "G20", "IMF", "GDP", "USD",
    "CPI", "FDI", "FX", "LNG", "WTI", "SPR", "BPS", "ECB", "BoE", "BOE",
    "UNSC", "AU", "SADC", "ECOWAS", "CSDP", "JEF", "AUKUS", "S&P", "CAC",
    "FTSE", "DAX", "OAT", "EUR", "GBP", "JPY", "CNY", "BRL", "ARS",
    "Nokia", "Thales", "Dassault", "MBDA", "Shell", "BP",
    "Five Eyes", "SIPRI", "EIA", "WEO", "IFS",
}

# Translation dictionary for common phrases/terms
TRANSLATIONS = {
    # Economic terms
    "GDP growth": "crescita del PIL",
    "GDP": "PIL",
    "inflation": "inflazione",
    "Inflation": "Inflazione",
    "unemployment": "disoccupazione",
    "Unemployment": "Disoccupazione",
    "current account": "conto corrente",
    "Current account": "Conto corrente",
    "fiscal balance": "bilancio fiscale",
    "trade surplus": "surplus commerciale",
    "trade deficit": "deficit commerciale",
    "trade disruption": "perturbazione commerciale",
    "trade openness": "apertura commerciale",
    "Trade openness": "Apertura commerciale",
    "trade rerouting": "reindirizzamento commerciale",
    "trade policy": "politica commerciale",
    "trade diversification": "diversificazione commerciale",
    "trade uncertainty": "incertezza commerciale",
    "basis points": "punti base",
    "stagflation": "stagflazione",
    "recession": "recessione",
    "bond yields": "rendimenti obbligazionari",
    "bond yield": "rendimento obbligazionario",
    "sovereign bonds": "obbligazioni sovrane",
    "sovereign bond": "obbligazione sovrana",
    "Sovereign bonds": "Obbligazioni sovrane",
    "credit rating": "rating creditizio",
    "credit ratings": "rating creditizi",
    "exchange rate": "tasso di cambio",
    "interest rate": "tasso di interesse",
    "policy rate": "tasso di riferimento",
    "central bank": "banca centrale",
    "Central bank": "Banca centrale",
    "government debt": "debito pubblico",
    "Government debt": "Debito pubblico",
    "public debt": "debito pubblico",
    "fiscal consolidation": "consolidamento fiscale",
    "fiscal trajectory": "traiettoria fiscale",
    "fiscal position": "posizione fiscale",
    "debt restructuring": "ristrutturazione del debito",
    "debt ratio": "rapporto debito/PIL",
    "debt trajectory": "traiettoria del debito",
    "supply chain": "catena di approvvigionamento",
    "supply chains": "catene di approvvigionamento",
    "foreign direct investment": "investimento diretto estero",
    "investment risk": "rischio di investimento",
    "Investment risk": "Rischio di investimento",
    "market crash": "crollo dei mercati",
    "risk premium": "premio per il rischio",
    "political risk": "rischio politico",
    "Political risk": "Rischio politico",
    "political risk premium": "premio per il rischio politico",
    "Political risk premium": "Premio per il rischio politico",
    "economic risk": "rischio economico",
    "financial market risk": "rischio dei mercati finanziari",
    "security risk": "rischio sicurezza",
    "oil price surge": "impennata del prezzo del petrolio",
    "oil price shock": "shock del prezzo del petrolio",
    "oil shock": "shock petrolifero",
    "Oil shock": "Shock petrolifero",
    "energy price shock": "shock dei prezzi energetici",
    "energy price": "prezzo dell'energia",
    "energy prices": "prezzi dell'energia",
    "energy security": "sicurezza energetica",
    "energy transition": "transizione energetica",
    "energy independence": "indipendenza energetica",
    "Energy independence": "Indipendenza energetica",
    "energy-intensive sectors": "settori ad alta intensita energetica",
    "energy-intensive": "ad alta intensita energetica",
    "energy-rich": "ricchi di energia",
    "energy-dependent": "dipendenti dall'energia",
    "energy sector": "settore energetico",
    "energy cost": "costo energetico",
    "energy costs": "costi energetici",
    "energy import": "importazione energetica",
    "energy imports": "importazioni energetiche",
    "energy crisis": "crisi energetica",
    "natural gas": "gas naturale",
    "natural gas prices": "prezzi del gas naturale",
    "commodity windfall": "guadagno straordinario dalle materie prime",
    "commodity prices": "prezzi delle materie prime",
    "commodity export": "esportazione di materie prime",
    "commodity exports": "esportazioni di materie prime",
    "defense spending": "spesa per la difesa",
    "Defense spending": "Spesa per la difesa",
    "defense industry": "industria della difesa",
    "defense stocks": "titoli della difesa",
    "defense sector": "settore della difesa",
    "defense communication": "comunicazioni per la difesa",
    "military spending": "spesa militare",
    "military expenditure": "spesa militare",
    "safe-haven": "bene rifugio",
    "safe haven": "bene rifugio",
    "earnings pressure": "pressione sugli utili",
    "rate cut": "taglio dei tassi",
    "rate cuts": "tagli dei tassi",
    "easing cycle": "ciclo di allentamento",
    "headwinds": "venti contrari",
    "tailwinds": "venti favorevoli",
    "import cost": "costo delle importazioni",
    "import costs": "costi delle importazioni",
    "export partners": "partner commerciali per l'export",
    "import partners": "partner commerciali per l'import",
    "industrial competitiveness": "competitivita industriale",
    "Industrial competitiveness": "Competitivita industriale",
    "rearmament": "riarmo",
    "regional instability": "instabilita regionale",
    "wage-price spiral": "spirale salari-prezzi",
    "risk-off sentiment": "sentimento di avversione al rischio",
    "risk-off": "avversione al rischio",
    "entry point": "punto di ingresso",
    "overweight": "sovrappesare",
    "Overweight": "Sovrappesare",
    "underweight": "sottopesare",
    "Underweight": "Sottopesare",

    # Political terms
    "political stability": "stabilita politica",
    "Political stability": "Stabilita politica",
    "political crisis": "crisi politica",
    "Political crisis": "Crisi politica",
    "political pressure": "pressione politica",
    "domestic political": "politica interna",
    "political disruptions": "perturbazioni politiche",
    "municipal elections": "elezioni comunali",
    "national election": "elezioni nazionali",
    "presidential election": "elezioni presidenziali",
    "general election": "elezioni generali",
    "cabinet reshuffle": "rimpasto di governo",
    "deputy leadership": "leadership vicaria",
    "ministerial code": "codice ministeriale",
    "head of state": "capo di stato",
    "head of government": "capo del governo",
    "President": "Presidente",
    "Prime Minister": "Primo Ministro",
    "King": "Re",
    "Chancellor": "Cancelliere",
    "full democracy": "democrazia piena",
    "flawed democracy": "democrazia imperfetta",
    "hybrid regime": "regime ibrido",
    "authoritarian": "autoritario",
    "free": "libero",
    "partly free": "parzialmente libero",
    "not free": "non libero",
    "freedom of press": "liberta di stampa",
    "rule of law": "stato di diritto",
    "governance": "governance",
    "corruption": "corruzione",
    "sanctions": "sanzioni",
    "international sanctions": "sanzioni internazionali",
    "selective default": "default selettivo",
    "Selective default": "Default selettivo",
    "EU accession": "adesione all'UE",
    "EU membership": "appartenenza all'UE",
    "alliance strain": "tensione nell'alleanza",
    "burden-sharing": "ripartizione degli oneri",
    "diplomatic status": "status diplomatico",
    "diplomatic positioning": "posizionamento diplomatico",
    "diplomatic activism": "attivismo diplomatico",

    # Military/security terms
    "Hormuz": "Hormuz",
    "Hormuz crisis": "crisi di Hormuz",
    "Hormuz closure": "chiusura di Hormuz",
    "Hormuz reopening": "riapertura di Hormuz",
    "Iran-Hormuz crisis": "crisi Iran-Hormuz",
    "Iran war": "guerra con l'Iran",
    "Iran strikes": "attacchi all'Iran",
    "Suez": "Suez",
    "shipping disruption": "perturbazione del trasporto marittimo",
    "maritime": "marittimo",
    "conflict": "conflitto",
    "conflict status": "stato di conflitto",
    "active conflict": "conflitto attivo",
    "nuclear energy": "energia nucleare",
    "Nuclear energy": "Energia nucleare",
    "nuclear arsenal": "arsenale nucleare",
    "nuclear advantage": "vantaggio nucleare",
    "warheads": "testate nucleari",
    "submarines": "sottomarini",
    "battle tanks": "carri armati",
    "military personnel": "personale militare",
    "active military": "militari in servizio attivo",
    "reserve military": "riserve militari",
    "armed forces": "forze armate",
    "army": "esercito",
    "navy": "marina",
    "air force": "aeronautica",
    "arms exports": "esportazioni di armi",
    "arms transfers": "trasferimenti di armi",

    # Trend/analysis terms
    "stable": "stabile",
    "growth": "crescita",
    "strong growth": "forte crescita",
    "strong_growth": "forte crescita",
    "decrease": "diminuzione",
    "strong decrease": "forte diminuzione",
    "strong_decrease": "forte diminuzione",
    "rising": "in aumento",
    "declining": "in calo",
    "improving": "in miglioramento",
    "deteriorating": "in deterioramento",
    "broadly stable": "sostanzialmente stabile",
    "broadly maintained": "sostanzialmente mantenuto",
    "broadly unchanged": "sostanzialmente invariato",
    "broadly stable with modest": "sostanzialmente stabile con modesta",
    "modestly rising": "in modesto aumento",
    "modestly deteriorating": "in modesto deterioramento",
    "moderately rising": "in moderato aumento",
    "mounting pressure": "pressione crescente",
    "Mounting pressure": "Pressione crescente",
    "challenging near-term": "breve termine impegnativo",
    "structural": "strutturale",
    "long-term": "lungo termine",
    "near-term": "breve termine",
    "short-term": "breve termine",
    "medium-term": "medio termine",

    # Data quality terms
    "Data quality": "Qualita dei dati",
    "data quality": "qualita dei dati",
    "data points": "punti dati",
    "Data quality is high": "La qualita dei dati e alta",
    "Flagged factors": "Fattori segnalati",
    "flagged factors": "fattori segnalati",
    "updated this run": "aggiornati in questa esecuzione",
    "active alert": "allerta attiva",
    "active alerts": "allerte attive",
    "Active alerts": "Allerte attive",
    "basic coverage": "copertura di base",
    "Tier 3 country with basic coverage": "Paese Tier 3 con copertura di base",
    "Tier 3 country with basic coverage only": "Paese Tier 3 con sola copertura di base",

    # Common phrases in narratives
    "No significant changes this week": "Nessun cambiamento significativo questa settimana",
    "No major domestic political disruptions this week": "Nessuna perturbazione politica interna significativa questa settimana",
    "Frontier market risk applies": "Si applica il rischio di mercato di frontiera",
    "Monitor for developments relevant to sector exposure": "Monitorare gli sviluppi rilevanti per l'esposizione settoriale",
    "requires monitoring": "richiede monitoraggio",
    "Oil price surge affects all energy importers": "L'impennata del prezzo del petrolio colpisce tutti gli importatori di energia",
    "outlook requires monitoring": "le prospettive richiedono monitoraggio",
    "Conditions persist": "Le condizioni persistono",
    "conditions persist": "le condizioni persistono",

    # Section headings / common
    "executive summary": "sintesi esecutiva",
    "Executive summary": "Sintesi esecutiva",
    "key changes": "cambiamenti chiave",
    "Key changes": "Cambiamenti chiave",
    "outlook": "prospettive",
    "Outlook": "Prospettive",
    "investor implications": "implicazioni per gli investitori",
    "Investor implications": "Implicazioni per gli investitori",

    # Misc
    "global": "globale",
    "global uncertainty": "incertezza globale",
    "global environment": "contesto globale",
    "institutional framework": "quadro istituzionale",
    "background pressure": "pressione di fondo",
    "institutions holding": "istituzioni che reggono",
    "technology sector": "settore tecnologico",
    "Technology sector": "Settore tecnologico",
    "provides growth base": "fornisce una base di crescita",
    "general strike": "sciopero generale",
    "turnout": "affluenza",
    "Record-low turnout": "Affluenza ai minimi storici",
    "second round": "secondo turno",
    "first round": "primo turno",
    "First round": "Primo turno",
    "best-ever": "miglior risultato di sempre",
    "National Rally": "Rassemblement National",
    "North Sea": "Mare del Nord",
    "Helsinki exchange": "Borsa di Helsinki",
    "entry point": "punto di ingresso",
    "partner relationships": "relazioni con i partner",
    "Partner relationships": "Relazioni con i partner",
    "weekly briefing": "briefing settimanale",
    "Weekly briefing": "Briefing settimanale",
    "this week": "questa settimana",
    "This week": "Questa settimana",
    "European-wide": "a livello europeo",
    "pro-Palestine protests": "proteste pro-Palestina",
}


def translate_text(text):
    """Translate an English text string to Italian using dictionary-based approach."""
    if not isinstance(text, str):
        return text
    if not text.strip():
        return text

    result = text

    # Replace country names (longer names first to avoid partial matches)
    sorted_countries = sorted(COUNTRY_NAMES.items(), key=lambda x: -len(x[0]))
    for en, it in sorted_countries:
        if en in result:
            result = result.replace(en, it)

    # Replace phrases (longer phrases first)
    sorted_translations = sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0]))
    for en, it in sorted_translations:
        if en in result:
            result = result.replace(en, it)

    # Second pass: translate remaining common English words/patterns in context
    # These are applied after the phrase translations
    result = translate_remaining_english(result)

    return result


def translate_remaining_english(text):
    """Second pass to translate remaining English sentence-level patterns."""
    result = text

    # Only translate multi-word phrases that are safe (won't break substrings)
    # These are complete sentence fragments commonly found in the data
    patterns = [
        # Common narrative patterns (very specific, longer first)
        ("'s economy faces mounting pressure from the global energy price shock triggered by the", " affronta una pressione crescente dallo shock globale dei prezzi energetici innescato dalla"),
        ("'s economy faces mounting pressure from the global", " affronta una pressione crescente dall'ambiente globale"),
        ("'s economy faces moderate headwinds from the global environment", " affronta venti contrari moderati dal contesto globale"),
        (" faces a challenging near-term as the energy price shock works through the economy.", " affronta un breve termine impegnativo mentre lo shock dei prezzi energetici si propaga nell'economia."),
        (" faces a challenging near-term as the shock dei prezzi energetici works through the economy.", " affronta un breve termine impegnativo mentre lo shock dei prezzi energetici si propaga nell'economia."),
        (" faces earnings pressure across energy-intensive sectors", " affronta pressione sugli utili nei settori ad alta intensita energetica"),
        (" faces severe economic disruption from", " affronta una grave perturbazione economica causata da"),
        (" remains relatively insulated from the", " rimane relativamente isolata dalla"),
        (" remains contained at", " rimane contenuto a"),
        (" is benefiting from elevated oil prices driven by the", " beneficia dei prezzi elevati del petrolio guidati dalla"),
        (" is in default selettivo", " e in default selettivo"),
        (" is moderate by European standards", " e moderato per gli standard europei"),
        (" stands at", " si attesta a"),
        (" records", " registra"),
        (" would provide significant relief, but structural energy security gaps require long-term investment.", " fornirebbe un sollievo significativo, ma le lacune strutturali nella sicurezza energetica richiedono investimenti a lungo termine."),
        (" would provide significant relief, but strutturale sicurezza energetica gaps require lungo termine investimento.", " fornirebbe un sollievo significativo, ma le lacune strutturali nella sicurezza energetica richiedono investimenti a lungo termine."),
        (" would provide significant relief", " fornirebbe un sollievo significativo"),
        (" constrains ECB rate cut options", " vincola le opzioni di taglio dei tassi della ECB"),
        (" constrains ECB taglio dei tassi options", " vincola le opzioni di taglio dei tassi della ECB"),
        (" Inflation at", " Inflazione a"),
        (" inflation at", " inflazione a"),
        (" while inflation is at", " mentre l'inflazione e a"),
        (" while inflazione is at", " mentre l'inflazione e a"),
        (" GDP growth stands at", " La crescita del PIL si attesta a"),
        (" crescita del PIL stands at", " La crescita del PIL si attesta a"),
        (" crescita del PIL si attesta a", " La crescita del PIL si attesta a"),
        (" with GDP growth at", " con crescita del PIL a"),
        (" with crescita del PIL at", " con crescita del PIL a"),
        (" GDP growth at", " crescita del PIL a"),
        (" amplifying vulnerability", " amplificando la vulnerabilita"),
        (", amplifying vulnerability", ", amplificando la vulnerabilita"),
        (", amplificando la vulnerabilita.", ", amplificando la vulnerabilita."),
        (" Key signal:", " Segnale chiave:"),
        (" Segnale chiave:", " Segnale chiave:"),
        (" Investment risk remains contained at", " Il rischio di investimento rimane contenuto a"),
        (" Rischio di investimento remains contained at", " Il rischio di investimento rimane contenuto a"),
        (" Investment risk at", " Rischio di investimento a"),
        (" Rischio di investimento at", " Rischio di investimento a"),
        # Additional high-frequency patterns
        (" With indipendenza energetica at only", " Con indipendenza energetica a solo"),
        (" With energy independence at only", " Con indipendenza energetica a solo"),
        (", the pass-through to production costs will be severe.", ", il trasferimento sui costi di produzione sara severo."),
        ("Inflazione at", "Inflazione a"),
        ("(in aumento)", "(in aumento)"),
        ("(in calo)", "(in calo)"),
        ("(stabile)", "(stabile)"),
        ("(surging)", "(in impennata)"),
        (" is at ", " e a "),
        (" is low at ", " e basso a "),
        (" is ", " e "),
        (" are ", " sono "),
        (" the ", " la "),
        (" from ", " da "),
        (" with ", " con "),
        (" while ", " mentre "),
        (" as ", " poiche "),
        (" but ", " ma "),
        (" and ", " e "),
        (" for ", " per "),
        (" of ", " di "),
        (" on ", " su "),
        (" in ", " in "),
        (" to ", " a "),
        (" by ", " da "),
        (" or ", " o "),
        (" an ", " un "),
        (" not ", " non "),
        (" will ", " sara "),
        (" has ", " ha "),
        (" have ", " hanno "),
        (" may ", " potrebbe "),
        (" can ", " puo "),
        (" this ", " questo "),
        (" that ", " che "),
        (" which ", " che "),
        (" its ", " la sua "),
        (" their ", " la loro "),
        (" been ", " stato "),
        (" expected ", " previsto "),
        (" announced ", " annunciato "),
        (" reported ", " riportato "),
        (" held ", " tenuto "),
        (" between ", " tra "),
        (" against ", " contro "),
        (" after ", " dopo "),
        (" about ", " circa "),
        (" only ", " solo "),
        (" also ", " anche "),
        (" still ", " ancora "),
        (" however ", " tuttavia "),
        (" although ", " sebbene "),
        (" due to ", " a causa di "),
        (" because ", " perche "),
        (" despite ", " nonostante "),
        (" without ", " senza "),
        (" during ", " durante "),
        (" through ", " attraverso "),
        (" under ", " sotto "),
        (" above ", " sopra "),
        (" below ", " sotto "),
        (" across ", " attraverso "),
        (" into ", " in "),
        (" over ", " su "),
        (" currently ", " attualmente "),
        (" significantly ", " significativamente "),
        (" particularly ", " particolarmente "),
        (" especially ", " specialmente "),
        (" relatively ", " relativamente "),
        (" primarily ", " principalmente "),
        (" approximately ", " approssimativamente "),
        (" likely ", " probabilmente "),
        (" recently ", " recentemente "),
        (" strongly ", " fortemente "),
        (" increasingly ", " sempre piu "),
        (" partially ", " parzialmente "),
        (" broadly ", " sostanzialmente "),
        (" modestly ", " modestamente "),
        ("elevated ", "elevato "),
        (" new ", " nuova "),
        (" key ", " chiave "),
        (" high ", " alto "),
        (" low ", " basso "),
        (" strong ", " forte "),
        (" weak ", " debole "),
        (" major ", " importante "),
        (" large ", " grande "),
        (" global ", " globale "),
        ("Global ", "Globale "),
        (" domestic ", " domestica "),
        (" external ", " esterna "),
        (" structural ", " strutturale "),
        (" significant ", " significativa "),
        (" potential ", " potenziale "),
        (" current ", " attuale "),
        (" recent ", " recente "),
        (" ongoing ", " in corso "),
        (" moderate ", " moderata "),
        (" severe ", " severa "),
        (" critical ", " critica "),
        (" positive ", " positiva "),
        (" negative ", " negativa "),
        (" direct ", " diretta "),
        (" overall ", " complessiva "),
        (" additional ", " aggiuntiva "),
        # Common nouns at word boundaries
        (" production ", " produzione "),
        (" sectors ", " settori "),
        (" markets ", " mercati "),
        (" prices ", " prezzi "),
        (" costs ", " costi "),
        (" reserves ", " riserve "),
        (" exports ", " esportazioni "),
        (" imports ", " importazioni "),
        (" competitors ", " concorrenti "),
        (" companies ", " aziende "),
        (" consumers ", " consumatori "),
        (" countries ", " paesi "),
        (" conditions ", " condizioni "),
        (" options ", " opzioni "),
        (" routes ", " rotte "),
        (" stocks ", " titoli "),
        (" levels ", " livelli "),
        (" rates ", " tassi "),
        (" flows ", " flussi "),
        (" partners ", " partner "),
        (" impacts ", " impatti "),
        (" concerns ", " preoccupazioni "),
        (" developments ", " sviluppi "),
        (" investigations ", " indagini "),
        (" challenges ", " sfide "),
        (" improvements ", " miglioramenti "),
        (" partner relationships broadly stable within", " relazioni con i partner sostanzialmente stabili all'interno di"),
        (" political stability broadly maintained", " stabilita politica sostanzialmente mantenuta"),
        (" political stability broadly unchanged", " stabilita politica sostanzialmente invariata"),
        (" trade openness broadly stable", " apertura commerciale sostanzialmente stabile"),
        (" broadly stable —", " sostanzialmente stabile —"),
        (" broadly stable with modest", " sostanzialmente stabile con modesta"),
        (" broadly stable.", " sostanzialmente stabile."),
        (" broadly stable", " sostanzialmente stabile"),
        (" broadly maintained.", " sostanzialmente mantenuta."),
        (" broadly maintained", " sostanzialmente mantenuta"),
        (" broadly unchanged.", " sostanzialmente invariata."),
        (" broadly unchanged", " sostanzialmente invariata"),
        (" investment risk broadly stable", " rischio di investimento sostanzialmente stabile"),
        (" Global trade disruption from Hormuz primarily affects Gulf-dependent routes.", " La perturbazione del commercio globale da Hormuz colpisce principalmente le rotte dipendenti dal Golfo."),
        (" Some trade rerouting benefits alternative routes.", " Alcuni reindirizzamenti commerciali avvantaggiano rotte alternative."),
        (" No major domestic political disruptions this week.", " Nessuna perturbazione politica interna significativa questa settimana."),
        (" Iran war creating some alliance strain over burden-sharing", " la guerra con l'Iran crea tensioni nell'alleanza sulla ripartizione degli oneri"),
        (" NATO cohesion tested by Iran war response and defense spending demands", " la coesione NATO messa alla prova dalla risposta alla guerra con l'Iran e dalle richieste di spesa per la difesa"),
        (" EU institutional framework and NATO membership provide stability despite global uncertainty", " il quadro istituzionale UE e l'appartenenza a NATO forniscono stabilita nonostante l'incertezza globale"),
        (" GDP growth slowing but not contracting", " crescita del PIL in rallentamento ma non in contrazione"),
        (" Oil shock and trade uncertainty create headwinds partially offset by ECB stability", " Lo shock petrolifero e l'incertezza commerciale creano venti contrari parzialmente compensati dalla stabilita della ECB"),
        (" inflation moderately rising from global oil price shock and tariff-related import cost increases", " inflazione in moderato aumento dallo shock globale del prezzo del petrolio e dall'aumento dei costi di importazione legati ai dazi"),
        (" current account modestly deteriorating from higher energy import costs and trade disruption", " conto corrente in modesto deterioramento per i maggiori costi di importazione energetica e la perturbazione commerciale"),
        (" debt modestly rising from defense spending increases (NATO 5% target pressure) and energy transition costs", " debito in modesto aumento per l'incremento della spesa per la difesa (pressione dall'obiettivo NATO del 5%) e i costi della transizione energetica"),
        (" FDI broadly stable with modest caution from global risk-off sentiment and trade disruption", " IDE sostanzialmente stabili con modesta cautela dal sentimento globale di avversione al rischio e perturbazione commerciale"),
        (" FDI facing headwinds from Section 301 investigation and trade policy uncertainty", " IDE che affrontano venti contrari dall'indagine Section 301 e dall'incertezza sulla politica commerciale"),
        (" appreciating vs USD", " in apprezzamento rispetto al USD"),
        (" appreciating vs weakening USD", " in apprezzamento rispetto al dollaro in indebolimento"),
        (" as ECB holds rates while Fed expected to cut", " poiche la ECB mantiene i tassi mentre la Fed dovrebbe tagliare"),
        (" Dollar weakness broadening", " Debolezza del dollaro in espansione"),
        (" bond yields rising modestly on inflation expectations from oil shock", " rendimenti obbligazionari in modesto aumento sulle aspettative di inflazione dallo shock petrolifero"),
        (" relationships with US deteriorating from Section 301 investigation targeting manufacturing sectors", " relazioni con gli USA in deterioramento per l'indagine Section 301 mirata ai settori manifatturieri"),
        (" relationships with US in deterioramento from Section 301 investigation targeting manufacturing sectors", " relazioni con gli USA in deterioramento per l'indagine Section 301 mirata ai settori manifatturieri"),
        (" on hold at", " in attesa a"),
        (" Oil shock inflation pass-through delays easing cycle", " Il trasferimento dell'inflazione dallo shock petrolifero ritarda il ciclo di allentamento"),
        (" Sterling modestly appreciating vs weakening USD", " La sterlina in modesto apprezzamento rispetto al dollaro in indebolimento"),
        (" BOE policy relatively hawkish", " Politica della BoE relativamente restrittiva"),
        (" Non-Eurozone flexibility", " Flessibilita extra-eurozona"),
        (" facing stagflation dilemma", " di fronte al dilemma della stagflazione"),
        (" Oil shock pushes inflation higher while growth weakens", " Lo shock petrolifero spinge l'inflazione in alto mentre la crescita rallenta"),
        (" March policy meeting critical", " riunione di politica monetaria di marzo critica"),
        (" general strike highlights wage-price spiral risk", " lo sciopero generale evidenzia il rischio di spirale salari-prezzi"),
        (" Protests past 300-day mark", " Proteste oltre la soglia dei 300 giorni"),
        (" EU accession suspended until end of 2028", " Adesione all'UE sospesa fino alla fine del 2028"),
        (" European Parliament did not recognize October 2024 election", " Il Parlamento Europeo non ha riconosciuto le elezioni di ottobre 2024"),
        (" with trend", " con tendenza"),
        (" and stable trend", " e tendenza stabile"),
        ("Overweight energy-efficient companies and defense", "Sovrappesare aziende efficienti dal punto di vista energetico e difesa"),
        ("Underweight industrial commodities consumers", "Sottopesare consumatori di materie prime industriali"),
        (" 10-year yield", " rendimento decennale"),
        (" may offer entry point", " potrebbe offrire un punto di ingresso"),
        (" remains anchored", " rimane ancorato"),
        (" policy rate broadly stable", " tasso di riferimento sostanzialmente stabile"),
        (" Central bank balancing growth and inflation concerns amid global uncertainty", " Banca centrale che bilancia crescita e preoccupazioni sull'inflazione in un contesto di incertezza globale"),
        (" currency supported by commodity export windfall", " valuta sostenuta dal guadagno straordinario dalle esportazioni di materie prime"),
        (" Oil/gas revenue boosting external position", " Entrate da petrolio/gas che rafforzano la posizione esterna"),
        (" bond yields stable to declining on improved fiscal position from commodity windfall", " rendimenti obbligazionari stabili o in calo per il miglioramento della posizione fiscale dal guadagno straordinario dalle materie prime"),
        (" investment risk improving on commodity windfall", " rischio di investimento in miglioramento grazie al guadagno straordinario dalle materie prime"),
        (" Fiscal position strengthening", " Posizione fiscale in rafforzamento"),
        (" Non-Hormuz export routes secure", " Rotte di esportazione non-Hormuz sicure"),
        (" non-Hormuz oil/commodity exports at elevated prices", " esportazioni non-Hormuz di petrolio/materie prime a prezzi elevati"),
        (" oil exporter status shields from energy cost pass-through", " lo status di esportatore di petrolio protegge dal trasferimento dei costi energetici"),
        (" debt ratio improving as commodity windfall boosts government revenue", " rapporto debito in miglioramento poiche il guadagno straordinario dalle materie prime aumenta le entrate pubbliche"),
        (" current account improving as oil/commodity prices surge and non-Hormuz export routes remain secure", " conto corrente in miglioramento poiche i prezzi di petrolio/materie prime salgono e le rotte di esportazione non-Hormuz rimangono sicure"),
        (" Trade surplus widening", " Surplus commerciale in ampliamento"),
        (" military spending broadly stable relative to GDP", " spesa militare sostanzialmente stabile rispetto al PIL"),
        (" outlook requires monitoring", " prospettive richiedono monitoraggio"),
        (" Frontier market risk applies", " Si applica il rischio di mercato di frontiera"),
        (" Monitor for developments relevant to sector exposure", " Monitorare gli sviluppi rilevanti per l'esposizione settoriale"),
        (" Oil price surge affects all energy importers", " L'impennata del prezzo del petrolio colpisce tutti gli importatori di energia"),
        (" Conditions persist", " Le condizioni persistono"),
        (" conditions persist", " le condizioni persistono"),
        (" with basic coverage only.", " con sola copertura di base."),
        (" with basic coverage.", " con copertura di base."),
        (" data points updated this run", " punti dati aggiornati in questa esecuzione"),
        ("Data quality is high with", "La qualita dei dati e alta con"),
        ("Flagged factors:", "Fattori segnalati:"),
        ("No significant changes this week", "Nessun cambiamento significativo questa settimana"),
    ]

    for en, it in patterns:
        if en in result:
            result = result.replace(en, it)

    return result


def should_translate_key(key):
    """Determine if a key's value should be translated."""
    # Keys whose string values should be translated
    translatable_keys = {
        "country_name", "name",
        "trend_reasoning", "reasoning",
        "executive_summary", "outlook", "investor_implications",
        "data_quality_note", "methodology",
        "title", "description",
        "key_changes", "key_changes_this_week",
        "reason",  # in metadata.active_flags
    }
    return key in translatable_keys


def should_never_translate_key(key):
    """Keys whose values must never be translated."""
    never_translate = {
        "source", "run_id", "country_code", "code", "region",
        "last_updated", "first_loaded", "flagged_at", "trend_updated",
        "generated_at", "confidence", "value", "tier",
        "factor", "factor_path", "previous_value", "new_value",
        "head_of_state_name", "head_of_government_name",
        "head_of_state_title", "head_of_government_title",
        "next_national_election_date",
        "partner_code", "country", "relationship_type", "diplomatic_status",
        "trend", "data_quality", "status",
        "period", "volume_change", "rank",
    }
    return key in never_translate


def translate_value(key, value, parent_key=None):
    """Translate a value based on its key context."""
    if value is None:
        return value

    if isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, str):
        # Never translate these keys
        if should_never_translate_key(key):
            # Special case: translate "reason" in active_flags but keep factor paths
            if key == "reason" and parent_key == "active_flags":
                # These are technical flag reasons - translate them
                return translate_text(value)
            return value

        # Translate these keys
        if should_translate_key(key):
            return translate_text(value)

        # For "value" key: only translate if it's a text string (not a code/number-like string)
        if key == "value":
            # Don't translate rating strings, regime types, status codes, dates
            if any(x in value for x in ["S&P:", "Moody's:", "Fitch:", "non_nuclear", "declared_arsenal",
                                         "full_democracy", "flawed_democracy", "hybrid_regime",
                                         "authoritarian", "free", "partly_free", "not_free",
                                         "fragile", "active_conflict", "stable", "growth", "decrease",
                                         "strong_growth", "strong_decrease",
                                         "2026", "2027", "2028", "2029"]):
                return value
            # Translate country names if the value is a country name
            if value in COUNTRY_NAMES:
                return COUNTRY_NAMES[value]
            # Don't translate short codes or person names
            if len(value) <= 3 or value[0].isupper() and " " not in value:
                return value
            # Translate longer text values
            return translate_text(value)

        return value

    if isinstance(value, list):
        return [translate_value(key, item, parent_key) for item in value]

    if isinstance(value, dict):
        return translate_dict(value, key)

    return value


def translate_dict(d, parent_key=None):
    """Recursively translate a dictionary."""
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = translate_dict(value, key)
        elif isinstance(value, list):
            translated_list = []
            for item in value:
                if isinstance(item, dict):
                    translated_list.append(translate_dict(item, key))
                elif isinstance(item, str):
                    if should_translate_key(parent_key or key):
                        translated_list.append(translate_text(item))
                    else:
                        translated_list.append(item)
                else:
                    translated_list.append(item)
            result[key] = translated_list
        else:
            result[key] = translate_value(key, value, parent_key)
    return result


def translate_country_file(code):
    """Read a country JSON file, translate text fields, write _it.json."""
    input_path = os.path.join(DATA_DIR, f"{code}.json")
    output_path = os.path.join(DATA_DIR, f"{code}_it.json")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Deep copy to avoid modifying original
    translated = copy.deepcopy(data)

    # Translate top-level text fields
    if "country_name" in translated:
        cn = translated["country_name"]
        translated["country_name"] = COUNTRY_NAMES.get(cn, cn)

    if "name" in translated:
        cn = translated["name"]
        translated["name"] = COUNTRY_NAMES.get(cn, cn)

    # Translate executive_summary, outlook, investor_implications, key_changes at top level
    for field in ["executive_summary", "outlook", "investor_implications", "data_quality_note"]:
        if field in translated and isinstance(translated[field], str):
            translated[field] = translate_text(translated[field])

    if "key_changes" in translated and isinstance(translated["key_changes"], list):
        translated["key_changes"] = [translate_text(item) if isinstance(item, str) else item
                                      for item in translated["key_changes"]]

    if "key_changes_this_week" in translated and isinstance(translated["key_changes_this_week"], list):
        translated["key_changes_this_week"] = [translate_text(item) if isinstance(item, str) else item
                                                for item in translated["key_changes_this_week"]]

    # Translate active_alerts
    if "active_alerts" in translated and isinstance(translated["active_alerts"], list):
        for alert in translated["active_alerts"]:
            if isinstance(alert, dict):
                if "title" in alert:
                    alert["title"] = translate_text(alert["title"])
                if "description" in alert:
                    alert["description"] = translate_text(alert["description"])

    # Translate narrative section
    if "narrative" in translated and isinstance(translated["narrative"], dict):
        narr = translated["narrative"]
        for field in ["executive_summary", "outlook", "investor_implications", "data_quality_note"]:
            if field in narr and isinstance(narr[field], str):
                narr[field] = translate_text(narr[field])
        if "key_changes_this_week" in narr and isinstance(narr["key_changes_this_week"], list):
            narr["key_changes_this_week"] = [translate_text(item) if isinstance(item, str) else item
                                              for item in narr["key_changes_this_week"]]

    # Translate trend_reasoning, reasoning, methodology fields throughout the structure
    translated = translate_nested_fields(translated)

    # Translate metadata.active_flags[].reason
    if "metadata" in translated and isinstance(translated["metadata"], dict):
        if "active_flags" in translated["metadata"] and isinstance(translated["metadata"]["active_flags"], list):
            for flag in translated["metadata"]["active_flags"]:
                if isinstance(flag, dict) and "reason" in flag:
                    flag["reason"] = translate_flag_reason(flag["reason"])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    return output_path


def translate_flag_reason(reason):
    """Translate metadata flag reasons - these are mostly technical but have some translatable parts."""
    if not isinstance(reason, str):
        return reason
    # These are technical strings with thresholds - translate key phrases
    result = reason
    result = result.replace("Large % change:", "Variazione % elevata:")
    result = result.replace("Large absolute change:", "Variazione assoluta elevata:")
    result = result.replace("threshold:", "soglia:")
    result = result.replace("Absolute change", "Variazione assoluta")
    result = result.replace("exceeds", "supera")
    result = result.replace("typical", "tipico")
    result = result.replace("Alternative source", "Fonte alternativa")
    result = result.replace("disagrees:", "discorda:")
    result = result.replace("vs primary", "rispetto al primario")
    result = result.replace("diff", "diff")
    result = result.replace("Change", "Variazione")
    result = result.replace("Event context:", "Contesto evento:")
    result = result.replace("has active event triggers", "ha trigger di evento attivi")
    result = result.replace("previous stored value", "valore precedente memorizzato")
    result = result.replace("appears to be", "sembra essere")
    result = result.replace("not", "non")
    result = result.replace("Current", "Il")
    result = result.replace("value is plausible for that index", "valore e plausibile per quell'indice")
    result = result.replace("Data mapping correction needed", "Necessaria correzione della mappatura dati")
    # Translate country names that appear
    for en, it in sorted(COUNTRY_NAMES.items(), key=lambda x: -len(x[0])):
        if en in result:
            result = result.replace(en, it)
    return result


def translate_nested_fields(obj, parent_key=None):
    """Recursively find and translate trend_reasoning, reasoning, methodology fields."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key in ("trend_reasoning", "reasoning") and isinstance(value, str):
                result[key] = translate_text(value)
            elif key == "methodology" and isinstance(value, str):
                result[key] = translate_methodology(value)
            elif isinstance(value, (dict, list)):
                result[key] = translate_nested_fields(value, key)
            else:
                result[key] = value
        return result
    elif isinstance(obj, list):
        return [translate_nested_fields(item, parent_key) for item in obj]
    else:
        return obj


def translate_methodology(text):
    """Translate methodology descriptions."""
    if not isinstance(text, str):
        return text
    result = text
    replacements = {
        "Average of": "Media di",
        "for energy, food, water, minerals": "per energia, cibo, acqua, minerali",
        "capped at": "limitato a",
        "elevated due to active": "elevato a causa di",
        "disruption": "perturbazione",
        "normalized": "normalizzato",
        "Sovereign rating implied spread": "Spread implicito del rating sovrano",
        "adjustments for instability, conflict, sanctions, autocracy": "aggiustamenti per instabilita, conflitto, sanzioni, autocrazia",
        "domestic_energy_production": "produzione_energetica_domestica",
        "domestic_energy_consumption": "consumo_energetico_domestico",
        "maritime_chokepoint_dependency": "dipendenza_da_strozzature_marittime",
        "normalized_trade_openness": "apertura_commerciale_normalizzata",
        "capital_account_openness": "apertura_conto_capitale",
        "stock_market_cap": "capitalizzazione_mercato_azionario",
        "financial_dev_index": "indice_sviluppo_finanziario",
        "ease_of_business": "facilita_di_fare_impresa",
        " economic ": " economico ",
        "military": "militare",
        "technology": "tecnologia",
        "diplomatic": "diplomatico",
        "soft_power": "soft_power",
        "political_risk": "rischio_politico",
        "economic_risk": "rischio_economico",
        "financial_market_risk": "rischio_mercati_finanziari",
        "security_risk": "rischio_sicurezza",
    }
    for en, it in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(en, it)
    return result


def main():
    success = 0
    errors = []

    for code in COUNTRIES:
        try:
            output_path = translate_country_file(code)
            # Validate JSON
            with open(output_path, 'r', encoding='utf-8') as f:
                json.load(f)
            success += 1
            print(f"OK: {code}_it.json")
        except Exception as e:
            errors.append((code, str(e)))
            print(f"ERROR: {code} - {e}")

    print(f"\nCompleted: {success}/{len(COUNTRIES)} files translated successfully")
    if errors:
        print(f"Errors: {len(errors)}")
        for code, err in errors:
            print(f"  {code}: {err}")


if __name__ == "__main__":
    main()
