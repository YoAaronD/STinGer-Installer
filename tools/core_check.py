"""Flag picks whose core (.rbf) isn't shipped by any scanned database.

usage: python3 -I tools/core_check.py <picks.csv> <label=repo_dir> [...]
MiSTer resolves an MRA's <rbf>X</rbf> to X.rbf or X_<anything>.rbf, so match the same way.
"""
import csv, os, sys

def main(picks, *sources):
    stems = set()
    for spec in sources:
        d = spec.split("=", 1)[1]
        for dp, _, fs in os.walk(os.path.join(d, "_Arcade")):
            stems |= {f[:-4].lower() for f in fs if f.lower().endswith(".rbf")}
        listing = os.path.join(d, ".rbf_list")  # optional: names from `git ls-tree` for sparse clones
        if os.path.exists(listing):
            stems |= {l.strip().lower() for l in open(listing) if l.strip()}
    ships = lambda rb: any(s == rb or s.startswith(rb + "_") for s in stems)
    rows = list(csv.DictReader(open(picks, encoding="utf-8")))
    for r in rows:
        r["core_status"] = ("ships with databases" if ships(r["core"].lower())
                            else "NOT in any database - install separately")
    with open(picks, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print({r["core"] for r in rows if r["core_status"].startswith("NOT")})

if __name__ == "__main__":
    main(*sys.argv[1:])
