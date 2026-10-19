/** The works the report cites, in order of first use. */
import type { Reference } from '#lib/learn/references.ts';

export const BIB: Reference[] = [
	{
		id: 'vaswani',
		authors:
			'A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, I. Polosukhin',
		title: 'Attention is all you need',
		venue: 'NeurIPS',
		year: 2017,
		url: 'https://arxiv.org/abs/1706.03762'
	},
	{
		id: 'clift',
		authors: 'J. Clift, D. Doryn, D. Murfet, J. Wallbridge',
		title: 'Logic and the 2-simplicial transformer',
		venue: 'ICLR',
		year: 2020,
		url: 'https://arxiv.org/abs/1909.00668'
	},
	{
		id: 'sanford23',
		authors: 'C. Sanford, D. Hsu, M. Telgarsky',
		title: 'Representational strengths and limitations of transformers',
		venue: 'NeurIPS',
		year: 2023,
		url: 'https://arxiv.org/abs/2306.02896'
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
		id: 'kozachinskiy',
		authors:
			'A. Kozachinskiy, F. Urrutia, H. Jimenez, T. Steifer, G. Pizarro, M. Fuentes, F. Meza, C. B. Calderon, C. Rojas',
		title: 'Strassen attention, split VC dimension and compositionality in transformers',
		venue: 'NeurIPS',
		year: 2025,
		url: 'https://arxiv.org/abs/2501.19215'
	},
	{
		id: 'chakrabarti',
		authors: 'S. Chakrabarti, T. Pitassi, J. Alman',
		title: 'Poly-attention: a general scheme for higher-order self-attention',
		venue: 'ICLR',
		year: 2026,
		url: 'https://arxiv.org/abs/2602.02422'
	},
	{
		id: 'alman',
		authors: 'J. Alman, Z. Song',
		title:
			'How to capture higher-order correlations? Generalizing matrix softmax attention to Kronecker computation',
		venue: 'ICLR',
		year: 2024,
		url: 'https://arxiv.org/abs/2310.04064'
	},
	{
		id: 'abbe',
		authors: 'E. Abbe, E. Boix-Adserà, T. Misiakiewicz',
		title: 'SGD learning on neural networks: leap complexity and saddle-to-saddle dynamics',
		venue: 'COLT',
		year: 2023,
		url: 'https://arxiv.org/abs/2302.11055'
	},
	{
		id: 'drozdov',
		authors: 'A. Drozdov, P. Verga, M. Yadav, M. Iyyer, A. McCallum',
		title: 'Unsupervised latent tree induction with deep inside-outside recursive autoencoders',
		venue: 'NAACL',
		year: 2019,
		url: 'https://arxiv.org/abs/1904.02142'
	},
	{
		id: 'dussolle',
		authors: 'A. Dussolle, P. Liò',
		title: 'How smoothing is N-simplicial attention?',
		venue: 'arXiv:2512.15600',
		year: 2025,
		url: 'https://arxiv.org/abs/2512.15600'
	},
	{
		id: 'homa',
		authors: 'S. Amiraslani, X. Gao',
		title:
			'Beyond pairwise attention: higher-order modular attention for efficient sequence learning',
		venue: 'arXiv:2603.11133',
		year: 2026,
		url: 'https://arxiv.org/abs/2603.11133'
	},
	{
		id: 'nexus',
		authors: 'H. Chen, C. Zhu, K. Han, Y. Tian, Y. Liang, T. Guo, X. Chen, D. Tao, Y. Wang',
		title: 'Nexus: higher-order attention mechanisms in transformers',
		venue: 'arXiv:2512.03377',
		year: 2025,
		url: 'https://arxiv.org/abs/2512.03377'
	},
	{
		id: 'bergen',
		authors: 'L. Bergen, T. J. O’Donnell, D. Bahdanau',
		title: 'Systematic generalization with edge transformers',
		venue: 'NeurIPS',
		year: 2021,
		url: 'https://arxiv.org/abs/2112.00578'
	},
	{
		id: 'floydnet',
		authors: 'J. Yu, M. Zeng, Q. Ye',
		title: 'FloydNet: a learning paradigm for global relational reasoning',
		venue: 'arXiv:2601.19094',
		year: 2026,
		url: 'https://arxiv.org/abs/2601.19094'
	},
	{
		id: 'zaheer',
		authors: 'M. Zaheer, S. Kottur, S. Ravanbakhsh, B. Poczos, R. Salakhutdinov, A. Smola',
		title: 'Deep sets',
		venue: 'NeurIPS',
		year: 2017,
		url: 'https://arxiv.org/abs/1703.06114'
	},
	{
		id: 'wagstaff',
		authors: 'E. Wagstaff, F. Fuchs, M. Engelcke, I. Posner, M. A. Osborne',
		title: 'On the limitations of representing functions on sets',
		venue: 'ICML',
		year: 2019,
		url: 'https://arxiv.org/abs/1901.09006'
	},
	{
		id: 'nanda',
		authors: 'N. Nanda, L. Chan, T. Lieberum, J. Smith, J. Steinhardt',
		title: 'Progress measures for grokking via mechanistic interpretability',
		venue: 'ICLR',
		year: 2023,
		url: 'https://arxiv.org/abs/2301.05217'
	},
	{
		id: 'alon',
		authors: 'N. Alon, R. Yuster, U. Zwick',
		title: 'Color-coding',
		venue: 'Journal of the ACM 42(4)',
		year: 1995
	},
	{
		id: 'dehghani',
		authors: 'M. Dehghani, S. Gouws, O. Vinyals, J. Uszkoreit, Ł. Kaiser',
		title: 'Universal transformers',
		venue: 'ICLR',
		year: 2019,
		url: 'https://arxiv.org/abs/1807.03819'
	},
	{
		id: 'sanford24',
		authors: 'C. Sanford, D. Hsu, M. Telgarsky',
		title: 'Transformers, parallel computation, and logarithmic depth',
		venue: 'ICML',
		year: 2024,
		url: 'https://arxiv.org/abs/2402.09268'
	},
	{
		id: 'velickovic',
		authors:
			'P. Veličković, A. P. Badia, D. Budden, R. Pascanu, A. Banino, M. Dashevskiy, R. Hadsell, C. Blundell',
		title: 'The CLRS algorithmic reasoning benchmark',
		venue: 'ICML',
		year: 2022,
		url: 'https://arxiv.org/abs/2205.15659'
	},
	{
		id: 'hla',
		authors: 'Y. Zhang, Z. Qin, M. Wang, Q. Gu',
		title: 'Higher-order linear attention',
		venue: 'arXiv:2510.27258',
		year: 2025,
		url: 'https://arxiv.org/abs/2510.27258'
	},
	{
		id: 'janossy',
		authors: 'R. L. Murphy, B. Srinivasan, V. Rao, B. Ribeiro',
		title:
			'Janossy pooling: learning deep permutation-invariant functions for variable-size inputs',
		venue: 'ICLR',
		year: 2019,
		url: 'https://arxiv.org/abs/1811.01900'
	}
];
