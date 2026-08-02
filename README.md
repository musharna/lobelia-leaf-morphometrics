# Lobelia Silhouettes

Automating leaf-trait extraction from digitized herbarium specimens of _Lobelia_ sect. _Lobelia_ — 23 eastern North American wildflowers.

Undergraduate research at **Kent State University**, Department of Biological Sciences, advised by **Dr. Andrea Case**. Proposal dated December 2021; work ran through 2022 with a final data pull in February 2024. It sat inside NSF award [**DEB-2015606**](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2015606) — _BEE: Ecological and evolutionary processes affecting the co-existence of close relatives_ (Case, Kent State; collaborative with Lynda Delph at Indiana and Nico Cellinese at Florida).

**Write-up with figures and results:** https://musharna.github.io/projects/LobeliaSilhouettes/

## The problem

Herbaria hold hundreds of millions of pressed plants, and digitization has photographed a large fraction of them. What has _not_ happened is the measurement: a sheet photographed at 5100 × 3500 px contains leaf areas, blade widths, petiole dimensions and phenology, essentially none of which is in a database.

_Lobelia_ sect. _Lobelia_ is a deliberately awkward test case. Several species grow as **basal rosettes**, and a rosette pressed flat is a pile of overlapping blades radiating from one point — much harder to delineate than the cleanly separated, planar leaves most herbarium-vision work targets.

## Pipeline

| stage               | what it does                                                                                                        | where                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Acquire          | GBIF Darwin Core Archive → image URLs keyed by `gbifID`, de-duplicated by hand per species                          | [`notebooks/01`](notebooks/01_gbif_darwincore_download.ipynb), [`docs/gbif-download-notes.md`](docs/gbif-download-notes.md)                                             |
| 2. Download         | threaded fetch of specimen sheets into per-species directories                                                      | [`notebooks/02`](notebooks/02_specimen_image_download.ipynb), [`03`](notebooks/03_specimen_image_download_threaded.ipynb), [`04`](notebooks/04_bulk_download_run.ipynb) |
| 3. Clean            | OpenCV Canny + Hough transform to strip sheet rulers and label edges                                                | [`notebooks/05`](notebooks/05_hough_line_removal.ipynb), [`06`](notebooks/06_hough_line_removal_probabilistic.ipynb)                                                    |
| 4. Detect & segment | GinJinn2 / Detectron2 Mask R-CNN R101-FPN, two-stage: 2048 px sliding windows → bbox → crop → instance segmentation | [`docs/ginjinn-workflow.md`](docs/ginjinn-workflow.md), [`docs/annotation-notes.md`](docs/annotation-notes.md)                                                          |
| 5. Measure          | `LeafArea` in R driving ImageJ, calibrated at 85 px/cm                                                              | [`docs/dismembered-sheet-workflow.md`](docs/dismembered-sheet-workflow.md)                                                                                              |

Annotation was done in CVAT and exported COCO-style; sheets were rescaled 5100 × 3500 → 1200 × 800 with model inputs normalized to 256 × 256, split 60 / 20 / 20.

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

`analysis/` ordinates leaf outline across the clade from the recovered segmentation masks: **486 leaves from 88 specimens across 8 species**, each outline resampled to 128 pseudo-landmarks, aligned, scaled to unit centroid size, and reduced by PCA.

| result                                | value     |
| ------------------------------------- | --------- |
| PC1 share of shape variance           | 48%       |
| corr(PC1, measured width:length)      | **0.978** |
| between-species share of PC1 (eta²)   | 0.493     |
| between-species share of PC2 (eta²)   | 0.006     |
| LDA accuracy, **grouped by specimen** | **0.372** |
| permuted-label null                   | 0.166     |
| LDA accuracy, naive split             | 0.430     |

Outline alone runs at roughly twice chance — real, and modest. PC2 is real variation, but _within_ plants rather than between species.

Two details are load-bearing rather than incidental:

- **Cross-validation is grouped by specimen.** Ten leaves off one plant are not ten independent observations; the naive split scores ~6 points higher for free.
- **Alignment was the hard part.** A first version produced a strongly **bimodal** PC1 holding 82.5% of variance — the signature of inconsistent orientation, not biology. `find_contours` traverses some outlines clockwise and others counter-clockwise, which reverses the landmark sequence and splits the sample in two under PCA. Pinning contour winding, the 180° rotation and the start landmark dropped PC1 to 48% and made it unimodal.

The masks themselves are **not** in this repo — they are lab material. The scripts expect them in a local `all_masks/` directory.

## Provenance

This is completed undergraduate work, published as a record rather than as a maintained project. The code is not packaged for reuse and the models are not included. These files were recovered in August 2026 from a laptop backup — the notebooks are as they were written, renamed for legibility and with outputs stripped.

## Licence

[MIT](LICENSE) for the code. The notes and the ledger describe the author's own work; specimen records referenced within remain under their sources' terms.
