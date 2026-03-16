/* ==========================================================================
   Stratoterra — Relation Explorer (D3 Force Graph + Bilateral)
   ========================================================================== */

var RelationExplorer = (function() {
  var containerEl = null;
  var currentMode = 'network'; // 'network' or 'bilateral'
  var currentCountry = null;
  var currentPair = null;
  var relationIndex = null;
  var loaded = false;
  var panelMode = false;

  async function loadIndex() {
    if (relationIndex) return;
    try {
      relationIndex = await DataLoader.getRelationIndex();
    } catch (err) {
      relationIndex = { pairs: [] };
    }
  }

  function render() {
    var html = '<div class="relation-explorer">';
    html += '<h2>Relation Explorer</h2>';

    // Mode selector — hidden in panel mode; replaced by back button when in bilateral mode
    if (!panelMode) {
      html += '<div class="compare-mode-toggle">';
      html += '<button class="layer-tab' + (currentMode === 'network' ? ' active' : '') + '" data-mode="network">Network Graph</button>';
      html += '<button class="layer-tab' + (currentMode === 'bilateral' ? ' active' : '') + '" data-mode="bilateral">Bilateral Detail</button>';
      html += '</div>';
    } else if (panelMode && currentMode === 'bilateral') {
      html += '<button id="rel-back-btn" class="layer-tab" style="margin-bottom:12px">← Network</button>';
    }

    // Country/Pair selector
    html += '<div class="relation-selector">';
    if (currentMode === 'network') {
      html += '<label>Center country: </label>';
      html += '<select id="relation-country-select" class="alert-filter-select">';
      html += '<option value="">Select...</option>';
      DataLoader.getSummary().filter(function(c) { return c.tier <= 2; }).forEach(function(c) {
        html += '<option value="' + c.code + '"' + (currentCountry === c.code ? ' selected' : '') + '>' + c.name + '</option>';
      });
      html += '</select>';
    } else {
      html += '<label>Select pair: </label>';
      html += '<select id="relation-pair-select" class="alert-filter-select">';
      html += '<option value="">Select...</option>';
      if (relationIndex && relationIndex.pairs) {
        relationIndex.pairs.forEach(function(p) {
          var pair = p.pair || (p.country_a + '_' + p.country_b);
          html += '<option value="' + pair + '"' + (currentPair === pair ? ' selected' : '') + '>' + pair.replace('_', ' ↔ ') + '</option>';
        });
      }
      html += '</select>';
    }
    html += '</div>';

    // Content area
    html += '<div id="relation-content">';
    if (currentMode === 'network' && currentCountry) {
      html += '<div id="network-graph" style="width:100%;height:500px;position:relative"></div>';
    } else if (currentMode === 'bilateral' && currentPair) {
      html += '<div id="bilateral-detail" class="panel-loading"><div class="skeleton" style="width:60%;height:20px;margin:12px auto"></div></div>';
    } else {
      html += '<div class="panel-no-data"><p>Select a country or pair to explore relationships.</p></div>';
    }
    html += '</div>';
    html += '</div>';

    containerEl.innerHTML = html;
    bindEvents();

    if (currentMode === 'network' && currentCountry) {
      drawNetworkGraph();
    } else if (currentMode === 'bilateral' && currentPair) {
      loadBilateral();
    }
  }

  function drawNetworkGraph() {
    var graphEl = document.getElementById('network-graph');
    if (!graphEl || !currentCountry) return;
    if (typeof d3 === 'undefined') {
      graphEl.innerHTML = '<div class="error-card"><p>D3.js not loaded.</p></div>';
      return;
    }

    // Build node/link data from relation index
    var pairs = (relationIndex && relationIndex.pairs) || [];
    var relevantPairs = pairs.filter(function(p) {
      return (p.country_a === currentCountry || p.country_b === currentCountry) ||
             (p.pair && p.pair.indexOf(currentCountry) !== -1);
    });

    var nodeSet = new Set([currentCountry]);
    var links = [];
    relevantPairs.forEach(function(p) {
      var a = p.country_a || p.pair.split('_')[0];
      var b = p.country_b || p.pair.split('_')[1];
      nodeSet.add(a);
      nodeSet.add(b);
      links.push({
        source: a,
        target: b,
        quality: p.composite_score || p.quality || 0.5,
        trade_volume: p.trade_volume_usd || 0
      });
    });

    var summaryMap = {};
    DataLoader.getSummary().forEach(function(c) { summaryMap[c.code] = c; });

    var nodes = Array.from(nodeSet).map(function(code) {
      var s = summaryMap[code];
      return { id: code, name: s ? s.name : code, isCenter: code === currentCountry, gdp: s ? s.gdp_nominal_usd : 0 };
    });

    // If no links, show connected countries from summary
    if (links.length === 0) {
      graphEl.innerHTML = '<div class="panel-no-data"><p>No relation data available for ' + currentCountry + '. Relations will appear after pipeline generates bilateral data.</p></div>';
      return;
    }

    var width = graphEl.offsetWidth;
    var height = Math.max(400, graphEl.parentElement.clientHeight - 60);

    // Clear any existing SVG
    d3.select(graphEl).selectAll('*').remove();

    var svg = d3.select(graphEl).append('svg').attr('width', width).attr('height', height);

    var maxTrade = Math.max.apply(null, links.map(function(l) { return l.trade_volume || 1; }));

    var simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(function(d) { return d.id; }).distance(120))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(30));

    // Links
    var link = svg.append('g').selectAll('line')
      .data(links).join('line')
      .attr('stroke', function(d) {
        if (d.quality >= 0.7) return '#00c853';
        if (d.quality >= 0.4) return '#ffd54f';
        return '#ff1744';
      })
      .attr('stroke-width', function(d) {
        return Math.max(1, (d.trade_volume / maxTrade) * 6);
      })
      .attr('stroke-opacity', 0.6);

    // Nodes
    var node = svg.append('g').selectAll('g')
      .data(nodes).join('g')
      .call(d3.drag()
        .on('start', function(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', function(event, d) { d.fx = event.x; d.fy = event.y; })
        .on('end', function(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    node.append('circle')
      .attr('r', function(d) { return d.isCenter ? 16 : 10; })
      .attr('fill', function(d) { return d.isCenter ? '#4A9FE5' : '#1E293B'; })
      .attr('stroke', function(d) { return d.isCenter ? '#fff' : '#334155'; })
      .attr('stroke-width', function(d) { return d.isCenter ? 2 : 1; });

    node.append('text')
      .text(function(d) { return d.id; })
      .attr('dy', function(d) { return d.isCenter ? -22 : -16; })
      .attr('text-anchor', 'middle')
      .attr('fill', '#F1F5F9')
      .attr('font-size', function(d) { return d.isCenter ? '13px' : '11px'; })
      .attr('font-weight', function(d) { return d.isCenter ? '600' : '400'; });

    simulation.on('tick', function() {
      link.attr('x1', function(d) { return d.source.x; }).attr('y1', function(d) { return d.source.y; })
          .attr('x2', function(d) { return d.target.x; }).attr('y2', function(d) { return d.target.y; });
      node.attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    });

    // Click link → show bilateral
    link.style('cursor', 'pointer').on('click', function(event, d) {
      var a = typeof d.source === 'object' ? d.source.id : d.source;
      var b = typeof d.target === 'object' ? d.target.id : d.target;
      currentPair = [a, b].sort().join('_');
      currentMode = 'bilateral';
      render();
    });
  }

  async function loadBilateral() {
    if (!currentPair) return;
    var parts = currentPair.split('_');
    var detailEl = document.getElementById('bilateral-detail');
    if (!detailEl) return;

    try {
      var data = await DataLoader.getRelation(parts[0], parts[1]);
      renderBilateral(detailEl, data);
    } catch (err) {
      detailEl.innerHTML = '<div class="error-card"><p>Bilateral detail not available for ' + currentPair.replace('_', ' ↔ ') + '.</p></div>';
    }
  }

  function renderBilateral(el, data) {
    var html = '<h3 style="margin-bottom:16px">' + (data.country_a_name || data.country_a) + ' ↔ ' + (data.country_b_name || data.country_b) + '</h3>';

    var dimensions = ['trade', 'diplomatic', 'military', 'financial', 'energy', 'scientific'];
    dimensions.forEach(function(dim) {
      var d = data[dim];
      if (!d) return;
      html += '<div class="factor-card" style="margin-bottom:12px">';
      html += '<div class="factor-card__header"><span class="factor-card__label" style="text-transform:capitalize">' + dim + '</span>';
      if (d.score != null) {
        var color = d.score >= 0.7 ? 'var(--relation-allied)' : d.score >= 0.4 ? 'var(--relation-neutral)' : 'var(--relation-hostile)';
        html += '<span class="data-value" style="color:' + color + '">' + d.score.toFixed(2) + '</span>';
      }
      html += '</div>';

      // Render dimension-specific fields
      if (dim === 'trade' && d.volume_usd) html += '<p style="font-size:12px;color:var(--text-secondary)">Volume: ' + Utils.formatCurrency(d.volume_usd) + '</p>';
      if (d.summary || d.description) html += '<p style="font-size:12px;color:var(--text-secondary)">' + esc(d.summary || d.description) + '</p>';
      html += '</div>';
    });

    if (data.composite_score != null) {
      var compColor = data.composite_score >= 0.7 ? 'var(--relation-allied)' : data.composite_score >= 0.4 ? 'var(--relation-neutral)' : 'var(--relation-hostile)';
      html += '<div class="factor-card" style="background:var(--bg-secondary)"><div class="factor-card__header"><span class="factor-card__label">Composite Score</span></div>';
      html += '<div class="factor-card__value" style="color:' + compColor + '">' + data.composite_score.toFixed(2) + '</div>';
      if (data.relationship_type) html += '<p style="font-size:12px;color:var(--text-secondary);margin-top:4px;text-transform:capitalize">' + data.relationship_type + '</p>';
      html += '</div>';
    }

    el.innerHTML = html;
  }

  function bindEvents() {
    containerEl.querySelectorAll('.compare-mode-toggle .layer-tab').forEach(function(btn) {
      btn.addEventListener('click', function() { currentMode = btn.getAttribute('data-mode'); render(); });
    });

    var backBtn = document.getElementById('rel-back-btn');
    if (backBtn) backBtn.addEventListener('click', function() { currentMode = 'network'; render(); });

    var countrySelect = document.getElementById('relation-country-select');
    if (countrySelect) countrySelect.addEventListener('change', function() { currentCountry = this.value || null; render(); });

    var pairSelect = document.getElementById('relation-pair-select');
    if (pairSelect) pairSelect.addEventListener('change', function() { currentPair = this.value || null; render(); });
  }

  function esc(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  return {
    show: async function(el, params, options) {
      containerEl = el;
      panelMode = !!(options && options.panelMode);
      await loadIndex();

      // Parse URL params
      if (params) {
        if (params.country) { currentCountry = params.country; currentMode = 'network'; }
        if (params.pair) { currentPair = params.pair; currentMode = 'bilateral'; }
      }

      render();
    }
  };
})();
