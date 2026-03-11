"""
Fetch IMF World Economic Outlook (WEO) data via DataMapper API.

Covers: GDP forecasts, inflation forecasts, unemployment forecasts,
fiscal balance, current account — forward-looking data that
complements World Bank's historical data.

API: https://www.imf.org/external/datamapper/api/
No API key required.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_fetcher import BaseFetcher, get_all_country_codes

logger = logging.getLogger("prefetch.imf")

BASE_URL = "https://www.imf.org/external/datamapper/api/v1"

# WEO indicator codes
INDICATORS = {
    "NGDPD": "gdp_nominal_usd_bn",        # GDP, current prices (USD bn)
    "NGDP_RPCH": "gdp_real_growth_pct",    # GDP, real growth %
    "PCPIPCH": "inflation_avg_pct",        # Inflation, avg consumer prices %
    "LUR": "unemployment_rate_pct",        # Unemployment rate %
    "GGXCNL_NGDP": "fiscal_balance_pct_gdp",  # General govt net lending % GDP
    "BCA_NGDPD": "current_account_pct_gdp",   # Current account % GDP
    "GGX_NGDP": "govt_expenditure_pct_gdp",   # General govt expenditure % GDP
    "GGXWDG_NGDP": "gross_debt_pct_gdp",      # General govt gross debt % GDP
}


class IMFFetcher(BaseFetcher):
    source_id = "imf_weo"
    output_filename = "imf_weo.json"

    def _fetch_indicator(self, indicator_code: str,
                         country_codes: list[str]) -> list[dict]:
        """Fetch one indicator for all countries at once.

        The DataMapper API returns 403 when country codes are appended
        to the URL, but works when fetching all countries. We fetch
        the full dataset and filter locally to tracked countries.
        """
        tracked = set(country_codes)
        url = f"{BASE_URL}/{indicator_code}"

        data = self.get_json(url, timeout=30)
        if not data or not isinstance(data, dict):
            return []

        records = []
        values_section = data.get("values", {}).get(indicator_code, {})
        for iso3, year_data in values_section.items():
            if iso3 not in tracked:
                continue
            if not isinstance(year_data, dict):
                continue
            for year_str, value in year_data.items():
                if value is None:
                    continue
                try:
                    val = float(value)
                except (ValueError, TypeError):
                    continue

                year_int = int(year_str) if year_str.isdigit() else None
                records.append({
                    "country_code": iso3,
                    "indicator_id": indicator_code,
                    "indicator_name": INDICATORS[indicator_code],
                    "value": val,
                    "year": year_str,
                    "is_forecast": year_int is not None and year_int >= 2026,
                    "source": "IMF WEO",
                    "source_url": f"{BASE_URL}/{indicator_code}",
                })

        return records

    def run(self) -> dict:
        all_codes = get_all_country_codes()
        all_records = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for ind_code in INDICATORS:
                f = executor.submit(self._fetch_indicator, ind_code, all_codes)
                futures[f] = ind_code

            for future in as_completed(futures):
                ind_code = futures[future]
                try:
                    records = future.result()
                    all_records.extend(records)
                    logger.info("IMF %s: %d records", ind_code, len(records))
                except Exception as e:
                    logger.error("IMF %s failed: %s", ind_code, e)
                    self.errors.append({"indicator": ind_code, "error": str(e)})

        # Keep most recent actual + latest forecast per country/indicator
        best_actual = {}
        best_forecast = {}
        for r in all_records:
            key = (r["country_code"], r["indicator_id"])
            target = best_forecast if r.get("is_forecast") else best_actual
            existing = target.get(key)
            if existing is None or (r["year"] or "") > (existing["year"] or ""):
                target[key] = r

        # Merge: prefer actuals, append distinct forecasts
        deduped = list(best_actual.values())
        for key, fr in best_forecast.items():
            if key not in best_actual:
                deduped.append(fr)
            else:
                # Also keep the forecast as a separate record
                fr["_type"] = "forecast"
                deduped.append(fr)

        countries_seen = set(r["country_code"] for r in deduped)
        return self.build_envelope(deduped, extra={
            "summary": {
                "total_records": len(deduped),
                "countries_covered": len(countries_seen),
                "indicators": list(INDICATORS.keys()),
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    fetcher = IMFFetcher()
    result = fetcher.execute()
    print(f"IMF WEO: {len(result.get('records', []))} records")
    return result


if __name__ == "__main__":
    main()
