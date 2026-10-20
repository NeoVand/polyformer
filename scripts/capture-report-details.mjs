import { chromium } from 'playwright';
import { writeFile } from 'node:fs/promises';
const browser = await chromium.launch({ headless: true });
const audit = [];
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
		page.on('pageerror', (error) => errors.push(error.message));
		await page.goto('http://127.0.0.1:4173/report', { waitUntil: 'networkidle' });
		await page.evaluate(() => document.fonts.ready);
		const tables = page.locator('article table');
		for (let index = 0; index < (await tables.count()); index++) {
			await tables
				.nth(index)
				.evaluate((el) => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 66));
			await page.waitForTimeout(160);
			await page.screenshot({
				path: `briefs/shots/report-table${index + 1}-${size}-${scheme}.png`
			});
		}
		const tableWidths = await tables.evaluateAll((t) =>
			t.map((el, i) => ({
				table: i + 1,
				width: Math.ceil(el.getBoundingClientRect().width),
				container: el.parentElement.clientWidth
			}))
		);
		await page.locator('#holonomy summary').click();
		await page
			.locator('#holonomy details')
			.evaluate((el) => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 66));
		await page.waitForTimeout(160);
		await page.screenshot({ path: `briefs/shots/report-computation-${size}-${scheme}.png` });
		for (let index = 0; index < 3; index++) {
			const theorem = page.locator('#theory .thm').nth(index);
			await theorem.locator('button').click();
			await theorem.evaluate((el) =>
				window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 66)
			);
			await page.waitForTimeout(160);
			await page.screenshot({
				path: `briefs/shots/report-proof${index + 1}-${size}-${scheme}.png`
			});
		}
		audit.push({
			size,
			scheme,
			tableWidths,
			errors,
			overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)
		});
		await page.close();
	}
await browser.close();
await writeFile('briefs/shots/report-audit.json', JSON.stringify(audit, null, 2) + '\n');
console.log(audit.filter((result) => result.errors.length || result.overflow));
