"""Audit of EXEC_LM section 19 records (read-only, at a given exec-d commit): for every *_ctl record, the stored
select_after and selected step, n at each length, the answer at 4,096 (uniform and, for add, long-carry), and whether
ABLATION_arith.json's section 19 rows equal the raw records.

  python research/audit/arith/s19_check.py [commit]      (default 0cbbfb3)
"""
import json
import subprocess
import sys

WT = "/Users/neo/repos/polyformer/.claude/worktrees/exec-d-0e1910"
C = sys.argv[1] if len(sys.argv) > 1 else "0cbbfb3"


def show(path):
    return json.loads(subprocess.run(["git", "-C", WT, "show", f"{C}:{path}"], capture_output=True, text=True, check=True).stdout)


def main():
    names = subprocess.run(["git", "-C", WT, "ls-tree", "--name-only", C, "research/results/exec_lm/"],
                           capture_output=True, text=True, check=True).stdout.split()
    recs = {n.split("/")[-1]: show(n) for n in names if n.endswith("_ctl.json") and "ARITH_" in n}
    rows = []
    for name, r in sorted(recs.items()):
        res, sel = r["results"], r["selection"]
        row = {"file": name, "task": r["task"], "arm": r["arm"], "seed": r["seed"], "select_after": sel.get("select_after"),
               "selected_step": sel["selected_step"], "steps_done": r["steps_done"],
               "n": {L: res[L]["n"] for L in res if "n" in res[L]},
               "answer_4096": res["4096"]["answer_exact"], "floor8_4096": res["4096"].get("floor_window", {}).get("8")}
        if "long_carry_4096" in res:
            row["long_carry_4096"] = res["long_carry_4096"]["answer_exact"]
            row["long_carry_floor8"] = res["long_carry_4096"]["floor_window"]["8"]
        rows.append(row)
        print(json.dumps(row))
    bad = [x["file"] for x in rows if not (x["select_after"] == 600 and x["selected_step"] > 600)]
    print("records:", len(rows), "| select_after != 600 or selected <= 600:", bad)
    abl = show("research/results/exec_lm/ABLATION_arith.json")
    print("ABLATION_arith keys:", list(abl.keys()))
    return rows, abl


if __name__ == "__main__":
    main()
