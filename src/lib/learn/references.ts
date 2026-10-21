/** Every work the paper cites. Citations are numbered by position in this list. */
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
		authors:
			'A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, I. Polosukhin',
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
		title:
			'How to capture higher-order correlations? Generalizing matrix softmax attention to Kronecker computation',
		venue: 'International Conference on Learning Representations',
		year: 2024
	},
	{
		id: 'kozachinskiy',
		authors:
			'A. Kozachinskiy, F. Urrutia, H. Jimenez, T. Steifer, G. Pizarro, M. Fuentes, F. Meza, C. Buc, C. Rojas',
		title:
			'Strassen attention: unlocking compositional abilities in transformers based on a new lower bound method',
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
		id: 'abbe',
		authors: 'E. Abbe, E. Boix-Adserà, T. Misiakiewicz',
		title: 'SGD learning on neural networks: leap complexity and saddle-to-saddle dynamics',
		venue: 'COLT',
		year: 2023,
		url: 'https://arxiv.org/abs/2302.11055'
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
		id: 'lla',
		authors: 'Y. Zuo, Y. Yin, Z. Zeng, A. Li, B. Zhu, Z. Wang',
		title:
			'Local Linear Attention: An optimal interpolation of linear and softmax attention for test-time regression',
		venue: 'arXiv:2510.01450',
		year: 2025,
		url: 'https://arxiv.org/abs/2510.01450'
	},
	{
		id: 'parallax',
		authors: 'Y. Zuo, D. Pai, Z. Zeng, A. Dewulf, S. Hu, Z. Wang',
		title: 'Parallax: Parameterized local linear attention for language modeling',
		venue: 'arXiv:2605.29157',
		year: 2026,
		url: 'https://arxiv.org/abs/2605.29157'
	},
	{
		id: 'seq2tens',
		authors: 'C. Toth, P. Bonnier, H. Oberhauser',
		title: 'Seq2Tens: An efficient representation of sequences by low-rank tensor projections',
		venue: 'ICLR',
		year: 2021,
		url: 'https://arxiv.org/abs/2006.07027'
	},
	{
		id: 'development',
		authors: 'H. Lou, S. Li, H. Ni',
		title: 'Path development network with finite-dimensional Lie group representation',
		venue: 'Transactions on Machine Learning Research',
		year: 2024,
		url: 'https://arxiv.org/abs/2204.00740'
	},
	{
		id: 'chughtai',
		authors: 'B. Chughtai, L. Chan, N. Nanda',
		title: 'A toy model of universality: reverse engineering how networks learn group operations',
		venue: 'arXiv:2302.03025',
		year: 2023,
		url: 'https://arxiv.org/abs/2302.03025'
	},
	{
		id: 'jaxjs',
		authors: 'E. Zhang',
		title: 'jax-js: JAX-style arrays, autodiff and jit in the browser',
		venue: 'Software, github.com/ekzhang/jax-js',
		year: 2025,
		url: 'https://github.com/ekzhang/jax-js'
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
		id: 'orthogonal',
		authors: 'M. Lezcano-Casado, D. Martínez-Rubio',
		title:
			'Cheap orthogonal constraints in neural networks: a simple parametrization of the orthogonal and unitary group',
		venue: 'ICML',
		year: 2019,
		url: 'https://arxiv.org/abs/1901.08428'
	},
	{
		id: 'iteratedsums',
		authors: 'J. Diehl, K. Ebrahimi-Fard, N. Tapia',
		title: 'Time-warping invariants of multidimensional time series',
		venue: 'Acta Applicandae Mathematicae 170:265–290',
		year: 2020,
		url: 'https://arxiv.org/abs/1906.05823'
	},
	{
		id: 'deepsignatures',
		authors: 'P. Bonnier, P. Kidger, I. Perez Arribas, C. Salvi, T. Lyons',
		title: 'Deep signature transforms',
		venue: 'NeurIPS',
		year: 2019,
		url: 'https://arxiv.org/abs/1905.08494'
	},
	{
		id: 'roughtransformers',
		authors: 'F. Moreno-Pino, Á. Arroyo, H. Waldon, X. Dong, Á. Cartea',
		title:
			'Rough Transformers: lightweight and continuous time series modelling through signature patching',
		venue: 'NeurIPS',
		year: 2024,
		url: 'https://arxiv.org/abs/2405.20799'
	},
	{
		id: 'deltaproduct',
		authors: 'J. Siems, T. Carstensen, A. Zela, F. Hutter, M. Pontil, R. Grazzi',
		title: 'DeltaProduct: improving state-tracking in linear RNNs via Householder products',
		venue: 'NeurIPS',
		year: 2025,
		url: 'https://arxiv.org/abs/2502.10297'
	},
	{
		id: 'automata',
		authors: 'B. Liu, J. T. Ash, S. Goel, A. Krishnamurthy, C. Zhang',
		title: 'Transformers learn shortcuts to automata',
		venue: 'ICLR',
		year: 2023,
		url: 'https://arxiv.org/abs/2210.10749'
	},
	{
		id: 'gdn',
		authors: 'S. Yang, J. Kautz, A. Hatamizadeh',
		title: 'Gated delta networks: improving Mamba2 with delta rule',
		venue: 'ICLR',
		year: 2025,
		url: 'https://arxiv.org/abs/2412.06464'
	},
	{
		id: 'path',
		authors: 'S. Yang et al.',
		title: 'PaTH attention: position encoding via accumulating Householder transformations',
		venue: 'arXiv',
		year: 2025,
		url: 'https://arxiv.org/abs/2505.16381'
	},
	{
		id: 'primer',
		authors: 'D. R. So et al.',
		title: 'Primer: searching for efficient transformers for language modeling',
		venue: 'NeurIPS',
		year: 2021,
		url: 'https://arxiv.org/abs/2109.08668'
	},
	{
		id: 'muon',
		authors: 'K. Jordan et al.',
		title: 'Muon: an optimizer for hidden layers in neural networks',
		venue: 'blog post',
		year: 2024,
		url: 'https://kellerjordan.github.io/posts/muon/'
	},
	{
		id: 'chollet',
		authors: 'F. Chollet',
		title: 'On the measure of intelligence',
		venue: 'arXiv',
		year: 2019,
		url: 'https://arxiv.org/abs/1911.01547'
	},
	{
		id: 'rope',
		authors: 'J. Su, Y. Lu, S. Pan, A. Murtadha, B. Wen, Y. Liu',
		title: 'RoFormer: enhanced transformer with rotary position embedding',
		venue: 'arXiv',
		year: 2021,
		url: 'https://arxiv.org/abs/2104.09864'
	},
	{
		id: 'fox',
		authors: 'Z. Lin, E. Nikishin, X. O. He, A. Courville',
		title: 'Forgetting Transformer: softmax attention with a forget gate',
		venue: 'ICLR',
		year: 2025,
		url: 'https://arxiv.org/abs/2503.02130'
	},
	{
		id: 'gatedattn',
		authors: 'Z. Qiu et al.',
		title:
			'Gated attention for large language models: non-linearity, sparsity, and attention-sink-free',
		venue: 'NeurIPS',
		year: 2025,
		url: 'https://arxiv.org/abs/2505.06708'
	},
	{
		id: 'valueres',
		authors: 'Z. Zhou, T. Wu, Z. Jiang, Z. Lan',
		title: 'Value residual learning for alleviating attention concentration in transformers',
		venue: 'arXiv',
		year: 2024,
		url: 'https://arxiv.org/abs/2410.17897'
	},
	{
		id: 'hnet',
		authors: 'S. Hwang, B. Wang, A. Gu',
		title: 'Dynamic chunking for end-to-end hierarchical sequence modeling',
		venue: 'ICLR',
		year: 2026,
		url: 'https://arxiv.org/abs/2507.07955'
	},
	{
		id: 'starfree',
		authors: 'A. Yang, D. Chiang, D. Angluin',
		title: 'Masked hard-attention transformers recognize exactly the star-free languages',
		venue: 'NeurIPS',
		year: 2024,
		url: 'https://arxiv.org/abs/2310.13897'
	}
];

/** Citation number (1-based) for a reference id. */
export const cite = (id: string) => REFERENCES.findIndex((r) => r.id === id) + 1;
