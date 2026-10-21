"""Tables of LOOPS results from results/loops_runs/*.json, with arm names recovered from argv.

    python research/loops_summary.py            # every run
    python research/loops_summary.py screen     # one manifest
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def flag(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def arm(argv):
    if flag(argv, "--ckpts"):
        return None
    if flag(argv, "--task"):
        sets = [argv[i + 1] for i, a in enumerate(argv) if a == "--set" and argv[i + 1] != "qkv_conv=3"]
        return f"{flag(argv, '--task')} L{flag(argv, '--layers')} " + " ".join(sets)
    a = flag(argv, "--arch")
    if a == "gpt":
        return "abs" if flag(argv, "--qkv_conv") == "3" else "abs_raw"
    if a == "gated_delta":
        return "gdn" if flag(argv, "--nh") == "1" else "deltaproduct"
    if a == "events":
        name = f"events l={flag(argv, '--ev_len', '8')} {flag(argv, '--ev_posenc', 'holo')}"
        ctx = flag(argv, "--ctx", "512")
        return name + (f" ctx{ctx}" if ctx != "512" else "")
    name = flag(argv, "--posenc", "abs")
    if flag(argv, "--forget", "0") == "1":
        name += "+forget"
    if flag(argv, "--vtrans", "0") == "1":
        name += "+vtrans" + (f"{flag(argv, '--vtrans_heads')}h" if flag(argv, "--vtrans_heads", "0") != "0" else "")
    if flag(argv, "--gate_out", "0") == "1":
        name += "+gate"
    if flag(argv, "--vres", "0") == "1":
        name += "+vres"
    ctx = flag(argv, "--ctx", "512")
    if ctx != "512":
        name += f" ctx{ctx}"
    if flag(argv, "--pattern"):
        name = f"hybrid[{flag(argv, '--pattern')}] " + name
    if flag(argv, "--loop_order"):
        name = f"loop[{flag(argv, '--loop_order')}] " + name
    if flag(argv, "--mlp", "2048") != "2048" and flag(argv, "--d", "512") == "512":
        name += f" mlp{flag(argv, '--mlp')}"
    return name


def rows(manifest=None):
    out = []
    for path in sorted((ROOT / "results" / "loops_runs").glob("*.json")):
        r = json.loads(path.read_text())
        if manifest and manifest not in r.get("manifest", ""):
            continue
        argv = r["argv"]
        out.append({
            "manifest": r.get("manifest"), "arm": arm(argv), "seed": flag(argv, "--seed"),
            "lr": flag(argv, "--lr"), "steps": flag(argv, "--steps"),
            "val": r.get("val_loss"), "val_raw": r.get("val_loss_raw"), "val_big": r.get("val_big_raw"),
            "test": r.get("test", {}) if isinstance(r.get("test"), dict) else r.get("test"),
            "params": r.get("params"), "nonembed": r.get("nonembed"),
            "tflops": r.get("train_flops"), "wall": r.get("wall"), "error": (r.get("error") or "")[:200],
            "job": r.get("job_id"),
        })
    return out


def main():
    manifest = sys.argv[1] if len(sys.argv) > 1 else None
    rs = rows(manifest)
    lm_rows = [r for r in rs if r["val_raw"] is not None]
    ref = {}
    for r in lm_rows:
        if r["arm"] == "abs":
            ref[(r["manifest"], r["seed"], r["lr"])] = r["val_raw"]
    for r in sorted(rs, key=lambda r: (r["manifest"] or "", r["val_raw"] or 99)):
        base = ref.get((r["manifest"], r["seed"], "0.008"))
        gain = f"{100 * (r['val_raw'] / base - 1):+.2f}%" if base and r["val_raw"] else ""
        val = f"{r['val_raw']:.6f}" if r["val_raw"] else ""
        big = f"{r['val_big']:.6f}" if r["val_big"] else ""
        if r["arm"] is None or r["lr"] is None:
            continue  # evaluation jobs: see loops_eval results
        print(f"{(r['manifest'] or '')[:18]:18s} {r['arm']:42s} s{r['seed']} lr{r['lr']:6s} val {val:9s} "
              f"big {big:9s} {gain:8s} wall {r['wall']} {r['error']}")
        if r["test"] and not r["val_raw"]:
            print("    ", json.dumps(r["test"])[:300])


if __name__ == "__main__":
    main()
