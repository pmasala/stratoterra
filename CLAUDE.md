# CLAUDE.md — Stratoterra Project Context

## What is this project?

Stratoterra is an AI-powered geopolitical intelligence platform for investors. It visualizes 200+ economic, political, military, and relational factors across 75 countries on an interactive 2D world map. Data is updated weekly via an autonomous AI agent pipeline. The web UI is a static site hosted on GitHub Pages.

## Architecture

```
Weekly Pipeline (Claude Code MAX, 3-5 hours)
  → 19 agents run sequentially (Agent 17 invoked twice)
  → Output: JSON data files in /data (English + translated variants)
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
│   │   ├── i18n.js            ← Internationalization module (EN/IT)
│   │   └── ...                ← Other JS modules
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
- **Localization**: UI strings and data content translated into multiple languages (EN default + IT). Agent 19 handles content translation as the last step before quality reporting

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
Phase 1:  GATHER      (Agents 1-6)    60-120 min   WebSearch/WebFetch + public APIs
Phase 2:  PROCESS     (Agent 7)       20-30 min    Map raw data to schema
Phase 3:  VALIDATE    (Agent 8)       15-20 min    Plausibility + consistency checks
Phase 3b: AUDIT       (Agent 17a)      2-5 min     Autonomous escalation audit
Phase 4:  INTEGRATE   (Agent 9)        5-10 min    Merge into /data
Phase 5:  ANALYZE     (Agents 10-12)  50-75 min    Trends, derived metrics, alerts
Phase 6:  SYNTHESIZE  (Agents 13-14)  30-45 min    Country narratives, weekly briefing
Phase 6.5: PUBLISH    (Agent 18)      20-30 min    Full-length articles with SVG
Phase 6.7: TRANSLATE  (Agent 19)      30-60 min    Translate content to target languages
Phase 7:  FINALIZE    (Agent 15)       5 min        Quality report
Phase 7b: AUDIT       (Agent 17b)      1-2 min     Autonomous quality audit (GO/NO-GO)
Phase 7c: COMMIT      (Agent 16)       5 min        Archive, chunks, git commit
```

### Autonomous Auditing

Agent 17 (Autonomous Auditor) replaces all human review checkpoints:
- **After Agent 8:** Resolves ESCALATE verdicts using rule-based decision framework (source count, confidence, trend alignment). Decisions: ACCEPT, ACCEPT_WITH_DOWNGRADE, REJECT.
- **After Agent 15:** Reviews quality report metrics against GO/CONDITIONAL_GO/NO_GO thresholds. If NO_GO, Agent 16 skips the commit.

No human intervention is required during the pipeline run.

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
- ESCALATE triggers Agent 17 autonomous audit (target: ≤20 per run)
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

## Localization (i18n)

The platform supports multiple languages. Currently: **English (en)** as default and **Italian (it)**.

### Architecture

1. **UI Strings** (`web/js/i18n.js`): All hardcoded UI strings (labels, buttons, headings, error messages) are managed through the `I18n` module. Each string has a translation key (e.g., `nav.map`, `metric.gdp_growth`). Translations are defined inline in the module.

2. **Data Content** (Agent 19): All narrative content (articles, briefings, country summaries, alerts, etc.) is generated in English by the pipeline, then translated by Agent 19 into target languages. Translated files are stored alongside originals with a `_{LANG}` suffix (e.g., `weekly_briefing_it.json`).

3. **DataLoader**: The data loader checks for a `translation_manifest.json` to know which languages have translated content. When a non-English language is active, it tries loading `_LANG.json` files first, falling back to English if not available.

4. **Language Selector**: Users switch languages via a dropdown in the header. The preference is saved in `localStorage`.

### Adding a New Language

1. Add the language to `I18n.SUPPORTED_LANGUAGES` in `web/js/i18n.js`
2. Add a complete translation dictionary in the `translations` object in `web/js/i18n.js`
3. Add the language to `target_languages` in `/agents/config/agent_19_translator.json`
4. Re-run Agent 19 to generate translated data files

### Conventions

- Translation keys use dot notation: `namespace.key` (e.g., `nav.map`, `metric.gdp_growth`)
- Constants (METRIC_CONFIG, REGIONS, etc.) store i18n keys as `label` values, resolved via `I18n.t()` at render time
- Numeric values, ISO codes, and structural data are never translated
- Country names in the target language follow conventional local usage

## Testing

**MANDATORY POLICY: After every pipeline run or any agent-driven data update, the full test suite (`python3 -m pytest tests/scripts/ -v`) MUST be executed and ALL tests MUST PASS (zero failures). No data commit is allowed until this gate passes. If any test fails, fix the root cause (in data, agents, or tests if the schema legitimately changed) before committing.**

Tests run automatically as part of Agent 15 and post-pipeline validation. See `docs/04_TEST_PLAN.md`. Key test groups:

- Schema validation (every file conforms to schema)
- Plausibility checks (values in realistic ranges)
- Consistency checks (cross-file, bilateral symmetry, sums)
- Regression checks (no data loss week-over-week)
- Coverage checks (Tier 1 ≥90%, Tier 2 ≥70%, Tier 3 ≥50%)

Test command: `python3 -m pytest tests/scripts/ -v --tb=short`

## Important Warnings

- **Never modify /data/ directly** — always go through the pipeline
- **No API keys needed** — pipeline uses Claude's native tools for all data access
- **Always validate before integrating** — Agent 8 must run before Agent 9
- **Staging files are ephemeral** — raw_collected and processed are cleaned each run
- **The /data/chunks/ directory is what the UI reads** — Agent 16 generates these
- **AI-generated content must be labeled** — all narratives and trend estimates
