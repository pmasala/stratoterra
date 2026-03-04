/* ==========================================================================
   Stratoterra — Constants & Configuration
   ========================================================================== */

const MAP_CONFIG = {
  center: [20, 0],
  zoom: 2,
  minZoom: 2,
  maxZoom: 8,
  maxBounds: [[-85, -200], [85, 200]],
  maxBoundsViscosity: 0.8,
  tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
  tileAttribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
  labelZoomThreshold: 4,
  geojsonPath: 'assets/geojson/world.geojson'
};

const COUNTRY_STYLE = {
  default: {
    fillColor: '#2a2a5a',
    weight: 1,
    opacity: 0.6,
    color: '#444488',
    fillOpacity: 0.7
  },
  hover: {
    weight: 2,
    color: '#6ca6ff',
    fillOpacity: 0.85
  },
  selected: {
    weight: 2.5,
    color: '#ffffff',
    fillOpacity: 0.9
  },
  dimmed: {
    fillOpacity: 0.15,
    opacity: 0.3
  }
};

// Color scale functions for metrics: value → hex color
// Each takes a normalized value and returns a color string
const COLOR_SCALES = {
  gdp_growth_trend: function(value) {
    // -5 to +10 mapped to red→yellow→green
    const norm = Math.max(0, Math.min(1, (value + 5) / 15));
    return interpolateColor('#ff1744', '#ffd54f', '#00c853', norm);
  },
  political_stability: function(value) {
    // 0 to 1 → red→yellow→green
    const norm = Math.max(0, Math.min(1, value));
    return interpolateColor('#ff1744', '#ffd54f', '#00c853', norm);
  },
  investment_risk: function(value) {
    // 0 (low risk) to 1 (high risk) → green→yellow→red (inverted)
    const norm = Math.max(0, Math.min(1, value));
    return interpolateColor('#00c853', '#ffd54f', '#ff1744', norm);
  },
  military_spending_trend: function(value) {
    // -10 to +15 → blue→yellow→red
    const norm = Math.max(0, Math.min(1, (value + 10) / 25));
    return interpolateColor('#448aff', '#ffd54f', '#ff1744', norm);
  },
  military_spending_pct_gdp: function(value) {
    // 0 to 6% → blue→yellow→red
    const norm = Math.max(0, Math.min(1, value / 6));
    return interpolateColor('#448aff', '#ffd54f', '#ff1744', norm);
  },
  alert_severity: function(value) {
    // 0=none, 1=watch, 2=warning, 3=critical
    if (value <= 0) return '#2a2a5a';
    if (value <= 1) return '#448aff';
    if (value <= 2) return '#ffab40';
    return '#ff1744';
  },
  composite_power: function(value) {
    // 0 to 100 → blue gradient
    const norm = Math.max(0, Math.min(1, value / 100));
    return interpolateColor('#1a1a3a', '#448aff', '#e8e8f0', norm);
  },
  energy_independence: function(value) {
    // 0 to 1 → red→yellow→green
    const norm = Math.max(0, Math.min(1, value));
    return interpolateColor('#ff1744', '#ffd54f', '#00c853', norm);
  },
  trade_openness: function(value) {
    // 0 to 200% → purple gradient
    const norm = Math.max(0, Math.min(1, value / 200));
    return interpolateColor('#1a1a3a', '#9c27b0', '#e8e8f0', norm);
  }
};

// Metric display config
const METRIC_CONFIG = {
  gdp_growth_trend:      { label: 'GDP Growth (%)',        field: 'gdp_real_growth_pct',    format: 'percent1',  legendMin: '-5%', legendMax: '+10%' },
  political_stability:   { label: 'Political Stability',   field: 'political_stability',    format: 'score',     legendMin: '0', legendMax: '1.0' },
  investment_risk:       { label: 'Investment Risk',        field: 'investment_risk_score',  format: 'score',     legendMin: 'Low', legendMax: 'High' },
  military_spending_trend:{ label: 'Military Spend Trend',  field: 'military_spending_trend',format: 'trend',     legendMin: 'Decline', legendMax: 'Growth' },
  military_spending_pct_gdp:{ label: 'Military Spend (% GDP)', field: 'military_expenditure_pct_gdp', format: 'percent1', legendMin: '0%', legendMax: '6%' },
  alert_severity:        { label: 'Alert Severity',         field: 'max_alert_severity',     format: 'severity',  legendMin: 'None', legendMax: 'Critical' },
  composite_power:       { label: 'National Power Index',   field: 'composite_national_power_index', format: 'decimal2', legendMin: '0', legendMax: '100' },
  energy_independence:   { label: 'Energy Independence',    field: 'energy_independence',    format: 'score',     legendMin: '0', legendMax: '1.0' },
  trade_openness:        { label: 'Trade Openness (%)',     field: 'trade_openness_pct',     format: 'percent0',  legendMin: '0%', legendMax: '200%' }
};

const TREND_LABELS = {
  strong_growth:    { label: 'Strong Growth',    arrow: '⬆', cssClass: 'trend--strong-growth' },
  growth:           { label: 'Growth',           arrow: '↗', cssClass: 'trend--growth' },
  stable:           { label: 'Stable',           arrow: '→', cssClass: 'trend--stable' },
  decrease:         { label: 'Decrease',         arrow: '↘', cssClass: 'trend--decrease' },
  strong_decrease:  { label: 'Strong Decrease',  arrow: '⬇', cssClass: 'trend--strong-decrease' }
};

const ALERT_SEVERITY = {
  critical: { label: 'Critical', color: '#ff1744', numericValue: 3 },
  warning:  { label: 'Warning',  color: '#ffab40', numericValue: 2 },
  watch:    { label: 'Watch',    color: '#448aff', numericValue: 1 },
  none:     { label: 'None',     color: '#2a2a5a', numericValue: 0 }
};

const REGIONS = {
  north_america:       { label: 'North America',       color: '#42a5f5' },
  latin_america:       { label: 'Latin America',       color: '#66bb6a' },
  europe:              { label: 'Europe',              color: '#ab47bc' },
  middle_east:         { label: 'Middle East',         color: '#ffa726' },
  sub_saharan_africa:  { label: 'Sub-Saharan Africa',  color: '#ef5350' },
  south_asia:          { label: 'South Asia',          color: '#26c6da' },
  east_asia:           { label: 'East Asia',           color: '#ec407a' },
  southeast_asia:      { label: 'Southeast Asia',      color: '#26a69a' },
  central_asia:        { label: 'Central Asia',        color: '#8d6e63' },
  oceania:             { label: 'Oceania',             color: '#78909c' }
};

const OVERLAY_ENTITIES = {
  EU:   { label: 'European Union',  color: '#3f51b5', members: ['AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE'] },
  NATO: { label: 'NATO',            color: '#1565c0', members: ['USA','GBR','FRA','DEU','CAN','ITA','ESP','TUR','POL','NLD','BEL','NOR','CZE','GRC','PRT','HUN','BGR','ROU','HRV','SVK','SVN','ALB','MNE','MKD','FIN','SWE','ISL','DNK','LUX','LVA','LTU','EST'] },
  BRICS:{ label: 'BRICS',           color: '#e65100', members: ['BRA','RUS','IND','CHN','ZAF','IRN','EGY','ETH','SAU','ARE'] },
  ASEAN:{ label: 'ASEAN',           color: '#00838f', members: ['IDN','THA','MYS','SGP','PHL','VNM','MMR','KHM','LAO','BRN'] },
  OPEC: { label: 'OPEC',            color: '#4e342e', members: ['SAU','IRN','IRQ','KWT','ARE','VEN','NGA','AGO','LBY','DZA','COG','GNQ','GAB'] },
  G7:   { label: 'G7',              color: '#7b1fa2', members: ['USA','GBR','FRA','DEU','JPN','ITA','CAN'] },
  G20:  { label: 'G20',             color: '#c62828', members: ['USA','GBR','FRA','DEU','JPN','ITA','CAN','AUS','BRA','ARG','CHN','IND','IDN','KOR','MEX','RUS','SAU','ZAF','TUR','ARE'] }
};

const TIER_CONFIG = {
  1: { label: 'Tier 1 — Major', color: '#e8e8f0' },
  2: { label: 'Tier 2 — Regional', color: '#9898b8' },
  3: { label: 'Tier 3 — Frontier', color: '#666690' }
};

// Helper: 3-stop color interpolation
function interpolateColor(colorLow, colorMid, colorHigh, t) {
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b];
  }
  function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(c => Math.round(Math.max(0, Math.min(255, c))).toString(16).padStart(2, '0')).join('');
  }
  const low = hexToRgb(colorLow);
  const mid = hexToRgb(colorMid);
  const high = hexToRgb(colorHigh);
  let from, to, local;
  if (t < 0.5) {
    from = low; to = mid; local = t * 2;
  } else {
    from = mid; to = high; local = (t - 0.5) * 2;
  }
  return rgbToHex(
    from[0] + (to[0] - from[0]) * local,
    from[1] + (to[1] - from[1]) * local,
    from[2] + (to[2] - from[2]) * local
  );
}
