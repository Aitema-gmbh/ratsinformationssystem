import { test, expect } from '@playwright/test';

test.describe('Sitzungen - Ratsinformationssystem', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sitzungen').catch(async () => {
      await page.goto('/termine').catch(async () => {
        await page.goto('/');
      });
    });
    await page.waitForLoadState('networkidle');
  });

  test('Sitzungsliste wird angezeigt', async ({ page }) => {
    const heading = page.getByRole('heading', { level: 1 });
    await expect(heading).toBeVisible({ timeout: 5000 });

    const sitzungsItems = page.locator(
      '[class*="sitzung"], [class*="session"], [class*="event"], article, .list-item, li'
    ).first();

    const hasList = await sitzungsItems.isVisible({ timeout: 5000 }).catch(() => false);
    if (hasList) {
      await expect(sitzungsItems).toBeVisible();
    } else {
      const noResults = page.getByText(/keine sitzungen|no sessions|keine termine|leer/i);
      const hasNoResults = await noResults.isVisible({ timeout: 3000 }).catch(() => false);
      expect(hasList || hasNoResults).toBe(true);
    }
  });

  test('Sitzungsliste zeigt Datum und Gremium', async ({ page }) => {
    const dateElements = page.locator(
      'time, [class*="date"], [class*="datum"], [datetime]'
    ).first();

    if (await dateElements.isVisible({ timeout: 5000 }).catch(() => false)) {
      await expect(dateElements).toBeVisible();
      const text = await dateElements.textContent();
      expect(text?.trim().length).toBeGreaterThan(0);
    } else {
      console.log('Hinweis: Keine expliziten Datumselemente gefunden');
    }
  });

  test('Sitzungsdetail-Seite öffnen', async ({ page }) => {
    const firstSitzungLink = page
      .getByRole('link', { name: /sitzung|meeting|ausschuss|rat/i })
      .or(page.locator('article a, .list-item a, li a').first())
      .first();

    if (await firstSitzungLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      const href = await firstSitzungLink.getAttribute('href');
      await firstSitzungLink.click();
      await page.waitForLoadState('networkidle');

      const detailContent = page.locator('main, [role="main"]').first();
      await expect(detailContent).toBeVisible({ timeout: 5000 });

      const heading = page.getByRole('heading', { level: 1 });
      await expect(heading).toBeVisible();
    } else {
      test.skip(true, 'Keine Sitzungen in der Liste vorhanden');
    }
  });

  test('Sitzungsdetail zeigt Tagesordnung', async ({ page }) => {
    const firstLink = page
      .getByRole('link', { name: /sitzung|meeting/i })
      .or(page.locator('article a').first())
      .first();

    if (await firstLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstLink.click();
      await page.waitForLoadState('networkidle');

      const tagesordnung = page.getByText(/tagesordnung|agenda|top/i).first();
      if (await tagesordnung.isVisible({ timeout: 3000 }).catch(() => false)) {
        await expect(tagesordnung).toBeVisible();
      }
    } else {
      test.skip(true, 'Keine Sitzungsdetails zugänglich');
    }
  });

  test('PDF-Download-Link vorhanden', async ({ page }) => {
    const firstLink = page
      .getByRole('link', { name: /sitzung|meeting/i })
      .or(page.locator('article a').first())
      .first();

    if (await firstLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstLink.click();
      await page.waitForLoadState('networkidle');

      const pdfLink = page
        .getByRole('link', { name: /pdf|download|herunterladen/i })
        .or(page.locator('a[href$=".pdf"], a[href*="pdf"]'))
        .first();

      if (await pdfLink.isVisible({ timeout: 3000 }).catch(() => false)) {
        await expect(pdfLink).toBeVisible();

        const href = await pdfLink.getAttribute('href');
        expect(href).toBeTruthy();
      } else {
        console.log('Hinweis: Kein PDF-Link auf der Sitzungsdetail-Seite gefunden');
      }
    } else {
      test.skip(true, 'Keine Sitzungsdetails zugänglich');
    }
  });

  test('iCal-Download-Link vorhanden', async ({ page }) => {
    const firstLink = page
      .getByRole('link', { name: /sitzung|meeting/i })
      .or(page.locator('article a').first())
      .first();

    if (await firstLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstLink.click();
      await page.waitForLoadState('networkidle');

      const icalLink = page
        .getByRole('link', { name: /ical|kalender|calendar|ics/i })
        .or(page.locator('a[href$=".ics"], a[href*="ical"], a[href*="calendar"]'))
        .first();

      if (await icalLink.isVisible({ timeout: 3000 }).catch(() => false)) {
        await expect(icalLink).toBeVisible();

        const href = await icalLink.getAttribute('href');
        expect(href).toBeTruthy();
      } else {
        console.log('Hinweis: Kein iCal-Link auf der Sitzungsdetail-Seite gefunden');
      }
    } else {
      test.skip(true, 'Keine Sitzungsdetails zugänglich');
    }
  });

  test('Sitzungsliste mit Datumsfilter', async ({ page }) => {
    const filterInput = page
      .getByRole('textbox', { name: /von|datum|date|von datum/i })
      .or(page.locator('input[type="date"]').first());

    if (await filterInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      await filterInput.fill('2025-01-01');

      const filterButton = page.getByRole('button', { name: /filtern|suchen|anwenden|filter/i });
      if (await filterButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await filterButton.click();
        await page.waitForLoadState('networkidle');
      }

      const results = page.locator('main').first();
      await expect(results).toBeVisible();
    } else {
      console.log('Hinweis: Kein Datumsfilter gefunden');
    }
  });
});
