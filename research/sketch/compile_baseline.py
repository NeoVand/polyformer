"""Can the untouched 0.8B write the page's plan? A $0 baseline for the language half (the compile step).

Three synthetic tasks, scored by running what the model writes, never by string match:
  plan     an arithmetic expression -> one binary operation per line (`t1 = 1234 - 567`), the sheet's work order
  equation a linear equation -> the same expression with x replaced by 0 and by 1 (algebra by evaluation needs no more)
  word     a word problem from templates -> one expression
Few-shot, greedy, chat template with thinking off. With an adapter path, the same with the E6 adapter on.

  python compile_baseline.py [adapter]       # writes compile_baseline.json and prints the rates
"""

import json
import random
import re
import sys

import torch
from transformers import AutoProcessor

import e2_column as e2

rng = random.Random(0)
proc = AutoProcessor.from_pretrained(e2.PATH)
tok = proc.tokenizer
model = e2.load_base().eval()
if len(sys.argv) > 1:
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, sys.argv[1]).eval()

SAFE = re.compile(r'^[\d\s+\-*/().x]+$')


def ev(expr, x=None):
    e = expr.replace('×', '*').replace('÷', '/').replace('−', '-')
    if x is not None:
        e = re.sub(r'(\d)\s*x', r'\1*x', e).replace('x', f'({x})')
    e = re.sub(r'(\d|\))\s*\(', r'\1*(', e)  # 3(x + 4) and (a)(b): implicit products
    if not SAFE.match(e.replace('x', '')):
        raise ValueError(expr)
    return eval(e, {'__builtins__': {}})


def gen(prompt, n=160):
    msgs = [{'role': 'user', 'content': prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = tok(text, return_tensors='pt').to(e2.dev)
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=n, do_sample=False)
    return tok.decode(out[0, ids['input_ids'].shape[1]:], skip_special_tokens=True).strip()


def rnd_expr(depth=2):
    if depth == 0:
        return str(rng.randrange(2, 10 ** rng.randrange(1, 5)))
    a, b = rnd_expr(depth - 1), rnd_expr(rng.randrange(depth))
    op = rng.choice(['+', '-', '×'])
    s = f'{a} {op} {b}'
    return f'({s})' if rng.random() < 0.5 else s


PLAN_SHOT = """Write the work order for a sheet that can only do one + - × or ÷ of two numbers per line.
Name each result t1, t2, ... and use earlier results by name. Write only the lines.

Problem: 3 × (45 - 7) + 12
t1 = 45 - 7
t2 = 3 × t1
t3 = t2 + 12

Problem: (120 + 35) × (9 - 4)
t1 = 120 + 35
t2 = 9 - 4
t3 = t1 × t2

Problem: {p}
"""


def first_answer(text):
    """the model's first answer only: stop at a blank line or where it starts another example"""
    out = []
    for line in text.strip().splitlines():
        if not line.strip() or re.match(r'\s*(Problem|Equation|Question)\b', line):
            break
        out.append(line)
    return '\n'.join(out)


def run_plan(text):
    env = {}
    last = None
    for line in first_answer(text).splitlines():
        m = re.match(r'\s*(t\d+)\s*=\s*(\S+)\s*([+\-×*/÷−])\s*(\S+)\s*$', line)
        if not m:
            continue
        name, a, op, b = m.groups()
        va, vb = (env[a] if a in env else int(a)), (env[b] if b in env else int(b))
        env[name] = {'+': va + vb, '-': va - vb, '−': va - vb, '×': va * vb, '*': va * vb}[op]
        last = env[name]
    return last


EQ_SHOT = """For the equation, write its left side and its right side twice: once with x replaced by 0, once with x replaced by 1.

Equation: 4(x + 3) - 5 = 2x + 9
L0 = 4 × (0 + 3) - 5
R0 = 2 × 0 + 9
L1 = 4 × (1 + 3) - 5
R1 = 2 × 1 + 9

Equation: {p}
"""


def rnd_eq():
    a, b, c = rng.randrange(2, 10), rng.randrange(1, 20), rng.randrange(1, 50)
    d, e = rng.randrange(1, 10), rng.randrange(1, 100)
    form = rng.choice([f'{a}(x + {b}) - {c} = {d}x + {e}', f'{a}x + {c} = {e} - {d}x',
                       f'{a}(x - {b}) = {d}(x + {c}) + {e}'])
    L, R = form.split(' = ')
    return form, [ev(L, 0), ev(R, 0), ev(L, 1), ev(R, 1)]


def run_eq(text):
    vals = {}
    for line in first_answer(text).splitlines():
        m = re.match(r'\s*([LR][01])\s*=\s*(.+)$', line)
        if m:
            try:
                vals[m.group(1)] = ev(m.group(2))
            except Exception:
                pass
    return [vals.get(k) for k in ('L0', 'R0', 'L1', 'R1')]


WORD_SHOT = """Write one arithmetic expression whose value answers the question. Write only the expression.

Question: A shelf has 7 rows of 24 books and 13 more on top. How many books?
Expression: 7 × 24 + 13

Question: {p}
Expression:"""

TEMPLATES = [
    (lambda a, b, c: f'A farmer packs {a} crates with {b} apples each and sells {c} apples. How many apples are left?',
     lambda a, b, c: a * b - c),
    (lambda a, b, c: f'Tickets cost {b} dollars. A school buys {a} tickets and pays a {c} dollar fee. What is the total?',
     lambda a, b, c: a * b + c),
    (lambda a, b, c: f'A train covers {b} km every hour for {a} hours, then {c} km more. How far does it go?',
     lambda a, b, c: a * b + c),
    (lambda a, b, c: f'{a} friends each give {b} dollars and then {c} dollars are spent. How much money remains?',
     lambda a, b, c: a * b - c),
    (lambda a, b, c: f'A wall has {a} rows of {b} bricks. {c} bricks are missing. How many bricks are there?',
     lambda a, b, c: a * b - c),
]


SAMPLES = []


def keep(task, prompt, out, right):
    SAMPLES.append({'task': task, 'problem': prompt, 'output': out, 'right': bool(right)})
    return bool(right)


def main():
    res = {}
    n = 60
    ok = 0
    for _ in range(n):
        p = rnd_expr(2)
        out = gen(PLAN_SHOT.format(p=p))
        try:
            right = run_plan(out) == ev(p)
        except Exception:
            right = False
        ok += keep('plan', p, out, right)
    res['plan'] = f'{ok}/{n}'
    ok = 0
    for _ in range(n):
        form, want = rnd_eq()
        out = gen(EQ_SHOT.format(p=form))
        ok += keep('equation', form, out, run_eq(out) == want)
    res['equation'] = f'{ok}/{n}'
    ok = 0
    for i in range(n):
        t, f = TEMPLATES[i % len(TEMPLATES)]
        a, b, c = rng.randrange(3, 40), rng.randrange(11, 300), rng.randrange(2, 99)
        full = gen(WORD_SHOT.format(p=t(a, b, c)), 40)
        out = (full.splitlines() or [''])[0]
        try:
            right = ev(out.replace('Expression:', '').strip()) == f(a, b, c)
        except Exception:
            right = False
        ok += keep('word', t(a, b, c), full, right)
    res['word'] = f'{ok}/{n}'
    res['adapter'] = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(res))
    with open('compile_baseline.json', 'a') as fh:
        fh.write(json.dumps(res) + '\n')
    with open('compile_samples.jsonl', 'a') as fh:
        for x in SAMPLES:
            fh.write(json.dumps({**x, 'adapter': res['adapter']}) + '\n')


main()
