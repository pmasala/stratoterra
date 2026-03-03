#!/usr/bin/env python3
"""
Enumerate all 435 Tier 1 bilateral pairs and report which are missing.
Usage: python3 agents/scripts/generate_missing_relations.py
"""

import os
import itertools
import json

T1_COUNTRIES = [
    "ARE", "AUS", "BRA", "CAN", "CHE", "CHN", "DEU", "ESP", "FRA", "GBR",
    "IDN", "IND", "ISR", "ITA", "JPN", "KOR", "MEX", "MYS", "NLD", "NOR",
    "POL", "RUS", "SAU", "SGP", "SWE", "THA", "TUR", "TWN", "USA", "ZAF",
]

CHUNKS_DIR = "data/chunks/relations"
RELATIONS_DIR = "data/relations"

all_pairs = [f"{a}_{b}" for a, b in itertools.combinations(T1_COUNTRIES, 2)]
assert len(all_pairs) == 435, f"Expected 435 pairs, got {len(all_pairs)}"

missing_chunks = [p for p in all_pairs if not os.path.exists(f"{CHUNKS_DIR}/{p}.json")]
missing_relations = [p for p in all_pairs if not os.path.exists(f"{RELATIONS_DIR}/{p}.json")]

print(f"Total T1 pairs: {len(all_pairs)}")
print(f"In chunks/relations: {len(all_pairs) - len(missing_chunks)}/{len(all_pairs)}")
print(f"In relations:        {len(all_pairs) - len(missing_relations)}/{len(all_pairs)}")
print()

if missing_chunks:
    print(f"Missing from chunks ({len(missing_chunks)}):")
    for p in missing_chunks:
        print(f"  {p}")
else:
    print("All 435 pairs present in chunks/relations/")

if missing_relations:
    print(f"\nMissing from relations ({len(missing_relations)}):")
    for p in missing_relations:
        print(f"  {p}")
else:
    print("All 435 pairs present in relations/")
