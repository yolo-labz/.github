"""Build the hero decision sheet: three candidates x four slots, side by side.

Candidates
  gpt      the GPT wide hero served today (rollout/gremlin-wide-hero.png) and the
           GPT square avatar master (exploration/2026-09-28/gremlin-square-avatar.png)
  blender  model/ rendered natively at each slot size (render_blender.py)
  svgkit   the vector model-sheet kit (mascot/gremlin-hero.svg, gremlin-avatar.svg)

Slots are the sizes the hero is served at. Every cell is a lossless PNG at the
slot's native pixel size on the same plate, so the sheet is 1:1 pixels, not a
mock-up. Nothing here edits a served asset.

Usage (stdlib + ImageMagick + rsvg-convert; Blender frames come from
render_blender.py):
    python3 build_sheet.py --src SRC_DIR --blender BLENDER_DIR --model MODEL_DIR --out OUT_DIR

SRC_DIR holds the unmodified sources, copied from `git show origin/main:...`.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

PLATE = "#1e1e2e"  # Mocha base: the site, the profile plate and all three sources
SHEET_BG = "#11111b"
SKIN = (0xA6, 0xE3, 0xA1)
SLOTS = [
    ("org", "Org profile area", 887, 640),
    ("portfolio", "Portfolio desktop hero", 804, 770),
    ("mobile", "Mobile hero", 390, 520),
    ("avatar", "Org avatar", 96, 96),
]
SOURCES = [
    ("gpt", "GPT master"),
    ("blender", "Blender render"),
    ("svgkit", "Vector model-sheet kit"),
]
ENC = {
    "webp": [
        "-quality",
        "88",
        "-define",
        "webp:method=4",
        "-define",
        "webp:thread-level=1",
    ],
    "avif": ["-quality", "60", "-define", "heic:speed=4", "-define", "heic:threads=1"],
}


def run(*argv, **kw):
    return subprocess.run(
        [str(a) for a in argv], check=True, capture_output=True, text=True, **kw
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(png: Path) -> tuple[int, int, int, int]:
    """Bounding box (w, h, x, y) of everything that is not the corner colour."""
    out = run("magick", png, "-fuzz", "6%", "-format", "%@", "info:").stdout
    w, h, x, y = (
        int(v) for v in re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", out).groups()
    )
    return w, h, x, y


def gpt_cell(src: Path, avatar_src: Path, slot, dest: Path):
    key, _, width, height = slot
    if key == "avatar":
        run(
            "magick",
            avatar_src,
            "-filter",
            "Lanczos",
            "-resize",
            f"{width}x{height}!",
            "-depth",
            "8",
            "-strip",
            dest,
        )
        return {
            "fit": "dedicated square avatar master, downscaled",
            "crop": [1254, 1254],
            "scale": round(width / 1254, 4),
            "upscaled": False,
            "padded": False,
        }
    img_w, img_h = 1774, 887
    bw, bh, bx, by = bbox(src)
    bg = run("magick", src, "-format", "%[hex:p{4,4}]", "info:").stdout.strip()
    need_w, need_h = bw * 1.12, bh * 1.12  # same 6 % margin per side as the Blender fit
    crop_w = max(need_w, need_h * width / height)
    crop_h = crop_w * height / width
    if (
        crop_h > img_h and crop_w * img_h / crop_h >= bw
    ):  # height-limited: use the full height
        crop_w, crop_h = crop_w * img_h / crop_h, img_h
    crop_w, crop_h = round(crop_w), round(crop_h)
    x = round(bx + bw / 2 - crop_w / 2)
    y = round(by + bh / 2 - crop_h / 2)
    x = min(max(x, 0), img_w - crop_w) if crop_w <= img_w else x
    y = min(max(y, 0), img_h - crop_h) if crop_h <= img_h else y
    padded = crop_w > img_w or crop_h > img_h
    # Composite the source onto a canvas the size of the window; the canvas colour
    # is the image's own corner colour, so padding is seamless.
    run(
        "magick",
        "-size",
        f"{crop_w}x{crop_h}",
        f"xc:#{bg}",
        src,
        "-geometry",
        f"{-x:+d}{-y:+d}",
        "-composite",
        "-filter",
        "Lanczos",
        "-resize",
        f"{width}x{height}!",
        "-depth",
        "8",
        "-strip",
        dest,
    )
    scale = width / crop_w
    return {
        "fit": "art-directed crop to the character, same margin as the Blender fit"
        + (", plate-padded where the art has no room" if padded else ""),
        "crop": [crop_w, crop_h],
        "scale": round(scale, 4),
        "upscaled": scale > 1,
        "padded": padded,
        "character_bbox_native": [bw, bh],
    }


def svg_cell(src_dir: Path, slot, dest: Path):
    key, _, width, height = slot
    if key == "avatar":
        run(
            "rsvg-convert",
            "-w",
            width,
            "-h",
            height,
            "-b",
            PLATE,
            src_dir / "gremlin-avatar.svg",
            "-o",
            dest,
        )
        return {
            "fit": "vector avatar tile, rendered at 96 px",
            "crop": [128, 128],
            "scale": round(width / 128, 4),
            "upscaled": False,
            "padded": False,
        }
    inner_w, inner_h = round(width * 0.94), round(height * 0.94)
    run(
        "rsvg-convert",
        "-w",
        inner_w,
        "-h",
        inner_h,
        "--keep-aspect-ratio",
        "-b",
        PLATE,
        src_dir / "gremlin-hero.svg",
        "-o",
        dest,
    )
    run(
        "magick",
        dest,
        "-background",
        PLATE,
        "-gravity",
        "center",
        "-extent",
        f"{width}x{height}",
        dest,
    )
    return {
        "fit": "vector, contained at 94 % (3:2 viewBox letterboxed on the plate)",
        "crop": [240, 160],
        "scale": None,
        "upscaled": False,
        "padded": True,
    }


def blender_cell(blender_dir: Path, slot, dest: Path):
    key, _, width, height = slot
    name = {
        "org": "org-887x640",
        "portfolio": "portfolio-804x770",
        "mobile": "mobile-390x520",
        "avatar": "avatar-96x96",
    }[key]
    run("cp", blender_dir / f"{name}.png", dest)
    return {
        "fit": "rendered natively at the slot size, camera fitted to the content"
        + (" (head only)" if key == "avatar" else ""),
        "crop": [width, height],
        "scale": 1.0,
        "upscaled": False,
        "padded": False,
    }


def encode(png: Path, out_dir: Path, stem: str) -> dict:
    sizes = {"png": png.stat().st_size}
    for fmt, args in ENC.items():
        target = out_dir / f"{stem}.{fmt}"
        run("magick", png, "-strip", *args, target)
        sizes[fmt] = target.stat().st_size
    return sizes


def dominant_skin_delta(png: Path, model_dir: Path) -> dict:
    """Most frequent non-plate colour (the skin) and its CIEDE2000 distance to the palette."""
    out = run("magick", png, "-format", "%c", "histogram:info:").stdout
    rows = []
    for line in out.splitlines():
        m = re.match(r"\s*(\d+):.*?\((\s*\d+),\s*(\d+),\s*(\d+)", line)
        if m:
            rows.append((int(m[1]), (int(m[2]), int(m[3]), int(m[4]))))
    spec = importlib.util.spec_from_file_location("model_check", model_dir / "check.py")
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    lab_skin = chk.rgb_to_lab(SKIN)
    # Only pixels that are greenish: g clearly above r and b. Pick the most populous.
    greens = [(n, c) for n, c in rows if c[1] > c[0] + 25 and c[1] > c[2] + 25]
    if not greens:
        return {"skin": None, "delta_e2000": None}
    _, colour = max(greens)
    return {
        "skin": "#{:02x}{:02x}{:02x}".format(*colour),
        "delta_e2000": round(chk.delta_e_2000(chk.rgb_to_lab(colour), lab_skin), 2),
    }


def character_extent(png: Path) -> list[int]:
    w, h, _, _ = bbox(png)
    return [w, h]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--blender", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src, blender, model, out = Path(a.src), Path(a.blender), Path(a.model), Path(a.out)
    cells_dir, work = out / "cells", out / ".work"
    cells_dir.mkdir(parents=True, exist_ok=True)
    work.mkdir(exist_ok=True)

    results = []
    for slot in SLOTS:
        key, label, width, height = slot
        for source, source_label in SOURCES:
            stem = f"{key}-{source}"
            png = work / f"{stem}.png"
            if source == "gpt":
                meta = gpt_cell(
                    src / "gremlin-wide-hero.png",
                    src / "gremlin-square-avatar.png",
                    slot,
                    png,
                )
            elif source == "blender":
                meta = blender_cell(blender, slot, png)
            else:
                meta = svg_cell(src, slot, png)
            ident = run("magick", "identify", "-format", "%w %h", png).stdout.split()
            assert [int(v) for v in ident] == [width, height], (stem, ident)
            weights = encode(png, cells_dir, stem)
            ext = character_extent(png)
            skin = dominant_skin_delta(png, model)
            results.append(
                {
                    "slot": key,
                    "slot_label": label,
                    "source": source,
                    "source_label": source_label,
                    "width": width,
                    "height": height,
                    "weights": weights,
                    "character_px": ext,
                    **skin,
                    **meta,
                }
            )

    (out / "results.json").write_text(
        json.dumps(
            {
                "plate": PLATE,
                "encoders": ENC,
                "slots": [list(s) for s in SLOTS],
                "cells": results,
                "sources_sha256": {
                    p.name: sha(p) for p in sorted(src.glob("*")) if p.is_file()
                },
            },
            indent=1,
        )
        + "\n"
    )
    sheet(out, work, results, src)
    print(f"build_sheet.py: {len(results)} cells, sheet {out / 'contact-sheet.png'}")


def sheet(out: Path, work: Path, results, src: Path) -> None:
    """One PNG: rows = slots, columns = candidates, every cell at native pixels."""
    pad, label_w, head_h, row_gap = 24, 250, 70, 70
    col_w = 887
    cols = len(SOURCES)
    width = label_w + cols * (col_w + pad) + pad
    row_h = {"org": 640, "portfolio": 770, "mobile": 520, "avatar": 520}
    total_h = head_h + sum(row_h[s[0]] + row_gap for s in SLOTS) + pad
    cmd = [
        "magick",
        "-size",
        f"{width}x{total_h}",
        f"xc:{SHEET_BG}",
        "-font",
        "DejaVu-Sans",
        "-fill",
        "#cdd6f4",
        "-pointsize",
        "26",
    ]
    for i, (_, label) in enumerate(SOURCES):
        cmd += ["-annotate", f"+{label_w + pad + i * (col_w + pad)}+44", label]
    y = head_h
    for key, label, w, h in SLOTS:
        cmd += [
            "-fill",
            "#a6adc8",
            "-pointsize",
            "20",
            "-annotate",
            f"+{pad}+{y + 28}",
            label,
            "-annotate",
            f"+{pad}+{y + 56}",
            f"{w} x {h} px",
        ]
        for i, (source, _) in enumerate(SOURCES):
            x = label_w + pad + i * (col_w + pad)
            cell = work / f"{key}-{source}.png"
            if key == "avatar":
                zoom = work / f"{key}-{source}-zoom.png"
                run("magick", cell, "-filter", "point", "-resize", "400%", zoom)
                word = src / "logo-wordmark-dark.png"
                lockup = work / f"{source}-lockup.png"
                run(
                    "magick",
                    "-size",
                    "440x96",
                    f"xc:{PLATE}",
                    cell,
                    "-geometry",
                    "+0+0",
                    "-composite",
                    "(",
                    word,
                    "-resize",
                    "320x",
                    ")",
                    "-geometry",
                    "+112+8",
                    "-composite",
                    lockup,
                )
                cmd += [
                    str(lockup),
                    "-geometry",
                    f"+{x}+{y}",
                    "-composite",
                    str(zoom),
                    "-geometry",
                    f"+{x}+{y + 112}",
                    "-composite",
                ]
            else:
                cmd += [str(cell), "-geometry", f"+{x}+{y}", "-composite"]
        y += row_h[key] + row_gap
    cmd += ["-depth", "8", "-strip", str(out / "contact-sheet.png")]
    run(*cmd)


if __name__ == "__main__":
    main()
