"""
Fetch exchange rates and commodity prices from free APIs.

Exchange rates: ExchangeRate-API (free tier, 1500 req/month)
Fallback: Open Exchange Rates API (frankfurter.app, no key needed)
Commodity prices: fetched from multiple free JSON endpoints.

Covers Agent 2's FX and commodity data needs.
"""

import logging
import os

from .base_fetcher import BaseFetcher

logger = logging.getLogger("prefetch.fx")

# All currencies tracked (39 currencies for 75 countries)
TRACKED_CURRENCIES = [
    "EUR", "GBP", "JPY", "CNY", "INR", "BRL", "RUB", "KRW", "AUD", "CAD",
    "CHF", "SEK", "NOK", "MXN", "IDR", "TRY", "ZAR", "SAR", "AED", "THB",
    "MYR", "SGD", "TWD", "PLN", "ILS", "PHP", "VND", "COP", "ARS", "CLP",
    "EGP", "NGN", "PKR", "BDT", "KZT", "UAH", "RON", "CZK", "HUF",
]

# Currency -> country code mapping for output
CURRENCY_TO_COUNTRY = {
    "EUR": "DEU", "GBP": "GBR", "JPY": "JPN", "CNY": "CHN", "INR": "IND",
    "BRL": "BRA", "RUB": "RUS", "KRW": "KOR", "AUD": "AUS", "CAD": "CAN",
    "CHF": "CHE", "SEK": "SWE", "NOK": "NOR", "MXN": "MEX", "IDR": "IDN",
    "TRY": "TUR", "ZAR": "ZAF", "SAR": "SAU", "AED": "ARE", "THB": "THA",
    "MYR": "MYS", "SGD": "SGP", "TWD": "TWN", "PLN": "POL", "ILS": "ISR",
    "PHP": "PHL", "VND": "VNM", "COP": "COL", "ARS": "ARG", "CLP": "CHL",
    "EGP": "EGY", "NGN": "NGA", "PKR": "PAK", "BDT": "BGD", "KZT": "KAZ",
    "UAH": "UKR", "RON": "ROU", "CZK": "CZE", "HUF": "HUN",
}

# Free FX API (no key needed, based on ECB data)
FRANKFURTER_URL = "https://api.frankfurter.app/latest"
EXCHANGERATE_URL = "https://v6.exchangerate-api.com/v6/{key}/latest/USD"


class FXCommoditiesFetcher(BaseFetcher):
    source_id = "fx_commodities"
    output_filename = "fx_commodities.json"

    def _fetch_fx_with_key(self) -> list[dict]:
        """Fetch FX rates using ExchangeRate-API (if key available)."""
        api_key = os.environ.get("EXCHANGERATE_API_KEY", "")
        if not api_key:
            return []

        url = EXCHANGERATE_URL.format(key=api_key)
        data = self.get_json(url, timeout=15)
        if not data or data.get("result") != "success":
            return []

        rates = data.get("conversion_rates", {})
        records = []
        for currency in TRACKED_CURRENCIES:
            rate = rates.get(currency)
            if rate is not None:
                records.append({
                    "currency": currency,
                    "country_code": CURRENCY_TO_COUNTRY.get(currency, ""),
                    "rate_vs_usd": rate,
                    "source": "ExchangeRate-API",
                    "indicator_name": "exchange_rate_vs_usd",
                })

        return records

    def _fetch_fx_frankfurter(self) -> list[dict]:
        """Fetch FX rates from Frankfurter (ECB data, no key needed)."""
        # Frankfurter uses EUR as base; fetch USD base
        data = self.get_json(FRANKFURTER_URL, params={"from": "USD"}, timeout=15)
        if not data or "rates" not in data:
            return []

        rates = data["rates"]
        records = []
        for currency in TRACKED_CURRENCIES:
            rate = rates.get(currency)
            if rate is not None:
                records.append({
                    "currency": currency,
                    "country_code": CURRENCY_TO_COUNTRY.get(currency, ""),
                    "rate_vs_usd": rate,
                    "source": "Frankfurter (ECB)",
                    "indicator_name": "exchange_rate_vs_usd",
                })

        return records

    # Precious metals to fetch: (symbol, name, indicator_name)
    METALS = [
        ("XAU", "gold", "gold_usd_oz"),
        ("XAG", "silver", "silver_usd_oz"),
        ("XPT", "platinum", "platinum_usd_oz"),
        ("XPD", "palladium", "palladium_usd_oz"),
    ]

    def _fetch_commodities(self) -> list[dict]:
        """Fetch precious metal prices from gold-api.com (free, no key).

        LLM agents gap-fill oil, gas, grains, and other non-metal commodities.
        """
        records = self._fetch_gold_api()
        if records:
            return records

        logger.warning("No commodity data from APIs — agents will gap-fill")
        return []

    def _fetch_gold_api(self) -> list[dict]:
        """Fetch spot prices from gold-api.com (free, no key needed)."""
        records = []
        for symbol, name, indicator in self.METALS:
            data = self.get_json(
                f"https://api.gold-api.com/price/{symbol}", timeout=15
            )
            if data and "price" in data:
                records.append({
                    "commodity": name,
                    "commodity_code": symbol,
                    "price_usd": data["price"],
                    "unit": "troy oz",
                    "source": "gold-api.com",
                    "indicator_name": indicator,
                })
            else:
                logger.warning("gold-api.com: no price for %s", symbol)
        return records

    def run(self) -> dict:
        # Try authenticated API first, fall back to Frankfurter
        fx_records = self._fetch_fx_with_key()
        if not fx_records:
            logger.info("No ExchangeRate-API key or failed, using Frankfurter")
            fx_records = self._fetch_fx_frankfurter()

        commodity_records = self._fetch_commodities()

        all_records = fx_records + commodity_records

        return self.build_envelope(all_records, extra={
            "fx_count": len(fx_records),
            "commodity_count": len(commodity_records),
            "summary": {
                "currencies_covered": len(fx_records),
                "commodities_covered": len(commodity_records),
                "fx_source": fx_records[0]["source"] if fx_records else "none",
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from dotenv import load_dotenv
    load_dotenv()
    fetcher = FXCommoditiesFetcher()
    result = fetcher.execute()
    print(f"FX: {result.get('fx_count', 0)} rates, "
          f"Commodities: {result.get('commodity_count', 0)} prices")
    return result


if __name__ == "__main__":
    main()
