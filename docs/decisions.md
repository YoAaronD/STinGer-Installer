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
- Menu (Aaron, 2026-11-20): three top-level folders. `_Core STGs` holds the scrolling STGs plus `_By Hardware`, `_By Year`, `_Hacks & Mods` and `_Practice ROMs` (MiSTer lists subfolders before games). Then `_Other Shooting Games` (Fixed Screen / Multidirectional / Overhead) and `_Other Vertical Games`. MiSTer sorts folders alphabetically and hides the leading `_`, so no numbers are needed. The by-hardware and by-year views hold Core STGs only. (Replaces the `_STG`-prefixed, `_Vertical Shooting`, flat and numbered layouts.)
- `_By Year` inside `_Core STGs` (Aaron's idea): surfaces lesser-known games from strong years like 1992–94. Same MRAs as the main folders, grouped by the MRA/MAD year; 3 games with no year go to `Unknown year`.
- **By Hardware** repeats the shooting games grouped by arcade board; boards with a single tate shooter go in `Other hardware`.
- The 3D section isn't in the tate build (almost all horizontal).

## Sources
- Distribution, Jotego, Coin-Op Collection, Ongo, **kuze** (NMK16 family, Jaleco MS1, Namco System 2), **shmupfan** (Taito G-NET, Dooyong, DEC8, Tecmo 16, 1945k III) and **Slop-Core** (TheJesusFish's Toaplan 2 cores: Batsugun, Dogyuun, V-Five, FixEight, Ghox).
- Slop-Core (2026-11-23): Ongo doesn't ship these cores; it hosts their ROMs (`OngoFiles/mame-slopcore`) and lists Slop-Core under recommended databases. The ROMs come through STinGer-ROMs.
- Databases Ongo recommends, checked 2026-11-23. Added: **decoryah** (Sky Alert, Varia Metal, Silver Millennium, Fighting Hawk; it ships its own ROMs), **jlrh** (Detana!! TwinBee) and **Blackwine Sega System 1/2** (Gardia). Nothing new in rmcores (Raiden, Darius) or asturur (Turbo Force, Aero Fighters). Rodimus skipped: test builds and bootlegs of classic cores Distribution already covers.
- Cores from small databases (decoryah, Slop-Core, jlrh, Blackwine) are delivered by STinGer's full database, only the ones its games use, instead of a downloader.ini section each: decoryah has no tags to filter with, and jlrh's 47 cores are 164 MB for one game. They update when STinGer rebuilds.
- A "Flip Screen" DIP switch in a game's MRA now counts as a flip setting (21 games moved off "upside down", Raiden Fighters and Varia Metal among them).
- When two sources ship the same game, the order is Distribution > Jotego > kuze > Coin-Op > shmupfan > Slop-Core > Ongo, after region.
- **Thunder Dragon** is pinned to kuze's feature-complete NMK16 core (`tdragon@kuze`); Coin-Op's NMK16 builds are betas.
- `templates/downloader.ini` enables all of them; `[mister]` carries no positive filter because Jotego and Coin-Op inherit it.

## Update All
- Installed via its official `[update_all_mister]` Downloader section in the template, not bundled.
- Checked in its source: it edits downloader.ini as a document, touching only databases in its catalog (and only the filter lines of Jotego/Coin-Op), so STinGer, kuze, shmupfan, Slop-Core and Ongo sections and our Distribution `filter = arcade` survive. Disabling Distribution/JTCORES/Coin-Op in its settings would remove cores STinGer needs.

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

- Truxton II / Tatsujin Oh: MAD gives it the parent title "Truxton - Tatsujin", which grouped it with the 1988 original and dropped it. Split out in data/split.csv.
- No curated "Start Here" list (Aaron): taste in STGs varies too much (Gun Frontier, DoDonPachi). STinGer stays neutral; discovery comes from the By Year / By Hardware views. Personal favorites: bundle wizzo's Favorites (mrext) - to test on a tate CRT.
- Favorites placement: mrext Favorites only treats top-level SD folders starting with `_` as favorites folders, so `_Arcade/_Favorites` isn't possible; it lives at the main menu as `@Favorites` (default `_@Favorites`, sorts above `Arcade`). Not bundled until the rotated-terminal question is settled.
- Rotated script terminal (possible calling card): the MiSTer kernel builds fbcon without `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION` (Linux-Kernel_MiSTer `MiSTer_defconfig`). With it enabled, `echo 3 > /sys/class/graphics/fbcon/rotate_all` (or 1, to test) at startup would turn every Scripts-menu terminal for a tate cab. Path: build a test kernel, confirm on the cab, then propose the one-line defconfig change upstream rather than shipping a custom kernel (Distribution/Update All overwrite it).
- Full install (2026-11-20): STinGer is the whole arcade menu. Other databases ship cores only (`arcaderbfsonly`), STinGer's `full.json.zip` puts its folders straight in `_Arcade` and carries shmupfan's 5 cores (shmupfan's database has no tags, so it can't be trimmed). Same db_id as the add-on database, so moving a card between the two cleans up after itself.
- Coin-Op and Update All: Update All rewrites Coin-Op's filter line every run (removes it for "public", `[MiSTer] ...` otherwise). So the cores-only rule lives in `[mister]`, Coin-Op has no line of its own, and every other database gets an explicit filter (`all` for untagged ones: Update All, MiSTercade maps).
- Repo must stay public: a private repo serves raw files as 404, which broke the first cab test.
- Folders stay inside `_Arcade` (Aaron, 2026-11-20). Top level was possible only with a `cores` symlink in each folder (the firmware looks for cores under the first `_` folder in a game's path), made by a script since Downloader can't create links, and it would leave an empty `Arcade` folder at the top of the main menu.
- Global rule softened (2026-11-21): `[mister] filter = !mra` instead of `arcaderbfsonly`. The strict rule starved anything switched on later in Update All (the arcade ROMs and BIOS databases installed nothing on the test card). Coin-Op tags all 419 of its game entries `mra`, so it still brings only its 52 cores; ROMs, BIOS, names and MiSTercade maps install untouched. Zero config after install.
- `menu_start_dir=_Arcade` ships in every flavor now (2026-11-21), ahead of the upstream patch. Stock MiSTer only logs unknown settings (on screen only with `sanity_check=1`, which is off), so it is harmless until the patch is merged, then works with no changes.
- Ongo's ROMs ship by default (Aaron, 2026-11-21): Ongo's database includes them, so the full install takes them too (`filter = arcaderbfsonly mame hbmame`, ~9 GB with its cores); still no Ongo game lists or console cores. It is how GunNail and Rapid Hero worked on Aaron's cab without his own ROMs. docs/ROMS.md counts both ROM sources (Ongo by default, Update All's Arcade ROMs switch optionally).
- Every menu folder must start with "_" (2026-11-21): MiSTer's core list hides folders without it, which made By Hardware and By Year look empty on the first cab test. Board and year subfolders are now `_Capcom CPS-2`, `_1993` and so on (shown without the "_").
- MiSTercade flavors drop the [Menu] block (2026-11-21, Blast City test): with it, the main menu lost sync on a MiSTercade V2 + IO DAC when the cab's marquee light came on; commented out, everything worked. MiSTercade flavors are now MiSTerAddons' ini plus only `osd_rotate=2` and `menu_start_dir`. One V2 flavor covers both V2 setups (standard direct video and IO DAC) through `direct_video=2`. Regular and Heber keep the block until tested.
- ROM list in STinGer's own database (Aaron, 2026-11-23: "happy to be associated with making STGs more accessible"). full.json.zip lists exactly the ROM zips its games use, 555 zips / 2.19 GB, pointing at the same archive.org files as Update All's Arcade ROMs (preferred) and Ongo. Replaces taking Ongo's whole 8.4 GB set; Ongo is cores-only again. Tags: `stgroms` (opt out with `!stgroms`), and ROMs only CV1000 games use also carry `cv1000`, so the default install is 1.30 GB. Users should leave Update All's Arcade ROMs switch off.

- CV1000 games in by default (Aaron, 2026-11-23): they're some of the best STGs, and 0.9 GB is a small price. They need Raki's Patreon core; the README and downloader.ini say so and link his Patreon. Still tagged `cv1000`, so `filter = !cv1000` leaves them (and their ROMs) out.
