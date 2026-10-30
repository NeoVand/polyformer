"""E7: the calculator's tables on the E6 adapter (SKETCHPAD3 T2).

E6 answers the adder (SUM, one token) and the multiplier (MUL ADD ADZ FLS NXT, three answers read at `=??` in one
forward pass): 1,795 rows. E7 adds the three tables of calc_tables.py, read the same way as the multiplier's steps:
SUB (column subtraction with borrow, 242 rows), EST (a quotient-digit guess from three digits, 400 rows with a
normalised divisor) and DEC (the guess lowered by one, 9 rows): 2,446 rows in all, one adapter.

Everything else is E6 (recipe v2 of e5_union: the whole-table certificate as the loss's sampler, margin hinge, KL to the
base on plain text, cosine lr, certificate-driven replay, stop at a minimum margin), continued from the E6 seed-3
adapter. This module only extends e5_union's row list, strata, answers and token alphabet, which its train / certify /
evaluate look up at call time, on top of e6_slots's slotted batch.

  python e7_calc.py smoke <init adapter> <steps>                  # a few steps and a certificate: the wiring
  python e7_calc.py train <steps> <seed> <hinge> <stop> <init>    # recipe v2 from <init>, then evaluate
  python e7_calc.py eval <adapter>
"""

import os
import sys

import calc_tables as ct
import e5_union as u
import e6_slots  # noqa: F401  (installs the slotted batch and run policy into e5_union)

_answer = u.answer


def answer(op, v):
    return ct.answer(op, v) if op in ct.ANSWER else _answer(op, v)


u.answer = answer
u.ROWS = u.ROWS + ct.ROWS
for r in ct.ROWS:
    u.BY_OP.setdefault(r[0], []).append(r)
u.STRATA2 = {**u.STRATA2, "SUB": 8, "EST": 12, "DEC": 2}
for ch in "SBC":
    ids = u.tok.encode(ch, add_special_tokens=False)
    assert len(ids) == 1, (ch, ids)
    u.CHAR_ID[ch] = ids[0]
u.ID_CHAR = {v: k for k, v in u.CHAR_ID.items()}
assert len(u.ROWS) == 2446, len(u.ROWS)
for op, v in u.ROWS:  # every answer is three (or, for SUM, one) single-token characters
    assert all(c in u.CHAR_ID for c in u.answer(op, v)), (op, v)


def rename(out):
    e7 = out.replace("e5_adapter", "e7_adapter")
    os.rename(out, e7)
    return e7


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke":
        init, steps = sys.argv[2], int(sys.argv[3])
        out = u.train(steps=steps, seed=0, hinge=4.0, v2=True, stop=None, init=init, every=steps)
        print("smoke adapter", rename(out), flush=True)
    elif cmd == "train":
        steps, seed, hinge, stop, init = sys.argv[2:7]
        out = u.train(steps=int(steps), seed=int(seed), hinge=float(hinge), v2=True, stop=float(stop), init=init)
        u.evaluate(rename(out))
    else:
        u.evaluate(sys.argv[2])
