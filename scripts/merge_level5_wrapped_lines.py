#!/usr/bin/env python3
"""Join rows split only by the page's line wrap, so one row holds one sentence."""
import sys
from pathlib import Path

def join(a, b):
    z = a[2].rstrip("…") + b[2].lstrip("…")
    polite = b[3].startswith("(polite")
    return [
        a[0] + (" " if b[0].startswith("_") else "") + b[0],
        a[1] + " " + b[1],
        z.replace("（客氣語尾）", ""),
        a[3] + "." if polite else a[3] + " " + b[3],
        a[4] + "。" if polite else a[4] + b[4],
        a[5] + "." if polite else a[5] + " " + b[5],
    ]

for name in sys.argv[1:]:
    path = Path(name)
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(("@", "#")) or not line.strip():
            out.append(line)
            continue
        row = line.split(" | ")
        if len(row) != 6:
            raise SystemExit(f"bad row: {line[:80]}")
        if out and not out[-1].startswith(("@", "#")) and out[-1].split(" | ")[2].endswith("……") and row[2].startswith("……"):
            out[-1] = " | ".join(join(out[-1].split(" | "), row))
        else:
            out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
