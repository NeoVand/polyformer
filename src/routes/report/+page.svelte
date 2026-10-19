<script lang="ts">
	import { asset } from '$app/paths';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import Cite from '#lib/learn/Cite.svelte';
	import ArityFigure from '#lib/report/ArityFigure.svelte';
	import { BIB } from '#lib/report/bib.ts';
	import CurvesFigure from '#lib/report/CurvesFigure.svelte';
	import EvidenceMatrix from '#lib/report/EvidenceMatrix.svelte';
	import FeynmanFigure from '#lib/report/FeynmanFigure.svelte';
	import MarginalDemo from '#lib/report/MarginalDemo.svelte';
	import NewtonDemo from '#lib/report/NewtonDemo.svelte';
	import ReplicationTable from '#lib/report/ReplicationTable.svelte';
	import TensorGraphFigure from '#lib/report/TensorGraphFigure.svelte';
	import Theorem from '#lib/report/Theorem.svelte';
	import type { Card } from '#lib/set/cards.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { Book, Compare, Feynman, FunctionIcon, Grid, Matrix, Note } from '#lib/ui/icons.ts';
	import DiagramFlow from '#lib/viz/DiagramFlow.svelte';
	import FlowLegend from '#lib/viz/FlowLegend.svelte';

	// ── which part of the paper is on screen ─────────────────────────────────
	const PARTS: Record<string, string> = {
		abstract: 'abstract',
		intro: 'abstract',
		hierarchy: 'hierarchy',
		dspa: 'dspa',
		composition: 'dspa',
		algebra: 'algebra',
		experiments: 'experiments',
		related: 'related',
		limits: 'related',
		appendix: 'appendix',
		references: 'appendix'
	};
	let section = $state('abstract');
	function watch(el: HTMLElement) {
		const io = new IntersectionObserver(
			(entries) => {
				for (const e of entries) if (e.isIntersecting) section = PARTS[e.target.id] ?? section;
			},
			{ rootMargin: '-35% 0px -60% 0px' }
		);
		el.querySelectorAll('section[id]').forEach((s) => io.observe(s));
		return () => io.disconnect();
	}

	// ── the recorded SET model, for the tree-expansion figure ────────────────
	let setModel = $state.raw<{ layout: number[][]; diagram: DiagramResult } | null>(null);
	let root = $state<number | null>(null);
	$effect(() => {
		fetch(asset('recorded/set-diagram.json'))
			.then((r) => (r.ok ? r.json() : null))
			.then((j) => j?.diagram && (setModel = j))
			.catch(() => {});
	});

	// ── results from the research harness (research/summarize.py writes these) ─
	interface Row {
		task: string;
		model: string;
		seeds: number[];
		bal: number[];
		bal_mean: number;
		params: number;
		curves?: [number, number][][];
	}
	const FILES = import.meta.glob<Row[]>('/src/lib/report/results/*.json', {
		eager: true,
		import: 'default'
	});
	const grid = (name: string): Row[] => FILES[`/src/lib/report/results/${name}.json`] ?? [];
	/** Newton attention at its default size gets a short id in the tables. */
	const newton = (rows: Row[], from = 'newton-K6-r32-h4') =>
		rows.map((r) => (r.model === from ? { ...r, model: 'newton' } : r));
	const baseline = grid('baseline');
	const phaseA = grid('phase_a');
	const newtonA = grid('newton_a');
	const newtonB = grid('newton_b');

	const BASE_TASKS = [
		{ id: 'set', label: 'SET' },
		{ id: 'set4', label: 'Four-card SET' },
		{ id: 'chase', label: 'Pointer chase', floor: 0.125 },
		{ id: 'compose3', label: 'Three-hop', floor: 0.125 }
	];
	const BASE_MODELS = [
		{ id: 'standard-1L', label: 'Standard, 1 layer' },
		{ id: 'standard-2L', label: 'Standard, 2 layers' },
		{ id: 'standard-3L', label: 'Standard, 3 layers' },
		{ id: 'tree', label: 'Tree' },
		{ id: 'strassen', label: 'Strassen' },
		{ id: 'cubic', label: 'Cubic' },
		{ id: 'quartic', label: 'Dense quartic' },
		{ id: 'dspa4', label: 'Feynman' },
		{ id: 'newton', label: 'Newton attention, rank 32' },
		{ id: 'newton-K6-r256-h4', label: 'Newton attention, rank 256' }
	];
	const LADDER_TASKS = [
		{ id: 'zs3', label: 'Match-3' },
		{ id: 'zs4', label: 'Match-4' },
		{ id: 'zs5', label: 'Match-5' },
		{ id: 'arity', label: 'Smallest arity', floor: 0.25 }
	];
	const LADDER_MODELS = [
		{ id: 'standard-1L', label: 'Standard, 1 layer' },
		{ id: 'standard-2L', label: 'Standard, 2 layers' },
		{ id: 'standard-3L', label: 'Standard, 3 layers' },
		{ id: 'cubic', label: 'Cubic' },
		{ id: 'quartic', label: 'Dense quartic' },
		{ id: 'dspa4', label: 'Feynman' },
		{ id: 'dspa5', label: 'Feynman with Newton primitives' },
		{ id: 'dspa5-d128', label: 'the same, width 128' },
		{ id: 'dspa5-d192', label: 'the same, width 192' },
		{ id: 'dspa5-lin', label: 'the same, no cubic sector' },
		{ id: 'newton', label: 'Newton attention, rank 32' },
		{ id: 'newton-K6-r256-h4', label: 'Newton attention, rank 256' }
	];
	const ORDER_MODELS = [
		{ id: 'newton-K3-r32-h4', label: 'Order 3' },
		{ id: 'newton-K4-r32-h4-s20000', label: 'Order 4, 20,000 steps' },
		{ id: 'newton-K6-r32-h4', label: 'Order 6' },
		{ id: 'newton-K6-r32-h4-s20000', label: 'Order 6, 20,000 steps' }
	];
	const RANKS = [8, 16, 32, 40, 48, 64, 128];
	const RANK_MODELS = RANKS.map((r) => ({ id: `newton-K6-r${r}-h1-s10000`, label: `Rank ${r}` }));
	const WIDE_MODELS = [
		{ id: 'newton-K6-r128-h4', label: 'Newton, rank 128' },
		{ id: 'newton-K6-r256-h4', label: 'Newton, rank 256' },
		{ id: 'newton-K3-r128-h4', label: 'Rank 128, order 3' },
		{ id: 'newton-K4-r128-h4', label: 'Rank 128, order 4' },
		{ id: 'standard-3L-d256', label: 'Standard, 3 layers, width 256' },
		{ id: 'cubic-d192', label: 'Cubic, width 192' }
	];
	const CURVE_MODELS = [
		{ id: 'standard-3L', label: 'Standard, 3 layers', tone: 0.45, dash: '2 3' },
		{ id: 'dspa5', label: 'Feynman, Newton primitives', tone: 0.6, dash: '6 3' },
		{ id: 'cubic', label: 'Cubic', tone: 0.8, dash: '' },
		{ id: 'quartic', label: 'Dense quartic', tone: 0.8, dash: '8 3 2 3' },
		{ id: 'newton', label: 'Newton, rank 32', tone: 0.7, dash: '1 3' },
		{ id: 'newton-K6-r256-h4', label: 'Newton, rank 256', tone: 1, dash: '', emphasis: true }
	];

	// ── equations ────────────────────────────────────────────────────────────
	const T = {
		match: String.raw`\mathrm{Match}_k(x)_i = \mathbf 1\Big[\,\exists\, S \subseteq [n]\setminus\{i\},\ |S| = k-1 :\ x_i + \textstyle\sum_{j\in S} x_j = 0\,\Big]`,
		thm1: String.raw`\mathbb E\big[f(X)\mid Y=1\big] \;=\; \mathbb E\big[f(X)\mid Y=0\big] \qquad\text{for every}\qquad f(x)=\sum_{S\subsetneq[r]} f_S(x_S)`,
		y: String.raw`Y = \mathbf 1[X_1+\cdots+X_r = 0]`,
		uniform: String.raw`\Pr\big[\,Y=1 \mid X_S = x_S\,\big] = \frac{|G|^{h-1}}{|G|^{h}} = \frac{1}{|G|}`,
		dc: String.raw`\mathcal D[M]_{jk} = M_{jk} - \bar M_{j\cdot} - \bar M_{\cdot k} + \bar M_{\cdot\cdot}`,
		deg2: String.raw`\ell_i(j,k) = u_i(j) + w_i(k) + c(j,k) \quad\Longrightarrow\quad \mathcal D[\ell_i] = \mathcal D[c]`,
		cubic: String.raw`\mathcal D[\ell_i] = \sum_{a=1}^{d} q_{ia}\; \mathcal D\big[\,K^{1}_{\cdot a}\, (K^{2}_{\cdot a})^{\top}\big]`,
		cubicHead: String.raw`A_{ijk} = \big\langle Q_i,\; K^1_j \odot K^2_k \big\rangle, \qquad y_i = \sum_{j,k} \operatorname{softmax}_{jk}(A_{i\cdot\cdot})\; V^1_j \odot V^2_k`,
		dspa: String.raw`\begin{aligned}\Phi^{r}_t \;=\;& \pi_{\text{leaf}}\, v_t \;+\; \sum_j \pi_j\, \Phi^{r-1}_j \;+\; \sum_{j,k} \pi_{jk}\, \Phi^{r-1}_j \odot \Phi^{r-1}_k \\ &+\; \sum_{j,m} \pi_{jm}\, \Phi^{r-1}_j \odot \Psi^{r}_m \;+\; \pi_{\text{carry}}\, \Phi^{r-1}_t, \qquad \Psi^r_m = \sum_{k,l} \rho^r_{m,kl}\, \Phi^{r-1}_k \odot \Phi^{r-1}_l\end{aligned}`,
		mu: String.raw`\mu_s = -\log |S_s|`,
		tree: String.raw`\Phi^R_t \;=\; \sum_{T \in \mathcal T_{R,t}} w_T(V) \bigodot_{\ell \in L(T)} v_{\tau(\ell)}, \qquad w_T \ge 0,\quad \sum_{T} w_T = 1,\quad |L(T)| \le 3^R`,
		degrees: String.raw`D_0 = 1, \qquad D_r \le \max\{D_{r-1},\, 2D_{r-1},\, 3D_{r-1}\}`,
		exch: String.raw`\sum_{j,k,l} H_{(t,j),(k,l)}\; \Phi_j \odot \Phi_k \odot \Phi_l, \qquad H_{(t,j),(k,l)} = \sum_{m=1}^{M} \pi_{t,jm}\, \rho_{m,kl}`,
		kernel: String.raw`K_{(i,j),(k,l)} = \mathbf 1\big[x_i + x_j + x_k + x_l = 0\big]`,
		rank: String.raw`\operatorname{rank} H \le M \qquad\text{while}\qquad \operatorname{rank} K = |G|`,
		phi: String.raw`\phi_c(x) = \omega^{\langle c,\, x\rangle},\qquad \omega = e^{2\pi i/3},\qquad \phi(x)\odot\phi(y) = \phi(x+y)`,
		newton: String.raw`\begin{aligned} P_j &= \sum_{t} \phi(x_t)^{\odot j}, \qquad r\,E_r = \sum_{j=1}^{r} (-1)^{j-1}\, E_{r-j}\odot P_j, \\ N_{i,k} &= \frac{1}{|G|}\sum_{c}\sum_{j=0}^{k-1} (-1)^j\, E_{k-1-j}(c)\; \phi_c(x_i)^{j+1} \end{aligned}`,
		gen: String.raw`\prod_{t=1}^{n}\big(1 + z\,e_{x_t}\big) = \sum_{r\ge 0} z^r E_r`,
		excl: String.raw`\prod_{t\ne i}\big(1 + z\,e_{x_t}\big) = \Big(\sum_r z^r E_r\Big)\Big(\sum_j (-z)^j e_{j x_i}\Big) \;\Longrightarrow\; E^{(-i)}_{r} = \sum_{j=0}^{r} (-1)^j\, e_{j x_i} * E_{r-j}`,
		coef: String.raw`N_{i,k} = \big[e_{-x_i}\big]\, E^{(-i)}_{k-1}, \qquad \big[e_g\big]\,A = \frac{1}{|G|}\sum_c \hat A(c)\,\overline{\phi_c(g)}`,
		cost: String.raw`O\big((kn + k^2)\,|G|\big)\quad\text{versus}\quad \Theta(n^k d)\ \text{for dense order-}k\text{ attention}`,
		width: String.raw`d \;\ge\; |G| - 1`,
		nPhase: String.raw`\phi_t = \sigma(W_g h_t) \odot \exp\!\big(i\, W_\theta h_t\big) \in \mathbb C^{r}`,
		nPow: String.raw`P^{(-q)}_j = \sum_{t \ne q} \phi_t^{\odot j}, \qquad m\, e^{(-q)}_m = \sum_{j=1}^{m} (-1)^{j-1}\, e^{(-q)}_{m-j} \odot P^{(-q)}_j`,
		nOut: String.raw`y_q = W_o \Big[\, \operatorname{Re},\, \operatorname{Im} \Big]\Big( \tbinom{n-1}{m}^{-1} \phi_q \odot e^{(-q)}_m \Big)_{m=0}^{K-1}`,
		nSubset: String.raw`\phi_q \odot e^{(-q)}_m \;=\; \sum_{S \subseteq [n]\setminus\{q\},\ |S| = m}\ \ \bigodot_{t \in S \cup \{q\}} \phi_t`,
		nCost: String.raw`O(nKr)`
	};
</script>

<svelte:head>
	<title>Report | Polyformer</title>
	<meta
		name="description"
		content="How many tokens make a relation? A working paper on attention that lets the data choose the arity, with proofs, live checks and every measured result."
	/>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'abstract', label: 'Paper', icon: Note },
		{ id: 'hierarchy', label: 'Arity', icon: FunctionIcon },
		{ id: 'dspa', label: 'Feynman', icon: Feynman },
		{ id: 'algebra', label: 'Algebra', icon: Matrix },
		{ id: 'experiments', label: 'Results', icon: Compare },
		{ id: 'related', label: 'Related', icon: Book },
		{ id: 'appendix', label: 'Appendix', icon: Grid }
	]}
	active={section}
>
	<article class="paper" {@attach watch}>
		<header class="title-block">
			<h1>How many tokens make a relation?</h1>
			<p class="subtitle">Attention that lets the data choose the arity</p>
			<p class="authors">
				Mostafa “Neo” Mohsenvand <span class="draft">Working draft, October 2026</span>
			</p>
		</header>

		<section id="abstract">
			<aside class="side key">
				<span class="ev-key proved">Proved here</span>
				<span class="ev-key measured">Measured</span>
				<span class="ev-key open">Open</span>
				<span>Every number on this page was measured with the code that runs this site.</span>
			</aside>
			<p class="abstract">
				<b>Abstract.</b> Attention scores tokens in pairs, yet many relations hold only among three
				or more tokens at once. Higher-order attention captures them at a cost that grows as <MathTex
					tex="n^k"
				/> and fixes the arity <MathTex tex="k" /> in advance. We ask whether the data can choose it.
				For relations defined by a zero sum in a finite abelian group, the label lives on characters of
				full degree, so every score built from fewer than <MathTex tex="k" /> tokens has the same mean
				on matching and non-matching tuples (Theorem 1). Composing arity from lower-order parts does not
				get around this in practice: an operator that mixes arities inside one softmax and can represent
				the composition (Theorem 3) does not learn it, and neither does standard attention at any depth
				we tried. In the group algebra, though, arity is the degree of a symmetric polynomial. Pooled
				power sums and Newton's identities count the
				<MathTex tex="k" />-way relations of every token, for every <MathTex tex="k" />, in time
				linear in the sequence (Theorem 5). Newton attention turns that identity into a layer with
				learnable phases. Offered every arity up to six, it solves SET and Match-3 on every seed,
				reaches 95% where the label is the smallest arity at which a token completes a relation (the
				best fixed-order operator reaches 54%), and is the only operator above chance on five-way
				relations. Capping its order below a task's arity returns it to exactly chance, and widening
				fixed-order baselines to its size does not move them.
			</p>
		</section>

		<section id="intro">
			<h2><span class="n">1</span>Introduction</h2>
			<p>
				Lay twelve SET cards on a table and ask which of them belong to a SET. No pair of cards
				settles it. Any two cards are completed by exactly one third card, and whether that card
				lies on the table is a fact about all three at once. Relations like this, among three or
				more objects at a time, run through reasoning: a path is a relation among its steps, a
				reaction among its reagents, an inference among its premises.
			</p>
			<p>
				A transformer head compares a query with one key at a time <Cite refs={BIB} id="vaswani" />.
				Whatever three tokens jointly imply has to be assembled from pairwise scores over several
				layers, and for some relations that is provably expensive <Cite
					refs={BIB}
					id={['sanford23', 'kozachinskiy']}
				/>. Higher-order attention scores a query against pairs of keys and solves such relations in
				one layer <Cite refs={BIB} id={['clift', 'sanford23', 'roy', 'chakrabarti']} />, at
				<MathTex tex="\Theta(n^3 d)" /> per head; order <MathTex tex="k" /> costs
				<MathTex tex="\Theta(n^k d)" />
				<Cite refs={BIB} id="alman" />. Each of these fixes the arity once, for every token and
				every input.
			</p>
			<p>
				We ask whether the data can choose the arity instead, and find that arity is algebra. For
				relations defined by a zero sum in a finite abelian group, a <MathTex tex="k" />-way
				relation is invisible on average to every score built from fewer tokens (Section 2). An
				operator that composes arity from lower-order parts can represent the answer but does not
				learn it (Sections 3, 4 and 6). Once arity is native, it is cheap: in the group algebra a
				Hadamard product is a convolution, pooled powers are power sums, and Newton's identities
				turn them into counts of relations of every arity at once, linear in the sequence (Section 5
				and Figure 1). Newton attention builds a layer from that identity. With every arity up to
				six on offer, it uses the one each task needs, and taking that arity off the menu sends it
				back to chance (Section 6).
			</p>
			<figure class="wide fig">
				<ArityFigure />
				<figcaption>
					<b>Figure 1.</b> (a) A query card and three relations it takes part in, written as sums:
					every attribute adds to zero modulo 3. (b) Under a character <MathTex tex="\chi" />
					each card is a phase, and a product of phases is the phase of the sum. A SET gives phase zero
					under all 81 characters of <MathTex tex={String.raw`\mathbb Z_3^4`} />, so they add to 81;
					any other triple splits them 27, 27, 27 and they cancel. (c) Phases pooled once into power
					sums and combined by Newton's identities give every token its count of relations of every
					arity, at a cost linear in <MathTex tex="n" />, where dense order-<MathTex tex="k" /> attention
					grows as <MathTex tex="n^k" />.
				</figcaption>
			</figure>
			<p class="contrib">
				<b>Contributions.</b> (i) Arity as Fourier degree, with an indistinguishability theorem for
				proper-subset scores. (ii) Feynman attention, an operator that mixes arities inside one
				softmax, its exact expansion as a sum over trees, and a rank obstruction that explains why
				composing arity through shared intermediates fails. (iii) Newton's identities in the group
				algebra, which count every arity at linear cost, and Newton attention, the layer built on
				them. (iv) A measured Match-<MathTex tex="k" /> ladder across ten operators, three seeds each,
				with order ablations and width-matched baselines. (v) Every result reproducible in this page or
				in the published harness.
			</p>
		</section>

		<section id="hierarchy">
			<h2><span class="n">2</span>The arity hierarchy</h2>
			<p>
				Let <MathTex tex="G" /> be a finite abelian group and <MathTex tex="x_1,\dots,x_n \in G" /> the
				tokens. SET is the case <MathTex tex={String.raw`G=\mathbb Z_3^4`} />: a card is four
				attributes with three values each, and three distinct cards form a SET exactly when they sum
				to zero.
			</p>
			<Theorem kind="Definition" n={1} name="Match-k">
				<MathTex display tex={T.match} />
				<p>Distinct positions only; repeated values at distinct positions are allowed.</p>
			</Theorem>

			<Theorem n={1} name="Proper-subset scores are blind on average" evidence="proved" id="thm1">
				<p>
					Let <MathTex tex="X_1,\dots,X_r" /> be independent and uniform on <MathTex tex="G" />,
					with
					<MathTex tex={T.y} />. For every proper subset <MathTex
						tex={String.raw`S \subsetneq [r]`}
					/>, the distribution of <MathTex tex="X_S" /> is uniform under both <MathTex tex="Y=1" /> and
					<MathTex tex="Y=0" />. Consequently
				</p>
				<MathTex display tex={T.thm1} />
				<p>
					and no threshold on such an <MathTex tex="f" /> separates every matching tuple from every other.
				</p>
				{#snippet proof()}
					<p>
						Fix <MathTex tex="X_S = x_S" />. The remaining <MathTex tex="h = r - |S| \ge 1" /> coordinates
						are uniform and independent. Choose all but one freely; the last is then determined by the
						zero-sum condition, so exactly <MathTex tex={String.raw`|G|^{h - 1}`} /> of the <MathTex
							tex="|G|^h"
						/> completions match:
					</p>
					<MathTex display tex={T.uniform} />
					<p>
						This does not depend on <MathTex tex="x_S" />, so <MathTex tex="X_S" /> is independent of
						<MathTex tex="Y" /> and has the same uniform law given either label. Each term
						<MathTex tex="f_S(X_S)" /> therefore has the same conditional mean under both labels, and
						so does their sum. A threshold that put every matching tuple strictly above every other would
						give the matching class a strictly larger mean.
					</p>
				{/snippet}
			</Theorem>
			<MarginalDemo />
			<aside class="side">
				The fact behind Theorem 1 is classical: the uniform distribution on solutions of one linear
				equation in <MathTex tex="r" /> unknowns is <MathTex tex="(r-1)" />-wise independent.
			</aside>
			<p>
				In Fourier terms the label is a sum of characters of full support, orthogonal to every
				function of fewer coordinates. Two consequences follow. A logit built from pairs carries no
				first-moment signal for a three-way relation; and the relation has leap <MathTex tex="k" /> in
				the sense of Abbe et al.
				<Cite refs={BIB} id="abbe" />, which predicts the long plateau and sudden snap seen when a
				model of the right order trains (Figure 5). The theorem is about means of scores. A softmax
				is not linear, so it is not by itself a lower bound on classifiers; representational lower
				bounds for pairwise attention on Match3 need communication complexity <Cite
					refs={BIB}
					id="sanford23"
				/>.
			</p>

			<Theorem
				kind="Proposition"
				n={2}
				name="Degree-2 scores cannot couple a pair to the query"
				evidence="proved"
			>
				<p>
					Write <MathTex tex="\mathcal D" /> for double centring, <MathTex tex={T.dc} />. If query
					<MathTex tex="i" />'s logit over pairs <MathTex tex="(j,k)" /> is a degree-2 polynomial in the
					three roles, as in standard, tree and Strassen attention, then
				</p>
				<MathTex display tex={T.deg2} />
				<p>
					is the same for every query. A cubic head instead gives <MathTex tex={T.cubic} />, which
					spans up to
					<MathTex tex="d" /> dimensions as the query varies.
				</p>
				{#snippet proof()}
					<p>
						A degree-2 polynomial in three roles has monomials pairing query with first key, query
						with second key, and the two keys. The first two depend on <MathTex tex="(i,j)" /> or <MathTex
							tex="(i,k)"
						/> only, so they are a row effect and a column effect of the pair matrix, which double centring
						removes. What remains is the centred key-key term, which does not involve the query.
					</p>
				{/snippet}
			</Theorem>
			<p>
				A cubic head scores the query against every pair of keys at once and reads the product of
				their values,
			</p>
			<MathTex display tex={T.cubicHead} />
			<p>
				Figure 2 shows one built by hand for SET. Its score tensor peaks exactly on the SETs, and
				the same numbers, read as attention on hyperedges, put the query's weight on a triangle
				rather than an edge.
			</p>
			<figure class="wide fig">
				<TensorGraphFigure />
				<figcaption>
					<b>Figure 2.</b> One cubic head on twelve SET cards. Left: the score tensor
					<MathTex tex={String.raw`A_{ijk}`} />, one block per triple sized by its score, with the
					query's slice as a solid plane. Right: the same scores as attention on hyperedges; every
					SET on the table is a membrane, and the lit triangle is where the query's weight goes. The
					query tours every card in a SET; pick a card or a block to take over, and drag either view
					to turn it.
				</figcaption>
			</figure>
		</section>

		<section id="dspa">
			<h2><span class="n">3</span>Feynman attention: arity as a choice inside one softmax</h2>
			<p>
				Feynman attention lets every token choose, at every round, how many tokens it reads. Each
				token keeps a state <MathTex tex="\Phi^r_t" />, starting from its value
				<MathTex tex="\Phi^0_t = v_t" /> and rebuilt for <MathTex tex="R" /> rounds:
			</p>
			<MathTex display tex={T.dspa} />
			<aside class="side">
				The name records the analogy that guided the design: the recursion is a Dyson–Schwinger
				equation, and unrolled, its output is a sum over Feynman diagrams (Theorem 3 and Figure 4).
			</aside>
			<p>
				One softmax <MathTex tex="\pi" /> runs over every option of every sector, scored by a single trilinear
				vertex
				<MathTex tex={String.raw`\langle q_t, a\odot b\rangle`} /> over tokens, a vacuum token and the
				virtual modes. The sectors offer very different numbers of options (one leaf, <MathTex
					tex="n"
				/> hops,
				<MathTex tex="n^2" /> pairs), so each sector gets a fixed bias <MathTex tex={T.mu} />, which
				gives every sector equal prior mass at initialisation. A carry keeps finished results fixed,
				and the read-out is RMS-normalised.
			</p>
			<Theorem n={3} name="Tree expansion" evidence="proved" id="thm3">
				<p>For every input and every setting of the weights, before normalisation,</p>
				<MathTex display tex={T.tree} />
				<p>
					where <MathTex tex={String.raw`\mathcal T_{R,t}`} /> is a finite set of token-labelled derivation
					trees (leaf, hop or carry with one child, pair with two, exchange with three) and <MathTex
						tex="w_T"
					/> is the product of the softmax weights along the tree. Without the exchange sector the bound
					is
					<MathTex tex="2^R" />.
				</p>
				{#snippet proof()}
					<p>
						Induction on rounds. Substitute the recurrence for each previous-round state and
						distribute the sums through the Hadamard products, which is valid because <MathTex
							tex={String.raw`(\mathbb R^d, +, \odot)`}
						/>
						is a commutative algebra. Each option contributes one tree per choice of child trees, weighted
						by the product of its own softmax weight and the children's weights. Replacing every leaf
						by the scalar 1 shows the weights sum to one, since each softmax sums to one. The number of
						leaves obeys
					</p>
					<MathTex display tex={T.degrees} />
					<p>
						the factor 3 coming from an exchange, which multiplies one state by a mode built from
						two.
					</p>
				{/snippet}
			</Theorem>
			<p class="caveat">
				Two qualifications matter. The weights depend on the input, so the output is a polynomial in
				the values only when the routing is frozen; and a finite softmax never selects one arity
				exactly: what adapts is how the weight is spread over trees of different sizes. Figures 3
				and 4 show that spread for trained models.
			</p>

			{#if setModel}
				{@const d = setModel.diagram}
				{@const cards = setModel.layout as unknown as Card[]}
				<figure class="wide fig split">
					<div>
						<DiagramFlow
							head={d.perHead[0]}
							n={d.n}
							rounds={d.rounds}
							rows={[Array.from({ length: cards.length }, (_, i) => i + 1)]}
							root={root ?? d.token}
							onroot={(t) => (root = t)}
							pitch={19}
							column={130}
						>
							{#snippet label(t)}<SetCard card={cards[t - 1]} width={15} />{/snippet}
						</DiagramFlow>
					</div>
					<figcaption>
						<b>Figure 3.</b> Theorem 3 for a Feynman attention model trained in a browser on SET
						(two rounds, step 1,500, 99.98% held out). Every token's state at every round, marked
						with the vertex of the sector it mostly uses. Lines show what one card reads, weighted
						by the share of its output they carry: each card in a SET reads its two partners at one
						cubic vertex. Hover or click a card to expand another.
						<span class="fig-key"><FlowLegend compact /></span>
					</figcaption>
				</figure>
			{/if}
			<figure class="wide fig">
				<FeynmanFigure />
				<figcaption>
					<b>Figure 4.</b> The same expansion as Feynman diagrams, one tree per output, rounds running
					left to right from the values to the read-out. Line weight is the tree's share of the output.
					(a) On SET a card's state is one cubic vertex joining its two SET partners. (b) On pointer chasing
					the query's state is a chain of hops along its list, one per round.
				</figcaption>
			</figure>
		</section>

		<section id="composition">
			<h2><span class="n">4</span>Why composing arity fails</h2>
			<p>
				Two rounds of cubic vertices reach degree four, yet Feynman attention does not learn
				four-card SET (Match-4 on <MathTex tex={String.raw`\mathbb Z_3^4`} />): it stays at chance
				on every seed, where dense quartic attention succeeds on two of three (Table 2). Degree is
				not the problem. A round-two contribution has the form
				<MathTex
					tex={String.raw`\pi^2_{i,jk}\,\pi^1_{j,ab}\,\pi^1_{k,cd}\,(v_a\odot v_b\odot v_c\odot v_d)`}
				/>: the root picks <MathTex tex="(j,k)" />, but what <MathTex tex="j" /> read in round one was
				decided once, for every query. Intermediates are shared.
			</p>
			<Theorem
				kind="Proposition"
				n={4}
				name="Shared modes need one per group element"
				evidence="proved"
			>
				<p>At fixed routing, the exchange sector contributes</p>
				<MathTex display tex={T.exch} />
				<p>
					so <MathTex tex={String.raw`\operatorname{rank} H \le M`} />. If every element of <MathTex
						tex="G"
					/> occurs as a sum <MathTex tex="x_i+x_j" /> and as a sum <MathTex tex="x_k+x_l" />, the
					Match-4 kernel
					<MathTex tex={T.kernel} /> has <MathTex tex={T.rank} />. Reproducing it through shared
					modes therefore needs
					<MathTex tex={String.raw`M \ge |G|`} />, and approximating it within spectral distance
					below one needs the same.
				</p>
				{#snippet proof()}
					<p>
						<MathTex tex="H" /> is a product of an <MathTex tex={String.raw`n^2 \times M`} /> and an
						<MathTex tex={String.raw`M \times n^2`} /> matrix. In <MathTex tex="K" />, the entry
						depends only on the row sum <MathTex tex="s = x_i + x_j" /> and the column sum <MathTex
							tex="s' = x_k + x_l"
						/>, and equals one exactly when <MathTex tex="s' = -s" />. Choosing one row for each
						value of <MathTex tex="s" /> and the matching column for <MathTex tex="-s" /> gives a <MathTex
							tex={String.raw`|G|\times|G|`}
						/> permutation submatrix, so the rank is <MathTex tex="|G|" />. A matrix within spectral
						distance below one of a permutation matrix is invertible, which gives the approximate
						version.
					</p>
				{/snippet}
			</Theorem>
			<p>
				This bounds one route to the answer, not every classifier, and it points to two remedies.
				One is classical: store every pair sum in an indexed memory and look up the complement,
				which settles all-query Match-4 in <MathTex tex="O(n^2)" /> and, with colour coding <Cite
					refs={BIB}
					id="alon"
				/>, Match-<MathTex tex="k" /> in <MathTex tex={String.raw`O(n^{\lceil k/2\rceil})`} />. The
				other, in the next section, needs no indexing. Section 6 shows that giving Feynman attention
				the primitives of that construction, and width above <MathTex tex="|G|" />, is still not
				enough for gradient descent to find it.
			</p>
		</section>

		<section id="algebra">
			<h2><span class="n">5</span>Arity in the group algebra</h2>
			<p>
				Embed each token by its characters, <MathTex tex={T.phi} />. A Hadamard product of
				embeddings is the embedding of the sum: Hadamard-product attention computes in the group
				algebra, where multiplication is convolution. Pooling a Hadamard power over tokens gives a
				power sum, and power sums determine the elementary symmetric polynomials whose coefficients
				count zero-sum subsets.
			</p>
			<Theorem n={5} name="Every arity at linear cost" evidence="checked" id="thm5">
				<p>
					For every finite abelian group, every <MathTex tex="k" /> and every input, with
					<MathTex tex="E_0 = \mathbf 1" />,
				</p>
				<MathTex display tex={T.newton} />
				<p>
					where <MathTex tex={String.raw`N_{i,k}`} /> is the number of <MathTex
						tex="(k-1)"
					/>-subsets of the other positions whose values sum with <MathTex tex="x_i" /> to zero. Every
					step is a Hadamard product, a Hadamard power or a sum over tokens, and all arities up to <MathTex
						tex="k"
					/> together cost
				</p>
				<MathTex display tex={T.cost} />
				{#snippet proof()}
					<p>
						In the group algebra <MathTex tex={String.raw`\mathbb C[G]`} />, with basis
						<MathTex tex="e_g" /> and <MathTex tex={String.raw`e_a * e_b = e_{a + b}`} />,
					</p>
					<MathTex display tex={T.gen} />
					<p>
						Newton's identities hold in any commutative algebra over the rationals, with power sums
						<MathTex tex={String.raw`P_j = \sum_t e_{x_t}^{*j} = \sum_t e_{j x_t}`} />. Removing
						token
						<MathTex tex="i" /> divides the generating function by <MathTex
							tex={String.raw`1 + z e_{x_i}`}
						/>:
					</p>
					<MathTex display tex={T.excl} />
					<p>
						The count is the coefficient of <MathTex tex={String.raw`e_{-x_i}`} /> in that series:
					</p>
					<MathTex display tex={T.coef} />
					<p>
						The Fourier transform turns every convolution into a Hadamard product, which gives the
						formula. Power sums cost <MathTex tex={String.raw`O(kn|G|)`} />, the recursion <MathTex
							tex={String.raw`O(k^2|G|)`}
						/> and the read-out <MathTex tex={String.raw`O(kn|G|)`} /> per arity. We checked the counts
						against enumeration on 60 random tables for <MathTex tex="k" /> = 2 to 6 in Python, and in
						this site's test suite; the demo below runs the same check live.
					</p>
				{/snippet}
			</Theorem>
			<NewtonDemo />
			<p>
				The width is not incidental. Exact counting reads every character, and a lower bound says
				that something of that size is needed:
			</p>
			<Theorem kind="Proposition" n={6} name="Width lower bound" evidence="open">
				<p>
					Any model that summarises the context into a query-independent state and reads it out
					bilinearly against the query needs <MathTex tex={T.width} />. The proof places one element <MathTex
						tex="h"
					/> among zeros, which makes the answer matrix a permutation plus a rank-one term; the write-up,
					and the extension to non-linear read-outs, are in progress.
				</p>
			</Theorem>

			<h3>Newton attention</h3>
			<p>
				Theorem 5 needs the characters of a known group. A layer has to learn them, and it should
				work for relations that are not zero sums. Newton attention keeps the algebra and learns the
				features. Each token gets <MathTex tex="r" /> complex channels with a learned phase and a learned
				gate,
			</p>
			<MathTex display tex={T.nPhase} />
			<p>
				so a character is one linear map away. Leave-one-out power sums and Newton's identities
				give, for every query <MathTex tex="q" />, the elementary symmetric polynomials of the other
				tokens,
			</p>
			<MathTex display tex={T.nPow} />
			<p>and the layer reads out every arity up to <MathTex tex="K" /> at once:</p>
			<MathTex display tex={T.nOut} />
			<Theorem kind="Remark" n={1} name="What the layer computes">
				<p>Each read-out term is an exact sum over distinct subsets that contain the query,</p>
				<MathTex display tex={T.nSubset} />
				<p>
					so the term with index <MathTex tex="m" /> is attention of arity <MathTex tex="m+1" />
					with a product kernel, every arity costs <MathTex tex={T.nCost} />, and no tuple is ever
					enumerated. Repeated indices, which make naive factorised higher-order attention count a
					token twice, are removed exactly by the alternating terms of the recursion. The output
					projection weighs the arities: that is where the data chooses.
				</p>
			</Theorem>
		</section>

		<section id="experiments">
			<h2><span class="n">6</span>Experiments</h2>
			<h3>6.1 In the browser</h3>
			<p>
				All runs use one layer unless noted, width 64, four heads and 4,000 steps on freshly sampled
				data, with 1,024 held-out tables. These numbers come from this site's jax-js engine, one
				seed each.
			</p>
			<table class="nums">
				<caption>Table 1. Held-out token accuracy, measured in a browser on WebGPU.</caption>
				<thead>
					<tr
						><th>Model</th><th class="r">SET</th><th class="r">Params</th><th class="r"
							>Pointer chase</th
						><th class="r">Params</th></tr
					>
				</thead>
				<tbody>
					<tr class="hi"
						><td>Cubic, 1 layer</td><td class="r">100%</td><td class="r">60k</td><td class="r"
							>84.5%</td
						><td class="r">63k</td></tr
					>
					<tr class="hi"
						><td>Feynman (2 rounds on SET, 4 on chase)</td><td class="r">100%</td><td class="r"
							>59k</td
						><td class="r">100%</td><td class="r">61k</td></tr
					>
					<tr
						><td>Strassen</td><td class="r">95.8%</td><td class="r">60k</td><td class="r">·</td><td
							class="r"
						></td></tr
					>
					<tr
						><td>Tree (Chakrabarti et al.)</td><td class="r">76.4%</td><td class="r">60k</td><td
							class="r">·</td
						><td class="r"></td></tr
					>
					<tr
						><td>Standard, 3 layers</td><td class="r">·</td><td class="r"></td><td class="r"
							>94.2%</td
						><td class="r">154k</td></tr
					>
					<tr
						><td>Standard, 2 layers</td><td class="r">64.4%</td><td class="r">102k</td><td class="r"
							>88.9%</td
						><td class="r">104k</td></tr
					>
					<tr
						><td>Standard, 1 layer</td><td class="r">60.5%</td><td class="r">52k</td><td class="r"
							>64.5%</td
						><td class="r">54k</td></tr
					>
					<tr class="base"
						><td>Majority class</td><td class="r">53.5%</td><td class="r"></td><td class="r">·</td
						><td class="r"></td></tr
					>
				</tbody>
			</table>

			<h3>6.2 Replication across seeds</h3>
			<p>
				The same operators in the research harness on cloud GPUs, three seeds each, 4,000 steps. The
				SET tasks are scored by balanced accuracy, the mean of the per-class hit rates, so always
				answering the majority class scores 50%.
			</p>
			<ReplicationTable
				rows={[...baseline, ...newton(newtonA), ...newtonB]}
				tasks={BASE_TASKS}
				models={BASE_MODELS}
				caption="Table 2. Mean of three seeds; each dot is one seed on a strip from chance to 100%. SET tasks: balanced accuracy, chance 50%. Pointer chase and three-hop: accuracy over eight answers, chance 12.5%."
			/>
			<p>
				SET is solved by cubic attention, Feynman attention and Newton attention at rank 256 on
				every seed; no depth of standard attention gets past 62%. On four-card SET dense quartic
				attention learns on two of three seeds, Newton attention at rank 256 reaches 76% on all
				three, and everything else stays at exactly chance. On three-hop composition Feynman
				attention succeeds on two of three seeds. On pointer chasing three standard layers match
				Feynman attention, with 2.5 times the parameters. Newton attention has no routing, and at
				rank 32 it is weak on both chain tasks.
			</p>

			<h3>6.3 The Match-<MathTex tex="k" /> ladder</h3>
			<p>
				Match-<MathTex tex="k" /> on <MathTex tex={String.raw`\mathbb Z_3^4`} /> for <MathTex
					tex="k"
				/> = 3, 4, 5 (twelve cards for <MathTex tex="k = 3" />, nine otherwise, so that about half
				the cards are positive), and a task whose label is the smallest arity at which a card
				completes a zero sum: none, 3, 4 or 5. Every operator, three seeds, 6,000 steps.
			</p>
			<ReplicationTable
				rows={[...phaseA, ...newton(newtonA), ...newtonB]}
				tasks={LADDER_TASKS}
				models={LADDER_MODELS}
				caption="Table 3. Balanced accuracy, mean of three seeds with each seed as a dot. Chance is 50% for Match-k and 25% for the smallest-arity task."
			/>
			<p>
				The ladder separates the operators by arity. Standard attention, at any depth we tried, gets
				no further than 66% on Match-3 and stays at chance from Match-4 up. Cubic attention and
				Feynman attention solve Match-3 and stop there. Dense quartic attention learns Match-4 on
				two of three seeds, after a long plateau and a sudden snap (Figure 5), as the leap of a
				four-way relation predicts. The Feynman attention variant that has every primitive of the
				Newton construction (pooled modes, self-products, products of modes) stays at exactly chance
				on Match-4 at width 64, 128 and 192, above the <MathTex tex="|G| = 81" /> that Proposition 6 asks
				for: the composition is representable, and it is not found. Removing its cubic sector loses Match-3
				as well.
			</p>
			<figure class="wide fig">
				<CurvesFigure
					rows={[...phaseA, ...newton(newtonA), ...newtonB]}
					panels={[
						{ task: 'zs3', title: 'Match-3' },
						{ task: 'zs4', title: 'Match-4' }
					]}
					models={CURVE_MODELS}
				/>
				<figcaption>
					<b>Figure 5.</b> Held-out balanced accuracy through training, mean of three seeds. Models of
					the task's order sit at chance and then snap; models below it never leave. Newton attention
					climbs without the long plateau; at rank 32 it stops short of exact.
				</figcaption>
			</figure>

			<h3>6.4 Newton attention</h3>
			<p>
				The order ablation is the cleanest result so far. Cap Newton attention at order 3 and
				Match-4 stays at exactly 50% on every seed; cap it at 4 and Match-5 does the same, even with
				20,000 steps. Offer order 6 and both leave chance on every seed. The same holds at rank 128
				(Table 6). Gradient descent uses the arity when the layer offers it.
			</p>
			<ReplicationTable
				rows={newtonA}
				tasks={[
					{ id: 'zs4', label: 'Match-4' },
					{ id: 'zs5', label: 'Match-5' }
				]}
				models={ORDER_MODELS}
				caption="Table 4. Newton attention with its order capped, rank 32, four heads. Balanced accuracy, three seeds."
			/>
			<p>
				Width is what it needs. At rank 32 it plateaus near 80% on Match-3 and 62% on Match-4, and
				20,000 steps do not move it. With one head, accuracy on Match-4 rises steadily with the
				number of channels, though without the sharp step at <MathTex tex="r = 40" /> conjugate pairs
				that exact character counting would suggest. With four heads of rank 256 it solves SET and Match-3
				on every seed, reaches 95% on the smallest-arity task and 71% on Match-4, and is the only model
				above chance on Match-5, at 57% on all three seeds.
			</p>
			<ReplicationTable
				rows={newtonA}
				tasks={[{ id: 'zs4', label: 'Match-4' }]}
				models={RANK_MODELS}
				caption="Table 5. Newton attention on Match-4 by rank, one head, order 6, 10,000 steps. Balanced accuracy, three seeds."
			/>
			{#if newtonB.length}
				<div class="wide">
					<ReplicationTable
						rows={newtonB}
						tasks={[
							...LADDER_TASKS,
							{ id: 'set', label: 'SET' },
							{ id: 'set4', label: 'Four-card SET' }
						]}
						models={WIDE_MODELS}
						caption="Table 6. Wider Newton attention, four heads, 6,000 steps, with its order ablation and width-matched baselines. Balanced accuracy, three seeds."
					/>
				</div>
				<p>
					Most of its parameters are in the read-out: at rank 256 the projection takes four heads of
					six arities of 256 complex channels to width 64, 0.79M of 0.96M parameters. Parameters
					alone do not explain the result: cubic attention widened to 0.52M and three standard
					layers widened to 2.4M stay at chance on Match-4 and Match-5. Dense quartic attention is
					still better on Match-4, 84% on two of three seeds with 69k parameters, at a cost that
					grows as
					<MathTex tex="n^4" />. A read-out that shares weights across arities is the next step.
				</p>
			{:else}
				<p class="pending">Running now: rank 128 and 256, with width-matched baselines.</p>
			{/if}

			<h3>6.5 Next</h3>
			<p>Established benchmarks, each on its own published protocol:</p>
			<table class="nums plan">
				<caption>Table 7. Planned benchmarks and the published numbers to beat.</caption>
				<thead><tr><th>Benchmark</th><th>Why</th><th>To beat</th></tr></thead>
				<tbody>
					<tr>
						<td>Match3, HOMA protocol (N = 6, 8)</td>
						<td>Direct arity test</td>
						<td>HOMA 99.3% and 92.5% <Cite refs={BIB} id="homa" /></td>
					</tr>
					<tr>
						<td>CLUTRR, train on chains of 2 to 3, test to 10</td>
						<td>Composing relations</td>
						<td>Edge Transformer 58.1% <Cite refs={BIB} id="bergen" /></td>
					</tr>
					<tr>
						<td>CLRS-30 subset, train n = 16, test n = 64</td>
						<td>Triplet algorithms (Floyd–Warshall, SCC, LCS, optimal BST)</td>
						<td
							>FloydNet 81.4% on Floyd–Warshall, fixed data <Cite
								refs={BIB}
								id={['floydnet', 'velickovic']}
							/></td
						>
					</tr>
					<tr>
						<td>p-hop, p = 16</td>
						<td>Depth versus arity</td>
						<td>3 standard layers 97.2%, one layer 48.9%</td>
					</tr>
				</tbody>
			</table>
		</section>

		<section id="related">
			<h2><span class="n">7</span>Related work</h2>
			<p>
				<b>Higher-order attention.</b> 2-simplicial attention <Cite refs={BIB} id="clift" /> introduced
				third-order scores and Hadamard pair values, with virtual entities as pair endpoints; Sanford
				et al. proved third-order attention solves Match3 where pairwise attention needs large width <Cite
					refs={BIB}
					id="sanford23"
				/>; Roy et al. made it fast <Cite refs={BIB} id="roy" />; Strassen attention <Cite
					refs={BIB}
					id="kozachinskiy"
				/> and poly-attention <Cite refs={BIB} id="chakrabarti" /> chart cheaper polynomial scores and
				their limits, and Alman and Song the complexity of the dense case <Cite
					refs={BIB}
					id="alman"
				/>. All fix the order. N-simplicial attention shows a constant key recovers lower orders <Cite
					refs={BIB}
					id="dussolle"
				/>, close to our vacuum token; HOMA fuses a pairwise and a triadic channel with a learned
				gate after separate softmaxes
				<Cite refs={BIB} id="homa" />; Nexus nests attention to a fixed depth <Cite
					refs={BIB}
					id="nexus"
				/>. Higher-order linear attention composes attention matrices through prefix summaries, with
				repeated indices allowed and orders two and three worked out <Cite refs={BIB} id="hla" />.
				We found no operator that offers several arities inside one softmax, or that sums over
				distinct subsets of every size through Newton's identities.
			</p>
			<p>
				<b>Relational and algorithmic reasoning.</b> Edge transformers <Cite
					refs={BIB}
					id="bergen"
				/> and FloydNet
				<Cite refs={BIB} id="floydnet" /> keep pair states and attend over pivots, the strongest results
				on composing relations and on CLRS <Cite refs={BIB} id="velickovic" />.
				<b>Trees and recursion.</b>
				Sums over trees with products of local weights go back to the inside algorithm and DIORA <Cite
					refs={BIB}
					id="drozdov"
				/>; adaptive depth to universal transformers <Cite refs={BIB} id="dehghani" />.
				<b>Sets and algebra.</b>
				Power sums underlie sum-decomposition of set functions and its width limits <Cite
					refs={BIB}
					id={['zaheer', 'wagstaff']}
				/>; Janossy pooling averages a function over k-subsets <Cite refs={BIB} id="janossy" />; and
				networks learn group operations through Fourier features <Cite refs={BIB} id="nanda" />.
			</p>
		</section>

		<section id="limits">
			<h2><span class="n">8</span>Limitations</h2>
			<ul>
				<li>Theorem 1 is about means of scores, not a lower bound for every classifier.</li>
				<li>
					Theorem 5 is a construction. Newton attention learns it exactly for three-way relations
					and only in part beyond: 71% on Match-4 and 57% on Match-5 at rank 256.
				</li>
				<li>
					The width <MathTex tex="|G|" /> grows exponentially with the number of attributes, and the tasks
					so far are synthetic and small.
				</li>
				<li>
					Newton attention has no routing, so on chain tasks it is weaker than Feynman attention,
					and its read-out is large: 0.79M of its 0.96M parameters at rank 256.
				</li>
			</ul>
		</section>

		<section id="appendix">
			<h2>Appendix A. Every measurement so far</h2>
			<p>
				Held-out token accuracy by task and model from the operator search that preceded this
				report, including operators the main text drops.
			</p>
			<EvidenceMatrix />
			<h2 class="app-b">Appendix B. Reproducing this report</h2>
			<p>
				The browser engine trains every model on this site with jax-js on WebGPU or WebAssembly. The
				research harness, the cloud runner and every raw result live in the repository's <code
					>research/</code
				>
				folder, alongside the plan this report follows; recorded browser runs are in
				<code>static/recorded/</code>.
			</p>
		</section>

		<section id="references" class="refs">
			<h2>References</h2>
			<ol>
				{#each BIB as r (r.id)}
					<li id="ref-{r.id}">
						{r.authors}.
						{#if r.url}<a href={r.url} rel="external">{r.title}</a>{:else}{r.title}{/if}.
						<span class="venue">{r.venue}, {r.year}.</span>
					</li>
				{/each}
			</ol>
		</section>
	</article>
</PageFrame>

<style>
	/* A text column with a margin for notes; figures may span both. No boxes, no rules
	   except the hairlines of tables: hierarchy comes from type and space. */
	.paper {
		--text: 660px;
		--gap: 44px;
		--side: 210px;
		max-width: calc(var(--text) + var(--gap) + var(--side) + 80px);
		margin: 0 auto;
		padding: 40px 40px 140px;
		font-size: 15px;
		line-height: 1.62;
		color: var(--color-ink-2);
	}
	.paper :global(:where(section, header) > *:not(.wide, .side)) {
		max-width: var(--text);
	}
	.title-block {
		padding-bottom: 6px;
	}
	h1 {
		margin: 0;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 44px;
		font-weight: 400;
		line-height: 1.08;
		letter-spacing: -0.01em;
		color: var(--color-ink);
	}
	.subtitle {
		margin: 8px 0 0;
		font-size: 18px;
		color: var(--color-ink-2);
	}
	.authors {
		margin: 14px 0 0;
		color: var(--color-ink);
	}
	.draft {
		margin-left: 12px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.side {
		float: right;
		clear: right;
		width: var(--side);
		margin: 4px 0 14px;
		font-size: 12.5px;
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.key {
		display: grid;
		gap: 4px;
		margin-top: 28px;
	}
	.ev-key {
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}
	.ev-key::before {
		content: '';
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink);
	}
	.ev-key.measured::before {
		background: var(--color-ink-3);
	}
	.ev-key.open::before {
		background: #444;
	}
	.abstract {
		margin: 26px 0 0;
		font-size: 14.5px;
		line-height: 1.6;
		color: var(--color-ink);
	}
	.abstract b,
	.contrib b {
		font-weight: 600;
	}
	section {
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	h2 {
		margin: 44px 0 12px;
		font-size: 22px;
		font-weight: 500;
		color: var(--color-ink);
	}
	h2 .n {
		margin-right: 12px;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		color: var(--color-ink-3);
	}
	h3 {
		margin: 28px 0 8px;
		font-size: 15px;
		font-weight: 600;
		color: var(--color-ink);
	}
	p {
		margin: 0 0 14px;
	}
	.contrib {
		font-size: 14px;
	}
	.caveat,
	.pending {
		font-size: 14px;
		color: var(--color-ink-3);
	}
	.fig {
		clear: both;
		margin: 22px 0 28px;
	}
	.fig.split {
		display: grid;
		grid-template-columns: minmax(0, 1fr) var(--side);
		gap: var(--gap);
		align-items: end;
	}
	.fig-key {
		display: block;
		margin-top: 10px;
	}
	figcaption {
		margin-top: 12px;
		max-width: var(--text);
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.split figcaption {
		margin: 0;
	}
	figcaption b {
		color: var(--color-ink-2);
		font-weight: 600;
	}
	.nums {
		width: 100%;
		margin: 12px 0 18px;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	.nums caption {
		caption-side: top;
		margin-bottom: 8px;
		text-align: left;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.nums th {
		padding: 0 8px 7px 0;
		border-bottom: 1px solid #262626;
		font-weight: 400;
		text-align: left;
		color: var(--color-ink-3);
	}
	.nums td {
		padding: 5px 8px 5px 0;
		vertical-align: top;
	}
	.nums tbody tr:first-child td {
		padding-top: 9px;
	}
	.nums tbody tr:last-child td {
		padding-bottom: 9px;
		border-bottom: 1px solid #262626;
	}
	.nums .r {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	.nums tr.hi td {
		color: var(--color-ink);
	}
	.nums tr.base td {
		color: var(--color-ink-3);
	}
	.plan td:first-child {
		color: var(--color-ink);
	}
	ul {
		margin: 0 0 14px;
		padding-left: 20px;
	}
	li {
		margin-bottom: 6px;
	}
	.app-b {
		font-size: 18px;
	}
	code {
		font-family: var(--font-mono);
		font-size: 0.9em;
		color: var(--color-ink);
	}
	.refs ol {
		padding-left: 22px;
		font-size: var(--text-sm);
		line-height: 1.55;
	}
	.refs li {
		margin-bottom: 8px;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	.refs a {
		color: var(--color-ink);
	}
	.venue {
		color: var(--color-ink-3);
	}
	/* one column: notes fall into the text, figures stack */
	@media (max-width: 1179px) {
		.paper {
			max-width: calc(var(--text) + 80px);
		}
		.side {
			float: none;
			width: auto;
			max-width: var(--text);
			margin: 0 0 14px;
		}
		.fig.split {
			display: block;
		}
		.split figcaption {
			margin-top: 12px;
		}
	}
	@media (max-width: 700px) {
		.paper {
			padding: 24px 18px 100px;
			font-size: 14.5px;
		}
		h1 {
			font-size: 32px;
		}
	}
</style>
