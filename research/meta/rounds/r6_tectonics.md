# R6: plate tectonics → ARC-AGI-3

## 1. Objects and techniques
- Rigid plate (McKenzie & Parker 1967; Morgan 1968): a spherical cap that moves without strain.
- Boundary types (Wilson 1965): ridges create crust, trenches destroy it, transforms slide it.
- Magnetic stripes (Vine–Matthews 1963): a symmetric record of reversals.
- Euler's theorem as Morgan used it (1968): transforms are small circles about one pole, and rate ∝ sin(distance from pole) checks the pole independently.
- Plate-circuit closure (McKenzie & Morgan 1969; NUVEL-1, 1990): velocities around a loop sum to zero. A closure misfit forced a new Indian Ocean boundary (Wiens et al. 1985).
- Hess's budget (1962): constant area plus creation at ridges means an unseen sink must exist.
- Crucial test: Wilson's predicted slip sense, confirmed by Sykes (1967).

## 2. Map to the problem
- P1: a plate is the largest set of cells sharing one rigid displacement. Each changed cell is typed as created, destroyed or transported.
- P2: one generator per (object, action), fitted from many cells. Independent observables must agree.
- P3: act where hypotheses that fit the past equally well predict opposite outcomes (Wilson–Sykes). Closed action loops serve as closure tests.
- P4: Wegener's jigsaw: complementary shapes suggest a join. Weak.
- P5: nothing (reconstruction is just backward chaining).
- P6: a new level is a "bend" (Hawaii–Emperor), so keep the pole and refit only the bent segment.
- P7: six plates explained the globe (Le Pichon 1968); every transition should constrain a global parameter.
- P8: rigid interiors are exact, and residuals along a known track flag change-points.

## 3. Map from the problem
- Geology could not intervene. Closure and redundant observables stood in for the ability to act.
- Kinematics predicted correctly without a mechanism, so an agent needs only kinematics.
- One profile settled it (Eltanin-19, 1966), because symmetry was a sharp prediction.

## 4. Grades
- Kinematic segmentation plus create/destroy/transport typing: FRAME (VGDL has these).
- One generator per object-action: FRAME.
- Discriminating action: TOOL (Box & Hill 1967).
- Loop closure plus splitting where residuals cluster: TOOL.
- Budget closure ⇒ hidden sink: TOOL, the best yield.
- Jigsaw goal prior: LOW. Planning: nothing.
- No HIT.

## 5. Candidates
A. Budget ledger (Hess). Stack per-transition changes in counts per colour, objects per type and counter readouts; the left null space of that matrix gives the conserved quantities. A transition that breaks one reveals creation, destruction or hidden state (a consumed key, an off-grid counter), and every rule hypothesis must respect the ledger. Counts that change only at level ends are goal candidates. Addresses P1, P2, P4, P8.
Kill: if the ledger cuts actions-to-first-correct-model by less than 20% against the same inducer without it.

B. Circuit probes (NUVEL). Mix in loops that the model predicts return to the same state (a then a⁻¹; the commutator a b a⁻¹ b⁻¹); a loop that fails to close points to the cells where the model is wrong. Fit all transitions jointly and add an object type or hidden variable where residuals cluster. Addresses P2, P3, P6, P8.
Kill: if probes find model errors per action at less than 1.5× the rate of curiosity actions.

## 6. Adversary
A: Movement puzzles have only trivial invariants, and painting games break conservation by design. Prior art: conserved moieties (Feinberg 1979; Famili & Palsson 2003); Liu & Tegmark 2021; Noether Networks (Alet et al. 2021); VGDL (Schaul 2013); EMPA (Tsividis et al. 2021).

B: Probes spend actions the score counts, and irreversible mechanics make loops fail for uninformative reasons. Prior art: homing sequences (Rivest & Schapire 1993); Pierce & Kuipers 1997; loop closure in SLAM (Lu & Milios 1997); EMPA.
