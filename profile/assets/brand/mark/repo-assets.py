#!/usr/bin/env python3
"""Bring one repo's header art to the org mark.

    python3 repo-assets.py REPO_CHECKOUT REPO_NAME "one line for the card"

- docs/assets/hero-{dark,light}.svg: footer becomes a lockup (mark + yolo-labz/REPO, 14 units); a borrowed gopher is
  replaced by the gremlin's head; a title that runs into the artwork is shrunk to clear it.
- .github/og-card.png: the 1280x640 social card from build.py.
"""
import re, subprocess, sys
from pathlib import Path
from master import svg, SHIP
from character import head_front, paint
from build import social, raster

FOOT = re.compile(r'<text x="1128" y="338" font-size="11"( text-anchor="end">)(yolo-labz/[^<]+)</text>')
GOPHER = re.compile(r'<g transform="translate\(1056,232\)" fill="#[0-9a-f]{6}" opacity="0.55">.*?</g>\s*', re.S)
TITLE = re.compile(r'(<text x="72" y="\d+" font-size=")(\d+)(" font-weight="700" letter-spacing="-\d+">(?:kokoro-speakd|chrome-bridge)</text>)')
FIT = {"kokoro-speakd": 72, "chrome-bridge": 76}

def inner(scheme):
    return re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg(SHIP, "colour", scheme, False).strip())

def patch(text, scheme, repo):
    foot = FOOT.search(text)
    if foot:
        label = foot.group(2); w = len(label) * 0.6 * 14
        x = 1128 - w - 34
        text = FOOT.sub(f'<text x="1128" y="338" font-size="14"\\1\\2</text>', text)
        text = text.replace("</svg>", f'<g transform="translate({x:.0f} 322) scale(1.5)">{inner(scheme)}</g></svg>')
    if GOPHER.search(text) and "gopher" in text:
        head = paint(head_front("grin"), scheme)
        text = GOPHER.sub(f'<g transform="translate(1056 240) scale(5.6)">{head}</g>\n  ', text, count=1)
        text = text.replace("a small gopher silhouette anchoring the lower-right corner", "the gremlin's head anchoring the lower-right corner")
    if repo in FIT: text = TITLE.sub(lambda m: m.group(1) + str(FIT[repo]) + m.group(3), text)
    return text

def main(root, repo, line):
    root = Path(root)
    for sch in ("dark", "light"):
        f = root / f"docs/assets/hero-{sch}.svg"
        if f.exists(): f.write_text(patch(f.read_text(), sch, repo))
    card = root / ".github/og-card.png"; card.parent.mkdir(exist_ok=True)
    raster(social(repo, line), 1280, 640, card)

if __name__ == "__main__": main(*sys.argv[1:4])
