# SHARED SKILL: Cache-Aware Data Fetching

## Purpose

This skill defines the cache-check logic that all gathering agents (01-06) must follow before fetching any data source. It prevents unnecessary refetching of data that hasn't changed since the last pipeline run.

## Instructions

Before querying any data source, perform this check:

### Step 1: Load Cache Context

Read these three files (they should already be loaded by the orchestrator, but verify):
- `/agents/config/cache_registry.json` — last fetch timestamps per source
- `/agents/config/factor_frequency_registry.json` — frequency classification per factor
- `/agents/config/release_calendar.json` — known publication dates for annual/quarterly sources

### Step 2: For Each Data Source You Are About to Query

Determine the **frequency tier** of the factors this source provides (from `factor_frequency_registry.json`):

#### STATIC factors
- **Action:** SKIP unless the orchestrator's `event_triggers` (from Agent 3) explicitly names a trigger event for this factor category.
- **Examples of triggers:** border treaty, new IPCC report, new Hofstede/WVS wave.

#### ANNUAL factors
- **Action:** Check `release_calendar.json` for this source's `expected_release_date` or `last_known_release`.
  - If `last_known_release` > `cache_registry.entries[source].last_fetched` → new edition available → FETCH.
  - If `last_known_release` <= `cache_registry.entries[source].last_fetched` → no new data → SKIP.
  - If no cache entry exists (first run) → FETCH.

#### QUARTERLY factors
- **Action:** Check `cache_registry.entries[source].last_fetched`.
  - If `last_fetched` was less than 90 days ago → SKIP.
  - If `last_fetched` was 90+ days ago, or no entry exists → FETCH.

#### MONTHLY factors
- **Action:** Check `cache_registry.entries[source].last_fetched`.
  - If `last_fetched` was less than 30 days ago → SKIP.
  - If `last_fetched` was 30+ days ago, or no entry exists → FETCH.

#### WEEKLY factors
- **Action:** Always FETCH. No caching.

#### DERIVED factors
- **Action:** Never fetch. These are computed by downstream agents (10-12).

### Step 3: Event Override

Check for `event_triggers` in the Agent 3 output file (`/staging/raw_collected/news_events_{DATE}.json`). If any trigger matches a factor you would otherwise SKIP:

- **Force-refresh** that factor regardless of cache TTL.
- Log the override reason.

Note: Agent 3 runs before Agents 4-6, so its output is available. For Agent 1 and Agent 2 (which may run before Agent 3), event overrides are not applicable — they rely solely on TTL-based caching.

### Step 4: Logging

For every source decision, add an entry to your output's `cache_decisions` array:

```json
{
  "source": "worldbank.wgi",
  "factor_category": "institutions.political.wgi_*",
  "frequency": "annual",
  "action": "skipped",
  "reason": "cached — last_fetched 2026-02-15, no new release since 2025-09-15",
  "last_fetched": "2026-02-15T10:00:00Z",
  "next_due": "2026-09-15"
}
```

Or for a fetch:

```json
{
  "source": "sipri.milex",
  "factor_category": "military.expenditure",
  "frequency": "annual",
  "action": "fetched",
  "reason": "new release detected — SIPRI 2026 released 2026-04-20, last_fetched was 2025-04-20",
  "last_fetched": null,
  "next_due": null
}
```

Or for an event override:

```json
{
  "source": "global_firepower",
  "factor_category": "military.personnel",
  "frequency": "annual",
  "action": "fetched",
  "reason": "event_override — Agent 3 trigger: 'Major military buildup announced in IND'",
  "last_fetched": "2026-01-15T10:00:00Z",
  "next_due": null
}
```

### Step 5: After Successful Fetch

Do NOT update `cache_registry.json` yourself. Agent 9 (Data Integrator) is responsible for updating the cache registry after validated data is integrated into `/data/`.

## Summary Decision Matrix

| Frequency | Cache Entry Exists? | TTL Expired / New Release? | Event Trigger? | Action |
|-----------|--------------------|-----------------------------|----------------|--------|
| static    | —                  | —                           | No             | SKIP   |
| static    | —                  | —                           | Yes            | FETCH  |
| annual    | No                 | —                           | —              | FETCH  |
| annual    | Yes                | No new release              | No             | SKIP   |
| annual    | Yes                | New release detected        | —              | FETCH  |
| quarterly | No                 | —                           | —              | FETCH  |
| quarterly | Yes                | < 90 days                   | No             | SKIP   |
| quarterly | Yes                | >= 90 days                  | —              | FETCH  |
| monthly   | No                 | —                           | —              | FETCH  |
| monthly   | Yes                | < 30 days                   | No             | SKIP   |
| monthly   | Yes                | >= 30 days                  | —              | FETCH  |
| weekly    | —                  | —                           | —              | FETCH  |
| derived   | —                  | —                           | —              | SKIP   |
