/**
 * Stand-ins for the unit tests and the page's end-to-end tests: a tokenizer read from the Python reference fixtures,
 * and a scripted causal LM that writes a given program, runs any table it is shown exactly (one tick = the row's
 * destination), and answers after `<final>` with a fixed sentence. No model and no network.
 */
import type { Forward, KV, LM } from './engine.ts';
import type { Tok } from './pb.ts';
import { fingerprint } from './transformers-lm.ts';

/** GPT-2 bytes_to_unicode, inverted. */
const BYTE = (() => {
	const bs: number[] = [];
	for (let b = 33; b <= 126; b++) bs.push(b);
	for (let b = 161; b <= 172; b++) bs.push(b);
	for (let b = 174; b <= 255; b++) bs.push(b);
	const cs = [...bs];
	let n = 0;
	for (let b = 0; b < 256; b++)
		if (!bs.includes(b)) {
			bs.push(b);
			cs.push(256 + n++);
		}
	return new Map(bs.map((b, i) => [String.fromCharCode(cs[i]), b]));
})();

export interface FixtureCase {
	question: string;
	question_ids: number[];
	question_offsets: [number, number][];
	tokens: Record<string, string>;
	chat_prompt_ids?: number[];
}

/**
 * A tokenizer that knows only the ids in the fixtures: decoding is byte-level BPE's own (token characters to bytes,
 * bytes to UTF-8 text, special tokens skipped); encoding knows the fixture's question and any text registered.
 */
export class FixtureTok implements Tok {
	private texts = new Map<string, { ids: number[]; offsets: [number, number][] }>();
	constructor(
		private tokens: Map<number, string>,
		private special: Set<number>
	) {}

	static from(
		cases: FixtureCase[],
		special: number[],
		extra: { tokens?: Record<string, string>; encoded?: Record<string, number[]> } = {}
	): FixtureTok {
		const tokens = new Map<number, string>();
		for (const c of cases) for (const [k, v] of Object.entries(c.tokens)) tokens.set(Number(k), v);
		for (const [k, v] of Object.entries(extra.tokens ?? {})) tokens.set(Number(k), v);
		const t = new FixtureTok(tokens, new Set(special));
		for (const [text, ids] of Object.entries(extra.encoded ?? {})) t.learn(text, ids);
		for (const c of cases) t.learn(c.question, c.question_ids, c.question_offsets);
		return t;
	}

	learn(text: string, ids: number[], offsets?: [number, number][]) {
		this.texts.set(text, { ids, offsets: offsets ?? [] });
	}

	encode(text: string): number[] {
		const have = this.texts.get(text);
		if (!have) throw new Error(`FixtureTok cannot encode ${JSON.stringify(text.slice(0, 40))}`);
		return [...have.ids];
	}

	encodeWithOffsets(text: string) {
		const have = this.texts.get(text);
		if (!have || have.offsets.length !== have.ids.length)
			throw new Error('FixtureTok has no offsets for this text');
		return { ids: [...have.ids], offsets: have.offsets.map((o) => [...o] as [number, number]) };
	}

	decode(ids: number[]): string {
		const bytes: number[] = [];
		const parts: string[] = [];
		const flush = () => {
			if (bytes.length) parts.push(new TextDecoder().decode(Uint8Array.from(bytes)));
			bytes.length = 0;
		};
		for (const id of ids) {
			if (this.special.has(id)) continue;
			const t = this.tokens.get(id);
			if (t === undefined) throw new Error(`FixtureTok does not know token ${id}`);
			const mapped = [...t].map((c) => BYTE.get(c));
			if (mapped.every((b) => b !== undefined)) bytes.push(...(mapped as number[]));
			else {
				flush();
				parts.push(t);
			}
		}
		flush();
		return parts.join('');
	}
}

// ------------------------------------------------------------------ a scripted LM

class FakeKV implements KV {
	disposed = false;
	constructor(
		readonly tokens: number[],
		private book: Set<FakeKV>
	) {
		book.add(this);
	}
	get length() {
		return this.tokens.length;
	}
	dispose() {
		if (this.disposed) throw new Error('disposed twice');
		this.disposed = true;
		this.book.delete(this);
	}
}

export interface FakeScript {
	/** the chat prompt's ids: a context starting with them is a generation, anything else a Π */
	prompt: number[];
	/** what the model writes after the prompt (it should end with <exec/>, else an end token follows) */
	program: number[];
	/** the end-of-turn token */
	end: number;
	/** the words after `<final>`, given the ids between `\n<final>` and ` </final>\n` */
	words: (line: number[]) => number[];
	/** ids of `\n<final>`, to find the line */
	finalOpen: number[];
	/** ids of ` </final>\n` */
	finalClose: number[];
	/** rows to get wrong when certifying: (s, e) → the argmax to give instead */
	wrong?: Map<string, number>;
	/** ticks whose logits differ in their last bits from the certified row's, by tick count */
	jitter?: (call: number) => boolean;
	vocab?: number;
}

/**
 * The scripted LM. Ticks read Π as rows of four tokens (s e t newline) and put the largest logit on the row's
 * destination (margin 8 + a little per row), so a correct table certifies and runs exactly; the first state id
 * of each row also gets a smaller logit, so the margin is the gap to it.
 */
export class FakeLM implements LM {
	readonly chunk: number;
	readonly live = new Set<FakeKV>();
	calls = 0;
	ticks = 0;
	private V: number;
	constructor(
		private s: FakeScript,
		chunk = 64
	) {
		this.chunk = chunk;
		this.V = s.vocab ?? 151936;
	}

	async forward(ids: number[], past: KV | null, keep: boolean): Promise<Forward> {
		this.calls++;
		const before = past ? (past as FakeKV).tokens : [];
		if (past && (past as FakeKV).disposed) throw new Error('forward on a disposed cache');
		const ctx = [...before, ...ids];
		const logits = new Float32Array(this.V);
		// the prompt, a part of it (a prefill chunk), or the prompt and more: a generation; anything else a Π
		const isGen = startsWith(ctx, this.s.prompt) || startsWith(this.s.prompt, ctx);
		if (isGen) {
			const at = ctx.length - this.s.prompt.length;
			const open = lastIndexOf(ctx, this.s.finalOpen);
			if (open >= 0) {
				const close = indexOfFrom(ctx, this.s.finalClose, open);
				if (close < 0) logits[0] = 1;
				else {
					const line = ctx.slice(open + this.s.finalOpen.length, close);
					const words = [...this.s.words(line), this.s.end];
					const k = ctx.length - (close + this.s.finalClose.length);
					logits[words[Math.min(k, words.length - 1)]] = 5;
				}
			} else if (at < 0) logits[0] = 1;
			else if (at < this.s.program.length) logits[this.s.program[at]] = 5;
			else logits[this.s.end] = 5;
		} else {
			// a tick: Π then the block [s][e]
			this.ticks++;
			const n = ctx.length;
			const s = ctx[n - 2];
			const e = ctx[n - 1];
			const P = before.length;
			let dest = -1;
			let k = 0;
			for (let i = 0; i + 2 < P; i += 4, k++)
				if (before[i] === s && before[i + 1] === e) {
					dest = before[i + 2];
					break;
				}
			const wrong = this.s.wrong?.get(`${s},${e}`);
			const top = wrong ?? (dest >= 0 ? dest : (before[0] ?? 0));
			const runner = before[0] === top ? (before[4] ?? 1) : (before[0] ?? 1);
			logits[runner] = 2;
			logits[top] = 10 + (k % 5) * 0.25;
			if (this.s.jitter?.(this.ticks)) logits[this.V - 1] = 1e-30;
		}
		const kv = new FakeKV(ctx, this.live);
		if (!keep) kv.dispose();
		return {
			logits,
			bits: fingerprint(new Uint8Array(logits.buffer)),
			past: keep ? kv : null
		};
	}
}

function startsWith(a: number[], b: number[]) {
	if (a.length < b.length) return false;
	for (let i = 0; i < b.length; i++) if (a[i] !== b[i]) return false;
	return true;
}

function indexOfFrom(a: number[], b: number[], from: number) {
	outer: for (let i = from; i + b.length <= a.length; i++) {
		for (let j = 0; j < b.length; j++) if (a[i + j] !== b[j]) continue outer;
		return i;
	}
	return -1;
}

function lastIndexOf(a: number[], b: number[]) {
	for (let i = a.length - b.length; i >= 0; i--) {
		let ok = true;
		for (let j = 0; j < b.length; j++)
			if (a[i + j] !== b[j]) {
				ok = false;
				break;
			}
		if (ok) return i;
	}
	return -1;
}
