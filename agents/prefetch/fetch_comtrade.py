"""
Fetch bilateral trade data from UN Comtrade API.

Covers: top export/import partners, top traded products,
trade values per bilateral pair.

API docs: https://comtradeapi.un.org/files/v1/app/reference/ListofReferences.json
Free tier: 100 requests/hour, no key needed for preview endpoint.
With key: higher limits.

NOTE (2026-03): The API dropped path-based URLs (/HS/{ISO3}/ALL).
Must use query params with M49 numeric reporter codes
(?reporterCode=842&period=2023).
"""

import logging
import os
import time

from .base_fetcher import BaseFetcher, get_countries_by_tier

logger = logging.getLogger("prefetch.comtrade")

# Comtrade preview endpoint (no key needed, limited data)
PREVIEW_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
# Authenticated endpoint (with key, full data)
DATA_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"

# Map ISO3 to Comtrade M49 numeric reporter codes.
# The preview endpoint requires numeric codes as query params.
ISO3_TO_M49 = {
    "USA": "842", "CHN": "156", "JPN": "392", "DEU": "276", "GBR": "826",
    "FRA": "250", "IND": "356", "ITA": "380", "CAN": "124", "KOR": "410",
    "RUS": "643", "BRA": "076", "AUS": "036", "ESP": "724", "MEX": "484",
    "IDN": "360", "NLD": "528", "SAU": "682", "TUR": "792", "CHE": "756",
    "POL": "616", "SWE": "752", "NOR": "578", "ISR": "376", "ARE": "784",
    "SGP": "702", "TWN": "158", "THA": "764", "MYS": "458", "ZAF": "710",
    "NGA": "566", "EGY": "818", "PAK": "586", "BGD": "050", "VNM": "704",
    "PHL": "608", "COL": "170", "ARG": "032", "CHL": "152", "PER": "604",
    "IRN": "364", "IRQ": "368", "KAZ": "398", "UKR": "804", "ROU": "642",
    "CZE": "203", "GRC": "300", "PRT": "620", "FIN": "246", "IRL": "372",
    "NZL": "554", "QAT": "634", "KWT": "414", "OMN": "512", "MAR": "504",
    "ETH": "231", "KEN": "404", "TZA": "834", "GHA": "288", "CIV": "384",
    "SEN": "686", "AGO": "024", "MOZ": "508", "COD": "180", "MMR": "104",
    "LKA": "144", "UZB": "860", "AZE": "031", "GEO": "268", "SRB": "688",
    "HUN": "348", "BGR": "100", "HRV": "191", "JOR": "400", "LBY": "434",
}

# Reverse lookup: M49 numeric code -> ISO3
M49_TO_ISO3 = {v: k for k, v in ISO3_TO_M49.items()}


class ComtradeFetcher(BaseFetcher):
    source_id = "comtrade"
    output_filename = "comtrade.json"

    def _get_api_key(self) -> str:
        return os.environ.get("COMTRADE_API_KEY", "")

    def _fetch_flow(self, m49: str, flow_code: str, year: str,
                    api_key: str = "") -> list[dict] | None:
        """Fetch one flow (X or M) for a country/year. Returns raw entries."""
        params = {"reporterCode": m49, "period": year, "flowCode": flow_code}
        if api_key:
            params["subscription-key"] = api_key
        result = self.get_json(PREVIEW_URL, params=params, timeout=30)
        if result and result.get("data"):
            return result["data"]
        return None

    def _fetch_country_trade(self, iso3: str, api_key: str = "") -> list[dict]:
        """Fetch trade summary for one country (top partners)."""
        m49 = ISO3_TO_M49.get(iso3)
        if not m49:
            logger.warning("No M49 code for %s — skipping", iso3)
            return []

        # Preview endpoint needs separate requests for exports (X) and
        # imports (M) because the 500-record cap truncates mixed results.
        # Try 2024 first, fall back to 2023.
        export_entries = None
        import_entries = None
        data_year = "2024"
        for year in ["2024", "2023"]:
            export_entries = self._fetch_flow(m49, "X", year, api_key)
            import_entries = self._fetch_flow(m49, "M", year, api_key)
            if export_entries or import_entries:
                data_year = year
                break

        records = []

        # Aggregate exports by partner
        if export_entries:
            by_partner = {}
            for entry in export_entries:
                partner_m49 = str(entry.get("partnerCode", ""))
                partner_iso3 = M49_TO_ISO3.get(partner_m49, "")
                if not partner_iso3 or partner_m49 == "0":
                    continue
                try:
                    value = float(entry.get("primaryValue", 0))
                except (ValueError, TypeError):
                    continue
                by_partner[partner_iso3] = by_partner.get(partner_iso3, 0) + value

            top = sorted(by_partner.items(), key=lambda x: -x[1])[:10]
            total = sum(v for _, v in top) or 1
            for partner, value in top:
                records.append({
                    "country_code": iso3, "partner_code": partner,
                    "flow": "export", "value_usd": value,
                    "pct_of_total": round(value / total * 100, 2),
                    "indicator_name": "top_export_partner",
                    "source": "UN Comtrade", "year": data_year,
                })

        # Aggregate imports by partner
        if import_entries:
            by_partner = {}
            for entry in import_entries:
                partner_m49 = str(entry.get("partnerCode", ""))
                partner_iso3 = M49_TO_ISO3.get(partner_m49, "")
                if not partner_iso3 or partner_m49 == "0":
                    continue
                try:
                    value = float(entry.get("primaryValue", 0))
                except (ValueError, TypeError):
                    continue
                by_partner[partner_iso3] = by_partner.get(partner_iso3, 0) + value

            top = sorted(by_partner.items(), key=lambda x: -x[1])[:10]
            total = sum(v for _, v in top) or 1
            for partner, value in top:
                records.append({
                    "country_code": iso3, "partner_code": partner,
                    "flow": "import", "value_usd": value,
                    "pct_of_total": round(value / total * 100, 2),
                    "indicator_name": "top_import_partner",
                    "source": "UN Comtrade", "year": data_year,
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

        # Sequential with throttling to respect rate limits.
        # Each country makes 2 requests (exports + imports), so throttle
        # more aggressively: pause every 3 countries (~6 requests).
        for i, iso3 in enumerate(priority_countries):
            logger.info("Comtrade %d/%d: %s", i + 1, len(priority_countries), iso3)
            records = self._fetch_country_trade(iso3, api_key)
            all_records.extend(records)

            if not api_key and (i + 1) % 3 == 0:
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
