"""Index a headerless/truncated ZIP by walking local file headers, and extract small docs in the same pass."""

import os
import signal
import struct
import sys
import zlib

signal.signal(
    signal.SIGALRM,
    lambda *_: (sys.stderr.write("aborting: walltime guard\n"), sys.exit(2)),
)
signal.alarm(int(sys.argv[4]) if len(sys.argv) > 4 else 14400)

path, index_out, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)

SEP = chr(92)
DOC_EXT = (
    ".docx",
    ".txt",
    ".pptx",
    ".xlsx",
    ".pdf",
    ".csv",
    ".json",
    ".py",
    ".ipynb",
    ".r",
)
MAX_DOC = 25 * 1024 * 1024


def wanted(name, usz):
    low = name.lower()
    if usz <= 0 or usz > MAX_DOC:
        return False
    if not low.endswith(DOC_EXT):
        return False
    return ("documents" + SEP + "research" + SEP) in low or "lobelia" in low


off = 0
scanned = 0
saved = 0
with open(path, "rb") as f, open(index_out, "w", encoding="utf-8") as idx:
    while True:
        f.seek(off)
        hdr = f.read(30)
        if len(hdr) < 30 or hdr[:4] != b"PK\x03\x04":
            break
        ver, flags, meth, mt, md, crc, csz, usz, nlen, elen = struct.unpack(
            "<HHHHHIIIHH", hdr[4:30]
        )
        name = f.read(nlen).decode("utf-8", "replace")
        data_off = off + 30 + nlen + elen
        scanned += 1
        idx.write(f"{name}\t{data_off}\t{csz}\t{usz}\t{meth}\n")

        if wanted(name, usz):
            f.seek(data_off)
            raw = f.read(csz if csz else usz)
            try:
                blob = raw if meth == 0 else zlib.decompress(raw, -15)
            except Exception as e:
                sys.stderr.write(f"DECOMP_FAIL {name} {e}\n")
                off = data_off + csz
                continue
            rel = name.rstrip(SEP).replace(SEP, "__").replace("/", "_")
            with open(os.path.join(outdir, rel), "wb") as o:
                o.write(blob)
            saved += 1
            print("SAVED", rel, usz, flush=True)

        if scanned % 25000 == 0:
            sys.stderr.write(f"scanned={scanned} off={off} saved={saved}\n")
            idx.flush()

        off = data_off + csz

sys.stderr.write(f"DONE scanned={scanned} saved={saved} final_off={off}\n")
