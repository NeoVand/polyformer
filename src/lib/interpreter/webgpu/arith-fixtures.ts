/** Test-only: arith_core's fixtures as copied by scripts/arith_fixtures.py (Node; never imported by the page). */
import { readFileSync } from 'node:fs';

export interface Example {
	question: string;
	chat_prompt_ids: number[];
	program_text: string;
	program_ids: number[];
	parsed: {
		mode: string;
		error: string | null;
		numbers: { first: [string, string]; second: [string, string] };
		register: {
			name: string;
			output: string;
			start: number;
			rows: number[][];
			pi_len: number;
			pi_sha256: string;
		};
	};
	reading: {
		spans: [[number, number], [number, number]];
		numbers: [string, string];
		pairs: [number, number][];
		error: string | null;
	};
	first_tick: {
		forward1: { ids: number[]; positions: number[] };
		forward2: { ids: number[]; positions: number[] };
	};
	run: { states: number[]; outputs: number[] };
	final_ids: number[];
	final_text: string;
	answer_ids: number[];
	answer_text: string;
	sum: string;
}

/** A run of the trained model from ARITH's counted gate (reference.json `model_runs`). */
export interface ModelRun {
	cell: string;
	question: string;
	program_ids: number[];
	anchors: { first: [string, string]; second: [string, string] };
	pi_len: number;
	pairs: [number, number][];
	states: number[];
	outputs: number[];
	final_ids: number[];
	final_text: string;
	answer_text: string;
	/** per row "sab" (digits): the carry cell's margin and the digit cell's */
	certificate: {
		pass: boolean;
		min_margin: number;
		rows: number;
		margins: [string, number, number][];
	};
}

export const arith = JSON.parse(
	readFileSync(new URL('./fixtures/arith.json', import.meta.url), 'utf8')
) as {
	tokenizer_sha256: string;
	ids: { nl: number; digits: number[]; im_end: number };
	adder_rows: string[][];
	examples: Example[];
	model_runs: { source: string; runs: ModelRun[] };
	failures: {
		case: string;
		question: string;
		program_ids: number[];
		parse_error: string | null;
		reading_error: string | null;
	}[];
	tokens: Record<string, string>;
	special: number[];
	encoded: Record<string, number[]>;
};
