#!/usr/bin/env python3
"""Build merged article index from daily article indexes.

Reads all daily article_index_{DATE}.json files from data/global/articles/,
merges them into a single index sorted newest-first, trims to 30 days,
and writes to data/chunks/global/article_index.json.

Also copies individual article files to data/chunks/global/articles/.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Project root (two levels up from this script)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ARTICLES_DIR = PROJECT_ROOT / "data" / "global" / "articles"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks" / "global"
CHUNKS_ARTICLES_DIR = CHUNKS_DIR / "articles"

RETENTION_DAYS = 30


def main():
    CHUNKS_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    # Collect all daily indexes
    all_articles = []
    index_files = sorted(ARTICLES_DIR.glob("article_index_*.json"), reverse=True)

    for idx_file in index_files:
        try:
            with open(idx_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: skipping {idx_file.name}: {e}", file=sys.stderr)
            continue

        date_str = data.get("date", "")
        if date_str < cutoff_str:
            continue

        articles = data.get("articles", [])
        all_articles.extend(articles)

    # Sort by published_at descending
    all_articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)

    # Write merged index
    merged = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "retention_days": RETENTION_DAYS,
        "article_count": len(all_articles),
        "articles": all_articles
    }

    out_path = CHUNKS_DIR / "article_index.json"
    with open(out_path, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"Merged article index: {len(all_articles)} articles -> {out_path}")

    # Copy individual article files to chunks
    copied = 0
    for article_file in ARTICLES_DIR.glob("article_*_*.json"):
        if article_file.name.startswith("article_index_"):
            continue
        dest = CHUNKS_ARTICLES_DIR / article_file.name
        shutil.copy2(article_file, dest)
        copied += 1

    print(f"Copied {copied} article files to {CHUNKS_ARTICLES_DIR}")

    # Also write article chunks keyed by article_id for DataLoader compatibility
    for article_file in ARTICLES_DIR.glob("article_*_*.json"):
        if article_file.name.startswith("article_index_"):
            continue
        try:
            with open(article_file) as f:
                art = json.load(f)
            art_id = art.get("article_id", "")
            if art_id:
                id_dest = CHUNKS_ARTICLES_DIR / (art_id + ".json")
                if not id_dest.exists():
                    shutil.copy2(article_file, id_dest)
        except (json.JSONDecodeError, OSError):
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
