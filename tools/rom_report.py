#!/usr/bin/env python3
"""ROM checklist: which zips each STinGer game needs, and which of them the Arcade ROMs database
(zakk4223/ArcadeROMsDB_MiSTer, the one Update All switches on) provides.

usage: rom_report.py <full.json> <picks.csv> <ongo.json.zip> <arcade_roms_db.json.zip> <sources dir> <out dir>
ROMs counted: the ones Ongo's database ships (part of STinGer's full install) plus Update All's
Arcade ROMs database (optional switch). The "where" column says which of the two each game needs.
writes <out dir>/roms.csv (one row per game) and <out dir>/ROMS.md (summary + the zips to supply yourself)

Status per game:
  covered      every zip the MRA lists is in the ROMs database
  parent only  the game's own zip is missing but its parent's is there. Works: the ROM databases use
               merged sets (clone files inside the parent zip); confirmed with 1941 (Japan), 2026-11-21
  partial      some zips are there, but not the game's own (e.g. GunNail: nmk004.zip yes, gunnail.zip no)
  missing      none of its zips are in the ROMs database: supply them yourself
"""
import csv, json, os, re, sys, zipfile, collections

def zips_in(db_zip):
    with zipfile.ZipFile(db_zip) as z:
        d = json.loads(z.read(z.namelist()[0]))
    return {os.path.basename(p).lower() for p in d["files"] if p.lower().endswith(".zip")}

def main(full_json, picks_csv, ongo_db, roms_db, sources, out_dir):
    ongo, ardb = zips_in(ongo_db), zips_in(roms_db)
    have = ongo | ardb

    db = json.load(open(full_json, encoding="utf-8"))
    # one entry per game: the main folders, not the By Hardware / By Year copies
    games = {}
    for path in db["files"]:
        if path.endswith(".mra") and "/_By " not in path:
            games[os.path.basename(path)] = path
    picks = {}
    for r in csv.DictReader(open(picks_csv, encoding="utf-8")):
        picks.setdefault(os.path.basename(r["mra_path"]), r)

    rows, need_count = [], collections.Counter()
    for name, path in sorted(games.items(), key=lambda kv: kv[1].lower()):
        r = picks.get(name)
        if not r:
            continue
        mra = os.path.join(sources, r["database"], r["mra_path"])
        try:
            text = open(mra, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        zips = []
        for m in re.finditer(r'zip="([^"]+)"', text):
            for z in m.group(1).split("|"):
                z = z.strip().lower()
                if z and z not in zips:
                    zips.append(z)
        own = (r["setname"] or "").lower() + ".zip"
        parent = (r["parent"] or "").lower() + ".zip" if r["parent"] else ""
        if not zips:
            status = "no zip listed"
        elif all(z in have for z in zips):
            status = "covered"
        elif own not in have and all(z in have for z in zips if z != own) and any(
                z == parent or own.startswith(z[:-4]) for z in zips if z != own):
            # the game's own zip is missing; what's there is its parent set (named in the database,
            # or the usual clone naming: 1941j -> 1941, ddonpachj -> ddonpach)
            status = "parent only"
        elif any(z in have for z in zips):
            status = "partial"
        else:
            status = "missing"
        missing = [z for z in zips if z not in have]
        found = [z for z in zips if z in have]
        where = ("Ongo" if all(z in ongo for z in found) else
                 "Arcade ROMs DB" if all(z in ardb for z in found) else "both") if found else ""
        if status in ("partial", "missing"):
            for z in missing:
                need_count[z] += 1
        rows.append({
            "folder": os.path.dirname(path).split("/", 1)[1] if "/" in path else "",
            "game": name[:-4], "setname": r["setname"], "core": r["core"], "source": r["database"],
            "status": status, "roms_from": where, "zips": " | ".join(zips), "not_in_roms_db": " | ".join(missing),
        })

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "roms.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    stat = collections.Counter(r["status"] for r in rows)
    by_src = collections.defaultdict(collections.Counter)
    for r in rows:
        by_src[r["source"]][r["status"]] += 1
    order = ["covered", "parent only", "partial", "missing", "no zip listed"]
    md = ["# ROMs for STinGer's games", "",
          "STinGer's full install brings exactly the ROM zips its games use, pointing at the same files",
          "Update All's Arcade ROMs (zakk4223/ArcadeROMsDB_MiSTer) and Ongo use: about 2.2 GB, or 1.3 GB",
          "without the CV1000 games. This is how far that gets you, game by game; the `roms_from` column",
          "says which source each game's ROMs come from. Opt out with `!stgroms` in STinGer's filter line.",
          "Full list: [`roms.csv`](roms.csv). Regenerated with every database build.", "",
          "| Status | Games | Meaning |", "| --- | --- | --- |"]
    meaning = {
        "covered": "Everything it needs comes with STinGer's ROM list",
        "parent only": "Only the parent set is there (typical for Japanese versions). Works: the zips are merged sets, so the clone's files are inside (tested with 1941 Japan)",
        "partial": "Some files are there, but not the game's own zip",
        "missing": "Neither source has it: supply the zips yourself",
        "no zip listed": "The MRA names no zip (homebrew or built-in)",
    }
    for s in order:
        if stat[s]:
            md.append(f"| {s} | {stat[s]} | {meaning[s]} |")
    md += ["", "## By source", "", "| Source | " + " | ".join(s for s in order if stat[s]) + " |",
           "| --- |" + " --- |" * sum(1 for s in order if stat[s])]
    for src in sorted(by_src):
        md.append(f"| {src} | " + " | ".join(str(by_src[src][s]) for s in order if stat[s]) + " |")
    md += ["", "## Zips to supply yourself", "",
           "For games marked partial or missing. Put them in `games/mame/` on the SD card.",
           "The number is how many STinGer games use that zip.", ""]
    for z, n in sorted(need_count.items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"- `{z}` ({n})")
    open(os.path.join(out_dir, "ROMS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    from_ = collections.Counter(r["roms_from"] for r in rows if r["status"] == "covered")
    md.insert(md.index("## By source"), "Covered games by where their ROMs come from: " +
              ", ".join(f"{k} {v}" for k, v in from_.most_common()) + ".\n")
    open(os.path.join(out_dir, "ROMS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f"rom_report: {len(rows)} games, " + ", ".join(f"{s} {stat[s]}" for s in order if stat[s]))

if __name__ == "__main__":
    main(*sys.argv[1:7])
