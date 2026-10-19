/**
 * Geometry for card symbols: playing-card suits centred on the origin in a 24 × 24
 * box. Each suit is one closed outline, so open and striped shading draw cleanly.
 */

export const SHAPE_SIZE = 24;

export const HEART =
	'M0,10.5 C-1.8,8.4 -11,3.2 -11,-3.4 C-11,-7.6 -8.1,-10.2 -5,-10.2 C-2.6,-10.2 -0.9,-8.8 0,-7 C0.9,-8.8 2.6,-10.2 5,-10.2 C8.1,-10.2 11,-7.6 11,-3.4 C11,3.2 1.8,8.4 0,10.5 Z';

export const SPADE =
	'M0,-11 C1.8,-8.6 11,-3.6 11,2.4 C11,5.8 8.6,7.8 5.8,7.8 C3.8,7.8 2.2,6.8 1.2,5.2 C1.5,7.9 2.8,10 5,11.2 L-5,11.2 C-2.8,10 -1.5,7.9 -1.2,5.2 C-2.2,6.8 -3.8,7.8 -5.8,7.8 C-8.6,7.8 -11,5.8 -11,2.4 C-11,-3.6 -1.8,-8.6 0,-11 Z';

/** The card diamond: a rhombus with gently pinched sides. */
export const DIAMOND = 'M0,-11.5 Q3.4,-5.2 8.8,0 Q3.4,5.2 0,11.5 Q-3.4,5.2 -8.8,0 Q-3.4,-5.2 0,-11.5 Z';

/** A club: three lobes and a flared stem, traced as a single outline. */
export const CLUB = (() => {
	const r = 4.9;
	const T = [0, -5.3];
	const Lc = [-5.6, 1.5];
	const Rc = [5.6, 1.5];
	/** The intersection of two equal circles that lies farther from the origin. */
	const outer = (a: number[], b: number[]) => {
		const mx = (a[0] + b[0]) / 2;
		const my = (a[1] + b[1]) / 2;
		const dx = b[0] - a[0];
		const dy = b[1] - a[1];
		const d = Math.hypot(dx, dy);
		const h = Math.sqrt(Math.max(0, r * r - (d / 2) ** 2));
		const p = [mx - (dy / d) * h, my + (dx / d) * h];
		const q = [mx + (dy / d) * h, my - (dx / d) * h];
		return Math.hypot(p[0], p[1]) > Math.hypot(q[0], q[1]) ? p : q;
	};
	const tl = outer(T, Lc);
	const tr = outer(T, Rc);
	const at = (c: number[], deg: number) => [
		c[0] + r * Math.cos((deg * Math.PI) / 180),
		c[1] + r * Math.sin((deg * Math.PI) / 180)
	];
	const sl = at(Lc, 24);
	const sr = at(Rc, 156);
	const f = (p: number[]) => `${p[0].toFixed(2)},${p[1].toFixed(2)}`;
	return [
		'M-4.8,11.2',
		`C-2.7,10 -1.3,7.6 ${f(sl)}`,
		`A${r},${r} 0 1 1 ${f(tl)}`,
		`A${r},${r} 0 1 1 ${f(tr)}`,
		`A${r},${r} 0 1 1 ${f(sr)}`,
		'C1.3,7.6 2.7,10 4.8,11.2',
		'Z'
	].join(' ');
})();

/** The three suits a card's shape attribute takes. */
export const SHAPES = [SPADE, HEART, CLUB] as const;

export const SET_COLOURS = ['var(--color-card-ink)', 'var(--color-card-red)', 'var(--color-card-gold)'];
