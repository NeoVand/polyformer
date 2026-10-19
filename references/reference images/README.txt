POLYFORMER — AUDITED UI REFERENCE IMAGES

This folder contains the ten revised dark UI concepts from round 2.
All images were edited with the built-in image generation tool, visually
reinspected after editing, and copied here from the reviewed outputs.

FILES
11  Linked tensor lab
    11-linked-tensor-lab.png

12  Role-aware hypergraph
    12-role-aware-hypergraph.png

13  Attention map atlas
    13-attention-map-atlas.png

14  Role swap experiment
    14-role-swap-experiment.png

15  Value flow studio
    15-value-flow-studio.png

16  Projection map wall
    16-projection-map-wall.png

17  Dark comparison bench
    17-dark-comparison-bench.png

18  Tensor tomography
    18-tensor-tomography.png

19  Feature interaction lens
    19-feature-interaction-lens.png

20  Research cockpit
    20-research-cockpit.png

AUDIT RESULTS
The review corrected:
- Scalar, selected-vector, matrix-slice, and full-tensor dimension mixups.
- False dependencies between attention scores and value composition.
- Missing normalization/aggregation connections and incorrect operators.
- Full-output labels applied to individual weighted pair contributions.
- Contradictory indices, duplicate query labels, and faulty numeric rulers.
- Incorrect displayed feature products and mismatched feature previews.

Core notation retained:
A_ijk = <Q_i, K^1_j ⊙ K^2_k>
D_jk = V^1_j ⊙ V^2_k
Y_i = sum_(j,k) P_ijk D_jk

A_ijk and P_ijk are scalars for one triple. D_jk is a feature vector.
The full A and P tensors have shape n × n × n.
The full D tensor has shape n × n × d_v.
D[:,:,c] and P[i,:,:] are two-dimensional slices.
Cubic normalization is left generic rather than imposing an unchosen axis
or scaling convention.

The role-swap concept compares ordered pair contributions. Separate
role-specific projections can distinguish (j,k) and (k,j); elementwise
multiplication itself remains commutative. This is not a theorem or a
measured comparison against another architecture.

VALIDATION AND SCOPE
No serious remaining mathematical-label or dataflow bloopers were
identified in the final visual review. The PNG copies match the reviewed
sources byte for byte. All ten are native 1672 × 941 PNGs.

These are UI design references. Heatmap fields and voxel intensities are
schematic artwork, not computed experimental data. Concept 19 contains an
explicit, checked binary Hadamard product and a 0.25 weighted contribution.
No benchmark or superiority claim is implied by the images.

REPRODUCTION RECORDS
_audit/round-02-generation-prompts.txt contains the original generation
prompts and provenance. The other _audit text files contain the actual
repair prompts, findings, intermediate paths, and final source paths.
The numbered PNGs in this folder are the selected final versions.

