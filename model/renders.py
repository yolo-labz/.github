#!/usr/bin/env python3
"""Publish the gremlin hero plate at the sizes downstream consumers ask for.

Nothing here is drawn: the character comes from ``params.json`` through
``gremlin.py`` exactly like ``make model``, the camera is fitted to it per frame,
and the only transformation afterwards is the format encode. The palette is the
kit's own two flavours — Mocha and Latte — so a light plate is the same character,
not a recolour someone chose here.

Why publish at all: the portfolio home render used to be produced by hand from a
900x900 ``make model`` output (crop, rescale, re-encode), which made the shipped
bytes unverifiable. A published plate with a pinned sha256 is the thing a consumer
can cite.

Usage
    python3 model/renders.py              # render, compare with manifest.json
    python3 model/renders.py --update     # accept a deliberate visual change
    python3 model/renders.py --verify      # sha256 + size check, no blender
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEST = REPO / "profile/assets/brand/renders"
MANIFEST = DEST / "manifest.json"

# Pinned encoder settings. Multithreaded WebP/AVIF encoding is not byte-stable, so
# every format is forced single-threaded and a fixed method/speed: two runs of the
# same pixels must produce the same file, or the sha256 contract in manifest.json
# would be unverifiable.
ENCODERS = {
    "webp": lambda quality: [
        "-quality", str(quality),
        "-define", "webp:method=4",
        "-define", "webp:thread-level=1",
    ],
    "avif": lambda quality: [
        "-quality", str(quality),
        "-define", "heic:speed=4",
        "-define", "heic:threads=1",
    ],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_size(path: Path) -> tuple[int, int]:
    """Read the pixel size out of a PNG, WebP or AVIF header."""
    head = path.read_bytes()[:64]
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        kind = head[12:16]
        if kind == b"VP8X":
            width = int.from_bytes(head[24:27], "little") + 1
            height = int.from_bytes(head[27:30], "little") + 1
            return width, height
        if kind == b"VP8 ":
            return (
                int.from_bytes(head[26:28], "little") & 0x3FFF,
                int.from_bytes(head[28:30], "little") & 0x3FFF,
            )
        raise SystemExit(f"renders.py: unhandled WebP variant {kind!r} in {path}")
    if head[4:8] == b"ftyp":
        # ISOBMFF: the box type is followed by version+flags (4 bytes), then the
        # 32-bit width and height. ``split`` puts the prefix first, so skip it.
        parts = path.read_bytes().split(b"ispe")
        if len(parts) > 1 and len(parts[1]) >= 12:
            return (
                int.from_bytes(parts[1][4:8], "big"),
                int.from_bytes(parts[1][8:12], "big"),
            )
    raise SystemExit(f"renders.py: cannot read image size from {path}")


def version(command: list[str]) -> str:
    out = subprocess.run(command, capture_output=True, text=True, check=False)
    text = (out.stdout or out.stderr).strip().splitlines()
    return text[0].strip() if text else "unknown"


def frames(params: dict) -> list[dict]:
    rows = []
    for width, height in params["renders"]["sizes"]:
        for theme in params["renders"]["themes"]:
            rows.append(
                {
                    "stem": "gremlin-hero-%dx%d-%s" % (width, height, theme),
                    "width": width,
                    "height": height,
                    "theme": theme,
                }
            )
    return rows


def render(blender: str, threads: int, build: Path, params: dict) -> list[dict]:
    rows = frames(params)
    spec = {
        "params": str(HERE / "params.json"),
        "view": params["renders"]["view"],
        "margin": params["renders"]["margin"],
        "frames": [
            {
                "file": row["stem"] + ".png",
                "width": row["width"],
                "height": row["height"],
                "theme": row["theme"],
            }
            for row in rows
        ],
    }
    build.mkdir(parents=True, exist_ok=True)
    spec_path = build / "frames.json"
    spec_path.write_text(json.dumps(spec, indent=1) + "\n")
    subprocess.run(
        [
            blender, "-b", "--factory-startup", "-t", str(threads),
            "-P", str(HERE / "render_hero.py"),
            "--", "--spec", str(spec_path), "--out", str(build),
            "--threads", str(threads),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return rows


def encode(build: Path, rows: list[dict], params: dict) -> list[Path]:
    produced = []
    quality = params["renders"]["quality"]
    for row in rows:
        source = build / (row["stem"] + ".png")
        if not source.is_file():
            raise SystemExit(f"renders.py: blender wrote no render at {source}")
        produced.append(source)
        for fmt in params["renders"]["formats"]:
            if fmt == "png":
                continue
            target = build / (row["stem"] + "." + fmt)
            subprocess.run(
                ["magick", str(source), "-strip", *ENCODERS[fmt](quality[fmt]),
                 str(target)],
                check=True,
            )
            produced.append(target)
    return produced


def manifest_rows(dest: Path, rows: list[dict], params: dict) -> list[dict]:
    out = []
    for row in rows:
        for fmt in params["renders"]["formats"]:
            path = dest / (row["stem"] + "." + fmt)
            width, height = image_size(path)
            if (width, height) != (row["width"], row["height"]):
                raise SystemExit(
                    "renders.py: %s is %dx%d, expected %dx%d"
                    % (path.name, width, height, row["width"], row["height"])
                )
            out.append(
                {
                    "file": path.name,
                    "format": fmt,
                    "theme": row["theme"],
                    "width": width,
                    "height": height,
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
    return out


def build_manifest(rows: list[dict], params: dict, blender: str) -> dict:
    return {
        "about": (
            "Hero plates generated from model/params.json. Regenerate with "
            "`make renders`; never retouch these bytes."
        ),
        "source": {
            "params_sha256": digest(HERE / "params.json"),
            "gremlin_sha256": digest(HERE / "gremlin.py"),
            "render_hero_sha256": digest(HERE / "render_hero.py"),
        },
        "tooling": {
            "blender": version([blender, "--version"]),
            "imagemagick": version(["magick", "--version"]),
            "encoder": {fmt: " ".join(ENCODERS[fmt]("Q")) for fmt in ENCODERS},
        },
        "view": params["renders"]["view"],
        "margin": params["renders"]["margin"],
        "quality": params["renders"]["quality"],
        "renders": rows,
    }


def verify(dest: Path = DEST) -> int:
    """Cheap, blender-free check that the committed plates match the manifest."""
    manifest_path = dest / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"renders.py: no {manifest_path}; run `make renders`")
    manifest = json.loads(manifest_path.read_text())
    failures = 0
    for row in manifest["renders"]:
        path = dest / row["file"]
        if not path.is_file():
            print("  RENDER %s: FAIL missing" % row["file"])
            failures += 1
            continue
        size = image_size(path)
        got = digest(path)
        if size != (row["width"], row["height"]) or got != row["sha256"]:
            print("  RENDER %s: FAIL %dx%d %s != %dx%d %s"
                  % (row["file"], *size, got[:12],
                     row["width"], row["height"], row["sha256"][:12]))
            failures += 1
            continue
        print("  RENDER %-34s %4dx%-4d %-4s %6d B %s ok"
              % (row["file"], row["width"], row["height"], row["format"],
                 row["bytes"], got[:16]))
    if failures:
        raise SystemExit("renders.py: %d render(s) do not match manifest.json"
                         % failures)
    print("renders.py: %d plates match manifest.json, their sizes and formats"
          % len(manifest["renders"]))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", default=str(REPO / "build/renders"))
    parser.add_argument("--dest", default=str(DEST))
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    dest = Path(args.dest)
    if args.verify:
        return verify(dest)

    params = json.loads((HERE / "params.json").read_text())
    rows = render(args.blender, args.threads, Path(args.build), params)
    produced = encode(Path(args.build), rows, params)

    previous = None
    if MANIFEST.is_file():
        previous = {row["file"]: row["sha256"]
                    for row in json.loads(MANIFEST.read_text())["renders"]}
    built = {path.name: digest(path) for path in produced}
    drift = sorted(
        name for name, sha in built.items()
        if previous is not None and previous.get(name) != sha
    )
    if previous is not None and not drift and set(built) == set(previous):
        print(
            "renders.py: reproduced %d/%d plates byte-identically against "
            "manifest.json" % (len(built), len(built))
        )
        # Provenance has to track the sources even when the pixels did not move:
        # a refactor in gremlin.py or render_hero.py must update its pinned hash.
        manifest = build_manifest(manifest_rows(dest, rows, params), params,
                                  args.blender)
        text = json.dumps(manifest, indent=1) + "\n"
        if text != MANIFEST.read_text():
            MANIFEST.write_text(text)
            print("renders.py: refreshed manifest.json provenance "
                  "(source hashes or tooling moved)")
        return 0
    if drift and not args.update:
        raise SystemExit(
            "renders.py: rendered bytes differ from manifest.json (%s). "
            "Re-run with --update only for a deliberate change."
            % "; ".join("%s: %s -> %s" % (name, (previous or {}).get(name, "new")[:12],
                                          built[name][:12]) for name in drift)
        )

    dest.mkdir(parents=True, exist_ok=True)
    for path in produced:
        (dest / path.name).write_bytes(path.read_bytes())
    manifest = build_manifest(manifest_rows(dest, rows, params), params, args.blender)
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n")
    for row in manifest["renders"]:
        print("  RENDER %-34s %4dx%-4d %-4s %6d B %s"
              % (row["file"], row["width"], row["height"], row["format"],
                 row["bytes"], row["sha256"][:16]))
    print("renders.py: wrote %d plates and manifest.json to %s"
          % (len(manifest["renders"]), dest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
