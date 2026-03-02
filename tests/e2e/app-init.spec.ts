import { test, expect } from '@playwright/test';
import { waitForAppInit, collectPageErrors, trackFailedRequests } from './fixtures/test-helpers';

test.describe('App Initialization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('page loads with correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/Stratoterra/);
  });

  test('map container is visible', async ({ page }) => {
    await expect(page.locator('#map-container')).toBeVisible();
  });

  test('75 countries loaded in summary data', async ({ page }) => {
    const count = await page.evaluate(() => (window as any).DataLoader.getSummary().length);
    expect(count).toBe(75);
  });

  test('navigation links are present for all 6 views', async ({ page }) => {
    const navLinks = page.locator('#main-nav .nav-link');
    await expect(navLinks).toHaveCount(6);

    const expectedViews = ['map', 'briefing', 'alerts', 'rankings', 'relations', 'compare'];
    for (const view of expectedViews) {
      await expect(page.locator(`.nav-link[data-view="${view}"]`)).toBeVisible();
    }
  });

  test('bottom bar with metric and overlay selectors is visible', async ({ page }) => {
    await expect(page.locator('#bottom-bar')).toBeVisible();
    await expect(page.locator('#metric-select')).toBeVisible();
    await expect(page.locator('#overlay-select')).toBeVisible();
  });

  test('no JavaScript errors on load', async ({ page }) => {
    // Re-load with error listener
    const errors = collectPageErrors(page);
    await page.goto('./');
    await waitForAppInit(page);
    expect(errors).toEqual([]);
  });

  test('no failed network requests on initial load', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);
    expect(failed, `Failed data requests on load: ${failed.join(', ')}`).toEqual([]);
  });
});
