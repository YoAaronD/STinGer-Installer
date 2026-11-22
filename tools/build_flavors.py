"""Build the per-hardware STinGer flavors: MiSTer.ini (base + STinGer overlay) plus the Downloader files.

usage: python3 -I tools/build_flavors.py <sources_dir> <out_dir>

Flavors:
  mistercade-v2  MiSTerAddons' MiSTercade V2 15kHz ini   + MiSTercade V2 control mappings drop-in
  mistercade-v1  MiSTerAddons' MiSTercade V1 15kHz ini   + MiSTercade V1 2025 control mappings drop-in
  heber-ms2      MiSTer's stock MiSTer.ini + Heber Multisystem2 Arcade player bindings (CTRLDock on usb-1.7)
  regular        MiSTer's stock MiSTer.ini (native 15kHz analog out) - controls are left to the user
Every flavor gets templates/downloader.ini (STinGer + the databases its games need).
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAVORS = {
    "mistercade-v2": ("misteraddons_ini/MiSTercade V2/15kHz/MiSTer.ini",
                      "misteraddons_mistercade/mistercade_v2/mappings/downloader_maps-v2-osd.ini"),
    "mistercade-v1": ("misteraddons_ini/MiSTercade V1/15kHz/MiSTer.ini",
                      "misteraddons_mistercade/mistercade_v1_2025/mappings/downloader_maps-v1-2025-osd.ini"),
    "heber-ms2":     ("main_mister/MiSTer.ini", None),
    "regular":       ("main_mister/MiSTer.ini", None),
}
# Extra [MiSTer] lines a flavor needs on top of its base, before STinGer's overlay.
FLAVOR_EXTRA = {
    # From Heber's Multisystem2 Arcade product page / manual: "Player Bindings are configured in the mister.ini file"
    "heber-ms2": ["player_1_controller=usb-1.7/input2/ ; Heber CTRLDock Arcade: JAMMA player 1",
                  "player_2_controller=usb-1.7/input3/ ; Heber CTRLDock Arcade: JAMMA player 2"],
}
# Overlay sections a flavor leaves out. MiSTercades: no [Menu] block. It routes the main menu through
# the scaler's analog output, which made the menu lose sync on a V2 + IO DAC board in a Blast City
# (2026-11-21) and goes to pins a standard dual-SDRAM V2 doesn't wire to the cab. MiSTerAddons'
# own inis leave it out too (their README lists it as optional).
SKIP_SECTIONS = {"mistercade-v2": {"menu"}, "mistercade-v1": {"menu"}}
KEY = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=")
SECTION = re.compile(r"^\s*\[([^\]]+)\]")

def parse_overlay(path):
    sections, cur = {}, None
    for line in open(path, encoding="utf-8"):
        s = SECTION.match(line)
        if s:
            cur = s.group(1); sections.setdefault(cur, []); continue
        if cur and KEY.match(line):
            sections[cur].append(line.rstrip("\n"))
    return sections

def apply(base_text, overlay):
    """Replace overlay keys in matching sections, append missing keys/sections. Comments are kept."""
    lines, out, cur, done = base_text.splitlines(), [], None, set()
    pending = {sec: {KEY.match(l).group(1).lower(): l for l in ls} for sec, ls in overlay.items()}

    def flush(sec):  # keys the base section didn't have go at its end
        if sec is None: return
        p = pending.get(sec_key(sec), {})
        for k, l in p.items():
            if (sec_key(sec), k) not in done:
                out.append(l); done.add((sec_key(sec), k))

    sec_key = lambda s: next((o for o in overlay if o.lower() == s.lower()), s)
    for line in lines:
        s = SECTION.match(line)
        if s:
            flush(cur); cur = s.group(1); out.append(line); continue
        m = KEY.match(line)
        if cur and m and (sec_key(cur), m.group(1).lower()) not in done and m.group(1).lower() in pending.get(sec_key(cur), {}):
            out.append(pending[sec_key(cur)][m.group(1).lower()])
            done.add((sec_key(cur), m.group(1).lower()))
            continue
        out.append(line)
    flush(cur)
    seen = {SECTION.match(l).group(1).lower() for l in lines if SECTION.match(l)}
    for sec, ls in overlay.items():
        if sec.lower() not in seen:
            out += ["", f"[{sec}]"] + ls
    return "\n".join(out) + "\n"

def main(sources, out):
    overlay = parse_overlay(os.path.join(ROOT, "templates", "stinger_overlay.ini"))
    for name, (base, maps) in FLAVORS.items():
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        text = open(os.path.join(sources, base), encoding="utf-8", errors="replace").read()
        if name in FLAVOR_EXTRA:
            text = apply(text, {"MiSTer": FLAVOR_EXTRA[name]})
        ov = {sec: ls for sec, ls in overlay.items() if sec.lower() not in SKIP_SECTIONS.get(name, set())}
        open(os.path.join(d, "MiSTer.ini"), "w", encoding="utf-8").write(apply(text, ov))
        shutil.copy(os.path.join(ROOT, "templates", "downloader.ini"), os.path.join(d, "downloader.ini"))
        if maps:
            ini = open(os.path.join(sources, maps), encoding="utf-8").read().rstrip("\n")
            open(os.path.join(d, os.path.basename(maps)), "w", encoding="utf-8").write(ini + "\n")
        print(name, "->", sorted(os.listdir(d)))

if __name__ == "__main__":
    main(*sys.argv[1:])
