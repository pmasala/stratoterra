#!/usr/bin/env python3
"""Extract all translatable text fields from country detail JSON files."""
import json
import os
import sys

DATA_DIR = "/home/user/stratoterra/data/chunks/country-detail"

# Fields that contain translatable text
TEXT_FIELDS = {
    "country_name", "executive_summary", "outlook", "investor_implications",
    "trend_reasoning", "reasoning", "methodology", "data_quality_note",
    "title", "description", "reason", "note"
}

def extract_text(obj, path=""):
    """Recursively extract all translatable text fields."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if k in TEXT_FIELDS and isinstance(v, str) and len(v.strip()) > 0:
                results.append({"path": new_path, "text": v})
            elif isinstance(v, (dict, list)):
                results.extend(extract_text(v, new_path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_path = f"{path}[{i}]"
            results.extend(extract_text(v, new_path))
    return results


def main():
    countries = sorted([f.replace(".json", "") for f in os.listdir(DATA_DIR)
                       if f.endswith(".json") and "_it" not in f])

    # Split into batches
    batch_size = 15
    batches = []
    for i in range(0, len(countries), batch_size):
        batches.append(countries[i:i+batch_size])

    for batch_idx, batch in enumerate(batches):
        batch_data = {}
        for code in batch:
            filepath = os.path.join(DATA_DIR, f"{code}.json")
            with open(filepath) as f:
                data = json.load(f)
            texts = extract_text(data)
            batch_data[code] = texts

        output_path = f"/home/user/stratoterra/staging/translate_batch_{batch_idx}.json"
        with open(output_path, "w") as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)

        # Count texts
        total = sum(len(v) for v in batch_data.values())
        print(f"Batch {batch_idx}: {len(batch)} countries, {total} text fields -> {output_path}")

    print(f"\nTotal batches: {len(batches)}")


if __name__ == "__main__":
    main()
