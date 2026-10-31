#!/usr/bin/env python3
"""Render the social cards from the gremlin model — no hand-made raster.

The card is not a designed image with a gremlin pasted on: it is a deterministic
compose of two generated things,

  1. the character, rendered from ``params.json`` through Blender exactly like
     ``make model`` (the same script, one view);
  2. the title, typeset in a real font over an SVG template and rasterised by
     ``rsvg-convert`` — never generated lettering, never a screenshot.

Everything the card shows comes from ``params.json`` (palette) plus the copy in
``docs/brand-positioning.md``'s positioning line, so a palette change moves the
cards with the character instead of leaving a stale raster behind.

Sizes are the platform contracts, not preferences:

| File | Size | Consumer |
| --- | --- | --- |
| ``og-card.png`` | 1200x630 | Open Graph ``og:image`` |
| ``twitter-card.png`` | 1200x600 | Twitter/X ``summary_large_image`` |
| ``social-preview-1280x640.png`` | 1280x640 | GitHub repository social preview |

A second run must reproduce every byte. ``cards.json`` carries the sha256 of each
committed card; a run compares against it and fails loudly on any drift, so
"regenerated" never quietly means "different".

Usage
    python3 model/cards.py                 # render, verify against cards.json, write
    python3 model/cards.py --update        # accept a deliberate visual change
    python3 model/cards.py --build DIR --dest DIR
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from pngmeta import normalise_png

CARDS = (
    {"file": "og-card.png", "width": 1200, "height": 630, "use": "Open Graph"},
    {
        "file": "twitter-card.png",
        "width": 1200,
        "height": 600,
        "use": "Twitter/X summary_large_image",
    },
    {
        "file": "social-preview-1280x640.png",
        "width": 1280,
        "height": 640,
        "use": "GitHub repository social preview",
    },
)

#: The positioning line from docs/brand-positioning.md, split for typesetting.
TITLE = "yolo-labz"
TAGLINE = "Small tools. Deliberate automation."
SUBTITLE = (
    "Open-source tools for scripting messaging,",
    "browser workflows and local services.",
)
FONT_STACK = "Inter, DejaVu Sans, sans-serif"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model_check():
    """Import model/check.py, whose colour maths the cards are held to."""
    spec = importlib.util.spec_from_file_location(
        "gremlin_model_check", HERE / "check.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_hero(blender: str, threads: int, build: Path) -> Path:
    """One Blender view from params.json — the same script `make model` runs."""
    build.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            blender,
            "-b",
            "--factory-startup",
            "-t",
            str(threads),
            "-P",
            str(HERE / "gremlin.py"),
            "--",
            "--out",
            str(build),
            "--views",
            "hero",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    hero = build / "gremlin-hero.png"
    if not hero.is_file():
        raise SystemExit(f"cards.py: blender wrote no hero render at {hero}")
    return hero


def card_svg(width: int, height: int, hero_b64: str, palette: dict) -> str:
    """One card as SVG: plate, character, typeset title. No hand-placed pixels."""
    base = palette["base"]["hex"]
    pale = palette["pale"]["hex"]
    node = palette["node"]["hex"]
    guide = palette["guide"]["hex"]

    pad = round(height * 0.075)
    hero_h = round(height * 0.90)
    hero_w = hero_h
    hero_x = width - pad - hero_w
    title_px = round(height * 0.150)
    tag_px = round(height * 0.046)
    sub_px = round(height * 0.040)

    y = round(height * 0.24)
    title_base = y
    rule_y = title_base + round(height * 0.045)
    tag_base = rule_y + round(height * 0.105)
    sub_base = tag_base + round(height * 0.105)
    sub_lead = round(sub_px * 1.45)

    def text(x, baseline, size, fill, content, weight=400, spacing="-0.01em"):
        return (
            f'  <text x="{x}" y="{baseline}" font-family="{FONT_STACK}" '
            f'font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" '
            f'fill="{fill}">{content}</text>'
        )

    body = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{base}"/>',
        (
            f'  <image x="{hero_x}" y="{height - hero_h}" width="{hero_w}" '
            f'height="{hero_h}" preserveAspectRatio="xMidYMax meet" '
            f'xlink:href="data:image/png;base64,{hero_b64}"/>'
        ),
        text(pad, title_base, title_px, pale, TITLE, weight=700, spacing="-0.02em"),
        (
            f'  <rect x="{pad}" y="{rule_y}" width="{round(width * 0.16)}" '
            f'height="{max(2, round(height * 0.005))}" fill="{node}"/>'
        ),
        text(pad, tag_base, tag_px, pale, TAGLINE),
        text(pad, sub_base, sub_px, guide, SUBTITLE[0]),
        text(pad, sub_base + sub_lead, sub_px, guide, SUBTITLE[1]),
        "</svg>",
    ]
    return "\n".join(body) + "\n"


def rasterise(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        ["rsvg-convert", "-o", str(png_path), str(svg_path)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    normalise_png(png_path)


def check_size(path: Path, width: int, height: int) -> None:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"cards.py: {path.name} is not a PNG")
    got = struct.unpack(">II", raw[16:24])
    if got != (width, height):
        raise SystemExit(
            f"cards.py: {path.name} is {got[0]}x{got[1]}, want {width}x{height}"
        )


def check_palette(model_check, params: dict, paths: list[Path]) -> list[str]:
    report: list[str] = []
    ok = model_check.check_palette(params, [str(p) for p in paths], report)
    for line in report:
        print(line)
    if not ok:
        raise SystemExit("cards.py: card palette drifted from params.json")
    return report


def verify(dest: Path) -> int:
    """Cheap, blender-free check that the committed cards match the contract."""
    manifest_path = dest / "cards.json"
    if not manifest_path.is_file():
        raise SystemExit(f"cards.py: no {manifest_path}; run `make cards`")
    manifest = json.loads(manifest_path.read_text())
    failures = 0
    for row in manifest["cards"]:
        path = dest / row["file"]
        if not path.is_file():
            print(f"  CARD {row['file']}: FAIL missing")
            failures += 1
            continue
        check_size(path, row["width"], row["height"])
        got = digest(path)
        if got != row["sha256"]:
            print(f"  CARD {row['file']}: FAIL {got[:12]} != {row['sha256'][:12]}")
            failures += 1
            continue
        print(f"  CARD {row['file']:<32} {row['width']}x{row['height']} {got[:16]} ok")
    if failures:
        raise SystemExit(f"cards.py: {failures} card(s) do not match cards.json")
    print(f"cards.py: {len(manifest['cards'])} cards match cards.json and their sizes")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", default=str(REPO / "build/cards"))
    parser.add_argument("--dest", default=str(REPO / "profile/assets/brand"))
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument(
        "--update",
        action="store_true",
        help="rewrite cards.json instead of failing on a changed card",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="check the committed cards against cards.json without rendering",
    )
    args = parser.parse_args(argv)

    if args.verify:
        return verify(Path(args.dest))

    build = Path(args.build)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    params = json.loads((HERE / "params.json").read_text())
    manifest_path = dest / "cards.json"
    previous = (
        json.loads(manifest_path.read_text()) if manifest_path.is_file() else None
    )
    known = {row["file"]: row["sha256"] for row in (previous or {}).get("cards", [])}

    hero = render_hero(args.blender, args.threads, build)
    hero_b64 = base64.b64encode(hero.read_bytes()).decode()

    produced = []
    for card in CARDS:
        svg_path = build / card["file"].replace(".png", ".svg")
        svg_path.write_text(
            card_svg(card["width"], card["height"], hero_b64, params["palette"])
        )
        rasterise(svg_path, build / card["file"])
        check_size(build / card["file"], card["width"], card["height"])
        produced.append(build / card["file"])

    check_palette(load_model_check(), params, produced)

    rows = []
    drifts = []
    for card, path in zip(CARDS, produced):
        sha = digest(path)
        rows.append(
            {
                "file": card["file"],
                "width": card["width"],
                "height": card["height"],
                "use": card["use"],
                "sha256": sha,
            }
        )
        if known.get(card["file"]) not in (None, sha):
            drifts.append(f"{card['file']}: {known[card['file']][:12]} -> {sha[:12]}")
    if drifts and not args.update:
        raise SystemExit(
            "cards.py: rendered bytes differ from the committed cards.json "
            f"({'; '.join(drifts)}). Re-run with --update only for a deliberate change."
        )

    for path in produced:
        (dest / path.name).write_bytes(path.read_bytes())
    manifest = {
        "schema": 1,
        "generated_by": "model/cards.py",
        "classification": "generated-example",
        "source": {
            "params": "model/params.json",
            "params_sha256": digest(HERE / "params.json"),
            "render": "model/gremlin.py --views hero (workbench, flat)",
            "typeset": FONT_STACK,
            "copy": "docs/brand-positioning.md (positioning line)",
        },
        "cards": rows,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for row in rows:
        print(
            f"  CARD {row['file']:<32} {row['width']}x{row['height']} {row['sha256'][:16]}"
        )
    print(f"cards.py: wrote {len(rows)} cards to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
