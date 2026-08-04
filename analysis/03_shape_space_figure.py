"""Leaf shape-space figure: small multiples, one panel per species.

Form choice: the dataviz skill caps ALL-PAIRS forms (scatter) at three categorical
hues, because any two points can end up adjacent. Eight species would breach that, so
this is small multiples with a SINGLE accent (#2e7d32, already validated against both
light and dark surfaces) over a recessive grey reference cloud. No pair of series
colours ever has to be told apart.
"""

import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import data, fig as fig_path  # noqa: E402

d = np.load(data("outlines.npz"), allow_pickle=True)
X, y, v = d["X"], d["labels"], d["vouchers"]
keep = ~np.isin(y, ["cardinalis", "unknown"])
X, y, v = X[keep], y[keep], v[keep]

Xc = X - X.mean(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
var = S**2 / (S**2).sum()
Z = U[:, :2] * S[:2]

order = sorted(set(y), key=lambda s: -(y == s).sum())
ACC, GREY, INK = "#2e7d32", "#d6d6d6", "#4a4a4a"

fig, axes = plt.subplots(2, 4, figsize=(13.2, 6.4), sharex=True, sharey=True)
for ax, sp in zip(axes.ravel(), order):
    m = y == sp
    ax.scatter(Z[~m, 0], Z[~m, 1], s=7, c=GREY, linewidths=0, rasterized=True)
    ax.scatter(Z[m, 0], Z[m, 1], s=11, c=ACC, linewidths=0)
    ax.set_title(f"$L.\\ {sp}$", fontsize=11.5, color=INK, pad=5)
    ax.text(
        0.97,
        0.05,
        f"n={m.sum()}  ({len(set(v[m]))} specimens)",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
        color=INK,
    )
    ax.tick_params(labelsize=8, colors=INK, length=3)
    for s_ in ax.spines.values():
        s_.set_color("#cccccc")
    ax.grid(True, color="#f0f0f0", linewidth=0.8)
    ax.set_axisbelow(True)

fig.supxlabel(
    f"PC1 — {var[0] * 100:.0f}% of shape variance (leaf breadth relative to length)",
    fontsize=10.5,
    color=INK,
    y=0.045,
)
fig.supylabel(f"PC2 — {var[1] * 100:.0f}%", fontsize=10.5, color=INK, x=0.012)
fig.suptitle(
    "Leaf shape space, one panel per species (grey = all 486 leaves)",
    fontsize=12.5,
    color=INK,
    y=0.985,
)
fig.tight_layout(rect=[0.02, 0.05, 1, 0.96])
out = fig_path("shape_space.png")
fig.savefig(out, dpi=155, facecolor="white")
print(
    "wrote",
    out,
    "| PC1",
    round(var[0] * 100, 1),
    "% PC2",
    round(var[1] * 100, 1),
    "% | n",
    len(y),
)
