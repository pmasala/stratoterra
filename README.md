# Stratoterra

**An AI-powered, interactive geopolitical intelligence platform for personal use.**

Live: [pmasala.github.io/stratoterra/web/](https://pmasala.github.io/stratoterra/web/)

---

## What is this?

An interactive web-based map that visualizes political, economic, military, and relational factors for 75 countries. Data is updated weekly by an autonomous 18-agent AI pipeline running on Claude Code MAX. The web UI is a static site hosted on GitHub Pages — zero backend, zero cost.

## Architecture

```
┌─────────────────────────────────┐
│  Claude Code MAX (weekly)       │
│  18 AI agents, fully autonomous │
│  ~3-5 hours per run             │
│  No human review required       │
│                                 │
│  Output: JSON data files        │
└───────────────┬─────────────────┘
                │ git push
                ▼
┌─────────────────────────────────┐
│  GitHub Pages                   │
│  Static HTML/JS/CSS + JSON data │
│  Interactive 2D Leaflet.js map  │
│  Zero backend, zero cost        │
└─────────────────────────────────┘
```

## Model Structure

The model organizes country data into 6 layers:

```
Layer 1: ENDOWMENTS   — Resources, Geography, Climate, Demographics
Layer 2: INSTITUTIONS — Cultural factors, Political system, Governance
Layer 3: ECONOMY      — Macroeconomics, Financial system, Trade
Layer 4: MILITARY     — Forces, Capabilities, Conflicts, Alliances
Layer 5: RELATIONS    — Bilateral trade, diplomatic, military, financial ties
Layer 6: DERIVED      — Computed: risk scores, vulnerability, power indices
```

Plus: Supranational entities (EU, NATO, BRICS, etc.) as overlays.

### Country Coverage

- **Tier 1 (30):** Major economies and powers — full coverage
- **Tier 2 (25):** Important regional players — high coverage
- **Tier 3 (20):** Frontier/watchlist — basic coverage

## Getting Started

### Prerequisites

- **Python 3.x** — for local server, tests, and pre-fetch scripts
- **Git**
- **Node.js + npm** — only needed for Playwright E2E tests
- **Claude Code MAX subscription** — only needed to run the data pipeline

### Clone and Run Locally

```bash
# Clone the repo
git clone https://github.com/pmasala/stratoterra.git
cd stratoterra

# Start a local server from the repo root
python3 -m http.server 8089

# Open in browser
# http://localhost:8089/web/
```

No build step — the frontend is vanilla HTML/JS/CSS. The local server must run from the repo root so that both `/web/` (the app) and `/data/` (the JSON data) are accessible.

### Running Tests

#### Data validation tests (pytest)

```bash
python3 -m pytest tests/scripts/ -v --tb=short
```

Covers schema validation, plausibility checks, cross-file consistency, regression, and coverage.

#### E2E browser tests (Playwright)

```bash
# Install dependencies (first time)
npm install
npx playwright install chromium

# Run headless
npm test

# Run with visible browser
npm run test:headed

# View HTML report
npm run test:report
```

Playwright auto-starts a local server on port 8089 and runs tests against Chromium (1280x720 viewport).

## Weekly Update Pipeline

The pipeline is fully autonomous — Agent 17 (Autonomous Auditor) replaces all human review checkpoints.

```
Phase 1:  GATHER      (Agents 1-6)     60-120 min   Data from 10+ public sources
Phase 2:  PROCESS     (Agent 7)        20-30 min    Map raw data to schema
Phase 3:  VALIDATE    (Agent 8)        15-20 min    Plausibility + consistency
Phase 3b: AUDIT       (Agent 17a)       2-5 min     Autonomous escalation audit
Phase 4:  INTEGRATE   (Agent 9)         5-10 min    Merge into /data
Phase 5:  ANALYZE     (Agents 10-12)   50-75 min    Trends, derived metrics, alerts
Phase 6:  SYNTHESIZE  (Agents 13-14)   30-45 min    Country narratives, briefing
Phase 6.5: ARTICLES   (Agent 18)       20-30 min    Full news articles with SVGs
Phase 7:  FINALIZE    (Agent 15)        5 min       Quality report
Phase 7b: AUDIT       (Agent 17b)       1-2 min     GO/NO-GO quality gate
Phase 7c: COMMIT      (Agent 16)        5 min       Archive, chunks, git commit
                                  Total: ~3-5 hours
```

### Running the Pipeline

```bash
# 1. Validate environment and create staging directories
./agents/scripts/run_weekly_update.sh

# 2. Run the orchestrator in Claude Code MAX
claude --dangerously-skip-permissions agents/prompts/orchestrator.md

# 3. Pipeline runs autonomously (~3-5 hours)
#    Agent 16 commits and pushes when done
#    GitHub Pages deploys automatically
```

No API keys or `.env` file needed — all data sources are accessed via Claude's native `WebSearch` and `WebFetch` tools, or through public APIs that require no authentication.

### Re-running a Single Agent

```bash
./agents/scripts/run_single_agent.sh <agent_number>
# Prints the agent prompt — copy-paste into Claude Code MAX
```

Agents are idempotent, so it's safe to re-run from any failure point.

### Daily Article Generation

Agent 18 can run standalone between weekly pipeline runs:

```bash
./agents/scripts/run_daily_articles.sh
```

Generates 5 news articles from the latest briefing, builds the article index, and commits.

## Pre-Fetch System (Optional)

Deterministic Python scripts that fetch structured data before the pipeline runs. This gives agents a head start with cached data.

```bash
# Install dependencies
pip install -r agents/prefetch/requirements.txt

# Run all no-key sources (World Bank, IMF, GDELT, FX/Commodities)
./agents/scripts/run_prefetch.sh --no-key

# Run all sources (requires API keys in agents/prefetch/.env)
./agents/scripts/run_prefetch.sh all
```

API keys are optional. See `agents/prefetch/.env.example` for the template. Sources that need keys (ACLED, EIA, Comtrade) are skipped if keys are missing.

Pre-fetch also runs automatically via GitHub Actions every Sunday at 06:00 UTC.

## CI/CD

Two GitHub Actions workflows:

| Workflow | Trigger | What it does |
|---|---|---|
| `static.yml` | Push to `main` | Deploys the entire repo to GitHub Pages |
| `prefetch.yml` | Sunday 06:00 UTC / manual | Runs pre-fetch scripts, commits results |

GitHub Pages serves the full repo — the frontend at `/web/` loads data from `/data/chunks/` using relative paths.

## Documentation

Detailed design specs in `docs/`:

| Document | Description |
|---|---|
| `01_FACTOR_MODEL_SPEC.md` | Complete data schema — 6 layers, 200+ factors |
| `02_AGENT_ARCHITECTURE.md` | Agent pipeline design — 18 agents, execution order |
| `03_REQUIREMENTS.md` | Functional and non-functional requirements |
| `04_TEST_PLAN.md` | Test specifications |
| `05_AGENT_CONFIGS.md` | Agent prompts and master orchestrator |
| `06_WEB_UI_SPEC.md` | Frontend design — layout, components, data loading |
| `07_DATA_SOURCES.md` | All data sources — APIs, rate limits, licensing |

## Cost

- Claude Code MAX subscription: (your existing subscription)
- Data sources: $0/month (all free tier)
- Hosting: $0/month (GitHub Pages)
- Domain (optional): ~$15/year

## License

Code: [AGPL-3.0](LICENSE) · Documentation: CC-BY-SA-4.0 · Data: CC-BY-4.0

## Disclaimer

This platform provides AI-generated geopolitical analysis for informational and educational purposes only. It does not constitute investment, financial, legal, or tax advice. Data is sourced from public databases and may be incomplete or delayed. Trend estimates are AI-generated assessments, not statistical forecasts.
