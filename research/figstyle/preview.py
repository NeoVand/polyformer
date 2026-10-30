import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from palette import P, use, cmap_density, cmap_exact, cmap_div
use()
fig = plt.figure(figsize=(7.2, 4.4))
gs = fig.add_gridspec(2, 4, height_ratios=[0.5, 1], hspace=0.6, wspace=0.5)
ax = fig.add_subplot(gs[0, :]); ax.axis("off")
names = ["ink", "ink_soft", "blue_grey", "blue_mist", "tint", "rose", "rose_light", "cobalt", "cobalt_light", "violet"]
for i, n in enumerate(names):
    ax.add_patch(plt.Rectangle((i, 0.35), 0.82, 0.55, color=P[n], ec=P["blue_mist"] if n == "tint" else P[n], lw=0.5))
    ax.text(i + 0.41, 0.18, n.replace("_", " "), ha="center", va="top", fontsize=6, color=P["ink"])
    ax.text(i + 0.41, 0.0, P[n], ha="center", va="top", fontsize=5, color=P["ink_soft"])
ax.set_xlim(-0.1, len(names)); ax.set_ylim(-0.25, 1.0)
ax.text(-0.1, 1.0, "a", fontsize=8, fontweight="bold", va="bottom")
L = np.array([16, 64, 256, 1024]); ax = fig.add_subplot(gs[1, 0])
ax.axvspan(4, 16, color=P["tint"], lw=0)
series = [("ours", [1, 1, 1, 1], P["rose"], "-"), ("alternative", [1, 0.99, 0.97, 0.92], P["cobalt"], "-"),
          ("baseline", [1, 0.96, 0.63, 0.55], P["ink_soft"], (0, (4, 2))), ("baseline 2", [1, 0.74, 0.25, 0.20], P["blue_grey"], (0, (1, 1.5)))]
for name, y, c, ls in series:
    ax.plot(L, y, color=c, ls=ls, marker="o", mfc="white", mew=0.8, ms=2.6)
    ax.text(1150, y[-1], name, color=c, fontsize=5.5, va="center")
ax.axhline(0.45, color=P["violet"], lw=0.6, ls=(0, (1, 2)))
ax.set_xscale("log"); ax.set_xticks(L); ax.set_xticklabels(["16", "64", "256", "1k"]); ax.minorticks_off()
ax.set_xlim(4, 1100); ax.set_ylim(0, 1.05); ax.set_xlabel("Length"); ax.set_ylabel("Exact")
ax.text(-0.35, 1.08, "b", transform=ax.transAxes, fontsize=8, fontweight="bold")
rng = np.random.default_rng(0)
pts = np.concatenate([rng.normal(c, 0.035, size=(600, 2)) for c in rng.uniform(-1, 1, size=(16, 2))])
for k, (cm, title, data) in enumerate([(cmap_density, "density", None), (cmap_exact, "exactness", None), (cmap_div, "diverging", None)]):
    ax = fig.add_subplot(gs[1, k + 1])
    if k == 0:
        ax.hist2d(pts[:, 0], pts[:, 1], bins=120, cmap=cm, range=[[-1.2, 1.2], [-1.2, 1.2]], vmin=0)
    else:
        x, y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))
        z = np.exp(-((x - 0.3) ** 2 + (y + 0.2) ** 2) / 0.05) if k == 1 else np.sin(3 * x) * np.cos(2 * y)
        ax.imshow(z, cmap=cm, origin="lower", vmin=(0 if k == 1 else -1), vmax=1, extent=[-1.2, 1.2, -1.2, 1.2])
    ax.set_aspect("equal"); ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(title, fontsize=6, color=P["ink_soft"])
    ax.text(-0.08, 1.12, "cde"[k], transform=ax.transAxes, fontsize=8, fontweight="bold")
fig.savefig(pathlib.Path(__file__).resolve().parent / "palette_preview.png", dpi=300)
print("ok")
