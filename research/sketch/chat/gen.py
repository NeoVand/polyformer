"""Batched chat generation for the CHAT stream, with the sheet runtime in the loop.

`chat_prefix` renders a conversation with the model's chat template (thinking off) and returns token ids. `generate`
runs greedy, left-padded batches. `converse` is the page's protocol: the model writes until it closes a ```sheet block
(the token "```" after an opening "```sheet"), the runtime appends its result lines `\\n= …\\n` as tokens (here the
host stand-in sheet_ref.run, said as such wherever it is scored), and the model goes on, up to `rounds` blocks.
"""

import re

import torch

OPEN = "```sheet"


def chat_prefix(tok, messages):
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return tok(text, add_special_tokens=False)["input_ids"]


def closed_block(text):
    """The work order if the text ends by closing a ```sheet block, else None."""
    i = text.rfind(OPEN)
    if i < 0 or not text.rstrip().endswith("```"):
        return None
    body = text[i + len(OPEN):]
    body = body[: body.rstrip().rfind("```")]
    if "```" in body:
        return None
    return body.strip("\n")


class StopAtFence:
    """Per-sequence stopping: a closed sheet block, or the end-of-turn token."""

    def __init__(self, tok, start, eos_ids):
        self.tok, self.start, self.eos = tok, start, set(eos_ids)
        self.fence = {i for i in range(len(tok)) if tok.decode([i]).strip() == "```"} if not hasattr(tok, "_fence") \
            else tok._fence
        tok._fence = self.fence

    def __call__(self, input_ids, scores, **kw):
        done = []
        for row in input_ids:
            last = int(row[-1])
            if last in self.eos:
                done.append(True)
            elif last in self.fence:
                done.append(closed_block(self.tok.decode(row[self.start:].tolist())) is not None)
            else:
                done.append(False)
        return torch.tensor(done, device=input_ids.device)


@torch.no_grad()
def generate(model, tok, prompts, max_new=512, batch=48, stop_at_fence=False):
    """Greedy continuations (lists of new token ids, trailing pads removed) for a list of token-id prompts."""
    from transformers import StoppingCriteriaList

    dev = next(model.parameters()).device
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    eos = [tok.convert_tokens_to_ids("<|im_end|>"), tok.eos_token_id]
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))  # similar lengths per batch
    out = [None] * len(prompts)
    for k in range(0, len(order), batch):
        idx = order[k : k + batch]
        L = max(len(prompts[i]) for i in idx)
        ids = torch.full((len(idx), L), pad, dtype=torch.long)
        mask = torch.zeros((len(idx), L), dtype=torch.long)
        for r, i in enumerate(idx):
            p = prompts[i]
            ids[r, L - len(p):] = torch.tensor(p)
            mask[r, L - len(p):] = 1
        kw = {}
        if stop_at_fence:
            kw["stopping_criteria"] = StoppingCriteriaList([StopAtFence(tok, L, eos)])
        g = model.generate(input_ids=ids.to(dev), attention_mask=mask.to(dev), max_new_tokens=max_new,
                           do_sample=False, pad_token_id=pad, eos_token_id=eos, **kw)
        for r, i in enumerate(idx):
            new = g[r, L:].tolist()
            while new and new[-1] == pad:
                new.pop()
            out[i] = new
    return out


def converse(model, tok, prompts, run_block, max_new=320, rounds=3, batch=48):
    """The page's protocol on a batch: returns, per prompt, the reply text (result lines included) and its blocks."""
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    state = [{"ids": list(p), "reply": [], "blocks": [], "done": False} for p in prompts]
    for _ in range(rounds + 1):
        live = [s for s in state if not s["done"]]
        if not live:
            break
        news = generate(model, tok, [s["ids"] for s in live], max_new, batch, stop_at_fence=True)
        for s, new in zip(live, news):
            s["ids"] += new
            s["reply"] += new
            text = tok.decode(s["reply"])
            block = closed_block(text) if new and new[-1] != im_end else None
            if block is None or len(s["blocks"]) >= rounds:
                s["done"] = True
                continue
            lines = run_block(block)
            s["blocks"].append({"block": block, "result": lines})
            res = tok("\n" + "\n".join(lines) + "\n", add_special_tokens=False)["input_ids"]
            s["ids"] += res
            s["reply"] += res
    return [{"text": tok.decode(s["reply"], skip_special_tokens=True).strip(), "blocks": s["blocks"]} for s in state]


def last_number(text):
    m = re.findall(r"-?\d[\d,]*\.?\d*", text.replace("$", ""))
    if not m:
        return None
    try:
        return float(m[-1].replace(",", "").rstrip("."))
    except ValueError:
        return None
