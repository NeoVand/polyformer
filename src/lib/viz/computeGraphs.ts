/**
 * Computation graphs for every operator the app discusses, after the figure in the original
 * Polyformer notebook (April 2023): the input X fans out through projections, Hadamard products
 * and merges build the scores and values, and each derived tensor carries its formula.
 * Coordinates are in the graph's own pixels; ComputeGraph.svelte draws them.
 */

export type NodeKind = 'input' | 'proj' | 'mid' | 'output';
export interface GraphNode {
	id: string;
	x: number;
	y: number;
	tex: string;
	kind: NodeKind;
	r?: number;
}
export interface GraphJoin {
	id: string;
	x: number;
	y: number;
	/** hadamard: ⊙ of its inputs; merge: inputs meet and continue; pool: a sum over tokens */
	op: 'hadamard' | 'merge' | 'pool';
}
export interface GraphEdge {
	from: string;
	to: string;
	tex?: string;
	/** Sideways bend as a fraction of the edge's length (positive bends to the edge's right). */
	bend?: number;
	/** An explicit control point, for edges that route around others. */
	via?: { x: number; y: number };
	/** Which side of the edge the label sits on. */
	side?: 1 | -1;
	labelAt?: number;
	arrowAt?: number;
	arrow?: boolean;
	/** A dashed edge: recurrence or something carried over, not computed here. */
	soft?: boolean;
}
export interface GraphNote {
	x: number;
	y: number;
	tex: string;
	align?: 'left' | 'center' | 'right';
}
export interface Graph {
	w: number;
	h: number;
	nodes: GraphNode[];
	joins: GraphJoin[];
	edges: GraphEdge[];
	notes: GraphNote[];
}

/** Scaled dot-product self-attention: pairs. */
export const PAIRWISE: Graph = {
	w: 520,
	h: 190,
	nodes: [
		{ id: 'X', x: 36, y: 100, tex: 'X', kind: 'input' },
		{ id: 'V', x: 160, y: 34, tex: 'V', kind: 'proj' },
		{ id: 'Q', x: 160, y: 104, tex: 'Q', kind: 'proj' },
		{ id: 'K', x: 160, y: 158, tex: 'K', kind: 'proj' },
		{ id: 'A', x: 284, y: 131, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 470, y: 66, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'qk', x: 226, y: 131, op: 'merge' },
		{ id: 'y', x: 392, y: 66, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V', tex: 'W_V', bend: -0.12, labelAt: 0.62 },
		{ from: 'X', to: 'Q', tex: 'W_Q', bend: 0.04, side: -1, labelAt: 0.68 },
		{ from: 'X', to: 'K', tex: 'W_K', bend: 0.14, side: 1, labelAt: 0.62 },
		{ from: 'Q', to: 'qk', bend: -0.25, arrow: false },
		{ from: 'K', to: 'qk', bend: 0.25, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'V', to: 'y', bend: -0.12, arrowAt: 0.5 },
		{ from: 'A', to: 'y', bend: 0.22 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: 284, y: 165, tex: String.raw`A_{ij} = \langle Q_i,\, K_j \rangle`, align: 'center' },
		{
			x: 420,
			y: 152,
			tex: String.raw`Y_i = \sum_{j} \operatorname{softmax}_{j}\!\big(A_{ij}/\sqrt{d}\big)\, V_j`,
			align: 'center'
		}
	]
};

/** Cubic polyattention: one query against ordered pairs of keys. */
export const CUBIC: Graph = {
	w: 560,
	h: 262,
	nodes: [
		{ id: 'X', x: 36, y: 132, tex: 'X', kind: 'input' },
		{ id: 'V1', x: 160, y: 30, tex: 'V^1', kind: 'proj' },
		{ id: 'V2', x: 160, y: 78, tex: 'V^2', kind: 'proj' },
		{ id: 'D', x: 280, y: 54, tex: 'D', kind: 'mid' },
		{ id: 'Q', x: 160, y: 136, tex: 'Q', kind: 'proj' },
		{ id: 'K1', x: 160, y: 184, tex: 'K^1', kind: 'proj' },
		{ id: 'K2', x: 160, y: 232, tex: 'K^2', kind: 'proj' },
		{ id: 'A', x: 304, y: 170, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 506, y: 110, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'vv', x: 216, y: 54, op: 'hadamard' },
		{ id: 'kk', x: 216, y: 208, op: 'hadamard' },
		{ id: 'qk', x: 250, y: 170, op: 'merge' },
		{ id: 'y', x: 418, y: 110, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V1', tex: 'W^1_V', bend: -0.1, labelAt: 0.72 },
		{ from: 'X', to: 'V2', tex: 'W^2_V', bend: -0.04, labelAt: 0.8 },
		{ from: 'X', to: 'Q', tex: 'W_Q', bend: 0.02, labelAt: 0.8 },
		{ from: 'X', to: 'K1', tex: 'W^1_K', bend: 0.06, side: 1, labelAt: 0.8 },
		{ from: 'X', to: 'K2', tex: 'W^2_K', bend: 0.12, side: 1, labelAt: 0.72 },
		{ from: 'V1', to: 'vv', bend: 0.18, arrow: false },
		{ from: 'V2', to: 'vv', bend: -0.18, arrow: false },
		{ from: 'vv', to: 'D' },
		{ from: 'K1', to: 'kk', bend: 0.18, arrow: false },
		{ from: 'K2', to: 'kk', bend: -0.18, arrow: false },
		{ from: 'Q', to: 'qk', bend: -0.2, arrow: false },
		{ from: 'kk', to: 'qk', bend: 0.2, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'D', to: 'y', bend: -0.22 },
		{ from: 'A', to: 'y', bend: 0.22 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: 280, y: 24, tex: String.raw`D_{jk} = V^1_j \odot V^2_k`, align: 'center' },
		{
			x: 304,
			y: 204,
			tex: String.raw`A_{ijk} = \langle Q_i,\, K^1_j \odot K^2_k \rangle`,
			align: 'center'
		},
		{
			x: 470,
			y: 196,
			tex: String.raw`Y_i = \sum_{j,k} \operatorname{softmax}_{jk}(A_{ijk})\, D_{jk}`,
			align: 'center'
		}
	]
};

/** Polyattention of any order N: one query against ordered N-tuples of keys. */
export const GENERAL: Graph = {
	w: 580,
	h: 326,
	nodes: [
		{ id: 'X', x: 36, y: 164, tex: 'X', kind: 'input' },
		{ id: 'V1', x: 160, y: 26, tex: 'V^1', kind: 'proj' },
		{ id: 'V2', x: 160, y: 70, tex: 'V^2', kind: 'proj' },
		{ id: 'VN', x: 160, y: 132, tex: 'V^N', kind: 'proj' },
		{ id: 'D', x: 290, y: 78, tex: 'D', kind: 'mid' },
		{ id: 'Q', x: 160, y: 190, tex: 'Q', kind: 'proj' },
		{ id: 'K1', x: 160, y: 234, tex: 'K^1', kind: 'proj' },
		{ id: 'KN', x: 160, y: 300, tex: 'K^N', kind: 'proj' },
		{ id: 'A', x: 314, y: 230, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 526, y: 150, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'vv', x: 222, y: 78, op: 'hadamard' },
		{ id: 'kk', x: 222, y: 266, op: 'hadamard' },
		{ id: 'qk', x: 258, y: 230, op: 'merge' },
		{ id: 'y', x: 432, y: 150, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V1', tex: 'W^1_V', bend: -0.1, labelAt: 0.72 },
		{ from: 'X', to: 'V2', tex: 'W^2_V', bend: -0.06, labelAt: 0.82 },
		{ from: 'X', to: 'VN', tex: 'W^N_V', bend: -0.02, labelAt: 0.82 },
		{ from: 'X', to: 'Q', tex: 'W_Q', bend: 0.02, labelAt: 0.82, side: 1 },
		{ from: 'X', to: 'K1', tex: 'W^1_K', bend: 0.06, side: 1, labelAt: 0.82 },
		{ from: 'X', to: 'KN', tex: 'W^N_K', bend: 0.1, side: 1, labelAt: 0.72 },
		{ from: 'V1', to: 'vv', bend: 0.2, arrow: false },
		{ from: 'V2', to: 'vv', bend: 0.08, arrow: false },
		{ from: 'VN', to: 'vv', bend: -0.18, arrow: false },
		{ from: 'vv', to: 'D' },
		{ from: 'K1', to: 'kk', bend: 0.18, arrow: false },
		{ from: 'KN', to: 'kk', bend: -0.18, arrow: false },
		{ from: 'Q', to: 'qk', bend: -0.2, arrow: false },
		{ from: 'kk', to: 'qk', bend: 0.2, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'D', to: 'y', bend: -0.2 },
		{ from: 'A', to: 'y', bend: 0.2 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: 160, y: 102, tex: String.raw`\vdots`, align: 'center' },
		{ x: 160, y: 268, tex: String.raw`\vdots`, align: 'center' },
		{
			x: 290,
			y: 46,
			tex: String.raw`D_{jk\cdots z} = V^1_j \odot V^2_k \odot \cdots \odot V^N_z`,
			align: 'center'
		},
		{
			x: 330,
			y: 266,
			tex: String.raw`A_{ijk\cdots z} = \langle Q_i,\, K^1_j \odot \cdots \odot K^N_z \rangle`,
			align: 'left'
		},
		{
			x: 480,
			y: 220,
			tex: String.raw`Y_i = \sum_{j,\dots,z} \operatorname{softmax}(A_{ij\cdots z})\, D_{j\cdots z}`,
			align: 'center'
		}
	]
};

/** Feynman attention: one softmax over sectors per token, rebuilt for R rounds. */
export const FEYNMAN: Graph = {
	w: 600,
	h: 250,
	nodes: [
		{ id: 'X', x: 36, y: 128, tex: 'X', kind: 'input' },
		{ id: 'v', x: 160, y: 40, tex: 'v', kind: 'proj' },
		{ id: 'q', x: 160, y: 124, tex: 'q', kind: 'proj' },
		{ id: 'u', x: 160, y: 172, tex: 'u', kind: 'proj' },
		{ id: 'w', x: 160, y: 220, tex: 'w', kind: 'proj' },
		{ id: 'pi', x: 304, y: 160, tex: String.raw`\pi`, kind: 'mid' },
		{ id: 'Phi0', x: 304, y: 64, tex: String.raw`\Phi^{r-1}`, kind: 'mid', r: 19 },
		{ id: 'Phi', x: 466, y: 108, tex: String.raw`\Phi^{r}`, kind: 'mid', r: 17 },
		{ id: 'Y', x: 562, y: 108, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'uw', x: 216, y: 196, op: 'hadamard' },
		{ id: 'quw', x: 250, y: 160, op: 'merge' },
		{ id: 'sum', x: 396, y: 108, op: 'pool' }
	],
	edges: [
		{ from: 'X', to: 'v', tex: 'W_v', bend: -0.12 },
		{ from: 'X', to: 'q', tex: 'W_q', bend: 0.02, side: -1 },
		{ from: 'X', to: 'u', tex: 'W_u', bend: 0.06, side: 1, labelAt: 0.78 },
		{ from: 'X', to: 'w', tex: 'W_w', bend: 0.12, side: 1, labelAt: 0.72 },
		{ from: 'v', to: 'Phi0', tex: String.raw`\Phi^0 = v`, bend: -0.1 },
		{ from: 'u', to: 'uw', bend: 0.18, arrow: false },
		{ from: 'w', to: 'uw', bend: -0.18, arrow: false },
		{ from: 'q', to: 'quw', bend: -0.2, arrow: false },
		{ from: 'uw', to: 'quw', bend: 0.2, arrow: false },
		{ from: 'quw', to: 'pi' },
		{ from: 'Phi0', to: 'sum', bend: -0.12 },
		{ from: 'pi', to: 'sum', bend: 0.12 },
		{ from: 'sum', to: 'Phi' },
		{
			from: 'Phi',
			to: 'Phi0',
			via: { x: 400, y: 0 },
			soft: true,
			tex: String.raw`r \to r+1`,
			labelAt: 0.5,
			side: -1
		},
		{ from: 'Phi', to: 'Y', tex: String.raw`r = R` }
	],
	notes: [
		{
			x: 240,
			y: 228,
			tex: String.raw`\pi = \operatorname{softmax}\big(\langle q_t,\, u \odot w\rangle + \mu\big)`,
			align: 'left'
		},
		{
			x: 430,
			y: 152,
			tex: String.raw`\text{leaf, hop, pair, exchange, carry}`,
			align: 'center'
		}
	]
};

/** Newton attention: phases, pooled power sums, Newton's identities, every arity read out. */
export const NEWTON: Graph = {
	w: 640,
	h: 226,
	nodes: [
		{ id: 'X', x: 36, y: 128, tex: 'X', kind: 'input' },
		{ id: 'phi', x: 150, y: 128, tex: String.raw`\phi`, kind: 'mid' },
		{ id: 'P', x: 318, y: 66, tex: 'P_j', kind: 'mid' },
		{ id: 'e', x: 448, y: 66, tex: 'e_m', kind: 'mid' },
		{ id: 'Y', x: 600, y: 128, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'pool', x: 246, y: 66, op: 'pool' },
		{ id: 'had', x: 512, y: 128, op: 'hadamard' }
	],
	edges: [
		{ from: 'X', to: 'phi', tex: String.raw`W_\theta,\, W_g` },
		{ from: 'phi', to: 'pool', tex: String.raw`\phi^{\odot j}`, bend: -0.1 },
		{ from: 'pool', to: 'P' },
		{ from: 'P', to: 'e', tex: String.raw`\text{Newton}` },
		{ from: 'e', to: 'had', bend: -0.18, arrow: false },
		{
			from: 'phi',
			to: 'had',
			tex: String.raw`\phi_q`,
			via: { x: 330, y: 196 },
			side: 1,
			arrowAt: 0.6,
			labelAt: 0.5
		},
		{ from: 'had', to: 'Y', tex: String.raw`W_o` }
	],
	notes: [
		{
			x: 150,
			y: 164,
			tex: String.raw`\phi_t = \sigma(W_g x_t)\, e^{\,i W_\theta x_t}`,
			align: 'center'
		},
		{
			x: 300,
			y: 28,
			tex: String.raw`P_j = \textstyle\sum_{t \ne q} \phi_t^{\odot j}`,
			align: 'center'
		},
		{
			x: 452,
			y: 28,
			tex: String.raw`m\, e_m = \textstyle\sum_{j} (-1)^{j-1} e_{m-j} \odot P_j`,
			align: 'center'
		},
		{ x: 512, y: 158, tex: String.raw`\text{arity } m+1`, align: 'center' },
		{
			x: 600,
			y: 172,
			tex: String.raw`Y_q = \textstyle\sum_{m<K} W^{(m)}_o\, \phi_q \odot e_m`,
			align: 'right'
		}
	]
};
