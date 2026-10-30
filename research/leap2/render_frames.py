"""Film strip of Qwen3.5-0.8B DeltaNet states (untouched weights) while 'Now x = v.' is written five times.
Rows: the four longest-lived heads. Columns: the state right after each '=' value token, then its change."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import torch

d = torch.load(sys.argv[1])
toks, frames = d["tokens"], d["frames"]
cmap = LinearSegmentedColormap.from_list("cobalt_rose", ["#1f3fbf", "#ffffff", "#c2185b"])
at = [t for t in range(2, len(toks)) if toks[t].strip().isdigit() and "=" in toks[t - 2] + toks[t - 1]]
heads = list(frames)
fig, ax = plt.subplots(2 * len(heads), len(at), figsize=(2.0 * len(at), 4.1 * len(heads)), facecolor="white")
for r, h in enumerate(heads):
    for c, t in enumerate(at):
        S, P = frames[h][t], frames[h][t - 1]
        for k, (M, lab) in enumerate(((S, "state"), (S - P, "change"))):
            a = ax[2 * r + k, c]
            v = float(M.abs().max()) or 1.0
            a.imshow(M.numpy(), cmap=cmap, vmin=-v, vmax=v, interpolation="nearest")
            a.set_xticks([]); a.set_yticks([])
            if c == 0:
                a.set_ylabel(f"{h}\n{lab}", fontsize=8)
            if r == 0 and k == 0:
                a.set_title(f"x = {toks[t].strip()}", fontsize=9)
fig.suptitle("Qwen3.5-0.8B DeltaNet memory (128x128 per head), untouched weights", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[2], dpi=110, facecolor="white")
print("wrote", sys.argv[2], "value tokens:", [toks[t] for t in at])
