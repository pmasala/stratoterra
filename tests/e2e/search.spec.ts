import { test, expect } from '@playwright/test';
import { waitForAppInit } from './fixtures/test-helpers';

/** Type into the search input character by character to reliably trigger the debounced handler. */
async function typeSearch(page: import('@playwright/test').Page, query: string) {
  const input = page.locator('#search');
  await input.click();
  await input.fill('');
  await input.type(query, { delay: 10 });
}

test.describe('Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('typing a query shows dropdown with results', async ({ page }) => {
    await typeSearch(page, 'United');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    const items = page.locator('.search-dropdown__item');
    await expect(items.first()).toBeVisible();
  });

  test('results filter by country name', async ({ page }) => {
    await typeSearch(page, 'Japan');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    const items = page.locator('.search-dropdown__item');
    const count = await items.count();
    expect(count).toBeGreaterThanOrEqual(1);
    await expect(items.first()).toContainText('Japan');
  });

  test('ISO code search works', async ({ page }) => {
    await typeSearch(page, 'DEU');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    await expect(page.locator('.search-dropdown__item[data-code="DEU"]')).toBeVisible();
  });

  test('dropdown closes on Escape', async ({ page }) => {
    await typeSearch(page, 'France');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    await page.locator('#search').press('Escape');
    await expect(page.locator('.search-dropdown')).not.toHaveClass(/open/);
  });

  test('arrow keys navigate dropdown items', async ({ page }) => {
    await typeSearch(page, 'United');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });

    await page.locator('#search').press('ArrowDown');
    await expect(page.locator('.search-dropdown__item.active')).toHaveCount(1);

    await page.locator('#search').press('ArrowDown');
    // Second item is now active
    const activeItems = page.locator('.search-dropdown__item.active');
    await expect(activeItems).toHaveCount(1);
  });

  test('Enter selects the active dropdown item', async ({ page }) => {
    await typeSearch(page, 'Brazil');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    await page.locator('#search').press('ArrowDown');
    await page.locator('#search').press('Enter');

    // Panel should open
    await page.waitForSelector('#country-panel.open', { timeout: 10_000 });
    await expect(page.locator('#country-panel')).toHaveClass(/open/);
  });

  test('clicking a result opens country panel', async ({ page }) => {
    await typeSearch(page, 'China');
    await page.waitForSelector('.search-dropdown__item[data-code="CHN"]', { timeout: 5_000 });
    await page.locator('.search-dropdown__item[data-code="CHN"]').click();

    await page.waitForSelector('#country-panel.open .panel-header__title', { timeout: 10_000 });
    await expect(page.locator('.panel-header__title')).toContainText('China');
  });

  test('max 8 results shown', async ({ page }) => {
    // Single letter should match many countries
    await typeSearch(page, 'a');
    await page.waitForSelector('.search-dropdown.open', { timeout: 5_000 });
    const count = await page.locator('.search-dropdown__item').count();
    expect(count).toBeLessThanOrEqual(8);
  });

  test('search input clears after selection', async ({ page }) => {
    await typeSearch(page, 'India');
    await page.waitForSelector('.search-dropdown__item[data-code="IND"]', { timeout: 5_000 });
    await page.locator('.search-dropdown__item[data-code="IND"]').click();
    await expect(page.locator('#search')).toHaveValue('');
  });

  test('/ keyboard shortcut focuses search', async ({ page }) => {
    await page.keyboard.press('/');
    await expect(page.locator('#search')).toBeFocused();
  });
});
