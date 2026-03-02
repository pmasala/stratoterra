import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

test.describe('Comparison View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'compare');
  });

  test('comparison title and search input visible', async ({ page }) => {
    await expect(page.locator('.comparison h2')).toHaveText('Country Comparison');
    await expect(page.locator('#compare-search')).toBeVisible();
  });

  test('adding 2 countries shows comparison table', async ({ page }) => {
    // Add first country
    await page.fill('#compare-search', 'United States');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="USA"]').click();

    // Add second country
    await page.fill('#compare-search', 'China');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="CHN"]').click();

    // Table should appear
    await expect(page.locator('.rankings-table')).toBeVisible();
    // Both countries appear as tags
    await expect(page.locator('.compare-tag')).toHaveCount(2);
  });

  test('table and radar mode toggle works', async ({ page }) => {
    // Add two countries first
    await page.fill('#compare-search', 'Germany');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="DEU"]').click();

    await page.fill('#compare-search', 'France');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="FRA"]').click();

    // Table mode is default
    await expect(page.locator('.layer-tab[data-mode="table"]')).toHaveClass(/active/);
    await expect(page.locator('.rankings-table')).toBeVisible();

    // Switch to radar
    await page.locator('.layer-tab[data-mode="radar"]').click();
    await expect(page.locator('.layer-tab[data-mode="radar"]')).toHaveClass(/active/);
    await expect(page.locator('#radar-canvas')).toBeVisible();
  });

  test('removing a country updates comparison', async ({ page }) => {
    // Add two countries
    await page.fill('#compare-search', 'Japan');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="JPN"]').click();

    await page.fill('#compare-search', 'India');
    await page.waitForSelector('#compare-dropdown.open');
    await page.locator('#compare-dropdown .search-dropdown__item[data-code="IND"]').click();

    await expect(page.locator('.compare-tag')).toHaveCount(2);

    // Remove first country
    await page.locator('.compare-tag__remove[data-code="JPN"]').click();
    await expect(page.locator('.compare-tag')).toHaveCount(1);
  });

  test('max 5 countries limit', async ({ page }) => {
    const countries = [
      { name: 'United States', code: 'USA' },
      { name: 'China', code: 'CHN' },
      { name: 'Germany', code: 'DEU' },
      { name: 'Japan', code: 'JPN' },
      { name: 'India', code: 'IND' },
    ];

    for (const { name, code } of countries) {
      await page.fill('#compare-search', name);
      await page.waitForSelector('#compare-dropdown.open');
      await page.locator(`#compare-dropdown .search-dropdown__item[data-code="${code}"]`).click();
    }

    await expect(page.locator('.compare-tag')).toHaveCount(5);
    // Search input should not be visible at max capacity
    await expect(page.locator('#compare-search')).toHaveCount(0);
  });
});
