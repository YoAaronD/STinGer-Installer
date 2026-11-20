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
echo "sources ready"
