#!/usr/bin/env python3
"""Draw STinGer's install splash: 1920x1080 PNG, the size Mr. Fusion shows over HDMI.

usage: make_splash.py <splash.txt> <out.png>
splash.txt: first line is the big headline, the rest is smaller text underneath.
Edit splash.txt to change the words; the art stays the same.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
W, H = 1920, 1080
BG, FG, ACCENT, DIM = (8, 8, 10), (236, 236, 236), (230, 40, 40), (140, 140, 150)

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

def centered(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)

def main(txt, out):
    lines = [l.rstrip("\n") for l in open(txt, encoding="utf-8") if l.strip()]
    headline, rest = (lines[0], lines[1:]) if lines else ("", [])
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # scanlines, for the CRT feel
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 14, 18))
    # wordmark: STinGer, with S T G in red
    big = font(FONT, 150)
    word = [("S", ACCENT), ("T", ACCENT), ("in", FG), ("G", ACCENT), ("er", FG)]
    total = sum(d.textlength(t, font=big) for t, _ in word)
    x = (W - total) / 2
    for t, c in word:
        d.text((x, 250), t, font=big, fill=c)
        x += d.textlength(t, font=big)
    d.rectangle([(W / 2 - 360, 450), (W / 2 + 360, 456)], fill=ACCENT)
    centered(d, 520, headline, font(FONT, 64), FG)
    y = 640
    for l in rest:
        centered(d, y, l, font(FONT_REG, 36), DIM)
        y += 56
    centered(d, H - 90, "vertical STG machine installer  -  built on Mr. Fusion", font(FONT_REG, 26), (90, 90, 100))
    im.save(out, optimize=True)

if __name__ == "__main__":
    main(*sys.argv[1:3])
