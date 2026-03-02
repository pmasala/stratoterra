import { test, expect } from '@playwright/test';
import { waitForAppInit, trackFailedRequests } from './fixtures/test-helpers';

test.describe('Data Integrity', () => {
  test('no 404s on initial page load (summary + geojson)', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);
    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);
  });

  test('country detail fetch returns valid JSON', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);

    // Open a country panel — triggers detail fetch
    await page.fill('#search', 'United States');
    await page.waitForSelector('.search-dropdown__item[data-code="USA"]');
    await page.locator('.search-dropdown__item[data-code="USA"]').click();
    await page.waitForSelector('#country-panel.open .panel-header__title', { timeout: 10_000 });

    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);

    // Verify the detail data actually loaded (not fallback "no data" state)
    const hasDetailData = await page.evaluate(() => {
      const panel = document.getElementById('country-panel');
      return panel !== null && !panel.querySelector('.panel-no-data');
    });
    expect(hasDetailData, 'Country detail should load real data, not the "no data" fallback').toBe(true);
  });

  test('briefing view fetches data without errors', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);

    await page.evaluate(() => { window.location.hash = '#briefing'; });
    await page.waitForSelector('#briefing-view.active', { timeout: 5_000 });

    // Wait for either briefing content or error card
    await page.waitForSelector('.briefing, .error-card', { timeout: 10_000 });

    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);

    // Should show real briefing content, not error state
    await expect(page.locator('.error-card')).toHaveCount(0);
    await expect(page.locator('.briefing')).toBeVisible();
  });

  test('alert dashboard fetches data without errors', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);

    await page.evaluate(() => { window.location.hash = '#alerts'; });
    await page.waitForSelector('#alerts-view.active', { timeout: 5_000 });

    await page.waitForSelector('.alerts-dashboard, .error-card', { timeout: 10_000 });

    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);
    await expect(page.locator('.error-card')).toHaveCount(0);
    await expect(page.locator('.alerts-dashboard')).toBeVisible();
  });

  test('rankings view loads data from summary (no extra fetch needed)', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);

    await page.evaluate(() => { window.location.hash = '#rankings'; });
    await page.waitForSelector('#rankings-view.active', { timeout: 5_000 });
    await page.waitForSelector('.rankings-table', { timeout: 10_000 });

    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);

    // Table should have rows (not empty)
    const rowCount = await page.locator('.rankings-row').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('relation index fetches without errors', async ({ page }) => {
    const failed = trackFailedRequests(page);
    await page.goto('./');
    await waitForAppInit(page);

    await page.evaluate(() => { window.location.hash = '#relations'; });
    await page.waitForSelector('#relations-view.active', { timeout: 5_000 });
    await page.waitForSelector('.relation-explorer', { timeout: 10_000 });

    expect(failed, `Failed requests: ${failed.join(', ')}`).toEqual([]);
  });

  test('all critical data endpoints return 200', async ({ page }) => {
    // Directly fetch the key data files the app depends on
    const endpoints = [
      '../data/chunks/country-summary/all_countries_summary.json',
      '../data/chunks/global/weekly_briefing.json',
      '../data/chunks/global/alert_index.json',
      '../data/chunks/global/global_rankings.json',
      '../data/chunks/relations/relation_index.json',
    ];

    await page.goto('./');

    for (const endpoint of endpoints) {
      const response = await page.request.get(
        `http://localhost:8089/web/${endpoint}`,
      );
      expect(
        response.status(),
        `${endpoint} should return 200, got ${response.status()}`,
      ).toBe(200);

      // Verify it's valid JSON
      const body = await response.text();
      expect(() => JSON.parse(body), `${endpoint} should be valid JSON`).not.toThrow();
    }
  });

  test('country detail files exist for Tier 1 countries', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);

    // Get Tier 1 country codes from summary data
    const tier1Codes: string[] = await page.evaluate(() => {
      return (window as any).DataLoader.getSummary()
        .filter((c: any) => c.tier === 1)
        .map((c: any) => c.code);
    });

    expect(tier1Codes.length).toBeGreaterThanOrEqual(25);

    // Verify each Tier 1 country detail file is fetchable
    const missing: string[] = [];
    for (const code of tier1Codes) {
      const response = await page.request.get(
        `http://localhost:8089/data/chunks/country-detail/${code}.json`,
      );
      if (response.status() !== 200) {
        missing.push(code);
      }
    }
    expect(missing, `Missing detail files for Tier 1 countries: ${missing.join(', ')}`).toEqual([]);
  });
});
