# Geopolitical Intelligence Model — Factor Model Specification

**Version:** 1.1
**Date:** 2026-03-14
**Status:** Active

---

## Overview

This document defines the complete data schema for the Geopolitical Intelligence Model. Every country in the model is described by factors organized into 6 layers. Bilateral relationships between countries form a separate relational layer. Supranational entities are modeled as overlays.

The model targets **75 countries** in 3 tiers: 30 Tier 1 (major economies), 25 Tier 2 (regional players), and 20 Tier 3 (frontier/watchlist), representing 95%+ of global investable markets.

---

## Data Conventions

- All monetary values in **USD** unless otherwise specified
- All percentages as **float 0-100** (not 0-1) unless explicitly noted as index
- All indices normalized to **float 0.0 - 1.0** unless otherwise specified
- All timestamps in **ISO 8601 UTC**
- Every factor carries metadata: `source`, `confidence` (0.0-1.0), `last_updated` (timestamp), `update_frequency` (enum)
- Trend enum values: `strong_growth | growth | stable | decrease | strong_decrease`
- Seasonal arrays are always **12 elements** (Jan=0 through Dec=11)

### Update Frequency Enum

```
update_frequency: enum {
  realtime,      // Updated within hours of change (not used in current pipeline)
  daily,         // Updated daily (not used in current pipeline)
  weekly,        // Updated every pipeline run (~7 days). Market data, events, leadership.
  monthly,       // Updated every ~30 days. Monetary/inflation, unemployment.
  quarterly,     // Updated every ~90 days. GDP, trade flows, FDI, fiscal data.
  annual,        // Updated when source publishes new edition. Governance indices, military baselines.
  static,        // Seed once, refresh only on rare trigger events. Geography, cultural factors.
  derived        // Recomputed each run from base factors. No external fetching.
}
```

The authoritative factor→frequency mapping is in `/agents/config/factor_frequency_registry.json`.
Agents use `/agents/config/release_calendar.json` for annual source publication dates
and `/agents/config/cache_registry.json` for runtime cache state.

### Confidence Scoring

```
confidence: float (0.0 - 1.0)
  0.0 - 0.2: Unverified / single unreliable source
  0.2 - 0.4: Single credible source, no corroboration
  0.4 - 0.6: Multiple sources with some disagreement
  0.6 - 0.8: Multiple credible sources, broadly consistent
  0.8 - 1.0: Official/authoritative source, cross-validated
```

---

## LAYER 1: ENDOWMENTS

### 1A. Natural Resources

Each resource instance per country:

```yaml
ResourceFactor:
  country_code: string                    # ISO 3166-1 alpha-3
  resource_type: ResourceTypeEnum         # See taxonomy below
  resource_category: ResourceCategoryEnum # ENERGY | METAL_CRITICAL | METAL_PRECIOUS | etc.
  
  # Quantities
  proven_reserves: float                  # Unit depends on resource type
  proven_reserves_unit: string            # "barrels", "tonnes", "cubic_meters", etc.
  annual_production: float
  annual_production_unit: string
  annual_domestic_consumption: float
  net_export_volume: float                # production - consumption
  
  # Ratios
  export_dependency_ratio: float          # 0-1, % of production exported
  import_dependency_ratio: float          # 0-1, % of consumption imported
  global_share_of_production: float       # 0-1
  global_share_of_reserves: float         # 0-1
  years_to_depletion: float              # reserves / annual_production, null if renewable
  
  # Cost & quality
  extraction_cost_relative: enum          # low | medium | high | very_high
  resource_quality_grade: enum            # premium | standard | low_grade
  
  # Seasonality
  seasonal_production_profile: float[12]  # Monthly multiplier, 1.0 = average month
  seasonal_demand_profile: float[12]      # Monthly multiplier for domestic consumption
  
  # Metadata
  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: update_frequency_enum
  notes: string
```

#### Resource Type Taxonomy

```yaml
ResourceTypeEnum:
  ENERGY:
    - crude_oil
    - natural_gas
    - coal_thermal
    - coal_metallurgical
    - uranium
    - thorium
    - geothermal_potential
    - hydroelectric_installed
    - hydroelectric_untapped
    - solar_irradiance_capacity
    - wind_energy_potential
    - tidal_wave_potential
    - biomass_potential

  METALS_CRITICAL:
    - iron_ore
    - copper
    - bauxite_aluminum
    - lithium
    - cobalt
    - nickel
    - manganese
    - chromium
    - tungsten
    - titanium
    - vanadium
    - molybdenum
    - tin
    - zinc
    - lead
    - graphite
    - silicon_semiconductor_grade

  RARE_EARTH_ELEMENTS:
    - neodymium
    - dysprosium
    - lanthanum
    - cerium
    - praseodymium
    - samarium
    - europium
    - gadolinium
    - terbium
    - yttrium
    - scandium
    - rare_earth_aggregate  # When individual breakdown unavailable

  PRECIOUS_METALS:
    - gold
    - silver
    - platinum
    - palladium
    - rhodium

  STRATEGIC_NON_METALS:
    - phosphate_rock
    - potash
    - fluorite
    - helium
    - sulfur
    - diamonds_industrial
    - diamonds_gem
    - salt
    - gypsum
    - limestone

  AGRICULTURAL_BIOLOGICAL:
    - arable_land_km2
    - arable_land_pct
    - permanent_cropland_km2
    - pasture_grazing_km2
    - forest_total_km2
    - forest_commercially_exploitable_km2
    - fish_stocks_marine_tonnes
    - fish_stocks_freshwater_tonnes
    - timber_production_capacity_m3

  WATER:
    - renewable_freshwater_total_km3
    - renewable_freshwater_per_capita_m3
    - groundwater_reserves_km3
    - desalination_capacity_m3_per_day
    - transboundary_water_dependency_pct  # % of freshwater from external sources
```

### 1B. Geography & Physical Factors

```yaml
GeographyFactor:
  country_code: string

  # Territory
  total_area_km2: float
  land_area_km2: float
  water_area_km2: float
  coastline_km: float
  highest_elevation_m: float
  lowest_elevation_m: float
  mean_elevation_m: float

  # Terrain composition (percentages summing to ~100)
  terrain:
    mountainous_pct: float
    hills_plateau_pct: float
    plains_pct: float
    desert_pct: float
    forest_pct: float
    wetland_pct: float
    tundra_ice_pct: float
    urban_built_pct: float

  # Classification
  landlocked: boolean
  island_nation: boolean
  archipelago: boolean
  transcontinental: boolean
  continents: string[]            # e.g., ["Europe", "Asia"] for Turkey

  # Strategic features
  strategic_waterway_control: string[]
    # e.g., ["Strait of Hormuz", "Bab el-Mandeb"]
  strategic_waterway_proximity_km: object[]
    # [{name: "Suez Canal", distance_km: 150}]
  geographic_fragmentation_index: float  # 0-1. High = Indonesia, low = France
  internal_natural_barriers: string[]
    # e.g., ["Andes divides Chile east-west", "Congo River basin"]
  time_zones_count: int

  # Metadata
  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: static
```

### 1C. Borders

One record per border pair:

```yaml
BorderFactor:
  country_a: string               # ISO 3166-1 alpha-3
  country_b: string
  border_length_km: float

  # Physical composition (percentages of border length)
  composition:
    land_open_pct: float
    river_pct: float
    lake_pct: float
    mountain_pct: float
    desert_pct: float
    forest_pct: float
    wall_fence_pct: float
    sea_gap_km: float             # If separated by water (e.g., UK-France ~34km)
    ice_barrier_km: float         # If applicable

  # Accessibility
  official_crossing_points: int
  major_crossing_points: int      # High-volume crossings
  rail_connections: int
  highway_connections: int
  ease_of_crossing_index: float   # 0-1, combines physical + political
  seasonal_accessibility: float[12]  # 0-1 per month. 0=impassable, 1=fully open

  # Political status
  border_dispute_active: boolean
  border_dispute_description: string
  border_dispute_severity: enum   # none | minor | moderate | serious | active_conflict
  demilitarized_zone: boolean
  militarized_border: boolean
  military_incidents_last_year: int

  # Metadata
  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: quarterly
```

### 1D. Maritime Access

```yaml
MaritimeAccess:
  country_code: string
  exclusive_economic_zone_km2: float
  continental_shelf_claims_km2: float

  major_ports:
    - name: string
      latitude: float
      longitude: float
      capacity_teu_annual: float        # Container throughput
      bulk_capacity_tonnes_annual: float
      max_vessel_depth_m: float
      ice_free_months: int
      global_ranking: int
      special_economic_zone: boolean

  nearest_major_shipping_lane_km: float
  maritime_chokepoint_dependency: string[]
    # Chokepoints this country's trade must transit
    # e.g., Japan: ["Strait of Malacca", "Strait of Hormuz", "Suez Canal"]

  submarine_cable_landing_points: int
  submarine_cable_connections: string[]  # Names of cables

  naval_base_count_domestic: int
  naval_base_count_foreign_hosted: int   # Foreign bases on this country's territory
  naval_base_count_abroad: int           # This country's bases abroad

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: annual
```

### 1E. Climate

```yaml
ClimateFactor:
  country_code: string
  koppen_classification_dominant: string
  koppen_classifications_present: string[]

  monthly_profile:                       # Array of 12
    - month: int                         # 0-11
      avg_temp_c: float
      min_temp_c: float
      max_temp_c: float
      precipitation_mm: float
      sunshine_hours: float
      extreme_weather_risk: enum         # low | medium | high | extreme

  natural_disaster_exposure:
    earthquake_risk: enum                # negligible | low | medium | high | extreme
    tsunami_risk: enum
    hurricane_typhoon_risk: enum
    flooding_risk: enum
    drought_risk: enum
    wildfire_risk: enum
    volcanic_risk: enum
    tornado_risk: enum
    landslide_risk: enum

  climate_change_vulnerability_index: float  # 0-1 (ND-GAIN or similar)
  climate_change_readiness_index: float      # 0-1

  sea_level_rise_exposure:
    population_below_1m_pct: float
    population_below_5m_pct: float
    gdp_below_5m_pct: float
    critical_infrastructure_below_5m_pct: float

  growing_season_days: int
  frost_free_days: int

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: static                   # Climate classification rarely changes; vulnerability indices are annual
```

### 1F. Demographics

```yaml
DemographicFactor:
  country_code: string

  # Population
  population_total: int
  population_growth_rate_pct: float
  population_density_per_km2: float
  median_age: float

  age_pyramid:
    age_0_14_pct: float
    age_15_24_pct: float
    age_25_54_pct: float
    age_55_64_pct: float
    age_65_plus_pct: float

  dependency_ratio: float               # (0-14 + 65+) / (15-64)
  youth_bulge_index: float              # 15-24 as ratio of adult population

  # Urbanization
  urbanization_rate_pct: float
  urbanization_trend: trend_enum
  largest_city_population: int
  largest_city_name: string
  primate_city_index: float             # Largest city pop / 2nd largest city pop

  # Education & labor
  literacy_rate_pct: float
  labor_force_total: int
  labor_force_participation_rate_pct: float
  female_labor_participation_pct: float
  unemployment_rate_pct: float
  youth_unemployment_rate_pct: float

  # Migration
  net_migration_rate_per_1000: float
  refugee_population_hosted: int
  refugee_population_originated: int
  diaspora_size_estimate: int
  remittance_inflows_pct_gdp: float

  # Diversity
  ethnic_fractionalization_index: float       # 0-1
  linguistic_fractionalization_index: float   # 0-1
  religious_fractionalization_index: float    # 0-1

  # Health
  life_expectancy_years: float
  infant_mortality_per_1000: float
  health_expenditure_pct_gdp: float
  physicians_per_1000: float
  hospital_beds_per_1000: float

  # Composite
  human_development_index: float              # 0-1

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: annual
```

---

## LAYER 2: INSTITUTIONS & CULTURE

### 2A. Endemic Cultural Factors (Historical / Deep-Structural)

```yaml
EndemicCulturalFactor:
  country_code: string

  # Hofstede cultural dimensions (scaled 0-100)
  individualism_vs_collectivism: float
  power_distance: float
  uncertainty_avoidance: float
  masculinity_vs_femininity: float
  long_term_orientation: float
  indulgence_vs_restraint: float

  # World Values Survey dimensions
  traditional_vs_secular: float          # -2 to 2
  survival_vs_self_expression: float     # -2 to 2
  generalized_trust_pct: float           # "Can most people be trusted?" %yes

  # Historical institutional depth
  state_formation_antiquity: enum
    # ancient | medieval | colonial_construct | post_cold_war | recent
  colonial_legacy_type: enum
    # none | british | french | spanish | portuguese | dutch |
    # ottoman | russian_soviet | japanese | belgian | italian | other
  colonial_independence_year: int         # null if never colonized
  post_independence_stability: enum
    # stable | periodic_disruption | frequent_disruption | chronic_instability
  rule_of_law_tradition_depth: enum
    # deep | moderate | shallow | contested
  property_rights_historical_strength: enum
    # strong | moderate | weak | absent

  # Economic culture
  entrepreneurial_orientation_index: float   # 0-1
  state_intervention_tradition: enum
    # minimal | moderate | significant | dominant
  informal_economy_estimated_pct_gdp: float
  corruption_cultural_tolerance: enum
    # low | moderate | high | endemic

  # Social capital
  civic_participation_index: float           # 0-1
  social_mobility_index: float               # 0-1
  gender_equality_index: float               # 0-1 (UNDP GII)
  religious_influence_on_governance: enum
    # secular | moderate_influence | significant_influence | theocratic

  source: string
  methodology_url: string
  confidence: float
  last_updated: timestamp
  update_frequency: static    # Hofstede/WVS/historical factors are static; indices like gender_equality are annual
  notes: string
```

### 2B. Current Political Factors

```yaml
CurrentPoliticalFactor:
  country_code: string

  # Regime & governance quality
  regime_type: enum
    # full_democracy | flawed_democracy | hybrid_regime |
    # authoritarian | failed_state | military_junta | theocracy
  democracy_index: float                     # 0-10 (EIU)
  democracy_index_trend: trend_enum
  freedom_house_status: enum                 # free | partly_free | not_free
  freedom_house_score: float                 # 0-100
  press_freedom_index_rank: int              # RSF
  corruption_perception_index: float         # 0-100 (TI)

  # World Bank Worldwide Governance Indicators (all -2.5 to 2.5)
  wgi_voice_accountability: float
  wgi_political_stability: float
  wgi_government_effectiveness: float
  wgi_regulatory_quality: float
  wgi_rule_of_law: float
  wgi_control_of_corruption: float

  # Leadership
  head_of_state_name: string
  head_of_state_title: string
  head_of_government_name: string            # If different from HoS
  years_current_leader_in_power: float
  succession_mechanism: enum
    # democratic_election | hereditary | party_selection |
    # military_appointment | unclear | transitional
  next_national_election_date: date          # null if not applicable
  election_integrity_score: float            # 0-1

  # Political dynamics
  leadership_transition_risk: enum           # low | medium | high | critical
  governing_coalition_stability: enum        # stable | fragile | crisis
  major_opposition_strength: enum            # weak | moderate | strong | dominant
  legislative_gridlock_level: enum           # none | mild | moderate | severe
  civil_unrest_level: enum                   # none | sporadic | frequent | endemic | crisis
  protest_frequency_last_quarter: int

  # Internal conflicts
  separatist_movements:
    - name: string
      region: string
      intensity: enum                        # political | militant | armed_conflict
      external_support: boolean
      population_affected_estimate: int

  active_insurgencies:
    - name: string
      type: string
      intensity: enum                        # low | medium | high
      territory_controlled_pct: float

  # Policy orientation (current government)
  economic_policy_orientation: float         # -1 (state control) to +1 (free market)
  trade_policy_orientation: float            # -1 (protectionist) to +1 (free trade)
  foreign_policy_orientation: float          # -1 (isolationist) to +1 (interventionist)
  foreign_policy_alignment: enum
    # western_aligned | non_aligned | china_aligned | russia_aligned |
    # multi_vector | regional_focused
  environmental_policy_commitment: float     # 0-1
  digital_governance_sophistication: float   # 0-1
  resource_nationalism_tendency: float       # 0-1
  migration_policy_openness: float           # 0-1

  # Sanctions status
  under_international_sanctions: boolean
  sanctions:
    - imposing_entity: string                # "US", "EU", "UN", etc.
      type: enum                             # comprehensive | sectoral | targeted_individuals
      sectors_affected: string[]
      since_date: date
      severity_score: float                  # 0-1

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: weekly
```

---

## LAYER 3: ECONOMY

### 3A. Macroeconomic Factors

```yaml
MacroeconomicFactor:
  country_code: string

  # Size & growth
  gdp_nominal_usd: float
  gdp_ppp_usd: float
  gdp_per_capita_nominal_usd: float
  gdp_per_capita_ppp_usd: float
  gdp_real_growth_rate_pct: float
  gdp_real_growth_trend: trend_enum
  gdp_composition:
    agriculture_pct: float
    industry_pct: float
    services_pct: float
  gni_per_capita_usd: float
  gdp_global_rank: int
  gdp_ppp_global_rank: int

  # Fiscal
  government_revenue_pct_gdp: float
  government_expenditure_pct_gdp: float
  fiscal_balance_pct_gdp: float
  public_debt_pct_gdp: float
  public_debt_trend: trend_enum
  external_debt_total_usd: float
  external_debt_pct_gdp: float
  external_debt_pct_exports: float
  debt_service_ratio: float                  # Debt service / export earnings
  sovereign_credit_rating:
    moodys: string
    moodys_outlook: enum                     # positive | stable | negative
    sp: string
    sp_outlook: enum
    fitch: string
    fitch_outlook: enum

  # Monetary & prices
  inflation_rate_cpi_pct: float
  inflation_trend: trend_enum
  core_inflation_pct: float
  central_bank_policy_rate_pct: float
  central_bank_independence_score: float      # 0-1
  money_supply_m2_growth_pct: float
  real_interest_rate_pct: float

  # External position
  current_account_balance_usd: float
  current_account_pct_gdp: float
  trade_balance_usd: float
  total_exports_usd: float
  total_imports_usd: float
  export_growth_trend: trend_enum
  import_growth_trend: trend_enum

  top_export_products:
    - product: string
      hs_code: string                        # Harmonized System code
      pct_of_total: float
      value_usd: float

  top_import_products:
    - product: string
      hs_code: string
      pct_of_total: float
      value_usd: float

  top_export_partners:
    - country: string
      pct_of_total: float
      value_usd: float

  top_import_partners:
    - country: string
      pct_of_total: float
      value_usd: float

  # Investment flows
  fdi_inflow_usd: float
  fdi_inflow_trend: trend_enum
  fdi_outflow_usd: float
  portfolio_investment_net_usd: float
  remittance_inflows_usd: float
  remittance_outflows_usd: float

  # Reserves & currency
  foreign_exchange_reserves_usd: float
  reserve_adequacy_months_of_imports: float
  gold_reserves_tonnes: float
  currency_code: string
  currency_name: string
  exchange_rate_vs_usd: float
  exchange_rate_trend_12m: trend_enum
  exchange_rate_regime: enum
    # free_floating | managed_float | crawling_peg | fixed_peg |
    # currency_board | dollarized | currency_union | multiple_rates
  capital_account_openness_index: float      # 0-1 (Chinn-Ito)
  swift_connected: boolean
  correspondent_banking_relationships: int

  # Financial system
  banking_sector_assets_pct_gdp: float
  non_performing_loans_pct: float
  stock_market_cap_pct_gdp: float
  stock_market_cap_usd: float
  stock_market_daily_turnover_usd: float
  bond_market_size_usd: float
  financial_development_index: float         # 0-1 (IMF)
  financial_inclusion_account_pct: float     # % adults with bank account

  # Labor & inequality
  gini_coefficient: float                    # 0-1
  income_share_top_10_pct: float
  income_share_bottom_40_pct: float
  poverty_rate_national_pct: float
  poverty_rate_190_usd_pct: float            # International poverty line
  minimum_wage_usd_monthly: float
  average_wage_usd_monthly: float
  median_wage_usd_monthly: float

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: annual                   # Inequality data is annual; wage data may lag 1-2 years
```

### 3B. Productive Capability & Value-Add Capacity

```yaml
CapabilityFactor:
  country_code: string

  # Economic complexity (Harvard Atlas)
  economic_complexity_index: float
  economic_complexity_rank: int
  product_diversification_count: int         # Products with RCA > 1
  export_sophistication_score: float         # PRODY-weighted

  # Human capital
  mean_years_of_schooling: float
  expected_years_of_schooling: float
  tertiary_enrollment_rate_pct: float
  stem_graduates_per_million: float
  vocational_training_enrollment_pct: float
  english_proficiency_index: float           # EF EPI
  pisa_scores:
    math: float
    science: float
    reading: float
  researchers_per_million: float
  r_and_d_expenditure_pct_gdp: float
  patent_applications_residents_annual: int
  patent_applications_per_million: float
  scientific_publications_per_million: float
  top_university_count_global_500: int
  top_university_count_global_100: int
  brain_drain_index: float                   # 0-1, 1 = severe brain drain

  # Technology & innovation
  global_innovation_index_rank: int          # WIPO
  global_innovation_index_score: float
  ict_development_index: float
  internet_penetration_pct: float
  fixed_broadband_per_100: float
  mobile_broadband_per_100: float
  smartphone_penetration_pct: float
  technology_readiness_level: enum
    # frontier | advanced | transitional | developing | nascent
  ai_readiness_index: float                  # 0-1

  # Specific capability domains (0-1 score each)
  # Based on: revealed comparative advantage + infrastructure +
  # human capital + active firms + patent activity
  capability_domains:
    advanced_manufacturing: float
    semiconductor_electronics: float
    pharmaceutical_biotech: float
    aerospace_defense_industry: float
    automotive: float
    petrochemical_refining: float
    agriculture_food_processing: float
    financial_services: float
    software_ai_digital: float
    renewable_energy_tech: float
    nuclear_technology: float
    shipbuilding_marine: float
    construction_infrastructure: float
    mining_extraction: float
    textiles_light_manufacturing: float
    tourism_hospitality: float
    logistics_shipping: float
    creative_industries_media: float
    space_technology: float
    medical_devices_healthtech: float

  # Physical infrastructure
  infrastructure_quality_index: float        # 0-1 (WEF or similar)
  road_network_km: float
  road_density_km_per_km2: float
  paved_road_pct: float
  rail_network_km: float
  high_speed_rail_km: float
  airport_count_major: int
  airport_passenger_capacity_annual: float
  logistics_performance_index: float         # World Bank LPI

  # Energy infrastructure
  electricity_generation_capacity_gw: float
  electricity_access_pct: float
  electricity_reliability_index: float       # 0-1
  energy_mix:
    fossil_pct: float
    nuclear_pct: float
    hydro_pct: float
    solar_pct: float
    wind_pct: float
    other_renewable_pct: float
  energy_intensity_mj_per_usd_gdp: float
  renewable_energy_trend: trend_enum

  # Digital infrastructure
  data_center_capacity_mw: float
  submarine_cable_landing_points: int
  cloud_availability_zones_major_providers: int
  five_g_coverage_pct: float
  fiber_optic_coverage_pct: float
  digital_infrastructure_trend: trend_enum

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: annual                   # Capability/infrastructure data is annual
```

---

## LAYER 4: MILITARY & SECURITY

```yaml
MilitaryFactor:
  country_code: string

  # Personnel
  active_military_personnel: int
  reserve_military_personnel: int
  paramilitary_personnel: int
  military_age_fit_population: int

  # Budget
  military_expenditure_usd: float
  military_expenditure_pct_gdp: float
  military_expenditure_per_capita_usd: float
  military_expenditure_trend: trend_enum
  procurement_budget_usd: float

  # Ground forces
  army:
    main_battle_tanks: int
    infantry_fighting_vehicles: int
    armored_personnel_carriers: int
    self_propelled_artillery: int
    towed_artillery: int
    rocket_projectors: int
    air_defense_systems: int

  # Naval forces
  navy:
    aircraft_carriers: int
    helicopter_carriers: int
    destroyers: int
    frigates: int
    corvettes: int
    submarines_total: int
    submarines_nuclear_powered: int
    submarines_nuclear_armed: int
    patrol_vessels: int
    mine_warfare_vessels: int
    amphibious_assault_ships: int
    total_naval_tonnage_tons: float
    blue_water_capability: boolean

  # Air forces
  air_force:
    fifth_gen_fighters: int
    fourth_gen_fighters: int
    multirole_aircraft: int
    attack_aircraft: int
    strategic_bombers: int
    transport_aircraft: int
    tanker_aircraft: int
    awacs_aircraft: int
    attack_helicopters: int
    transport_helicopters: int
    combat_drones: int
    reconnaissance_drones: int
    drone_swarm_capability: boolean

  # Strategic capabilities
  nuclear:
    status: enum
      # declared_arsenal | undeclared_suspected | threshold_capable |
      # nuclear_sharing | non_nuclear | renounced
    warheads_estimated: int
    delivery_systems:
      icbm: boolean
      icbm_count: int
      irbm: boolean
      srbm: boolean
      slbm: boolean
      air_launched_cruise_missiles: boolean
    second_strike_capability: boolean
    nuclear_triad: boolean

  missile_defense:
    ballistic_missile_defense: boolean
    system_names: string[]
    coverage: enum                           # point | area | national | none

  hypersonic_capability: boolean
  space_military_capability: enum            # none | emerging | established | advanced
  anti_satellite_capability: boolean

  cyber:
    capability_level: enum                   # none | basic | intermediate | advanced | elite
    known_apt_groups: int                    # Known Advanced Persistent Threat groups attributed
    offensive_cyber_doctrine: boolean
    cyber_command_established: boolean

  electronic_warfare_capability: enum        # basic | intermediate | advanced

  # Power projection
  overseas_military_bases: int
  overseas_base_locations:
    - host_country: string
      base_type: enum                        # naval | air | army | logistics | intelligence
      personnel_estimate: int
  airlift_capacity_strategic_tons: float
  sealift_capacity_tons: float
  aerial_refueling_sorties_per_day: int
  force_projection_range_km: float           # Operational radius without forward basing

  # Defense industry
  domestic_arms_production: enum
    # none | basic_small_arms | intermediate | advanced | full_spectrum
  arms_exports_usd_annual: float
  arms_imports_usd_annual: float
  top_arms_suppliers:
    - country: string
      pct_of_imports: float
  top_arms_customers:
    - country: string
      pct_of_exports: float
  defense_industry_self_sufficiency: float   # 0-1

  # Intelligence
  intelligence_budget_estimated_usd: float
  sigint_capability: enum                    # none | basic | regional | global
  humint_reach: enum                         # limited | moderate | extensive | global
  satellite_reconnaissance: boolean
  satellite_count_military: int

  # Combat readiness
  active_conflicts:
    - name: string
      type: enum                             # internal | external | peacekeeping | counter_terrorism
      since_date: date
      intensity: enum                        # low | medium | high
      personnel_deployed: int
  recent_combat_experience: boolean
  military_readiness_estimate: enum
    # low | moderate | high | very_high | combat_proven
  conscription_active: boolean
  conscription_length_months: int
  professional_military_pct: float           # % career soldiers vs conscripts

  # Alliances (summary, detail in relations)
  alliance_memberships: string[]             # ["NATO", "Five Eyes", etc.]
  mutual_defense_treaty_count: int
  military_cooperation_agreements_count: int

  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: annual                   # Structural military data is annual; active_conflicts and events are weekly
```

---

## LAYER 5: BILATERAL RELATIONS

One record per directed country pair (A→B may differ from B→A for some fields):

```yaml
BilateralRelation:
  country_a: string                          # ISO alpha-3
  country_b: string
  relation_id: string                        # "{country_a}_{country_b}"

  # --- TRADE ---
  trade:
    bilateral_trade_volume_usd: float
    a_exports_to_b_usd: float
    b_exports_to_a_usd: float
    trade_balance_a_perspective_usd: float
    trade_dependency_a_on_b: float           # 0-1 (b's share of a's total trade)
    trade_dependency_b_on_a: float
    top_products_a_to_b:
      - product: string
        hs_code: string
        value_usd: float
    top_products_b_to_a:
      - product: string
        hs_code: string
        value_usd: float
    free_trade_agreement: boolean
    fta_name: string
    trade_disputes_active:
      - description: string
        wto_case: boolean
        initiated_by: string
        since_date: date
    avg_tariff_a_on_b_pct: float
    avg_tariff_b_on_a_pct: float
    sanctions_a_on_b: boolean
    sanctions_b_on_a: boolean
    trade_trend: trend_enum

  # --- MOVEMENT OF PEOPLE ---
  people:
    visa_a_to_b: enum
      # visa_free | visa_on_arrival | e_visa | visa_required | restricted | banned
    visa_b_to_a: enum
    tourist_flow_a_to_b_annual: int
    tourist_flow_b_to_a_annual: int
    diaspora_a_in_b: int
    diaspora_b_in_a: int
    remittance_a_to_b_usd: float
    remittance_b_to_a_usd: float
    direct_flight_routes: int
    flight_time_capital_hours: float
    shipping_time_main_port_days: float
    land_travel_possible: boolean
    land_travel_time_capital_hours: float

  # --- DIPLOMATIC ---
  diplomatic:
    diplomatic_relations_established: boolean
    diplomatic_relations_since: date
    embassy_a_in_b: boolean
    consulates_a_in_b: int
    embassy_b_in_a: boolean
    consulates_b_in_a: int
    relationship_status: enum
      # allied | close_partner | friendly | neutral | cool | tense | hostile | conflict
    relationship_trend: trend_enum
    un_voting_alignment_score: float         # 0-1 (UNGA voting similarity)
    shared_organization_memberships: string[]
    recent_diplomatic_incidents:
      - date: date
        description: string
        severity: enum                       # minor | moderate | serious | critical
        resolved: boolean
    ambassador_recalled: boolean
    diplomatic_expulsions_last_year: int

  # --- MILITARY ---
  military:
    alliance_type: enum
      # mutual_defense | strategic_partnership | cooperation_agreement |
      # arms_trade_only | none | adversarial | active_conflict
    alliance_name: string
    joint_exercises_annual: int
    arms_trade_a_to_b_usd: float
    arms_trade_b_to_a_usd: float
    military_base_a_in_b: boolean
    military_base_b_in_a: boolean
    troops_a_stationed_in_b: int
    troops_b_stationed_in_a: int
    intelligence_sharing: boolean
    intelligence_sharing_level: enum         # none | limited | extensive | integrated
    border_militarization: enum
      # demilitarized | low | moderate | high | active_conflict
    military_incidents_last_year: int
    military_cooperation_trend: trend_enum

  # --- SCIENCE & TECHNOLOGY ---
  science_tech:
    joint_research_publications_annual: int
    joint_patents_annual: int
    student_exchange_a_to_b: int
    student_exchange_b_to_a: int
    research_collaboration_agreements: int
    technology_transfer_restrictions: boolean
    technology_transfer_direction: enum      # a_to_b | b_to_a | bidirectional | restricted | none
    joint_space_programs: boolean
    nuclear_cooperation_agreement: boolean
    science_cooperation_trend: trend_enum

  # --- FINANCIAL ---
  financial:
    fdi_a_in_b_stock_usd: float
    fdi_b_in_a_stock_usd: float
    fdi_flow_a_to_b_annual_usd: float
    fdi_flow_b_to_a_annual_usd: float
    bilateral_currency_swap: boolean
    currency_swap_amount_usd: float
    sovereign_debt_a_held_by_b_usd: float
    sovereign_debt_b_held_by_a_usd: float
    bilateral_investment_treaty: boolean
    double_taxation_agreement: boolean
    correspondent_banking_active: boolean
    financial_sanctions_active: boolean
    financial_relationship_trend: trend_enum

  # --- ENERGY ---
  energy:
    pipeline_connections:
      - type: enum                           # oil | gas | hydrogen
        name: string
        capacity_unit_per_year: float
        utilization_pct: float
    electricity_grid_interconnection: boolean
    electricity_trade_gwh_annual: float
    lng_trade_a_to_b_usd: float
    lng_trade_b_to_a_usd: float
    oil_trade_a_to_b_usd: float
    oil_trade_b_to_a_usd: float
    energy_dependency_a_on_b: float          # 0-1
    energy_dependency_b_on_a: float
    joint_energy_projects: string[]
    energy_relationship_trend: trend_enum

  # --- COMPOSITE SCORES (derived) ---
  composite:
    cooperation_index: float                 # 0-1 (weighted aggregate of positive indicators)
    tension_index: float                     # 0-1 (weighted aggregate of negative indicators)
    interdependence_index: float             # 0-1 (mutual dependency)
    power_asymmetry: float                   # -1 to 1 (neg = a dominates, pos = b dominates)
    relationship_stability: float            # 0-1 (volatility of recent changes)
    investor_relevance_score: float          # 0-1 (how much does this pair matter for investors?)

  # Metadata
  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: weekly
```

---

## LAYER 6: DERIVED METRICS (Computed)

These are not collected — they are computed from Layers 1-5:

```yaml
DerivedMetrics:
  country_code: string
  computed_at: timestamp

  # --- VULNERABILITY & DEPENDENCY ---
  resource_self_sufficiency_index: float     # 0-1
  energy_independence_index: float           # 0-1
  food_independence_index: float             # 0-1
  water_security_index: float               # 0-1
  technology_independence_index: float       # 0-1
  supply_chain_chokepoint_exposure: float    # 0-1
  single_partner_concentration_risk: float   # 0-1 (HHI of trade partners)
  sanctions_vulnerability_index: float       # 0-1
  critical_import_dependency:
    - resource: string
      primary_supplier: string
      supplier_share_pct: float
      substitutability: enum                 # easy | moderate | difficult | near_impossible
      strategic_criticality: enum            # low | medium | high | critical

  # --- NATIONAL POWER & INFLUENCE ---
  composite_national_power_index: float      # 0-100
  economic_power_component: float            # 0-100
  military_power_component: float            # 0-100
  soft_power_component: float                # 0-100
  diplomatic_network_centrality: float       # 0-1 (graph centrality measure)
  economic_coercion_capability: float        # 0-1 (ability to weaponize trade/finance)
  economic_coercion_vulnerability: float     # 0-1 (susceptibility to coercion)
  alliance_strength_score: float             # 0-1

  # --- INVESTOR-SPECIFIC DERIVED ---
  political_risk_premium_bps: float          # Estimated basis points
  market_accessibility_score: float          # 0-1 (for foreign portfolio investors)
  expropriation_risk_score: float            # 0-1
  currency_crisis_probability_12m: float     # 0-1
  sovereign_default_probability_12m: float   # 0-1
  fdi_attractiveness_composite: float        # 0-1
  ease_of_doing_business_score: float        # 0-100
  capital_flight_risk: float                 # 0-1
  regulatory_stability_index: float          # 0-1 (how predictable is the regulatory env?)

  # --- TRAJECTORY ESTIMATES ---
  # Array of trend estimates for key factors
  trend_estimates:
    - factor_path: string                    # e.g., "macroeconomic.gdp_real_growth_rate_pct"
      current_value: float
      previous_quarter_value: float
      trend: trend_enum
      trend_confidence: float                # 0-1
      reasoning: string                      # Natural language explanation
      supporting_events:
        - event_description: string
          event_date: date
          source_url: string
          impact_direction: enum             # positive | negative | neutral
          impact_magnitude: enum             # minor | moderate | major | transformative
      counter_arguments: string              # What could invalidate this trend?
      time_horizon: "quarterly"
      estimated_at: timestamp

  # --- ALERTS & FLAGS ---
  active_alerts:
    - alert_type: enum
        # political_instability | economic_crisis | military_escalation |
        # sanctions_change | regime_change_risk | currency_crisis |
        # supply_chain_disruption | social_unrest | natural_disaster |
        # election_approaching | policy_shift | trade_war_escalation
      severity: enum                         # watch | warning | critical | emergency
      title: string
      description: string
      affected_factors: string[]
      first_detected: timestamp
      last_updated: timestamp
      source_events: string[]
```

---

## SUPRANATIONAL ENTITIES

```yaml
SupranationalEntity:
  entity_id: string                          # e.g., "EU", "NATO", "BRICS"
  name: string
  type: enum
    # economic_union | military_alliance | trade_bloc | political_forum |
    # commodity_cartel | development_bank | regulatory_body |
    # security_partnership | cultural_organization
  founded_year: int

  members:
    - country_code: string
      membership_type: enum                  # full | associate | observer | applicant | suspended
      joined_date: date
      voting_weight: float                   # If applicable

  # Aggregate metrics (computed from member data)
  aggregate_gdp_usd: float
  aggregate_gdp_ppp_usd: float
  aggregate_population: int
  aggregate_military_personnel: int
  aggregate_military_expenditure_usd: float
  aggregate_land_area_km2: float
  global_trade_share_pct: float

  # Institutional characteristics
  decision_making: enum
    # unanimous | qualified_majority | simple_majority | weighted_voting |
    # hegemon_led | consensus
  has_collective_defense: boolean
  has_common_market: boolean
  has_common_currency: boolean
  has_parliament: boolean
  has_court: boolean
  has_standing_military: boolean
  enforcement_capability: enum               # none | limited | moderate | strong
  budget_usd: float

  # Current state
  cohesion_index: float                      # 0-1
  cohesion_trend: trend_enum
  expansion_momentum: enum                   # expanding | stable | contracting | crisis
  current_presidency_rotation: string        # Country holding presidency, if applicable

  internal_tensions:
    - description: string
      countries_involved: string[]
      severity: enum                         # minor | moderate | serious | existential
      since_date: date

  recent_actions:
    - date: date
      action: string
      significance: enum                     # routine | notable | major | historic

  # Metadata
  source: string
  confidence: float
  last_updated: timestamp
  update_frequency: weekly
```

---

## DATA STORAGE FORMAT

For the static-site architecture, all data is stored as JSON files:

```
/data
├── /countries
│   ├── USA.json          # All layers 1-4 + layer 6 for one country
│   ├── CHN.json
│   ├── DEU.json
│   └── ...
├── /relations
│   ├── USA_CHN.json      # Bilateral relation
│   ├── USA_RUS.json
│   └── ...
├── /supranational
│   ├── EU.json
│   ├── NATO.json
│   └── ...
├── /indices
│   ├── country_list.json         # Master list with basic metadata
│   ├── relation_index.json       # Index of all bilateral pairs
│   ├── supranational_index.json
│   ├── resource_index.json       # Cross-reference: resource → countries
│   └── alert_index.json          # All active alerts across countries
├── /timeseries
│   ├── USA_gdp.json              # Historical values for key metrics
│   ├── USA_military_expenditure.json
│   └── ...
├── /metadata
│   ├── schema_version.json
│   ├── last_update.json          # When was the dataset last refreshed?
│   ├── data_sources.json         # Registry of all sources used
│   └── update_log.json           # Log of what changed in each update cycle
└── /global
    ├── global_rankings.json      # Pre-computed rankings for quick display
    ├── chokepoints.json          # Strategic waterways and land corridors
    └── event_feed.json           # Recent events affecting the model
```

---

## COUNTRY SCOPE

### Tier 1: Major Economies & Powers (30 countries)
Core investable markets. Full factor coverage required.

USA, CHN, JPN, DEU, GBR, FRA, IND, ITA, CAN, KOR,
RUS, BRA, AUS, ESP, MEX, IDN, NLD, SAU, TUR, CHE,
POL, SWE, NOR, ISR, ARE, SGP, TWN, THA, MYS, ZAF

### Tier 2: Important Regional Players (25 countries)
Significant for regional dynamics or specific investment themes.

NGA, EGY, PAK, BGD, VNM, PHL, COL, ARG, CHL, PER,
IRN, IRQ, KAZ, UKR, ROU, CZE, GRC, PRT, FIN, IRL,
NZL, QAT, KWT, OMN, MAR

### Tier 3: Frontier / Watchlist (20 countries)
Monitored at reduced detail. Escalate to Tier 2 on significant events.

ETH, KEN, TZA, GHA, CIV, SEN, AGO, MOZ, COD,
MMR, LKA, UZB, AZE, GEO, SRB, HUN, BGR, HRV,
JOR, LBY

---

## NEXT STEPS

1. Agent architecture specification → `02_AGENT_ARCHITECTURE.md`
2. Requirements document → `03_REQUIREMENTS.md`
3. Test plan → `04_TEST_PLAN.md`
4. Claude Code agent configurations → `05_AGENT_CONFIGS.md`
5. Web UI specification → `06_WEB_UI_SPEC.md`
6. Data source registry → `07_DATA_SOURCES.md`
