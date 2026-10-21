<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import LanguageFigure, { EARLY } from '../LanguageFigure.svelte';
	import { number } from '../toc.ts';
</script>

<section class="part" id="part-language">
	<header class="part-head">
		<span class="roman">Part V</span>
		<h2>The language test</h2>
		<p class="part-lede">
			Puzzles are a controlled setting. The question that matters is whether any of this makes a
			better language model.
		</p>
	</header>

	<section class="chapter" id="language">
		<h3><span class="n">{number('language')}</span>What we tried on text</h3>
		<p class="src">
			<span class="mark measured"></span>Cloud GPUs, three seeds per model; research notes SEARCH §8
			and LOCAL §0
		</p>
		<p>
			A language model reads text as tokens, pieces of words, and predicts the next token at every
			position. Its <em>loss</em> is the average cross-entropy of those predictions on held-out text,
			measured in nats per token: lower is better. Our test bed was FineWeb-Edu, a large collection of
			educational web pages, cut into tokens with GPT-2's tokenizer. Each model had six layers of width
			512, about 19 million parameters outside the embeddings, and trained on 400 million tokens, roughly
			the amount such a model can usefully absorb.
		</p>
		<p>
			<strong>How we kept ourselves honest.</strong> New layers often cost more compute than softmax
			attention, and a model that computes more can look better for that reason alone. So every
			comparison matched training compute, by giving the cheaper model more tokens or the more
			expensive one fewer layers. Each layer got its own learning-rate search, three seeds, and a
			bar written down before the runs: at least
			<strong>1% lower loss than softmax at equal compute, on all three seeds</strong>. For scale,
			giving softmax a seventh layer, about 7% more compute, lowered its loss by about 0.4%. Writing
			the bar down first means a result cannot be talked up afterwards.
		</p>
		<p>
			<strong>Subset attention.</strong> The first language layer combined the two ideas of Parts II and
			IV. A softmax picks which tokens matter, and Newton's identities turn those weights into sums over
			subsets of every size; an optional extra term follows chains of hops, for pointer-like structure.
			We called it free-field attention. It lost: 2.2% worse than softmax at equal compute, 1.1% worse
			even with 6% more compute, and still 0.8% worse when it started out as plain softmax with the higher
			arities switched off. On TinyStories, a corpus of simple children's stories, it was 2.8% to 4.3%
			worse.
		</p>
		<p>
			<strong>Mechanism tests.</strong> On small diagnostic tasks, such as recalling the value
			stored under a key or continuing a repeated pattern, the only big win came from a trick that
			mixes each token's key with the previous token's, and softmax gained exactly as much from the
			same trick. The higher-order terms alone won nothing. And on the pattern-continuation circuit
			that language models form early in training, called an <em>induction head</em>, the hop sector
			made the circuit appear later, not earlier: after 1.1 to 1.2 times as many tokens as softmax
			needed.
		</p>
		<p>
			<strong>A better estimate instead of more order.</strong> Softmax attention returns a weighted
			average of values. Statisticians call that a local-constant estimate, and it is biased
			whenever the values change systematically across the keys. <em>Local-linear attention</em>
			fits a small linear model instead <Cite id="lla" />, and <em>Parallax</em> adds a learned
			linear correction to the weights <Cite id="parallax" />. With the Muon optimiser <Cite
				id="muon"
			/>, both helped: 0.39% and 0.75% lower loss at equal compute, consistent across seeds, and
			both short of 1%. Under AdamW, Parallax's gain shrank to about 0.3%. Our own variant used
			subsets of up to nine tokens, and the published method, which uses only pairs, beat it.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<LanguageFigure groups={EARLY} />
				<figcaption>
					Change in held-out loss against the softmax baseline of the same study, at equal compute;
					lower is better. Small numbers under each value are the three seeds. The dashed line is
					the 1% bar we set in advance. A later study, in section {number('combined')}, adds a
					stronger baseline and two recurrent networks.
				</figcaption>
			</figure>
		</div>
		<p>
			One more number puts these in perspective. Switching the optimiser from AdamW to Muon lowered
			the loss of every model by about 4% at 100 million tokens, more than any change to the layer,
			although the gap narrowed to about 0.5% by 400 million tokens.
		</p>
	</section>

	<section class="chapter" id="language-reading">
		<h3><span class="n">{number('language-reading')}</span>What the language result means</h3>
		<p class="src"><span class="mark new"></span>Our reading of the evidence</p>
		<p>
			The puzzles are a worst case for pairs by design: their answers depend only on whole groups,
			and every smaller piece looks random. Text is not like that. Most of what predicts the next
			token is visible in pairs: the previous few tokens, a name mentioned earlier, a matching
			bracket. Our layers paid for structure that text at this scale rarely needs, and their extra
			terms made optimisation harder. The two things that helped, mixing in the previous token and
			correcting the estimate, are both first-order fixes.
		</p>
		<p>
			These results are about small models. A higher-order layer could still pay at larger scale,
			and 2-simplicial attention has been reported to improve how loss scales on reasoning and code
			at billions of parameters <Cite id="roy" />. We could not test that. What we could test was a
			sharper question about the puzzles themselves: <em>why</em> did the winning layers win? The answer
			changed how we thought about everything above.
		</p>
		<p class="pull">
			Up to here the story was about how many tokens a layer looks at. From here on it is about what
			the layer does with them: <em>average</em> them, <em>multiply</em> them, or <em>compose</em> them.
		</p>
	</section>
</section>

<style>
	.pull {
		margin-top: 22px;
		padding-left: 16px;
		border-left: 1px solid var(--color-rule);
		color: var(--color-ink);
	}
</style>
