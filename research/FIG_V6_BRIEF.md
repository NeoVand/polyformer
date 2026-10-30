# FIG_V6: figures with character (Neo's feedback, 24 Oct ~14:15)

Neo: "The fig options are not great." Think harder and more boldly, own the ideas, teach. Nature figures have many
panels and reveal details. Every data panel is built from records; schematics are designed deliberately, with taste.

## Keep and improve (Neo liked these)
- **The proofs-click set** (pr1_blindness, pr2_kicks, pr3_scale_clock): expand into multi-panel figures with detail.
- **Mechanism** (m1_tesseract, m2_basins, m3_clusters):
  - Basins: boundaries must be sharp and clean. Compute the reached class on a much finer grid, or trace boundaries
    as anti-aliased polygons (marching squares on a high-resolution label grid). Re-derive every label from the data
    and assert it: each region labelled with the class it reaches, each centre with its true class. Higher resolution.
  - Tesseract globes: the filled norm disk is intrusive. Use a dotted, empty circle for the sphere outline.
- **Training losses rank the trackers backwards** (s3_loss).
- **Exact final states** (r1_matrix and r3_slopes; Neo said "exact final states are good").

## New figures we do not have yet
1. **Conceptual: what the loss is made of, and what we add.** Not boxes and arrows. A designed schematic that teaches:
   the next-token loss as a landscape whose valley floor is flat along the drift direction (blind), and the added terms
   as forces: certified pairs as threads pulling equivalent histories together, the fixed norm as the sphere the state
   lives on, next-state as a flow along trajectories, the minimal automaton as the lattice the state settles onto.
2. **Architecture:** frozen language-model features, the state slot on its sphere, the readout, and the three losses,
   drawn as one elegant object with deliberate typography.
3. **The domains, in a cool way: what the method solves.** For each of the six domains: a real input snippet, the
   hidden state machine it implies (drawn as a small automaton or state picture), the checker that certifies pairs,
   the length gap (train vs test), and the outcome. An infographic with character.
4. **Conceptual figures for the proofs:** blindness (the loss floor masks the per-step error), stiffness (first-order
   vs floor-damped response, with the analytic slopes), closure and its counterexample (a scale clock on a cone vs the
   sphere), error correction and the certificate (balls mapping into balls along the automaton graph), the error
   cocycle (error vectors transported around a cycle; an expanding cycle breaks, a contracting one holds).
5. **Landscapes and vector fields, for a reason:** the loss landscape around the drifting and the exact solutions with
   each term's gradient as streamlines (next-token's gradient vanishes along the drift; the equivalence term's points
   back); the learned transition's vector field near the class centres from real checkpoints (contraction).
6. **3D, done with great care.** Blender 5.2 is installed (/Applications/Blender.app; headless:
   `Blender -b -P script.py`). Candidates: a glass sphere with the tesseract's edges as tubes; the loss landscape as
   lit terrain built from v4/landscape/grid.json.

## Process
1. **Inspiration with image models.** Use the OpenAI Images API (Neo: use gpt-image-2.5-sunburst only). Source ~/.polyformer_keys in the shell; never print, log or commit the keys.
   Write long, explicit prompts for each figure: content, panels, layout, palette (Cobalt and Rose from
   research/figstyle/palette.json, white backgrounds), typography, mood, references (Nature, Quanta, Distill). Make 2-4
   variants per figure, save each image with its prompt in paper/nmi/figures/v6/inspiration/. Cap $25.
   **Nature does not accept AI-generated images in published figures, so these are design references only.** No
   generated pixel goes into the paper.
2. **Build** the best ideas faithfully: real data in matplotlib with the house style, schematics in SVG/TikZ quality,
   3D in Blender.
3. **Deliver** paper/nmi/figures/v6/: Figure 1-5 drafts as multi-panel Nature-style figures, Extended Data candidates,
   the inspiration sheet, and a README saying what each panel teaches. Send nothing to Neo directly; commit, no push,
   and report the paths.
