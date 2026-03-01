/* ==========================================================================
   Stratoterra — Comparison Tool
   ========================================================================== */

var ComparisonTool = (function() {
  var containerEl = null;
  var selectedCodes = [];
  var mode = 'table'; // 'table' or 'radar'

  var RADAR_AXES = [
    { label: 'Economic', field: 'overall_score' },
    { label: 'Military', fn: function(c) { return c.military_spending_usd ? Math.min(1, c.military_spending_usd / 900000000000) : 0; } },
    { label: 'Technology', field: 'economic_complexity_index', normalize: function(v) { return (v + 2) / 4.5; } },
    { label: 'Stability', field: 'political_stability' },
    { label: 'Openness', field: 'trade_openness_pct', normalize: function(v) { return Math.min(1, v / 200); } },
    { label: 'Energy', field: 'energy_independence' }
  ];

  function render() {
    var summary = DataLoader.getSummary();
    var selected = selectedCodes.map(function(code) { return Utils.getCountryByCode(code, summary); }).filter(Boolean);

    var html = '<div class="comparison">';
    html += '<h2>Country Comparison</h2>';

    // Country selector
    html += '<div class="compare-selector">';
    html += '<div class="compare-tags">';
    selected.forEach(function(c) {
      html += '<span class="compare-tag">' + esc(c.name) + ' <button class="compare-tag__remove" data-code="' + c.code + '">✕</button></span>';
    });
    html += '</div>';
    if (selectedCodes.length < 5) {
      html += '<input type="text" class="compare-search" id="compare-search" placeholder="Add country... (' + (5 - selectedCodes.length) + ' remaining)" />';
      html += '<div class="search-dropdown" id="compare-dropdown"></div>';
    }
    html += '</div>';

    if (selected.length < 2) {
      html += '<div class="panel-no-data"><p>Select at least 2 countries to compare (up to 5).</p></div>';
      html += '</div>';
      containerEl.innerHTML = html;
      bindSelector();
      return;
    }

    // Mode toggle
    html += '<div class="compare-mode-toggle">';
    html += '<button class="layer-tab' + (mode === 'table' ? ' active' : '') + '" data-mode="table">Table</button>';
    html += '<button class="layer-tab' + (mode === 'radar' ? ' active' : '') + '" data-mode="radar">Radar Chart</button>';
    html += '</div>';

    if (mode === 'table') {
      html += renderTable(selected);
    } else {
      html += renderRadar(selected);
    }

    html += '</div>';
    containerEl.innerHTML = html;
    bindSelector();
    bindMode();
    bindRemove();

    if (mode === 'radar') {
      drawRadar(selected);
    }
  }

  function renderTable(selected) {
    var metrics = [
      { label: 'GDP', field: 'gdp_nominal_usd', format: 'currency' },
      { label: 'GDP Growth', field: 'gdp_real_growth_pct', format: 'percent' },
      { label: 'GDP/Capita', field: 'gdp_per_capita_usd', format: 'currency' },
      { label: 'Population', field: 'population', format: 'number' },
      { label: 'Inflation', field: 'inflation_rate_pct', format: 'percent' },
      { label: 'Political Stability', field: 'political_stability', format: 'score' },
      { label: 'Investment Risk', field: 'investment_risk_score', format: 'score' },
      { label: 'Military Spending', field: 'military_spending_usd', format: 'currency' },
      { label: 'Economic Complexity', field: 'economic_complexity_index', format: 'decimal' },
      { label: 'Energy Independence', field: 'energy_independence', format: 'score' },
      { label: 'Trade Openness', field: 'trade_openness_pct', format: 'percent' },
      { label: 'Overall Score', field: 'overall_score', format: 'score' },
      { label: 'Alerts', field: 'alert_count', format: 'number' }
    ];

    var html = '<div class="rankings-table-wrap"><table class="rankings-table">';
    html += '<thead><tr><th>Metric</th>';
    selected.forEach(function(c) { html += '<th>' + esc(c.name) + '</th>'; });
    html += '</tr></thead><tbody>';

    metrics.forEach(function(m) {
      var vals = selected.map(function(c) { return c[m.field]; });
      var best = findBest(vals, m.field);
      html += '<tr><td style="font-weight:600">' + m.label + '</td>';
      selected.forEach(function(c, i) {
        var isBest = i === best;
        var cls = isBest ? 'data-value" style="color:var(--trend-strong-growth)' : 'data-value';
        html += '<td class="' + cls + '">' + formatVal(c[m.field], m.format) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table></div>';
    return html;
  }

  function renderRadar(selected) {
    return '<div class="radar-container"><canvas id="radar-canvas" width="500" height="500" style="max-width:100%;display:block;margin:0 auto"></canvas>' +
      '<div class="radar-legend">' + selected.map(function(c, i) {
        var colors = ['#6ca6ff', '#ff6b6b', '#ffd54f', '#69f0ae', '#ab47bc'];
        return '<span class="radar-legend__item"><span style="display:inline-block;width:12px;height:3px;background:' + colors[i % colors.length] + ';margin-right:6px;vertical-align:middle"></span>' + esc(c.name) + '</span>';
      }).join('') + '</div></div>';
  }

  function drawRadar(selected) {
    var canvas = document.getElementById('radar-canvas');
    if (!canvas) return;

    var labels = RADAR_AXES.map(function(a) { return a.label; });
    var datasets = selected.map(function(c) {
      return {
        label: c.name,
        values: RADAR_AXES.map(function(a) {
          var val;
          if (a.fn) val = a.fn(c);
          else val = c[a.field] || 0;
          if (a.normalize) val = a.normalize(val);
          return Math.max(0, Math.min(1, val));
        })
      };
    });

    Charts.drawRadarChart(canvas, datasets, labels);
  }

  function findBest(vals, field) {
    // For risk, lower is better
    var lowerIsBetter = field === 'investment_risk_score' || field === 'inflation_rate_pct' || field === 'alert_count';
    var bestIdx = 0;
    for (var i = 1; i < vals.length; i++) {
      if (vals[i] == null) continue;
      if (vals[bestIdx] == null) { bestIdx = i; continue; }
      if (lowerIsBetter ? vals[i] < vals[bestIdx] : vals[i] > vals[bestIdx]) bestIdx = i;
    }
    return bestIdx;
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

  function bindSelector() {
    var input = document.getElementById('compare-search');
    var dropdown = document.getElementById('compare-dropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', Utils.debounce(function() {
      var q = input.value.toLowerCase();
      if (q.length < 1) { dropdown.classList.remove('open'); return; }
      var summary = DataLoader.getSummary();
      var matches = summary.filter(function(c) {
        return (c.name.toLowerCase().indexOf(q) !== -1 || c.code.toLowerCase().indexOf(q) !== -1) && selectedCodes.indexOf(c.code) === -1;
      }).slice(0, 6);

      if (matches.length === 0) { dropdown.classList.remove('open'); return; }
      dropdown.innerHTML = matches.map(function(c) {
        return '<div class="search-dropdown__item" data-code="' + c.code + '">' + esc(c.name) + ' <span class="search-dropdown__item-region">' + c.code + '</span></div>';
      }).join('');
      dropdown.classList.add('open');
    }, 150));

    dropdown.addEventListener('click', function(e) {
      var item = e.target.closest('.search-dropdown__item');
      if (item) {
        var code = item.getAttribute('data-code');
        if (selectedCodes.indexOf(code) === -1 && selectedCodes.length < 5) {
          selectedCodes.push(code);
          render();
        }
      }
    });
  }

  function bindMode() {
    containerEl.querySelectorAll('.compare-mode-toggle .layer-tab').forEach(function(btn) {
      btn.addEventListener('click', function() { mode = btn.getAttribute('data-mode'); render(); });
    });
  }

  function bindRemove() {
    containerEl.querySelectorAll('.compare-tag__remove').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var code = btn.getAttribute('data-code');
        selectedCodes = selectedCodes.filter(function(c) { return c !== code; });
        render();
      });
    });
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
