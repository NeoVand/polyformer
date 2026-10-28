/**
 * pb_families.answer_correct, ported: whether a plain-words answer states exactly what the question's answer key
 * requires. Keys are written by research/demolive/dl_web.py (static/interpreter/prompts.json); answer.spec.ts checks
 * this port against the Python on every suggested prompt's truth, predicted and reworded answers.
 */

export interface Slot {
	label: string;
	kind: 'num' | 'word';
	value: string | number;
	domain: (string | number)[];
}

export interface AnswerKey {
	yesno: boolean | null;
	option?: string | null;
	digits?: string | null;
	text?: string | null;
	slots?: Slot[];
	[k: string]: unknown;
}

import { pyStrip } from './pb.ts';

const isAlnum = (c: string) => /[\p{L}\p{N}]/u.test(c);

/** pb_families._norm */
const norm = (text: string) =>
	[...text]
		.map((c) => (isAlnum(c) ? c.toLowerCase() : ' '))
		.join('')
		.split(/\s+/)
		.filter(Boolean)
		.join(' ');

/** pb_families.last_number */
function lastNumber(text: string): string | null {
	const runs = text.match(/\d(?:[\d,\u2009\u202f ]*\d)?/g);
	return runs ? runs[runs.length - 1].replace(/\D/g, '') : null;
}

function lastOption(text: string): string | null {
	const found = [...text.matchAll(/\(([A-Z])\)/g)];
	return found.length ? found[found.length - 1][1] : null;
}

/** Single letters keep their case (so the article "a" is not the value "A"); words compare in lower case. */
const tokw = (w: string) => (w.length === 1 ? w : w.toLowerCase());

function mentions(slots: Slot[], t: string): string[] {
	const domain = new Set(slots.flatMap((sl) => sl.domain.map((x) => tokw(String(x)))));
	const out: string[] = [];
	for (const m of t.matchAll(/[A-Za-z]+|\d+/g)) {
		const end = m.index + m[0].length;
		if (/^\s*=/.test(t.slice(end))) continue;
		const w = tokw(m[0]);
		if (domain.has(w)) out.push(w);
	}
	return out;
}

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function labelled(slot: Slot, t: string): string[] {
	const lab = slot.label;
	if (!lab || !/^[\p{L}]+$/u.test(lab)) return [];
	const re = new RegExp(
		`(?<![A-Za-z0-9_])${escapeRe(lab)}(?![A-Za-z0-9_])\\s*(?:=|:|\\bis\\b|\\bwas\\b)?\\s*([A-Za-z]+|\\d+)`,
		'gi'
	);
	const found = [...t.matchAll(re)].map((m) => tokw(m[1]));
	if (slot.kind === 'num') return found.filter((x) => /^\d+$/.test(x));
	const domain = new Set(slot.domain.map((v) => tokw(String(v))));
	return found.filter((x) => domain.has(x));
}

function oneSlot(slot: Slot, t: string): boolean {
	const want = tokw(String(slot.value));
	if (slot.kind === 'word') {
		const found = mentions([slot], t);
		return found.includes(want) && found.every((w) => w === want);
	}
	const got = labelled(slot, t);
	if (got.length) return got.length === 1 && got[0] === want;
	const domain = new Set(slot.domain);
	const nums = [...t.matchAll(/(?<![\d.])\d+(?![\d.]*\d)/g)].map((m) => parseInt(m[0], 10));
	const inDomain = nums.filter((n) => domain.has(n));
	return inDomain.length === 1 && inDomain[0] === slot.value;
}

const sameList = (a: string[], b: string[]) =>
	a.length === b.length && a.every((x, i) => x === b[i]);

function manySlots(slots: Slot[], t: string): boolean {
	const want = slots.map((sl) => tokw(String(sl.value)));
	const labels = slots.map((sl) => sl.label);
	if (labels.every(Boolean) && new Set(labels).size === labels.length) {
		const got = slots.map((sl) => labelled(sl, t));
		if (got.every((g) => g.length)) {
			if (got.some((g, i) => g.some((x) => x !== want[i]))) return false;
			const words = slots.filter((sl) => sl.kind === 'word');
			const mentioned = mentions(words, t).filter((w) => !/^\d+$/.test(w));
			const expected = words.map((sl) => tokw(String(sl.value))).filter((w) => !/^\d+$/.test(w));
			return sameList([...mentioned].sort(), [...expected].sort());
		}
	}
	return sameList(mentions(slots, t), want);
}

/** pb_families.answer_correct */
export function answerCorrect(key: AnswerKey, text: string): boolean {
	const t = pyStrip(text);
	if (key.option !== undefined && key.option !== null) return lastOption(t) === key.option;
	if (key.digits !== undefined && key.digits !== null) return lastNumber(t) === key.digits;
	if (key.text !== undefined && key.text !== null) return norm(t) === norm(key.text);
	if (key.yesno !== null) {
		const low = t.toLowerCase().replace(/^[*"' ]+/, '');
		if (!low.startsWith(key.yesno ? 'yes' : 'no')) return false;
	}
	const slots = key.slots ?? [];
	if (slots.length === 1) return oneSlot(slots[0], t);
	if (slots.length) return manySlots(slots, t);
	return true;
}
