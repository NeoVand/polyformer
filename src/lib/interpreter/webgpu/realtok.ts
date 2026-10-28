/**
 * Node only (tests and the parity script): Qwen3's real tokenizer from a tokenizer.json on disk, wrapped as the
 * clock's `Tok`. Looks in $QWEN_TOKENIZER, the local Savant export, then the Hugging Face cache
 * (QWEN_TOKENIZER=none runs the tests on the fixtures' own tokens only).
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { qwenTok, type RawTokenizer } from './tokenizer.ts';
import type { Tok } from './pb.ts';

export function findTokenizer(): string | null {
	if (process.env.QWEN_TOKENIZER === 'none') return null;
	const cands = [
		process.env.QWEN_TOKENIZER,
		resolve(process.cwd(), '../models/savant-4b-preview/tokenizer.json'),
		resolve(process.cwd(), '../models/qwen3-4b-pb-s2g750/tokenizer.json')
	];
	const snaps = join(homedir(), '.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots');
	if (existsSync(snaps))
		for (const d of readdirSync(snaps)) cands.push(join(snaps, d, 'tokenizer.json'));
	return cands.find((p) => p && existsSync(p)) ?? null;
}

export async function realTok(path: string): Promise<Tok> {
	const { PreTrainedTokenizer } = await import('@huggingface/transformers');
	const json = JSON.parse(readFileSync(path, 'utf8'));
	const cfgPath = join(path, '../tokenizer_config.json');
	const config = existsSync(cfgPath) ? JSON.parse(readFileSync(cfgPath, 'utf8')) : {};
	const t = new PreTrainedTokenizer(json, config) as unknown as { _tokenizer: RawTokenizer };
	return qwenTok(t._tokenizer);
}
