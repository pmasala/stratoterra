/* ==========================================================================
   Stratoterra — Data Loader
   ========================================================================== */

var DataLoader = (function() {
  var cache = {};
  var summaryData = null;
  var summaryMap = {};
  var basePath = '';

  function detectBasePath() {
    // Support both local file and served via HTTP
    var scripts = document.getElementsByTagName('script');
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].src && scripts[i].src.indexOf('data-loader.js') !== -1) {
        var src = scripts[i].src;
        var idx = src.lastIndexOf('/js/');
        if (idx !== -1) {
          basePath = src.substring(0, idx + 1);
          return;
        }
      }
    }
  }

  function dataPath(relativePath) {
    // Data files are at ../data/ relative to web/
    return basePath + '../data/' + relativePath;
  }

  function chunkPath(relativePath) {
    return dataPath('chunks/' + relativePath);
  }

  async function fetchJSON(path) {
    if (cache[path]) return cache[path];
    try {
      var response = await fetch(path);
      if (!response.ok) throw new Error('HTTP ' + response.status + ' loading ' + path);
      var data = await response.json();
      cache[path] = data;
      return data;
    } catch (err) {
      console.error('[DataLoader] Failed to load:', path, err.message);
      throw err;
    }
  }

  return {
    async init() {
      detectBasePath();
      try {
        var raw = await fetchJSON(chunkPath('country-summary/all_countries_summary.json'));
        // Handle both bare array and wrapper dict {countries: [...]}
        if (Array.isArray(raw)) {
          summaryData = raw;
        } else if (raw && Array.isArray(raw.countries)) {
          summaryData = raw.countries;
          // Preserve metadata for getSummaryMeta()
          summaryData._meta = { generated_at: raw.generated_at, run_id: raw.run_id };
        } else {
          summaryData = [];
        }
        // Build lookup map
        summaryData.forEach(function(c) { summaryMap[c.code] = c; });
        return summaryData;
      } catch (err) {
        console.warn('[DataLoader] Summary data not yet available:', err.message);
        summaryData = [];
        return summaryData;
      }
    },

    getSummary() {
      return summaryData || [];
    },

    getSummaryMeta() {
      return (summaryData && summaryData._meta) || {};
    },

    getSummaryByCode(code) {
      return summaryMap[code] || null;
    },

    async getCountryDetail(code) {
      return fetchJSON(chunkPath('country-detail/' + code + '.json'));
    },

    async getTimeseries(code, category) {
      return fetchJSON(chunkPath('timeseries/' + code + '_' + category + '.json'));
    },

    async getBriefing() {
      return fetchJSON(chunkPath('global/weekly_briefing.json'));
    },

    async getAlerts() {
      return fetchJSON(chunkPath('global/alert_index.json'));
    },

    async getRankings() {
      return fetchJSON(chunkPath('global/global_rankings.json'));
    },

    async getSupranational(id) {
      return fetchJSON(chunkPath('supranational/' + id + '.json'));
    },

    async getRelationIndex() {
      return fetchJSON(chunkPath('relations/relation_index.json'));
    },

    async getRelation(codeA, codeB) {
      // Alphabetically ordered pair
      var pair = [codeA, codeB].sort().join('_');
      return fetchJSON(chunkPath('relations/' + pair + '.json'));
    },

    async getArticleIndex() {
      return fetchJSON(chunkPath('global/article_index.json'));
    },

    async getArticle(articleId) {
      return fetchJSON(chunkPath('global/articles/' + articleId + '.json'));
    },

    async getChokepoints() {
      return fetchJSON(dataPath('global/chokepoints.json'));
    },

    async getCountryList() {
      return fetchJSON(dataPath('indices/country_list.json'));
    },

    clearCache() {
      cache = {};
    }
  };
})();
