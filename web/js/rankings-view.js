/* ==========================================================================
   Stratoterra — Rankings View
   ========================================================================== */

var RankingsView = (function() {
  var containerEl = null;
  var sortField = 'gdp_nominal_usd';
  var sortAsc = false;
  var filterRegion = 'all';
  var filterTier = 'all';
  var currentGroup = 'economic';

  var METRIC_GROUPS = {
    economic: {
      label: 'rankings.group_economic',
      columns: [
        { field: 'gdp_nominal_usd', label: 'rankings.col_gdp', format: 'currency' },
        { field: 'gdp_real_growth_pct', label: 'rankings.col_growth', format: 'percent' },
        { field: 'gdp_per_capita_usd', label: 'rankings.col_gdp_cap', format: 'currency' },
        { field: 'inflation_rate_pct', label: 'rankings.col_inflation', format: 'percent' },
        { field: 'trade_openness_pct', label: 'rankings.col_trade_open', format: 'percent' },
        { field: 'political_risk_premium_bps', label: 'rankings.col_risk_prem', format: 'number' }
      ]
    },
    power: {
      label: 'rankings.group_power',
      columns: [
        { field: 'composite_national_power_index', label: 'rankings.col_overall', format: 'score' },
        { field: 'military_expenditure_usd', label: 'rankings.col_mil_spend', format: 'currency' },
        { field: 'population', label: 'rankings.col_population', format: 'number' },
        { field: 'energy_independence', label: 'rankings.col_energy_ind', format: 'score' }
      ]
    },
    risk: {
      label: 'rankings.group_risk',
      columns: [
        { field: 'investment_risk_score', label: 'rankings.col_inv_risk', format: 'score' },
        { field: 'political_stability', label: 'rankings.col_pol_stability', format: 'score' },
        { field: 'political_risk_premium_bps', label: 'rankings.col_risk_prem', format: 'number' },
        { field: 'alert_count', label: 'rankings.col_alerts', format: 'number' }
      ]
    },
    development: {
      label: 'rankings.group_development',
      columns: [
        { field: 'gdp_per_capita_usd', label: 'rankings.col_gdp_cap', format: 'currency' },
        { field: 'composite_national_power_index', label: 'rankings.col_power_index', format: 'score' },
        { field: 'energy_independence', label: 'rankings.col_energy', format: 'score' },
        { field: 'trade_openness_pct', label: 'rankings.col_trade_pct', format: 'percent' }
      ]
    }
  };

  function render() {
    var summary = DataLoader.getSummary();
    var filtered = summary.filter(function(c) {
      if (filterRegion !== 'all' && c.region !== filterRegion) return false;
      if (filterTier !== 'all' && c.tier !== parseInt(filterTier)) return false;
      return true;
    });

    filtered.sort(function(a, b) {
      var va = a[sortField], vb = b[sortField];
      if (va == null) return 1;
      if (vb == null) return -1;
      if (typeof va === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      return sortAsc ? va - vb : vb - va;
    });

    var group = METRIC_GROUPS[currentGroup];
    var cols = group.columns;

    var html = '<div class="rankings">';
    html += '<h2>' + I18n.t('rankings.title') + '</h2>';

    // Group tabs
    html += '<div class="rankings-groups">';
    Object.keys(METRIC_GROUPS).forEach(function(key) {
      var cls = key === currentGroup ? 'layer-tab active' : 'layer-tab';
      html += '<button class="' + cls + '" data-group="' + key + '">' + I18n.t(METRIC_GROUPS[key].label) + '</button>';
    });
    html += '</div>';

    // Filters
    html += '<div class="alert-filters">';
    html += '<select id="rank-region-filter" class="alert-filter-select">';
    html += '<option value="all">' + I18n.t('rankings.all_regions') + '</option>';
    Object.keys(REGIONS).forEach(function(r) {
      html += '<option value="' + r + '"' + (filterRegion === r ? ' selected' : '') + '>' + I18n.t(REGIONS[r].label) + '</option>';
    });
    html += '</select>';
    html += '<select id="rank-tier-filter" class="alert-filter-select">';
    html += '<option value="all">' + I18n.t('rankings.all_tiers') + '</option>';
    html += '<option value="1"' + (filterTier === '1' ? ' selected' : '') + '>' + I18n.t('rankings.tier_1') + '</option>';
    html += '<option value="2"' + (filterTier === '2' ? ' selected' : '') + '>' + I18n.t('rankings.tier_2') + '</option>';
    html += '<option value="3"' + (filterTier === '3' ? ' selected' : '') + '>' + I18n.t('rankings.tier_3') + '</option>';
    html += '</select>';
    html += '<span style="color:var(--text-muted);font-size:12px">' + filtered.length + ' ' + I18n.t('rankings.countries') + '</span>';
    html += '</div>';

    // Table
    html += '<div class="rankings-table-wrap"><table class="rankings-table">';
    html += '<thead><tr>';
    html += '<th class="rank-col">' + I18n.t('rankings.col_rank') + '</th>';
    html += sortTh('name', I18n.t('rankings.col_country'));
    html += sortTh('region', I18n.t('rankings.col_region'));
    cols.forEach(function(col) {
      html += sortTh(col.field, I18n.t(col.label));
    });
    html += '</tr></thead>';
    html += '<tbody>';
    filtered.forEach(function(c, i) {
      html += '<tr class="rankings-row" data-code="' + c.code + '">';
      html += '<td class="rank-col">' + (i + 1) + '</td>';
      html += '<td class="name-col"><strong>' + esc(c.name) + '</strong> <span class="data-value" style="font-size:11px;color:var(--text-muted)">' + c.code + '</span></td>';
      html += '<td>' + (REGIONS[c.region] ? I18n.t(REGIONS[c.region].label) : c.region) + '</td>';
      cols.forEach(function(col) {
        html += '<td class="data-value">' + formatVal(c[col.field], col.format) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table></div>';
    html += '</div>';

    containerEl.innerHTML = html;

    // Bind events
    containerEl.querySelectorAll('.rankings-groups .layer-tab').forEach(function(btn) {
      btn.addEventListener('click', function() { currentGroup = btn.getAttribute('data-group'); sortField = METRIC_GROUPS[currentGroup].columns[0].field; render(); });
    });
    containerEl.querySelectorAll('.sort-th').forEach(function(th) {
      th.addEventListener('click', function() {
        var field = th.getAttribute('data-field');
        if (sortField === field) sortAsc = !sortAsc;
        else { sortField = field; sortAsc = false; }
        render();
      });
    });
    var rf = document.getElementById('rank-region-filter');
    var tf = document.getElementById('rank-tier-filter');
    if (rf) rf.addEventListener('change', function() { filterRegion = this.value; render(); });
    if (tf) tf.addEventListener('change', function() { filterTier = this.value; render(); });

    // Row clicks navigate to map
    containerEl.querySelectorAll('.rankings-row').forEach(function(row) {
      row.addEventListener('click', function() {
        var code = row.getAttribute('data-code');
        window.location.hash = '#map';
        setTimeout(function() { CountryPanel.open(code); }, 200);
      });
    });
  }

  function sortTh(field, label) {
    var arrow = '';
    if (sortField === field) arrow = sortAsc ? ' ▲' : ' ▼';
    return '<th class="sort-th" data-field="' + field + '" style="cursor:pointer">' + label + arrow + '</th>';
  }

  function formatVal(val, fmt) {
    if (val == null) return '—';
    switch(fmt) {
      case 'currency': return Utils.formatCurrency(val);
      case 'percent': return Utils.formatPercent(val, 1);
      case 'score': return Utils.formatScore(val);
      case 'decimal': return Number(val).toFixed(2);
      case 'number': return Utils.formatNumber(val);
      default: return String(val);
    }
  }

  function esc(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  return {
    show: function(el) {
      containerEl = el;
      render();
    }
  };
})();
