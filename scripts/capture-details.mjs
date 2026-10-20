import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

const browser = await chromium.launch({ headless: true });
const audit = [];
await mkdir('briefs/shots', { recursive: true });
for (const colorScheme of ['dark', 'light']) {
	const page = await browser.newPage({
		viewport: { width: 390, height: 844 },
		colorScheme,
		deviceScaleFactor: 1
	});
	const errors = [];
	page.on('pageerror', (error) => errors.push(error.message));
	for (const target of [
		{ path: '/', name: 'landing-graph', selector: '.tile.graph', animated: true },
		{ path: '/', name: 'landing-composition', selector: '.tile.flow', animated: true },
		{ path: '/', name: 'landing-results', selector: '.tile.chart' },
		{ path: '/compare', name: 'compare-runs', selector: '.board' },
		{
			path: '/compare',
			name: 'compare-characters',
			selector: '.character-check',
			groups: true
		},
		{
			path: '/explore/diagrams',
			name: 'explore-diagrams-expanded',
			selector: '.pane.one',
			animated: true
		},
		{ path: '/explore/newton', name: 'explore-newton-inspector', selector: '.inspector' }
	]) {
		await page.goto('http://127.0.0.1:4173' + target.path, { waitUntil: 'networkidle' });
		await page.evaluate(() => document.fonts.ready);
		if (target.groups)
			await page.locator('.title-row').getByRole('button', { name: 'Groups', exact: true }).click();
		await page.locator(target.selector).evaluate((element) => {
			window.scrollTo(0, element.getBoundingClientRect().top + window.scrollY - 64);
		});
		await page.waitForTimeout(1100);
		const prefix = `briefs/shots/${target.name}-mobile-${colorScheme}`;
		await page.screenshot({ path: prefix + '.png' });
		if (target.animated) {
			await page.waitForTimeout(1000);
			await page.screenshot({ path: prefix + '-frame2.png' });
		}
		audit.push({
			page: target.name,
			colorScheme,
			errors: [...errors],
			overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)
		});
	}
	await page.close();
}
await browser.close();
await writeFile('briefs/shots/details-audit.json', JSON.stringify(audit, null, 2) + '\n');
console.log(audit.filter((result) => result.errors.length || result.overflow));
