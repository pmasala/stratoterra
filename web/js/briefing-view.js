/* ==========================================================================
   Stratoterra — Weekly Briefing View
   ========================================================================== */

var BriefingView = (function() {
  var containerEl = null;
  var loaded = false;

  function slugify(str) {
    return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  function render(data) {
    var html = '<div class="briefing">';

    // Headline
    html += '<div class="briefing-headline">';
    html += '<h2>' + esc(data.headline || 'Weekly Briefing') + '</h2>';
    html += '<p class="briefing-date">' + Utils.formatDate(data.date || data.generated_date) + '</p>';
    html += '</div>';

    // Market Context Strip
    if (data.market_context) {
      var mc = data.market_context;
      if (typeof mc === 'string') {
        // Plain text market context
        html += '<div class="briefing-section"><h3>Market Context</h3><p>' + esc(mc) + '</p></div>';
      } else if (mc.oil_brent_usd || mc.gold_usd || mc.eur_usd || mc.us_10y_yield || mc.dxy_index) {
        // Structured numeric market data
        html += '<div class="market-strip">';
        if (mc.oil_brent_usd) html += marketChip('Brent', '$' + mc.oil_brent_usd, mc.oil_change_pct);
        if (mc.gold_usd) html += marketChip('Gold', '$' + mc.gold_usd, mc.gold_change_pct);
        if (mc.eur_usd) html += marketChip('EUR/USD', mc.eur_usd.toFixed(4), mc.eur_usd_change_pct);
        if (mc.us_10y_yield) html += marketChip('US 10Y', mc.us_10y_yield.toFixed(2) + '%', mc.us_10y_change_bps);
        if (mc.dxy_index) html += marketChip('DXY', mc.dxy_index.toFixed(1), mc.dxy_change_pct);
        html += '</div>';
      } else if (mc.summary || mc.notable_moves) {
        // Summary + notable moves format
        html += '<div class="briefing-section"><h3>Market Context</h3>';
        if (mc.summary) html += '<p>' + esc(mc.summary) + '</p>';
        if (mc.notable_moves && mc.notable_moves.length) {
          html += '<div class="market-strip">';
          mc.notable_moves.forEach(function(m) {
            if (typeof m === 'string') {
              html += '<div class="market-chip"><span class="market-chip__label">' + esc(m) + '</span></div>';
              return;
            }
            var label = m.asset || m.name || '';
            var val = m.value != null ? (m.unit ? m.value.toLocaleString() + ' ' + m.unit : String(m.value)) : '';
            var changePct = m.change_pct;
            var changeClass = changePct > 0 ? 'trend--growth' : changePct < 0 ? 'trend--decrease' : 'trend--stable';
            var changeStr = changePct != null ? (changePct > 0 ? '+' : '') + Number(changePct).toFixed(1) + '%' : '';
            var driver = m.driver || m.description || '';
            html += '<div class="market-chip" title="' + esc(driver) + '">';
            html += '<span class="market-chip__label">' + esc(label) + '</span>';
            if (val) html += '<span class="market-chip__value data-value">' + esc(val) + '</span>';
            if (changeStr) html += '<span class="market-chip__change ' + changeClass + '">' + esc(changeStr) + '</span>';
            html += '</div>';
          });
          html += '</div>';
        }
        html += '</div>';
      }
    }

    // Top Stories
    if (data.top_stories && data.top_stories.length) {
      html += '<div class="briefing-section">';
      html += '<h3>Top Stories</h3>';
      data.top_stories.forEach(function(story, i) {
        var sevClass = story.severity ? 'alert-badge--' + story.severity : '';
        html += '<div class="story-card">';
        html += '<div class="story-card__header">';
        if (story.severity) html += '<span class="alert-badge ' + sevClass + '">' + esc(story.severity) + '</span>';
        html += '<span class="story-card__number">#' + (i + 1) + '</span>';
        html += '</div>';
        html += '<h4 class="story-card__title">' + esc(story.title) + '</h4>';
        html += '<p class="story-card__body">' + esc(story.summary || story.description) + '</p>';
        var storyCountries = story.countries || story.countries_affected || story.countries_involved || [];
        if (storyCountries.length) {
          html += '<div class="story-card__countries">';
          storyCountries.forEach(function(c) {
            html += '<span class="panel-sources__tag">' + esc(c) + '</span>';
          });
          html += '</div>';
        }
        var investorNote = story.investor_action || story.investor_impact;
        if (investorNote) {
          html += '<div class="story-card__action"><strong>Investor action:</strong> ' + esc(investorNote) + '</div>';
        }
        html += '</div>';
      });
      html += '</div>';
    }

    // Regional Roundup
    if (data.regional_summaries) {
      html += '<div class="briefing-section">';
      html += '<h3>Regional Roundup</h3>';
      var regions = Object.keys(data.regional_summaries);
      html += '<div class="region-tabs" id="region-tabs">';
      regions.forEach(function(r, i) {
        var label = REGIONS[r] ? REGIONS[r].label : r;
        var cls = i === 0 ? 'region-tab active' : 'region-tab';
        html += '<button class="' + cls + '" data-region="' + slugify(r) + '">' + esc(label) + '</button>';
      });
      html += '</div>';
      regions.forEach(function(r, i) {
        var cls = i === 0 ? 'region-content active' : 'region-content';
        var summary = data.regional_summaries[r];
        html += '<div class="' + cls + '" id="region-' + slugify(r) + '">';
        html += '<p>' + esc(typeof summary === 'string' ? summary : summary.summary || JSON.stringify(summary)) + '</p>';
        html += '</div>';
      });
      html += '</div>';
    }

    html += '</div>';
    containerEl.innerHTML = html;

    // Bind region tabs
    var tabsEl = document.getElementById('region-tabs');
    if (tabsEl) {
      tabsEl.addEventListener('click', function(e) {
        var btn = e.target.closest('.region-tab');
        if (!btn) return;
        var region = btn.getAttribute('data-region');
        tabsEl.querySelectorAll('.region-tab').forEach(function(t) { t.classList.remove('active'); });
        btn.classList.add('active');
        containerEl.querySelectorAll('.region-content').forEach(function(c) { c.classList.remove('active'); });
        var content = document.getElementById('region-' + region);
        if (content) content.classList.add('active');
      });
    }
  }

  function marketChip(label, value, change) {
    var changeClass = change > 0 ? 'trend--growth' : change < 0 ? 'trend--decrease' : 'trend--stable';
    var changeStr = change != null ? (change > 0 ? '+' : '') + change.toFixed(1) + (label.includes('10Y') ? 'bps' : '%') : '';
    return '<div class="market-chip">' +
      '<span class="market-chip__label">' + label + '</span>' +
      '<span class="market-chip__value data-value">' + value + '</span>' +
      (changeStr ? '<span class="market-chip__change ' + changeClass + '">' + changeStr + '</span>' : '') +
      '</div>';
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
      if (loaded) return;

      containerEl.innerHTML = '<div class="panel-loading"><div class="skeleton" style="width:60%;height:24px;margin:16px auto"></div><div class="skeleton" style="width:80%;height:16px;margin:8px auto"></div></div>';

      try {
        var data = await DataLoader.getBriefing();
        render(data);
        loaded = true;
      } catch (err) {
        containerEl.innerHTML = '<div class="error-card"><h3 class="error-card__title">Briefing unavailable</h3><p>Weekly briefing data has not been generated yet.</p></div>';
      }
    },

    reset: function() {
      loaded = false;
    }
  };
})();
