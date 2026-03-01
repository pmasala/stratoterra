/* ==========================================================================
   Stratoterra — Alert Dashboard
   ========================================================================== */

var AlertDashboard = (function() {
  var containerEl = null;
  var loaded = false;
  var allAlerts = [];
  var filterRegion = 'all';
  var filterType = 'all';

  function render() {
    var filtered = allAlerts.filter(function(a) {
      if (filterRegion !== 'all' && a.region !== filterRegion) return false;
      if (filterType !== 'all' && a.type !== filterType) return false;
      return true;
    });

    var critical = filtered.filter(function(a) { return a.severity === 'critical'; });
    var warning = filtered.filter(function(a) { return a.severity === 'warning'; });
    var watch = filtered.filter(function(a) { return a.severity === 'watch'; });

    var html = '<div class="alerts-dashboard">';
    html += '<h2>Alert Dashboard</h2>';

    // Summary counts
    html += '<div class="alert-summary-bar">';
    html += '<div class="alert-summary-count alert-summary-count--critical"><span class="alert-summary-count__num">' + critical.length + '</span><span class="alert-summary-count__label">Critical</span></div>';
    html += '<div class="alert-summary-count alert-summary-count--warning"><span class="alert-summary-count__num">' + warning.length + '</span><span class="alert-summary-count__label">Warning</span></div>';
    html += '<div class="alert-summary-count alert-summary-count--watch"><span class="alert-summary-count__num">' + watch.length + '</span><span class="alert-summary-count__label">Watch</span></div>';
    html += '</div>';

    // Filters
    html += '<div class="alert-filters">';
    html += '<select id="alert-region-filter" class="alert-filter-select">';
    html += '<option value="all">All Regions</option>';
    Object.keys(REGIONS).forEach(function(r) {
      html += '<option value="' + r + '"' + (filterRegion === r ? ' selected' : '') + '>' + REGIONS[r].label + '</option>';
    });
    html += '</select>';
    html += '<select id="alert-type-filter" class="alert-filter-select">';
    html += '<option value="all">All Types</option>';
    var types = new Set();
    allAlerts.forEach(function(a) { if (a.type) types.add(a.type); });
    types.forEach(function(t) {
      html += '<option value="' + t + '"' + (filterType === t ? ' selected' : '') + '>' + t.charAt(0).toUpperCase() + t.slice(1) + '</option>';
    });
    html += '</select>';
    html += '</div>';

    // Alert sections
    if (critical.length) html += renderAlertSection('Critical', critical, 'critical');
    if (warning.length) html += renderAlertSection('Warning', warning, 'warning');
    if (watch.length) html += renderAlertSection('Watch', watch, 'watch');
    if (filtered.length === 0) {
      html += '<div class="panel-no-data"><p>No alerts match the current filters.</p></div>';
    }

    html += '</div>';
    containerEl.innerHTML = html;

    // Bind filters
    var regionFilter = document.getElementById('alert-region-filter');
    var typeFilter = document.getElementById('alert-type-filter');
    if (regionFilter) regionFilter.addEventListener('change', function() { filterRegion = this.value; render(); });
    if (typeFilter) typeFilter.addEventListener('change', function() { filterType = this.value; render(); });
  }

  function renderAlertSection(title, alerts, severity) {
    var html = '<div class="alert-section">';
    html += '<h3 class="alert-section__title" style="color:var(--alert-' + severity + ')">' + title + ' (' + alerts.length + ')</h3>';
    alerts.forEach(function(a) {
      html += '<div class="alert-card alert-card--' + severity + '">';
      html += '<div class="alert-card__header">';
      html += '<span class="alert-badge alert-badge--' + severity + '">' + severity + '</span>';
      if (a.type) html += '<span class="alert-card__type">' + esc(a.type) + '</span>';
      html += '</div>';
      html += '<h4 class="alert-card__title">' + esc(a.title) + '</h4>';
      html += '<p class="alert-card__body">' + esc(a.description || a.summary) + '</p>';
      if (a.countries && a.countries.length) {
        html += '<div class="alert-card__countries">';
        a.countries.forEach(function(c) {
          html += '<span class="panel-sources__tag">' + esc(c) + '</span>';
        });
        html += '</div>';
      }
      if (a.investor_action) {
        html += '<div class="alert-card__action"><strong>Action:</strong> ' + esc(a.investor_action) + '</div>';
      }
      html += '</div>';
    });
    html += '</div>';
    return html;
  }

  function esc(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  return {
    show: async function(el) {
      containerEl = el;
      if (loaded) { render(); return; }

      containerEl.innerHTML = '<div class="panel-loading"><div class="skeleton" style="width:60%;height:24px;margin:16px auto"></div></div>';

      try {
        var data = await DataLoader.getAlerts();
        allAlerts = data.alerts || data || [];
        loaded = true;
        render();
      } catch (err) {
        containerEl.innerHTML = '<div class="error-card"><h3 class="error-card__title">Alerts unavailable</h3><p>Alert data has not been generated yet.</p></div>';
      }
    },

    reset: function() {
      loaded = false;
      allAlerts = [];
    }
  };
})();
