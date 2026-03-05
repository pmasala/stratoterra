/* ==========================================================================
   Stratoterra — Briefing View (News-Channel Style)
   Listing mode: article card grid
   Detail mode: full article with SVG hero, sections, sources, AI disclaimer
   ========================================================================== */

var BriefingView = (function() {
  var containerEl = null;
  var lastMode = null;   // 'listing' | article id
  var briefingData = null;

  function slugify(str) {
    return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  function esc(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  function sanitizeSVG(str) {
    if (!str) return '';
    try {
      var doc = new DOMParser().parseFromString(str, 'image/svg+xml');
      var svg = doc.querySelector('svg');
      if (!svg) return '';
      svg.querySelectorAll('script').forEach(function(s) { s.remove(); });
      svg.querySelectorAll('*').forEach(function(el) {
        Array.from(el.attributes).forEach(function(a) {
          if (a.name.startsWith('on')) el.removeAttribute(a.name);
        });
      });
      return svg.outerHTML;
    } catch (e) {
      return '';
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      var d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  }

  function severityClass(sev) {
    if (sev === 'critical' || sev === 'transformative') return 'alert-badge--critical';
    if (sev === 'warning' || sev === 'significant') return 'alert-badge--warning';
    if (sev === 'watch') return 'alert-badge--watch';
    return '';
  }

  /* ---- Listing Mode (card grid) ---- */
  function renderListing(articles, briefing) {
    var html = '<div class="briefing">';

    // Market context strip (from weekly briefing)
    if (briefing) {
      html += renderMarketContext(briefing);
    }

    if (articles && articles.length) {
      html += '<div class="article-grid">';
      articles.forEach(function(art, i) {
        var featured = i === 0 ? ' article-card--featured' : '';
        html += '<a class="article-card' + featured + '" href="#briefing/article/' + esc(art.article_id) + '">';
        if (art.hero_svg) {
          html += '<div class="article-card__image">' + sanitizeSVG(art.hero_svg) + '</div>';
        }
        html += '<div class="article-card__body">';
        html += '<div class="article-card__meta">';
        html += '<span class="article-card__date">' + formatDate(art.published_at) + '</span>';
        if (art.severity) {
          html += '<span class="alert-badge ' + severityClass(art.severity) + '">' + esc(art.severity) + '</span>';
        }
        if (art.categories && art.categories.length) {
          art.categories.forEach(function(cat) {
            html += '<span class="article-card__category">' + esc(cat) + '</span>';
          });
        }
        html += '</div>';
        html += '<h3 class="article-card__headline">' + esc(art.headline) + '</h3>';
        if (art.subheadline) {
          html += '<p class="article-card__subheadline">' + esc(art.subheadline) + '</p>';
        }
        var excerpt = art.lede_excerpt || '';
        if (excerpt) {
          html += '<p class="article-card__excerpt">' + esc(excerpt) + '</p>';
        }
        html += '</div>';
        html += '</a>';
      });
      html += '</div>';
    } else if (briefing) {
      // Fallback: render old-style top stories
      html += renderTopStories(briefing);
    }

    // Regional roundup
    if (briefing && briefing.regional_summaries) {
      html += renderRegionalRoundup(briefing);
    }

    html += '</div>';
    containerEl.innerHTML = html;
    bindRegionTabs();
  }

  function renderMarketContext(data) {
    var html = '';
    if (!data.market_context) return html;
    var mc = data.market_context;
    if (typeof mc === 'string') {
      html += '<div class="briefing-section"><h3>Market Context</h3><p>' + esc(mc) + '</p></div>';
    } else if (mc.oil_brent_usd || mc.gold_usd || mc.eur_usd || mc.us_10y_yield || mc.dxy_index) {
      html += '<div class="market-strip">';
      if (mc.oil_brent_usd) html += marketChip('Brent', '$' + mc.oil_brent_usd, mc.oil_change_pct);
      if (mc.gold_usd) html += marketChip('Gold', '$' + mc.gold_usd, mc.gold_change_pct);
      if (mc.eur_usd) html += marketChip('EUR/USD', mc.eur_usd.toFixed(4), mc.eur_usd_change_pct);
      if (mc.us_10y_yield) html += marketChip('US 10Y', mc.us_10y_yield.toFixed(2) + '%', mc.us_10y_change_bps);
      if (mc.dxy_index) html += marketChip('DXY', mc.dxy_index.toFixed(1), mc.dxy_change_pct);
      html += '</div>';
    } else if (mc.summary || mc.notable_moves) {
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
    return html;
  }

  function renderTopStories(data) {
    var html = '';
    if (!data.top_stories || !data.top_stories.length) return html;
    html += '<div class="briefing-section"><h3>Top Stories</h3>';
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
    return html;
  }

  function renderRegionalRoundup(data) {
    var html = '';
    if (!data.regional_summaries) return html;
    html += '<div class="briefing-section"><h3>Regional Roundup</h3>';
    var regions = Object.keys(data.regional_summaries);
    html += '<div class="region-tabs" id="region-tabs">';
    regions.forEach(function(r, i) {
      var label = (typeof REGIONS !== 'undefined' && REGIONS[r]) ? REGIONS[r].label : r;
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
    return html;
  }

  function bindRegionTabs() {
    var tabsEl = document.getElementById('region-tabs');
    if (!tabsEl) return;
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

  /* ---- Article Detail Mode ---- */
  function renderArticle(art) {
    var html = '<div class="article">';

    // Back link
    html += '<a href="#briefing" class="article__back">&larr; Back to Briefing</a>';

    // Meta badges
    html += '<div class="article__meta">';
    if (art.severity) {
      html += '<span class="alert-badge ' + severityClass(art.severity) + '">' + esc(art.severity) + '</span>';
    }
    if (art.categories && art.categories.length) {
      art.categories.forEach(function(cat) {
        html += '<span class="article-card__category">' + esc(cat) + '</span>';
      });
    }
    html += '</div>';

    // Headline
    html += '<h1 class="article__headline">' + esc(art.headline) + '</h1>';
    if (art.subheadline) {
      html += '<p class="article__subheadline">' + esc(art.subheadline) + '</p>';
    }

    // Byline
    html += '<div class="article__byline">';
    html += '<span>' + formatDate(art.published_at) + '</span>';
    if (art.ai_generated) {
      html += '<span class="article__ai-badge">AI-Generated</span>';
    }
    html += '</div>';

    // Hero SVG
    if (art.hero_svg) {
      html += '<figure class="article__hero">';
      html += sanitizeSVG(art.hero_svg);
      if (art.hero_svg_alt) {
        html += '<figcaption class="article__hero-caption">' + esc(art.hero_svg_alt) + '</figcaption>';
      }
      html += '</figure>';
    }

    // Body sections
    html += '<div class="article__body">';
    if (art.body && art.body.length) {
      art.body.forEach(function(block) {
        if (block.type === 'lede') {
          html += '<p class="article__lede">' + esc(block.content) + '</p>';
        } else if (block.type === 'section') {
          if (block.heading) html += '<h2>' + esc(block.heading) + '</h2>';
          html += '<p>' + esc(block.content) + '</p>';
        }
      });
    }
    html += '</div>';

    // Countries
    if (art.countries_affected && art.countries_affected.length) {
      html += '<div class="article__countries">';
      html += '<span class="article__countries-label">Countries:</span> ';
      art.countries_affected.forEach(function(c) {
        html += '<span class="panel-sources__tag">' + esc(c) + '</span>';
      });
      html += '</div>';
    }

    // Sources
    if (art.sources && art.sources.length) {
      html += '<div class="article__sources">';
      html += '<h3>Sources</h3><ul>';
      art.sources.forEach(function(src) {
        if (src.url) {
          html += '<li><a href="' + esc(src.url) + '" target="_blank" rel="noopener noreferrer">' + esc(src.name) + '</a>';
        } else {
          html += '<li>' + esc(src.name);
        }
        if (src.accessed) html += ' <span class="article__source-date">(accessed ' + esc(src.accessed) + ')</span>';
        html += '</li>';
      });
      html += '</ul></div>';
    }

    // AI Disclaimer
    if (art.ai_disclaimer) {
      html += '<div class="article__disclaimer">' + esc(art.ai_disclaimer) + '</div>';
    }

    html += '</div>';
    containerEl.innerHTML = html;
    containerEl.scrollTop = 0;
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

  /* ---- Loading skeleton ---- */
  function showLoading() {
    containerEl.innerHTML = '<div class="panel-loading"><div class="skeleton" style="width:60%;height:24px;margin:16px auto"></div><div class="skeleton" style="width:80%;height:16px;margin:8px auto"></div></div>';
  }

  return {
    show: async function(el, params) {
      containerEl = el;
      params = params || {};

      if (params.articleId) {
        // Article detail mode
        if (lastMode === params.articleId) return;
        showLoading();
        try {
          var article = await DataLoader.getArticle(params.articleId);
          renderArticle(article);
          lastMode = params.articleId;
        } catch (err) {
          containerEl.innerHTML = '<div class="error-card"><h3 class="error-card__title">Article not found</h3><p>This article could not be loaded.</p><a href="#briefing">&larr; Back to Briefing</a></div>';
        }
      } else {
        // Listing mode
        if (lastMode === 'listing') return;
        showLoading();

        // Load briefing data (always needed for market context / fallback)
        try {
          briefingData = await DataLoader.getBriefing();
        } catch (e) {
          briefingData = null;
        }

        // Try loading article index
        try {
          var index = await DataLoader.getArticleIndex();
          var articles = index.articles || index;
          renderListing(Array.isArray(articles) ? articles : [], briefingData);
        } catch (e) {
          // No articles yet — fall back to briefing-only rendering
          if (briefingData) {
            renderListing(null, briefingData);
          } else {
            containerEl.innerHTML = '<div class="error-card"><h3 class="error-card__title">Briefing unavailable</h3><p>Weekly briefing data has not been generated yet.</p></div>';
          }
        }
        lastMode = 'listing';
      }
    },

    reset: function() {
      lastMode = null;
      briefingData = null;
    }
  };
})();
