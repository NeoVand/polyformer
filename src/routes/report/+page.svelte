<script lang="ts">
	import { asset } from '$app/paths';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import Cite from '#lib/learn/Cite.svelte';
	import { BIB } from '#lib/report/bib.ts';
	import EvidenceMatrix from '#lib/report/EvidenceMatrix.svelte';
	import MarginalDemo from '#lib/report/MarginalDemo.svelte';
	import NewtonDemo from '#lib/report/NewtonDemo.svelte';
	import ReplicationTable from '#lib/report/ReplicationTable.svelte';
	import baseline from '#lib/report/results/baseline.json';
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

	// ── replicated results (research/results/baseline.jsonl, three seeds each) ──
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
		{ id: 'dspa4', label: 'DS-PA' }
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
		width: String.raw`d \;\ge\; |G| - 1`
	};
</script>

<svelte:head>
	<title>Report | Polyformer</title>
	<meta
		name="description"
		content="Let the data choose the arity: a working paper on higher-order attention, with proofs, live checks and every measured result."
	/>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'abstract', label: 'Paper', icon: Note },
		{ id: 'hierarchy', label: 'Arity', icon: FunctionIcon },
		{ id: 'dspa', label: 'DS-PA', icon: Feynman },
		{ id: 'algebra', label: 'Algebra', icon: Matrix },
		{ id: 'experiments', label: 'Results', icon: Compare },
		{ id: 'related', label: 'Related', icon: Book },
		{ id: 'appendix', label: 'Appendix', icon: Grid }
	]}
	active={section}
>
	<article class="paper" {@attach watch}>
		<header class="title-block">
			<p class="draft">Working draft, October 2026. Updated as results come in.</p>
			<h1>Let the data choose the arity</h1>
			<p class="subtitle">
				Higher-order attention, the group algebra, and attention as a sum over diagrams
			</p>
			<p class="authors">Mostafa “Neo” Mohsenvand</p>
			<p class="key">
				<span class="ev-key proved">Proved here</span>
				<span class="ev-key measured">Measured</span>
				<span class="ev-key open">Open</span>
				Every number on this page was measured with the code that runs this site.
			</p>
		</header>

		<section id="abstract">
			<h2 class="sr">Abstract</h2>
			<p class="abstract">
				Attention scores tokens in pairs, yet many relations hold only among three or more tokens at
				once. Higher-order attention captures them at a cost that grows as <MathTex tex="n^k" /> with
				the arity <MathTex tex="k" />, and every variant we know of fixes <MathTex tex="k" /> in advance.
				We study attention in which the data chooses the arity. For zero-sum relations over a finite abelian
				group we show that every score built from proper subsets of a <MathTex tex="k" />-tuple has
				the same mean on matching and non-matching tuples, so a
				<MathTex tex="k" />-way relation needs a <MathTex tex="k" />-way term (Theorem 1). We
				introduce DS-PA, a recursion that offers each token its own value, one other token, two
				tokens at once or a learned virtual mode inside a single softmax, and show that its output
				is a sum over Feynman-like trees whose weights are products of local softmax weights
				(Theorem 3). We locate why composing arity across rounds can fail, namely intermediates
				shared by every query, and bound the virtual modes this requires (Proposition 4). Finally,
				in the group algebra a Hadamard product is a convolution and pooling yields power sums, so
				rounds of products and pools compute elementary symmetric polynomials by Newton's
				identities: they count the <MathTex tex="k" />-way matches of every token for every <MathTex
					tex="k"
				/> at a cost linear in sequence length (Theorem 5). Experiments are under way; the results so
				far are reported with their limits.
			</p>
		</section>

		<section id="intro">
			<h2><span class="n">1</span>Introduction</h2>
			<p>
				A transformer head compares a query with one key at a time <Cite refs={BIB} id="vaswani" />.
				Whatever three tokens jointly imply has to be assembled from those pairwise scores over
				several layers, and for some relations that is provably expensive <Cite
					refs={BIB}
					id={['sanford23', 'kozachinskiy']}
				/>. Third-order attention scores a query against pairs of keys and solves such relations in
				one layer
				<Cite refs={BIB} id={['clift', 'sanford23', 'roy', 'chakrabarti']} />, at a cost of
				<MathTex tex="\Theta(n^3 d)" /> per head, and order-<MathTex tex="k" /> attention at
				<MathTex tex="\Theta(n^k d)" />
				<Cite refs={BIB} id="alman" />. The arity is a design decision made once, for every token
				and every input.
			</p>
			<p>
				This report asks whether the data can make that decision. Section 2 makes the arity
				hierarchy precise for zero-sum relations. Section 3 defines DS-PA, an operator that mixes
				arities inside one softmax and composes them over rounds, and gives its exact expansion as a
				sum over trees. Section 4 shows where composition breaks and why. Section 5 shows how it can
				work: in the group algebra, arity is the degree of a symmetric polynomial, and rounds of
				Hadamard products build every degree at linear cost. Section 6 reports experiments.
			</p>
			<p class="contrib">
				<b>Contributions so far.</b> (i) A Fourier-degree view of arity with a clean indistinguishability
				theorem. (ii) DS-PA and its tree expansion. (iii) A rank obstruction for shared intermediates.
				(iv) The Newton construction, with a matching width bound in progress. (v) Every result runs on
				this page.
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
			<p>
				In Fourier terms the label is a sum of characters of full support, orthogonal to every
				function of fewer coordinates. Two consequences follow. A logit built from pairs carries no
				first-moment signal for a three-way relation; and the relation has leap <MathTex tex="k" /> in
				the sense of Abbe et al.
				<Cite refs={BIB} id="abbe" />, which predicts the long plateau and sudden “snap” we see when
				a model of the right order trains on SET. The theorem is about means of scores. A softmax is
				not linear, so it is not by itself a lower bound on classifiers; genuine representational
				lower bounds for pairwise attention on Match3 need communication complexity <Cite
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
		</section>

		<section id="dspa">
			<h2><span class="n">3</span>DS-PA: arity as a choice inside one softmax</h2>
			<p>
				Each token keeps a state <MathTex tex="\Phi^r_t" />, starting from its value
				<MathTex tex="\Phi^0_t = v_t" /> and rebuilt for <MathTex tex="R" /> rounds:
			</p>
			<MathTex display tex={T.dspa} />
			<p>
				One softmax <MathTex tex="\pi" /> runs over every option of every sector, scored by a single trilinear
				vertex
				<MathTex tex={String.raw`\langle q_t, a\odot b\rangle`} /> over tokens, a vacuum token and the
				virtual modes. The sectors offer very different numbers of options (one leaf, <MathTex
					tex="n"
				/> hops,
				<MathTex tex="n^2" /> pairs), so each sector gets a fixed bias <MathTex tex={T.mu} />, which
				gives every sector equal prior mass at initialisation. A carry keeps finished results fixed,
				and the read-out is RMS-normalised. The name records the analogy that guided it: unrolled,
				the recursion is a Dyson–Schwinger equation resummed into diagrams.
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
				exactly: what adapts is how the weight is spread over trees of different sizes. The figure
				shows that spread for a model trained on SET.
			</p>

			{#if setModel}
				{@const d = setModel.diagram}
				{@const cards = setModel.layout as unknown as Card[]}
				<figure class="fig">
					<DiagramFlow
						head={d.perHead[0]}
						n={d.n}
						rounds={d.rounds}
						rows={[Array.from({ length: cards.length }, (_, i) => i + 1)]}
						root={root ?? d.token}
						onroot={(t) => (root = t)}
						pitch={20}
						column={140}
					>
						{#snippet label(t)}<SetCard card={cards[t - 1]} width={15} />{/snippet}
					</DiagramFlow>
					<div class="fig-key"><FlowLegend compact /></div>
					<figcaption>
						<b>Figure 1.</b> Theorem 3 for a DS-PA model trained in a browser on SET (two rounds, step
						1,500, 99.98% held out). Every token's state at every round, with the Feynman vertex of the
						sector it mostly uses. Lines show what one card reads, weighted by the share of its output
						they carry: each card in a SET reads its two partners at one cubic vertex. Hover or click
						a card to expand another.
					</figcaption>
				</figure>
			{/if}
		</section>

		<section id="composition">
			<h2><span class="n">4</span>Why composing arity can fail</h2>
			<p>
				Two rounds of cubic vertices reach degree four, yet a DS-PA layer does not learn four-card
				SET (Match-4 on
				<MathTex tex={String.raw`\mathbb Z_3^4`} />): it stays at the majority rate, where dense
				quartic attention succeeds (Appendix A). Degree is not the problem. A round-two contribution
				has the form
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
				This bounds one route to the answer, not every classifier. It also points to two remedies.
				One is classical: store every pair sum in an indexed memory and look up the complement,
				which settles all-query Match-4 in
				<MathTex tex="O(n^2)" /> and, with colour coding <Cite refs={BIB} id="alon" />, Match-<MathTex
					tex="k"
				/> in
				<MathTex tex={String.raw`O(n^{\lceil k/2\rceil})`} />. The other, in the next section, needs
				no indexing at all.
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
				Each step is an operation an attention layer can offer: a token's state times itself (a
				Hadamard power), pooling over tokens into a mode (a power sum), products between modes (the
				recursion), and a token's state times the modes (the read-out). A DS-PA variant with
				sum-pooled modes, self-products and round-dependent coefficients can therefore represent
				Match-<MathTex tex="k" /> for every <MathTex tex="k \le R" /> with width
				<MathTex tex="|G|" />, which is the architecture we are now training (Section 6.3). The
				width is not incidental:
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
			<p>
				So the trade-off is a triangle: dense order-<MathTex tex="k" /> attention needs width
				<MathTex tex="O(\log |G|)" /> and time <MathTex tex="n^k" />; composition needs width
				<MathTex tex="|G|" /> and time linear in <MathTex tex="n" />; pairwise attention, by Theorem
				1, sees nothing on average. Related constructions use power sums to represent set functions
				<Cite refs={BIB} id={['zaheer', 'wagstaff']} /> and Fourier features to perform group operations
				<Cite refs={BIB} id="nanda" />; what is new here is reading higher-order attention, and the
				choice of arity, through that algebra.
			</p>
		</section>

		<section id="experiments">
			<h2><span class="n">6</span>Experiments</h2>
			<h3>6.1 What is measured so far</h3>
			<p>
				All runs use one layer unless noted, width 64, four heads and 4,000 steps on freshly sampled
				data, with 1,024 held-out tables. The browser numbers come from this site's jax-js engine
				and are one seed each.
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
						><td>DS-PA (2 rounds on SET, 4 on chase)</td><td class="r">100%</td><td class="r"
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
			<p>
				On pointer chasing the gain is parameter efficiency, not a depth separation: three standard
				layers come close, and logarithmic-depth constructions for multi-hop tasks are known <Cite
					refs={BIB}
					id="sanford24"
				/>.
			</p>

			<h3>6.2 Replication across seeds</h3>
			<p>
				The same operators in the research harness on cloud GPUs, three seeds each, 4,000 steps. The
				SET tasks are scored by balanced accuracy, the mean of the per-class hit rates, so always
				answering the majority class scores 50%.
			</p>
			<ReplicationTable
				rows={baseline}
				tasks={BASE_TASKS}
				models={BASE_MODELS}
				caption="Table 2. Mean of three seeds; each dot is one seed on a strip from chance to 100%. SET tasks: balanced accuracy, chance 50%. Pointer chase and three-hop: accuracy over eight answers, chance 12.5%."
			/>
			<p>
				Replication changes two single-seed conclusions. On three-hop composition DS-PA succeeds on
				two of three seeds, where every other operator stays near chance. On four-card SET only
				dense quartic attention learns, and only on two of three seeds; cubic attention and DS-PA
				stay at exactly chance, which is the failure Section 4 explains. SET is solved by cubic
				attention and DS-PA on every seed, and no depth of standard attention gets past 62%. On
				pointer chasing three standard layers match DS-PA, with 2.5 times the parameters.
			</p>

			<h3>6.3 Next</h3>
			<p>
				Running now: the Match-<MathTex tex="k" /> ladder for <MathTex tex="k" /> = 3, 4 and 5 on
				<MathTex tex={String.raw`\mathbb Z_3^4`} />, and a task whose label is the smallest arity at
				which each card completes a zero-sum (none, 3, 4 or 5): the data literally chooses the
				arity. Every operator, three seeds, including a DS-PA variant with the primitives of Section
				5 and a width sweep to test Proposition 6. Then established benchmarks, each on its own
				published protocol:
			</p>
			<table class="nums plan">
				<caption>Table 3. Planned benchmarks and the published numbers to beat.</caption>
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
				/>. We found no operator that offers several arities inside one softmax, or that is defined
				by a diagram resummation.
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
				<b>Algebra.</b>
				Power sums underlie sum-decomposition of set functions and its width limits <Cite
					refs={BIB}
					id={['zaheer', 'wagstaff']}
				/>, and networks learn group operations through Fourier features <Cite
					refs={BIB}
					id="nanda"
				/>.
			</p>
		</section>

		<section id="limits">
			<h2><span class="n">8</span>Limitations</h2>
			<ul>
				<li>Theorem 1 is about means of scores, not a lower bound for every classifier.</li>
				<li>
					Theorem 5 is a construction. Whether training finds it is the experimental question of
					Section 6.3, and its width <MathTex tex="|G|" /> grows exponentially with the number of attributes.
				</li>
				<li>The results so far are single-seed, on synthetic tasks, at small scale.</li>
				<li>The operator's name will change before submission: “poly-attention” is taken.</li>
			</ul>
		</section>

		<section id="appendix">
			<h2>Appendix A. Every measurement so far</h2>
			<p>
				Held-out token accuracy by task and model. Filled cells were measured in this site's engine;
				outlined cells in the offline harness, one seed each, and are being replaced by the
				replication in Section 6.2.
			</p>
			<EvidenceMatrix />
			<h2 class="app-b">Appendix B. Reproducing this report</h2>
			<p>
				The browser engine trains every model on this site with jax-js on WebGPU or WebAssembly. The
				research harness and the cloud runner live in the repository's <code>research/</code>
				folder, alongside the plan this report follows; recorded runs are in
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
	.paper {
		max-width: 760px;
		padding: 36px 40px 140px;
		font-size: 15px;
		line-height: 1.66;
		color: var(--color-ink-2);
	}
	.title-block {
		padding-bottom: 10px;
	}
	.draft {
		margin: 0 0 14px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	h1 {
		margin: 0;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 42px;
		font-weight: 400;
		line-height: 1.08;
		color: var(--color-ink);
	}
	.subtitle {
		margin: 10px 0 0;
		font-size: 17px;
		color: var(--color-ink-2);
	}
	.authors {
		margin: 14px 0 0;
		color: var(--color-ink);
	}
	.key {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px 16px;
		margin: 18px 0 0;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.ev-key {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.ev-key::before {
		content: '';
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink);
	}
	.ev-key.measured::before {
		background: transparent;
		box-shadow: inset 0 0 0 1.5px var(--color-ink-2);
	}
	.ev-key.open::before {
		background: transparent;
		box-shadow: inset 0 0 0 1px #555;
	}
	.sr {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}
	.abstract {
		margin: 26px 0 0;
		padding: 16px 18px;
		border-radius: 8px;
		background: #0e0e0e;
		color: var(--color-ink);
		font-size: 14.5px;
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
		margin: 26px 0 8px;
		font-size: 15px;
		font-weight: 500;
		color: var(--color-ink);
	}
	p {
		margin: 0 0 14px;
	}
	.contrib,
	.caveat {
		font-size: 14px;
	}
	.caveat {
		color: var(--color-ink-3);
	}
	.fig {
		margin: 18px 0 26px;
	}
	.fig-key {
		margin-top: 10px;
	}
	figcaption {
		margin-top: 10px;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	figcaption b {
		color: var(--color-ink-2);
		font-weight: 500;
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
		padding: 0 8px 8px 0;
		font-weight: 400;
		text-align: left;
		color: var(--color-ink-3);
	}
	.nums td {
		padding: 7px 8px 7px 0;
		border-top: 1px solid #1a1a1a;
		vertical-align: top;
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
