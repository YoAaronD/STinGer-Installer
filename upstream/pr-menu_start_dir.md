**Title:** Add menu_start_dir: open the core list in a chosen folder

---

Adds an optional MiSTer.ini setting that picks the folder the core list opens in after boot:

```ini
menu_start_dir=_Arcade
```

**Why:** lots of setups live in one folder. An arcade cabinet that only runs arcade cores, someone who mostly plays one console, a kiosk or a kid's MiSTer. Today the core list always opens at the SD root, so that's one extra step every time. With this set, the menu opens where you actually play.

**Behavior**
- Path is relative to the SD root (e.g. `_Arcade`, `_Console`, `_Arcade/_Organized`).
- Only applies when the current core is in the root, i.e. the menu itself (after boot, or returning from a core). While a core from a subfolder is loaded, the list still opens next to that core, exactly as before.
- Back / `..` still lead up to the root; nothing is locked down.
- A missing or wrong folder falls back to the root.
- Unset (the default) changes nothing.

**Change:** 19 lines in `cfg.h`, `cfg.cpp`, `menu.cpp` (in `SelectFile()`, right after `ResolveExistingCorePath()`), plus a commented example in `MiSTer.ini`.

**Tested** on a DE10-Nano with a standard MiSTer setup, and on a MiSTercade V2 in a Blast City (15 kHz CRT):
- boot → core list opens inside `_Arcade`
- Back → root
- launch a game, return to the menu → opens in `_Arcade` again
- `menu_start_dir=_Console` → opens in `_Console`
- setting commented out → opens at the root as before
- misspelled folder (`_Arcadee`) → root

<!-- video -->
