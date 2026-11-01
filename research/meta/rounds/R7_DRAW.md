# Round 7 draw (1 Nov 2026): what certified bounded-view neural computation is FOR

**Goal.** Find what certified, bounded-view neural computation (Sketchpad) is for: a use where a guarantee on a neural
network's own computation matters to someone, which no calculator, tool or output checker trivially provides, and
which one person can show in weeks.

**How the fields were drawn.** From the 40-item offline list in the unstuck skill. That list is unprincipled: one
author's stand-in, not a published taxonomy. We used a seeded RNG (seed 20261101) and skipped the fields used in rounds
5 and 6. The subfields were drawn by the next eight digits, index = (digit mod 8) + 1.

| Field | Subfield list (8) | Digit → pick |
|---|---|---|
| 39 wine tasting | 1 descriptive sensory panels · 2 blind-tasting deduction grids · 3 aroma wheel · 4 triangle/discrimination tests · 5 appellation (AOC) certification of terroir · 6 vintage charts · 7 fault thresholds (TCA) · 8 en primeur barrel scoring | 4 → **5 appellation certification** |
| 3 archaeology | 1 stratigraphy (Harris matrix) · 2 radiocarbon calibration · 3 seriation · 4 typology · 5 experimental archaeology · 6 provenance by isotope/chemical sourcing · 7 decipherment · 8 site formation processes | 5 → **6 provenance sourcing** |
| 4 architecture | 1 pattern language · 2 prescriptive vs performance building codes · 3 structural load paths · 4 modular grids · 5 shearing layers · 6 post-occupancy evaluation · 7 universal design · 8 fire egress | 2 → **3 structural load paths** |
| 20 field linguistics | 1 elicitation frames · 2 minimal pairs · 3 interlinear glossing · 4 paradigm tables · 5 Swadesh lists · 6 documentation archives · 7 consultant texts · 8 phonotactics | 2 → **3 interlinear glossing** |
| 2 ethology | 1 fixed action patterns · 2 supernormal stimuli · 3 imprinting · 4 honest signalling · 5 ethograms · 6 dominance hierarchies · 7 stigmergy · 8 corvid cache-recovery memory | 7 → **8 cache-recovery memory** |
| 36 surgery | 1 WHO safety checklist · 2 time-out and site marking · 3 sponge and instrument counts · 4 frozen sections · 5 laparoscopic triangulation · 6 M&M conferences · 7 enhanced recovery · 8 telesurgery | 8 → **1 WHO safety checklist** |
| 35 sports coaching | 1 periodisation · 2 deliberate practice · 3 video analysis · 4 constraints-led approach · 5 tactical periodisation · 6 load monitoring · 7 set-piece playbooks · 8 talent identification | 7 → **8 talent identification** |
| 8 child development | 1 object permanence · 2 core number systems (approximate vs exact) · 3 theory of mind · 4 Piagetian conservation · 5 statistical word learning · 6 scaffolding (ZPD) · 7 executive function · 8 counting principles | 1 → **2 core number systems** |

**Dead framings** (variants need a stated change of level):
- long arithmetic for its own sake;
- GSM8K gains at 0.8B (fresh items: −5.8);
- a universal interpreter as the claim (Lewandowski et al. 2026 already show it);
- certified CLRS-style algorithm families (DNAR, ICML 2025);
- logit drift as the explanation of frontier errors;
- certified retrieval (a witness plus a checker is cheaper);
- latent programs written into hidden states;
- adapter-per-operation as the general method.

Reports go to `rounds/r7_<slug>.md`.
