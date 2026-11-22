# ROMs for STinGer's games

STinGer's full install brings the ROMs Ongo's database ships. Update All's Arcade ROMs switch
(zakk4223/ArcadeROMsDB_MiSTer) adds more. This is how far the two get you, game by game;
the `roms_from` column in the full list says which one each game relies on.
Full list: [`roms.csv`](roms.csv). Regenerated with every database build.

| Status | Games | Meaning |
| --- | --- | --- |
| covered | 388 | Everything it needs comes with Ongo's ROMs and/or Update All's ROMs switch |
| parent only | 124 | Only the parent set is there (typical for Japanese versions). Works if those zips are merged sets; otherwise supply the clone zip |
| partial | 51 | Some files are there, but not the game's own zip |
| missing | 3 | Neither source has it: supply the zips yourself |
| no zip listed | 10 | The MRA names no zip (homebrew or built-in) |

Covered games by where their ROMs come from: Update All ROMs 253, Ongo (default) 126, both 9.

## By source

| Source | covered | parent only | partial | missing | no zip listed |
| --- | --- | --- | --- | --- | --- |
| coinop | 10 | 6 | 5 | 0 | 0 |
| distribution | 213 | 56 | 19 | 3 | 10 |
| jotego | 29 | 24 | 13 | 0 | 0 |
| kuze | 13 | 6 | 1 | 0 | 0 |
| ongo | 113 | 26 | 12 | 0 | 0 |
| shmupfan | 10 | 6 | 1 | 0 | 0 |

## Zips to supply yourself

For games marked partial or missing. Put them in `games/mame/` on the SD card.
The number is how many STinGer games use that zip.

- `jtbeta.zip` (3)
- `ktiger.zip` (3)
- `ddonpachj.zip` (2)
- `hishouza.zip` (2)
- `rayforce.zip` (2)
- `/hbmame/brubber.zip` (1)
- `/hbmame/dkong.zip` (1)
- `/sound/carnival.zip` (1)
- `/sound/journey.zip` (1)
- `/sound/pulsar.zip` (1)
- `arkanoidj.zip` (1)
- `arkatayt.zip` (1)
- `bronx.zip` (1)
- `btlfield.zip` (1)
- `buraiken.zip` (1)
- `cfishing.zip` (1)
- `chamburger.zip` (1)
- `coinopkey.zip` (1)
- `crazycop.zip` (1)
- `csweetht.zip` (1)
- `daisenpu.zip` (1)
- `ddpdojb.zip` (1)
- `ddpdojblk.zip` (1)
- `devilfsg.zip` (1)
- `dfeveron.zip` (1)
- `excthour.zip` (1)
- `flkatcka.zip` (1)
- `froggers2.zip` (1)
- `futari10.zip` (1)
- `futariblj.zip` (1)
- `garuka.zip` (1)
- `gmahou.zip` (1)
- `gunball.zip` (1)
- `karatedo.zip` (1)
- `karatevs.zip` (1)
- `labyrunr.zip` (1)
- `mahoudai.zip` (1)
- `makyosen.zip` (1)
- `popflamn.zip` (1)
- `raphero.zip` (1)
- `ringking.zip` (1)
- `rushcrsh.zip` (1)
- `samesame2.zip` (1)
- `sbagman2.zip` (1)
- `scrambles.zip` (1)
- `shippumd.zip` (1)
- `slapfighb1.zip` (1)
- `sncwgltd.zip` (1)
- `sngkace.zip` (1)
- `tigerhb2.zip` (1)
- `trigon.zip` (1)
