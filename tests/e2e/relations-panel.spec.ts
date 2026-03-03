import { test, expect } from '@playwright/test';
import { waitForAppInit, openCountryViaSearch, navigateToView } from './fixtures/test-helpers';

// Helper: open the relations panel via the toggle button
async function openRelationsPanel(page: Parameters<typeof waitForAppInit>[0]) {
  await page.locator('#relations-toggle').click();
  await page.waitForSelector('#relations-panel.open', { timeout: 5_000 });
}

// Helper: close the relations panel via the toggle button
async function closeRelationsPanel(page: Parameters<typeof waitForAppInit>[0]) {
  await page.locator('#relations-toggle').click();
  await page.waitForFunction(
    () => !document.getElementById('relations-panel')?.classList.contains('open'),
    { timeout: 3_000 },
  );
}

test.describe('Relations Panel (map)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  // --- Toggle button ---

  test('relations-toggle button is visible in the bottom bar on map view', async ({ page }) => {
    await expect(page.locator('#relations-toggle')).toBeVisible();
    await expect(page.locator('#relations-toggle')).toHaveText('↔ Relations');
  });

  test('relations-toggle is hidden on non-map views (bottom bar hides)', async ({ page }) => {
    await navigateToView(page, 'briefing');
    // Bottom bar is display:none on non-map views
    await expect(page.locator('#bottom-bar')).toBeHidden();
  });

  // --- Open / close ---

  test('clicking toggle opens the relations panel', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-panel')).toHaveClass(/open/);
    await expect(page.locator('#relations-panel')).not.toHaveClass(/hidden/);
  });

  test('relations panel contains the Relation Explorer heading', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-panel .relation-explorer h2')).toHaveText('Relation Explorer');
  });

  test('clicking toggle again closes the panel', async ({ page }) => {
    await openRelationsPanel(page);
    await closeRelationsPanel(page);
    await expect(page.locator('#relations-panel')).not.toHaveClass(/open/);
  });

  test('toggle button gets .active class when panel is open', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-toggle')).toHaveClass(/active/);
  });

  test('toggle button loses .active class when panel is closed', async ({ page }) => {
    await openRelationsPanel(page);
    await closeRelationsPanel(page);
    await expect(page.locator('#relations-toggle')).not.toHaveClass(/active/);
  });

  test('#main-content gets panel-open class when relations panel is open', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#main-content')).toHaveClass(/panel-open/);
  });

  test('#main-content loses panel-open class when relations panel is closed', async ({ page }) => {
    await openRelationsPanel(page);
    await closeRelationsPanel(page);
    await expect(page.locator('#main-content')).not.toHaveClass(/panel-open/);
  });

  // --- Panel mode: no mode-toggle tabs ---

  test('mode-toggle buttons (Network/Bilateral) are NOT shown in panel mode', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-panel .compare-mode-toggle')).toHaveCount(0);
  });

  test('country selector is shown in panel mode (network mode default)', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-panel #relation-country-select')).toBeVisible();
  });

  // --- D3 network graph ---

  test('selecting USA loads network graph in panel', async ({ page }) => {
    await openRelationsPanel(page);
    await page.selectOption('#relations-panel #relation-country-select', 'USA');
    await page.waitForSelector('#relations-panel #network-graph', { timeout: 10_000 });
    await expect(page.locator('#relations-panel #network-graph')).toBeVisible();
  });

  test('network graph renders SVG nodes for USA', async ({ page }) => {
    await openRelationsPanel(page);
    await page.selectOption('#relations-panel #relation-country-select', 'USA');
    await page.waitForSelector('#relations-panel #network-graph svg', { timeout: 10_000 });
    const circles = page.locator('#relations-panel #network-graph svg circle');
    const count = await circles.count();
    expect(count, 'Should render at least 2 nodes (USA + partners)').toBeGreaterThanOrEqual(2);
  });

  // --- Bilateral drill-down in panel mode ---

  test('clicking a network link switches to bilateral mode with back button', async ({ page }) => {
    await openRelationsPanel(page);
    await page.selectOption('#relations-panel #relation-country-select', 'USA');
    await page.waitForSelector('#relations-panel #network-graph svg line', { timeout: 10_000 });

    // Click the first link line
    await page.locator('#relations-panel #network-graph svg line').first().click();

    // Back button should appear (panel mode bilateral)
    await page.waitForSelector('#relations-panel #rel-back-btn', { timeout: 5_000 });
    await expect(page.locator('#relations-panel #rel-back-btn')).toBeVisible();
    await expect(page.locator('#relations-panel #rel-back-btn')).toHaveText('← Network');
  });

  test('← Network back button returns to network mode', async ({ page }) => {
    await openRelationsPanel(page);
    await page.selectOption('#relations-panel #relation-country-select', 'USA');
    await page.waitForSelector('#relations-panel #network-graph svg line', { timeout: 10_000 });
    await page.locator('#relations-panel #network-graph svg line').first().click();
    await page.waitForSelector('#relations-panel #rel-back-btn', { timeout: 5_000 });

    await page.locator('#relations-panel #rel-back-btn').click();

    // Back button should be gone, country selector should reappear
    await expect(page.locator('#relations-panel #rel-back-btn')).toHaveCount(0);
    await expect(page.locator('#relations-panel #relation-country-select')).toBeVisible();
  });

  // --- Mutual exclusion ---

  test('opening relations panel closes country panel', async ({ page }) => {
    await openCountryViaSearch(page, 'Germany', 'DEU');
    await expect(page.locator('#country-panel')).toHaveClass(/open/);

    await openRelationsPanel(page);
    // Country panel should no longer be open
    await expect(page.locator('#country-panel')).not.toHaveClass(/open/);
    await expect(page.locator('#relations-panel')).toHaveClass(/open/);
  });

  test('opening country panel closes relations panel', async ({ page }) => {
    await openRelationsPanel(page);
    await expect(page.locator('#relations-panel')).toHaveClass(/open/);

    await openCountryViaSearch(page, 'France', 'FRA');
    // Relations panel should be closed
    await expect(page.locator('#relations-panel')).not.toHaveClass(/open/);
    await expect(page.locator('#country-panel')).toHaveClass(/open/);
  });

  // --- Navigation closes panel ---

  test('navigating to Briefing closes the relations panel', async ({ page }) => {
    await openRelationsPanel(page);
    await navigateToView(page, 'briefing');
    await expect(page.locator('#relations-panel')).not.toHaveClass(/open/);
  });

  test('navigating to Rankings closes the relations panel', async ({ page }) => {
    await openRelationsPanel(page);
    await navigateToView(page, 'rankings');
    await expect(page.locator('#relations-panel')).not.toHaveClass(/open/);
  });

  // --- Keyboard ---

  test('Escape key closes the relations panel', async ({ page }) => {
    await openRelationsPanel(page);
    await page.keyboard.press('Escape');
    await page.waitForFunction(
      () => !document.getElementById('relations-panel')?.classList.contains('open'),
      { timeout: 3_000 },
    );
    await expect(page.locator('#relations-panel')).not.toHaveClass(/open/);
  });

  // --- Both panels coexist structurally ---

  test('#relations-panel and #country-panel exist in DOM simultaneously', async ({ page }) => {
    await expect(page.locator('#relations-panel')).toBeAttached();
    await expect(page.locator('#country-panel')).toBeAttached();
  });
});
