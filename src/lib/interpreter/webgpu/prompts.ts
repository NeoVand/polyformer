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
