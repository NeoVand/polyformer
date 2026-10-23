<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import Theorem from '#lib/report/Theorem.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { NERODE } from '#lib/viz/computeGraphs.ts';
	import ExactFigure from '../ExactFigure.svelte';
	import { number, roman } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	const objective = String.raw`\begin{aligned} \mathcal L \;=\;& \operatorname{CE}\big(x_{t+1} \,\big|\, h(x_{\le t})\big) \\ &+\; \mu \operatorname*{E}_{u \sim v} d(z_u,\, z_v) \\ &+\; \lambda \operatorname*{E}_{u \not\sim v'} \max\big(0,\, m - d(z_u,\, z_{v'})\big) \end{aligned}`;
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
			1,024 exactly, on every seed.
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
</section>

<style>
	.verdict {
		white-space: nowrap;
	}
</style>
