"""Local tables from events_probe.py and loops_eval.py results (needs tiktoken to show boundary tokens).

    python research/events_report.py events_probe_8k        # a manifest's probe/eval jobs
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def label(cfg):
    if cfg.get("arch") == "events":
        return f"events l={cfg.get('ev_len'):g} {cfg.get('ev_posenc')}" + (
            f" dmain{cfg['ev_dmain']}" if cfg.get("ev_dmain") not in (None, cfg.get("d")) else "")
    name = cfg.get("posenc") or "abs"
    if cfg.get("forget"):
        name += "+forget"
    return (f"hybrid {name}" if cfg.get("pattern") else name) + f" d{cfg.get('d')}"


def main():
    manifest = sys.argv[1]
    try:
        import tiktoken
        enc = tiktoken.get_encoding("gpt2")
    except ImportError:
        enc = None
    for path in sorted((ROOT / "results" / "loops_runs").glob("*.json")):
        r = json.loads(path.read_text())
        if r.get("manifest") != manifest:
            continue
        test = r
        for row in test.get("probe", []):
            cfg = row["cfg"]
            print(f"\n{label(cfg)} seed {cfg.get('seed')} ctx {cfg.get('ctx')}  {row['ckpt']}")
            for name, p in row["probes"].items():
                print(f"  {name:10s} acc {p['acc']:.3f} (chance {p['chance']:.2f})  answer loss {p['loss']:.3f}")
            b = row.get("boundaries")
            if b:
                print(f"  boundaries: rate {b['rate']:.4f}, mean event length {b['mean_event_length']:.2f}; "
                      f"on/after punctuation, newline or clause word {b['share_any']:.3f} of boundaries "
                      f"vs {b['base_any']:.3f} of tokens")
                for k, v in b["by_category"].items():
                    print(f"    {k:15s} {v['share']:.3f} vs base {v['base']:.3f}")
                if enc:
                    top = ", ".join(f"{enc.decode([i])!r} {c}/{t}" for i, c, t in b["top_tokens"][:25])
                    print("  top boundary tokens (count/occurrences):", top)
                    s = b["samples"][0]
                    text = "".join(("│" if f else "") + enc.decode([i]) for i, f in zip(s["ids"][:300], s["boundary"]))
                    print("  sample:", text.replace("\n", "⏎"))
        for row in test.get("eval", []):
            cfg = row["cfg"]
            d = row["full"]["buckets"]["distance"]
            print(f"{label(cfg):36s} s{cfg.get('seed')} all {row['full']['loss']:.4f}  " +
                  "  ".join(f"{k} {v['loss']:.4f}" for k, v in d.items() if v["loss"] is not None))


if __name__ == "__main__":
    main()
