#!/usr/bin/env bash
# Fetch upstream MRA sources and Downloader databases into ./sources (gitignored).
# Only MRA files and database files are checked out, never cores or other binaries.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p sources

sparse_mras() {  # <dir> <repo url>
  local dir="sources/$1" url="$2"
  if [ ! -d "$dir/.git" ]; then
    git clone -q --filter=blob:none --no-checkout --depth 1 "$url" "$dir"
  else
    git -C "$dir" fetch -q --depth 1 origin && git -C "$dir" reset -q --soft FETCH_HEAD
  fi
  git -C "$dir" sparse-checkout set --no-cone '/_Arcade/**/*.mra'
  git -C "$dir" checkout -q HEAD -- . 2>/dev/null || git -C "$dir" checkout -q HEAD
  # list core file names so core_check.py can tell which cores ship
  git -C "$dir" ls-tree -r --name-only HEAD | grep -i '_Arcade/cores/.*\.rbf$' | sed 's#.*/##; s/\.rbf$//' > "$dir/.rbf_list" || true
}

sparse_mras distribution https://github.com/MiSTer-devel/Distribution_MiSTer
sparse_mras jotego       https://github.com/jotego/jtcores_mister
sparse_mras coinop       https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA
sparse_mras ongo         https://github.com/OngoGablogian/MiSTer_Ongo
sparse_mras kuze         https://github.com/kuzearcade/kuzecores

# MiSTer Arcade Database (genre / rotation / flip per setname)
if [ ! -d sources/mad/.git ]; then
  git clone -q --depth 1 https://github.com/Toryalai1/MiSTer_ArcadeDatabase sources/mad
else
  git -C sources/mad pull -q --ff-only
fi

# Downloader databases (for upstream screen tags)
mkdir -p sources/dbs
git -C sources/distribution show HEAD:db.json.zip        > sources/dbs/distribution.json.zip
git -C sources/jotego       show HEAD:jtbindb.json.zip   > sources/dbs/jotego.json.zip
git -C sources/coinop fetch -q --depth 1 --filter=blob:none origin db
git -C sources/coinop show FETCH_HEAD:db.json.zip        > sources/dbs/coinop.json.zip
git -C sources/ongo   fetch -q --depth 1 --filter=blob:none origin db
git -C sources/ongo   show FETCH_HEAD:db.json.zip        > sources/dbs/ongo.json.zip
git -C sources/kuze fetch -q --depth 1 --filter=blob:none origin db
git -C sources/kuze show FETCH_HEAD:db.json.zip          > sources/dbs/kuze.json.zip
python3 -I - <<'PY'   # kuze ships its cores outside the repo tree: list them from its database
import json, zipfile
z = zipfile.ZipFile("sources/dbs/kuze.json.zip"); d = json.load(z.open(z.namelist()[0]))
open("sources/kuze/.rbf_list", "w").write("\n".join(p.split("/")[-1][:-4] for p in d["files"] if p.lower().endswith(".rbf")) + "\n")
PY

# shmupfan's database points at MRAs in its individual core repos: mirror them
mkdir -p sources/shmupfan_db
curl -sSL -o sources/dbs/shmupfan.json https://raw.githubusercontent.com/shmupfan/Distribution/main/db.json \
  || git -C sources/shmupfan_db clone -q --depth 1 https://github.com/shmupfan/Distribution . 2>/dev/null
[ -s sources/dbs/shmupfan.json ] || cp sources/shmupfan_db/db.json sources/dbs/shmupfan.json
python3 -I tools/mirror_db.py sources/dbs/shmupfan.json sources/shmupfan
# Flavor bases: MiSTerAddons' official MiSTercade inis + control mappings, and MiSTer's stock MiSTer.ini
for pair in "misteraddons_ini misteraddons/mister_ini" "misteraddons_mistercade misteraddons/MiSTercade"; do
  set -- $pair
  if [ ! -d "sources/$1/.git" ]; then git clone -q --depth 1 "https://github.com/$2" "sources/$1"
  else git -C "sources/$1" pull -q --ff-only; fi
done
if [ ! -d sources/main_mister/.git ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/MiSTer-devel/Main_MiSTer sources/main_mister
  git -C sources/main_mister sparse-checkout set --no-cone /MiSTer.ini
else git -C sources/main_mister pull -q --ff-only; fi
echo "sources ready"
