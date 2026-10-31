"""Base-model control on the calculator's 2,446 views, with E7 through the same scorer (paper review, 31 Oct 2026).

A reviewer asked how well the unadapted Qwen3.5-0.8B does on the same views under the same pinned prompt. Every query
is the server certificate's prompt form (e6_slots.batch: `OP<image>=`, plus the two slots `??` for the three-answer
tables) and is scored as e5_union.certify scores it (e2_column.margins at `=`, `?`, `?`: a view passes when, at every
output position, the correct token beats every other token of the full vocabulary).

  e7     E7 (the arithmetic adapter), zero-shot: the sanity check (2,446 / 2,446, min margin 3.96 on SUM); the job stops
         here if it fails
  zs     base, zero-shot, the deployed prompt
  fs     base, 8-shot: a fixed prefix of 8 solved views of the same table (seed 0), each `OP<image>=` followed by its
         correct output tokens and a newline, then the deployed query; identical for every query of that table
  zs_tf, fs_tf  the same, except that the query's 2nd and 3rd outputs are read after the true earlier outputs (teacher
         forcing, the form the examples show) instead of at the slots; every margin > 0 then means greedy decoding of
         the outputs is exactly right. SUM (one output) is the same in both forms.

Sequences are built from token ids, each view's segment through the processor exactly as the certificate builds it, so
every output is its single-character token (tokenising `=c` or `-N` as text would merge characters). Images use the
model's own placeholders, one `<|vision_start|><|image_pad|><|vision_end|>` per view, in one sequence, no chat template.
FLS has 2 views: its prefix shows each 4 times, in a seeded order. Few-shot results are reported for all views, for the
views that are not in the prefix (the queries proper), and for the example views.

  python base_control.py <E7 adapter> <out.json>          # writes <out.json> and <out>_rows.json
"""

import json
import math
import random
import statistics
import sys
import time

import torch
import transformers
from peft import PeftModel

import e2_column as e2
import e5_union as u
import e7_calc  # noqa: F401  (the 2,446 rows; installs e6_slots's slotted batch as u.batch)
from e6_slots import SLOT_ID, SLOTS

OPS = ["SUM", "MUL", "ADD", "ADZ", "FLS", "NXT", "SUB", "EST", "DEC"]
K, SEED = 8, 0
E7_MIN = 3.9598007202148438  # eval_e7_server.json, SUM
NL = u.tok.encode("\n", add_special_tokens=False)
assert len(NL) == 1, NL
NL = NL[0]


def answer_ids(op, v):
    return [u.CHAR_ID[c] for c in u.answer(op, v)]


def draw_prefixes():
    rng = random.Random(SEED)
    pre = {}
    for op in OPS:
        rows = u.BY_OP[op]
        if len(rows) >= K:
            pre[op] = rng.sample(rows, K)
        else:
            ex = (rows * math.ceil(K / len(rows)))[:K]
            rng.shuffle(ex)
            pre[op] = ex
    return pre


def segment(op, v):
    p = u.prompt_inputs(op, v)  # the certificate's cached processor output for `OP<image>=`
    return p["input_ids"][0].tolist(), p["mm_token_type_ids"][0].tolist(), p["pixel_values"], p["image_grid_thw"]


def sequence(row, prefix, form):
    ids, mm, pvs, thws = [], [], [], []
    for op, v in prefix:
        i, m, pv, thw = segment(op, v)
        a = answer_ids(op, v)
        ids += i + a + [NL]
        mm += m + [0] * (len(a) + 1)
        pvs.append(pv)
        thws.append(thw)
    op, v = row
    i, m, pv, thw = segment(op, v)
    a = answer_ids(op, v)
    ids += i
    mm += m
    pvs.append(pv)
    thws.append(thw)
    n = len(ids)
    extra = a[:-1] if form == "tf" else ([] if op == "SUM" else [SLOT_ID] * SLOTS)
    ids += extra
    mm += [0] * len(extra)
    return ids, mm, pvs, thws, (list(range(n - 1, n - 1 + len(a))), a)


def batch(rows, prefixes, form):
    """Right-padded batch, as e6_slots.batch; with no prefix and form 'slot' it is e6_slots.batch exactly."""
    seqs = [sequence(r, prefixes[r[0]] if prefixes else [], form) for r in rows]
    L = max(len(s[0]) for s in seqs)
    input_ids = torch.full((len(rows), L), u.PAD, dtype=torch.long)
    mask = torch.zeros((len(rows), L), dtype=torch.long)
    mm = torch.zeros((len(rows), L), dtype=torch.long)
    for i, s in enumerate(seqs):
        input_ids[i, : len(s[0])] = torch.tensor(s[0])
        mask[i, : len(s[0])] = 1
        mm[i, : len(s[1])] = torch.tensor(s[1])
    inp = {"input_ids": input_ids, "attention_mask": mask, "mm_token_type_ids": mm,
           "pixel_values": torch.cat([pv for s in seqs for pv in s[2]]),
           "image_grid_thw": torch.cat([t for s in seqs for t in s[3]])}
    return {k: t.to(u.dev) for k, t in inp.items()}, [s[4] for s in seqs]


@torch.no_grad()
def score(model, prefixes, form, chunk):
    out = []
    for k in range(0, len(u.ROWS), chunk):
        part = u.ROWS[k : k + chunk]
        inp, spans = batch(part, prefixes, form)
        lg = model(**inp).logits.float()
        for i, (pos, ans) in enumerate(spans):
            l, a = lg[i, pos], torch.tensor(ans, device=lg.device)
            out.append({"m": [round(float(x), 4) for x in e2.margins(l, a)],
                        "got": "".join(u.tok.decode([int(t)]) for t in l.argmax(-1).tolist())})
        del lg
    return out


@torch.no_grad()
def batched_vs_single(model, prefixes, form, n_per_op=2):
    """The batched (right-padded, mixed tables) logits at the output positions must match single-row forwards."""
    rng = random.Random(1)
    rows = [r for op in OPS for r in rng.sample(u.BY_OP[op], min(n_per_op, len(u.BY_OP[op])))]
    inp, spans = batch(rows, prefixes, form)
    lg = model(**inp).logits.float()
    worst = 0.0
    for i, r in enumerate(rows):
        inp1, sp1 = batch([r], prefixes, form)
        l1 = model(**inp1).logits.float()[0, sp1[0][0]]
        worst = max(worst, float((l1 - lg[i, spans[i][0]]).abs().max()))
    return worst


def summarise(res, keep=lambda r: True):
    def block(items):
        if not items:
            return {"views": 0}
        vm = [min(x["m"]) for _, x in items]
        pos = [m > 0 for _, x in items for m in x["m"]]
        by_pos = {}
        for _, x in items:
            for j, m in enumerate(x["m"]):
                by_pos.setdefault(j, []).append(m > 0)
        return {"views": len(items), "pass": sum(m > 0 for m in vm), "pass_share": round(sum(m > 0 for m in vm) / len(vm), 4),
                "positions": len(pos), "positions_correct": sum(pos), "position_share": round(sum(pos) / len(pos), 4),
                "correct_by_position": [sum(v) for _, v in sorted(by_pos.items())],
                "median_margin": round(statistics.median(vm), 3), "min_margin": round(min(vm), 3)}

    items = [(r, x) for r, x in zip(u.ROWS, res) if keep(r)]
    out = {op: block([(r, x) for r, x in items if r[0] == op]) for op in OPS}
    out["total"] = block(items)
    out["tables_fully_passing"] = [op for op in OPS if out[op]["views"] and out[op]["pass"] == out[op]["views"]]
    return out


def main(adapter, path):
    t0 = time.time()
    meta = {"rows": len(u.ROWS), "torch": torch.__version__, "transformers": transformers.__version__,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else str(u.dev), "adapter": adapter}
    rows_out, res = {}, {"meta": meta}

    # the builder with no prefix is the certificate's batch
    from e6_slots import batch as slotted
    a, sa = batch(u.ROWS[:64] + u.ROWS[-64:], None, "slot")
    b, sb = slotted(u.ROWS[:64] + u.ROWS[-64:])
    assert sa == sb and all(torch.equal(a[k], b[k]) for k in a), "builder differs from e6_slots.batch"

    # E7 sanity, through this scorer and through e5_union.certify
    e7 = PeftModel.from_pretrained(e2.load_base(), adapter).eval()
    r7 = score(e7, None, "slot", 64)
    ok, by_op, mins, fails = u.certify(e7)
    s7 = summarise(r7)
    res["e7_sanity"] = {**s7, "certify": {"pass": ok, "by_op": by_op, "min_margin": {k: round(v, 4) for k, v in mins.items()},
                                          "fails": fails[:20]},
                        "expected": {"pass": 2446, "min_margin": round(E7_MIN, 4)}}
    min7 = min(min(x["m"]) for x in r7)
    res["e7_sanity"]["ok"] = s7["total"]["pass"] == 2446 and ok == 2446 and abs(min7 - E7_MIN) <= 0.01
    rows_out["e7"] = r7
    print("e7 sanity", json.dumps({"pass": s7["total"]["pass"], "certify": ok, "min": min7, "ok": res["e7_sanity"]["ok"]}),
          f"({time.time() - t0:.0f}s)", flush=True)
    del e7
    torch.cuda.empty_cache()
    if not res["e7_sanity"]["ok"]:
        json.dump(res, open(path, "w"), indent=1)
        raise SystemExit("E7 sanity failed: stop")

    base = e2.load_base().eval()
    pre = draw_prefixes()
    ex = {op: {v for _, v in rows} for op, rows in pre.items()}
    is_ex = lambda r: r[1] in ex[r[0]]
    res["prefix"] = {op: ["".join(v).replace(" ", "_") + "=" + "".join(u.answer(op, v)) for _, v in rows] for op, rows in pre.items()}
    res["batched_vs_single_max_abs_logit_diff"] = {"zs": batched_vs_single(base, None, "slot"),
                                                   "fs": batched_vs_single(base, pre, "slot"),
                                                   "fs_tf": batched_vs_single(base, pre, "tf")}
    print("batched vs single", res["batched_vs_single_max_abs_logit_diff"], flush=True)
    assert max(res["batched_vs_single_max_abs_logit_diff"].values()) < 1e-2, "batched forward disagrees with single"
    for name, prefixes, form, chunk in (("zs", None, "slot", 64), ("zs_tf", None, "tf", 64),
                                        ("fs", pre, "slot", 32), ("fs_tf", pre, "tf", 32)):
        r = score(base, prefixes, form, chunk)
        rows_out[name] = r
        if prefixes is None:
            res[name] = summarise(r)
        else:
            res[name] = {"all": summarise(r), "queries": summarise(r, lambda x: not is_ex(x)),
                         "examples": summarise(r, is_ex)}
        t = (res[name] if prefixes is None else res[name]["queries"])["total"]
        print(name, json.dumps(t), f"({time.time() - t0:.0f}s)", flush=True)
    res["meta"]["seconds"] = round(time.time() - t0)
    json.dump(res, open(path, "w"), indent=1)
    rows = [{"op": op, "v": "".join(v).replace(" ", "_"), "want": "".join(u.answer(op, v)),
             **{k: rows_out[k][i] for k in rows_out}} for i, (op, v) in enumerate(u.ROWS)]
    json.dump(rows, open(path.replace(".json", "_rows.json"), "w"))
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
