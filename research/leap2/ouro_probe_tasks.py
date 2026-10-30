"""Task generators shared by ouro_probe.py and lfm3_probe.py."""

import random

def number(n, rng):
    return rng.randint(10 ** (n - 1), 10**n - 1)


def add_case(n, rng):
    shots = "".join(f"{(a := number(n, rng))}+{(b := number(n, rng))}={a + b}\n" for _ in range(4))
    a, b = number(n, rng), number(n, rng)
    return shots + f"{a}+{b}=", str(a + b)


def mul_case(n, rng):
    shots = "".join(f"{(a := number(n, rng))}*{(b := number(n, rng))}={a * b}\n" for _ in range(4))
    a, b = number(n, rng), number(n, rng)
    return shots + f"{a}*{b}=", str(a * b)


def swap_case(k, rng):
    def one():
        cups = list("ABCDE")
        moves = []
        for _ in range(k):
            i, j = rng.sample(range(5), 2)
            cups[i], cups[j] = cups[j], cups[i]
            moves.append(f"{i + 1}-{j + 1}")
        return f"Start: A B C D E\nSwaps: {', '.join(moves)}\nEnd:", " " + " ".join(cups)

    shots = "".join(q + a + "\n\n" for q, a in (one() for _ in range(3)))
    q, a = one()
    return shots + q, a


TASKS = {
    "add3": lambda r: add_case(3, r),
    "add5": lambda r: add_case(5, r),
    "add8": lambda r: add_case(8, r),
    "add12": lambda r: add_case(12, r),
    "mul2": lambda r: mul_case(2, r),
    "mul3": lambda r: mul_case(3, r),
    "swap2": lambda r: swap_case(2, r),
    "swap4": lambda r: swap_case(4, r),
    "swap8": lambda r: swap_case(8, r),
}

TEXT = open("/Users/neo/repos/polyformer/research/PRIMER.md").read()[:3000]

