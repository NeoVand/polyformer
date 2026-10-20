import { chromium } from 'playwright';
import { writeFile } from 'node:fs/promises';
const chapters = [
	'intro',
	'groups',
	'language',
	'features',
	'order',
	'representations',
	'holonomy',
	'group-results',
	'limits',
	'programs',
	'meaning'
];
const findings = [];
const browser = await chromium.launch({ headless: true });
for (const [device, width, height] of [
	['desktop', 1440, 900],
	['mobile', 390, 844]
]) {
	for (const colorScheme of ['dark', 'light']) {
		const context = await browser.newContext({
			viewport: { width, height },
			colorScheme,
			deviceScaleFactor: 1
		});
		const page = await context.newPage();
		const errors = [];
		page.on('pageerror', (e) => errors.push(e.message));
		await page.goto('http://127.0.0.1:4173/learn', { waitUntil: 'networkidle' });
		await page.evaluate(() => document.fonts.ready);
		for (const id of chapters) {
			await page.evaluate((id) => {
				if (id === 'intro') window.scrollTo(0, 0);
				else document.getElementById(id).scrollIntoView();
			}, id);
			await page.waitForTimeout(1050);
			const path = `briefs/shots/learn-${id}-${device}-${colorScheme}`;
			await page.screenshot({ path: path + '.png' });
			if (['representations', 'groups'].includes(id)) {
				const button = page.locator('aside.figure button').first();
				await button.click();
				await page.screenshot({ path: path + '-motion.png' });
				await page.waitForTimeout(1000);
				await page.screenshot({ path: path + '-frame2.png' });
			}
			const geometry = await page.evaluate(() => {
				const f = document.querySelector('aside.figure');
				const inner = f.querySelector('figure');
				return {
					scroll: document.documentElement.scrollWidth,
					width: innerWidth,
					figure: f?.getBoundingClientRect().toJSON(),
					content: inner?.getBoundingClientRect().toJSON(),
					caption: inner?.querySelector('figcaption')?.getBoundingClientRect().toJSON(),
					heading: inner?.querySelector('header')?.textContent
				};
			});
			findings.push({ id, device, colorScheme, geometry, errors: [...errors] });
		}
		await context.close();
	}
}
await browser.close();
await writeFile('briefs/shots/learn-audit.json', JSON.stringify(findings, null, 2) + '\n');
console.log(
	JSON.stringify(
		findings.filter(
			(f) =>
				f.errors.length ||
				f.geometry.scroll > f.geometry.width ||
				f.geometry.content?.bottom > f.geometry.figure.bottom + 1
		),
		null,
		2
	)
);
