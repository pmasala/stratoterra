import { test, expect } from '@playwright/test';
import { waitForAppInit } from './fixtures/test-helpers';

test.describe('Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('typing a query shows dropdown with results', async ({ page }) => {
    await page.fill('#search', 'United');
    await page.waitForSelector('.search-dropdown.open', { timeout: 3_000 });
    const items = page.locator('.search-dropdown__item');
    await expect(items.first()).toBeVisible();
  });

  test('results filter by country name', async ({ page }) => {
    await page.fill('#search', 'Japan');
    await page.waitForSelector('.search-dropdown.open');
    const items = page.locator('.search-dropdown__item');
    const count = await items.count();
    expect(count).toBeGreaterThanOrEqual(1);
    await expect(items.first()).toContainText('Japan');
  });

  test('ISO code search works', async ({ page }) => {
    await page.fill('#search', 'DEU');
    await page.waitForSelector('.search-dropdown.open');
    await expect(page.locator('.search-dropdown__item[data-code="DEU"]')).toBeVisible();
  });

  test('dropdown closes on Escape', async ({ page }) => {
    await page.fill('#search', 'France');
    await page.waitForSelector('.search-dropdown.open');
    await page.locator('#search').press('Escape');
    await expect(page.locator('.search-dropdown')).not.toHaveClass(/open/);
  });

  test('arrow keys navigate dropdown items', async ({ page }) => {
    await page.fill('#search', 'United');
    await page.waitForSelector('.search-dropdown.open');

    await page.locator('#search').press('ArrowDown');
    await expect(page.locator('.search-dropdown__item.active')).toHaveCount(1);

    await page.locator('#search').press('ArrowDown');
    // Second item is now active
    const activeItems = page.locator('.search-dropdown__item.active');
    await expect(activeItems).toHaveCount(1);
  });

  test('Enter selects the active dropdown item', async ({ page }) => {
    await page.fill('#search', 'Brazil');
    await page.waitForSelector('.search-dropdown.open');
    await page.locator('#search').press('ArrowDown');
    await page.locator('#search').press('Enter');

    // Panel should open
    await page.waitForSelector('#country-panel.open', { timeout: 10_000 });
    await expect(page.locator('#country-panel')).toHaveClass(/open/);
  });

  test('clicking a result opens country panel', async ({ page }) => {
    await page.fill('#search', 'China');
    await page.waitForSelector('.search-dropdown__item[data-code="CHN"]');
    await page.locator('.search-dropdown__item[data-code="CHN"]').click();

    await page.waitForSelector('#country-panel.open .panel-header__title', { timeout: 10_000 });
    await expect(page.locator('.panel-header__title')).toContainText('China');
  });

  test('max 8 results shown', async ({ page }) => {
    // Single letter should match many countries
    await page.fill('#search', 'a');
    await page.waitForSelector('.search-dropdown.open');
    const count = await page.locator('.search-dropdown__item').count();
    expect(count).toBeLessThanOrEqual(8);
  });

  test('search input clears after selection', async ({ page }) => {
    await page.fill('#search', 'India');
    await page.waitForSelector('.search-dropdown__item[data-code="IND"]');
    await page.locator('.search-dropdown__item[data-code="IND"]').click();
    await expect(page.locator('#search')).toHaveValue('');
  });

  test('/ keyboard shortcut focuses search', async ({ page }) => {
    await page.keyboard.press('/');
    await expect(page.locator('#search')).toBeFocused();
  });
});
