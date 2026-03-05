/* ==========================================================================
   Stratoterra — Intel Overlays Module
   Renders 15 toggleable geopolitical intel layers on the Leaflet map.
   ========================================================================== */

var IntelOverlays = (function() {
  'use strict';

  var map = null;
  var LG = {};
  var panelEl = null;
  var cardEl = null;
  var initialized = false;

  var LAYER_IDS = [
    'flights','naval','airports','ports','chokepoints','cables',
    'bases','conflicts','missiles','nuclear',
    'power','pipelines','cyber','migration','sanctions'
  ];

  var DEFAULT_ON = ['flights','naval','airports','ports','bases','conflicts','power'];

  // Colour map
  var C = {
    amber:'#f0a500', red:'#d63031', green:'#00b894',
    blue:'#0984e3', teal:'#00cec9', purple:'#6c5ce7', orange:'#e17055'
  };
  var INTENSITY = { Critical:C.red, High:C.orange, Moderate:C.amber, Low:C.green };
  var FLIGHT_C  = { civilian:C.blue, military:C.red, surveillance:C.amber, diplomatic:C.purple };
  var NAVAL_C   = { carrier:C.teal, destroyer:C.blue, frigate:C.purple, submarine:C.red };

  /* ── Icon factories ──────────────────────────────────────── */
  function mkIcon(sym, bg, border, size) {
    size = size || 14;
    return L.divIcon({
      className:'',
      html:'<svg width="'+size+'" height="'+size+'" viewBox="0 0 '+size+' '+size+'" xmlns="http://www.w3.org/2000/svg">'+
        '<circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'"'+
        ' fill="'+bg+'" stroke="'+border+'" stroke-width="1.4"/>'+
        '<text x="'+(size/2)+'" y="'+(size*0.78)+'" text-anchor="middle"'+
        ' font-size="'+(size*0.6)+'" fill="'+border+'">'+sym+'</text></svg>',
      iconSize:[size,size], iconAnchor:[size/2,size/2]
    });
  }

  function mkFlag(flag) {
    return L.divIcon({
      className:'',
      html:'<span style="font-size:17px;line-height:1;cursor:pointer;filter:drop-shadow(0 1px 3px rgba(0,0,0,.8))">'+flag+'</span>',
      iconSize:[20,20], iconAnchor:[10,10]
    });
  }

  /* ── Detail card ─────────────────────────────────────────── */
  function showCard(type, name, rows) {
    var typeEl = document.getElementById('sc-type');
    var nameEl = document.getElementById('sc-name');
    var cont   = document.getElementById('sc-rows');
    if (!typeEl || !nameEl || !cont) return;

    typeEl.textContent = type;
    nameEl.textContent = name;
    cont.innerHTML = '';
    rows.forEach(function(r) {
      var k = r[0], v = r[1], cls = r[2] || '';
      cont.innerHTML += '<div class="sc-row">'+
        '<span class="sc-key">'+k+'</span>'+
        '<span class="sc-val '+cls+'">'+v+'</span></div>';
    });
    cardEl.style.display = 'block';
  }

  function hideCard() {
    if (cardEl) cardEl.style.display = 'none';
  }

  /* ── Escaped HTML helper ─────────────────────────────────── */
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  /* ── Per-layer renderers ─────────────────────────────────── */
  var renderers = {
    airports: function(features) {
      features.forEach(function(a) {
        var m = L.marker(a.ll, {icon: mkIcon('\u2708','rgba(9,132,227,.15)',C.blue,15)});
        m.on('click', function() { showCard('AIRPORT', a.name, [
          ['IATA code', a.code, 'hi'], ['Passenger traffic', a.traffic]
        ]); });
        m.bindTooltip('<b>'+esc(a.name)+'</b> \u00b7 '+esc(a.code), {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.airports.addLayer(m);
      });
    },

    ports: function(features) {
      features.forEach(function(p) {
        var m = L.marker(p.ll, {icon: mkIcon('\u2693','rgba(0,206,201,.12)',C.teal,15)});
        m.on('click', function() { showCard('STRATEGIC PORT', p.name, [
          ['Country', p.country], ['Capacity', p.cap]
        ]); });
        m.bindTooltip('<b>'+esc(p.name)+'</b>', {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.ports.addLayer(m);
      });
    },

    bases: function(features) {
      features.forEach(function(b) {
        var m = L.marker(b.ll, {icon: mkFlag(b.flag)});
        m.on('click', function() { showCard('MILITARY BASE', b.name, [
          ['Nation', b.country], ['Facility', b.type], ['Personnel', b.size]
        ]); });
        m.bindTooltip('<b>'+esc(b.name)+'</b><br>'+b.flag+' '+esc(b.country)+' \u00b7 '+esc(b.type),
          {className:'st-tip',direction:'top',offset:[0,-6]});
        LG.bases.addLayer(m);
      });
    },

    conflicts: function(features) {
      features.forEach(function(c) {
        var col = INTENSITY[c.intensity] || C.red;
        var r = ({Critical:220, High:160, Moderate:100, Low:65})[c.intensity] * 1000;
        var pulse = L.circle(c.ll, {radius:r*1.6, color:col, fillColor:col, fillOpacity:.04, weight:1, dashArray:'5 4'});
        var core  = L.circle(c.ll, {radius:r, color:col, fillColor:col, fillOpacity:.13, weight:1.5});
        var lbl   = L.marker(c.ll, {icon: L.divIcon({
          className:'',
          html:'<div style="color:'+col+';font-family:\'Outfit\',sans-serif;font-size:11px;font-weight:700;white-space:nowrap;text-shadow:0 1px 3px #000;letter-spacing:.5px">'+esc(c.name)+'</div>',
          iconAnchor:[-6,4]
        })});
        [pulse,core].forEach(function(el) {
          el.on('click', function() { showCard('CONFLICT ZONE', c.name, [
            ['Intensity', c.intensity, c.intensity==='Critical'?'danger': c.intensity==='High'?'warn':'ok'],
            ['Since', c.since], ['Type', c.type], ['Casualties', c.casualties, 'danger']
          ]); });
        });
        LG.conflicts.addLayer(pulse);
        LG.conflicts.addLayer(core);
        LG.conflicts.addLayer(lbl);
      });
    },

    power: function(features) {
      features.forEach(function(p) {
        var col = p.type==='Nuclear'?C.orange : p.type==='Gas'?C.purple : '#636e72';
        var sym = p.type==='Nuclear'?'\u2622':'\u26a1';
        var m = L.marker(p.ll, {icon: mkIcon(sym, col+'22', col, 15)});
        m.on('click', function() { showCard('POWER STATION', p.name, [
          ['Type', p.type, p.type==='Nuclear'?'warn':''],
          ['Output', p.mw ? p.mw.toLocaleString()+' MW' : 'Decommissioned', 'hi'],
          ['Country', p.country]
        ]); });
        m.bindTooltip('<b>'+esc(p.name)+'</b><br>'+esc(p.type)+' \u00b7 '+(p.mw||0)+' MW',
          {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.power.addLayer(m);
      });
    },

    nuclear: function(features) {
      features.forEach(function(n) {
        var m = L.marker(n.ll, {icon: mkIcon('\u2622','rgba(225,112,85,.15)',C.orange,16)});
        m.on('click', function() { showCard('NUCLEAR SITE \u2622', n.name, [
          ['Type', n.type, 'warn'], ['Country', n.country]
        ]); });
        m.bindTooltip('<b>'+esc(n.name)+'</b><br>\u2622 '+esc(n.type)+' \u00b7 '+esc(n.country),
          {className:'st-tip',direction:'top',offset:[0,-5]});
        LG.nuclear.addLayer(m);
      });
    },

    missiles: function(features) {
      features.forEach(function(m) {
        var ring = L.circle(m.ll, {
          radius: m.range*1000,
          color:C.red, fillColor:C.red, fillOpacity:.04,
          weight:1, dashArray:'4 5'
        });
        var pin = L.marker(m.ll, {icon: L.divIcon({
          className:'',
          html:'<div style="font-size:15px;filter:drop-shadow(0 0 5px '+C.red+')">\ud83d\ude80</div>',
          iconSize:[18,18], iconAnchor:[9,9]
        })});
        ring.bindTooltip('<b>'+esc(m.name)+'</b><br>Range: '+m.range.toLocaleString()+' km',
          {className:'st-tip',direction:'top'});
        pin.on('click', function() { showCard('MISSILE COVERAGE', m.name, [
          ['System', m.system], ['Range', m.range.toLocaleString()+' km', 'danger'], ['Country', m.country]
        ]); });
        LG.missiles.addLayer(ring);
        LG.missiles.addLayer(pin);
      });
    },

    chokepoints: function(features) {
      features.forEach(function(c) {
        var col = INTENSITY[c.risk] || C.orange;
        var m = L.marker(c.ll, {icon: L.divIcon({
          className:'',
          html:'<svg width="20" height="18" viewBox="0 0 20 18" xmlns="http://www.w3.org/2000/svg">'+
            '<polygon points="10,1 19,17 1,17" fill="'+col+'22" stroke="'+col+'" stroke-width="1.6"/>'+
            '<text x="10" y="14" text-anchor="middle" font-size="9" fill="'+col+'" font-weight="bold">!</text></svg>',
          iconSize:[20,18], iconAnchor:[10,9]
        })});
        m.on('click', function() { showCard('SEA CHOKEPOINT', c.name, [
          ['Daily flow', c.flow, 'hi'],
          ['Risk level', c.risk, c.risk==='Critical'?'danger':c.risk==='High'?'warn':'ok']
        ]); });
        m.bindTooltip('<b>'+esc(c.name)+'</b><br>'+esc(c.flow), {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.chokepoints.addLayer(m);
      });
    },

    cables: function(features) {
      features.forEach(function(c) {
        var pl = L.polyline(c.path, {color:C.purple, weight:2, opacity:.6, dashArray:'8 5'});
        pl.on('click', function() { showCard('SUBMARINE CABLE', c.name, [['Operator', c.owner], ['Status', 'Active']]); });
        pl.bindTooltip('<b>'+esc(c.name)+'</b><br>'+esc(c.owner), {className:'st-tip',direction:'top'});
        LG.cables.addLayer(pl);
      });
    },

    pipelines: function(features) {
      features.forEach(function(p) {
        var pl = L.polyline(p.path, {color:C.orange, weight:2.5, opacity:.65, dashArray:'10 5'});
        pl.on('click', function() { showCard('PIPELINE', p.name, [
          ['Product', p.prod, 'hi'], ['From', p.from], ['To', p.to]
        ]); });
        pl.bindTooltip('<b>'+esc(p.name)+'</b><br>'+esc(p.prod)+': '+esc(p.from)+' \u2192 '+esc(p.to),
          {className:'st-tip',direction:'top'});
        LG.pipelines.addLayer(pl);
      });
    },

    flights: function(features) {
      features.forEach(function(f) {
        var col = FLIGHT_C[f.type] || C.blue;
        var pl = L.polyline(f.path, {color:col, weight:1.5, opacity:.65, dashArray:'7 5'});
        var mid = [(f.path[0][0]+f.path[1][0])/2, (f.path[0][1]+f.path[1][1])/2];
        var lbl = L.marker(mid, {icon: L.divIcon({
          className:'',
          html:'<div style="color:'+col+';font-family:\'JetBrains Mono\',monospace;font-size:9.5px;white-space:nowrap;text-shadow:0 1px 2px #000">\u2708 '+esc(f.label)+'</div>',
          iconAnchor:[-4,5]
        })});
        pl.on('click', function() { showCard('FLIGHT TRAJECTORY', f.label, [['Type', f.type.toUpperCase()]]); });
        LG.flights.addLayer(pl);
        LG.flights.addLayer(lbl);
      });
    },

    naval: function(features) {
      features.forEach(function(n) {
        var col = NAVAL_C[n.type] || C.teal;
        var pl = L.polyline(n.path, {color:col, weight:2, opacity:.65, dashArray:'10 6'});
        var mi = Math.floor(n.path.length / 2);
        var mp = n.path[mi];
        var lbl = L.marker(mp, {icon: L.divIcon({
          className:'',
          html:'<div style="color:'+col+';font-family:\'JetBrains Mono\',monospace;font-size:9.5px;white-space:nowrap;text-shadow:0 1px 2px #000">\u2693 '+esc(n.label)+'</div>',
          iconAnchor:[-4,4]
        })});
        pl.on('click', function() { showCard('NAVAL ROUTE', n.label, [['Vessel class', n.type.toUpperCase(), 'hi'], ['Status', 'Active']]); });
        LG.naval.addLayer(pl);
        LG.naval.addLayer(lbl);
      });
    },

    migration: function(features) {
      features.forEach(function(m) {
        var pl = L.polyline(m.path, {color:C.orange, weight:2.5, opacity:.5, dashArray:'5 8'});
        pl.on('click', function() { showCard('MIGRATION CORRIDOR', m.label, [['Volume', m.vol, 'warn'], ['Status', 'Ongoing']]); });
        pl.bindTooltip('<b>'+esc(m.label)+'</b><br>'+esc(m.vol), {className:'st-tip',direction:'top'});
        LG.migration.addLayer(pl);
      });
    },

    cyber: function(features) {
      features.forEach(function(c) {
        var col = ({Critical:C.red, High:C.orange, Moderate:C.amber, Classified:C.blue})[c.sev] || C.purple;
        var m = L.marker(c.ll, {icon: L.divIcon({
          className:'',
          html:'<svg width="14" height="14" viewBox="0 0 14 14" xmlns="http://www.w3.org/2000/svg">'+
            '<rect x="1" y="1" width="12" height="12" rx="2" fill="'+col+'22" stroke="'+col+'" stroke-width="1.3"/>'+
            '<text x="7" y="11" text-anchor="middle" font-size="9" fill="'+col+'">\u2328</text></svg>',
          iconSize:[14,14], iconAnchor:[7,7]
        })});
        m.on('click', function() { showCard('CYBER OPERATIONS', c.name, [
          ['Origin', c.origin, 'hi'], ['Target', c.target],
          ['Severity', c.sev, c.sev==='Critical'?'danger':c.sev==='High'?'warn':'']
        ]); });
        m.bindTooltip('<b>'+esc(c.name)+'</b><br>Origin: '+esc(c.origin), {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.cyber.addLayer(m);
      });
    },

    sanctions: function(features) {
      features.forEach(function(s) {
        var m = L.marker(s.ll, {icon: mkIcon('\ud83d\udd12','rgba(214,48,49,.12)',C.red,14)});
        m.on('click', function() { showCard('ACTIVE SANCTIONS', s.name, [
          ['Issuing body', s.body], ['Type', s.type], ['In force since', s.since, 'warn']
        ]); });
        m.bindTooltip('<b>'+esc(s.name)+'</b><br>'+esc(s.body)+' \u00b7 Since '+esc(s.since),
          {className:'st-tip',direction:'top',offset:[0,-4]});
        LG.sanctions.addLayer(m);
      });
    }
  };

  /* ── Update badge counts in the panel ────────────────────── */
  function updateBadge(layerId, count) {
    var row = document.querySelector('.st-row[data-layer="'+layerId+'"]');
    if (!row) return;
    var badge = row.querySelector('.st-badge');
    if (badge) badge.textContent = count;
  }

  /* ── Fetch a single layer JSON ───────────────────────────── */
  function fetchLayer(layerId) {
    return DataLoader.getOverlayLayer(layerId)
      .then(function(data) {
        if (renderers[layerId] && data.features) {
          renderers[layerId](data.features);
          updateBadge(layerId, data.features.length);
        }
      });
  }

  /* ── Wire panel toggle logic ─────────────────────────────── */
  function wirePanel() {
    // Layer row toggles
    document.querySelectorAll('#st-layers .st-row').forEach(function(row) {
      var id = row.dataset.layer;
      if (!id || !LG[id]) return;

      // Set initial state: if NOT in default-on list, remove from map
      if (DEFAULT_ON.indexOf(id) === -1) {
        row.classList.remove('on');
      } else {
        row.classList.add('on');
        LG[id].addTo(map);
      }

      row.addEventListener('click', function(e) {
        e.stopPropagation();
        var on = row.classList.toggle('on');
        if (on) { LG[id].addTo(map); } else { LG[id].remove(); }
      });
    });

    // Collapse/expand header
    var head = document.getElementById('st-layers-head');
    if (head) {
      head.addEventListener('click', function() {
        head.classList.toggle('collapsed');
        var body = document.getElementById('st-layers-body');
        if (body) body.classList.toggle('hidden');
      });
    }

    // Card close button
    var closeBtn = document.getElementById('st-card-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() { hideCard(); });
    }

    // Click map to close card
    map.on('click', function() { hideCard(); });
  }

  /* ── Public API ──────────────────────────────────────────── */
  return {
    init: function() {
      map = MapView.getMap();
      if (!map) {
        console.error('[IntelOverlays] No map instance available');
        return Promise.resolve();
      }

      panelEl = document.getElementById('st-layers');
      cardEl  = document.getElementById('st-card');

      // Create layer groups
      LAYER_IDS.forEach(function(id) {
        LG[id] = L.layerGroup();
      });

      // Fetch all layers
      var promises = LAYER_IDS.map(function(id) {
        return fetchLayer(id).catch(function(err) {
          console.warn('[IntelOverlays] Failed to load layer:', id, err);
        });
      });

      return Promise.allSettled
        ? Promise.allSettled(promises).then(function() { wirePanel(); initialized = true; })
        : Promise.all(promises.map(function(p) {
            return p.then(function(v) { return {status:'fulfilled',value:v}; },
                          function(e) { return {status:'rejected',reason:e}; });
          })).then(function() { wirePanel(); initialized = true; });
    },

    show: function() {
      if (panelEl) panelEl.style.display = '';
      if (cardEl) cardEl.style.display = cardEl.dataset.wasOpen === 'true' ? 'block' : 'none';
    },

    hide: function() {
      if (cardEl) {
        cardEl.dataset.wasOpen = cardEl.style.display === 'block' ? 'true' : 'false';
        cardEl.style.display = 'none';
      }
      if (panelEl) panelEl.style.display = 'none';
    }
  };
})();
