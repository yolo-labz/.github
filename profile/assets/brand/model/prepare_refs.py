#!/usr/bin/env python3
"""Prepare immutable local references; never calls a browser or image model."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BRAND = REPO / "profile/assets/brand"
BASE = "64880882f235922007dd22a0cdb22c7ea5f09f83"
ANCHOR_COMMIT = "637a7fbd3f47127f157d0e0dbbccc807bff57c87"
ANCHOR_PATH = "profile/assets/brand/exploration/2026-09-28/gremlin-anchor.png"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path, source):
    data = {
        "kind": "reference",
        "classification": "exploration-not-approved-master",
        "image": path.relative_to(HERE).as_posix(),
        "sha256": digest(path),
        "source": source,
        "prompt": None,
        "prompt_sha256": None,
        "note": "Prepared/imported reference, not a new S1 generation",
    }
    path.with_suffix(".provenance.json").write_text(json.dumps(data, indent=2) + "\n")


def prepare():
    refs = HERE / "refs"
    refs.mkdir(exist_ok=True)
    sources = []
    svg_paths = sorted((BRAND / "mascot").glob("*.svg"))
    svg_paths += sorted(BRAND.glob("logo-mark-*.svg"))
    for path in svg_paths:
        sources.append(
            {
                "path": path.relative_to(REPO).as_posix(),
                "commit": BASE,
                "sha256": digest(path),
            }
        )
    (refs / "sources.json").write_text(json.dumps(sources, indent=2) + "\n")
    panels = []
    for name in ("model-sheet", "hero", "idle", "working", "asleep"):
        source = BRAND / "mascot" / f"gremlin-{name}.png"
        target = refs / source.name
        shutil.copyfile(source, target)
        reference(target, {"commit": BASE, "path": source.relative_to(REPO).as_posix()})
        panels.append((target, f"CANONICAL SVG KIT / {name}"))
    anchor = refs / "anchor-2026-09-28.png"
    anchor.write_bytes(
        subprocess.check_output(
            ["git", "show", f"{ANCHOR_COMMIT}:{ANCHOR_PATH}"], cwd=REPO
        )
    )
    assert (
        digest(anchor)
        == "dcd882cb9d7f99316f0278d03c172a9f14135c195efe67556d451a9bd172baeb"
    )
    reference(anchor, {"commit": ANCHOR_COMMIT, "path": ANCHOR_PATH})
    panels.append((anchor, "SECONDARY ATTITUDE ONLY / NOT GEOMETRY"))
    command = ["magick", "-limit", "thread", "1"]
    for image, label in panels:
        command += [
            "(",
            str(image),
            "-resize",
            "720x480",
            "-background",
            "#1e1e2e",
            "-gravity",
            "center",
            "-extent",
            "768x560",
            "-font",
            "DejaVu-Sans",
            "-fill",
            "#cdd6f4",
            "-pointsize",
            "20",
            "-gravity",
            "south",
            "-annotate",
            "+0+14",
            label,
            ")",
        ]
    board = refs / "canonical-reference-board.png"
    command += ["-background", "#1e1e2e", "-append", str(board)]
    subprocess.run(command, check=True)
    reference(
        board,
        {
            "method": "deterministic vertical composition; no image generation",
            "recipe": "prepare_refs.py",
            "inputs": [
                {"image": p.relative_to(HERE).as_posix(), "sha256": digest(p)}
                for p, _label in panels
            ],
        },
    )
    print(
        "PASS: SVG source hashes, six imported references and labelled reference board"
    )


if __name__ == "__main__":
    prepare()
