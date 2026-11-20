"""Merge upstream Downloader screen tags into the picks and settle CCW-tate status where we can.

usage: python3 -I tools/tag_merge.py <picks.csv> <label=db.json.zip> [...]

Upstream tags (Distribution, Jotego, Coin-Op, partly Ongo) describe where an MRA works:
  screentateccw / screentatecw  - playable on a CCW / CW tate cab (natively or via flip)
  screentateflip                - the game has a flip setting
  screennotate                  - not for tate at all
"""
import csv, json, os, sys, zipfile

def load(path):
    z = zipfile.ZipFile(path)
    d = json.load(z.open(z.namelist()[0]))
    inv = {v: k for k, v in d.get("tag_dictionary", {}).items()}
    out = {}
    for p, f in d["files"].items():
        if p.endswith(".mra"):
            out[p] = {inv.get(t, str(t)) for t in f.get("tags", [])}
    return out

def settle(ours, rot, tags):
    """Return (final status, note)."""
    s = {t for t in tags if t.startswith("screen")}
    if not s - {"screenhorizontalscanrate15khz", "screenhorizontalscanrate31khz"}:
        return ours, ""                                 # upstream has no opinion
    ccw, cw, flip = "screentateccw" in s, "screentatecw" in s, "screentateflip" in s
    if "screennotate" in s and not (ccw or cw):
        if ours.startswith("horizontal"):
            return ours, "confirmed by DB tags"
        return ours, "CONFLICT: DB tags say not for tate"
    if ccw:
        if ours == "native":
            return ours, "confirmed by DB tags"
        if ours == "flip setting":
            return ours, "confirmed by DB tags"
        if ours.startswith("vertical, direction unknown"):
            return ("native or flip setting" if (cw and flip) else "native"), "settled by DB tags"
        if ours.startswith("UPSIDE DOWN"):
            return "flip setting", "settled by DB tags (core has a flip)"
        return ours, "CONFLICT: DB tags say playable on CCW tate"
    if cw:
        if ours.startswith("UPSIDE DOWN"):
            return ours, "confirmed by DB tags"
        if ours.startswith("vertical, direction unknown"):
            return "UPSIDE DOWN (no flip known)", "settled by DB tags (CW only)"
        return ours, "CONFLICT: DB tags say CW tate only"
    return ours, ""

def main(picks, *sources):
    dbs = {}
    for spec in sources:
        label, path = spec.split("=", 1)
        dbs[label] = load(path)
    rows = list(csv.DictReader(open(picks, encoding="utf-8")))
    for r in rows:
        tags = dbs.get(r["database"], {}).get(r["mra_path"], set())
        r["db_screen_tags"] = " ".join(sorted(t[6:] for t in tags if t.startswith("screen") and "scanrate" not in t))
        r["tate_ccw_cab"], r["tag_note"] = settle(r["tate_ccw_cab"], r["rotation"], tags)
    with open(picks, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main(*sys.argv[1:])
