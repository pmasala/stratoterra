# Geopolitical Intelligence Model — Web UI Specification

**Version:** 1.1
**Date:** 2026-03-14
**Status:** Active
**Depends on:** `01_FACTOR_MODEL_SPEC.md`, `03_REQUIREMENTS.md`

---

## 1. Architecture

### 1.1 Technology Stack

```
Frontend:
  - HTML5 + CSS3 + Vanilla JavaScript (IIFEs, no framework, no build step)
  - Map rendering: Leaflet.js (https://leafletjs.com) + GeoJSON (CDN)
  - Network graphs: D3.js force-directed layout (CDN)
  - Charts: Inline SVG/Canvas
  - Responsive layout: CSS Grid + Flexbox (768px mobile breakpoint)
  - Routing: Hash-based (#view or #view/sub/path?params) via app.js

Hosting:
  - GitHub Pages (static files only)
  - Deployed from main branch via .github/workflows/static.yml
  - No build step — pure static site
  - Live URL: https://pmasala.github.io/stratoterra/web/

Data:
  - Pre-computed JSON files served as static assets from /data/chunks/
  - DataLoader IIFE caches all fetches, loads on demand
  - No backend, no API calls at runtime (except loading JSON)
```

### 1.2 File Structure

```
/web
├── index.html                    # Single page application entry
├── /css
│   ├── main.css                 # Global styles + design tokens (:root custom properties)
│   ├── panels.css               # Panel layouts
│   ├── responsive.css           # Media queries (768px breakpoint)
│   └── overlays.css             # Intel overlay styling
├── /js
│   ├── app.js                   # Main router (hash-based routing)
│   ├── data-loader.js           # IIFE: DataLoader for fetching/caching chunks
│   ├── map-view.js              # Leaflet.js map rendering
│   ├── country-panel.js         # Country detail panel
│   ├── relation-explorer.js     # D3.js bilateral relation explorer
│   ├── briefing-view.js         # Stories listing & article detail view
│   ├── alert-dashboard.js       # Alert severity mode
│   ├── comparison-tool.js       # Country comparison view
│   ├── rankings-view.js         # Global rankings tables
│   ├── charts.js                # Chart rendering
│   ├── search.js                # Search autocomplete dropdown
│   ├── overlays.js              # Intel overlay management
│   ├── utils.js                 # Sanitization, fetch wrappers
│   └── constants.js             # Color scales, enum labels, config
└── /assets                      # Static assets (icons, images)
```

---

## 2. Page Layout

### 2.1 Main Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER BAR                                                     │
│ [Logo] Geopolitical Intelligence Model    [Search] [Menu ≡]   │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│                                                                │
│                     MAIN CONTENT AREA                          │
│                                                                │
│              (Map / Briefing / Rankings / etc.)                │
│                                                                │
│                                                                │
│                                                                │
├──────────────────────────────────────────────────────────────┤
│ BOTTOM BAR                                                     │
│ [Metric Selector ▾] [Overlay: None ▾]  Last updated: Mar 1   │
│ Color legend: ████ Strong Growth → ████ Strong Decrease        │
└──────────────────────────────────────────────────────────────┘
```

When a country is selected:

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER BAR                                                     │
├────────────────────────────────┬─────────────────────────────┤
│                                │                               │
│                                │    COUNTRY DETAIL PANEL      │
│        MAP VIEW                │    (scrollable)              │
│        (shrinks to ~60%)       │                               │
│                                │    ┌─────────────────────┐   │
│                                │    │ Executive Summary    │   │
│                                │    ├─────────────────────┤   │
│                                │    │ Key Changes         │   │
│                                │    ├─────────────────────┤   │
│                                │    │ Layer Tabs:         │   │
│                                │    │ [Endow][Inst][Econ] │   │
│                                │    │ [Mil][Rel][Derived] │   │
│                                │    ├─────────────────────┤   │
│                                │    │ Factor Details      │   │
│                                │    │ (expandable cards)  │   │
│                                │    └─────────────────────┘   │
│                                │                               │
├────────────────────────────────┴─────────────────────────────┤
│ BOTTOM BAR                                                     │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation Structure

```
Primary Navigation (Top menu / sidebar):
├── 🌍 Map View (default)
├── 📋 Weekly Briefing
├── ⚠️ Alerts ({count})
├── 📊 Rankings
├── 🔗 Relations
├── ⚖️ Compare
└── ℹ️ About / Methodology

Secondary Navigation (within views):
- Map View: metric selector, overlay selector
- Country Panel: layer tabs
- Rankings: metric selector, region filter
- Relations: country pair selector, dimension filter
```

---

## 3. View Specifications

### 3.1 Map View (Landing Page)

**Purpose:** Primary entry point. Visual overview of the world with country-level data displayed as a choropleth map.

**Map Configuration:**
```javascript
// Using Leaflet.js with GeoJSON country boundaries

const map = L.map('map-container', {
  center: [20, 0],                         // Centered slightly north (more land visible)
  zoom: 2,                                  // World view
  minZoom: 2,                               // Prevent zooming out too far
  maxZoom: 8,                               // Country-level detail
  zoomControl: true,
  worldCopyJump: true,                      // Seamless horizontal wrapping
  maxBoundsViscosity: 1.0
});

// Base layer: minimal tile layer for ocean/context (or pure CSS background)
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
  attribution: '© CartoDB',
  maxZoom: 19
}).addTo(map);

// GeoJSON country layer with data-driven styling
const countryLayer = L.geoJSON(countriesGeoJSON, {
  style: feature => ({
    fillColor: colorScale(feature.properties.metricValue),
    fillOpacity: 0.75,
    weight: 1,
    color: '#444488',                       // Border color
    opacity: 0.6
  }),
  onEachFeature: (feature, layer) => {
    layer.on({
      mouseover: e => highlightCountry(e),
      mouseout: e => resetHighlight(e),
      click: e => openCountryPanel(feature.properties.code)
    });
    layer.bindTooltip(tooltipHTML(feature.properties), {
      sticky: true,
      className: 'country-tooltip'
    });
  }
}).addTo(map);
```

**Map Projection:**
- Default: Web Mercator (standard for Leaflet, familiar to users)
- Optional future enhancement: switch to Natural Earth or Robinson projection via D3.js for more accurate area representation (important when coloring by GDP or population)

**Metric Selector (Bottom Bar):**
Dropdown or segmented control to choose which metric colors the map:

| Metric | Color Scale | Description |
|---|---|---|
| GDP Growth Trend | Green → Red | Current quarterly trend |
| Political Stability | Blue → Red | WGI political stability |
| Military Spending Trend | Neutral → Red | Spending trajectory |
| Investment Risk | Green → Red | Composite risk score |
| Alert Severity | Green → Yellow → Red | Highest active alert |
| Economic Complexity | Blue gradient | Harvard ECI |
| Energy Independence | Green → Red | Self-sufficiency |
| Trade Openness | Light → Dark | Trade/GDP ratio |

**Overlay Selector:**
Toggle to highlight supranational entities:
- None (default)
- EU member states
- NATO member states
- BRICS members
- ASEAN members
- OPEC members
- G7 / G20

When overlay active: member countries get a thicker border or pattern overlay; non-members dim to 30% opacity. Overlay legend appears.

**Tooltip (on hover):**
```html
<div class="tooltip">
  <div class="tooltip-header">
    <span class="flag">🇺🇸</span>
    <strong>United States</strong>
    <span class="alert-badge critical">⚠ 1</span>
  </div>
  <div class="tooltip-metric">
    GDP Growth: <span class="trend growth">↑ 2.3%</span>
  </div>
  <div class="tooltip-metric">
    Risk Score: <span class="value">0.25</span> (Low)
  </div>
  <div class="tooltip-hint">Click for details</div>
</div>
```

**Map Interactions:**
- Scroll wheel: zoom in/out
- Click and drag: pan
- Click country: open detail panel, zoom to fit country bounds
- Double-click: zoom in to point
- Escape / click outside country: close panel, reset zoom
- Keyboard: arrow keys to pan, +/- to zoom

**Region Quick-Zoom Buttons (optional sidebar):**
Small buttons to jump to predefined views:
- 🌍 World
- 🌎 Americas
- 🌍 Europe
- 🌍 Africa & Middle East
- 🌏 Asia-Pacific

**Visual Enhancements:**
- Disputed borders shown as dashed lines
- Chokepoints marked with small icons (Suez, Hormuz, Malacca, Panama, etc.)
- Active conflict zones can show a subtle pulsing overlay
- Country labels appear at zoom level ≥ 4

### 3.2 Country Detail Panel

**Purpose:** Deep-dive into a single country's factor profile.

**Layout:**

```
┌─────────────────────────────────────┐
│ ← Back          🇺🇸 United States    │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ EXECUTIVE SUMMARY                │ │
│ │ The US economy continues to      │ │
│ │ show resilience with 2.3% GDP    │ │
│ │ growth...                        │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ KEY CHANGES THIS WEEK            │ │
│ │ • Fed held rates steady at 5.25% │ │
│ │ • New tariffs on Chinese EVs     │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ ACTIVE ALERTS                    │ │
│ │ ⚠ WARNING: Trade tensions with   │ │
│ │   China escalating               │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [Endow] [Inst] [Econ] [Mil]     │ │
│ │ [Relations] [Derived]            │ │
│ │                                  │ │
│ │ Currently showing: ECONOMY       │ │
│ │                                  │ │
│ │ GDP (nominal)    $28.5T   ↑     │ │
│ │ ████████████░░  confidence 0.93  │ │
│ │ [sparkline chart ~~~/\~~]        │ │
│ │                                  │ │
│ │ GDP Growth       2.3%    ↗      │ │
│ │ ████████████░░  confidence 0.88  │ │
│ │ Trend: growth (0.72 conf)       │ │
│ │ "Supported by consumer spending  │ │
│ │  and labor market resilience..." │ │
│ │                                  │ │
│ │ Inflation        3.1%    ↘      │ │
│ │ ...                              │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ OUTLOOK                          │ │
│ │ The US is expected to maintain   │ │
│ │ moderate growth...               │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ INVESTOR IMPLICATIONS            │ │
│ │ Dollar strength supports...      │ │
│ └──────────────────────────────────┘ │
│                                      │
│ Data sources: World Bank, IMF, ...   │
│ Last updated: 2026-03-01             │
└─────────────────────────────────────┘
```

**Factor Card Component:**

Each factor is displayed as a card:
```
┌──────────────────────────────────────┐
│ GDP Real Growth Rate           ↗     │
│ 2.3%                                 │
│ Trend: growth    Confidence: ██████░ │
│ [▁▂▃▃▄▅▆▅▅▆] (sparkline)            │
│                                      │
│ ▸ Show reasoning                     │
│ ▸ Show sources                       │
└──────────────────────────────────────┘
```

Clicking "Show reasoning" expands:
```
│ AI Trend Assessment (2026-Q1):       │
│ "Supported by consumer spending and  │
│  labor market resilience, though     │
│  manufacturing shows weakness..."     │
│                                      │
│ Supporting evidence:                 │
│ • Fed GDP forecast: 2.1% for 2026   │
│ • Unemployment at 3.8% (Feb 2026)   │
│ • ISM Manufacturing: 49.2 (contract) │
│                                      │
│ Counter-arguments:                   │
│ • Consumer savings rate declining    │
│ • Fiscal deficit widening            │
│                                      │
│ Source: World Bank API (2025-12-31)  │
│ Confidence: 0.88                     │
```

**Layer Tabs Content:**

| Tab | Contents |
|---|---|
| Endowments | Natural resources (top 10 by value), geography summary, climate, demographics |
| Institutions | Regime type, governance scores, cultural dimensions, current political dynamics |
| Economy | All macroeconomic factors, financial system, labor market |
| Military | Personnel, capabilities summary, nuclear status, active conflicts, alliances |
| Relations | Top 10 bilateral partners (by trade volume), with mini-scores. Click any for full relation view. |
| Derived | Composite scores, vulnerability indices, investor metrics, trend estimates summary |

### 3.3 Weekly Briefing View

**Purpose:** Narrative overview of the week's most important developments.

```
┌──────────────────────────────────────────────┐
│ 📋 WEEKLY BRIEFING                            │
│ Week of February 22 – March 1, 2026          │
│                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                               │
│ HEADLINE                                      │
│ "Trade tensions dominate as US and China       │
│  exchange tariff threats; European growth      │
│  stabilizes"                                   │
│                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                               │
│ TOP STORIES                                   │
│                                               │
│ 1. [🔴 MAJOR] US-China Trade Escalation       │
│    Summary text... 3-4 sentences              │
│    Countries: 🇺🇸 USA, 🇨🇳 China              │
│    [View USA →] [View China →]                │
│                                               │
│ 2. [🟡 MODERATE] ECB Signals Rate Hold        │
│    ...                                        │
│                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                               │
│ REGIONAL ROUNDUP                              │
│                                               │
│ [N.America] [Europe] [E.Asia] [S.Asia]       │
│ [MENA] [SubSaharan] [LatAm] [CentralAsia]   │
│ [SE.Asia] [Oceania]                           │
│                                               │
│ Currently showing: East Asia                  │
│ "Japan's Q4 GDP surprised to the downside..." │
│                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                               │
│ MARKET CONTEXT                                │
│ Oil: $82.50 (+2.3%)  Gold: $2,150 (-0.5%)   │
│ EUR/USD: 1.085 (-0.3%)  10Y UST: 4.25%      │
│                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                               │
│ Data updated: 2026-03-01 | Coverage: 92%     │
│ AI-generated content. Not financial advice.   │
└──────────────────────────────────────────────┘
```

### 3.4 Alert Dashboard

```
┌──────────────────────────────────────────────┐
│ ⚠️ ACTIVE ALERTS                              │
│                                               │
│ Filter: [All ▾] [Region ▾] [Type ▾]         │
│                                               │
│ 🔴 CRITICAL (2)                               │
│ ┌──────────────────────────────────────────┐ │
│ │ Ukraine conflict escalation               │ │
│ │ Countries: UKR, RUS                       │ │
│ │ Status: ONGOING since 2022-02-24         │ │
│ │ Investor action: Review E.Europe exposure │ │
│ │ [View Details →]                          │ │
│ └──────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────┐ │
│ │ Argentina sovereign default risk          │ │
│ │ ...                                       │ │
│ └──────────────────────────────────────────┘ │
│                                               │
│ 🟡 WARNING (7)                                │
│ ...                                           │
│                                               │
│ 🔵 WATCH (15)                                 │
│ ...                                           │
│                                               │
│ Alert trend: 24 active (▲ 3 from last week)  │
└──────────────────────────────────────────────┘
```

### 3.5 Relation Explorer

**Two modes:**

**Mode A: Country Relationship Web**
Select one country → see its connections as a force-directed graph.

```
                    CAN
                   / (trade)
              GBR --- USA --- CHN
               |    / | \     |
              FRA  /  |  \   JPN
               |  /   |   \   |
              DEU  MEX  KOR  TWN
               |
              ITA

Edge thickness = trade volume
Edge color = relationship quality (green=allied, yellow=neutral, red=hostile)
Click any edge for bilateral detail
```

**Mode B: Bilateral Deep-Dive**
Select two countries → see full bilateral relationship card.

```
┌──────────────────────────────────────────────┐
│ 🇺🇸 United States  ↔  🇨🇳 China               │
│ Overall: TENSE (deteriorating)               │
│                                               │
│ TRADE                                        │
│ Bilateral volume: $690B                      │
│ US exports to CN: $150B  CN exports to US: $540B│
│ Trade disputes: 3 active                     │
│ Tariff avg US→CN: 18%  CN→US: 12%           │
│ Trend: ↘ decrease                            │
│ [View trade details →]                       │
│                                               │
│ DIPLOMATIC                                   │
│ Status: tense                                │
│ UN voting alignment: 0.15                    │
│ Recent incidents: 2 this quarter             │
│                                               │
│ MILITARY                                     │
│ Alliance: adversarial                        │
│ Incidents: South China Sea patrols           │
│                                               │
│ FINANCIAL                                    │
│ CN holds $800B US treasuries                 │
│ FDI flows declining                          │
│                                               │
│ ENERGY                                       │
│ Minimal direct energy trade                  │
│                                               │
│ COMPOSITE SCORES                             │
│ Cooperation: 0.35  Tension: 0.72            │
│ Interdependence: 0.65  Power asymmetry: -0.3│
└──────────────────────────────────────────────┘
```

### 3.6 Comparison Tool

```
┌──────────────────────────────────────────────┐
│ ⚖️ COMPARE COUNTRIES                          │
│                                               │
│ Selected: [USA ×] [CHN ×] [IND ×] [+ Add]   │
│                                               │
│ View: [Table] [Radar Chart]                  │
│                                               │
│ RADAR CHART MODE:                            │
│                                               │
│           Economic Power                      │
│               ╱╲                              │
│    Military ╱    ╲ Technology                 │
│            │  ╱╲  │                           │
│            │╱    ╲│                           │
│    Stability └────┘ Openness                  │
│                                               │
│   ── USA  -- CHN  ·· IND                     │
│                                               │
│ TABLE MODE:                                  │
│ Metric          │ USA    │ CHN    │ IND      │
│ GDP ($T)        │ 28.5   │ 18.2   │ 4.1      │
│ GDP Growth %    │ 2.3 ↗  │ 4.5 ↘  │ 6.8 →   │
│ Pop (M)         │ 335    │ 1,412  │ 1,440    │
│ Military ($B)   │ 886    │ 292    │ 83       │
│ Risk Score      │ 0.25   │ 0.45   │ 0.40     │
│ ...             │ ...    │ ...    │ ...      │
└──────────────────────────────────────────────┘
```

### 3.7 Rankings View

```
┌──────────────────────────────────────────────┐
│ 📊 GLOBAL RANKINGS                            │
│                                               │
│ Metric: [GDP Nominal ▾]  Region: [All ▾]    │
│                                               │
│ #  │ Country          │ Value    │ Trend     │
│ 1  │ 🇺🇸 United States │ $28.5T  │ ↗ growth  │
│ 2  │ 🇨🇳 China          │ $18.2T  │ ↘ slower  │
│ 3  │ 🇯🇵 Japan          │ $4.2T   │ → stable  │
│ 4  │ 🇩🇪 Germany        │ $4.1T   │ → stable  │
│ 5  │ 🇮🇳 India          │ $4.0T   │ ↗ growth  │
│ ...                                          │
│                                               │
│ Available metrics:                           │
│ Economic: GDP, GDP/capita, GDP growth,       │
│   inflation, debt/GDP, trade volume          │
│ Power: Military spending, composite power,   │
│   nuclear capability                         │
│ Risk: Political stability, investment risk,  │
│   corruption, sanctions exposure             │
│ Development: HDI, ECI, innovation index      │
└──────────────────────────────────────────────┘
```

---

## 4. Design System

### 4.1 Color Palette

```css
:root {
  /* Background */
  --bg-primary: #0a0a1a;        /* Deep navy/black */
  --bg-secondary: #12122a;      /* Slightly lighter */
  --bg-panel: #1a1a3a;          /* Panel background */
  --bg-card: #222250;           /* Card background */

  /* Text */
  --text-primary: #e8e8f0;      /* Main text */
  --text-secondary: #9898b8;    /* Muted text */
  --text-accent: #6ca6ff;       /* Links, highlights */

  /* Trend colors */
  --trend-strong-growth: #00c853;
  --trend-growth: #69f0ae;
  --trend-stable: #ffd54f;
  --trend-decrease: #ff8a65;
  --trend-strong-decrease: #ff1744;

  /* Alert colors */
  --alert-critical: #ff1744;
  --alert-warning: #ffab40;
  --alert-watch: #448aff;

  /* Confidence */
  --confidence-high: #00c853;
  --confidence-medium: #ffd54f;
  --confidence-low: #ff8a65;

  /* Relationship quality */
  --relation-allied: #00c853;
  --relation-friendly: #69f0ae;
  --relation-neutral: #9898b8;
  --relation-cool: #ff8a65;
  --relation-hostile: #ff1744;

  /* Map-specific */
  --map-ocean: #0a0a2a;
  --map-land-default: #2a2a5a;
  --map-border: #444488;
  --map-highlight: #6ca6ff;
  --map-highlight-border: #88bbff;
  --map-dimmed: rgba(42, 42, 90, 0.3);     /* For non-overlay countries */
}
```

### 4.2 Typography

```css
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
}

h1 { font-size: 24px; font-weight: 700; }
h2 { font-size: 20px; font-weight: 600; }
h3 { font-size: 16px; font-weight: 600; }

.data-value { font-family: 'JetBrains Mono', monospace; font-size: 18px; }
.trend-label { font-size: 12px; font-weight: 500; text-transform: uppercase; }
.confidence-bar { height: 4px; border-radius: 2px; }
```

### 4.3 Component Patterns

**Trend Indicator:**
```html
<span class="trend trend--growth">
  <span class="trend-arrow">↗</span>
  <span class="trend-label">Growth</span>
</span>
```

**Confidence Bar:**
```html
<div class="confidence-bar">
  <div class="confidence-fill" style="width: 88%"
       data-level="high"></div>
</div>
<span class="confidence-value">0.88</span>
```

**Alert Badge:**
```html
<span class="alert-badge alert-badge--critical">⚠ 2</span>
<span class="alert-badge alert-badge--warning">● 5</span>
```

**Sparkline:**
Rendered with Canvas or SVG inline. 100px wide, 30px tall.
Shows last 8 data points as a mini line chart.

---

## 5. Data Loading Strategy

### 5.1 Data Loader Module

```javascript
// /js/data-loader.js

class DataLoader {
  constructor(baseUrl = './data/chunks') {
    this.baseUrl = baseUrl;
    this.cache = new Map();
    this.manifest = null;
  }

  async init() {
    // Load manifest first
    this.manifest = await this.fetchJSON('manifest.json');
    // Load country summary (needed for map)
    const summary = await this.fetchJSON('country-summary/all_countries_summary.json');
    this.cache.set('summary', summary);
    return summary;
  }

  async getCountryDetail(code) {
    const key = `country:${code}`;
    if (this.cache.has(key)) return this.cache.get(key);
    const data = await this.fetchJSON(`country-detail/${code}.json`);
    this.cache.set(key, data);
    return data;
  }

  async getRelation(codeA, codeB) {
    // Ensure canonical ordering
    const [a, b] = [codeA, codeB].sort();
    const key = `relation:${a}_${b}`;
    if (this.cache.has(key)) return this.cache.get(key);
    const data = await this.fetchJSON(`relations/${a}_${b}.json`);
    this.cache.set(key, data);
    return data;
  }

  async getTimeseries(code, category) {
    const key = `ts:${code}_${category}`;
    if (this.cache.has(key)) return this.cache.get(key);
    const data = await this.fetchJSON(`timeseries/${code}_${category}.json`);
    this.cache.set(key, data);
    return data;
  }

  async getBriefing() {
    return this.fetchJSON('global/weekly_briefing.json');
  }

  async getAlerts() {
    return this.fetchJSON('global/alert_index.json');
  }

  async getRankings() {
    return this.fetchJSON('global/global_rankings.json');
  }

  async fetchJSON(path) {
    const url = `${this.baseUrl}/${path}`;
    const response = await fetch(url);
    if (!response.ok) {
      console.error(`Failed to load: ${url}`);
      return null;
    }
    return response.json();
  }
}
```

### 5.2 Loading States

Every view that loads data shows:

```
LOADING STATE:
┌────────────────────┐
│   ◌ Loading...     │
│   Skeleton UI      │
│   (pulsing grey    │
│    placeholder     │
│    blocks)         │
└────────────────────┘

ERROR STATE:
┌────────────────────┐
│   ⚠ Data not       │
│   available        │
│                    │
│   Last updated:    │
│   {date}           │
│                    │
│   [Retry]          │
└────────────────────┘
```

---

## 6. Responsive Behavior

### 6.1 Desktop (≥1280px)
- Full map view with side panel
- All features available
- Optimal experience

### 6.2 Tablet (768px - 1279px)
- Map view with full-screen overlay panel
- Slightly simplified charts
- All features available

### 6.3 Mobile (<768px)
- Simplified map (less detail, larger touch targets)
- Country detail as full-screen view
- Weekly briefing as scrollable article
- Alert list
- Limited comparison (2 countries max)
- Bottom tab navigation instead of sidebar

---

## 7. Accessibility

- All interactive elements keyboard-navigable
- ARIA labels on all controls
- Color is never the only indicator (always paired with text/icon)
- High contrast between text and background (WCAG AA)
- Screen reader compatible data tables
- Focus indicators visible

---

## 8. Disclaimers

Displayed at the bottom of every page:

```
This platform provides AI-generated geopolitical analysis for
informational and educational purposes only. It does not constitute
investment, financial, legal, or tax advice. Data is sourced from
public databases and may be incomplete or delayed. Trend estimates
are AI-generated assessments, not statistical forecasts. Always
consult qualified professionals before making investment decisions.

Data sources: World Bank, IMF, SIPRI, ACLED, and others.
See Methodology page for details.

Last updated: {date} | Data quality: {coverage}% coverage
```

---

## 9. Implementation Phases

### Phase 1 (MVP): COMPLETE
- [x] Map rendering with country coloring by multiple metrics
- [x] Country summary loading and tooltip on hover
- [x] Country detail panel with all 6 layer tabs
- [x] Weekly briefing / stories view with article detail
- [x] Alert dashboard with severity mode
- [x] Search by country name (autocomplete dropdown)
- [x] Responsive: desktop + mobile (768px breakpoint)
- [x] Disclaimer

### Phase 2: COMPLETE
- [x] All 6 layer tabs in country detail
- [x] Rankings view
- [x] Supranational overlays (Conflict Zones enabled by default)
- [x] Comparison tool
- [x] Alert severity as default color-by mode
- [x] SVG article illustrations with DOMParser sanitization

### Phase 3: COMPLETE
- [x] Relation explorer (D3.js network graph)
- [x] Bilateral deep-dive view
- [x] Mobile-friendly layout
- [x] Hash-based routing (#view/sub/path)
- [x] Blinking borders for critical-alert countries

### Phase 4 (Stretch): PLANNED
- [ ] Animated timeline showing data changes over time
- [ ] Custom watchlist with browser localStorage
- [ ] Export data as CSV
- [ ] Timeseries historical charts
