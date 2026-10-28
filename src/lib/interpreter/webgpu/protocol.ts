/** Messages between the page and the worker that holds Savant-4B (worker.ts, client.svelte.ts). */
import type { EngineEvent, HostInfo, ModelInfo, Truth } from './engine.ts';
import type { LoadProgress } from './transformers-lm.ts';
import type { LlmCtx, LlmTrace, Poke } from '../trace.ts';

export interface Loaded {
	model: ModelInfo;
	host: HostInfo;
	device: string;
	dtype: string;
	/** the export computes only the last position's logits on request */
	lastOnly: boolean;
	seconds: number;
}

export type PokeResult = Poke & { min_margin: number | null; seconds: Record<string, number> };

export type ToWorker =
	| { type: 'load'; base: string; dtype: string; device: 'webgpu' | 'cpu' }
	| {
			type: 'ask';
			rid: number;
			question: string;
			opts: {
				id: string;
				title?: string;
				family?: string | null;
				truth?: Truth | null;
				lookupAfter?: number | null;
			};
	  }
	| {
			type: 'poke';
			rid: number;
			question: string;
			ctx: LlmCtx;
			register: string;
			step: number;
			forced: number;
			truth?: Truth | null;
			from?: string;
			lookupAfter?: number | null;
	  }
	| { type: 'cancel'; rid: number };

export type FromWorker =
	| { type: 'progress'; progress: LoadProgress }
	| { type: 'loaded'; loaded: Loaded }
	| { type: 'load-error'; error: string }
	| { type: 'event'; rid: number; event: EngineEvent }
	| { type: 'answered'; rid: number; trace: LlmTrace }
	| { type: 'poked'; rid: number; poke: PokeResult }
	| { type: 'failed'; rid: number; error: string; cancelled: boolean };
