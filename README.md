# Polyformer

Cubic polyattention, trained live in the browser. Each query scores every ordered pair of other
tokens with one trilinear product,

```
A_ijk = <Q_i, K1_j ⊙ K2_k>,   P = softmax over (j, k),   Y_i = Σ_jk P_ijk (V1_j ⊙ V2_k)
```

and the app compares it with standard, tree (Columbia) and Strassen attention on SET, a task whose
rule is a genuine three-way interaction. Everything runs client-side: jax-js trains the models in a
Web Worker on WebGPU, falling back to WebAssembly.

## Pages

- **Compare** (`/compare`): the SET bench. Five models, identical batches, live accuracy and loss
  curves, per-model parameters, FLOPs and step time, deterministic seeds.
- **Explore** (`/explore`): the linked tensor lab for the trained cubic model: voxel cube of P,
  hypergraph of the layout, query slices, and the pair moment `M_i = V1ᵀ P_i V2`.
- **Learn** (`/learn`): the derivation, from pairwise attention to the coupling barrier and SET as
  Match3 over Z₃⁴.
- **Notes** (`/notes`): what the bench shows, related work, how it runs.

## Develop

```sh
pnpm install
pnpm dev          # http://localhost:5173
pnpm check        # svelte-check + TypeScript
pnpm lint         # prettier + eslint
pnpm test:unit -- --run
pnpm build && pnpm preview
```

Append `?backend=wasm` to force the WebAssembly backend.

## Layout

- `src/lib/set/`: SET deck, layouts, labels and encoding.
- `src/lib/model/operators/`: attention operators. A new operator implements `AttentionOperator`
  and is registered in `operators/index.ts`; the block, optimizer, worker and UI pick it up.
- `src/lib/model/`: transformer, fused AdamW step, brute-force references for tests.
- `src/lib/engine/`: training worker, RPC client and the session-wide bench state.
- `src/lib/ui/`, `src/lib/explore/`: components and read-outs.
