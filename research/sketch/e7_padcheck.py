"""E7, the adder's rows in the common padded prompt form (CALC3.md, waves): `SUM<image>=???` (two slots and the one
`?` that pads a one-token word to the multiplier's two-token words), the answer still read at `=`. Every layer is
causal, so the margins should equal the unpadded ones up to float rounding; this measures it on all 242 rows.

  python e7_padcheck.py <adapter>
"""

import json
import sys

import torch
from peft import PeftModel

import e2_column as e2
import e5_union as u
import e7_calc  # noqa: F401  (the 2,446-row tables)
from e6_slots import SLOT_ID, batch as slotted_batch

PAD_SUM = 3  # slots 2 + 1 pad: the browser's padFor('ADD-FAST') when every word is padded to two tokens


def padded_batch(rows):
    inp, spans = slotted_batch(rows)
    # append PAD_SUM `?`s after each SUM prompt (the slotted batch gives SUM none); rows are right-padded, so rebuild
    ids, mask, mm = inp["input_ids"], inp["attention_mask"], inp["mm_token_type_ids"]
    L = ids.shape[1] + PAD_SUM
    out = {k: torch.zeros((ids.shape[0], L), dtype=t.dtype, device=t.device) for k, t in
           (("input_ids", ids), ("attention_mask", mask), ("mm_token_type_ids", mm))}
    out["input_ids"].fill_(u.PAD)
    for i in range(ids.shape[0]):
        n = int(mask[i].sum())
        extra = PAD_SUM if rows[i][0] == "SUM" else 0
        out["input_ids"][i, :n] = ids[i, :n]
        out["input_ids"][i, n:n + extra] = SLOT_ID
        out["attention_mask"][i, :n + extra] = 1
        out["mm_token_type_ids"][i, :n] = mm[i, :n]
    out["pixel_values"], out["image_grid_thw"] = inp["pixel_values"], inp["image_grid_thw"]
    return out, spans


@torch.no_grad()
def margins(model, rows, make):
    res = []
    for k in range(0, len(rows), 64):
        part = rows[k:k + 64]
        inp, spans = make(part)
        lg = model(**inp).logits.float()
        for i, (pos, ans) in enumerate(spans):
            res.append(float(e2.margins(lg[i, pos], torch.tensor(ans, device=e2.dev)).min()))
    return res


if __name__ == "__main__":
    model = PeftModel.from_pretrained(e2.load_base(), sys.argv[1]).eval()
    rows = u.BY_OP["SUM"]
    a = margins(model, rows, slotted_batch)
    b = margins(model, rows, padded_batch)
    d = [abs(x - y) for x, y in zip(a, b)]
    print(json.dumps({"rows": len(rows), "unpadded_min": min(a), "padded_min": min(b), "padded_pass": sum(x > 0 for x in b),
                      "max_abs_diff": max(d), "mean_abs_diff": sum(d) / len(d)}), flush=True)
