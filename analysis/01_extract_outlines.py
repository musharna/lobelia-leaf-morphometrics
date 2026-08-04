"""Extract normalised leaf outlines from every mask, for a shape-space ordination.

Alignment is the whole ballgame here. A first version produced a strongly BIMODAL PC1
holding 82.5% of variance - the signature of inconsistent orientation, not biology.
Three things are now pinned explicitly:
  1. contour WINDING (find_contours traverses some shapes clockwise, others not, which
     reverses the landmark sequence and splits the sample in two under PCA),
  2. the 180-degree rotation about the long axis (SVD sign is arbitrary),
  3. the start landmark.
"""

import os
import sys
import glob
import signal
import collections
import numpy as np
from PIL import Image
from skimage import measure

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DATA, data  # noqa: E402

signal.signal(signal.SIGALRM, lambda *_: (sys.stderr.write("guard\n"), sys.exit(2)))
signal.alarm(1800)

SRC = data("masks")
OUT = os.path.join(DATA, "outlines.npz")
K, AREA_FLOOR, SOLIDITY_MIN = 128, 5000, 0.80


def signed_area(c):
    x, y = c[:, 0], c[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def resample(c, k):
    d = np.sqrt((np.diff(c, axis=0) ** 2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    if s[-1] == 0:
        return None
    t = np.linspace(0, s[-1], k, endpoint=False)
    return np.column_stack([np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])])


rows, labels, vouchers, solidities = [], [], [], []
n_masks = n_comp = 0
# Attrition, split by WHY a component was dropped. "too small" and "too damaged"
# are different facts about herbarium material and worth reporting separately.
rej_small = rej_rough = rej_both = 0
for f in sorted(glob.glob(os.path.join(SRC, "*.tif"))):
    n_masks += 1
    sp = (
        os.path.basename(f)
        .split("__")[0]
        .replace("groupleafcrops", "")
        .replace("indvleafcrops", "")
    )
    a = np.array(Image.open(f).convert("L"))
    fg = a > 127
    if fg.mean() > 0.5:
        fg = ~fg
    for p in measure.regionprops(measure.label(fg)):
        n_comp += 1
        small, rough = p.area < AREA_FLOOR, p.solidity < SOLIDITY_MIN
        if small or rough:
            rej_both += small and rough
            rej_small += small and not rough
            rej_rough += rough and not small
            continue
        cs = measure.find_contours(np.pad(p.image.astype(float), 2), 0.5)
        if not cs:
            continue
        c = max(cs, key=len)
        # 1. pin winding BEFORE resampling, so the landmark order is comparable
        if signed_area(c) < 0:
            c = c[::-1]
        pts = resample(c, K)
        if pts is None:
            continue
        pts = pts - pts.mean(0)
        # rotate the long axis onto x
        _, _, vt = np.linalg.svd(pts, full_matrices=False)
        pts = pts @ vt.T
        # 2. pin the 180-degree flip: a leaf is wider toward the base, so put the
        #    broader half at -x and the tip at +x. Compare mean |y| either side.
        w_pos = np.abs(pts[pts[:, 0] > 0, 1]).mean() if (pts[:, 0] > 0).any() else 0.0
        w_neg = np.abs(pts[pts[:, 0] < 0, 1]).mean() if (pts[:, 0] < 0).any() else 0.0
        if w_pos > w_neg:
            pts = pts * np.array([-1.0, 1.0])
        # rotation may have mirrored the shape; restore winding in the new frame
        if signed_area(pts) < 0:
            pts = pts * np.array([1.0, -1.0])
        pts = pts / np.sqrt((pts**2).sum())
        # 3. start at the tip (max x)
        pts = np.roll(pts, -int(np.argmax(pts[:, 0])), axis=0)
        rows.append(pts.ravel())
        labels.append(sp)
        vouchers.append(os.path.basename(f))
        # Keep solidity. It is the only damage proxy we have, and 02 needs it to test
        # whether the surviving damage biases the shape axes it is about to measure.
        solidities.append(p.solidity)

X = np.array(rows)
np.savez(
    OUT,
    X=X,
    labels=np.array(labels),
    vouchers=np.array(vouchers),
    solidity=np.array(solidities),
)
print(f"masks={n_masks} components={n_comp} leaves_kept={len(rows)}")
measurable = len(rows) + rej_rough
print(
    f"attrition: kept {len(rows)}/{n_comp} ({len(rows) / n_comp:.1%}) | "
    f"dropped too-small {rej_small}, too-damaged {rej_rough}, both {rej_both}"
)
print(
    f"  of components big enough to measure, {rej_rough}/{measurable} "
    f"({rej_rough / measurable:.1%}) were too damaged to use"
)
for sp, n in collections.Counter(labels).most_common():
    print(f"  {sp:20s} {n}")
