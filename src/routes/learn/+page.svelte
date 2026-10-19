<script lang="ts">
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { resolve } from '$app/paths';
	import { Cards, Cube, FunctionIcon, Layers, Link, Network } from '#lib/ui/icons.ts';
	import type { Card } from '#lib/set/cards.ts';

	let section = $state('pairwise');

	const sections = [
		{ id: 'pairwise', label: 'Pairwise attention', icon: Network },
		{ id: 'product', label: 'A generalized dot product', icon: FunctionIcon },
		{ id: 'cubic', label: 'Cubic polyattention', icon: Cube },
		{ id: 'barrier', label: 'The coupling barrier', icon: Layers },
		{ id: 'set', label: 'SET as Match3', icon: Cards },
		{ id: 'binding', label: 'Values as binding', icon: Link }
	];

	// one attribute, the three cases
	const cases: { name: string; cards: Card[]; e: number; all: number }[] = [
		{
			name: 'Count: all equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[1, 2, 2, 2]
			],
			e: 3,
			all: 1
		},
		{
			name: 'Count: two equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			],
			e: 1,
			all: 0
		},
		{
			name: 'Count: all different',
			cards: [
				[0, 0, 0, 0],
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			],
			e: 0,
			all: 0
		}
	];
</script>

<svelte:head>
	<title>Learn | Polyformer</title>
</svelte:head>

<PageFrame rail={sections} active={section} onselect={(id) => (section = id)}>
	<article class="learn">
		<header class="intro">
			<h1 class="page-title">From pairs to triples</h1>
			<p class="lede">
				Attention lets each token score every other token. Cubic polyattention lets each token score
				every ordered pair of other tokens, with one trilinear product. This page builds it up in
				six steps and shows why it learns SET where every degree-2 design stalls.
			</p>
		</header>

		<section id="pairwise">
			<h2><span class="n">1</span>Pairwise attention</h2>
			<p>
				A query <MathTex tex="Q_i" /> scores each key <MathTex tex="K_j" /> with a dot product, the scores
				are normalized over <MathTex tex="j" />, and the output is a weighted sum of values.
			</p>
			<MathTex
				display
				tex={'P_{ij} = \\operatorname{softmax}_j \\frac{\\langle Q_i, K_j \\rangle}{\\sqrt{d}}, \\qquad Y_i = \\sum_j P_{ij} V_j'}
			/>
			<p>
				Every score involves exactly two tokens. Relations among three tokens must be assembled
				indirectly, across heads or layers.
			</p>
		</section>

		<section id="product">
			<h2><span class="n">2</span>A generalized dot product</h2>
			<p>
				The dot product sums the products of matching coordinates. Nothing stops at two factors: the
				trilinear form multiplies three.
			</p>
			<MathTex
				display
				tex="\langle a, b \rangle = \sum_c a_c b_c \qquad\longrightarrow\qquad \langle a, b, e \rangle = \sum_c a_c\, b_c\, e_c = \langle a,\, b \odot e \rangle"
			/>
			<p>
				Written with the Hadamard product <MathTex tex="\odot" />, it is still one dot product: the
				query against the elementwise product of two keys. It is large only when all three vectors
				agree on the same coordinates.
			</p>
		</section>

		<section id="cubic">
			<h2><span class="n">3</span>Cubic polyattention</h2>
			<p>
				Give each token one query and two role-specific keys and values. Query <MathTex tex="i" />
				scores the ordered pair <MathTex tex="(j, k)" />, with <MathTex tex="j" /> in role 1 and
				<MathTex tex="k" /> in role 2:
			</p>
			<MathTex
				display
				tex={"A_{ijk} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\rangle, \\qquad P_{ijk} = \\frac{\\exp(A_{ijk}/\\sqrt{d})}{\\sum_{j'k'} \\exp(A_{ij'k'}/\\sqrt{d})}"}
			/>
			<MathTex
				display
				tex={'D_{jk} = V^1_j \\odot V^2_k, \\qquad Y_i = \\sum_{j,k} P_{ijk}\\, D_{jk}'}
			/>
			<figure class="ports">
				<svg viewBox="0 0 300 150" aria-hidden="true">
					<polygon points="150,22 62,124 238,124" class="mem" />
					<circle cx="150" cy="22" r="7" class="port" />
					<rect x="55" y="117" width="14" height="14" class="port" />
					<polygon points="238,115 247,124 238,133 229,124" class="port" />
					<text x="150" y="8" class="t">query i</text>
					<text x="38" y="146" class="t">role 1 j</text>
					<text x="262" y="146" class="t">role 2 k</text>
				</svg>
				<figcaption class="hint">
					One hyperedge. Roles are carried by the separate projections, so <MathTex tex="(j,k)" /> and
					<MathTex tex="(k,j)" /> are different pairs even though <MathTex tex="\odot" /> commutes.
				</figcaption>
			</figure>
			<p>
				The softmax runs jointly over all <MathTex tex="n^2" /> ordered pairs. Pairs that reuse the query
				or repeat a key are masked, and a sink token at position 0 gives every query somewhere to put
				weight it does not need. Both contractions are matrix products,
				<MathTex tex={'(Q_i \\odot K^1)\\,K^{2\\top}'} /> for the scores and
				<MathTex tex="P_i V^2" /> for the values, so the cost is <MathTex tex="O(n^3 d)" /> with no <MathTex
					tex="n^3 d"
				/> intermediate.
			</p>
		</section>

		<section id="barrier">
			<h2><span class="n">4</span>The coupling barrier</h2>
			<p>
				Earlier triple-attention designs keep every score term degree 2: a sum of pairwise dot
				products on the edges of the triangle. The Columbia tree uses the path
				<MathTex tex="i - j - k" />; Strassen attention uses all three edges.
			</p>
			<MathTex display tex={'A^{\\text{deg 2}}_{ijk} = f(i,j) + g(j,k) + h(i,k)'} />
			<p>
				Fix the query and double-center the score matrix over <MathTex tex="(j,k)" />. The terms
				that depend on <MathTex tex="(i,j)" /> or <MathTex tex="(i,k)" /> alone cancel, and what remains
				is the centered <MathTex tex="g(j,k)" />, which is the same for every query:
			</p>
			<MathTex
				display
				tex={'\\tilde A^{\\text{deg 2}}_{i,jk} = \\tilde g(j,k) \\qquad \\text{vs.} \\qquad \\tilde A^{\\text{cubic}}_{i,jk} = \\sum_c Q_{ic}\\, \\tilde K^1_{jc}\\, \\tilde K^2_{kc}'}
			/>
			<p>
				So in any degree-2 head the way <MathTex tex="j" /> and <MathTex tex="k" /> couple is decided
				before the query arrives. The query can only re-weight <MathTex tex="j" /> and
				<MathTex tex="k" /> separately. In the cubic head each query mixes up to
				<MathTex tex="d" /> coupling patterns of its own: which pairs belong together depends on who is
				asking.
			</p>
		</section>

		<section id="set">
			<h2><span class="n">5</span>SET is Match3 over <MathTex tex={'\\mathbb{Z}_3^4'} /></h2>
			<p>
				A SET card has four attributes with three values each, so a card is a vector in
				<MathTex tex={'\\mathbb{Z}_3^4'} />. Three cards form a SET when every attribute is all the
				same or all different, which is exactly <MathTex tex="a + b + c \equiv 0 \pmod 3" />. Write <MathTex
					tex={'e_{ab}'}
				/> for “cards a and b agree on this attribute”. Then, per attribute,
			</p>
			<MathTex
				display
				tex={'\\mathbb{1}[\\text{SET}] = 1 - (e_{ab} + e_{bc} + e_{ac}) + 3\\,\\mathbb{1}[a = b = c]'}
			/>
			<div class="cases">
				{#each cases as c (c.name)}
					<div class="case">
						<div class="trio">
							{#each c.cards as card, i (i)}<SetCard {card} width={52} />{/each}
						</div>
						<div class="case-name">{c.name}</div>
						<div class="hint num">
							1 − {c.e} + 3·{c.all} = {1 - c.e + 3 * c.all}
						</div>
					</div>
				{/each}
			</div>
			<p>
				The agreement terms are pairwise, so a degree-2 head can express them. The last term is not:
				with one-hot attribute embeddings, <MathTex
					tex={'\\mathbb{1}[a=b=c] = \\langle a,\\, b \\odot c\\rangle'}
				/>, a single trilinear product. Pairwise logits are also blind on average: every pair of
				cards completes exactly one SET, so any score built from pairs has the same mean on SET and
				non-SET triples.
			</p>
			<p>
				A cubic head can score the whole rule at once. Place each attribute value
				<MathTex tex="v" /> on the unit circle at <MathTex tex="\omega^v" />, with
				<MathTex tex={'\\omega = e^{2\\pi i/3}'} />. Then
			</p>
			<MathTex
				display
				tex={'\\mathbb{1}[a + b + c \\equiv 0] = \\tfrac{1}{3}\\bigl(1 + 2\\,\\mathrm{Re}(\\omega^a \\omega^b \\omega^c)\\bigr)'}
			/>
			<MathTex
				display
				tex={'\\mathrm{Re}(z_1 z_2 z_3) = x_1x_2x_3 - x_1y_2y_3 - y_1x_2y_3 - y_1y_2x_3, \\qquad z = x + iy'}
			/>
			<p>
				and the real part of a product of three unit numbers is four trilinear products of their
				cosines and sines. Four channels per attribute make sixteen, one head of the bench’s width:
				it scores every SET at 4 and every other triple at most 2.5.
			</p>
			<p>
				The task in the <a href={resolve('/compare')}>SET bench</a> deals 12 cards and asks, for each
				card, whether it belongs to some SET on the table.
			</p>
		</section>

		<section id="binding">
			<h2><span class="n">6</span>Values as binding</h2>
			<p>
				Scores choose pairs; values decide what a pair says. The Hadamard pair value multiplies the
				two keys’ features channel by channel, so a channel is active only when both tokens carry
				it. It is the diagonal of a richer object, the pair moment:
			</p>
			<MathTex
				display
				tex={'M_i = V^{1\\top} P_i\\, V^2 = \\sum_{j,k} P_{ijk}\\, V^1_j V^{2\\top}_k, \\qquad \\operatorname{diag}(M_i) = Y_i'}
			/>
			<p>
				Each entry <MathTex tex={'(M_i)_{ab}'} /> asks: how much does the query’s chosen pair have feature
				<MathTex tex="a" /> in role 1 together with feature <MathTex tex="b" /> in role 2? The
				<a href={resolve('/explore')}>linked tensor lab</a> shows this matrix for the trained model.
			</p>
		</section>
	</article>
</PageFrame>

<style>
	.learn {
		max-width: 760px;
		padding: 28px 28px 80px 40px;
	}
	.intro {
		padding-bottom: 20px;
		border-bottom: 1px solid var(--color-edge);
	}
	section {
		padding: 26px 0 6px;
		border-bottom: 1px solid #1c1c1c;
		scroll-margin-top: calc(var(--bar-h) + 12px);
	}
	section:last-child {
		border-bottom: 0;
	}
	h2 {
		display: flex;
		align-items: baseline;
		gap: 12px;
		font-size: var(--text-lg);
		font-weight: 500;
		letter-spacing: -0.01em;
		margin-bottom: 10px;
	}
	.n {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
		width: 14px;
	}
	p {
		color: var(--color-ink-2);
		line-height: 1.65;
		margin: 0 0 12px;
		max-width: 68ch;
	}
	p :global(.katex) {
		color: var(--color-ink);
	}
	a {
		color: var(--color-ink);
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
	}
	a:hover {
		text-decoration-color: var(--color-ink);
	}
	section :global(.math.display) {
		margin: 4px 0 14px;
		padding: 10px 16px;
		background: var(--color-panel);
		border: 1px solid #1f1f1f;
		border-radius: var(--radius-ui);
	}
	.ports {
		margin: 4px 0 16px;
		display: flex;
		align-items: center;
		gap: 22px;
	}
	.ports svg {
		width: 240px;
		flex: none;
	}
	.ports .mem {
		fill: rgb(245 245 245 / 0.12);
		stroke: #f5f5f5;
		stroke-width: 1.3;
		stroke-linejoin: round;
		filter: drop-shadow(0 0 5px rgb(255 255 255 / 0.25));
	}
	.ports .port {
		fill: var(--color-void);
		stroke: var(--color-ink);
		stroke-width: 1.5;
	}
	.ports .t {
		fill: var(--color-ink-2);
		font-size: 12px;
		text-anchor: middle;
	}
	.ports figcaption {
		max-width: 34ch;
		line-height: 1.55;
	}
	.cases {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
		margin: 2px 0 16px;
	}
	.case {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 12px;
		background: var(--color-panel);
		border: 1px solid #1f1f1f;
		border-radius: var(--radius-ui);
	}
	.trio {
		display: flex;
		gap: 4px;
	}
	.case-name {
		font-size: var(--text-sm);
	}
	@media (max-width: 760px) {
		.learn {
			padding: 18px 16px 60px;
		}
		.ports {
			flex-direction: column;
			align-items: flex-start;
		}
		.cases {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
