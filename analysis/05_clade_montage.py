"""Cross-species Lobelia leaf-shape figure from the project's own segmentation masks.

COMPOSED MONTAGE: one representative leaf per species, each scaled to a common length.
Compares SHAPE, not size - absolute scale is deliberately not preserved.

Representative-leaf selection is tiered rather than "largest component", because the
largest component in a mask is often a stem fragment or merged debris:
  area >= 5000 px, then max area among solidity >= 0.90, else >= 0.85, else >= 0.80.
A species whose mask cannot supply such a component is EXCLUDED and reported.
"""

import os
import signal
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage import measure

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import data
from _paths import fig as fig_path

signal.signal(
    signal.SIGALRM, lambda *_: (sys.stderr.write("walltime guard\n"), sys.exit(2))
)
signal.alarm(900)

SRC = data("masks")
OUT = fig_path("clade_leaf_shapes.png")
AREA_FLOOR = 5000
LEAF_H, PAD_X, LABEL_H, TOP = 460, 26, 74, 26

SPECIES = {
    "LAPABS17132.jpg_mask.tif": ("apalachicolensis", "BS17132"),
    "LAPPEAC21008_1.jpg_mask.tif": ("appendiculata", "AC21008"),
    "LCANBAC21060_1.jpg_mask.tif": ("canbyi", "AC21060"),
    "LCARDST17131_1.jpg_mask.tif": ("cardinalis", "ST17131"),
    "LELONAC21058_2.jpg_mask.tif": ("elongata", "AC21058"),
    "LGLANAC21060_2.jpg_mask.tif": ("glandulosa", "AC21060"),
    "LINFLAC17091_2.jpg_mask.tif": ("inflata", "AC17091"),
    "LPUBEAC21051_2.jpg_mask.tif": ("puberula", "AC21051"),
    "LSIPHAC17142_1.jpg_mask.tif": ("siphilitica", "AC17142"),
    "LSPICSH21036_4.jpg_mask.tif": ("spicata", "SH21036"),
}


def pick_leaf(path):
    a = np.array(Image.open(path).convert("L"))
    fg = a > 127
    if fg.mean() > 0.5:
        fg = ~fg
    props = [p for p in measure.regionprops(measure.label(fg)) if p.area >= AREA_FLOOR]
    for thr in (0.90, 0.85, 0.80):
        cand = [p for p in props if p.solidity >= thr]
        if cand:
            p = max(cand, key=lambda q: q.area)
            return p, thr
    return None, None


def resolve(fn):
    """Find fn under SRC, tolerating the two mask-naming schemes in circulation.

    The earlier extraction wrote bare names (LGLANAC21060_2.jpg_mask.tif); the
    canonical 104-mask set prefixes species and crop set
    (glandulosagroupleafcrops__LGLANAC21060_2.jpg_mask.tif). Match on suffix so
    either layout works.
    """
    direct = os.path.join(SRC, fn)
    if os.path.exists(direct):
        return direct
    hits = [f for f in os.listdir(SRC) if f.endswith(fn)]
    if len(hits) == 1:
        return os.path.join(SRC, hits[0])
    if not hits:
        return None
    raise RuntimeError(f"{fn} is ambiguous under {SRC}: {sorted(hits)}")


tiles, dropped = [], []
for fn, (sp, vouch) in sorted(SPECIES.items(), key=lambda kv: kv[1][0]):
    path = resolve(fn)
    if path is None:
        dropped.append((sp, vouch))
        print(f"DROP {sp:18s} voucher={vouch} - no mask named {fn} under {SRC}")
        continue
    p, thr = pick_leaf(path)
    if p is None:
        dropped.append((sp, vouch))
        print(
            f"DROP {sp:18s} voucher={vouch} - no component >= {AREA_FLOOR}px with solidity >= 0.80"
        )
        continue
    comp = p.image
    h, w = comp.shape
    new_w = max(8, round(w * (LEAF_H / h)))
    leaf = Image.fromarray(np.where(comp, 0, 255).astype(np.uint8)).resize(
        (new_w, LEAF_H), Image.LANCZOS
    )
    tiles.append((sp, leaf))
    print(
        f"KEEP {sp:18s} voucher={vouch:9s} area={int(p.area):7d} solidity={p.solidity:.3f} tier>={thr} -> {new_w}x{LEAF_H}"
    )

total_w = sum(t[1].width for t in tiles) + PAD_X * (len(tiles) + 1)
canvas = Image.new("L", (total_w, TOP + LEAF_H + LABEL_H), 255)
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
for cand in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]:
    if os.path.exists(cand):
        font = ImageFont.truetype(cand, 19)
        break

x = PAD_X
for sp, leaf in tiles:
    canvas.paste(leaf, (x, TOP))
    tw = draw.textlength(sp, font=font)
    draw.text((x + leaf.width / 2 - tw / 2, TOP + LEAF_H + 16), sp, fill=60, font=font)
    x += leaf.width + PAD_X

canvas.save(OUT, optimize=True)
print(
    f"\nwrote {OUT} {canvas.size} {os.path.getsize(OUT)} bytes | kept={len(tiles)} dropped={[d[0] for d in dropped]}"
)
