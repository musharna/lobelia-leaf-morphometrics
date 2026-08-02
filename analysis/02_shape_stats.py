"""Species-discrimination statistics over the leaf outlines.

Two controls are deliberate and load-bearing:
  * cross-validation is GROUPED BY SPECIMEN. Leaves off one plant are not independent
    observations; a naive split lets the model see other leaves from the same plant and
    scores about 6 points higher for free.
  * a PERMUTED-LABEL null, so "better than chance" is measured rather than assumed.
"""
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score

d = np.load("outlines.npz", allow_pickle=True)
X, y, v = d["X"], d["labels"], d["vouchers"]
keep = ~np.isin(y, ["cardinalis", "unknown"])   # n=3 and unlabelled
X, y, v = X[keep], y[keep], v[keep]

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

for k in range(2):
    z = Z[:, k]; gm = z.mean()
    ssb = sum(((z[y == s].mean() - gm) ** 2) * (y == s).sum() for s in set(y))
    print(f"PC{k+1} eta^2 (between-species share) = {ssb / ((z - gm) ** 2).sum():.3f}")

cv = GroupKFold(n_splits=8)
print(f"LDA grouped by specimen : {cross_val_score(LDA(), Z, y, groups=v, cv=cv).mean():.3f}")
print(f"LDA naive split         : {cross_val_score(LDA(), Z, y, cv=StratifiedKFold(8, shuffle=True, random_state=0)).mean():.3f}")
rng = np.random.default_rng(0)
null = [cross_val_score(LDA(), Z, rng.permutation(y), groups=v, cv=cv).mean() for _ in range(12)]
print(f"permuted-label null     : {np.mean(null):.3f} +/- {np.std(null):.3f}")
print(f"majority-class baseline : {max((y == s).mean() for s in set(y)):.3f}")
