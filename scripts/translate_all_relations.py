#!/usr/bin/env python3
"""
Translate all bilateral relation JSON files from English to Italian.
Uses comprehensive country name translation and text field translation.
"""
import json
import os
import copy
import re

RELATIONS_DIR = "/home/user/stratoterra/data/chunks/relations"

COUNTRY_NAMES_EN_IT = {
    "Angola": "Angola", "United Arab Emirates": "Emirati Arabi Uniti",
    "Argentina": "Argentina", "Australia": "Australia", "Azerbaijan": "Azerbaigian",
    "Bangladesh": "Bangladesh", "Bulgaria": "Bulgaria", "Brazil": "Brasile",
    "Canada": "Canada", "Switzerland": "Svizzera", "Chile": "Cile",
    "China": "Cina", "Côte d'Ivoire": "Costa d'Avorio", "DR Congo": "RD Congo",
    "Colombia": "Colombia", "Czech Republic": "Repubblica Ceca", "Czechia": "Repubblica Ceca",
    "Germany": "Germania", "Egypt": "Egitto", "Spain": "Spagna",
    "Ethiopia": "Etiopia", "Finland": "Finlandia", "France": "Francia",
    "United Kingdom": "Regno Unito", "Georgia": "Georgia", "Ghana": "Ghana",
    "Greece": "Grecia", "Croatia": "Croazia", "Hungary": "Ungheria",
    "Indonesia": "Indonesia", "India": "India", "Ireland": "Irlanda",
    "Iran": "Iran", "Iraq": "Iraq", "Israel": "Israele", "Italy": "Italia",
    "Jordan": "Giordania", "Japan": "Giappone", "Kazakhstan": "Kazakistan",
    "Kenya": "Kenya", "South Korea": "Corea del Sud", "Korea": "Corea del Sud",
    "Kuwait": "Kuwait", "Libya": "Libia", "Sri Lanka": "Sri Lanka",
    "Morocco": "Marocco", "Mexico": "Messico", "Myanmar": "Myanmar",
    "Mozambique": "Mozambico", "Malaysia": "Malesia", "Nigeria": "Nigeria",
    "Netherlands": "Paesi Bassi", "Norway": "Norvegia", "New Zealand": "Nuova Zelanda",
    "Oman": "Oman", "Pakistan": "Pakistan", "Peru": "Perù", "Philippines": "Filippine",
    "Poland": "Polonia", "Portugal": "Portogallo", "Qatar": "Qatar",
    "Romania": "Romania", "Russia": "Russia", "Saudi Arabia": "Arabia Saudita",
    "Senegal": "Senegal", "Singapore": "Singapore", "Serbia": "Serbia",
    "Sweden": "Svezia", "Thailand": "Thailandia", "Turkey": "Turchia",
    "Taiwan": "Taiwan", "Tanzania": "Tanzania", "Ukraine": "Ucraina",
    "United States": "Stati Uniti", "Uzbekistan": "Uzbekistan", "Vietnam": "Vietnam",
    "South Africa": "Sudafrica",
    # Additional forms
    "UK": "Regno Unito", "US": "Stati Uniti", "UAE": "EAU",
    "Republic of Korea": "Repubblica di Corea",
}

# Exact match translations for common phrases
EXACT_TRANSLATIONS = {
    "Diplomatic relations are normal.": "Le relazioni diplomatiche sono normali.",
    "Diplomatic relations are strained.": "Le relazioni diplomatiche sono tese.",
    "Limited military cooperation.": "Cooperazione militare limitata.",
    "Allied security cooperation.": "Cooperazione di sicurezza alleata.",
    "Financial linkages proportional to bilateral trade volume.": "Legami finanziari proporzionali al volume degli scambi commerciali bilaterali.",
    "Energy trade data not separately tracked for this pair.": "Dati sul commercio energetico non tracciati separatamente per questa coppia.",
    "Scientific collaboration data not tracked for this pair.": "Dati sulla collaborazione scientifica non tracciati per questa coppia.",
    "No significant bilateral energy trade.": "Nessun commercio energetico bilaterale significativo.",
    "No significant military relationship.": "Nessuna relazione militare significativa.",
    "No significant military relationship. Occasional exchanges at multilateral defence forums.": "Nessuna relazione militare significativa. Scambi occasionali in forum di difesa multilaterali.",
    "Normal diplomatic relations.": "Relazioni diplomatiche normali.",
    "Normal diplomatic ties.": "Legami diplomatici normali.",
    "Strained relations.": "Relazioni tese.",
    "No direct energy trade relationship.": "Nessun rapporto commerciale energetico diretto.",
    "Limited financial linkages.": "Legami finanziari limitati.",
    "Limited scientific collaboration.": "Collaborazione scientifica limitata.",
    "Growing scientific collaboration.": "Collaborazione scientifica in crescita.",
    "No significant scientific collaboration.": "Nessuna collaborazione scientifica significativa.",
    "No significant financial linkages.": "Nessun legame finanziario significativo.",
    "Minimal military ties.": "Legami militari minimi.",
    "No military cooperation.": "Nessuna cooperazione militare.",
    "No formal military relationship.": "Nessuna relazione militare formale.",
    "Moderate financial linkages.": "Legami finanziari moderati.",
    "Limited energy trade.": "Commercio energetico limitato.",
    "Limited bilateral trade.": "Commercio bilaterale limitato.",
}

# Word/phrase-level translation dictionary
TERM_DICT = {
    # Geopolitical
    "bilateral trade": "scambi commerciali bilaterali",
    "trade relations": "relazioni commerciali",
    "diplomatic relations": "relazioni diplomatiche",
    "military cooperation": "cooperazione militare",
    "defense cooperation": "cooperazione nella difesa",
    "defence cooperation": "cooperazione nella difesa",
    "security cooperation": "cooperazione di sicurezza",
    "financial linkages": "legami finanziari",
    "energy trade": "commercio energetico",
    "scientific collaboration": "collaborazione scientifica",
    "arms transfers": "trasferimenti di armi",
    "joint exercises": "esercitazioni congiunte",
    "joint military exercises": "esercitazioni militari congiunte",
    "defense ties": "legami di difesa",
    "defence ties": "legami di difesa",
    "trade volume": "volume degli scambi",
    "trade balance": "bilancia commerciale",
    "trade surplus": "surplus commerciale",
    "trade deficit": "deficit commerciale",
    "trade agreement": "accordo commerciale",
    "free trade agreement": "accordo di libero scambio",
    "bilateral relations": "relazioni bilaterali",
    "diplomatic ties": "legami diplomatici",
    "economic ties": "legami economici",
    "strategic partnership": "partenariato strategico",
    "comprehensive partnership": "partenariato globale",
    "mutual defense": "difesa reciproca",
    "mutual defence": "difesa reciproca",
    "peace treaty": "trattato di pace",
    "ceasefire": "cessate il fuoco",
    "sanctions": "sanzioni",
    "embargo": "embargo",
    "territorial dispute": "disputa territoriale",
    "border dispute": "disputa di confine",
    "sovereignty": "sovranità",
    "annexation": "annessione",
    "occupation": "occupazione",
    "peacekeeping": "mantenimento della pace",
    "humanitarian aid": "aiuti umanitari",
    "foreign aid": "aiuti esteri",
    "development aid": "aiuti allo sviluppo",
    "investment": "investimento",
    "foreign direct investment": "investimenti diretti esteri",
    "sovereign wealth fund": "fondo sovrano",
    "sovereign wealth funds": "fondi sovrani",
    "central bank": "banca centrale",
    "interest rate": "tasso d'interesse",
    "exchange rate": "tasso di cambio",
    "inflation": "inflazione",
    "recession": "recessione",
    "GDP": "PIL",
    "gross domestic product": "prodotto interno lordo",
    # Commodities
    "crude oil": "petrolio greggio",
    "natural gas": "gas naturale",
    "LNG": "GNL",
    "liquefied natural gas": "gas naturale liquefatto",
    "oil exports": "esportazioni di petrolio",
    "oil imports": "importazioni di petrolio",
    "petroleum": "petrolio",
    "refined petroleum": "petrolio raffinato",
    "agricultural products": "prodotti agricoli",
    "manufactured goods": "beni manufatti",
    "raw materials": "materie prime",
    "minerals": "minerali",
    "rare earths": "terre rare",
    "semiconductors": "semiconduttori",
    "machinery": "macchinari",
    "chemicals": "prodotti chimici",
    "textiles": "tessuti",
    "automotive": "automotive",
    "vehicles": "veicoli",
    "electronics": "elettronica",
    "pharmaceuticals": "farmaceutici",
    "weapons": "armi",
    "defense equipment": "equipaggiamento militare",
    "defence equipment": "equipaggiamento militare",
    # Organizations
    "European Union": "Unione Europea",
    "United Nations": "Nazioni Unite",
    "African Union": "Unione Africana",
    "Arab League": "Lega Araba",
    "Gulf Cooperation Council": "Consiglio di Cooperazione del Golfo",
    "World Trade Organization": "Organizzazione Mondiale del Commercio",
    "International Monetary Fund": "Fondo Monetario Internazionale",
    "World Bank": "Banca Mondiale",
    # Relations
    "normal": "normali",
    "strained": "tese",
    "friendly": "amichevoli",
    "hostile": "ostili",
    "neutral": "neutrale",
    "warm": "cordiali",
    "cool": "fredde",
    "tense": "tese",
    "frozen": "congelate",
    "improving": "in miglioramento",
    "deteriorating": "in deterioramento",
    "stable": "stabili",
    "growing": "in crescita",
    "declining": "in declino",
    "significant": "significativo",
    "substantial": "sostanziale",
    "modest": "modesto",
    "limited": "limitato",
    "minimal": "minimo",
    "strong": "forte",
    "weak": "debole",
    "robust": "robusto",
    "complex": "complesso",
    "complicated": "complicato",
    "contentious": "controverso",
    # Actions/events
    "exports": "esporta",
    "imports": "importa",
    "invests": "investe",
    "supplies": "fornisce",
    "purchases": "acquista",
    "maintains": "mantiene",
    "supports": "sostiene",
    "opposes": "si oppone a",
    "recognizes": "riconosce",
    "condemns": "condanna",
    "cooperation": "cooperazione",
    "collaboration": "collaborazione",
    "partnership": "partenariato",
    "alliance": "alleanza",
    "rivalry": "rivalità",
    "competition": "competizione",
    "conflict": "conflitto",
    "tension": "tensione",
    "dispute": "disputa",
    "agreement": "accordo",
    "treaty": "trattato",
    "negotiations": "negoziati",
    "summit": "vertice",
    "talks": "colloqui",
}


def translate_country_name(name):
    """Translate a country name to Italian."""
    if name in COUNTRY_NAMES_EN_IT:
        return COUNTRY_NAMES_EN_IT[name]
    return name


def translate_text(text):
    """Translate a text field to Italian using exact matches and term replacement."""
    if not text or not isinstance(text, str):
        return text

    text = text.strip()

    # Try exact match first
    if text in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[text]

    # Check for "Bilateral trade between X and Y valued at approximately $N" pattern
    m = re.match(r'^Bilateral trade between (.+?) and (.+?) valued at approximately \$(.+?) USD\.$', text)
    if m:
        c1 = translate_country_name(m.group(1))
        c2 = translate_country_name(m.group(2))
        val = m.group(3)
        return f"Scambi commerciali bilaterali tra {c1} e {c2} per un valore di circa ${val} USD."

    # For longer text, do country name + term replacement
    result = text
    # Replace country names (longer names first to avoid partial matches)
    for en, it in sorted(COUNTRY_NAMES_EN_IT.items(), key=lambda x: -len(x[0])):
        if en in result:
            result = result.replace(en, it)

    return result


def translate_relation_file(filepath):
    """Translate a single relation JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    translated = copy.deepcopy(data)

    # Translate country names
    if "country_a_name" in translated:
        translated["country_a_name"] = translate_country_name(translated["country_a_name"])
    if "country_b_name" in translated:
        translated["country_b_name"] = translate_country_name(translated["country_b_name"])

    # Translate summary fields in each section
    for section in ["trade", "diplomatic", "military", "financial", "energy", "scientific"]:
        if section in translated and "summary" in translated[section]:
            translated[section]["summary"] = translate_text(translated[section]["summary"])

        # Translate disputes and recent_incidents if present
        if section in translated:
            if "disputes" in translated[section]:
                for i, d in enumerate(translated[section]["disputes"]):
                    if isinstance(d, str):
                        translated[section]["disputes"][i] = translate_text(d)
                    elif isinstance(d, dict):
                        for k in ["description", "summary", "title"]:
                            if k in d:
                                d[k] = translate_text(d[k])
            if "recent_incidents" in translated[section]:
                for i, inc in enumerate(translated[section]["recent_incidents"]):
                    if isinstance(inc, str):
                        translated[section]["recent_incidents"][i] = translate_text(inc)
                    elif isinstance(inc, dict):
                        for k in ["description", "summary", "title"]:
                            if k in inc:
                                inc[k] = translate_text(inc[k])

    # Translate relationship_type
    rel_type_map = {
        "neutral": "neutrale",
        "friendly": "amichevole",
        "allied": "alleato",
        "hostile": "ostile",
        "strained": "teso",
        "rival": "rivale",
        "complex": "complesso",
    }
    if "relationship_type" in translated:
        rt = translated["relationship_type"]
        translated["relationship_type"] = rel_type_map.get(rt, rt)

    return translated


def main():
    files = sorted([f for f in os.listdir(RELATIONS_DIR)
                   if f.endswith('.json') and '_it' not in f and f != 'relation_index.json'])

    print(f"Processing {len(files)} relation files...")
    count = 0
    for filename in files:
        src_path = os.path.join(RELATIONS_DIR, filename)
        out_path = os.path.join(RELATIONS_DIR, filename.replace('.json', '_it.json'))

        try:
            translated = translate_relation_file(src_path)
            with open(out_path, 'w') as f:
                json.dump(translated, f, indent=2, ensure_ascii=False)
            count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Done. Translated {count}/{len(files)} files.")


if __name__ == "__main__":
    main()
