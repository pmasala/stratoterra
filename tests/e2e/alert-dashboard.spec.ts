import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

test.describe('Alert Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'alerts');
  });

  test('alerts load real data, not error state', async ({ page }) => {
    await page.waitForSelector('.alerts-dashboard, .error-card', { timeout: 10_000 });
    await expect(page.locator('.error-card')).toHaveCount(0);
    await expect(page.locator('.alerts-dashboard')).toBeVisible();
  });

  test('alert dashboard title is visible', async ({ page }) => {
    await page.waitForSelector('.alerts-dashboard h2', { timeout: 10_000 });
    await expect(page.locator('.alerts-dashboard h2')).toHaveText('Alert Dashboard');
  });

  test('alert cards are loaded', async ({ page }) => {
    await page.waitForSelector('.alert-card', { timeout: 10_000 });
    const cards = page.locator('.alert-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('summary bar shows severity counts', async ({ page }) => {
    await page.waitForSelector('.alert-summary-bar', { timeout: 10_000 });
    await expect(page.locator('.alert-summary-count--critical')).toBeVisible();
    await expect(page.locator('.alert-summary-count--warning')).toBeVisible();
    await expect(page.locator('.alert-summary-count--watch')).toBeVisible();

    // Each count has a number
    const criticalNum = await page.locator('.alert-summary-count--critical .alert-summary-count__num').textContent();
    expect(Number(criticalNum)).toBeGreaterThanOrEqual(0);
  });

  test('filter dropdowns are present', async ({ page }) => {
    await page.waitForSelector('.alert-filters', { timeout: 10_000 });
    await expect(page.locator('#alert-region-filter')).toBeVisible();
    await expect(page.locator('#alert-type-filter')).toBeVisible();
  });

  test('alert sections are grouped by severity', async ({ page }) => {
    await page.waitForSelector('.alert-section', { timeout: 10_000 });
    const sections = page.locator('.alert-section');
    const count = await sections.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Each section has a title
    await expect(sections.first().locator('.alert-section__title')).toBeVisible();
  });

  test('alert card structure has badge, title, body', async ({ page }) => {
    await page.waitForSelector('.alert-card', { timeout: 10_000 });
    const card = page.locator('.alert-card').first();

    await expect(card.locator('.alert-badge')).toBeVisible();
    await expect(card.locator('.alert-card__title')).toBeVisible();
    await expect(card.locator('.alert-card__body')).toBeVisible();
  });
});
