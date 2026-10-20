import { chromium } from 'playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
const selected = process.argv.slice(2);
const targets = [
	{ name: 'landing', path: '/', animated: true },
	{ name: 'compare', path: '/compare' },
	{ name: 'compare-groups', path: '/compare', groups: true },
	{ name: 'explore-cubic', path: '/explore', animated: true },
	{ name: 'explore-newton', path: '/explore/newton' },
	{ name: 'explore-diagrams', path: '/explore/diagrams', animated: true },
	{ name: 'explore-groups', path: '/explore/groups', animated: true },
	{ name: 'learn', path: '/learn' },
	{ name: 'report', path: '/report' }
].filter((t) => !selected.length || selected.includes(t.name));
await mkdir('briefs/shots', { recursive: true });
const browser = await chromium.launch({ headless: true });
const findings = [];
for (const size of [
	{ name: 'desktop', width: 1440, height: 900 },
	{ name: 'mobile', width: 390, height: 844 }
]) {
	for (const colorScheme of ['dark', 'light']) {
		const context = await browser.newContext({
			viewport: { width: size.width, height: size.height },
			colorScheme,
			deviceScaleFactor: 1
		});
		for (const target of targets) {
			const page = await context.newPage();
			const errors = [];
			page.on('pageerror', (e) => errors.push(e.message));
			await page.goto('http://127.0.0.1:4173' + target.path, { waitUntil: 'networkidle' });
			await page.evaluate(() => document.fonts.ready);
			if (target.groups)
				await page
					.locator('.title-row')
					.getByRole('button', { name: 'Groups', exact: true })
					.click();
			await page.waitForTimeout(1100);
			const prefix = `briefs/shots/${target.name}-${size.name}-${colorScheme}`;
			await page.screenshot({ path: prefix + '.png' });
			if (target.animated) {
				await page.waitForTimeout(1000);
				await page.screenshot({ path: prefix + '-frame2.png' });
			}
			const overflow = await page.evaluate(() => ({
				width: window.innerWidth,
				scroll: document.documentElement.scrollWidth,
				height: document.documentElement.scrollHeight
			}));
			findings.push({ page: target.name, size: size.name, colorScheme, errors, overflow });
			await page.close();
		}
		await context.close();
	}
}
await browser.close();
let audit = findings;
if (selected.length) {
	try {
		const previous = JSON.parse(await readFile('briefs/shots/audit.json', 'utf8'));
		audit = [...previous.filter((entry) => !selected.includes(entry.page)), ...findings];
	} catch {
		// A targeted first capture has no earlier audit to retain.
	}
}
await writeFile('briefs/shots/audit.json', JSON.stringify(audit, null, 2) + '\n');
console.log(
	JSON.stringify(
		findings.filter((x) => x.errors.length || x.overflow.scroll > x.overflow.width),
		null,
		2
	)
);
