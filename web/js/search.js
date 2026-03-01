/* ==========================================================================
   Stratoterra — Search Autocomplete
   ========================================================================== */

var Search = (function() {
  var inputEl = null;
  var dropdownEl = null;
  var results = [];
  var activeIndex = -1;
  var onSelect = null;

  function filter(query) {
    if (!query || query.length < 1) return [];
    var q = query.toLowerCase();
    var summary = DataLoader.getSummary();
    return summary.filter(function(c) {
      return c.name.toLowerCase().indexOf(q) !== -1 || c.code.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 8);
  }

  function render() {
    if (results.length === 0) {
      dropdownEl.classList.remove('open');
      return;
    }

    var html = '';
    results.forEach(function(c, i) {
      var cls = i === activeIndex ? 'search-dropdown__item active' : 'search-dropdown__item';
      var regionLabel = REGIONS[c.region] ? REGIONS[c.region].label : c.region;
      html += '<div class="' + cls + '" data-code="' + c.code + '">';
      html += '<span>' + escHtml(c.name) + '</span>';
      html += '<span class="search-dropdown__item-region">' + escHtml(regionLabel) + '</span>';
      html += '</div>';
    });
    dropdownEl.innerHTML = html;
    dropdownEl.classList.add('open');
  }

  function selectResult(code) {
    inputEl.value = '';
    dropdownEl.classList.remove('open');
    results = [];
    activeIndex = -1;
    if (onSelect) onSelect(code);
  }

  function escHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  return {
    init: function(input, dropdown, selectCallback) {
      inputEl = input;
      dropdownEl = dropdown;
      onSelect = selectCallback;

      inputEl.addEventListener('input', Utils.debounce(function() {
        results = filter(inputEl.value);
        activeIndex = -1;
        render();
      }, 150));

      inputEl.addEventListener('keydown', function(e) {
        if (results.length === 0) return;

        if (e.key === 'ArrowDown') {
          e.preventDefault();
          activeIndex = Math.min(activeIndex + 1, results.length - 1);
          render();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          activeIndex = Math.max(activeIndex - 1, 0);
          render();
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (activeIndex >= 0 && activeIndex < results.length) {
            selectResult(results[activeIndex].code);
          }
        } else if (e.key === 'Escape') {
          dropdownEl.classList.remove('open');
          results = [];
          activeIndex = -1;
        }
      });

      dropdownEl.addEventListener('click', function(e) {
        var item = e.target.closest('.search-dropdown__item');
        if (item) selectResult(item.getAttribute('data-code'));
      });

      document.addEventListener('click', function(e) {
        if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
          dropdownEl.classList.remove('open');
        }
      });
    }
  };
})();
