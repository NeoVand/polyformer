/** The paper's parts and sections, in reading order. Section numbers come from here. */
export interface Part {
	id: string;
	title: string;
	sections: { id: string; title: string }[];
}

export const PARTS: Part[] = [
	{
		id: 'part-question',
		title: 'The question',
		sections: [
			{ id: 'intro', title: 'What this is about' },
			{ id: 'puzzles', title: 'The puzzles' },
			{ id: 'encoding', title: 'How a puzzle becomes tokens' }
		]
	},
	{
		id: 'part-pairs',
		title: 'Attention beyond pairs',
		sections: [
			{ id: 'pairwise', title: 'Attention compares pairs' },
			{ id: 'blind', title: 'Why pairs are blind to SET' },
			{ id: 'cubic', title: 'Scoring whole triples' },
			{ id: 'barrier', title: 'Cheaper relatives, and what they miss' },
			{ id: 'head', title: 'A head built by hand' },
			{ id: 'training', title: 'What training shows' },
			{ id: 'arity', title: 'Four cards need a four-way term' }
		]
	},
	{
		id: 'part-feynman',
		title: 'Letting the data choose the arity',
		sections: [
			{ id: 'feynman', title: 'Where Feynman diagrams come from' },
			{ id: 'dyson', title: 'Summing all the diagrams at once' },
			{ id: 'diagrams', title: 'Feynman attention' },
			{ id: 'sectors', title: 'Making it train' },
			{ id: 'chase', title: 'What Feynman attention learns' }
		]
	},
	{
		id: 'part-newton',
		title: 'Every arity at once',
		sections: [
			{ id: 'composition', title: 'Big relations do not grow from small ones' },
			{ id: 'groups', title: 'A group is a rule for combining' },
			{ id: 'characters', title: 'Relations as agreeing phases' },
			{ id: 'newton', title: "Newton's shortcut" },
			{ id: 'newtonattn', title: 'Newton attention' },
			{ id: 'transfer', title: 'Small relations teach large ones' }
		]
	},
	{
		id: 'part-language',
		title: 'The language test',
		sections: [
			{ id: 'language', title: 'What we tried on text' },
			{ id: 'language-reading', title: 'What the language result means' }
		]
	},
	{
		id: 'part-turn',
		title: 'The turn: composition',
		sections: [
			{ id: 'coordinates', title: 'Good coordinates are not enough' },
			{ id: 'order', title: 'When order changes the answer' },
			{ id: 'representations', title: 'Operations as rotations' },
			{ id: 'holonomy', title: 'Holonomy attention' }
		]
	},
	{
		id: 'part-results',
		title: 'What each kind of layer can learn',
		sections: [
			{ id: 'ceiling', title: 'The price of forgetting order' },
			{ id: 'learned', title: 'The heads learn the group' },
			{ id: 'theory', title: 'What is proved' },
			{ id: 'programs', title: 'Running small programs' },
			{ id: 'word-problems', title: 'Long products: word problems' }
		]
	},
	{
		id: 'part-limits',
		title: 'Where composition does not pay',
		sections: [
			{ id: 'combined', title: 'One layer with everything' },
			{ id: 'dilution', title: 'Is the loss hiding it?' },
			{ id: 'arc', title: 'Grid puzzles in the style of ARC' }
		]
	},
	{
		id: 'part-memory',
		title: 'Memory on text',
		sections: [
			{ id: 'two-memories', title: 'Two memories on text' },
			{ id: 'segments', title: 'The models find events on their own' },
			{ id: 'fair', title: 'A stronger baseline erases it at short range' },
			{ id: 'context', title: 'What pays at long context' },
			{ id: 'event-model', title: 'Events as the unit of memory' },
			{ id: 'why-text', title: 'Why text rewards resets, not groups' }
		]
	},
	{
		id: 'part-exact',
		title: 'States that stay exact',
		sections: [
			{ id: 'flat-set', title: 'Why training lands near exact' },
			{ id: 'nerode-term', title: 'One state for equivalent histories' },
			{ id: 'certified', title: 'Lean as the referee' },
			{ id: 'exact-limits', title: 'What is shown, and what is not' },
			{ id: 'hardening', title: 'Harder tests of the same result' },
			{ id: 'nerode-metric', title: 'The three clauses in one loss' },
			{ id: 'state-geometry', title: 'What the exact state is, and what it saves' },
			{ id: 'natural-proofs', title: 'Natural proofs: the kind of step, not the terms' },
			{ id: 'kernel-oracle', title: 'Reading out verdicts, not strings' }
		]
	},
	{
		id: 'part-lessons',
		title: 'What we learned',
		sections: [
			{ id: 'lessons', title: 'Finding structure is the hard part' },
			{ id: 'next', title: 'What we would try next' },
			{ id: 'related', title: 'What is new here, and what is not' },
			{ id: 'methods', title: 'Methods, cost and reproducibility' }
		]
	}
];

const ORDER = PARTS.flatMap((p) => p.sections.map((s) => s.id));
const ROMAN = [
	'I',
	'II',
	'III',
	'IV',
	'V',
	'VI',
	'VII',
	'VIII',
	'IX',
	'X',
	'XI',
	'XII',
	'XIII',
	'XIV'
];

/** The part's roman numeral in reading order. Throws on an unknown id so typos surface. */
export function roman(id: string): string {
	const i = PARTS.findIndex((p) => p.id === id);
	if (i < 0 || i >= ROMAN.length) throw new Error(`unknown paper part: ${id}`);
	return ROMAN[i];
}

/** The section's number in reading order, 1-based. Throws on an unknown id so typos surface. */
export function number(id: string): number {
	const i = ORDER.indexOf(id);
	if (i < 0) throw new Error(`unknown paper section: ${id}`);
	return i + 1;
}

/** Every anchor the paper has: its parts, its sections and the reference list. */
export const ANCHORS = new Set([
	...PARTS.flatMap((p) => [p.id, ...p.sections.map((s) => s.id)]),
	'references'
]);

/** Anchors of the old Learn page whose section was renamed or merged in the paper. */
export const LEARN_ANCHORS: Record<string, string> = {
	'part-setting': 'part-question',
	'part-known': 'part-pairs',
	'part-new': 'part-pairs',
	'part-beyond': 'part-feynman',
	'part-algebra': 'part-newton',
	'part-compose': 'part-turn',
	product: 'cubic',
	cost: 'cubic',
	degree2: 'barrier',
	set: 'blind',
	binding: 'head',
	features: 'coordinates',
	'group-results': 'learned',
	limits: 'theory',
	meaning: 'lessons'
};

/** Anchors of the old Report page whose section was renamed or merged in the paper. */
export const REPORT_ANCHORS: Record<string, string> = {
	abstract: 'intro',
	beginning: 'part-pairs',
	composition: 'coordinates',
	'character-results': 'coordinates',
	'fig-characters': 'newtonattn',
	groups: 'ceiling',
	'fig-ladder': 'ceiling',
	meaning: 'lessons',
	reproducibility: 'methods'
};

/** Where an old page's anchor lives now: renamed, kept, a reference, or the top. */
export function movedAnchor(map: Record<string, string>, hash: string): string {
	const id = decodeURIComponent(hash.replace(/^#/, ''));
	if (map[id]) return map[id];
	if (ANCHORS.has(id) || id.startsWith('ref-')) return id;
	return '';
}
