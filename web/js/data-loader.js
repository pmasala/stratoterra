/* ==========================================================================
   Stratoterra — Data Loader (with i18n-aware localized content support)
   ========================================================================== */

var DataLoader = (function() {
  var cache = {};
  var summaryData = null;
  var summaryMap = {};
  var basePath = '';
  var translationManifest = null;
  var availableLanguages = null;

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

  function wait(ms) { return new Promise(function(r) { setTimeout(r, ms); }); }

  /**
   * Resolve a chunk path to a localized version if available.
   * For non-English languages, tries the _LANG.json variant first,
   * falls back to the English original.
   */
  function localizedChunkPath(relativePath) {
    var lang = (typeof I18n !== 'undefined') ? I18n.getLang() : 'en';
    if (lang === 'en' || !hasLanguage(lang)) {
      return chunkPath(relativePath);
    }
    // Insert language suffix before .json
    var localized = relativePath.replace(/\.json$/, '_' + lang + '.json');
    return chunkPath(localized);
  }

  /**
   * Check if translations exist for a given language.
   */
  function hasLanguage(lang) {
    if (!availableLanguages) return false;
    return availableLanguages.indexOf(lang) !== -1;
  }

  /**
   * Fetch JSON with localization fallback: try localized file first,
   * fall back to English original if the localized version doesn't exist.
   */
  async function fetchLocalizedJSON(relativePath, retries) {
    var lang = (typeof I18n !== 'undefined') ? I18n.getLang() : 'en';
    if (lang !== 'en' && hasLanguage(lang)) {
      var localizedPath = relativePath.replace(/\.json$/, '_' + lang + '.json');
      try {
        return await fetchJSON(chunkPath(localizedPath), 0);
      } catch (e) {
        // Localized version not available, fall back to English
      }
    }
    return fetchJSON(chunkPath(relativePath), retries);
  }

  async function fetchJSON(path, retries) {
    if (cache[path]) return cache[path];
    retries = retries != null ? retries : 3;
    var lastErr;
    for (var attempt = 0; attempt <= retries; attempt++) {
      try {
        var response = await fetch(path);
        if (!response.ok) throw new Error('HTTP ' + response.status + ' loading ' + path);
        var data = await response.json();
        cache[path] = data;
        return data;
      } catch (err) {
        lastErr = err;
        if (attempt < retries) {
          var delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
          console.warn('[DataLoader] Retry ' + (attempt + 1) + '/' + retries + ' for:', path, '(' + delay + 'ms)');
          await wait(delay);
        }
      }
    }
    console.error('[DataLoader] Failed to load after ' + retries + ' retries:', path, lastErr.message);
    throw lastErr;
  }

  return {
    async init() {
      detectBasePath();

      // Try to load translation manifest to know which languages are available
      try {
        translationManifest = await fetchJSON(chunkPath('translation_manifest.json'), 0);
        availableLanguages = translationManifest.target_languages || [];
        console.log('[DataLoader] Translation manifest loaded. Available languages:', availableLanguages);
      } catch (e) {
        translationManifest = null;
        availableLanguages = [];
      }

      try {
        var raw = await fetchLocalizedJSON('country-summary/all_countries_summary.json');
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

    getTranslationManifest() {
      return translationManifest;
    },

    getAvailableLanguages() {
      return availableLanguages || [];
    },

    async getCountryDetail(code) {
      return fetchLocalizedJSON('country-detail/' + code + '.json');
    },

    async getTimeseries(code, category) {
      // Timeseries are numeric — no localization needed
      return fetchJSON(chunkPath('timeseries/' + code + '_' + category + '.json'));
    },

    async getBriefing() {
      return fetchLocalizedJSON('global/weekly_briefing.json');
    },

    async getAlerts() {
      return fetchLocalizedJSON('global/alert_index.json');
    },

    async getRankings() {
      return fetchLocalizedJSON('global/global_rankings.json');
    },

    async getSupranational(id) {
      return fetchLocalizedJSON('supranational/' + id + '.json');
    },

    async getRelationIndex() {
      // Relation index is structural — no localization needed
      return fetchJSON(chunkPath('relations/relation_index.json'));
    },

    async getRelation(codeA, codeB) {
      // Alphabetically ordered pair
      var pair = [codeA, codeB].sort().join('_');
      return fetchLocalizedJSON('relations/' + pair + '.json');
    },

    async getArticleIndex() {
      return fetchLocalizedJSON('global/article_index.json');
    },

    async getArticle(articleId) {
      return fetchLocalizedJSON('global/articles/' + articleId + '.json');
    },

    async getOverlayLayer(layerId) {
      // Overlay layers are geographic data — no localization needed
      return fetchJSON(chunkPath('global/overlays/' + layerId + '.json'));
    },

    async getChokepoints() {
      return fetchJSON(dataPath('global/chokepoints.json'));
    },

    async getCountryList() {
      return fetchJSON(dataPath('indices/country_list.json'));
    },

    clearCache() {
      cache = {};
    },

    /**
     * Reload all data for a new language.
     * Called when the user switches language.
     */
    async reloadForLanguage() {
      // Clear cache so localized files are fetched fresh
      cache = {};
      summaryData = null;
      summaryMap = {};
      await this.init();
    }
  };
})();
