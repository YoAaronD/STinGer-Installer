"""Build a candidate shmup list from MiSTer Distribution MRAs + the MiSTer Arcade Database.

usage: python3 -I tools/classify.py <ArcadeDatabase.csv> <overrides.csv> <out.csv> <label=dir> [<label=dir> ...]
"""
import csv, html, os, re, sys, collections
import xml.etree.ElementTree as ET

TIERS = {
    # core: scrolling / flying shmups
    "Shooter - Flying Vertical": "core", "Shooter - Flying Horizontal": "core",
    "Shooter - Flying": "core", "Shooter - Flying Diagonal": "core",
    "Shooter - Misc. Horizontal": "core", "Shooter - Misc. Vertical": "core",
    "Shooter - Flying (chase view)": "core", "Shooter": "core",
    # fixed shooters (Galaga, Invaders, Centipede...)
    "Shooter - Gallery": "fixed",
    # multidirectional (Asteroids, Robotron, Time Pilot, Bosconian...)
    "Shooter - Field": "multidirectional",
    # overhead run-and-gun / vehicle (Commando, Guwange, Out Zone, Jackal...)
    "Shooter - Walking": "overhead", "Shooter - Driving Vertical": "overhead",
    "Shooter - Driving Horizontal": "overhead", "Shooter - Driving": "overhead",
    "Shooter - Driving Diagonal": "overhead",
}

def norm_rot(s):
    s = (s or "").strip().lower().replace("(", " (").replace("  ", " ")
    if s.startswith("vertical (ccw"): return "ccw"
    if s.startswith("vertical (cw"): return "cw"
    if s.startswith("vertical"): return "vertical?"
    if "180" in s: return "horizontal180"
    if s.startswith("horizontal"): return "horizontal"
    return "horizontal?" if not s else "unknown"  # MiSTer MRAs omit the tag for horizontal games

def norm_flip(s):
    s = (s or "").strip().lower()
    return {"yes": "yes", "no": "no", "n-a": "n/a"}.get(s, "unknown")

def tate_ccw(rot, flip):
    if rot == "ccw": return "native"
    if rot == "cw": return "flip setting" if flip == "yes" else "UPSIDE DOWN (no flip known)"
    if rot == "vertical?": return "vertical, direction unknown"
    if rot == "horizontal?": return "horizontal? (no rotation tag): scaler rotation only"
    if rot.startswith("horizontal"): return "horizontal: scaler rotation only"
    return "unknown"

def yoko(rot):
    if rot == "horizontal?": return "native? (no rotation tag)"
    if rot.startswith("horizontal"): return "native"
    if rot in ("cw", "ccw", "vertical?"): return "vertical: scaler rotation"
    return "unknown"

def read_mra(path):
    raw = open(path, "rb").read().decode("utf-8", "replace")
    raw = re.sub(r"&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", raw)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    g = lambda t: (root.findtext(t) or "").strip()
    return {k: g(k) for k in ("name", "setname", "parent", "rbf", "rotation", "flip", "region",
                                "category", "year", "manufacturer", "platform")}

def main(mad_csv, ovr_csv, out, *sources):
    others = "--others" in sources
    sources = [x for x in sources if x != "--others"]
    mad = {r["setname"]: r for r in csv.DictReader(open(mad_csv, encoding="utf-8-sig"))}
    ovr = {}
    for r in csv.DictReader(l for l in open(ovr_csv, encoding="utf-8") if not l.startswith("#")):
        ovr[r["setname_or_title"]] = r
    ct_path = os.path.join(os.path.dirname(os.path.abspath(ovr_csv)), "core_tiers.csv")
    core_tier = {r["rbf"].lower(): r["tier"] for r in csv.DictReader(l for l in open(ct_path) if not l.startswith("#"))} if os.path.exists(ct_path) else {}
    rows, stats = [], collections.Counter()
    for src_spec in sources:
     label, dist = src_spec.split("=", 1)
     for dp, _, fs in os.walk(os.path.join(dist, "_Arcade")):
        for f in fs:
            if not f.endswith(".mra"): continue
            p = os.path.join(dp, f)
            m = read_mra(p)
            if not m: stats["unparseable"] += 1; continue
            d = (m["setname"] and mad.get(m["setname"])) or (m["parent"] and mad.get(m["parent"])) or {}
            cat = html.unescape(d.get("category", ""))
            title = html.unescape(d.get("parent_title", "") or m["name"])
            tier, src = TIERS.get(cat), "db category"
            o = ovr.get(m["setname"]) or ovr.get(title) or ovr.get(html.unescape(d.get("name", ""))) or next(
                (v for k, v in ovr.items() if k.startswith("re:") and re.search(k[3:], m["name"] or f, re.I)), None)
            excluded = False
            if o:
                tier = o["tier"] if o["action"] == "include" else None; src = "override: " + o["reason"]
                excluded = o["action"] == "exclude"
            if not d and not o:
                stats["not in DB"] += 1
                mc = re.sub(r"[^a-z]", "", m["category"].lower())
                if "shootemup" in mc or "shmup" in mc:  # MRA's own tag is specific enough
                    tier, src = "core", "MRA tag: " + m["category"]
                elif "gun" in mc:  # light-gun games aren't STGs
                    tier = None
                elif "shoot" in mc and m["rbf"].lower() in core_tier:
                    tier, src = core_tier[m["rbf"].lower()], "core rule: " + m["rbf"]
                elif "shoot" in mc:  # generic 'Shooter' -> needs a human look
                    tier, src = "unsorted", "MRA tag: " + m["category"] + "; not in DB"
            rot = norm_rot(m["rotation"] or d.get("rotation"))
            if o and (o.get("rotation") or "").strip():  # manual rotation fix, e.g. 'ccw (assumed)'
                rot = o["rotation"].split()[0].strip(); src += " | rotation: " + o["rotation"].strip()
            if not tier and others and not excluded and rot in ("ccw", "cw", "vertical?"):
                tier, src = "other", "vertical, not a shooter"
            if not tier: continue
            flip = norm_flip(m["flip"] or d.get("flip"))
            rows.append({
                "title": title, "mra_name": m["name"] or f[:-4], "setname": m["setname"],
                "region": m["region"], "parent": m["parent"],
                "alternative": "yes" if "_alternatives" in dp else "no",
                "tier": tier, "db_category": cat or m["category"], "core": m["rbf"],
                "year": m["year"] or d.get("year", ""),
                "manufacturer": html.unescape(m["manufacturer"] or d.get("manufacturer", "")),
                "rotation": rot, "flip": flip,
                "tate_ccw_cab": tate_ccw(rot, flip), "yoko_cab": yoko(rot),
                "database": label, "in_db": "yes" if d else "no", "source": src, "mra_path": os.path.relpath(p, dist),
            })
    rows.sort(key=lambda r: (r["alternative"], r["tier"], r["title"].lower()))
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(dict(stats))
    main_rows = [r for r in rows if r["alternative"] == "no"]
    print("total", len(rows), "main", len(main_rows))
    for k in ("database", "tier", "rotation", "tate_ccw_cab", "yoko_cab", "source"):
        print(k, collections.Counter(r[k] for r in main_rows).most_common())

if __name__ == "__main__":
    main(*sys.argv[1:])
