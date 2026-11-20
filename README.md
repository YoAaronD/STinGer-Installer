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
and the [MiSTer Arcade Database](https://github.com/Toryalai1/MiSTer_ArcadeDatabase) for genre data.

| Step | Script | What it does |
| --- | --- | --- |
| 1 | `classify.py` | Tiers every MRA (core / fixed / multidirectional / overhead / 3d / other) from the arcade DB, the MRA's own tags, and `data/overrides.csv` |
| 2 | `select_versions.py` | One version per game: pinned (`data/prefer.csv`) > no hacks > Japan > World > newest. Practice ROMs, hacks and `data/split.csv` matches become their own entries |
| 3 | `core_check.py` | Flags games whose core no database ships (e.g. Raki's CV1000 core, Patreon-only) |
| 4 | `tag_merge.py` | Folds in upstream Downloader screen tags to confirm or settle tate status |

### The files you edit

- `data/overrides.csv`: include/exclude a game, set its tier, fix its rotation. Keys are a setname, a title, or `re:<regex>` on the MRA name.
- `data/prefer.csv`: pin a specific set as a game's pick.
- `data/split.csv`: names that are their own game, not a version of their folder's game (Black Label, Zakk's Garegga…).
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

## Roadmap

- [x] Candidate list with Japanese-first version picking
- [x] Upstream screen tags merged
- [ ] Cab test: folder layout, `filter = arcade`, `osd_rotate=2`
- [ ] Downloader database with `_Shmups` tree and filter tags
- [ ] `MiSTer.ini` / `downloader.ini` templates for CCW CRT tate
- [ ] Installer image (Mr. Fusion remaster with the inis pre-loaded)
