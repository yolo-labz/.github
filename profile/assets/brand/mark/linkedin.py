#!/usr/bin/env python3
"""LinkedIn sizes from the character and the lockup. No claims: the mark, the name, one neutral line.

    python3 linkedin.py OUTDIR

banner-1584x396   personal profile banner (the profile photo covers the lower left on desktop: nothing lives there)
page-banner-1128x191  company page banner
avatar-400        profile or page picture (the head mark, 70 % on the ground, survives a circle crop)
post-1200x627     feed image and Featured card
carousel-1080x1350  carousel cover
"""
import re, sys
from pathlib import Path
from character import state, head_front, paint, wrap
from master import PAL
from build import raster, tile, head, wordmark

P = PAL["dark"]
MONO = "JetBrains Mono, JetBrainsMono Nerd Font Mono, monospace"
def inner_wordmark():
    w = wordmark("dark"); return re.sub(r"^<svg[^>]*>|</svg>\s*$", "", w.strip())
def canvas(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img"><title>{title}</title>'
            f'<rect width="{w}" height="{h}" fill="{P["ground"]}"/>{body}</svg>\n')
def g(frag, x, y, s): return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{paint(frag, "dark")}</g>'
def lockup(x, y, s): return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{inner_wordmark()}</g>'   # 470 x 128 units
def ground_line(x0, x1, y): return f'<path d="M{x0} {y} H{x1}" stroke="#45475a" stroke-width="2"/>'

def banner():
    h = 396; s = h * 0.62 / 25.8
    body = ground_line(640, 1584, 340) + lockup(700, 120, 1.1) + g(state("idle"), 1280, 396 - 56 - 25.8 * s, s)
    return canvas(1584, 396, body, "yolo-labz banner")
def page_banner():
    s = 191 * 0.86 / 25.8
    body = lockup(60, 30, 1.0) + g(state("idle"), 900, 191 - 10 - 25.8 * s, s)
    return canvas(1128, 191, body, "yolo-labz page banner")
def avatar():
    return head(tile("dark", pupils=True, scale=0.70, rx=0), "yolo-labz")
def post():
    s = 627 * 0.74 / 25.8
    body = g(state("working"), 760, 627 * 0.13, s) + lockup(70, 90, 1.0) + ground_line(70, 1130, 560)
    return canvas(1200, 627, body, "yolo-labz post")
def carousel():
    s = 1350 * 0.50 / 25.8
    body = g(state("idle"), 1080 / 2 - 8 * s + 0, 1350 * 0.18, s) + lockup(110, 1120, 1.0) + ground_line(110, 970, 1090)
    return canvas(1080, 1350, body, "yolo-labz carousel cover")

def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    for name, fn, w, h in (("banner-1584x396", banner, 1584, 396), ("page-banner-1128x191", page_banner, 1128, 191),
                           ("avatar-400", avatar, 400, 400), ("post-1200x627", post, 1200, 627), ("carousel-1080x1350", carousel, 1080, 1350)):
        s = fn(); (out / f"{name}.svg").write_text(s); raster(s, w, h, out / f"{name}.png")
if __name__ == "__main__": main(sys.argv[1])
