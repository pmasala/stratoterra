"""
Fetch bilateral trade data from UN Comtrade API.

Covers: top export/import partners, top traded products,
trade values per bilateral pair.

API docs: https://comtradeapi.un.org/files/v1/app/reference/ListofReferences.json
Free tier: 100 requests/hour, no key needed for preview endpoint.
With key: higher limits.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_fetcher import BaseFetcher, get_countries_by_tier, ISO3_TO_ISO2

logger = logging.getLogger("prefetch.comtrade")

# Comtrade preview endpoint (no key needed, limited data)
PREVIEW_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
# Authenticated endpoint (with key, full data)
DATA_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"

# Map ISO3 to Comtrade reporter codes (M49 numeric codes)
# Comtrade accepts ISO3 in the preview endpoint
ISO3_TO_M49 = {
    "USA": "842", "CHN": "156", "JPN": "392", "DEU": "276", "GBR": "826",
    "FRA": "250", "IND": "356", "ITA": "380", "CAN": "124", "KOR": "410",
    "RUS": "643", "BRA": "076", "AUS": "036", "ESP": "724", "MEX": "484",
    "IDN": "360", "NLD": "528", "SAU": "682", "TUR": "792", "CHE": "756",
    "POL": "616", "SWE": "752", "NOR": "578", "ISR": "376", "ARE": "784",
    "SGP": "702", "TWN": "158", "THA": "764", "MYS": "458", "ZAF": "710",
}


class ComtradeFetcher(BaseFetcher):
    source_id = "comtrade"
    output_filename = "comtrade.json"

    def _get_api_key(self) -> str:
        return os.environ.get("COMTRADE_API_KEY", "")

    def _fetch_country_trade(self, iso3: str, api_key: str = "") -> list[dict]:
        """Fetch trade summary for one country (top partners)."""
        # Use preview endpoint (no key, limited but sufficient)
        url = f"{PREVIEW_URL}/{iso3}/ALL"
        params = {
            "period": "2024",
            "motCode": "0",  # All modes of transport
        }
        if api_key:
            params["subscription-key"] = api_key

        data = self.get_json(url, params=params, timeout=30)
        if not data or "data" not in data:
            return []

        records = []
        entries = data.get("data", [])

        # Aggregate by partner country
        exports_by_partner = {}
        imports_by_partner = {}

        for entry in entries:
            partner = entry.get("partnerISO3", "") or entry.get("partnerCode", "")
            flow_code = entry.get("flowCode", "")
            value = entry.get("primaryValue", 0)

            if not partner or partner == "WLD":
                continue

            try:
                value = float(value)
            except (ValueError, TypeError):
                continue

            if flow_code == "X":  # Export
                exports_by_partner[partner] = exports_by_partner.get(partner, 0) + value
            elif flow_code == "M":  # Import
                imports_by_partner[partner] = imports_by_partner.get(partner, 0) + value

        # Top 10 export partners
        top_exports = sorted(exports_by_partner.items(), key=lambda x: -x[1])[:10]
        total_exports = sum(v for _, v in top_exports) or 1
        for partner, value in top_exports:
            records.append({
                "country_code": iso3,
                "partner_code": partner,
                "flow": "export",
                "value_usd": value,
                "pct_of_total": round(value / total_exports * 100, 2),
                "indicator_name": "top_export_partner",
                "source": "UN Comtrade",
                "year": "2024",
            })

        # Top 10 import partners
        top_imports = sorted(imports_by_partner.items(), key=lambda x: -x[1])[:10]
        total_imports = sum(v for _, v in top_imports) or 1
        for partner, value in top_imports:
            records.append({
                "country_code": iso3,
                "partner_code": partner,
                "flow": "import",
                "value_usd": value,
                "pct_of_total": round(value / total_imports * 100, 2),
                "indicator_name": "top_import_partner",
                "source": "UN Comtrade",
                "year": "2024",
            })

        return records

    def run(self) -> dict:
        api_key = self._get_api_key()
        tiers = get_countries_by_tier()
        all_records = []

        # Fetch Tier 1 and Tier 2 countries (55 total)
        # Rate limit: 100 req/hour for free tier, so we throttle
        priority_countries = []
        for tier_name in ["tier_1", "tier_2"]:
            for c in tiers[tier_name]:
                priority_countries.append(c["code"])

        # Sequential with throttling to respect rate limits
        for i, iso3 in enumerate(priority_countries):
            logger.info("Comtrade %d/%d: %s", i + 1, len(priority_countries), iso3)
            records = self._fetch_country_trade(iso3, api_key)
            all_records.extend(records)

            # Throttle: ~2 requests per second for free tier
            if not api_key and (i + 1) % 5 == 0:
                time.sleep(2)

        countries = set(r["country_code"] for r in all_records)
        return self.build_envelope(all_records, extra={
            "summary": {
                "total_records": len(all_records),
                "countries_covered": len(countries),
                "has_api_key": bool(api_key),
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from dotenv import load_dotenv
    load_dotenv()
    fetcher = ComtradeFetcher()
    result = fetcher.execute()
    print(f"Comtrade: {len(result.get('records', []))} records")
    return result


if __name__ == "__main__":
    main()
