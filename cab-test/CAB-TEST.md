# STinGer cab test: MiSTercade V2, tate CCW CRT

Database published 2026-11-20 (db branch d5ba657): 1,014 menu entries, all pinned to upstream commits.

## Pick a route

**A: add to your current card (safe, nothing removed)**
1. Back up `/media/fat/downloader.ini` and `/media/fat/MiSTer.ini` anyway.
2. Copy `A-add-to-current-card/downloader_stinger.ini` to `/media/fat/`.
   If your downloader.ini already has an Ongo, kuze or shmupfan section, delete that section from `downloader_stinger.ini`.
3. Have Raki's CV1000 core? Uncomment `filter = arcade` under the STinGer section.
4. On the cab: Scripts → `update` (or `update_all`). Let it finish, then reboot.

**B: full STinGer flavor (spare SD card only)**
This turns the card into an arcade-only setup: Distribution's console and computer cores are **deleted** on the first update.
1. Start from a fresh card, e.g. Mr. Fusion with its first update done.
2. Copy all three files from `B-full-flavor-spare-card/` to `/media/fat/`, replacing what's there.
3. Scripts → `update`, then reboot.

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
