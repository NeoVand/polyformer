<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import Theorem from '#lib/report/Theorem.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { NERODE, ORACLE } from '#lib/viz/computeGraphs.ts';
	import ExactFigure from '../ExactFigure.svelte';
	import ExecFigure from '../ExecFigure.svelte';
	import ArithFigure from '../ArithFigure.svelte';
	import SeedGrid, { type SeedRow } from '../SeedGrid.svelte';
	import { number, roman } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	const objective = String.raw`\begin{aligned} \mathcal L \;=\;& \operatorname{CE}\big(x_{t+1} \,\big|\, h(x_{\le t})\big) \\ &+\; \mu \operatorname*{E}_{u \sim v} d(z_u,\, z_v) \\ &+\; \lambda \operatorname*{E}_{u \not\sim v'} \max\big(0,\, m - d(z_u,\, z_{v'})\big) \end{aligned}`;
	const bisim = String.raw`d(u, v) = (1-\gamma)\,\|o(u) - o(v)\|_{\mathrm{TV}} + \gamma \operatorname*{E}_{x} d(ux, vx)`;
	const metricLoss = String.raw`\begin{aligned} \mathcal L_M = \operatorname*{E}_{u,v,x} \Big[ & d_N\big(h(u), h(v)\big) - (1-\gamma)\|o(u) - o(v)\|_{\mathrm{TV}} \\ & - \gamma \operatorname{sg} d_N\big(h(ux), h(vx)\big) \Big]^2 \end{aligned}`;
	// research/LEAN_H.md 3.1 and 3.2 (seeds 0 / 1 / 2): exact match at 8, 64, 256, 1,024 and 4,096 steps;
	// the recurrence is LEAN_H's control under the same compiler flag, the term its rerun of LEAN_S1's arm
	const lengthRows: SeedRow[] = [
		{
			name: 'recurrence',
			cells: [
				[1, 1, 1],
				[0.924, 0.674, 0.984],
				[0.527, 0, 0.949],
				[0.43, 0, 0.891],
				[0.406, 0, 0.746]
			]
		},
		{
			name: '+ term',
			cells: [
				[1, 1, 1],
				[1, 1, 1],
				[1, 1, 1],
				[1, 0.754, 1],
				[1, 0.555, 1]
			]
		},
		{
			name: '+ next-latent',
			cells: [
				[1, 1, 1],
				[1, 1, 1],
				[1, 1, 1],
				[1, 0.996, 1],
				[0.988, 0.992, 1]
			]
		},
		{
			name: '+ both',
			cells: [
				[1, 1, 1],
				[1, 1, 1],
				[1, 1, 1],
				[1, 1, 1],
				[1, 1, 1]
			]
		},
		{
			name: 'transformer',
			cells: [
				[0.98, 0.984, 0.984],
				[0.066, 0.047, 0.053],
				[0.035, 0.012, 0.018],
				[0.012, 0, 0.004],
				null
			]
		}
	];
	// LEAN_S1 6.2 and its decoder pilot, LEAN_N 5, 7, 10, 11.2 and 12.5: unrelated-state distance under the term
	const heads = [
		{
			label: 'Linear, per position (stage one)',
			lin: 'yes',
			unrelated: '0.42–0.52',
			exact: '3 of 3'
		},
		{
			label: 'Linear, per position, chains in proof format',
			lin: 'yes',
			unrelated: '0.19–0.27',
			exact: '3 of 3'
		},
		{ label: 'Linear, the change', lin: 'yes', unrelated: '0.23–0.26', exact: '2 of 2' },
		{
			label: 'Verdict head, conditioned on the probe',
			lin: 'for each probe',
			unrelated: '0.18–0.20',
			exact: '2 of 2'
		},
		{
			label: 'Autoregressive decoder, two blocks',
			lin: 'no',
			unrelated: '0.010',
			exact: '0 of 2 (pilot)'
		},
		{ label: 'MLP, per position', lin: 'no', unrelated: '0.005–0.009', exact: '0 of 3 (≤ 0.02)' },
		{ label: 'Copy head into the premises', lin: 'no', unrelated: '0.014–0.016', exact: '0 of 2' }
	];
	// COURSE.md 4.2 with the amendments of 4.4 and 4.5; LEAN_N 12.3 and 12.5
	const oracle = [
		{
			clause: 'gate',
			registered:
				'Chains first: the combination exact in its verdicts at 256 steps on both seeds, under one configuration',
			status:
				'passed: 1.00000 on both seeds at 24,000 steps (linear head 0.576 / 0.580; probe-conditioned at 12,000 steps 0.99999 / 0.99146)'
		},
		{
			clause: 'P1',
			registered:
				'Tracking exists: at depth 1 the combination beats the state-blind arm on the hard class by at least 10 points, on both seeds; otherwise the direction stops',
			status: 'fails'
		},
		{
			clause: 'P2',
			registered:
				'Exactness carries: from depth 1 to depths 4–6 the combination loses at most half the points the plain recurrence loses, and is at least 5 points above the transformer at depths 4–6 and 7–12',
			status: 'fails'
		},
		{
			clause: 'P3',
			registered:
				'The prover guard: at depths 4–6, keeping 90% of accepted probes, it rejects at least half of the rejected ones',
			status: 'fails'
		}
	];
	// research/EXEC_LM.md section 4 (seeds 0 / 1 / 2): the registered clauses and what the batch returned
	const execClauses = [
		{
			clause: 'P1',
			registered: 'The slot with the objective exact (≥ 0.99) at 256 statements on 3 of 3 seeds',
			measured: '1.000 / 1.000 / 1.000',
			verdict: 'pass'
		},
		{
			clause: 'P2',
			registered: 'The final-state arm below 0.5 at 64 on 3 of 3',
			measured: '0.340 / 0.342 / 0.340',
			verdict: 'pass'
		},
		{
			clause: 'P3',
			registered:
				'Chain of thought lower at 256 than at 16 on 3 of 3, lower at 1,024 than at 256 on the mean, at 8 tokens per statement',
			measured: '1.000 to 0.055 / 0.316 / 0.367; mean 0.246 to 0.198',
			verdict: 'pass'
		},
		{
			clause: 'P4',
			registered: 'The slot alone below 0.95 at 256 on at least one seed',
			measured: '0.072 / 0.053 / 0.137',
			verdict: 'pass'
		},
		{
			clause: 'Kill',
			registered: 'The objective exact at 256 on no more seeds than the slot alone',
			measured: '3 against 0',
			verdict: 'does not fire'
		},
		{
			clause: 'Norm',
			registered: 'With the slot at a fixed norm, exact at 1,024 on 3 of 3 seeds, on Modal',
			measured: '1.000 / 1.000 / 1.000',
			verdict: 'pass'
		}
	];
	// research/LEAN_S1.md, section 6.2: the registered clauses and what the batch returned
	const predictions = [
		{
			clause: 'P1',
			registered: 'Recurrence + term exact (≥ 0.99) at 256 steps on 3 of 3 seeds',
			measured: '1.000 / 1.000 / 1.000 at 256, and at 1,024',
			verdict: 'pass'
		},
		{
			clause: 'P2',
			registered: 'Recurrence below 0.95 at 256 on at least one seed',
			measured: '0.004 / 0.027 / 0.891',
			verdict: 'pass'
		},
		{
			clause: 'P3',
			registered: 'Transformer below 0.50 at 256 on 3 of 3',
			measured: '0.019 / 0.012 / 0.010',
			verdict: 'pass'
		},
		{
			clause: 'P4',
			registered:
				'Growth of the pair distance from 8 to 256 predicts the drift over the recurrence runs, Spearman ≥ 0.7',
			measured: '+0.75 over 9 runs; +0.85 against the drift to 1,024',
			verdict: 'pass'
		},
		{
			clause: 'P5',
			registered: 'The control does not raise the exact count',
			measured: '0 of 3',
			verdict: 'pass'
		},
		{
			clause: 'Kill',
			registered: 'Recurrence + term exact on no more seeds than the recurrence',
			measured: '3 against 0',
			verdict: 'does not fire'
		},
		{
			clause: 'Also',
			registered: 'Transformer exact at the training length on 3 of 3',
			measured: '0.70 / 0.76 / 0.76',
			verdict: 'fails',
			quiet: true
		}
	];
</script>

<section class="part" id="part-exact">
	<header class="part-head">
		<span class="roman">Part {roman('part-exact')}</span>
		<h2>States that stay exact</h2>
		<p class="part-lede">
			Part {roman('part-results')} showed layers that learn a group's own representation. Carrying that
			state exactly along a sequence far longer than any seen in training is a different problem, and
			every construction we tried has the same failure: training finds the exact transition on some seeds
			and a slowly drifting one on others, at the same training loss. This part says why the objective
			forces that, states the term that removes it, and tests the term where a proof assistant certifies
			every pair of equivalent histories. With the term, a recurrence trained on 8 rewrite steps tracks
			1,024 exactly, on every seed. A second night tested that result harder, found what the exact state
			is, and took the method to natural proofs, where it failed in a way that changed the target. A third
			put a pretrained code model in the loop: read through it, a slot carries the exact state of a program
			64 times past its training length without generating a token.
		</p>
	</header>

	<section class="chapter" id="flat-set">
		<h3><span class="n">{number('flat-set')}</span>Why training lands near exact</h3>
		<p class="src">
			<span class="mark new"></span>The argument and its proof (EXACTNESS §1, PROOFS A1);
			<span class="mark measured inline"></span>six seeds of the group task (INVARIANCE), the rerun
			of one seed on two machines (LEAN_S1)
		</p>
		<p>
			Call a carried state <em>exact</em> when the learned transition composes the events
			faithfully, so that the state after a history depends only on what that history determines
			about the future; call it <em>near-exact</em> when each step adds a small error <MathTex
				tex={String.raw`\varepsilon`}
			/>. A loss computed on training sequences of length <MathTex tex="L" /> cannot tell the two apart.
			The errors add to at most <MathTex tex={String.raw`L\varepsilon`} /> over a sequence, and about
			<MathTex tex={String.raw`\sqrt{L}\,\varepsilon`} /> when they point in random directions; the loss
			is smooth at its minimum, so it rises by at most of order <MathTex
				tex={String.raw`L^2\varepsilon^2`}
			/>, or <MathTex tex={String.raw`L\varepsilon^2`} />, scaled by its own floor once the readout
			has a margin. Exactness at a test length <MathTex tex="N" /> asks something else: the accumulated
			error must stay inside the readout's decision margin, which needs <MathTex
				tex={String.raw`\varepsilon`}
			/> of order <MathTex tex="1/N" />. The two requirements come apart as soon as <MathTex
				tex="N"
			/> is much larger than <MathTex tex="L" />. The exact transition and a whole family of
			drifting ones are then one minimiser to the precision of the loss, a flat set, and which point
			of it training reaches is decided by initialisation and rounding.
		</p>
		<Theorem
			kind="Proposition"
			n="4"
			name="A length-L loss is blind to small per-step error"
			evidence="proved"
		>
			<p>
				Let the learned transition differ from an exact one by at most <MathTex
					tex={String.raw`\varepsilon`}
				/> per step on the exact states, not amplify errors, and feed a readout whose logits change by
				at most <MathTex tex="K" /> per unit of state; let <MathTex tex={String.raw`\rho_L`} /> be the
				loss of the exact transition at length <MathTex tex="L" />. Then the length-<MathTex
					tex="L"
				/> loss exceeds <MathTex tex={String.raw`\rho_L`} /> by at most <MathTex
					tex={String.raw`\rho_L\,(e^{\sqrt2 K\varepsilon L} - 1)`}
				/> when the errors add coherently, and by about <MathTex
					tex={String.raw`K^2\varepsilon^2 L`}
				/> when they are random, while exactness at length <MathTex tex="N" /> requires <MathTex
					tex={String.raw`\sqrt2 K\varepsilon N`}
				/> below the logit margin <MathTex tex={String.raw`m \approx \log(1/\rho_L)`} />. The
				training loss therefore cannot certify exactness beyond <MathTex
					tex={String.raw`N \approx 0.85\, mL`}
				/>
				(coherent) or of order <MathTex tex={String.raw`m^2 L`} /> (random). At <MathTex
					tex="L = 16"
				/> and <MathTex tex={String.raw`\rho_L = 5 \cdot 10^{-4}`} />, the loss of the group task
				can certify 64 events and cannot certify 256.
			</p>
			{#snippet proof()}
				<p>
					The state error after <MathTex tex="t" /> steps is at most <MathTex
						tex={String.raw`t\varepsilon`}
					/> (coherent) or of root-mean-square size <MathTex
						tex={String.raw`\sqrt t\,\varepsilon`}
					/>
					(a martingale). For logits <MathTex tex="z" /> with error probability <MathTex
						tex="s(z)"
					/>, a perturbation <MathTex tex="u" /> changes the cross-entropy by at most <MathTex
						tex={String.raw`s(z)\,(e^{a} - 1)`}
					/> with <MathTex tex={String.raw`a \le \sqrt2\,\|u\|`} />, and leaves the argmax unchanged
					whenever <MathTex tex={String.raw`\sqrt2\,\|u\| < m(z)`} />; summing over the positions
					gives the bounds, and <MathTex tex={String.raw`s \le \rho_L`} /> at the exact state. Two explicit
					transitions, one coherent with <MathTex tex={String.raw`\varepsilon = 0.049`} /> and one random
					with <MathTex tex={String.raw`\varepsilon = 0.35`} />, are invisible at 16 and wrong at
					256.
				</p>
			{/snippet}
		</Theorem>
		<p>
			That is what the measurements show. On the <MathTex tex="S_5" /> word problem of section {number(
				'word-problems'
			)}, carried by a per-event recurrence and trained on 16 events, the recurrence is exact at 256
			events on three seeds of six, at training losses that do not separate the exact seeds from the
			drifting ones. On the certified rewrite chains of section {number('certified')}, the same seed
			in the same configuration was exact at 256 steps on one H100 and at chance on another: the
			container's rounding chose. More data at the same length does not move the flat set, and
			longer training sequences shrink it only as <MathTex tex="1/L" />, a constant factor at a
			linear cost. The fix has to be a term that sees the per-step error at first order.
		</p>
	</section>

	<section class="chapter" id="nerode-term">
		<h3><span class="n">{number('nerode-term')}</span>One state for equivalent histories</h3>
		<p class="src">
			<span class="mark prior"></span>Nerode equivalence and bisimulation <Cite
				id={['nerode', 'park', 'milner', 'rutten']}
			/>, state abstraction by equivalence <Cite id={['givan', 'vanderpol']} />, the names
			compression and distinction <Cite id="vafa" />;
			<span class="mark new inline"></span>the objective, the two corrections and the two halves
			(EXACTNESS §§2, 7; PROOFS A2–A6);
			<span class="mark measured inline"></span>75 runs on the group task, registered first
			(INVARIANCE)
		</p>
		<p>
			Two histories are <em>equivalent</em>, written <MathTex tex={String.raw`u \sim v`} />, when
			every continuation has the same future after either: in the word problem, when the words
			multiply to the same group element; in a rewrite chain, when both end at the same expression;
			in language, roughly, when two prefixes are paraphrases. Nerode's theorem says that the
			classes of this relation are the states of the smallest automaton that predicts the data <Cite
				id="nerode"
			/>. The same idea stated between processes rather than histories is bisimulation <Cite
				id={['park', 'milner', 'rutten']}
			/>, and in reinforcement learning it is the criterion for collapsing a Markov decision process
			to its minimal model <Cite id={['givan', 'vanderpol']} />. An exact state map sends equivalent
			histories to one state and inequivalent ones to different states.
		</p>
		<p>
			The term asks for the first half directly. Let <MathTex tex="h(u)" /> be the carried state after
			history <MathTex tex="u" />, and <MathTex tex="N" /> the normalisation the readout applies before
			it reads the state, a LayerNorm in every model here. To the next-token loss, add on sampled equivalent
			pairs a distance between the two normalised states. For a drifting transition the two states move
			apart along the longer history, so the term grows with the drift at first order, where the loss
			of section {number('flat-set')} is flat. With the second half written out as well:
		</p>
		<Theorem kind="Definition" name="The Nerode objective">
			<p>
				For a primary loss on the next token, sampled equivalent pairs <MathTex
					tex={String.raw`u \sim v`}
				/>, and sampled inequivalent pairs <MathTex tex={String.raw`u \not\sim v'`} /> whose futures differ
				at an observed position, write <MathTex tex={String.raw`z_u = N h(u)`} /> for the readout's view
				of the state and add two terms to the primary loss:
			</p>
			<MathTex tex={objective} display />
			<p>
				with <MathTex tex="d" /> a distance on normalised states and <MathTex tex="m" /> a margin. The
				second term is <em>compression</em>: it needs known equivalents, such as reduced words,
				certified rewrites or paraphrases. The third is <em>distinction</em>: it needs known
				inequivalents whose futures differ where the loss looks.
			</p>
		</Theorem>
		<div class="figure wide graph">
			<ComputeGraph
				graph={NERODE}
				label="Computation graph of the per-event recurrence with the Nerode term"
			/>
		</div>
		<p class="caption">
			Two equivalent histories run through one recurrence with the same weights. At each event the
			slot <MathTex tex="w" /> attends to the event's tokens from a query <MathTex
				tex={String.raw`\mathrm{LN}(w)`}
			/> and an MLP updates it, four ticks per event with residuals; the readout reads <MathTex
				tex={String.raw`\mathrm{LN}(w)`}
			/>. The term compares the two readout views by <MathTex tex={String.raw`1 - \cos`} /> and adds <MathTex
				tex={String.raw`\mu`}
			/> times it to the cross-entropy. Dashed: the slot carried to the next event.
		</p>
		<p>
			<strong>Two corrections</strong>, both found by the group test and both now part of the
			theory. First, <em>measure the distance where the state is read</em>. As first written, the
			term used a root-mean-square distance on the raw state. The recurrence has a direction its
			LayerNorm discards, a common shift of every coordinate, and training paid the term by growing
			the state along it: equivalent and unrelated states alike came within 0.002, the readout's
			view was untouched, and the term made the drift worse (0 of 3 seeds exact, against 2 of 3
			without it). Measured as a centred cosine, the readout's own view, it selects: 5 of 6 seeds
			exact at 256 events with a word's reduced form as its partner, and 3 of 3 exact to 1,024 with
			random equivalent words of every length, against 3 of 6 without the term. Second,
			<em>start the term after a representation exists</em>. For a state carried as a rotation, the
			term is already zero when every event is the identity, and switched on from the start it keeps
			the model there: 0 of 9 runs trained, under three schedules. Held at zero for 1,500 steps and
			then ramped, the same state is exact to 1,024 on 3 of 3. The identity is a strict saddle of
			the joint objective whose escape rate falls as <MathTex tex={String.raw`1/\mu`} />, and a
			watershed at a quarter turn per transposition separates it from the faithful representation:
			the remedy is a delay, not a ramp.
		</p>
		<Theorem
			kind="Proposition"
			n="5"
			name="What the term selects, and which distances select"
			evidence="proved"
		>
			<p>
				At an exact solution whose readout has margin <MathTex tex="m" />, along a direction in
				which the transition drifts, the cross-entropy has gradient and curvature of order <MathTex
					tex={String.raw`e^{-m} \approx \rho_L`}
				/>, and in at least seven directions of the normalised state none at all; the term has zero
				gradient and curvature <MathTex tex={String.raw`\mu\,\|A(u) - A(v)\|^2`} />, the squared
				difference of the drift accumulated along the two histories, with no margin factor. It has
				no trivial minimum exactly when <MathTex tex="d" /> factors through the readout's normalisation
				<MathTex tex="N" /> and is non-degenerate there: the raw Euclidean distance fails by scale, the
				root-mean-square distance by the mean shift the recurrence can produce with one parameter, and
				the centred cosine passes. Its zero set is every transition whose normalised state is constant
				on the equivalence classes, not the exact transition alone, so distinction has to come from elsewhere:
				an emission that already separates the states, a distinction term, or recurrence through the normalised
				state with observed distinguishing futures.
			</p>
			{#snippet proof()}
				<p>
					Write the learned transition as the exact one plus <MathTex
						tex={String.raw`\varepsilon\delta`}
					/> and propagate each step's error along the exact flow to the end of the history; the normalised
					states of a pair differ by <MathTex
						tex={String.raw`\varepsilon\,(A(u) - A(v)) + O(\varepsilon^2)`}
					/>. For <MathTex tex={String.raw`d_{\cos} = \tfrac12\|z_u - z_v\|^2`} /> the value is second
					order, the gradient first order and the curvature <MathTex
						tex={String.raw`\|A(u) - A(v)\|^2`}
					/>, independent of the readout. The cross-entropy's Hessian in the logits is bounded by
					its error probability, of order <MathTex tex={String.raw`e^{-m}`} />, and its readout has
					rank at most 119 on the 126-dimensional tangent space of the centred sphere in
					<MathTex tex={String.raw`\mathbb R^{128}`} />. LayerNorm is invariant under <MathTex
						tex={String.raw`w \mapsto w + \alpha\mathbf 1`}
					/>, which the recurrence propagates exactly, and the root-mean-square distance of any two
					states tends to zero under it: a distance that factors through <MathTex tex="N" /> is constant
					on those fibres and vanishes only where the readout's views agree. A three-state automaton with
					two states of equal emission shows raw recurrence alone does not separate the classes.
				</p>
			{/snippet}
		</Theorem>
		<p>
			<strong>The two halves.</strong> Compression cannot create a state the primary loss does not
			need. If the loss is satisfied by a state that ignores the input, the constant map has zero
			compression, and training collapses onto it; our first attempt at a language form, with
			paraphrase pairs, did exactly that. Distinction comes for free when the primary loss is
			<em>dense</em> in the state, every supervised position revealing it: group words, program
			traces, rewrite chains. It has to be added as a term, or manufactured in the data, when the
			loss is not dense, and on text about one token in a hundred depends on the state (section {number(
				'dilution'
			)}). Two more things the group test settled. Pairs that share the path and differ only in
			distractors leave the drift at the base's value (2 of 3 exact, as without the term), so the
			mechanism is invariance across paths and not a generic consistency regulariser. And the
			diagnostic is the <em>growth</em> of the distance along the sequence, not its level at the training
			length: over 42 runs the growth from 16 to 256 events predicts the drift at Spearman +0.86 to 256
			and +0.91 to 1,024, while the level predicts nothing (−0.16).
		</p>
	</section>

	<section class="chapter" id="certified">
		<h3><span class="n">{number('certified')}</span>Lean as the referee</h3>
		<p class="src">
			<span class="mark new"></span>Certified rewrite chains as a test of the term (LEAN_S1);
			<span class="mark prior inline"></span>Lean 4 <Cite id="lean4" />;
			<span class="mark measured inline"></span>predictions registered before the batch, three
			seeds, 12 H100 jobs; the group task (INVARIANCE)
		</p>
		<p>
			The group task has one weakness as a test: equivalence is known because we built the group.
			The second test takes its equivalences from a proof assistant. A state is an expression tree
			over four natural-number atoms, 960 trees in all; a history is a start expression followed by
			rewrite steps, each one core Lean lemma (commutativity or associativity of <MathTex tex="+" /> or
			<MathTex tex={String.raw`\times`} />) at one named position; two histories are equivalent
			exactly when they end at the same tree, since the tree determines every future state. Lean 4 <Cite
				id="lean4"
			/> certifies every step, by rewriting the left side of <MathTex
				tex={String.raw`e_k = e_{k+1}`}
			/> with the lemma, and every equivalence, by <code>rfl</code>, syntactic identity of the two
			trees; a step counts only on Lean's positive confirmation that the proof rests on no admitted
			axiom, since Lean stops reporting errors after a hundred in a file. 1.3 million certificates,
			none failed, about fifteen minutes on a laptop with Lean 4.35. Nothing enters the term
			uncertified, and the trace is dense: every step changes the tree.
		</p>
		<p>
			Four arms, three seeds each, on Modal H100s: the recurrence of the graph above (one slot of
			width 128, four ticks per event, a linear position-wise readout of the tree's seven tokens);
			the same with the term on random certified partners, measured as a centred cosine, <MathTex
				tex={String.raw`\mu = 1`}
			/>, held at zero for 2,400 of 12,000 steps and then ramped; the same term on
			<em>inequivalent</em> pairs at the same cost, as a control; and a four-layer transformer over
			the events at equal per-event compute. Training chains have 8 steps, with two certified
			partners each; <em>exact</em> means the whole decoded tree is right at the last step of a held-out
			chain run free, with no teacher forcing. The predictions were written down before the batch.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<ExactFigure />
				<figcaption>
					Left: exact match of the decoded state at the last step of held-out chains, by chain
					length, trained at 8 steps; thin lines are seeds, the heavy line their mean. Right: the
					centred-cosine distance between the states of certified-equivalent held-out pairs, by
					length (not evaluated at 1,024). The recurrence with the term is exact to 1,024 on every
					seed and its pair distance does not grow; without the term it is exact at the training
					length and loses the tree by 256 on two seeds of three, its pair distance growing seven-
					to eightfold; the control pulls every state together and destroys the readout; the
					transformer never learns the task in distribution.
				</figcaption>
			</figure>
		</div>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Registered before the batch</th><th>Measured</th><th>Verdict</th></tr></thead
				>
				<tbody>
					{#each predictions as r (r.clause)}
						<tr class:quiet={r.quiet}>
							<th>{r.registered}</th><td>{r.measured}</td><td class="verdict">{r.verdict}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			The registered clauses of the Lean stage and what the batch returned; seeds 0, 1 and 2. The
			last row was predicted but was not a verdict.
		</p>
		<p>
			Every registered clause holds and the kill does not fire. The recurrence with the term is
			exact at 8, 64, 256 and 1,024 steps on all three seeds, 128 times its training length, with
			the pair distance at 0.0002 and flat along the sequence; no held-out chain diverges at any
			step. The recurrence without it is exact at 8 on every seed and collapses by 256 on two, its
			pair distance growing from 0.11 to 0.81 and 0.91, and holds on the third, where the distance
			grows only to 0.16: the order the growth diagnostic predicts. The control makes the point
			about what the term is not: pulling inequivalent states together brings them within 0.005 of
			one another and destroys the readout, 2 to 8% of trees right after 64 steps. The invariance
			effect is to pull <em>equivalent</em> states together while the primary loss keeps inequivalent
			ones apart, and the kernel's certificate of equivalence is what makes the first half well defined.
		</p>
		<p>
			The group task, registered the same way, tells the same story once the two corrections are in,
			and it is where they came from: the predictions as registered, with the root-mean-square
			distance, failed, and passed under the cosine variant registered beside them. Trained on only
			8 events, the base recurrence is at chance by 256 on every seed and the term with random
			partners is exact on 3 of 3. One more lesson came from the chains. Under an autoregressive
			decoder the term collapsed the state, unrelated trees 0.010 apart, because a two-block decoder
			can amplify any residual difference for free; a linear head, read where the term is measured,
			closed that minimum. Measure invariance through a head that cannot invert it, or add the
			distinction half.
		</p>
	</section>

	<section class="chapter" id="exact-limits">
		<h3><span class="n">{number('exact-limits')}</span>What is shown, and what is not</h3>
		<p class="src"><span class="mark new"></span>Our reading of the two tests</p>
		<p>
			Shown: a loss at the training length cannot select the exact transition, the invariance term
			can, and on two tasks where every equivalence is known it does, on every seed, at 32 to 128
			times the training length. Not shown: the domain is a first-tier synthetic one. The state
			space is finite, 960 trees, and every transition is seen in training, so this is the group
			setting with a kernel attached and not compositional generalisation; at five and six atoms the
			one-slot recurrence memorised its chains instead of learning the rewrite, and the plan's six
			to eight atoms were not reached. The transformer control is under-trained, 0.70 to 0.76 exact
			at the training length, so its collapse at 256 is partly a failure to learn the task at this
			budget, and a larger or longer-trained transformer is the fair comparison. The second tier,
			distributivity, is generated and tested but was not run. Seeds 0 and 1 of the two recurrence
			arms were the calibration pilot, rerun; seed 2 and the other arms were new. And the language
			form is open: paraphrase gives the equivalences only approximately, text supplies distinction
			only at the decision density, and the dense primary loss the theory asks for, a running state
			the text determines at every position, would have to be manufactured.
		</p>
		<p>
			<strong>Provenance.</strong> The theory of the flat set, the objective and its two corrections
			are new in this project. The Nerode and bisimulation lineage is prior work <Cite
				id={['nerode', 'park', 'milner', 'rutten', 'givan']}
			/>; the closest prior results we found are a proof that zero contrastive loss gives a Markov
			decision process homomorphism, with no claim about length <Cite id="vanderpol" />, and the
			compression and distinction metrics used to evaluate a generative model's world model <Cite
				id="vafa"
			/>; we found no earlier result that measures exact state identity at many times the training
			length from such an objective. The certificates were measured with Lean 4.35, the training on
			Modal; the group study cost $3.89 and the Lean stage $9.85. Full records, with every
			registered clause:
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/EXACTNESS.md`}>EXACTNESS</a>,
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/PROOFS.md`}>PROOFS</a>,
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/INVARIANCE.md`}>INVARIANCE</a> and
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/LEAN_S1.md`}>LEAN_S1</a>.
		</p>
	</section>

	<section class="chapter" id="hardening">
		<h3><span class="n">{number('hardening')}</span>Harder tests of the same result</h3>
		<p class="src">
			<span class="mark prior"></span>Next-latent prediction <Cite id="nextlat" />;
			<span class="mark measured inline"></span>five studies, each registered before its spend
			(LEAN_H, LEAN_S, METRIC, EXEC_D; 23 October); seeds stated with every number
		</p>
		<p>
			The limits above are where the first test left things. The night after, registered studies
			pressed on each of them, and on the comparison the first test lacked: the nearest prior
			method. <em>Next-latent prediction</em> (NextLat) trains a model to predict its own next state
			from the current state and the next input, against a target held fixed by a stop-gradient <Cite
				id="nextlat"
			/>. It uses no equivalent pairs at all. On the same recurrence and the same chains it is exact
			at 256 steps on 3 of 3 seeds and at 4,096 on 2 of 3 (0.988 / 0.992 / 1.000); our registered
			prediction that it would fall short failed. The invariance term alone, rerun on the same
			seeds, is exact at 4,096 on 2 of 3. The two together are exact at every length to 4,096 on 3
			of 3, 512 times the training length, with the lowest pair distance of any arm (0.00012).
		</p>
		<div class="figure wide">
			<figure class="pf">
				<SeedGrid
					lengths={[8, 64, 256, 1024, 4096]}
					rows={lengthRows}
					axis="rewrite steps; trained at 8"
					label="Exactness of each seed by chain length, for five models"
				/>
				<figcaption>
					Each dot is one seed at one chain length: filled when the decoded tree is exact (exact
					match ≥ 0.99), a ring filled in proportion to its exact match when it is not. Recurrence:
					the plain tracker under the same compiler setting as the others. Transformer: depth 8 at
					twice the recurrence's compute per event and twice its steps, evaluated to 1,024. Three
					seeds each (LEAN_H).
				</figcaption>
			</figure>
		</div>
		<p>
			Both objectives reach exactness the same way, through a pair distance that does not grow along
			the chain; the term's floor is ten times lower (0.0002 against 0.002). What the paper can
			claim is complementarity and one shared mechanism, not that the term does what NextLat cannot.
			Six seeds tell the same story (three more seeds, LEAN_S): the term, NextLat and both are exact
			at 256 on 6 of 6 each, the plain recurrence on 0 of 6; at 1,024 both and NextLat are exact on
			6 of 6 and the term alone on 5 of 6. The lede's "every seed at 1,024" was the first test's
			three seeds: rerun on other machines, the term's seed 1 is 0.754 at 1,024, and same-seed
			reruns on two H100s are not bit-identical.
		</p>
		<ul class="list">
			<li>
				<strong>A fairer transformer.</strong> Over depth 4 to 8, width 128 and 256, and 12,000 or 24,000
				steps, no transformer is exact at the training length. The best (depth 8, 2.03 times the compute
				per event, twice the steps) reaches 0.980–0.984 at 8 steps and 0.012–0.035 at 256, and its length
				failure does not shrink as its in-distribution accuracy rises from 0.70 to 0.98.
			</li>
			<li>
				<strong>Tier 2.</strong> Distributivity and factoring change the size of the tree (818,563 certificates,
				none failed). At 12,000 steps the base is not exact even at the training length (0.97–0.98), and
				the term lifts it to exact in distribution and from 0.47 to 0.90 at 256, exact on no seed. At
				24,000 steps the combination is exact at 64 and 256 on 2 of 2 seeds with a flat pair distance
				of 0.0002 (METRIC): the shortfall was under-training.
			</li>
			<li>
				<strong>The floor lever.</strong> The term never reaches zero: the distance between
				equivalent states settles at a <em>floor</em> (0.0002 on tier 1), which PROOFS A3 shows is
				optimisation noise, proportional to the final learning rate over <MathTex
					tex={String.raw`\mu`}
				/>. Lowering the final learning rate tenfold lowers the floor 2.5 times on every seed.
				Raising <MathTex tex={String.raw`\mu`} /> to 3 lowers its level 2.7 to 5.7 times but adds growth,
				and loses 4,096 on one seed: the lever is the learning rate. Across 18 runs the sign of the distance's
				growth from 8 to 256 predicts exactness at 4,096 in 17; over the width and data runs, every run
				whose distance did not grow was exact at 1,024 (10 of 10), and a growing one rarely was (5 of
				53).
			</li>
			<li>
				<strong>Width and data.</strong> With the learning rate scaled as 128/<MathTex tex="d" />,
				the term is exact at 256 on 5 of 5 runs at widths 256 and 512, and both objectives on 1 of 3
				at width 64. At fixed compute, more chains (5,000 to 80,000) never make the plain recurrence
				exact (0 of 8), NextLat stays exact (8 of 8), and the term drops to 1 of 3 at 80,000: each
				pair was seen 9.6 times instead of 38, the distance grew 25–28 times along the chain, and
				four times the partners per step, or <MathTex tex={String.raw`\mu = 3`} />, restore 2 of 2.
				The term's strength must scale with the data per step.
			</li>
			<li>
				<strong>A second certified domain.</strong> Code execution on a register machine of eight
				named Boolean variables, with statements <code>x = y | c</code> and <code>x = y op z</code>;
				equivalent partners come from reordering and dead code, each pair certified by running both
				programs. Trained on 4 to 16 statements, at 256 the plain recurrence is 0.055 / 0.246 /
				0.068, the term 0.981 / 1.000 / 1.000 (exact on 2 of 3; the miss is 10 of 512 programs), the
				control 0.021 / 0.193 / 0.158, and a five-layer transformer 0.26 (EXEC_D). No arm is exact
				at 1,024: the state's norm grows with length and acts as a clock that returns past about 256
				statements. The reach is domain-dependent: at least 128 times the training length on rewrite
				chains, 16 times on code.
			</li>
		</ul>
	</section>

	<section class="chapter" id="nerode-metric">
		<h3><span class="n">{number('nerode-metric')}</span>The three clauses in one loss</h3>
		<p class="src">
			<span class="mark prior"></span>Bisimulation metrics <Cite id={['ferns', 'dbc']} />;
			<span class="mark new inline"></span>the three-clause reading and the metric loss, with proofs
			of its zero set and of no collapse (EXACTNESS §8);
			<span class="mark measured inline"></span>18 runs, registered first (METRIC)
		</p>
		<p>
			The Myhill–Nerode theorem says what the smallest automaton is: the coarsest <em
				>right congruence</em
			> consistent with the output, where a right congruence is a grouping of histories that survives
			appending any input. That is three clauses, and the arms above supply them one at a time.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Clause</th><th>What it asks of the state</th><th>Supplied by</th></tr></thead
				>
				<tbody>
					<tr
						><th>Consistent with the output</th><td>histories with different outputs differ</td><td
							>the cross-entropy</td
						></tr
					>
					<tr
						><th>A right congruence</th><td
							>the state after <MathTex tex="ux" /> is fixed by the state after <MathTex tex="u" /> and
							the input <MathTex tex="x" /></td
						><td>next-latent prediction</td></tr
					>
					<tr
						><th>The coarsest one</th><td>equivalent histories share a state</td><td
							>the invariance term</td
						></tr
					>
				</tbody>
			</table>
		</div>
		<p class="caption">
			The combination of the three terms is the theorem written as a loss; each one alone leaves
			open a direction the others close.
		</p>
		<p>
			One equation holds all three. The <em>bisimulation metric</em> on histories <Cite
				id="ferns"
			/> is the fixed point of
		</p>
		<MathTex tex={bisim} display />
		<p>
			with <MathTex tex="o(u)" /> the output after <MathTex tex="u" />, <MathTex
				tex={String.raw`\|\cdot\|_{\mathrm{TV}}`}
			/> the total-variation distance, the same input <MathTex tex="x" /> fed to both histories, and
			<MathTex tex={String.raw`0 < \gamma < 1`} />. Its zero set is exactly the Nerode equivalence
			when every input has positive probability (proved here). The <em>Nerode metric loss</em> fits
			the readout's distance to it, with a stop-gradient <MathTex
				tex={String.raw`\operatorname{sg}`}
			/> on the successor term as in deep bisimulation for control <Cite id="dbc" />:
		</p>
		<MathTex tex={metricLoss} display />
		<p>
			where <MathTex tex={String.raw`d_N = (1 - \cos)/2`} /> in the readout's view. Certified equivalent
			pairs enter with target 0; inequivalent pairs need no certificate, since their target comes from
			their outputs. Two properties are proved: no constant state map minimises it once any sampled pair
			has different outputs, so the paraphrase collapse of section {number('nerode-term')} cannot happen;
			and at its zero it contains all three clauses.
		</p>
		<p>
			Measured: alone, it is exact at 256 and 1,024 on 3 of 3 seeds and at 4,096 on 2 of 3 (0.969 /
			0.996 / 0.996), with a pair-distance floor 40 to 80 times the term's but flat, and the readout
			laid out as the metric (unrelated end states 0.74 apart against a mean output distance of
			0.75, Spearman 0.90–0.92). On tier 2 at 12,000 steps no arm is exact and the order at 256 is
			the combination 0.922, the term 0.893, NextLat 0.842, the metric 0.807; at 24,000 steps the
			metric gains 0.10 but its floor still grows. The explicit combination is the strongest form of
			the three clauses, and the single equation the weakest. On the language-shaped task of section {number(
				'dilution'
			)}, with matched pairs and <MathTex tex={String.raw`\gamma = 0.9`} />, the state moves (the
			running-state probe from 0.27 to 0.45–0.48, paired decision accuracy from 0.000 to 0.07), but
			what it carries is the first owner: the model names the first owner on 69–86% of decisions on
			two seeds. Distinction now exists without labels, and it picks the cheapest feature that
			separates the pairs. Open.
		</p>
	</section>

	<section class="chapter" id="state-geometry">
		<h3>
			<span class="n">{number('state-geometry')}</span>What the exact state is, and what it saves
		</h3>
		<p class="src">
			<span class="mark measured"></span>24 retrained checkpoints, four arms × six seeds
			(MECHANISM); a search over certified rewrites, three seeds, every solution checked by Lean
			(PROVER_PROXY)
		</p>
		<p>
			Under the term, alone or with NextLat, the exact state is the minimal automaton laid out in a
			small linear code. The held-out states fall into exactly 960 clusters for the 960 trees, each
			pure (purity 1.000 on 12 of 12 checkpoints). The code spans about 20 dimensions (19–22), and
			is 95–97% an affine image of the tree's one-hot <em>Polish string</em>, the tree written out
			token by token with each operator before its arguments. A rewrite acts on it as the linear map
			of the permutation it induces on that string: residual 1–4%, composing to 2–5%. It is not one
			map per lemma and position (residual 11–22%), and not a rotation (singular values 0.2–1.6).
			The plain recurrence uses 76–98 dimensions, is nonlinear from the first steps, and never forms
			pure clusters (none at 99% purity below 30,000 clusters).
		</p>
		<p>
			The objectives buy length within the training distribution of events and nothing outside it.
			No arm reads an unseen atom name or a fifth atom (0.000 at step 0), and a held-out (lemma,
			position) event is applied correctly on its first occurrence 18–51% of the time. Indexing
			atoms by role makes fresh names identical inputs, at a price in exactness at 256 (the term
			0.89, the combination 0.97).
		</p>
		<p>
			What exactness saves is kernel calls. Each problem asks for a rewrite path from a start tree
			to a target, a thousand problems at each distance. A searcher that asks Lean for the state
			after every step pays 64 kernel calls per solved problem with uniform proposals and 442 with
			an edit-distance look-ahead, at success 0.999 and 0.942. A searcher that moves on the
			tracker's predicted states and asks Lean only to confirm a claimed solution, with the
			combination as its imagination, takes the kernel's search step for step (1.2 million held
			states and 2.8 million candidate successors per seed, all equal to the kernel's) at <strong
				>one call per solved problem</strong
			>, with the same success, on 3 of 3 seeds. With every walk started from a given expression the
			drifting recurrence loses nothing, since its first error comes after 70 to 80 rewrites and
			solutions take 33. After a certified prefix of 4,096 rewrites, though, its reading of the goal
			is silently wrong on 27–47% of problems and its search loses 10 to 19 points; the combination
			reads every prefix exactly (exploratory, registered before it ran). Lean certifies all 11,310
			distinct solutions.
		</p>
	</section>

	<section class="chapter" id="natural-proofs">
		<h3>
			<span class="n">{number('natural-proofs')}</span>Natural proofs: the kind of step, not the
			terms
		</h3>
		<p class="src">
			<span class="mark measured"></span>mathlib proofs from LeanDojo Benchmark 4, every step
			replayed in Lean; three readouts, two to three seeds each, registered first (LEAN_N_DATA,
			LEAN_N)
		</p>
		<p>
			The natural test takes real proofs: 4,579 from five mathlib directories (natural numbers,
			integers, reals, lists, special functions), split by length, with proofs of at most 4 steps
			for training and of 8 to 15 for test. The headline test set is 82 proofs that are both
			Lean-confirmed at every step and name a premise no training proof names. Three readouts of the
			same tracker failed at the same place.
		</p>
		<ul class="list">
			<li>
				<strong>The whole state</strong>, decoded through a position-wise MLP head: every arm
				memorises its training proofs (1.000) and is exact on 0 of 736 unseen test steps whose state
				is not
				<code>no goals</code>.
			</li>
			<li>
				<strong>The change</strong>, through a linear head: which goals closed, one changed goal,
				and a flag for anything else. The kind of step is right 0.90–0.94 of the time in
				distribution, and closures stay exact at 0.93–1.00 on the longer test proofs; the rewritten
				target and the types of added hypotheses are exact on 0–2% and 6% of unseen steps. Run free,
				every arm is at 0.000.
			</li>
			<li>
				<strong>A copy head</strong> that points into the premise statements: on chains it gives up stage
				one's reach (0.914 and 0.941 at 256), so the natural runs were not launched.
			</li>
		</ul>
		<p>
			Stated plainly: the readouts learn what kind of step a tactic is and never produce the new
			terms a step introduces. The obstacle on natural proofs was generating content, not tracking
			state. Reading verdicts instead of strings met the same boundary from the other side (section {number(
				'kernel-oracle'
			)}): rerun with an audited protocol, a critic given the true state judges whether a tactic
			applies no better than a one-word table on the tactic's head word. Along the way the three
			readouts confirmed a rule about where the term may be measured:
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Readout, on chains</th><th>Linear in the state</th><th class="num"
							>Unrelated distance</th
						><th>Exact at 256</th></tr
					></thead
				>
				<tbody>
					{#each heads as h (h.label)}
						<tr class:quiet={h.lin === 'no'}>
							<th>{h.label}</th><td>{h.lin}</td><td class="num">{h.unrelated}</td><td>{h.exact}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Unrelated distance: the centred-cosine distance between the states of unrelated histories at
			the end of training under the term; the plain recurrence keeps them 0.81–0.84 apart. Exact at
			256: seeds exact on certified chains at 256 steps; the verdict head at 24,000 steps (LEAN_S1,
			LEAN_N).
		</p>
		<p>
			A head that can amplify an arbitrarily small difference in the state lets the term be paid by
			pulling every state together, which is the collapse; a head linear in the state cannot,
			because its margins shrink with the spread and the collapse costs cross-entropy. Measure
			invariance through a head linear in the state, or add the distinction half.
		</p>
	</section>

	<section class="chapter" id="kernel-oracle">
		<h3><span class="n">{number('kernel-oracle')}</span>Reading out verdicts, not strings</h3>
		<p class="src">
			<span class="mark new"></span>The diagnosis and the corrected course (COURSE, 23 October);
			<span class="mark measured inline"></span>probe data replayed in Lean, the chain gate on two
			seeds, the natural pilot and its audited rerun (LEAN_N §§12–13, D1_AUDIT)
		</p>
		<p>
			The failure had a reason in our own theory. Section {number('nerode-term')} says the state is the
			class of histories with the same future, and the kernel decides futures; yet on natural proofs we
			scored the reproduction of Lean's printed state, which is generation of new text. The parts of the
			readout that were <em>decisions</em> (the kind of step, which goals closed) worked at once and
			held on longer proofs. And the two halves of section {number('nerode-term')} ask for a primary loss
			dense in the state: a rewrite chain shows the whole state after every step, a natural proof shows
			one result per step. A prover does not need the strings either. It gets the state text from the
			kernel for one call; what it cannot get cheaply is what the kernel will say about tactics it has
			not yet run.
		</p>
		<p>
			So the second stage becomes a <em>kernel oracle</em>. The tracker sees the initial proof state
			once, then one tactic per step, and never an intermediate state. At each step it predicts what
			the kernel would say to a <em>probe</em> tactic tried there: accepted or rejected, goals left,
			proof complete, and the class of error. Several probes per state make the loss dense: the gold
			tactic, the tactic of another step (accepted 21.9% of the time, the hard class), a swapped
			premise (10.3%), permuted arguments (44.8%), and a tactic from another proof (5.7%), each
			verdict from Lean. Nothing is decoded. The arms are the plain recurrence, the combination, a
			transformer at equal compute, a <em>state-blind</em> arm that sees only the probe, and an upper
			bound handed the true state.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={ORACLE} label="Computation graph of the kernel oracle" />
		</div>
		<p class="caption">
			The slot <MathTex tex="w" /> reads the initial state <MathTex tex="s_0" /> once, then one gold tactic
			<MathTex tex={String.raw`\tau_t`} /> per step. A probe <MathTex tex={String.raw`\pi`} /> is scored
			by a head linear in the readout's view <MathTex tex="z_t" /> for each probe, and the target is the
			kernel's verdict <MathTex tex="v" />. Next-latent prediction and the invariance term act on
			the slot as before. Dashed: the slot carried to the next step.
		</p>
		<p>
			The chain gate comes first: the oracle must be exact on certified chains before a natural
			number is read. With a linear head on the slot after the probe it was not (0.576 and 0.580 at
			256): two verdict bits per state do not pin down the ten bits of a tree, the sparse primary
			loss the two halves warn about. With the head conditioned on the probe, seed 0 is exact to 256
			steps (one wrong verdict in 131,072) and seed 1 reaches 0.991 with errors flat in depth,
			under-fit rather than drifting. The gate counts only as two seeds under one configuration, so
			both were rerun at 24,000 steps: every verdict on every chain is right at 8, 16, 64 and 256
			steps on both seeds (1.00000), with unrelated states 0.18–0.20 apart, so no collapse. The
			chain gate has passed. The natural pilot, five arms on two seeds, is next; its predictions
			were committed before any natural number was seen:
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Registered before the pilot</th><th>Status</th></tr></thead>
				<tbody>
					{#each oracle as r (r.clause)}
						<tr>
							<th>{r.registered}</th><td>{r.status}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Accuracy on the hard class is balanced accuracy over every misplaced-gold probe at a depth,
			with a bootstrap interval over proofs; depth <MathTex tex="k" /> means the slot has carried
			<MathTex tex="k - 1" /> steps without the kernel. Two seeds per arm.
		</p>
		<p>
			We found no published model that predicts Lean's verdicts several steps ahead without the
			kernel; the nearest work predicts the steps remaining, embeds a tactic by the edit it makes,
			or keeps the kernel in the loop at every step (searched 23 October). If P1 and P2 hold, the
			next number is kernel calls spared at equal theorems proved when the oracle filters a prover's
			search, with the recall of accepted tactics beside it.
		</p>
		<p>
			They did not hold. On natural proofs all three predictions failed: balanced accuracy on the
			hard class sat at 0.57–0.78 for every arm in every depth band, with overlapping intervals, and
			the critic given the kernel's true state read 0.64–0.69, inside the others. An independent
			audit reproduced every number and found the comparison unable to decide: that critic met the
			probe only at the end, saw renamed hypotheses on 44–48% of probes, and was judged at its last
			step after memorising its training probes, while a logistic regression on the tactic's head
			word out-ranked every arm. Rerun with consistent names, the probe attending to the state and
			checkpoints chosen on validation, the critic given the true state reads 0.69–0.75 against the
			one-word table's 0.705 and 0.755. Whether a mathlib tactic applies to a goal is not learnable
			from 2,565 theorems by a small encoder trained from scratch, beyond that prior. The
			exact-state line on natural proofs waits on a pretrained encoder of goals and tactics.
		</p>
	</section>

	<section class="chapter" id="latent-exec">
		<h3><span class="n">{number('latent-exec')}</span>Latent execution without chain of thought</h3>
		<p class="src">
			<span class="mark prior"></span>Qwen2.5-Coder <Cite id="qwencoder" />, scratchpads for
			intermediate computation <Cite id="scratchpad" />;
			<span class="mark new inline"></span>the slot on a frozen code model with the objective;
			<span class="mark measured inline"></span>12 runs, three seeds per arm, registered before the
			batch; the fixed-norm replication and the arithmetic rung, each registered before its run
			(EXEC_LM §§4, 7, 10)
		</p>
		<p>
			The last test puts a pretrained language model in the loop, where a pretrained encoder was
			missing above. The programs are the register machine of section {number('hardening')} written as
			Python: four of eight bit variables <code>v0</code>–<code>v7</code>, all 0 at the start, and
			statements such as <code>v3 = (v1 + v2) % 2</code>. The state is the eight bits, and
			<em>exact</em> means all eight right after the last statement. Training programs have 4 to 16
			statements; test programs have 16 to 1,024. Four arms use Qwen2.5-Coder-0.5B, a
			0.5-billion-parameter code model <Cite id="qwencoder" />, and every number is read against a
			shallow floor:
		</p>
		<ul class="list">
			<li>
				<strong>Slot + objective.</strong> The language model is frozen and reads each statement line
				on its own. The recurrent slot of the earlier sections, width 128, attends to that statement's
				hidden states from the model's middle layer, and a linear head reads the eight bits from LN(slot).
				It is trained with next-latent prediction and the invariance term, on pairs of programs certified
				equivalent by running both. It generates no tokens. In the headline runs the slot is also rescaled
				to a fixed norm after every statement.
			</li>
			<li><strong>Slot alone.</strong> The same, without the two terms.</li>
			<li>
				<strong>Chain of thought.</strong> The model fully fine-tuned to write the state after every
				statement, a scratchpad <Cite id="scratchpad" />, and judged running free on what it wrote
				itself: 8 generated tokens per statement.
			</li>
			<li>
				<strong>Final state only.</strong> The model fine-tuned to write the state once, after the whole
				program.
			</li>
			<li>
				<strong>Shallow floor.</strong> A table from each variable's last assignment to its most frequent
				final value. It reads one statement per variable and follows no dependency.
			</li>
		</ul>
		<div class="figure wide">
			<figure class="pf">
				<ExecFigure />
				<figcaption>
					Exact final state: the share of test programs whose state is exact after the last
					statement, by program length, trained on 4 to 16 statements; light marks are the three
					seeds, the line their mean, and the dashed line the shallow floor. The slot with the
					objective is drawn at a fixed norm (solid) and, lighter and dashed, as in the registered
					batch with its norm free. Tokens: what each arm generates per statement; the final-state
					arm writes 8 per program. The language-model arms are judged on the first 512, 512, 256
					and 64 programs of the same test sets.
				</figcaption>
			</figure>
		</div>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Registered before the batch</th><th>Measured</th><th>Verdict</th></tr></thead
				>
				<tbody>
					{#each execClauses as r (r.clause)}
						<tr>
							<th>{r.registered}</th><td>{r.measured}</td><td class="verdict">{r.verdict}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			The registered clauses of the execution test and what the runs returned; seeds 0, 1 and 2. The
			last row was registered later, before its own run.
		</p>
		<p>
			<strong>The headline.</strong> With the slot rescaled to a fixed norm after every statement,
			the slot with the objective is exact at 1,024 statements, 64 times its training length, on 3
			of 3 seeds, and the distance to a certified short partner stays at 1–3 × 10⁻⁴ from 16 to
			1,024. The prediction was registered before the run and holds in two replications, on a laptop
			and on Modal. In the registered batch the norm was free: it grew 1.2–1.35 times by 1,024, the
			clock of section {number('hardening')}, and fixing it removes the tail.
		</p>
		<p>
			In the registered batch all four predictions pass and the kill does not fire. The slot with
			the objective is exact at 256 statements, sixteen times its training length, on every seed,
			and never wrong at any statement along the way on 100%, 100% and 99.8% of programs; at 1,024
			it ends exact on 0.73–0.97 of programs and the median program is never wrong. The same slot
			without the objective drifts below the floor by 256 (0.05–0.14). Writing the state keeps it
			only at the training length: chain of thought is exact at 16 and at 0.06–0.37 by 256, with its
			first error at statements 53 to 90, and it pays 8 tokens per statement for that, 8,192 at
			1,024 statements. Asked for the final state alone, the model learns less than the
			one-statement table at every length. As on the rewrite chains, the growth of the distance to a
			certified short partner predicts the drift (Spearman +0.88), and unrelated states stay
			0.09–0.22 apart, so nothing collapsed.
		</p>
		<p>
			Two caveats bound the claim. The state lives in the slot, not in the language model, which is
			frozen and reads one statement at a time; the domain is four bit variables with assignments
			and one-bit arithmetic, trained on 4 to 16 statements. The fine-tuned arms had 2,000 steps of
			full fine-tuning, enough to fit the training length exactly, and smaller test sets at 256 and
			1,024.
		</p>
		<h4>Where the step is arithmetic</h4>
		<p>
			A second rung makes each step a real operation: eight variables over 0 to 15, with addition,
			subtraction and multiplication modulo 16 and conditionals. Here the flat slot cannot fit even
			the training length (0.375 exact at 16, one pilot seed): routing a value by its name is what
			fails. A register-shaped state fits it on 3 of 3 seeds (1.000, 1.000, 0.998): eight registers,
			each normalised after every write, read and written by attention from the operand names to
			learned name keys, with one shared operation network and the same objective. Past the training
			length it settles on a plateau of 0.72–0.77 exact from 256 to 1,024, where a register that
			went wrong is later overwritten correctly.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<ArithFigure />
				<figcaption>
					The share of test programs whose whole state is exact after each statement, on the
					arithmetic rung, trained on at most 16 statements; each statement is read from the
					shortest test set that reaches it. Light lines are seeds, heavy lines their mean. The
					Markov step and the register slot have three seeds each; the whole-history chain of
					thought is one pilot seed, tested to 256.
				</figcaption>
			</figure>
		</div>
		<p>
			The same language model does better as a <em>Markov step</em>. Fine-tuned on single steps, a
			state line and a statement in and the next state line out, with states drawn uniformly over
			all values, and run with only its own last state line and the statement in context (74
			tokens), it is exact at 1,024 statements on 3 of 3 seeds. Its error is 0.5–2 × 10⁻⁵ per step,
			every error falls on a conditional, and every one is repaired before the last statement. With
			its whole history in context the same model is exact at 16 and at 0 by 256 (one pilot seed),
			and trained only on the states that zero-start programs reach, the bounded-context step
			plateaus at 0.27. Two changes made the language model exact at 64 times the training length:
			cut the context to the carried state, and train the step on the states it will meet. It still
			writes 8 tokens per statement, but its context never grows.
		</p>
		<p>A paper draft built on these exact-state results now exists.</p>
	</section>
</section>

<style>
	.verdict {
		white-space: nowrap;
	}
</style>
