"""
Gather what the report's Newton attention figures need from the raw runs:

    python3 research/figdata.py

writes src/lib/report/results/newton_diag.json with, for the standard configuration
(rank 256, four heads, order 6, full read-out, one layer, 6,000 steps):
  - per task, the mean balanced accuracy and the mean accuracy with each arity knocked out;
  - every run's (characters found, accuracy) for the scatter;
  - four example channels' per-card phases from the figure run on Match-3.
"""

import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS = ROOT / "research" / "results"
TASKS = {"zs3": ("Match-3", 0.5), "zs4": ("Match-4", 0.5), "zs5": ("Match-5", 0.5), "arity": ("Smallest arity", 0.25)}


def load(name: str) -> list[dict]:
    path = RESULTS / f"{name}.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def standard(r: dict) -> bool:
    a = r.get("argv", [])
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    return (
        r.get("model") == "newton_K6_r256"
        and r.get("layers") == 1
        and opt("--steps", "") == "6000"
        and opt("--heads", "4") == "4"
        and "diag" in r
    )


def main() -> None:
    runs = [r for r in load("newton_c") + load("newton_fig") if not r.get("error") and standard(r)]
    knock = []
    for task, (label, chance) in TASKS.items():
        rs = [r for r in runs if r["task"] == task]
        if not rs:
            continue
        K = len(rs[0]["diag"]["knockout"])
        knock.append(
            {
                "task": task,
                "label": label,
                "chance": chance,
                "runs": len(rs),
                "bal": round(statistics.mean(r["bal_acc"] for r in rs), 4),
                "knockout": [round(statistics.mean(r["diag"]["knockout"][k] for r in rs), 4) for k in range(K)],
                "contrib": [round(statistics.mean(r["diag"]["contrib"][k] for r in rs), 4) for k in range(K)],
            }
        )
    scatter = [
        {"task": r["task"], "seed": r["seed"], "found": r["diag"]["chars"]["distinct"], "of": r["diag"]["chars"]["of"], "bal": r["bal_acc"]}
        for r in runs
        if r["task"] in TASKS and "chars" in r["diag"]
    ]
    examples = []
    for r in load("newton_fig"):
        if r.get("task") == "zs3" and "diag" in r and "examples" in r["diag"].get("chars", {}):
            examples = r["diag"]["chars"]["examples"]
            hist = r["diag"]["chars"]["hist"]
            break
    else:
        hist = []
    out = {"knock": knock, "scatter": scatter, "examples": examples, "hist": hist}
    dest = ROOT / "src" / "lib" / "report" / "results" / "newton_diag.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    for k in knock:
        print(k["label"], k["runs"], k["bal"], k["knockout"])
    print(len(scatter), "scatter points;", len(examples), "example channels")


if __name__ == "__main__":
    main()
