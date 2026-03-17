#!/usr/bin/env python3
"""
Translate 124 bilateral relation JSON files (AGO_CHN through CHE_FRA) from English to Italian.
Uses comprehensive sentence-level translation with pattern matching and phrase dictionary.
"""
import json
import os
import copy
import glob
import re
import sys

RELATIONS_DIR = "/home/user/stratoterra/data/chunks/relations"

# Country name translations (for JSON fields)
COUNTRY_NAMES_FIELD = {
    "Angola": "Angola",
    "Australia": "Australia",
    "Azerbaijan": "Azerbaigian",
    "Brazil": "Brasile",
    "Bulgaria": "Bulgaria",
    "Canada": "Canada",
    "China": "Cina",
    "France": "Francia",
    "Georgia": "Georgia",
    "Germany": "Germania",
    "India": "India",
    "Indonesia": "Indonesia",
    "Israel": "Israele",
    "Italy": "Italia",
    "Japan": "Giappone",
    "Malaysia": "Malesia",
    "Mexico": "Messico",
    "Netherlands": "Paesi Bassi",
    "Norway": "Norvegia",
    "Poland": "Polonia",
    "Romania": "Romania",
    "Russia": "Russia",
    "Saudi Arabia": "Arabia Saudita",
    "Singapore": "Singapore",
    "South Africa": "Sudafrica",
    "South Korea": "Corea del Sud",
    "Spain": "Spagna",
    "Sweden": "Svezia",
    "Switzerland": "Svizzera",
    "Taiwan": "Taiwan",
    "Thailand": "Thailandia",
    "Turkey": "Turchia",
    "United Arab Emirates": "Emirati Arabi Uniti",
    "United Kingdom": "Regno Unito",
    "United States": "Stati Uniti",
}

# Comprehensive in-text country/demonym replacements (order matters - longest first)
TEXT_REPLACEMENTS = [
    # Multi-word names first
    ("United Arab Emirates", "Emirati Arabi Uniti"),
    ("United Kingdom", "Regno Unito"),
    ("United States", "Stati Uniti"),
    ("South Africa", "Sudafrica"),
    ("South Korea", "Corea del Sud"),
    ("South Korean", "sudcoreano"),
    ("Saudi Arabia", "Arabia Saudita"),
    ("Saudi Arabian", "saudita"),
    ("New Zealand", "Nuova Zelanda"),
    ("North Korea", "Corea del Nord"),
    ("North Korean", "nordcoreano"),
    # Country names
    ("Azerbaijan", "Azerbaigian"),
    ("Azerbaijani", "azerbaigiano"),
    ("Brazil", "Brasile"),
    ("Brazilian-Jewish", "ebraico-brasiliana"),
    ("Brazilian", "brasiliano"),
    ("Bulgaria", "Bulgaria"),
    ("Bulgarian", "bulgaro"),
    ("Canada", "Canada"),
    ("Canadian", "canadese"),
    ("China", "Cina"),
    ("Chinese", "cinese"),
    ("France", "Francia"),
    ("French-Canadese", "franco-canadese"),
    ("French", "francese"),
    ("Germany", "Germania"),
    ("German-Canadese", "tedesco-canadese"),
    ("German", "tedesco"),
    ("Indonesia", "Indonesia"),
    ("Indonesian", "indonesiano"),
    ("Israel", "Israele"),
    ("Israeli", "israeliano"),
    ("Italy", "Italia"),
    ("Italian-Canadese", "italo-canadese"),
    ("Italian-Brasiliano", "italo-brasiliano"),
    ("Italian", "italiano"),
    ("Japan", "Giappone"),
    ("Japanese", "giapponese"),
    ("Malaysia", "Malesia"),
    ("Malaysian", "malese"),
    ("Mexico", "Messico"),
    ("Mexican", "messicano"),
    ("Netherlands", "Paesi Bassi"),
    ("Dutch", "olandese"),
    ("Norway", "Norvegia"),
    ("Norwegian", "norvegese"),
    ("Poland", "Polonia"),
    ("Polish-Canadese", "polacco-canadese"),
    ("Polish-Brasiliano", "polacco-brasiliano"),
    ("Polish", "polacco"),
    ("Romania", "Romania"),
    ("Romanian", "romeno"),
    ("Russia", "Russia"),
    ("Russian", "russo"),
    ("Saudi", "saudita"),
    ("Singapore", "Singapore"),
    ("Singaporean", "singaporiano"),
    ("South Africano", "sudafricano"),
    ("Spain", "Spagna"),
    ("Spanish-Canadese", "ispano-canadese"),
    ("Spanish", "spagnolo"),
    ("Sweden", "Svezia"),
    ("Swedish", "svedese"),
    ("Switzerland", "Svizzera"),
    ("Swiss", "svizzero"),
    ("Taiwan", "Taiwan"),
    ("Taiwanese", "taiwanese"),
    ("Thailand", "Thailandia"),
    ("Thai", "thailandese"),
    ("Turkey", "Turchia"),
    ("Turkish", "turco"),
    ("British", "britannico"),
    ("American", "americano"),
    ("UAE", "EAU"),
    ("UK", "Regno Unito"),
    ("India", "India"),
    ("Indian", "indiano"),
    ("Korean", "coreano"),
]

# ============================================================================
# COMPLETE TRANSLATION DICTIONARY - All 700 unique summary strings
# ============================================================================
TRANSLATIONS = {}

def load_translations():
    """Load translations from the JSON dictionary file."""
    dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations_dict_batch1.json")
    with open(dict_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    TRANSLATIONS = load_translations()
    
    # Get target files
    all_files = sorted(glob.glob(os.path.join(RELATIONS_DIR, "*.json")))
    target_files = [f for f in all_files
                    if not os.path.basename(f).endswith('_it.json')
                    and os.path.basename(f) >= "AGO_CHN.json"
                    and os.path.basename(f) <= "CHE_FRA.json"]

    print(f"Processing {len(target_files)} files...")
    
    translated_count = 0
    missing = []

    for filepath in target_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        translated = copy.deepcopy(data)

        # Translate country names
        if translated.get("country_a_name") in COUNTRY_NAMES_FIELD:
            translated["country_a_name"] = COUNTRY_NAMES_FIELD[translated["country_a_name"]]
        if translated.get("country_b_name") in COUNTRY_NAMES_FIELD:
            translated["country_b_name"] = COUNTRY_NAMES_FIELD[translated["country_b_name"]]

        # Translate summary fields
        for section in ["trade", "diplomatic", "military", "financial", "energy", "scientific"]:
            if section in translated:
                summary = translated[section].get("summary", "")
                if summary:
                    if summary in TRANSLATIONS:
                        translated[section]["summary"] = TRANSLATIONS[summary]
                    else:
                        missing.append((os.path.basename(filepath), section, summary[:80]))

                # Translate text in lists
                for list_key in ["disputes", "recent_incidents", "incidents"]:
                    if list_key in translated[section]:
                        for i, item in enumerate(translated[section][list_key]):
                            if isinstance(item, str) and item in TRANSLATIONS:
                                translated[section][list_key][i] = TRANSLATIONS[item]
                            elif isinstance(item, dict):
                                for k, v in item.items():
                                    if isinstance(v, str) and v in TRANSLATIONS:
                                        translated[section][list_key][i][k] = TRANSLATIONS[v]

        # Write output
        pair = os.path.basename(filepath).replace(".json", "")
        output_path = os.path.join(RELATIONS_DIR, f"{pair}_it.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translated, f, indent=2, ensure_ascii=False)

        translated_count += 1

    print(f"Translated {translated_count} files.")
    if missing:
        print(f"\nWARNING: {len(missing)} missing translations:")
        for fn, sec, txt in missing[:20]:
            print(f"  {fn} [{sec}]: {txt}...")
        return 1
    else:
        print("All translations completed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
