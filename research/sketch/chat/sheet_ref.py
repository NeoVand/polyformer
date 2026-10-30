"""A Python stand-in for the sheet runtime of CONTRACT seam 3: parse a work order and print its result lines.

It computes with exact fractions on the host, so it is NOT the certified sheet; it exists to write the `= …` lines of
the synthetic dialogues and to score what the model writes (GSM8K and the held-out families run blocks through it, said
as such). The formats follow the PROGRAM stream's runtime (src/lib/sketchpad/program on branch `program`, 30 Oct):
`= <value>` per statement; decimals truncated toward zero, trailing zeros dropped unless `to k places`, `…` when digits
were cut; every ÷ and √ cut at k places (`to k places`) or else 12; `solve` prints `x = …` with `n/d (≈ 6 places)` for
fractions; `expand` prints `3x^2 - x + 4`; systems print `x = …, y = …`.

  python sheet_ref.py "1234 × 5678 − 99"      # prints the result lines
"""

import math
import re
import sys
from fractions import Fraction

VARS = ("x", "y", "z")
NORM = [("×", "*"), ("÷", "/"), ("−", "-"), ("–", "-"), ("√", " sqrt "), ("·", "*"), ("²", "^2"), ("³", "^3")]
TOKEN = re.compile(r"\s*(?:(\d+\.\d*|\.\d+|\d+)|([A-Za-z_]\w*)|(\*\*|[-+*/^(),=]))")


class SheetError(Exception):
    pass


class CheckFailed(SheetError):
    pass


# --- polynomials over Fractions in x, y, z: {(ex, ey, ez): coef}; a number is a constant polynomial ---------------

def const(c):
    return {(0, 0, 0): Fraction(c)} if c else {}


def var(v):
    e = [0, 0, 0]
    e[VARS.index(v)] = 1
    return {tuple(e): Fraction(1)}


def padd(a, b, s=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + s * v
        if out[k] == 0:
            del out[k]
    return out


def pmul(a, b):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = tuple(x + y for x, y in zip(ka, kb))
            out[k] = out.get(k, 0) + va * vb
            if out[k] == 0:
                del out[k]
    return out


def is_const(p):
    return all(k == (0, 0, 0) for k in p)


def cval(p):
    if not is_const(p):
        raise SheetError("expected a number, got an expression in x")
    return p.get((0, 0, 0), Fraction(0))


class Approx(Fraction):
    """A value with digits cut (prints with …)."""


def cut(q: Fraction, places: int) -> Fraction:
    s = 10 ** places
    n = abs(q.numerator) * s // q.denominator
    v = Fraction(n if q >= 0 else -n, s)
    return Approx(v) if v != q else v


def approx(*vals):
    return any(isinstance(v, Approx) for v in vals)


def mark(v, a):
    return Approx(v) if a else Fraction(v)


# --- parser: precedence ^ (right) > unary - > implicit and * / > + - ------------------------------------------------

class Parser:
    def __init__(self, text, env, places):
        self.toks, pos = [], 0
        while pos < len(text):
            if text[pos:].strip() == "":
                break
            m = TOKEN.match(text, pos)
            if not m:
                raise SheetError(f"bad token at {text[pos:pos + 8]!r}")
            self.toks.append(m.group(1) or m.group(2) or m.group(3))
            pos = m.end()
        self.i, self.env, self.places = 0, env, places

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self, want=None):
        t = self.peek()
        if t is None or (want and t != want):
            raise SheetError(f"expected {want or 'more'}, got {t}")
        self.i += 1
        return t

    def expr(self):
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            w = self.term()
            v = mark_poly(padd(v, w, 1 if op == "+" else -1), poly_approx(v) or poly_approx(w))
        return v

    def term(self):
        v = self.unary()
        while True:
            t = self.peek()
            if t in ("*", "/"):
                self.take()
                w = self.unary()
                v = self.div(v, w) if t == "/" else mark_poly(pmul(v, w), poly_approx(v) or poly_approx(w))
            elif t is not None and (t == "(" or t[0].isdigit() or t[0] == "." or t[0].isalpha()) and t not in (
                    "to", "places"):
                w = self.power()  # implicit product: 2x, 3(x - 2), (a)(b)
                v = mark_poly(pmul(v, w), poly_approx(v) or poly_approx(w))
            else:
                return v

    def div(self, a, b):
        d = cval(b)
        if d == 0:
            raise SheetError("division by zero")
        if is_const(a):
            q = cval(a) / d
            k = self.places if self.places is not None else 12
            c = cut(q, k)
            return const_poly(c if (self.places is not None or isinstance(c, Approx)) else q,
                              approx(cval(a), d) or isinstance(c, Approx))
        return mark_poly({k: v / d for k, v in a.items()}, poly_approx(a))

    def unary(self):
        if self.peek() == "-":
            self.take()
            v = self.unary()
            return mark_poly({k: -c for k, c in v.items()}, poly_approx(v))
        if self.peek() == "+":
            self.take()
            return self.unary()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() in ("^", "**"):
            self.take()
            neg = False
            if self.peek() == "-":
                self.take()
                neg = True
            e = self.take()
            if not e.isdigit() or int(e) > 12 or neg:
                raise SheetError("exponent must be an integer from 0 to 12")
            out = const(1)
            for _ in range(int(e)):
                out = pmul(out, base)
            return mark_poly(out, poly_approx(base))
        return base

    def atom(self):
        t = self.take()
        if t == "(":
            v = self.expr()
            self.take(")")
            return v
        if t[0].isdigit() or t[0] == ".":
            return const(Fraction(t))
        if t == "sqrt":  # √(…) per seam 3; a bare √2 is read as √(2)
            if self.peek() == "(":
                self.take("(")
                v = cval(self.expr())
                self.take(")")
            else:
                v = cval(self.atom())
            if v < 0:
                raise SheetError("square root of a negative number")
            k = self.places if self.places is not None else 12
            s = 10 ** k
            r = math.isqrt(v.numerator * s * s // v.denominator)
            root = Fraction(r, s)
            return const_poly(root, root * root != v or approx(v))
        if t == "gcd":
            self.take("(")
            a = cval(self.expr())
            self.take(",")
            b = cval(self.expr())
            self.take(")")
            if a.denominator != 1 or b.denominator != 1:
                raise SheetError("gcd needs integer arguments")
            return const(math.gcd(int(a), int(b)))
        if t in VARS:
            return var(t)
        if t in self.env:
            return const_poly(self.env[t], isinstance(self.env[t], Approx))
        raise SheetError(f"unknown name {t}")


def const_poly(v, a=False):
    return {(0, 0, 0): mark(v, a)} if v else ({(0, 0, 0): Approx(0)} if a else {})


def poly_approx(p):
    return any(isinstance(v, Approx) for v in p.values())


def mark_poly(p, a):
    if not a:
        return p
    return {k: Approx(v) for k, v in p.items()} or {(0, 0, 0): Approx(0)}


def parse_expr(text, env, places=None):
    p = Parser(text, env, places)
    v = p.expr()
    if p.peek() is not None:
        raise SheetError(f"unexpected {p.peek()}")
    return v


# --- display ------------------------------------------------------------------------------------------------------

def decimal(v: Fraction, places=12, fixed=False) -> str:
    n = abs(v.numerator) * 10 ** places
    q, r = divmod(n, v.denominator)
    digits = str(q).rjust(places + 1, "0")
    s = digits[:-places] + "." + digits[-places:] if places else digits
    if not fixed and places:
        s = s.rstrip("0").rstrip(".")
    if v < 0 and q:
        s = "-" + s
    return s + ("…" if r or isinstance(v, Approx) else "")


def root_text(v: Fraction) -> str:
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator} (≈ {decimal(v, 6, True)})"


def poly_text(c):
    """c[i] = coefficient of x^i (integers), as `3x^2 - x + 4`."""
    out = ""
    for i in range(len(c) - 1, -1, -1):
        if c[i] == 0:
            continue
        a = abs(c[i])
        body = ("" if a == 1 and i > 0 else str(a)) + ("" if i == 0 else "x" if i == 1 else f"x^{i}")
        out += ((" - " if c[i] < 0 else " + ") if out else ("-" if c[i] < 0 else "")) + body
    return out or "0"


# --- algebra ------------------------------------------------------------------------------------------------------

def univariate(p):
    if any(k[1] or k[2] for k in p):
        raise SheetError("only x may appear here")
    deg = max((k[0] for k in p), default=0)
    return [p.get((i, 0, 0), Fraction(0)) for i in range(deg + 1)]


def integer_coeffs(c):
    lcm = 1
    for v in c:
        lcm = lcm * Fraction(v).denominator // math.gcd(lcm, Fraction(v).denominator)
    out = [int(Fraction(v) * lcm) for v in c]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def solve_one(eq, env):
    L, R = eq.split("=", 1)
    f = padd(parse_expr(L, env), parse_expr(R, env), -1)
    c = integer_coeffs(univariate(f))
    if len(c) == 1:
        return "every x" if c[0] == 0 else "no solution"
    if len(c) == 2:
        return "x = " + root_text(Fraction(-c[0], c[1]))
    if len(c) == 3:
        k, b, a = c
        disc = b * b - 4 * a * k
        if disc < 0:
            return "no real roots"
        s = math.isqrt(disc)
        den = 2 * a
        if s * s == disc:
            roots = []
            for num in (-b - s, -b + s):
                r = Fraction(num, den)
                if r not in roots:
                    roots.append(r)
            return "x = " + ", ".join(root_text(r) for r in roots)
        bounds = []
        for sg in (-1, 1):
            r = (-b + sg * math.sqrt(disc)) / den
            lo = math.floor(r * 10 ** 6) / 10 ** 6
            bounds.append(f"[{lo:.6f}, {lo + 1e-6:.6f}]")
        return f"x = ({-b} ± √{disc})/({den}); six-place bounds {', '.join(bounds)}"
    roots, rem = rational_roots(c)
    facs = "".join(f"({poly_text([-r.numerator, r.denominator])})" for r in roots)
    return (f"proven roots: {', '.join(root_text(r) for r in roots) or 'none'}; factors {facs or 'none'}; remaining "
            f"{poly_text(rem)}. Guesses are not certified; checks prove these roots, not that no others exist.")


def rational_roots(c):
    roots, rem = [], list(c)
    changed = True
    while changed and len(rem) > 1:
        changed = False
        a0, an = rem[0], rem[-1]
        if a0 == 0:
            roots.append(Fraction(0))
            rem = rem[1:]
            changed = True
            continue
        cands = sorted({Fraction(s * p, q) for p in divisors(abs(a0)) for q in divisors(abs(an)) for s in (1, -1)})
        for r in cands:
            q = synthetic(rem, r)
            if q is not None:
                roots.append(r)
                rem = q
                changed = True
                break
    return roots, rem


def divisors(n):
    return [d for d in range(1, min(n, 10 ** 5) + 1) if n % d == 0] if n else [1]


def synthetic(c, r):
    """Divide sum c[i] x^i by (q x - p), r = p/q; None unless exact with integer quotient."""
    p, q = r.numerator, r.denominator
    out = [0] * (len(c) - 1)
    acc = Fraction(c[-1])
    for i in range(len(c) - 2, -1, -1):
        out[i] = acc / q
        acc = c[i] + p * out[i]
    if acc != 0 or any(Fraction(v).denominator != 1 for v in out):
        return None
    return [int(v) for v in out]


def solve_system(eqs, env):
    names = [v for v in VARS[: len(eqs)]]
    rows = []
    for eq in eqs:
        L, R = eq.split("=", 1)
        f = padd(parse_expr(L, env), parse_expr(R, env), -1)
        if any(sum(k) > 1 for k in f) or any(k[VARS.index(v)] for v in VARS[len(eqs):] for k in f):
            raise SheetError("a system must be linear in " + ", ".join(names))
        row = [f.get(tuple(int(j == i) for j in range(3)), Fraction(0)) for i in range(len(eqs))]
        rows.append(row + [-f.get((0, 0, 0), Fraction(0))])
    n = len(rows)
    m = [r[:] for r in rows]
    for col in range(n):  # Gaussian elimination over Fractions (the sheet uses Cramer / Bareiss; same answer)
        piv = next((r for r in range(col, n) if m[r][col] != 0), None)
        if piv is None:
            return "zero determinant; no unique solution"
        m[col], m[piv] = m[piv], m[col]
        for r in range(n):
            if r != col and m[r][col] != 0:
                k = m[r][col] / m[col][col]
                m[r] = [a - k * b for a, b in zip(m[r], m[col])]
    return ", ".join(f"{names[i]} = {root_text(m[i][n] / m[i][i])}" for i in range(n))


def expand(text, env):
    c = univariate(parse_expr(text, env))
    if any(Fraction(v).denominator != 1 for v in c):
        raise SheetError("expand needs integer coefficients")
    c = [int(v) for v in c]
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return poly_text(c)


def factor(text, env):
    c = integer_coeffs(univariate(parse_expr(text, env)))
    roots, rem = rational_roots(c)
    facs = "".join(f"({poly_text([-r.numerator, r.denominator])})" for r in roots)
    return (f"proven roots: {', '.join(root_text(r) for r in roots) or 'none'}; factors {facs or 'none'}; remaining "
            f"{poly_text(rem)}. Guesses are not certified; checks prove these roots, not that no others exist.")


# --- statements -----------------------------------------------------------------------------------------------------

PLACES = re.compile(r"\s+to\s+(\d+)\s+places?\s*$")


def normalise(line):
    for a, b in NORM:
        line = line.replace(a, b)
    return line


def run_line(line, env):
    """One statement -> its result text (without the leading '= '), updating env for assignments."""
    s = normalise(line.strip())
    if s.startswith("solve "):
        eqs = [e.strip() for e in split_top(s[6:])]
        if len(eqs) == 1:
            return solve_one(eqs[0], env)
        return solve_system(eqs, env)
    if s.startswith("expand "):
        return expand(s[7:], env)
    if s.startswith("factor "):
        return factor(s[7:], env)
    places = None
    m = PLACES.search(s)
    if m:
        places = int(m.group(1))
        s = s[: m.start()]
    name = None
    m = re.match(r"^([A-Za-z_]\w*)\s*=(.*)$", s)
    if m and m.group(1) not in VARS + ("sqrt", "gcd"):
        name, s = m.group(1), m.group(2)
    v = cval(parse_expr(s, env, places))
    if name:
        env[name] = v
    return decimal(v, places if places is not None else 12, places is not None)


def split_top(s):
    """Split on commas outside brackets (gcd(a, b) keeps its comma)."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + [cur]


def run(block: str):
    """Result lines of a work order (one '= …' per statement); errors become '= error: …'."""
    env, lines = {}, []
    for line in block.strip().splitlines():
        if not line.strip():
            continue
        try:
            lines.append("= " + run_line(line, env))
        except CheckFailed:
            lines.append("= check failed")
        except (SheetError, ZeroDivisionError, ValueError, IndexError, KeyError) as e:
            lines.append(f"= error: {e}")
    return lines


def value(block: str):
    """The exact value of the last expression statement (a Fraction), for scoring; None on an error."""
    env, last = {}, None
    for line in block.strip().splitlines():
        if not line.strip():
            continue
        s = normalise(line.strip())
        if s.startswith(("solve ", "expand ", "factor ")):
            return None
        m = PLACES.search(s)
        places = int(m.group(1)) if m else None
        s = s[: m.start()] if m else s
        name = None
        m = re.match(r"^([A-Za-z_]\w*)\s*=(.*)$", s)
        if m and m.group(1) not in VARS + ("sqrt", "gcd"):
            name, s = m.group(1), m.group(2)
        try:
            last = cval(parse_expr(s, env, places))
        except (SheetError, ZeroDivisionError, ValueError, IndexError, KeyError):
            return None
        if name:
            env[name] = last
    return last


if __name__ == "__main__":
    print("\n".join(run("\n".join(sys.argv[1:]))))
