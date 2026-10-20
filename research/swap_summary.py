"""Reproduce GROUPS.md section 7 tables and GPU-time estimate from the immutable result rows."""

import collections
import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).parent / "results"
ORDER = [
    "holo_d2_h128_K4_fnorm", "holo_d3_h85_K4_fnorm", "holo_d4_h64_K4_fnorm",
    "newton_K4_r64_shared_fnorm", "sa_1", "sa_2", "sa_3", "orthornn_d6_h42",
]


def read(name):
    path = ROOT / f"{name}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def main():
    all_rows = []
    main_cells = {}
    for grid in ("grp_swap_pilot", "grp_swap"):
        rows = read(grid)
        all_rows.extend(rows)
        cells = collections.defaultdict(list)
        for row in rows:
            if "error" in row:
                print(f"ERROR {grid}: {row['argv']}: {row['error']}")
                continue
            key = f"sa_{row['layers']}" if row["model"] == "sa" else row["model"]
            cells[key].append(row)
        print(f"\n{grid}\n")
        print("| Arm | Balanced accuracy %, mean (seeds in order) | Parameters | Train seconds, mean |")
        print("|---|---|---|---|")
        for key in ORDER:
            runs = sorted(cells[key], key=lambda row: row["seed"])
            if not runs:
                continue
            vals = [100 * row["bal_acc"] for row in runs]
            print(f"| {key} | {statistics.mean(vals):.2f} ({', '.join(f'{v:.2f}' for v in vals)}) "
                  f"| {runs[0]['params']:,} | {statistics.mean(row['secs'] for row in runs):.1f} |")
        if grid == "grp_swap":
            main_cells = cells
    complete = all(sorted(row["seed"] for row in main_cells.get(key, [])) == [0, 1, 2] for key in ORDER)
    if complete:
        criteria = {
            "S1": (ORDER[:1] + ORDER[3:4], lambda value: value <= 0.6404),
            "S2": (ORDER[1:3], lambda value: value >= 0.95),
            "S3": (ORDER[-1:], lambda value: value >= 0.95),
            "S4": (ORDER[4:7], lambda value: value >= 0.95),
        }
        print("\nRegistered decisions (all three seeds required):")
        for prediction, (keys, criterion) in criteria.items():
            holds = all(criterion(row["bal_acc"]) for key in keys for row in main_cells[key])
            print(f"{prediction}: {'holds' if holds else 'fails'}")
    else:
        print("\nMain grid incomplete or duplicated: require exactly seeds 0, 1, 2 for every arm.")
    total = sum(row.get("wall", 0) for row in all_rows)
    print(f"\n{len(all_rows)} rows, subprocess wall {total:.1f}s = {total / 3600:.3f} L4-hours; "
          f"GPU-only list-price estimate ${total * 0.000222:.2f}.")
    print("Pricing source: https://modal.com/pricing, fetched 2026-10-20; excludes CPU, memory and idle container time.")


if __name__ == "__main__":
    main()
