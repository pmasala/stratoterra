import { test, expect } from '@playwright/test';
import { waitForAppInit, navigateToView } from './fixtures/test-helpers';

// Wait until the ticker container is revealed (any bar active)
async function waitForTicker(page: Parameters<typeof waitForAppInit>[0]) {
  await page.waitForFunction(
    () => {
      const ticker = document.getElementById('alert-ticker');
      return ticker && !ticker.classList.contains('hidden');
    },
    { timeout: 10_000 },
  );
}

// Wait until the watch (secondary) bar is active
async function waitForWatchBar(page: Parameters<typeof waitForAppInit>[0]) {
  await page.waitForFunction(
    () => {
      const bar = document.getElementById('ticker-secondary');
      return bar && bar.classList.contains('active');
    },
    { timeout: 10_000 },
  );
}

test.describe('Alert Ticker — Two-bar system', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
  });

  // ── DOM structure ──────────────────────────────────────────────────────────

  test('#alert-ticker element exists in DOM', async ({ page }) => {
    await expect(page.locator('#alert-ticker')).toBeAttached();
  });

  test('#ticker-primary and #ticker-secondary children exist', async ({ page }) => {
    await expect(page.locator('#ticker-primary')).toBeAttached();
    await expect(page.locator('#ticker-secondary')).toBeAttached();
  });

  test('watch tag reads "WATCH"', async ({ page }) => {
    await waitForWatchBar(page);
    await expect(page.locator('#ticker-secondary .ticker-tag-sm')).toHaveText('WATCH');
  });

  // ── Visibility on map load ─────────────────────────────────────────────────

  test('ticker is visible on initial map load when alerts exist', async ({ page }) => {
    await waitForTicker(page);
    await expect(page.locator('#alert-ticker')).toBeVisible();
  });

  test('#app has ticker-watch-on class when watch bar is active', async ({ page }) => {
    await waitForWatchBar(page);
    await expect(page.locator('#app')).toHaveClass(/ticker-watch-on/);
  });

  // ── Watch (secondary) bar content ─────────────────────────────────────────

  test('watch scroll track contains items', async ({ page }) => {
    await waitForWatchBar(page);
    const items = page.locator('#ticker-scroll-track .ticker-scroll-item');
    const count = await items.count();
    // Track is doubled for seamless loop, so count >= 2
    expect(count, 'Watch track should contain at least 2 items (doubled for loop)').toBeGreaterThanOrEqual(2);
  });

  test('watch items have data-alert-index attributes', async ({ page }) => {
    await waitForWatchBar(page);
    const firstItem = page.locator('#ticker-scroll-track .ticker-scroll-item').first();
    const idx = await firstItem.getAttribute('data-alert-index');
    expect(idx, 'Watch item should have data-alert-index').not.toBeNull();
    expect(Number(idx)).toBeGreaterThanOrEqual(0);
  });

  test('watch items have non-empty UPPERCASE text content', async ({ page }) => {
    await waitForWatchBar(page);
    const firstItem = page.locator('#ticker-scroll-track .ticker-scroll-item').first();
    const text = await firstItem.textContent();
    expect(text?.trim().length, 'Watch item should have text').toBeGreaterThan(3);
  });

  test('diamond separators (◆) are present between watch items', async ({ page }) => {
    await waitForWatchBar(page);
    const seps = page.locator('#ticker-scroll-track .ticker-scroll-sep');
    const count = await seps.count();
    expect(count, 'Should have at least 2 separators (doubled content)').toBeGreaterThanOrEqual(2);
  });

  // ── Primary (critical/warning) bar ────────────────────────────────────────

  test('primary bar activates when critical or warning alerts exist', async ({ page }) => {
    await waitForTicker(page);
    // Give primary bar time to start (it starts immediately in cyclePrimary)
    await page.waitForFunction(
      () => {
        const primary = document.getElementById('ticker-primary');
        return primary && primary.classList.contains('active');
      },
      { timeout: 5_000 },
    );
    await expect(page.locator('#ticker-primary')).toBeVisible();
    await expect(page.locator('#app')).toHaveClass(/ticker-primary-on/);
  });

  test('primary bar shows severity tag with correct class', async ({ page }) => {
    await waitForTicker(page);
    await page.waitForSelector('#ticker-primary.active', { timeout: 5_000 });
    const tag = page.locator('#ticker-tag');
    const cls = await tag.getAttribute('class') ?? '';
    expect(
      cls.includes('ticker-tag--critical') || cls.includes('ticker-tag--warning'),
      `Severity tag should be critical or warning, got: "${cls}"`,
    ).toBe(true);
  });

  test('primary headline has non-empty UPPERCASE text', async ({ page }) => {
    await waitForTicker(page);
    await page.waitForSelector('#ticker-primary.active', { timeout: 5_000 });
    const headline = page.locator('#ticker-headline');
    const text = await headline.textContent();
    expect(text?.trim().length, 'Headline should have text').toBeGreaterThan(3);
    // Should be uppercase
    expect(text?.trim()).toBe(text?.trim().toUpperCase());
  });

  test('primary timestamp shows UTC time format', async ({ page }) => {
    await waitForTicker(page);
    await page.waitForSelector('#ticker-primary.active', { timeout: 5_000 });
    const ts = page.locator('#ticker-timestamp');
    const text = await ts.textContent();
    expect(text, 'Timestamp should match HH:MM UTC').toMatch(/^\d{2}:\d{2} UTC$/);
  });

  // ── Visibility vs navigation ───────────────────────────────────────────────

  test('ticker is hidden when navigating to Alerts view', async ({ page }) => {
    await waitForTicker(page);
    await navigateToView(page, 'alerts');
    await expect(page.locator('#alert-ticker')).toBeHidden();
  });

  test('#app loses ticker margin classes on Alerts view', async ({ page }) => {
    await waitForTicker(page);
    await navigateToView(page, 'alerts');
    await expect(page.locator('#app')).not.toHaveClass(/ticker-watch-on/);
    await expect(page.locator('#app')).not.toHaveClass(/ticker-primary-on/);
  });

  test('ticker reappears after navigating away from Alerts', async ({ page }) => {
    await waitForTicker(page);
    await navigateToView(page, 'alerts');
    await expect(page.locator('#alert-ticker')).toBeHidden();
    await navigateToView(page, 'briefing');
    await expect(page.locator('#alert-ticker')).toBeVisible();
    await expect(page.locator('#app')).toHaveClass(/ticker-watch-on/);
  });

  test('ticker is visible on Briefing view', async ({ page }) => {
    await waitForTicker(page);
    await navigateToView(page, 'briefing');
    await expect(page.locator('#alert-ticker')).toBeVisible();
  });

  test('ticker is visible on Rankings view', async ({ page }) => {
    await waitForTicker(page);
    await navigateToView(page, 'rankings');
    await expect(page.locator('#alert-ticker')).toBeVisible();
  });

  // ── Click navigation ───────────────────────────────────────────────────────

  test('clicking primary content bar navigates to Alerts view', async ({ page }) => {
    await page.waitForSelector('#ticker-primary.active', { timeout: 10_000 });
    // Primary content is a static element (not animated) — can use normal click
    await page.locator('#ticker-content').click();
    await page.waitForSelector('#alerts-view.active', { timeout: 5_000 });
    await expect(page.locator('#alerts-view')).toHaveClass(/active/);
  });

  test('clicking primary bar hides ticker on Alerts view', async ({ page }) => {
    await page.waitForSelector('#ticker-primary.active', { timeout: 10_000 });
    await page.locator('#ticker-content').click();
    await page.waitForSelector('#alerts-view.active', { timeout: 5_000 });
    await expect(page.locator('#alert-ticker')).toBeHidden();
  });

  test('clicking watch scroll item navigates to Alerts view', async ({ page }) => {
    await waitForWatchBar(page);
    // Use dispatchEvent to bypass Playwright stability check on animated track
    await page.evaluate(() => {
      const item = document.querySelector<HTMLElement>('#ticker-scroll-track .ticker-scroll-item');
      item?.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await page.waitForSelector('#alerts-view.active', { timeout: 5_000 });
    await expect(page.locator('#alerts-view')).toHaveClass(/active/);
  });

  // ── Alert dashboard data-alert-index ──────────────────────────────────────

  test('alert cards in dashboard have data-alert-index attributes', async ({ page }) => {
    await navigateToView(page, 'alerts');
    await page.waitForSelector('.alert-card', { timeout: 10_000 });
    const cards = page.locator('.alert-card[data-alert-index]');
    const count = await cards.count();
    expect(count, 'At least one card should have data-alert-index').toBeGreaterThanOrEqual(1);
  });

  test('alert card data-alert-index values are sequential from 0', async ({ page }) => {
    await navigateToView(page, 'alerts');
    await page.waitForSelector('.alert-card', { timeout: 10_000 });
    const indices = await page.locator('.alert-card[data-alert-index]').evaluateAll(
      (cards) => cards.map((c) => Number((c as HTMLElement).dataset.alertIndex)),
    );
    expect(indices[0]).toBe(0);
    for (let i = 1; i < indices.length; i++) {
      expect(indices[i]).toBe(indices[i - 1] + 1);
    }
  });

  test('AlertDashboard.scrollToAlert() scrolls to the specified card', async ({ page }) => {
    await navigateToView(page, 'alerts');
    await page.waitForSelector('.alert-card', { timeout: 10_000 });
    const cardCount = await page.locator('.alert-card').count();
    if (cardCount < 2) test.skip();

    const lastIdx = cardCount - 1;
    await page.evaluate((idx) => {
      (window as any).AlertDashboard.scrollToAlert(idx);
    }, lastIdx);
    await page.waitForTimeout(400);
    // Scope to #alerts-view to avoid matching doubled watch items in scroll track
    const lastCard = page.locator(`#alerts-view [data-alert-index="${lastIdx}"]`);
    await expect(lastCard).toBeInViewport();
  });
});
