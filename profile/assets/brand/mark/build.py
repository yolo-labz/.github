#!/usr/bin/env python3
"""Build every logo, icon and avatar from the one master in master.py. Nothing in the set is drawn by hand.

    python3 profile/assets/brand/mark/build.py            # write the set
    python3 profile/assets/brand/mark/build.py --verify   # rebuild to a temp dir, compare bytes with the committed files
    python3 profile/assets/brand/mark/build.py --social OUT.png --repo NAME --line "one line"

Needs rsvg-convert and ImageMagick (magick). No Python packages.
"""
import argparse, hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from master import DIRS, PAL, SHIP, svg

BRAND = HERE.parent
TITLE = "yolo-labz"
DESC = "yolo-labz: the gremlin's head, pointed ears and two slanted eyes."

def head(s, desc=DESC):
    """add role + title/desc to the root element"""
    return s.replace(' viewBox="0 0 16 16"', ' viewBox="0 0 16 16" width="128" height="128" role="img" aria-labelledby="t d"', 1).replace(
        ">", f'><title id="t">{TITLE}</title><desc id="d">{desc}</desc>', 1)

def tile(scheme, pupils=True, scale=0.82, rx=3.4):
    return svg(SHIP, "colour", scheme, True, pupils=pupils, scale=scale, rx=rx)
def loose(scheme, pupils=True):
    return svg(SHIP, "colour", scheme, False, pupils=pupils)

def favicon_svg():
    """scheme-aware tile: dark by default, light under prefers-color-scheme: light. No pupils (sub-pixel at 16)."""
    D, d, l = DIRS[SHIP], PAL["dark"], PAL["light"]
    sc = 0.82; t = (1 - sc) * 8
    sil = "".join(f'<path d="{p}"/>' for p in D["sil"])
    feat = "".join(f'<path d="{p}"/>' for p in D["feat"].values())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="128" height="128" role="img" aria-labelledby="t d"><title id="t">{TITLE}</title><desc id="d">{DESC}</desc><style>.g{{fill:{d["ground"]}}}.s{{fill:{d["skin"]}}}.f{{fill:{d["feat"]}}}@media (prefers-color-scheme:light){{.g{{fill:{l["ground"]}}}.s{{fill:{l["skin"]}}}.f{{fill:{l["feat"]}}}}}</style><rect class="g" width="16" height="16" rx="3.4"/><g transform="translate({t:.3f} {t+0.2:.3f}) scale({sc})"><g class="s">{sil}</g><g class="f">{feat}</g></g></svg>
'''

def mono_svg():
    s = svg(SHIP, "mono", "dark", False)
    return head(s.replace(PAL["dark"]["ink"], "currentColor"), "yolo-labz: the gremlin's head in one colour.")

def wordmark(scheme):
    P = PAL[scheme]
    frag = (HERE / "wordmark-text.svgfrag").read_text().strip()
    frag = frag.replace("fill:#cdd6f4", f"fill:{P['ink']}").replace("fill:#cba6f7", f"fill:{P['node']}")
    mark = svg(SHIP, "colour", scheme, False, pupils=True)
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", mark.strip())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 470 128" width="470" height="128" role="img" aria-labelledby="t d">'
            f'<title id="t">{TITLE}</title><desc id="d">yolo-labz horizontal lockup: the gremlin mark and the name in monospace.</desc>'
            f'<g transform="translate(4 12) scale(6.5)">{inner}</g>'
            f'<g transform="translate(6 0)">{frag}</g></svg>\n')

def social(repo=None, line="Small tools. Deliberate automation."):
    """1280 x 640 card: ground, mark at the left, name and one line at the right. Fonts are only needed at build time."""
    P = PAL["dark"]
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg(SHIP, "colour", "dark", False, pupils=True).strip())
    name = repo or "yolo-labz"
    esc = lambda x: x.replace("&", "&amp;").replace("<", "&lt;")
    sub = f'<text x="560" y="214" font-family="JetBrains Mono, JetBrainsMono Nerd Font Mono, monospace" font-size="30" fill="{P["node"]}">yolo-labz</text>' if repo else ""
    size = 92 if len(name) <= 14 else (72 if len(name) <= 20 else 54)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640">'
            f'<rect width="1280" height="640" fill="{P["ground"]}"/>'
            f'<g transform="translate(96 160) scale(25)">{inner}</g>'
            f'{sub}<text x="560" y="{330 if repo else 300}" font-family="JetBrains Mono, JetBrainsMono Nerd Font Mono, monospace" font-weight="500" font-size="{size}" fill="{P["ink"]}">{esc(name)}</text>'
            f'<text x="560" y="{400 if repo else 372}" font-family="Inter, sans-serif" font-size="34" fill="#a6adc8">{esc(line)}</text></svg>\n')

def raster(svg_text, w, h, out):
    p = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-f", "png"], input=svg_text.encode(), capture_output=True)
    if p.returncode: raise SystemExit(p.stderr.decode())
    q = subprocess.run(["magick", "png:-", "-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", "png:-"], input=p.stdout, capture_output=True)
    if q.returncode: raise SystemExit(q.stderr.decode())
    out.write_bytes(q.stdout)

def build(root):
    root = Path(root); (root / "favicons").mkdir(parents=True, exist_ok=True); (root / "mark").mkdir(parents=True, exist_ok=True)
    W = lambda rel, text: (root / rel).write_text(text)
    for sch in ("dark", "light"):
        t = head(tile(sch)); W(f"logo-mark-{sch}.svg", t); raster(t, 512, 512, root / f"logo-mark-{sch}.png")
        w = wordmark(sch); W(f"logo-wordmark-{sch}.svg", w); raster(w, 940, 256, root / f"logo-wordmark-{sch}.png")
    W("logo-mark-mono.svg", mono_svg())
    fav = favicon_svg(); W("favicons/favicon.svg", fav)
    for n in (16, 32, 48, 64, 128, 192, 512):
        raster(tile("dark", pupils=n >= 64), n, n, root / f"favicons/favicon-{n}.png")
    raster(tile("dark", pupils=True, scale=0.82, rx=0), 180, 180, root / "favicons/apple-touch-icon.png")
    subprocess.run(["magick"] + [str(root / f"favicons/favicon-{n}.png") for n in (16, 32, 48)] + [str(root / "favicons/favicon.ico")], check=True)
    # org avatar: full-bleed square (GitHub rounds or circles it), mark at 0.70 so the ear tips survive a circle crop
    av = head(tile("dark", pupils=True, scale=0.70, rx=0), "yolo-labz org avatar: the gremlin's head on the base colour.")
    W("mark/avatar.svg", av); raster(av, 460, 460, root / "mark/avatar-460.png"); raster(av, 96, 96, root / "mark/avatar-96.png")
    s = social(); W("mark/social-org.svg", s); raster(s, 1280, 640, root / "mark/social-org-1280x640.png")

OUT = ["logo-mark-dark.svg","logo-mark-dark.png","logo-mark-light.svg","logo-mark-light.png","logo-mark-mono.svg","logo-wordmark-dark.svg","logo-wordmark-dark.png","logo-wordmark-light.svg","logo-wordmark-light.png",
       "favicons/favicon.svg","favicons/favicon.ico","favicons/apple-touch-icon.png"]+[f"favicons/favicon-{n}.png" for n in (16,32,48,64,128,192,512)]+["mark/avatar.svg","mark/avatar-460.png","mark/avatar-96.png","mark/social-org.svg","mark/social-org-1280x640.png"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--verify", action="store_true"); ap.add_argument("--social"); ap.add_argument("--repo"); ap.add_argument("--line", default="Small tools. Deliberate automation.")
    a = ap.parse_args()
    if a.social:
        raster(social(a.repo, a.line), 1280, 640, Path(a.social)); sys.exit(0)
    if a.verify:
        with tempfile.TemporaryDirectory() as td:
            build(td); bad = [f for f in OUT if sha(Path(td)/f) != sha(BRAND/f)]
        print("drift:", bad or "none"); sys.exit(1 if bad else 0)
    build(BRAND)
    json.dump({f: sha(BRAND/f) for f in OUT}, open(HERE/"manifest.json","w"), indent=1); print("built", len(OUT), "files")
