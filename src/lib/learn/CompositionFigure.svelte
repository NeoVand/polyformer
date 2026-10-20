<script lang="ts">
	import MathTex from '#lib/ui/Math.svelte';
	import A5Rotation from '#lib/viz/A5Rotation.svelte';
	import CharactersResult from '#lib/report/CharactersResult.svelte';
	import GroupLadder from '#lib/report/GroupLadder.svelte';

	let { section }: { section: string } = $props();
	let ticks = $state(1);
	let element = $state(1);
	const point = (value: number, radius = 48) => ({
		x: Math.sin((value * 2 * Math.PI) / 3) * radius,
		y: -Math.cos((value * 2 * Math.PI) / 3) * radius
	});
	const triangle = [
		[0, -43],
		[37.24, 21.5],
		[-37.24, 21.5]
	];
	// R sends top -> right -> left. F fixes top and exchanges left and right.
	const arrangements = [
		{ id: 'turn-flip', label: 'Turn, then flip', first: [1, 2, 0], last: [2, 1, 0] },
		{ id: 'flip-turn', label: 'Flip, then turn', first: [0, 2, 1], last: [1, 0, 2] }
	];
	const reductions = [
		{ name: 'Local-linear', gain: 0.4, detail: 'Exact local fit' },
		{ name: 'Parallax', gain: 0.75, detail: 'Pairwise correction · prior work' }
	];
	const programs = [
		{
			name: 'First swap 0 ↔ 1',
			states: [
				[0, 1, 2],
				[1, 0, 2],
				[1, 2, 0]
			],
			answer: 1
		},
		{
			name: 'First swap 1 ↔ 2',
			states: [
				[0, 1, 2],
				[0, 2, 1],
				[2, 0, 1]
			],
			answer: 2
		}
	];
</script>

{#if section === 'groups'}
	<figure class="composition-figure">
		<header>
			<span>One clock · three positions</span><button onclick={() => (ticks = (ticks + 1) % 3)}
				>Change first move</button
			>
		</header>
		<svg
			class="clocks"
			viewBox="0 0 480 190"
			role="img"
			aria-label={`${ticks} plus two ticks is ${(ticks + 2) % 3} modulo three`}
		>
			{#each [{ id: 'first', value: ticks }, { id: 'second', value: 2 }, { id: 'sum', value: (ticks + 2) % 3 }] as clock, i (clock.id)}
				<g transform={`translate(${80 + i * 160} 86)`}>
					<circle r="45" class="clock-face" />
					{#each [0, 1, 2] as tick (tick)}
						{@const p = point(tick, 61)}
						<text x={p.x} y={p.y + 4} text-anchor="middle">{tick}</text>
					{/each}
					<line
						x1="0"
						y1="0"
						x2="0"
						y2="-38"
						class="hand"
						style:transform={`rotate(${clock.value * 120}deg)`}
					/>
					<circle r="3" class="ink" />
					<text x="0" y="91" text-anchor="middle" class="formula"
						>{clock.value}{i === 2 ? ' mod 3' : clock.value === 1 ? ' tick' : ' ticks'}</text
					>
				</g>
			{/each}
			<text x="160" y="91" text-anchor="middle" class="operator">+</text>
			<text x="320" y="91" text-anchor="middle" class="operator">=</text>
		</svg>
		<div class="card-sums">
			<span>A card has four clocks</span>
			<MathTex tex={String.raw`(0,1,2,0) + (1,1,0,2) + (2,1,1,1) = (0,0,0,0)`} />
		</div>
		<figcaption>
			Wrap each sum at 3. These three cards return all four hands to zero, so they form a SET.
			Swapping the cards leaves the answer unchanged.
		</figcaption>
	</figure>
{:else if section === 'language'}
	<figure class="composition-figure">
		<header><span>Language · smaller loss is better</span></header>
		<div class="gain-axis"><span>Gain at equal computation</span><span>1% target</span></div>
		<div class="gains">
			{#each reductions as row (row.name)}
				<div class="gain-row">
					<div class="name">{row.name}<small>{row.detail}</small></div>
					<div class="gain-track"><i style:width={`${row.gain * 100}%`}></i></div>
					<span class="value">{row.gain}%</span>
				</div>
			{/each}
		</div>
		<figcaption>
			S6, FineWeb-Edu, 400M tokens, Muon; reported approximate gains. Both are below the registered
			1% threshold. This does not establish an advantage from higher arity.
		</figcaption>
	</figure>
{:else if section === 'features'}
	<figure class="composition-figure">
		<CharactersResult />
		<figcaption>
			GROUPS §5.1. The softmax runs receive all characters and train for 6,000 steps. The Newton row
			is the separately recorded reference, not a matched frozen-feature ablation.
		</figcaption>
	</figure>
{:else if section === 'order' || section === 'limits'}
	<figure class="composition-figure">
		<header>
			<span>Same operations · different order</span><span>Read left to right</span>
		</header>
		<svg
			class="triangles"
			viewBox="0 0 480 330"
			role="img"
			aria-label="A labelled triangle turned then flipped ends differently from the same triangle flipped then turned"
		>
			{#each arrangements as row, r (row.id)}
				<text x="10" y={18 + r * 164} class="quiet">{row.label}</text>
				{#each ['Start', 'First move', 'Both moves'] as label, c (label)}
					{@const positions = c === 0 ? [0, 1, 2] : c === 1 ? row.first : row.last}
					<g transform={`translate(${76 + c * 164} ${89 + r * 164})`}>
						<polygon points="0,-43 37.24,21.5 -37.24,21.5" class="triangle-edge" />
						{#each ['A', 'B', 'C'] as letter, i (letter)}
							<g
								class="corner"
								style:transform={`translate(${triangle[positions[i]][0]}px, ${triangle[positions[i]][1]}px)`}
							>
								<circle r="3" class="ink" />
								<text
									x={triangle[positions[i]][0] * 0.38}
									y={triangle[positions[i]][1] * 0.38 + 4}
									text-anchor="middle">{letter}</text
								>
							</g>
						{/each}
						<text x="0" y="66" text-anchor="middle" class="quiet">{label}</text>
					</g>
				{/each}
			{/each}
		</svg>
		<figcaption>
			The outline stays the same; the corner labels reveal the difference. Losing the order makes
			these two histories indistinguishable.
		</figcaption>
	</figure>
{:else if section === 'representations'}
	<figure class="composition-figure">
		<header>
			<span>The 60 rotations of an icosahedron</span><button
				onclick={() => (element = (element + 1) % 60)}>Next rotation</button
			>
		</header>
		<div class="solid"><A5Rotation {element} model="ideal" /></div>
		<div class="rotation-key">
			<span>Operation {element + 1} / 60</span><span>Open point: start · filled point: image</span>
		</div>
		<figcaption>
			A computed 3-dimensional representation of A₅. The marked corner moves; the solid returns to
			the same outline after each group rotation. The lab compares it with a trained head.
		</figcaption>
	</figure>
{:else if section === 'holonomy'}
	<figure class="composition-figure">
		<header><span>Read token b · keep the sequence order</span></header>
		<div class="product-sequence">
			<span>a</span><span class="marked">b</span><span>c</span><span>d</span>
		</div>
		<div class="sectors">
			<div><span>Size 1</span><MathTex tex="B" /></div>
			<div><span>Size 2</span><MathTex tex="AB + BC + BD" /></div>
			<div><span>Size 3</span><MathTex tex="ABC + ABD + BCD" /></div>
			<div><span>Size 4</span><MathTex tex="ABCD" /></div>
		</div>
		<figcaption>
			A, B, C and D are the tokens' gated matrices. Every term includes B. Each product keeps the
			tokens' left-to-right order; each row sums subsets of one size.
		</figcaption>
	</figure>
{:else if section === 'group-results'}
	<figure class="composition-figure ladder-figure">
		<div class="ladder-body"><GroupLadder group="a5" compact /></div>
		<figcaption>
			GROUPS §5.2, three-seed means at 6,000 steps. The dashed ceiling is exact for order-blind
			inputs; softmax has positions and is not covered by that bound.
		</figcaption>
	</figure>
{:else if section === 'programs'}
	<figure class="composition-figure">
		<header><span>A small program · inspect variable 0</span></header>
		<div class="programs">
			{#each programs as program (program.name)}
				<div class="program">
					<div class="program-name">{program.name}, then the other swap</div>
					<div class="states">
						{#each program.states as state, stage (stage)}
							<div class="state">
								<span>{stage === 0 ? 'Start' : `After ${stage}`}</span>
								<div>
									{#each state as value, i (i)}<b class:selected={i === 0}>{value}</b>{/each}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
		<figcaption>
			A two-instruction illustration: the same swaps leave variable 0 holding 1 in one order, 2 in
			the other. The measured benchmark uses two interleaved three-instruction programs.
		</figcaption>
	</figure>
{:else}
	<figure class="composition-figure">
		<header><span>What happens when features meet?</span></header>
		<ol class="principles">
			<li>
				<span>Compare</span><strong>Pairwise scores</strong>
				<p>Find relevant tokens and retrieve their values.</p>
			</li>
			<li>
				<span>Add phases</span><strong>Commuting products</strong>
				<p>Combine clock moves. Keep content, lose order.</p>
			</li>
			<li>
				<span>Compose rotations</span><strong>Ordered products</strong>
				<p>Let the representation retain the order that changes the answer.</p>
			</li>
		</ol>
		<figcaption>
			A design principle for the measured tasks. Whether it helps on natural data remains an
			experimental question.
		</figcaption>
	</figure>
{/if}

<style>
	.composition-figure {
		width: 100%;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 20px;
		min-width: 0;
		color: var(--color-ink);
	}
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		font-size: 12px;
		color: var(--color-ink-2);
	}
	button {
		flex: none;
		padding: 4px 0 4px 10px;
		color: var(--color-ink);
		font-size: 11px;
		background: none;
		border: 0;
		cursor: pointer;
		text-decoration: underline;
		text-underline-offset: 4px;
		text-decoration-color: var(--color-rule);
	}
	button:hover {
		text-decoration-color: currentColor;
	}
	button:focus-visible {
		outline: 1px solid currentColor;
		outline-offset: 4px;
	}
	svg {
		width: 100%;
		height: auto;
		overflow: visible;
	}
	text {
		fill: currentColor;
		font: 13px var(--font-sans);
	}
	.quiet {
		fill: var(--color-ink-3);
		font-size: 12px;
	}
	.formula {
		font-size: 15px;
	}
	.operator {
		font-size: 20px;
	}
	.clock-face,
	.triangle-edge {
		fill: none;
		stroke: var(--color-ink-3);
		stroke-width: 1;
	}
	.hand {
		stroke: currentColor;
		stroke-width: 1.6;
		transition: transform 850ms cubic-bezier(0.65, 0, 0.35, 1);
	}
	.ink {
		fill: currentColor;
	}
	.corner {
		transition: transform 850ms cubic-bezier(0.65, 0, 0.35, 1);
	}
	.card-sums {
		display: grid;
		gap: 12px;
		text-align: center;
		font-size: 11px;
		color: var(--color-ink-2);
	}
	.card-sums :global(.math) {
		font-size: 13px;
	}
	figcaption {
		margin: 0;
		font-size: 12px;
		line-height: 1.6;
		color: var(--color-ink-3);
	}
	.gain-axis {
		display: flex;
		justify-content: space-between;
		color: var(--color-ink-3);
		font-size: 11px;
	}
	.gains {
		display: grid;
		gap: 24px;
	}
	.gain-row {
		display: grid;
		grid-template-columns: 1.2fr 1fr 42px;
		align-items: center;
		gap: 16px;
	}
	.name,
	.value {
		font-size: 13px;
	}
	small {
		display: block;
		font-size: 10px;
		color: var(--color-ink-3);
		margin-top: 3px;
	}
	.gain-track {
		position: relative;
		height: 7px;
		background: var(--color-rule);
	}
	.gain-track i {
		height: 7px;
		background: var(--color-ink);
		display: block;
	}
	.value {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	.solid {
		height: 330px;
		width: 100%;
	}
	.rotation-key {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		font-size: 11px;
		color: var(--color-ink-3);
	}
	.product-sequence {
		display: flex;
		justify-content: center;
		gap: 36px;
		font:
			26px 'KaTeX_Main',
			serif;
		color: var(--color-ink-3);
	}
	.product-sequence .marked {
		color: var(--color-ink);
	}
	.sectors {
		display: grid;
		gap: 20px;
	}
	.sectors > div {
		display: grid;
		grid-template-columns: 70px 1fr;
		align-items: center;
		gap: 20px;
	}
	.sectors > div > span {
		font-size: 12px;
		color: var(--color-ink-3);
	}
	.sectors :global(.math) {
		font-size: 20px;
	}
	.ladder-body {
		max-width: 390px;
		width: 100%;
		margin: 0 auto;
	}
	.programs {
		display: grid;
		gap: 30px;
	}
	.program-name {
		font-size: 12px;
		color: var(--color-ink-2);
		margin-bottom: 12px;
	}
	.states {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 18px;
	}
	.state > span {
		display: block;
		font-size: 11px;
		color: var(--color-ink-3);
		margin-bottom: 8px;
	}
	.state > div {
		display: flex;
		gap: 16px;
	}
	.state b {
		font-size: 20px;
		font-weight: 400;
		color: var(--color-ink-3);
	}
	.state b.selected {
		color: var(--color-ink);
	}
	.principles {
		display: grid;
		gap: 32px;
		padding: 0;
		list-style: none;
	}
	.principles li {
		display: grid;
		grid-template-columns: 125px 1fr;
		gap: 5px 20px;
	}
	.principles span {
		font-size: 11px;
		color: var(--color-ink-3);
		padding-top: 2px;
	}
	.principles strong {
		font-size: 16px;
		font-weight: 400;
	}
	.principles p {
		grid-column: 2;
		font-size: 12px;
		color: var(--color-ink-2);
		line-height: 1.5;
		margin: 0;
	}
	@media (max-width: 1100px) {
		.composition-figure {
			gap: 10px;
			max-width: 540px;
			margin: 0 auto;
			max-height: 100%;
		}
		header {
			font-size: 11px;
		}
		figcaption {
			font-size: 10px;
			line-height: 1.4;
		}
		.clocks {
			max-height: 155px;
		}
		.card-sums {
			gap: 5px;
		}
		.card-sums :global(.math) {
			font-size: 11px;
		}
		.triangles {
			max-height: 225px;
		}
		.solid {
			height: 185px;
		}
		.rotation-key {
			font-size: 9px;
		}
		.ladder-body {
			max-width: 325px;
		}
		.ladder-figure {
			gap: 6px;
		}
		.ladder-body :global(h4) {
			margin-bottom: 0;
			font-size: 11px;
		}
		.ladder-body :global(p) {
			font-size: 9px;
			margin-top: 0;
		}
		.sectors {
			gap: 12px;
		}
		.sectors :global(.math) {
			font-size: 16px;
		}
		.product-sequence {
			font-size: 20px;
		}
		.programs {
			gap: 14px;
		}
		.program-name {
			margin-bottom: 8px;
			font-size: 10px;
		}
		.state > span {
			margin-bottom: 3px;
		}
		.state b {
			font-size: 17px;
		}
		.principles {
			gap: 16px;
		}
		.principles strong {
			font-size: 14px;
		}
		.principles li {
			grid-template-columns: 110px 1fr;
			gap: 3px 10px;
		}
		.principles p {
			font-size: 11px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.hand,
		.corner {
			transition: none;
		}
	}
</style>
