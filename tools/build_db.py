"""Generate the STinGer Downloader database (tate build).

usage: python3 -I tools/build_db.py <picks.csv> <data_dir> <out_dir> <label=repo_dir> [...]

Every entry points at the MRA inside its upstream repo, pinned to the commit we built from,
and is saved under _Arcade/<layout folder>/<display name>.mra. STinGer hosts no MRAs itself.
"""
import csv, hashlib, json, os, re, subprocess, sys, time, urllib.parse, zipfile

DB_ID = "YoAaronD/STinGer-Installer"
DB_URL = "https://raw.githubusercontent.com/YoAaronD/STinGer-Installer/db/db.json.zip"
REPOS = {  # label -> GitHub owner/repo the MRAs are downloaded from
    "distribution": "MiSTer-devel/Distribution_MiSTer",
    "jotego": "jotego/jtcores_mister",
    "coinop": "Coin-OpCollection/Distribution-MiSTerFPGA",
    "ongo": "OngoGablogian/MiSTer_Ongo",
    "kuze": "kuzearcade/kuzecores",
    # shmupfan's MRAs live in several core repos; mirror_db.py records each one's URL in .urls.json
}
# Filter tags per tier. Downloader lowercases tags and ignores '-' and '_'.
TIER_TAG = {"core": "stg", "fixed": "stgfixed", "multidirectional": "stgmultidirectional",
            "overhead": "stgoverhead", "practice": "stgpractice", "hack": "stghacks", "other": "tateother"}

def read_csv(path):
    return list(csv.DictReader(l for l in open(path, encoding="utf-8") if not l.startswith("#")))

def read_layout(path):
    prefix = next(l.split("=", 1)[1].strip() for l in open(path, encoding="utf-8") if l.startswith("# prefix="))
    return {r["tier"]: (r["folder"].replace("{prefix}", prefix), r["in_tate_build"] == "yes") for r in read_csv(path)}

def safe_name(name):
    name = re.sub(r'[<>:"/\\|?*]', "-", name)  # characters Windows / exFAT won't take
    return re.sub(r"\s+", " ", name).strip().rstrip(".")

def read_hardware(data_dir, mad_csv):
    hw = {r["key"]: r["board"] for r in read_csv(os.path.join(data_dir, "hardware.csv"))}
    mad = {}
    if mad_csv and os.path.exists(mad_csv):
        mad = {r["setname"]: r.get("platform", "") for r in csv.DictReader(open(mad_csv, encoding="utf-8-sig"))}
    def board(row):
        plat = mad.get(row["setname"], "")
        return (hw.get(row["core"]) or (hw.get("mad:" + plat) if plat else None)
                or (re.sub(r" (hardware|based)$", "", plat) if plat else None) or row["core"])
    return board

HARDWARE_TIERS = {"core", "fixed", "multidirectional", "overhead"}
MIN_BOARD_GAMES = 2  # boards with fewer tate STGs than this go to "Other hardware"

def is_tate(row):
    s = row["tate_ccw_cab"]
    return not (s.startswith("horizontal") or s == "unknown")

def main(picks, data_dir, out_dir, *sources):
    layout = read_layout(os.path.join(data_dir, "layout.csv"))
    prefix = next(l.split("=", 1)[1].strip() for l in open(os.path.join(data_dir, "layout.csv"), encoding="utf-8")
                  if l.startswith("# prefix="))
    mad_csv = next((s.split("=", 1)[1] for s in sources if s.startswith("mad=")), None)
    sources = tuple(s for s in sources if not s.startswith("mad="))
    board_of = read_hardware(data_dir, mad_csv)
    hardware_entries = []  # (board, file name, entry) for the _STG Hardware view
    display = {r["setname"]: r["display_name"] for r in read_csv(os.path.join(data_dir, "display_names.csv"))}
    roots = dict(s.split("=", 1) for s in sources)
    commits = {k: subprocess.check_output(["git", "-C", v, "rev-parse", "HEAD"], text=True).strip()
               for k, v in roots.items() if k in REPOS}
    url_maps = {k: json.load(open(os.path.join(v, ".urls.json"))) for k, v in roots.items()
                if os.path.exists(os.path.join(v, ".urls.json"))}

    tags, files, folders, skipped = {}, {}, {}, []
    def tag_ids(*names):
        return [tags.setdefault(n, len(tags)) for n in names]

    for r in read_csv(picks):
        folder, in_build = layout.get(r["tier"], (None, False))
        if not in_build or not is_tate(r):
            continue
        if r["core_status"].startswith("NOT") and r["core"] != "ikacore_CV1k":
            skipped.append((r["mra_name"], "core not shipped anywhere: " + r["core"])); continue
        src = os.path.join(roots[r["database"]], r["mra_path"])
        blob = open(src, "rb").read()
        base = display.get(r["setname"]) or os.path.basename(r["mra_path"])[:-4]
        dest = f"_Arcade/{folder}/{safe_name(base)}.mra"
        if dest in files:  # same file name from two sources: keep both, label the second
            dest = f"_Arcade/{folder}/{safe_name(base)} [{r['database']}].mra"
        extra = []
        if r["core"] == "ikacore_CV1k": extra.append("cv1000")
        if r["rotation"].startswith("cw"): extra.append("needsflip")
        files[dest] = {
            "hash": hashlib.md5(blob).hexdigest(),
            "size": len(blob),
            "url": url_maps[r["database"]][r["mra_path"]] if r["database"] in url_maps else
                   f"https://raw.githubusercontent.com/{REPOS[r['database']]}/{commits[r['database']]}/"
                   + urllib.parse.quote(r["mra_path"]),
            "tags": tag_ids("arcade", TIER_TAG[r["tier"]], *extra),
        }
        folders.setdefault(f"_Arcade/{folder}", {"tags": tag_ids("arcade", TIER_TAG[r["tier"]])})
        if r["tier"] in HARDWARE_TIERS:
            hardware_entries.append((board_of(r), os.path.basename(dest), files[dest], extra))

    # _STG Hardware/<board>/: the same MRAs again, grouped by arcade board
    counts = {}
    for b, *_ in hardware_entries: counts[b] = counts.get(b, 0) + 1
    hw_root = f"_Arcade/{prefix} Hardware"
    for b, name, entry, extra in hardware_entries:
        board = b if counts[b] >= MIN_BOARD_GAMES else "Other hardware"
        path = f"{hw_root}/{safe_name(board)}/{name}"
        files[path] = dict(entry, tags=tag_ids("arcade", "stghardware", *extra))
        folders.setdefault(f"{hw_root}/{safe_name(board)}", {"tags": tag_ids("arcade", "stghardware")})
    folders.setdefault(hw_root, {"tags": tag_ids("arcade", "stghardware")})
    folders["_Arcade"] = {"tags": tag_ids("arcade")}

    db = {
        "v": 1,
        "db_id": DB_ID,
        "db_url": DB_URL,
        "timestamp": int(time.time()),
        "files": dict(sorted(files.items())),
        "folders": dict(sorted(folders.items())),
        "tag_dictionary": tags,
        # Raki's CV1000 core is Patreon-only: leave those entries off unless the user opts in.
        "default_options": {"filter": "!cv1000"},
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "db.json"), "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=1, ensure_ascii=False)
    with zipfile.ZipFile(os.path.join(out_dir, "db.json.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("db.json", json.dumps(db, separators=(",", ":"), ensure_ascii=False))
    by_folder = {}
    for p in files: by_folder[p.split("/")[1]] = by_folder.get(p.split("/")[1], 0) + 1
    print(f"{len(files)} MRAs in {len(folders) - 1} folders: {dict(sorted(by_folder.items()))}")
    for name, why in skipped: print("  skipped:", name, "-", why)

if __name__ == "__main__":
    main(*sys.argv[1:])
