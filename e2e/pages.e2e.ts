import { expect, test } from '@playwright/test';

test('root redirects to the SET bench', async ({ page }) => {
	await page.goto('/');
	await expect(page).toHaveURL(/\/compare$/);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('SET bench');
	await expect(page.getByRole('button', { name: 'Start training' })).toBeVisible();
});

test('learn renders the derivation with KaTeX', async ({ page }) => {
	await page.goto('/learn');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('From pairs to triples');
	await expect(page.locator('#barrier .katex').first()).toBeVisible();
});

test('explore and notes render', async ({ page }) => {
	await page.goto('/explore');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Cubic attention');
	await page.goto('/notes');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Research log');
});
