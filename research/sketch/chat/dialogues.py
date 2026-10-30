"""Synthetic dialogues for the chat fine-tune (SKETCHPAD3 T4), in the work-order format of CONTRACT seam 3.

A sheet reply is three segments: the model's text up to and including the closing fence of a ```sheet block, the
runtime's result lines (`\\n= …\\n`, masked from the loss; written here by sheet_ref.py, the host stand-in), and the
model's continuation, which uses the value from the `= …` line verbatim. A sheet line is the translation only: the
expression from the words, or the equation as typed; it never contains the answer.

Families (each has train templates and held-out templates; the evaluation uses only held-out ones):
  calc      direct requests: multi-digit + − × ÷, decimals, money, percent, ÷ and √ to k places, gcd, powers,
            in symbols or in words
  prose     an expression typed in symbols inside mixed text, copied into the sheet
  word      word problems: the expression from the words (some multi-line with names)
  equation  solve (linear, quadratic), 2×2 systems, expand, factor; the equation copied as typed (² → ^2)
  distract  must not open the sheet: chit-chat, facts, writing, code, maths talk, single-digit arithmetic, and
            instruction prompts from HuggingFaceH4/no_robots; the reply is stock Qwen's own (filled in by
            stock_replies.py; single-digit arithmetic falls back to a template if stock gets it wrong)

  python dialogues.py <out dir> [--n 3000] [--format expr|ops] [--seed 0]
    writes train.jsonl and heldout.jsonl (the evaluation set); distractor turns (and 15% of train dialogues' earlier
    turns) carry a prompt but no reply until stock_replies.py fills them with stock Qwen's own greedy answers

--format ops writes the older work order (one binary operation per line, `t1 = a op b`) for the arithmetic families;
it exists so that format is one retrain away, and is not trained.
"""

import argparse
import json
import pathlib
import random
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sheet_ref  # noqa: E402

FMT = "expr"

# --- expression trees: ("num", "12.5") | (op, a, b) | ("sqrt", a) | ("gcd", a, b) | ("pow", a, "k") ---------------

SYM = {"+": "+", "-": "−", "*": "×", "/": "÷"}
PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "pow": 3}
WORD = {"+": ["plus", "added to"], "-": ["minus"], "*": ["times", "multiplied by"], "/": ["divided by"]}


def num(v):
    return ("num", str(v))


def infix(n, parent=0, right=False):
    k = n[0]
    if k == "num":
        return n[1]
    if k == "sqrt":
        return f"√({infix(n[1])})"
    if k == "gcd":
        return f"gcd({infix(n[1])}, {infix(n[2])})"
    if k == "pow":
        b = infix(n[1], 4)
        return f"{b}^{n[2]}"
    p = PREC[k]
    s = f"{infix(n[1], p)} {SYM[k]} {infix(n[2], p, True)}"
    if p < parent or (right and p == parent):  # a right child of equal precedence keeps its brackets: a − (b + c)
        return f"({s})"
    return s


def ops_lines(n, out):
    """The older work order: one binary operation per line, results named t1, t2, …"""
    k = n[0]
    if k == "num":
        return n[1]
    if k == "sqrt":
        a = ops_lines(n[1], out)
        out.append(f"t{len(out) + 1} = √({a})")
    elif k == "gcd":
        a, b = ops_lines(n[1], out), ops_lines(n[2], out)
        out.append(f"t{len(out) + 1} = gcd({a}, {b})")
    elif k == "pow":
        a = ops_lines(n[1], out)
        out.append(f"t{len(out) + 1} = {a}^{n[2]}")
    else:
        a, b = ops_lines(n[1], out), ops_lines(n[2], out)
        out.append(f"t{len(out) + 1} = {a} {SYM[k]} {b}")
    return f"t{len(out)}"


def block_lines(tree, places=None):
    suffix = f" to {places} places" if places is not None else ""
    if FMT == "ops" and tree[0] != "num":
        out = []
        ops_lines(tree, out)
        out[-1] += suffix
        return out
    return [infix(tree) + suffix]


def words(n):
    """An expression in words, for the `calc` family's spoken form (one or two operations)."""
    k = n[0]
    if k == "num":
        return n[1]
    a, b = words(n[1]), words(n[2])
    if n[1][0] not in ("num",) and PREC[n[1][0]] < PREC[k]:
        a = f"the sum of {words(n[1][1])} and {words(n[1][2])}" if n[1][0] == "+" else \
            f"the difference of {words(n[1][1])} and {words(n[1][2])}"
    return f"{a} {R.choice(WORD[k])} {b}"


# --- numbers --------------------------------------------------------------------------------------------------------

R = random.Random(0)


def n_int(lo_digits=2, hi_digits=4):
    d = R.randint(lo_digits, hi_digits)
    return R.randint(10 ** (d - 1), 10 ** d - 1)


def n_dec(places=None):
    p = places or R.choice([1, 2, 2, 3])
    return f"{R.randint(1, 999)}.{R.randint(0, 10 ** p - 1):0{p}d}"


def money():
    return f"{R.randint(2, 499)}.{R.choice(['99', '50', '25', '75', '49', '95', f'{R.randint(0, 99):02d}'])}"


def commas(v):
    return f"{int(v):,}" if R.random() < 0.35 else str(v)


def rand_tree(depth, dec=False):
    if depth == 0:
        return num(n_dec() if dec and R.random() < 0.4 else n_int(1 if R.random() < 0.2 else 2, 4))
    op = R.choice(["+", "-", "*", "*", "+", "/"] if not dec else ["+", "-", "*"])
    a, b = rand_tree(R.randrange(depth), dec), rand_tree(R.randrange(depth), dec)
    if op == "/":
        b = num(R.choice([2, 4, 5, 8, 10, 16, 20, 25, 40, 50, 125]) if R.random() < 0.7 else n_int(1, 2))
    return (op, a, b)


# --- reply text ----------------------------------------------------------------------------------------------------

LEAD = ["I'll work it out on the sheet.", "Let me put this on my sheet.", "I'll compute it on the sheet.",
        "Here it is on the sheet.", "Let me do the arithmetic on the sheet.", "On the sheet:", "",
        "I'll write this out on my sheet so every digit is exact.", "Let me calculate that exactly."]


def sheet_reply(lines, cont, lead=None):
    """[(text, loss)] segments; the result lines come from the stand-in runtime."""
    result = sheet_ref.run("\n".join(lines))
    lead = R.choice(LEAD) if lead is None else lead
    head = (lead + "\n\n" if lead else "") + "```sheet\n" + "\n".join(lines) + "\n```"
    last = result[-1][2:]
    if last.startswith("error"):
        raise ValueError(f"stand-in error on {lines}: {result}")
    return [[head, True], ["\n" + "\n".join(result) + "\n", False], [cont(last).replace("….", "…"), True]], last


def ans(v):
    """A value as the continuation quotes it: verbatim, with a word when digits were cut."""
    return v


def cont_calc(expr_text):
    forms = [lambda v: f"So {expr_text} = {v}.", lambda v: f"The result is {v}.", lambda v: f"That comes to {v}.",
             lambda v: f"{expr_text} = {v}."]
    f = R.choice(forms)
    return lambda v: f(v) + (" (The sheet cut the digits there, so the last digit shown is not rounded.)"
                             if v.endswith("…") and R.random() < 0.5 else "")


# --- the calc family -----------------------------------------------------------------------------------------------

CALC_ASK = {
    "train": ["What is {e}?", "Compute {e}.", "Calculate {e}, please.", "{e} = ?", "How much is {e}?",
              "Can you work out {e}?", "what's {e}", "Evaluate {e}.", "Please compute {e}.", "{e}?",
              "Work out {e} for me."],
    "heldout": ["Could you evaluate {e} for me?", "I need the value of {e}.", "Quick one: {e}", "Give me {e}.",
                "What do you get for {e}?"],
}
CALC_SPECIAL = {
    "train": {
        "div_places": ["Divide {a} by {b} to {k} decimal places.", "What is {a} ÷ {b} to {k} places?",
                       "Give {a}/{b} to {k} decimal places.", "{a}/{b} to {k} places, please.",
                       "What's {a} divided by {b}, to {k} decimals?"],
        "sqrt": ["What is the square root of {a} to {k} decimal places?", "Find √{a} to {k} places.",
                 "Square root of {a}, {k} decimals please."],
        "gcd": ["What is the greatest common divisor of {a} and {b}?", "Find gcd({a}, {b}).",
                "What's the GCD of {a} and {b}?"],
        "pow": ["What is {a} to the power {k}?", "Compute {a}^{k}.", "What is {a} raised to the power {k}?",
                "{a} to the power of {k}?"],
        "percent": ["What is {p}% of {a}?", "Find {p} percent of {a}.", "How much is {p}% of {a}?",
                    "Work out {p}% of {a}."],
    },
    "heldout": {
        "div_places": ["I need {a} divided by {b}, correct to {k} decimal places.", "{a} over {b}, {k} places?"],
        "sqrt": ["Can you give me the square root of {a} to {k} decimals?"],
        "gcd": ["What's the largest number that divides both {a} and {b}?"],
        "pow": ["How big is {a} to the power of {k}?"],
        "percent": ["Take {p}% of {a}. What is it?"],
    },
}


def calc_item(split):
    kind = R.choices(["expr", "words", "dec", "div_places", "sqrt", "gcd", "pow", "percent"],
                     [30, 12, 14, 10, 8, 8, 6, 12])[0]
    if kind in ("expr", "words", "dec"):
        if kind == "words":
            tree = rand_tree(R.choice([1, 1, 2]))
            e = words(tree)
        else:
            tree = rand_tree(R.choice([1, 2, 2, 3]), dec=kind == "dec")
            e = infix(tree)
            if R.random() < 0.25:
                e = e.replace("×", "*").replace("÷", "/").replace("−", "-")
        q = R.choice(CALC_ASK[split]).format(e=e)
        lines = block_lines(tree)
        return q, lines, cont_calc(infix(tree)), kind
    t = R.choice(CALC_SPECIAL[split][kind])
    if kind == "div_places":
        a, b, k = n_int(2, 6), n_int(1, 3), R.randint(2, 8)
        tree, places = ("/", num(a), num(b)), k
        return t.format(a=a, b=b, k=k), block_lines(tree, places), lambda v: f"{a} ÷ {b} = {v} to {k} places.", kind
    if kind == "sqrt":
        a, k = R.choice([n_int(1, 2), n_int(2, 4), R.choice([2, 3, 5, 7, 10])]), R.randint(2, 6)
        return t.format(a=a, k=k), block_lines(("sqrt", num(a)), k), lambda v: f"√{a} = {v} to {k} places.", kind
    if kind == "gcd":
        g = R.randint(2, 99)
        a, b = g * R.randint(2, 300), g * R.randint(2, 300)
        return t.format(a=a, b=b), block_lines(("gcd", num(a), num(b))), lambda v: f"The greatest common divisor is {v}.", kind
    if kind == "pow":
        a, k = R.randint(2, 99), R.randint(2, 9)
        return t.format(a=a, k=k), block_lines(("pow", num(a), str(k))), lambda v: f"{a}^{k} = {v}.", kind
    a, p = R.choice([n_int(2, 5), money()]), R.choice([5, 8, 12, 15, 17.5, 20, 25, 33, 7.25, 3])
    tree = ("/", ("*", num(a), num(p)), num(100))
    return t.format(a=a, p=p), block_lines(tree), lambda v: f"{p}% of {a} is {v}.", kind


# --- the prose family: an expression typed inside mixed text -------------------------------------------------------

PROSE = {
    "train": ["In my notes I have {e}. What does it come to?",
              "My spreadsheet formula is {e} and I want to double-check the total.",
              "I'm writing a budget memo. The line item is {e}; what number should I put?",
              "Homework says: simplify {e}. Can you give me the number?",
              "The invoice shows {e} — what's the final figure?",
              "Before the meeting I need the value of {e}, then a one-line summary of it.",
              "Hey! Random question while I cook: {e}?",
              "My kid wrote {e} on a worksheet. What's the right answer?",
              "For the report, total = {e}. Can you fill in the total?",
              "Is {e} more or less than 10000? Give me the number too.",
              "I keep getting different answers for {e}. Which is right?",
              "Translate this into a value: {e}."],
    "heldout": ["The whiteboard after the meeting just says {e}. What is that equal to?",
                "Sanity check for my lab notebook: {e} = ?",
                "I copied {e} from the textbook margin; what's the number?",
                "Our team's estimate was {e}. What figure does that give?",
                "Can you tell me what {e} works out to, and whether it's a whole number?",
                "A friend texted me {e} and asked for the answer. Help?"],
}


def prose_item(split):
    tree = rand_tree(R.choice([2, 2, 3]), dec=R.random() < 0.3)
    e = infix(tree)
    if R.random() < 0.3:
        e = e.replace("×", "*").replace("÷", "/").replace("−", "-")
    q = R.choice(PROSE[split]).format(e=e)

    def cont(v):
        s = f"So {infix(tree)} = {v}."
        if "more or less than 10000" in q:
            s += " That is " + ("more" if Fraction(v.rstrip("…")) > 10000 else "less") + " than 10000."
        if "whole number" in q:
            s += " It is " + ("" if Fraction(v.rstrip("…")).denominator == 1 and not v.endswith("…") else "not ") + \
                 "a whole number."
        if "summary" in q:
            s += f" In one line: the expression evaluates to {v}."
        return s

    return q, block_lines(tree), cont, "prose"


# --- the word family -----------------------------------------------------------------------------------------------
# each: (question, tree builder, answer sentence); numbers drawn per item

def W(q, tree, sent, **draw):
    return (q, tree, sent, draw)


I2, I3, I4 = (lambda: R.randint(11, 99)), (lambda: R.randint(100, 999)), (lambda: R.randint(1000, 9999))
S1 = lambda: R.randint(3, 40)  # noqa: E731
M = lambda: money()  # noqa: E731

WORDS = {
    "train": [
        W("A farmer packs {a} crates with {b} apples each and sells {c} apples. How many apples are left?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "{v} apples are left.", a=S1, b=I2, c=I3),
        W("Tickets cost {b} dollars. A school buys {a} tickets and pays a {c} dollar fee. What is the total?",
          lambda a, b, c: ("+", ("*", num(a), num(b)), num(c)), "The total is {v} dollars.", a=I2, b=I2, c=I2),
        W("A train covers {b} km every hour for {a} hours, then {c} km more. How far does it go?",
          lambda a, b, c: ("+", ("*", num(a), num(b)), num(c)), "It goes {v} km.", a=S1, b=I2, c=I3),
        W("{a} friends each give {b} dollars, and then {c} dollars are spent. How much money remains?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "{v} dollars remain.", a=S1, b=I2, c=I2),
        W("A library has {a} shelves with {b} books on each. {c} books are checked out. How many are on the shelves?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "{v} books are on the shelves.", a=I2, b=I2, c=I3),
        W("A bakery makes {a} trays of {b} cookies and packs them into boxes of {c}. How many boxes?",
          lambda a, b, c: ("/", ("*", num(a), num(b)), num(c)), "That makes {v} boxes.", a=S1, b=I2,
          c=lambda: R.choice([2, 4, 5, 8, 10, 12])),
        W("I bought {a} notebooks at ${b} each and a pen for ${c}. How much did I spend?",
          lambda a, b, c: ("+", ("*", num(a), num(b)), num(c)), "You spent ${v}.", a=lambda: R.randint(2, 12), b=M, c=M),
        W("A jacket costs ${a}. It is on sale for {p}% off. What is the sale price?",
          lambda a, p: ("-", num(a), ("/", ("*", num(a), num(p)), num(100))), "The sale price is ${v}.", a=M,
          p=lambda: R.choice([10, 15, 20, 25, 30, 40])),
        W("A meal costs ${a} and I leave a {p}% tip. What do I pay in total?",
          lambda a, p: ("+", num(a), ("/", ("*", num(a), num(p)), num(100))), "You pay ${v} in total.", a=M,
          p=lambda: R.choice([15, 18, 20, 22])),
        W("A tank holds {a} liters. {b} liters leak out each day for {c} days. How much is left?",
          lambda a, b, c: ("-", num(a), ("*", num(b), num(c))), "{v} liters are left.", a=I4, b=I2,
          c=lambda: R.randint(2, 30)),
        W("A rectangle is {a} m long and {b} m wide. What is its area?",
          lambda a, b: ("*", num(a), num(b)), "The area is {v} square meters.", a=I2, b=I2),
        W("A rectangular garden is {a} m by {b} m. How much fencing goes around it?",
          lambda a, b: ("*", num(2), ("+", num(a), num(b))), "It needs {v} m of fencing.", a=I2, b=I2),
        W("{a} people share a bill of ${b} equally. How much does each pay?",
          lambda a, b: ("/", num(b), num(a)), "Each pays ${v}.", a=lambda: R.choice([2, 4, 5, 8]), b=M),
        W("A car uses {a} liters of fuel per 100 km. How much fuel for {b} km?",
          lambda a, b: ("/", ("*", num(a), num(b)), num(100)), "It needs {v} liters.", a=lambda: R.choice(
              ["5.5", "6.2", "7", "8.4", "9.1"]), b=I3),
        W("A factory makes {a} parts an hour for {b} hours a day, {c} days a week. How many parts a week?",
          lambda a, b, c: ("*", ("*", num(a), num(b)), num(c)), "It makes {v} parts a week.", a=I3,
          b=lambda: R.randint(6, 12), c=lambda: R.randint(4, 7)),
        W("A school has {a} classes of {b} students and {c} teachers. How many people is that?",
          lambda a, b, c: ("+", ("*", num(a), num(b)), num(c)), "That is {v} people.", a=S1, b=I2, c=I2),
        W("I had ${a} in my account, paid rent of ${b} and got paid ${c}. What is my balance?",
          lambda a, b, c: ("+", ("-", num(a), num(b)), num(c)), "Your balance is ${v}.", a=M, b=M, c=M),
        W("A recipe needs {a} g of flour per batch. How much flour for {b} batches, minus the {c} g already in the bowl?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "You need {v} g more.", a=I3, b=S1, c=I3),
        W("An app had {a} users. It gained {b} a day for {c} days and lost {d}. How many users now?",
          lambda a, b, c, d: ("-", ("+", num(a), ("*", num(b), num(c))), num(d)), "It has {v} users now.",
          a=I4, b=I3, c=S1, d=I3),
        W("A runner does {a} laps of a {b} m track. How many kilometers is that?",
          lambda a, b: ("/", ("*", num(a), num(b)), num(1000)), "That is {v} km.", a=S1, b=I3),
        W("A box weighs {a} kg empty and holds {b} items of {c} kg each. What is the full weight?",
          lambda a, b, c: ("+", num(a), ("*", num(b), num(c))), "The full box weighs {v} kg.", a=lambda: n_dec(1),
          b=S1, c=lambda: n_dec(2)),
        W("Population was {a} and grew by {p}%. What is it now?",
          lambda a, p: ("+", num(a), ("/", ("*", num(a), num(p)), num(100))), "It is now {v}.", a=I4,
          p=lambda: R.choice([2, 3, 4, 5, 8, 10, 12])),
        W("A printer prints {a} pages a minute. How many minutes for {b} pages? Give it to 2 decimal places.",
          lambda a, b: ("/", num(b), num(a)), "It takes {v} minutes.", a=I2, b=I4, places=2),
        W("Three numbers are {a}, {b} and {c}. What is their average?",
          lambda a, b, c: ("/", ("+", ("+", num(a), num(b)), num(c)), num(3)), "Their average is {v}.",
          a=I3, b=I3, c=I3),
        W("A store sells {a} shirts at ${b} and {c} hats at ${d}. What is the revenue?",
          lambda a, b, c, d: ("+", ("*", num(a), num(b)), ("*", num(c), num(d))), "The revenue is ${v}.",
          a=I2, b=M, c=I2, d=M),
        W("A warehouse can hold {c} kg. It already stores {a} sacks of {b} kg. How much more can it hold?",
          lambda a, b, c: ("-", num(c), ("*", num(a), num(b))), "It can hold {v} kg more.", a=I2, b=I2,
          c=lambda: R.randint(5000, 30000)),
        W("I have ${c} and buy {a} items at ${b} each. How much money do I have left?",
          lambda a, b, c: ("-", num(c), ("*", num(a), num(b))), "You have ${v} left.", a=lambda: R.randint(2, 9),
          b=M, c=lambda: R.randint(1000, 9000)),
        W("A coat costs ${a}. It is {p}% off, and delivery adds ${b}. What do I pay?",
          lambda a, p, b: ("+", ("-", num(a), ("/", ("*", num(a), num(p)), num(100))), num(b)), "You pay ${v}.",
          a=M, p=lambda: R.choice([5, 10, 15, 20, 30, 35]), b=M),
        W("A {a} m roll of ribbon is cut into pieces of {b} m. How many pieces?",
          lambda a, b: ("/", num(a), num(b)), "That gives {v} pieces.", a=I3,
          b=lambda: R.choice(["0.5", "0.25", "2", "4", "5", "1.25"])),
    ],
    "heldout": [
        W("A beekeeper has {a} hives, each producing {b} kg of honey. She sells {c} kg. How much honey does she keep?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "She keeps {v} kg.", a=S1, b=I2, c=I2),
        W("A concert hall has {a} rows of {b} seats; {c} seats are broken. How many seats can be sold?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "{v} seats can be sold.", a=I2, b=I2, c=I2),
        W("A cyclist rides {a} km on Monday, {b} km on Tuesday and {c} km on Wednesday. What is the total distance?",
          lambda a, b, c: ("+", ("+", num(a), num(b)), num(c)), "The total is {v} km.", a=I2, b=I2, c=I3),
        W("Each crate holds {a} bottles. A shop orders {b} crates and {c} loose bottles. How many bottles arrive?",
          lambda a, b, c: ("+", ("*", num(a), num(b)), num(c)), "{v} bottles arrive.", a=I2, b=I2, c=I2),
        W("A phone plan costs ${a} a month plus a ${b} activation fee. What does a year cost?",
          lambda a, b: ("+", ("*", num(12), num(a)), num(b)), "A year costs ${v}.", a=M, b=M),
        W("A pool holds {a} liters and a hose fills {b} liters a minute. How many minutes to fill it?",
          lambda a, b: ("/", num(a), num(b)), "It takes {v} minutes.", a=lambda: R.randint(100, 999) * 100,
          b=lambda: R.choice([4, 5, 8, 10, 16, 20, 25, 40])),
        W("A laptop priced at ${a} gets a {p}% discount and then ${b} shipping is added. What is the final price?",
          lambda a, p, b: ("+", ("-", num(a), ("/", ("*", num(a), num(p)), num(100))), num(b)),
          "The final price is ${v}.", a=M, p=lambda: R.choice([10, 15, 20, 25]), b=M),
        W("A field is {a} m by {b} m and seed costs ${c} per square meter. What does seeding it cost?",
          lambda a, b, c: ("*", ("*", num(a), num(b)), num(c)), "It costs ${v}.", a=I2, b=I2,
          c=lambda: R.choice(["0.25", "0.4", "1.2", "0.75"])),
        W("A charity collected ${a} and splits it equally among {b} shelters. How much does each get?",
          lambda a, b: ("/", num(a), num(b)), "Each shelter gets ${v}.", a=I4, b=lambda: R.choice([4, 5, 8, 10, 16])),
        W("A worker earns ${a} an hour, works {b} hours, and pays ${c} in fees. What does the worker take home?",
          lambda a, b, c: ("-", ("*", num(a), num(b)), num(c)), "The worker takes home ${v}.", a=M, b=S1, c=M),
        W("A truck carries {a} boxes of {b} kg each. Its limit is {c} kg. How many kg under the limit is it?",
          lambda a, b, c: ("-", num(c), ("*", num(a), num(b))), "It is {v} kg under the limit.", a=I2, b=I2,
          c=lambda: R.randint(10000, 20000)),
        W("Snow fell {a} cm, {b} cm and {c} cm on three days, then {d} cm melted. How deep is it now?",
          lambda a, b, c, d: ("-", ("+", ("+", num(a), num(b)), num(c)), num(d)), "It is {v} cm deep.",
          a=lambda: n_dec(1), b=lambda: n_dec(1), c=lambda: n_dec(1), d=lambda: R.randint(1, 50)),
    ],
}


def word_item(split):
    q, tb, sent, draw = R.choice(WORDS[split])
    places = draw.get("places")
    vals = {k: (f() if callable(f) else f) for k, f in draw.items() if k != "places"}
    tree = tb(**vals)
    lines = block_lines(tree, places)
    if FMT == "expr" and R.random() < 0.15 and tree[0] in "+-*/" and tree[1][0] != "num":
        lines = [f"a = {infix(tree[1])}", infix((tree[0], ("num", "a"), tree[2]))]  # a named step
    return q.format(**vals), lines, lambda v: sent.format(v=v), "word"


# --- the equation family --------------------------------------------------------------------------------------------

EQ_ASK = {
    "train": {"solve": ["Solve {q}.", "Find x: {q}", "What value of x satisfies {q}?", "Solve for x: {q}",
                        "{q}. What is x?", "Please solve {q}.", "Help me find x: {q}", "{q}. Solve for x, please."],
              "system": ["Solve the system {q}.", "Find x and y: {q}", "Solve {q} for x and y."],
              "expand": ["Expand {q}.", "Multiply out {q}.", "What is {q} expanded?"],
              "factor": ["Factor {q}.", "Factorise {q}.", "Can you factor {q}?"]},
    "heldout": {"solve": ["Can you help me solve {q}?", "{q} — what's x?", "I'm stuck on {q}. What is x?"],
                "system": ["I have two equations, {q}. What are x and y?"],
                "expand": ["Write {q} out as a polynomial."],
                "factor": ["Break {q} into factors."]},
}


def lin_side():
    a, b = R.randint(2, 12), R.randint(1, 60)
    return R.choice([f"{a}x + {b}", f"{a}x − {b}", f"{a}(x + {b})", f"{a}(x − {b})", f"{b} − {a}x",
                     f"{a}(x − {b}) + {R.randint(1, 30)}", f"{b}", f"{a}x"])


def lin2(a, b, r):
    """a x + b y = r, written the way a person types it."""
    def term(c, v, first):
        mag = "" if abs(c) == 1 else str(abs(c))
        sign = ("−" if c < 0 else "") if first else (" − " if c < 0 else " + ")
        return f"{sign}{mag}{v}"
    return f"{term(a, 'x', True)}{term(b, 'y', False)} = {r}".replace("-", "−")


def sq(t):
    return t.replace("^2", "²") if R.random() < 0.3 else t


def eq_item(split):
    kind = R.choices(["linear", "quadratic", "system", "expand", "factor"], [40, 25, 15, 10, 10])[0]
    t = R.choice(EQ_ASK[split]["solve" if kind in ("linear", "quadratic") else kind])
    if kind == "linear":
        while True:
            L, Rt = lin_side(), lin_side()
            q = f"{L} = {Rt}"
            if "x" in q and sheet_ref.run("solve " + q)[0].startswith("= x ="):
                break
        typed, line = q, "solve " + q
    elif kind == "quadratic":
        r1, r2, a = R.randint(-12, 12), R.randint(-12, 12), R.choice([1, 1, 1, 2, 3])
        if R.random() < 0.25:
            b, c = R.randint(-9, 9), R.randint(-20, 20)
        else:
            b, c = -a * (r1 + r2), a * r1 * r2
        lhs = sheet_ref.poly_text([c, b, a])
        q = R.choice([f"{lhs} = 0", f"{sheet_ref.poly_text([0, b, a])} = {-c}" if b or a else f"{lhs} = 0"])
        if R.random() < 0.2:
            q = f"(x − {r1})(x + {r2}) = 0".replace("− -", "+ ").replace("+ -", "− ")
        typed = sq(q.replace("-", "−"))
        line = "solve " + q.replace("-", "−")
    elif kind == "system":
        x, y = R.randint(-9, 12), R.randint(-9, 12)
        a, b, c, d = (R.choice([v for v in range(-6, 8) if v]) for _ in range(4))
        if a * d == b * c:
            d = d + 1 if d != -1 else 2
        e1, e2 = lin2(a, b, a * x + b * y), lin2(c, d, c * x + d * y)
        q = f"{e1}, {e2}"
        typed = f"{e1} and {e2}" if R.random() < 0.6 else q
        line = "solve " + q
    elif kind == "expand":
        a, b, e = R.choice([1, 1, 2, 3]), R.randint(-9, 9) or 1, R.randint(2, 6)
        inner = sheet_ref.poly_text([b, a])
        q = R.choice([f"({inner})^{e}", f"({inner})({sheet_ref.poly_text([R.randint(-9, 9) or 2, R.choice([1, 2])])})"])
        typed, line = sq(q.replace("-", "−")), "expand " + q.replace("-", "−")
    else:
        roots = [R.randint(-9, 9) for _ in range(R.choice([2, 2, 3]))]
        c = [1]
        for r in roots:
            c = [(c[i - 1] if i else 0) - r * (c[i] if i < len(c) else 0) for i in range(len(c) + 1)]
        q = sheet_ref.poly_text(c)
        typed, line = sq(q.replace("-", "−")), "factor " + q.replace("-", "−")
    question = t.format(q=typed)

    def cont(v):
        if kind in ("linear", "quadratic"):
            if v.startswith("x = ") and "±" not in v and "," in v:
                return f"So x = {v[4:].replace(', ', ' or x = ')}."
            if v.startswith("x = ") and "±" in v:
                return f"So {v.split(';')[0]}, which is about " + " or ".join(
                    b.strip("[] ").split(",")[0] for b in v.split("bounds ")[1].split("], [")) + "."
            return f"So {v}." if v.startswith("x =") else f"So the equation has {v}." if v == "no real roots" else \
                f"The answer: {v}."
        if kind == "system":
            return f"So {v}."
        if kind == "expand":
            return f"So {typed} = {v}."
        fac = v.split("factors ")[1].split(";")[0]
        rem = v.split("remaining ")[1].split(".")[0]
        return f"So {typed} = {fac if rem == '1' else fac + '(' + rem + ')'}."

    return question, [line], cont, kind


# --- distractors ------------------------------------------------------------------------------------------------------

CHITCHAT = {"train": ["hi!", "Hello, how are you today?", "Tell me a joke.", "What's your name?", "Thanks a lot!",
                      "Good morning! Any tips for staying focused?", "I'm bored. Suggest something fun.",
                      "Can you recommend a good book?", "What do you like to talk about?", "Say something nice.",
                      "How's the weather where you are?", "I just got a puppy!"],
            "heldout": ["hey there", "What should I cook tonight?", "I had a long day.", "Do you like music?",
                        "Give me a fun fact."]}
FACTS = {"train": ["What is the capital of France?", "Who wrote Pride and Prejudice?", "How many legs does a spider have?",
                   "What year did the Berlin Wall fall?", "What is photosynthesis?", "Who painted the Mona Lisa?",
                   "How many continents are there?", "What is the tallest mountain on Earth?",
                   "What is the chemical symbol for gold?", "Why is the sky blue?", "How many days are in a leap year?",
                   "When did the first person walk on the Moon?", "What is DNA?", "Who was Ada Lovelace?"],
         "heldout": ["What is the capital of Japan?", "How many players are on a soccer team?",
                     "Who discovered penicillin?", "What causes the seasons?", "How many sides does a hexagon have?"]}
WRITING = {"train": ["Write a haiku about autumn.", "Write a short poem about the sea.",
                     "Write a two-sentence horror story.", "Write a polite email declining a meeting.",
                     "Give me three slogans for a coffee shop.", "Describe a sunset in one paragraph.",
                     "Write a limerick about a cat.", "Summarize the plot of Romeo and Juliet in three sentences."],
           "heldout": ["Write a short poem about numbers.", "Write a thank-you note to a teacher.",
                       "Write a four-line poem about rain."]}
CODE = {"train": ["Write a Python function that reverses a string.", "What does `git rebase` do?",
                  "Write a SQL query that counts the rows in a table called orders.",
                  "How do I read a file line by line in Python?", "Explain what a for loop is.",
                  "Write a JavaScript function that returns the largest number in an array.",
                  "What is the difference between a list and a tuple in Python?"],
        "heldout": ["Write a Python function that checks whether a number is even.",
                    "What does HTTP 404 mean?", "How do I sort a list in Python?"]}
MATHTALK = {"train": ["What is a prime number?", "Explain the Pythagorean theorem.", "What is a derivative, intuitively?",
                      "Why can't you divide by zero?", "What is the difference between mean and median?",
                      "What does 'percent' mean?", "Is zero even or odd?"],
            "heldout": ["What is a fraction?", "What is an integer?", "What does it mean for a number to be irrational?"]}
SINGLE = {"train": ["What is {a} + {b}?", "what's {a} times {b}", "{a} minus {b}?", "Quick: {a} × {b}",
                    "What is {a} plus {b}?", "How much is {a} × {b}?", "{a} + {b} = ?", "{a} × {b} = ?",
                    "What is {a} − {b}?"],
          "heldout": ["Tell me {a} + {b}.", "What's {a} times {b}?", "{a} − {b} = ?"]}


def single_item(split):
    a, b = R.randint(1, 9), R.randint(1, 9)
    t = R.choice(SINGLE[split])
    if ("minus" in t or "−" in t) and b > a:
        a, b = b, a
    q = t.format(a=a, b=b)
    v = a + b if ("+" in t or "plus" in t) else a * b if ("×" in t or "times" in t) else a - b
    return q, v


def distract_items(split, n, rng):
    out = []
    pools = [("chitchat", CHITCHAT), ("facts", FACTS), ("writing", WRITING), ("code", CODE), ("mathtalk", MATHTALK)]
    for i in range(n):
        r = rng.random()
        if r < 0.22:
            q, v = single_item(split)
            out.append({"sub": "single", "prompt": q, "single_value": v})
        elif r < 0.62:
            name, pool = rng.choice(pools)
            out.append({"sub": name, "prompt": rng.choice(pool[split])})
        else:
            out.append({"sub": "no_robots", "prompt": None})  # filled from the hub by stock_replies.py
    return out


# --- assembly ---------------------------------------------------------------------------------------------------------

MAKERS = {"calc": calc_item, "prose": prose_item, "word": word_item, "equation": eq_item}


def leaves(n):
    return [n[1]] if n[0] == "num" else [x for c in n[1:] if isinstance(c, tuple) for x in leaves(c)]


def mental(lines):
    """Single-digit + − × with at most one operation: mental arithmetic, a distractor, never a sheet line."""
    if len(lines) != 1 or any(w in lines[0] for w in ("÷", "/", "√", "gcd", "^", "solve", "expand", "factor", "places")):
        return False
    nums = [t for t in lines[0].replace("(", " ").replace(")", " ").split() if t[0].isdigit()]
    return all(len(t) == 1 for t in nums) and len(nums) <= 2


def sheet_dialogue(fam, split):
    for _ in range(50):
        try:
            q, lines, cont, sub = MAKERS[fam](split)
            if mental(lines):
                continue
            segs, last = sheet_reply(lines, cont)
            truth = sheet_ref.value("\n".join(lines))
            return {"family": fam, "sub": sub, "split": split, "needs_sheet": True, "user": q, "lines": lines,
                    "result": last, "truth": str(truth) if truth is not None else None, "segments": segs}
        except (ValueError, ZeroDivisionError, sheet_ref.SheetError, KeyError):
            continue
    raise RuntimeError(fam)


def main():
    global FMT
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--heldout", type=int, default=120, help="held-out items per sheet family")
    ap.add_argument("--format", default="expr", choices=["expr", "ops"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--replies-from", help="train_full.jsonl of an earlier build: keep its distractor dialogues and "
                    "stock replies (and its held-out file), regenerate only the sheet dialogues")
    a = ap.parse_args()
    FMT = a.format
    R.seed(a.seed)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n_dis = round(a.n * 0.3)
    n_sheet = a.n - n_dis
    mix = {"calc": 0.24, "prose": 0.2, "word": 0.34, "equation": 0.22}
    train = []
    for fam, f in mix.items():
        train += [sheet_dialogue(fam, "train") for _ in range(round(n_sheet * f))]
    if a.replies_from:
        old = [json.loads(line) for line in open(a.replies_from)]
        train += [d for d in old if d["family"] == "distract"]
        for _ in range(150):  # symbol-form single-digit questions, answered in stock's own style (`3 + 4 = 7`)
            t = R.choice(["{a} + {b} = ?", "{a} × {b} = ?", "What is {a} − {b}?"])
            x, y = R.randint(1, 9), R.randint(1, 9)
            if "−" in t and y > x:
                x, y = y, x
            v = x + y if "+" in t else x * y if "×" in t else x - y
            op = "+" if "+" in t else "×" if "×" in t else "−"
            train.append({"family": "distract", "sub": "single", "split": "train", "needs_sheet": False,
                          "user": t.format(a=x, b=y), "single_value": v, "segments": None,
                          "reply": f"{x} {op} {y} = {v}", "reply_finished": True})
    else:
        dis = distract_items("train", n_dis, R)
        for i, d in enumerate(dis):
            train.append({"family": "distract", "sub": d["sub"], "split": "train", "needs_sheet": False,
                          "user": d["prompt"], "single_value": d.get("single_value"), "segments": None})
    # two-turn dialogues: 15% get an earlier exchange (a distractor or another sheet dialogue) as context
    for d in train:
        if a.replies_from and d["family"] == "distract":
            continue  # keeps its own earlier turn, already answered
        if R.random() < 0.15:
            if R.random() < 0.5:
                h = sheet_dialogue(R.choice(list(mix)), "train")
                d["history"] = {"user": h["user"], "assistant": "".join(t for t, _ in h["segments"])}
            elif a.replies_from:
                h = R.choice([x for x in train if x["family"] == "distract" and x.get("reply_finished")])
                d["history"] = {"user": h["user"], "assistant": h["reply"]}
            else:
                h = distract_items("train", 1, R)[0]
                d["history"] = {"user": h["prompt"], "assistant": None, "sub": h["sub"],
                                "single_value": h.get("single_value")}
    R.shuffle(train)
    held = [sheet_dialogue(fam, "heldout") for fam in mix for _ in range(a.heldout)]
    if a.format == "expr":
        held += [sheet_dialogue("word", "heldout") for _ in range(a.heldout // 2)]  # word problems are registered at 0.9
    hd = distract_items("heldout", 2 * a.heldout, R)
    held += [{"family": "distract", "sub": d["sub"], "split": "heldout", "needs_sheet": False, "user": d["prompt"],
              "single_value": d.get("single_value"), "segments": None} for d in hd]
    for i, d in enumerate(train):
        d["id"] = f"t{i}"
    for i, d in enumerate(held):
        d["id"] = f"h{i}"
    sfx = "" if a.format == "expr" else "_ops"
    if a.replies_from:
        sfx += "_full"
        held = [json.loads(line) for line in open(pathlib.Path(a.replies_from).parent / "heldout_full.jsonl")]
    with open(out / f"train{sfx}.jsonl", "w") as f:
        for d in train:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with open(out / f"heldout{sfx}.jsonl", "w") as f:
        for d in held:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    count = {}
    for d in train:
        count[d["family"]] = count.get(d["family"], 0) + 1
    print(json.dumps({"train": len(train), "by_family": count, "heldout": len(held)}))


if __name__ == "__main__":
    main()
