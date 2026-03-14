import { test, expect } from '@playwright/test';
import {
  waitForAppInit,
  openCountryViaSearch,
  clickLayerTab,
  expectFactorCardPopulated,
  navigateToView,
} from './fixtures/test-helpers';

/**
 * Comprehensive field-population tests.
 * Verifies that Category A fields (data exists in JSON) show real values
 * in the UI, not "—" placeholders.
 */

const SEED_COUNTRIES = [
  { name: 'United States', code: 'USA' },
  { name: 'China', code: 'CHN' },
  { name: 'Germany', code: 'DEU' },
  { name: 'India', code: 'IND' },
  { name: 'Brazil', code: 'BRA' },
];

// ─── Suite 1: Economy Tab ────────────────────────────────────────────────────

test.describe('Field Population — Economy Tab', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test.describe(code, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto('./');
        await waitForAppInit(page);
        await openCountryViaSearch(page, name, code);
        // Economy tab is active by default
      });

      test('macro fields populated', async ({ page }) => {
        const tab = '#tab-economy';
        await expectFactorCardPopulated(page, 'GDP Growth', tab);
        await expectFactorCardPopulated(page, 'GDP/Capita', tab);
        await expectFactorCardPopulated(page, 'Inflation', tab);
        await expectFactorCardPopulated(page, 'Unemployment', tab);
        await expectFactorCardPopulated(page, 'Debt/GDP', tab);
        await expectFactorCardPopulated(page, 'Current Account', tab);
        await expectFactorCardPopulated(page, 'FX Reserves', tab);
      });

      test('financial fields populated', async ({ page }) => {
        const tab = '#tab-economy';
        await expectFactorCardPopulated(page, 'Policy Rate', tab);
        await expectFactorCardPopulated(page, '10Y Yield', tab);
        // At least one credit rating should be populated
        const sp = page.locator(`${tab} .factor-card`).filter({ hasText: 'Credit (S&P)' }).locator('.factor-card__value');
        const moodys = page.locator(`${tab} .factor-card`).filter({ hasText: 'Credit (Moodys)' }).locator('.factor-card__value');
        const spVal = await sp.textContent();
        const moodysVal = await moodys.textContent();
        const hasRating = (spVal?.trim() !== '—') || (moodysVal?.trim() !== '—');
        expect(hasRating, `${code} should have at least one credit rating`).toBe(true);
      });

      test('trade fields populated', async ({ page }) => {
        const tab = '#tab-economy';
        await expectFactorCardPopulated(page, 'Exports', tab);
        await expectFactorCardPopulated(page, 'Imports', tab);
        await expectFactorCardPopulated(page, 'Balance', tab);
      });

      if (code !== 'USA') {
        test('FX vs USD populated for non-USD country', async ({ page }) => {
          // RUS may not have exchange_rate_vs_usd
          if (code === 'RUS') return;
          await expectFactorCardPopulated(page, 'FX vs USD', '#tab-economy');
        });
      }
    });
  }

  test('USA GDP shows trillions', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await openCountryViaSearch(page, 'United States', 'USA');
    const gdpCard = page.locator('#tab-economy .factor-card').filter({ hasText: 'GDP (Nominal)' });
    const gdpValue = await gdpCard.locator('.factor-card__value').textContent();
    expect(gdpValue, 'USA GDP should contain T for trillions').toContain('T');
  });
});

// ─── Suite 2: Institutions Tab ───────────────────────────────────────────────

test.describe('Field Population — Institutions Tab', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test.describe(code, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto('./');
        await waitForAppInit(page);
        await openCountryViaSearch(page, name, code);
        await clickLayerTab(page, 'institutions');
      });

      test('governance indicators populated', async ({ page }) => {
        const tab = '#tab-institutions';
        await expectFactorCardPopulated(page, 'Democracy Index', tab);
        await expectFactorCardPopulated(page, 'Freedom Score', tab);
        await expectFactorCardPopulated(page, 'Freedom Status', tab);
        await expectFactorCardPopulated(page, 'Press Freedom', tab);
        await expectFactorCardPopulated(page, 'Corruption (CPI)', tab);
        await expectFactorCardPopulated(page, 'Rule of Law', tab);
        await expectFactorCardPopulated(page, 'Govt Effectiveness', tab);
        await expectFactorCardPopulated(page, 'Regulatory Quality', tab);
        await expectFactorCardPopulated(page, 'Political Stability', tab);
      });

      test('voice & accountability populated', async ({ page }) => {
        await expectFactorCardPopulated(page, 'Voice & Account.', '#tab-institutions');
      });

      test('corruption control populated', async ({ page }) => {
        await expectFactorCardPopulated(page, 'Corruption Ctrl', '#tab-institutions');
      });

      test('head of state populated', async ({ page }) => {
        await expectFactorCardPopulated(page, 'Head of State', '#tab-institutions');
      });
    });
  }

  // Head of Government only for countries that have it (parliamentary/dual exec)
  for (const { name, code } of [
    { name: 'Germany', code: 'DEU' },
    { name: 'China', code: 'CHN' },
    { name: 'Russia', code: 'RUS' },
    { name: 'India', code: 'IND' },
  ]) {
    test(`${code} has Head of Gov't`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      await clickLayerTab(page, 'institutions');
      await expectFactorCardPopulated(page, "Head of Gov't", '#tab-institutions');
    });
  }

  // Fragile States Index — only some countries have it
  for (const { name, code } of [
    { name: 'China', code: 'CHN' },
    { name: 'India', code: 'IND' },
    { name: 'Brazil', code: 'BRA' },
  ]) {
    test(`${code} has Fragile States Index`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      await clickLayerTab(page, 'institutions');
      await expectFactorCardPopulated(page, 'Fragile States', '#tab-institutions');
    });
  }
});

// ─── Suite 3: Military Tab ───────────────────────────────────────────────────

test.describe('Field Population — Military Tab', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test.describe(code, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto('./');
        await waitForAppInit(page);
        await openCountryViaSearch(page, name, code);
        await clickLayerTab(page, 'military');
      });

      test('personnel fields populated', async ({ page }) => {
        const tab = '#tab-military';
        await expectFactorCardPopulated(page, 'Active Military', tab);
        await expectFactorCardPopulated(page, 'Reserve', tab);
      });

      test('equipment fields populated', async ({ page }) => {
        const tab = '#tab-military';
        await expectFactorCardPopulated(page, 'Tanks', tab);
        await expectFactorCardPopulated(page, 'Aircraft', tab);
        await expectFactorCardPopulated(page, 'Naval Vessels', tab);
      });
    });
  }

  // Nuclear warheads — only for nuclear powers
  for (const { name, code } of [
    { name: 'United States', code: 'USA' },
    { name: 'China', code: 'CHN' },
    { name: 'India', code: 'IND' },
  ]) {
    test(`${code} has nuclear warhead count`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      await clickLayerTab(page, 'military');
      const nucCard = page.locator('#tab-military .factor-card').filter({ hasText: 'Nuclear' });
      const nucValue = await nucCard.locator('.factor-card__value').textContent();
      expect(nucValue?.trim(), `${code} should show warhead count`).toMatch(/\d+.*warheads/);
    });
  }
});

// ─── Suite 4: Endowments Tab ─────────────────────────────────────────────────

test.describe('Field Population — Endowments Tab', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test(`${code} demographics populated`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      await clickLayerTab(page, 'endowments');
      const tab = '#tab-endowments';
      await expectFactorCardPopulated(page, 'Population', tab);
      await expectFactorCardPopulated(page, 'Growth', tab);
      await expectFactorCardPopulated(page, 'Median Age', tab);
      await expectFactorCardPopulated(page, 'HDI', tab);
    });
  }
});

// ─── Suite 5: Derived Tab ────────────────────────────────────────────────────

test.describe('Field Population — Derived Tab', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test(`${code} composite indices populated`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      await clickLayerTab(page, 'derived');
      const tab = '#tab-derived';
      await expectFactorCardPopulated(page, 'Composite Power', tab);
      await expectFactorCardPopulated(page, 'Energy Independence', tab);
      await expectFactorCardPopulated(page, 'Supply Chain Exposure', tab);
    });
  }
});

// ─── Suite 6: Executive Summary & Narrative ──────────────────────────────────

test.describe('Field Population — Executive Summary', () => {
  for (const { name, code } of SEED_COUNTRIES) {
    test(`${code} has executive summary > 50 chars`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      const summary = await page.locator('.exec-summary').textContent();
      expect(summary!.length, `${code} exec summary too short`).toBeGreaterThan(50);
    });

    test(`${code} has key changes list`, async ({ page }) => {
      await page.goto('./');
      await waitForAppInit(page);
      await openCountryViaSearch(page, name, code);
      const items = page.locator('.key-changes li');
      const count = await items.count();
      expect(count, `${code} should have key changes`).toBeGreaterThan(0);
    });
  }
});

// ─── Suite 7: Briefing View ──────────────────────────────────────────────────

test.describe('Field Population — Briefing View', () => {
  test('article cards populated', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'briefing');

    // Article headlines
    await page.waitForSelector('.article-card__headline', { timeout: 10_000 });
    const headlines = page.locator('.article-card__headline');
    const count = await headlines.count();
    expect(count, 'Should have article headlines').toBeGreaterThan(0);

    const text = await headlines.first().textContent();
    expect(text!.trim().length, 'Article headline too short').toBeGreaterThan(5);
  });

  test('regional tabs have content', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'briefing');

    // Click a regional tab and verify content appears
    const tabs = page.locator('.region-tab, .briefing-region-tab');
    const tabCount = await tabs.count();
    if (tabCount > 1) {
      await tabs.nth(1).click();
      // Wait for content to render
      await page.waitForTimeout(300);
      // Should have some visible content in the briefing
      const content = page.locator('.briefing-view .region-content.active, .briefing-view .briefing-region.active');
      if (await content.count() > 0) {
        const text = await content.first().textContent();
        expect(text!.trim().length).toBeGreaterThan(0);
      }
    }
  });
});

// ─── Suite 8: Alert Dashboard ────────────────────────────────────────────────

test.describe('Field Population — Alert Dashboard', () => {
  test('alert cards have titles and descriptions', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'alerts');

    const alertCards = page.locator('.alert-card');
    const count = await alertCards.count();
    expect(count, 'Should have alert cards').toBeGreaterThan(0);

    // Check first 3 alerts
    const checkCount = Math.min(count, 3);
    for (let i = 0; i < checkCount; i++) {
      const card = alertCards.nth(i);
      const title = await card.locator('.alert-card__title').textContent();
      expect(title!.trim().length, `Alert ${i} title should not be empty`).toBeGreaterThan(0);

      const desc = await card.locator('.alert-card__body').textContent();
      expect(desc!.trim().length, `Alert ${i} description should not be empty`).toBeGreaterThan(0);
    }
  });

  test('severity badges have valid values', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'alerts');

    const badges = page.locator('.alert-card__severity, .severity-badge');
    const count = await badges.count();
    const validSeverities = ['critical', 'warning', 'watch'];

    const checkCount = Math.min(count, 5);
    for (let i = 0; i < checkCount; i++) {
      const text = await badges.nth(i).textContent();
      const severity = text!.trim().toLowerCase();
      expect(validSeverities, `Badge "${severity}" should be a valid severity`).toContain(severity);
    }
  });
});

// ─── Suite 9: Rankings View ──────────────────────────────────────────────────

test.describe('Field Population — Rankings View', () => {
  test('table rows have country names and values', async ({ page }) => {
    await page.goto('./');
    await waitForAppInit(page);
    await navigateToView(page, 'rankings');

    const rows = page.locator('.rankings-table tbody tr, .ranking-row');
    const count = await rows.count();
    expect(count, 'Should have ranking rows').toBeGreaterThan(0);

    // Check first 3 rows have country name and at least one cell with data
    const checkCount = Math.min(count, 3);
    for (let i = 0; i < checkCount; i++) {
      const row = rows.nth(i);
      const text = await row.textContent();
      expect(text!.trim().length, `Row ${i} should have content`).toBeGreaterThan(0);
    }
  });
});
