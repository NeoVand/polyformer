# Stage-2 language planning handoff

The implementation and validation are local only. They do not import Modal or launch work.
The planner lives below `research/analysis/`, so it does not change the frozen top-level
`research/*.py` source map. No executable language plan has been frozen.

Paths below are relative to the worktree:

- `research/analysis/beyond_language_protocol.py`: planner, validation-only rate selector, final-block exporter.
- `research/analysis/test_beyond_language_protocol.py`: 20 CPU tests.
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
All arms receive the ceiling of one common training-FLOP target, with less than one update excess.
Both GDN1 and DP4 receive all three final seeds. All earlier seed-block jobs must be terminal before
exporting the next block. Failures remain failures; a failed comparator cannot satisfy the headline.

Stage-1 closure must contain all passed candidates and no pending/integrity-invalid candidate.
An explicit audited unconfirmed closure can retain numerical failures, reference-floor failures, or
budget deferrals without advancing that candidate. The plan copies closed candidate statuses and
budget-deferral provenance; it never reclassifies Stage-1 outcomes.

The plan freezes every top-level research Python hash, all five model hashes, the exact full argparse
configuration, JAX/Optax/NumPy versions, Section5 registration hash, compute counters, timeouts,
Stage-1 closure hash, reporting bridge hash, and planner hash. Result selection checks job, manifest,
source, runtime, configuration, completed steps, tokens, FLOPs and final raw validation identity.
It allows BEYOND Log updates outside Section5; a Section5 change invalidates exports.

## Freeze after Stage1 and the reporting amendment

Commit the planner, the reporting amendment, the Stage-1 closure artifact, the source bridge and
the Section5 registration before freezing. Keep the planner in its nested analysis location.
It hashes all top-level research Python files and separately records its own source hash.

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

B/C plus five controls: $76.24 forecast including $2.326004 settled language pilots;
$98.36 sum of all timeout reservations. A/B/C plus five controls: $92.15 forecast,
$119.61 sum of timeout reservations, so actual settlement must release reservations between batches.
Neither estimate authorizes exceeding the $100 language cap. All cases require the runner's ledger
check at launch, at most eight globally active jobs, and no budget transfers.

Forecasts include a 15% convolution runtime allowance, compilation allowance, final evaluation,
checkpoint and candidate-ablation allowance, 30% timeout headroom rounded to100 seconds, and
the runner's152-second resource overhead per job. The final write-up should report actual measured
runtime and ledger estimates, not replace them with these forecasts.
