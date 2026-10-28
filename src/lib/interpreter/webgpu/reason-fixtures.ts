/** Test-only: reason_core's fixtures as copied by scripts/reason_fixtures.py (Node; never imported by the page). */
import { readFileSync } from 'node:fs';
import type { Tok } from './pb.ts';
import { FixtureTok } from './testkit.ts';

export interface ReasonFixtureCall {
	call: number;
	/** the call's ids in the response: [start, end), from its <program> to its <exec/> */
	start: number;
	end: number;
	/** S1 as the call saw it */
	notes: string;
	final_ids: number[];
	final_text: string;
	mode: 'tape' | 'numbers';
	error: string | null;
	spans: ([number, number, number] | ['result', number])[];
	how: ('exact' | 'relaxed')[];
	value: string | null;
}

export interface ReasonFixtureCase {
	name: string;
	question: string;
	prompt_ids: number[];
	/** the response without its final <|im_end|>: the model's ids and the clock's finals */
	response_ids: number[];
	response_text: string;
	calls: ReasonFixtureCall[];
}

export const reason = JSON.parse(
	readFileSync(new URL('./fixtures/reason.json', import.meta.url), 'utf8')
) as {
	format: string;
	copied_from: { path: string; branch: string; commit: string | null; sha256: string };
	tokenizer_sha256: string;
	cases: ReasonFixtureCase[];
	locate: {
		sources: string[];
		before: string;
		after: string;
		from: [number, number];
		want: [number, number, number, 'exact' | 'relaxed'] | null;
	}[];
	ids: { nl: number; im_end: number; endoftext: number; digits: number[] };
	tokens: Record<string, string>;
	special: number[];
	encoded: Record<string, number[]>;
	walked: Record<string, { ids: number[]; offsets: [number, number][] }>;
};

/** A tokenizer that knows only the fixtures' ids and texts (with offsets for every source a call reads). */
export function reasonTok(): Tok {
	const t = FixtureTok.from([], reason.special, {
		tokens: reason.tokens,
		encoded: reason.encoded
	});
	for (const [text, w] of Object.entries(reason.walked)) t.learn(text, w.ids, w.offsets);
	return t;
}

/**
 * The pieces the model writes in a fixture transcript: the response cut at each clock's final (the text and the call
 * before each final, then the text after the last).
 */
export function piecesOf(c: ReasonFixtureCase): number[][] {
	const out: number[][] = [];
	let at = 0;
	for (const call of c.calls) {
		out.push(c.response_ids.slice(at, call.end));
		at = call.end + call.final_ids.length;
	}
	out.push(c.response_ids.slice(at));
	return out;
}
