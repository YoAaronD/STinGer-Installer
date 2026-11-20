# Decisions log

Calls made while curating the list, so they don't get relitigated. Most are encoded in `data/*.csv`.

## Scope
- **Tate first, CCW, CRT.** Yoko and LCD-tate setups are possible later modes; the data supports them.
- **No console or computer cores.** On a rotated CRT they need scaler rotation. Distribution and Ongo get `filter = arcade`; Jotego and Coin-Op are arcade-only already.
- **CW/CCW is not a filter.** Most cores can flip, so every vertical game is in.
- **Completeness over quality.** Bad shmups are still shmups (e.g. Mission Craft).

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

## Setup facts
- `osd_rotate=2` (rotate left, -90°) for a CCW cab, per the MiSTer ini docs and the maintainer's own setups.
- Raki's CV1000 core is Patreon-only; Ongo ships the CV1000 MRAs but not the core.
- Jotego's premium betas need `filter = [mister]` under `[jtcores]`; keep filters scoped per database.
