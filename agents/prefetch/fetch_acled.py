"""
Fetch conflict event data from ACLED API.

Covers: armed conflict events, protests, riots, violence against
civilians, strategic developments. Used by Agent 5.

API docs: https://apidocs.acleddata.com/
Requires free API key + email (register at acleddata.com).
"""

import logging
import os
from datetime import datetime, timedelta, timezone

from .base_fetcher import BaseFetcher, get_all_country_codes

logger = logging.getLogger("prefetch.acled")

API_URL = "https://api.acleddata.com/acled/read/"

# ISO3 -> ACLED country name mapping for countries that differ
ISO3_TO_ACLED_NAME = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "KOR": "South Korea",
    "PRK": "North Korea",
    "RUS": "Russia",
    "CZE": "Czech Republic",
    "COD": "Democratic Republic of Congo",
    "CIV": "Ivory Coast",
}


class ACLEDFetcher(BaseFetcher):
    source_id = "acled"
    output_filename = "acled.json"

    def _get_credentials(self) -> tuple[str, str]:
        key = os.environ.get("ACLED_API_KEY", "")
        email = os.environ.get("ACLED_EMAIL", "")
        return key, email

    def run(self) -> dict:
        key, email = self._get_credentials()
        if not key or not email:
            logger.warning("ACLED credentials not set — skipping live fetch")
            return self.build_envelope([], skipped=[{
                "reason": "ACLED_API_KEY or ACLED_EMAIL not set in .env",
            }])

        # Fetch events from the past 10 days (overlap for safety)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=10)
        date_start = start_date.strftime("%Y-%m-%d")
        date_end = end_date.strftime("%Y-%m-%d")

        all_records = []
        page = 1
        page_size = 5000

        while True:
            params = {
                "key": key,
                "email": email,
                "event_date": f"{date_start}|{date_end}",
                "event_date_where": "BETWEEN",
                "limit": page_size,
                "page": page,
            }

            data = self.get_json(API_URL, params=params, timeout=60)
            if not data or not isinstance(data, dict):
                break

            events = data.get("data", [])
            if not events:
                break

            all_records.extend(events)
            logger.info("ACLED page %d: %d events", page, len(events))

            # If we got less than page_size, we're done
            if len(events) < page_size:
                break
            page += 1

            # Safety limit
            if page > 10:
                break

        # Filter to tracked countries
        tracked = set(get_all_country_codes())
        filtered = []
        for evt in all_records:
            iso3 = evt.get("iso3", "") or evt.get("iso", "")
            # ACLED sometimes uses numeric ISO codes — try country name matching
            if iso3 not in tracked:
                continue

            filtered.append({
                "event_id": evt.get("data_id", ""),
                "event_date": evt.get("event_date", ""),
                "event_type": evt.get("event_type", ""),
                "sub_event_type": evt.get("sub_event_type", ""),
                "country_code": iso3,
                "country": evt.get("country", ""),
                "admin1": evt.get("admin1", ""),
                "location": evt.get("location", ""),
                "lat": evt.get("latitude"),
                "lon": evt.get("longitude"),
                "source": evt.get("source", ""),
                "fatalities": evt.get("fatalities", 0),
                "actor1": evt.get("actor1", ""),
                "actor2": evt.get("actor2", ""),
                "notes": evt.get("notes", ""),
                "source_api": "ACLED",
            })

        # Summarize by country and event type
        by_country = {}
        by_type = {}
        total_fatalities = 0
        for r in filtered:
            cc = r["country_code"]
            et = r["event_type"]
            by_country[cc] = by_country.get(cc, 0) + 1
            by_type[et] = by_type.get(et, 0) + 1
            try:
                total_fatalities += int(r.get("fatalities", 0) or 0)
            except (ValueError, TypeError):
                pass

        return self.build_envelope(filtered, extra={
            "date_range": {"start": date_start, "end": date_end},
            "summary": {
                "total_events": len(filtered),
                "total_unfiltered": len(all_records),
                "countries_with_events": len(by_country),
                "total_fatalities": total_fatalities,
                "by_country": dict(sorted(by_country.items(), key=lambda x: -x[1])[:20]),
                "by_event_type": by_type,
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from dotenv import load_dotenv
    load_dotenv()
    fetcher = ACLEDFetcher()
    result = fetcher.execute()
    print(f"ACLED: {len(result.get('records', []))} events")
    return result


if __name__ == "__main__":
    main()
