import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

// Serve the production build on 4173 before running this script.
const base = process.env.QA_URL ?? 'http://127.0.0.1:4173';
await mkdir('briefs/shots', { recursive: true });
const browser = await chromium.launch({ headless: true });
const audit = [];
const scrollToSection = (element) => {
	window.scrollTo(
		0,
		Math.min(
			element.getBoundingClientRect().top + window.scrollY - 66,
			document.documentElement.scrollHeight - window.innerHeight
		)
	);
};

for (const [size, width, height] of [
	['desktop', 1440, 900],
	['mobile', 390, 844]
]) {
	for (const theme of ['dark', 'light']) {
		const context = await browser.newContext({
			viewport: { width, height },
			colorScheme: theme,
			deviceScaleFactor: 1
		});
		const page = await context.newPage();
		const errors = [];
		page.on('pageerror', (error) => errors.push(error.message));
		await page.goto(`${base}/explore/groups`, { waitUntil: 'networkidle' });
		await page.evaluate(() => document.fonts.ready);
		await page.waitForTimeout(1000);
		const stem = `briefs/shots/explore-groups-${size}-${theme}`;
		const model = page.getByRole('group', { name: 'Model', exact: true });
		await model.getByRole('button', { name: 'Recorded', exact: true }).click();
		await page.waitForTimeout(950);
		await page.screenshot({ path: `${stem}.png` });
		await page.waitForTimeout(1000);
		await page.screenshot({ path: `${stem}-frame2.png` });
		await model.getByRole('button', { name: 'Ideal', exact: true }).click();
		await page.waitForTimeout(950);
		await page.screenshot({ path: `${stem}-ideal.png` });
		await page.getByRole('button', { name: 'Element 31:', exact: false }).click();
		await page.waitForTimeout(220);
		await page.screenshot({ path: `${stem}-motion.png` });
		await page.waitForTimeout(1000);
		await page.screenshot({ path: `${stem}-motion-frame2.png` });

		await model.getByRole('button', { name: 'Recorded', exact: true }).click();
		await page.getByRole('button', { name: 'Element 13:', exact: false }).click();
		await page.waitForTimeout(950);
		const order = page.getByRole('region', { name: 'Order matters', exact: true });
		await order.evaluate(scrollToSection);
		for (const [button, suffix] of [
			['Start', 'start'],
			['First move', 'first'],
			['Both moves', 'final']
		]) {
			await order.getByRole('button', { name: button, exact: true }).click();
			await page.waitForTimeout(950);
			await page.screenshot({ path: `${stem}-order-${suffix}.png` });
		}
		if (size === 'mobile') {
			await page
				.getByRole('complementary', { name: 'What the recording shows' })
				.evaluate(scrollToSection);
			await page.screenshot({ path: `${stem}-inspector.png` });
		}
		audit.push({
			size,
			theme,
			errors,
			overflow: await page.evaluate(() => ({
				width: innerWidth,
				scroll: document.documentElement.scrollWidth
			})),
			model: 'Recorded default, then Ideal',
			motionFrames: '220 ms after selecting element 31, then 1000 ms later',
			orderSteps: ['Start', 'First move', 'Both moves']
		});
		await context.close();
	}
}
await browser.close();
await writeFile('briefs/shots/groups-audit.json', JSON.stringify(audit, null, 2) + '\n');
console.log(JSON.stringify(audit, null, 2));
