/**
 * Certified arithmetic in the browser (ARITH_FORMAT number mode), end to end, with the model replaced by the page's
 * stand-in (webgpu/stub.ts). The stand-in replays the engine's own run of "What is 4096 plus 77?" on a scripted model
 * (e2e/fixtures/arith-run.json, checked by webgpu/engine-arith.spec.ts) and reruns its certified table on the numbers
 * of the question sent, as a certified executor would. The real arithmetic model is not exported yet.
 */
import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const arith = JSON.parse(readFileSync('e2e/fixtures/arith-run.json', 'utf8'));
const prose = JSON.parse(readFileSync('static/traces/live-prose-train-256.json', 'utf8'));
const SHOTS = process.env.ARITH_SHOTS;

async function stub(page: Page, delay = 25) {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.addInitScript(
		(s) => {
			(globalThis as { __SAVANT_STUB__?: unknown }).__SAVANT_STUB__ = s;
		},
		{ gpu: 'Stand-in GPU', traces: [prose, arith], delay, loadMs: 600 }
	);
}

const load = async (page: Page) => {
	await page.getByRole('button', { name: /Load Savant-4B/ }).click();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
};

const additionChip = (page: Page) =>
	page.getByRole('group', { name: 'Suggested questions' }).getByTitle('Addition', { exact: true });

const question = (page: Page) => page.getByRole('textbox', { name: 'Your question' });

async function numbers(page: Page) {
	const m = (await question(page).inputValue()).match(/^What is (\d+) plus (\d+)\?$/);
	expect(m).not.toBeNull();
	return [m![1], m![2]] as const;
}

test('the published page has no Addition suggestion until the arithmetic model is pinned', async ({
	page
}) => {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.goto('/interpreter');
	await expect(
		page.getByRole('group', { name: 'Suggested questions' }).getByTitle('Shell game')
	).toBeVisible();
	await expect(additionChip(page)).toHaveCount(0);
	await expect(page.getByText(/Arithmetic and other new kinds of question/)).toBeVisible();
});

test('the Addition suggestion writes two random numbers of the chosen length', async ({ page }) => {
	await stub(page);
	await page.goto('/interpreter');
	await additionChip(page).click();
	const lengths = page.getByRole('group', { name: 'Length' });
	await expect(lengths.getByRole('button')).toHaveText(['10', '100', '1,000']);
	const [a, b] = await numbers(page);
	expect([a.length, b.length]).toEqual([10, 10]);
	await lengths.getByRole('button', { name: '1,000' }).click();
	const [c, d] = await numbers(page);
	expect([c.length, d.length]).toEqual([1000, 1000]);
	expect(c[0]).not.toBe('0');
	await lengths.getByRole('button', { name: '10', exact: true }).click();
	const [e] = await numbers(page);
	expect(e.length).toBe(10);
	expect(e).not.toBe(a);
	await expect(page.getByText(/additions of any length among them/)).toBeVisible();
});

test('an addition runs: the written sum, both cells of every row, the carry machine, the sum, a poke', async ({
	page
}) => {
	await page.setViewportSize({ width: 1440, height: 1000 });
	await stub(page, 30);
	await page.goto('/interpreter');
	await load(page);
	await additionChip(page).click();
	const [a, b] = await numbers(page);
	const sum = (BigInt(a) + BigInt(b)).toString();
	await expect(page.getByText(/Enter runs it in this browser · /)).toBeVisible();
	await page.getByRole('button', { name: 'Send' }).click();

	// certifying: the rows fill in, two cells each
	const cert = page.getByRole('region', { name: 'The certificate' });
	await expect(cert).toContainText('so far');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/arith-certify.png` });

	await expect(page.locator('.bot .answer')).toHaveText(`The sum is ${sum}.`, { timeout: 20_000 });
	await expect(page.locator('.bot .prov')).toContainText(
		'Right: the clock’s sum is the sum of the two numbers it read'
	);
	await expect(page.locator('.bot .note')).toContainText('wrote the adder’s 200-row table');
	await expect(cert).toContainText('200 of 200');
	await expect(cert).toContainText('both cells of every row right');
	await expect(cert).toContainText('11 of 11 columns had both forwards bitwise equal');

	const run = page.getByRole('region', { name: 'The run' });
	await expect(run).toContainText('Savant-4B, two forwards per column');
	await expect(run.getByLabel('The sum so far')).toHaveText(sum.padStart(11, '0'));
	await expect(run).toContainText('11 of 11 digits');
	const program = page.getByRole('region', { name: 'The program' });
	await expect(program).toContainText('2 carries × 100 digit pairs');
	await expect(program.getByRole('img', { name: /carry 0 and carry 1/ })).toContainText(
		'a+b ≤ 9 / a+b'
	);
	const state = page.getByRole('region', { name: 'The state is digital' });
	await expect(state).toContainText('the second forward writes');

	// the numbers went with the question, to score it
	const additions = await page.evaluate(
		() => (globalThis as { __SAVANT_STUB__?: { additions?: unknown[] } }).__SAVANT_STUB__?.additions
	);
	expect(additions).toEqual([{ a, b }]);

	// back to column 3, then force the other carry and run on
	await run.getByRole('button', { name: /^Column 3:/ }).click();
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/arith-run.png` });
	const poke = page.getByRole('region', { name: 'Poke the brain' });
	await expect(poke).toContainText('Force a carry');
	await poke
		.getByRole('group', { name: 'State to force at the playhead' })
		.getByRole('button', { disabled: false })
		.first()
		.click();
	await poke.getByRole('button', { name: /^Force .+ run on$/ }).click();
	await expect(poke).toContainText("clock's sum");
	await expect(poke).toContainText('The sum came out where the table says from the forced carry.');
	await expect(poke).toContainText('columns after the poke bitwise equal');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/arith-poke.png` });
});

test('a 1,000-digit addition runs and its sum wraps inside the panels', async ({ page }) => {
	await page.setViewportSize({ width: 1440, height: 1000 });
	await stub(page, 4);
	await page.goto('/interpreter');
	await load(page);
	await additionChip(page).click();
	await page.getByRole('group', { name: 'Length' }).getByRole('button', { name: '1,000' }).click();
	const [a, b] = await numbers(page);
	const sum = (BigInt(a) + BigInt(b)).toString();
	await page.getByRole('button', { name: 'Send' }).click();
	// the stand-in plays one column per event, as the engine does
	await expect(page.getByRole('status')).toContainText(/Adding · column [\d,]+ of 1,001/, {
		timeout: 20_000
	});
	await expect(page.getByText(/Running in this browser: column/)).toBeVisible();
	await expect(page.locator('.bot .answer')).toHaveText(`The sum is ${sum}.`, { timeout: 60_000 });
	const run = page.getByRole('region', { name: 'The run' });
	await expect(run).toContainText('columns 989 to 1,001 of 1,001');
	await expect(run.getByLabel('The sum so far')).toHaveText(sum.padStart(1001, '0'));
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/arith-1000.png` });
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(1440);
});

test('an addition typed by hand is checked on the page, and at phone width nothing scrolls sideways', async ({
	page
}) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await stub(page, 6);
	await page.goto('/interpreter');
	await load(page);
	await question(page).fill('What is 99999999999999999999 plus 1?');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer')).toHaveText('The sum is 100000000000000000000.', {
		timeout: 20_000
	});
	await expect(page.locator('.bot .prov')).toContainText('Right: the clock’s sum is the sum');
	await expect(page.locator('.bot .prov')).not.toContainText('the words');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/arith-phone.png`, fullPage: true });
});
