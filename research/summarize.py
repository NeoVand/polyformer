"""
Aggregate research/results/<grid>.jsonl into per-(task, model) statistics and
write them where the report can read them:

    python3 research/summarize.py baseline

prints a markdown table and writes src/lib/report/results/<grid>.json. Each row
keeps its seeds' raw values, so the page can show the spread, not just a mean.
"""

import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def label(r: dict) -> str:
    m = r["model"].split("_")[0]
    if m == "sa":
        return f"standard-{r['layers']}L"
    return m


def main(grid: str) -> None:
    rows = [json.loads(l) for l in (ROOT / "research" / "results" / f"{grid}.jsonl").read_text().splitlines() if l.strip()]
    rows = [r for r in rows if not r.get("error")]
    cells: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        cells.setdefault((r["task"], label(r)), []).append(r)
    out = []
    for (task, model), rs in sorted(cells.items()):
        bal = [r["bal_acc"] for r in rs]
        tok = [r["tok_acc"] for r in rs]
        out.append(
            {
                "task": task,
                "model": model,
                "seeds": [r["seed"] for r in rs],
                "bal": bal,
                "tok": tok,
                "bal_mean": round(statistics.mean(bal), 4),
                "bal_min": round(min(bal), 4),
                "bal_max": round(max(bal), 4),
                "params": rs[0]["params"],
                "pos_rate": rs[0]["pos_rate"],
                "secs": round(statistics.mean(r["secs"] for r in rs), 1),
            }
        )
    dest = ROOT / "src" / "lib" / "report" / "results"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{grid}.json").write_text(json.dumps(out, indent=1) + "\n")
    tasks = sorted({o["task"] for o in out})
    print("| model | " + " | ".join(tasks) + " |")
    print("|---|" + "---|" * len(tasks))
    for model in sorted({o["model"] for o in out}):
        cells_txt = []
        for t in tasks:
            o = next((x for x in out if x["task"] == t and x["model"] == model), None)
            cells_txt.append(f"{o['bal_mean']*100:.1f} ({o['bal_min']*100:.0f}-{o['bal_max']*100:.0f}) n={len(o['seeds'])}" if o else "")
        print(f"| {model} | " + " | ".join(cells_txt) + " |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "baseline")
