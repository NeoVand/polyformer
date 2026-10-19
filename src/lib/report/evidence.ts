/**
 * Every accuracy the project has measured, with where it came from. Browser
 * numbers come from this app's own engine (seed 0, 4,000 steps, 1,024 held-out
 * examples); harness numbers from the offline research harness used to choose
 * the tasks (one layer unless noted, d = 64, 4 heads, 4,000 steps, seed 0).
 */
export type Source = 'browser' | 'harness';

export interface EvidenceTask {
	id: string;
	label: string;
	detail: string;
}

export interface EvidenceModel {
	id: string;
	label: string;
}

export interface Cell {
	acc: number;
	source: Source;
	/** The run reported "about this", at the majority rate. */
	approx?: boolean;
}

export const TASKS: EvidenceTask[] = [
	{ id: 'set', label: 'SET', detail: 'three cards sum to 0' },
	{ id: 'set4', label: 'Four-card SET', detail: 'four cards sum to 0' },
	{ id: 'chase', label: 'Pointer chase', detail: 'one to three hops' },
	{ id: 'mod32', label: 'Match3 mod 32', detail: 'eight tokens, 8,000 steps' },
	{ id: 'hop3', label: 'Three-hop composition', detail: 'chained relations' }
];

export const MODELS: EvidenceModel[] = [
	{ id: 'std1', label: 'Standard, 1 layer' },
	{ id: 'std2', label: 'Standard, 2 layers' },
	{ id: 'std3', label: 'Standard, 3 layers' },
	{ id: 'tree', label: 'Tree (Columbia)' },
	{ id: 'strassen', label: 'Strassen' },
	{ id: 'cubic', label: 'Cubic' },
	{ id: 'quartic', label: 'Quartic' },
	{ id: 'hyperchain', label: 'Hyperchain' },
	{ id: 'dspa', label: 'Feynman' }
];

const b = (acc: number): Cell => ({ acc, source: 'browser' });
const h = (acc: number, approx = false): Cell => ({ acc, source: 'harness', approx });

export const EVIDENCE: Record<string, Partial<Record<string, Cell>>> = {
	set: {
		std1: b(0.605),
		std2: b(0.644),
		std3: h(0.59),
		tree: b(0.764),
		strassen: b(0.958),
		cubic: b(1),
		dspa: b(1)
	},
	set4: {
		std3: h(0.63, true),
		strassen: h(0.63, true),
		cubic: h(0.63, true),
		quartic: h(1),
		dspa: h(0.63, true)
	},
	chase: {
		std1: b(0.646),
		std2: b(0.889),
		std3: b(0.942),
		cubic: b(0.845),
		dspa: b(1)
	},
	mod32: {
		std3: h(0.91),
		tree: h(0.85),
		strassen: h(0.82),
		cubic: h(1)
	},
	hop3: {
		std2: h(1),
		tree: h(0.6, true),
		cubic: h(0.6, true),
		hyperchain: h(1),
		dspa: h(0.6, true)
	}
};
