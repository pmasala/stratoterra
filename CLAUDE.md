# CLAUDE.md — Stratoterra Project Context

## What is this project?

Stratoterra is an AI-powered geopolitical intelligence platform for investors. It visualizes 200+ economic, political, military, and relational factors across 75 countries on an interactive 2D world map. Data is updated weekly via an autonomous AI agent pipeline. The web UI is a static site hosted on GitHub Pages.

## Architecture

```
Weekly Pipeline (Claude Code MAX, 3-5 hours)
  → 16 agents run sequentially
  → Output: JSON data files in /data
  → git commit + push

GitHub Pages (static site)
  → HTML/JS/CSS in /web
  → Reads chunked JSON from /data/chunks
  → Leaflet.js 2D map + panels
  → Zero backend
```

## Project Structure

```
stratoterra/
├── CLAUDE.md              ← You are here
├── setup_project.sh       ← Run once to create directory structure
├── LICENSE                 ← AGPL-3.0
│
├── docs/                  ← Design specifications (read these first!)
│   ├── 00_README.md
│   ├── 01_FACTOR_MODEL_SPEC.md    ← Complete data schema (6 layers, 200+ factors)
│   ├── 02_AGENT_ARCHITECTURE.md   ← 16 agents, pipeline design
│   ├── 03_REQUIREMENTS.md         ← Functional & non-functional requirements
│   ├── 04_TEST_PLAN.md            ← Test specifications
│   ├── 05_AGENT_CONFIGS.md        ← Agent prompts (the orchestrator lives here)
│   ├── 06_WEB_UI_SPEC.md          ← Frontend design
│   └── 07_DATA_SOURCES.md         ← All data sources with API details
│
├── agents/
│   ├── config/            ← Agent configuration files
│   ├── prompts/           ← Individual agent prompt files
│   └── scripts/           ← Helper scripts for agents
│
├── data/                  ← THE MODEL (JSON files, served to UI)
│   ├── countries/         ← One {ISO3}.json per country (full factor model)
│   ├── relations/         ← One {A}_{B}.json per bilateral pair
│   ├── supranational/     ← EU.json, NATO.json, etc.
│   ├── indices/           ← country_list.json, alert_index.json, relation_index.json
│   ├── timeseries/        ← Historical values for key metrics
│   ├── metadata/          ← Schema version, update logs, quality reports
│   ├── global/            ← Weekly briefing, rankings, event feed, chokepoints
│   └── chunks/            ← UI-optimized chunks (lazy-loaded by frontend)
│       ├── country-summary/   ← all_countries_summary.json (~500KB, loaded on init)
│       ├── country-detail/    ← Per-country detail files (loaded on click)
│       ├── relations/         ← Relation files (loaded on demand)
│       ├── timeseries/        ← Chart data (loaded on demand)
│       ├── global/            ← Briefing, alerts, rankings
│       └── supranational/     ← Entity profiles
│
├── staging/               ← Intermediate agent outputs (cleaned between runs)
│   ├── raw_collected/     ← Agent 1-6 outputs
│   ├── processed/         ← Agent 7 output
│   ├── validated/         ← Agent 8 output + escalation reports
│   ├── trends/            ← Agent 10 output
│   └── run_log.json       ← Pipeline execution log
│
├── web/                   ← Static frontend (deployed to GitHub Pages)
│   ├── index.html
│   ├── js/
│   ├── css/
│   └── assets/
│
├── archive/               ← Historical snapshots per weekly run
│
└── tests/
    ├── fixtures/          ← Mock data for offline testing
    ├── schemas/           ← JSON Schema validation files
    ├── scripts/           ← Test runner scripts
    └── reports/           ← Test result outputs
```

## Key Design Decisions

- **75 countries** in 3 tiers: 30 Tier 1 (major economies), 25 Tier 2 (regional players), 20 Tier 3 (frontier/watchlist)
- **~300-400 bilateral pairs** tracked (not all 2,775 possible), focused on meaningful interactions
- **6-layer factor model**: Endowments → Institutions → Economy → Military → Relations → Derived
- **Weekly cadence**: All data gathered and processed in one batch run
- **No live backend**: Everything is pre-computed JSON served as static files
- **2D map** using Leaflet.js (not 3D globe — better for data overlays and readability)
- **GitHub Pages** hosting (free, sufficient bandwidth for personal/small audience use)
- **AGPL-3.0 license** for code; CC-BY-SA-4.0 for documentation; CC-BY-4.0 for data

## Weekly Pipeline — How to Run

The full pipeline is defined in `docs/05_AGENT_CONFIGS.md`. The master orchestrator prompt is at the top of that file.

**Prerequisites:** Claude Code MAX subscription. No API keys or `.env` file needed — all data sources are accessed via Claude's native `WebSearch` and `WebFetch` tools, or through public APIs (World Bank, IMF) that require no authentication.

**Quick start:**
```bash
./agents/scripts/run_weekly_update.sh   # validates environment, creates staging dirs
claude --dangerously-skip-permissions agents/prompts/orchestrator.md
```

### Pipeline Phases

```
Phase 1: GATHER      (Agents 1-6)   60-120 min   WebSearch/WebFetch + public APIs
Phase 2: PROCESS     (Agent 7)      20-30 min    Map raw data to schema
Phase 3: VALIDATE    (Agent 8)      15-20 min    Plausibility + consistency checks
  ⚠ HUMAN REVIEW: Escalated items presented here (~30 min)
Phase 4: INTEGRATE   (Agent 9)      5-10 min     Merge into /data
Phase 5: ANALYZE     (Agents 10-12) 50-75 min    Trends, derived metrics, alerts
Phase 6: SYNTHESIZE  (Agents 13-14) 30-45 min    Country narratives, weekly briefing
Phase 7: FINALIZE    (Agents 15-16) 7-10 min     Quality report, archive, commit
  ⚠ HUMAN REVIEW: Quality report presented here (~15 min)
```

### Human Review Budget: ~2 hours

- Reviewing ESCALATED items from Agent 8: ~30 min
- Reading quality report from Agent 15: ~15 min
- Spot-checking country narratives: ~30 min
- Reviewing and approving git commit: ~5 min
- Buffer for investigating issues: ~40 min

## Agent Communication

Agents communicate via files in `/staging/`. Each agent reads from defined input files and writes to defined output files. No shared memory or database — purely file-based.

The pipeline is sequential. If an agent fails:
1. Check `staging/run_log.json` for the failure point
2. Fix the issue
3. Re-run from the failed agent onward (agents are idempotent)

## Data Sources (all free)

Primary sources — see `docs/07_DATA_SOURCES.md` for full details:
- **World Bank API** — GDP, population, governance (CC-BY 4.0)
- **IMF** — WEO forecasts, IFS monetary data, trade flows
- **UN Comtrade** — Bilateral trade (free tier: 100 req/hour)
- **GDELT Project** — Global news events (free, real-time)
- **ACLED** — Conflict events (free for non-commercial)
- **SIPRI** — Military spending, arms transfers
- **Trading Economics** — Bond yields, credit ratings, FX (web fetch)
- **EIA** — Energy production/consumption
- **USGS** — Mineral resources
- **Freedom House, EIU, Transparency International** — Governance indices

All sources are free tier. Total API cost: $0/month. Gathering agents access these via Claude's native `WebSearch` and `WebFetch` tools — no API keys required.

## Data Quality Rules

- Every data point has a confidence score (0.0 - 1.0)
- Multi-source corroboration required for high confidence
- Validation verdicts: ACCEPT, ACCEPT_WITH_NOTE, FLAG, REJECT, ESCALATE
- ESCALATE triggers human review (target: ≤20 per run)
- Trend estimates always include reasoning, evidence, and counter-arguments

## Code Style & Conventions

- **Country codes**: Always ISO 3166-1 alpha-3 (USA, CHN, DEU)
- **Relation pairs**: Alphabetically ordered (CHN_USA, not USA_CHN)
- **Monetary values**: Always USD
- **Dates**: ISO 8601 (2026-03-01T12:00:00Z)
- **Percentages**: 0-100 for display values, 0.0-1.0 for indices/scores
- **Trend labels**: strong_growth, growth, stable, decrease, strong_decrease
- **Alert severities**: critical, warning, watch
- **JSON files**: Pretty-printed with 2-space indent for readability

## Testing

Tests run automatically as part of Agent 15 and post-pipeline validation. See `docs/04_TEST_PLAN.md`. Key test groups:

- Schema validation (every file conforms to schema)
- Plausibility checks (values in realistic ranges)
- Consistency checks (cross-file, bilateral symmetry, sums)
- Regression checks (no data loss week-over-week)
- Coverage checks (Tier 1 ≥90%, Tier 2 ≥70%, Tier 3 ≥50%)

## Important Warnings

- **Never modify /data/ directly** — always go through the pipeline
- **No API keys needed** — pipeline uses Claude's native tools for all data access
- **Always validate before integrating** — Agent 8 must run before Agent 9
- **Staging files are ephemeral** — raw_collected and processed are cleaned each run
- **The /data/chunks/ directory is what the UI reads** — Agent 16 generates these
- **AI-generated content must be labeled** — all narratives and trend estimates
