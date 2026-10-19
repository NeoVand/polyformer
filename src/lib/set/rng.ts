/** Small seeded PRNG (mulberry32). Deterministic across browsers and backends. */
export type Rng = () => number;

export function mulberry32(seed: number): Rng {
	let s = seed | 0;
	return () => {
		s = (s + 0x6d2b79f5) | 0;
		let t = Math.imul(s ^ (s >>> 15), 1 | s);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/** Standard normal via Box–Muller. */
export function gaussian(rng: Rng): number {
	const u = Math.max(rng(), 1e-12);
	const v = rng();
	return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

/** Mix a base seed with a stream id so independent streams never collide. */
export function deriveSeed(seed: number, stream: number): number {
	let h = (seed ^ 0x9e3779b9) >>> 0;
	h = Math.imul(h ^ (stream + 0x85ebca6b), 0xc2b2ae35) >>> 0;
	h ^= h >>> 16;
	return h >>> 0;
}
