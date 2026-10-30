# The blindness theorem, built from scratch

*A step-by-step guide for anyone with college calculus and a little linear algebra.*

By the end you should be able to state the theorem, prove it on a blank page, and say in one sentence why it matters.
The core proof is short. Most of this document builds the intuition so that each step feels inevitable.

The theorem is formalised in Lean 4 with Mathlib (`Polyformer.blindness`, file `Blindness.lean` in the `lean`
worktree). The machine-checked version uses only the three standard axioms and no `sorry`.

---

## 0. The one-sentence version

> **A training loss that only looks at the states a network actually reaches cannot tell whether small errors near those
> states shrink or grow.**

Two networks can produce exactly the same training loss, value for value, on every training example. One of them
quietly corrects its mistakes. The other quietly amplifies them. Training cannot see the difference, because the
difference lives in *derivatives*, and the loss only reads *values*.

That is the whole idea. The rest of this document makes it precise.

---

## 1. The setting: a tracker

We study a network that reads a sequence of events and keeps a running internal state. Call it a **tracker**.

- The **state** is a vector $h \in \mathbb{R}^d$. (Later we will put it on a sphere; ignore that for now.)
- For each possible **event** $x$ (a token, a move, a statement) there is an **update map**
  $$F_x : \mathbb{R}^d \to \mathbb{R}^d.$$
  Reading event $x$ in state $h$ produces the new state $F_x(h)$.
- A **readout** turns a state into an answer, for example the scores (logits) of the possible outputs.

Start from a fixed state $h_0$. Reading the events $x_1, x_2, \dots, x_t$ produces
$$h_1 = F_{x_1}(h_0),\quad h_2 = F_{x_2}(h_1),\quad \dots,\quad h_t = F_{x_t}(h_{t-1}).$$

**Running example.** A tracker that follows the position of a ball under three cups. Each event is a swap of two cups.
The true state is "which cup has the ball". A network must carry that fact in its vector $h$, forever, through any
number of swaps.

---

## 2. What training actually looks at

Training uses a **finite** set of example sequences. Run the tracker on all of them and collect every state it visits.
Call these the **reached states**:
$$c_1, c_2, \dots, c_n.$$

There are finitely many, because there are finitely many training sequences of finite length.

Every standard training loss is built from quantities computed **along these runs**:

- **Next-token likelihood (cross-entropy).** At each position, read out from $h_t$ and compare with the label.
- **Next-state regression.** Compare $h_t$ with a target vector.
- **Equivalence terms.** Compare the final states of two sequences that should end in the same place.

All of these depend on the tracker only through the states $h_t$ along the training runs. Those states are produced
by applying the maps $F_x$ to reached states. So the whole loss depends only on

$$\text{the values } F_x(c_s) \text{ for the reached states } c_s \text{ and the events } x \text{ applied there.}$$

We will call any such loss a **reached-state objective**. Here is the precise definition we need:

> **Definition.** An objective $J$ *reads only reached values* if any two trackers that give the same value
> $F_x(c_s)$ at every reached state $c_s$ (for every event $x$ applied there in training) get the same $J$.

**Why that definition captures cross-entropy.** Suppose two trackers $F$ and $G$ agree at every reached state. Run both
on a training sequence from the same $h_0$. By induction:

- At step 0 they are in the same state $h_0$.
- If they are both in state $h_{t-1}$, which is a reached state, then $G_{x_t}(h_{t-1}) = F_{x_t}(h_{t-1})$ because
  they agree there. So they are both in state $h_t$.

So the two trackers walk **exactly the same path** through every training sequence. Every readout, every loss term and
every gradient with respect to the readout is identical. The loss cannot tell them apart.

Hold on to this picture: *on the training data, the two networks are literally indistinguishable.*

---

## 3. What decides whether errors grow: the derivative

Now ask a different question. Suppose at some step the state is slightly off: instead of the reached state $c$, the
network is at $c + e$, where $e$ is a small error vector. What happens after one more event?

Calculus answers it. The **Jacobian** $DF_x(c)$ is the $d \times d$ matrix of partial derivatives of $F_x$ at $c$, and
for small $e$:
$$F_x(c + e) \approx F_x(c) + DF_x(c)\, e.$$

The error after the step is approximately $DF_x(c)\,e$. The Jacobian decides its fate:

- If $DF_x(c)$ shrinks vectors (all its singular values are below 1), the error shrinks. The tracker **corrects
  itself**.
- If it stretches some direction (a singular value above 1), errors along that direction grow. The tracker **drifts**.

**One-dimensional picture.** Take $d = 1$ and $F(h) = a\,h$. An error $e$ becomes $a e$, then $a^2 e$, and after $t$
steps $a^t e$.

- With $a = 0.7$, after 20 steps the error is multiplied by $0.7^{20} \approx 0.0008$. It has essentially vanished.
- With $a = 1.1$, after 20 steps it is multiplied by $1.1^{20} \approx 6.7$. After 100 steps the factor is about
  $13{,}780$.

Over a long sequence, the errors are multiplied by the **product of the Jacobians along the path**. So the derivatives
at the reached states decide whether the tracker survives a long input.

---

## 4. The key observation: values do not determine slopes

Here is the heart of the matter, in one dimension first.

Suppose you know that a function passes through the point $(0, 0)$, that is $f(0) = 0$. What is its slope at 0?

You cannot tell. Both $f(h) = 0.7\,h$ and $g(h) = 1.1\,h$ pass through $(0,0)$. They agree at the point and disagree
on the slope.

Now suppose you know the function's value at **finitely many** points. Same answer: the values do not pin down the
slopes. You can draw a smooth curve through the given points with **any** slopes you like at those points.

That is the entire theorem. Everything below makes "draw a smooth curve with any slopes you like" rigorous in $d$
dimensions, and checks that it does not disturb anything else.

The tool for that is a **bump function**.

---

## 5. The tool: a smooth bump

A **bump function** around a point $c$ is a smooth function $\varphi : \mathbb{R}^d \to [0,1]$ with:

1. $\varphi(z) = 1$ for $z$ close to $c$ (say $|z - c| \le r/2$);
2. $\varphi(z) = 0$ for $z$ far from $c$ (say $|z - c| \ge r$);
3. $\varphi$ is infinitely differentiable everywhere.

**Why does such a function exist?** Polynomials cannot do it: a polynomial that is constant on a whole ball is constant
everywhere. The trick is a famous function from calculus:
$$S(t) = \begin{cases} e^{-1/t} & t > 0, \\ 0 & t \le 0. \end{cases}$$

$S$ is zero for $t \le 0$ and positive for $t > 0$, and **all** of its derivatives exist and are continuous, even at
$t = 0$. (Every derivative of $e^{-1/t}$ has the form $p(1/t)\,e^{-1/t}$ for a polynomial $p$, and that tends to 0 as
$t \to 0^+$ because the exponential wins.)

From $S$ we build the bump:
$$\varphi(z) = \frac{S\bigl(r^2 - |z-c|^2\bigr)}{S\bigl(r^2 - |z-c|^2\bigr) + S\bigl(|z-c|^2 - r^2/4\bigr)}.$$

Check it:

- If $|z - c| \le r/2$, the second $S$ in the denominator is 0, so $\varphi = 1$.
- If $|z - c| \ge r$, the numerator is 0, so $\varphi = 0$.
- In between, both $S$ terms are positive, so the denominator never vanishes, and $\varphi$ is a ratio of smooth
  functions.

You do not need the formula to follow the proof. You only need the three properties above.

**Picture.** A smooth plateau of height 1 over the small ball, sloping down to 0, and flat zero everywhere outside the
larger ball.

---

## 6. The construction in one dimension

Let us prove the one-dimensional version completely. It contains every idea.

**Given:** a smooth map $f : \mathbb{R} \to \mathbb{R}$, finitely many reached points $c_1, \dots, c_n$ (all
different), and target slopes $m_1, \dots, m_n$ (any real numbers you like).

**Wanted:** a smooth map $g$ with
- $g(c_s) = f(c_s)$ for every $s$ (same values), and
- $g'(c_s) = m_s$ for every $s$ (prescribed slopes).

**Step 1: give each point its own private neighbourhood.** The points are finitely many and distinct, so there is a
radius $r > 0$ small enough that the intervals $(c_s - r, c_s + r)$ do not overlap. Take a bump $\varphi_s$ around
each $c_s$ with that $r$.

**Step 2: write down the new map.**
$$g(h) = f(h) + \sum_{s=1}^{n} \varphi_s(h)\,\bigl(m_s - f'(c_s)\bigr)\,(h - c_s).$$

Read it slowly. Near $c_s$ we add a straight line through $c_s$ whose slope is "what we want minus what we have". The
bump switches that correction on near $c_s$ and off everywhere else.

**Step 3: values are unchanged.** At $h = c_s$:

- The factor $(h - c_s)$ in the $s$-th term is zero.
- Every other term has $\varphi_{s'}(c_s) = 0$, because $c_s$ is outside the other bumps.

So $g(c_s) = f(c_s)$.

**Step 4: slopes are as prescribed.** Differentiate the $s$-th correction term with the product rule:
$$\frac{d}{dh}\Bigl[\varphi_s(h)\,(m_s - f'(c_s))\,(h - c_s)\Bigr] = \varphi_s'(h)\,(m_s - f'(c_s))\,(h - c_s) + \varphi_s(h)\,(m_s - f'(c_s)).$$

At $h = c_s$, the first piece contains $(h - c_s) = 0$, so it vanishes. The second piece is $1 \cdot (m_s - f'(c_s))$
because $\varphi_s(c_s) = 1$. Near $c_s$ the other bumps are identically zero, so their terms contribute nothing.
Therefore
$$g'(c_s) = f'(c_s) + \bigl(m_s - f'(c_s)\bigr) = m_s.$$

**Step 5: smoothness.** $g$ is a finite sum of products of smooth functions, so it is smooth.

**Step 6: nothing changes far away.** Outside all the bumps, every $\varphi_s$ is zero, so $g = f$ there.

That is the one-dimensional blindness theorem. Prescribe any slopes you like at the reached points, and the values,
which are everything the loss can see, stay exactly the same.

> **Try it yourself.** Take $f(h) = 0.7\,h$, one reached point $c = 0$, and target slope $m = 1.1$. Write $g$ and check
> $g(0) = 0$ and $g'(0) = 1.1$. You now have a self-correcting tracker and a drifting one with identical training
> behaviour.

---

## 7. The construction in $d$ dimensions

Nothing changes except that slopes become matrices.

**Given:** smooth update maps $F_x : \mathbb{R}^d \to \mathbb{R}^d$; finitely many distinct reached states
$c_1, \dots, c_n$; and, for each reached state $c_s$ and event $x$, any $d \times d$ matrix $M_{s,x}$ you like.

**Construction.** Choose $r$ so that the balls of radius $r$ around the $c_s$ are disjoint, and bumps $\varphi_s$ as in
§5. Define
$$G_x(z) = F_x(z) + \sum_{s=1}^{n} \varphi_s(z)\,\bigl(M_{s,x} - DF_x(c_s)\bigr)\,(z - c_s).$$

**Values.** At $z = c_s$ the $s$-th correction is multiplied by $(z - c_s) = 0$, and the other bumps vanish at $c_s$. So
$G_x(c_s) = F_x(c_s)$.

**Jacobian.** Write $A = M_{s,x} - DF_x(c_s)$, a fixed matrix. The product rule for a scalar function times a vector
function gives
$$D\bigl[\varphi_s(z)\,A\,(z - c_s)\bigr] = A\,(z - c_s)\,\nabla\varphi_s(z)^{\top} + \varphi_s(z)\,A.$$

At $z = c_s$ the first term is zero because it contains $(z - c_s)$, and the second is $A$ because $\varphi_s(c_s) = 1$.
So
$$DG_x(c_s) = DF_x(c_s) + M_{s,x} - DF_x(c_s) = M_{s,x}.$$

**Everything else.** $G_x$ is smooth, and $G_x = F_x$ outside the balls.

---

## 8. Putting it together: the theorem

**Theorem (blindness).** Let a tracker's reached states on the training data be finitely many. For any choice of
matrices $M_{s,x}$ there is a smooth tracker that agrees with it at every reached state and has Jacobian $M_{s,x}$ at
every reached state $c_s$ for every event $x$. Every objective that reads only reached values takes the same value at
both trackers.

**Proof.**
1. Build $G$ as in §7. It has the same values and the prescribed Jacobians at every reached state.
2. By the induction of §2, $G$ and $F$ walk exactly the same path through every training sequence.
3. An objective that reads only reached values therefore sees identical inputs, so it returns the same number. $\square$

**Make it vivid.** Pick every $M_{s,x}$ with all singular values equal to $0.5$: the new tracker halves every small
error at every reached state, so it corrects itself. Or pick them with a singular value of $2$: errors double at every
step, so it drifts and eventually breaks. Both trackers have **the same training loss, the same gradients of the loss
with respect to the readout, and the same predictions on every training example.** Training is blind to the
difference.

---

## 9. The sphere version (what the paper actually states)

In our networks the state is normalised after every step to lie on a sphere. This is the **closure**:
$$N(z) = \frac{z}{|z|}.$$

The paper calls the normalised state a **view**, and the update is $N \circ F_x$. Does the construction survive?

Yes, with one small check. Apply $N$ after the corrected map: $G_x' = N \circ G_x$.

- **Values.** At a reached view, $G_x(c_s) = F_x(c_s)$ already has length 1, so $N$ leaves it unchanged.
- **Jacobian.** At a unit vector $u$, the derivative of $N$ is
  $$DN(u) = I - u u^{\top},$$
  the projection that removes the component along $u$. On the sphere, small errors are **tangent** vectors
  (perpendicular to the current state). If we choose $M_{s,x}$ to send tangent vectors at $c_s$ to tangent vectors at
  $u = F_x(c_s)$, the projection leaves those outputs alone:
  $$D(N \circ G_x)(c_s)\,v = (I - uu^\top)\,M_{s,x}\,v = M_{s,x}\,v \quad\text{for tangent } v.$$

So on the sphere, too, we can prescribe any Jacobian on tangent vectors while keeping every reached value. That is
exactly Theorem 1(a) of the paper.

---

## 10. Corollary: next-token likelihood is blind

Next-token likelihood (cross-entropy) is computed from the readout of each state along the training sequences. By §2
it reads only reached values. So by the theorem:

> **Corollary.** Next-token likelihood, next-state regression and equivalence losses all take the same value on a
> self-correcting tracker and on a drifting one that agree on the reached states.

There is a second way to see why this matters for **long** sequences. Along a path $c_0 \to c_1 \to \dots \to c_t$, a
small initial error $e$ becomes approximately
$$DF_{x_t}(c_{t-1})\,\cdots\,DF_{x_2}(c_1)\,DF_{x_1}(c_0)\;e.$$

The theorem lets us choose every factor in that product. So the long-run fate of errors, which decides whether the
tracker works at length 1,000 or 10,000, is completely unconstrained by the training loss. The Lean formalisation
proves this "error cocycle" statement too.

---

## 11. What the theorem does *not* say

Read these carefully. They are where people go wrong.

1. **It does not say training produces a bad tracker.** It says the loss cannot *tell* good from bad. Which one you
   get depends on everything else: the architecture, the initialisation, the optimiser. In our experiments a closure
   onto a sphere often supplies self-correction by itself, and the interpreter's lookup supplies it by design. The
   theorem explains why those help: they put robustness where the loss cannot reach.
2. **The new tracker need not be one your network can represent.** It is any smooth map. The theorem is about the
   *objective*, not about one architecture. That is exactly the point: the objective carries no information about the
   Jacobians, so any guarantee must come from somewhere else.
3. **It is about values at reached states only.** An objective that also looks *off* the path, for example by kicking
   the state and asking it to come back, reads more than values. That is the remedy.

The paper adds a sharper warning, **Corollary 1 (finite reads)**. Even an objective that reads values and finitely
many derivatives at finitely many points cannot certify that a whole ball around each state is safe. Any point of the
ball that it never reads can be sent out of its cell without changing the objective. The proof is the same bump trick:
put a tiny bump at the unread point. This is why a guarantee for every input needs a **certificate** (a check of every
case), not just a loss.

---

## 12. Optional: how cheap a drift looks to the loss (Theorem 1(c))

The theorem says the loss cannot see error dynamics *at all*. Part (c) puts numbers on a related fact: a slow drift
costs **almost nothing** in loss at the training length, yet it breaks the tracker at long lengths.

### 12.1 Errors add up at most linearly

Suppose the learned update is **non-expansive**: $|\hat F_x(a) - \hat F_x(b)| \le |a - b|$. Suppose also that at the
exact states it misses the right next state by at most $\varepsilon$: $|\hat F_x(z_t) - F_x(z_t)| \le \varepsilon$. Let
$e_t = |\hat z_t - z_t|$ be the learned tracker's distance from the exact one after $t$ events. Then
$$e_{t+1} = |\hat F(\hat z_t) - F(z_t)| \le \underbrace{|\hat F(\hat z_t) - \hat F(z_t)|}_{\le\, e_t} + \underbrace{|\hat F(z_t) - F(z_t)|}_{\le\, \varepsilon} \le e_t + \varepsilon.$$

Starting from $e_0 = 0$, induction gives $e_t \le \varepsilon\, t$.

**Why non-expansion matters.** Without it, the drift can be exponential. Take the learned map $x \mapsto 2x + \varepsilon$
near an exact state 0. The error after $t$ steps is $\varepsilon(2^t - 1)$. The Lean formalisation found exactly this
counterexample, which is why the paper now states the assumption explicitly.

### 12.2 When the readout stays right

Let the logits be $K$-Lipschitz in the state, and let the exact tracker's smallest logit margin be $m$ (correct logit
minus the largest wrong logit). Moving the state by $e_t$ changes the gap between the correct logit and any wrong one
by at most $\sqrt{2}\,K\,e_t$. (Two coordinates of a vector are at most $\sqrt{2}$ times its length in total, by
Cauchy–Schwarz.)

So the answer stays right as long as $\sqrt{2}\,K\,\varepsilon\, t < m$, that is, up to length
$$N \approx \frac{m}{\sqrt{2}\,K\,\varepsilon}.$$

The bound is sharp. A tracker that drifts at exactly rate $\varepsilon$ along the worst direction fails just after $N$.

### 12.3 What it costs in loss: a clean little identity

Cross-entropy at the correct label $y$ is
$$\mathrm{CE} = \log\Bigl(1 + \sum_{j \ne y} e^{\ell_j - \ell_y}\Bigr) = \log(1 + S).$$

Suppose every wrong logit rises by at most $a$ relative to the correct one. Then $S$ grows by at most a factor $e^{a}$,
and
$$\mathrm{CE}_{\text{new}} - \mathrm{CE}_{\text{old}} \le \log\frac{1 + e^{a} S}{1 + S} = \log\bigl(1 + (e^{a} - 1)\,s\bigr) \le (e^{a} - 1)\,s,$$
where $s = S/(1+S)$ is exactly the model's **probability of being wrong** at that position. (The middle equality is
just algebra; the last step uses $\log(1+x) \le x$.)

At training length $L$, the shift is at most $a = \sqrt{2}\,K\,\varepsilon\,L$. Averaging over positions, the excess
training loss is at most
$$\bar s\,\bigl(e^{\sqrt{2} K \varepsilon L} - 1\bigr),$$
where $\bar s$ is the exact tracker's average error probability.

### 12.4 The punchline, with numbers

Take a confident model ($\bar s = 10^{-3}$), $K = 1$, margin $m = 5$, a tiny drift $\varepsilon = 10^{-3}$ per step,
and training length $L = 16$:

- **Excess loss at training length:** $10^{-3} \times (e^{0.0226} - 1) \approx 2.3 \times 10^{-5}$. That is invisible
  next to ordinary noise in the loss.
- **Length at which the readout can break:** $N \approx 5 / (1.414 \times 10^{-3}) \approx 3{,}500$ events.

The loss charges almost nothing for a drift that destroys the tracker a few thousand steps later. Training has no
reason to remove it.

---

## 13. Rebuild it yourself: a checklist

Close this document and try to rebuild the argument from these prompts.

1. What does a reached-state objective depend on? (Values $F_x(c_s)$ at finitely many points.)
2. Why do two trackers that agree at reached states give the same loss? (They walk the same path; induction.)
3. What decides whether errors grow? (The Jacobians at the reached states, multiplied along the path.)
4. How do you change a derivative at a point without changing any value? (Add $\varphi(z)\,A\,(z - c)$ with a bump
   $\varphi$; the factor $(z - c)$ kills the value, and the product rule gives slope $A$.)
5. Why use bumps with disjoint supports? (So each correction acts only near its own point.)
6. Why does the sphere not break it? (The projection $I - uu^\top$ leaves tangent vectors alone.)

If you can answer all six, you can derive the blindness theorem from scratch.

---

## 14. Why it matters, in one paragraph

Language models are trained by next-token likelihood. The blindness theorem says that objective is silent about the
one property that decides whether a long internal computation survives: whether small errors die out or pile up. So
when a model loses track of a long calculation, the training objective never asked it not to. The fix has to look
where the loss does not. One way is an **architecture** that corrects errors by construction: a closure, or a lookup
that snaps to exact symbols. The other is an **objective that probes off the path**: kick the state and require it to
come back. With a **certificate**, you can go further and check every case, which no loss alone can do.

---

### Where to read more

- The paper's statement: Theorem 1 in `paper/jewel/main.tex`. The proof is in the Supplementary Information,
  §"Blindness (Theorem 1(a))".
- The Lean formalisation: `Polyformer.blindness` in `Blindness.lean`, plus the likelihood corollary, Theorem 1(b) and
  Theorem 1(c) with its non-expansion hypothesis. Status and modelling choices are in `research/lean/STATUS.md` on the
  `lean` branch.
