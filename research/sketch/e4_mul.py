"""E4 (SKETCHPAD2.md): long multiplication on the canvas. Control is position; the model's output names the next step.

Canvas rows (columns x counted from the right): a (multiplicand), b (multiplier), cM (multiply carry), p (product
scratch), cA (add carry), R (running result). Pass j works on multiplier digit b[j]; the cursor x runs j .. n+j.
Ops, each a certified lookup over a 3-cell fovea strip gathered by the cropper:
  MUL x: view (a[x-j], b[j], cM[x]) -> p[x], cM[x+1], next ADD (or ADZ when a[x-j] is blank: the pass's last column)
  ADD x: view (cA[x], p[x], R[x])   -> R[x], cA[x+1], next MUL at x+1
  ADZ x: same view                  -> R[x], cA[x+1], next FLS at x+1
  FLS x: view (cA[x], p[x], R[x])   -> R[x], next NXT   (p is blank here; the add with nothing)
  NXT  : view (b[j+1], -, -)         -> next MUL at x=j+1 on pass j+1, or HALT when b[j+1] is blank
Carry and product cells are consumed (cleared) when read; that is the painter's only rule beyond stamping.
Output tokens: three per tick: glyph1, glyph2, next-op letter (M A Z F N H); "-" for an unused glyph slot.

usage: e4_mul.py dry            (runtime driven by the reference tables)
       e4_mul.py train <steps> <seed> <kl> | e4_mul.py eval <adapter>
"""

import json
import random
import sys
import time

B = " "
DIG = "0123456789"
OPS = {"MUL": "M", "ADD": "A", "ADZ": "Z", "FLS": "F", "NXT": "N"}


def ref(op, v):
    """The true table: view (3 glyphs) -> (g1, g2, next-op letter)."""
    if op == "MUL":
        a, b, c = v
        if a == B:  # flush the multiply carry into p; last column of the pass
            return (c if c != B else "0", "0", "Z")
        s = int(a) * int(b) + (int(c) if c != B else 0)
        return (str(s % 10), str(s // 10), "A")
    if op in ("ADD", "ADZ", "FLS"):
        c, p, r = v
        s = sum(int(g) for g in (c, p, r) if g != B)
        nxt = {"ADD": "M", "ADZ": "F", "FLS": "N"}[op]
        if op == "FLS":
            return (str(s) if s else B, "-", nxt)  # s <= 1 + 9: R had nothing beyond this pass
        return (str(s % 10), str(s // 10), nxt)
    if op == "NXT":
        return ("-", "-", "H" if v[0] == B else "M")
    raise ValueError(op)


def domain():
    rows = []
    for a in B + DIG:
        for b in DIG:
            for c in B + "012345678":
                rows.append(("MUL", (a, b, c)))
    for op in ("ADD", "ADZ"):
        for c in B + "1":
            for p in DIG:
                for r in B + DIG:
                    rows.append((op, (c, p, r)))
    for c in B + "1":
        rows.append(("FLS", (c, B, B)))
    for b in B + DIG:
        rows.append(("NXT", (b, B, B)))
    return rows


class Canvas:
    def __init__(self, a: str, b: str):
        self.n, self.m = len(a), len(b)
        W = self.n + self.m + 2
        self.W = W
        self.rows = {k: [B] * W for k in ("a", "b", "cM", "p", "cA", "R")}
        for i, d in enumerate(reversed(a)):
            self.rows["a"][i] = d
        for i, d in enumerate(reversed(b)):
            self.rows["b"][i] = d

    def get(self, row, x):
        return self.rows[row][x] if 0 <= x < self.W else B

    def result(self):
        return "".join(reversed(self.rows["R"])).strip().lstrip("0") or "0"


def view(cv, op, x, j):
    if op == "MUL":
        return (cv.get("a", x - j), cv.get("b", j), cv.get("cM", x))
    if op in ("ADD", "ADZ", "FLS"):
        return (cv.get("cA", x), cv.get("p", x), cv.get("R", x))
    return (cv.get("b", j + 1), B, B)


def run(a, b, policy, edit=None, max_ticks=10**6):
    """policy(op, view) -> (g1, g2, next). Returns (result, ticks, trace)."""
    cv = Canvas(a, b)
    op, x, j, ticks = "MUL", 0, 0, 0
    while ticks < max_ticks:
        if edit and edit[0] == ticks:
            cv.rows[edit[1]][edit[2]] = edit[3]
        v = view(cv, op, x, j)
        g1, g2, nxt = policy(op, v)
        ticks += 1
        if op == "MUL":
            cv.rows["cM"][x] = B  # consumed
            cv.rows["p"][x] = g1
            if x + 1 < cv.W:
                cv.rows["cM"][x + 1] = g2
            op = "ADD" if nxt == "A" else "ADZ"
        elif op in ("ADD", "ADZ"):
            cv.rows["cA"][x] = B
            cv.rows["p"][x] = B
            cv.rows["R"][x] = g1
            if x + 1 < cv.W:
                cv.rows["cA"][x + 1] = "1" if g2 == "1" else B
            if nxt == "M":
                op, x = "MUL", x + 1
            else:
                op, x = "FLS", x + 1
        elif op == "FLS":
            cv.rows["cA"][x] = B
            if g1 != B:
                cv.rows["R"][x] = g1
            op = "NXT"
        elif op == "NXT":
            if nxt == "H":
                return cv.result(), ticks, cv
            j += 1
            for k in ("cM", "p", "cA"):
                cv.rows[k] = [B] * cv.W
            op, x = "MUL", j
    return None, ticks, cv


def dry():
    rng = random.Random(0)
    reference = lambda op, v: ref(op, v)
    rows = domain()
    print("domain rows:", len(rows), {o: sum(r[0] == o for r in rows) for o in OPS})
    for n, m, k in ((1, 1, 100), (4, 4, 200), (6, 6, 200), (10, 10, 100), (7, 3, 100), (2, 9, 100), (40, 40, 10)):
        bad = 0
        for _ in range(k):
            a = str(rng.randint(10 ** (n - 1), 10**n - 1))
            b = str(rng.randint(10 ** (m - 1), 10**m - 1))
            got, ticks, _ = run(a, b, reference)
            bad += got != str(int(a) * int(b))
        print(f"{n}x{m}: {k - bad}/{k} exact, ticks for last {ticks}")
    for a, b in (("0", "5"), ("10", "10"), ("99", "99"), ("100", "1"), ("1", "1000")):
        print(a, "*", b, "=", run(a, b, reference)[0], "want", int(a) * int(b))


if __name__ == "__main__" and sys.argv[1] == "dry":
    dry()
