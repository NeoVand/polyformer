/**
 * Which characters of Z_3^4 a trained Newton attention layer has learned.
 *
 * A channel is the character χ_c when its phase on every card x, at every position, is
 * 2π⟨c, x⟩/3 up to one constant rotation. Its fidelity to c is the gate-weighted resultant
 *
 *     R_c = |Σ g · e^{i(a − 2π⟨c,x⟩/3)}| / Σ g
 *
 * over every (card, position) sample: 1 exactly for a character, small for anything else.
 * A character and its conjugate (c and −c) are the same channel read the other way round,
 * so the 80 non-trivial characters make 40 classes, the ones a layer has to find.
 */
import { ATTRS, DECK, type Card } from '../set/cards.ts';

/** The probe layout the worker uses: table b, position p + 1 holds this card. */
export const deckIndexAt = (b: number, p: number, size: number) => (b + p * size) % DECK.length;

const nonzero = (c: readonly number[]) => c.some((v) => v !== 0);
const firstNonzero = (c: readonly number[]) => c.find((v) => v !== 0) ?? 0;

/** One representative per conjugate pair: the characters whose first non-zero entry is 1. */
export const CLASSES: Card[] = DECK.filter((c) => nonzero(c) && firstNonzero(c) === 1);

/** ⟨c, x⟩ mod 3. */
export const charValue = (c: readonly number[], x: readonly number[]) => {
	let s = 0;
	for (let a = 0; a < ATTRS; a++) s += c[a] * x[a];
	return ((s % 3) + 3) % 3;
};

export interface ChannelFit {
	head: number;
	channel: number;
	/** Index into CLASSES of the closest character. */
	cls: number;
	/** +1 when the channel is the representative itself, −1 when it is its conjugate. */
	sign: 1 | -1;
	/** Resultant length, 0 … 1. */
	R: number;
	/** The constant rotation that best aligns the channel with the character. */
	offset: number;
}

export interface PhaseProbe {
	heads: number;
	n: number;
	dh: number;
	/** [table, head, position, channel]; tables 0 … 80 hold the deck. */
	angle: Float32Array;
	gate: Float32Array;
}

const TAU = 2 * Math.PI;

/** Per-card sums Σ_p g e^{ia} over positions for one channel: [81 × (re, im)], and Σ g. */
function cardSums(probe: PhaseProbe, h: number, c: number) {
	const { heads, n, dh } = probe;
	const size = n - 1;
	const z = new Float64Array(DECK.length * 2);
	let total = 0;
	for (let b = 0; b < DECK.length; b++)
		for (let p = 0; p < size; p++) {
			const at = ((b * heads + h) * n + p + 1) * dh + c;
			const g = probe.gate[at];
			const a = probe.angle[at];
			const x = deckIndexAt(b, p, size);
			z[x * 2] += g * Math.cos(a);
			z[x * 2 + 1] += g * Math.sin(a);
			total += g;
		}
	return { z, total };
}

/** The closest character class for every channel of every head. */
export function fitChannels(probe: PhaseProbe): ChannelFit[] {
	const out: ChannelFit[] = [];
	// ω^{−⟨c,x⟩} for every class and card, as cos and sin
	const cos = CLASSES.map((c) => DECK.map((x) => Math.cos((-TAU * charValue(c, x)) / 3)));
	const sin = CLASSES.map((c) => DECK.map((x) => Math.sin((-TAU * charValue(c, x)) / 3)));
	for (let h = 0; h < probe.heads; h++)
		for (let ch = 0; ch < probe.dh; ch++) {
			const { z, total } = cardSums(probe, h, ch);
			let best: ChannelFit = { head: h, channel: ch, cls: 0, sign: 1, R: 0, offset: 0 };
			for (let k = 0; k < CLASSES.length; k++) {
				// Σ_x z_x ω^{∓⟨c,x⟩}: the conjugate flips the sign of the character's phase
				for (const sign of [1, -1] as const) {
					let re = 0;
					let im = 0;
					for (let x = 0; x < DECK.length; x++) {
						const cr = cos[k][x];
						const ci = sign * sin[k][x];
						re += z[x * 2] * cr - z[x * 2 + 1] * ci;
						im += z[x * 2] * ci + z[x * 2 + 1] * cr;
					}
					const R = Math.hypot(re, im) / Math.max(total, 1e-12);
					if (R > best.R)
						best = { head: h, channel: ch, cls: k, sign, R, offset: Math.atan2(im, re) };
				}
			}
			out.push(best);
		}
	return out;
}

/** The best resultant any channel reaches for each of the 40 classes. */
export function classStrength(fits: ChannelFit[]): Float32Array {
	const s = new Float32Array(CLASSES.length);
	for (const f of fits) s[f.cls] = Math.max(s[f.cls], f.R);
	return s;
}

/** Classes some channel matches with a resultant above `threshold` (0.9, as in the paper). */
export const countFound = (strength: Float32Array, threshold = 0.9) =>
	strength.reduce((n, v) => n + (v > threshold ? 1 : 0), 0);

/**
 * One channel's phase on each card of the deck, rotated so the character it matches sits at
 * 0, 1/3 and 2/3 of a turn: the circular mean over positions, and its length (0 … 1).
 */
export function cardPhases(
	probe: PhaseProbe,
	fit: ChannelFit
): { angle: number; length: number }[] {
	const { z } = cardSums(probe, fit.head, fit.channel);
	const size = probe.n - 1;
	return DECK.map((_, x) => {
		const re = z[x * 2];
		const im = z[x * 2 + 1];
		// card x sits at position p + 1 of exactly one table
		let gates = 0;
		for (let p = 0; p < size; p++) {
			const b = (((x - p * size) % DECK.length) + DECK.length) % DECK.length;
			gates +=
				probe.gate[((b * probe.heads + fit.head) * probe.n + p + 1) * probe.dh + fit.channel];
		}
		// undo the constant rotation; the conjugate runs the other way round
		const a = fit.sign * (Math.atan2(im, re) - fit.offset);
		return { angle: ((a % TAU) + TAU) % TAU, length: Math.hypot(re, im) / Math.max(gates, 1e-12) };
	});
}
