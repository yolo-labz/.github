"""Publish the served hero and avatar files adopted on 08/11/2026.

The decision (hero-decision/README.md): the GPT master for every hero slot, the
vector model-sheet kit for the 96 px avatar. This script cuts the served files
with the same crop and encoder settings the decision sheet was judged on
(hero-decision/build_sheet.py), then writes manifest.json with the size and
sha256 of every output and the sha256 of every input.

Usage (ImageMagick 7 with WebP/AVIF delegates, rsvg-convert):
    python3 profile/assets/brand/hero/publish.py            # from the repo root
    python3 profile/assets/brand/hero/publish.py --verify   # sizes + sha256 only

Encoder bytes can differ across ImageMagick/libheif builds, so --verify checks
the committed files against the manifest; it does not re-encode.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent
SHEET = BRAND / "hero-decision" / "build_sheet.py"
GPT_WIDE = BRAND / "rollout" / "gremlin-wide-hero.png"
AVATAR_SVG = BRAND / "mascot" / "gremlin-avatar.svg"
ALT = (
    "Green programming gremlin with pointed ears and a fanged grin typing on a keyboard, "
    "with mauve code accents"
)
AVATAR_ALT = "The yolo-labz gremlin's head: pointed ears, mauve eyes and a fanged grin"

# (stem, width, height, formats). The 402 plate shares the 804 crop window
# (same aspect), so phones see the same framing at half the pixels.
HEROES = [
    ("gremlin-hero-gpt-887x640", 887, 640, ("webp",)),
    ("gremlin-hero-gpt-804x770", 804, 770, ("avif", "webp", "png")),
    ("gremlin-hero-gpt-402x385", 402, 385, ("avif", "webp")),
]
# 96 px is the decided slot; 460 px is the upload GitHub asks for an org avatar.
AVATARS = [
    ("gremlin-avatar-96", 96, ("png", "webp")),
    ("gremlin-avatar-460", 460, ("png",)),
]


def load_sheet():
    spec = importlib.util.spec_from_file_location("build_sheet", SHEET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def emit(sheet, png: Path, stem: str, formats) -> None:
    for fmt in formats:
        target = HERE / f"{stem}.{fmt}"
        if fmt == "png":
            sheet.run(
                "magick",
                png,
                "-strip",
                "-define",
                "png:exclude-chunks=date,time",
                target,
            )
        else:
            sheet.run("magick", png, "-strip", *sheet.ENC[fmt], target)


def build() -> None:
    sheet = load_sheet()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for stem, width, height, formats in HEROES:
            png = work / f"{stem}.png"
            sheet.gpt_cell(GPT_WIDE, GPT_WIDE, ("hero", "", width, height), png)
            emit(sheet, png, stem, formats)
        for stem, size, formats in AVATARS:
            png = work / f"{stem}.png"
            sheet.svg_cell(BRAND / "mascot", ("avatar", "", size, size), png)
            emit(sheet, png, stem, formats)


def describe(sheet, path: Path) -> dict:
    width, height = sheet.run(
        "magick", "identify", "-format", "%w %h", f"{path}[0]"
    ).stdout.split()
    return {
        "file": path.name,
        "width": int(width),
        "height": int(height),
        "bytes": path.stat().st_size,
        "sha256": sheet.sha(path),
    }


def manifest() -> dict:
    sheet = load_sheet()
    files = [f"{stem}.{fmt}" for stem, _, _, formats in HEROES for fmt in formats]
    files += [f"{stem}.{fmt}" for stem, _, formats in AVATARS for fmt in formats]
    return {
        "schema": 1,
        "decision": "hero-decision/README.md (adopted 08/11/2026)",
        "alt": {"hero": ALT, "avatar": AVATAR_ALT},
        "inputs": {
            str(p.relative_to(BRAND)): sheet.sha(p) for p in (GPT_WIDE, AVATAR_SVG)
        },
        "files": [describe(sheet, HERE / name) for name in files],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    pinned = HERE / "manifest.json"
    if args.verify:
        want = json.loads(pinned.read_text())
        got = manifest()
        if want != got:
            print("hero manifest drift:", json.dumps(got, indent=2), file=sys.stderr)
            return 1
        print(f"hero: {len(got['files'])} files match manifest.json")
        return 0
    build()
    pinned.write_text(json.dumps(manifest(), indent=2) + "\n")
    print(f"wrote {pinned}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
