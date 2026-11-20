#!/usr/bin/env bash
# Rebuild data/picks.csv from upstream sources. Run tools/fetch_sources.sh first.
set -euo pipefail
cd "$(dirname "$0")/.."
S=sources
SRC="distribution=$S/distribution jotego=$S/jotego coinop=$S/coinop ongo=$S/ongo kuze=$S/kuze shmupfan=$S/shmupfan"
mkdir -p build

# 1. classify every MRA (shooter tiers, plus vertical non-shooters as "other")
python3 -I tools/classify.py "$S/mad/ArcadeDatabase.csv" data/overrides.csv build/classified.csv $SRC --others
# 2. one version per game: pinned > no hacks > Japan > World > newest revision
python3 -I tools/select_versions.py build/classified.csv data/prefer.csv build/picks.csv
# 3. flag cores no database ships (e.g. Raki's CV1000 core)
python3 -I tools/core_check.py build/picks.csv $SRC
# 4. fold in upstream screen tags (tate CW/CCW/flip)
python3 -I tools/tag_merge.py build/picks.csv \
  distribution=$S/dbs/distribution.json.zip jotego=$S/dbs/jotego.json.zip \
  coinop=$S/dbs/coinop.json.zip ongo=$S/dbs/ongo.json.zip kuze=$S/dbs/kuze.json.zip

# 5. publish a trimmed, sorted copy
python3 -I - <<'EOF'
import csv
r = list(csv.DictReader(open("build/picks.csv", encoding="utf-8")))
keep = ["mra_name","tier","tate_ccw_cab","tag_note","rotation","flip","core","core_status","database",
        "also_in","pick_reason","other_versions","year","manufacturer","db_category","setname","mra_path"]
order = {"core":0,"fixed":1,"multidirectional":2,"overhead":3,"3d":4,"practice":5,"hack":6,"other":7}
r.sort(key=lambda x: (order.get(x["tier"], 9), x["mra_name"].lower()))
with open("data/picks.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keep, extrasaction="ignore"); w.writeheader(); w.writerows(r)
print(f"data/picks.csv: {len(r)} entries")
EOF

# 6. generate the Downloader database (tate build) into build/db/
python3 -I tools/build_db.py data/picks.csv data build/db $SRC mad=$S/mad/ArcadeDatabase.csv

# 7. per-hardware flavors (MiSTercade V2 / V1 / regular) into build/flavors/
python3 -I tools/build_flavors.py $S build/flavors
