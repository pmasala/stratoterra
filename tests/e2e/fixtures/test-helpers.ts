import { type Page, expect } from '@playwright/test';

/**
 * Track failed network requests (4xx/5xx) for JSON data files.
 * Call before page.goto(), then check failedRequests after the page loads.
 */
export function trackFailedRequests(page: Page): string[] {
  const failed: string[] = [];
  page.on('response', (response) => {
    const url = response.url();
    if (url.match(/\.(json|geojson)(\?|$)/) && response.status() >= 400) {
      failed.push(`${response.status()} ${url}`);
    }
  });
  return failed;
}

/**
 * Wait for the Stratoterra app to fully initialize:
 * - DOM ready
 * - DataLoader.getSummary() returns 75 countries
 * - Map container visible
 */
export async function waitForAppInit(page: Page) {
  // Wait for the map container to exist in DOM (app bootstrapped)
  // Note: map may be hidden if loaded with a non-map hash route
  await page.waitForSelector('#map-container', { state: 'attached', timeout: 15_000 });

  // Wait for summary data to load (75 countries)
  await page.waitForFunction(
    () => {
      try {
        return (window as any).DataLoader?.getSummary()?.length === 75;
      } catch {
        return false;
      }
    },
    { timeout: 15_000 },
  );
}

/**
 * Open a country panel by typing into the search box and clicking the result.
 */
export async function openCountryViaSearch(page: Page, name: string, code: string) {
  const searchInput = page.locator('#search');
  await searchInput.fill(name);
  // Wait for dropdown to appear with the matching result
  await page.waitForSelector(`.search-dropdown__item[data-code="${code}"]`, { timeout: 5_000 });
  await page.locator(`.search-dropdown__item[data-code="${code}"]`).click();
  // Wait for panel to open and finish loading (panel-header__title shows country name)
  await page.waitForSelector('#country-panel.open .panel-header__title', { timeout: 10_000 });
}

/**
 * Close the country panel and wait for it to hide.
 */
export async function closePanel(page: Page) {
  await page.locator('#panel-close-x').click();
  // Panel adds .hidden after 400ms transition
  await page.waitForFunction(
    () => {
      const panel = document.getElementById('country-panel');
      return panel && !panel.classList.contains('open');
    },
    { timeout: 3_000 },
  );
}

/**
 * Navigate to a view by hash and wait for the container to become active.
 */
export async function navigateToView(page: Page, view: string) {
  const containerMap: Record<string, string> = {
    map: '#map-container',
    briefing: '#briefing-view.active',
    alerts: '#alerts-view.active',
    rankings: '#rankings-view.active',
    relations: '#relations-view.active',
    compare: '#compare-view.active',
  };
  await page.evaluate((v) => { window.location.hash = '#' + v; }, view);
  const selector = containerMap[view];
  if (view === 'map') {
    await page.waitForSelector(selector, { state: 'visible', timeout: 5_000 });
  } else {
    await page.waitForSelector(selector, { timeout: 5_000 });
  }
}

/**
 * Collect console errors during a test. Returns the error list.
 */
export function collectPageErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on('pageerror', (err) => errors.push(err.message));
  return errors;
}

/**
 * Click a layer tab in the country panel and wait for it to become active.
 */
export async function clickLayerTab(page: Page, tabId: string) {
  await page.locator(`.layer-tab[data-tab="${tabId}"]`).click();
  await expect(page.locator(`.layer-tab[data-tab="${tabId}"]`)).toHaveClass(/active/);
  await expect(page.locator(`#tab-${tabId}`)).toHaveClass(/active/);
}

/**
 * Assert that a factor card with the given label shows a real value (not "—", "null", or empty).
 * Searches within `container` selector if provided, otherwise within `#country-panel`.
 */
export async function expectFactorCardPopulated(page: Page, label: string, container?: string) {
  const scope = container ? page.locator(container) : page.locator('#country-panel');
  // Find the factor-card that contains this label
  const cards = scope.locator('.factor-card');
  const count = await cards.count();
  let found = false;
  for (let i = 0; i < count; i++) {
    const card = cards.nth(i);
    const cardLabel = await card.locator('.factor-card__label').textContent();
    if (cardLabel?.trim() === label) {
      const value = await card.locator('.factor-card__value').textContent();
      expect(value?.trim(), `"${label}" should have a real value, got "${value}"`).not.toBe('—');
      expect(value?.trim(), `"${label}" should not be null`).not.toBe('null');
      expect(value?.trim(), `"${label}" should not be empty`).toBeTruthy();
      found = true;
      break;
    }
  }
  expect(found, `Factor card with label "${label}" not found`).toBe(true);
}
