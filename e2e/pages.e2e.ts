import { expect, test } from '@playwright/test';

test('landing presents the composition story and links the paper', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learning to compose');
	await page.getByRole('link', { name: 'Read the paper' }).click();
	await expect(page).toHaveURL(/\/paper$/);
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

test('paper includes completed word-problem results with their limits', async ({ page }) => {
	await page.goto('/paper');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Learning to compose');
	const wordProblems = page.locator('#word-problems');
	await expect(wordProblems).toContainText('294 runs');
	await expect(
		wordProblems
			.getByRole('row')
			.filter({ has: page.getByRole('rowheader', { name: 'Holonomy attention', exact: true }) })
			.getByRole('cell')
	).toHaveText(['100.0', '100.0', '99.8', '98.4']);
	await expect(wordProblems).toContainText('20,000-step amendment runs');
	await expect(wordProblems).toContainText('no demonstrated capacity gain');
	await expect(wordProblems).toContainText('97.3% (99.7, 96.9, 95.3)');
	await expect(wordProblems).toContainText('Some predictions failed');
	await expect(page.locator('main')).not.toContainText('results pending');
	await expect(page.locator('main')).toContainText('Seq2Tens');
});

test('old Learn and Report links land on the matching paper section', async ({ page }) => {
	await page.goto('/report#groups');
	await expect(page).toHaveURL(/\/paper#ceiling$/);
	await page.goto('/learn#binding');
	await expect(page).toHaveURL(/\/paper#head$/);
	await page.goto('/learn#word-problems');
	await expect(page).toHaveURL(/\/paper#word-problems$/);
	await page.goto('/report');
	await expect(page).toHaveURL(/\/paper$/);
});
