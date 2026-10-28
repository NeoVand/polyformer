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
	/**
	 * ARITH_FORMAT's Mealy block instead of PROMPTBOX's: Π is rows of six tokens (s a b t o newline); forward 1 on
	 * [s][a][b] puts the top logit on the row's t, forward 2 on [s][a][b][t] puts it on the row's o, both right after
	 * Π and never kept (anything else throws). `wrongT` and `wrongO` give other argmaxes for some cells, keyed "s,a,b";
	 * `margins` gives a cell's two margins (else 8 to 9, varying by row).
	 */
	mealy?: {
		nl: number;
		wrongT?: Map<string, number>;
		wrongO?: Map<string, number>;
		margins?: Map<string, [number, number]>;
	};
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
	/** Mealy mode: every block fed after Π, with the position of its first token */
	readonly blocks: { ids: number[]; at: number }[] = [];
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
		} else if (this.s.mealy) {
			this.ticks++;
			const M = this.s.mealy;
			const find = (pi: number[], s: number, a: number, b: number) => {
				for (let i = 0, k = 0; i + 4 < pi.length; i += 6, k++)
					if (pi[i] === s && pi[i + 1] === a && pi[i + 2] === b)
						return { t: pi[i + 3], o: pi[i + 4], k };
				return null;
			};
			if (!past) logits[0] = 1;
			else {
				// §4: both forwards right after Π (rows of six ending in a newline), neither cache kept
				if (keep || before.length % 6 !== 0 || before.at(-1) !== M.nl)
					throw new Error('a Mealy forward must run on Π’s own cache and keep nothing');
				if (ids.length !== 3 && ids.length !== 4)
					throw new Error(`a Mealy forward feeds [s][a][b] or [s][a][b][t], not ${ids.length} ids`);
				this.blocks.push({ ids: [...ids], at: before.length });
				const [s, a, b] = ids;
				const key = `${s},${a},${b}`;
				const r = find(before, s, a, b);
				const k = r?.k ?? 0;
				const [m1, m2] = M.margins?.get(key) ?? [8 + (k % 5) * 0.25, 8 + (k % 3) * 0.5];
				const top =
					ids.length === 3
						? (M.wrongT?.get(key) ?? r?.t ?? before[0])
						: (M.wrongO?.get(key) ?? r?.o ?? before[0]);
				const runner = top === M.nl ? before[0] : M.nl;
				// every other logit is 0, so the margin is exactly m while m < 40
				logits[top] = 40;
				logits[runner] = 40 - (ids.length === 3 ? m1 : m2);
			}
			if (this.s.jitter?.(this.ticks)) logits[this.V - 1] = 1e-30;
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

// ------------------------------------------------------------------ a scripted LM for calls in the middle (REASON)

export interface TranscriptScript {
	/** the chat prompt's ids: a context starting with them is a generation, anything else a Π */
	prompt: number[];
	/** what the model writes, piece by piece; after every piece but the last the clock appends a final line */
	pieces: number[][];
	/** the end-of-turn token, written after the last piece */
	end: number;
	/** decodes ids, to see where the clock's final line ends (`</final>\n`) */
	decode: (ids: number[]) => string;
	/** Π rows end with the newline id */
	nl: number;
	vocab?: number;
}

/**
 * A scripted model for transcripts with calls in the middle (REASON_FORMAT): it writes `pieces` in order and, after
 * each piece but the last, expects the clock's final line (anything up to `</final>\n`) before writing the next. A
 * context that leaves the script throws. Ticks run whatever table they are shown, exactly: a Moore tick ([s][e] over
 * rows of four) lands on the row's destination; a Mealy forward ([s][a][b], then [s][a][b][t], over rows of six,
 * keeping nothing) puts its top logit on the row's t, then its o. Every tick records its block and its cache, so a
 * test can check that each call's Π was built fresh at positions 0 ….
 */
export class TranscriptLM implements LM {
	readonly chunk = 64;
	readonly live = new Set<FakeKV>();
	calls = 0;
	ticks = 0;
	/** every tick block: its ids, the position of its first token, and the cache it ran over (its Π) */
	readonly blocks: { ids: number[]; at: number; pi: number[] }[] = [];
	private V: number;
	private finals = new Map<number, number[]>();
	constructor(private s: TranscriptScript) {
		this.V = s.vocab ?? 151936;
	}

	async forward(ids: number[], past: KV | null, keep: boolean): Promise<Forward> {
		this.calls++;
		if (past && (past as FakeKV).disposed) throw new Error('forward on a disposed cache');
		const before = past ? (past as FakeKV).tokens : [];
		const ctx = [...before, ...ids];
		const logits = new Float32Array(this.V);
		const { prompt, nl } = this.s;
		/** generation's logits are never compared bit for bit: skip hashing 600 kB per token */
		let bits: string | null = null;
		if (startsWith(ctx, prompt) || startsWith(prompt, ctx)) {
			const next = ctx.length >= prompt.length ? this.next(ctx.slice(prompt.length)) : null;
			logits[next ?? 0] = 5;
			bits = `generation ${next}`;
		} else if (!past) {
			logits[0] = 1;
		} else if (ids.length === 2) {
			// a Moore tick: Π (rows of s e t newline) then [s][e]
			this.ticks++;
			this.blocks.push({ ids: [...ids], at: before.length, pi: before });
			const [s, e] = ids;
			let dest = before[0];
			for (let i = 0; i + 3 < before.length; i += 4)
				if (before[i] === s && before[i + 1] === e && before[i + 3] === nl) {
					dest = before[i + 2];
					break;
				}
			logits[dest === before[0] ? before[4] : before[0]] = 2;
			logits[dest] = 10;
		} else if (ids.length === 3 || ids.length === 4) {
			// a Mealy forward: Π (rows of s a b t o newline) then [s][a][b] or [s][a][b][t], never kept
			if (keep || before.length % 6 !== 0 || before.at(-1) !== nl)
				throw new Error('a Mealy forward must run on Π’s own cache and keep nothing');
			this.ticks++;
			this.blocks.push({ ids: [...ids], at: before.length, pi: before });
			const [s, a, b] = ids;
			let top = before[0];
			for (let i = 0; i + 5 < before.length; i += 6)
				if (before[i] === s && before[i + 1] === a && before[i + 2] === b) {
					top = ids.length === 3 ? before[i + 3] : before[i + 4];
					break;
				}
			logits[top] = 40;
			logits[top === nl ? before[0] : nl] = 32;
		} else throw new Error(`no tick feeds ${ids.length} ids over a Π`);
		const kv = new FakeKV(ctx, this.live);
		if (!keep) kv.dispose();
		return {
			logits,
			bits: bits ?? fingerprint(new Uint8Array(logits.buffer)),
			past: keep ? kv : null
		};
	}

	/**
	 * The id the script writes after `resp`: the next of its piece, or the end token after the last. Null while `resp`
	 * ends inside the clock's final line (the engine is feeding it); throws when `resp` is off the script.
	 */
	private next(resp: number[]): number | null {
		const { pieces } = this.s;
		let at = 0;
		for (let i = 0; i < pieces.length; i++) {
			const p = pieces[i];
			for (let j = 0; j < p.length; j++) {
				if (at + j === resp.length) return p[j];
				if (resp[at + j] !== p[j])
					throw new Error(`the transcript left the script at response position ${at + j}`);
			}
			at += p.length;
			if (i === pieces.length - 1) break;
			// the clock's line, up to and including `</final>\n`
			const memo = this.finals.get(at);
			if (memo && memo.every((x, j) => resp[at + j] === x)) {
				at += memo.length;
				continue;
			}
			let k = at;
			while (k < resp.length && !this.s.decode(resp.slice(at, k + 1)).endsWith('</final>\n')) k++;
			if (k >= resp.length) return null;
			this.finals.set(at, resp.slice(at, k + 1));
			at = k + 1;
		}
		if (at === resp.length) return this.s.end;
		throw new Error('the transcript ran past the script');
	}
}
