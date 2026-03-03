import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('clicking nav links switches views', async ({ page }) => {
    // Click Briefing
    await page.locator('[data-view="briefing"]').click();
    await expect(page.locator('#briefing-view')).toHaveClass(/active/);
    await expect(page.locator('#map-container')).toBeHidden();

    // Click Alerts
    await page.locator('[data-view="alerts"]').click();
    await expect(page.locator('#alerts-view')).toHaveClass(/active/);
    await expect(page.locator('#briefing-view')).not.toHaveClass(/active/);
  });

  test('hash changes on navigation', async ({ page }) => {
    await page.locator('[data-view="rankings"]').click();
    await expect(page).toHaveURL(/#rankings/);

    await page.locator('[data-view="map"]').click();
    await expect(page).toHaveURL(/#map/);
  });

  test('keyboard shortcuts 1-5 navigate views', async ({ page }) => {
    await page.keyboard.press('2');
    await expect(page.locator('#briefing-view')).toHaveClass(/active/);

    await page.keyboard.press('3');
    await expect(page.locator('#alerts-view')).toHaveClass(/active/);

    await page.keyboard.press('4');
    await expect(page.locator('#rankings-view')).toHaveClass(/active/);

    await page.keyboard.press('5');
    await expect(page.locator('#compare-view')).toHaveClass(/active/);

    await page.keyboard.press('1');
    await expect(page.locator('#map-container')).toBeVisible();
  });

  test('bottom bar hides on non-map views and shows on map', async ({ page }) => {
    await navigateToView(page, 'briefing');
    await expect(page.locator('#bottom-bar')).toBeHidden();

    await navigateToView(page, 'map');
    await expect(page.locator('#bottom-bar')).toBeVisible();
  });

  test('active nav link updates on navigation', async ({ page }) => {
    await page.locator('[data-view="alerts"]').click();
    await expect(page.locator('[data-view="alerts"]')).toHaveClass(/active/);
    await expect(page.locator('[data-view="map"]')).not.toHaveClass(/active/);
  });

  test('browser back/forward works with hash routing', async ({ page }) => {
    await navigateToView(page, 'briefing');
    await navigateToView(page, 'alerts');

    await page.goBack();
    await expect(page).toHaveURL(/#briefing/);
    await expect(page.locator('#briefing-view')).toHaveClass(/active/);

    await page.goForward();
    await expect(page).toHaveURL(/#alerts/);
    await expect(page.locator('#alerts-view')).toHaveClass(/active/);
  });

  test('country panel closes when navigating away from map', async ({ page }) => {
    // Open a country panel
    await page.fill('#search', 'United States');
    await page.waitForSelector('.search-dropdown__item[data-code="USA"]');
    await page.locator('.search-dropdown__item[data-code="USA"]').click();
    await page.waitForSelector('#country-panel.open');

    // Navigate away
    await navigateToView(page, 'briefing');

    // Panel should be closed
    await expect(page.locator('#country-panel')).not.toHaveClass(/open/);
  });

  test('direct hash URL loads the correct view', async ({ page }) => {
    await page.goto('./#rankings');
    await waitForAppInit(page);
    await expect(page.locator('#rankings-view')).toHaveClass(/active/);
  });
});
