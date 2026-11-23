# STinGer Installer

A shmup-focused MiSTer build for **vertical (tate) CRT arcade cabinets**.

> Status: early. The game list is built and curated; the downloader database,
> ini templates and installer image are next.

> **Cave CV1000 games** (Mushihime-sama, Mushihime-sama Futari, Espgaluda II, DoDonPachi Dai-Fukkatsu, Ibara and more) are included, and they need Raki's CV1000 core, which is on [his Patreon](https://www.patreon.com/cw/ikamusume). It's a few dollars a month, and it's what makes these games possible on MiSTer. Put the core (`ikacore_CV1k_*.rbf`) in `_Arcade/cores`. To leave the CV1000 games out instead, set `filter = !cv1000` in the STinGer and STinGer-ROMs sections of downloader.ini.

## Goals

1. **An STG-focused MiSTer.** Every shooting game MiSTer can run, sorted into its own menu, without anyone combing through databases by hand.
2. **Leave everything else alone.** No consoles, no computer cores, no horizontal games cluttering a vertical cab.
3. **No config hassle.** Flash an SD card, boot, and it works on a CCW-rotated 15 kHz CRT out of the box.

## Scope (for now)

- **Tate, CCW-rotated monitor, CRT.** Horizontal games and console/computer cores are out of scope: on a rotated CRT they'd need scaler rotation, which looks poor at 15 kHz.
- **CW vs CCW isn't a filter.** Most cores can flip the picture, so every vertical game counts. The list still records each game's native direction, so you know which ones need a one-time flip.
- **Japanese versions preferred**, newest revision within the region, with hand-pinned exceptions (e.g. the original *Battle Garegga* over Type 2).

## How the list is built

```
tools/fetch_sources.sh   # sparse-clone MRAs + Downloader DBs into ./sources
tools/build.sh           # regenerate data/picks.csv
```

Sources: [Distribution](https://github.com/MiSTer-devel/Distribution_MiSTer),
[Jotego](https://github.com/jotego/jtcores_mister),
[Coin-Op Collection](https://github.com/Coin-OpCollection/Distribution-MiSTerFPGA),
[Ongo](https://github.com/OngoGablogian/MiSTer_Ongo),
[kuze](https://github.com/kuzearcade/kuzecores),
[Slop-Core](https://github.com/TheJesusFish/Slop-Core),
[decoryah](https://github.com/decoryah/MiSTer_decoryah),
[jlrh](https://github.com/jlrh/jlrh-misterfpga-db),
[Blackwine](https://github.com/TheJesusFish/Blackwine-SegaSystem1-2_MiSTer),
[shmupfan](https://github.com/shmupfan/Distribution),
and the [MiSTer Arcade Database](https://github.com/Toryalai1/MiSTer_ArcadeDatabase) for genre data.

| Step | Script | What it does |
| --- | --- | --- |
| 1 | `classify.py` | Tiers every MRA (core / fixed / multidirectional / overhead / 3d / other) from the arcade DB, the MRA's own tags, and `data/overrides.csv` |
| 2 | `select_versions.py` | One version per game: pinned (`data/prefer.csv`) > no hacks > Japan > World > newest. Practice ROMs, hacks and `data/split.csv` matches become their own entries |
| 3 | `core_check.py` | Flags games whose core no database ships (e.g. Raki's CV1000 core, Patreon-only) |
| 4 | `tag_merge.py` | Folds in upstream Downloader screen tags to confirm or settle tate status |
| 5 | `build_db.py` | Writes the Downloader database: every tate entry points at its upstream MRA, pinned to a commit, saved under its `_STG` folder and display name |

### The files you edit

- `data/overrides.csv`: include/exclude a game, set its tier, fix its rotation. Keys are a setname, a title, or `re:<regex>` on the MRA name.
- `data/prefer.csv`: pin a specific set as a game's pick.
- `data/split.csv`: names that are their own game, not a version of their folder's game (Black Label, Zakk's Garegga…).
- `data/layout.csv`: which `_Arcade` folder each tier goes in (nested with `/`).
- `data/hardware.csv`: board names for the By Hardware view, by core or by arcade-DB platform.
- `data/display_names.csv`: the name a game shows in the menu, when upstream's MRA name isn't what we want.
- `data/core_tiers.csv`: default tier for shooters on a core the arcade DB doesn't know (e.g. CV1000).

## Tiers

| Tier | Examples |
| --- | --- |
| core | DoDonPachi, Batsugun, Raiden, 1941 |
| fixed | Galaga, Space Invaders, Phoenix |
| multidirectional | Time Pilot, Robotron, Bosconian |
| overhead | Commando, Out Zone, Guwange |
| 3d | Space Harrier, After Burner (kept out of the regular sections) |
| practice | CV1000 practice ROMs, DoDonPachi trainer |
| hack | Visibility mods, fan hacks |
| other | Vertical games that aren't shooters (Pac-Man, Mappy…) |

## Menu layout

STinGer comes two ways. Both use the same folders; only where they sit differs.

**Full install** (the flavors): STinGer *is* the arcade menu. The other databases deliver cores only,
so `Arcade` opens straight onto STinGer's folders:

```
_Arcade/
  _Core STGs/                   DoDonPachi, Truxton II, Raiden, 1941…
    _By Hardware/               the Core STGs again, one folder per board (CV1000, NMK16, Cave 68000…)
    _By Year/                   the Core STGs again, one folder per release year (1992, 1993…)
    _Hacks & Mods/              Zakk's Garegga, visibility mods
    _Practice ROMs/             practice / trainer sets
  _Other Shooting Games/
    _Fixed Screen Shooting/     Galaga, Phoenix…
    _Multidirectional Shooting/
    _Overhead Shooting/         Out Zone, Commando, Mercs…
  _Other Vertical Games/        everything else that plays on a tate CCW monitor
```

**Add-on** (`cab-test/downloader_stinger.ini` dropped onto an existing setup): the same tree inside
`_Arcade/_Vertical Arcade/`, next to the arcade collection you already have. Nothing else changes.

Folder names live in `data/layout.csv`; board names in `data/hardware.csv`.

### How the full install keeps the menu clean

| Database | Filter | Why |
| --- | --- | --- |
| `[mister]` | `!mra` | Skips stock game lists for any database without its own filter line |
| Distribution | `arcaderbfsonly all_filters font` | Arcade cores, essentials, plus the video filters and fonts the inis use |
| Jotego, Ongo, kuze | `arcaderbfsonly` | Cores only (Update All appends `!jtbeta` to Jotego's) |
| Coin-Op Collection | none: falls back to `[mister]` | Update All rewrites Coin-Op's filter line on every run; every value it writes starts with `[MiSTer]` |
| shmupfan | no section | Its database has no tags, so STinGer's `full.json.zip` delivers its 5 cores |
| 240p Test Suite | `240psuite` | Just the core (Utility), for setting up the CRT |
| STinGer | `all` | The menu and the cores of a few small databases its games need. `!cv1000` leaves out the CV1000 games. Must stay explicit, or it would inherit `!mra` |
| STinGer-ROMs | `all` | Exactly the ROM zips STinGer's games use (~2.2 GB, 0.9 GB of it CV1000). `!cv1000` skips the CV1000 ones |

The full install brings exactly the ROM zips STinGer's games use, pointing at the same archive.org files
Update All's Arcade ROMs and Ongo use. Leave Update All's Arcade ROMs switch off. [`docs/ROMS.md`](docs/ROMS.md)
lists, game by game, what's covered and the few zips to supply yourself.

Anything switched on later in Update All (arcade ROMs, BIOS, names files) installs normally with no edits:
`!mra` only removes stock game lists.

## Where this is going

STinGer's long-term aim: **the shortcut to an arcade MiSTer, whatever your screen.** Flash one image, boot, and get a MiSTer set up for your board and display, with every shooting game sorted and ready.

It's built in three layers, so new setups add a flavor instead of a rewrite:

| Layer | What it covers | Status |
| --- | --- | --- |
| Content | Game list, tiers, menu folders, the Downloader databases | Built (hardware-independent) |
| Hardware | MiSTercade V1/V2, Heber Multisystem² Arcade, regular MiSTer | Flavors built; add-on tested on a MiSTercade V2 cab |
| Display | CRT tate CCW first; tate CW, yoko and LCD tate later | Data already records every game's orientation |

The installer is what ties them together, staged so it never blocks the build:

1. **Remastered Mr. Fusion**: stock Mr. Fusion with STinGer's inis preloaded (MiSTercade cabs first).
2. **STinGer's own installer**: a Mr. Fusion fork (GPLv3) that drops the HDMI check (needed for boards like the Heber), detects MiSTercade boards by USB ID (`16D0:1358` V2, `16D0:10BE` V1-family), and asks a one-screen question for whatever it can't detect (tate CCW / tate CW / yoko, CRT / LCD).

## Roadmap

- [x] Candidate list with Japanese-first version picking
- [x] Upstream screen tags merged
- [x] Downloader databases with filter tags (`db` branch): `db.json.zip` (add-on), `full.json.zip` (full install)
- [ ] Nightly GitHub Action to rebuild and publish the database
- [x] `MiSTer.ini` / `downloader.ini` templates for CCW CRT tate
- [x] Hardware flavors: MiSTercade V2 / V1, Heber Multisystem² Arcade, regular
- [x] Update All installed through its official Downloader section
- [x] Add-on tested on a MiSTercade V2 tate cab (Kyle, 2026-11-20): every database installs, folders and games work
- [ ] Full install on a spare card (MiSTercade V2, then Heber): cores-only filters, menu straight in Arcade, survives Update All
- [ ] Cleaner menu names (drop `[MD]`/`[CoC]` tags, date stamps)
- [ ] Installer stage 1: Mr. Fusion remaster with the inis preloaded
- [ ] Installer stage 2: STinGer's own Mr. Fusion fork with hardware detection and a display picker
- [ ] More displays: tate CW, yoko, LCD tate
- [ ] **Install images (stage 1):** `installer/build_image.sh` makes Mr. Fusion images per flavor with STinGer's files and splash. Untested yet: build on AD1 (WSL), flash a spare card.
- [ ] **Yoko CRT ("hori STinGer")**, parked 2026-11-21. Agreed so far: curate only the shooters (189 horizontal picks,
      108 Core STGs); keep the normal arcade library untouched beside them (no cores-only filters, no "other" folder);
      put all of STinGer in one folder at the top of Arcade (`@...`, name undecided); 3D shooters get their own folder.
      Groundwork in place: `build_db.py variant=yoko` and `data/layout_yoko.csv` (not wired into the build yet).
      Still to do: folder name, curation pass on the horizontal list, flavors (downloader + ini without menu rotation).

### Upstream proposals (MiSTer itself)

Patches and the build/test guide for AD1 are in [`upstream/`](upstream/README.md).

- [ ] **Rotated script console** (Linux-Kernel_MiSTer): enable `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION` so Update All, the downloader and other scripts can display upright on a tate cab (`echo 3 > /sys/class/graphics/fbcon/rotate_all`). Test kernel on a cab first.
- [ ] **Menu start folder** (Main_MiSTer): a MiSTer.ini setting such as `menu_start_dir=_Arcade` so the core list opens there after boot instead of the SD root. Today the start folder is always the menu core's location (`get_rbf_dir()` in `user_io.cpp`, used by `SelectFile()` in `menu.cpp`).
