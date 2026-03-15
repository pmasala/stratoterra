"""
Fetch conflict event data from ACLED API.

Covers: armed conflict events, protests, riots, violence against
civilians, strategic developments. Used by Agent 5.

API docs: https://apidocs.acleddata.com/
Auth: OAuth 2.0 (password grant) — register at acleddata.com.
Requires ACLED_EMAIL and ACLED_PASSWORD in .env.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from .base_fetcher import BaseFetcher, get_all_country_codes, CACHE_DIR

logger = logging.getLogger("prefetch.acled")

TOKEN_URL = "https://acleddata.com/oauth/token"
API_URL = "https://acleddata.com/api/acled/read"
TOKEN_CACHE_FILE = CACHE_DIR / ".acled_token_cache.json"

# Token refresh margin: refresh if less than 5 minutes remain
REFRESH_MARGIN_SECONDS = 300

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


class ACLEDAuth:
    """OAuth 2.0 client for ACLED API (password grant)."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._access_token = ""
        self._refresh_token = ""
        self._expires_at = 0.0  # unix timestamp

    def _save_cache(self) -> None:
        """Persist tokens to disk for reuse across runs."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_at": self._expires_at,
        }
        TOKEN_CACHE_FILE.write_text(json.dumps(data))

    def _load_cache(self) -> bool:
        """Load cached tokens. Returns True if a usable token was found."""
        if not TOKEN_CACHE_FILE.exists():
            return False
        try:
            data = json.loads(TOKEN_CACHE_FILE.read_text())
            self._access_token = data.get("access_token", "")
            self._refresh_token = data.get("refresh_token", "")
            self._expires_at = data.get("expires_at", 0.0)
            return bool(self._access_token)
        except (json.JSONDecodeError, OSError):
            return False

    def _token_valid(self) -> bool:
        return self._access_token and time.time() < (self._expires_at - REFRESH_MARGIN_SECONDS)

    def _authenticate(self) -> bool:
        """Obtain tokens using username/password grant."""
        logger.info("ACLED: authenticating with credentials")
        try:
            resp = requests.post(TOKEN_URL, data={
                "username": self.email,
                "password": self.password,
                "grant_type": "password",
                "client_id": "acled",
            }, timeout=30)
            resp.raise_for_status()
            return self._parse_token_response(resp.json())
        except requests.RequestException as e:
            logger.error("ACLED auth failed: %s", e)
            return False

    def _refresh(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self._refresh_token:
            return False
        logger.info("ACLED: refreshing access token")
        try:
            resp = requests.post(TOKEN_URL, data={
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
                "client_id": "acled",
            }, timeout=30)
            resp.raise_for_status()
            return self._parse_token_response(resp.json())
        except requests.RequestException as e:
            logger.warning("ACLED token refresh failed: %s", e)
            return False

    def _parse_token_response(self, data: dict) -> bool:
        token = data.get("access_token", "")
        if not token:
            logger.error("ACLED: no access_token in response")
            return False
        self._access_token = token
        self._refresh_token = data.get("refresh_token", self._refresh_token)
        expires_in = data.get("expires_in", 86400)
        self._expires_at = time.time() + expires_in
        self._save_cache()
        logger.info("ACLED: token obtained (expires in %ds)", expires_in)
        return True

    def get_token(self) -> str:
        """Return a valid access token, refreshing or re-authenticating as needed."""
        # Try cached token from a previous run
        if not self._access_token:
            self._load_cache()

        # Token still valid?
        if self._token_valid():
            return self._access_token

        # Try refresh
        if self._refresh_token and self._refresh():
            return self._access_token

        # Full re-authentication
        if self._authenticate():
            return self._access_token

        return ""


class ACLEDFetcher(BaseFetcher):
    source_id = "acled"
    output_filename = "acled.json"

    def _get_credentials(self) -> tuple[str, str]:
        email = os.environ.get("ACLED_EMAIL", "")
        password = os.environ.get("ACLED_PASSWORD", "")
        return email, password

    def _api_get(self, auth: ACLEDAuth, params: dict) -> dict | None:
        """Make an authenticated API call with automatic 401 retry."""
        token = auth.get_token()
        if not token:
            return None

        self.stats["requests_made"] += 1
        try:
            resp = self.session.get(
                API_URL, params=params, timeout=60,
                headers={"Authorization": f"Bearer {token}"},
            )

            # On 401, try refreshing token and retry once
            if resp.status_code == 401:
                logger.warning("ACLED: 401 — attempting token refresh")
                token = auth.get_token()
                if not token:
                    self.stats["requests_failed"] += 1
                    return None
                resp = self.session.get(
                    API_URL, params=params, timeout=60,
                    headers={"Authorization": f"Bearer {token}"},
                )

            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            self.stats["requests_failed"] += 1
            self.errors.append({
                "url": API_URL,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            logger.warning("ACLED request failed: %s", e)
            return None

    def run(self) -> dict:
        email, password = self._get_credentials()
        if not email or not password:
            logger.warning("ACLED credentials not set — skipping live fetch")
            return self.build_envelope([], skipped=[{
                "reason": "ACLED_EMAIL or ACLED_PASSWORD not set in .env",
            }])

        auth = ACLEDAuth(email, password)
        if not auth.get_token():
            logger.error("ACLED: could not obtain access token")
            return self.build_envelope([], skipped=[{
                "reason": "ACLED OAuth authentication failed",
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
                "_format": "json",
                "event_date": f"{date_start}|{date_end}",
                "event_date_where": "BETWEEN",
                "limit": page_size,
                "page": page,
            }

            data = self._api_get(auth, params)
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
