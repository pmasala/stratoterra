/* ==========================================================================
   Stratoterra — Main Application (Router + Initialization)
   ========================================================================== */

(function() {
  'use strict';

  var views = {
    map: { containerId: 'map-container', init: false },
    briefing: { containerId: 'briefing-view', init: false },
    alerts: { containerId: 'alerts-view', init: false },
    rankings: { containerId: 'rankings-view', init: false },
    relations: { containerId: 'relations-view', init: false },
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
      // Close country panel when leaving map
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
        AlertDashboard.show(el);
        break;
      case 'rankings':
        RankingsView.show(el);
        break;
      case 'relations':
        RelationExplorer.show(el, params);
        break;
      case 'compare':
        ComparisonTool.show(el);
        break;
    }
  }

  document.addEventListener('DOMContentLoaded', async function() {
    // Initialize data loader
    await DataLoader.init();

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
      // Escape closes panel
      if (e.key === 'Escape') {
        if (CountryPanel.isOpen()) {
          CountryPanel.close();
          return;
        }
      }

      // Don't handle shortcuts when typing in inputs
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

      // Number shortcuts for views
      if (e.key === '1') window.location.hash = '#map';
      if (e.key === '2') window.location.hash = '#briefing';
      if (e.key === '3') window.location.hash = '#alerts';
      if (e.key === '4') window.location.hash = '#rankings';
      if (e.key === '5') window.location.hash = '#relations';
      if (e.key === '6') window.location.hash = '#compare';

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
      if (summary.length > 0 && summary[0].last_updated) {
        dateEl.textContent = Utils.formatDate(summary[0].last_updated);
      } else {
        dateEl.textContent = 'Not yet available';
      }
    }

    console.log('[Stratoterra] Initialized. Countries loaded:', DataLoader.getSummary().length);
  });
})();
