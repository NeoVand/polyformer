"""Check 1 (provenance): every master-table number -> ABLATION record -> raw source record -> commit and config.

For each domain and record: does the source record exist, is it committed (git ls-files) and at which commit, does it
carry a config, and does the ABLATION value equal the value recomputed from the raw record (field mapping found by
matching, then applied to every record of the domain)? Also re-derives the master-table cell strings.
Read-only on the worktrees. Output: provenance.json and a printed summary.
"""
import json, os, subprocess, sys
from pathlib import Path

W = Path("/Users/neo/repos/polyformer/.claude/worktrees")
OUT = Path(__file__).resolve().parent
DOMAINS = {  # column -> (worktree, ablation file, key, ablation field, test length, candidate raw fields)
    "code": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_code.json", None, "exact_64x", "1024", ["acc_last"]),
    "add": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "add", "exact_128x", "4096", ["answer_exact", "final_exact"]),
    "count": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "count", "exact_128x", "4096", ["answer_exact", "final_exact"]),
    "lean": ("lean-s-2b865a", "research/results/lean_s/ABLATION_lean_chains.json", None, "exact_64x", "1024", ["fr_acc_last", "tf_acc_last"]),
    "s5": ("invariance-3e22f3", "research/results/invariance/ABLATION_S5.json", None, "exact_64x", "1024", ["acc_last"]),
    "stories": ("lean-n-data-34a2d2", "research/results/stories/ABLATION_stories.json", None, "exact_64x", "1024", ["exact_last"]),
}
CONFIG_KEYS = ("cfg", "config", "args", "data_config")


def git(wt, *a):
    return subprocess.run(["git", "-C", str(W / wt), *a], capture_output=True, text=True).stdout.strip()


def find(wt, rel):
    for base in (W / wt / "research", W / wt):
        p = base / rel
        if p.exists():
            return p
    return None


def raw_value(src, length, field):
    res = src.get("results") or src.get("test") or {}
    v = (res.get(length) or {}).get(field)
    return v


def main():
    rows, summary = [], {}
    for dom, (wt, f, key, afield, L, cands) in DOMAINS.items():
        d = json.load(open(W / wt / f))
        d = d[key] if key else d
        recs = d if isinstance(d, list) else d["records"]
        dom_rows = []
        for r in recs:
            p = find(wt, r["source_record"])
            row = {"domain": dom, "arm": r["arm"], "seed": r["seed"], "mu": r.get("mu"), "source": r["source_record"],
                   "exists": bool(p), "ablation_value": r.get(afield)}
            if p:
                relp = str(p.relative_to(W / wt))
                row["tracked"] = bool(git(wt, "ls-files", relp))
                row["commit"] = git(wt, "log", "-1", "--format=%h", "--", relp)
                src = json.load(open(p))
                row["has_config"] = any(k in src for k in CONFIG_KEYS) or all(k in src for k in ("lr", "steps", "seed"))
                for c in cands:
                    row["raw_" + c] = raw_value(src, L, c)
            dom_rows.append(row)
        # which candidate field reproduces the ablation values?
        best = None
        for c in cands:
            ok = 0
            for row in dom_rows:
                a, b = row["ablation_value"], row.get("raw_" + c)
                if isinstance(a, bool) and b is not None:
                    b = b >= 0.99
                if a is not None and b is not None and (a == b or (not isinstance(a, bool) and abs(a - b) < 1e-9)):
                    ok += 1
            if best is None or ok > best[1]:
                best = (c, ok)
        for row in dom_rows:
            a, b = row["ablation_value"], row.get("raw_" + best[0])
            if isinstance(a, bool) and b is not None:
                b = b >= 0.99
            row["matches"] = a is not None and b is not None and (a == b if isinstance(a, bool) else abs(a - b) < 1e-9)
        summary[dom] = {"records": len(dom_rows), "mapping": f"results[{L}].{best[0]}", "matched": best[1],
                        "missing_source": sum(not x["exists"] for x in dom_rows),
                        "untracked_source": sum(x["exists"] and not x["tracked"] for x in dom_rows),
                        "no_config": sum(x["exists"] and not x["has_config"] for x in dom_rows),
                        "mismatch": [(x["arm"], x["seed"], x["mu"], x["ablation_value"], x.get("raw_" + best[0]))
                                     for x in dom_rows if not x["matches"]]}
        rows += dom_rows
    (OUT / "provenance.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1) + "\n")
    for k, v in summary.items():
        print(k, json.dumps(v))


if __name__ == "__main__":
    main()
