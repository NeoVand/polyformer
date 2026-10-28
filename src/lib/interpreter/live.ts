/**
 * The live model, through research/demolive/dl_server.py. The page asks its own origin's `/api`, which only the
 * local dev or preview server proxies to 127.0.0.1 (vite.config.ts). The built site has no such route, so there
 * the health check fails and the page replays recordings.
 */
import type { Ablation, BaseAnswerMeta, LlmTrace, Poke } from './trace.ts';

export interface Health {
	schema: 'polyformer.demolive/0';
	ok: boolean;
	model: string;
	adapters: { compile_adapter: string; executor_adapter: string };
	warm: boolean;
	spent_estimate_usd: number;
	cap_usd: number;
	busy: boolean;
	scaledown_seconds: number;
}

export type LiveEvent =
	| {
			type: 'stage';
			stage: string;
			register?: string;
			rows?: number;
			total?: number;
			prompt_tokens?: number;
	  }
	| { type: 'program'; text: string; tokens: number; seconds: number; exec: boolean }
	| { type: 'tape'; events: number; span: [number, number] }
	| {
			type: 'certificate';
			register: string;
			pass: boolean;
			rows: number;
			rows_wrong: number;
			min_margin: number;
	  }
	| { type: 'progress'; stage: string; done: number; total: number; seconds: number }
	| { type: 'trace'; trace: LlmTrace }
	| { type: 'error'; error: string };

export class LiveError extends Error {
	constructor(
		readonly status: number,
		message: string
	) {
		super(message);
	}
}

const API = '/api';
const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', '[::1]']);

/** The server's health, or null when there is no live model behind this page (the published site). */
export async function health(timeoutMs = 1500): Promise<Health | null> {
	// The local server only ever runs on this machine; the published site has no /api, so do not probe it there.
	if (typeof location !== 'undefined' && !LOCAL_HOSTS.has(location.hostname)) return null;
	try {
		const r = await fetch(`${API}/health`, { signal: AbortSignal.timeout(timeoutMs) });
		if (!r.ok) return null;
		const h = (await r.json()) as Health;
		return h?.schema === 'polyformer.demolive/0' && h.ok ? h : null;
	} catch {
		return null;
	}
}

async function post<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
	const r = await fetch(`${API}/${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body),
		signal
	});
	if (!r.ok) {
		const err = await r.json().catch(() => ({ error: r.statusText }));
		throw new LiveError(r.status, err.error ?? r.statusText);
	}
	return r.json() as Promise<T>;
}

/** The loop for one question, streamed: stages, progress, and the run's trace last. */
export async function* ask(question: string, signal?: AbortSignal): AsyncGenerator<LiveEvent> {
	const r = await fetch(`${API}/ask`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ question }),
		signal
	});
	if (!r.ok || !r.body) {
		const err = await r.json().catch(() => ({ error: r.statusText }));
		throw new LiveError(r.status, err.error ?? r.statusText);
	}
	const reader = r.body.pipeThrough(new TextDecoderStream()).getReader();
	let buf = '';
	for (;;) {
		const { value, done } = await reader.read();
		if (value) buf += value;
		let nl: number;
		while ((nl = buf.indexOf('\n')) >= 0) {
			const line = buf.slice(0, nl).trim();
			buf = buf.slice(nl + 1);
			if (line) yield JSON.parse(line) as LiveEvent;
		}
		if (done) break;
	}
	if (buf.trim()) yield JSON.parse(buf) as LiveEvent;
}

export interface PokeResult {
	register: string;
	step: number;
	forced: string;
	final: string;
	predicted_state: string | null;
	match: boolean;
	answer_after: string;
	ticks: number;
	ticks_bitwise_equal_to_certified_row: number;
	min_margin: number | null;
	predicted?: string | null;
	answer_states_prediction?: boolean | null;
}

/** Force the register's state entering tick `step` to its `forced`-th state, run on, and read the words. */
export async function poke(
	t: LlmTrace,
	register: string,
	step: number,
	forced: number
): Promise<Poke> {
	const p = await post<PokeResult>('poke', {
		question: t.prompt,
		ctx: t.ctx,
		register,
		step,
		forced
	});
	const reg = t.registers.find((r) => r.name === register);
	const was = step > 0 ? reg?.steps[step - 1]?.t : reg?.program.start;
	return {
		step,
		from: was ?? '',
		forced: p.forced,
		final: p.final,
		predicted_state: p.predicted_state,
		answer_after: p.answer_after,
		predicted: p.predicted ?? null,
		match: p.match,
		answer_states_prediction: p.answer_states_prediction ?? null,
		ticks: p.ticks,
		ticks_equal: p.ticks_bitwise_equal_to_certified_row,
		live: true
	};
}

/** The same register with the executor adapter off: the table and every tick on the base weights. */
export async function ablate(t: LlmTrace, register: string): Promise<Ablation> {
	const a = await post<Ablation>('ablate', { question: t.prompt, ctx: t.ctx, register });
	return { ...a, correct: a.correct ?? null, live: true };
}

/** Qwen3-4B with no adapter, on the same question. */
export function base(question: string) {
	return post<{ base_answer: string; base_answer_meta: BaseAnswerMeta }>('base', { question });
}
