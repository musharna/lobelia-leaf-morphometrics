# Lobelia leaf morphometrics

Automating leaf-trait extraction from digitized herbarium specimens of _Lobelia_ sect. _Lobelia_ — 23 eastern North American wildflowers.

Undergraduate research at **Kent State University**, Department of Biological Sciences, advised by **Dr. Andrea Case**. Proposal dated December 2021; work ran through 2022 with a final data pull in February 2024. It sat inside NSF award [**DEB-2015606**](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2015606) — _BEE: Ecological and evolutionary processes affecting the co-existence of close relatives_ (Case, Kent State; collaborative with Lynda Delph at Indiana and Nico Cellinese at Florida).

> **Which project is this?** Two related but distinct pieces of _Lobelia_ work, easy to confuse
> because both reduce a pressed plant to an outline:
>
> - **this repo — semi-automated leaf measurement** (2021–24): dismembering and digitizing vouchers,
>   cropping leaves, and measuring area and perimeter from them.
> - **the digital reconstruction of _Lobelia_ silhouettes** (2018–19): whole-plant silhouettes
>   restored from herbarium sheets, credited in Godden et al. 2025. That work came **first** and is
>   **not in this repo** — see the [write-up](https://musharna.github.io/projects/LobeliaSilhouettes/).
>
> They also make opposite choices about scale: the silhouettes preserve true size from each sheet's
> ruler; this pipeline normalises size away so that only leaf _shape_ is compared.
>
> This repo was first published as `lobelia-silhouettes`, a name that conflated the two. The old
> URL redirects here.

**Write-up with figures and results:** https://musharna.github.io/projects/LobeliaLeafMeasurement/

## The problem

Herbaria hold hundreds of millions of pressed plants, and digitization has photographed a large fraction of them. What has _not_ happened is the measurement: a sheet photographed at 5100 × 3500 px contains leaf areas, blade widths, petiole dimensions and phenology, essentially none of which is in a database.

_Lobelia_ sect. _Lobelia_ is a deliberately awkward test case. Several species grow as **basal rosettes**, and a rosette pressed flat is a pile of overlapping blades radiating from one point — much harder to delineate than the cleanly separated, planar leaves most herbarium-vision work targets.

## Pipeline

| stage                 | what it does                                                                                          | where                                                                      |
| --------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1. Collect            | _Lobelia_ vouchers from multiple sites, dismembered and digitized so leaves lie flat and separated    | [`docs/dismembered-sheet-workflow.md`](docs/dismembered-sheet-workflow.md) |
| 2. Whole-plant traits | ImageJ against the 1 cm scale standard: base-to-first-leaf, base-to-first-flower, stem thickness      | [`docs/dismembered-sheet-workflow.md`](docs/dismembered-sheet-workflow.md) |
| 3. Crop leaves        | semi-automated per-leaf cropping in ImageJ; unreadable leaves excluded by explicit criterion          | [`docs/dismembered-sheet-workflow.md`](docs/dismembered-sheet-workflow.md) |
| 4. Measure            | threshold each crop, then area and perimeter via the `LeafArea` R package driving ImageJ, at 85 px/cm | [`docs/dismembered-sheet-workflow.md`](docs/dismembered-sheet-workflow.md) |
| 5. Analyse            | R / RStudio                                                                                           | —                                                                          |

Presented at Michigan State University on 9 February 2024 as _Semi-Automated Extraction of Leaf
Traits from Herbarium Vouchers_.

### The aggregator-scale ambition, which was never finished

A parallel goal was to skip the dismembering — segment measurable leaves straight off an intact
sheet and run the whole clade at aggregator scale. That is what the GBIF acquisition and the
2,906 → 2,733 image corpus were assembled for:

| stage                        | what it does                                                                                                        | where                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Acquire                      | GBIF Darwin Core Archive → image URLs keyed by `gbifID`, de-duplicated by hand per species                          | [`notebooks/01`](notebooks/01_gbif_darwincore_download.ipynb), [`docs/gbif-download-notes.md`](docs/gbif-download-notes.md)                                             |
| Download                     | threaded fetch of specimen sheets into per-species directories                                                      | [`notebooks/02`](notebooks/02_specimen_image_download.ipynb), [`03`](notebooks/03_specimen_image_download_threaded.ipynb), [`04`](notebooks/04_bulk_download_run.ipynb) |
| Clean                        | OpenCV Canny + Hough transform to strip sheet rulers and label edges                                                | [`notebooks/05`](notebooks/05_hough_line_removal.ipynb), [`06`](notebooks/06_hough_line_removal_probabilistic.ipynb)                                                    |
| _Detect & segment (planned)_ | GinJinn2 / Detectron2 Mask R-CNN R101-FPN, two-stage: 2048 px sliding windows → bbox → crop → instance segmentation | [`docs/ginjinn-workflow.md`](docs/ginjinn-workflow.md), [`docs/annotation-notes.md`](docs/annotation-notes.md)                                                          |

**The segmentation stage was never completed on _Lobelia_.** The workflow in
`docs/ginjinn-workflow.md` is rehearsed against GinJinn's own tutorial dataset — every command
names `leucanthemum`, not a _Lobelia_ species — and the notes stop at `## not working???`. The
project's own to-do list still reads "annotate small sets / create model / decide best model", and
the February 2024 talk lists the CVAT-aided segmentation pipeline under _Future Research Interests_.

Annotation was to be done in CVAT and exported COCO-style, with sheets rescaled 5100 × 3500 → 1200 × 800, model inputs at 256 × 256, and a 60 / 20 / 20 split.

## Corpus

`data/gbif_acquisition_ledger.xlsx` is the per-species acquisition ledger — occurrence records screened, duplicates purged (with reasoning), download failures, and final image counts, per species, retrieved 2022-01-14.

Across the **20 of 23** species tabs complete on both ends: **2,906 occurrence records screened → 2,733 specimen images retained.** Three tabs are unfinished, so the true corpus is larger, not smaller.

Coverage is extremely long-tailed — 811 retained sheets for _L. cardinalis_ against a single usable one for _L. apalachicolensis_. Any model trained on it inherits that skew.

A later, narrower pull for _L. siphilitica_ alone is permanently citable:
**GBIF Occurrence Download [10.15468/dl.5gavr9](https://doi.org/10.15468/dl.5gavr9)** — 452 preserved-specimen records across 19 institutional datasets, retrieved 2024-02-16, CC BY-NC 4.0.

## What did not work

Most leaf-morphometrics tooling assumes an idealized input that digitized herbarium material never satisfies — MorphoLeaf needs clean high-contrast single leaves on a uniform background; LeafJ failed to detect whole leaves; LeafMachine and MASS are MATLAB-licensed; TraitEx would not import the images at all. See [`docs/morphometrics-tool-survey.md`](docs/morphometrics-tool-survey.md).

The rosette problem was never fully solved. Delineating individual leaves in a flattened rosette, where blades overlap and converge on a single point, remained the open edge of the project.

## What is deliberately not in this repo

- **No specimen imagery.** The raw sheets carry explicit copyright reservations burned into the pixels (e.g. "© 2017 UNM Herbarium. All rights reserved.", Northern Arizona University ASC "copyright reserved") — notwithstanding the CC-BY-NC licence field on the aggregator record. An aggregator's licence field is the aggregator's assertion, not the rights-holder's.
- **No lab specimen photographs or derived masks.** Those belong to the Case lab.
- **No grant proposal.** The NSF programme document is not mine to publish.
- **Notebook outputs are stripped.** They were tens of thousands of download log lines.
- One plaintext credential and one account name present in the original working notes have been removed; those lines are marked in [`docs/working-notes.md`](docs/working-notes.md). Everything else is verbatim.

## Shape-space analysis (added 2026)

`analysis/` ordinates leaf outline across the clade from the recovered **ImageJ-thresholded** leaf masks: **486 leaves from 88 specimens across 8 species**, each outline resampled to 128 pseudo-landmarks, aligned, scaled to unit centroid size, and reduced by PCA.

| result                                | value     |
| ------------------------------------- | --------- |
| PC1 share of shape variance           | 48%       |
| corr(PC1, measured width:length)      | **0.978** |
| between-species share of PC1 (eta²)   | 0.493     |
| between-species share of PC2 (eta²)   | 0.006     |
| LDA accuracy, **grouped by specimen** | **0.372** |
| permuted-label null                   | 0.166     |
| LDA accuracy, naive split             | 0.430     |

Outline alone runs at roughly twice chance — real, and modest.

**What PC2 is, measured rather than asserted.** PC2 carries 26% of shape variance and
essentially no species signal (eta² 0.006). Partitioning it by _specimen_ instead gives
eta² **0.211** — so about 79% of PC2 is leaf-to-leaf variation _within a single plant_,
not between plants and emphatically not between species.

### Damage contaminates PC1, and the result survives it anyway

Thresholded herbarium masks include torn and punctured laminae. Solidity (outline
convexity) is the only damage proxy available, and it tracks the axis the whole result
rests on:

| check                                     | value                 |
| ----------------------------------------- | --------------------- |
| solidity vs PC1 (Spearman)                | **+0.360**, p 2.5e-16 |
| same, mean _within_ species               | **+0.308**            |
| eta² of solidity by species               | 0.150                 |
| eta² PC1 by species, raw → damage-removed | 0.493 → **0.434**     |
| LDA grouped, raw → damage-removed         | 0.372 → **0.360**     |
| **LDA on solidity ALONE, no shape**       | **0.195**             |
| majority-class baseline                   | 0.191                 |

Damaged leaves read as _narrower_, which is what losing lamina should do. The contamination
is real and holds within species, so it is not species-level covariation. But residualising
every PC on solidity costs only 0.012 accuracy, and **damage with no shape information at all
classifies at 0.195 against a 0.191 baseline** — it cannot carry the species signal by itself.
The published result stands.

One coincidence worth stating: _L. glandulosa_ is both the **most damaged** species (mean
solidity 0.851) and the PC1 outlier driving the strongest agreement with the 2024 analysis.

**Attrition.** Of **1,206 connected components** across the 104 masks, 490 were usable
(40.6%); 186 were too small, 238 too damaged, 292 both. Of components large enough to measure
at all, **32.7% were rejected as too damaged to use.**

Two details are load-bearing rather than incidental:

- **Cross-validation is grouped by specimen.** Ten leaves off one plant are not ten independent observations; the naive split scores ~6 points higher for free.
- **Alignment was the hard part.** A first version produced a strongly **bimodal** PC1 holding 82.5% of variance — the signature of inconsistent orientation, not biology. `find_contours` traverses some outlines clockwise and others counter-clockwise, which reverses the landmark sequence and splits the sample in two under PCA. Pinning contour winding, the 180° rotation and the start landmark dropped PC1 to 48% and made it unimodal.

### Running it

The masks themselves are **not** in this repo — they are lab material, and the
source sheets carry all-rights-reserved notices regardless of the licence field
on the aggregator record. Point the scripts at your own copy:

```bash
pip install -r requirements.txt        # scikit-learn is pinned: LDA scores move between versions
export LOBELIA_DATA=/path/to/data      # must contain masks/ ; 01 writes outlines.npz here
export LOBELIA_FIGDIR=/path/to/figures # defaults to ./figures
python analysis/01_extract_outlines.py     # masks/      -> outlines.npz
python analysis/02_shape_stats.py          # outlines.npz -> the table above
python analysis/03_shape_space_figure.py   # outlines.npz -> shape_space.png
python analysis/04_synthesis_figure.py     # outlines.npz -> shape_synthesis.png
python analysis/05_clade_montage.py        # masks/       -> clade_leaf_shapes.png
python analysis/06_species_counts_chart.py # inlined ledger counts -> species-counts chart
```

Defaults are `./data` and `./figures`; both roots are resolved in
[`analysis/_paths.py`](analysis/_paths.py) and nothing hardcodes an absolute
path. `05` accepts either mask-naming scheme (bare `LGLANAC21060_2.jpg_mask.tif`
or species-prefixed `glandulosagroupleafcrops__…`), matching on suffix.

Verified end to end on 2026-08-04 against the 104 recovered masks: `01`
reproduces `outlines.npz` bit-for-bit, `02` reproduces every figure in the table
above, and `03`/`04`/`05` reproduce their published PNGs byte-for-byte.

`recover_masks_from_zip.py` and `index_zip.py` are the recovery path the masks
themselves came out of: index a backup zip's central directory, then extract the
`*_mask.tif` members by offset, keeping species and voucher in the filename so
provenance survives extraction.

## Provenance

This is completed undergraduate work, published as a record rather than as a maintained project. The code is not packaged for reuse and the models are not included. These files were recovered in August 2026 from a laptop backup — the notebooks are as they were written, renamed for legibility and with outputs stripped.

## Licence

[MIT](LICENSE) for the code. The notes and the ledger describe the author's own work; specimen records referenced within remain under their sources' terms.
