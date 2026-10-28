/**
 * Qwen3's tokenizer as the clock uses it (pb.ts's `Tok`), over the JavaScript tokenizer transformers.js loads. Two
 * things the Python `tokenizers` library gives for free are rebuilt here: decoding skips special tokens with no
 * clean-up (its defaults), and token offsets, which the JavaScript tokenizer does not return, come from the tokens'
 * bytes: Qwen3's tokenizer is byte-level BPE, so the tokens' bytes, in order, are the question's UTF-8 bytes.
 */
import type { Tok } from './pb.ts';

/** The JavaScript tokenizer's surface used here (@huggingface/tokenizers, as transformers.js holds it). */
export interface RawTokenizer {
	encode(
		text: string,
		options?: { add_special_tokens?: boolean }
	): { ids: number[]; tokens: string[] };
	decode(
		ids: number[],
		options?: { skip_special_tokens?: boolean; clean_up_tokenization_spaces?: boolean | null }
	): string;
	get_added_tokens_decoder(): Map<number, { content: string }>;
}

/** GPT-2's bytes_to_unicode, inverted: the byte each printable stand-in character means. */
function byteDecoder(): Map<string, number> {
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
}

const BYTES = byteDecoder();
const utf8 = new TextEncoder();

/** The bytes a token stands for: an added token's text, or a byte-level token's characters mapped back to bytes. */
function tokenBytes(token: string, added: boolean): number {
	if (added) return utf8.encode(token).length;
	let n = 0;
	for (const c of token) {
		if (!BYTES.has(c)) throw new Error(`not a byte-level token: ${JSON.stringify(token)}`);
		n++;
	}
	return n;
}

/**
 * For each UTF-8 byte of `text`, the UTF-16 index of the character it belongs to; and the index after it.
 * Offsets of a token are [start of the character holding its first byte, end of the one holding its last byte),
 * which is how `tokenizers` aligns byte-level tokens that split a character.
 */
function byteToChar(text: string): { start: Int32Array; end: Int32Array; bytes: number } {
	const total = utf8.encode(text).length;
	const start = new Int32Array(total);
	const end = new Int32Array(total);
	let b = 0;
	for (let i = 0; i < text.length;) {
		const cp = text.codePointAt(i)!;
		const units = cp > 0xffff ? 2 : 1;
		const n = cp < 0x80 ? 1 : cp < 0x800 ? 2 : cp < 0x10000 ? 3 : 4;
		for (let k = 0; k < n; k++) {
			start[b + k] = i;
			end[b + k] = i + units;
		}
		b += n;
		i += units;
	}
	return { start, end, bytes: total };
}

export function qwenTok(raw: RawTokenizer): Tok {
	const added = new Set<string>([...raw.get_added_tokens_decoder().values()].map((t) => t.content));
	return {
		encode: (text) => raw.encode(text, { add_special_tokens: false }).ids,
		decode: (ids) =>
			ids.length
				? raw.decode(ids, { skip_special_tokens: true, clean_up_tokenization_spaces: false })
				: '',
		encodeWithOffsets(text) {
			const { ids, tokens } = raw.encode(text, { add_special_tokens: false });
			const map = byteToChar(text);
			const offsets: [number, number][] = [];
			let b = 0;
			for (const t of tokens) {
				const n = tokenBytes(t, added.has(t));
				if (n === 0 || b + n > map.bytes) throw new Error('token bytes do not cover the text');
				offsets.push([map.start[b], map.end[b + n - 1]]);
				b += n;
			}
			// the tokenizer normalises to NFC: on text that is not NFC already the bytes would not line up
			if (b !== map.bytes) throw new Error('token bytes do not cover the text (is it NFC?)');
			return { ids, offsets };
		}
	};
}
