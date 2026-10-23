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

/**
 * Holonomy attention: per-token rotations, ordered products over every group that contains the
 * reading token, computed from a left-to-right and a right-to-left running product.
 */
export const HOLONOMY: Graph = {
	w: 690,
	h: 236,
	nodes: [
		{ id: 'X', x: X0, y: 118, tex: 'X', kind: 'input' },
		{ id: 'M', x: 140, y: 118, tex: 'M', kind: 'mid' },
		{ id: 'scanL', x: 252, y: 48, tex: String.raw`\text{scan}\rightarrow`, kind: 'op', w: 66 },
		{ id: 'L', x: 340, y: 48, tex: 'L_a', kind: 'mid' },
		{ id: 'scanR', x: 252, y: 188, tex: String.raw`\leftarrow\text{scan}`, kind: 'op', w: 66 },
		{ id: 'R', x: 340, y: 188, tex: 'R_b', kind: 'mid' },
		{ id: 'prod', x: 458, y: 118, tex: String.raw`L_a\, M_i\, R_b`, kind: 'op', w: 92 },
		{ id: 'F', x: 585, y: 118, tex: 'F_r', kind: 'mid' },
		{ id: 'Y', x: 655, y: 118, tex: 'Y', kind: 'output' }
	],
	joins: [{ id: 'sum', x: 530, y: 118, op: 'pool' }],
	edges: [
		{ from: 'X', to: 'M', tex: String.raw`W_A,\, w_g` },
		{ from: 'M', to: 'scanL', out: 90, enter: 0 },
		{ from: 'M', to: 'scanR', out: -90, enter: 0 },
		{ from: 'scanL', to: 'L' },
		{ from: 'scanR', to: 'R' },
		{ from: 'M', to: 'prod', tex: 'M_i', labelAt: 0.42 },
		{ from: 'L', to: 'prod', enter: -90 },
		{ from: 'R', to: 'prod', enter: 90 },
		{ from: 'prod', to: 'sum' },
		{ from: 'sum', to: 'F' },
		{ from: 'F', to: 'Y', tex: String.raw`\alpha_r,\, W_o` }
	],
	notes: [
		{ x: 126, y: 154, tex: String.raw`M_t = g_t\, e^{A_t}`, align: 'right' },
		{
			x: 300,
			y: 16,
			tex: String.raw`L_a(t) = L_a(t{-}1) + L_{a-1}(t{-}1)\, M_t`,
			align: 'center'
		},
		{
			x: 300,
			y: 222,
			tex: String.raw`R_b(t) = R_b(t{+}1) + M_t\, R_{b-1}(t{+}1)`,
			align: 'center'
		},
		{
			x: 686,
			y: 82,
			tex: String.raw`F_r(i) = \textstyle\sum_{a+b=r-1} L_a(i)\, M_i\, R_b(i)`,
			align: 'right'
		},
		{
			x: 686,
			y: 154,
			tex: String.raw`Y_i = \textstyle\sum_{r \le K} \alpha_r \odot W_o \operatorname{vec} F_r(i)`,
			align: 'right'
		}
	]
};

/**
 * Attention in carried frames (LOOPS): every token turns a frame by a move computed from its
 * content, and a query compares a key through the rotation accumulated between them.
 */
export const FRAMES: Graph = {
	w: 690,
	h: 268,
	nodes: [
		{ id: 'X', x: X0, y: 118, tex: 'X', kind: 'input' },
		{ id: 'V', x: PROJ, y: 36, tex: 'V', kind: 'proj' },
		{ id: 'Q', x: PROJ, y: 118, tex: 'Q', kind: 'proj' },
		{ id: 'K', x: PROJ, y: 164, tex: 'K', kind: 'proj' },
		{ id: 'M', x: PROJ, y: 222, tex: 'M_t', kind: 'proj' },
		{ id: 'scan', x: 250, y: 222, tex: String.raw`\text{scan}`, kind: 'op', w: 54 },
		{ id: 'F', x: 330, y: 222, tex: 'F_t', kind: 'mid' },
		{ id: 'hol', x: 425, y: 222, tex: String.raw`F_i^{\top} F_j`, kind: 'op', w: 74 },
		{ id: 'A', x: 545, y: 141, tex: 'A', kind: 'mid' },
		{ id: 'Y', x: 655, y: 118, tex: 'Y', kind: 'output' }
	],
	joins: [
		{ id: 'qk', x: 250, y: 141, op: 'merge' },
		{ id: 's', x: 490, y: 141, op: 'merge' },
		{ id: 'y', x: 600, y: 118, op: 'merge' }
	],
	edges: [
		{ from: 'X', to: 'V', tex: 'W_V', labelAt: 0.74 },
		{ from: 'X', to: 'Q', tex: 'W_Q', labelAt: 0.62 },
		{ from: 'X', to: 'K', tex: 'W_K', side: 1, labelAt: 0.74 },
		{ from: 'X', to: 'M', tex: String.raw`W_M,\, w_f`, side: 1, labelAt: 0.74 },
		{ from: 'Q', to: 'qk', enter: -55, arrow: false },
		{ from: 'K', to: 'qk', enter: 55, arrow: false },
		{ from: 'qk', to: 's', arrowAt: 0.5 },
		{ from: 'M', to: 'scan' },
		{ from: 'scan', to: 'F' },
		{ from: 'F', to: 'hol' },
		{ from: 'hol', to: 's', enter: 90, arrow: false },
		{ from: 's', to: 'A' },
		{ from: 'V', to: 'y', enter: -50, arrowAt: 0.45 },
		{ from: 'A', to: 'y', enter: 50 },
		{ from: 'y', to: 'Y' }
	],
	notes: [
		{ x: 330, y: 188, tex: String.raw`F_t = M_1 M_2 \cdots M_t`, align: 'center' },
		{
			x: 686,
			y: 252,
			tex: String.raw`A_{ij} = q_i^{\top} F_i^{\top} F_j\, k_j + \textstyle\sum_{j<s\le i} \log f_s`,
			align: 'right'
		},
		{
			x: 686,
			y: 12,
			tex: String.raw`Y_i = \textstyle\sum_{j \le i} \operatorname{softmax}_j(A_{ij})\, V_j`,
			align: 'right'
		}
	]
};

/**
 * The event model (EVENTS): recurrent layers over tokens, attention over the events a router
 * marks, and the event outputs handed back to the tokens they cover.
 */
export const EVENTS: Graph = {
	w: 770,
	h: 226,
	nodes: [
		{ id: 'X', x: X0, y: 52, tex: 'X', kind: 'input' },
		{ id: 'enc', x: 120, y: 52, tex: String.raw`\text{GDN}\,{\times}2`, kind: 'op', w: 70 },
		{ id: 'h', x: 205, y: 52, tex: 'h_t', kind: 'mid' },
		{ id: 'chunk', x: 280, y: 160, tex: String.raw`\text{chunk}`, kind: 'op', w: 60 },
		{ id: 'z', x: 352, y: 160, tex: 'z_e', kind: 'mid' },
		{
			id: 'main',
			x: 450,
			y: 160,
			tex: String.raw`\text{attention}\,{\times}6`,
			kind: 'op',
			w: 100
		},
		{ id: 'ye', x: 545, y: 160, tex: 'y_e', kind: 'mid' },
		{ id: 'dechunk', x: 615, y: 160, tex: String.raw`\text{dechunk}`, kind: 'op', w: 70 },
		{ id: 'dec', x: 680, y: 52, tex: String.raw`\text{GDN}\,{\times}2`, kind: 'op', w: 66 },
		{ id: 'Y', x: 742, y: 52, tex: 'Y', kind: 'output' }
	],
	joins: [{ id: 'add', x: 615, y: 52, op: 'merge' }],
	edges: [
		{ from: 'X', to: 'enc' },
		{ from: 'enc', to: 'h' },
		{ from: 'h', to: 'add' },
		{ from: 'h', to: 'chunk', out: -90, enter: 0 },
		{ from: 'chunk', to: 'z' },
		{ from: 'z', to: 'main' },
		{ from: 'main', to: 'ye' },
		{ from: 'ye', to: 'dechunk' },
		{ from: 'dechunk', to: 'add', out: 90, enter: 90, arrow: false },
		{ from: 'add', to: 'dec' },
		{ from: 'dec', to: 'Y' }
	],
	notes: [
		{
			x: 450,
			y: 130,
			tex: String.raw`\text{frames and forget gate, over events}`,
			align: 'center'
		},
		{
			x: 232,
			y: 194,
			tex: String.raw`p_t = \tfrac12\big(1 - \cos(W_q h_t,\, W_k h_{t-1})\big)`,
			align: 'left'
		},
		{ x: 232, y: 214, tex: String.raw`b_t = [\,p_t \ge \tfrac12\,]`, align: 'left' },
		{
			x: 615,
			y: 196,
			tex: String.raw`\bar y_e = p_e\, y_e + (1 - p_e)\, \bar y_{e-1}`,
			align: 'center'
		},
		{ x: 680, y: 18, tex: String.raw`\text{state cut where } b_t = 1`, align: 'center' }
	]
};

/**
 * The per-event recurrence with the Nerode term (EXACTNESS, LEAN_S1): two equivalent histories
 * run through one recurrence with shared weights; the slot attends to each event's tokens and an
 * MLP updates it; the readout reads the slot through LayerNorm, and the term compares the two
 * readout views.
 */
export const NERODE: Graph = {
	w: 810,
	h: 330,
	nodes: [
		{ id: 'wu0', x: X0, y: 70, tex: 'w_{t-1}', kind: 'mid', r: 18 },
		{ id: 'u', x: X0, y: 126, tex: 'u_t', kind: 'input' },
		{ id: 'Ku', x: 150, y: 108, tex: 'K', kind: 'proj' },
		{ id: 'Vu', x: 150, y: 144, tex: 'V', kind: 'proj' },
		{ id: 'attu', x: 240, y: 70, tex: String.raw`\text{attend}`, kind: 'op', w: 60 },
		{ id: 'au', x: 318, y: 70, tex: 'a_t', kind: 'mid' },
		{ id: 'mlpu', x: 386, y: 70, tex: String.raw`\text{MLP}`, kind: 'op', w: 50 },
		{ id: 'wu1', x: 456, y: 70, tex: 'w_t', kind: 'mid' },
		{ id: 'lnu', x: 520, y: 70, tex: String.raw`\text{LN}`, kind: 'op', w: 40 },
		{ id: 'zu', x: 584, y: 70, tex: 'z_u', kind: 'mid' },
		{ id: 'Y', x: 770, y: 70, tex: 'Y', kind: 'output' },
		{ id: 'wv0', x: X0, y: 262, tex: 'w_{s-1}', kind: 'mid', r: 18 },
		{ id: 'v', x: X0, y: 206, tex: 'v_s', kind: 'input' },
		{ id: 'Kv', x: 150, y: 224, tex: 'K', kind: 'proj' },
		{ id: 'Vv', x: 150, y: 188, tex: 'V', kind: 'proj' },
		{ id: 'attv', x: 240, y: 262, tex: String.raw`\text{attend}`, kind: 'op', w: 60 },
		{ id: 'av', x: 318, y: 262, tex: 'a_s', kind: 'mid' },
		{ id: 'mlpv', x: 386, y: 262, tex: String.raw`\text{MLP}`, kind: 'op', w: 50 },
		{ id: 'wv1', x: 456, y: 262, tex: 'w_s', kind: 'mid' },
		{ id: 'lnv', x: 520, y: 262, tex: String.raw`\text{LN}`, kind: 'op', w: 40 },
		{ id: 'zv', x: 584, y: 262, tex: 'z_v', kind: 'mid' },
		{ id: 'dist', x: 700, y: 166, tex: String.raw`1 - \cos`, kind: 'op', w: 60 },
		{ id: 'L', x: 770, y: 166, tex: String.raw`\mathcal L_N`, kind: 'output', r: 17 }
	],
	joins: [{ id: 'dm', x: 640, y: 166, op: 'merge' }],
	edges: [
		{ from: 'wu0', to: 'attu' },
		{ from: 'u', to: 'Ku', tex: 'W_K', labelAt: 0.74 },
		{ from: 'u', to: 'Vu', tex: 'W_V', side: 1, labelAt: 0.74 },
		{ from: 'Ku', to: 'attu', enter: 70, arrow: false },
		{ from: 'Vu', to: 'attu', enter: 110, arrow: false },
		{ from: 'attu', to: 'au' },
		{ from: 'au', to: 'mlpu' },
		{ from: 'mlpu', to: 'wu1' },
		{ from: 'wu1', to: 'lnu' },
		{ from: 'lnu', to: 'zu' },
		{ from: 'zu', to: 'Y', tex: 'W_o', labelAt: 0.5 },
		{ from: 'wu1', to: 'wu0', out: 120, enter: 240, reach: [60, 60], soft: true, arrowAt: 0.5 },
		{ from: 'wv0', to: 'attv' },
		{ from: 'v', to: 'Kv', tex: 'W_K', side: 1, labelAt: 0.74 },
		{ from: 'v', to: 'Vv', tex: 'W_V', labelAt: 0.74 },
		{ from: 'Kv', to: 'attv', enter: -70, arrow: false },
		{ from: 'Vv', to: 'attv', enter: -110, arrow: false },
		{ from: 'attv', to: 'av' },
		{ from: 'av', to: 'mlpv' },
		{ from: 'mlpv', to: 'wv1' },
		{ from: 'wv1', to: 'lnv' },
		{ from: 'lnv', to: 'zv' },
		{
			from: 'wv1',
			to: 'wv0',
			out: -120,
			enter: -240,
			reach: [60, 60],
			soft: true,
			arrowAt: 0.5
		},
		{ from: 'zu', to: 'dm', out: -50, enter: -55, arrow: false },
		{ from: 'zv', to: 'dm', out: 50, enter: 55, arrow: false },
		{ from: 'dm', to: 'dist' },
		{ from: 'dist', to: 'L' }
	],
	notes: [
		{ x: 250, y: 34, tex: String.raw`t \to t+1`, align: 'center' },
		{ x: 250, y: 298, tex: String.raw`s \to s+1`, align: 'center' },
		{ x: X0, y: 166, tex: String.raw`u \sim v`, align: 'center' },
		{
			x: 300,
			y: 157,
			tex: String.raw`a_t = \operatorname{softmax}(q K^{\top})\, V,\quad q = \mathrm{LN}(w_{t-1})`,
			align: 'left'
		},
		{
			x: 300,
			y: 177,
			tex: String.raw`w_t = w_{t-1} + a_t + \operatorname{MLP}\big(\mathrm{LN}(w_{t-1} + a_t)\big)\text{, four ticks}`,
			align: 'left'
		},
		{ x: 584, y: 40, tex: String.raw`z_u = \mathrm{LN}(w_t)`, align: 'center' },
		{ x: 584, y: 292, tex: String.raw`z_v = \mathrm{LN}(w_s)`, align: 'center' },
		{
			x: 800,
			y: 100,
			tex: String.raw`\text{cross-entropy of } Y \text{ against the state}`,
			align: 'right'
		},
		{ x: 800, y: 196, tex: String.raw`\mathcal L_N = \mu\,(1 - \cos(z_u, z_v))`, align: 'right' },
		{ x: 800, y: 216, tex: String.raw`\text{over sampled pairs } u \sim v`, align: 'right' }
	]
};
