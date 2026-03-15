"""
Fetch IMF World Economic Outlook (WEO) data via DataMapper API.

Covers: GDP forecasts, inflation forecasts, unemployment forecasts,
fiscal balance, current account — forward-looking data that
complements World Bank's historical data.

Primary API: https://www.imf.org/external/datamapper/api/
Fallback API: https://dataservices.imf.org/REST/SDMX_JSON.svc (SDMX JSON)
No API key required.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_fetcher import BaseFetcher, get_all_country_codes

logger = logging.getLogger("prefetch.imf")

BASE_URL = "https://www.imf.org/external/datamapper/api/v1"
SDMX_BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc"

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

# Mapping from DataMapper indicators to SDMX IFS database indicators
# Used as fallback when DataMapper API returns 403.
SDMX_IFS_INDICATORS = {
    "NGDP_RPCH": ("IFS", "NGDP_R_SA_XDC_R_PT"),   # Real GDP growth (approx)
    "PCPIPCH": ("IFS", "PCPI_IX"),                   # Consumer price index
    "LUR": ("IFS", "LUR_PT"),                        # Unemployment rate
}


class IMFFetcher(BaseFetcher):
    source_id = "imf_weo"
    output_filename = "imf_weo.json"

    def _fetch_indicator(self, indicator_code: str,
                         country_codes: list[str]) -> list[dict]:
        """Fetch one indicator for all countries at once.

        Tries the DataMapper API first; if it returns 403 (which
        happens when the API blocks automated requests), falls back
        to the IMF SDMX JSON REST API for available indicators.
        """
        tracked = set(country_codes)
        url = f"{BASE_URL}/{indicator_code}"

        data = self.get_json(url, timeout=30)
        if data and isinstance(data, dict):
            records = self._parse_datamapper_response(
                data, indicator_code, tracked)
            if records:
                return records

        # DataMapper failed — try SDMX fallback for supported indicators
        sdmx_records = self._fetch_indicator_sdmx(indicator_code, tracked)
        if sdmx_records:
            logger.info("IMF %s: got %d records via SDMX fallback",
                        indicator_code, len(sdmx_records))
            return sdmx_records

        return []

    def _parse_datamapper_response(self, data: dict, indicator_code: str,
                                   tracked: set[str]) -> list[dict]:
        """Parse a DataMapper API response into records."""
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

    def _fetch_indicator_sdmx(self, indicator_code: str,
                              tracked: set[str]) -> list[dict]:
        """Fetch indicator data from IMF SDMX JSON REST API as fallback.

        Only a subset of WEO indicators map to IFS SDMX series.
        Returns empty list for unmapped indicators.
        """
        if indicator_code not in SDMX_IFS_INDICATORS:
            return []

        database, series_code = SDMX_IFS_INDICATORS[indicator_code]
        # Build country filter: take first 10 tracked countries to
        # keep request size manageable
        sample_codes = sorted(tracked)[:25]
        country_filter = "+".join(sample_codes)

        url = (f"{SDMX_BASE_URL}/CompactData/{database}"
               f"/A.{country_filter}.{series_code}"
               f"?startPeriod=2020&endPeriod=2026")

        data = self.get_json(url, timeout=45)
        if not data or not isinstance(data, dict):
            return []

        records = []
        try:
            dataset = data.get("CompactData", {}).get("DataSet", {})
            series_list = dataset.get("Series", [])
            # Normalize to list if single series returned
            if isinstance(series_list, dict):
                series_list = [series_list]

            for series in series_list:
                iso2 = series.get("@REF_AREA", "")
                # Convert ISO2 back to ISO3
                from .base_fetcher import ISO2_TO_ISO3
                iso3 = ISO2_TO_ISO3.get(iso2, iso2)
                if iso3 not in tracked:
                    continue

                obs_list = series.get("Obs", [])
                if isinstance(obs_list, dict):
                    obs_list = [obs_list]

                for obs in obs_list:
                    year_str = obs.get("@TIME_PERIOD", "")
                    value = obs.get("@OBS_VALUE")
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
                        "source": "IMF IFS (SDMX fallback)",
                        "source_url": url,
                    })
        except (KeyError, TypeError) as e:
            logger.warning("IMF SDMX parse error for %s: %s",
                           indicator_code, e)

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
