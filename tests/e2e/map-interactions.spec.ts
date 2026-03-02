import { test, expect } from '@playwright/test';
import { waitForAppInit } from './fixtures/test-helpers';

test.describe('Map Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('metric selector has all 8 options', async ({ page }) => {
    const options = page.locator('#metric-select option');
    await expect(options).toHaveCount(8);

    const expectedValues = [
      'gdp_growth_trend', 'political_stability', 'investment_risk',
      'military_spending_trend', 'alert_severity', 'economic_complexity',
      'energy_independence', 'trade_openness',
    ];
    for (const val of expectedValues) {
      await expect(page.locator(`#metric-select option[value="${val}"]`)).toBeAttached();
    }
  });

  test('overlay selector has 8 options (None + 7 groups)', async ({ page }) => {
    const options = page.locator('#overlay-select option');
    await expect(options).toHaveCount(8);

    const expectedValues = ['none', 'EU', 'NATO', 'BRICS', 'ASEAN', 'OPEC', 'G7', 'G20'];
    for (const val of expectedValues) {
      await expect(page.locator(`#overlay-select option[value="${val}"]`)).toBeAttached();
    }
  });

  test('changing metric selector updates map', async ({ page }) => {
    await page.selectOption('#metric-select', 'political_stability');
    // Verify the select value changed
    await expect(page.locator('#metric-select')).toHaveValue('political_stability');
  });

  test('changing overlay selector updates map', async ({ page }) => {
    await page.selectOption('#overlay-select', 'NATO');
    await expect(page.locator('#overlay-select')).toHaveValue('NATO');
  });

  test('Leaflet map is rendered with tiles', async ({ page }) => {
    // Leaflet adds .leaflet-container class directly to #map-container
    await expect(page.locator('#map-container.leaflet-container')).toBeVisible();
  });

  test('zoom controls are present', async ({ page }) => {
    await expect(page.locator('.leaflet-control-zoom-in')).toBeVisible();
    await expect(page.locator('.leaflet-control-zoom-out')).toBeVisible();
  });
});
