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

test('report includes completed word-problem results with their limits', async ({ page }) => {
	await page.goto('/report');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Learning to compose');
	const wordProblems = page.locator('#word-problems');
	await expect(wordProblems).toContainText('294 runs');
	await expect(
		wordProblems
			.getByRole('row')
			.filter({ has: page.getByRole('rowheader', { name: 'Holonomy', exact: true }) })
			.getByRole('cell')
	).toHaveText(['100.0', '100.0', '99.8', '98.4']);
	await expect(wordProblems).toContainText('20,000-step amendment runs');
	await expect(wordProblems).toContainText('no demonstrated capacity gain');
	await expect(wordProblems).toContainText('97.3% (99.7, 96.9, 95.3)');
	await expect(wordProblems).toContainText('Some predictions failed');
	await expect(page.locator('main')).not.toContainText('results pending');
	await expect(page.locator('main')).toContainText('Seq2Tens');
	await page.goto('/learn');
	await expect(page.locator('#word-problems')).toContainText('98.4%');
	await expect(
		page.locator('#word-problems').getByRole('link', { name: 'full results' })
	).toHaveAttribute('href', '/report#word-problems');
});
