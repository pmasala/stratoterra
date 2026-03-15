#!/usr/bin/env python3
"""
Run all pre-fetch scripts and produce a consolidated summary.

Usage:
    python -m agents.prefetch.run_all           # Run all fetchers
    python -m agents.prefetch.run_all worldbank  # Run specific fetcher
    python -m agents.prefetch.run_all --no-key   # Skip fetchers that need API keys

Run from project root: python -m agents.prefetch.run_all
"""

import argparse
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.prefetch.fetch_worldbank import WorldBankFetcher
from agents.prefetch.fetch_imf import IMFFetcher
from agents.prefetch.fetch_gdelt import GDELTFetcher
from agents.prefetch.fetch_fx_commodities import FXCommoditiesFetcher
from agents.prefetch.fetch_acled import ACLEDFetcher
from agents.prefetch.fetch_eia import EIAFetcher
from agents.prefetch.fetch_comtrade import ComtradeFetcher

logger = logging.getLogger("prefetch.runner")

# Fetchers ordered by priority. The first group needs no API keys.
FETCHER_REGISTRY = {
    # No API key required
    "worldbank": {"class": WorldBankFetcher, "needs_key": False, "group": "no_key"},
    "imf": {"class": IMFFetcher, "needs_key": False, "group": "no_key"},
    "gdelt": {"class": GDELTFetcher, "needs_key": False, "group": "no_key"},
    "fx_commodities": {"class": FXCommoditiesFetcher, "needs_key": False, "group": "no_key"},
    # API key required (free registration)
    "acled": {"class": ACLEDFetcher, "needs_key": True, "group": "with_key"},
    "eia": {"class": EIAFetcher, "needs_key": True, "group": "with_key"},
    "comtrade": {"class": ComtradeFetcher, "needs_key": True, "group": "with_key"},
}


def run_fetcher(name: str, config: dict) -> dict:
    """Run a single fetcher and return its result summary."""
    fetcher = config["class"]()
    result = fetcher.execute()
    return {
        "source": name,
        "records": len(result.get("records", [])),
        "errors": len(result.get("errors", [])),
        "fallback": result.get("_fallback", False),
        "elapsed": result.get("stats", {}).get("elapsed_seconds", 0),
    }


def main():
    parser = argparse.ArgumentParser(description="Run Stratoterra pre-fetch scripts")
    parser.add_argument("sources", nargs="*", help="Specific sources to fetch (default: all)")
    parser.add_argument("--no-key", action="store_true",
                        help="Skip sources that require API keys")
    parser.add_argument("--parallel", action="store_true", default=True,
                        help="Run fetchers in parallel (default)")
    parser.add_argument("--sequential", action="store_true",
                        help="Run fetchers sequentially")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Load .env if available
    try:
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded .env from %s", env_path)
    except ImportError:
        pass

    # Determine which fetchers to run
    to_run = {}
    if args.sources:
        for name in args.sources:
            if name in FETCHER_REGISTRY:
                to_run[name] = FETCHER_REGISTRY[name]
            else:
                logger.error("Unknown source: %s (available: %s)",
                             name, ", ".join(FETCHER_REGISTRY.keys()))
                sys.exit(1)
    else:
        for name, config in FETCHER_REGISTRY.items():
            if args.no_key and config["needs_key"]:
                logger.info("Skipping %s (needs API key)", name)
                continue
            to_run[name] = config

    logger.info("Running %d fetchers: %s", len(to_run), ", ".join(to_run.keys()))
    start = time.monotonic()
    results = []

    if args.sequential or len(to_run) == 1:
        for name, config in to_run.items():
            result = run_fetcher(name, config)
            results.append(result)
    else:
        # Run no-key fetchers in parallel, then key-based (some have rate limits)
        no_key = {n: c for n, c in to_run.items() if not c["needs_key"]}
        with_key = {n: c for n, c in to_run.items() if c["needs_key"]}

        # Parallel: no-key group
        if no_key:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(run_fetcher, n, c): n
                    for n, c in no_key.items()
                }
                for f in as_completed(futures):
                    name = futures[f]
                    try:
                        results.append(f.result())
                    except Exception as e:
                        logger.error("%s crashed: %s", name, e)
                        results.append({
                            "source": name, "records": 0,
                            "errors": 1, "fallback": False,
                            "elapsed": 0, "crash": str(e),
                        })

        # Sequential: key-based group (respect rate limits)
        for name, config in with_key.items():
            try:
                results.append(run_fetcher(name, config))
            except Exception as e:
                logger.error("%s crashed: %s", name, e)
                results.append({
                    "source": name, "records": 0,
                    "errors": 1, "fallback": False,
                    "elapsed": 0, "crash": str(e),
                })

    total_elapsed = round(time.monotonic() - start, 1)

    # Write summary report
    summary = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_elapsed_seconds": total_elapsed,
        "fetchers_run": len(results),
        "total_records": sum(r["records"] for r in results),
        "total_errors": sum(r["errors"] for r in results),
        "fallbacks_used": sum(1 for r in results if r.get("fallback")),
        "results": results,
    }

    summary_path = PROJECT_ROOT / "staging" / "prefetched" / "_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Print results table
    print(f"\n{'Source':<20} {'Records':>8} {'Errors':>8} {'Fallback':>10} {'Time':>8}")
    print("-" * 58)
    for r in results:
        fb = "YES" if r.get("fallback") else ""
        print(f"{r['source']:<20} {r['records']:>8} {r['errors']:>8} {fb:>10} {r['elapsed']:>7.1f}s")
    print("-" * 58)
    print(f"{'TOTAL':<20} {summary['total_records']:>8} {summary['total_errors']:>8} "
          f"{summary['fallbacks_used']:>10} {total_elapsed:>7.1f}s")

    if summary["total_errors"] > 0:
        print(f"\nWarning: {summary['total_errors']} errors occurred. "
              f"Check staging/prefetched/_summary.json for details.")

    # Only fail if we got no data at all or a fetcher crashed.
    # API errors that still produced partial data (or used fallback)
    # should not block the CI pipeline.
    has_crashes = any(r.get("crash") for r in results)
    if has_crashes:
        return 1
    if summary["total_records"] == 0:
        print("\nFATAL: No records obtained from any source.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
