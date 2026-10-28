/**
 * Calls in the middle of the words (REASON_FORMAT) in the browser, end to end, with the model replaced by the page's
 * stand-in (webgpu/stub.ts). The stand-in plays the engine's own runs of reason_core's fixture transcripts on a
 * scripted model (e2e/fixtures/reason-runs.json, checked by webgpu/engine-reason.spec.ts) back as the engine's events:
 * words, a call, the clock's final line, words, … The model that writes this format is still training, so MULTI_CALL
 * is off and the page sends no such option; the chat renders any run that has calls in it.
 */
import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const [chain, retry, lies] = JSON.parse(readFileSync('e2e/fixtures/reason-runs.json', 'utf8'));
const prose = JSON.parse(readFileSync('static/traces/live-prose-train-256.json', 'utf8'));
const SHOTS = process.env.REASON_SHOTS;
// the reference's error transcript asks the chain's question: give it its own, so the stand-in can tell them apart
retry.prompt = chain.prompt.replace('By how much', 'Again: by how much');

async function stub(page: Page, delay = 4) {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.addInitScript(
		(s) => {
			(globalThis as { __SAVANT_STUB__?: unknown }).__SAVANT_STUB__ = s;
		},
		{ gpu: 'Stand-in GPU', traces: [prose, chain, retry, lies], delay, loadMs: 300 }
	);
}

async function ask(page: Page, question: string) {
	await page.getByRole('button', { name: /Load Savant-4B/ }).click();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
	await page.getByRole('textbox', { name: 'Your question' }).fill(question);
	await page.getByRole('button', { name: 'Send' }).click();
}

const reply = (page: Page) => page.locator('.bot').last();
const callLine = (page: Page, k: number) =>
	reply(page).getByRole('button', { name: new RegExp(`^call ${k} `) });

test('a reply with calls in the middle: the words, three certified calls and their results, the answer', async ({
	page
}) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await stub(page, 8);
	await page.goto('/interpreter');
	await ask(page, chain.prompt);

	// while it runs: the call the clock has, in the status line, after the finished ones
	await expect(page.getByRole('status')).toContainText(/Call 1 · Certifying register · row/, {
		timeout: 20_000
	});
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-running.png` });
	await expect(page.getByRole('status')).toContainText(/Call 3 · /, {
		timeout: 20_000
	});
	await expect(reply(page)).toContainText("That is store X's total.");
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-call3.png` });

	// finished: the header line, the words between the calls, each call compact with its result
	await expect(reply(page).locator('.reason .summary')).toHaveText('3 calls · all certified', {
		timeout: 20_000
	});
	const calls = chain.reason.calls;
	for (const c of calls) {
		await expect(callLine(page, c.k)).toContainText('task: ');
		await expect(reply(page).getByLabel(`Result of call ${c.k}`)).toHaveText(`→ ${c.value}`);
	}
	await expect(reply(page).locator('.call .status').first()).toContainText(
		'certified · 200 rows · run exact'
	);
	await expect(reply(page)).toContainText(`Answer: ${calls[2].value}`);
	await expect(reply(page).locator('.prov')).toContainText('every call run by the clock');
	// the stand-in got no multiCall option: the flag is off
	const sent = await page.evaluate(
		() =>
			(globalThis as { __SAVANT_STUB__?: { multiCalls?: unknown[] } }).__SAVANT_STUB__?.multiCalls
	);
	expect(sent).toEqual([null]);

	// the panels on the right show the last call that ran, and a picker for the others
	const bar = page.locator('.bar');
	await expect(bar.locator('.title')).toHaveText('Call 3, 32 columns');
	const run = page.locator('main').getByRole('region', { name: 'The run' });
	await expect(run.getByLabel('The difference so far')).toHaveText(
		calls[2].value.padStart(32, '0')
	);
	await expect(page.locator('main').getByRole('region', { name: 'The certificate' })).toContainText(
		'2 borrows and 100 digit pairs'
	);
	await bar.getByRole('group', { name: 'Call' }).getByRole('button', { name: '1' }).click();
	await expect(bar.locator('.title')).toHaveText('Call 1, 31 columns');
	await expect(run.getByLabel('The sum so far')).toHaveText(calls[0].value.padStart(31, '0'));

	// a call opens to the run and the certificate inline, and reads where it read
	await callLine(page, 3).click();
	await expect(callLine(page, 3)).toHaveAttribute('aria-expanded', 'true');
	const open = reply(page).locator('.call.open');
	await expect(open.locator('.reads')).toContainText('first');
	await expect(open.locator('.reads')).toContainText('from result 1');
	await expect(open.locator('.reads')).toContainText('from result 2');
	await expect(open.getByRole('region', { name: 'The run' })).toContainText('borrow');
	await expect(open.getByRole('region', { name: 'The certificate' })).toContainText('200 of 200');
	await expect(open).toContainText('32 of 32 columns had both forwards bitwise equal');
	await expect(open).toContainText('Π built fresh for this call');
	await expect(open).toContainText('not whether the table is the subtracter');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-done.png` });
	await open.getByRole('button', { name: 'Show it in the panels' }).click();
	await expect(bar.locator('.title')).toHaveText('Call 3, 32 columns');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(1440);
});

test('an error line where the clock cannot read a call, then the retry', async ({ page }) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await stub(page);
	await page.goto('/interpreter');
	await ask(page, retry.prompt);
	await expect(reply(page).locator('.reason .summary')).toHaveText(
		'3 calls · 2 ran, both certified · call 2 got an error line',
		{ timeout: 20_000 }
	);
	await expect(reply(page).locator('.call').nth(1).locator('.status')).toHaveText(
		'error: first number: no result 5'
	);
	await expect(reply(page)).toContainText('There is no result 5; I meant result 1.');
	await expect(reply(page).getByLabel('Result of call 3')).toHaveText(
		`→ ${retry.reason.calls[2].value}`
	);
	// the error line took no number: call 3 made result 2 (REASON_FORMAT §12)
	await expect(reply(page).locator('.call').nth(2).locator('.status')).toContainText('as result 2');
	// the error call opens to its program and the clock's reason
	await callLine(page, 2).click();
	await expect(reply(page).locator('.call.open')).toContainText(
		'the clock could not run call 2: first number: no result 5'
	);
	await expect(reply(page).locator('.call.open .src')).toContainText('first: result 5');
	// in the panels, the error call has no run
	await page
		.locator('.bar')
		.getByRole('group', { name: 'Call' })
		.getByRole('button', { name: '2' })
		.click();
	await expect(page.getByRole('region', { name: 'No run' })).toContainText(
		'the clock could not run call 2'
	);
	await page.getByRole('group', { name: 'Call' }).getByRole('button', { name: '3' }).click();
	await expect(page.locator('.bar .title')).toHaveText('Call 3, 32 columns');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-error.png` });
});

test('at phone width a reply with calls fits, opened or not, with no sideways scroll', async ({
	page
}) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await stub(page);
	await page.goto('/interpreter');
	await ask(page, chain.prompt);
	await expect(reply(page).locator('.reason .summary')).toHaveText('3 calls · all certified', {
		timeout: 20_000
	});
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
	await callLine(page, 1).click();
	await expect(
		reply(page).locator('.call.open').getByRole('region', { name: 'The run' })
	).toBeVisible();
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-phone.png`, fullPage: true });
});

test('a tape read from the notes runs as a call, and its result is a state', async ({ page }) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await stub(page);
	await page.goto('/interpreter');
	await ask(page, lies.prompt);
	await expect(reply(page).locator('.reason .summary')).toHaveText('1 call · certified', {
		timeout: 20_000
	});
	await expect(reply(page).getByLabel('Result of call 1')).toHaveText('→ honest');
	await callLine(page, 1).click();
	const open = reply(page).locator('.call.open');
	await expect(open.locator('.reads')).toContainText('40 events');
	await expect(open.locator('.reads')).toContainText('from the notes');
	await expect(page.locator('.bar .title')).toHaveText('Call 1, 40 events');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/reason-tape.png` });
});
