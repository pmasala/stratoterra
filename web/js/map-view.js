/* ==========================================================================
   Stratoterra — Map View (Leaflet)
   ========================================================================== */

var MapView = (function() {
  var map = null;
  var geoLayer = null;
  var currentMetric = 'alert_severity';
  var currentOverlay = 'none';
  var selectedFeature = null;
  var summaryLookup = {};
  var onCountryClick = null;
  var legendEl = null;
  var chokeMarkers = [];
  var labelMarkers = [];

  function getStyle(feature) {
    var code = feature.properties.ISO_A3;
    var summary = summaryLookup[code];
    var fillColor = COUNTRY_STYLE.default.fillColor;

    if (summary && currentMetric && COLOR_SCALES[currentMetric]) {
      var value = Utils.getMetricValue(summary, currentMetric);
      if (value != null) {
        fillColor = COLOR_SCALES[currentMetric](value);
      }
    }

    // Dimmed if overlay is active and country not a member
    if (currentOverlay !== 'none' && OVERLAY_ENTITIES[currentOverlay]) {
      var members = OVERLAY_ENTITIES[currentOverlay].members;
      if (members.indexOf(code) === -1) {
        return Object.assign({}, COUNTRY_STYLE.default, {
          fillColor: fillColor,
          fillOpacity: COUNTRY_STYLE.dimmed.fillOpacity,
          opacity: COUNTRY_STYLE.dimmed.opacity
        });
      } else {
        return Object.assign({}, COUNTRY_STYLE.default, {
          fillColor: fillColor,
          weight: 2.5,
          color: OVERLAY_ENTITIES[currentOverlay].color,
          fillOpacity: 0.85
        });
      }
    }

    return Object.assign({}, COUNTRY_STYLE.default, { fillColor: fillColor });
  }

  function buildTooltipHTML(code) {
    var summary = summaryLookup[code];
    if (!summary) return '<div class="country-tooltip"><div class="country-tooltip__name">' + code + '</div><div style="color:var(--text-muted)">No data available</div></div>';

    var metricLabel = METRIC_CONFIG[currentMetric] ? METRIC_CONFIG[currentMetric].label : currentMetric;
    var metricValue = Utils.getMetricValue(summary, currentMetric);
    var formattedValue = Utils.formatMetricValue(metricValue, currentMetric);

    var html = '<div class="country-tooltip">';
    html += '<div class="country-tooltip__name">' + summary.name + '</div>';
    html += '<div class="country-tooltip__metric"><span class="country-tooltip__metric-label">' + metricLabel + '</span><span class="country-tooltip__metric-value">' + formattedValue + '</span></div>';

    if (summary.gdp_nominal_usd) {
      html += '<div class="country-tooltip__metric"><span class="country-tooltip__metric-label">GDP</span><span class="country-tooltip__metric-value">' + Utils.formatCurrency(summary.gdp_nominal_usd) + '</span></div>';
    }
    if (summary.investment_risk_score != null) {
      html += '<div class="country-tooltip__metric"><span class="country-tooltip__metric-label">Risk</span><span class="country-tooltip__metric-value">' + Utils.formatScore(summary.investment_risk_score) + '</span></div>';
    }
    if (summary.alert_count > 0) {
      var sevClass = 'alert-badge--' + (summary.max_alert_severity || 'watch');
      html += '<div style="margin-top:4px"><span class="alert-badge ' + sevClass + '">' + summary.alert_count + ' alert' + (summary.alert_count > 1 ? 's' : '') + '</span></div>';
    }
    html += '</div>';
    return html;
  }

  function onEachFeature(feature, layer) {
    var code = feature.properties.ISO_A3;

    layer.on('mouseover', function(e) {
      if (selectedFeature !== layer) {
        layer.setStyle(COUNTRY_STYLE.hover);
        layer.bringToFront();
      }
      layer.bindTooltip(buildTooltipHTML(code), { sticky: true, direction: 'auto' }).openTooltip(e.latlng);
    });

    layer.on('mouseout', function() {
      if (selectedFeature !== layer) {
        geoLayer.resetStyle(layer);
      }
      layer.closeTooltip();
    });

    layer.on('click', function() {
      // Deselect previous
      if (selectedFeature && selectedFeature !== layer) {
        geoLayer.resetStyle(selectedFeature);
      }
      selectedFeature = layer;
      layer.setStyle(COUNTRY_STYLE.selected);
      layer.bringToFront();

      // Zoom to country
      map.fitBounds(layer.getBounds(), { padding: [50, 50], maxZoom: 5 });

      if (onCountryClick) onCountryClick(code);
    });
  }

  function updateLegend() {
    if (!legendEl) return;
    var config = METRIC_CONFIG[currentMetric];
    if (!config) return;

    // Build gradient from color scale
    var stops = [];
    for (var i = 0; i <= 10; i++) {
      var t = i / 10;
      var min, max, val;
      switch(currentMetric) {
        case 'gdp_growth_trend': val = -5 + t * 15; break;
        case 'political_stability': val = t; break;
        case 'investment_risk': val = t; break;
        case 'military_spending_trend': val = -10 + t * 25; break;
        case 'alert_severity': val = t * 3; break;
        case 'economic_complexity': val = -2 + t * 4.5; break;
        case 'energy_independence': val = t; break;
        case 'trade_openness': val = t * 200; break;
        default: val = t;
      }
      stops.push(COLOR_SCALES[currentMetric](val));
    }

    legendEl.innerHTML = '<div class="color-legend__title">' + config.label + '</div>' +
      '<div class="color-legend__gradient" style="background:linear-gradient(to right,' + stops.join(',') + ')"></div>' +
      '<div class="color-legend__labels"><span>' + config.legendMin + '</span><span>' + config.legendMax + '</span></div>';
  }

  function deselectCountry() {
    if (selectedFeature) {
      geoLayer.resetStyle(selectedFeature);
      selectedFeature = null;
    }
  }

  return {
    async init(containerId, options) {
      options = options || {};
      onCountryClick = options.onCountryClick || null;

      // Create map
      map = L.map(containerId, {
        center: MAP_CONFIG.center,
        zoom: MAP_CONFIG.zoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom,
        maxBounds: MAP_CONFIG.maxBounds,
        maxBoundsViscosity: MAP_CONFIG.maxBoundsViscosity,
        zoomControl: true,
        attributionControl: true,
        worldCopyJump: true
      });

      // Add tile layer
      L.tileLayer(MAP_CONFIG.tileUrl, {
        attribution: MAP_CONFIG.tileAttribution,
        subdomains: 'abcd',
        maxZoom: MAP_CONFIG.maxZoom
      }).addTo(map);

      // Build summary lookup
      var summary = DataLoader.getSummary();
      if (Array.isArray(summary)) {
        summary.forEach(function(c) { summaryLookup[c.code] = c; });
      }

      // Load and render GeoJSON
      try {
        var response = await fetch(MAP_CONFIG.geojsonPath);
        var geojsonData = await response.json();

        geoLayer = L.geoJSON(geojsonData, {
          style: getStyle,
          onEachFeature: onEachFeature
        }).addTo(map);
      } catch (err) {
        console.error('[MapView] Failed to load GeoJSON:', err);
      }

      // Create legend
      legendEl = document.createElement('div');
      legendEl.className = 'color-legend';
      document.getElementById(containerId).appendChild(legendEl);
      updateLegend();

      return map;
    },

    setMetric(metricId) {
      if (!COLOR_SCALES[metricId]) return;
      currentMetric = metricId;
      if (geoLayer) {
        geoLayer.eachLayer(function(layer) {
          if (layer.feature) {
            layer.setStyle(getStyle(layer.feature));
          }
        });
      }
      // Re-apply selected style
      if (selectedFeature) {
        selectedFeature.setStyle(COUNTRY_STYLE.selected);
        selectedFeature.bringToFront();
      }
      updateLegend();
    },

    setOverlay(overlayId) {
      currentOverlay = overlayId;
      if (geoLayer) {
        geoLayer.eachLayer(function(layer) {
          if (layer.feature) {
            layer.setStyle(getStyle(layer.feature));
          }
        });
      }
      if (selectedFeature) {
        selectedFeature.setStyle(COUNTRY_STYLE.selected);
        selectedFeature.bringToFront();
      }
    },

    setSummaryData(summary) {
      summaryLookup = {};
      if (Array.isArray(summary)) {
        summary.forEach(function(c) { summaryLookup[c.code] = c; });
      }
    },

    deselectCountry: deselectCountry,

    getMap() { return map; },

    invalidateSize() {
      if (map) setTimeout(function() { map.invalidateSize(); }, 300);
    }
  };
})();
