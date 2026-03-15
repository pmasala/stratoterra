"""
Fetch energy data from US Energy Information Administration (EIA) API v2.

Covers: oil/gas/coal production and consumption, electricity generation,
renewable energy capacity by country.

API docs: https://www.eia.gov/opendata/documentation.php
Requires free API key (register at eia.gov/opendata).
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_fetcher import BaseFetcher, get_all_country_codes

logger = logging.getLogger("prefetch.eia")

API_BASE = "https://api.eia.gov/v2"

# EIA series groups to fetch
# EIA uses its own country codes (mostly ISO2 but with exceptions)
SERIES_CONFIGS = [
    {
        "id": "petroleum_production",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "57",  # Crude oil production
            "facets[activityId][]": "1",   # Production
            "facets[unit][]": "TBPD",      # Thousand barrels per day
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "oil_production_kbpd",
    },
    {
        "id": "petroleum_consumption",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "5",   # Petroleum products
            "facets[activityId][]": "2",   # Consumption
            "facets[unit][]": "TBPD",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "oil_consumption_kbpd",
    },
    {
        "id": "natural_gas_production",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "26",  # Dry natural gas
            "facets[activityId][]": "1",   # Production
            "facets[unit][]": "BCF",       # Billion cubic feet
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "natgas_production_bcf",
    },
    {
        "id": "natural_gas_consumption",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "26",
            "facets[activityId][]": "2",
            "facets[unit][]": "BCF",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "natgas_consumption_bcf",
    },
    {
        "id": "coal_production",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "7",   # Coal
            "facets[activityId][]": "1",
            "facets[unit][]": "MT",        # Thousand metric tons
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "coal_production_mt",
    },
    {
        "id": "electricity_generation",
        "route": "/international/data/",
        "params": {
            "frequency": "annual",
            "data[0]": "value",
            "facets[productId][]": "2",   # Electricity
            "facets[activityId][]": "12",  # Generation
            "facets[unit][]": "BKWH",      # Billion kilowatt-hours
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "500",
        },
        "indicator_name": "electricity_generation_bkwh",
    },
]


class EIAFetcher(BaseFetcher):
    source_id = "eia"
    output_filename = "eia.json"

    def _get_api_key(self) -> str:
        return os.environ.get("EIA_API_KEY", "")

    def _fetch_series(self, config: dict, api_key: str) -> list[dict]:
        """Fetch one series from the EIA international data API."""
        url = f"{API_BASE}{config['route']}"
        params = dict(config["params"])
        params["api_key"] = api_key

        data = self.get_json(url, params=params, timeout=30)
        if not data or "response" not in data:
            return []

        response = data["response"]
        entries = response.get("data", [])

        tracked = set(get_all_country_codes())

        records = []
        # Keep most recent year per country
        best = {}
        for entry in entries:
            # EIA international endpoint returns ISO3 country codes
            iso3 = entry.get("countryRegionId", "")

            if iso3 not in tracked:
                continue

            value = entry.get("value")
            if value is None:
                continue

            try:
                value = float(value)
            except (ValueError, TypeError):
                continue

            period = entry.get("period", "")
            key = iso3
            if key not in best or period > best[key]["year"]:
                best[key] = {
                    "country_code": iso3,
                    "indicator_name": config["indicator_name"],
                    "value": value,
                    "year": period,
                    "unit": entry.get("unit", ""),
                    "source": "US EIA",
                    "series_id": config["id"],
                }

        return list(best.values())

    def run(self) -> dict:
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("EIA_API_KEY not set — skipping live fetch")
            return self.build_envelope([], skipped=[{
                "reason": "EIA_API_KEY not set in .env",
            }])

        all_records = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for config in SERIES_CONFIGS:
                f = executor.submit(self._fetch_series, config, api_key)
                futures[f] = config["id"]

            for future in as_completed(futures):
                series_id = futures[future]
                try:
                    records = future.result()
                    all_records.extend(records)
                    logger.info("EIA %s: %d records", series_id, len(records))
                except Exception as e:
                    logger.error("EIA %s failed: %s", series_id, e)
                    self.errors.append({"series": series_id, "error": str(e)})

        countries = set(r["country_code"] for r in all_records)
        return self.build_envelope(all_records, extra={
            "summary": {
                "total_records": len(all_records),
                "countries_covered": len(countries),
                "series_fetched": [c["id"] for c in SERIES_CONFIGS],
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from dotenv import load_dotenv
    load_dotenv()
    fetcher = EIAFetcher()
    result = fetcher.execute()
    print(f"EIA: {len(result.get('records', []))} records")
    return result


if __name__ == "__main__":
    main()
