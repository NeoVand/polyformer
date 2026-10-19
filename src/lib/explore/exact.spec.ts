import { describe, expect, it } from 'vitest';
import { dealLayout, isSet, LAYOUT_SIZE } from '../set/cards.ts';
import { mulberry32 } from '../set/rng.ts';
import { exactProbe, SINK_LOGIT } from './exact.ts';

describe('exact cubic SET head', () => {
	it('scores every SET at 4 and every other distinct triple at most 2.5', () => {
		const rng = mulberry32(7);
		for (let trial = 0; trial < 20; trial++) {
			const layout = dealLayout(rng);
			const p = exactProbe(layout);
			const n = p.n;
			for (let i = 1; i < n; i++)
				for (let j = 1; j < n; j++)
					for (let k = 1; k < n; k++) {
						if (i === j || i === k || j === k) continue;
						const a = p.scores[(i * n + j) * n + k];
						if (isSet(layout[i - 1], layout[j - 1], layout[k - 1])) expect(a).toBeCloseTo(4, 5);
						else expect(a).toBeLessThanOrEqual(2.5 + 1e-5);
					}
		}
	});

	it('puts most of its weight on SET pairs, or on the sink when there are none', () => {
		const rng = mulberry32(11);
		const layout = dealLayout(rng);
		const p = exactProbe(layout, 6);
		const n = p.n;
		for (let i = 1; i <= LAYOUT_SIZE; i++) {
			let onSets = 0;
			for (let j = 1; j < n; j++)
				for (let k = 1; k < n; k++)
					if (j !== k && j !== i && k !== i && isSet(layout[i - 1], layout[j - 1], layout[k - 1]))
						onSets += p.weights[(i * n + j) * n + k];
			const sink = p.weights[i * n * n];
			expect(onSets + sink).toBeGreaterThan(0.85);
			expect(p.scores[i * n * n]).toBe(SINK_LOGIT);
		}
	});
});
