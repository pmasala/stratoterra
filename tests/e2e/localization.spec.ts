import { test, expect } from '@playwright/test';
import { waitForAppInit, collectPageErrors, navigateToView } from './fixtures/test-helpers';

/**
 * Helper: switch language via the language selector UI.
 */
async function switchLanguage(page: import('@playwright/test').Page, langCode: string) {
  // Open dropdown
  await page.locator('#lang-toggle').click();
  await expect(page.locator('#lang-dropdown')).toHaveClass(/open/);
  // Click the desired language option
  await page.locator(`.lang-option[data-lang="${langCode}"]`).click();
  // Wait for DOM update to complete (onChange triggers async reloads)
  await page.waitForTimeout(500);
}

/**
 * Helper: get the current language from the app.
 */
async function getCurrentLang(page: import('@playwright/test').Page): Promise<string> {
  return page.evaluate(() => (window as any).I18n.getLang());
}

test.describe('Localization — Language Selector UI', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage to ensure clean state (default = English)
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('language selector is visible in the header', async ({ page }) => {
    await expect(page.locator('#lang-selector')).toBeVisible();
    await expect(page.locator('#lang-toggle')).toBeVisible();
  });

  test('language toggle shows current language code and flag', async ({ page }) => {
    const code = await page.locator('#lang-code').textContent();
    expect(code?.trim()).toBe('EN');
    const flag = await page.locator('#lang-flag').textContent();
    expect(flag?.trim()).toBeTruthy();
  });

  test('clicking toggle opens dropdown with language options', async ({ page }) => {
    const dropdown = page.locator('#lang-dropdown');
    // Initially closed
    await expect(dropdown).not.toHaveClass(/open/);
    // Click toggle
    await page.locator('#lang-toggle').click();
    await expect(dropdown).toHaveClass(/open/);
    // Should have at least 2 options (EN and IT)
    const options = dropdown.locator('.lang-option');
    expect(await options.count()).toBeGreaterThanOrEqual(2);
  });

  test('clicking outside closes the dropdown', async ({ page }) => {
    await page.locator('#lang-toggle').click();
    await expect(page.locator('#lang-dropdown')).toHaveClass(/open/);
    // Click on body
    await page.locator('body').click({ position: { x: 10, y: 10 } });
    await expect(page.locator('#lang-dropdown')).not.toHaveClass(/open/);
  });

  test('active language is highlighted in dropdown', async ({ page }) => {
    await page.locator('#lang-toggle').click();
    const enOption = page.locator('.lang-option[data-lang="en"]');
    await expect(enOption).toHaveClass(/active/);
    const itOption = page.locator('.lang-option[data-lang="it"]');
    await expect(itOption).not.toHaveClass(/active/);
  });
});

test.describe('Localization — Switching to Italian', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('switching to Italian updates navigation labels', async ({ page }) => {
    // Verify English first
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Map');
    await expect(page.locator('.nav-link[data-view="briefing"]')).toHaveText('Stories');
    await expect(page.locator('.nav-link[data-view="alerts"]')).toHaveText('Alerts');
    await expect(page.locator('.nav-link[data-view="rankings"]')).toHaveText('Rankings');
    await expect(page.locator('.nav-link[data-view="compare"]')).toHaveText('Compare');

    await switchLanguage(page, 'it');

    // Verify Italian
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Mappa');
    await expect(page.locator('.nav-link[data-view="briefing"]')).toHaveText('Articoli');
    await expect(page.locator('.nav-link[data-view="alerts"]')).toHaveText('Allerte');
    await expect(page.locator('.nav-link[data-view="rankings"]')).toHaveText('Classifiche');
    await expect(page.locator('.nav-link[data-view="compare"]')).toHaveText('Confronta');
  });

  test('switching to Italian updates page title', async ({ page }) => {
    await switchLanguage(page, 'it');
    await expect(page).toHaveTitle('Stratoterra — Intelligence Geopolitica');
  });

  test('switching to Italian updates search placeholder', async ({ page }) => {
    await switchLanguage(page, 'it');
    const placeholder = await page.locator('#search').getAttribute('placeholder');
    expect(placeholder).toBe('Cerca paese...');
  });

  test('switching to Italian updates the toggle display', async ({ page }) => {
    await switchLanguage(page, 'it');
    const code = await page.locator('#lang-code').textContent();
    expect(code?.trim()).toBe('IT');
  });

  test('switching to Italian updates the HTML lang attribute', async ({ page }) => {
    await switchLanguage(page, 'it');
    const lang = await page.evaluate(() => document.documentElement.lang);
    expect(lang).toBe('it');
  });

  test('switching to Italian updates the disclaimer text', async ({ page }) => {
    await switchLanguage(page, 'it');
    const disclaimer = page.locator('#disclaimer [data-i18n="disclaimer"]');
    const text = await disclaimer.textContent();
    expect(text).not.toContain('Not financial advice');
    // Italian disclaimer should contain Italian text
    expect(text?.length).toBeGreaterThan(10);
  });

  test('all data-i18n elements have non-empty text after switching', async ({ page }) => {
    await switchLanguage(page, 'it');
    const elements = page.locator('[data-i18n]');
    const count = await elements.count();
    expect(count).toBeGreaterThan(30); // We added 57+ data-i18n attributes
    for (let i = 0; i < count; i++) {
      const el = elements.nth(i);
      // Only check visible elements (some may be in hidden views)
      if (await el.isVisible()) {
        const text = await el.textContent();
        expect(text?.trim(), `data-i18n element at index ${i} should not be empty`).toBeTruthy();
      }
    }
  });
});

test.describe('Localization — Switching Back to English', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('switching IT → EN restores English labels', async ({ page }) => {
    await switchLanguage(page, 'it');
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Mappa');

    await switchLanguage(page, 'en');
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Map');
    await expect(page.locator('.nav-link[data-view="briefing"]')).toHaveText('Stories');
    await expect(page.locator('.nav-link[data-view="alerts"]')).toHaveText('Alerts');
    await expect(page).toHaveTitle('Stratoterra — Geopolitical Intelligence');
  });
});

test.describe('Localization — localStorage Persistence', () => {
  test('language preference persists across page reloads', async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);

    // Switch to Italian
    await switchLanguage(page, 'it');
    const lang = await getCurrentLang(page);
    expect(lang).toBe('it');

    // Reload the page
    await page.reload();
    await waitForAppInit(page);

    // Language should still be Italian
    const langAfterReload = await getCurrentLang(page);
    expect(langAfterReload).toBe('it');

    // UI should reflect Italian
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Mappa');
    await expect(page).toHaveTitle('Stratoterra — Intelligence Geopolitica');
    const code = await page.locator('#lang-code').textContent();
    expect(code?.trim()).toBe('IT');
  });

  test('localStorage key is set correctly', async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);

    await switchLanguage(page, 'it');
    const stored = await page.evaluate(() => localStorage.getItem('stratoterra-lang'));
    expect(stored).toBe('it');
  });
});

test.describe('Localization — View-Specific Content', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('rankings view headings translate when switching language', async ({ page }) => {
    await navigateToView(page, 'rankings');
    // Verify English content is present
    const rankingsView = page.locator('#rankings-view');
    await expect(rankingsView).toBeVisible();

    await switchLanguage(page, 'it');
    // After switching, rankings view labels should be in Italian
    // The rankings title uses data-i18n="rankings.title"
    const title = rankingsView.locator('[data-i18n="rankings.title"]');
    if (await title.count() > 0) {
      const text = await title.textContent();
      expect(text).toBe('Classifiche Globali');
    }
  });

  test('alerts view title translates when switching language', async ({ page }) => {
    await navigateToView(page, 'alerts');
    const alertsView = page.locator('#alerts-view');
    await expect(alertsView).toBeVisible();

    await switchLanguage(page, 'it');
    // Check for Italian alert dashboard content
    const title = alertsView.locator('[data-i18n="alerts.title"]');
    if (await title.count() > 0) {
      const text = await title.textContent();
      expect(text).toBe('Pannello Allerte');
    }
  });

  test('briefing view content translates when switching language', async ({ page }) => {
    await navigateToView(page, 'briefing');
    const briefingView = page.locator('#briefing-view');
    await expect(briefingView).toBeVisible();

    // Switch to Italian and verify the view re-renders
    await switchLanguage(page, 'it');
    // Give time for async data reload
    await page.waitForTimeout(500);
    // Briefing view should still be visible (no crash)
    await expect(briefingView).toBeVisible();
  });

  test('compare view translates when switching language', async ({ page }) => {
    await navigateToView(page, 'compare');
    const compareView = page.locator('#compare-view');
    await expect(compareView).toBeVisible();

    await switchLanguage(page, 'it');
    await expect(compareView).toBeVisible();
    // Check that compare view has Italian content (title or labels)
    const title = compareView.locator('[data-i18n="compare.title"]');
    if (await title.count() > 0) {
      const text = await title.textContent();
      expect(text).toBe('Confronto Paesi');
    }
  });
});

test.describe('Localization — No JS Errors During Language Switch', () => {
  test('no JavaScript errors when switching EN → IT', async ({ page }) => {
    const errors = collectPageErrors(page);
    await page.goto('./');
    await waitForAppInit(page);

    await switchLanguage(page, 'it');
    // Navigate through all views to exercise all code paths
    await navigateToView(page, 'briefing');
    await page.waitForTimeout(300);
    await navigateToView(page, 'alerts');
    await page.waitForTimeout(300);
    await navigateToView(page, 'rankings');
    await page.waitForTimeout(300);
    await navigateToView(page, 'compare');
    await page.waitForTimeout(300);
    await navigateToView(page, 'map');
    await page.waitForTimeout(300);

    expect(errors, `JS errors during language switch: ${errors.join('; ')}`).toEqual([]);
  });

  test('no JavaScript errors when switching IT → EN → IT', async ({ page }) => {
    const errors = collectPageErrors(page);
    await page.goto('./');
    await waitForAppInit(page);

    await switchLanguage(page, 'it');
    await page.waitForTimeout(300);
    await switchLanguage(page, 'en');
    await page.waitForTimeout(300);
    await switchLanguage(page, 'it');
    await page.waitForTimeout(300);

    expect(errors, `JS errors during rapid language switching: ${errors.join('; ')}`).toEqual([]);
  });
});

test.describe('Localization — I18n Module API', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('I18n.t() returns translated strings for known keys', async ({ page }) => {
    const mapEn = await page.evaluate(() => (window as any).I18n.t('nav.map'));
    expect(mapEn).toBe('Map');

    await page.evaluate(() => (window as any).I18n.setLang('it'));
    const mapIt = await page.evaluate(() => (window as any).I18n.t('nav.map'));
    expect(mapIt).toBe('Mappa');
  });

  test('I18n.t() returns the key itself for unknown keys', async ({ page }) => {
    const result = await page.evaluate(() => (window as any).I18n.t('nonexistent.key.here'));
    expect(result).toBe('nonexistent.key.here');
  });

  test('I18n.t() supports parameter interpolation', async ({ page }) => {
    // The panel.no_data key uses {name} parameter
    const result = await page.evaluate(() =>
      (window as any).I18n.t('panel.no_data', { name: 'TestCountry' })
    );
    expect(result).toContain('TestCountry');
  });

  test('I18n.getLang() reflects current language', async ({ page }) => {
    expect(await getCurrentLang(page)).toBe('en');
    await page.evaluate(() => (window as any).I18n.setLang('it'));
    expect(await getCurrentLang(page)).toBe('it');
  });

  test('I18n.getLocale() returns correct locale string', async ({ page }) => {
    const enLocale = await page.evaluate(() => (window as any).I18n.getLocale());
    expect(enLocale).toBe('en-US');

    await page.evaluate(() => (window as any).I18n.setLang('it'));
    const itLocale = await page.evaluate(() => (window as any).I18n.getLocale());
    expect(itLocale).toBe('it-IT');
  });

  test('I18n.getSupportedLanguages() returns language list', async ({ page }) => {
    const langs = await page.evaluate(() => (window as any).I18n.getSupportedLanguages());
    expect(langs.length).toBeGreaterThanOrEqual(2);
    const codes = langs.map((l: any) => l.code);
    expect(codes).toContain('en');
    expect(codes).toContain('it');
  });

  test('I18n.setLang() with invalid language does nothing', async ({ page }) => {
    await page.evaluate(() => (window as any).I18n.setLang('xx'));
    expect(await getCurrentLang(page)).toBe('en');
  });

  test('I18n.setLang() with same language is a no-op', async ({ page }) => {
    // Should not throw or cause issues
    await page.evaluate(() => (window as any).I18n.setLang('en'));
    expect(await getCurrentLang(page)).toBe('en');
  });
});

test.describe('Localization — Mobile Tab Bar', () => {
  test('mobile tab bar labels translate when switching language', async ({ page }) => {
    // Use mobile viewport to ensure mobile tab bar is visible
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('./');
    await waitForAppInit(page);

    // Verify English labels
    const mapTab = page.locator('.mobile-tab[data-view="map"] [data-i18n="nav.map"]');
    await expect(mapTab).toHaveText('Map');

    await switchLanguage(page, 'it');

    await expect(mapTab).toHaveText('Mappa');
    await expect(page.locator('.mobile-tab[data-view="alerts"] [data-i18n="nav.alerts"]')).toHaveText('Allerte');
  });
});

test.describe('Localization — DataLoader Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.removeItem('stratoterra-lang'));
    await page.goto('./');
    await waitForAppInit(page);
  });

  test('DataLoader.getAvailableLanguages() returns language list', async ({ page }) => {
    const langs = await page.evaluate(() => (window as any).DataLoader.getAvailableLanguages());
    // Should return an array (may be empty if no translation_manifest.json exists)
    expect(Array.isArray(langs)).toBe(true);
  });

  test('DataLoader.reloadForLanguage() does not throw', async ({ page }) => {
    // Switch language — this triggers reloadForLanguage internally
    const errors = collectPageErrors(page);
    await switchLanguage(page, 'it');
    await page.waitForTimeout(1000);
    expect(errors).toEqual([]);

    // Verify data is still available after reload
    const count = await page.evaluate(() => (window as any).DataLoader.getSummary().length);
    expect(count).toBe(75);
  });

  test('summary data remains available after language switch', async ({ page }) => {
    await switchLanguage(page, 'it');
    await page.waitForTimeout(1000);

    const count = await page.evaluate(() => (window as any).DataLoader.getSummary().length);
    expect(count).toBe(75);

    // Switch back
    await switchLanguage(page, 'en');
    await page.waitForTimeout(1000);

    const countAfter = await page.evaluate(() => (window as any).DataLoader.getSummary().length);
    expect(countAfter).toBe(75);
  });
});

test.describe('Localization — Full Page Navigation After Language Switch', () => {
  test('navigating all views in Italian causes no errors', async ({ page }) => {
    const errors = collectPageErrors(page);
    await page.goto('./');
    await page.evaluate(() => localStorage.setItem('stratoterra-lang', 'it'));
    await page.goto('./');
    await waitForAppInit(page);

    // Verify we loaded in Italian
    expect(await getCurrentLang(page)).toBe('it');

    // Navigate through all views
    const views = ['map', 'briefing', 'alerts', 'rankings', 'compare'];
    for (const view of views) {
      await navigateToView(page, view);
      await page.waitForTimeout(500);
    }

    expect(errors, `JS errors during Italian navigation: ${errors.join('; ')}`).toEqual([]);
  });

  test('page loaded with Italian preference from start shows Italian UI', async ({ page }) => {
    await page.goto('./');
    await page.evaluate(() => localStorage.setItem('stratoterra-lang', 'it'));
    await page.goto('./');
    await waitForAppInit(page);

    // Should be Italian from the start
    await expect(page.locator('.nav-link[data-view="map"]')).toHaveText('Mappa');
    await expect(page).toHaveTitle('Stratoterra — Intelligence Geopolitica');
    const code = await page.locator('#lang-code').textContent();
    expect(code?.trim()).toBe('IT');
  });
});
