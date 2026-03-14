# Geopolitical Intelligence Model — Test Plan

**Version:** 1.1
**Date:** 2026-03-14
**Status:** Active
**Depends on:** `01_FACTOR_MODEL_SPEC.md`, `02_AGENT_ARCHITECTURE.md`, `03_REQUIREMENTS.md`

---

## 1. Testing Strategy Overview

### 1.1 Test Levels

```
┌────────────────────────────────────────────┐
│  Level 4: ACCEPTANCE TESTS                  │
│  Full system validation against MVP criteria│
├────────────────────────────────────────────┤
│  Level 3: END-TO-END TESTS                  │
│  Full pipeline execution with test data     │
├────────────────────────────────────────────┤
│  Level 2: INTEGRATION TESTS                 │
│  Agent-to-agent data flow validation        │
├────────────────────────────────────────────┤
│  Level 1: UNIT TESTS                        │
│  Individual agent & function validation     │
└────────────────────────────────────────────┘
```

### 1.2 Testing Approach for Claude Code Agents

Since agents are Claude Code prompt-driven processes (not traditional compiled code), testing takes a different form:

- **Unit tests** validate that individual agent outputs conform to expected schemas and contain sensible values
- **Integration tests** validate that output from Agent N is correctly consumed by Agent N+1
- **End-to-end tests** run the entire pipeline against a controlled dataset and verify final output
- **Regression tests** compare weekly outputs against previous weeks to detect unexpected changes

All tests are implemented as **validation scripts** that Claude Code runs after each agent or after the full pipeline. These scripts are JSON schema validators, data consistency checkers, and assertion-based verifiers.

### 1.3 Test Data Strategy

```
/tests
├── /fixtures                           # Static test data
│   ├── /mock_sources                   # Fake API responses for offline testing
│   ├── /expected_outputs               # Expected agent outputs for known inputs
│   └── /seed_data                      # Minimal starting dataset for testing
│
├── /schemas                            # JSON Schema validation files
│   ├── country_detail_schema.json
│   ├── country_summary_schema.json
│   ├── alert_schema.json
│   ├── briefing_schema.json
│   ├── relation_schema.json
│   └── manifest_schema.json
│
├── /scripts                            # Python test modules (pytest)
│   ├── run_all_tests.py                # Master test runner (JSON report output)
│   ├── test_schema_validation.py       # JSON schema conformance
│   ├── test_plausibility.py            # Value range checks
│   ├── test_data_consistency.py        # Cross-file symmetry
│   ├── test_agent_outputs.py           # Agent output validation
│   ├── test_pipeline_flow.py           # End-to-end pipeline
│   ├── test_ui_data_contract.py        # UI data expectations
│   ├── test_overlay_data.py            # Overlay geospatial data
│   ├── test_prefetch.py                # Pre-fetch unit tests
│   ├── test_prefetch_integration.py    # Pre-fetch integration tests
│   └── test_e2e_pipeline.py            # Full pipeline smoke test
│
├── /e2e                                # Playwright browser tests (TypeScript)
│   ├── app-init.spec.ts                # App initialization & data loading
│   ├── map-interactions.spec.ts        # Pan, zoom, click countries
│   ├── country-panel.spec.ts           # Country detail panel
│   ├── briefing-view.spec.ts           # Stories listing & article detail
│   ├── alert-dashboard.spec.ts         # Alert severity mode
│   ├── alert-ticker.spec.ts            # Alert ticker display
│   ├── search.spec.ts                  # Search autocomplete
│   ├── data-integrity.spec.ts          # Live data contract checks
│   └── fixtures/test-helpers.ts        # Shared test utilities
│
└── /reports                            # Test result outputs (gitignored)
    └── test_report_{date}.json
```

---

## 2. Unit Tests

### 2.1 Schema Validation Tests

**Purpose:** Verify that every data file conforms to the defined JSON schema.

```yaml
TEST_GROUP: Schema Validation
TEST_ID_PREFIX: UT-SCH

tests:

  - id: UT-SCH-001
    name: Country file validates against schema
    description: >
      Each country JSON file must conform to the country schema
      defined in 01_FACTOR_MODEL_SPEC.md
    input: /data/countries/{code}.json (each file)
    validation:
      - File is valid JSON
      - country_code is valid ISO 3166-1 alpha-3
      - All required top-level sections present (endowments, institutions, economy, military, derived)
      - All numeric fields are numbers (not strings)
      - All enum fields contain valid values
      - All confidence scores in range [0.0, 1.0]
      - All timestamps are valid ISO 8601
      - All percentage fields in range [0, 100] or [0.0, 1.0] as specified
      - All trend_enum fields contain valid values
    pass_criteria: Zero validation errors per file
    frequency: Every pipeline run

  - id: UT-SCH-002
    name: Relation file validates against schema
    input: /data/relations/{pair}.json (each file)
    validation:
      - File is valid JSON
      - country_a and country_b are valid ISO codes
      - country_a < country_b alphabetically (canonical ordering)
      - All sub-dimensions present (trade, people, diplomatic, military, science_tech, financial, energy, composite)
      - All numeric fields are numbers
      - Confidence and index values in valid ranges
    pass_criteria: Zero validation errors per file

  - id: UT-SCH-003
    name: Supranational entity file validates
    input: /data/supranational/{entity}.json
    validation:
      - Valid JSON
      - All member countries exist in country_list.json
      - Aggregate metrics are positive numbers
      - Cohesion_index in [0, 1]

  - id: UT-SCH-004
    name: Staging output files validate
    input: /staging/raw_collected/*.json, /staging/processed/*.json
    validation:
      - Each file has required metadata (collection_date, agent, summary)
      - Each record has source, confidence, timestamp
      - Event records have valid event_type from taxonomy
      - Factor update records have valid factor_path

  - id: UT-SCH-005
    name: Weekly briefing validates
    input: /data/global/weekly_briefing_{date}.json
    validation:
      - Has all required sections (headline, top_stories, regional_summaries, etc.)
      - top_stories is non-empty array
      - All country references are valid ISO codes
      - All dates are valid

  - id: UT-SCH-006
    name: Alert index validates
    input: /data/indices/alert_index.json
    validation:
      - Each alert has: severity, title, description, countries_affected, status
      - Severity is valid enum
      - Status is valid lifecycle state
      - All country codes are valid

  - id: UT-SCH-007
    name: Manifest file validates
    input: /data/chunks/manifest.json
    validation:
      - Lists all expected chunk files
      - Each entry has: path, last_modified, size_bytes
      - All referenced files actually exist on disk

  - id: UT-SCH-008
    name: Timeseries files validate
    input: /data/timeseries/*.json
    validation:
      - Timestamps are chronologically ordered
      - No duplicate timestamps
      - Values are numeric
      - No gaps exceeding 2× expected frequency
```

### 2.2 Data Plausibility Tests

**Purpose:** Verify that factor values are within realistic ranges.

```yaml
TEST_GROUP: Data Plausibility
TEST_ID_PREFIX: UT-PLB

tests:

  - id: UT-PLB-001
    name: GDP values are plausible
    validation:
      - GDP nominal > 0 for all countries
      - GDP per capita in range [$200, $200,000]
      - GDP growth rate in range [-30%, +30%]
      - GDP PPP > GDP nominal × 0.3 and < GDP nominal × 5.0
      - GDP composition (agriculture + industry + services) in range [95%, 105%]
    pass_criteria: No violations

  - id: UT-PLB-002
    name: Population values are plausible
    validation:
      - Population > 10,000 for all tracked countries
      - Population growth rate in range [-5%, +5%]
      - Median age in range [14, 55]
      - Age pyramid percentages sum to range [98%, 102%]
      - Life expectancy in range [40, 90]

  - id: UT-PLB-003
    name: Military values are plausible
    validation:
      - Active military <= population × 0.05 (5% of population)
      - Military expenditure <= GDP × 0.20 (20% of GDP is extreme upper bound)
      - Nuclear warheads: only countries with nuclear_status = declared_arsenal or undeclared_suspected should have warheads > 0
      - No country has > 10,000 nuclear warheads (current global max ~5,500)
      - Aircraft carriers: no country has > 15

  - id: UT-PLB-004
    name: Geographic values are plausible
    validation:
      - Total area > 0
      - Coastline >= 0
      - Landlocked countries have coastline == 0
      - Terrain composition percentages sum to range [95%, 105%]
      - Elevation values: lowest >= -500m, highest <= 9,000m

  - id: UT-PLB-005
    name: Economic indices in range
    validation:
      - Democracy index in [0, 10]
      - Freedom House score in [0, 100]
      - Corruption perception index in [0, 100]
      - WGI scores in [-2.5, 2.5]
      - Gini coefficient in [0, 1]
      - HDI in [0, 1]
      - All capability domain scores in [0, 1]
      - Economic complexity index in [-3, 3]

  - id: UT-PLB-006
    name: Relation values are plausible
    validation:
      - Bilateral trade volume > 0 (if relation exists)
      - Trade dependency ratios in [0, 1]
      - UN voting alignment in [0, 1]
      - All composite scores in [0, 1]
      - power_asymmetry in [-1, 1]
      - Flight time > 0 hours
      - Shipping time > 0 days

  - id: UT-PLB-007
    name: Resource values are plausible
    validation:
      - Annual production >= 0
      - Domestic consumption >= 0
      - Global share of production in [0, 1]
      - Global share of reserves in [0, 1]
      - Sum of all countries' global_share_of_production for one resource in [0.8, 1.2]
        (allowing for rounding / data incompleteness)
      - Seasonal profiles: 12 elements, all > 0, average ≈ 1.0

  - id: UT-PLB-008
    name: Derived metrics are plausible
    validation:
      - All indices in [0, 1] unless otherwise specified
      - Composite national power index in [0, 100]
      - Political risk premium >= 0 (in basis points)
      - Probability scores in [0, 1]
      - Self-sufficiency indices in [0, 1]
```

### 2.3 Agent Output Tests

**Purpose:** Verify that each agent produces correctly structured output.

```yaml
TEST_GROUP: Agent Output Validation
TEST_ID_PREFIX: UT-AGT

tests:

  - id: UT-AGT-001
    name: Official Stats Gatherer output structure
    trigger: After Agent 1 completes
    input: /staging/raw_collected/official_stats_{date}.json
    validation:
      - Has collection_date, agent, records, errors, skipped, summary
      - Each record has: country_code, factor_path, new_value, source, confidence
      - summary.total_queries > 0
      - summary.successful > summary.total_queries × 0.80 (>80% success rate)
      - No duplicate (country_code, factor_path) pairs

  - id: UT-AGT-002
    name: Financial Data Gatherer output structure
    trigger: After Agent 2 completes
    input: /staging/raw_collected/financial_data_{date}.json
    validation:
      - Same base structure as UT-AGT-001
      - Exchange rates present for all Tier 1-2 currencies
      - Each rate has market_timestamp within last 7 days
      - weekly_change_pct computed correctly

  - id: UT-AGT-003
    name: News Events Gatherer output structure
    trigger: After Agent 3 completes
    input: /staging/raw_collected/news_events_{date}.json
    validation:
      - Has events array and summary
      - Each event has: event_id, headline, date, event_type, countries_involved, severity, certainty_level, confidence
      - event_type values are from defined taxonomy
      - severity values are valid enum
      - certainty_level values are valid enum
      - summary.relevant_events_extracted > 0
      - No duplicate event_ids
      - All dates within last 14 days

  - id: UT-AGT-004
    name: Fact Extractor output structure
    trigger: After Agent 7 completes
    input: /staging/processed/factor_updates_{date}.json
    validation:
      - Each update has: update_id, target, factor_path, new_value, source_agent, confidence
      - factor_path matches a valid path in the schema
      - country_code is valid ISO code
      - No conflicting updates (same factor_path + country with different values)
        without explicit conflict resolution

  - id: UT-AGT-005
    name: Validator output structure
    trigger: After Agent 8 completes
    input: /staging/validated/validated_updates_{date}.json
    validation:
      - Every update from processor has a corresponding validation verdict
      - Verdict is one of: ACCEPT, ACCEPT_WITH_NOTE, FLAG, REJECT, ESCALATE
      - REJECT and ESCALATE entries have reason field
      - Distribution: REJECT < 10%, ESCALATE < 5%
      - Validation report has summary statistics

  - id: UT-AGT-006
    name: Trend Estimator output structure
    trigger: After Agent 10 completes
    input: /staging/trends/trend_estimates_{date}.json
    validation:
      - Has estimates for each Tier 1-2 country × key factors
      - Each estimate has: factor_path, country_code, trend, confidence, reasoning, supporting_evidence
      - trend is valid enum
      - confidence in [0, 1]
      - reasoning is non-empty string with > 20 characters
      - supporting_evidence has >= 1 entry
      - Total estimates ≈ 55 countries × 11 factors = ~605 (allow ±10%)

  - id: UT-AGT-007
    name: Country Profile Synthesizer output
    trigger: After Agent 13 completes
    validation:
      - Each Tier 1-2 country JSON has updated narrative section
      - narrative.executive_summary is non-empty, 100-500 characters
      - narrative.generated_at is within last 24 hours
      - narrative.key_changes_this_week is array
      - narrative.outlook is non-empty
      - narrative.investor_implications is non-empty

  - id: UT-AGT-008
    name: Weekly Briefing output
    trigger: After Agent 14 completes
    validation:
      - /data/global/weekly_briefing_{date}.json exists
      - Has headline, top_stories (≥ 3), regional_summaries (all regions present)
      - All referenced country codes are valid
      - No region summary is empty
```

---

## 3. Integration Tests

### 3.1 Agent Pipeline Flow Tests

**Purpose:** Verify that data flows correctly between agents.

```yaml
TEST_GROUP: Integration - Pipeline Flow
TEST_ID_PREFIX: IT-FLW

tests:

  - id: IT-FLW-001
    name: Gatherer → Processor data flow
    description: >
      All records produced by gathering agents (Agents 1-6) are
      consumed and mapped by the Fact Extractor (Agent 7)
    validation:
      - Count total records across all gathering agent outputs
      - Count mapped + unmapped in processor output
      - mapped + unmapped == total input records
      - unmapped < 10% of total
      - Every gatherer agent is represented in processor input
        (no agent's output was missed)

  - id: IT-FLW-002
    name: Processor → Validator data flow
    description: >
      All factor_updates from processor are evaluated by validator
    validation:
      - Count updates in processor output
      - Count verdicts in validator output
      - They should match exactly
      - Each update_id in processor has corresponding verdict in validator

  - id: IT-FLW-003
    name: Validator → Integrator data flow
    description: >
      Only ACCEPT and FLAG verdicts are integrated into /data.
      REJECT items are discarded. ESCALATE items are held.
    validation:
      - Count ACCEPT + FLAG verdicts
      - Count changes in /data (diff against previous state)
      - Changes should equal ACCEPT + FLAG count (±5% for merge deduplication)
      - REJECT items: verify corresponding factor in /data was NOT changed
      - ESCALATE items: verify they are listed in escalation report

  - id: IT-FLW-004
    name: Data → Trend Estimator input completeness
    description: >
      Trend Estimator receives current data + timeseries + events
    validation:
      - For each trend estimate produced, verify the input country exists in /data
      - Verify timeseries data was available for the factor being estimated
      - Verify recent events for the country were considered
        (check event references in supporting_evidence)

  - id: IT-FLW-005
    name: Derived Metrics use current data
    description: >
      Derived metrics should be computed from the just-updated factor values
    validation:
      - For each derived metric, check that input factors have
        last_updated >= start of current run
      - Verify composite scores change when underlying factors change
        (not using stale cached values)

  - id: IT-FLW-006
    name: Alerts reference valid data
    description: >
      Every alert references existing countries and factors
    validation:
      - Each alert's countries_affected are in country_list.json
      - Each alert's factors_affected are valid factor paths in schema
      - Alert thresholds are evaluated against current (not stale) values
```

### 3.2 Data Consistency Tests (Cross-File)

```yaml
TEST_GROUP: Integration - Data Consistency
TEST_ID_PREFIX: IT-CON

tests:

  - id: IT-CON-001
    name: Country list and country files match
    validation:
      - Every country in country_list.json has a corresponding {code}.json file
      - Every {code}.json file is listed in country_list.json
      - No orphaned files

  - id: IT-CON-002
    name: Relation files match relation index
    validation:
      - Every pair in relation_index.json has a corresponding file
      - Every relation file is in the index
      - Composite scores in index match those in the detail file

  - id: IT-CON-003
    name: Bilateral trade symmetry
    validation:
      - For each relation A_B:
        A's exports to B should ≈ B's imports from A (within 20% tolerance)
      - Sum of all bilateral exports for country A ≈ A's total_exports (within 30%)
      - Flag large discrepancies for investigation

  - id: IT-CON-004
    name: Global resource shares sum correctly
    validation:
      - For each resource type:
        Sum of global_share_of_production across all countries in [0.7, 1.1]
        (allowing for untracked countries and rounding)
      - No country has global_share > 1.0

  - id: IT-CON-005
    name: Supranational aggregate consistency
    validation:
      - For each supranational entity:
        aggregate_gdp ≈ sum of member countries' GDP (within 5%)
        aggregate_population ≈ sum of member populations (within 2%)
      - All listed members exist in country_list.json

  - id: IT-CON-006
    name: Rankings consistency
    validation:
      - global_rankings.json lists all Tier 1-2 countries for each metric
      - Rankings are correctly ordered (descending or ascending as appropriate)
      - No duplicate ranks
      - Values in rankings match values in country files

  - id: IT-CON-007
    name: Timeseries continuity
    validation:
      - For each timeseries file:
        Most recent entry timestamp matches last_updated in country file
        No gaps > 2× expected update frequency
        Values don't jump implausibly between consecutive entries

  - id: IT-CON-008
    name: Chunk manifest accuracy
    validation:
      - Every file listed in manifest.json exists
      - File sizes in manifest match actual file sizes (within 1KB)
      - last_modified dates are accurate
      - Summary chunk contains all countries from country_list.json
```

---

## 4. End-to-End Tests

### 4.1 Full Pipeline Test (Controlled Environment)

```yaml
TEST_GROUP: End-to-End Pipeline
TEST_ID_PREFIX: E2E-PIP

tests:

  - id: E2E-PIP-001
    name: Full pipeline with seed data
    description: >
      Run the complete 18-agent pipeline using seed/mock data to verify
      the entire system works end-to-end without depending on live APIs
    setup:
      - Copy seed data to /data (3 countries: USA, CHN, DEU)
      - Copy mock API responses to /tests/fixtures/mock_sources
      - Configure agents to use mock sources instead of live APIs
    execution:
      - Run all 18 agents in sequence
    validation:
      - All agents complete without errors
      - /data/countries has updated files for USA, CHN, DEU
      - /data/relations has updated files for USA_CHN, USA_DEU, CHN_DEU
      - Trend estimates generated for all 3 countries
      - Derived metrics computed for all 3 countries
      - Weekly briefing generated
      - Alert index generated
      - Quality report generated
      - All schema validation tests pass
      - All plausibility tests pass
      - All consistency tests pass
    pass_criteria: All sub-validations pass
    estimated_duration: 30-45 minutes

  - id: E2E-PIP-002
    name: Full pipeline with live data (smoke test)
    description: >
      Run the pipeline against live data sources for a small subset
      (5 countries) to verify real-world data flow works
    setup:
      - Configure for 5 countries only: USA, CHN, DEU, JPN, BRA
      - Use live APIs
    execution:
      - Run all 18 agents
    validation:
      - All agents complete (some data collection failures acceptable)
      - At least 80% of expected data points collected
      - Output passes schema validation
      - Trend estimates generated
      - No pipeline-breaking errors
    pass_criteria: Pipeline completes, data quality > 70%
    estimated_duration: 1-2 hours
    frequency: Monthly (not every run)

  - id: E2E-PIP-003
    name: Recovery test — agent failure mid-pipeline
    description: >
      Simulate a failure at Agent 7 (Processor) and verify
      recovery by re-running from Agent 7
    setup:
      - Run Agents 1-6 successfully
      - Corrupt the Agent 7 output file
    execution:
      - Detect failure
      - Re-run from Agent 7 onward
    validation:
      - Agent 7 re-processes successfully
      - Downstream agents (8-16) complete normally
      - Final output matches what a clean run would produce
    pass_criteria: Recovery produces identical output to clean run

  - id: E2E-PIP-004
    name: Idempotency test
    description: >
      Running the pipeline twice on the same week with no new data
      should produce identical output
    setup:
      - Run full pipeline once
      - Record output hashes for all files
    execution:
      - Run full pipeline again immediately
    validation:
      - All output files are identical (same hashes)
      - Timeseries does not get duplicate entries
      - No spurious alerts generated
    pass_criteria: Byte-identical output (excluding timestamps in metadata)
```

### 4.2 UI Data Contract Tests

```yaml
TEST_GROUP: End-to-End UI Data Contract
TEST_ID_PREFIX: E2E-UI

tests:

  - id: E2E-UI-001
    name: Summary chunk loadable and renderable
    description: >
      The all_countries_summary.json chunk contains everything
      needed to render the initial map view
    validation:
      - File exists and is valid JSON
      - Size < 1MB (target < 500KB)
      - Contains entry for every tracked country
      - Each entry has: code, name, region, latitude, longitude,
        gdp_trend, risk_score, alert_count
      - latitude in [-90, 90], longitude in [-180, 180]
      - All required color-metric fields present

  - id: E2E-UI-002
    name: Country detail chunks loadable
    description: >
      Each country detail file contains everything needed
      for the country detail panel
    validation:
      - Each Tier 1-2 country has a detail chunk
      - Each file has: all 6 layers, narrative section, active alerts
      - File sizes are reasonable (< 200KB each)
      - Narrative section has generated_at within last 7 days

  - id: E2E-UI-003
    name: Relation chunks loadable
    description: >
      Relation files contain everything needed for the relation explorer
    validation:
      - relation_index.json exists and has composite scores for all pairs
      - Each detail relation file has all 7 sub-dimensions + composite
      - Relation files are < 50KB each

  - id: E2E-UI-004
    name: Global data chunks loadable
    description: >
      Weekly briefing, alerts, rankings, events all load correctly
    validation:
      - weekly_briefing_{date}.json exists and has current week's date
      - alert_index.json exists
      - global_rankings.json exists with at least 5 ranking categories
      - event_feed.json exists with events from last 4 weeks

  - id: E2E-UI-005
    name: Timeseries chunks support charting
    description: >
      Timeseries files have enough history and correct format for charts
    validation:
      - Each timeseries has >= 8 data points (2 years quarterly)
      - Data points are chronologically ordered
      - Values are numeric
      - Timestamps parse correctly
```

---

## 5. Regression Tests

### 5.1 Weekly Regression Checks

```yaml
TEST_GROUP: Regression
TEST_ID_PREFIX: REG

tests:

  - id: REG-001
    name: No country data lost
    description: >
      After a weekly run, no country that had data before
      should have less data than before (unless explicitly removed)
    validation:
      - For each country file:
        Count of non-null factors this week >= count last week - 5
        (allowing for minor data availability fluctuations)
      - If any country loses > 10 factors: FAIL

  - id: REG-002
    name: No relation data lost
    validation:
      - Number of relation files >= last week's count
      - No relation file has significantly fewer populated fields

  - id: REG-003
    name: Timeseries only grows
    validation:
      - Each timeseries file has >= entries as last week
      - No historical data points were deleted or modified

  - id: REG-004
    name: Trend estimate consistency
    description: >
      Trend estimates should not wildly oscillate week to week
      without a clear reason
    validation:
      - For each trend that changed by 2+ levels (e.g., growth → strong_decrease):
        Verify there is a supporting event with severity >= "major"
      - Flag unjustified wild swings

  - id: REG-005
    name: Alert lifecycle continuity
    validation:
      - Ongoing alerts from last week still exist (as ongoing, escalated, deescalated, or resolved)
      - No alert disappeared without being resolved
      - New alerts have status = "new"

  - id: REG-006
    name: Coverage does not regress
    validation:
      - Overall factor coverage % >= last week's - 2%
      - No Tier 1 country drops below 80% coverage
      - No Tier 2 country drops below 60% coverage
```

---

## 6. Performance Tests

```yaml
TEST_GROUP: Performance
TEST_ID_PREFIX: PERF

tests:

  - id: PERF-001
    name: Page load performance
    description: Measure initial page load time
    method: >
      Use browser dev tools or Lighthouse to measure:
      - Time to first contentful paint
      - Time to interactive (map renders)
    target:
      - First contentful paint: < 2 seconds
      - Time to interactive: < 5 seconds
      - Total transfer size (initial load): < 2MB
    frequency: After each UI code change

  - id: PERF-002
    name: Country detail load performance
    method: Measure time from click to panel fully rendered
    target: < 2 seconds
    frequency: After each UI code change

  - id: PERF-003
    name: Data file sizes within limits
    validation:
      - manifest.json: < 10KB
      - all_countries_summary.json: < 1MB
      - Individual country files: < 200KB each
      - Individual relation files: < 50KB each
      - weekly_briefing: < 50KB
      - Total /data directory: < 150MB
    frequency: Every pipeline run

  - id: PERF-004
    name: Pipeline execution time
    validation:
      - Total pipeline duration: < 6 hours
      - No single agent takes > 90 minutes
      - Log duration per agent for trend tracking
    frequency: Every pipeline run

  - id: PERF-005
    name: Browser memory usage
    method: Open site, load 10 country details, check memory
    target: < 500MB browser tab memory
    frequency: Monthly
```

---

## 7. Data Quality Validation Tests (Run Weekly)

These tests run as part of Agent 15 (Quality Reporter) but are documented here as test specifications:

```yaml
TEST_GROUP: Data Quality
TEST_ID_PREFIX: DQ

tests:

  - id: DQ-001
    name: Tier 1 coverage check
    validation:
      - Each of 30 Tier 1 countries: >= 90% factors non-null
      - Report per-country coverage percentage
    action_on_fail: Flag in quality report, investigate data source issues

  - id: DQ-002
    name: Tier 2 coverage check
    validation:
      - Each of 25 Tier 2 countries: >= 70% factors non-null
    action_on_fail: Flag in quality report

  - id: DQ-003
    name: Staleness check
    validation:
      - No financial data > 7 days old
      - No macroeconomic data > 120 days old
      - No political event data > 7 days old
      - No military data > 120 days old
    action_on_fail: List stale factors in quality report

  - id: DQ-004
    name: Confidence distribution check
    validation:
      - Average confidence across all factors > 0.6
      - No more than 5% of factors with confidence < 0.3
      - No Tier 1 country has average confidence < 0.5
    action_on_fail: Identify low-confidence areas, investigate sources

  - id: DQ-005
    name: Source diversity check
    validation:
      - No single source provides > 40% of all data points
      - Each major data category has >= 2 sources
    action_on_fail: Recommend additional sources in quality report

  - id: DQ-006
    name: Trend estimate quality check
    validation:
      - All Tier 1-2 countries have trend estimates
      - Average confidence of trend estimates > 0.5
      - No trend estimate has empty reasoning
      - No trend estimate has zero supporting evidence
    action_on_fail: Flag low-quality estimates for manual review

  - id: DQ-007
    name: Backtest trend accuracy (quarterly)
    description: >
      Every quarter, compare trend predictions from 3 months ago
      against actual outcomes
    validation:
      - Compute directional accuracy (predicted direction matches actual)
      - Target: > 60% directional accuracy
      - Report accuracy by factor type and by country tier
    action_on_fail: >
      If accuracy < 50%, investigate methodology.
      Publish accuracy metrics on the site for transparency.
    frequency: Quarterly
```

---

## 8. Test Execution Schedule

| Test Group | When | Duration | How |
|---|---|---|---|
| Schema Validation (UT-SCH) | Every pipeline run | 2 min | Automated script |
| Plausibility (UT-PLB) | Every pipeline run | 2 min | Automated script |
| Agent Output (UT-AGT) | After each agent | 1 min each | Automated check |
| Pipeline Flow (IT-FLW) | Every pipeline run | 5 min | Automated script |
| Data Consistency (IT-CON) | Every pipeline run | 5 min | Automated script |
| Regression (REG) | Every pipeline run | 3 min | Automated diff |
| Data Quality (DQ) | Every pipeline run | 5 min | Agent 15 |
| Performance (PERF-003, 004) | Every pipeline run | 1 min | Automated check |
| E2E Seed Data (E2E-PIP-001) | Before first production run, after major changes | 45 min | Manual trigger |
| E2E Live Smoke (E2E-PIP-002) | Monthly | 2 hours | Manual trigger |
| E2E Recovery (E2E-PIP-003) | After major changes | 1 hour | Manual trigger |
| E2E Idempotency (E2E-PIP-004) | After major changes | 4 hours | Manual trigger |
| UI Data Contract (E2E-UI) | Every pipeline run | 2 min | Automated script |
| UI Performance (PERF-001, 002, 005) | After UI code changes | 10 min | Manual Lighthouse |
| Trend Backtest (DQ-007) | Quarterly | 30 min | Manual trigger |

**Total automated testing per weekly run: ~25 minutes** (runs as part of Agent 15 and post-pipeline validation)

---

## 9. Test Implementation

### 9.1 Validation Script Structure

All automated tests are implemented as Python scripts that Claude Code runs:

```python
# /tests/scripts/test_schema_validation.py
# Claude Code executes this after the pipeline completes

import json
import os
import sys
from pathlib import Path

class TestResult:
    def __init__(self, test_id, name):
        self.test_id = test_id
        self.name = name
        self.passed = True
        self.errors = []
        self.warnings = []

    def fail(self, message):
        self.passed = False
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "name": self.name,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings
        }

def run_all_tests(data_dir, staging_dir):
    results = []

    # UT-SCH-001: Country schema validation
    results.append(test_country_schemas(data_dir))

    # UT-SCH-002: Relation schema validation
    results.append(test_relation_schemas(data_dir))

    # UT-PLB-001: GDP plausibility
    results.append(test_gdp_plausibility(data_dir))

    # ... (all other tests)

    # Generate report
    report = {
        "run_date": datetime.utcnow().isoformat(),
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "results": [r.to_dict() for r in results]
    }

    return report
```

### 9.2 Running Tests

**Data validation tests (pytest):**
```bash
python3 -m pytest tests/scripts/ -v --tb=short

# Or use the master test runner (outputs JSON report):
python3 tests/scripts/run_all_tests.py --verbose \
  --output tests/reports/test_report_{date}.json
```

Tests run as part of Agent 15 and must all pass before Agent 16 commits.

**E2E browser tests (Playwright):**
```bash
# Install dependencies (first time)
npm install && npx playwright install chromium

# Run headless
npm test

# Run with visible browser
npm run test:headed

# View HTML report
npm run test:report
```

Playwright auto-starts a local server on port 8089 (see `playwright.config.ts`)
and runs tests against Chromium at `http://localhost:8089/web/`.

---

## 10. Playwright E2E Browser Tests

**Purpose:** Verify the web UI works correctly end-to-end in a real browser.

**Configuration:** `playwright.config.ts` in project root.
- Server: `python3 -m http.server 8089` (auto-started)
- Browser: Chromium, viewport 1280x720
- Timeout: 30s per test
- Workers: 4 local, 1 in CI

```yaml
TEST_GROUP: Playwright E2E
TEST_ID_PREFIX: PW

tests:

  - id: PW-001
    name: App initialization
    file: tests/e2e/app-init.spec.ts
    validation:
      - Map container renders
      - Country summary data loads
      - At least 70 countries appear on map

  - id: PW-002
    name: Map interactions
    file: tests/e2e/map-interactions.spec.ts
    validation:
      - Click country opens detail panel
      - Pan and zoom work
      - Tooltip appears on hover

  - id: PW-003
    name: Country detail panel
    file: tests/e2e/country-panel.spec.ts
    validation:
      - Panel shows country name and data
      - Layer tabs switch content
      - Close button works

  - id: PW-004
    name: Briefing view
    file: tests/e2e/briefing-view.spec.ts
    validation:
      - Story cards render from article index
      - Click card navigates to article detail
      - SVG illustration renders safely

  - id: PW-005
    name: Alert dashboard
    file: tests/e2e/alert-dashboard.spec.ts
    validation:
      - Alert severity color-by mode works
      - Alert list populates

  - id: PW-006
    name: Search
    file: tests/e2e/search.spec.ts
    validation:
      - Search input accepts text
      - Autocomplete dropdown appears
      - Selecting result navigates to country

  - id: PW-007
    name: Data integrity
    file: tests/e2e/data-integrity.spec.ts
    validation:
      - Fetched JSON parses correctly
      - Key fields are present and non-null
```

---

## 11. Pre-Fetch Integration Tests

**Purpose:** Verify the deterministic pre-fetch data pipeline works correctly.

```yaml
TEST_GROUP: Pre-Fetch
TEST_ID_PREFIX: PF

tests:

  - id: PF-UNIT
    name: Pre-fetch unit tests
    file: tests/scripts/test_prefetch.py
    validation:
      - Each fetcher class instantiates correctly
      - Output format matches expected schema
      - Rate limiting and retry logic works
      - Error handling for API failures

  - id: PF-INTEGRATION
    name: Pre-fetch integration tests
    file: tests/scripts/test_prefetch_integration.py
    validation:
      - World Bank returns valid indicator data
      - IMF returns WEO forecasts
      - GDELT returns event data
      - FX/commodities returns exchange rates
      - Output files written to staging/prefetched/
      - JSON output is valid and non-empty
```

**Run:** `python3 -m pytest tests/scripts/test_prefetch*.py -v`

---

## 12. Defect Severity Classification

| Severity | Definition | Response |
|---|---|---|
| **S1 - Critical** | Data corruption, completely wrong values displayed, pipeline cannot complete | Fix immediately before next publication |
| **S2 - Major** | Significant data gaps, wrong trends for Tier 1 country, broken UI feature | Fix within 1 weekly cycle |
| **S3 - Minor** | Small data inaccuracies, Tier 3 country issues, UI cosmetic issues | Fix within 2-4 weekly cycles |
| **S4 - Trivial** | Documentation typos, minor display formatting, edge case data gaps | Fix when convenient |
