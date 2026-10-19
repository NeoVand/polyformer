<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import DiagramSum from '#lib/learn/DiagramSum.svelte';
	import { REFERENCES } from '#lib/learn/references.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import type { Card } from '#lib/set/cards.ts';
	import { Atom, Book, Cube, Matrix, Note } from '#lib/ui/icons.ts';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { CUBIC, FEYNMAN, GENERAL, NEWTON, PAIRWISE } from '#lib/viz/computeGraphs.ts';

	const PARTS = [
		{ id: 'part-known', label: 'Known', icon: Book, title: 'What was known' },
		{ id: 'part-new', label: 'New here', icon: Cube, title: 'What this project adds' },
		{ id: 'part-beyond', label: 'Beyond', icon: Atom, title: 'Letting the data choose the arity' },
		{ id: 'part-algebra', label: 'Algebra', icon: Matrix, title: 'Arity is algebra' },
		{ id: 'references', label: 'Sources', icon: Note, title: 'References' }
	];
	const CHAPTERS: { id: string; title: string; part: string }[] = [
		{ id: 'pairwise', title: 'Pairwise attention', part: 'part-known' },
		{ id: 'product', title: 'A generalized dot product', part: 'part-known' },
		{ id: 'cubic', title: 'Cubic polyattention', part: 'part-known' },
		{ id: 'cost', title: 'What it costs', part: 'part-known' },
		{ id: 'degree2', title: 'Cheaper, degree-2 relatives', part: 'part-known' },
		{ id: 'barrier', title: 'The coupling barrier', part: 'part-new' },
		{ id: 'set', title: 'SET is Match3', part: 'part-new' },
		{ id: 'head', title: 'A head built by hand', part: 'part-new' },
		{ id: 'binding', title: 'Values as binding', part: 'part-new' },
		{ id: 'training', title: 'What training shows', part: 'part-new' },
		{ id: 'arity', title: 'Order k needs a k-way term', part: 'part-new' },
		{ id: 'feynman', title: 'Where Feynman diagrams come from', part: 'part-beyond' },
		{ id: 'dyson', title: 'Summing them all at once', part: 'part-beyond' },
		{ id: 'diagrams', title: 'Sum over diagrams', part: 'part-beyond' },
		{ id: 'sectors', title: 'Making it train', part: 'part-beyond' },
		{ id: 'chase', title: 'What Feynman attention learns', part: 'part-beyond' },
		{ id: 'composition', title: 'Composing arity does not train', part: 'part-algebra' },
		{ id: 'characters', title: 'A relation is agreement of phases', part: 'part-algebra' },
		{ id: 'newton', title: 'Every arity at once', part: 'part-algebra' },
		{ id: 'newtonattn', title: 'Newton attention', part: 'part-algebra' },
		{ id: 'transfer', title: 'Small relations teach large ones', part: 'part-algebra' }
	];
	const number = (id: string) => CHAPTERS.findIndex((c) => c.id === id) + 1;

	let section = $state('pairwise');
	const part = $derived(CHAPTERS.find((c) => c.id === section)?.part ?? section);

	/** The chapter crossing the middle band of the viewport drives the figure. */
	function watch(el: HTMLElement) {
		const io = new IntersectionObserver(
			(entries) => {
				for (const e of entries) if (e.isIntersecting) section = e.target.id;
			},
			{ rootMargin: '-40% 0px -55% 0px' }
		);
		el.querySelectorAll('section[id]').forEach((s) => io.observe(s));
		return () => io.disconnect();
	}

	// one attribute, the three cases
	const cases: { name: string; cards: Card[]; e: number; all: number }[] = [
		{
			name: 'All equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[1, 2, 2, 2]
			],
			e: 3,
			all: 1
		},
		{
			name: 'Two equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			],
			e: 1,
			all: 0
		},
		{
			name: 'All different',
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

<PageFrame rail={PARTS.map(({ id, label, icon }) => ({ id, label, icon }))} active={part}>
	<div class="learn">
		<article class="text" {@attach watch}>
			<header class="intro">
				<h1>From pairs to diagrams</h1>
				<p class="lede">
					How attention generalizes from pairs of tokens to triples, why that matters, how a
					Feynman-diagram view lets the data decide how many tokens each interaction joins, and how
					the algebra of the inputs turns every arity into something one layer can learn. Every
					chapter says where its content comes from:
				</p>
				<ul class="legend">
					<li><span class="mark prior"></span>Prior work, with references</li>
					<li><span class="mark new"></span>New in this project</li>
					<li><span class="mark measured"></span>Measured with this app's engine</li>
				</ul>
				<nav class="toc" aria-label="Chapters">
					{#each PARTS.slice(0, 4) as p (p.id)}
						<div class="toc-part">
							<span class="toc-title">{p.title}</span>
							<ol>
								{#each CHAPTERS.filter((c) => c.part === p.id) as c (c.id)}
									<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- in-page anchor -->
									<li><a href="#{c.id}"><span class="num">{number(c.id)}</span>{c.title}</a></li>
								{/each}
							</ol>
						</div>
					{/each}
				</nav>
			</header>

			<!-- ── Part I ─────────────────────────────────────────────────── -->
			<h2 class="part" id="part-known">What was known</h2>

			<section id="pairwise">
				<h3><span class="n">1</span>Pairwise attention</h3>
				<p class="src"><span class="mark prior"></span>Prior work <Cite id="vaswani" /></p>
				<p>
					A transformer layer lets every token look at every other one. Each token emits a query <MathTex
						tex="Q_i"
					/>, a key <MathTex tex="K_i" /> and a value <MathTex tex="V_i" />; a query scores each key
					with a dot product, the scores are normalized over keys, and the output is the weighted
					sum of values:
				</p>
				<MathTex
					display
					tex={"P_{ij} = \\frac{\\exp\\left(\\langle Q_i, K_j \\rangle/\\sqrt{d}\\right)}{\\sum_{j'} \\exp\\left(\\langle Q_i, K_{j'} \\rangle/\\sqrt{d}\\right)}, \\qquad Y_i = \\sum_j P_{ij}\\, V_j"}
				/>
				<ComputeGraph graph={PAIRWISE} label="Computation graph of pairwise attention" />
				<p>
					Every score involves exactly two tokens. A relation among three tokens must be assembled
					indirectly, across heads and layers, and there are simple tasks where small transformers
					provably cannot do that
					<Cite id={['hahn', 'sanford']} />. The cost is <MathTex tex="O(n^2 d)" /> per head for a sequence
					of
					<MathTex tex="n" /> tokens.
				</p>
			</section>

			<section id="product">
				<h3><span class="n">2</span>A generalized dot product</h3>
				<p class="src"><span class="mark prior"></span>Standard multilinear algebra</p>
				<p>
					The dot product sums the products of matching coordinates. Nothing stops at two factors:
					the trilinear form multiplies three, and it can be written as one dot product against an
					elementwise (Hadamard) product:
				</p>
				<MathTex
					display
					tex="\langle a, b \rangle = \sum_c a_c b_c \qquad\longrightarrow\qquad \langle a, b, e \rangle = \sum_c a_c\, b_c\, e_c = \langle a,\, b \odot e \rangle"
				/>
				<p>
					It is large only when all three vectors are large on the same coordinates. Read the other
					way, a width-<MathTex tex="d" /> trilinear form is a sum of <MathTex tex="d" /> rank-one three-way
					tensors, one per coordinate. That count comes back in chapter 6: it is how many different ways
					of pairing tokens a single query can ask for.
				</p>
			</section>

			<section id="cubic">
				<h3><span class="n">3</span>Cubic polyattention</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['clift', 'sanford', 'roy']} />,
					derived independently in this project's notebook <Cite id="neo" />
				</p>
				<p>
					Give each token one query and two role-specific keys and values. Query <MathTex tex="i" /> scores
					the ordered pair
					<MathTex tex="(j, k)" />, with <MathTex tex="j" /> in role 1 and <MathTex tex="k" /> in role
					2, and the softmax runs jointly over all pairs:
				</p>
				<MathTex
					display
					tex={"A_{ijk} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\rangle, \\qquad P_{ijk} = \\frac{\\exp(A_{ijk}/\\sqrt{d})}{\\sum_{j'k'} \\exp(A_{ij'k'}/\\sqrt{d})}, \\qquad Y_i = \\sum_{j,k} P_{ijk}\\,\\bigl(V^1_j \\odot V^2_k\\bigr)"}
				/>
				<ComputeGraph graph={CUBIC} label="Computation graph of cubic polyattention" />
				<p>
					Clift et al. introduced this operator as 2-simplicial attention, and Sanford et al.
					studied it as tensor attention and showed that one head solves Match3, a task that defeats
					pairwise attention. Roy et al. made it fast enough to train at scale. The Polyformer
					notebook arrived at the same operator independently in April 2023 under the name cubic
					polyattention, which this app keeps.
				</p>
				<p>
					The scores fill an <MathTex tex="n \times n \times n" /> tensor. Pairs that reuse the query
					or repeat a key are masked, and a sink token at position 0 gives every query somewhere to put
					weight it does not need.
				</p>
			</section>

			<section id="cost">
				<h3><span class="n">4</span>What it costs</h3>
				<p class="src"><span class="mark prior"></span>Prior work <Cite id={['roy', 'alman']} /></p>
				<p>
					For one query, all <MathTex tex="n^2" /> pair scores come from a single matrix product, and
					the values factor the same way, so no <MathTex tex="n \times n \times d" /> tensor is ever built:
				</p>
				<MathTex
					display
					tex={'S_i = \\bigl(Q_i \\odot K^1\\bigr)\\,K^{2\\top} \\in \\mathbb{R}^{n \\times n}, \\qquad Y_i = \\sum_j V^1_j \\odot \\bigl(P_i V^2\\bigr)_j'}
				/>
				<p>
					That is <MathTex tex="O(n^2 d)" /> per query and <MathTex tex="O(n^3 d)" /> per head, against
					<MathTex tex="O(n^2 d)" /> for pairwise attention. Roy et al. restrict each role to a local
					window of
					<MathTex tex="w" /> keys, which costs <MathTex tex="O(n\,w^2 d)" /> and makes long sequences
					practical. Alman and Song study when such higher-order attention can be computed faster than
					the naive bound at all, and find it depends on how large the entries are allowed to be.
				</p>
			</section>

			<section id="degree2">
				<h3><span class="n">5</span>Cheaper, degree-2 relatives</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['kozachinskiy', 'chakrabarti']} />
				</p>
				<p>
					A cheaper way to involve three tokens is to sum pairwise dot products along the edges of
					the triangle
					<MathTex tex="(i, j, k)" />. Each term is bilinear, so the whole score has degree 2 in the
					token features:
				</p>
				<MathTex
					display
					tex={'\\begin{aligned}A^{\\text{tree}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle \\\\ A^{\\text{Strassen}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle + \\langle Q_i, K^2_k \\rangle\\end{aligned}'}
				/>
				<p>
					Strassen attention, named for its fast matrix-multiplication algorithm, scores all three
					edges and runs in
					<MathTex tex={'O(n^{\\omega})'} /> time. Chakrabarti, Pitassi and Alman unify all of these as
					poly-attention: polynomials over a graph of token roles, classified by cost and by what they
					can compute. Their tree mechanism is the path <MathTex tex="i - j - k" />.
				</p>
			</section>

			<!-- ── Part II ────────────────────────────────────────────────── -->
			<h2 class="part" id="part-new">What this project adds</h2>

			<section id="barrier">
				<h3><span class="n">6</span>The coupling barrier</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					Fix a query and look at its <MathTex tex="n \times n" /> score matrix over pairs. For any degree-2
					score
					<MathTex tex={'A_{ijk} = f(i,j) + g(j,k) + h(i,k)'} />, the softmax factorizes:
				</p>
				<MathTex
					display
					tex={'P_{ijk} = \\frac{1}{Z_i}\\; \\underbrace{e^{f(i,j)}}_{\\text{row weight}}\\; \\underbrace{e^{g(j,k)}}_{\\text{shared kernel}}\\; \\underbrace{e^{h(i,k)}}_{\\text{column weight}}'}
				/>
				<p>
					<strong>Claim.</strong> Every query sees the same coupling kernel <MathTex
						tex={'G_{jk} = e^{g(j,k)}'}
					/>; it can only rescale its rows and columns. <strong>Proof.</strong> Once <MathTex
						tex="i"
					/> is fixed,
					<MathTex tex="f(i,j)" /> depends on <MathTex tex="j" /> alone and <MathTex tex="h(i,k)" /> on
					<MathTex tex="k" />
					alone. Double centering, <MathTex
						tex={'\\tilde M = M - \\bar M_{j\\cdot} - \\bar M_{\\cdot k} + \\bar M'}
					/>, removes exactly such terms, so <MathTex tex={'\\tilde A_{i,jk} = \\tilde g(j,k)'} /> for
					every
					<MathTex tex="i" />. ∎
				</p>
				<p>
					Which pairs belong together is therefore decided before the query arrives. The cubic score
					has no such limit:
				</p>
				<MathTex
					display
					tex={'\\tilde A^{\\text{cubic}}_{i,jk} = \\sum_{c=1}^{d} Q_{ic}\\; \\bigl(K^1_{\\cdot c} \\otimes K^2_{\\cdot c}\\bigr)^{\\sim}_{jk}'}
				/>
				<p>
					a query-dependent mix of up to <MathTex tex="d" /> coupling patterns. The figure shows it on
					real heads: three identical slices from a degree-2 head, three different ones from a cubic head.
				</p>
			</section>

			<section id="set">
				<h3><span class="n">7</span>SET is Match3</h3>
				<p class="src">
					<span class="mark prior"></span>Match3 <Cite id="sanford" />, SET geometry <Cite
						id="davis"
					/>;
					<span class="mark new inline"></span>the reduction and averaging argument are new here
				</p>
				<p>
					A SET card has four attributes with three values each, so a card is a vector in <MathTex
						tex={'\\mathbb{Z}_3^4'}
					/>. Three cards form a SET when every attribute is all the same or all different, which is
					exactly
					<MathTex tex="a + b + c \equiv 0 \pmod 3" /> in every coordinate. SETs are the lines of the
					affine space
					<MathTex tex={'\\mathrm{AG}(4, 3)'} />: any two cards determine the third, so the deck
					holds exactly 1,080 SETs among its 85,320 triples. Per attribute, the rule splits into
					pairwise agreement and one three-way term:
				</p>
				<MathTex
					display
					tex={'\\mathbb{1}[\\text{SET}] = 1 - (e_{ab} + e_{bc} + e_{ac}) + 3\\,\\mathbb{1}[a = b = c]'}
				/>
				<div class="cases">
					{#each cases as c (c.name)}
						<div class="case">
							<div class="trio">
								{#each c.cards as card, i (i)}<SetCard {card} width={30} />{/each}
							</div>
							<div class="case-name">{c.name}</div>
							<div class="hint num">1 − {c.e} + 3·{c.all} = {1 - c.e + 3 * c.all}</div>
						</div>
					{/each}
				</div>
				<p>
					<strong>Pairwise scores are blind on average.</strong> Let
					<MathTex tex={'\\Phi(T) = \\sum_{\\{a,b\\} \\subset T} \\varphi(a,b)'} /> be any score built
					from pairs. Every pair of cards lies in exactly one SET and in exactly 79 triples, so pairs
					are covered evenly by both, and the mean of
					<MathTex tex="\Phi" /> over SETs equals its mean over all triples: three times the mean of
					<MathTex tex="\varphi" /> over pairs. Only the three-way term separates them. ∎
				</p>
				<p>
					The task on the <a href={resolve('/compare')}>bench</a> deals twelve cards and asks, for each
					card, whether it belongs to some SET on the table.
				</p>
			</section>

			<section id="head">
				<h3><span class="n">8</span>A head built by hand</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					One cubic head can compute the whole rule. Put each attribute value <MathTex tex="v" /> on the
					unit circle at
					<MathTex tex="\omega^v" /> with <MathTex tex={'\\omega = e^{2\\pi i/3}'} />. Summing the
					three cube roots of unity picks out multiples of 3:
				</p>
				<MathTex
					display
					tex={'\\mathbb{1}[a + b + c \\equiv 0] = \\tfrac{1}{3}\\left(1 + 2\\cos\\tfrac{2\\pi}{3}(a + b + c)\\right)'}
				/>
				<p>
					and the cosine of a sum of three angles is four trilinear products of their cosines and
					sines:
				</p>
				<MathTex
					display
					tex="\cos(\alpha + \beta + \gamma) = c_\alpha c_\beta c_\gamma - c_\alpha s_\beta s_\gamma - s_\alpha c_\beta s_\gamma - s_\alpha s_\beta c_\gamma"
				/>
				<p>
					So with four channels per attribute, <MathTex tex="Q = (c, -c, -s, -s)" />, <MathTex
						tex="K^1 = (c, s, c, s)"
					/>
					and <MathTex tex="K^2 = (c, s, s, c)" />, sixteen channels give
				</p>
				<MathTex
					display
					tex={'A_{ijk} = \\sum_{t=1}^{4} \\cos\\tfrac{2\\pi}{3}\\bigl(a_t + b_t + c_t\\bigr) = 4 - \\tfrac{3}{2}\\,m'}
				/>
				<p>
					where <MathTex tex="m" /> counts the attributes that break the rule. Every SET scores 4 and
					everything else at most 2.5. This head is the default in the
					<a href={resolve('/explore')}>tensor lab</a>, so its pictures are exact before anything
					has trained.
				</p>
			</section>

			<section id="binding">
				<h3><span class="n">9</span>Values as binding</h3>
				<p class="src">
					<span class="mark prior"></span>Bilinear values <Cite id="clift" />, Hadamard values <Cite
						id="chakrabarti"
					/>;
					<span class="mark new inline"></span>the indexing check is new here
				</p>
				<p>
					Scores choose pairs; values decide what a pair says. Clift et al. combine a pair's values
					with a full bilinear map; the Hadamard value keeps only its diagonal, which costs the same
					as the scores. Both are views of one object, the pair moment:
				</p>
				<MathTex
					display
					tex={'M_i = V^{1\\top} P_i\\, V^2 = \\sum_{j,k} P_{ijk}\\, V^1_j V^{2\\top}_k, \\qquad \\operatorname{diag}(M_i) = Y_i'}
				/>
				<p>
					The value must be read at the keys. Poly-attention's definition does this, but its
					released implementation of the tree mechanism reads one value at the query position
					instead. With the same scores, that indexing drops SET to chance (54%), while Hadamard and
					full-moment values reach 100% in about 800 steps.
				</p>
			</section>

			<section id="training">
				<h3><span class="n">10</span>What training shows</h3>
				<p class="src">
					<span class="mark measured"></span>Measured with this app's engine <Cite id="jaxjs" />
				</p>
				<p>
					Every model on the bench sees identical batches; only the attention operator differs. One
					layer, width 64, four heads, 4,000 steps of AdamW, seed 0, scored on 1,024 held-out
					tables:
				</p>
				<table class="nums">
					<thead
						><tr><th>Model</th><th>Held-out accuracy</th><th>Reaches 95%</th><th>ms / step</th></tr
						></thead
					>
					<tbody>
						<tr class="hi"><td>Cubic</td><td>100%</td><td>step 500</td><td>12.2</td></tr>
						<tr><td>Feynman, 2 rounds</td><td>100%</td><td>step 700</td><td>35.7</td></tr>
						<tr><td>Strassen</td><td>95.8%</td><td>step 2,350</td><td>11.3</td></tr>
						<tr><td>Tree (Columbia)</td><td>76.4%</td><td>never</td><td>11.0</td></tr>
						<tr><td>Standard, 2 layers</td><td>64.4%</td><td>never</td><td>15.5</td></tr>
						<tr><td>Standard, 1 layer</td><td>60.5%</td><td>never</td><td>8.4</td></tr>
					</tbody>
				</table>
				<p>
					Always guessing the more common answer scores 53.5%. The cubic head sits at chance until
					step 400 and is at 99% by step 500: the three-way rule is learned all at once rather than
					gradually. At this length the cubic head costs about the same time per step as the
					degree-2 ones. The ordering held on a second seed in offline runs.
				</p>
			</section>

			<section id="arity">
				<h3>
					<span class="n">11</span><span
						>Order <MathTex tex="k" /> needs a <MathTex tex="k" />-way term</span
					>
				</h3>
				<p class="src">
					<span class="mark prior"></span>Match-<MathTex tex="t" /> and <MathTex tex="t" />-tensor
					attention
					<Cite id="sanford" />; <span class="mark new inline"></span>the four-card test is new here
				</p>
				<p>
					Ask instead whether four cards sum to zero, and cubic attention stalls at the majority
					rate, just as pairwise attention did on SET. The counting argument of chapter 7 moves up
					one order: three cards almost always determine the fourth, so every score built from
					triples is close to blind on average. A quartic head learns it:
				</p>
				<MathTex
					display
					tex={'A_{ijkl} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\odot K^3_l \\rangle'}
				/>
				<p>
					Every order has the same shape, the original notebook's general polyattention: a query
					against ordered tuples of role-specific keys, with values multiplied along the tuple.
				</p>
				<ComputeGraph graph={GENERAL} label="Computation graph of polyattention of order N" />
				<p>
					A fixed arity is a fixed bet. The head pays <MathTex tex="n^k" /> whether the data needs pairs,
					triples or long chains, and some problems need a different depth for every example.
				</p>
			</section>

			<!-- ── Part III ───────────────────────────────────────────────── -->
			<h2 class="part" id="part-beyond">Letting the data choose the arity</h2>
			<p class="part-lede">
				Chapter 11 ended on a fixed bet: a head of order <MathTex tex="k" /> pays for <MathTex
					tex="k"
				/>-way terms whether the data needs them or not. Physics met the same problem in the 1940s,
				how to add up interactions among any number of particles, and answered it with a picture
				language. This part tells that story first, then borrows it.
			</p>

			<section id="feynman">
				<h3><span class="n">12</span>Where Feynman diagrams come from</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['feynman', 'dyson']} />
				</p>
				<p>
					In quantum electrodynamics, the theory of electrons and light, the quantity you want is an
					<em>amplitude</em>: a number whose square gives the probability of a process, say two
					electrons flying at each other and leaving with given momenta. The theory cannot be solved
					exactly. What it offers instead is a small number, the electron's charge <MathTex
						tex="e"
					/>, with <MathTex tex="\alpha = e^2/4\pi \approx 1/137" />. So the amplitude is computed
					as a power series in <MathTex tex="e" />: perturbation theory.
				</p>
				<p>
					In 1949 Feynman showed that every term of that series can be drawn. A straight line is a
					particle moving freely (a <em>propagator</em>), a wavy line is a photon, and a dot where
					three lines meet is an <em>interaction</em>, the place where an electron emits or absorbs
					a photon. Each dot contributes one factor of <MathTex tex="e" />, so a diagram with <MathTex
						tex="V"
					/> dots is a term of order <MathTex tex="e^V" />. The same year Dyson showed that the
					pictures follow exactly from the formal calculations of Schwinger and Tomonaga, which
					turned them from a heuristic into a method. For two electrons scattering:
				</p>
				<DiagramSum
					lhs="blob"
					width={64}
					terms={[
						{ kind: 'tree-t', caption: 'e^2' },
						{ kind: 'tree-u', caption: 'e^2' },
						{ kind: 'vacuum', caption: 'e^4' },
						{ kind: 'vertex', caption: 'e^4' },
						{ kind: 'box', caption: 'e^4' }
					]}
				/>
				<p>
					The hatched blob is everything that can happen; the right side lists the ways it can
					happen. At lowest order the electrons exchange one photon, either way round. At the next
					order the photon briefly becomes an electron–positron pair (the loop), or one electron
					emits and reabsorbs a photon of its own, or the electrons trade two photons. Every picture
					is one term, with exact rules for turning it into a number: a factor for each line, a
					coupling for each vertex, an integral for each loop.
				</p>
				<p>
					Two ideas carry over to attention. A complicated interaction among many particles is built
					from one small vertex, used over and over. And nobody decides in advance how many
					particles take part: the theory sums over all the diagrams, and the couplings decide how
					much each one contributes.
				</p>
			</section>

			<section id="dyson">
				<h3><span class="n">13</span>Summing them all at once</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['dyson', 'schwinger']} />
				</p>
				<p>
					Listing diagrams one at a time never ends. Dyson and Schwinger found equations that sum
					whole families of them at once. The simplest is for a single particle. Draw the <em
						>dressed</em
					>
					propagator, everything that can happen to an electron on its way from one point to another,
					as a double line, and let the blob <MathTex tex="\Sigma" />, the self-energy, stand for
					every diagram that cannot be split in two by cutting one line. Then
				</p>
				<DiagramSum
					lhs="dressed"
					width={92}
					more={false}
					terms={[{ kind: 'bare' }, { kind: 'bare-sigma-dressed' }]}
				/>
				<MathTex display tex="G = G_0 + G_0\, \Sigma\, G" />
				<p>
					The dressed line appears on both sides, so the equation is self-consistent. Substituting
					it into itself unrolls it into an infinite series:
				</p>
				<DiagramSum
					lhs="dressed"
					width={92}
					terms={[
						{ kind: 'bare' },
						{ kind: 'bare-sigma-bare' },
						{ kind: 'bare-sigma-bare-sigma-bare' }
					]}
				/>
				<MathTex
					display
					tex={'G = G_0 + G_0 \\Sigma G_0 + G_0 \\Sigma G_0 \\Sigma G_0 + \\cdots = G_0\\,\\bigl(1 - \\Sigma\\, G_0\\bigr)^{-1}'}
				/>
				<p>
					Solving the equation sums every term of that series in one go. In the full theory <MathTex
						tex="\Sigma"
					/> itself depends on dressed propagators and vertices, so the equations form a tower that is
					cut off in practice; stopping after <MathTex tex="R" /> substitutions keeps exactly the diagrams
					up to depth <MathTex tex="R" />.
				</p>
				<p>
					That is the shape Feynman attention borrows. Read "a particle's dressed line" as "a
					token's state", "one more application of the interaction" as "one more round of
					attention", and "the couplings" as "softmax weights". A token's final state is then a sum
					over diagrams up to depth <MathTex tex="R" />, built from one vertex, with the weights
					learned from data.
				</p>
			</section>

			<section id="diagrams">
				<h3><span class="n">14</span>Sum over diagrams</h3>
				<p class="src"><span class="mark new"></span>New in this project: Feynman attention</p>
				<p>
					Each token's state <MathTex tex="\Phi_t" /> is rebuilt for <MathTex tex="R" /> rounds from the
					previous round's states. Round 0 is the token's own value, <MathTex
						tex="\Phi^0_t = v_t"
					/>. Each later round chooses, with one softmax, among five kinds of term:
				</p>
				<MathTex
					display
					tex={'\\begin{aligned}\\Phi^{r}_t = \\;& \\pi_{\\text{leaf}}\\, v_t + \\sum_j \\pi_j\\, \\Phi^{r-1}_j \\\\ &+ \\sum_{jk} \\pi_{jk}\\, \\Phi^{r-1}_j \\odot \\Phi^{r-1}_k \\\\ &+ \\sum_{jm} \\pi_{jm}\\, \\Phi^{r-1}_j \\odot \\Psi^{r}_m + \\pi_{\\text{carry}}\\, \\Phi^{r-1}_t\\end{aligned}'}
				/>
				<p>
					Read term by term: keep your own value (a leaf), copy another token's state (a hop, a
					propagator), multiply two tokens' states (a cubic vertex), multiply one token's state by a
					virtual mode (an exchange), or keep what you had (a carry). The dictionary between the two
					pictures:
				</p>
				<table class="dict">
					<thead><tr><th>Field theory</th><th>Feynman attention</th></tr></thead>
					<tbody>
						<tr
							><td>a particle's dressed line</td><td>a token's state <MathTex tex="\Phi_t" /></td
							></tr
						>
						<tr
							><td>the bare propagator <MathTex tex="G_0" /></td><td
								>the token's own value <MathTex tex="v_t" /></td
							></tr
						>
						<tr><td>the interaction vertex</td><td>one trilinear score</td></tr>
						<tr
							><td>the coupling <MathTex tex="e" /></td><td
								>a softmax weight <MathTex tex="\pi" /></td
							></tr
						>
						<tr><td>order in perturbation theory</td><td>the round <MathTex tex="r" /></td></tr>
						<tr><td>a virtual photon</td><td>a virtual mode <MathTex tex="\Psi_m" /></td></tr>
						<tr><td>the vacuum</td><td>a vacuum token of value 1</td></tr>
					</tbody>
				</table>
				<ComputeGraph graph={FEYNMAN} label="Computation graph of Feynman attention" />
				<p>
					All five terms are scored by a single vertex,
					<MathTex tex="\langle q_t \odot \omega_r,\; u_\alpha \odot w_\beta \rangle" />, where
					<MathTex tex="\omega_r" /> is a learned clock for round <MathTex tex="r" /> and
					<MathTex tex="\alpha, \beta" /> range over tokens, the vacuum and <MathTex tex="M" /> virtual
					modes: a leaf pairs the vacuum with itself, a hop pairs a token with the vacuum, a cubic term
					pairs two tokens. A mode
					<MathTex
						tex={'\\Psi^r_m = \\sum_{kl} \\rho_{m,kl}\\, \\Phi^{r-1}_k \\odot \\Phi^{r-1}_l'}
					/> is a learned query that binds a pair of tokens by itself, so an exchange reaches three other
					tokens at once.
				</p>
				<p>
					<strong>Two worked expansions.</strong> On SET, a card needs one cubic vertex: its round-1 state
					reads the product of the two cards that complete a SET with it,
				</p>
				<MathTex
					display
					tex={'\\Phi^1_i \\approx \\sum_{(j,k)\\,\\in\\,\\text{SETs}(i)} \\pi_{jk}\\; v_j \\odot v_k'}
				/>
				<p>
					On pointer chasing, the query needs a chain of hops as long as its list. If the query
					starts at node
					<MathTex tex="a" />, which points to <MathTex tex="b" />, which points to the last node <MathTex
						tex="c"
					/>, then
				</p>
				<MathTex
					display
					tex="\Phi^4_q \approx \Phi^3_a \approx \Phi^2_b \approx \Phi^1_c \approx \cdots \approx v_c"
				/>
				<p>
					one hop per round, carried once the end is reached. In the language of chapter 12 the
					first is a single vertex, the second a long propagator; the same layer can be either, and
					which one is decided by the weights. Unrolled, a state is a weighted sum of trees: after <MathTex
						tex="R"
					/> rounds one token can draw on anything from one token to <MathTex tex="3^R" /> of them. Each
					round costs <MathTex tex="O(n^3 d + n^2 M d)" />, like one cubic layer. The figure draws
					those trees in the style of TikZ-Feynman <Cite id="ellis" />; the
					<a href={resolve('/explore/diagrams')}>Diagrams</a> screen draws them for a model training live.
				</p>
			</section>

			<section id="sectors">
				<h3><span class="n">15</span>Making it train</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					The first versions did not learn. Three changes fixed that, each for a reason that can be
					stated:
				</p>
				<p>
					<strong>Chemical potentials.</strong> The sectors offer very different numbers of options:
					one leaf, about
					<MathTex tex="n" /> hops, about <MathTex tex="n^2" /> cubic pairs, <MathTex tex="nM" /> exchanges.
					With equal logits a softmax gives each sector mass in proportion to its size, so at initialization
					almost everything goes to cubic and exchange terms. A fixed bias per sector removes that:
				</p>
				<MathTex
					display
					tex={"\\mu_s = -\\log |S_s| \\quad\\Longrightarrow\\quad \\sum_{o \\in S_s} \\frac{e^{\\mu_s}}{\\sum_{s'} |S_{s'}|\\, e^{\\mu_{s'}}} = \\frac{1}{5}"}
				/>
				<p>
					like a chemical potential fixing how many particles of each kind a system holds.
					<strong>An RMS readout.</strong> Hadamard products of values below 1 shrink geometrically
					with depth, so the final state is divided by its root mean square.
					<strong>An absorbing carry.</strong> Without a way to keep its state, a token must rebuild everything
					every round, and an answer found in round 1 is overwritten in round 2. The carry term makes
					finished results fixed points.
				</p>
			</section>

			<section id="chase">
				<h3><span class="n">16</span>What Feynman attention learns</h3>
				<p class="src"><span class="mark measured"></span>Measured with this app's engine</p>
				<p>
					Pointer chasing asks for a depth that varies by example <Cite id="chakrabarti07" />:
					twelve nodes form linked lists, and the query must return the payload at the end of its
					start node's list, one to three hops away.
				</p>
				<table class="nums">
					<thead
						><tr><th>Model</th><th>Held-out accuracy</th><th>Parameters</th><th>ms / step</th></tr
						></thead
					>
					<tbody>
						<tr class="hi"
							><td>Feynman, 4 rounds, 1 layer</td><td>100%</td><td>61k</td><td>103</td></tr
						>
						<tr><td>Standard, 3 layers</td><td>94.2%</td><td>154k</td><td>43</td></tr>
						<tr><td>Standard, 2 layers</td><td>88.9%</td><td>104k</td><td>28</td></tr>
						<tr><td>Cubic, 1 layer</td><td>84.5%</td><td>63k</td><td>20</td></tr>
						<tr><td>Standard, 1 layer</td><td>64.5%</td><td>54k</td><td>15</td></tr>
					</tbody>
				</table>
				<p>
					Feynman attention passes 95% by step 250. Its trained computation tree, expanded with the
					diagram probe, follows the true pointer path one hop per round, the same algorithm as the
					ideal construction. It is not a universal winner: on four-card SET it stays at the
					majority rate, and on three-hop composition, where an untied chain of heads succeeds, it
					stalls near 60%.
				</p>
			</section>

			<!-- ── Part IV ────────────────────────────────────────────────── -->
			<h2 class="part" id="part-algebra">Arity is algebra</h2>
			<p class="part-lede">
				Part III let one softmax choose among arities. This part asks what an arity is, why stacking
				smaller ones does not reach it, and how a single layer can offer every arity at once.
			</p>

			<section id="composition">
				<h3><span class="n">17</span>Composing arity does not train</h3>
				<p class="src">
					<span class="mark measured"></span>Measured on cloud GPUs with the research harness, three
					seeds per model
				</p>
				<p>
					Match-<MathTex tex="k" /> generalizes SET: a card is positive when it and <MathTex
						tex="k-1"
					/> others on the table sum to zero, attribute by attribute, modulo 3. SET is Match-3, and chapter
					11's four-card test is Match-4. On Match-3, 4 and 5, standard attention at any depth stays at
					chance from Match-4 up. Cubic attention and Feynman attention solve Match-3 and stop there.
					Dense quartic attention learns Match-4 on two seeds of three, after a long plateau.
				</p>
				<p>
					Most telling: Feynman attention given every building block of the construction in chapter
					19, at widths up to 192, stays at exactly chance on Match-4. It could represent the answer
					by composing smaller products; gradient descent never finds the composition.
				</p>
				<p>
					Chapter 7's counting argument, made exact, says why. For a zero-sum relation, any set of
					fewer than <MathTex tex="k" /> of its cards is uniformly distributed whether or not the relation
					holds, so nothing built from fewer cards correlates with the label. A gradient has nothing to
					climb until the model already computes a <MathTex tex="k" />-way product. Abbe et al. call
					the number of coordinates that must be learned together the leap of a function <Cite
						id="abbe"
					/>; here it is <MathTex tex="k" />.
				</p>
			</section>

			<section id="characters">
				<h3><span class="n">18</span>A relation is agreement of phases</h3>
				<p class="src">
					<span class="mark prior"></span>Characters of finite abelian groups, classical;
					<span class="mark new inline"></span>reading attention through them is new here
				</p>
				<p>
					Give every card a phase. Pick <MathTex tex={String.raw`c \in \mathbb Z_3^4`} /> and send card
					<MathTex tex="x" /> to the unit complex number <MathTex
						tex={String.raw`\phi_c(x) = \omega^{\langle c, x\rangle}`}
					/>, with <MathTex tex={String.raw`\omega = e^{2\pi i/3}`} />. Multiplying phases adds
					cards,
					<MathTex tex={String.raw`\phi_c(x)\,\phi_c(y) = \phi_c(x + y)`} />, so a SET's three
					phases multiply to 1 for every one of the 81 choices of <MathTex tex="c" />. A near miss
					may agree under a few of them, but averaged over all 81 the products of any other triple
					cancel:
				</p>
				<MathTex
					display
					tex={String.raw`\frac{1}{81}\sum_{c} \phi_c(x)\,\phi_c(y)\,\phi_c(z) \;=\; \mathbf 1\big[x + y + z = 0\big]`}
				/>
				<p>
					These <MathTex tex={String.raw`\phi_c`} /> are the characters of the group, its Fourier basis.
					In this basis a <MathTex tex="k" />-way relation is a product of <MathTex tex="k" /> phases,
					averaged, and a Hadamard product of character vectors is the character vector of a sum of cards.
					Networks are known to find Fourier features for group arithmetic <Cite id="nanda" />;
					chapter 20 shows an attention layer finding these.
				</p>
			</section>

			<section id="newton">
				<h3><span class="n">19</span>Every arity at once</h3>
				<p class="src">
					<span class="mark new"></span>New in this project, built on Newton's identities
				</p>
				<p>
					Pool every token's phases into power sums, <MathTex
						tex={String.raw`P_j = \sum_t \phi(x_t)^{\odot j}`}
					/>: one pass over the sequence for each <MathTex tex="j" />. Newton's identities turn
					power sums into elementary symmetric polynomials, the sums over every set of <MathTex
						tex="m"
					/> distinct tokens of the product of their phases:
				</p>
				<MathTex
					display
					tex={String.raw`m\, e_m \;=\; \sum_{j=1}^{m} (-1)^{j-1}\, e_{m-j} \odot P_j, \qquad e_m = \sum_{|S| = m}\; \bigodot_{t \in S} \phi(x_t)`}
				/>
				<p>
					Averaged over the characters, as in chapter 18, the coefficient of each card in <MathTex
						tex={String.raw`e_{k-1}`}
					/> of the other cards counts its zero-sum relations of size <MathTex tex="k" />. A handful
					of power sums count every card's relations of every size, with no tuple ever listed. The
					figure counts them live on a fresh table and checks each count against brute-force
					enumeration.
				</p>
			</section>

			<section id="newtonattn">
				<h3><span class="n">20</span>Newton attention</h3>
				<p class="src">
					<span class="mark new"></span>New in this project;
					<span class="mark measured inline"></span>measured on cloud GPUs, three seeds per model
				</p>
				<p>
					Newton attention makes that construction learnable. Each token gets <MathTex tex="r" /> complex
					channels with a learned phase and a learned gate, so a character is one linear map away. The
					rest is fixed algebra: leave-one-out power sums, Newton's identities, and for each arity the
					query's phases times the elementary symmetric polynomial of the other tokens. A linear read-out
					weighs the arities. Every arity up to <MathTex tex="K" /> costs <MathTex tex="O(nKr)" />,
					linear in the sequence.
				</p>
				<ComputeGraph graph={NEWTON} label="Computation graph of Newton attention" />
				<p>
					With every arity up to six on offer, it solves SET, Match-3, Match-4 and a task whose
					label is the smallest arity at which a card completes a relation, on every seed (the best
					fixed-order operator reaches 54% on the last), and with more channels it reaches 97.5% on
					Match-5. Cap its order below the task's arity and it falls to exactly chance. Two details
					matter. Each arity's features are normalised before the read-out, because high arities are
					products of many numbers below one and otherwise barely learn. And one read-out is shared
					by every arity, because the same characters count relations of every size.
				</p>
				<p>
					Two probes show what it learned. Switch off one arity at a time: on Match-3 only arity 3
					matters, on Match-4 only arity 4, and on the smallest-arity task exactly arities 3, 4 and
					5. Nothing told it which arities the task has. And its channels become characters. Every
					run that solves its task has found all 40 up to conjugation, and a run that falls short
					has accuracy close to linear in how many it found.
				</p>
			</section>

			<section id="transfer">
				<h3><span class="n">21</span>Small relations teach large ones</h3>
				<p class="src">
					<span class="mark measured inline"></span>Measured on cloud GPUs, three seeds per model
				</p>
				<p>
					A character that counts triples also counts quadruples. So train one layer on Match-3, 4
					and 5 at once, with the first token saying which, and score it on each. Each arity sees a
					third of the data, yet the mixed layer is exact on all three on every seed, where the same
					layer trained on Match-5 alone reaches 85%. Even the first version of the layer, with its
					own read-out per arity, went from 57% to 83% on Match-5 this way. Easy relations find the
					characters and hard ones reuse them, the staircase that carries a learner past a leap <Cite
						id="abbe"
					/>.
				</p>
				<p>
					Where it does not help is text. In a byte-level language model of 3.3M parameters trained
					on enwik8, a Newton attention branch beside softmax attention leaves bits per character
					where they were, 1.657 against 1.651, and Newton attention in place of softmax attention
					is much worse, at 2.50. It has no keys or values, so it cannot fetch a particular earlier
					token, which language modelling relies on. It is a layer for relations among many tokens,
					not a replacement for attention. The Compare tab's four-card suite trains it in your
					browser next to cubic attention, Feynman attention and two standard layers.
				</p>
			</section>

			<section id="references" class="refs">
				<h2 class="part">References</h2>
				<ol>
					{#each REFERENCES as r (r.id)}
						<li id="ref-{r.id}">
							<span class="who">{r.authors}.</span>
							{#if r.url}
								<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
								<a href={r.url} rel="external noopener noreferrer" target="_blank">{r.title}</a>.
							{:else}
								<span class="title">{r.title}</span>.
							{/if}
							<span class="venue">{r.venue}, {r.year}.</span>
						</li>
					{/each}
				</ol>
			</section>
		</article>

		<aside class="figure" aria-live="polite">
			<LearnFigure {section} />
		</aside>
	</div>
</PageFrame>

<style>
	.learn {
		display: grid;
		grid-template-columns: minmax(0, 620px) minmax(0, 1fr);
		gap: 48px;
		padding: 0 32px 0 40px;
	}
	.text {
		padding: 32px 0 30vh;
	}
	h1 {
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 38px;
		font-weight: 400;
		line-height: 1.1;
	}
	.lede {
		margin-top: 12px;
		font-size: 15px;
		line-height: 1.65;
		color: var(--color-ink-2);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 6px 20px;
		margin-top: 10px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.legend li {
		display: inline-flex;
		align-items: center;
	}
	.mark {
		display: inline-block;
		flex: none;
		width: 7px;
		height: 7px;
		margin-right: 6px;
		border-radius: 50%;
		border: 1px solid var(--color-ink-3);
		vertical-align: 0;
	}
	.mark.new {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.mark.measured {
		border-color: var(--color-ink-2);
		background: radial-gradient(circle, var(--color-ink-2) 0 1.5px, transparent 2px);
	}
	.mark.inline {
		margin-left: 4px;
	}
	.toc {
		display: grid;
		grid-template-columns: repeat(3, auto);
		gap: 18px;
		margin-top: 26px;
		padding-top: 18px;
		border-top: 1px solid #1a1a1a;
	}
	.toc-title {
		display: block;
		margin-bottom: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.toc ol {
		display: grid;
		gap: 3px;
	}
	.toc a {
		display: flex;
		gap: 8px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		text-decoration: none;
	}
	.toc a:hover {
		color: var(--color-ink);
	}
	.toc a .num {
		min-width: 14px;
	}
	h2.part {
		margin: 56px 0 4px;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 26px;
		font-weight: 400;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	section {
		padding: 26px 0 4px;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	h3 {
		display: flex;
		align-items: baseline;
		gap: 12px;
		font-size: 18px;
		font-weight: 500;
		letter-spacing: -0.01em;
	}
	.n {
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 15px;
		color: var(--color-ink-3);
		min-width: 14px;
	}
	.src {
		margin: 4px 0 12px 26px;
		line-height: 1.6;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	p {
		color: var(--color-ink-2);
		font-size: 15px;
		line-height: 1.7;
		margin: 0 0 12px;
	}
	p :global(.katex) {
		color: var(--color-ink);
	}
	strong {
		font-weight: 500;
		color: var(--color-ink);
	}
	em {
		font-style: italic;
		color: var(--color-ink);
	}
	.part-lede {
		margin-top: 10px;
		color: var(--color-ink-2);
	}
	.dict {
		width: 100%;
		margin: 2px 0 16px;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	.dict th {
		padding: 0 12px 6px 0;
		text-align: left;
		font-weight: 400;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.dict td {
		padding: 4px 12px 4px 0;
		color: var(--color-ink-2);
	}
	.dict td:last-child {
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
		padding: 6px 0;
		overflow-x: auto;
		font-size: 15.5px;
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
		gap: 5px;
	}
	.trio {
		display: flex;
		gap: 6px;
	}
	.case-name {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.nums {
		width: 100%;
		margin: 2px 0 14px;
		border-collapse: collapse;
		font-size: var(--text-sm);
		font-variant-numeric: tabular-nums;
	}
	.nums th {
		padding: 0 10px 6px 0;
		text-align: left;
		font-weight: 400;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.nums td {
		padding: 4px 10px 4px 0;
		color: var(--color-ink-2);
	}
	.nums tr.hi td {
		color: var(--color-ink);
	}
	.refs ol {
		display: grid;
		gap: 10px;
		margin-top: 14px;
		padding-left: 22px;
		list-style: decimal;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.refs li:target {
		color: var(--color-ink);
	}
	.refs .who,
	.refs .title {
		color: var(--color-ink-2);
	}

	/* the sticky figure */
	.figure {
		position: sticky;
		top: calc(var(--bar-h) + 20px);
		height: calc(100dvh - var(--bar-h) - 40px);
		display: grid;
		align-items: center;
	}

	/* phones and tablets: the figure pins under the bar and the text scrolls beneath it */
	@media (max-width: 1100px) {
		.learn {
			grid-template-columns: minmax(0, 1fr);
			gap: 0;
			padding: 0 16px;
		}
		.figure {
			order: -1;
			z-index: 5;
			top: var(--bar-h);
			height: 42dvh;
			margin: 0 -16px;
			padding: 10px 16px;
			background: var(--color-void);
			border-bottom: 1px solid #1a1a1a;
			overflow: hidden;
		}
		.figure :global(figcaption) {
			display: none;
		}
		.text {
			padding: 20px 0 80px;
		}
		.toc {
			grid-template-columns: minmax(0, 1fr);
		}
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 30px;
		}
		.cases {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
