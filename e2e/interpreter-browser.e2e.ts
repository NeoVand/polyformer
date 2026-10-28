/**
 * Savant-4B in the browser, end to end, with the model replaced by the page's stand-in (webgpu/stub.ts): it plays a
 * recorded run back as the engine's own events, so every stage the page shows for a real run is exercised without a
 * GPU or a 2.8 GB download. The real model is checked separately (research/demolive/DEMOLIVE.md, "In the browser").
 */
import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const read = (id: string) => JSON.parse(readFileSync(`static/traces/${id}.json`, 'utf8'));
const prompts: {
	prompts: { id: string; title: string; question: string; recorded: string | null }[];
} = JSON.parse(readFileSync('static/interpreter/prompts.json', 'utf8'));
const prose = read('live-prose-train-256');
const robot = read('live-robot-train-2048');

async function stub(page: Page, opts: { gpu?: string; traces?: unknown[]; delay?: number } = {}) {
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.addInitScript(
		(s) => {
			(globalThis as { __SAVANT_STUB__?: unknown }).__SAVANT_STUB__ = s;
		},
		{
			gpu: 'gpu' in opts ? opts.gpu : 'Stand-in GPU',
			traces: opts.traces ?? [prose],
			delay: opts.delay ?? 12,
			loadMs: 1200
		}
	);
}

const load = async (page: Page) => {
	await page.getByRole('button', { name: /Load Savant-4B/ }).click();
	await expect(page.getByRole('progressbar', { name: 'Download' })).toBeVisible();
	await expect(page.getByText(/Running in this tab on/)).toBeVisible();
};

const pick = async (page: Page, family: string, title: string) => {
	await page
		.getByRole('group', { name: 'Suggested questions' })
		.getByTitle(family, { exact: true })
		.click();
	await page.getByTitle(title, { exact: true }).click();
};

test('the model step: the offer, the licence, the download and where it runs', async ({ page }) => {
	await stub(page);
	await page.goto('/interpreter');
	const model = page.getByRole('region', { name: 'The model' });
	await expect(model).toContainText('Savant-4B preview');
	await expect(model.getByRole('button', { name: /Load Savant-4B/ })).toContainText(
		'nothing leaves your browser'
	);
	await expect(model).toContainText('Weights © the Polyformer authors, all rights reserved');
	await expect(model.getByRole('link', { name: 'Model card' })).toHaveAttribute(
		'href',
		'https://huggingface.co/mohsenvand/savant-4b-preview'
	);
	await load(page);
	await expect(page.getByText('Interpreter, in your browser')).toBeVisible();
	await expect(model).toContainText('Stand-in GPU');
});

test('a suggested question runs live: program, certificate, ticks, answer, then a poke', async ({
	page
}) => {
	await stub(page, { delay: 90 });
	await page.goto('/interpreter');
	await load(page);
	await pick(page, 'Story', 'Story, 64 events');
	await expect(page.getByRole('textbox', { name: 'Your question' })).toHaveValue(
		prompts.prompts.find((p) => p.id === 'prose-64')!.question
	);
	await expect(page.getByText(/Enter runs it in this browser/)).toBeVisible();
	await page.getByRole('button', { name: 'Send' }).click();

	// the model writing, then the panels as the clock takes over
	await expect(page.getByRole('region', { name: 'The model at work' })).toBeVisible();
	await expect(page.getByRole('status')).toContainText(/Reading your question|Writing the program/);
	const cert = page.getByRole('region', { name: 'The certificate' });
	await expect(cert).toContainText('so far');
	await expect(page.getByRole('status')).toContainText(/Running register · tick/);
	await expect(page.locator('.bot .answer')).toHaveText(prose.answer, { timeout: 15_000 });
	await expect(cert).toContainText('8 of 8');
	await expect(page.locator('.bot .prov')).toContainText('in this browser on Stand-in GPU');
	await expect(page.getByRole('region', { name: 'The run' })).toContainText(
		'Attention weights are not measured in the browser'
	);

	// a poke, in this browser
	const poke = page.getByRole('region', { name: 'Poke the brain' });
	await poke
		.getByRole('group', { name: 'State to force at the playhead' })
		.getByRole('button', { disabled: false })
		.first()
		.click();
	await poke.getByRole('button', { name: /^Force .+ run on$/ }).click();
	await expect(poke).toContainText('The stand-in answers');
	await expect(poke).toContainText('run in this browser');
	await expect(poke).toContainText('needs the base Qwen3-4B weights');
	const poked = await page.evaluate(
		() => (globalThis as { __SAVANT_STUB__?: { poked?: unknown[] } }).__SAVANT_STUB__?.poked
	);
	expect(poked).toHaveLength(1);
});

test('a recorded question run here keeps its recorded base answer and adapter-off run', async ({
	page
}) => {
	await stub(page);
	await page.goto('/interpreter');
	await load(page);
	await pick(page, 'Story', 'Story, 256 events, recorded');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer')).toHaveText(prose.answer, { timeout: 15_000 });
	await page.getByRole('button', { name: "Show the base model's answer (recorded)" }).click();
	await expect(page.locator('.bot .base')).toContainText('recorded');
	const poke = page.getByRole('region', { name: 'Poke the brain' });
	await poke
		.getByRole('group', { name: 'The executor adapter' })
		.getByRole('button', { name: 'off' })
		.click();
	await expect(poke).toContainText(`Answer becomes ${prose.registers[0].ablation.answer}`);
});

test('two registers, a question typed by hand, and the register picker', async ({ page }) => {
	await stub(page, { traces: [robot], delay: 4 });
	await page.goto('/interpreter');
	await load(page);
	await page
		.getByRole('textbox', { name: 'Your question' })
		.fill('A robot walks: left up up right. Where?');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer')).toHaveText(robot.answer, { timeout: 30_000 });
	await expect(page.locator('.bot .prov')).toContainText('not one of the suggested ones');
	const regs = page.getByRole('group', { name: 'Register' });
	await regs.getByRole('button', { name: 'y' }).click();
	await expect(page.getByRole('region', { name: 'The program' })).toContainText(
		'register y of x, y'
	);
});

test('lookup mode goes with the question when chosen, and every tick runs otherwise', async ({
	page
}) => {
	await stub(page, { delay: 4 });
	await page.goto('/interpreter');
	await load(page);
	const ticks = page.getByRole('group', { name: 'Ticks' });
	await expect(ticks.getByRole('button', { name: /every event/ })).toHaveAttribute(
		'aria-pressed',
		'true'
	);
	await pick(page, 'Parity', 'Parity, 1,024 bits');
	const plain = await page.getByText(/Enter runs it in this browser/).innerText();
	await ticks.getByRole('button', { name: /first 64/ }).click();
	await expect(page.getByText(/Enter runs it in this browser/)).not.toHaveText(plain);
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer')).toHaveCount(1, { timeout: 15_000 });
	await ticks.getByRole('button', { name: /every event/ }).click();
	await page.getByRole('textbox', { name: 'Your question' }).fill('Bits: 1 0 1. Even?');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.locator('.bot .answer')).toHaveCount(2, { timeout: 15_000 });
	const lookups = await page.evaluate(
		() => (globalThis as { __SAVANT_STUB__?: { lookups?: unknown[] } }).__SAVANT_STUB__?.lookups
	);
	expect(lookups).toEqual([64, null]);
});

test('Stop ends a run, and it can run again', async ({ page }) => {
	await stub(page, { delay: 120 });
	await page.goto('/interpreter');
	await load(page);
	await pick(page, 'Story', 'Story, 64 events');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.getByRole('status')).toBeVisible();
	await page.getByRole('button', { name: 'Stop' }).click();
	await expect(page.getByText('Stopped.')).toBeVisible();
	const again = page.getByRole('button', { name: 'Run it again' });
	await expect(again).toBeEnabled();
});

test('a question sent before the model loads waits, then runs', async ({ page }) => {
	await stub(page);
	await page.goto('/interpreter');
	await pick(page, 'Story', 'Story, 64 events');
	await page.getByRole('button', { name: 'Send' }).click();
	await expect(page.getByText(/There is no recorded run of this question/)).toBeVisible();
	await page.locator('.bot').getByRole('button', { name: 'Load Savant-4B' }).click();
	await expect(page.locator('.bot .answer')).toHaveText(prose.answer, { timeout: 15_000 });
});

test('without WebGPU the page says why and the recordings still replay', async ({ page }) => {
	await stub(page, { gpu: undefined });
	await page.goto('/interpreter');
	const model = page.getByRole('region', { name: 'The model' });
	await expect(model).toContainText('This browser has no WebGPU');
	await expect(model.getByRole('button', { name: /Load Savant-4B/ })).toHaveCount(0);
	await pick(page, 'Story', 'Story, 256 events, recorded');
	await expect(page.getByText('Enter replays the recorded run')).toBeVisible();
	await page.getByRole('button', { name: 'Send' }).click();
	await page.getByRole('slider', { name: 'Step of the run' }).fill('255');
	await expect(page.locator('.bot .answer')).toHaveText(prose.answer);
});

for (const width of [390, 1440])
	test(`no sideways scroll at ${width} px, before and after a run`, async ({ page }) => {
		await page.setViewportSize({ width, height: width < 600 ? 844 : 900 });
		await stub(page);
		await page.goto('/interpreter');
		const wide = () => page.evaluate(() => document.documentElement.scrollWidth);
		expect(await wide()).toBeLessThanOrEqual(width);
		await load(page);
		await pick(page, 'Story', 'Story, 64 events');
		await page.getByRole('button', { name: 'Send' }).click();
		await expect(page.locator('.bot .answer')).toHaveText(prose.answer, { timeout: 15_000 });
		expect(await wide()).toBeLessThanOrEqual(width);
	});
