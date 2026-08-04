"""Where inputs and outputs live.

Nothing in this repo hardcodes an absolute path. Both roots are overridable so a
checkout can point at wherever the masks actually sit:

    LOBELIA_DATA    inputs  (default: ./data)     masks/, outlines.npz
    LOBELIA_FIGDIR  outputs (default: ./figures)

The imagery itself is NOT in this repo — .gitignore excludes it, and the source
herbarium sheets carry all-rights-reserved notices regardless of the licence
field on the aggregator record. Point LOBELIA_DATA at your own copy.
"""

import os

DATA = os.environ.get("LOBELIA_DATA", "data")
FIGS = os.environ.get("LOBELIA_FIGDIR", "figures")


def data(*parts):
    """Path under the data root. Fails loud if it is missing."""
    p = os.path.join(DATA, *parts)
    if not os.path.exists(p):
        raise FileNotFoundError(
            f"{p} not found. Set LOBELIA_DATA to the directory holding "
            f"masks/ and outlines.npz (currently {DATA!r})."
        )
    return p


def fig(*parts):
    """Path under the figure root, creating it on demand."""
    os.makedirs(FIGS, exist_ok=True)
    return os.path.join(FIGS, *parts)
