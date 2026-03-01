# Geopolitical Intelligence Model

**An AI-powered, interactive geopolitical intelligence platform for investors.**

---

## What is this?

An interactive web-based map that visualizes political, economic, military, and relational factors for ~75 countries. The model is updated weekly using an AI agent pipeline running on Claude Code MAX. The web UI is a static site hosted on GitHub Pages.

## Architecture

```
┌─────────────────────────────────┐
│  Claude Code MAX (weekly)       │
│  16 AI agents in sequence       │
│  3-5 hours per run              │
│  Human review: ~2 hours         │
│                                 │
│  Output: JSON data files        │
└───────────────┬─────────────────┘
                │ git push
                ▼
┌─────────────────────────────────┐
│  GitHub Pages                   │
│  Static HTML/JS/CSS             │
│  Reads JSON chunks              │
│  Interactive 2D world map       │
│  Zero backend, zero cost        │
└─────────────────────────────────┘
```

## Documentation

| Document | Description |
|---|---|
| `01_FACTOR_MODEL_SPEC.md` | Complete data schema — every factor, data type, source, and update frequency for all 6 layers of the model |
| `02_AGENT_ARCHITECTURE.md` | Agent pipeline design — 16 agents, their roles, execution order, error handling, and the full weekly workflow |
| `03_REQUIREMENTS.md` | Functional and non-functional requirements — what the system must do, quality targets, constraints |
| `04_TEST_PLAN.md` | Unit, integration, end-to-end, regression, and performance test specifications |
| `05_AGENT_CONFIGS.md` | Ready-to-use Claude Code prompt configurations for each agent and the master orchestrator |
| `06_WEB_UI_SPEC.md` | Frontend design — layout, components, interactions, color system, responsive behavior, data loading strategy |
| `07_DATA_SOURCES.md` | Complete registry of all data sources — APIs, URLs, rate limits, licensing, cost, reliability ratings |

## Model Structure

The model organizes country data into 6 layers:

```
Layer 1: ENDOWMENTS — Resources, Geography, Climate, Demographics
Layer 2: INSTITUTIONS — Cultural factors, Political system, Governance
Layer 3: ECONOMY — Macroeconomics, Financial system, Trade
Layer 4: MILITARY — Forces, Capabilities, Conflicts, Alliances
Layer 5: RELATIONS — Bilateral trade, diplomatic, military, financial ties
Layer 6: DERIVED — Computed: risk scores, vulnerability, power indices
```

Plus: Supranational entities (EU, NATO, BRICS, etc.) as overlays.

## Country Coverage

- **Tier 1 (30):** Major economies and powers — full coverage
- **Tier 2 (25):** Important regional players — high coverage
- **Tier 3 (20):** Frontier/watchlist — basic coverage

## Weekly Update Pipeline

```
Phase 1: Gather data from 10+ source types     (60-120 min)
Phase 2: Process and structure into schema      (20-30 min)
Phase 3: Validate — plausibility + consistency  (15-20 min)
Phase 4: Integrate into data store              (5-10 min)
Phase 5: Analyze — trends + derived + alerts    (50-75 min)
Phase 6: Synthesize — narratives + briefing     (30-45 min)
Phase 7: Finalize — quality report + archive    (7-10 min)
                                          Total: ~3-5 hours
```

## Getting Started

### Prerequisites
- Claude Code MAX subscription
- GitHub account with GitHub Pages enabled
- Git installed locally

### Initial Setup

```bash
# Clone the repo
git clone https://github.com/{you}/geopolitical-model.git
cd geopolitical-model

# Run the setup script
bash agents/scripts/setup_project.sh

# Seed initial data (first run will take longer)
# Open Claude Code MAX and paste the orchestrator prompt from 05_AGENT_CONFIGS.md
```

### Weekly Update

1. Open Claude Code MAX
2. Navigate to the project directory
3. Paste or invoke the orchestrator prompt
4. Monitor progress (~3-5 hours)
5. Review escalations when prompted (~30 min)
6. Review quality report when prompted (~15 min)
7. Approve and push: `git push origin main`
8. GitHub Pages deploys automatically

## Cost

- Claude Code MAX subscription: (your existing subscription)
- Data sources: $0/month (all free tier)
- Hosting: $0/month (GitHub Pages)
- Domain (optional): ~$15/year

## Disclaimer

This platform provides AI-generated geopolitical analysis for informational and educational purposes only. It does not constitute investment, financial, legal, or tax advice. Data is sourced from public databases and may be incomplete or delayed. Trend estimates are AI-generated assessments, not statistical forecasts.
