"""
Fetch event data from GDELT Project API v2.

Covers: global news events, conflict signals, cooperation events.
Agent 3 (News & Events) uses this as its primary structured source.

API docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
No API key required. Rate limit: ~1 request/second for doc API.
"""

import logging
import time

from .base_fetcher import BaseFetcher, get_all_country_codes

logger = logging.getLogger("prefetch.gdelt")

DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GEO_API = "https://api.gdeltproject.org/api/v2/geo/geo"

# Pause between GDELT queries to avoid 429 rate limiting.
QUERY_DELAY_SECONDS = 5

# Thematic queries to cover different event types
THEME_QUERIES = [
    {
        "id": "top_events",
        "query": "sourcelang:english",
        "sort": "hybridrel",
        "maxrecords": 250,
        "description": "Top 250 events by relevance",
    },
    {
        "id": "military_conflict",
        "query": "(theme:MILITARY OR theme:ARMED_CONFLICT) AND sourcelang:english",
        "sort": "datedesc",
        "maxrecords": 100,
        "description": "Military and conflict events",
    },
    {
        "id": "sanctions_trade",
        "query": "(theme:ECON_TRADE_DISPUTE OR sanctions OR tariff) AND sourcelang:english",
        "sort": "datedesc",
        "maxrecords": 100,
        "description": "Trade disputes and sanctions",
    },
    {
        "id": "elections_governance",
        "query": "(theme:ELECTION OR theme:GOVERNMENT OR coup OR referendum) AND sourcelang:english",
        "sort": "datedesc",
        "maxrecords": 100,
        "description": "Elections and governance changes",
    },
    {
        "id": "economic_crisis",
        "query": "(theme:ECON_BANKRUPTCY OR theme:ECON_DEBTCRISIS OR default OR recession) AND sourcelang:english",
        "sort": "datedesc",
        "maxrecords": 75,
        "description": "Economic crises and defaults",
    },
]


class GDELTFetcher(BaseFetcher):
    source_id = "gdelt"
    output_filename = "gdelt.json"

    def _fetch_doc_query(self, query_config: dict) -> list[dict]:
        """Run a single GDELT doc API query."""
        params = {
            "query": query_config["query"],
            "timespan": "7d",
            "mode": "artlist",
            "format": "json",
            "maxrecords": query_config.get("maxrecords", 250),
            "sort": query_config.get("sort", "hybridrel"),
        }

        data = self.get_json(DOC_API, params=params, timeout=30)
        if not data:
            return []

        articles = data.get("articles", [])
        records = []
        for art in articles:
            records.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "source": art.get("domain", ""),
                "language": art.get("language", ""),
                "seendate": art.get("seendate", ""),
                "socialimage": art.get("socialimage", ""),
                "query_id": query_config["id"],
            })

        return records

    def _fetch_geo_conflicts(self) -> list[dict]:
        """Fetch geo-tagged conflict/cooperation events.

        The GDELT Geo API v2 returns point data for event locations.
        This endpoint is unreliable (frequently returns 404), so failures
        are handled gracefully.
        """
        params = {
            "query": "conflict OR military OR sanctions OR protest",
            "timespan": "7d",
            "mode": "PointData",
            "format": "GeoJSON",
        }

        data = self.get_json(GEO_API, params=params, timeout=30)
        if not data or not isinstance(data, dict):
            logger.info("GDELT Geo API unavailable — skipping geo events")
            return []

        features = data.get("features", [])
        if not features:
            return []

        records = []
        for feature in features[:500]:
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])
            records.append({
                "name": props.get("name", ""),
                "url": props.get("url", ""),
                "count": props.get("count", 0),
                "lat": coords[1] if len(coords) >= 2 else None,
                "lon": coords[0] if len(coords) >= 2 else None,
                "type": "geo_event",
                "query_id": "geo_conflicts",
            })

        return records

    def run(self) -> dict:
        all_records = []

        # Fetch all thematic doc queries with delay to avoid rate limiting
        for i, qconfig in enumerate(THEME_QUERIES):
            if i > 0:
                logger.info("Waiting %ds between GDELT queries...", QUERY_DELAY_SECONDS)
                time.sleep(QUERY_DELAY_SECONDS)

            logger.info("GDELT query: %s", qconfig["id"])
            records = self._fetch_doc_query(qconfig)
            all_records.extend(records)
            logger.info("  -> %d articles", len(records))

        # Fetch geo data (separate endpoint, delay before it too)
        time.sleep(QUERY_DELAY_SECONDS)
        logger.info("GDELT geo conflicts query")
        geo_records = self._fetch_geo_conflicts()
        logger.info("  -> %d geo events", len(geo_records))

        # Deduplicate by URL
        seen_urls = set()
        deduped = []
        for r in all_records:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped.append(r)

        return self.build_envelope(deduped, extra={
            "geo_events": geo_records,
            "summary": {
                "total_articles": len(deduped),
                "total_geo_events": len(geo_records),
                "by_query": {
                    q["id"]: len([r for r in deduped if r.get("query_id") == q["id"]])
                    for q in THEME_QUERIES
                },
            }
        })


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    fetcher = GDELTFetcher()
    result = fetcher.execute()
    print(f"GDELT: {len(result.get('records', []))} articles, "
          f"{len(result.get('geo_events', []))} geo events")
    return result


if __name__ == "__main__":
    main()
