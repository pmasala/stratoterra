/* ==========================================================================
   Stratoterra — Alert Dashboard
   Shows only the most recent day's alerts, with manga-style hero illustration.
   ========================================================================== */

var AlertDashboard = (function() {
  var containerEl = null;
  var loaded = false;
  var allAlerts = [];
  var filterRegion = 'all';
  var filterType = 'all';
  var globalIdx = 0;

  /* ── Date helpers ───────────────────────────────────────── */
  function dateOf(a) {
    return (a.last_updated || a.first_triggered || '').slice(0, 10);
  }

  function latestDate(alerts) {
    var d = '';
    alerts.forEach(function(a) { var ad = dateOf(a); if (ad > d) d = ad; });
    return d;
  }

  function filterCurrentDay(alerts) {
    var today = latestDate(alerts);
    if (!today) return alerts;
    return alerts.filter(function(a) { return dateOf(a) === today; });
  }

  /* ── Text helpers ───────────────────────────────────────── */
  function esc(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  function wrapText(text, maxLen) {
    var words = text.split(' ');
    var lines = [];
    var cur = '';
    words.forEach(function(w) {
      if ((cur + ' ' + w).length > maxLen && cur) { lines.push(cur); cur = w; }
      else { cur = cur ? cur + ' ' + w : w; }
    });
    if (cur) lines.push(cur);
    return lines.slice(0, 3);
  }

  /* ── Manga-style hero SVG ───────────────────────────────── */
  function buildMangaHero(alert) {
    var title = (alert.title || alert.headline || 'ALERT').toUpperCase();
    var countries = (alert.countries || (alert.country_code ? [alert.country_code] : []));
    var sev = alert.severity || 'critical';
    var sevColor = sev === 'critical' ? '#ff1744' : sev === 'warning' ? '#ffab40' : '#448aff';
    var sevLabel = sev.toUpperCase();

    var lines = wrapText(title, 48);
    var titleY = 140 - (lines.length - 1) * 16;

    // Speed lines radiating from center
    var speed = '';
    for (var i = 0; i < 36; i++) {
      var a = i * 10 * Math.PI / 180;
      var r0 = 55 + (i % 3) * 25;
      var x1 = 450 + Math.cos(a) * r0, y1 = 140 + Math.sin(a) * r0;
      var x2 = 450 + Math.cos(a) * 520, y2 = 140 + Math.sin(a) * 520;
      speed += '<line x1="'+Math.round(x1)+'" y1="'+Math.round(y1)+
        '" x2="'+Math.round(x2)+'" y2="'+Math.round(y2)+
        '" stroke="#fff" stroke-width="'+(0.5+i%4*0.6).toFixed(1)+
        '" opacity="'+(0.03+i%5*0.02).toFixed(2)+'"/>';
    }

    // Title tspans
    var tspans = lines.map(function(l, i) {
      return '<tspan x="450" dy="'+(i === 0 ? 0 : 32)+'">' + esc(l) + '</tspan>';
    }).join('');

    var svg =
      '<svg viewBox="0 0 900 280" xmlns="http://www.w3.org/2000/svg">' +
      '<rect width="900" height="280" fill="#0B1120"/>' +
      // Halftone dots
      '<defs><pattern id="ht" width="6" height="6" patternUnits="userSpaceOnUse">' +
      '<circle cx="3" cy="3" r="0.7" fill="#fff" opacity="0.05"/></pattern></defs>' +
      '<rect width="900" height="280" fill="url(#ht)"/>' +
      // Speed lines
      '<g>' + speed + '</g>' +
      // Impact burst
      '<polygon points="450,35 475,108 548,65 495,128 570,140 495,155 548,215 475,172 450,245 425,172 352,215 405,155 330,140 405,128 352,65 425,108" ' +
      'fill="'+sevColor+'" opacity="0.1"/>' +
      // Outer panel frame
      '<rect x="12" y="8" width="876" height="264" fill="none" stroke="#fff" stroke-width="3.5"/>' +
      // Inner accent frame
      '<rect x="20" y="16" width="860" height="248" fill="none" stroke="'+sevColor+'" stroke-width="1" opacity="0.4"/>' +
      // Diagonal corner accents (manga panel feel)
      '<line x1="12" y1="8" x2="40" y2="8" stroke="'+sevColor+'" stroke-width="5"/>' +
      '<line x1="12" y1="8" x2="12" y2="36" stroke="'+sevColor+'" stroke-width="5"/>' +
      '<line x1="888" y1="272" x2="860" y2="272" stroke="'+sevColor+'" stroke-width="5"/>' +
      '<line x1="888" y1="272" x2="888" y2="244" stroke="'+sevColor+'" stroke-width="5"/>' +
      // Severity badge (tilted)
      '<g transform="translate(450,40) rotate(-2)">' +
      '<rect x="-72" y="-15" width="144" height="30" rx="2" fill="'+sevColor+'"/>' +
      '<text x="0" y="6" text-anchor="middle" fill="#fff" font-size="14" font-weight="800" ' +
      'font-family="Outfit,sans-serif" letter-spacing="3">' + esc(sevLabel) + '</text></g>' +
      // Headline
      '<text x="450" y="'+titleY+'" text-anchor="middle" fill="#F1F5F9" font-size="22" ' +
      'font-weight="700" font-family="Outfit,sans-serif" letter-spacing="0.5">' + tspans + '</text>' +
      // Countries
      '<text x="450" y="240" text-anchor="middle" fill="#E8C547" font-size="13" ' +
      'font-family="JetBrains Mono,monospace" letter-spacing="1.5">' + esc(countries.join(' \u00b7 ')) + '</text>' +
      '</svg>';

    return '<div class="alert-manga-hero">' + svg + '</div>';
  }

  /* ── Render ─────────────────────────────────────────────── */
  function render() {
    var filtered = allAlerts.filter(function(a) {
      if (filterRegion !== 'all') {
        var alertRegion = a.region;
        if (!alertRegion) {
          var codes = a.countries || (a.country_code ? [a.country_code] : []);
          if (codes.length > 0) alertRegion = Utils.getCountryRegion(codes[0]);
        }
        if (alertRegion !== filterRegion) return false;
      }
      if (filterType !== 'all' && a.type !== filterType) return false;
      return true;
    });

    var critical = filtered.filter(function(a) { return a.severity === 'critical'; });
    var warning = filtered.filter(function(a) { return a.severity === 'warning'; });
    var watch = filtered.filter(function(a) { return a.severity === 'watch'; });

    var html = '<div class="alerts-dashboard">';

    // Manga hero for the most important alert
    var heroAlert = critical[0] || warning[0];
    if (heroAlert) {
      html += buildMangaHero(heroAlert);
    }

    html += '<h2>Alert Dashboard</h2>';

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
    globalIdx = 0;
    if (critical.length) html += renderAlertSection('Critical', critical, 'critical');
    if (warning.length) html += renderAlertSection('Warning', warning, 'warning');
    if (watch.length) html += renderAlertSection('Watch', watch, 'watch');
    if (filtered.length === 0) {
      html += '<div class="panel-no-data"><p>No alerts for today.</p></div>';
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
      var alertTitle = a.title || a.headline || '';
      var alertBody = a.description || a.details || a.summary || '';
      var alertType = a.type || a.trigger || '';
      var alertCountries = a.countries || (a.country_code ? [a.country_code] : []);
      html += '<div class="alert-card alert-card--' + severity + '" data-alert-index="' + (globalIdx++) + '">';
      html += '<div class="alert-card__header">';
      html += '<span class="alert-badge alert-badge--' + severity + '">' + severity + '</span>';
      if (alertType) html += '<span class="alert-card__type">' + esc(Utils.formatLabel(alertType)) + '</span>';
      html += '</div>';
      html += '<h4 class="alert-card__title">' + esc(alertTitle) + '</h4>';
      html += '<p class="alert-card__body">' + esc(alertBody) + '</p>';
      if (alertCountries.length) {
        html += '<div class="alert-card__countries">';
        alertCountries.forEach(function(c) {
          html += '<span class="panel-sources__tag">' + esc(Utils.resolveCountryName(c)) + '</span>';
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

  return {
    show: async function(el, params) {
      containerEl = el;
      if (loaded) {
        render();
        if (params && params.alertIndex != null) {
          setTimeout(function() { AlertDashboard.scrollToAlert(params.alertIndex); }, 200);
        }
        return;
      }

      containerEl.innerHTML = '<div class="panel-loading"><div class="skeleton" style="width:60%;height:24px;margin:16px auto"></div></div>';

      try {
        var data = await DataLoader.getAlerts();
        var raw = data.alerts || data || [];
        // Filter out resolved alerts, then keep only current day
        var active = raw.filter(function(a) {
          return a.severity && a.status !== 'resolved';
        });
        allAlerts = filterCurrentDay(active);
        loaded = true;
        render();
        if (params && params.alertIndex != null) {
          setTimeout(function() { AlertDashboard.scrollToAlert(params.alertIndex); }, 200);
        }
      } catch (err) {
        containerEl.innerHTML = '<div class="error-card"><h3 class="error-card__title">Alerts unavailable</h3><p>Alert data has not been generated yet.</p></div>';
      }
    },

    scrollToAlert: function(index) {
      var card = containerEl && containerEl.querySelector('[data-alert-index="' + index + '"]');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    reset: function() {
      loaded = false;
      allAlerts = [];
    }
  };
})();
