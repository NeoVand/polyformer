/** Metadata checked in research/PRIOR_ART.md and results/prior_art_verified.json.
 * The original Transformer citation is retained from the report's bibliography.
 */
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
		id: 'chakrabarti',
		authors: 'S. Chakrabarti, T. Pitassi, J. Alman',
		title: 'Poly-attention: a general scheme for higher-order self-attention',
		venue: 'ICLR',
		year: 2026,
		url: 'https://arxiv.org/abs/2602.02422'
	},
	{
		id: 'lla',
		authors: 'Y. Zuo, Y. Yin, Z. Zeng, A. Li, B. Zhu, Z. Wang',
		title:
			'Local linear attention: an optimal interpolation of linear and softmax attention for test-time regression',
		venue: 'arXiv preprint',
		year: 2025,
		url: 'https://arxiv.org/abs/2510.01450'
	},
	{
		id: 'parallax',
		authors: 'Y. Zuo, D. Pai, Z. Zeng, A. Dewulf, S. Hu, Z. Wang',
		title: 'Parallax: parameterized local linear attention for language modeling',
		venue: 'arXiv preprint',
		year: 2026,
		url: 'https://arxiv.org/abs/2605.29157'
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
		id: 'seq2tens',
		authors: 'C. Toth, P. Bonnier, H. Oberhauser',
		title: 'Seq2Tens: an efficient representation of sequences by low-rank tensor projections',
		venue: 'ICLR',
		year: 2021,
		url: 'https://arxiv.org/abs/2006.07027'
	},
	{
		id: 'pathdev',
		authors: 'H. Lou, S. Li, H. Ni',
		title: 'Path Development Network with finite-dimensional Lie group representation',
		venue: 'Transactions on Machine Learning Research (first preprint 2022)',
		year: 2024,
		url: 'https://arxiv.org/abs/2204.00740'
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
		id: 'chughtai',
		authors: 'B. Chughtai, L. Chan, N. Nanda',
		title: 'A toy model of universality: reverse engineering how networks learn group operations',
		venue: 'arXiv preprint',
		year: 2023,
		url: 'https://arxiv.org/abs/2302.03025'
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
	}
];
