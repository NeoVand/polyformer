<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import { BIB } from '#lib/report/bib.ts';
	import CharactersResult from '#lib/report/CharactersResult.svelte';
	import GroupLadder from '#lib/report/GroupLadder.svelte';
	import { CHARACTER_ROWS, GROUP_ROWS, SWAP_ROWS } from '#lib/report/groupResults.ts';
	import Theorem from '#lib/report/Theorem.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import { Book, Compare, FunctionIcon, Grid, Matrix, Note } from '#lib/ui/icons.ts';
	import baseline from '#lib/report/results/baseline.json';
	import phaseA from '#lib/report/results/phase_a.json';
	import newtonE from '#lib/report/results/newton_e.json';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	const source = (path: string) => `${repo}${path}`;
	const sections: Record<string, string> = {
		abstract: 'abstract',
		beginning: 'beginning',
		language: 'beginning',
		composition: 'composition',
		'character-results': 'composition',
		holonomy: 'composition',
		groups: 'groups',
		theory: 'theory',
		programs: 'programs',
		'word-problems': 'programs',
		related: 'related',
		meaning: 'related',
		reproducibility: 'related',
		references: 'related'
	};
	let section = $state('abstract');
	function watch(element: HTMLElement) {
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries)
					if (entry.isIntersecting) section = sections[entry.target.id] ?? section;
			},
			{ rootMargin: '-20% 0px -65% 0px' }
		);
		element.querySelectorAll('section[id]').forEach((entry) => observer.observe(entry));
		return () => observer.disconnect();
	}
	const earlyModels = [
		{ id: 'standard-1L', label: 'Softmax 1L' },
		{ id: 'standard-2L', label: 'Softmax 2L' },
		{ id: 'standard-3L', label: 'Softmax 3L' },
		{ id: 'cubic', label: 'Cubic' },
		{ id: 'newton-K6-r256-h4-shared-fnorm', label: 'Newton, shared + normalized' }
	];
	const earlyTasks = [
		{ id: 'set', label: 'SET' },
		{ id: 'zs3', label: 'Match-3' },
		{ id: 'zs4', label: 'Match-4' },
		{ id: 'zs5', label: 'Match-5' }
	];
	// Three-seed means from wp_main.jsonl, rounded as in research/wp_summary.py.
	const wordRows = [
		{ label: 'Holonomy', scores: ['100.0', '100.0', '99.8', '98.4'] },
		{ label: 'Orthogonal RNN', scores: ['100.0', '100.0', '71.4', '29.3'] },
		{ label: 'Householder RNN', scores: ['98.9', '100.0', '99.9', '100.0'] },
		{ label: 'Newton (commuting)', scores: ['17.5', '5.5', '12.3', '4.5'] },
		{ label: 'Softmax 1L', scores: ['14.0', '4.7', '7.3', '2.8'] },
		{ label: 'Softmax 2L', scores: ['14.0', '4.8', '7.2', '2.4'] },
		{ label: 'DeltaProduct', scores: ['14.2', '4.8', '10.4', '3.5'] }
	];
	const wordTasks = ['A₅ · 16', 'A₅ · 64', 'S₅ · 16', 'S₅ · 64'];
	function earlyResult(model: string, task: string) {
		const rows = model.startsWith('newton') ? newtonE : task === 'set' ? baseline : phaseA;
		const row = rows.find((entry) => entry.model === model && entry.task === task);
		return row ? (row.bal_mean * 100).toFixed(2) : '—';
	}
	const eq = {
		character: String.raw`\chi(a+b)=\chi(a)\chi(b),\qquad \chi(x)=e^{i\theta(x)}`,
		sectors: String.raw`F_r(i)=\sum_{\substack{s_1<\cdots<s_r\\i\in\{s_1,\ldots,s_r\}}} M_{s_1}\cdots M_{s_r}`,
		polynomial: String.raw`\prod_{t=1}^{n}(I+zM_t)=\sum_{r=0}^{n}z^r E_r`,
		recurrence: String.raw`E_r(t)=E_r(t-1)+E_{r-1}(t-1)M_t`,
		bayes: String.raw`\mathrm{BA}\le B^*=\frac12+\frac{\mathbb E|p(O)-\pi|}{4\pi(1-\pi)}`,
		representation: String.raw`\rho(ab)=\rho(a)\rho(b)`,
		readout: String.raw`F_r(i)=\sum_{a+b=r-1}L_a(i)\,M_i\,R_b(i)`,
		compression: String.raw`\mu(A_1\otimes\cdots\otimes A_r)=A_1\cdots A_r`
	};
</script>

<svelte:head>
	<title>Learning to compose · Report | Polyformer</title>
	<meta
		name="description"
		content="From higher-order attention to group representations: a working paper with exact order-blind limits, learned rotations, negative language results, and controlled comparisons."
	/>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'abstract', label: 'Paper', icon: Note },
		{ id: 'beginning', label: 'The road', icon: FunctionIcon },
		{ id: 'composition', label: 'Composition', icon: Matrix },
		{ id: 'groups', label: 'Results', icon: Compare },
		{ id: 'theory', label: 'Theory', icon: Book },
		{ id: 'programs', label: 'Programs', icon: Grid },
		{ id: 'related', label: 'Context', icon: Book }
	]}
	active={section}
>
	<article class="paper" {@attach watch}>
		<header class="title-block">
			<p class="eyebrow">Polyformer · research report</p>
			<h1>Learning to compose</h1>
			<p class="subtitle">From higher-order attention to group representations</p>
			<p class="authors">Mostafa “Neo” Mohsenvand <span>Working draft · 20 October 2026</span></p>
		</header>

		<section id="abstract">
			<aside class="side">
				<b>The central result</b>A layer that discards order has an exact accuracy ceiling. Learned
				rotation products cross it. This is a restricted separation with stated assumptions.
			</aside>
			<p class="abstract">
				Attention compares tokens in pairs. On deliberately relational tasks, native products over
				more tokens learn what our softmax baselines do not. But higher-order models did not meet
				our registered language-model improvement threshold. That negative result led to a sharper
				question: <strong>what should features do when they meet?</strong> Supplying every character feature
				of a finite group still leaves softmax at chance on Match-4 in our training regime; Newton attention
				supplies the missing product and solves it. When composition depends on order, commuting products
				reach at most an exact information ceiling. Holonomy attention instead multiplies learned rotations
				and acquires approximate group representations, including the icosahedral rotations of A₅. We
				give qualified constructive theorems and a swap-program benchmark where ordinary order-aware baselines
				also succeed. On A₅/S₅ running products, short subset products improve learning over the same
				rotation-based matrix recurrence within the tested budget; they add no demonstrated state-tracking
				capacity. The contribution is a specific relational use of established sequence-composition ideas,
				with measured gains and explicit limits.
			</p>
			<p class="reading">
				For the visual introduction, start with <a href={resolve('/learn')}>Learn</a>. For the
				rotations themselves, open <a href={resolve('/explore/groups')}>the group lab</a>.
			</p>
		</section>

		<section id="beginning">
			<h2><span>1</span> The road began with relations</h2>
			<p>
				A softmax attention head scores each query–key pair, then mixes values using those scores <Cite
					refs={BIB}
					id="vaswani"
				/>. A relation can live beyond any one pair. In SET, each card has four attributes with
				three possible values; three cards form a set when every attribute is all the same or all
				different. Encoding each attribute as 0, 1 or 2 makes this a sum of zero, coordinate by
				coordinate, wrapping around after 2. Match-k asks whether a token belongs to any k-token
				zero-sum subset.
			</p>
			<p>
				For independent uniform group elements conditioned on an r-way zero sum, every proper subset
				remains uniform. Looking at fewer than r elements cannot detect that constraint by itself.
				This fact motivates native interactions of the right order; it does <em>not</em> prove that
				a multilayer transformer cannot combine pairwise computations into the answer. Higher-order
				attention and Match-k limitations have substantial prior art <Cite
					refs={BIB}
					id={['clift', 'sanford23', 'chakrabarti']}
				/>.
			</p>
			<aside class="side">
				<b>Measured here</b>Balanced accuracy averages sensitivity on positive tokens and
				specificity on negative tokens. Chance is 50%, even if the labels are imbalanced.
			</aside>
			<p>
				Cubic attention scores a query with two partners together. Newton attention sums products
				over subsets of several sizes, using a recurrence instead of enumerating them. On our
				synthetic tasks, this choice matters decisively.
			</p>
			<div class="table-scroll wide">
				<table>
					<thead
						><tr
							><th scope="col">One layer unless shown</th>{#each earlyTasks as task (task.id)}<th
									scope="col"
									class="num">{task.label}</th
								>{/each}</tr
						></thead
					>
					<tbody
						>{#each earlyModels as model (model.id)}<tr
								><th scope="row">{model.label}</th>{#each earlyTasks as task (task.id)}<td
										class="num">{earlyResult(model.id, task.id)}</td
									>{/each}</tr
							>{/each}</tbody
					>
				</table>
			</div>
			<p class="caption">
				<b>Table 1.</b> Balanced accuracy %, three-seed means. SET:
				<a href={source('src/lib/report/results/baseline.json')}>baseline</a>; Match-k:
				<a href={source('src/lib/report/results/phase_a.json')}>phase_a</a>; Newton:
				<a href={source('src/lib/report/results/newton_e.json')}>newton_e</a>. These are
				research-harness results, distinct from the browser runs in Compare. Width and parameter
				counts differ; this is evidence of learning behavior, not an efficiency ranking.
			</p>
			<p>
				The earlier Feynman/DS-PA branch composes attention operations through repeated computation.
				It succeeds on SET and pointer chains, yet did not make the harder Match-k tasks easy at its
				tested budget. Its useful lesson survives: a layer's internal computation matters as much as
				the number of tokens in a score.
			</p>
		</section>

		<section id="language">
			<h2><span>2</span> Language did not reward higher order</h2>
			<aside class="side">
				<b>Negative evidence</b><a href={source('research/SEARCH.md')}>SEARCH §8</a> and
				<a href={source('research/LOCAL.md')}>LOCAL §0</a>. These conclusions concern our
				small-model scale and training budgets.
			</aside>
			<p>
				We tested the proposed subset mechanisms on token-level language modeling and controlled
				diagnostic tasks. The search did not produce a higher-order replacement that cleared our
				registered improvement threshold. This is part of the result.
			</p>
			<div class="table-scroll wide">
				<table class="language-table">
					<thead
						><tr><th scope="col">Stage</th><th scope="col">Outcome at the registered gate</th></tr
						></thead
					>
					<tbody>
						<tr
							><th scope="row">S0 · language</th><td
								>Free-field at 0.97× FLOPs was 2.2% worse on FineWeb-Edu at 400M tokens; the
								improved initialization was still 0.8% worse.</td
							></tr
						>
						<tr
							><th scope="row">S1 · diagnostics</th><td
								>The capability gate passed, but a softmax control with the same look-back keys
								explained the gains. Subset sectors alone won no family.</td
							></tr
						>
						<tr
							><th scope="row">S2 · induction</th><td
								>Walks reached the phase-change measure in 1.10–1.23× softmax's tokens: later,
								against a target of at most 0.60×.</td
							></tr
						>
						<tr
							><th scope="row">S6 · local regression</th><td
								>Local-linear attention gained about 0.4%; Parallax about 0.75%. Both fell short of
								the 1% loss-reduction gate.</td
							></tr
						>
					</tbody>
				</table>
			</div>
			<p class="caption">
				<b>Table 2.</b> Rounded headlines exactly as summarized in the research notes. The S6 per-seed
				local-linear gains at equal FLOPs were 0.40%, 0.39%, 0.37%; Parallax's were 0.64–0.90% under Muon.
				Lower language loss is better.
			</p>
			<p>
				Local-linear attention and Parallax are prior mechanisms <Cite
					refs={BIB}
					id={['lla', 'parallax']}
				/>. The latter's correction uses a pair sector and beat our higher-arity solved variant.
				That changes more than arity, so it is suggestive evidence rather than an isolated arity
				test. We stopped claiming that more order was the destination.
			</p>
		</section>

		<section id="composition">
			<h2><span>3</span> The turn: how features compose</h2>
			<p>
				A <strong>group</strong> is a collection of operations that can be composed, with an
				operation that does nothing and an inverse that undoes each operation. Composition is
				associative: regrouping a sequence does not change its result. A group is
				<strong>abelian</strong>, or commutative, when swapping two operations never changes their
				product. Clock arithmetic is the simplest example: adding two hours and then three hours is
				the same as adding three and then two.
			</p>
			<p>
				A <strong>character</strong> of a finite abelian group encodes each element as a point on the
				unit circle. Its angle is a phase. Combining group elements adds their phases, so their complex
				values multiply:
			</p>
			<MathTex tex={eq.character} display />
			<p>
				Here χ names the encoding, a + b means the group's operation, and i in the exponential is
				the imaginary unit. For SET cards, the group is Z₃⁴: four independent three-hour clocks. Its
				complete character bank gives every distinction between cards. Newton attention directly
				multiplies these phase features and sums the products over subsets. A zero-sum subset
				becomes a product that returns to the circle's starting point.
			</p>
			<p>
				That suggests two explanations of Newton's success. Perhaps it only needs the right
				coordinates. Or perhaps the important ingredient is performing the product. We separated
				them experimentally.
			</p>
		</section>

		<section id="character-results">
			<h3>Experiment 1 · give softmax all the coordinates</h3>
			<aside class="side">
				<b>Measured here</b>Width 192; one or two softmax layers; an MLP; no positions; 6,000 steps;
				three seeds. Source: <a href={source('research/GROUPS.md')}>GROUPS §5.1</a>.
			</aside>
			<p>
				We froze the input to all forty conjugate character pairs of Z₃⁴, then trained softmax plus
				an MLP. A conjugate pair contains one clock encoding and the same clock running backward;
				together they can be stored as real cosine and sine coordinates. A rotated version of that
				bank controls for the coordinate basis. Learned tables are the third control.
			</p>
			<figure id="fig-characters" class="wide">
				<CharactersResult />
				<figcaption>
					<b>Figure 1.</b> Knowing the features did not teach the tested softmax models the
					composition. Both depths stayed at chance on Match-4 in every seed. Newton's reference
					result is from <code>newton_e</code>; it is not a newly trained arm of this grid.
				</figcaption>
			</figure>
			<div class="table-scroll wide">
				<table>
					<thead
						><tr
							><th scope="col">Arm</th>{#each ['Match-3', 'Match-4', 'Match-5'] as task (task)}<th
									scope="col"
									class="num">{task}</th
								>{/each}</tr
						></thead
					>
					<tbody
						>{#each CHARACTER_ROWS as row (row.id)}<tr
								><th scope="row">{row.label}</th>{#each row.values as value, i (i)}<td class="num"
										>{value.display}{#if value.seeds}<small>({value.seeds})</small>{/if}</td
									>{/each}</tr
							>{/each}</tbody
					>
				</table>
			</div>
			<p class="caption">
				<b>Table 3.</b> Balanced accuracy %, mean (seeds 0, 1, 2), copied at the precision of GROUPS
				§5.1. <a href={source('research/results/grp_e1.jsonl')}>Raw experiment 1</a>. The
				exploratory 20,000-step softmax 2L extension also gave 50.0% on Match-4 in every seed.
			</p>
			<p>
				<strong>This is a learning result, not an impossibility theorem.</strong> Uniform softmax
				can collect all character sums; a sufficiently wide MLP can implement Newton's identities on
				this finite domain. The computation exists inside that model class. Training did not find it
				at the tested widths and budgets. Transformers have learned Fourier composition circuits in
				other settings <Cite refs={BIB} id="nanda" />. Native multiplication supplied a useful
				inductive bias here.
			</p>
		</section>

		<section id="holonomy">
			<h2><span>4</span> From clock hands to rotations</h2>
			<p>
				Clock hands commute. Spatial rotations generally do not: turning an object around one axis
				and then another can end somewhere different from reversing those turns. A <strong
					>representation</strong
				> assigns a matrix ρ(g) to each group element g so that matrix multiplication preserves the group's
				composition law:
			</p>
			<MathTex tex={eq.representation} display />
			<p>
				A representation is <strong>faithful</strong> if different elements receive different
				matrices. It is <strong>irreducible</strong>, or an <strong>irrep</strong>, if no change of
				basis splits its action into independent smaller blocks. A₄ is the group of 12 rotations of
				a tetrahedron; A₅ is the group of 60 rotations of an icosahedron. Both have faithful
				three-dimensional rotation representations. These definitions describe possible structure;
				the training labels do not supply the matrices.
			</p>
			<aside class="side">
				<b>Architectural choice</b>A head is a parallel feature channel. Here its dimension d is the
				size of each rotation matrix, separate from the model's token-embedding width.
			</aside>
			<p>
				<strong>Holonomy attention</strong> gives each token a learned rotation U and a scalar gate
				g between zero and one. Write M = gU. A rotation is produced by exponentiating a
				skew-symmetric matrix, an established orthogonal parameterization <Cite
					refs={BIB}
					id="orthogonal"
				/>. For each token i and subset size r, the layer sums products over all r-position subsets
				containing that token, keeping the sequence order:
			</p>
			<MathTex tex={eq.sectors} display />
			<p>
				The integer r is the <strong>arity</strong>. Each token can appear at most once in a subset.
				The individual U matrices are rotations; their gated sums generally are not. The algebra of
				matrices, rather than only the rotation group, holds the layer's resulting features.
			</p>
			<p>
				At d = 2, all rotations commute. The layer reduces to Newton's phase products, up to the
				matrix-to-complex identification. At d ≥ 3, the product can preserve order even without
				position embeddings. This changes the information available to the readout.
			</p>
			<details>
				<summary>The computation · ordered products without enumerating subsets</summary>
				<p>
					A formal variable z records subset size. In the product below, choosing I skips a token
					and choosing zM selects it:
				</p>
				<MathTex tex={eq.polynomial} display />
				<p>The coefficient Eᵣ holds all size-r products. Processing one token at a time gives:</p>
				<MathTex tex={eq.recurrence} display />
				<p>
					For a marked token i, compute these sums on both sides. Lₐ uses a positions before i and
					Rᵦ uses b positions after i:
				</p>
				<MathTex tex={eq.readout} display />
				<p>
					The implementation costs O(nK²Hd³) for n tokens, maximum arity K, H heads and d × d
					matrices. It divides each arity by its subset count, RMS-normalizes it, and combines
					arities with learned weights and one shared projection. This is a dynamic program with
					real internal computation, not a constant-time product oracle.
				</p>
			</details>
		</section>

		<section id="groups">
			<h2><span>5</span> Experiment 2 · make order matter</h2>
			<aside class="side">
				<b>Protocol</b>Three seeds, 6,000 steps, 2,048 held-out sequences; width 64. Matrix heads ×
				dimension ≈ 256. Holonomy and Newton have no positions; softmax does. This is not a
				FLOP-matched comparison.
			</aside>
			<p>
				<strong>Ordered Match-3</strong> labels a token positive when it belongs to a triple whose product,
				taken in sequence order, is the identity—the operation that does nothing. We compare cyclic groups
				Z₁₂ and Z₆₀, where order cannot matter, with A₄ and A₅, where it can. Groups of equal size share
				the same vocabulary size; the smaller tasks have six positions, the larger ones eleven.
			</p>

			<figure id="fig-ladder" class="wide">
				<GroupLadder />
				<figcaption>
					<b>Figure 2.</b> A commuting model cannot cross the dashed population ceiling without additional
					order information. The noncommuting heads do. The vertical lines are exact calculations for
					these task lengths, not fitted to the training results. Dots are three-seed means at 6,000 steps;
					softmax has positional embeddings.
				</figcaption>
			</figure>
			<div class="table-scroll wide">
				<table>
					<thead
						><tr
							><th scope="col">Arm</th>{#each ['Z₁₂', 'A₄', 'Z₆₀', 'A₅'] as group (group)}<th
									scope="col"
									class="num">{group}</th
								>{/each}</tr
						></thead
					>
					<tbody
						>{#each GROUP_ROWS as row (row.id)}<tr
								><th scope="row">{row.label}</th>{#each row.values as value, i (i)}<td class="num"
										>{value.display}{#if value.seeds}<small>({value.seeds})</small>{/if}</td
									>{/each}</tr
							>{/each}</tbody
					>
				</table>
			</div>
			<p class="caption">
				<b>Table 4.</b> Balanced accuracy %, mean (seeds 0, 1, 2), exactly as displayed in
				<a href={source('research/GROUPS.md')}>GROUPS §5.2</a>.
				<a href={source('research/results/grp_e2.jsonl')}>Raw experiment 2</a>. A₅ d = 5 rounds to
				100.0; its individual scores are 99.97, 99.96, 99.98, so this is not literal perfect
				accuracy.
			</p>
			<p>
				Newton and d = 2 stay below the exact order-blind ceilings: <strong
					>A₄ 83.0546984493%</strong
				>
				and <strong>A₅ 77.2287515874%</strong>. The large groups expose a striking training gap:
				positional softmax remains near chance, while noncommuting heads learn the relation. On the
				smaller A₄ task, three softmax layers reach 99.7%; the distinction is already narrower than
				a universal softmax failure.
			</p>
			<h3>What the heads learned</h3>
			<p>
				We test the composition law directly: how close is U(a)U(b) to U(ab), averaged over every
				pair? This is the <strong>homomorphism error</strong>. We also compare each head's trace—the
				sum of its diagonal entries—with the known traces of irreducible representations. These
				diagnostics reveal approximate group structure inside trained heads.
			</p>
			<div class="table-scroll">
				<table>
					<thead
						><tr
							><th scope="col">Group</th><th scope="col">d = 2</th><th scope="col">d = 3</th><th
								scope="col">d = 4</th
							><th scope="col">d = 5</th></tr
						></thead
					>
					<tbody>
						<tr
							><th scope="row">A₄</th><td>none; 1′, 1″; 1′, 1″</td><td>3; 3; 3</td><td
								>3; none; 3</td
							><td>none (×3)</td></tr
						>
						<tr
							><th scope="row">A₅</th><td>none (×3)</td><td>3, 3′; 3, 3′; 3, 3′</td><td
								>3′; 4; 3, 4</td
							><td>5; 5; 4, 5</td></tr
						>
					</tbody>
				</table>
			</div>
			<p class="caption">
				<b>Table 5.</b> Detected irreps per seed, from GROUPS §5.2. Detection requires multiplicity ≥
				½ and homomorphism error &lt; 0.5. “None” means none passed this diagnostic, which can miss structure
				in heads whose gates suppress some elements.
			</p>
			<p>
				The three-dimensional A₅ heads recover both icosahedral irreps, with best reported
				homomorphism errors down to 0.05. The registered dimension prediction was <strong
					>undecided</strong
				>: d = 3 scored 93.4–94.8%, between its decision thresholds. An exploratory 20,000-step
				extension reached <strong>99.21%, 99.38%, 99.34%</strong>. Larger dimensions learn faster in
				these runs; these observations do not prove a universal minimum dimension or exact
				convergence.
			</p>
			<p>
				The earlier hypothesis that accuracy must track the total Fourier mass of available irreps
				was too restrictive. A nonlinear readout with token gates can use a faithful representation
				without holding every irrep. Faithfulness is sufficient under the theorem below; it is not
				necessary.
			</p>
		</section>

		<section id="theory">
			<h2><span>6</span> What can be proved</h2>
			<p class="caption">
				<b>Proved here, with conditions.</b> Full statements and constructions:
				<a href={source('research/THEORY.md')}>THEORY</a>. Numerical checks:
				<a href={source('research/results/theory_checks.json')}>theory_checks.json</a>.
			</p>
			<p>
				The boundary is between <strong>position-free commuting composition</strong> and composition that
				preserves relevant order. It is not a separation between every softmax network and every holonomy
				network.
			</p>
			<Theorem n="1" name="Losing order has a sharp price" evidence="proved">
				<p>
					If a predictor sees only the marked token and the multiset of the other tokens, its best
					possible balanced accuracy is the order-blind Bayes ceiling. More width or a larger
					classifier cannot recover the discarded order.
				</p>
				{#snippet proof()}
					<p>
						Let O be that order-blind observation, p(O) the probability of a positive label given
						it, and π the overall positive rate. The optimal prediction is positive exactly when
						p(O) ≥ π. Comparing the positive and negative contributions at each observation gives:
					</p>
					<MathTex tex={eq.bayes} display />
					<p>
						This bound is attained. Randomization cannot improve the larger of two choices. It
						applies to one position-free Newton layer and to commuting holonomy heads with
						token-only gates and a pointwise readout. It does not apply when positions, causal
						masks, neighborhood information or an order-aware preprocessing layer enter the
						observation.
					</p>
				{/snippet}
			</Theorem>
			<p>
				For Match-3, fixing the marked element gives every other element a unique partner that would
				complete a solution if it came later. Counting the orderings that avoid all such pairs gives
				an exact conditional probability. An integer dynamic program aggregates these probabilities
				to the A₄ and A₅ ceilings above. A₄ also agrees with exhaustive enumeration of all 2,985,984
				sequences and 52,416 observation classes; A₅ is exact without enumerating its full sequence
				space.
			</p>
			<Theorem n="2" name="Faithful rotations suffice for Match-3" evidence="proved">
				<p>
					A faithful orthogonal representation, sufficiently many token-gated heads, and a
					sufficiently wide readout retaining the own-token identity can represent ordered Match-3
					exactly at every fixed length. For A₄ and A₅, a three-dimensional rotation representation
					is sufficient.
				</p>
				{#snippet proof()}
					<p>
						Use paired heads: one multiplies the faithful representation, the other uses identity
						matrices with the same gates. Varying finite positive gates separates candidate triples
						by their token content, including repetitions. For a fixed content triple, its
						successful orders have trace d; all unsuccessful orders, if any successful order exists,
						share a second trace below d. The identity heads count candidates. The trace sum and
						candidate count therefore recover the exact number of successes.
					</p>
					<p>
						For group size m, at most (m + 1)(m + 2) heads suffice; gates can be chosen from ¼, ½
						and ¾. Shared arity normalization preserves the classification margin. The implemented
						SO(d) parameterization requires determinant +1; an O(d) representation can be embedded
						in SO(d + 1). A₄ and A₅ already lie in SO(3).
					</p>
				{/snippet}
			</Theorem>
			<p>
				This is an existence construction with generous head and readout requirements, not a
				certificate for the trained width or gradient descent. The corresponding theorem for
				arbitrary Match-k uses <strong>position-selective gates</strong>. Those gates are not
				silently granted to the position-free experiment, and a token-only sufficiency theorem for
				arbitrary k remains open.
			</p>
			<Theorem
				kind="Corollary"
				n="3"
				name="Faithfulness is stronger than necessary"
				evidence="proved"
			>
				<p>
					For fixed homomorphic matrix families with arbitrarily many token-gated copies and a
					readout retaining the own token, exact Match-3 is possible if and only if the families
					jointly preserve noncommuting pairs: whenever ab ≠ ba, some head must distinguish their
					two product orders.
				</p>
				{#snippet proof()}
					<p>
						If every head makes a and b commute, the triples (a, b, (ab)⁻¹) and (b, a, (ab)⁻¹),
						marked at their final element, collide in every head while their labels differ. Identity
						padding extends this obstruction to every fixed length. Conversely, the token-gate
						counting construction can choose a representation that distinguishes the two
						orientations of each order-sensitive content triple.
					</p>
					<p>
						As a counterexample to faithful-dimension necessity, project A₅ × Z₃ onto a faithful A₅
						representation in SO(3). The map discards the abelian Z₃ factor, so it is not faithful,
						but it preserves every noncommuting pair. With the stated gates it suffices for Match-3
						even though the full group has no faithful orthogonal representation of dimension at
						most three.
					</p>
				{/snippet}
			</Theorem>
			<h3>Softmax's capacity is not the disputed point</h3>
			<p>
				For finite abelian groups at a fixed sequence length, uniform softmax carrying every
				character, an own-token residual and a sufficiently large MLP can implement Match-k. With
				positions and enough heads and width, one softmax layer can recover the full ordered
				sequence and represent any labeling of this finite input domain. These constructive facts
				rule out the broad claim “softmax cannot compose.” What remains is an empirical question of
				learnability and efficiency at realistic resources.
			</p>
		</section>

		<section id="programs">
			<h2><span>7</span> A second test: execute swap programs</h2>
			<aside class="side">
				<b>Preregistered confirmation</b>Predictions committed before the three-seed grid. Six
				instructions, one query; 6,000 steps. <a href={source('research/GROUPS.md')}>GROUPS §8</a>.
			</aside>
			<p>
				Start with two independent sets of four variables, each holding values 0, 1, 2, 3.
				Interleave three random swaps from each set, then query one variable. To answer, a model
				must select the relevant instructions and apply them in order. This is a controlled toy
				program-execution task, not a natural-code benchmark.
			</p>
			<p>
				For example, after <code>swap(0,1); swap(1,2); swap(2,3)</code>, reading variable 0 returns
				1. Reversing those statements returns 3. Knowing which statements occurred is not enough.
			</p>

			<div class="table-scroll">
				<table>
					<thead
						><tr><th scope="col">Arm</th><th scope="col" class="num">Balanced accuracy %</th></tr
						></thead
					>
					<tbody
						>{#each SWAP_ROWS as row (row.id)}<tr
								><th scope="row">{row.label}</th><td class="num"
									>{row.result.display}<small>({row.result.seeds})</small></td
								></tr
							>{/each}
						<tr class="ceiling-row"
							><th scope="row">Exact order-blind population ceiling</th><td class="num"
								>62.037… = 100 × 67/108</td
							></tr
						>
					</tbody>
				</table>
			</div>
			<p class="caption">
				<b>Table 6.</b> Mean (seeds 0, 1, 2), copied from GROUPS §8.3.
				<a href={source('research/results/grp_swap.jsonl')}>Raw swap-program results</a>. The
				ceiling concerns population accuracy; finite test scores can be slightly higher. The
				matrix-state RNN is a generic learned orthogonal recurrence, not a claimed reproduction of a
				published architecture.
			</p>
			<p>
				The commuting models again finish near their exact information ceiling. Holonomy d = 3 and d
				= 4 solve the task. So does the matrix RNN, and so do two or three positional softmax
				layers. Even one softmax layer reaches 98.95%. All four registered criteria hold.
			</p>
			<p>
				<strong
					>This benchmark confirms the symmetry barrier and shows no advantage over order-aware
					baselines.</strong
				> Three relevant instructions create a small finite universe; the experiment does not distinguish
				a general execution algorithm from learning that finite function. It does not test length generalization,
				new variables, natural code, or equal-FLOP efficiency. Independent training and test draws are
				not deduplicated, so exact stream collisions are possible.
			</p>
		</section>

		<section id="word-problems">
			<h3>Word problems · short products help learn the long one</h3>
			<p>
				Here the model reads A₅ or S₅ operations and predicts their running product at every
				position: 60 or 120 classes. A binary variant asks whether that product fixes one letter.
				Predictions were committed before the main grid; 294 runs include pilots, the three-seed
				grid, registered amendments and exploratory follow-ups.
			</p>
			<div class="table-scroll">
				<table aria-label="Word-problem class accuracy">
					<thead>
						<tr>
							<th scope="col">Arm</th>
							{#each wordTasks as task (task)}
								<th scope="col" class="num">{task}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each wordRows as row (row.label)}
							<tr>
								<th scope="row">{row.label}</th>
								{#each wordTasks as task, i (task)}
									<td class="num">{row.scores[i]}</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<p class="caption">
				<b>Table 7.</b> Balanced accuracy %, all positions, three-seed means rounded to one decimal.
				Main-grid runs: width 64, 6,000 steps at length 16; 12,000 at 64. Holonomy uses d = 3 on A₅,
				d = 5 on S₅; the orthogonal RNN uses d = 5 except A₅ at 64 (d = 3). Householder RNN: d = 5;
				it and DeltaProduct use two Householder steps per token on A₅, four on S₅. One layer unless
				shown.
				<a href={source('research/results/wp_main.jsonl')}>Raw results</a>;
				<a href={source('research/GROUPS.md')}>GROUPS §7</a>.
			</p>
			<p>
				<strong>The predicted structural limits held.</strong> A₅ class tracking succeeds with three-dimensional
				rotations; a faithful S₅ representation needs dimension five in one rotation head, or four with
				reflections. Newton stays below its estimated commuting ceiling. One- and two-layer softmax reach
				only 0.8–1.7% in the second half of class sequences. Removing holonomy's prefix product leaves
				positions 1–3 nearly perfect and accuracy at most 10% from position 5 onward. A second layer rescued
				none of the tested failing arms.
			</p>
			<p>
				<strong>The surprise is learning speed.</strong> The prefix is already an orthogonal matrix-state
				RNN. We predicted that adding short-product sectors would change accuracy by at most three points;
				the S₅ gaps above reject that prediction. In the registered 20,000-step amendment runs, the prefix-only
				RNN reaches 100.0% at length 16 and 99.4% at 64. Short products improve speed and reliability
				within this budget, with no demonstrated capacity gain. Householder transitions are faster still
				on S₅ classes: every seed reaches 90% by 1,800 steps at length 16 and 2,400 at 64.
			</p>
			<p>
				<strong>Some predictions failed.</strong> The class-task thresholds hold only after the registered
				amendments; the binary-task prediction remains false. A₅ holonomy d = 3 reaches just 63.0% at
				length 16, while exploratory d = 4 runs reach 100.0% on all three seeds: the label depends on
				a different representation. S₅ binary tracking at 64 also misses its threshold, and DeltaProduct's
				predicted S₅ binary success at 16 fails on one seed (61.7%). An available group representation
				does not by itself guarantee learning the readout.
			</p>
			<p>
				<strong>Length generalization was measured.</strong> Trained at 16 and tested at 64, S₅ holonomy
				d = 5 reaches 97.3% (99.7, 96.9, 95.3); the Householder RNN reaches 98.2%. This rejects the prediction
				that rotations would fail to extrapolate. A₅ holonomy d = 3 reaches 100.0%, but one Householder
				seed falls to 77.2%, another miss. These are finite length tests, not arbitrary-length guarantees.
			</p>
			<p class="caption">
				These comparisons are not matched for parameters or FLOPs. DeltaProduct is a minimal
				width-64 implementation without the published short convolution; its class-task result does
				not establish a limitation of the method <Cite refs={BIB} id="deltaproduct" />. Softmax uses
				learned positions, so its untrained positions 17–64 make its extrapolation scores
				uninterpretable. Full predictions, per-seed results and amendment runs:
				<a href={source('research/GROUPS.md')}>GROUPS §§7.6–7.8</a>.
			</p>
		</section>

		<section id="related">
			<h2><span>8</span> What belongs to this project</h2>
			<p>
				<strong>Ordered-subsequence products are prior art.</strong> Seq2Tens already sums
				noncommutative tensor products over ordered subsequences, graded by their length <Cite
					refs={BIB}
					id="seq2tens"
				/>. Holonomy's matrix polynomial is a compression of that feature map: replace each tensor
				product by ordinary matrix multiplication through the map μ:
			</p>
			<MathTex tex={eq.compression} display />
			<p>
				<strong>Learned rotation products are also prior art.</strong> Path Development Networks
				learn a map into a Lie algebra and compose matrix exponentials along a sequence <Cite
					refs={BIB}
					id="pathdev"
				/>. They are the closest precedent for the learned group products. Seq2Tens is the closest
				precedent for the ordered-subset generating construction. The present distinction is the
				particular gated matrix parameterization and a separate readout for each subset size and
				each token contained in that subset.
			</p>
			<p>
				The broader lineage includes iterated-sums signatures, learned signature transforms and
				attention over signature features <Cite
					refs={BIB}
					id={['iteratedsums', 'deepsignatures', 'roughtransformers']}
				/>. Permutation-invariant pooling is established <Cite refs={BIB} id="zaheer" />. Learned
				group representations have already been recovered from networks trained on group operations <Cite
					refs={BIB}
					id="chughtai"
				/>. Matrix-transition structure has already been linked to state tracking, including in
				DeltaProduct <Cite refs={BIB} id="deltaproduct" />, and transformers can learn automaton
				shortcuts <Cite refs={BIB} id="automata" />.
			</p>
			<p>
				The narrower contribution is the <strong>marked, arity-resolved matrix realization</strong>,
				the task-specific order-blind bound and exact ceiling calculation, the qualified
				constructive Match-3 results, and controlled measurements of what training discovers. Our
				literature audit found no exact prior instance of that complete combination. Two closely
				related thesis leads still require full-text comparison, so we make no first-of-its-kind
				claim. The <a href={source('research/PRIOR_ART.md')}>prior-art audit</a> records the overlap and
				verification status explicitly.
			</p>
		</section>

		<section id="meaning">
			<h2><span>9</span> What the result suggests next</h2>
			<p>
				The useful question has changed from “how many tokens enter one score?” to <strong
					>“which composition law does the layer make easy to learn?”</strong
				> On these controlled tasks, clock arithmetic supports unordered relations; spatial rotations
				preserve the order that changes the answer. A model can discover approximate representations of
				that structure from labels.
			</p>
			<p>
				That is a precise synthetic result. It does not establish a language-model improvement, a
				universal representation-dimension law, a general optimization barrier, or a universal
				advantage over recurrence. Short-product features improved learning speed and reliability
				against the same rotation prefix in these runs; Householder recurrence was faster on S₅
				classes. Whether those gains survive resource matching and natural data remains open.
			</p>
			<ol class="next">
				<li>
					<b>Selection and composition.</b> Test richer query-conditioned subsequences and longer programs,
					with matrix recurrence and strong positional softmax controls.
				</li>
				<li>
					<b>Resource-matched comparisons.</b> Measure accuracy against parameters, training FLOPs and
					time, then test lengths and group elements outside the training regime.
				</li>
				<li>
					<b>Natural data.</b> Evaluate a holonomy branch on language and code only after defining an
					equal-FLOP protocol. The earlier negative language evidence remains the starting point.
				</li>
			</ol>
		</section>

		<section id="reproducibility">
			<h3>Evidence and reproducibility</h3>
			<p>
				The research harness, predictions and raw rows are in <a href={source('research/GROUPS.md')}
					>GROUPS</a
				>; full qualifications and proofs are in <a href={source('research/THEORY.md')}>THEORY</a>.
				Exact ceilings are retained in
				<a href={source('research/results/theory_ceiling.json')}>theory_ceiling.json</a>. The
				initial attention study's full grids remain in
				<a href={source('src/lib/report/results')}>the report result archive</a>. Every plotted
				group value uses the same display precision as its research table.
			</p>
			<p>
				Hand-built representations are checked separately from learned ones. The native A₄/A₅
				Match-3 constructions make zero label errors on 64 test sequences per group before and after
				normalization; arbitrary-k positional constructions are checked separately. These finite
				checks support the implementation, while the mathematical arguments establish the stated
				theorems. The three-seed scores describe this harness and budget; they are not confidence
				intervals or claims of universal convergence.
			</p>
		</section>

		<section id="references" class="refs">
			<h2>References</h2>
			<ol>
				{#each BIB as reference (reference.id)}<li id="ref-{reference.id}">
						{reference.authors}. {#if reference.url}<a href={reference.url} rel="external"
								>{reference.title}</a
							>{:else}{reference.title}{/if}. <span>{reference.venue}, {reference.year}.</span>
					</li>{/each}
			</ol>
		</section>
	</article>
</PageFrame>

<style>
	.paper {
		--text: 680px;
		--side: 208px;
		--gap: 44px;
		max-width: 1012px;
		margin: 0 auto;
		padding: 38px 40px 110px;
		color: var(--color-ink-2);
		font-size: 14px;
		line-height: 1.65;
	}
	.paper :global(:where(section, header) > *:not(.wide, .side)) {
		max-width: var(--text);
	}
	.title-block {
		margin-bottom: 25px;
	}
	.eyebrow {
		color: var(--color-ink-3);
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		margin-bottom: 12px;
	}
	h1 {
		margin: 0;
		color: var(--color-ink);
		font-size: 36px;
		font-weight: 450;
		line-height: 1.12;
		letter-spacing: -0.04em;
	}
	.subtitle {
		margin: 8px 0 0;
		font-size: 16px;
	}
	.authors {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 16px;
		margin: 16px 0 0;
		color: var(--color-ink);
		font-size: 12px;
	}
	.authors span {
		color: var(--color-ink-3);
	}
	section {
		clear: both;
		scroll-margin-top: calc(var(--bar-h) + 20px);
	}
	.side {
		float: right;
		clear: right;
		width: var(--side);
		margin: 4px 0 15px 36px;
		color: var(--color-ink-3);
		font-size: 11px;
		line-height: 1.65;
	}
	.side b {
		display: block;
		color: var(--color-ink-2);
		font-weight: 500;
		margin-bottom: 5px;
	}
	.abstract {
		font-size: 14px;
		color: var(--color-ink);
		line-height: 1.75;
	}
	.reading {
		margin-top: 18px;
		font-size: 12px;
		color: var(--color-ink-3);
	}
	h2 {
		margin: 50px 0 16px;
		color: var(--color-ink);
		font-size: 23px;
		font-weight: 500;
		letter-spacing: -0.025em;
		line-height: 1.25;
	}
	h2 > span {
		color: var(--color-ink-3);
		display: inline-block;
		margin-right: 12px;
		font-size: 15px;
		font-weight: 400;
	}
	h3 {
		margin: 30px 0 12px;
		color: var(--color-ink);
		font-size: 16px;
		font-weight: 500;
		line-height: 1.4;
	}
	p {
		margin: 0 0 15px;
	}
	strong,
	b {
		color: var(--color-ink);
		font-weight: 550;
	}
	a {
		color: inherit;
		text-underline-offset: 3px;
		text-decoration-color: var(--color-ink-3);
	}
	a:hover {
		color: var(--color-ink);
	}
	figure {
		clear: both;
		margin: 28px 0 26px;
		scroll-margin-top: calc(var(--bar-h) + 24px);
	}
	figure > :global(div) {
		max-width: 800px;
	}
	figcaption,
	.caption {
		max-width: var(--text);
		margin: 13px 0 22px;
		color: var(--color-ink-3);
		font-size: 11px;
		line-height: 1.6;
	}
	.table-scroll {
		clear: both;
		overflow-x: auto;
		margin: 20px 0 0;
		padding-bottom: 3px;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 12px;
		line-height: 1.5;
	}
	th,
	td {
		padding: 10px 14px 10px 0;
		text-align: left;
		vertical-align: top;
		font-weight: 400;
	}
	th:last-child,
	td:last-child {
		padding-right: 0;
	}
	thead {
		border-top: 1px solid var(--color-ink-3);
		border-bottom: 1px solid var(--color-ink-3);
		color: var(--color-ink-3);
	}
	tbody {
		border-bottom: 1px solid var(--color-ink-3);
	}
	tbody th {
		color: var(--color-ink);
		min-width: 165px;
	}
	.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	td small {
		display: block;
		color: var(--color-ink-3);
		font-size: 10px;
		white-space: nowrap;
	}
	.language-table tbody th {
		min-width: 140px;
	}
	.ceiling-row {
		color: var(--color-ink-3);
	}
	.ceiling-row th {
		color: inherit;
	}
	details {
		margin: 22px 0;
		font-size: 13px;
	}
	summary {
		cursor: pointer;
		color: var(--color-ink);
		font-size: 12px;
		padding: 8px 0;
	}
	details[open] summary {
		margin-bottom: 10px;
	}
	code {
		font: 0.9em var(--font-mono);
		color: var(--color-ink);
		overflow-wrap: anywhere;
	}
	.next {
		list-style: decimal;
		padding-left: 18px;
	}
	.next li {
		padding-left: 5px;
		margin-bottom: 10px;
	}
	.refs ol {
		list-style: decimal;
		padding-left: 21px;
		font-size: 12px;
		line-height: 1.6;
	}
	.refs li {
		margin-bottom: 12px;
		padding-left: 3px;
		scroll-margin-top: calc(var(--bar-h) + 20px);
	}
	.refs li span {
		color: var(--color-ink-3);
	}
	@media (max-width: 1179px) {
		.paper {
			max-width: 800px;
		}
		.side {
			float: none;
			width: auto;
			margin: 0 0 15px;
			max-width: var(--text);
		}
		.side b {
			display: inline;
			margin-right: 7px;
		}
	}
	@media (max-width: 700px) {
		.paper {
			padding: 28px 20px 80px;
			font-size: 13px;
		}
		h1 {
			font-size: 31px;
		}
		.subtitle {
			font-size: 14px;
			line-height: 1.5;
		}
		h2 {
			font-size: 21px;
			margin-top: 40px;
		}
		h3 {
			font-size: 15px;
		}
		.abstract {
			font-size: 13px;
		}
		th,
		td {
			padding: 9px 14px 9px 0;
		}
		table {
			font-size: 11px;
		}
		tbody th,
		.language-table tbody th {
			min-width: 96px;
		}
		.num,
		td small {
			white-space: normal;
		}
		td small {
			font-size: 9px;
		}
		th,
		td {
			padding-right: 8px;
		}
		.side {
			font-size: 11px;
		}
		.reading {
			font-size: 11px;
		}
	}
</style>
