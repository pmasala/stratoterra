import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

test.describe('Relations View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'relations');
  });

  test('relation explorer title and mode toggle are visible', async ({ page }) => {
    await expect(page.locator('.relation-explorer h2')).toHaveText('Relation Explorer');
    await expect(page.locator('.compare-mode-toggle .layer-tab[data-mode="network"]')).toBeVisible();
    await expect(page.locator('.compare-mode-toggle .layer-tab[data-mode="bilateral"]')).toBeVisible();
  });

  test('network mode shows country selector', async ({ page }) => {
    // Network mode is default
    await expect(page.locator('.layer-tab[data-mode="network"]')).toHaveClass(/active/);
    await expect(page.locator('#relation-country-select')).toBeVisible();
  });

  test('selecting a country in network mode loads graph or message', async ({ page }) => {
    await page.selectOption('#relation-country-select', 'USA');
    // Should show either a D3 graph (SVG) or a "no data" message
    await page.waitForSelector('#network-graph', { timeout: 10_000 });
    const graphContent = page.locator('#network-graph');
    await expect(graphContent).toBeVisible();
  });

  test('bilateral mode shows pair selector', async ({ page }) => {
    await page.locator('.layer-tab[data-mode="bilateral"]').click();
    await expect(page.locator('.layer-tab[data-mode="bilateral"]')).toHaveClass(/active/);
    await expect(page.locator('#relation-pair-select')).toBeVisible();
  });
});
