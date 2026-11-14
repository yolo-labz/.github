#!/usr/bin/env python3
"""Build the served hero and avatar files in ../hero/ from the character source.

    python3 hero.py            writes hero/gremlin-hero-*.{avif,webp,png}, hero/gremlin-avatar-*, hero/manifest.json

The hero is the 'working' state on the dark ground. Sizes are the ones the org README (887x640) and the portfolio
(804x770 and 402x385) already serve, so no consumer changes a path.
"""
import hashlib, json, subprocess
from pathlib import Path
from character import state, wrap
from master import PAL
from build import raster, tile, head

HERE = Path(__file__).resolve().parent; OUT = HERE.parent / "hero"
ALT = {"hero": "The yolo-labz gremlin typing on a keyboard, angular dark eyes with purple pupils, pointed ears and a small fanged grin",
       "avatar": "The yolo-labz gremlin's head: pointed ears, dark angular eyes with purple pupils"}

def hero_svg(w, h):
    # figure box in u: x -3.6..19.6, y 0..25.8; centred with a margin, ground behind it
    fw, fh = 23.2, 25.8; s = min(w * 0.74 / fw, h * 0.80 / fh)
    x = (w - fw * s) / 2 + 3.6 * s; y = (h - fh * s) / 2
    body = f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.3f})">{state("working")}</g>'
    return wrap(body, f"0 0 {w} {h}", "The yolo-labz gremlin typing", "The gremlin at a keyboard with code brackets around its head.", "dark", ground=True).replace('<svg ', f'<svg width="{w}" height="{h}" ', 1)

def encode(svg, w, h, name):
    png = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-f", "png"], input=svg.encode(), capture_output=True, check=True).stdout
    strip = ["-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt"]
    base = Path(name).stem
    for ext, extra in (("png", []), ("webp", ["-quality", "92", "-define", "webp:method=6"]), ("avif", ["-quality", "70"])):
        if ext == "png" and "804" not in name: continue
        if ext in ("webp", "avif") or "804" in name:
            subprocess.run(["magick", "png:-"] + strip + extra + [str(OUT / f"{base}.{ext}")], input=png, check=True)

def main():
    OUT.mkdir(exist_ok=True)
    for w, h in ((887, 640), (804, 770), (402, 385)):
        svg = hero_svg(w, h); name = f"gremlin-hero-{w}x{h}"
        (OUT / f"{name}.svg").write_text(svg)
        encode(svg, w, h, name)
    (OUT / "gremlin-hero-887x640.avif").unlink(missing_ok=True); (OUT / "gremlin-hero-887x640.png").unlink(missing_ok=True)
    (OUT / "gremlin-hero-402x385.png").unlink(missing_ok=True)
    av = head(tile("dark", pupils=True, scale=0.70, rx=0), "yolo-labz org avatar")
    raster(av, 460, 460, OUT / "gremlin-avatar-460.png"); raster(av, 96, 96, OUT / "gremlin-avatar-96.png")
    subprocess.run(["magick", str(OUT / "gremlin-avatar-96.png"), "-quality", "92", str(OUT / "gremlin-avatar-96.webp")], check=True)
    files = []
    for n in ("gremlin-hero-887x640.webp", "gremlin-hero-804x770.avif", "gremlin-hero-804x770.webp", "gremlin-hero-804x770.png",
              "gremlin-hero-402x385.avif", "gremlin-hero-402x385.webp", "gremlin-avatar-96.png", "gremlin-avatar-96.webp", "gremlin-avatar-460.png"):
        b = (OUT / n).read_bytes()
        wh = subprocess.run(["magick", "identify", "-format", "%w %h", str(OUT / n) + "[0]"], capture_output=True, text=True).stdout.split()
        files.append(dict(file=n, width=int(wh[0]), height=int(wh[1]), bytes=len(b), sha256=hashlib.sha256(b).hexdigest()))
    src = hashlib.sha256((HERE / "character.py").read_bytes()).hexdigest()
    (OUT / "manifest.json").write_text(json.dumps(dict(schema=1, alt=ALT, inputs={"mark/character.py": src}, files=files), indent=2) + "\n")

if __name__ == "__main__": main()
