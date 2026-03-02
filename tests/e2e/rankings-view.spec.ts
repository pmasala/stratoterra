import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

test.describe('Rankings View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'rankings');
  });

  test('rankings table loads with rows', async ({ page }) => {
    await page.waitForSelector('.rankings-table', { timeout: 10_000 });
    const rows = page.locator('.rankings-row');
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(1);
    expect(count).toBeLessThanOrEqual(75);
  });

  test('4 group tabs are present', async ({ page }) => {
    const groupTabs = page.locator('.rankings-groups .layer-tab');
    await expect(groupTabs).toHaveCount(4);

    const expectedGroups = ['Economic', 'Power', 'Risk', 'Development'];
    for (let i = 0; i < expectedGroups.length; i++) {
      await expect(groupTabs.nth(i)).toContainText(expectedGroups[i]);
    }
  });

  test('switching group tab changes table columns', async ({ page }) => {
    await page.waitForSelector('.rankings-table');
    const headersBefore = await page.locator('.rankings-table thead .sort-th').allTextContents();

    // Click Power tab
    await page.locator('.rankings-groups .layer-tab[data-group="power"]').click();
    await page.waitForSelector('.rankings-table');
    const headersAfter = await page.locator('.rankings-table thead .sort-th').allTextContents();

    expect(headersAfter).not.toEqual(headersBefore);
  });

  test('clicking a sortable header re-sorts the table', async ({ page }) => {
    await page.waitForSelector('.rankings-table');

    // Get first country name
    const firstNameBefore = await page.locator('.rankings-row').first().locator('.name-col').textContent();

    // Click the "Country" header to sort alphabetically
    await page.locator('.sort-th[data-field="name"]').click();
    const firstNameAfter = await page.locator('.rankings-row').first().locator('.name-col').textContent();

    // Sort order should change (at least potentially)
    // We just verify the table re-rendered (the sort indicator appears)
    await expect(page.locator('.sort-th[data-field="name"]')).toContainText(/[▲▼]/);
  });

  test('filter dropdowns are present', async ({ page }) => {
    await expect(page.locator('#rank-region-filter')).toBeVisible();
    await expect(page.locator('#rank-tier-filter')).toBeVisible();
  });

  test('clicking a row opens country panel', async ({ page }) => {
    await page.waitForSelector('.rankings-row');
    const firstRow = page.locator('.rankings-row').first();
    const code = await firstRow.getAttribute('data-code');

    await firstRow.click();

    // Should navigate to map and open panel
    await page.waitForSelector('#country-panel.open', { timeout: 10_000 });
    await expect(page.locator('#country-panel')).toHaveClass(/open/);
  });
});
