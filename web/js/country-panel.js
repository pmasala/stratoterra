/* ==========================================================================
   Stratoterra — Country Detail Panel
   ========================================================================== */

var CountryPanel = (function() {
  var panelEl = null;
  var currentCode = null;
  var _isOpen = false;
  var activeTab = 'economy';

  var TAB_DEFS = [
    { id: 'endowments',   label: 'Endowments' },
    { id: 'institutions',  label: 'Institutions' },
    { id: 'economy',       label: 'Economy' },
    { id: 'military',      label: 'Military' },
    { id: 'relations',     label: 'Relations' },
    { id: 'derived',       label: 'Derived' }
  ];

  function renderPanel(code, detail, summary) {
    var name = detail ? detail.name : (summary ? summary.name : code);
    var html = '';

    // Header
    html += '<div class="panel-header">';
    html += '<button class="panel-header__back" id="panel-close-btn">← Back</button>';
    html += '<span class="panel-header__title">' + escH(name) + '</span>';
    html += '<button class="panel-header__close" id="panel-close-x">✕</button>';
    html += '</div>';

    if (!detail) {
      html += '<div class="panel-no-data">';
      html += '<div class="panel-no-data__icon">📊</div>';
      html += '<p>Detailed data not yet available for ' + escH(name) + '.</p>';
      if (summary) {
        html += renderSummaryFallback(summary);
      }
      html += '</div>';
      panelEl.innerHTML = html;
      bindCloseButtons();
      return;
    }

    // Executive Summary
    html += '<div class="panel-section">';
    html += '<div class="panel-section__title">Executive Summary</div>';
    html += '<div class="exec-summary">' + escH(detail.executive_summary || '') + '</div>';
    html += '</div>';

    // Key Changes
    if (detail.key_changes && detail.key_changes.length > 0) {
      html += '<div class="panel-section">';
      html += '<div class="panel-section__title">Key Changes</div>';
      html += '<ul class="key-changes">';
      detail.key_changes.forEach(function(change) {
        html += '<li>' + escH(change) + '</li>';
      });
      html += '</ul>';
      html += '</div>';
    }

    // Active Alerts
    if (detail.active_alerts && detail.active_alerts.length > 0) {
      html += '<div class="panel-section">';
      html += '<div class="panel-section__title">Active Alerts</div>';
      detail.active_alerts.forEach(function(alert) {
        html += '<div class="panel-alert">';
        html += '<div class="panel-alert__icon panel-alert__icon--' + (alert.severity || 'watch') + '"></div>';
        html += '<div class="panel-alert__content">';
        html += '<div class="panel-alert__title">' + escH(alert.title) + '</div>';
        html += '<div class="panel-alert__desc">' + escH(alert.description || '') + '</div>';
        html += '</div></div>';
      });
      html += '</div>';
    }

    // Layer Tabs
    html += '<div class="layer-tabs" id="layer-tabs">';
    TAB_DEFS.forEach(function(tab) {
      var cls = tab.id === activeTab ? 'layer-tab active' : 'layer-tab';
      html += '<button class="' + cls + '" data-tab="' + tab.id + '">' + tab.label + '</button>';
    });
    html += '</div>';

    // Tab content
    TAB_DEFS.forEach(function(tab) {
      var cls = tab.id === activeTab ? 'layer-content active' : 'layer-content';
      html += '<div class="' + cls + '" id="tab-' + tab.id + '">';
      html += renderLayerTab(tab.id, detail);
      html += '</div>';
    });

    // Outlook & Implications
    if (detail.outlook || detail.investor_implications) {
      html += '<div class="outlook-section">';
      if (detail.outlook) {
        html += '<h4>Outlook</h4><p>' + escH(detail.outlook) + '</p>';
      }
      if (detail.investor_implications) {
        html += '<h4>Investor Implications</h4><p>' + escH(detail.investor_implications) + '</p>';
      }
      html += '</div>';
    }

    // Narrative
    if (detail.narrative) {
      html += renderNarrative(detail.narrative);
    }

    // Data Sources Footer
    html += renderSourcesFooter(detail);

    panelEl.innerHTML = html;
    bindCloseButtons();
    bindTabs();
    bindExpandables();
  }

  // Unwrap {value, confidence, ...} objects to plain values
  function unwrapValue(obj) {
    if (obj && typeof obj === 'object' && 'value' in obj) return obj.value;
    return obj;
  }

  // Restructure flat pipeline data into the nested format expected by render functions
  function normalizeLayer(tabId, raw, detail) {
    if (!raw) return null;

    switch(tabId) {
      case 'endowments': return {
        demographics: {
          population: raw.population || raw.population_total,
          population_growth_pct: raw.population_growth_pct,
          median_age: raw.median_age,
          life_expectancy: raw.life_expectancy,
          human_development_index: raw.hdi
        }
      };

      case 'institutions': return {
        political_system: {
          regime_type: raw.regime_type,
          head_of_state: raw.head_of_state_name,
          head_of_state_title: raw.head_of_state_title,
          head_of_government: raw.head_of_government_name,
          next_election: raw.next_national_election_date
        },
        governance: {
          democracy_index: raw.democracy_index,
          freedom_score: raw.freedom_house_score,
          freedom_status: raw.freedom_house_status,
          press_freedom_rank: raw.press_freedom_index_rank,
          corruption_perceptions_index: raw.corruption_perception_index,
          rule_of_law_score: raw.wgi_rule_of_law,
          government_effectiveness: raw.wgi_government_effectiveness,
          regulatory_quality: raw.wgi_regulatory_quality,
          political_stability_index: raw.wgi_political_stability,
          voice_accountability: raw.wgi_voice_accountability,
          control_of_corruption: raw.wgi_control_of_corruption,
          fragile_states_index: raw.fragile_states_index
        }
      };

      case 'economy': {
        // Parse composite credit rating string
        var creditSP = null, creditMoodys = null;
        var cr = raw.sovereign_credit_rating;
        if (typeof cr === 'string') {
          var spMatch = cr.match(/S&P:\s*([^,]+)/);
          var mMatch = cr.match(/Moody's:\s*([^,]+)/);
          if (spMatch) creditSP = spMatch[1].trim();
          if (mMatch) creditMoodys = mMatch[1].trim();
        }

        var exportsUsd = raw.total_exports_usd;
        var importsUsd = raw.total_imports_usd;

        // Extract partner country codes from top_export_partners array
        var topPartners = null;
        if (raw.top_export_partners && Array.isArray(raw.top_export_partners)) {
          topPartners = raw.top_export_partners.map(function(p) { return p.country; });
        }

        return {
          macro: {
            gdp_nominal_usd: raw.gdp_nominal_usd,
            gdp_real_growth_pct: raw.gdp_real_growth_pct,
            gdp_per_capita_usd: raw.gdp_per_capita_usd,
            inflation_rate_pct: raw.inflation_cpi_pct,
            unemployment_rate_pct: raw.unemployment_rate_pct,
            debt_to_gdp_pct: raw.govt_debt_pct_gdp,
            current_account_gdp_pct: raw.current_account_pct_gdp,
            foreign_reserves_usd: raw.fx_reserves_usd
          },
          financial: {
            policy_rate_pct: raw.central_bank_policy_rate_pct,
            ten_year_yield_pct: raw.sovereign_bond_yield_10yr_pct,
            credit_rating_sp: creditSP,
            credit_rating_moodys: creditMoodys,
            fx_rate_per_usd: raw.exchange_rate_vs_usd
          },
          trade: {
            exports_usd: exportsUsd,
            imports_usd: importsUsd,
            trade_balance_usd: (exportsUsd != null && importsUsd != null) ? exportsUsd - importsUsd : null,
            trade_openness_pct: raw.trade_openness_pct,
            top_trade_partners: topPartners,
            avg_applied_tariff_pct: raw.avg_applied_tariff_pct,
            fta_count: detail && detail.layers && detail.layers.relations ? detail.layers.relations.fta_count : null,
            sanctions_status: detail && detail.layers && detail.layers.institutions ? detail.layers.institutions.under_international_sanctions : null
          }
        };
      }

      case 'military': {
        // Pull alliance_memberships from raw (may be an array directly)
        var alliances = raw.alliance_memberships;
        if (Array.isArray(alliances)) { /* already an array */ }
        else { alliances = null; }

        // Capabilities from top-level detail.military nested sub-objects (not in layers.military)
        var milDetail = detail ? detail.military : null;
        var tanks = unwrapValue(milDetail && milDetail.army && milDetail.army.main_battle_tanks);
        var aircraft = unwrapValue(milDetail && milDetail.air_force && milDetail.air_force.total_aircraft);
        var subs = unwrapValue(milDetail && milDetail.navy && milDetail.navy.submarines_total);
        var nukes = unwrapValue(milDetail && milDetail.nuclear && milDetail.nuclear.warheads_estimated);

        return {
          personnel: {
            active_military: raw.active_military_personnel,
            reserve_military: raw.reserve_military_personnel
          },
          spending: {
            defense_budget_usd: raw.defense_spending_usd || raw.military_expenditure_usd,
            defense_pct_gdp: raw.military_expenditure_pct_gdp,
            spending_trend: raw.military_expenditure_trend
          },
          capabilities: {
            tanks: tanks,
            aircraft: aircraft,
            naval_vessels: subs,
            nuclear_warheads: nukes
          },
          alliance_memberships: alliances
        };
      }

      case 'relations': {
        // Pull alliance_memberships from military layer
        var milLayer = detail && detail.layers ? detail.layers.military : null;
        var alliancesRel = milLayer ? milLayer.alliance_memberships : null;
        if (Array.isArray(alliancesRel)) { /* ok */ }
        else { alliancesRel = null; }

        return {
          alliance_memberships: alliancesRel,
          fta_count: raw.fta_count
        };
      }

      case 'derived': return {
        composite_power_index: raw.composite_national_power_index,
        energy_independence: raw.energy_independence_index,
        supply_chain_exposure: raw.supply_chain_chokepoint_exposure,
        vulnerability_index: raw.vulnerability_index,
        investment_risk_score: raw.investment_risk_score,
        resource_self_sufficiency_index: raw.resource_self_sufficiency_index,
        market_accessibility_score: raw.market_accessibility_score,
        political_risk_premium_bps: raw.political_risk_premium_bps
      };

      default: return raw;
    }
  }

  function renderLayerTab(tabId, detail) {
    var layers = detail.layers || {};
    var raw = layers[tabId];
    if (!raw) return '<div class="panel-no-data"><p>Data not available for this layer.</p></div>';

    var data = normalizeLayer(tabId, raw, detail);

    switch(tabId) {
      case 'endowments': return renderEndowments(data);
      case 'institutions': return renderInstitutions(data);
      case 'economy': return renderEconomy(data);
      case 'military': return renderMilitary(data);
      case 'relations': return renderRelations(data);
      case 'derived': return renderDerived(data);
      default: return '';
    }
  }

  function renderEndowments(data) {
    var html = '';
    // Natural Resources
    if (data.natural_resources) {
      var nr = data.natural_resources;
      html += '<div class="panel-section__title">Natural Resources</div>';
      if (nr.top_resources) {
        nr.top_resources.forEach(function(r) {
          html += factorCard(r.name, formatResourceValue(r), null, r.global_rank ? 'Global #' + r.global_rank : null, r.source, r.confidence);
        });
      }
      html += '<div class="factor-grid">';
      html += miniFactorCard('Arable Land', Utils.formatPercent(nr.arable_land_pct, 1));
      html += miniFactorCard('Freshwater', Utils.formatNumber(nr.freshwater_per_capita_m3) + ' m³/cap');
      html += miniFactorCard('Self-Sufficiency', Utils.formatScore(nr.resource_self_sufficiency));
      html += '</div>';
    }
    // Geography
    if (data.geography) {
      var g = data.geography;
      html += '<div class="panel-section__title" style="margin-top:16px">Geography</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Area', Utils.formatNumber(g.area_km2) + ' km²');
      html += miniFactorCard('Coastline', Utils.formatNumber(g.coastline_km) + ' km');
      html += miniFactorCard('Borders', g.borders_count);
      html += miniFactorCard('Terrain', g.terrain_type || '—');
      html += '</div>';
      if (g.strategic_position) {
        html += '<p style="font-size:12px;color:var(--text-secondary);margin-top:8px;padding:0 4px">' + escH(g.strategic_position) + '</p>';
      }
    }
    // Demographics
    if (data.demographics) {
      var d = data.demographics;
      html += '<div class="panel-section__title" style="margin-top:16px">Demographics</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Population', Utils.formatNumber(d.population));
      html += miniFactorCard('Growth', Utils.formatPercent(d.population_growth_pct, 1));
      html += miniFactorCard('Median Age', d.median_age);
      html += miniFactorCard('Urbanization', Utils.formatPercent(d.urbanization_pct, 0));
      html += miniFactorCard('Working Age', Utils.formatPercent(d.working_age_pct, 0));
      html += miniFactorCard('HDI', Utils.formatScore(d.human_development_index));
      html += miniFactorCard('Gini', d.gini_coefficient);
      html += miniFactorCard('Net Migration', d.net_migration_per_1000 + '/1K');
      html += '</div>';
    }
    return html;
  }

  function renderInstitutions(data) {
    var html = '';
    if (data.political_system) {
      var ps = data.political_system;
      html += '<div class="panel-section__title">Political System</div>';
      html += factorCard('Regime Type', ps.regime_type, null, null, ps.source, ps.confidence);
      html += '<div class="factor-grid">';
      html += miniFactorCard('Head of State', ps.head_of_state || '—');
      html += miniFactorCard('Head of Gov\'t', ps.head_of_government || '—');
      html += miniFactorCard('Legislature', ps.legislative_type || '—');
      html += miniFactorCard('Next Election', ps.next_election || '—');
      html += miniFactorCard('Years Since Change', ps.years_since_transition || '—');
      html += '</div>';
    }
    if (data.governance) {
      var g = data.governance;
      html += '<div class="panel-section__title" style="margin-top:16px">Governance Indicators</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Democracy Index', Utils.formatScore(g.democracy_index));
      html += miniFactorCard('Freedom Score', g.freedom_score);
      html += miniFactorCard('Freedom Status', g.freedom_status || '—');
      html += miniFactorCard('Press Freedom', '#' + g.press_freedom_rank);
      html += miniFactorCard('Corruption (CPI)', g.corruption_perceptions_index);
      html += miniFactorCard('Voice & Account.', Utils.formatScore(g.voice_accountability));
      html += miniFactorCard('Corruption Ctrl', Utils.formatScore(g.control_of_corruption));
      html += miniFactorCard('Rule of Law', Utils.formatScore(g.rule_of_law_score));
      html += miniFactorCard('Govt Effectiveness', Utils.formatScore(g.government_effectiveness));
      html += miniFactorCard('Regulatory Quality', Utils.formatScore(g.regulatory_quality));
      html += miniFactorCard('Political Stability', Utils.formatScore(g.political_stability_index));
      html += miniFactorCard('Fragile States', g.fragile_states_index != null ? g.fragile_states_index.toFixed(1) : '—');
      html += '</div>';
    }
    if (data.cultural) {
      var c = data.cultural;
      html += '<div class="panel-section__title" style="margin-top:16px">Cultural Dimensions</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Individualism', c.hofstede_individualism);
      html += miniFactorCard('Power Distance', c.hofstede_power_distance);
      html += miniFactorCard('Uncertainty Av.', c.hofstede_uncertainty_avoidance);
      html += miniFactorCard('Masculinity', c.hofstede_masculinity);
      html += miniFactorCard('Social Trust', Utils.formatScore(c.social_trust_index));
      html += '</div>';
    }
    return html;
  }

  function renderEconomy(data) {
    var html = '';
    if (data.macro) {
      var m = data.macro;
      html += '<div class="panel-section__title">Macroeconomic Indicators</div>';
      html += factorCard('GDP (Nominal)', Utils.formatCurrency(m.gdp_nominal_usd), m.trend ? m.trend.direction : null, null, m.source, m.confidence);

      // Trend/reasoning expandable
      if (m.trend) {
        html += renderReasoning(m.trend);
      }

      html += '<div class="factor-grid">';
      html += miniFactorCard('GDP Growth', Utils.formatPercent(m.gdp_real_growth_pct, 1));
      html += miniFactorCard('GDP/Capita', Utils.formatCurrency(m.gdp_per_capita_usd));
      html += miniFactorCard('Inflation', Utils.formatPercent(m.inflation_rate_pct, 1));
      html += miniFactorCard('Unemployment', Utils.formatPercent(m.unemployment_rate_pct, 1));
      html += miniFactorCard('Debt/GDP', Utils.formatPercent(m.debt_to_gdp_pct, 0));
      html += miniFactorCard('Fiscal Balance', Utils.formatPercent(m.fiscal_balance_gdp_pct, 1));
      html += miniFactorCard('Current Account', Utils.formatPercent(m.current_account_gdp_pct, 1));
      html += miniFactorCard('FX Reserves', Utils.formatCurrency(m.foreign_reserves_usd));
      html += '</div>';
    }
    if (data.financial) {
      var f = data.financial;
      html += '<div class="panel-section__title" style="margin-top:16px">Financial System</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Policy Rate', Utils.formatPercent(f.policy_rate_pct, 2));
      html += miniFactorCard('10Y Yield', Utils.formatPercent(f.ten_year_yield_pct, 2));
      html += miniFactorCard('Credit (S&P)', f.credit_rating_sp || '—');
      html += miniFactorCard('Credit (Moodys)', f.credit_rating_moodys || '—');
      html += miniFactorCard('Stock YTD', Utils.formatPercent(f.stock_market_ytd_pct, 1));
      html += miniFactorCard('Currency', f.currency_code || '—');
      html += miniFactorCard('FX vs USD', f.fx_rate_per_usd != null ? Utils.formatNumber(f.fx_rate_per_usd, 2) : '—');
      html += miniFactorCard('Banking Health', Utils.formatScore(f.banking_sector_health));
      html += '</div>';
    }
    if (data.trade) {
      var t = data.trade;
      html += '<div class="panel-section__title" style="margin-top:16px">Trade</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Exports', Utils.formatCurrency(t.exports_usd));
      html += miniFactorCard('Imports', Utils.formatCurrency(t.imports_usd));
      html += miniFactorCard('Balance', Utils.formatCurrency(t.trade_balance_usd));
      html += miniFactorCard('Openness', Utils.formatPercent(t.trade_openness_pct, 0));
      html += miniFactorCard('FTAs', t.fta_count != null ? t.fta_count : '—');
      html += miniFactorCard('Sanctions', t.sanctions_status === true ? 'Yes' : t.sanctions_status === false ? 'None' : (t.sanctions_status || '—'));
      html += miniFactorCard('Avg Tariff', Utils.formatPercent(t.avg_applied_tariff_pct, 1));
      html += '</div>';
      if (t.top_export_products && t.top_export_products.length) {
        html += '<p style="font-size:11px;color:var(--text-muted);margin-top:8px">Top exports: ' + t.top_export_products.join(', ') + '</p>';
      }
      if (t.top_trade_partners && t.top_trade_partners.length) {
        html += '<p style="font-size:11px;color:var(--text-muted);margin-top:4px">Top partners: ' + t.top_trade_partners.join(', ') + '</p>';
      }
    }
    return html;
  }

  function renderMilitary(data) {
    var html = '';
    if (data.personnel) {
      var p = data.personnel;
      html += '<div class="panel-section__title">Personnel</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Active Military', Utils.formatNumber(p.active_military));
      html += miniFactorCard('Reserve', Utils.formatNumber(p.reserve_military));
      html += miniFactorCard('Paramilitary', Utils.formatNumber(p.paramilitary));
      html += miniFactorCard('Conscription', p.conscription ? 'Yes' : 'No');
      html += '</div>';
    }
    if (data.spending) {
      var s = data.spending;
      html += '<div class="panel-section__title" style="margin-top:16px">Defense Spending</div>';
      html += factorCard('Defense Budget', Utils.formatCurrency(s.defense_budget_usd), s.spending_trend, Utils.formatPercent(s.defense_pct_gdp, 1) + ' of GDP', s.source, s.confidence);
      html += '<div class="factor-grid">';
      html += miniFactorCard('Arms Imports', Utils.formatCurrency(s.arms_imports_usd));
      html += miniFactorCard('Arms Exports', Utils.formatCurrency(s.arms_exports_usd));
      html += '</div>';
    }
    if (data.capabilities) {
      var c = data.capabilities;
      html += '<div class="panel-section__title" style="margin-top:16px">Capabilities</div>';
      html += '<div class="factor-grid">';
      html += miniFactorCard('Tanks', Utils.formatNumber(c.tanks));
      html += miniFactorCard('Aircraft', Utils.formatNumber(c.aircraft));
      html += miniFactorCard('Naval Vessels', Utils.formatNumber(c.naval_vessels));
      html += miniFactorCard('Nuclear', c.nuclear_warheads ? Utils.formatNumber(c.nuclear_warheads) + ' warheads' : 'None');
      html += miniFactorCard('Cyber Tier', c.cyber_capability_tier || '—');
      html += miniFactorCard('Space', c.space_capability ? 'Yes' : 'No');
      html += miniFactorCard('Power Projection', Utils.formatScore(c.power_projection_score));
      html += '</div>';
    }
    if (data.conflicts) {
      var co = data.conflicts;
      html += '<div class="panel-section__title" style="margin-top:16px">Conflicts & Incidents</div>';
      if (co.active_conflicts && co.active_conflicts.length > 0) {
        co.active_conflicts.forEach(function(conflict) {
          html += '<p style="font-size:12px;color:var(--alert-critical);margin-bottom:4px">⚠ ' + escH(typeof conflict === 'string' ? conflict : conflict.name || JSON.stringify(conflict)) + '</p>';
        });
      } else {
        html += '<p style="font-size:12px;color:var(--text-muted)">No active conflicts</p>';
      }
      if (co.recent_incidents && co.recent_incidents.length > 0) {
        html += '<p style="font-size:11px;color:var(--text-secondary);margin-top:8px">Recent: ' + co.recent_incidents.map(escH).join('; ') + '</p>';
      }
    }
    return html;
  }

  function renderRelations(data) {
    var html = '';
    if (data.top_partners && data.top_partners.length) {
      html += '<div class="panel-section__title">Top Partners</div>';
      data.top_partners.forEach(function(p) {
        var qualColor = getRelationColor(p.quality);
        html += '<div class="factor-card" style="display:flex;justify-content:space-between;align-items:center">';
        html += '<div>';
        html += '<span style="font-weight:600">' + escH(p.code) + '</span>';
        html += '<span style="font-size:11px;color:var(--text-muted);margin-left:8px">' + escH(p.type || '') + '</span>';
        html += '</div>';
        html += '<div style="display:flex;align-items:center;gap:8px">';
        html += '<div style="width:40px;height:6px;background:rgba(100,100,180,0.2);border-radius:3px;overflow:hidden"><div style="height:100%;width:' + Math.round(p.quality * 100) + '%;background:' + qualColor + ';border-radius:3px"></div></div>';
        html += '<span class="data-value" style="font-size:13px">' + Utils.formatScore(p.quality) + '</span>';
        html += '</div></div>';
      });
    }
    if (data.alliance_memberships) {
      html += '<div class="panel-section__title" style="margin-top:16px">Alliance Memberships</div>';
      html += '<div style="display:flex;flex-wrap:wrap;gap:4px">';
      data.alliance_memberships.forEach(function(a) {
        html += '<span class="panel-sources__tag" style="font-size:12px">' + escH(a) + '</span>';
      });
      html += '</div>';
    }
    if (data.diplomatic_reach_score != null) {
      html += '<div class="factor-grid" style="margin-top:12px">';
      html += miniFactorCard('Diplomatic Reach', Utils.formatScore(data.diplomatic_reach_score));
      html += miniFactorCard('UN Alignment (West)', Utils.formatScore(data.un_voting_alignment_west));
      html += '</div>';
    }
    return html;
  }

  function renderDerived(data) {
    var html = '<div class="panel-section__title">Composite Indices</div>';
    html += '<div class="factor-grid">';
    html += miniFactorCard('Composite Power', Utils.formatScore(data.composite_power_index));
    html += miniFactorCard('Economic Power', Utils.formatScore(data.economic_power));
    html += miniFactorCard('Military Power', Utils.formatScore(data.military_power));
    html += miniFactorCard('Technology', Utils.formatScore(data.technology_index));
    html += miniFactorCard('Soft Power', Utils.formatScore(data.soft_power_index));
    html += miniFactorCard('Diplomatic Influence', Utils.formatScore(data.diplomatic_influence));
    html += '</div>';
    html += '<div class="panel-section__title" style="margin-top:16px">Vulnerability & Risk</div>';
    html += '<div class="factor-grid">';
    html += miniFactorCard('Vulnerability', Utils.formatScore(data.vulnerability_index));
    html += miniFactorCard('Supply Chain Exposure', Utils.formatScore(data.supply_chain_exposure));
    html += miniFactorCard('Energy Independence', Utils.formatScore(data.energy_independence));
    html += miniFactorCard('Investment Risk', Utils.formatScore(data.investment_risk_score));
    html += '</div>';
    html += '<div class="panel-section__title" style="margin-top:16px">Development</div>';
    html += '<div class="factor-grid">';
    html += miniFactorCard('Economic Complexity', data.economic_complexity_index != null ? data.economic_complexity_index.toFixed(2) : '—');
    html += miniFactorCard('Innovation Index', Utils.formatScore(data.innovation_index));
    html += '</div>';
    return html;
  }

  function renderReasoning(trend) {
    var id = 'reasoning-' + Math.random().toString(36).substr(2, 6);
    var html = '<div class="reasoning-expand">';
    html += '<button class="reasoning-toggle" data-target="' + id + '">';
    html += '<span class="reasoning-toggle__arrow">▶</span> Show reasoning';
    html += '</button>';
    html += '<div class="reasoning-body" id="' + id + '">';
    if (trend.assessment) {
      html += '<div class="reasoning-body__assessment">' + escH(trend.assessment) + '</div>';
    }
    if (trend.evidence && trend.evidence.length) {
      html += '<ul class="reasoning-body__evidence">';
      trend.evidence.forEach(function(e) {
        html += '<li>' + escH(e) + '</li>';
      });
      html += '</ul>';
    }
    if (trend.counter_arguments && trend.counter_arguments.length) {
      html += '<div class="reasoning-body__counter">';
      html += '<div class="reasoning-body__counter-title">Counter-arguments</div>';
      html += '<ul class="reasoning-body__evidence reasoning-body__counter">';
      trend.counter_arguments.forEach(function(c) {
        html += '<li>' + escH(c) + '</li>';
      });
      html += '</ul></div>';
    }
    html += '</div></div>';
    return html;
  }

  function renderNarrative(narrative) {
    var html = '<div class="narrative-section">';
    html += '<div class="panel-section__title">Analysis</div>';
    if (narrative.ai_generated) {
      html += '<div class="ai-label">✦ AI-Generated Analysis</div>';
    }
    if (narrative.executive_overview) {
      html += '<p>' + escH(narrative.executive_overview) + '</p>';
    }
    if (narrative.key_developments) {
      html += '<h4>Key Developments</h4><p>' + escH(narrative.key_developments) + '</p>';
    }
    if (narrative.risk_factors) {
      html += '<h4>Risk Factors</h4><p>' + escH(narrative.risk_factors) + '</p>';
    }
    if (narrative.opportunities) {
      html += '<h4>Opportunities</h4><p>' + escH(narrative.opportunities) + '</p>';
    }
    html += '</div>';
    return html;
  }

  function renderSourcesFooter(detail) {
    var sources = new Set();
    function collectSources(obj) {
      if (!obj || typeof obj !== 'object') return;
      if (obj.source) {
        obj.source.split(',').forEach(function(s) { sources.add(s.trim()); });
      }
      Object.values(obj).forEach(function(v) {
        if (typeof v === 'object') collectSources(v);
      });
    }
    collectSources(detail.layers);
    if (sources.size === 0) return '';

    var html = '<div class="panel-sources">';
    html += '<div class="panel-sources__title">Data Sources</div>';
    html += '<div class="panel-sources__list">';
    sources.forEach(function(s) {
      html += '<span class="panel-sources__tag">' + escH(s) + '</span>';
    });
    html += '</div></div>';
    return html;
  }

  function renderSummaryFallback(summary) {
    var html = '<div style="padding:16px">';
    html += '<div class="factor-grid">';
    html += miniFactorCard('GDP', Utils.formatCurrency(summary.gdp_nominal_usd));
    html += miniFactorCard('Growth', Utils.formatPercent(summary.gdp_real_growth_pct, 1));
    html += miniFactorCard('Population', Utils.formatNumber(summary.population));
    html += miniFactorCard('Stability', Utils.formatScore(summary.political_stability));
    html += miniFactorCard('Risk', Utils.formatScore(summary.investment_risk_score));
    html += miniFactorCard('Region', REGIONS[summary.region] ? REGIONS[summary.region].label : summary.region);
    html += '</div>';
    if (summary.trend_headline) {
      html += '<p style="margin-top:12px;font-size:13px;color:var(--text-secondary);font-style:italic">"' + escH(summary.trend_headline) + '"</p>';
    }
    html += '</div>';
    return html;
  }

  // --- Helper HTML builders ---

  function factorCard(label, value, trend, subtitle, source, confidence) {
    var html = '<div class="factor-card">';
    html += '<div class="factor-card__header">';
    html += '<span class="factor-card__label">' + escH(label) + '</span>';
    if (confidence != null) {
      html += Utils.confidenceBarHTML(confidence);
    }
    html += '</div>';
    html += '<div class="factor-card__value">' + escH(String(value)) + '</div>';
    if (trend || subtitle) {
      html += '<div class="factor-card__footer">';
      if (trend) html += Utils.trendHTML(trend);
      if (subtitle) html += '<span style="font-size:11px;color:var(--text-muted)">' + escH(subtitle) + '</span>';
      html += '</div>';
    }
    if (source) {
      html += '<div class="factor-card__source">' + escH(source) + '</div>';
    }
    html += '</div>';
    return html;
  }

  function miniFactorCard(label, value) {
    return '<div class="factor-card" style="padding:8px">' +
      '<div class="factor-card__label">' + escH(label) + '</div>' +
      '<div class="factor-card__value" style="font-size:14px">' + escH(String(value != null ? value : '—')) + '</div>' +
      '</div>';
  }

  function formatResourceValue(r) {
    if (r.production_daily_barrels) return Utils.formatNumber(r.production_daily_barrels) + ' bbl/day';
    if (r.production_bcm_year) return Utils.formatNumber(r.production_bcm_year) + ' bcm/yr';
    if (r.production_mt_year) return Utils.formatNumber(r.production_mt_year) + ' MT/yr';
    if (r.production_tonnes_year) return Utils.formatNumber(r.production_tonnes_year) + ' t/yr';
    return '—';
  }

  function getRelationColor(quality) {
    if (quality >= 0.8) return 'var(--relation-allied)';
    if (quality >= 0.6) return 'var(--relation-friendly)';
    if (quality >= 0.4) return 'var(--relation-neutral)';
    if (quality >= 0.2) return 'var(--relation-cool)';
    return 'var(--relation-hostile)';
  }

  function escH(str) {
    if (str == null) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  // --- Event binding ---

  function bindCloseButtons() {
    var closeBtn = document.getElementById('panel-close-btn');
    var closeX = document.getElementById('panel-close-x');
    if (closeBtn) closeBtn.addEventListener('click', function() { CountryPanel.close(); });
    if (closeX) closeX.addEventListener('click', function() { CountryPanel.close(); });
  }

  function bindTabs() {
    var tabsEl = document.getElementById('layer-tabs');
    if (!tabsEl) return;
    tabsEl.addEventListener('click', function(e) {
      var btn = e.target.closest('.layer-tab');
      if (!btn || btn.classList.contains('disabled')) return;
      var tabId = btn.getAttribute('data-tab');
      activeTab = tabId;
      // Update active states
      tabsEl.querySelectorAll('.layer-tab').forEach(function(t) { t.classList.remove('active'); });
      btn.classList.add('active');
      panelEl.querySelectorAll('.layer-content').forEach(function(c) { c.classList.remove('active'); });
      var content = document.getElementById('tab-' + tabId);
      if (content) content.classList.add('active');
    });
  }

  function bindExpandables() {
    panelEl.querySelectorAll('.reasoning-toggle').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var targetId = btn.getAttribute('data-target');
        var body = document.getElementById(targetId);
        if (body) {
          btn.classList.toggle('open');
          body.classList.toggle('open');
        }
      });
    });
  }

  // --- Public API ---

  return {
    init: function(el) {
      panelEl = el;
    },

    open: async function(code) {
      if (!panelEl) return;
      currentCode = code;
      _isOpen = true;
      activeTab = 'economy';

      // Show panel
      panelEl.classList.remove('hidden');
      panelEl.offsetHeight; // reflow
      panelEl.classList.add('open');

      document.getElementById('main-content').classList.add('panel-open');
      MapView.invalidateSize();

      // Show loading state
      panelEl.innerHTML = '<div class="panel-header"><span class="panel-header__title">Loading...</span><button class="panel-header__close" id="panel-close-x">✕</button></div>' +
        '<div class="panel-loading"><div class="skeleton" style="width:80%;height:16px;margin:8px auto"></div><div class="skeleton" style="width:60%;height:16px;margin:8px auto"></div><div class="skeleton" style="width:70%;height:16px;margin:8px auto"></div></div>';
      document.getElementById('panel-close-x').addEventListener('click', function() { CountryPanel.close(); });

      // Load detail data
      var summary = DataLoader.getSummaryByCode(code);
      var detail = null;
      try {
        detail = await DataLoader.getCountryDetail(code);
      } catch (err) {
        // Detail not available — show summary fallback
      }

      // Only render if still showing same country
      if (currentCode === code) {
        renderPanel(code, detail, summary);
      }
    },

    close: function() {
      if (!panelEl) return;
      _isOpen = false;
      currentCode = null;
      panelEl.classList.remove('open');
      document.getElementById('main-content').classList.remove('panel-open');
      MapView.invalidateSize();
      MapView.deselectCountry();

      setTimeout(function() {
        if (!_isOpen) {
          panelEl.classList.add('hidden');
          panelEl.innerHTML = '';
        }
      }, 400);
    },

    isOpen: function() {
      return _isOpen;
    },

    getCurrentCode: function() {
      return currentCode;
    }
  };
})();
