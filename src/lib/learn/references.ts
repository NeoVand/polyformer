/** The works the Learn page cites, numbered in order of first use. */
export interface Reference {
	id: string;
	authors: string;
	title: string;
	venue: string;
	year: number;
	url?: string;
}

export const REFERENCES: Reference[] = [
	{
		id: 'vaswani',
		authors: 'A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, I. Polosukhin',
		title: 'Attention is all you need',
		venue: 'Advances in Neural Information Processing Systems 30',
		year: 2017,
		url: 'https://arxiv.org/abs/1706.03762'
	},
	{
		id: 'hahn',
		authors: 'M. Hahn',
		title: 'Theoretical limitations of self-attention in neural sequence models',
		venue: 'Transactions of the Association for Computational Linguistics 8, 156–171',
		year: 2020
	},
	{
		id: 'sanford',
		authors: 'C. Sanford, D. Hsu, M. Telgarsky',
		title: 'Representational strengths and limitations of transformers',
		venue: 'Advances in Neural Information Processing Systems 36',
		year: 2023,
		url: 'https://arxiv.org/abs/2306.02896'
	},
	{
		id: 'clift',
		authors: 'J. Clift, D. Doryn, D. Murfet, J. Wallbridge',
		title: 'Logic and the 2-simplicial transformer',
		venue: 'International Conference on Learning Representations',
		year: 2020,
		url: 'https://openreview.net/forum?id=rkecJ6VFvr'
	},
	{
		id: 'roy',
		authors: 'A. Roy, T. Chou, S. S. Duvvuri, S. Chen, J. Yu, X. Wang, M. Zaheer, R. Anil',
		title: 'Fast and simplex: 2-simplicial attention in Triton',
		venue: 'arXiv:2507.02754',
		year: 2025,
		url: 'https://arxiv.org/abs/2507.02754'
	},
	{
		id: 'neo',
		authors: 'M. Mohsenvand',
		title: 'Polyformer: embracing the bitter lesson',
		venue: 'Unpublished notebook, Complex Learning Group, 11 April',
		year: 2023
	},
	{
		id: 'alman',
		authors: 'J. Alman, Z. Song',
		title: 'How to capture higher-order correlations? Generalizing matrix softmax attention to Kronecker computation',
		venue: 'International Conference on Learning Representations',
		year: 2024
	},
	{
		id: 'kozachinskiy',
		authors: 'A. Kozachinskiy, F. Urrutia, H. Jimenez, T. Steifer, G. Pizarro, M. Fuentes, F. Meza, C. Buc, C. Rojas',
		title: 'Strassen attention: unlocking compositional abilities in transformers based on a new lower bound method',
		venue: 'arXiv:2501.19215',
		year: 2025,
		url: 'https://arxiv.org/abs/2501.19215'
	},
	{
		id: 'chakrabarti',
		authors: 'S. Chakrabarti, T. Pitassi, J. Alman',
		title: 'Poly-attention: a general scheme for higher order self-attention',
		venue: 'International Conference on Learning Representations',
		year: 2026,
		url: 'https://arxiv.org/abs/2602.02422'
	},
	{
		id: 'davis',
		authors: 'B. L. Davis, D. Maclagan',
		title: 'The card game SET',
		venue: 'The Mathematical Intelligencer 25(3), 33–40',
		year: 2003
	},
	{
		id: 'dyson',
		authors: 'F. J. Dyson',
		title: 'The S matrix in quantum electrodynamics',
		venue: 'Physical Review 75, 1736',
		year: 1949,
		url: 'https://doi.org/10.1103/PhysRev.75.1736'
	},
	{
		id: 'schwinger',
		authors: 'J. Schwinger',
		title: "On the Green's functions of quantized fields. I",
		venue: 'Proceedings of the National Academy of Sciences 37, 452–455',
		year: 1951,
		url: 'https://doi.org/10.1073/pnas.37.7.452'
	},
	{
		id: 'feynman',
		authors: 'R. P. Feynman',
		title: 'Space-time approach to quantum electrodynamics',
		venue: 'Physical Review 76, 769',
		year: 1949,
		url: 'https://doi.org/10.1103/PhysRev.76.769'
	},
	{
		id: 'chakrabarti07',
		authors: 'A. Chakrabarti',
		title: 'Lower bounds for multi-player pointer jumping',
		venue: 'IEEE Conference on Computational Complexity, 33–45',
		year: 2007
	},
	{
		id: 'ellis',
		authors: 'J. P. Ellis',
		title: 'TikZ-Feynman: Feynman diagrams with TikZ',
		venue: 'arXiv:1601.05437',
		year: 2016,
		url: 'https://arxiv.org/abs/1601.05437'
	},
	{
		id: 'jaxjs',
		authors: 'E. Zhang',
		title: 'jax-js: JAX-style arrays, autodiff and jit in the browser',
		venue: 'Software, github.com/ekzhang/jax-js',
		year: 2025,
		url: 'https://github.com/ekzhang/jax-js'
	}
];

/** Citation number (1-based) for a reference id. */
export const cite = (id: string) => REFERENCES.findIndex((r) => r.id === id) + 1;
