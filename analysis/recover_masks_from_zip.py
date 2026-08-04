import sys, os, zlib, signal
signal.signal(signal.SIGALRM, lambda *_: (sys.stderr.write("guard\n"), sys.exit(2)))
signal.alarm(1800)
zip_path, index_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
rows = []
for line in open(index_path, encoding="utf-8", errors="replace"):
    p = line.rstrip("\n").split("\t")
    if len(p) == 5 and p[0].endswith("_mask.tif"):
        rows.append((p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])))
print("masks in index:", len(rows), flush=True)
f = open(zip_path, "rb"); ok = 0
for name, off, csz, usz, meth in rows:
    f.seek(off); raw = f.read(csz if csz else usz)
    try:
        blob = raw if meth == 0 else zlib.decompress(raw, -15)
    except Exception as e:
        print("FAIL", name, e, flush=True); continue
    parts = name.rstrip(chr(92)).split(chr(92))
    # keep species + voucher in the filename so provenance survives extraction
    sp = parts[5] if len(parts) > 5 else "unknown"
    base = f"{sp}__{parts[-1]}"
    open(os.path.join(outdir, base), "wb").write(blob); ok += 1
print("extracted", ok, "of", len(rows), flush=True)
