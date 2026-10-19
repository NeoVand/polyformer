"""
Gather what the report's Newton attention figures need from the raw runs:

    python3 research/figdata.py

writes src/lib/report/results/newton_diag.json with
  - per task, the mean balanced accuracy and the mean accuracy with each arity knocked out, for
    the final configuration (rank 256, four heads, order 6, shared and normalised read-out, one
    layer, 6,000 steps);
  - every single-task run's (characters found, accuracy) for the scatter, whatever its configuration;
  - four example channels' per-card phases from the figure run on Match-3;
  - the mixed-arity runs, scored on each arity, in the replication tables' row format;
and src/lib/report/results/lm.json with the language-model runs' validation bits per character.
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


def final(r: dict) -> bool:
    a = r.get("argv", [])
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    return (
        not r.get("error")
        and opt("--rank", "") == "256"
        and opt("--readout", "full") == "shared"
        and opt("--fnorm", "0") == "1"
        and opt("--steps", "") == "6000"
        and "diag" in r
    )


def regime(r: dict) -> str:
    a = r.get("argv", [])
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    name = f"{r['task']}-r{opt('--rank', '32')}"
    name += "-shared" if opt("--readout", "full") == "shared" else ""
    name += "-fnorm" if opt("--fnorm", "0") == "1" else ""
    return name + f"-s{opt('--steps', '?')}"


def mixed_rows() -> list[dict]:
    """One model trained on several arities, scored on each, in the tables' row format."""
    groups: dict[tuple[str, str], list[float]] = {}
    seeds: dict[tuple[str, str], list[int]] = {}
    for r in load("newton_d") + load("newton_f"):
        if r.get("error") or "per_k" not in r:
            continue
        for k, v in r["per_k"].items():
            key = (f"zs{k}", regime(r))
            groups.setdefault(key, []).append(v)
            seeds.setdefault(key, []).append(r["seed"])
    return [
        {"task": t, "model": m, "seeds": seeds[(t, m)], "bal": v, "bal_mean": round(statistics.mean(v), 4), "params": 0}
        for (t, m), v in sorted(groups.items())
    ]


def lm_rows() -> list[dict]:
    """enwik8 runs, one row per architecture, each seed's final validation bpc and its curve."""
    out: dict[str, dict] = {}
    for r in load("lm_a"):
        if r.get("error"):
            continue
        row = out.setdefault(r["arch"], {"arch": r["arch"], "params": r["params"], "steps": r["steps"],
                                         "rank": r["rank"], "order": r["order"], "seeds": [], "bpc": [], "curves": []})
        row["seeds"].append(r["seed"])
        row["bpc"].append(r["val_bpc"])
        row["curves"].append([[c[0], c[2]] for c in r["curve"]])
    for row in out.values():
        row["mean"] = round(statistics.mean(row["bpc"]), 4)
    return [out[a] for a in ("gpt", "hybrid", "newton") if a in out]


def main() -> None:
    runs = [r for r in load("newton_c") + load("newton_fig") if not r.get("error") and standard(r)]
    fixed = [r for r in load("newton_e") if final(r)]
    knock = []
    for task, (label, chance) in TASKS.items():
        rs = [r for r in fixed if r["task"] == task]
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
    # every single-task run with a character probe, whatever its configuration, for the scatter
    for r in load("newton_e"):
        if not r.get("error") and r.get("task") in TASKS and "chars" in r.get("diag", {}):
            scatter.append({"task": r["task"], "seed": r["seed"], "found": r["diag"]["chars"]["distinct"],
                            "of": r["diag"]["chars"]["of"], "bal": r["bal_acc"]})
    for r in load("newton_c"):
        if not r.get("error") and not standard(r) and r.get("layers") == 1 and r.get("task") in TASKS and "chars" in r.get("diag", {}):
            scatter.append({"task": r["task"], "seed": r["seed"], "found": r["diag"]["chars"]["distinct"],
                            "of": r["diag"]["chars"]["of"], "bal": r["bal_acc"]})
    out = {"knock": knock, "scatter": scatter, "examples": examples, "hist": hist, "mixed": mixed_rows()}
    dest = ROOT / "src" / "lib" / "report" / "results" / "newton_diag.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    lm = lm_rows()
    (ROOT / "src" / "lib" / "report" / "results" / "lm.json").write_text(json.dumps(lm, indent=1) + "\n")
    for row in lm:
        print(row["arch"], row["params"], row["mean"], row["bpc"])
    for k in knock:
        print(k["label"], k["runs"], k["bal"], k["knockout"])
    print(len(scatter), "scatter points;", len(examples), "example channels")


if __name__ == "__main__":
    main()
