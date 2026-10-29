/** Messages between the page and the worker that holds the sketchpad model (worker.ts, pad.svelte.ts). */
import type { Kind } from './models.ts';
import type { Op } from './multiplier.ts';

/** `ADD` is the adder's prompt; the multiplier's five ops have their own. */
export type TickOp = 'ADD-FAST' | Op;

export interface LoadedInfo {
	kind: Kind;
	seconds: number;
	/** fingerprint of every model file the worker fetched, by path */
	prints: Record<string, string>;
	sprites: string;
	gpu: string;
	transformers: string;
}

export type ToWorker =
	| { type: 'load'; kind: Kind; base: string; sprites: string }
	| { type: 'certify'; rid: number; kind: Kind }
	| { type: 'tick'; rid: number; op: TickOp; cells: string[] }
	| { type: 'chat'; rid: number; question: string; maxNew: number }
	| { type: 'cancel'; rid: number };

export type FromWorker =
	| {
			type: 'progress';
			kind: Kind;
			files: Record<string, { loaded: number; total: number }>;
			stage: 'download' | 'compile';
	  }
	| { type: 'loaded'; info: LoadedInfo }
	| { type: 'load-error'; kind: Kind; error: string }
	/** a run of certificate rows from `start`; `got` is the model's own answer where a row failed */
	| { type: 'cert-rows'; rid: number; start: number; margins: number[]; got: (string | null)[] }
	| { type: 'cert-done'; rid: number; seconds: number }
	| {
			type: 'tick';
			rid: number;
			/** the answer tokens as text */
			out: string[];
			/** argmax margin of the adder's single token (the multiplier decodes greedily: null) */
			margin: number | null;
			ms: number;
			/** the 32 x 96 RGBA strip the model read */
			strip: Uint8ClampedArray;
	  }
	| { type: 'chat-delta'; rid: number; text: string }
	| { type: 'done'; rid: number; ms: number }
	| { type: 'failed'; rid: number; error: string; cancelled: boolean };
