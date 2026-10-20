# Stage-2 language planning handoff

The planner and its tests are local only and do not launch work. The separate dataset helper
uses Modal's read-only Volume download API from the local process; it creates no App or Function.
The planner lives below `research/analysis/`, so it does not change the frozen top-level
`research/*.py` source map. No executable language plan has been frozen.

Paths below are relative to the worktree:

- `research/analysis/beyond_language_protocol.py`: planner, validation-only rate selector, final-block exporter.
- `research/analysis/test_beyond_language_protocol.py`: 30 CPU tests, including all seven survivor subsets and dataset integrity.
- `research/analysis/beyond_dataset_fingerprint.py`: replayable streaming token-file fingerprint.
- `research/results/beyond_language_planning/dataset.json`: pre-quality corpus fingerprint and provenance limits.
- `research/results/beyond_language_planning/proof.json`: artifact hashes, test output and portability checks.
- `research/results/beyond_language_planning/tables.md`: B/C and A/B/C draft planning tables.
- `research/results/beyond_language_planning/budget.json`: timing inputs and previously settled language spend.

Use a Python environment containing the pinned research dependencies. From the worktree, run
`python research/analysis/test_beyond_language_protocol.py`; from the research directory, run
`python analysis/test_beyond_language_protocol.py`. Tests resolve sibling sources and fixtures from
their own location. Planner commands detect the research directory from either working directory;
`--research-root PATH` can select it explicitly. Paths supplied as arguments are relative to the
current working directory.

## Protocol behavior

Every included arm receives fresh seed-0 rate trials at .002/.004/.008 for 3051 updates, vseqs1024,
vbig0, warmup305 and 8 evaluation marks. Every trial must be terminal before selection. Only
`val_loss_raw` at the final configured update selects a rate; `curve[-1].val_raw` must match.
Exact ties choose the smaller rate. Failed/nonfinite trials remain in the artifact and cannot win.
No rounded loss, intermediate validation, final held-out loss, test field, or ablation selects rates.

Final seeds are 1/2/3, each with a fresh complete schedule, warmup400, 16 evaluation marks,
vseqs1024/vbig1024 and final checkpoint saving. Candidates additionally run inference ablations.
Candidate schedules use the original common nominal training-FLOP target. Each of the five controls
receives the smallest whole-update count covering every candidate under all four declared arithmetic
conventions. Intentional additional work is separate from ceiling roundoff; only the latter is below
one update. Both GDN1 and DP4 receive all three final seeds. All earlier seed-block jobs must be terminal before
exporting the next block. Failures remain failures; a failed comparator cannot satisfy the headline.

Stage-1 closure must contain all passed candidates and no pending/integrity-invalid candidate.
An explicit audited unconfirmed closure can retain numerical failures, reference-floor failures, or
budget deferrals without advancing that candidate. The plan copies closed candidate statuses and
budget-deferral provenance; it never reclassifies Stage-1 outcomes. The active written-rule policy
must be exactly the prospectively registered policy. The original strict selection is checked at its
registration commit, and full strict-code confirmation outcomes remain alongside the active outcomes.

The plan freezes every top-level research Python hash, all five model hashes, the exact full argparse
configuration, JAX/Optax/NumPy versions, Section5 registration hash, compute counters, timeouts,
Stage-1 closure hash, reporting bridge hash, planner hash, gate-policy adapter hash, and committed dataset evidence.
Result selection checks job, manifest,
source, runtime, configuration, completed steps, tokens, FLOPs and final raw validation identity.
It allows BEYOND Log updates outside Section5; a Section5 change invalidates exports.

## Dataset fingerprint

The completed read-only command was:

```sh
/tmp/beyond-venv/bin/python research/analysis/beyond_dataset_fingerprint.py \
  --out research/results/beyond_language_planning/dataset.json
```

The environment-specific Python path can be replaced with any local Python containing Modal.
No Modal Function was called. The helper streamed 1,504,194,984 bytes in 39.894 seconds and
verified that the file sizes and modification timestamps agreed before and after the read.

| File | Bytes | Tokens | SHA-256 |
| --- | ---: | ---: | --- |
| train.bin | 1,489,165,168 | 744,582,584 | `b5684af6fa868293bf2628c41b08e54ea2a0ef8894f515bab299d17e909cf10b` |
| val.bin | 15,029,816 | 7,514,908 | `5afa5156b009815de51f8b244741fc7ff0bab45fb582ed99ccce5dd2ed0cf0b9` |

The current preparation source selects `HuggingFaceFW/fineweb-edu`,
`sample/10BT/000_00000.parquet`; holds out zero-based document indices divisible by 100;
and applies GPT-2 ordinary tokenization with EOT 50256 appended after each document.
This is evidence of the current source recipe, not proof of the historical preparation invocation.
The original Hugging Face revision, source Parquet digest, and tokenizer build are unknown.
The binary hashes identify the corpus actually present now.

Production `freeze` requires `--dataset-evidence` committed at `--evidence-commit`.
The plan embeds the full evidence, its canonical seal, the file-byte SHA, and a worktree-relative path.
Plan verification, rate selection, final reporting, and exports verify the local bound evidence,
preparation/helper source hashes, and every arm's dataset path. They do not hash the remote files
for every job. Drafts may omit dataset evidence.

Canonical evidence seal: `234bfccad2d94c2cacfa837dc4435e49fe03024954ba0ac8b7a3304c1615ba32`.
File-byte SHA: `8fbe5ba2a626dc61375af5fac0b80992910e6eb1ed6ac91c443fe75036135570`.

After the study, repeat with a new immutable output and compare both files:

```sh
python research/analysis/beyond_dataset_fingerprint.py \
  --compare research/results/beyond_language_planning/dataset.json \
  --out research/results/beyond_language_planning/dataset_final.json
```

This final rehash is planned, not yet performed. A mismatch raises an error. Size/mtime checks
are not an atomic volume snapshot; pre/post matching hashes establish the observed endpoints,
not a claim that every training invocation independently verified its mount.

## Conservative control allowance

Policy ID: `3a340829e3fa07d6808280c240992af63283088ac92a3d68d7935cb7822d0991`.

Let F be the original forward FLOPs/token, N the original training FLOPs/token including the chunk
solve backward surcharge, and H=51,511,296 the vocabulary projection outside the checkpointed blocks.
Let Δ be the registered source-upper forward adjustment: 3,200,904 for either softmax,
3,231,552 for Parallax/B/C, 6,371,040 for A, and zero for either RNN. The A adjustment explicitly
charges its duplicate ordinary value product without assuming compiler sharing.

The four training-work estimates/token are N, N+F−H, N+3Δ, and N+F−H+4Δ.
For each control j, use

`steps_j = ceil(max over candidates i and conventions k of steps_i * W_ik / W_jk)`.

Candidate steps and all rate sweeps retain their original schedules. Every final control has at least
every candidate's total work under each declared convention. The planner uses exact rational
arithmetic and records every per-token count, total, binding requirement, nonnegative slack and
minimal-ceiling witness. Tests independently check 240 dominance inequalities and 35 minimality
witnesses across all seven nonempty candidate subsets.

These estimates cover specified attention and whole-block recomputation sensitivities. They are
not measurements or guarantees of equal hardware-executed GPU FLOPs. The original counter audit
remains available under `proof.json.counter_sensitivity_read_only`; it includes the earlier CSE
estimate for A and must not be confused with the more conservative no-CSE allowance.

## Freeze after Stage1 and the reporting amendment

Commit the planner, the dataset helper/evidence, the reporting amendment, the Stage-1 closure artifact, the source bridge and
the Section5 registration before freezing. Keep the planner in its nested analysis location.
It hashes all top-level research Python files and separately records its own source hash.
Section5 must contain the control-allowance policy ID above before freezing is permitted.

The source bridge is a canonical JSON object sealed with the planner's `seal()` function. It contains:

```json
{
  "schema": "stage2_source_bridge",
  "schema_version": 1,
  "classification": "report_only",
  "audit": {
    "proof_path": "committed/path/to/reporting-proof.json",
    "proof_sha256": "file hash",
    "unchanged_training": true
  },
  "allowed_changed_files": ["lm.py"],
  "before_commit": "full committed Stage1 source SHA",
  "after_commit": "full committed reporting amendment SHA",
  "old_model_source_hashes": {"five exact MODEL_SOURCES": "hashes"},
  "new_model_source_hashes": {"five exact MODEL_SOURCES": "hashes"},
  "diff": "exact output of git diff BEFORE AFTER -- research/lm.py",
  "diff_sha256": "SHA256 of UTF-8 diff bytes",
  "sha256": "canonical seal of all preceding fields"
}
```

The bridge verifier checks both committed source endpoints for every model source and the exact
committed lm.py diff. Only lm.py may differ. The diff hash is the **git diff text** hash, which may
differ from the separately delivered `apply_patch` file hash. Production freeze also requires the
unrounded reporting amendment to be present.

Commands below are templates. Their planning/export steps do not spend money. The bounded runner
still owns every reservation and actual launch; no launch command is included here.

```sh
python research/analysis/beyond_language_protocol.py freeze \
  --confirmation research/results/STAGE1_CLOSURE.json \
  --source-bridge research/results/STAGE2_BRIDGE.json \
  --dataset-evidence research/results/beyond_language_planning/dataset.json \
  --budget research/results/beyond_language_planning/budget.json \
  --evidence-commit HEAD \
  --out research/results/STAGE2_PLAN.json
```

Commit the plan, then export its exact tuning grid:

```sh
python research/analysis/beyond_language_protocol.py export \
  --plan research/results/STAGE2_PLAN.json --plan-commit HEAD \
  --phase tuning --out research/results/STAGE2_TUNING_JOBS.json
python research/beyond_modal.py plan \
  --name beyond_language_tuning --stage language \
  --jobs research/results/STAGE2_TUNING_JOBS.json
```

After all tuning results are terminal, select using all exact tuning manifests (repeat `--manifest`
if the grid was split). A pending invocation prints status and exits2 without creating the immutable
selection file.

```sh
python research/analysis/beyond_language_protocol.py select \
  --plan research/results/STAGE2_PLAN.json --plan-commit HEAD \
  --manifest research/manifests/beyond_language_tuning.json \
  --results-dir research/results/beyond_runs \
  --out research/results/STAGE2_SELECTION.json
```

Commit the selected-rate artifact before exporting seed1:

```sh
python research/analysis/beyond_language_protocol.py export \
  --plan research/results/STAGE2_PLAN.json --plan-commit HEAD \
  --phase final --selection research/results/STAGE2_SELECTION.json \
  --selection-commit HEAD --seed 1 \
  --results-dir research/results/beyond_runs \
  --out research/results/STAGE2_SEED1_JOBS.json
```

Repeat with seed2 and seed3 only after the prior complete block is terminal. Exports include every
registered arm. No rerun, larger timeout, rate extension or dropped comparator is silently generated.

## Budget

B/C plus five controls: $77.09 forecast including $2.326004 settled language pilots;
$99.82 sum of all timeout reservations. A/B/C plus five controls: $94.26 forecast,
$122.17 sum of timeout reservations, so actual settlement must release reservations between batches.
Neither estimate authorizes exceeding the $100 language cap. All cases require the runner's ledger
check at launch, at most eight globally active jobs, and no budget transfers.

The allowance adds $0.853041 forecast/$1.464528 maximum reservations in the B/C case and
$2.117802 forecast/$2.562924 maximum reservations in the A/B/C case. Original nominal-only
scenarios are preserved in budget.json as historical inputs; current scenario forecasts are recorded
separately. The current tables and frozen plan distinguish original updates from added control work.

Forecasts include a 15% convolution runtime allowance, compilation allowance, final evaluation,
checkpoint and candidate-ablation allowance, 30% timeout headroom rounded to100 seconds, and
the runner's152-second resource overhead per job. The final write-up should report actual measured
runtime and ledger estimates, not replace them with these forecasts.
