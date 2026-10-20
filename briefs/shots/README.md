# Production visual review

260 final views of the composition story, captured with Playwright from the built static site.
`desktop` means **1440 × 900**; `mobile` means **390 × 844**, both at device scale 1.
Every main page and new lesson/report section has `dark` and `light` browser-preference
captures. The app deliberately keeps its monochrome dark instrument palette in both.

| Filename family | What it shows |
|---|---|
| `landing-*` | One-screen desktop introduction and four tiles; phone reading order. `graph`, `composition`, and `results` capture the lower phone tiles. |
| `compare-*` | Existing browser bench, recorded curves, complete phone controls, and runs. `compare-groups-*` shows the recorded dimension ladder; `compare-characters-*` shows the supplied-feature experiment. |
| `explore-cubic-*` | Linked tensor and hypergraph; phone caption and reflowed controls. |
| `explore-diagrams-*` | Every-token computation; `expanded` captures the second phone pane and its diagram. |
| `explore-newton-*` | Recorded character discovery; `inspector` captures arity ablations, the table and provenance. |
| `explore-groups-*` | Learned versus computed A5 rotations, all 60 elements, and the order demo. `ideal`, `motion`, `order-start`, `order-first`, `order-final`, and `inspector` cover the switches, transitions and measurement notes. |
| `learn-*` | Course opening and every new group/composition chapter. See [learn-review.md](learn-review.md) for chapter-by-chapter descriptions. |
| `report-*` | Paper opening and named section anchors. `fig-characters` and `fig-ladder` show the two result figures. `table1`–`table6` cover native tasks, language, supplied characters, groups, learned representations and swap programs. `computation` and `proof1`–`proof3` show expanded details. |

`-frame2` is a second frame about one second later. For interactive motion, `-motion`
shows the transition and `-frame2` its settled state. The group lab uses
`-motion-frame2` for its second transition frame.

The review opened the images, corrected problems, rebuilt, and re-shot the affected
views. Fixes include mobile report tables, theorem provenance spacing, triangle
outlines and label motion, the mobile accuracy ladder, icosahedron caption clearance,
diagram-pane overflow, cubic captions and controls, Compare controls and curve
contrast, full landing legend names, and hypergraph labels leaking above navigation.
The final audits report no browser errors or horizontal page overflow. Report tables
fit within the phone text column; Learn figure bounds include their captions.

To reproduce, run `pnpm build`, then `node scripts/serve-story.mjs` in another terminal.
From the repository root, run the capture scripts:

```sh
node scripts/capture-story.mjs
node scripts/capture-details.mjs
node scripts/capture-learn.mjs
node scripts/capture-report.mjs
node scripts/capture-report-details.mjs
node scripts/capture-groups.mjs
```

The `*-audit.json` files record viewport geometry and runtime checks. The visual
review accompanies those checks; it is not inferred solely from them.

`training-smoke.json` records a real one-layer baseline training for ten WASM steps,
hovering the loss chart, then pausing with no errors. `compare-transport-mobile-*`
shows its final control layout. `base-path-smoke.json` checks all eight routes,
navigation and the A5 recording after a separate `BASE_PATH=/polyformer pnpm build`,
using `BASE_PATH=/polyformer PORT=4182 node scripts/serve-story.mjs`.
