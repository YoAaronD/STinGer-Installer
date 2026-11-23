"""Generate the STinGer Downloader databases.

usage: python3 -I tools/build_db.py <picks.csv> <data_dir> <out_dir> <label=repo_dir> [...] [variant=yoko]

Tate (default): data/layout.csv, writes db.json.zip (add-on) and full.json.zip (full install).
Yoko (variant=yoko): data/layout_yoko.csv, horizontal games, writes yoko.json.zip. Its folders sit
in _Arcade next to the normal arcade library, which a yoko cab keeps.

Every entry points at the MRA inside its upstream repo, pinned to the commit we built from,
and is saved under _Arcade/<layout folder>/<display name>.mra. STinGer hosts no MRAs itself.
"""
import csv, hashlib, json, os, re, subprocess, sys, time, urllib.parse, zipfile

DB_ID = "YoAaronD/STinGer-Installer"
DB_URL = "https://raw.githubusercontent.com/YoAaronD/STinGer-Installer/db/db.json.zip"
# Full install (the flavors): same db_id, so switching between the two cleans up after itself.
FULL_DB_URL = "https://raw.githubusercontent.com/YoAaronD/STinGer-Installer/db/full.json.zip"
# ROM list: its own repo and database, so a takedown there can never take the menu with it.
ROMS_DB_ID = "YoAaronD/STinGer-ROMs"
ROMS_DB_URL = "https://raw.githubusercontent.com/YoAaronD/STinGer-ROMs/main/db.json.zip"
YOKO_DB_URL = "https://raw.githubusercontent.com/YoAaronD/STinGer-Installer/db/yoko.json.zip"
ADDON_ROOT = "_Arcade/_Vertical Arcade"
REPOS = {  # label -> GitHub owner/repo the MRAs are downloaded from
    "distribution": "MiSTer-devel/Distribution_MiSTer",
    "jotego": "jotego/jtcores_mister",
    "coinop": "Coin-OpCollection/Distribution-MiSTerFPGA",
    "ongo": "OngoGablogian/MiSTer_Ongo",
    "kuze": "kuzearcade/kuzecores",
    "slopcore": "TheJesusFish/Slop-Core",
    "jlrh": "jlrh/jlrh-misterfpga-db",
    # shmupfan's, decoryah's and Blackwine's MRAs live in other repos; mirror_db.py records each one's URL in .urls.json
}
# Filter tags per tier. Downloader lowercases tags and ignores '-' and '_'.
TIER_TAG = {"core": "stg", "fixed": "stgfixed", "multidirectional": "stgmultidirectional",
            "overhead": "stgoverhead", "practice": "stgpractice", "hack": "stghacks", "other": "tateother", "3d": "stg3d"}

def read_csv(path):
    return list(csv.DictReader(l for l in open(path, encoding="utf-8") if not l.startswith("#")))

def read_layout(path):
    return {r["tier"]: (r["folder"], (r.get("in_build") or r.get("in_tate_build")) == "yes") for r in read_csv(path)}

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

def year_of(r):
    m = re.match(r"(19|20)\d\d", r.get("year") or "")
    return m.group(0) if m else "Unknown year"

HARDWARE_TIERS = {"core"}  # the by-hardware and by-year views hold Core STGs only
MIN_BOARD_GAMES = 2  # boards with fewer tate STGs than this go to "Other hardware"

def is_tate(row):
    s = row["tate_ccw_cab"]
    return not (s.startswith("horizontal") or s == "unknown")

def is_yoko(row):
    return row["yoko_cab"].startswith("native")

def main(picks, data_dir, out_dir, *sources):
    opts = dict(s.split("=", 1) for s in sources
                if s.split("=", 1)[0] in ("mad", "shmupfan_db", "core_dbs", "variant", "roms_dbs"))
    yoko = opts.get("variant") == "yoko"
    layout = read_layout(os.path.join(data_dir, "layout_yoko.csv" if yoko else "layout.csv"))
    fits = is_yoko if yoko else is_tate
    mad_csv = opts.get("mad")
    sources = tuple(s for s in sources if s.split("=", 1)[0] not in opts)
    board_of = read_hardware(data_dir, mad_csv)
    hardware_entries = []  # (board, file name, entry) for the _STG Hardware view
    year_entries = []  # (year, file name, entry) for the _By Year view
    game_zips = []     # ([zip names], is_cv1000) for each game, for the full install's ROM list
    used_cores = set()  # core names STinGer's games use, for the cores the full install delivers
    display = {r["setname"]: r["display_name"] for r in read_csv(os.path.join(data_dir, "display_names.csv"))}
    roots = dict(s.split("=", 1) for s in sources)
    commits = {k: subprocess.check_output(["git", "-C", v, "rev-parse", "HEAD"], text=True).strip()
               for k, v in roots.items() if k in REPOS}
    url_maps = {k: json.load(open(os.path.join(v, ".urls.json"))) for k, v in roots.items()
                if os.path.exists(os.path.join(v, ".urls.json"))}

    tags, files, folders, skipped = {}, {}, {}, []
    def tag_ids(*names):
        return [tags.setdefault(n, len(tags)) for n in names]
    def add_folder(path, *tag_names):  # the folder and every parent folder up to _Arcade
        parts = path.split("/")
        for i in range(2, len(parts) + 1):
            folders.setdefault("/".join(parts[:i]), {"tags": tag_ids("arcade")})
        folders[path] = {"tags": tag_ids(*tag_names)}

    for r in read_csv(picks):
        folder, in_build = layout.get(r["tier"], (None, False))
        if not in_build or not fits(r):
            continue
        if r["core_status"].startswith("NOT") and r["core"] != "ikacore_CV1k":
            skipped.append((r["mra_name"], "core not shipped anywhere: " + r["core"])); continue
        src = os.path.join(roots[r["database"]], r["mra_path"])
        blob = open(src, "rb").read()
        game_zips.append((mra_zips(blob), r["core"] == "ikacore_CV1k"))
        used_cores.add((r["database"], r["core"].lower()))
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
        add_folder(f"_Arcade/{folder}", "arcade", TIER_TAG[r["tier"]])
        if r["tier"] in HARDWARE_TIERS:
            hardware_entries.append((board_of(r), os.path.basename(dest), files[dest], extra))
            year_entries.append((year_of(r), os.path.basename(dest), files[dest], extra))

    # _STG Hardware/<board>/: the same MRAs again, grouped by arcade board
    counts = {}
    for b, *_ in hardware_entries: counts[b] = counts.get(b, 0) + 1
    hw_root = "_Arcade/" + layout["hardware"][0]
    for b, name, entry, extra in hardware_entries:
        board = b if counts[b] >= MIN_BOARD_GAMES else "Other hardware"
        # MiSTer's core list only shows folders whose names start with "_" (it hides the rest)
        path = f"{hw_root}/_{safe_name(board)}/{name}"
        files[path] = dict(entry, tags=tag_ids("arcade", "stghardware", *extra))
        add_folder(f"{hw_root}/_{safe_name(board)}", "arcade", "stghardware")

    # _By Year/<year>/: the same MRAs again, grouped by release year
    if "year" in layout:
        yr_root = "_Arcade/" + layout["year"][0]
        for y, name, entry, extra in year_entries:
            path = f"{yr_root}/_{y}/{name}"
            files[path] = dict(entry, tags=tag_ids("arcade", "stgyear", *extra))
            add_folder(f"{yr_root}/_{y}", "arcade", "stgyear")
    folders["_Arcade"] = {"tags": tag_ids("arcade")}

    db = {
        "v": 1,
        "db_id": DB_ID,
        "db_url": DB_URL,
        "timestamp": int(time.time()),
        "files": dict(sorted(files.items())),
        "folders": dict(sorted(folders.items())),
        "tag_dictionary": tags,
        # CV1000 games are in by default (they need Raki's Patreon core); tagged cv1000 so they can be skipped.
    }
    os.makedirs(out_dir, exist_ok=True)
    if yoko:
        write_db(dict(db, db_url=YOKO_DB_URL), out_dir, "yoko")
    else:
        write_db(db, out_dir, "db")
        write_db(full_variant(db, opts.get("shmupfan_db"), opts.get("core_dbs", ""), used_cores), out_dir, "full")
        if opts.get("roms_dbs"):
            write_db(roms_db(opts["roms_dbs"].split(","), game_zips), out_dir, "roms")
    by_folder = {}
    for p in files:
        k = "/".join(p.split("/")[1:-1]) if not p.startswith(hw_root + "/") else hw_root[8:]
        by_folder[k] = by_folder.get(k, 0) + 1
    print(f"{len(files)} MRAs in {len(folders) - 1} folders: {dict(sorted(by_folder.items()))}")
    for name, why in skipped: print("  skipped:", name, "-", why)

def write_db(db, out_dir, name):
    with open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=1, ensure_ascii=False)
    with zipfile.ZipFile(os.path.join(out_dir, name + ".json.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("db.json", json.dumps(db, separators=(",", ":"), ensure_ascii=False))

def mra_zips(blob):
    """Zip names an MRA asks for, e.g. zip="1941j.zip|1941.zip" -> ["1941j.zip", "1941.zip"]."""
    names = []
    for m in re.finditer(rb'zip="([^"]+)"', blob):
        for z in m.group(1).decode("utf-8", "replace").split("|"):
            z = z.strip().lower()
            if z and z not in names:
                names.append(z)
    return names

def rom_index(roms_dbs):
    """zip name -> entry from the ROM databases, first database wins (list them in priority order).
    Paths use the "|games/..." form: games folder on whichever drive holds it (SD or USB)."""
    index = {}
    for path in roms_dbs:
        with zipfile.ZipFile(path) as z:
            d = json.loads(z.read(z.namelist()[0]))
        for p, v in d["files"].items():
            if not p.lower().endswith(".zip"):
                continue
            rel = p.lstrip("|")
            if not rel.startswith("games/"):
                continue
            index.setdefault(os.path.basename(rel).lower(),
                             ("|" + rel, {"hash": v["hash"], "size": v["size"], "url": v["url"]}))
    return index

def roms_db(roms_dbs, game_zips):
    """STinGer-ROMs: exactly the ROM zips STinGer's games ask for, pointing at the same files the ROM
    databases use (Update All's Arcade ROMs first, then Ongo). Zips only CV1000 games use are tagged
    cv1000, so they can be skipped along with those games ("filter = !cv1000")."""
    tags = {}
    def tag_ids(*names):
        return [tags.setdefault(n, len(tags)) for n in names]
    index = rom_index(roms_dbs)
    needed = {}
    for zips, cv in game_zips:
        for z in zips:
            needed[z] = needed.get(z, True) and cv
    files, folders = {}, {"|games": {"tags": tag_ids("arcade", "stgroms")}}
    for z, only_cv in sorted(needed.items()):
        if z not in index:
            continue
        path, entry = index[z]
        files[path] = dict(entry, tags=tag_ids("arcade", "stgroms", *(("cv1000",) if only_cv else ())))
        folders.setdefault(path.rsplit("/", 1)[0], {"tags": tag_ids("arcade", "stgroms")})
    return {"v": 1, "db_id": ROMS_DB_ID, "db_url": ROMS_DB_URL, "timestamp": int(time.time()),
            "files": files, "folders": dict(sorted(folders.items())), "tag_dictionary": tags}

def full_variant(db, shmupfan_db, core_dbs="", used_cores=()):
    """The full install: STinGer's folders sit straight in _Arcade (the other databases ship
    cores only there), and STinGer also delivers cores from databases with no tags to trim
    their loose MRAs with: all of shmupfan's, and just the ones STinGer's games use from each
    of core_dbs (decoryah, Slop-Core, jlrh, Blackwine), so a database with dozens of
    cores doesn't install them all for one or two games."""
    def move(path):
        return "_Arcade" + path[len(ADDON_ROOT):] if path.startswith(ADDON_ROOT + "/") else path
    tags = dict(db["tag_dictionary"])
    files = {move(p): v for p, v in db["files"].items()}
    folders = {move(p): v for p, v in db["folders"].items() if p != ADDON_ROOT}
    def add_cores(path, tag, keep):
        with open(path, "rb") as f:
            raw = f.read()
        if path.endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                raw = z.read(z.namelist()[0])
        src = json.loads(raw)
        core_tags = [tags.setdefault(n, len(tags)) for n in ("arcade", tag)]
        for p, v in src["files"].items():
            if p.startswith("_Arcade/cores/") and p.endswith(".rbf") and keep(p):
                url = v.get("url") or src["base_files_url"] + urllib.parse.quote(p)
                files[p] = {"hash": v["hash"], "size": v["size"], "url": url, "tags": core_tags}
        folders.setdefault("_Arcade/cores", {"tags": core_tags})
    if shmupfan_db:
        add_cores(shmupfan_db, "shmupfancores", lambda p: True)
    def core_name(p):  # metro_20261018c.rbf -> metro
        return re.sub(r"_[0-9][0-9a-z]*$", "", os.path.basename(p)[:-4]).lower()
    for spec in filter(None, core_dbs.split(",")):
        label, path = spec.split(":", 1)
        add_cores(path, "stingercores", lambda p: (label, core_name(p)) in used_cores)
    return dict(db, db_url=FULL_DB_URL, files=dict(sorted(files.items())),
                folders=dict(sorted(folders.items())), tag_dictionary=tags)

if __name__ == "__main__":
    main(*sys.argv[1:])
