/**
 * The questions the page suggests for Savant-4B (static/interpreter/prompts.json, written by
 * research/demolive/dl_web.py from PROMPTBOX's generators): six trained families at 64 to 2,048 events, plus the
 * eight questions DEMOLIVE recorded on the server, whose base-model answers and adapter-off runs are on the page.
 */
import type { Truth } from './engine.ts';

export interface SuggestedPrompt {
	id: string;
	family: string;
	L: number;
	title: string;
	/** the recorded trace's id, when this is one of DEMOLIVE's recorded questions */
	recorded: string | null;
	/** the length the page offers first for its family */
	default: boolean;
	heldout_phrasing?: boolean;
	question: string;
	/** chat-prompt tokens */
	tokens: number;
	truth: Truth;
}

export interface PromptSet {
	schema: 'polyformer.prompts/0';
	lengths: number[];
	prompts: SuggestedPrompt[];
}

export const FAMILIES: { id: string; label: string; unit: string }[] = [
	{ id: 'cups', label: 'Shell game', unit: 'swaps' },
	{ id: 'parity', label: 'Parity', unit: 'bits' },
	{ id: 'robot', label: 'Robot walk', unit: 'moves' },
	{ id: 'compass', label: 'Compass', unit: 'turns' },
	{ id: 'cycle', label: 'Cycle', unit: 'steps' },
	{ id: 'prose', label: 'Story', unit: 'events' }
];

/** The prompt whose text is exactly this (a suggestion sent unedited), if any. */
export const exactPrompt = (set: PromptSet | null, text: string) =>
	set?.prompts.find((p) => p.question.trim() === text.trim()) ?? null;

/** Lookup mode runs this many events for real, then reads each step from its certified row. */
export const LOOKUP_AFTER = 64;

/** Ticks a question will run: one per event per register (or the first `lookupAfter`), plus one per row. */
export const ticksOf = (p: SuggestedPrompt, lookupAfter: number | null = null) =>
	p.truth.registers.reduce(
		(a, r) => a + r.rows + Math.min(p.truth.events, lookupAfter ?? Infinity),
		0
	);

/**
 * A suggested addition (ARITH_FORMAT number mode): two random numbers of `digits` digits, written into the question
 * the arithmetic model was trained on. The page keeps the numbers to score the run against; the clock reads them
 * from the question itself.
 */
export interface Addition {
	digits: number;
	a: string;
	b: string;
	question: string;
	title: string;
}

/** The lengths the page offers, in digits per number. */
export const ADDITION_DIGITS = [10, 100, 1000];

/** One number of exactly `digits` digits (no leading zero), from `random` (Math.random unless a test passes one). */
export function randomNumber(digits: number, random: () => number = Math.random): string {
	let s = String(1 + Math.floor(random() * 9));
	for (let k = 1; k < digits; k++) s += String(Math.floor(random() * 10));
	return s;
}

export function makeAddition(digits: number, random: () => number = Math.random): Addition {
	const a = randomNumber(digits, random);
	const b = randomNumber(digits, random);
	// the clock runs one column per digit of the longer number, then one more 0 0 pair
	const columns = digits + 1;
	return {
		digits,
		a,
		b,
		question: `What is ${a} plus ${b}?`,
		title: `Addition of two ${digits.toLocaleString('en-US')}-digit numbers, ${columns.toLocaleString('en-US')} columns`
	};
}

/** Ticks an addition runs: one per row of the adder's 200 (each two forwards), then one per column. */
export const additionTicks = (add: Addition, lookupAfter: number | null = null) =>
	200 + Math.min(add.digits + 1, lookupAfter ?? Infinity);

/**
 * Composite questions for the reasoning model, from REASON's training templates (`reason_data.py`).
 * Each training template has six phrasings; the last two are held out, so these use phrasing 0.
 * Held-out templates (parking_fee, four_total, coin_add_or_sub, drone_compass, rumor_chain, marble_trades) are not used.
 */
export interface ReasonPrompt {
	id: string;
	/** `reason_data.TRAIN_TEMPLATES` name */
	template: string;
	/** phrasing index; 0–3 are trained, 4–5 are held out */
	phrasing: number;
	title: string;
	question: string;
}

export const REASON_PROMPTS: readonly ReasonPrompt[] = [
	{
		id: 'sales-compare',
		template: 'sales_compare',
		phrasing: 0,
		title: 'Two stores',
		question:
			'Store X produced 4821 items last year and 903 items this year. Store Y produced 1750 items last year and 2604 items this year. Over the two years, by how many items did the larger total exceed the smaller one?'
	},
	{
		id: 'deposit-chain',
		template: 'deposit_chain',
		phrasing: 0,
		title: 'A deposit',
		question:
			'An account starts with 1200 cents. Then 340 cents are added, and later another 55 cents. How many cents are there in the end?'
	},
	{
		id: 'parity-pick-sum',
		template: 'parity_pick_sum',
		phrasing: 0,
		title: 'Parity, then a sum',
		question:
			'A sensor wrote this bit string: 1 0 1 1. If the number of 1s is odd, the shipment total is 48 plus 17; if it is even, the total is 48 plus 9. What is the shipment total?'
	},
	{
		id: 'shelf-bill',
		template: 'shelf_bill',
		phrasing: 0,
		title: 'A shelf bill',
		question:
			"A shelf holds at most 4 crates and starts with 1. Here is the log: in out in in. 'in' brings one crate and 'out' removes one; an 'in' when the shelf is full is turned away, and an 'out' when it is empty does nothing. Storage costs 3 dollars per crate per day. What is the daily storage bill, in dollars, for the crates left at the end?"
	}
];

/** The composite whose text is exactly this, if any. */
export const exactReason = (text: string) =>
	REASON_PROMPTS.find((p) => p.question.trim() === text.trim()) ?? null;
