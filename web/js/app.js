/* ==========================================================================
   Stratoterra — Main Application (Router + Initialization)
   ========================================================================== */

(function() {
  'use strict';

  /* --- Alert Ticker — Primary (critical/warning, rotating) + Secondary (watch, marquee) --- */
  var AlertTicker = (function() {
    var tickerEl, primaryEl, tagEl, tagDotEl, tagLabelEl, contentEl, headlineEl, timestampEl;
    var secondaryEl, scrollTrackEl, appEl;
    var initialized = false;

    var criticalQueue = [];
    var warningQueue  = [];
    var watchItems    = [];

    var rotationTimer = null;
    var currentAlert  = null;

    function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
    function pad(n) { return String(n).padStart(2, '0'); }
    function utcTime() {
      var n = new Date();
      return pad(n.getUTCHours()) + ':' + pad(n.getUTCMinutes()) + ' UTC';
    }

    function applyAlert(alert, severity) {
      var isCritical = severity === 'critical';
      tagEl.className         = 'ticker-tag ticker-tag--' + severity;
      tagLabelEl.textContent  = severity.toUpperCase();
      tagDotEl.className      = 'ticker-tag__dot' + (isCritical ? '' : ' hidden');
      contentEl.className     = 'ticker-content ticker-content--' + severity;
      headlineEl.textContent  = alert.title.toUpperCase();
      timestampEl.textContent = utcTime();
      currentAlert = alert;
    }

    function scheduleCycle() {
      rotationTimer = setTimeout(cyclePrimary, 30000);
    }

    function cyclePrimary() {
      rotationTimer = null;
      var nextAlert, nextSev;

      if (criticalQueue.length > 0) {
        nextAlert = criticalQueue[0];
        criticalQueue.push(criticalQueue.shift()); // rotate
        nextSev = 'critical';
      } else if (warningQueue.length > 0) {
        nextAlert = warningQueue[0];
        warningQueue.push(warningQueue.shift());
        nextSev = 'warning';
      } else {
        primaryEl.classList.remove('active');
        appEl.classList.remove('ticker-primary-on');
        currentAlert = null;
        return;
      }

      if (currentAlert) {
        // Crossfade: fade out → swap content → fade in
        contentEl.style.transition = 'opacity 0.4s';
        contentEl.style.opacity    = '0';
        var captured = { alert: nextAlert, sev: nextSev };
        setTimeout(function() {
          applyAlert(captured.alert, captured.sev);
          contentEl.style.opacity = '1';
          setTimeout(function() { contentEl.style.transition = ''; }, 400);
          scheduleCycle();
        }, 400);
      } else {
        applyAlert(nextAlert, nextSev);
        primaryEl.classList.add('active');
        appEl.classList.add('ticker-primary-on');
        scheduleCycle();
      }
    }

    function buildWatchScroll() {
      var html = watchItems.map(function(a) {
        return '<span class="ticker-scroll-item" data-alert-index="' + a._globalIndex + '">' +
               esc(a.title.toUpperCase()) + '</span>' +
               '<span class="ticker-scroll-sep" aria-hidden="true">&#9670;</span>';
      }).join('');
      scrollTrackEl.innerHTML = html + html; // doubled for seamless loop
      scrollTrackEl.style.animationDuration = Math.max(45, watchItems.length * 8) + 's';
      secondaryEl.classList.add('active');
      appEl.classList.add('ticker-watch-on');
    }

    return {
      init: async function() {
        tickerEl      = document.getElementById('alert-ticker');
        primaryEl     = document.getElementById('ticker-primary');
        tagEl         = document.getElementById('ticker-tag');
        tagDotEl      = document.getElementById('ticker-tag-dot');
        tagLabelEl    = document.getElementById('ticker-tag-label');
        contentEl     = document.getElementById('ticker-content');
        headlineEl    = document.getElementById('ticker-headline');
        timestampEl   = document.getElementById('ticker-timestamp');
        secondaryEl   = document.getElementById('ticker-secondary');
        scrollTrackEl = document.getElementById('ticker-scroll-track');
        appEl         = document.getElementById('app');

        try {
          var data = await DataLoader.getAlerts();
          var allAlerts = Array.isArray(data) ? data : (data.alerts || []);

          allAlerts.forEach(function(a, i) {
            a._globalIndex = i;
            if      (a.severity === 'critical') criticalQueue.push(a);
            else if (a.severity === 'warning')  warningQueue.push(a);
            else if (a.severity === 'watch')    watchItems.push(a);
          });

          if (watchItems.length > 0) buildWatchScroll();
          if (criticalQueue.length > 0 || warningQueue.length > 0) cyclePrimary();

          // Reveal container if any bar is active
          if (watchItems.length > 0 || criticalQueue.length > 0 || warningQueue.length > 0) {
            tickerEl.classList.remove('hidden');
          }

          // Click: primary content → navigate to that alert
          contentEl.addEventListener('click', function() {
            if (!currentAlert) return;
            navigateTo('alerts', { alertIndex: currentAlert._globalIndex });
          });

          // Click: watch scroll item → navigate to that alert
          scrollTrackEl.addEventListener('click', function(e) {
            var item = e.target.closest('[data-alert-index]');
            if (!item) return;
            navigateTo('alerts', { alertIndex: parseInt(item.getAttribute('data-alert-index'), 10) });
          });

          // Keep UTC timestamp current
          setInterval(function() {
            if (currentAlert) timestampEl.textContent = utcTime();
          }, 60000);

          initialized = true;
        } catch(e) {}
      },

      hide: function() {
        if (!initialized) return;
        if (rotationTimer) { clearTimeout(rotationTimer); rotationTimer = null; }
        tickerEl.classList.add('hidden');
        appEl.classList.remove('ticker-watch-on');
        appEl.classList.remove('ticker-primary-on');
      },

      show: function() {
        if (!initialized) return;
        tickerEl.classList.remove('hidden');
        if (watchItems.length > 0)                    appEl.classList.add('ticker-watch-on');
        if (primaryEl.classList.contains('active')) {
          appEl.classList.add('ticker-primary-on');
          if (!rotationTimer) scheduleCycle();
        }
      }
    };
  })();

  var views = {
    map: { containerId: 'map-container', init: false },
    briefing: { containerId: 'briefing-view', init: false },
    alerts: { containerId: 'alerts-view', init: false },
    rankings: { containerId: 'rankings-view', init: false },
    compare: { containerId: 'compare-view', init: false }
  };

  var currentView = 'map';

  function parseHash() {
    var hash = window.location.hash.replace('#', '') || 'map';
    var parts = hash.split('?');
    var view = parts[0];
    var params = {};
    if (parts[1]) {
      parts[1].split('&').forEach(function(p) {
        var kv = p.split('=');
        params[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1] || '');
      });
    }
    return { view: view, params: params };
  }

  function navigateTo(viewName, params) {
    // Hide all view containers
    document.querySelectorAll('.view-container').forEach(function(el) {
      el.classList.remove('active');
    });

    // Handle map view specially (it's not a .view-container)
    var mapContainer = document.getElementById('map-container');
    var bottomBar = document.getElementById('bottom-bar');

    if (viewName === 'map') {
      mapContainer.style.display = '';
      bottomBar.style.display = '';
      if (MapView.getMap()) MapView.getMap().invalidateSize();
    } else {
      mapContainer.style.display = 'none';
      bottomBar.style.display = 'none';
      // Close panels when leaving map
      if (CountryPanel.isOpen()) CountryPanel.close();
    }

    // Show target view
    var viewConfig = views[viewName];
    if (viewConfig && viewName !== 'map') {
      var el = document.getElementById(viewConfig.containerId);
      if (el) {
        el.classList.add('active');
        showView(viewName, el, params);
      }
    }

    // Alert ticker visibility
    if (viewName === 'alerts') {
      AlertTicker.hide();
    } else {
      AlertTicker.show();
    }

    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(function(link) {
      link.classList.toggle('active', link.getAttribute('data-view') === viewName);
    });

    currentView = viewName;
  }

  function showView(viewName, el, params) {
    switch (viewName) {
      case 'briefing':
        BriefingView.show(el);
        break;
      case 'alerts':
        AlertDashboard.show(el, params);
        break;
      case 'rankings':
        RankingsView.show(el);
        break;
      case 'compare':
        ComparisonTool.show(el);
        break;
    }
  }

  document.addEventListener('DOMContentLoaded', async function() {
    // Initialize data loader
    await DataLoader.init();

    // Initialize alert ticker (fire-and-forget)
    AlertTicker.init();

    // Initialize country panel
    CountryPanel.init(document.getElementById('country-panel'));

    // Initialize map
    await MapView.init('map-container', {
      onCountryClick: function(code) {
        CountryPanel.open(code);
      }
    });

    // Initialize search
    Search.init(
      document.getElementById('search'),
      document.getElementById('search-dropdown'),
      function(code) {
        // Navigate to map and open country
        if (currentView !== 'map') {
          window.location.hash = '#map';
        }
        setTimeout(function() {
          CountryPanel.open(code);
        }, currentView !== 'map' ? 200 : 0);
      }
    );

    // Wire metric selector
    var metricSelect = document.getElementById('metric-select');
    if (metricSelect) {
      metricSelect.addEventListener('change', function() {
        MapView.setMetric(this.value);
      });
    }

    // Wire overlay selector
    var overlaySelect = document.getElementById('overlay-select');
    if (overlaySelect) {
      overlaySelect.addEventListener('change', function() {
        MapView.setOverlay(this.value);
      });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
      // Escape closes panels
      if (e.key === 'Escape') {
        if (CountryPanel.isOpen()) { CountryPanel.close(); return; }
      }

      // Don't handle shortcuts when typing in inputs
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

      // Number shortcuts for views
      if (e.key === '1') window.location.hash = '#map';
      if (e.key === '2') window.location.hash = '#briefing';
      if (e.key === '3') window.location.hash = '#alerts';
      if (e.key === '4') window.location.hash = '#rankings';
      if (e.key === '5') window.location.hash = '#compare';

      // / to focus search
      if (e.key === '/') {
        e.preventDefault();
        document.getElementById('search').focus();
      }
    });

    // Router: hash change
    window.addEventListener('hashchange', function() {
      var route = parseHash();
      navigateTo(route.view, route.params);
    });

    // Initial route
    var initialRoute = parseHash();
    if (initialRoute.view !== 'map') {
      navigateTo(initialRoute.view, initialRoute.params);
    }

    // Update last-updated date
    var dateEl = document.getElementById('last-updated-date');
    if (dateEl) {
      var summary = DataLoader.getSummary();
      var meta = DataLoader.getSummaryMeta();
      var lastDate = meta.generated_at || (summary.length > 0 && summary[0].last_updated);
      if (lastDate) {
        dateEl.textContent = Utils.formatDate(lastDate);
      } else {
        dateEl.textContent = 'Not yet available';
      }
    }

    console.log('[Stratoterra] Initialized. Countries loaded:', DataLoader.getSummary().length);
  });
})();
