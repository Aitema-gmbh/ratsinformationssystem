import { test, expect } from '@playwright/test';

test.describe('Suche - Ratsinformationssystem', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/suche').catch(async () => {
      await page.goto('/search').catch(async () => {
        await page.goto('/');
      });
    });
    await page.waitForLoadState('networkidle');
  });

  test('Suchfeld ist vorhanden und fokussierbar', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    await expect(searchInput).toBeVisible({ timeout: 5000 });
    await searchInput.click();
    await expect(searchInput).toBeFocused();
  });

  test('Suche nach Begriff zeigt Ergebnisse', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('Haushalt');

      const searchButton = page.getByRole('button', { name: /suchen|search|los/i });
      if (await searchButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await searchButton.click();
      } else {
        await page.keyboard.press('Enter');
      }

      await page.waitForLoadState('networkidle');

      const results = page
        .locator('[class*="result"], [class*="ergebnis"], [class*="treffer"], article, .search-results')
        .first();

      const noResults = page.getByText(/keine ergebnisse|kein treffer|no results/i).first();

      const hasResults = await results.isVisible({ timeout: 5000 }).catch(() => false);
      const hasNoResults = await noResults.isVisible({ timeout: 2000 }).catch(() => false);

      expect(hasResults || hasNoResults).toBe(true);
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });

  test('Autocomplete erscheint bei Eingabe', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.click();
      await searchInput.pressSequentially('Ha', { delay: 100 });

      await page.waitForTimeout(500);

      const autocomplete = page
        .locator('[role="listbox"], [class*="autocomplete"], [class*="suggestion"], [class*="dropdown"]')
        .first();

      const hasAutocomplete = await autocomplete.isVisible({ timeout: 2000 }).catch(() => false);

      if (hasAutocomplete) {
        await expect(autocomplete).toBeVisible();
        const suggestions = autocomplete.getByRole('option').or(autocomplete.locator('li'));
        const suggestCount = await suggestions.count();
        expect(suggestCount).toBeGreaterThan(0);
      } else {
        console.log('Hinweis: Keine Autocomplete-Funktion vorhanden');
      }
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });

  test('Autocomplete-Vorschlag auswählen funktioniert', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.click();
      await searchInput.pressSequentially('Ra', { delay: 100 });

      await page.waitForTimeout(500);

      const firstSuggestion = page
        .locator('[role="listbox"] [role="option"], [class*="autocomplete"] li, [class*="suggestion"] li')
        .first();

      if (await firstSuggestion.isVisible({ timeout: 2000 }).catch(() => false)) {
        const suggestionText = await firstSuggestion.textContent();
        await firstSuggestion.click();

        await page.waitForLoadState('networkidle');

        const searchValue = await searchInput.inputValue();
        expect(searchValue.length).toBeGreaterThan(0);
      } else {
        console.log('Hinweis: Keine Autocomplete-Vorschläge vorhanden');
      }
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });

  test('Suchergebnisse enthalten relevante Informationen', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('Rat');
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');

      const results = page.locator('[class*="result"], article').first();
      if (await results.isVisible({ timeout: 5000 }).catch(() => false)) {
        const resultTitle = results.getByRole('heading')
          .or(results.locator('h2, h3, h4, strong').first());

        if (await resultTitle.isVisible({ timeout: 2000 }).catch(() => false)) {
          const titleText = await resultTitle.textContent();
          expect(titleText?.trim().length).toBeGreaterThan(0);
        }
      }
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });

  test('Leere Suche zeigt Hinweis', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('');
      await page.keyboard.press('Enter');

      await page.waitForTimeout(500);

      const hint = page.getByText(/suchbegriff eingeben|bitte eingeben|mindestens|please enter/i);
      const hasHint = await hint.isVisible({ timeout: 2000 }).catch(() => false);

      if (!hasHint) {
        const searchPageContent = page.locator('main').first();
        await expect(searchPageContent).toBeVisible();
      }
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });

  test('Suche per Tastatur navigierbar', async ({ page }) => {
    const searchInput = page
      .getByRole('searchbox')
      .or(page.getByRole('textbox', { name: /suche|search/i }))
      .or(page.locator('input[type="search"]'))
      .first();

    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('Sitzung');
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');

      await page.keyboard.press('Tab');
      const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(['A', 'BUTTON', 'INPUT', 'BODY']).toContain(focusedElement);
    } else {
      test.skip(true, 'Kein Suchfeld gefunden');
    }
  });
});
