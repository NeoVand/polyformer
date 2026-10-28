import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

interface Entry {
	id: string;
	title: string;
	group?: string;
	file: string;
}
const index: { traces: Entry[] } = JSON.parse(readFileSync('static/traces/index.json', 'utf8'));
const llm = index.traces.filter((e) => e.group === 'llm');
const read = (e: Entry) => JSON.parse(readFileSync(`static/${e.file}`, 'utf8'));

/** A running local server would spend GPU time, so tests only ever see a stub or nothing. */
const noServer = (page: Page) =>
	page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));

/** The frozen-core recordings sit behind a disclosure under the suggested questions. */
async function pickOlder(page: Page, title: string) {
	await page.getByRole('button', { name: /More recorded runs/ }).click();
	await page.getByTitle(title, { exact: true }).click();
}

/** A recorded Qwen3-4B question: its family, then its recorded length. */
async function pickRecorded(page: Page, e: Entry) {
	const family = e.title.replace(/ \(new wording\)/, '').replace(/,.*$/, '');
	await page
		.getByRole('group', { name: 'Suggested questions' })
		.getByTitle(family, { exact: true })
		.click();
	await page.getByTitle(`${e.title}, recorded`, { exact: true }).click();
}

test('interpreter replays a recorded run, labels the mock program, and answers at the end', async ({
	page
}) => {
	await noServer(page);
	await page.goto('/interpreter');
	await page.getByRole('button', { name: /More recorded runs/ }).click();
	const older = page
		.getByRole('group', { name: 'Recorded runs on the frozen core' })
		.getByRole('button');
	await expect(older).toHaveCount(index.traces.filter((e) => e.group !== 'llm').length);
	await page.getByTitle('Shell game, 1,024 swaps', { exact: true }).click();
	await expect(page.getByRole('textbox', { name: 'Your question' })).toHaveValue(/^Shell game!/);
	await expect(page.getByText('Point at left: the ball is there.')).toHaveCount(0);

	await page.getByRole('button', { name: 'Send' }).click();
	const program = page.getByRole('region', { name: 'The program' });
	await expect(program.locator('.src.mock')).toContainText('mock');
	await page.getByRole('slider', { name: 'Step of the run' }).fill('1023');
	await expect(page.locator('.bot .answer')).toHaveText('Point at left: the ball is there.');
	await expect(page.getByText('ran a 3-state program over 1,024 events · certified')).toBeVisible();
	await expect(page.getByRole('region', { name: 'The certificate' })).toContainText('9 of 9');
});

test('interpreter keeps interventions it has no recording for disabled', async ({ page }) => {
	await noServer(page);
	await page.goto('/interpreter');
	await pickOlder(page, 'Greatest common divisor, 11,349 instructions');
	await page.getByRole('button', { name: 'Send' }).click();
	const poke = page.getByRole('region', { name: 'Poke the brain' });
	await expect(poke).toContainText('needs the live model');
	await expect(poke.getByRole('button', { name: 'off' })).toBeDisabled();
	await page.getByRole('slider', { name: 'Step of the run' }).fill('11348');
	await expect(page.locator('.bot .answer')).toHaveText('The greatest common divisor is 12.');
});

test('a recorded Qwen3-4B run shows its own program, certificate, pokes and adapter-off run', async ({
	page
}) => {
	test.skip(!llm.length, 'no Qwen3-4B runs recorded');
	const e = llm[0];
	const f = read(e);
	const reg = f.registers[0];
	await noServer(page);
	await page.goto('/interpreter');
	await pickRecorded(page, e);
	await expect(page.getByRole('region', { name: 'The program' }).locator('.src.mock')).toHaveCount(
		0
	);
	await page.getByRole('button', { name: 'Send' }).click();
	await page.getByRole('slider', { name: 'Step of the run' }).fill(String(reg.steps.length - 1));
	await expect(page.locator('.bot .answer')).toHaveText(f.answer);
	await expect(page.locator('.bot .prov')).toContainText(
		f.score.answer_correct ? 'Right' : 'Wrong'
	);

	const rows = reg.program.rows.length;
	const right = reg.program.rows.filter((r: { ok: boolean }) => r.ok).length;
	await expect(page.getByRole('region', { name: 'The certificate' })).toContainText(
		`${right} of ${rows}`
	);

	const poke = page.getByRole('region', { name: 'Poke the brain' });
	const matched = reg.pokes.filter((p: { match: boolean }) => p.match).length;
	await expect(poke).toContainText(`${matched} of ${reg.pokes.length} match the program`);
	await poke
		.getByRole('group', { name: 'The executor adapter' })
		.getByRole('button', { name: 'off' })
		.click();
	await expect(poke).toContainText(`Answer becomes ${reg.ablation.answer}`);
});

test('a recorded question that never reached the run shows what the model wrote and why', async ({
	page
}) => {
	const e = llm.find((x) => !read(x).registers.length);
	test.skip(!e, 'every recorded question reached the run');
	const f = read(e!);
	await noServer(page);
	await page.goto('/interpreter');
	await pickRecorded(page, e!);
	await page.getByRole('button', { name: 'Send' }).click();
	const panel = page.getByRole('region', { name: 'No run' });
	await expect(panel).toContainText(f.note);
	await expect(panel.locator('.src')).toContainText('<program>');
	await expect(page.locator('.bot.active .note')).toContainText(`truth: ${f.truth}`);
});

test('with the local server up, an edited prompt runs live and a poke runs on the model', async ({
	page
}) => {
	test.skip(!llm.length, 'no Qwen3-4B runs recorded');
	const e = llm[0];
	const f = read(e);
	const reg = f.registers[0];
	const adapters = {
		compile_adapter: f.model.compile_adapter,
		executor_adapter: f.model.executor_adapter
	};
	let asked = '';
	let poked: { register?: string; step?: number; forced?: number } = {};
	await page.route('**/api/**', (r) => r.fulfill({ status: 404, body: '' }));
	await page.route('**/api/health', (r) =>
		r.fulfill({
			json: {
				schema: 'polyformer.demolive/0',
				ok: true,
				model: f.model.name,
				adapters,
				warm: true,
				spent_estimate_usd: 1,
				cap_usd: 40,
				busy: false,
				scaledown_seconds: 300
			}
		})
	);
	await page.route('**/api/ask', (r) => {
		asked = r.request().postDataJSON().question;
		const events = [
			{ type: 'stage', stage: 'compile' },
			{
				type: 'trace',
				trace: { ...f, prompt: asked, live: true, truth: null, provenance: undefined }
			}
		];
		return r.fulfill({
			contentType: 'application/x-ndjson',
			body: events.map((x) => JSON.stringify(x)).join('\n') + '\n'
		});
	});
	await page.route('**/api/poke', (r) => {
		poked = r.request().postDataJSON();
		const n = reg.steps.length - (poked.step ?? 0);
		return r.fulfill({
			json: {
				register: poked.register,
				step: poked.step,
				forced: reg.program.states[poked.forced ?? 0],
				final: reg.program.states[poked.forced ?? 0],
				predicted_state: reg.program.states[poked.forced ?? 0],
				match: true,
				answer_after: 'stubbed answer',
				ticks: n,
				ticks_bitwise_equal_to_certified_row: n,
				min_margin: 9
			}
		});
	});

	await page.goto('/interpreter');
	await expect(page.getByText(/The local server is connected/)).toBeVisible();
	await expect(page.getByText('Interpreter, live')).toBeVisible();
	await pickRecorded(page, e);
	const box = page.getByRole('textbox', { name: 'Your question' });
	const edited = (await box.inputValue()) + ' Please answer briefly.';
	await box.fill(edited);
	await page.getByRole('button', { name: 'Send' }).click();
	await page.getByRole('slider', { name: 'Step of the run' }).fill(String(reg.steps.length - 1));
	await expect(page.locator('.bot .answer')).toHaveText(f.answer);
	expect(asked).toBe(edited);
	await expect(page.locator('.bot .prov .live-word')).toBeVisible();

	const poke = page.getByRole('region', { name: 'Poke the brain' });
	await poke
		.getByRole('group', { name: 'State to force at the playhead' })
		.getByRole('button', { disabled: false })
		.first()
		.click();
	await poke.getByRole('button', { name: /^Force .+ run on$/ }).click();
	await expect(poke).toContainText('stubbed answer');
	await expect(poke).toContainText('run live');
	expect(poked.register).toBe(reg.name);
});
