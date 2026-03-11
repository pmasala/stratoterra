"""
Fetch structured data from World Bank Open Data API.

Covers: GDP, inflation, unemployment, demographics, governance (WGI),
trade, fiscal, infrastructure indicators for all 75 countries.

API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
No API key required. Rate limit: ~50 req/min (soft).
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_fetcher import (
    BaseFetcher,
    ISO3_TO_ISO2,
    ISO2_TO_ISO3,
    get_countries_by_tier,
)

logger = logging.getLogger("prefetch.worldbank")

BASE_URL = "https://api.worldbank.org/v2"

# Indicator groups — batched by theme to stay within URL length limits.
INDICATOR_GROUPS = {
    "gdp": [
        "NY.GDP.MKTP.CD",       # GDP current USD
        "NY.GDP.PCAP.CD",       # GDP per capita
        "NY.GDP.MKTP.KD.ZG",    # GDP growth %
        "NY.GDP.MKTP.PP.CD",    # GDP PPP
    ],
    "fiscal": [
        "GC.DOD.TOTL.GD.ZS",   # Govt debt % GDP
        "BN.CAB.XOKA.GD.ZS",   # Current account % GDP
        "FI.RES.TOTL.CD",       # Total reserves incl gold
        "BX.KLT.DINV.CD.WD",   # FDI net inflows
    ],
    "trade": [
        "NE.EXP.GNFS.CD",      # Exports goods+services
        "NE.IMP.GNFS.CD",       # Imports goods+services
    ],
    "labor": [
        "FP.CPI.TOTL.ZG",      # Inflation CPI %
        "SL.UEM.TOTL.ZS",      # Unemployment %
        "SL.TLF.CACT.ZS",      # Labor force participation
    ],
    "demographics": [
        "SP.POP.TOTL",          # Population
        "SP.POP.GROW",          # Population growth %
        "SP.DYN.LE00.IN",      # Life expectancy
        "SP.URB.TOTL.IN.ZS",   # Urban population %
    ],
    "development": [
        "SI.POV.GINI",          # Gini index
        "SE.ADT.LITR.ZS",      # Literacy rate
        "SH.XPD.CHEX.GD.ZS",  # Health expenditure % GDP
    ],
    "infrastructure": [
        "EG.ELC.ACCS.ZS",      # Electricity access %
        "IT.NET.USER.ZS",      # Internet users %
    ],
    "wgi": [
        "VA.EST",               # Voice & Accountability
        "PV.EST",               # Political Stability (Absence of Violence)
        "GE.EST",               # Govt Effectiveness
        "RQ.EST",               # Regulatory Quality
        "RL.EST",               # Rule of Law
        "CC.EST",               # Control of Corruption
    ],
}

# Friendly names for output
INDICATOR_NAMES = {
    "NY.GDP.MKTP.CD": "gdp_nominal_usd",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "NY.GDP.MKTP.PP.CD": "gdp_ppp_usd",
    "GC.DOD.TOTL.GD.ZS": "govt_debt_pct_gdp",
    "BN.CAB.XOKA.GD.ZS": "current_account_pct_gdp",
    "FI.RES.TOTL.CD": "reserves_total_usd",
    "BX.KLT.DINV.CD.WD": "fdi_net_inflows_usd",
    "NE.EXP.GNFS.CD": "exports_usd",
    "NE.IMP.GNFS.CD": "imports_usd",
    "FP.CPI.TOTL.ZG": "inflation_cpi_pct",
    "SL.UEM.TOTL.ZS": "unemployment_pct",
    "SL.TLF.CACT.ZS": "labor_force_participation_pct",
    "SP.POP.TOTL": "population",
    "SP.POP.GROW": "population_growth_pct",
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "SI.POV.GINI": "gini_index",
    "SE.ADT.LITR.ZS": "literacy_rate_pct",
    "SH.XPD.CHEX.GD.ZS": "health_expenditure_pct_gdp",
    "EG.ELC.ACCS.ZS": "electricity_access_pct",
    "IT.NET.USER.ZS": "internet_users_pct",
    "VA.EST": "wgi_voice_accountability",
    "PV.EST": "wgi_political_stability",
    "GE.EST": "wgi_govt_effectiveness",
    "RQ.EST": "wgi_regulatory_quality",
    "RL.EST": "wgi_rule_of_law",
    "CC.EST": "wgi_control_of_corruption",
}


class WorldBankFetcher(BaseFetcher):
    source_id = "worldbank"
    output_filename = "worldbank.json"

    def __init__(self):
        super().__init__()
        self.tracked_iso2 = set()
        self.tracked_iso3 = set()
        self._init_country_sets()

    def _init_country_sets(self):
        tiers = get_countries_by_tier()
        for tier_countries in tiers.values():
            for c in tier_countries:
                code = c["code"]
                self.tracked_iso3.add(code)
                iso2 = ISO3_TO_ISO2.get(code)
                if iso2:
                    self.tracked_iso2.add(iso2)

    def _fetch_single_indicator(self, iso2_list: list[str],
                                indicator: str,
                                date_range: str = "2020:2025") -> list[dict]:
        """Fetch one indicator for a batch of countries.

        World Bank supports semicolon-delimited country lists but only
        one indicator per call.
        """
        countries_str = ";".join(iso2_list)
        url = f"{BASE_URL}/country/{countries_str}/indicator/{indicator}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": "1000",
        }

        records = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            params["page"] = str(page)
            data = self.get_json(url, params=params, timeout=45)
            if not data or not isinstance(data, list) or len(data) < 2:
                # Check for error message
                if data and isinstance(data, list) and len(data) > 0:
                    msg = data[0]
                    if isinstance(msg, dict) and "message" in msg:
                        logger.warning("WB API error for %s: %s", indicator, msg)
                break

            metadata = data[0]
            total_pages = metadata.get("pages", 1)
            entries = data[1] if data[1] else []

            for entry in entries:
                if entry.get("value") is None:
                    continue
                iso3 = entry.get("countryiso3code", "")
                if not iso3:
                    iso2_code = entry.get("country", {}).get("id", "")
                    iso3 = ISO2_TO_ISO3.get(iso2_code, "")

                if iso3 not in self.tracked_iso3:
                    continue

                records.append({
                    "country_code": iso3,
                    "indicator_id": indicator,
                    "indicator_name": INDICATOR_NAMES.get(indicator, indicator),
                    "value": entry["value"],
                    "year": entry.get("date"),
                    "source": "World Bank",
                    "source_url": f"{BASE_URL}/country/{iso3}/indicator/{indicator}",
                })

            page += 1

        return records

    def _fetch_indicator_batch(self, iso2_list: list[str],
                                indicators: list[str],
                                date_range: str = "2020:2025") -> list[dict]:
        """Fetch multiple indicators for a batch of countries.

        Calls _fetch_single_indicator per indicator (WB API only supports
        one indicator per request).
        """
        records = []
        for indicator in indicators:
            batch = self._fetch_single_indicator(iso2_list, indicator, date_range)
            records.extend(batch)
        return records

    def _fetch_group(self, group_name: str, indicators: list[str]) -> list[dict]:
        """Fetch one indicator group for all countries in tier batches."""
        tiers = get_countries_by_tier()
        all_records = []

        for tier_name, countries in tiers.items():
            iso2_batch = []
            for c in countries:
                iso2 = ISO3_TO_ISO2.get(c["code"])
                if iso2:
                    iso2_batch.append(iso2)

            if not iso2_batch:
                continue

            # Split into sub-batches of 25 (URL length safety)
            for i in range(0, len(iso2_batch), 25):
                chunk = iso2_batch[i:i + 25]
                records = self._fetch_indicator_batch(chunk, indicators)
                all_records.extend(records)

        logger.info("Group '%s': %d records", group_name, len(all_records))
        return all_records

    def run(self) -> dict:
        all_records = []

        # Fetch all indicator groups in parallel threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for group_name, indicators in INDICATOR_GROUPS.items():
                future = executor.submit(self._fetch_group, group_name, indicators)
                futures[future] = group_name

            for future in as_completed(futures):
                group_name = futures[future]
                try:
                    records = future.result()
                    all_records.extend(records)
                except Exception as e:
                    logger.error("Group '%s' failed: %s", group_name, e)
                    self.errors.append({
                        "group": group_name,
                        "error": str(e),
                    })

        # Deduplicate: keep the most recent year per country+indicator
        best = {}
        for r in all_records:
            key = (r["country_code"], r["indicator_id"])
            existing = best.get(key)
            if existing is None or (r["year"] or "") > (existing["year"] or ""):
                best[key] = r

        deduped = list(best.values())

        # Build summary
        countries_seen = set(r["country_code"] for r in deduped)
        indicators_seen = set(r["indicator_id"] for r in deduped)

        return self.build_envelope(deduped, extra={
            "summary": {
                "total_records": len(deduped),
                "countries_covered": len(countries_seen),
                "indicators_covered": len(indicators_seen),
                "by_group": {
                    gname: len([r for r in deduped if r["indicator_id"] in inds])
                    for gname, inds in INDICATOR_GROUPS.items()
                },
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    fetcher = WorldBankFetcher()
    result = fetcher.execute()
    print(f"World Bank: {result['stats'].get('requests_made', 0)} requests, "
          f"{len(result.get('records', []))} records")
    return result


if __name__ == "__main__":
    main()
