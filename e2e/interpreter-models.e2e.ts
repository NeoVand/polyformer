/**
 * The visitor picks which Savant to download. r3 is live. The reasoning model’s weights are still a placeholder, so
 * the published page hides it; the stand-in offers it, and a question then goes out with that model’s multiCall flag.
 * Forgetting a download deletes that model’s cache prefix and leaves the other model’s files.
 */
import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const prose = JSON.parse(readFileSync('static/traces/live-prose-train-256.json', 'utf8'));
const [chain] = JSON.parse(readFileSync('e2e/fixtures/reason-runs.json', 'utf8'));
const SHOTS = process.env.MODEL_SHOTS;

async function stub(page: Page, delay = 4) {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.addInitScript(
		(s) => {
			(globalThis as { __SAVANT_STUB__?: unknown }).__SAVANT_STUB__ = s;
		},
		{ gpu: 'Stand-in GPU', traces: [prose, chain], delay, loadMs: 400 }
	);
}

const model = (page: Page) => page.getByRole('region', { name: 'The model' });
const choice = (page: Page, name: RegExp) => model(page).getByRole('radio', { name });
const r3 = (page: Page) => choice(page, /Savant-4B preview r3/);
const reason = (page: Page) => choice(page, /Savant-4B Reason \(preview\)/);

async function bases(page: Page) {
	await expect(reason(page)).toBeVisible();
	const a = await r3(page).getAttribute('data-base');
	const b = await reason(page).getAttribute('data-base');
	expect(a).toBeTruthy();
	expect(b).toBeTruthy();
	return [new URL(a!, page.url()).href, new URL(b!, page.url()).href] as const;
}

test('the published page hides the reasoning model until its weights are filled in', async ({
	page
}) => {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.goto('/interpreter');
	await expect(page.getByText('Certified addition and the six task families')).toBeVisible();
	await expect(page.getByRole('button', { name: /^Load Savant-4B(?! Reason)/ })).toContainText(
		'~3.3 GB'
	);
	await expect(reason(page)).toHaveCount(0);
	await expect(page.getByTitle('Story', { exact: true })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Two stores', exact: true })).toHaveCount(0);
});

test('each model is a choice, with its own questions, and the choice is remembered', async ({
	page
}) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await stub(page);
	await page.goto('/interpreter');
	await expect(r3(page)).toHaveAttribute('aria-checked', 'true');
	await expect(r3(page)).toContainText('Certified addition and the six task families');
	await expect(r3(page)).toContainText('~3.3 GB');
	await expect(reason(page)).toContainText('Reasons in words and calls programs mid-thought');
	await expect(page.getByTitle('Story', { exact: true })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Two stores', exact: true })).toHaveCount(0);
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/model-picker-desktop.png` });

	await reason(page).click();
	await expect(reason(page)).toHaveAttribute('aria-checked', 'true');
	await expect(r3(page)).toHaveAttribute('aria-checked', 'false');
	await expect(page.getByTitle('Story', { exact: true })).toHaveCount(0);
	const stores = page.getByRole('button', { name: 'Two stores', exact: true });
	await expect(stores).toBeVisible();
	await expect(page.getByTitle('Addition', { exact: true })).toBeVisible();
	await expect(page.getByText(/composites from its training templates/)).toBeVisible();
	await expect(page.getByText(/Additions of any length are among them too/)).toBeVisible();
	await stores.click();
	await expect(page.getByRole('textbox', { name: 'Your question' })).toHaveValue(
		/Store X produced 4821/
	);

	await page.reload();
	await expect(reason(page)).toHaveAttribute('aria-checked', 'true');
	expect(await page.evaluate(() => localStorage.getItem('polyformer.interpreter.model'))).toBe(
		'reason'
	);
});

test('selecting each model sends that model’s call flag, and a reasoning run shows its calls', async ({
	page
}) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await stub(page, 8);
	await page.goto('/interpreter');
	await reason(page).click();
	await page.getByRole('button', { name: /Load Savant-4B Reason/ }).click();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
	await page.getByRole('textbox', { name: 'Your question' }).fill(chain.prompt);
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .reason .summary')).toHaveText('3 calls · all certified', {
		timeout: 20_000
	});
	await expect(page.locator('.bot .prov')).toContainText('Savant-4B Reason (preview)');
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/model-picker-reason.png` });

	await r3(page).click();
	await page.getByRole('button', { name: /^Load Savant-4B(?! Reason)/ }).click();
	await expect(page.getByText(/running in this tab on/i)).toBeVisible();
	await page.getByRole('textbox', { name: 'Your question' }).fill(prose.prompt);
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer').last()).toHaveText(prose.answer, { timeout: 15_000 });
	await expect(page.locator('.bot .prov').last()).toContainText('Savant-4B preview r3');

	const sent = await page.evaluate(
		() =>
			(globalThis as { __SAVANT_STUB__?: { multiCalls?: unknown[] } }).__SAVANT_STUB__?.multiCalls
	);
	expect(sent).toEqual([true, null]);
});

test('forgetting one download leaves the other model’s files', async ({ page }) => {
	await stub(page);
	await page.goto('/interpreter');
	const [r3url, reasonUrl] = await bases(page);
	expect(r3url.startsWith(reasonUrl) || reasonUrl.startsWith(r3url)).toBe(false);
	await page.evaluate(
		async ({ a, b }) => {
			const c = await caches.open('transformers-cache');
			await c.put(new URL('onnx/a', a).href, new Response('r3'));
			await c.put(new URL('onnx/b', b).href, new Response('reason'));
		},
		{ a: r3url, b: reasonUrl }
	);

	await page.getByRole('button', { name: /^Load Savant-4B(?! Reason)/ }).click();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
	await page.getByRole('button', { name: 'Forget the download' }).click();
	await expect
		.poll(() =>
			page.evaluate(async () =>
				(await (await caches.open('transformers-cache')).keys()).map((r) => r.url)
			)
		)
		.toEqual([new URL('onnx/b', reasonUrl).href]);

	await reason(page).click();
	await page.getByRole('button', { name: /Load Savant-4B Reason/ }).click();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
	await page.getByRole('button', { name: 'Forget the download' }).click();
	await expect
		.poll(() =>
			page.evaluate(async () =>
				(await (await caches.open('transformers-cache')).keys()).map((r) => r.url)
			)
		)
		.toEqual([]);
});

test('the picker fits a phone width', async ({ page }) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await stub(page);
	await page.goto('/interpreter');
	await expect(reason(page)).toBeVisible();
	await expect(r3(page)).toContainText('one program per question');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
	await reason(page).click();
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
	if (SHOTS) await page.screenshot({ path: `${SHOTS}/model-picker-phone.png`, fullPage: true });
});
