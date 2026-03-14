# Geopolitical Intelligence Model — Requirements Specification

**Version:** 1.1
**Date:** 2026-03-14
**Status:** Active
**Depends on:** `01_FACTOR_MODEL_SPEC.md`, `02_AGENT_ARCHITECTURE.md`

---

## 1. Project Overview

### 1.1 Product Vision

An interactive, web-based geopolitical intelligence platform that provides investors with a comprehensive, data-driven view of global political, economic, and military dynamics. The platform visualizes quantitative factors for ~75 countries and their bilateral relationships on an interactive world map, with AI-generated weekly trend estimates.

### 1.2 Target User

**Primary:** Individual investor or small fund manager seeking a structured, visual way to understand geopolitical risk and opportunity across global markets.

**User Profile:**
- Comfortable with financial data and geopolitical concepts
- Wants to explore, not just read reports
- Values transparency of methodology and data provenance
- Weekly engagement pattern (checks after each update cycle)
- Desktop-first usage (complex visualizations)

### 1.3 Core Value Proposition

- **Unified model:** Resources, geography, politics, economics, military, and relations in one coherent framework
- **Visual exploration:** Interactive map as primary interface, not tables or reports
- **AI-powered trends:** Weekly trend estimates with reasoning, not just raw data
- **Transparency:** Every data point traceable to source, every trend estimate explained

---

## 2. System Architecture

### 2.1 Architecture Summary

```
┌──────────────────────────────────────────────┐
│           WEEKLY UPDATE PIPELINE              │
│                                               │
│  You + Claude Code MAX                        │
│  Trigger: Manual, weekly                      │
│  Duration: 3-5 hours                          │
│  Output: Updated JSON data files              │
│                                               │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │Agent│→│Agent│→│Agent│→│Agent│→│Agent│→... │
│  │  1  │ │  2  │ │  3  │ │  4  │ │  5  │    │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │
│         ↓                                     │
│    /data (JSON files)                         │
│         ↓                                     │
│    git commit + push                          │
└──────────────────────────────────────────────┘
              ↓ (GitHub Pages deploy)
┌──────────────────────────────────────────────┐
│           STATIC WEB UI                       │
│                                               │
│  Hosting: GitHub Pages                        │
│  Tech: HTML + JS + CSS (no backend)           │
│  Data: Fetches JSON chunks from /data         │
│  Rendering: Interactive 2D map + panels       │
│                                               │
│  ┌───────────────────────────────────┐       │
│  │  Map View (entry point)            │       │
│  │  → Country panels (on click)       │       │
│  │  → Relation explorer               │       │
│  │  → Weekly briefing                 │       │
│  │  → Alert dashboard                 │       │
│  │  → Comparison tools                │       │
│  └───────────────────────────────────┘       │
└──────────────────────────────────────────────┘
```

### 2.2 Hosting: GitHub Pages

- **Repository:** `pmasala/stratoterra` on GitHub
- **Branch:** `main` branch — deployed via `static.yml` GitHub Actions workflow
- **Data delivery:** JSON files served as static assets from the same repo
- **Custom domain:** Optional (CNAME record)
- **HTTPS:** Provided by GitHub Pages
- **Build:** No build step needed if using vanilla JS; optional build step if using a framework
- **Size limits:** GitHub Pages soft limit 1GB repo, 100MB per file. Our data will be well under this with chunking.
- **Bandwidth:** 100GB/month soft limit. Sufficient for personal/small-audience use.

### 2.3 Data Chunking Strategy

Total estimated data: ~50-100MB raw JSON across all files.

**Chunking approach:**

```
/data
├── /chunks
│   ├── manifest.json                    # Master index: what chunks exist,
│   │                                    # last modified dates, sizes
│   │
│   ├── /country-summary
│   │   └── all_countries_summary.json   # ~500KB
│   │       # Minimal data for ALL countries:
│   │       # name, code, region, GDP, population, risk_score,
│   │       # trend_headline, alert_count, lat/lng for map plotting
│   │       # This is loaded on page init for the map view
│   │
│   ├── /country-detail
│   │   ├── USA.json                     # ~50-100KB per country
│   │   ├── CHN.json                     # Full factor model for one country
│   │   └── ...                          # Loaded on-demand when user clicks
│   │
│   ├── /relations
│   │   ├── relation_index.json          # ~20KB: list of all pairs with
│   │   │                                # composite scores only
│   │   ├── USA_CHN.json                 # ~10-20KB per pair
│   │   └── ...                          # Loaded on-demand
│   │
│   ├── /timeseries
│   │   ├── ts_index.json                # What timeseries are available
│   │   ├── USA_macro.json               # Key macro indicators over time
│   │   ├── USA_military.json            # Military spending over time
│   │   └── ...                          # Loaded on-demand for charts
│   │
│   ├── /global
│   │   ├── weekly_briefing.json         # ~20KB
│   │   ├── alert_index.json             # ~10KB
│   │   ├── global_rankings.json         # ~30KB
│   │   ├── event_feed.json              # ~30KB (last 4 weeks of events)
│   │   └── chokepoints.json             # ~5KB
│   │
│   ├── /supranational
│   │   ├── supranational_index.json     # ~5KB
│   │   ├── EU.json                      # ~10KB each
│   │   ├── NATO.json
│   │   └── ...
│   └── /global/articles
│       ├── article_index.json           # ~10KB (merged 30-day index)
│       ├── art_2026-03-14_001.json      # ~15KB per article
│       └── ...                          # Daily articles with SVG illustrations
```

**Loading strategy:**

```
Page load:
  1. Fetch manifest.json (~1KB)
  2. Fetch all_countries_summary.json (~500KB)
  3. Render map with all countries colored by default metric
  → Page is interactive in < 3 seconds

User clicks country:
  4. Fetch {country_code}.json (~80KB)
  5. Render country detail panel
  → Panel appears in < 1 second

User explores relations:
  6. Fetch relation_index.json (~20KB, cached after first load)
  7. Fetch specific relation file on demand (~15KB)

User views charts:
  8. Fetch timeseries file on demand (~20KB)

User reads briefing:
  9. Fetch weekly_briefing.json (~20KB)
```

**Estimated initial page load:** ~600KB (manifest + summary + map assets)
**Estimated total if user explores everything:** ~5-10MB

---

## 3. Functional Requirements

### 3.1 Data Pipeline (Agent System)

#### FR-DP-001: Weekly Update Orchestration
- The system shall execute a defined sequence of 18 agents in order (Agent 17 invoked twice)
- Each agent shall read from defined input files and write to defined output files
- The orchestrator shall log start/end time and status for each agent
- If an agent fails, the system shall stop and report which agent failed
- The system shall support re-running from any specific agent

#### FR-DP-002: Data Gathering
- The system shall collect data from at least 10 distinct source types (APIs, web pages, datasets)
- Each data point collected shall include: source name, source URL, collection timestamp, raw value
- The system shall respect rate limits for all API sources
- The system shall handle API failures gracefully (retry, then skip and flag)

#### FR-DP-003: Data Processing
- All collected data shall be normalized to the schema defined in `01_FACTOR_MODEL_SPEC.md`
- Monetary values shall be converted to USD using current exchange rates
- Each processed data point shall be assigned a confidence score (0.0-1.0)
- Data points that cannot be mapped to the schema shall be logged but not discarded

#### FR-DP-004: Data Validation
- Every proposed factor update shall pass plausibility checks before integration
- The system shall detect statistical anomalies (values > 3σ from historical trend)
- The system shall check internal consistency (percentages sum correctly, ratios consistent)
- The system shall cross-validate multi-source data points
- Validation verdicts: ACCEPT, ACCEPT_WITH_NOTE, FLAG, REJECT, ESCALATE

#### FR-DP-005: Autonomous Escalation Handling
- The system shall resolve ESCALATED items automatically via Agent 17 (Autonomous Auditor)
- Agent 17 shall evaluate each escalation using rule-based criteria:
  - Source count (1, 2, 3+ independent sources)
  - Confidence score (high ≥ 0.7, moderate 0.4-0.69, low < 0.4)
  - Validator recommendation from Agent 8
  - Trend alignment with recent data
- Decisions: ACCEPT, ACCEPT_WITH_DOWNGRADE, or REJECT
- Target: ≤ 20 escalations per weekly run
- No human intervention is required during the pipeline run

#### FR-DP-006: Trend Estimation
- The system shall produce trend estimates for ~11 key factors per Tier 1-2 country
- Each estimate shall include: trend label, confidence, reasoning (natural language), supporting evidence, counter-arguments
- Trend labels: strong_growth, growth, stable, decrease, strong_decrease
- Estimates shall consider both quantitative trends and qualitative event signals

#### FR-DP-007: Alert Generation
- The system shall automatically generate alerts when predefined thresholds are crossed
- Alert severities: critical, warning, watch
- Alerts shall include: title, description, affected countries, affected factors, investor implications
- Alerts shall have lifecycle states: new, ongoing, escalated, deescalated, resolved

#### FR-DP-008: Synthesis
- The system shall generate narrative summaries for each Tier 1-2 country
- Narratives shall include: executive summary, key changes, outlook, investor implications
- The system shall generate a weekly global briefing
- All generated text shall be clearly marked as AI-generated

#### FR-DP-009: Archiving & Version Control
- Each weekly run shall create an archived snapshot of the previous data state
- All changes shall be committed to git with a descriptive commit message
- The system shall maintain at least 52 weeks of historical data
- Timeseries data shall retain at least 20 quarters (5 years) of history

#### FR-DP-010: Data Quality Reporting
- Each run shall produce a quality report covering: coverage, staleness, confidence distribution, validation summary, source health, agent performance
- The quality report shall flag any Tier 1 country with factor coverage < 80%
- The quality report shall flag any factor with confidence < 0.3

### 3.2 Web UI

#### FR-UI-001: Map View (Landing Page)
- The UI shall display an interactive 2D world map showing all tracked countries
- Countries shall be color-coded by a user-selectable metric
- Available color metrics (minimum): GDP growth trend, political stability, military spending trend, overall risk score, alert severity
- The map shall be zoomable and pannable
- Hovering over a country shall show a tooltip with: country name, selected metric value, alert indicator
- Clicking a country shall open the country detail panel
- The map shall load and be interactive within 5 seconds on a modern broadband connection

#### FR-UI-002: Country Detail Panel
- Clicking a country on the map shall open a detail panel (slide-in from right or modal)
- The panel shall display all 6 layers of the factor model in a structured, navigable layout
- Each factor shall show: current value, trend arrow, confidence indicator, last updated date
- Factors with active alerts shall be visually highlighted
- The panel shall include the AI-generated narrative summary
- Key factors shall include sparkline mini-charts showing recent history
- The panel shall load within 2 seconds of clicking (on-demand data fetch)

#### FR-UI-003: Relation Explorer
- Users shall be able to select two countries and view their bilateral relationship
- The relation view shall show all sub-dimensions: trade, people, diplomatic, military, science, financial, energy
- Users shall be able to view a single country's relationship web: a network graph showing its connections
- The network graph shall be filterable by relationship dimension (e.g., show only trade links)
- Edge thickness shall represent relationship magnitude
- Edge color shall represent relationship quality (cooperative → hostile)

#### FR-UI-004: Weekly Briefing View
- The UI shall have a "This Week" section showing the weekly briefing
- Top stories shall be displayed with summaries and links to affected countries
- Regional summaries shall be navigable
- Market context (commodities, currencies, rates) shall be displayed

#### FR-UI-005: Alert Dashboard
- The UI shall display all active alerts sorted by severity
- Each alert shall be clickable, navigating to the affected country
- The dashboard shall show alert trends (more/fewer alerts than last week)
- Users shall be able to filter alerts by: severity, region, type

#### FR-UI-006: Comparison Tool
- Users shall be able to select 2-5 countries and compare them side by side
- Comparison shall show selected factors in a table or radar chart
- Users shall be able to select which factors to compare

#### FR-UI-007: Global Rankings
- The UI shall provide sortable rankings of countries by any key metric
- Rankings shall show the metric value, rank, trend, and change from previous period
- Users shall be able to filter rankings by region or tier

#### FR-UI-008: Search & Navigation
- The UI shall include a search bar to find countries by name
- Keyboard shortcuts for common actions (Escape to close panel, etc.)
- Breadcrumb navigation showing current location in the UI hierarchy

#### FR-UI-009: Data Transparency
- Every displayed data point shall show its source on hover or click
- The UI shall display a "Data last updated" timestamp prominently
- The UI shall show confidence indicators (color-coded) for uncertain data
- AI-generated trend estimates shall show the reasoning on click

#### FR-UI-010: Supranational Overlay
- Users shall be able to toggle supranational entity overlays on the map
- Selecting an overlay (e.g., EU, NATO) shall highlight member countries
- Clicking the overlay label shall show the entity's profile

#### FR-UI-011: Responsive Design
- The UI shall be optimized for desktop (1920×1080 minimum target)
- The UI shall be functional on tablet (1024×768)
- The UI shall gracefully degrade on mobile (show briefing and country cards, skip map)

#### FR-UI-012: Performance
- Initial page load (map + summary data): < 5 seconds
- Country detail panel load: < 2 seconds
- Relation data load: < 2 seconds
- All interactions (pan map, open panels): < 100ms response
- Browser memory usage: < 500MB

#### FR-UI-013: Offline Awareness
- If data files fail to load, the UI shall display a clear error message
- The UI shall show "last updated" date so users know data freshness
- The UI shall cache loaded chunks in browser memory for session duration

---

## 4. Non-Functional Requirements

### 4.1 Data Quality

#### NFR-DQ-001: Coverage
- Tier 1 countries (30): ≥ 90% of schema factors populated
- Tier 2 countries (25): ≥ 70% of schema factors populated
- Tier 3 countries (20): ≥ 50% of schema factors populated

#### NFR-DQ-002: Freshness
- Financial data (exchange rates, bond yields): ≤ 1 week old
- Macroeconomic data: ≤ 1 quarter old
- Political data: ≤ 1 week old for events, ≤ 1 year for indices
- Military data: ≤ 1 quarter old
- Demographic data: ≤ 1 year old
- Geographic/cultural data: ≤ 3 years old (rarely changes)

#### NFR-DQ-003: Accuracy
- Official statistical data: target < 5% deviation from source
- AI-extracted data: target < 15% deviation from ground truth
- Trend estimates: target > 60% directional accuracy (backtested)
- All data points must have traceable provenance

#### NFR-DQ-004: Consistency
- No internal contradictions (e.g., GDP composition must sum to ~100%)
- Bilateral data symmetric where applicable (A→B trade ≈ B→A trade)
- Timeseries continuous (no unexplained gaps)

### 4.2 Reliability

#### NFR-RE-001: Pipeline Reliability
- Weekly pipeline success rate target: > 95% (< 3 failures per year)
- Any single agent failure shall not corrupt existing data
- Recovery from failure shall take < 30 minutes

#### NFR-RE-002: Website Availability
- GitHub Pages uptime: 99.9% (GitHub's SLA)
- No dependency on external APIs at runtime (all data pre-computed)
- Graceful degradation: site works even if some data chunks are unavailable

### 4.3 Security & Privacy

#### NFR-SE-001: No PII
- The system shall not collect or store personally identifiable information
- Exception: names of heads of state (public information)

#### NFR-SE-002: API Key Management
- No API keys in source code or committed files
- API keys stored in environment variables or .env file in .gitignore

#### NFR-SE-003: Source Attribution
- All data displayed shall credit its source
- No proprietary data used without license compliance

### 4.4 Maintainability

#### NFR-MA-001: Schema Evolution
- The factor model schema shall be versioned
- Schema changes shall be backward-compatible where possible
- A migration script shall handle breaking schema changes

#### NFR-MA-002: Agent Modularity
- Each agent shall be independently re-runnable
- Adding a new data source shall require modifying only the relevant gathering agent and the data source registry
- Adding a new factor shall require: schema update, relevant gatherer update, processor mapping update

#### NFR-MA-003: Documentation
- Every agent shall have a config file documenting its purpose, inputs, outputs, and methodology
- The factor model schema shall be fully documented
- Data sources shall be registered with access details and rate limits

### 4.5 Cost

#### NFR-CO-001: Operating Cost
- Claude Code MAX subscription: existing cost
- API costs for data sources: target < $50/month (prefer free sources)
- GitHub Pages: free
- Domain name (optional): ~$15/year

---

## 5. Constraints

### 5.1 Technical Constraints
- **No backend server.** The web UI is purely static. All computation happens in the weekly Claude Code session.
- **GitHub Pages limits.** 1GB repo, 100MB per file, 100GB/month bandwidth, no server-side processing.
- **Claude Code session limits.** Single session must complete all 18 agents. If session times out, re-run from last completed agent.
- **Web scraping fragility.** Web page layouts change without notice. Agents must handle extraction failures gracefully.
- **Free API tier limits.** Many APIs have rate limits or request caps on free tiers. Agents must stay within limits.

### 5.2 Data Constraints
- **No real-time data.** Data is at most 1 week old (updated weekly).
- **Incomplete coverage.** Not all factors will be available for all countries. The UI must handle missing data gracefully.
- **AI estimation uncertainty.** Trend estimates are AI-generated assessments, not statistically rigorous forecasts. This must be communicated clearly to users.
- **English language bias.** Most sources are English-language, potentially missing non-English government announcements or local news.

### 5.3 Legal Constraints
- **Data licensing.** Some data sources restrict commercial use. Track licensing status in data source registry.
- **Not financial advice.** The platform must include a disclaimer that it does not constitute investment advice.
- **Attribution requirements.** Some data sources require attribution. Implement in UI.

---

## 6. Acceptance Criteria

### 6.1 MVP (Minimum Viable Product)

The MVP is reached when:

- [ ] Factor model schema is fully defined and documented
- [ ] At least 30 Tier 1 countries have data for Layers 1-4 (Endowments, Institutions, Economy, Military)
- [ ] At least 100 bilateral relations are populated (top trade pairs)
- [ ] The weekly agent pipeline runs end-to-end successfully
- [ ] Trend estimates are generated for Tier 1 countries
- [ ] The map view renders with country coloring by at least 3 metrics
- [ ] Clicking a country shows a detail panel with available data
- [ ] The weekly briefing is generated and displayed
- [ ] Alerts are generated and displayed
- [ ] The site is deployed on GitHub Pages
- [ ] Data loads are chunked and on-demand

### 6.2 Full Product (Post-MVP)

- [ ] All 75 countries populated to target coverage levels
- [ ] 300+ bilateral relations populated
- [ ] Supranational entity overlays functional
- [ ] Relation explorer with network graph visualization
- [ ] Comparison tool functional
- [ ] Timeseries charts for key factors
- [ ] Scenario sandbox (stretch goal)
- [ ] Mobile-friendly view (briefing + country cards)
- [ ] Custom watchlist functionality
- [ ] Backtesting dashboard for trend estimate accuracy

---

## 7. Glossary

| Term | Definition |
|------|-----------|
| **Factor** | A single quantitative or categorical data point describing an aspect of a country |
| **Layer** | A thematic grouping of related factors (e.g., Layer 1: Endowments) |
| **Trend Estimate** | AI-generated assessment of a factor's quarterly trajectory |
| **Bilateral Relation** | The multi-dimensional relationship record between two countries |
| **Confidence Score** | 0-1 measure of data reliability, based on source quality and corroboration |
| **Escalation** | A data update that requires human review before integration |
| **Alert** | An automated notification triggered when predefined thresholds are crossed |
| **Derived Metric** | A composite score computed from multiple base factors |
| **Chunk** | A JSON file containing a subset of the data model, loaded on-demand by the UI |
| **Agent** | A defined processing step in the weekly update pipeline, executed by Claude Code |
| **Tier 1/2/3** | Country priority levels determining data coverage depth |
