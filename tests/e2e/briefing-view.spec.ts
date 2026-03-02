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

  test('briefing headline is visible', async ({ page }) => {
    await page.waitForSelector('.briefing-headline', { timeout: 10_000 });
    await expect(page.locator('.briefing-headline h2')).toBeVisible();
    const text = await page.locator('.briefing-headline h2').textContent();
    expect(text!.length).toBeGreaterThan(0);
  });

  test('briefing date is displayed', async ({ page }) => {
    await page.waitForSelector('.briefing-date', { timeout: 10_000 });
    await expect(page.locator('.briefing-date')).toBeVisible();
  });

  test('top stories section shows story cards', async ({ page }) => {
    await page.waitForSelector('.story-card', { timeout: 10_000 });
    const storyCards = page.locator('.story-card');
    const count = await storyCards.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // Each story card has a title
    await expect(storyCards.first().locator('.story-card__title')).toBeVisible();
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
    await page.waitForSelector('.region-tab', { timeout: 10_000 });
    const tabs = page.locator('.region-tab');
    const count = await tabs.count();
    expect(count).toBeGreaterThanOrEqual(2);

    // First tab is active
    await expect(tabs.first()).toHaveClass(/active/);

    // Click second tab
    await tabs.nth(1).click();
    await expect(tabs.nth(1)).toHaveClass(/active/);
    await expect(tabs.first()).not.toHaveClass(/active/);
  });

  test('story cards contain severity badges', async ({ page }) => {
    await page.waitForSelector('.story-card', { timeout: 10_000 });
    // At least one story should have a severity badge
    const badges = page.locator('.story-card .alert-badge');
    const count = await badges.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});
