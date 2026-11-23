# STinGer cab test: MiSTercade V2, tate CCW CRT

Databases published 2026-11-20: add-on (`db.json.zip`, 1,014 menu entries) and full install (`full.json.zip`, plus shmupfan's 5 cores), all pinned to upstream commits. Route A passed on Kyle's cab.

## Pick a route

**A: add to your current card (safe, nothing removed)**
1. Back up `/media/fat/downloader.ini` and `/media/fat/MiSTer.ini` anyway.
2. Copy `A-add-to-current-card/downloader_stinger.ini` to `/media/fat/`.
   If your downloader.ini already has an Ongo, kuze or shmupfan section, delete that section from `downloader_stinger.ini`.
3. The CV1000 games need Raki's core (Patreon) in `_Arcade/cores`. Without it, uncomment `filter = !cv1000` under the STinGer section to leave them out.
4. On the cab: Scripts → `update` (or `update_all`). Let it finish, then reboot.

**B: full STinGer install (spare SD card only)**
This makes the card arcade-only and tate-only. The first update **deletes** Distribution's console and
computer cores and every stock arcade entry: STinGer becomes the whole arcade menu.
1. Start from a fresh card (e.g. Mr. Fusion with its first update done).
2. Copy all three files from `B-full-flavor-spare-card/` to `/media/fat/`, replacing what's there.
3. Scripts → `update`, reboot, then run `update_all` once.

What's different with B:
- [ ] Main menu → Arcade opens straight onto Core STGs, Other Shooting Games, Other Vertical Games (no Vertical Arcade folder, no stock games)
- [ ] Still the same after `update_all` (it rewrites Coin-Op's filter line; Coin-Op's games must not come back)
- [ ] Psyvariar / any G-NET game boots (its core now comes through STinGer, with no shmupfan section)
- [ ] Controls work without remapping (the MiSTercade maps file has its own filter line)

## What to check

Menu
- [ ] Main menu → Arcade → **Vertical Arcade** is there
- [ ] Inside: Core STGs, Other Shooting Games, Other Vertical Games, in that order
- [ ] Core STGs opens with By Hardware, By Year, Hacks & Mods, Practice ROMs, then the games
- [ ] Folder names read cleanly (no `_`), nothing cut off at the right edge
- [ ] Menu text is upright on the CCW monitor (`osd_rotate=2`)

Games (one per source; each one tests a different database)
- [ ] DoDonPachi (Japan): Distribution
- [ ] Truxton II / Tatsujin Oh: Coin-Op (and the fix from today)
- [ ] Battle Garegga Zakk Version: Distribution (the renamed hack)
- [ ] Thunder Dragon 2: kuze
- [ ] Psyvariar (By Hardware → Taito G-NET): shmupfan
- [ ] Raiden Fighters (Japan): Ongo, Seibu SPI
- [ ] A Jotego game, e.g. 1943 Kai: Jotego
- [ ] Any CW game (Truxton II is one): flip setting in the core's menu turns it upright

Controls
- [ ] Buttons right with no remapping, thanks to the MiSTercade maps (keyed by setname)

Coexistence
- [ ] Run `update_all` once afterwards: the STinGer, Ongo, kuze and shmupfan entries survive, and Vertical Arcade is still intact

## Note down

- Any game that won't boot (most likely a missing core): name, folder
- Anything sideways or upside down
- Folder names you want to change after seeing them on the glass
- Update All screens: sideways? (the rotated-terminal idea)
