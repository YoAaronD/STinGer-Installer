# Decisions log

Calls made while curating the list, so they don't get relitigated. Most are encoded in `data/*.csv`.

## Scope
- **Tate first, CCW, CRT.** Yoko and LCD-tate setups are possible later modes; the data supports them.
- **No console or computer cores.** On a rotated CRT they need scaler rotation. Distribution and Ongo get `filter = arcade`; Jotego and Coin-Op are arcade-only already.
- **CW/CCW is not a filter.** Most cores can flip, so every vertical game is in.
- **Completeness over quality.** Bad shmups are still shmups (e.g. Mission Craft).

## Menu layout
- Everything lives under **`_Arcade`**, like a regular install, so MRAs find their cores in `_Arcade/cores`.
- One top folder says **vertical** up front: `_Vertical Arcade`. Inside it, the shooting folders first, then `_Other Games`.
- Main tier is `_Scrolling STGs` (Aaron's call); the rest avoid repeating "STG": `_Fixed Screen Shooting`, `_Multidirectional Shooting`, `_Overhead Shooting`, `_By Hardware`, `_Practice ROMs`, `_Hacks & Mods`, `_Other Games`. (Replaces the earlier `_STG`-prefixed and `_Vertical Shooting` layouts.)
- **By Hardware** repeats the shooting games grouped by arcade board; boards with a single tate shooter go in `Other hardware`.
- The 3D section isn't in the tate build (almost all horizontal).

## Sources
- Distribution, Jotego, Coin-Op Collection, Ongo, **kuze** (NMK16 family, Jaleco MS1, Namco System 2) and **shmupfan** (Taito G-NET, Dooyong, DEC8, Tecmo 16, 1945k III).
- When two sources ship the same game, the order is Distribution > Jotego > kuze > Coin-Op > shmupfan > Ongo, after region.
- **Thunder Dragon** is pinned to kuze's feature-complete NMK16 core (`tdragon@kuze`); Coin-Op's NMK16 builds are betas.
- `templates/downloader.ini` enables all of them; `[mister]` carries no positive filter because Jotego and Coin-Op inherit it.

## Update All
- Installed via its official `[update_all_mister]` Downloader section in the template, not bundled.
- Checked in its source: it edits downloader.ini as a document, touching only databases in its catalog (and only the filter lines of Jotego/Coin-Op), so STinGer, kuze, shmupfan and Ongo sections and our Distribution `filter = arcade` survive. Disabling Distribution/JTCORES/Coin-Op in its settings would remove cores STinGer needs.

## Version picking
- Japanese first, then World, newest revision within the region.
- **Battle Garegga:** the original (Feb 3 1996) set, `bgaregga`, not Type 2.
- **Battle Bakraid / Batrider:** Unlimited Version (Japan) / Japan B version, pinned.
- **Black Label** releases are their own games (DoDonPachi Dai-Ou-Jou BL, and the CV1000 Black Labels).
- **Zakk's Garegga** (`bgareggz`) is its own entry next to the original, shown as **Battle Garegga Zakk Version** (`data/display_names.csv`).
- **DonPachi "Satsuei version"** is excluded as a variant; the plain Japan set is used.

## Sections
- **3D / into-the-screen** (Space Harrier, After Burner, cockpit-view games) is its own section, not in the regular STG tiers.
- **Practice ROMs and trainers** are set aside in their own section.
- **Hacks & mods** (visibility mods, fan hacks) never replace an original.
- **Out Zone-style overhead shooters count as STG** (overhead tier), including Gundhara.

## Individual calls
| Game | Call |
| --- | --- |
| Crazy War | fixed tier (not a scrolling shmup) |
| Iron Fortress | fixed tier (fixed-screen tank game) |
| Pirates (NIX) | excluded: Cabal-style crosshair game |
| Mogu Chan, Gain Ground, Seicross | not shooters |
| The Bounty | core (Orca, Toaplan forerunner) |
| The Percussor | multidirectional |
| Fortress 2 Blue Arcade | excluded: artillery game |
| Brave Blade | core, rotation assumed CCW (verify) |
| Strike Gunner, Daioh, Eight Forces, War of Aero, U.N. Defense Force, Mad Shark, Galmedes, SD Gundam Neo Battling, Zing Zing Zip, Twin Eagle | core (MRAs tagged only "Arcade") |

## Flavors
- Four flavors: **MiSTercade V2**, **MiSTercade V1** (V1 2025 mappings), **Heber Multisystem² Arcade** (stock ini + its CTRLDock player bindings; analog JAMMA video with composite sync, no HDMI), **regular/other** (e.g. a Blast City's D-sub with a standard MiSTer).
- The Heber board is the first test bed: it exercises the plain analog path with almost no board-specific settings.
- STinGer never replaces a MiSTercade's ini: it takes MiSTerAddons' official 15kHz ini and adds only `osd_rotate=2` and the `[Menu]` block.
- MiSTercade control mappings come from MiSTerAddons' own drop-in Downloader inis and apply by set name.

## Setup facts
- `osd_rotate=2` (rotate left, -90°) for a CCW cab, per the MiSTer ini docs, MiSTerAddons' V2 notes and the maintainer's own setups. Stock MiSTer.ini now also offers `3` (match the game's direction, analog only).
- Raki's CV1000 core is Patreon-only; Ongo ships the CV1000 MRAs but not the core.
- Jotego's premium betas need `filter = [mister]` under `[jtcores]`; keep filters scoped per database.
