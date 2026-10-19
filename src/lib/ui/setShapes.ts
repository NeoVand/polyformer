/** Geometry for SET symbols, drawn upright in a 24 × 56 box centred on the origin. */

export const SHAPE_W = 24;
export const SHAPE_H = 56;

export const DIAMOND = 'M0,-27 L11.5,0 L0,27 L-11.5,0 Z';
export const OVAL = 'M-11,-16 A11,11 0 0 1 11,-16 L11,16 A11,11 0 0 1 -11,16 Z';

/** A squiggle: an S-shaped centreline with a tapered width. */
export const SQUIGGLE = (() => {
	const N = 28;
	const right: string[] = [];
	const left: string[] = [];
	for (let s = 0; s <= N; s++) {
		const y = -27 + (54 * s) / N;
		const t = y / 27;
		const cx = 4.2 * Math.sin(Math.PI * t) + 1.2 * t;
		const w = 7.4 * Math.pow(Math.max(0, 1 - t ** 4), 0.55) + 0.6;
		right.push(`${(cx + w).toFixed(2)},${y.toFixed(2)}`);
		left.push(`${(cx - w).toFixed(2)},${y.toFixed(2)}`);
	}
	return `M${right.join(' L')} L${left.reverse().join(' L')} Z`;
})();

export const SHAPES = [DIAMOND, OVAL, SQUIGGLE] as const;

export const SET_COLOURS = [
	'var(--color-set-red)',
	'var(--color-set-green)',
	'var(--color-set-purple)'
];
