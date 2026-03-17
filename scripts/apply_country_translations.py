#!/usr/bin/env python3
"""Apply Italian translations back to country detail JSON files."""
import json
import os
import copy

DATA_DIR = "/home/user/stratoterra/data/chunks/country-detail"
STAGING_DIR = "/home/user/stratoterra/staging"


def set_nested(obj, path, value):
    """Set a value at a dot/bracket-notation path in a nested object."""
    parts = []
    i = 0
    current = ""
    while i < len(path):
        if path[i] == '.':
            if current:
                parts.append(current)
            current = ""
        elif path[i] == '[':
            if current:
                parts.append(current)
            current = ""
            j = path.index(']', i)
            parts.append(int(path[i+1:j]))
            i = j
        else:
            current += path[i]
        i += 1
    if current:
        parts.append(current)

    # Navigate to parent
    node = obj
    for p in parts[:-1]:
        if isinstance(p, int):
            node = node[p]
        else:
            node = node[p]

    # Set value
    last = parts[-1]
    if isinstance(last, int):
        node[last] = value
    else:
        node[last] = value


def main():
    total_files = 0
    for batch_idx in range(5):
        translated_path = os.path.join(STAGING_DIR, f"translated_batch_{batch_idx}.json")
        if not os.path.exists(translated_path):
            print(f"Batch {batch_idx}: translated file not found, skipping")
            continue

        with open(translated_path) as f:
            translations = json.load(f)

        for code, text_list in translations.items():
            # Read original file
            src_path = os.path.join(DATA_DIR, f"{code}.json")
            with open(src_path) as f:
                data = json.load(f)

            # Deep copy and apply translations
            translated = copy.deepcopy(data)
            for item in text_list:
                try:
                    set_nested(translated, item["path"], item["text"])
                except (KeyError, IndexError, TypeError) as e:
                    print(f"  Warning: could not set {item['path']} in {code}: {e}")

            # Write _it.json
            out_path = os.path.join(DATA_DIR, f"{code}_it.json")
            with open(out_path, "w") as f:
                json.dump(translated, f, indent=2, ensure_ascii=False)
            total_files += 1

        print(f"Batch {batch_idx}: translated {len(translations)} country files")

    print(f"\nTotal files written: {total_files}")


if __name__ == "__main__":
    main()
