"""E6: the union adapter answers a multiplier step in one forward pass.

E5 writes a multiplier step's three answer tokens (glyph, glyph, next step) one after another: three decoder calls per
tick in the browser. E6 appends two placeholder slots to the prompt (`MUL<image>=??`) and reads the three answers at
`=`, the first `?` and the second `?`, so a tick is one forward pass (the adder's SUM rows already were). Each slot's
answer is a function of the view alone, so nothing is lost by not feeding the earlier answers back; the first answer
keeps the position it had in E5, and training continues from the E5 adapter.

Everything else is E5 (recipe v2: the whole-table certificate as the loss's sampler, margin hinge, KL to the base on
text, cosine lr, certificate-driven replay, stop at a minimum margin): this module only swaps the batch builder and the
run policy of e5_union, which its train/certify/evaluate look up at call time.

  python e6_slots.py smoke <init adapter>                         # margins per answer position on a few rows
  python e6_slots.py train <steps> <seed> <hinge> <stop> <init>   # recipe v2 from <init>, then evaluate
  python e6_slots.py eval <adapter>
"""

import json
import os
import random
import sys

import torch
from peft import PeftModel

import e2_column as e2
import e5_union as u

SLOT = "?"
_ids = u.tok.encode(SLOT, add_special_tokens=False)
assert len(_ids) == 1, _ids
SLOT_ID = _ids[0]
SLOTS = 2  # placeholders after `=` for the multiplier's second and third answers


def batch(rows):
    """Right-padded batch; a multiplier row is its prompt plus two slots, and its answers sit at `=` and the slots."""
    seqs, mms, pvs, thws, spans = [], [], [], [], []
    for op, v in rows:
        p = u.prompt_inputs(op, v)
        ans = [u.CHAR_ID[c] for c in u.answer(op, v)]
        n = p["input_ids"][0].shape[0]
        extra = [] if op == "SUM" else [SLOT_ID] * SLOTS
        ids = p["input_ids"][0].tolist() + extra
        mm = p["mm_token_type_ids"][0].tolist() + [0] * len(extra)
        seqs.append(ids)
        mms.append(mm)
        pvs.append(p["pixel_values"])
        thws.append(p["image_grid_thw"])
        spans.append((list(range(n - 1, n - 1 + len(ans))), ans))
    L = max(len(s) for s in seqs)
    input_ids = torch.full((len(rows), L), u.PAD, dtype=torch.long)
    mask = torch.zeros((len(rows), L), dtype=torch.long)
    mm = torch.zeros((len(rows), L), dtype=torch.long)
    for i, (s, m) in enumerate(zip(seqs, mms)):
        input_ids[i, : len(s)] = torch.tensor(s)
        mask[i, : len(s)] = 1
        mm[i, : len(m)] = torch.tensor(m)
    inp = {"input_ids": input_ids, "attention_mask": mask, "mm_token_type_ids": mm,
           "pixel_values": torch.cat(pvs), "image_grid_thw": torch.cat(thws)}
    return {k: t.to(u.dev) for k, t in inp.items()}, spans


def policy(model):
    """A run's step: one forward of the prompt (plus the slots for the multiplier), the argmax at each answer place."""

    @torch.no_grad()
    def act(op, v):
        inp, spans = batch([(op, v)])
        lg = model(**inp).logits[0]
        return [u.ID_CHAR.get(int(lg[p].argmax()), "?") for p in spans[0][0]]

    return act


u.batch = batch
u.policy = policy


def smoke(init):
    model = PeftModel.from_pretrained(e2.load_base(), init).eval()
    rng = random.Random(0)
    rows = [r for op in ("MUL", "ADD", "ADZ", "FLS", "NXT", "SUM") for r in rng.sample(u.BY_OP[op], 2)]
    with torch.no_grad():
        for (op, v), (lg, ans) in zip(rows, u.row_logits(model, rows)):
            print(op, "".join(v).replace(u.B, "_"), "margins by answer position:",
                  [round(float(x), 2) for x in e2.margins(lg, ans)], flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke":
        smoke(sys.argv[2])
    elif cmd == "train":
        steps, seed, hinge, stop, init = sys.argv[2:7]
        out = u.train(steps=int(steps), seed=int(seed), hinge=float(hinge), v2=True, stop=float(stop), init=init)
        e6 = out.replace("e5_adapter", "e6_adapter")
        os.rename(out, e6)
        u.evaluate(e6)
    else:
        u.evaluate(sys.argv[2])
