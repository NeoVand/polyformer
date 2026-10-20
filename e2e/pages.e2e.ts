import { expect, test } from '@playwright/test';

test('landing presents the composition story and links the course and paper', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learning to compose');
	await page.getByRole('link', { name: 'Read how it works' }).click();
	await expect(page).toHaveURL(/\/learn$/);
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learning to compose');
	await expect(page.locator('#groups')).toContainText('A group is a rule for combining');
});

test('group comparison is recorded and keeps training controls out of the suite', async ({
	page
}) => {
	await page.goto('/compare');
	await page.locator('.title-row').getByRole('button', { name: 'Groups', exact: true }).click();
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('What composition changes');
	await expect(page.getByText(/77\.2287515874/)).toBeVisible();
	await expect(page.getByRole('button', { name: 'Train', exact: true })).toHaveCount(0);
	await page.locator('.title-row').getByRole('button', { name: 'SET', exact: true }).click();
	await expect(page.getByRole('button', { name: 'Train', exact: true })).toBeVisible();
});

test('holonomy lab opens with a visible model and can inspect the real recording', async ({
	page
}) => {
	await page.goto('/explore/groups');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learning to turn');
	await expect(
		page.getByRole('group', { name: 'Group element', exact: true }).getByRole('button')
	).toHaveCount(60);
	await page.getByRole('button', { name: 'Recorded', exact: true }).click();
	await expect(page.getByText(/Learned head/)).toBeVisible();
	await page.getByRole('button', { name: 'Element 12:', exact: false }).click();
	await expect(page.getByRole('button', { name: 'Element 12:', exact: false })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
});

test('report preserves the scope and the pending word-problem handoff', async ({ page }) => {
	await page.goto('/report');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Learning to compose');
	await expect(page.locator('main')).toContainText('results pending');
	await expect(page.locator('main')).toContainText('Seq2Tens');
});
