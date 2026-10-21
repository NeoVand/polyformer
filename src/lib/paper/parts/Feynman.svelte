<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import DiagramSum from '#lib/learn/DiagramSum.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { FEYNMAN } from '#lib/viz/computeGraphs.ts';
	import { number } from '../toc.ts';
</script>

<section class="part" id="part-feynman">
	<header class="part-head">
		<span class="roman">Part III</span>
		<h2>Letting the data choose the arity</h2>
		<p class="part-lede">
			A head of order <MathTex tex="k" /> pays for <MathTex tex="k" />-way terms whether the data
			needs them or not. Physics faced a similar problem in the 1940s: how to add up interactions
			among any number of particles. Its answer was a picture language, Feynman diagrams, and
			equations that add up all the pictures at once. This part borrows that idea to build a layer
			that decides, token by token, how many others to combine.
		</p>
	</header>

	<section class="chapter" id="feynman">
		<h3><span class="n">{number('feynman')}</span>Where Feynman diagrams come from</h3>
		<p class="src"><span class="mark prior"></span>Prior work <Cite id={['feynman', 'dyson']} /></p>
		<p>
			In quantum electrodynamics, the theory of electrons and light, the quantity you want is an
			<em>amplitude</em>: a number whose square gives the probability of a process, say two
			electrons flying at each other and leaving with given momenta. The theory cannot be solved
			exactly. What it offers instead is a small number, the electron's charge <MathTex tex="e" />,
			with
			<MathTex tex="\alpha = e^2/4\pi \approx 1/137" />. So the amplitude is computed as a power
			series in
			<MathTex tex="e" />.
		</p>
		<p>
			In 1949 Feynman showed that every term of that series can be drawn. A straight line is a
			particle moving freely (a <em>propagator</em>), a wavy line is a photon, and a dot where three
			lines meet is an <em>interaction</em>, where an electron emits or absorbs a photon. Each dot
			contributes one factor of <MathTex tex="e" />, so diagrams with more dots count for less. For
			two electrons scattering:
		</p>
		<div class="figure">
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
		</div>
		<p>
			The hatched blob is everything that can happen; the right side lists the ways it can happen,
			each one term with exact rules for turning it into a number. Two ideas carry over to
			attention. A complicated interaction among many particles is built from one small vertex, used
			over and over; read "particles" as "tokens". And nobody decides in advance how many particles
			take part: the theory adds up all the diagrams, and the couplings decide how much each one
			counts. In attention that would mean nobody fixes the arity in advance.
		</p>
		<div class="figure wide"><LearnFigure section="feynman" /></div>
	</section>

	<section class="chapter" id="dyson">
		<h3><span class="n">{number('dyson')}</span>Summing all the diagrams at once</h3>
		<p class="src">
			<span class="mark prior"></span>Prior work <Cite id={['dyson', 'schwinger']} />
		</p>
		<p>
			Listing diagrams one at a time never ends. Dyson and Schwinger found equations that add up
			whole families of them at once. Draw as a double line everything that can happen to an
			electron on its way from one point to another, every emission and reabsorption included: the <em
				>dressed</em
			>
			propagator. The plain single line, nothing happening, is the bare one. Let the blob
			<MathTex tex="\Sigma" /> stand for every way the electron can interact with itself in one stretch
			that cannot be cut in two by snipping a single line. Then
		</p>
		<div class="figure">
			<DiagramSum
				lhs="dressed"
				width={92}
				more={false}
				terms={[{ kind: 'bare' }, { kind: 'bare-sigma-dressed' }]}
			/>
		</div>
		<MathTex display tex="G = G_0 + G_0\, \Sigma\, G" />
		<p>
			The dressed line appears on both sides, so the equation refers to itself. Substituting it into
			itself unrolls it into an infinite series, and solving it sums every term in one go:
		</p>
		<div class="figure">
			<DiagramSum
				lhs="dressed"
				width={92}
				terms={[
					{ kind: 'bare' },
					{ kind: 'bare-sigma-bare' },
					{ kind: 'bare-sigma-bare-sigma-bare' }
				]}
			/>
		</div>
		<MathTex
			display
			tex={String.raw`\begin{aligned} G &= G_0 + G_0 \Sigma G_0 + G_0 \Sigma G_0 \Sigma G_0 + \cdots \\ &= G_0\,\bigl(1 - \Sigma\, G_0\bigr)^{-1} \end{aligned}`}
		/>
		<p>
			Stopping after <MathTex tex="R" /> substitutions keeps exactly the diagrams up to depth
			<MathTex tex="R" />. That is the shape our layer borrows. Read "a particle's dressed line" as
			"a token's state", "one more application of the interaction" as "one more round of attention",
			and "the couplings" as "softmax weights". One difference matters: in physics the coupling is a
			constant of nature, while here the weights are computed fresh from the input, for every token
			and every round.
		</p>
	</section>

	<section class="chapter" id="diagrams">
		<h3><span class="n">{number('diagrams')}</span>Feynman attention</h3>
		<p class="src"><span class="mark new"></span>New in this project</p>
		<p>
			Feynman attention gives every token a <em>state</em>
			<MathTex tex="\Phi_t" /> and rebuilds it for <MathTex tex="R" /> rounds from the previous round's
			states. Round 0 is the token's own value,
			<MathTex tex="\Phi^0_t = v_t" />. In each later round the token chooses, with one softmax,
			among five kinds of term, called <em>sectors</em>:
		</p>
		<MathTex
			display
			tex={'\\begin{aligned}\\Phi^{r}_t = \\;& \\pi_{\\text{leaf}}\\, v_t + \\sum_j \\pi_j\\, \\Phi^{r-1}_j \\\\ &+ \\sum_{jk} \\pi_{jk}\\, \\Phi^{r-1}_j \\odot \\Phi^{r-1}_k \\\\ &+ \\sum_{jm} \\pi_{jm}\\, \\Phi^{r-1}_j \\odot \\Psi^{r}_m + \\pi_{\\text{carry}}\\, \\Phi^{r-1}_t\\end{aligned}'}
		/>
		<p>
			Term by term: keep your own value (a <em>leaf</em>); copy another token's state (a
			<em>hop</em>, the analogue of a propagator); multiply two tokens' states (a
			<em>cubic vertex</em>); multiply one token's state by a <em>virtual mode</em>
			<MathTex tex="\Psi_m" />, a learned summary of pairs (an
			<em>exchange</em>); or keep what you had (a <em>carry</em>). The weights <MathTex tex="\pi" /> are
			one softmax over all the options of all five sectors together, so every token in every round picks
			its own mix. After <MathTex tex="R" /> rounds a token's state can draw on anything from one token
			up to <MathTex tex="3^R" /> of them. Each round costs about as much as one cubic layer.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={FEYNMAN} label="Computation graph of Feynman attention" />
		</div>
		<p>
			<strong>Two worked examples.</strong> On SET one cubic vertex is enough: a card's round-1
			state reads the product of the two cards that complete a SET with it. On pointer chasing the
			query needs a chain of hops: if the query points at node <MathTex tex="a" />, which points to <MathTex
				tex="b"
			/>, which points to the last node <MathTex tex="c" />, then
		</p>
		<MathTex
			display
			tex="\Phi^4_q \approx \Phi^3_a \approx \Phi^2_b \approx \Phi^1_c \approx v_c"
		/>
		<p>
			one hop per round, with carries once the end is reached. The first is a single vertex, the
			second a long propagator; the same layer can be either, and its weights decide. The figure
			draws both trees in the style of TikZ-Feynman <Cite id="ellis" />;
			<a href={resolve('/explore/diagrams')}>Explore, Feynman</a> draws them for a model training live.
		</p>
		<div class="figure wide"><LearnFigure section="diagrams" /></div>
	</section>

	<section class="chapter" id="sectors">
		<h3><span class="n">{number('sectors')}</span>Making it train</h3>
		<p class="src"><span class="mark new"></span>New in this project</p>
		<p>
			The first versions did not learn: on SET and pointer chasing they stayed near chance. Three
			changes fixed that, each for a reason that can be stated.
		</p>
		<p>
			<strong>Balance the sectors.</strong> The sectors offer very different numbers of options: one
			leaf and one carry, about <MathTex tex="n" /> hops, about <MathTex tex="n^2" /> cubic pairs. When
			all scores start out about equal, a softmax gives each sector weight in proportion to its number
			of options, so nearly all the weight goes to cubic and exchange terms and the simple, useful hops
			are drowned out. A fixed offset per sector, minus the logarithm of its number of options, gives
			every sector the same total weight at the start. In physics this offset is a
			<em>chemical potential</em>, which sets how many particles of each kind a system holds.
		</p>
		<div class="figure wide"><LearnFigure section="sectors" /></div>
		<p>
			<strong>Rescale the output.</strong> Products of numbers below 1 shrink with every round, so the
			final state is divided by its root mean square, which restores its scale.
		</p>
		<p>
			<strong>Let answers stay put.</strong> Without a way to keep its state, a token rebuilds everything
			every round, and an answer found in round 1 is overwritten in round 2. The carry term lets a finished
			answer survive.
		</p>
	</section>

	<section class="chapter" id="chase">
		<h3><span class="n">{number('chase')}</span>What Feynman attention learns</h3>
		<p class="src"><span class="mark measured"></span>Measured with this app's engine</p>
		<p>
			Pointer chasing asks for a number of lookups that changes from puzzle to puzzle <Cite
				id="chakrabarti07"
			/>. Four rounds are enough: one to read the start node, then one per hop.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Model</th><th class="num">Held-out accuracy</th><th class="num">Parameters</th><th
							class="num">ms / step</th
						></tr
					></thead
				>
				<tbody>
					<tr class="hi"
						><th>Feynman, 4 rounds, 1 layer</th><td class="num">100%</td><td class="num">61k</td><td
							class="num">103</td
						></tr
					>
					<tr
						><th>Standard, 3 layers</th><td class="num">94.2%</td><td class="num">154k</td><td
							class="num">43</td
						></tr
					>
					<tr
						><th>Standard, 2 layers</th><td class="num">88.9%</td><td class="num">104k</td><td
							class="num">28</td
						></tr
					>
					<tr
						><th>Cubic, 1 layer</th><td class="num">84.5%</td><td class="num">63k</td><td
							class="num">20</td
						></tr
					>
					<tr
						><th>Standard, 1 layer</th><td class="num">64.5%</td><td class="num">54k</td><td
							class="num">15</td
						></tr
					>
				</tbody>
			</table>
		</div>
		<p class="caption">Pointer chasing, seed 0, in the browser. Chance is 12.5%.</p>
		<p>
			Feynman attention passes 95% by step 250. Opening up a trained model shows it following the
			true pointer path one hop per round, the same algorithm as the worked example. Hover a row in
			the figure to see what each token reads in each round.
		</p>
		<div class="figure wide"><LearnFigure section="chase" /></div>
		<p>
			It is not a universal winner. On Match-4 it stays at chance. On three-hop composition it
			succeeds on two seeds of three in the cloud runs, well above three ordinary layers (52%) but
			not reliably: one set of weights, reused every round, has to perform three different lookups.
			The next part starts from that Match-4 failure.
		</p>
	</section>
</section>
