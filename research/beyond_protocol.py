"""Plan BEYOND Stage 1 without launching work or reading test scores.

Examples (outputs are ordinary job lists accepted by beyond_modal.py plan):
    python research/beyond_protocol.py initial --output /tmp/initial.json
    python research/beyond_protocol.py alternates --manifest main --output /tmp/alt.json
    python research/beyond_protocol.py select --manifest main --manifest alternate \
        --output /tmp/selected.json
    python research/beyond_protocol.py confirm --selection /tmp/selected.json \
        --arm references --output /tmp/references.json
    python research/beyond_protocol.py confirm --selection /tmp/selected.json \
        --arm B --seed 1 --output /tmp/b-seed1.json
    python research/beyond_protocol.py descriptive --output /tmp/descriptive.json
    python research/beyond_protocol.py protocol --output /tmp/protocol.json
    python research/beyond_protocol.py self-test
    python research/beyond_protocol.py verify-costs

The planner is standard-library-only except the explicit verify-costs command,
which checks the frozen table against the live JAX model counter. It reserves
no money and imports no Modal client. The launcher's $25 screen ledger cap is
authoritative. Candidates that lack confirmations remain unconfirmed.
"""

import argparse
import hashlib
import json
import math
import pathlib
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
EPS = 1e-12
ARMS = ("S", "P", "A", "B", "C", "prefix", "GDN1", "DP4")
PRIORITY = ("B", "C", "A")
WORD_REFERENCES = ("prefix", "GDN1", "DP4")
MODEL_SOURCES = ("lm.py", "beyond_layers.py", "beyond_diag.py", "diag.py", "groups.py")
PRIMARY_CELLS = (
    ("wp_s5_16", 1), ("wp_a5_16", 1),
    ("mqar_small", 2), ("induction_small", 2),
    ("wp_s5_16", 2), ("wp_a5_16", 2),
)
DESCRIPTIVE_CELLS = (
    ("mqar_small", 1), ("induction_small", 1),
    ("gmatch_a5_causal", 1), ("gmatch_a5_causal", 2),
    ("regression", 1), ("regression", 2),
)
# B's exact forward FLOPs/token at the registered width, including the
# continuous regression adapter. Every arm receives this same total budget.
REFERENCE_FPT = {
    "mqar_small": {1: 614929.6875, 2: 1164323.375},
    "induction_small": {1: 582161.6875, 2: 1131555.375},
    "wp_a5_16": {1: 506060.23529411765, 2: 996504.4705882353},
    "wp_s5_16": {1: 521420.23529411765, 2: 1011864.4705882353},
    "gmatch_a5_causal": {1: 506060.23529411765, 2: 996504.4705882353},
    "regression": {1: 491483.29411764705, 2: 981927.5294117647},
}
ARM_SPECS = {
    "S": ("gpt", {"qkv_conv": 3}),
    "P": ("plx", {"qkv_conv": 3}),
    "A": ("beyond_a", {"qkv_conv": 3, "group_init": "random"}),
    "B": ("beyond_b", {"qkv_conv": 3, "group_init": "random"}),
    "C": ("beyond_c", {"qkv_conv": 3, "group_init": "random"}),
    "prefix": ("prefix", {"qkv_conv": 0, "group_init": "random"}),
    "GDN1": ("gated_delta", {"qkv_conv": 0, "nh": 1, "beta_max": 1.0,
                             "delta_unroll": 4, "delta_chunk": 0}),
    "DP4": ("gated_delta", {"qkv_conv": 0, "nh": 4, "beta_max": 2.0,
                            "delta_unroll": 4, "delta_chunk": 0}),
    "LLA": ("lla", {"qkv_conv": 0}),
}
COMMON_SETTINGS = {
    "gdim": 5, "gheads": 4, "group_nh": 4, "group_order": 2,
    "branch_scale": 0.1, "conv_width": 4,
    "delta_key_ratio": 0.75, "delta_v_expand": 2.0,
}
PROTOCOL = {
    "name": "beyond-stage1-adaptive-v1", "schema": 1,
    "d": 128, "heads": 4, "mlp": 512, "batch": 64, "opt": "muon", "wd": 0.1,
    "reference_steps": 6000, "reference_arm": "B",
    "reference_fpt": REFERENCE_FPT, "common_settings": COMMON_SETTINGS,
    "arms": ARM_SPECS, "primary_cells": PRIMARY_CELLS,
    "descriptive_cells": DESCRIPTIVE_CELLS,
    "first_lr": 0.004, "word_alternate_lr": 0.002, "retrieval_alternate_lr": 0.008,
    "saturation_validation": 0.97, "threshold_tolerance": EPS,
    "retrieval_threshold": 0.90, "word_threshold": 0.95, "reference_margin": 0.03,
    "evalset": 1024, "testset": 2048, "evals": 6,
    "confirm_seeds": [1, 2, 3], "confirmation_priority": PRIORITY,
    "execution_priority": ["primary_and_required_alternates", "shared_references",
                           "B_confirmations", "48_mandatory_descriptives",
                           "C_confirmations", "A_confirmations", "optional_LLA"],
    "reference_tie_priority": WORD_REFERENCES,
    "budget": "Launcher enforces settled + outstanding + new reservations <= $25. "
              "No development-budget transfer; uncompleted confirmations remain unconfirmed.",
    "selection": "Final validation only; never test or intermediate curves. First rate .004; "
                 "eligible alternate only below .97 or after a terminal invalid first run. "
                 "Select highest final validation among authorized executed rates, lower LR on ties.",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


PROTOCOL_ID = digest(PROTOCOL)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def at_least(value, threshold):
    return finite(value) and value >= threshold - EPS


def cell_key(task, depth, arm=None):
    return f"{task}/L{depth}" + (f"/{arm}" if arm else "")


def is_word(task):
    return task.startswith("wp_")


def primary_arms(task):
    return ARMS if is_word(task) else tuple(a for a in ARMS if a != "prefix")


def alternate_eligible(task, arm):
    return arm not in ("S", "P") if is_word(task) else arm != "prefix"


def alternate_rate(task):
    return 0.002 if is_word(task) else 0.008


def make_job(task, depth, arm, lr=0.004, seed=0, phase="initial"):
    arch, arm_settings = ARM_SPECS[arm]
    settings = {**COMMON_SETTINGS, **arm_settings}
    target = REFERENCE_FPT[task][depth]
    argv = [
        "--task", task, "--arch", arch, "--layers", str(depth),
        "--d", "128", "--heads", "4", "--mlp", "512", "--chart", "8",
        "--pos", "0" if is_word(task) or task in ("regression", "gmatch_a5_causal") else "1",
        "--seed", str(seed), "--steps", "6000", "--target-fpt", repr(target),
        "--batch", "64", "--lr", repr(lr), "--opt", "muon", "--wd", "0.1",
        "--evalset", "1024", "--testset", "2048", "--evalbatch", "128",
        "--evals", "6", "--progress",
    ]
    for name, value in sorted(settings.items()):
        argv.extend(("--set", name + "=" + json.dumps(value, separators=(",", ":"))))
    return {
        "script": "beyond_diag.py", "gpu": "L4", "max_seconds": 600, "attempt": 0,
        "argv": argv,
        "protocol": {"id": PROTOCOL_ID, "phase": phase, "task": task, "layers": depth,
                     "arm": arm, "seed": seed, "lr": lr, "target_fpt": target,
                     "identity_settings": settings},
    }


def initial_jobs():
    return [make_job(t, d, a) for t, d in PRIMARY_CELLS for a in primary_arms(t)]


def descriptive_jobs(optional_lla=False):
    if optional_lla:
        return [make_job("regression", d, "LLA", phase="optional_descriptive") for d in (1, 2)]
    return [make_job(t, d, a, phase="descriptive") for t, d in DESCRIPTIVE_CELLS for a in ARMS]


def parse_argv(argv):
    values, settings = {}, {}
    i = 0
    while i < len(argv):
        flag = argv[i]
        if not flag.startswith("--"):
            raise ValueError(f"unexpected argument {flag!r}")
        name = flag[2:].replace("-", "_")
        raw = True
        if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            i += 1
            raw = argv[i]
        if name == "set":
            key, sep, val = str(raw).partition("=")
            if not sep or key in settings:
                raise ValueError(f"invalid or repeated setting {raw!r}")
            try:
                settings[key] = json.loads(val)
            except json.JSONDecodeError:
                settings[key] = val
        else:
            if name in values:
                raise ValueError(f"repeated argument {name}")
            try:
                values[name] = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                values[name] = raw
        i += 1
    return values, settings


def identify_job(job):
    """Trust the actual argv/config identity, not a human-facing arm label."""
    args, settings = parse_argv(job["argv"])
    matches = [a for a, (arch, extra) in ARM_SPECS.items()
               if args.get("arch") == arch and all(settings.get(k) == v for k, v in extra.items())]
    if len(matches) != 1:
        raise ValueError("job architecture/variant is not uniquely registered")
    arm = matches[0]
    task, depth = args.get("task"), args.get("layers")
    if (task, depth) not in PRIMARY_CELLS or arm not in primary_arms(task):
        raise ValueError("selection accepts only registered primary cells")
    lr = args.get("lr")
    if args.get("seed") != 0 or lr not in (0.004, alternate_rate(task)):
        raise ValueError("selection accepts only registered seed0 rates")
    expected, expected_settings = parse_argv(make_job(task, depth, arm, lr)["argv"])
    if args != expected or settings != expected_settings:
        raise ValueError("job differs from registered identity, budget, optimizer or evaluation settings")
    if job.get("script", "beyond_diag.py") != "beyond_diag.py" or job.get("attempt", 0) != 0:
        raise ValueError("unregistered script or retry attempt")
    if job.get("protocol", {}).get("id", PROTOCOL_ID) != PROTOCOL_ID:
        raise ValueError("job belongs to a different protocol")
    return task, depth, arm, lr, args, settings


def make_record(job, result=None, ledger=None):
    task, depth, arm, lr, args, settings = identify_job(job)
    ledger = ledger or {}
    score, error = None, ""
    status = str(ledger.get("status", "pending")).upper()
    if result is not None:
        if not isinstance(result, dict):
            raise ValueError("result must be a JSON object")
        error = str(result.get("error") or result.get("failure") or "")
        if result.get("error"):
            status = "TIMEOUT" if any(s in error.lower() for s in ("timeout", "timed out", "exceeded")) else "ERROR"
        elif result.get("failure") or result.get("nonfinite_fields"):
            status = "INVALID"
        else:
            cfg = result.get("config", {})
            required = {**settings, "arch": args["arch"], "d": 128, "heads": 4,
                        "layers": depth, "mlp": 512, "pos": args["pos"]}
            if any(cfg.get(k) != v for k, v in required.items()):
                raise ValueError(f"{job.get('id', '?')}: result config disagrees with registered job")
            metric = "bal_late" if is_word(task) else "acc"
            validation = result.get("validation")
            score = validation.get(metric) if isinstance(validation, dict) else None
            status = "COMPLETE" if finite(score) and 0 <= score <= 1 else "INVALID"
            if status == "INVALID":
                error = "missing, nonfinite or out-of-range final validation"
        # The held-out test and intermediate curve are intentionally never read.
    elif status in ("COMPLETE", "ERROR", "FAIL", "TIMEOUT"):
        status, error = "INVALID", "terminal ledger entry has no result artifact"
    return {"task": task, "layers": depth, "arm": arm, "lr": lr, "status": status,
            "score": score if status == "COMPLETE" else None, "error": error,
            "job_id": job.get("id", digest(job["argv"])[:24]), "argv": job["argv"],
            "identity_settings": settings}


def load_records(manifests, results_dir=ROOT / "results/beyond_runs",
                 ledger_path=ROOT / "results/beyond_budget.json"):
    ledger = json.loads(pathlib.Path(ledger_path).read_text()) if pathlib.Path(ledger_path).exists() else {}
    records, seen, source_identity = [], set(), None
    for name in manifests:
        path = pathlib.Path(name)
        if not path.exists():
            path = ROOT / "manifests" / (path.stem + ".json")
        manifest = json.loads(path.read_text())
        if "sha256" in manifest:
            content = {k: v for k, v in manifest.items() if k != "sha256"}
            if digest(content) != manifest["sha256"]:
                raise ValueError(f"modified immutable manifest: {path}")
        sources = {k: manifest.get("source_hashes", {}).get(k) for k in MODEL_SOURCES}
        if not all(sources.values()):
            raise ValueError(f"missing model-source identity in {path}")
        if source_identity is not None and sources != source_identity:
            raise ValueError("cannot select across different model/data source versions")
        source_identity = sources
        for job in manifest["jobs"]:
            if job["id"] in seen:
                continue
            seen.add(job["id"])
            result_path = pathlib.Path(results_dir) / (job["id"] + ".json")
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            records.append(make_record(job, result, ledger.get("jobs", {}).get(job["id"], {})))
    return records, source_identity or {}


def terminal(record):
    return record is not None and record["status"] in ("COMPLETE", "INVALID", "ERROR", "TIMEOUT", "FAIL")


def index_records(records):
    indexed = {}
    for r in records:
        key = (r["task"], r["layers"], r["arm"], r["lr"])
        if key in indexed and indexed[key]["job_id"] != r["job_id"]:
            raise ValueError(f"duplicate experimental identity: {key}")
        indexed[key] = r
    return indexed


def needs_alternate(first):
    return terminal(first) and (first["status"] != "COMPLETE" or not at_least(first["score"], 0.97))


def alternate_jobs(records):
    indexed, jobs = index_records(records), []
    for task, depth in PRIMARY_CELLS:
        for arm in primary_arms(task):
            if not alternate_eligible(task, arm):
                continue
            first = indexed.get((task, depth, arm, 0.004))
            rate = alternate_rate(task)
            if needs_alternate(first) and (task, depth, arm, rate) not in indexed:
                jobs.append(make_job(task, depth, arm, rate, phase="alternate"))
    return jobs


def choose(records):
    """Wait for each required alternate; never choose from incomplete tuning."""
    indexed, selected = index_records(records), {}
    for task, depth in PRIMARY_CELLS:
        for arm in primary_arms(task):
            first = indexed.get((task, depth, arm, 0.004))
            alt = indexed.get((task, depth, arm, alternate_rate(task)))
            item = {"task": task, "layers": depth, "arm": arm, "state": "pending_first",
                    "selected": None}
            if terminal(first):
                candidates = [first]
                required = alternate_eligible(task, arm) and needs_alternate(first)
                if required and not terminal(alt):
                    item["state"] = "pending_alternate"
                else:
                    if required:
                        candidates.append(alt)
                    elif alt is not None:
                        item["unexpected_alternate_ignored"] = alt["job_id"]
                    valid = [r for r in candidates if r["status"] == "COMPLETE"]
                    if valid:
                        # Exact validation ties prefer the lower numerical rate.
                        item.update(state="ready", selected=min(valid, key=lambda r: (-r["score"], r["lr"])))
                    else:
                        item["state"] = "failed"
            selected[cell_key(task, depth, arm)] = item
    return selected


def select(records, source_identity=None):
    selected = choose(records)
    references, gates = {}, {}
    for task, depth in PRIMARY_CELLS:
        arms = WORD_REFERENCES if is_word(task) else ("S",)
        options = [selected[cell_key(task, depth, arm)] for arm in arms]
        ready = [o["selected"] for o in options if o["state"] == "ready"]
        if any(o["state"].startswith("pending") for o in options):
            reference = {"state": "pending", "selected": None}
        elif not ready:
            reference = {"state": "failed", "selected": None}
        else:
            best = min(ready, key=lambda r: (-r["score"], arms.index(r["arm"])))
            reference = {"state": "ready", "selected": best}
        references[cell_key(task, depth)] = reference
    for arm in PRIORITY:
        cells = {}
        for task, depth in PRIMARY_CELLS:
            candidate = selected[cell_key(task, depth, arm)]
            reference = references[cell_key(task, depth)]
            threshold = 0.95 if is_word(task) else 0.90
            status = "pending"
            score = candidate["selected"]["score"] if candidate["selected"] else None
            ref_score = reference["selected"]["score"] if reference["selected"] else None
            if candidate["state"] == "failed":
                status = "fail"
            elif candidate["state"] == "ready" and not at_least(score, threshold):
                status = "fail"
            elif reference["state"] == "failed":
                status = "no_positive_control"
            elif reference["state"] == "ready" and not at_least(ref_score, threshold):
                status = "no_positive_control"
            elif candidate["state"] == reference["state"] == "ready":
                status = "pass" if at_least(score + 0.03, ref_score) else "fail"
            cells[cell_key(task, depth)] = {
                "status": status, "validation": score, "reference_validation": ref_score,
                "absolute_threshold": threshold, "maximum_reference_gap": 0.03,
                "reference_arm": reference["selected"]["arm"] if reference["selected"] else None,
            }
        statuses = [c["status"] for c in cells.values()]
        state = ("rejected" if "fail" in statuses else "screen_passed_unconfirmed"
                 if all(s == "pass" for s in statuses) else "pending")
        gates[arm] = {"status": state, "cells": cells}
    report = {"protocol": PROTOCOL, "protocol_id": PROTOCOL_ID,
              "model_source_hashes": source_identity or {}, "selected": selected,
              "references": references, "seed0_gates": gates,
              "survivors": [a for a in PRIORITY if gates[a]["status"] == "screen_passed_unconfirmed"],
              "confirmation_status": "unconfirmed; seed0 selection does not establish a three-seed pass"}
    report["sha256"] = digest(report)
    return report


def confirmation_jobs(selection, arm="references", seeds=(1, 2, 3)):
    if selection.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("selection protocol differs from the current registered protocol")
    if "sha256" in selection and digest({k: v for k, v in selection.items() if k != "sha256"}) != selection["sha256"]:
        raise ValueError("selection file changed after rate freezing")
    if not seeds or len(set(seeds)) != len(seeds) or any(s not in (1, 2, 3) for s in seeds):
        raise ValueError("confirmation seeds must be distinct members of 1,2,3")
    survivors = selection["survivors"]
    if arm not in ("references", "all", *PRIORITY):
        raise ValueError("unknown confirmation arm")
    if arm in PRIORITY and arm not in survivors:
        raise ValueError(f"{arm} has not passed all six seed0 primary gates")
    if not survivors:
        return []
    chosen = (["references", *survivors] if arm == "all" else [arm])
    jobs = []
    for who in chosen:
        for task, depth in PRIMARY_CELLS:
            item = (selection["references"][cell_key(task, depth)] if who == "references"
                    else selection["selected"][cell_key(task, depth, who)])
            if item["state"] != "ready":
                raise ValueError("cannot freeze an incomplete selection")
            row = item["selected"]
            for seed in seeds:
                job = make_job(task, depth, row["arm"], row["lr"], seed, phase="confirmation")
                job["protocol"]["frozen_selection_sha256"] = selection.get("sha256")
                job["protocol"]["selected_seed0_job"] = row["job_id"]
                jobs.append(job)
    return jobs


def verify_costs():
    import beyond_diag as bd
    checked = []
    for task, depths in REFERENCE_FPT.items():
        _, context, vocab, pos, _ = bd.TASKS[task]
        for depth, expected in depths.items():
            args, settings = parse_argv(make_job(task, depth, "B")["argv"])
            ns = argparse.Namespace(**args)
            ns.set = list(settings.items())
            cfg = bd.model_config(ns, context, vocab, pos)
            actual = bd.task_flops(cfg, context, task == "regression")
            if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-7):
                raise AssertionError(f"frozen FLOP target drifted: {task} L{depth}: {actual} != {expected}")
            for arm in ARMS:
                a, settings = parse_argv(make_job(task, depth, arm)["argv"])
                ns = argparse.Namespace(**a)
                ns.set = list(settings.items())
                cfg = bd.model_config(ns, context, vocab, pos)
                steps, own, _ = bd.compute_budget(cfg, context, 6000, [], task == "regression", expected)
                assert steps * own <= 6000 * expected + 1e-5
                assert 6000 * expected - steps * own < own + 1e-5
            checked.append(cell_key(task, depth))
    return {"verified_reference_cells": checked, "variant_budget_checks": len(checked) * len(ARMS)}


def self_test():
    def result(job, score=0.99, **extra):
        args, settings = parse_argv(job["argv"])
        cfg = {**settings, **{k: args[k] for k in ("arch", "d", "heads", "layers", "mlp", "pos")}}
        return {"config": cfg, "validation": {"acc": score, "bal_late": score}, **extra}

    jobs = initial_jobs()
    assert len(jobs) == 46 and len(descriptive_jobs()) == 48 and len(descriptive_jobs(True)) == 2
    records = [make_record(j, result(j)) for j in jobs]
    baseline = select(records)
    assert baseline["survivors"] == list(PRIORITY)
    assert len(confirmation_jobs(baseline)) == 18
    assert len(confirmation_jobs(baseline, "B")) == 18
    assert len(confirmation_jobs(baseline, "all")) == 72
    assert not alternate_jobs(records)
    # Held-out test values, including NaN, cannot enter any decision.
    changed = [make_record(j, result(j, test={"acc": float("nan"), "bal_late": -100})) for j in jobs]
    assert select(changed) == baseline
    task, depth = PRIMARY_CELLS[0]
    first = make_job(task, depth, "B")
    bad = make_record(first, result(first, float("nan")))
    assert bad["status"] == "INVALID" and len(alternate_jobs([bad])) == 1
    assert alternate_jobs([make_record(first)]) == []
    alt = make_job(task, depth, "B", 0.002, phase="alternate")
    before = make_record(first, result(first, 0.96, test={"bal_late": 1}))
    after = make_record(alt, result(alt, 0.99, test={"bal_late": 0}))
    key = cell_key(task, depth, "B")
    assert choose([before])[key]["state"] == "pending_alternate"
    assert choose([before, after])[key]["selected"]["lr"] == 0.002
    tied = make_record(alt, result(alt, 0.96))
    assert choose([before, tied])[key]["selected"]["lr"] == 0.002
    assert alternate_jobs([bad, make_record(alt)]) == []  # no duplicate dispatch
    saturated = make_record(first, result(first, 0.97 - EPS / 2))
    assert not alternate_jobs([saturated])
    assert at_least(0.95 - EPS / 2, 0.95) and not at_least(0.95 - 1e-8, 0.95)
    assert at_least(0.97 + 0.03, 1.0)
    # Actual nh/beta settings distinguish the two matrix controls.
    gd, dp = make_job(task, depth, "GDN1"), make_job(task, depth, "DP4")
    gd["protocol"]["arm"] = "DP4"
    assert identify_job(gd)[2] == "GDN1" and identify_job(dp)[2] == "DP4"
    wrong_cfg = result(dp)
    wrong_cfg["config"]["nh"] = 1
    try:
        make_record(dp, wrong_cfg)
    except ValueError:
        pass
    else:
        raise AssertionError("variant/config mismatch accepted")
    missing = [r for r in records if not (r["arm"] == "B" and (r["task"], r["layers"]) == PRIMARY_CELLS[-1])]
    assert "B" not in select(missing)["survivors"]  # all six gates required
    mixed = [r for r in records if not (r["arm"] == "B" and (r["task"], r["layers"]) == (task, depth))]
    rejected = select(mixed + [make_record(first, result(first, 0.50)), make_record(alt, result(alt, 0.51))])
    assert rejected["seed0_gates"]["B"]["status"] == "rejected"
    try:
        confirmation_jobs(rejected, "B")
    except ValueError:
        pass
    else:
        raise AssertionError("rejected candidate confirmed")
    # A different DP4 score must change the selected reference without merging variants.
    reference_rows = [r for r in records if not (r["arm"] == "DP4" and (r["task"], r["layers"]) == (task, depth))]
    reference_rows.append(make_record(dp, result(dp, 1.0)))
    assert select(reference_rows)["references"][cell_key(task, depth)]["selected"]["arm"] == "DP4"
    # New report-only config/output fields do not alter registered identity.
    richer = result(first, component_parameters={"attention": 123})
    richer["config"]["report_only_metadata"] = "permitted"
    assert make_record(first, richer)["status"] == "COMPLETE"
    pilot = make_job(task, depth, "B")
    index = pilot["argv"].index("--target-fpt")
    del pilot["argv"][index:index + 2]
    try:
        identify_job(pilot)
    except ValueError:
        pass
    else:
        raise AssertionError("unmatched pilot accepted as main-grid evidence")
    # Exercise JSON round-tripping and the immutable-manifest/result loader.
    with tempfile.TemporaryDirectory() as directory:
        folder = pathlib.Path(directory)
        outputs = folder / "results"
        outputs.mkdir()
        job = make_job(task, depth, "B")
        job["id"] = digest(job["argv"])[:24]
        sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in MODEL_SOURCES}
        manifest = {"name": "synthetic", "source_hashes": sources, "jobs": [job]}
        manifest["sha256"] = digest(manifest)
        path = folder / "manifest.json"
        path.write_text(json.dumps(manifest))
        (outputs / (job["id"] + ".json")).write_text(json.dumps({"error": "subprocess exceeded 600 seconds"}))
        loaded, identity = load_records([path], outputs, folder / "missing-ledger.json")
        assert identity == sources and loaded[0]["status"] == "TIMEOUT"
        assert len(alternate_jobs(loaded)) == 1
        frozen = json.loads(json.dumps(baseline))
        assert len(confirmation_jobs(frozen, "B", (1,))) == 6
        manifest["jobs"][0]["argv"][0] = "modified"
        path.write_text(json.dumps(manifest))
        try:
            load_records([path], outputs, folder / "missing-ledger.json")
        except ValueError as error:
            assert "modified immutable" in str(error)
        else:
            raise AssertionError("modified manifest accepted")
    return {"passed": True, "checks": [
        "46/48/2 job counts", "18 shared confirmations", "test-score independence",
        "invalid first triggers alternate", "pending is not invalid", "no duplicate alternate",
        "final-validation selection and lower-rate ties", "floating thresholds",
        "distinct nh/beta variants and config rejection", "all six gates required",
        "failed candidate cannot confirm", "strongest reference chosen",
        "extra report metadata accepted", "unmatched pilots rejected",
        "manifest/result/selection JSON roundtrip", "timeouts trigger alternate",
        "immutable manifests checked", "confirmation seed subsets",
    ]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("protocol", "initial", "descriptive", "self-test", "verify-costs"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--output")
        if name == "descriptive":
            cmd.add_argument("--optional-lla", action="store_true", help="emit only the two optional LLA jobs")
    for name in ("alternates", "select"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--manifest", action="append", required=True)
        cmd.add_argument("--results-dir", type=pathlib.Path, default=ROOT / "results/beyond_runs")
        cmd.add_argument("--ledger", type=pathlib.Path, default=ROOT / "results/beyond_budget.json")
        cmd.add_argument("--output")
    cmd = sub.add_parser("confirm")
    cmd.add_argument("--selection", required=True, type=pathlib.Path)
    cmd.add_argument("--arm", choices=("references", "all", *PRIORITY), default="references")
    cmd.add_argument("--seed", action="append", type=int)
    cmd.add_argument("--output")
    args = ap.parse_args()
    if args.command == "protocol":
        out = {"protocol_id": PROTOCOL_ID, **PROTOCOL}
    elif args.command == "initial":
        out = initial_jobs()
    elif args.command == "descriptive":
        out = descriptive_jobs(args.optional_lla)
    elif args.command == "self-test":
        out = self_test()
    elif args.command == "verify-costs":
        out = verify_costs()
    elif args.command in ("alternates", "select"):
        records, sources = load_records(args.manifest, args.results_dir, args.ledger)
        out = alternate_jobs(records) if args.command == "alternates" else select(records, sources)
    else:
        selection = json.loads(args.selection.read_text())
        for filename, expected in selection.get("model_source_hashes", {}).items():
            if hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() != expected:
                raise ValueError(f"model/data source changed since rate selection: {filename}")
        out = confirmation_jobs(selection, args.arm, tuple(args.seed or (1, 2, 3)))
    text = json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(text)
        print(json.dumps({"output": str(args.output), "jobs": len(out) if isinstance(out, list) else None,
                          "protocol_id": PROTOCOL_ID, "launched": False}))
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
