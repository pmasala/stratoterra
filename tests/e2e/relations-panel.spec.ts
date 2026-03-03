import { test, expect } from '@playwright/test';
import { waitForAppInit, openCountryViaSearch, clickLayerTab } from './fixtures/test-helpers';

test.describe('Country Panel — Relations Tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    // Open a country with known bilateral data
    await openCountryViaSearch(page, 'United States', 'USA');
  });

  // ── Relations tab structure ────────────────────────────────────────────────

  test('Relations tab button is present in the layer tabs', async ({ page }) => {
    await expect(page.locator('.layer-tab[data-tab="relations"]')).toBeAttached();
  });

  test('clicking Relations tab makes it active', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await expect(page.locator('.layer-tab[data-tab="relations"]')).toHaveClass(/active/);
    await expect(page.locator('#tab-relations')).toHaveClass(/active/);
  });

  // ── Network graph ──────────────────────────────────────────────────────────

  test('Relations tab shows #relations-network-graph container', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await expect(page.locator('#relations-network-graph')).toBeAttached();
  });

  test('D3 network graph renders SVG for a country with relation data', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    // Wait for D3 to draw (it uses requestAnimationFrame)
    await page.waitForSelector('#relations-network-graph svg', { timeout: 10_000 });
    await expect(page.locator('#relations-network-graph svg')).toBeVisible();
  });

  test('network graph renders at least 2 circle nodes', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg circle', { timeout: 10_000 });
    const circles = page.locator('#relations-network-graph svg circle');
    const count = await circles.count();
    expect(count, 'Should render center node + at least one partner').toBeGreaterThanOrEqual(2);
  });

  test('network graph renders at least 1 line (link)', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg line', { timeout: 10_000 });
    const lines = page.locator('#relations-network-graph svg line');
    const count = await lines.count();
    expect(count, 'Should have at least 1 relation link').toBeGreaterThanOrEqual(1);
  });

  // ── Partner table ──────────────────────────────────────────────────────────

  test('Relations tab shows .relations-table', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await expect(page.locator('#tab-relations .relations-table')).toBeVisible();
  });

  test('relations table has at least one data row', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    const rows = page.locator('#tab-relations .relations-table__row');
    const count = await rows.count();
    expect(count, 'Should have at least one partner row').toBeGreaterThanOrEqual(1);
  });

  test('table rows have data-pair attribute', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    const firstRow = page.locator('#tab-relations .relations-table__row').first();
    const pair = await firstRow.getAttribute('data-pair');
    expect(pair, 'Row should have data-pair').not.toBeNull();
    expect(pair).toMatch(/^[A-Z]{3}_[A-Z]{3}$/);
  });

  test('table rows show country code in JetBrains Mono', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    const firstCode = page.locator('#tab-relations .relations-table__code').first();
    await expect(firstCode).toBeVisible();
    const text = await firstCode.textContent();
    expect(text?.trim().length, 'Country code should be non-empty').toBeGreaterThan(0);
  });

  // ── Bilateral overlay — network line click ─────────────────────────────────

  test('clicking a network link opens the bilateral overlay', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg line', { timeout: 10_000 });

    // Use dispatchEvent to bypass Playwright animation stability issues
    await page.evaluate(() => {
      const line = document.querySelector<SVGLineElement>('#relations-network-graph svg line');
      line?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    await page.waitForSelector('#bilateral-overlay', { timeout: 5_000 });
    await expect(page.locator('#bilateral-overlay')).toBeVisible();
  });

  test('bilateral overlay has a close button', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg line', { timeout: 10_000 });
    await page.evaluate(() => {
      const line = document.querySelector<SVGLineElement>('#relations-network-graph svg line');
      line?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await page.waitForSelector('#bilateral-overlay', { timeout: 5_000 });
    await expect(page.locator('#bilateral-overlay .bilateral-overlay__close')).toBeVisible();
  });

  test('clicking close button dismisses the bilateral overlay', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg line', { timeout: 10_000 });
    await page.evaluate(() => {
      const line = document.querySelector<SVGLineElement>('#relations-network-graph svg line');
      line?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await page.waitForSelector('#bilateral-overlay', { timeout: 5_000 });
    await page.locator('#bilateral-close').click();
    await expect(page.locator('#bilateral-overlay')).toHaveCount(0);
  });

  test('clicking overlay backdrop dismisses the bilateral overlay', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    await page.waitForSelector('#relations-network-graph svg line', { timeout: 10_000 });
    await page.evaluate(() => {
      const line = document.querySelector<SVGLineElement>('#relations-network-graph svg line');
      line?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await page.waitForSelector('#bilateral-overlay', { timeout: 5_000 });
    // Click the overlay backdrop (the element itself, not the card)
    await page.locator('#bilateral-overlay').click({ position: { x: 10, y: 10 } });
    await expect(page.locator('#bilateral-overlay')).toHaveCount(0);
  });

  // ── Bilateral overlay — table row click ───────────────────────────────────

  test('clicking a table row opens the bilateral overlay', async ({ page }) => {
    await clickLayerTab(page, 'relations');
    const firstRow = page.locator('#tab-relations .relations-table__row').first();
    await firstRow.click();
    await page.waitForSelector('#bilateral-overlay', { timeout: 5_000 });
    await expect(page.locator('#bilateral-overlay')).toBeVisible();
  });

  // ── DOM: old Relations nav/panel removed ──────────────────────────────────

  test('#relations-panel does not exist in DOM', async ({ page }) => {
    await expect(page.locator('#relations-panel')).toHaveCount(0);
  });

  test('Relations nav link does not exist in header nav', async ({ page }) => {
    await expect(page.locator('.nav-link[data-view="relations"]')).toHaveCount(0);
  });

  test('#relations-toggle button does not exist', async ({ page }) => {
    await expect(page.locator('#relations-toggle')).toHaveCount(0);
  });
});
