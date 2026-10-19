/**
 * Computation graphs for every operator the app discusses, after the figure in the original
 * Polyformer notebook (April 2023): the input X fans out through projections, Hadamard products
 * and merges build the scores and values, and each derived tensor carries its formula.
 * Coordinates are in the graph's own pixels; ComputeGraph.svelte draws them.
 */

export type NodeKind = 'input' | 'proj' | 'mid' | 'output' | 'op';
export interface GraphNode {
	id: string;
	x: number;
	y: number;
	tex: string;
	/** An `op` is an operation drawn as a box; every other kind is a tensor, a circle. */
	kind: NodeKind;
	r?: number;
	/** An op box's width (its height is fixed). */
	w?: number;
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
	/**
	 * Direction the edge leaves its source, in degrees (0 right, 90 up), as TikZ's `out`.
	 * Defaults to 0, or for the input's fan-out to most of the straight line's angle.
	 */
	out?: number;
	/** Direction of travel as it arrives (0 rightward, −90 coming down onto the target). */
	enter?: number;
	/** Scales how far the curve keeps its end directions. */
	loose?: number;
	/** Explicit lengths for which each end keeps its direction, for arches drawn by hand. */
	reach?: [number, number];
	/** Which side of the edge the label sits on: −1 left of travel (above a rightward edge). */
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

// Columns shared by every graph, so the same roles line up from figure to figure.
const X0 = 40;
const PROJ = 165;
const HAD = 235;
const MERGE = 282;
const MID = 330;

/** Scaled dot-product self-attention: pairs. X and Y share a row. */
export const PAIRWISE: Graph = {
	w: 630,
	h: 176,
	nodes: [
		{ id: 'X', x: X0, y: 92, tex: 'X', kind: 'input' },
		{ id: 'V', x: PROJ, y: 30, tex: 'V', kind: 'proj' },
		{ id: 'Q', x: PROJ, y: 92, tex: 'Q', kind: 'proj' },
		{ id: 'K', x: PROJ, y: 142, tex: 'K', kind: 'proj' },
		{ id: 'A', x: MID, y: 117, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 560, y: 92, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'qk', x: MERGE, y: 117, op: 'merge' },
		{ id: 'y', x: 470, y: 92, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V', tex: 'W_V', labelAt: 0.74 },
		{ from: 'X', to: 'Q', tex: 'W_Q', labelAt: 0.62 },
		{ from: 'X', to: 'K', tex: 'W_K', side: 1, labelAt: 0.74 },
		{ from: 'Q', to: 'qk', enter: -55, arrow: false },
		{ from: 'K', to: 'qk', enter: 55, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'V', to: 'y', enter: -50, arrowAt: 0.45 },
		{ from: 'A', to: 'y', enter: 50 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: MID, y: 152, tex: String.raw`A_{ij} = \langle Q_i,\, K_j \rangle`, align: 'center' },
		{
			x: 560,
			y: 62,
			tex: String.raw`Y_i = \sum_{j} \operatorname{softmax}_{j}(A_{ij})\, V_j`,
			align: 'center'
		}
	]
};

/** Cubic polyattention: one query against ordered pairs of keys. */
export const CUBIC: Graph = {
	w: 630,
	h: 250,
	nodes: [
		{ id: 'X', x: X0, y: 107, tex: 'X', kind: 'input' },
		{ id: 'V1', x: PROJ, y: 26, tex: 'V^1', kind: 'proj' },
		{ id: 'V2', x: PROJ, y: 72, tex: 'V^2', kind: 'proj' },
		{ id: 'D', x: MID, y: 49, tex: 'D', kind: 'mid' },
		{ id: 'Q', x: PROJ, y: 130, tex: 'Q', kind: 'proj' },
		{ id: 'K1', x: PROJ, y: 176, tex: 'K^1', kind: 'proj' },
		{ id: 'K2', x: PROJ, y: 222, tex: 'K^2', kind: 'proj' },
		{ id: 'A', x: MID, y: 165, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 560, y: 107, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'vv', x: HAD, y: 49, op: 'hadamard' },
		{ id: 'kk', x: HAD, y: 199, op: 'hadamard' },
		{ id: 'qk', x: MERGE, y: 165, op: 'merge' },
		{ id: 'y', x: 470, y: 107, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V1', tex: 'W^1_V', labelAt: 0.76 },
		{ from: 'X', to: 'V2', tex: 'W^2_V', labelAt: 0.76 },
		{ from: 'X', to: 'Q', tex: 'W_Q', labelAt: 0.76 },
		{ from: 'X', to: 'K1', tex: 'W^1_K', labelAt: 0.76 },
		{ from: 'X', to: 'K2', tex: 'W^2_K', labelAt: 0.76 },
		{ from: 'V1', to: 'vv', enter: -55, arrow: false },
		{ from: 'V2', to: 'vv', enter: 55, arrow: false },
		{ from: 'vv', to: 'D' },
		{ from: 'K1', to: 'kk', enter: -55, arrow: false },
		{ from: 'K2', to: 'kk', enter: 55, arrow: false },
		{ from: 'Q', to: 'qk', enter: -55, arrow: false },
		{ from: 'kk', to: 'qk', enter: 55, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'D', to: 'y', enter: -50 },
		{ from: 'A', to: 'y', enter: 50 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: MID, y: 18, tex: String.raw`D_{jk} = V^1_j \odot V^2_k`, align: 'center' },
		{
			x: MID,
			y: 198,
			tex: String.raw`A_{ijk} = \langle Q_i,\, K^1_j \odot K^2_k \rangle`,
			align: 'center'
		},
		{
			x: 626,
			y: 77,
			tex: String.raw`Y_i = \sum_{j,k} \operatorname{softmax}_{jk}(A_{ijk})\, D_{jk}`,
			align: 'right'
		}
	]
};

/** Polyattention of any order N: one query against ordered N-tuples of keys. */
export const GENERAL: Graph = {
	w: 640,
	h: 330,
	nodes: [
		{ id: 'X', x: X0, y: 158, tex: 'X', kind: 'input' },
		{ id: 'V1', x: PROJ, y: 26, tex: 'V^1', kind: 'proj' },
		{ id: 'V2', x: PROJ, y: 70, tex: 'V^2', kind: 'proj' },
		{ id: 'VN', x: PROJ, y: 136, tex: 'V^N', kind: 'proj' },
		{ id: 'D', x: MID, y: 81, tex: 'D', kind: 'mid' },
		{ id: 'Q', x: PROJ, y: 196, tex: 'Q', kind: 'proj' },
		{ id: 'K1', x: PROJ, y: 240, tex: 'K^1', kind: 'proj' },
		{ id: 'KN', x: PROJ, y: 306, tex: 'K^N', kind: 'proj' },
		{ id: 'A', x: MID, y: 235, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 565, y: 158, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'vv', x: HAD, y: 81, op: 'hadamard' },
		{ id: 'kk', x: HAD, y: 273, op: 'hadamard' },
		{ id: 'qk', x: MERGE, y: 235, op: 'merge' },
		{ id: 'y', x: 475, y: 158, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V1', tex: 'W^1_V', labelAt: 0.78 },
		{ from: 'X', to: 'V2', tex: 'W^2_V', labelAt: 0.78 },
		{ from: 'X', to: 'VN', tex: 'W^N_V', labelAt: 0.78 },
		{ from: 'X', to: 'Q', tex: 'W_Q', labelAt: 0.78 },
		{ from: 'X', to: 'K1', tex: 'W^1_K', labelAt: 0.78 },
		{ from: 'X', to: 'KN', tex: 'W^N_K', labelAt: 0.78 },
		{ from: 'V1', to: 'vv', enter: -60, arrow: false },
		{ from: 'V2', to: 'vv', enter: -30, arrow: false },
		{ from: 'VN', to: 'vv', enter: 55, arrow: false },
		{ from: 'vv', to: 'D' },
		{ from: 'K1', to: 'kk', enter: -50, arrow: false },
		{ from: 'KN', to: 'kk', enter: 55, arrow: false },
		{ from: 'Q', to: 'qk', enter: -55, arrow: false },
		{ from: 'kk', to: 'qk', enter: 55, arrow: false },
		{ from: 'qk', to: 'A' },
		{ from: 'D', to: 'y', enter: -50 },
		{ from: 'A', to: 'y', enter: 50 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: PROJ, y: 103, tex: String.raw`\vdots`, align: 'center' },
		{ x: PROJ, y: 273, tex: String.raw`\vdots`, align: 'center' },
		{
			x: MID,
			y: 48,
			tex: String.raw`D_{jk\cdots z} = V^1_j \odot V^2_k \odot \cdots \odot V^N_z`,
			align: 'center'
		},
		{
			x: 262,
			y: 272,
			tex: String.raw`A_{ijk\cdots z} = \langle Q_i,\, K^1_j \odot \cdots \odot K^N_z \rangle`,
			align: 'left'
		},
		{
			x: 636,
			y: 126,
			tex: String.raw`Y_i = \sum_{j,\dots,z} \operatorname{softmax}(A_{ij\cdots z})\, D_{j\cdots z}`,
			align: 'right'
		}
	]
};

/** Feynman attention: one softmax over sectors per token, rebuilt for R rounds. */
export const FEYNMAN: Graph = {
	w: 600,
	h: 252,
	nodes: [
		{ id: 'X', x: X0, y: 115, tex: 'X', kind: 'input' },
		{ id: 'v', x: PROJ, y: 56, tex: 'v', kind: 'proj' },
		{ id: 'q', x: PROJ, y: 140, tex: 'q', kind: 'proj' },
		{ id: 'u', x: PROJ, y: 186, tex: 'u', kind: 'proj' },
		{ id: 'w', x: PROJ, y: 232, tex: 'w', kind: 'proj' },
		{ id: 'pi', x: MID, y: 175, tex: String.raw`\pi`, kind: 'mid' },
		{ id: 'Phi0', x: MID, y: 56, tex: String.raw`\Phi^{r-1}`, kind: 'mid', r: 19 },
		{ id: 'Phi', x: 512, y: 115, tex: String.raw`\Phi^{r}`, kind: 'mid', r: 17 },
		{ id: 'Y', x: 578, y: 115, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'uw', x: HAD, y: 209, op: 'hadamard' },
		{ id: 'quw', x: MERGE, y: 175, op: 'merge' },
		{ id: 'sum', x: 440, y: 115, op: 'pool' }
	],
	edges: [
		{ from: 'X', to: 'v', tex: 'W_v', labelAt: 0.78 },
		{ from: 'X', to: 'q', tex: 'W_q', labelAt: 0.78 },
		{ from: 'X', to: 'u', tex: 'W_u', labelAt: 0.78 },
		{ from: 'X', to: 'w', tex: 'W_w', labelAt: 0.78 },
		{ from: 'v', to: 'Phi0', tex: String.raw`\Phi^0 = v`, labelAt: 0.45 },
		{ from: 'u', to: 'uw', enter: -55, arrow: false },
		{ from: 'w', to: 'uw', enter: 55, arrow: false },
		{ from: 'q', to: 'quw', enter: -55, arrow: false },
		{ from: 'uw', to: 'quw', enter: 55, arrow: false },
		{ from: 'quw', to: 'pi' },
		{ from: 'Phi0', to: 'sum', enter: -50 },
		{ from: 'pi', to: 'sum', enter: 50 },
		{ from: 'sum', to: 'Phi' },
		{
			from: 'Phi',
			to: 'Phi0',
			out: 150,
			enter: 210,
			reach: [64, 64],
			soft: true,
			arrowAt: 0.5
		},
		{ from: 'Phi', to: 'Y', tex: String.raw`r = R` }
	],
	notes: [
		{ x: 410, y: 26, tex: String.raw`r \to r+1`, align: 'center' },
		{
			x: 262,
			y: 236,
			tex: String.raw`\pi = \operatorname{softmax}\big(\langle q_t,\, u \odot w\rangle + \mu\big)`,
			align: 'left'
		},
		{
			x: 512,
			y: 150,
			tex: String.raw`\text{leaf, hop, pair, exchange, carry}`,
			align: 'center'
		}
	]
};

/** Newton attention: phases, pooled power sums, Newton's identities, every arity read out. */
export const NEWTON: Graph = {
	w: 660,
	h: 206,
	nodes: [
		{ id: 'X', x: X0, y: 128, tex: 'X', kind: 'input' },
		{ id: 'phi', x: 150, y: 128, tex: String.raw`\phi`, kind: 'mid' },
		{ id: 'P', x: 310, y: 56, tex: 'P_j', kind: 'mid' },
		{ id: 'newton', x: 402, y: 56, tex: String.raw`\text{Newton}`, kind: 'op', w: 66 },
		{ id: 'e', x: 494, y: 56, tex: 'e_m', kind: 'mid' },
		{ id: 'Y', x: 620, y: 128, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'pool', x: 238, y: 56, op: 'pool' },
		{ id: 'had', x: 552, y: 128, op: 'hadamard' }
	],
	edges: [
		{ from: 'X', to: 'phi', tex: String.raw`W_\theta,\, W_g` },
		{ from: 'phi', to: 'pool', tex: String.raw`\phi^{\odot j}`, labelAt: 0.4 },
		{ from: 'pool', to: 'P' },
		{ from: 'P', to: 'newton' },
		{ from: 'newton', to: 'e' },
		{ from: 'e', to: 'had', enter: -90, arrow: false },
		{ from: 'phi', to: 'had', tex: String.raw`\phi_q`, side: 1, arrowAt: 0.5, labelAt: 0.5 },
		{ from: 'had', to: 'Y', tex: String.raw`\alpha_m,\, W_o` }
	],
	notes: [
		{
			x: 150,
			y: 164,
			tex: String.raw`\phi_t = \sigma(W_g x_t)\, e^{\,i W_\theta x_t}`,
			align: 'center'
		},
		{
			x: 274,
			y: 18,
			tex: String.raw`P_j = \textstyle\sum_{t \ne q} \phi_t^{\odot j}`,
			align: 'center'
		},
		{
			x: 494,
			y: 18,
			tex: String.raw`m\, e_m = \textstyle\sum_{j} (-1)^{j-1} e_{m-j} \odot P_j`,
			align: 'center'
		},
		{ x: 552, y: 156, tex: String.raw`\text{arity } m+1`, align: 'center' },
		{
			x: 652,
			y: 186,
			tex: String.raw`Y_q = \textstyle\sum_{m<K} \alpha_m \odot W_o\, \nu(\phi_q \odot e_m)`,
			align: 'right'
		}
	]
};
