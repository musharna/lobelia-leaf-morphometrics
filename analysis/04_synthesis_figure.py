"""Does the landmark PC1 track a simple dimensionless shape index?

Shape index = perimeter / sqrt(area). Dimensionless, so the unit-centroid-size
normalisation of the outlines is irrelevant and no pixel calibration is needed.

NOTE ON WHAT THIS IS NOT. Both quantities are computed here, in 2026, from the
SAME 128-landmark outlines in outlines.npz: PC1 from the SVD below, and the
shape index by shoelace polyarea + polygon perimeter on those same coordinates.
The 2024 LeafArea/ImageJ area+perimeter table does not survive on disk, so this
is a WITHIN-METHOD consistency check, not agreement between two measurement
campaigns. It shares its entire input with the thing it might be read as
corroborating, and so cannot fail informatively as a test of the 2024 result.
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
X, y = d["X"], d["labels"]
keep = ~np.isin(y, ["cardinalis", "unknown"])
X, y = X[keep], y[keep]
P = X.reshape(len(X), -1, 2)


def polyarea(p):
    x, yy = p[:, 0], p[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(yy, -1)) - np.dot(np.roll(x, -1), yy))


per = np.array(
    [np.sum(np.linalg.norm(np.diff(np.vstack([p, p[:1]]), axis=0), axis=1)) for p in P]
)
ar = np.array([polyarea(p) for p in P])
SI = per / np.sqrt(ar)
Xc = X - X.mean(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
pc1 = U[:, 0] * S[0]
r = float(np.corrcoef(pc1, SI)[0, 1])

ACC, GREY, INK = "#2e7d32", "#c9c9c9", "#3a3a3a"
FOUR = {"glandulosa", "appendiculata", "puberula", "elongata"}

fig, ax = plt.subplots(figsize=(10.4, 6.2))
ax.scatter(pc1, SI, s=13, c=GREY, linewidths=0, rasterized=True, zorder=1)
# Label placement: seven of eight species cluster near PC1 = 0, so labels are pushed
# apart vertically and joined to their point by a leader line rather than left to collide.
cents = []
for sp in sorted(set(y)):
    m = y == sp
    cents.append([sp, float(pc1[m].mean()), float(SI[m].mean()), sp in FOUR])
cents.sort(key=lambda c: -c[2])

span = SI.max() - SI.min()
minsep = span * 0.062
placed = []
for sp, mx, my, inpaper in cents:
    ly = my
    for _, _, py in placed:
        if abs(ly - py) < minsep:
            ly = py - minsep
    placed.append((sp, mx, ly))

lx = pc1.max() * 0.52
for (sp, mx, my, inpaper), (_, _, ly) in zip(cents, placed):
    ax.scatter(
        [mx],
        [my],
        s=130 if inpaper else 72,
        c=ACC if inpaper else "#9dba95",
        edgecolors="white",
        linewidths=1.6,
        zorder=3,
    )
    ax.annotate(
        "",
        xy=(mx, my),
        xytext=(lx, ly),
        zorder=2,
        arrowprops=dict(arrowstyle="-", color="#b9b9b9", lw=0.9, shrinkA=2, shrinkB=6),
    )
    ax.text(
        lx + 0.006,
        ly,
        f"$L.\\ {sp}$",
        va="center",
        fontsize=10.5,
        color=INK if inpaper else "#6f6f6f",
        fontweight="bold" if inpaper else "normal",
        zorder=4,
    )

b, a = np.polyfit(pc1, SI, 1)
xs = np.linspace(pc1.min(), pc1.max(), 50)
ax.plot(xs, b * xs + a, ls="--", lw=1.6, c=ACC, alpha=0.65, zorder=2)
ax.text(
    0.985,
    0.955,
    f"r = {r:.2f}   n = {len(y)} leaves",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=11.5,
    color=INK,
)
ax.set_xlim(pc1.min() - 0.02, pc1.max() * 1.42)
ax.set_xlabel("PC1 of leaf outline  —  narrow  →  broad", fontsize=11, color=INK)
ax.set_ylabel(
    "perimeter / $\\sqrt{\\mathrm{area}}$   (dimensionless)", fontsize=11, color=INK
)
ax.set_title(
    f"Two shape descriptors from the same {len(y)} leaf outlines",
    fontsize=12.5,
    color=INK,
    pad=10,
)
ax.grid(True, color="#f0f0f0", lw=0.8)
ax.set_axisbelow(True)
for s_ in ax.spines.values():
    s_.set_color("#cccccc")
ax.tick_params(labelsize=9, colors=INK)
fig.tight_layout()
out = fig_path("shape_synthesis.png")
fig.savefig(out, dpi=155, facecolor="white")
print("wrote", out, "| r =", round(r, 3))
for sp in sorted(set(y), key=lambda s: -SI[y == s].mean()):
    print(f"  {sp:18s} SI={SI[y == sp].mean():.2f}  PC1={pc1[y == sp].mean():+.3f}")
