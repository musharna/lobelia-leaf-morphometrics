"""Species-discrimination statistics over the leaf outlines.

Two controls are deliberate and load-bearing:
  * cross-validation is GROUPED BY SPECIMEN. Leaves off one plant are not independent
    observations; a naive split lets the model see other leaves from the same plant and
    scores about 6 points higher for free.
  * a PERMUTED-LABEL null, so "better than chance" is measured rather than assumed.
"""

import os
import sys

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import data  # noqa: E402

d = np.load(data("outlines.npz"), allow_pickle=True)
X, y, v = d["X"], d["labels"], d["vouchers"]
sol = d["solidity"] if "solidity" in d.files else None  # absent in pre-2026-08 npz
keep = ~np.isin(y, ["cardinalis", "unknown"])  # n=3 and unlabelled
X, y, v = X[keep], y[keep], v[keep]
if sol is not None:
    sol = sol[keep]

Xc = X - X.mean(0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
var = S**2 / (S**2).sum()
Z = U[:, :10] * S[:10]

print(f"{len(y)} leaves | {len(set(y))} species | {len(set(v))} specimens")
print("variance explained:", np.round(var[:4] * 100, 1))

# Is PC1 what it looks like? Correlate against directly measured width:length.
P = X.reshape(len(X), -1, 2)
ar = (P[:, :, 1].max(1) - P[:, :, 1].min(1)) / (P[:, :, 0].max(1) - P[:, :, 0].min(1))
print(f"corr(PC1, width/length) = {np.corrcoef(Z[:, 0], ar)[0, 1]:+.3f}")


def eta2(z, groups):
    """Share of variance in z lying BETWEEN groups."""
    gm = z.mean()
    ssb = sum(
        ((z[groups == g].mean() - gm) ** 2) * (groups == g).sum() for g in set(groups)
    )
    return ssb / ((z - gm) ** 2).sum()


# PC2 holds a quarter of shape variance but no species signal. Partition it by SPECIMEN
# as well, so "it is within-plant variation" is measured rather than asserted.
for k in range(2):
    print(
        f"PC{k + 1} eta^2  between-species = {eta2(Z[:, k], y):.3f}   "
        f"between-specimen = {eta2(Z[:, k], v):.3f}"
    )

cv = GroupKFold(n_splits=8)
print(
    f"LDA grouped by specimen : {cross_val_score(LDA(), Z, y, groups=v, cv=cv).mean():.3f}"
)
print(
    f"LDA naive split         : {cross_val_score(LDA(), Z, y, cv=StratifiedKFold(8, shuffle=True, random_state=0)).mean():.3f}"
)
rng = np.random.default_rng(0)
null = [
    cross_val_score(LDA(), Z, rng.permutation(y), groups=v, cv=cv).mean()
    for _ in range(12)
]
print(f"permuted-label null     : {np.mean(null):.3f} +/- {np.std(null):.3f}")
maj = max((y == s).mean() for s in set(y))
print(f"majority-class baseline : {maj:.3f}")

# ----------------------------------------------------------------------------------
# Does the damage that SURVIVED the solidity>=0.80 filter still bias the shape axes?
#
# Solidity is the only damage proxy available. A torn lamina is less convex, so if
# solidity tracks a PC then that PC is partly measuring preservation, not biology.
# The load-bearing control is the LAST line: LDA on solidity ALONE, no shape at all.
# If damage could carry the species signal by itself, that number would rival the
# shape model. It does not, which is what licenses keeping the published result.
# ----------------------------------------------------------------------------------
if sol is None:
    print("\n[damage] no solidity in outlines.npz -- re-run 01 to enable this section")
else:
    from scipy.stats import spearmanr

    print(
        f"\n--- residual-damage check (n={len(sol)}, solidity {sol.min():.3f}-{sol.max():.3f}) ---"
    )
    for k in range(3):
        r, p = spearmanr(sol, Z[:, k])
        print(f"solidity vs PC{k + 1}       : rho = {r:+.3f}  p = {p:.2e}")

    # Within species, so this cannot be species-level covariation of damage and shape.
    rs = [
        spearmanr(sol[y == s], Z[y == s, 0]).statistic
        for s in sorted(set(y))
        if (y == s).sum() >= 20
    ]
    print(f"within-species PC1 rho  : mean {np.mean(rs):+.3f} over {len(rs)} species")
    print(
        f"eta^2 of solidity by species = {eta2(sol, y):.3f}  (do species differ in damage?)"
    )

    # Residualise every PC on solidity, then re-run the same grouped CV.
    Zr = np.column_stack(
        [
            Z[:, k] - np.polyval(np.polyfit(sol, Z[:, k], 1), sol)
            for k in range(Z.shape[1])
        ]
    )
    print(
        f"eta^2 PC1 by species    : {eta2(Z[:, 0], y):.3f} raw -> {eta2(Zr[:, 0], y):.3f} damage-removed"
    )
    print(
        f"LDA grouped, raw        : {cross_val_score(LDA(), Z, y, groups=v, cv=cv).mean():.3f}"
    )
    print(
        f"LDA grouped, damage-removed : {cross_val_score(LDA(), Zr, y, groups=v, cv=cv).mean():.3f}"
    )
    solo = cross_val_score(LDA(), sol.reshape(-1, 1), y, groups=v, cv=cv).mean()
    print(
        f"LDA on SOLIDITY ALONE   : {solo:.3f}  vs majority-class {maj:.3f}  <-- damage-only control"
    )
