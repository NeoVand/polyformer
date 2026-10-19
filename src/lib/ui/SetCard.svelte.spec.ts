import { page } from 'vitest/browser';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import SetCard from './SetCard.svelte';

describe('SetCard.svelte', () => {
	it('draws one symbol per count and names the card for screen readers', async () => {
		render(SetCard, { card: [2, 1, 0, 2] });
		const card = page.getByRole('img', { name: 'three solid purple circles' });
		await expect.element(card).toBeInTheDocument();
		expect(card.element().querySelectorAll('path').length).toBe(3);
	});

	it('uses a stripe pattern for striped shading', async () => {
		render(SetCard, { card: [0, 0, 1, 0] });
		const card = page.getByRole('img', { name: 'one striped red diamond' });
		await expect.element(card).toBeInTheDocument();
		expect(card.element().querySelector('path')?.getAttribute('fill')).toMatch(/^url\(#stripe-/);
	});
});
