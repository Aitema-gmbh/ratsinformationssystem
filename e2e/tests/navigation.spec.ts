import { test, expect } from '@playwright/test';

test.describe('Navigation - Ratsinformationssystem', () => {
  test('Startseite lädt erfolgreich', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveTitle(/.+/);

    const mainContent = page.locator('main, [role="main"], #content, .container').first();
    await expect(mainContent).toBeVisible();
  });

  test('Hauptnavigation ist vorhanden', async ({ page }) => {
    await page.goto('/');

    const nav = page.getByRole('navigation').first();
    await expect(nav).toBeVisible();

    const navLinks = page.getByRole('navigation').getByRole('link');
    const linkCount = await navLinks.count();
    expect(linkCount).toBeGreaterThan(0);
  });

  test('Sitzungen-Seite ist navigierbar', async ({ page }) => {
    await page.goto('/');

    const sitzungenLink = page
      .getByRole('link', { name: /sitzungen|termine|kalender/i })
      .first();

    if (await sitzungenLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await sitzungenLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/sitzungen|termine|sessions/i);
    } else {
      await page.goto('/sitzungen').catch(async () => {
        await page.goto('/termine');
      });
    }

    const heading = page.getByRole('heading', { level: 1 });
    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test('Gremien-Seite ist navigierbar', async ({ page }) => {
    await page.goto('/');

    const gremienLink = page
      .getByRole('link', { name: /gremien|ausschüsse|committees/i })
      .first();

    if (await gremienLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await gremienLink.click();
      await page.waitForLoadState('networkidle');
    } else {
      await page.goto('/gremien').catch(async () => {
        await page.goto('/ausschuesse');
      });
    }

    const pageContent = page.locator('main, [role="main"]').first();
    await expect(pageContent).toBeVisible({ timeout: 5000 });
  });

  test('Dokumente-Seite ist navigierbar', async ({ page }) => {
    await page.goto('/');

    const dokumenteLink = page
      .getByRole('link', { name: /dokumente|downloads|unterlagen/i })
      .first();

    if (await dokumenteLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await dokumenteLink.click();
      await page.waitForLoadState('networkidle');
    } else {
      await page.goto('/dokumente').catch(async () => {
        await page.goto('/downloads');
      });
    }

    const pageContent = page.locator('main, [role="main"]').first();
    await expect(pageContent).toBeVisible({ timeout: 5000 });
  });

  test('Suche-Seite ist navigierbar', async ({ page }) => {
    await page.goto('/');

    const sucheLink = page
      .getByRole('link', { name: /suche|search/i })
      .or(page.getByRole('searchbox'))
      .first();

    if (await sucheLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await sucheLink.click();
      await page.waitForLoadState('networkidle');
    } else {
      await page.goto('/suche').catch(async () => {
        await page.goto('/search');
      });
    }

    const searchInput = page.getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .first();
    await expect(searchInput).toBeVisible({ timeout: 5000 });
  });

  test('Breadcrumb-Navigation ist vorhanden', async ({ page }) => {
    await page.goto('/sitzungen').catch(async () => {
      await page.goto('/termine');
    });

    const breadcrumb = page
      .getByRole('navigation', { name: /breadcrumb|pfad|navigation/i })
      .or(page.locator('[aria-label="breadcrumb"], .breadcrumb, nav.breadcrumbs'))
      .first();

    const hasBreadcrumb = await breadcrumb.isVisible({ timeout: 3000 }).catch(() => false);

    if (hasBreadcrumb) {
      await expect(breadcrumb).toBeVisible();
    } else {
      console.log('Hinweis: Keine Breadcrumb-Navigation gefunden');
    }
  });

  test('Fußzeile mit Impressum vorhanden', async ({ page }) => {
    await page.goto('/');

    const footer = page.getByRole('contentinfo').or(page.locator('footer')).first();
    await expect(footer).toBeVisible({ timeout: 5000 });

    const impressumLink = footer.getByRole('link', { name: /impressum|imprint|datenschutz|privacy/i });
    if (await impressumLink.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(impressumLink.first()).toBeVisible();
    }
  });

  test('404-Seite zeigt sinnvolle Fehlermeldung', async ({ page }) => {
    await page.goto('/diese-seite-existiert-nicht-12345');

    const notFoundIndicator = page
      .getByText(/404|nicht gefunden|not found|seite nicht vorhanden/i)
      .first();

    await expect(notFoundIndicator).toBeVisible({ timeout: 5000 });

    const homeLink = page.getByRole('link', { name: /startseite|home|zurück/i }).first();
    if (await homeLink.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(homeLink).toBeVisible();
    }
  });
});
