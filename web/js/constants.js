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
// label values are i18n keys — resolve with I18n.t(config.label) at render time
const METRIC_CONFIG = {
  gdp_growth_trend:      { label: 'metric.gdp_growth_pct',        field: 'gdp_real_growth_pct',    format: 'percent1',  legendMin: '-5%', legendMax: '+10%' },
  political_stability:   { label: 'metric.political_stability',   field: 'political_stability',    format: 'score',     legendMin: '0', legendMax: '1.0' },
  investment_risk:       { label: 'metric.investment_risk',        field: 'investment_risk_score',  format: 'score',     legendMin: 'legend.low', legendMax: 'legend.high' },
  military_spending_trend:{ label: 'metric.military_spend_trend',  field: 'military_spending_trend',format: 'trend',     legendMin: 'legend.decline', legendMax: 'legend.growth' },
  military_spending_pct_gdp:{ label: 'metric.military_spend_pct_gdp', field: 'military_expenditure_pct_gdp', format: 'percent1', legendMin: '0%', legendMax: '6%' },
  alert_severity:        { label: 'metric.alert_severity',         field: 'max_alert_severity',     format: 'severity',  legendMin: 'severity.none', legendMax: 'severity.critical' },
  composite_power:       { label: 'metric.national_power_index',   field: 'composite_national_power_index', format: 'decimal2', legendMin: '0', legendMax: '100' },
  energy_independence:   { label: 'metric.energy_independence',    field: 'energy_independence',    format: 'score',     legendMin: '0', legendMax: '1.0' },
  trade_openness:        { label: 'metric.trade_openness_pct',     field: 'trade_openness_pct',     format: 'percent0',  legendMin: '0%', legendMax: '200%' }
};

// Helper: resolve metric label via I18n
function getMetricLabel(metricId) {
  var config = METRIC_CONFIG[metricId];
  if (!config) return metricId;
  return I18n.t(config.label);
}

// Helper: resolve legend label via I18n (passes through raw values like '0%')
function getLegendLabel(value) {
  if (!value) return value;
  if (value.indexOf('.') !== -1 && isNaN(Number(value))) {
    return I18n.t(value);
  }
  return value;
}

const TREND_LABELS = {
  strong_growth:    { label: 'trend.strong_growth',    arrow: '⬆', cssClass: 'trend--strong-growth' },
  growth:           { label: 'trend.growth',           arrow: '↗', cssClass: 'trend--growth' },
  stable:           { label: 'trend.stable',           arrow: '→', cssClass: 'trend--stable' },
  decrease:         { label: 'trend.decrease',         arrow: '↘', cssClass: 'trend--decrease' },
  strong_decrease:  { label: 'trend.strong_decrease',  arrow: '⬇', cssClass: 'trend--strong-decrease' }
};

const ALERT_SEVERITY = {
  critical: { label: 'severity.critical', color: '#ff1744', numericValue: 3 },
  warning:  { label: 'severity.warning',  color: '#ffab40', numericValue: 2 },
  watch:    { label: 'severity.watch',    color: '#448aff', numericValue: 1 },
  none:     { label: 'severity.none',     color: '#2a2a5a', numericValue: 0 }
};

const REGIONS = {
  north_america:       { label: 'region.north_america',       color: '#42a5f5' },
  latin_america:       { label: 'region.latin_america',       color: '#66bb6a' },
  europe:              { label: 'region.europe',              color: '#ab47bc' },
  middle_east:         { label: 'region.middle_east',         color: '#ffa726' },
  sub_saharan_africa:  { label: 'region.sub_saharan_africa',  color: '#ef5350' },
  south_asia:          { label: 'region.south_asia',          color: '#26c6da' },
  east_asia:           { label: 'region.east_asia',           color: '#ec407a' },
  southeast_asia:      { label: 'region.southeast_asia',      color: '#26a69a' },
  central_asia:        { label: 'region.central_asia',        color: '#8d6e63' },
  oceania:             { label: 'region.oceania',             color: '#78909c' }
};

const OVERLAY_ENTITIES = {
  EU:   { label: 'overlay.eu',    color: '#3f51b5', members: ['AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE'] },
  NATO: { label: 'overlay.nato',  color: '#1565c0', members: ['USA','GBR','FRA','DEU','CAN','ITA','ESP','TUR','POL','NLD','BEL','NOR','CZE','GRC','PRT','HUN','BGR','ROU','HRV','SVK','SVN','ALB','MNE','MKD','FIN','SWE','ISL','DNK','LUX','LVA','LTU','EST'] },
  BRICS:{ label: 'overlay.brics', color: '#e65100', members: ['BRA','RUS','IND','CHN','ZAF','IRN','EGY','ETH','SAU','ARE'] },
  ASEAN:{ label: 'overlay.asean', color: '#00838f', members: ['IDN','THA','MYS','SGP','PHL','VNM','MMR','KHM','LAO','BRN'] },
  OPEC: { label: 'overlay.opec',  color: '#4e342e', members: ['SAU','IRN','IRQ','KWT','ARE','VEN','NGA','AGO','LBY','DZA','COG','GNQ','GAB'] },
  G7:   { label: 'overlay.g7',    color: '#7b1fa2', members: ['USA','GBR','FRA','DEU','JPN','ITA','CAN'] },
  G20:  { label: 'overlay.g20',   color: '#c62828', members: ['USA','GBR','FRA','DEU','JPN','ITA','CAN','AUS','BRA','ARG','CHN','IND','IDN','KOR','MEX','RUS','SAU','ZAF','TUR','ARE'] }
};

const TIER_CONFIG = {
  1: { label: 'tier.1', color: '#e8e8f0' },
  2: { label: 'tier.2', color: '#9898b8' },
  3: { label: 'tier.3', color: '#666690' }
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
