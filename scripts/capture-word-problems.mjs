import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

// Run against a production preview: pnpm preview --host 127.0.0.1 --port 4173.
const destination = 'briefs/shots/phase3b';
await mkdir(destination, { recursive: true });
const browser = await chromium.launch({ headless: true });
const audit = [];

try {
	for (const [size, width, height] of [
		['desktop', 1440, 900],
		['mobile', 390, 844]
	]) {
		for (const colorScheme of ['light', 'dark']) {
			const context = await browser.newContext({
				viewport: { width, height },
				colorScheme,
				deviceScaleFactor: 1
			});
			for (const [route, selectors] of [
				['report', ['#abstract', '#word-problems', '#meaning']],
				['learn', ['#programs', '#word-problems']],
				['compare', ['.source']]
			]) {
				const page = await context.newPage();
				const errors = [];
				page.on('pageerror', (error) => errors.push(error.message));
				await page.goto(`http://127.0.0.1:4173/${route}`, { waitUntil: 'networkidle' });
				await page.evaluate(() => document.fonts.ready);
				if (route === 'compare')
					await page
						.locator('.title-row')
						.getByRole('button', { name: 'Groups', exact: true })
						.click();
				for (const selector of selectors) {
					const bounds = await page.locator(selector).evaluate((element) => {
						const rect = element.getBoundingClientRect();
						return { top: rect.top + window.scrollY, height: rect.height };
					});
					// The mobile course keeps its illustration below the navigation.
					const topInset = route === 'learn' && size === 'mobile' ? 390 : 72;
					const stride = height - topInset - 58;
					const frames = Math.max(1, Math.ceil((bounds.height - 60) / stride));
					const captures = [];
					for (let frame = 0; frame < frames; frame++) {
						await page.evaluate(
							(y) => window.scrollTo(0, y),
							bounds.top - topInset + frame * stride
						);
						// Let scroll observers update the active chapter and its illustration.
						await page.waitForTimeout(250);
						const filename = `${route}-${selector.slice(1)}-${size}-${colorScheme}-${frame + 1}.png`;
						await page.screenshot({ path: `${destination}/${filename}`, animations: 'disabled' });
						captures.push(filename);
					}
					const geometry = await page.locator(selector).evaluate((element) => ({
						pageWidth: document.documentElement.scrollWidth,
						viewportWidth: innerWidth,
						tables: [...element.querySelectorAll('table')].map((table) => ({
							width: table.getBoundingClientRect().width,
							container: table.parentElement.clientWidth
						}))
					}));
					audit.push({
						route,
						selector,
						size,
						colorScheme,
						captures,
						geometry,
						errors: [...errors]
					});
				}
				await page.close();
			}
			await context.close();
		}
	}
} finally {
	await browser.close();
}
await writeFile(`${destination}/audit.json`, JSON.stringify(audit, null, 2) + '\n');
const failures = audit.filter(
	(entry) =>
		entry.errors.length ||
		entry.geometry.pageWidth > entry.geometry.viewportWidth ||
		entry.geometry.tables.some((table) => table.width > table.container + 1)
);
console.log(
	JSON.stringify(
		{ screenshots: audit.flatMap((entry) => entry.captures).length, failures },
		null,
		2
	)
);
if (failures.length) process.exitCode = 1;
