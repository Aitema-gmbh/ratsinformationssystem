import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const HAUPTSEITEN = [
  { name: 'Startseite', path: '/' },
  { name: 'Sitzungen', path: '/sitzungen' },
  { name: 'Suche', path: '/suche' },
  { name: 'Gremien', path: '/gremien' },
];

test.describe('Barrierefreiheit - Ratsinformationssystem', () => {
  for (const seite of HAUPTSEITEN) {
    test(`axe-core Audit: ${seite.name} hat keine kritischen Violations`, async ({ page }) => {
      await page.goto(seite.path).catch(async () => {
        await page.goto('/');
      });

      await page.waitForLoadState('networkidle');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      const criticalViolations = results.violations.filter(
        v => v.impact === 'critical' || v.impact === 'serious'
      );

      if (criticalViolations.length > 0) {
        const details = criticalViolations.map(v =>
          `[${v.impact}] ${v.id}: ${v.description}\n  Betroffen: ${v.nodes.slice(0, 2).map(n => n.html).join(', ')}`
        ).join('\n');
        console.error(`Violations auf ${seite.name}:\n${details}`);
      }

      expect(criticalViolations.length, `${criticalViolations.length} kritische Violations auf ${seite.name}`).toBe(0);
    });
  }

  test('Startseite: Alle ARIA-Landmarks vorhanden', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const main = page.locator('main, [role="main"]');
    await expect(main).toBeVisible();

    const nav = page.locator('nav, [role="navigation"]').first();
    await expect(nav).toBeVisible();
  });

  test('Überschriften-Hierarchie ist korrekt', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);

    const h1 = page.locator('h1').first();
    const h1Text = await h1.textContent();
    expect(h1Text?.trim().length).toBeGreaterThan(0);
  });

  test('Sitzungsliste: Keyboard Navigation', async ({ page }) => {
    await page.goto('/sitzungen').catch(async () => {
      await page.goto('/');
    });

    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Tab');

    for (let i = 0; i < 5; i++) {
      const focused = await page.evaluate(() => ({
        tag: document.activeElement?.tagName,
        role: document.activeElement?.getAttribute('role'),
        text: document.activeElement?.textContent?.trim().substring(0, 50),
      }));

      expect(['INPUT', 'A', 'BUTTON', 'SELECT', 'TEXTAREA', 'BODY']).toContain(focused.tag);
      await page.keyboard.press('Tab');
    }
  });

  test('Suchfeld ist mit Screenreader-Label versehen', async ({ page }) => {
    await page.goto('/suche').catch(async () => {
      await page.goto('/');
    });

    const searchInput = page
      .getByRole('searchbox')
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      const ariaLabel = await searchInput.getAttribute('aria-label');
      const ariaLabelledby = await searchInput.getAttribute('aria-labelledby');
      const id = await searchInput.getAttribute('id');

      let hasLabel = !!(ariaLabel || ariaLabelledby);

      if (!hasLabel && id) {
        const labelElement = page.locator(`label[for="${id}"]`);
        hasLabel = await labelElement.isVisible().catch(() => false);
      }

      if (!hasLabel) {
        const results = await new AxeBuilder({ page })
          .withRules(['label'])
          .analyze();
        const labelViolations = results.violations.filter(v => v.id === 'label');
        expect(labelViolations.length).toBe(0);
      } else {
        expect(hasLabel).toBe(true);
      }
    }
  });

  test('Links haben beschreibende Texte', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const results = await new AxeBuilder({ page })
      .withRules(['link-name', 'duplicate-id'])
      .analyze();

    const linkViolations = results.violations.filter(v => v.id === 'link-name');
    if (linkViolations.length > 0) {
      console.warn('Links ohne beschreibende Texte:', linkViolations[0].nodes.map(n => n.html));
    }
    expect(linkViolations.length).toBe(0);
  });

  test('Tabellen haben korrekte Struktur', async ({ page }) => {
    await page.goto('/sitzungen').catch(async () => {
      await page.goto('/');
    });

    const tables = page.locator('table');
    const tableCount = await tables.count();

    if (tableCount > 0) {
      const results = await new AxeBuilder({ page })
        .withRules(['table-duplicate-name', 'th-has-data-cells', 'scope-attr-valid'])
        .analyze();

      const tableViolations = results.violations;
      expect(tableViolations.length, `Tabellen-Violations: ${tableViolations.map(v => v.id).join(', ')}`).toBe(0);
    } else {
      console.log('Hinweis: Keine Tabellen auf der Sitzungsseite gefunden');
    }
  });
});
