import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
for (const [size, width, height] of [
	['desktop', 1440, 900],
	['mobile', 390, 844]
])
	for (const scheme of ['light', 'dark']) {
		const page = await browser.newPage({
			viewport: { width, height },
			colorScheme: scheme,
			deviceScaleFactor: 1
		});
		const errors = [];
		page.on('pageerror', (e) => errors.push(e.message));
		await page.goto('http://127.0.0.1:4173/report', { waitUntil: 'networkidle' });
		await page.screenshot({ path: `briefs/shots/report-intro-${size}-${scheme}.png` });
		for (const anchor of [
			'beginning',
			'language',
			'composition',
			'character-results',
			'fig-characters',
			'holonomy',
			'groups',
			'fig-ladder',
			'theory',
			'programs',
			'word-problems',
			'related',
			'meaning',
			'references'
		]) {
			await page.locator(`#${anchor}`).scrollIntoViewIfNeeded();
			await page.evaluate((id) => {
				const el = document.getElementById(id);
				window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 66);
			}, anchor);
			await page.waitForTimeout(140);
			await page.screenshot({ path: `briefs/shots/report-${anchor}-${size}-${scheme}.png` });
		}
		console.log(
			JSON.stringify({
				size,
				scheme,
				errors,
				overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)
			})
		);
		await page.close();
	}
await browser.close();
