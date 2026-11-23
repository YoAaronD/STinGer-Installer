#!/usr/bin/env bash
# Build a STinGer install image from an official Mr. Fusion release.
#
#   installer/build_image.sh [flavor ...]        (default: mistercade-v2 mistercade-v1 regular)
#
# Run from the repo root on Linux / WSL Ubuntu, after tools/build.sh has made build/flavors/.
# Needs: sudo apt install -y p7zip-full mtools unzip zip curl python3-pil
#
# What it changes, nothing else: Mr. Fusion's own Linux, partitioning and install steps are untouched.
#   - release.7z on the MRFUSION partition gets the flavor's MiSTer.ini, downloader.ini and
#     MiSTercade mapping drop-in, so the first boot lands on a STinGer setup
#   - splash.png is replaced with STinGer's (installer/splash.txt holds its words)
#
# Env:
#   MRF_ZIP=path/to/mr-fusion-*.img.zip   use a local Mr. Fusion release (or Heber's fork for heber-ms2)
#   OUT=dist                              where the images go
#
# Mr. Fusion is GPLv3 (https://github.com/MiSTer-devel/mr-fusion); the images say so and link back.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${OUT:-$ROOT/dist}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
FLAVORS=("$@")
[ ${#FLAVORS[@]} -eq 0 ] && FLAVORS=(mistercade-v2 mistercade-v1 regular)

for tool in 7z mcopy mdel mdir unzip zip python3; do
  command -v $tool >/dev/null || { echo "missing $tool: sudo apt install -y p7zip-full mtools unzip zip python3-pil"; exit 1; }
done

# 1. the Mr. Fusion release
if [ -z "${MRF_ZIP:-}" ]; then
  url=$(curl -fsSL https://api.github.com/repos/MiSTer-devel/mr-fusion/releases/latest \
        | grep -o '"browser_download_url": *"[^"]*\.img\.zip"' | head -1 | cut -d'"' -f4)
  [ -n "$url" ] || { echo "couldn't find the Mr. Fusion release; download it and set MRF_ZIP"; exit 1; }
  echo "Mr. Fusion: $url"
  MRF_ZIP=$WORK/$(basename "$url")
  curl -fL -o "$MRF_ZIP" "$url"
fi
unzip -q -o "$MRF_ZIP" -d "$WORK/mrf"
BASE_IMG=$(find "$WORK/mrf" -name '*.img' | head -1)
[ -n "$BASE_IMG" ] || { echo "no .img inside $MRF_ZIP"; exit 1; }
MRF_NAME=$(basename "$MRF_ZIP" .img.zip)

# offset of partition 1 (the MRFUSION FAT partition), read from the MBR
OFFSET=$(python3 - "$BASE_IMG" <<'PY'
import struct, sys
mbr = open(sys.argv[1], "rb").read(512)
assert mbr[510:512] == b"\x55\xaa", "no MBR"
print(struct.unpack_from("<I", mbr, 0x1BE + 8)[0] * 512)
PY
)
export MTOOLS_SKIP_CHECK=1
mdir -i "$BASE_IMG@@$OFFSET" ::/ | grep -qi 'release *7z' || { echo "release.7z not found on the MRFUSION partition"; exit 1; }

# 2. splash
python3 "$ROOT/installer/make_splash.py" "$ROOT/installer/splash.txt" "$WORK/splash.png"

# 3. the stock release, unpacked once
mcopy -i "$BASE_IMG@@$OFFSET" ::/release.7z "$WORK/release.7z"
7z x -y -bd -o"$WORK/release" "$WORK/release.7z" >/dev/null
[ -d "$WORK/release/files" ] || { echo "unexpected release.7z layout (no files/)"; exit 1; }

mkdir -p "$OUT"
for flavor in "${FLAVORS[@]}"; do
  src=$ROOT/build/flavors/$flavor
  [ -f "$src/downloader.ini" ] || { echo "no build/flavors/$flavor (run tools/build.sh first)"; exit 1; }
  echo "== $flavor"
  img=$WORK/STinGer-$flavor.img
  cp "$BASE_IMG" "$img"

  # release.7z + this flavor's files
  rm -rf "$WORK/rel" && cp -r "$WORK/release" "$WORK/rel"
  cp "$src"/*.ini "$WORK/rel/files/"
  printf 'STinGer %s, built %s on %s\nhttps://github.com/YoAaronD/STinGer-Installer\n' \
    "$flavor" "$(date -u +%Y-%m-%d)" "$MRF_NAME" > "$WORK/rel/files/STinGer.txt"
  rm -f "$WORK/release.new.7z"
  (cd "$WORK/rel" && 7z a -t7z -mx=9 -bd "$WORK/release.new.7z" . >/dev/null)

  mdel -i "$img@@$OFFSET" ::/release.7z
  mcopy -i "$img@@$OFFSET" "$WORK/release.new.7z" ::/release.7z
  mdel -i "$img@@$OFFSET" ::/splash.png 2>/dev/null || true
  mcopy -i "$img@@$OFFSET" "$WORK/splash.png" ::/splash.png
  mdir -i "$img@@$OFFSET" ::/ | grep -i -E 'release|splash|free'

  (cd "$WORK" && zip -q -9 "$OUT/STinGer-$flavor.img.zip" "STinGer-$flavor.img")
  rm -f "$img"
  echo "-> $OUT/STinGer-$flavor.img.zip"
done
