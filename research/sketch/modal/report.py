"""Summarise fetched sketch runs: python report.py out/<job> [out/<job> ...]

Reads files/e4_adapter_s*/train_log.json and eval.json (and run.log) as written by e4_train.py on Modal, and prints one
compact block per job: certificate rows by op at each checkpoint, min margins, perplexity ratio, products exact.
"""
import json
import pathlib
import sys


def show(job_dir: pathlib.Path):
    print(f"== {job_dir.name}")
    log = job_dir / "run.log"
    if log.exists():
        tail = log.read_text().strip().splitlines()[-3:]
        print("  log tail:", " | ".join(t[:120] for t in tail))
    for ad in sorted(job_dir.glob("files/e*_adapter_s*")):
        tl = ad / "train_log.json"
        if tl.exists():
            d = json.loads(tl.read_text())
            print(f"  {ad.name}: rows {d.get('rows')}, ppl0 {d.get('ppl0', 0):.2f}")
            for e in d["log"]:
                by = e.get("by_op", {})
                print(f"    step {e['step']:>5}  cert {e['cert']:>5}  loss {e['loss']:.3f}  ppl x{e['ppl_ratio']:.3f}  "
                      f"by_op {by}  min_margin {e.get('min_margin')}  fails {e.get('fails', [])[:4]}")
        ev = ad / "eval.json"
        if ev.exists():
            r = json.loads(ev.read_text())
            scores = "  ".join(f"{k} {v}" for k, v in r.items() if isinstance(v, str) and "/" in v)
            print(f"    EVAL cert {r.get('cert')}/{r.get('rows')}  by_op {r.get('by_op')}  min_margin {r.get('min_margin')}  "
                  f"ppl {r.get('ppl', float('nan')):.2f}  {scores}")
            if r.get("fails"):
                print("    fails:", r["fails"][:10])


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(pathlib.Path(a))
