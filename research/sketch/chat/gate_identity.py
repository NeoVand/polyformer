"""T5 identity test for the `lora_gate` input (ONNX Runtime, CPU), one shard of the work.

Three decoder graphs, each with the inside patch (hidden_states out, steer in) and the same external weights:
  stock.onnx     the base fp16 decoder, no LoRA
  today.onnx     the page's `arithmetic/` graph of 30 Oct (E6 seed 3, ungated)
  gated_e6.onnx  the same adapter with the gate (patch_onnx_lora.py, default)
Pairs: stock vs gated at gate 0, today vs gated at gate 1. Every call feeds both graphs of a pair the same inputs and
compares logits, hidden_states and every present state bit for bit (fp16 bit patterns), plus the argmax.

  chat  100 prompts from HuggingFaceH4/no_robots (test split, first user turn, chat template, thinking off): one prefill
        call with all logits kept, then 24 greedy decode calls through the cache, fed the first graph's argmax
  rows  all 1,795 E6 table rows (the SUM rows and the multiplier rows with their two slots), inputs_embeds and the 3-D
        positions captured from the Hugging Face forward (fp32 vision tower and embeddings: the inputs differ from the
        page's q4/fp16 ones, which does not matter for an identity test), one prefill call each; also counts the rows
        whose argmax at every answer place is right, as a sanity check that the inputs are real

  python chat/gate_identity.py <onnx dir> <shard> <shards>    # writes gate_identity_<shard>.json
"""

import json
import os
import pathlib
import sys
import time

import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
D, SHARD, SHARDS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
N_CHAT, DECODE = 100, 24


def session(name):
    so = ort.SessionOptions()
    so.intra_op_num_threads = os.cpu_count()
    return ort.InferenceSession(f"{D}/{name}", so, providers=["CPUExecutionProvider"])


class Graph:
    def __init__(self, name, gate=None, sess=None):
        self.name, self.gate = name, gate
        self.s = sess or session(name)
        self.inputs = [i.name for i in self.s.get_inputs()]
        self.outputs = [o.name for o in self.s.get_outputs()]
        assert (gate is not None) == ("lora_gate" in self.inputs), (name, gate)

    def empty(self):
        past = {}
        for n in self.inputs:
            if n.startswith("past_conv"):
                past[n] = np.zeros((1, 6144, 3), np.float16)
            elif n.startswith("past_recurrent"):
                past[n] = np.zeros((1, 16, 128, 128), np.float16)
            elif n.startswith("past_key_values"):
                past[n] = np.zeros((1, 2, 0, 256), np.float16)
        return past

    def run(self, emb, pos, total, past, keep):
        feed = {"inputs_embeds": emb, "attention_mask": np.ones((1, total), np.int64), "position_ids": pos,
                "num_logits_to_keep": np.array(keep, np.int64), "steer": np.zeros(emb.shape, np.float32), **past}
        if self.gate is not None:
            feed["lora_gate"] = np.array([self.gate], np.float16)
        out = dict(zip(self.outputs, self.s.run(None, feed)))
        nxt = {}
        for k, v in out.items():
            if k.startswith("present_conv") or k.startswith("present_recurrent"):
                nxt[k.replace("present", "past", 1)] = v
            elif k.startswith("present."):
                nxt["past_key_values." + k[len("present."):]] = v
        assert set(nxt) == set(past), sorted(set(nxt) ^ set(past))[:4]
        return out, nxt


def bits(a):
    return a.view(np.uint16) if a.dtype == np.float16 else a.view(np.uint32) if a.dtype == np.float32 else a


class Tally:
    def __init__(self):
        self.calls = self.logits_bit = self.hidden_bit = self.present_bit = self.argmax_same = 0
        self.max_logit_diff = self.max_hidden_diff = 0.0
        self.first_diff = None

    def add(self, a, b, where):
        self.calls += 1
        lb = np.array_equal(bits(a["logits"]), bits(b["logits"]))
        hb = np.array_equal(bits(a["hidden_states"]), bits(b["hidden_states"]))
        pb = all(np.array_equal(bits(a[k]), bits(b[k])) for k in a if k.startswith("present"))
        self.logits_bit += lb
        self.hidden_bit += hb
        self.present_bit += pb
        self.argmax_same += bool(np.array_equal(a["logits"].argmax(-1), b["logits"].argmax(-1)))
        dl = float(np.nanmax(np.abs(a["logits"].astype(np.float32) - b["logits"].astype(np.float32))))
        dh = float(np.nanmax(np.abs(a["hidden_states"].astype(np.float32) - b["hidden_states"].astype(np.float32))))
        self.max_logit_diff = max(self.max_logit_diff, dl)
        self.max_hidden_diff = max(self.max_hidden_diff, dh)
        if not (lb and hb and pb) and self.first_diff is None:
            self.first_diff = {"where": where, "logits_bit": lb, "hidden_bit": hb, "present_bit": pb, "logit_diff": dl}

    def json(self):
        return dict(self.__dict__)


def text_pos(start, n):
    return np.tile(np.arange(start, start + n, dtype=np.int64), (3, 1, 1))


def chat_part(pairs, tally, log):
    from datasets import load_dataset
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("/sk/model")
    ds = load_dataset("HuggingFaceH4/no_robots", split="test")
    prompts = [r["messages"][0]["content"][:600] for r in ds if r["messages"][0]["role"] == "user"][:N_CHAT]
    embed = session("embed_tokens_q4.onnx")
    greedy = {}
    for i in range(SHARD, len(prompts), SHARDS):
        text = tok.apply_chat_template([{"role": "user", "content": prompts[i]}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False)
        ids = tok(text)["input_ids"]
        for key, (ga, gb) in pairs.items():
            emb = embed.run(None, {"input_ids": np.array([ids], np.int64)})[0]
            S = len(ids)
            pa, pb = ga.empty(), gb.empty()
            oa, pa = ga.run(emb, text_pos(0, S), S, pa, S)
            ob, pb = gb.run(emb, text_pos(0, S), S, pb, S)
            tally[key].add(oa, ob, f"chat {i} prefill")
            toks_a, toks_b = [], []
            for t in range(DECODE):
                na, nb = int(oa["logits"][0, -1].argmax()), int(ob["logits"][0, -1].argmax())
                toks_a.append(na)
                toks_b.append(nb)
                e1 = embed.run(None, {"input_ids": np.array([[na]], np.int64)})[0]  # both fed the first graph's token
                oa, pa = ga.run(e1, text_pos(S + t, 1), S + t + 1, pa, 1)
                ob, pb = gb.run(e1, text_pos(S + t, 1), S + t + 1, pb, 1)
                tally[key].add(oa, ob, f"chat {i} step {t}")
            greedy.setdefault(key, []).append({"prompt": i, "same": toks_a == toks_b, "text": tok.decode(toks_a)})
        log(f"chat {i}: " + "; ".join(f"{k} {tally[k].logits_bit}/{tally[k].calls}" for k in pairs))
    return greedy


def rows_part(pairs, tally, log):
    import torch

    import e2_column as e2
    import e5_union as u
    import e6_slots  # noqa: F401  (installs the one-forward batch builder into e5_union)

    model = e2.load_base().eval()
    lm = model.model.language_model
    cap = {}

    class Stop(Exception):
        pass

    def hook(mod, args, kwargs):
        cap["emb"] = kwargs["inputs_embeds"].detach().float().numpy()
        p = kwargs["position_ids"]
        cap["pos"] = (p[-3:] if p.shape[0] == 4 else p).detach().long().numpy()
        raise Stop

    lm.register_forward_pre_hook(hook, with_kwargs=True)
    right = {k: 0 for k in pairs}
    done = 0
    for j in range(SHARD, len(u.ROWS), SHARDS):
        op, v = u.ROWS[j]
        inp, spans = u.batch([(op, v)])
        with torch.no_grad():
            try:
                model(**inp)
            except Stop:
                pass
        emb, pos = cap["emb"], cap["pos"]
        S = emb.shape[1]
        assert pos.shape == (3, 1, S), pos.shape
        places, ans = spans[0]
        for key, (ga, gb) in pairs.items():
            oa, _ = ga.run(emb, pos, S, ga.empty(), S)
            ob, _ = gb.run(emb, pos, S, gb.empty(), S)
            tally[key].add(oa, ob, f"row {op} {''.join(v)}")
            right[key] += all(int(ob["logits"][0, p].argmax()) == a for p, a in zip(places, ans))
        done += 1
        if done % 25 == 0:
            log(f"rows {done}: " + "; ".join(f"{k} {tally[k].logits_bit}/{tally[k].calls}" for k in pairs))
    return {"rows": done, "argmax_right_at_every_answer_place": right}


def main():
    t0 = time.time()
    res = {"shard": SHARD, "shards": SHARDS, "ort": ort.__version__}
    lines = open(f"gate_identity_{SHARD}.log", "w")

    def log(s):
        lines.write(f"{time.time() - t0:7.1f}s {s}\n")
        lines.flush()

    gated = session("gated_e6.onnx")
    pairs = {"stock_vs_gate0": (Graph("stock.onnx"), Graph("gated_e6.onnx", 0.0, gated)),
             "today_vs_gate1": (Graph("today.onnx"), Graph("gated_e6.onnx", 1.0, gated))}
    log("sessions ready")
    for part, fn in (("chat", chat_part), ("rows", rows_part)):
        tally = {k: Tally() for k in pairs}
        extra = fn(pairs, tally, log)
        res[part] = {k: t.json() for k, t in tally.items()}
        res[part + "_extra"] = extra
        json.dump(res, open(f"gate_identity_{SHARD}.json", "w"), indent=1)
        log(f"{part} done")
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(f"gate_identity_{SHARD}.json", "w"), indent=1)
    print(json.dumps({p: {k: f"{v['logits_bit']}/{v['calls']}" for k, v in res[p].items()} for p in ("chat", "rows")}))


main()
