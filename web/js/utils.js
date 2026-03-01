/* ==========================================================================
   Stratoterra — Utility Functions
   ========================================================================== */

const Utils = {
  formatNumber(value, decimals) {
    if (value == null || isNaN(value)) return '—';
    decimals = decimals != null ? decimals : 0;
    if (Math.abs(value) >= 1e12) return (value / 1e12).toFixed(1) + 'T';
    if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(1) + 'B';
    if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(1) + 'M';
    if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(1) + 'K';
    return Number(value).toFixed(decimals);
  },

  formatCurrency(value, currency) {
    if (value == null || isNaN(value)) return '—';
    currency = currency || 'USD';
    const symbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency === 'GBP' ? '£' : currency + ' ';
    if (Math.abs(value) >= 1e12) return symbol + (value / 1e12).toFixed(2) + 'T';
    if (Math.abs(value) >= 1e9) return symbol + (value / 1e9).toFixed(1) + 'B';
    if (Math.abs(value) >= 1e6) return symbol + (value / 1e6).toFixed(1) + 'M';
    return symbol + Number(value).toLocaleString();
  },

  formatPercent(value, decimals) {
    if (value == null || isNaN(value)) return '—';
    decimals = decimals != null ? decimals : 1;
    return Number(value).toFixed(decimals) + '%';
  },

  formatScore(value) {
    if (value == null || isNaN(value)) return '—';
    return Number(value).toFixed(2);
  },

  formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  },

  formatRelativeDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const now = new Date();
    const diffMs = now - d;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return diffDays + 'd ago';
    if (diffDays < 30) return Math.floor(diffDays / 7) + 'w ago';
    return Math.floor(diffDays / 30) + 'mo ago';
  },

  debounce(fn, delay) {
    let timer;
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function() { fn.apply(context, args); }, delay);
    };
  },

  throttle(fn, limit) {
    let last = 0;
    return function() {
      const now = Date.now();
      if (now - last >= limit) {
        last = now;
        return fn.apply(this, arguments);
      }
    };
  },

  getCountryByCode(code, countries) {
    if (!countries) return null;
    if (Array.isArray(countries)) return countries.find(function(c) { return c.code === code; });
    return countries[code] || null;
  },

  getTrendInfo(trend) {
    return TREND_LABELS[trend] || TREND_LABELS.stable;
  },

  getSeverityInfo(severity) {
    return ALERT_SEVERITY[severity] || ALERT_SEVERITY.none;
  },

  getMetricValue(summary, metricId) {
    if (!summary || !METRIC_CONFIG[metricId]) return null;
    var field = METRIC_CONFIG[metricId].field;
    // Handle trend fields that map to numeric values
    if (metricId === 'military_spending_trend') {
      var trendMap = { strong_growth: 12, growth: 6, stable: 0, decrease: -5, strong_decrease: -10 };
      return trendMap[summary[field]] != null ? trendMap[summary[field]] : 0;
    }
    if (metricId === 'alert_severity') {
      var sevMap = { critical: 3, warning: 2, watch: 1, none: 0 };
      return sevMap[summary[field]] != null ? sevMap[summary[field]] : 0;
    }
    if (metricId === 'gdp_growth_trend') {
      // This can be a numeric value or a trend label
      if (typeof summary[field] === 'number') return summary[field];
      var growthMap = { strong_growth: 7, growth: 3, stable: 1, decrease: -1, strong_decrease: -4 };
      return growthMap[summary[field]] != null ? growthMap[summary[field]] : summary.gdp_real_growth_pct || 0;
    }
    return summary[field] != null ? summary[field] : null;
  },

  formatMetricValue(value, metricId) {
    if (value == null) return '—';
    var config = METRIC_CONFIG[metricId];
    if (!config) return String(value);
    switch (config.format) {
      case 'percent1': return this.formatPercent(value, 1);
      case 'percent0': return this.formatPercent(value, 0);
      case 'score': return this.formatScore(value);
      case 'decimal2': return Number(value).toFixed(2);
      case 'severity':
        var labels = ['None', 'Watch', 'Warning', 'Critical'];
        return labels[Math.round(value)] || 'None';
      case 'trend':
        if (value > 5) return '↗ Strong';
        if (value > 0) return '↗ Growth';
        if (value > -5) return '↘ Decline';
        return '⬇ Strong Decline';
      default: return String(value);
    }
  },

  // Build HTML for confidence bar
  confidenceBarHTML(confidence) {
    if (confidence == null) return '';
    var level = confidence >= 0.7 ? 'high' : confidence >= 0.4 ? 'medium' : 'low';
    var pct = Math.round(confidence * 100);
    return '<span class="confidence-bar"><span class="confidence-bar__fill confidence-bar__fill--' + level + '" style="width:' + pct + '%"></span></span>';
  },

  // Build HTML for trend indicator
  trendHTML(trendKey) {
    var info = this.getTrendInfo(trendKey);
    return '<span class="trend ' + info.cssClass + '"><span class="trend-arrow"></span> ' + info.label + '</span>';
  },

  // Clamp a value between min and max
  clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }
};
