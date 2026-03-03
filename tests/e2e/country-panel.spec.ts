import { test, expect } from '@playwright/test';
import { waitForAppInit, openCountryViaSearch, closePanel, collectPageErrors, trackFailedRequests } from './fixtures/test-helpers';

test.describe('Country Panel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('opens via search and shows country name', async ({ page }) => {
    await openCountryViaSearch(page, 'United States', 'USA');
    await expect(page.locator('.panel-header__title')).toContainText('United States');
  });

  test('close button (X) closes the panel', async ({ page }) => {
    await openCountryViaSearch(page, 'Germany', 'DEU');
    await closePanel(page);
    await expect(page.locator('#country-panel')).not.toHaveClass(/open/);
  });

  test('back button closes the panel', async ({ page }) => {
    await openCountryViaSearch(page, 'France', 'FRA');
    await page.locator('#panel-close-btn').click();
    await expect(page.locator('#country-panel')).not.toHaveClass(/open/);
  });

  test('Escape key closes the panel', async ({ page }) => {
    await openCountryViaSearch(page, 'Japan', 'JPN');
    await page.keyboard.press('Escape');
    await expect(page.locator('#country-panel')).not.toHaveClass(/open/);
  });

  test('panel shows 6 layer tabs (detail data loaded, not fallback)', async ({ page }) => {
    await openCountryViaSearch(page, 'United States', 'USA');

    // Verify real detail data loaded — fallback state shows .panel-no-data, not tabs
    await expect(page.locator('#country-panel .panel-no-data')).toHaveCount(0);

    const tabs = page.locator('#layer-tabs .layer-tab');
    await expect(tabs).toHaveCount(6);

    const expectedTabs = ['Endowments', 'Institutions', 'Economy', 'Military', 'Relations', 'Derived'];
    for (let i = 0; i < expectedTabs.length; i++) {
      await expect(tabs.nth(i)).toContainText(expectedTabs[i]);
    }
  });

  test('Economy tab is active by default', async ({ page }) => {
    await openCountryViaSearch(page, 'China', 'CHN');
    await expect(page.locator('.layer-tab[data-tab="economy"]')).toHaveClass(/active/);
    await expect(page.locator('#tab-economy')).toHaveClass(/active/);
  });

  test('clicking a tab switches content', async ({ page }) => {
    await openCountryViaSearch(page, 'India', 'IND');

    // Click Military tab
    await page.locator('.layer-tab[data-tab="military"]').click();
    await expect(page.locator('.layer-tab[data-tab="military"]')).toHaveClass(/active/);
    await expect(page.locator('#tab-military')).toHaveClass(/active/);
    await expect(page.locator('#tab-economy')).not.toHaveClass(/active/);
  });

  test('panel shows executive summary', async ({ page }) => {
    await openCountryViaSearch(page, 'United States', 'USA');
    await expect(page.locator('.exec-summary')).toBeVisible();
    const text = await page.locator('.exec-summary').textContent();
    expect(text!.length).toBeGreaterThan(10);
  });

  test('factor cards display formatted values', async ({ page }) => {
    await openCountryViaSearch(page, 'United States', 'USA');
    const values = page.locator('.factor-card__value');
    const count = await values.count();
    expect(count).toBeGreaterThan(0);
  });

  test('switching countries updates the panel', async ({ page }) => {
    await openCountryViaSearch(page, 'Japan', 'JPN');
    await expect(page.locator('.panel-header__title')).toContainText('Japan');

    // Open a different country
    await openCountryViaSearch(page, 'Brazil', 'BRA');
    await expect(page.locator('.panel-header__title')).toContainText('Brazil');
  });

  test('panel-open class added to main-content', async ({ page }) => {
    await openCountryViaSearch(page, 'Germany', 'DEU');
    await expect(page.locator('#main-content')).toHaveClass(/panel-open/);

    await closePanel(page);
    await expect(page.locator('#main-content')).not.toHaveClass(/panel-open/);
  });

  test('Relations tab shows all T1 bilateral partners for USA (29 expected)', async ({ page }) => {
    await openCountryViaSearch(page, 'United States', 'USA');

    // Navigate to the Relations tab
    await page.locator('.layer-tab[data-tab="relations"]').click();
    await expect(page.locator('.layer-tab[data-tab="relations"]')).toHaveClass(/active/);
    await expect(page.locator('#tab-relations')).toHaveClass(/active/);

    // Wait for partner cards to appear (relation index is fetched async)
    await page.waitForFunction(
      () => document.querySelectorAll('#tab-relations .factor-card').length >= 29,
      { timeout: 10_000 },
    );

    const partnerCards = page.locator('#tab-relations .factor-card');
    const count = await partnerCards.count();
    expect(count, `Relations tab should show all 29 T1 bilateral partners, got ${count}`).toBeGreaterThanOrEqual(29);
  });

  test('Relations tab shows partners for another T1 country (CHN, 29 expected)', async ({ page }) => {
    await openCountryViaSearch(page, 'China', 'CHN');

    await page.locator('.layer-tab[data-tab="relations"]').click();
    await expect(page.locator('#tab-relations')).toHaveClass(/active/);

    await page.waitForFunction(
      () => document.querySelectorAll('#tab-relations .factor-card').length >= 29,
      { timeout: 10_000 },
    );

    const count = await page.locator('#tab-relations .factor-card').count();
    expect(count, `CHN Relations tab should show 29 T1 partners, got ${count}`).toBeGreaterThanOrEqual(29);
  });

  // Seed countries: verify 5 important countries render without errors
  const seedCountries = [
    { name: 'United States', code: 'USA' },
    { name: 'China', code: 'CHN' },
    { name: 'Germany', code: 'DEU' },
    { name: 'Russia', code: 'RUS' },
    { name: 'India', code: 'IND' },
  ];

  for (const { name, code } of seedCountries) {
    test(`${code} panel renders with real data, no errors`, async ({ page }) => {
      const errors = collectPageErrors(page);
      const failed = trackFailedRequests(page);
      await openCountryViaSearch(page, name, code);

      // Check that key sections exist
      await expect(page.locator('.panel-header__title')).toContainText(name);

      // Verify real detail data loaded, not the "no data" fallback
      await expect(page.locator('#country-panel .panel-no-data')).toHaveCount(0);

      // Check that at least some factor cards rendered
      const cardCount = await page.locator('.factor-card').count();
      expect(cardCount).toBeGreaterThan(0);

      // No failed network requests
      expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);

      // No JS errors
      expect(errors).toEqual([]);
    });
  }
});
