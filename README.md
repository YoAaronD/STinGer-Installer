# STinGer Installer

A shmup-focused MiSTer build for **vertical (tate) CRT arcade cabinets**.

> Status: early. The game list is built and curated; the downloader database,
> ini templates and installer image are next.

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

```
_Arcade/
  _Vertical Arcade/
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

Folder names live in `data/layout.csv`; board names in `data/hardware.csv`.

## Where this is going

STinGer's long-term aim: **the shortcut to an arcade MiSTer, whatever your screen.** Flash one image, boot, and get a MiSTer set up for your board and display, with every shooting game sorted and ready.

It's built in three layers, so new setups add a flavor instead of a rewrite:

| Layer | What it covers | Status |
| --- | --- | --- |
| Content | Game list, tiers, `_STG` folders, the Downloader database | Built (hardware-independent) |
| Hardware | MiSTercade V1/V2, Heber Multisystem² Arcade, regular MiSTer | Flavors built, untested on hardware |
| Display | CRT tate CCW first; tate CW, yoko and LCD tate later | Data already records every game's orientation |

The installer is what ties them together, staged so it never blocks the build:

1. **Remastered Mr. Fusion**: stock Mr. Fusion with STinGer's inis preloaded (MiSTercade cabs first).
2. **STinGer's own installer**: a Mr. Fusion fork (GPLv3) that drops the HDMI check (needed for boards like the Heber), detects MiSTercade boards by USB ID (`16D0:1358` V2, `16D0:10BE` V1-family), and asks a one-screen question for whatever it can't detect (tate CCW / tate CW / yoko, CRT / LCD).

## Roadmap

- [x] Candidate list with Japanese-first version picking
- [x] Upstream screen tags merged
- [x] Downloader database with `_STG` tree and filter tags (`db` branch)
- [ ] Nightly GitHub Action to rebuild and publish the database
- [x] `MiSTer.ini` / `downloader.ini` templates for CCW CRT tate
- [x] Hardware flavors: MiSTercade V2 / V1, Heber Multisystem² Arcade, regular
- [x] Update All installed through its official Downloader section
- [ ] Test on a MiSTercade V2 tate cab (then Heber): `_STG` folders, games boot, `filter = arcade`, `osd_rotate=2`, Update All keeps our sections
- [ ] Cleaner menu names (drop `[MD]`/`[CoC]` tags, date stamps)
- [ ] Installer stage 1: Mr. Fusion remaster with the inis preloaded
- [ ] Installer stage 2: STinGer's own Mr. Fusion fork with hardware detection and a display picker
- [ ] More displays: tate CW, yoko, LCD tate
