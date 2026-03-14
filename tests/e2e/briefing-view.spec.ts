import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView, trackFailedRequests } from './fixtures/test-helpers';

test.describe('Briefing View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'briefing');
  });

  test('briefing loads real data, not error state', async ({ page }) => {
    // Wait for either real content or error card
    await page.waitForSelector('.briefing, .error-card', { timeout: 10_000 });
    await expect(page.locator('.error-card')).toHaveCount(0);
    await expect(page.locator('.briefing')).toBeVisible();
  });

  test('article cards are visible', async ({ page }) => {
    await page.waitForSelector('.article-card', { timeout: 10_000 });
    const cards = page.locator('.article-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Each article card has a headline
    await expect(cards.first().locator('.article-card__headline')).toBeVisible();
  });

  test('article card shows date', async ({ page }) => {
    await page.waitForSelector('.article-card', { timeout: 10_000 });
    await expect(page.locator('.article-card__date').first()).toBeVisible();
  });

  test('market context section exists in briefing data', async ({ page }) => {
    await page.waitForSelector('.briefing', { timeout: 10_000 });
    // Market context structure may vary (chips with prices or summary text)
    // Verify the briefing data includes market context
    const hasMarketContext = await page.evaluate(async () => {
      const data = await (window as any).DataLoader.getBriefing();
      return data && 'market_context' in data;
    });
    expect(hasMarketContext).toBe(true);
  });

  test('regional tabs are present and switchable', async ({ page }) => {
    // Region tabs appear if weekly briefing data has regional_summaries
    const hasTabs = await page.locator('.region-tab').count();
    if (hasTabs >= 2) {
      const tabs = page.locator('.region-tab');
      await expect(tabs.first()).toHaveClass(/active/);

      await tabs.nth(1).click();
      await expect(tabs.nth(1)).toHaveClass(/active/);
      await expect(tabs.first()).not.toHaveClass(/active/);
    }
  });

  test('article cards contain severity badges', async ({ page }) => {
    await page.waitForSelector('.article-card', { timeout: 10_000 });
    // At least one article should have a severity badge
    const badges = page.locator('.article-card .alert-badge');
    const count = await badges.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});
