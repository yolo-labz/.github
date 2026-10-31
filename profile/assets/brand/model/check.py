#!/usr/bin/env python3
"""Fail-closed model-sheet/source/provenance/privacy acceptance; entirely offline."""

import argparse
import hashlib
import json
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BRAND = REPO / "profile/assets/brand"
PRIVATE_URL = re.compile(
    rb"https?://(?:chatgpt\.com/(?:c|g)/|[^\s]*oaiusercontent\.com)"
    rb"|[?&](?:sig|token|signature)=",
    re.IGNORECASE,
)
SHEETS = ("turnaround", "expressions", "poses", "hands-keyboard", "colour-material")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(name):
    path = (HERE / name).resolve()
    assert path.is_relative_to(HERE) and ".private" not in path.parts, (
        "Unsafe public path"
    )
    assert path.is_file(), f"Missing: {name}"
    return path


def css_value(css, selector, property_name):
    pattern = rf"\.{selector}\s*\{{[^}}]*\b{property_name}:\s*(#[0-9a-f]{{6}})"
    return re.search(pattern, css, re.IGNORECASE).group(1).lower()


def source_palette():
    hero = (BRAND / "mascot/gremlin-hero.svg").read_text().split("@media", 1)
    asleep = (BRAND / "mascot/gremlin-asleep.svg").read_text().split("@media", 1)
    result = {}
    for i, theme in enumerate(("mocha", "latte")):
        values = {
            role: css_value(hero[i], role, "fill")
            for role in ("skin", "pale", "dark", "node", "key")
        }
        values["keyboard_detail"] = css_value(hero[i], "kbd", "stroke")
        values["support"] = css_value(asleep[i], "sub", "stroke")
        mark = ET.parse(BRAND / f"logo-mark-{('dark', 'light')[i]}.svg")
        values["background"] = mark.getroot().find("{*}rect").attrib["fill"].lower()
        result[theme] = values
    return result


def check_spec(spec):
    assert spec["classification"] == "exploration-not-approved-master"
    assert spec["palette"] == source_palette(), "SPEC palette mismatch against SVG kit"
    content = local("SPEC.md").read_text()
    assert all(
        value in content for row in spec["palette"].values() for value in row.values()
    )
    tree = ET.parse(BRAND / "mascot/gremlin-model-sheet.svg")
    head = next(e for e in tree.findall(".//{*}ellipse") if e.get("class") == "skin")
    unit = 2 * float(head.attrib["ry"])
    expected = {
        "unit": unit,
        "head_width": 2 * float(head.attrib["rx"]) / unit,
        "head_height": 1,
        "ear_span": 196 / unit,
        "ear_tip_x": 98 / unit,
        "ear_tip_y": -68 / unit,
        "eye_radius": 11 / unit,
        "pupil_radius": 4.5 / unit,
        "torso_width": 88 / unit,
        "torso_height": 52 / unit,
        "keyboard_width": 180 / unit,
    }
    assert spec["head_units"] == expected, "SPEC proportion mismatch"
    assert spec["counts"] == {
        "ears": 2,
        "eyes": 2,
        "fangs": 3,
        "claws_per_hand": 3,
        "hands": 2,
        "feet": 2,
        "tails": 1,
    }
    assert spec["sheets"] == list(SHEETS) and spec["maximum_sends"] == 8
    assert spec["line_weights"] == {
        "head": 6 / unit,
        "brows": 5 / unit,
        "claws": 3.5 / unit,
        "keyboard": 2.5 / unit,
        "output_brackets": 4 / unit,
    }


def check_references():
    prompts = json.loads(local("prompts/manifest.json").read_text())
    assert len(prompts) == len(SHEETS)
    for prompt in prompts:
        assert digest(local(prompt["prompt"])) == prompt["prompt_sha256"]
        assert digest(local(prompt["reference"])) == prompt["reference_sha256"]
        text = local(prompt["prompt"]).read_text()
        assert "PRESERVE EXACTLY" in text and "CHANGE ONLY" in text
    for source in json.loads(local("refs/sources.json").read_text()):
        path = (REPO / source["path"]).resolve()
        assert path.is_relative_to(REPO) and digest(path) == source["sha256"]
        original = subprocess.check_output(
            ["git", "show", f"{source['commit']}:{source['path']}"], cwd=REPO
        )
        assert hashlib.sha256(original).hexdigest() == source["sha256"]
    for image in HERE.rglob("*.png"):
        if ".private" in image.parts:
            continue
        record = json.loads(
            local(image.with_suffix(".provenance.json").relative_to(HERE)).read_text()
        )
        assert local(record["image"]) == image.resolve()
        assert digest(image) == record["sha256"], f"Image hash mismatch: {image.name}"
        assert record["kind"] in {"reference", "model-sheet"}, (
            "Unknown image provenance kind"
        )
        if record["kind"] == "reference":
            source = record["source"]
            if "commit" in source:
                raw = subprocess.check_output(
                    ["git", "show", f"{source['commit']}:{source['path']}"], cwd=REPO
                )
                assert hashlib.sha256(raw).hexdigest() == record["sha256"]
            else:
                for item in source["inputs"]:
                    assert digest(local(item["image"])) == item["sha256"]


def check_privacy():
    for path in HERE.rglob("*"):
        if not path.is_file() or ".private" in path.parts:
            continue
        assert not PRIVATE_URL.search(path.read_bytes()), f"Private URL: {path.name}"
    tracked = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=REPO)
        .decode()
        .split("\0")
    )
    assert not any(".private" in Path(name).parts for name in tracked), (
        "Private receipt tracked"
    )
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(HERE / ".private" / "sentinel")],
        cwd=REPO,
        check=False,
    )
    assert result.returncode == 0, "Private receipts must stay ignored"


def check_sheets():
    for name in SHEETS:
        image = local(f"{name}.png")
        record = json.loads(local(f"{name}.provenance.json").read_text())
        assert record["kind"] == "model-sheet"
        assert record["classification"] == "exploration-not-approved-master"
        assert record["identity"] == "chatgpt-c"
        assert (
            record["receipt"]["status"] == "ok"
            and record["receipt"]["send_confirmed"] is True
        )
        assert record["timestamp"] and record["model"]["evidence"]
        assert re.fullmatch(r"[0-9a-f]{64}", record["receipt_sha256"])
        assert digest(image) == record["sha256"]
        prompt = local(record["prompt"])
        assert digest(prompt) == record["prompt_sha256"]
        assert (
            "PRESERVE EXACTLY" in prompt.read_text()
            and "CHANGE ONLY" in prompt.read_text()
        )
        assert record["references"], "Reference-anchored generation required"
        for ref in record["references"]:
            assert digest(local(ref["image"])) == ref["sha256"]
        png = image.read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", png[16:24])
        assert min(width, height) >= 512
        assert [width, height] == [record["width"], record["height"]]
        assert record["receipt"]["bytes"] == len(png)
    status = json.loads(local("generation-status.json").read_text())
    assert status["generated_images"] == 5 and 0 < status["sends_used"] <= 8


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-only", action="store_true")
    parser.add_argument("--spec-json", default="spec.json")
    args = parser.parse_args()
    spec = json.loads(local(args.spec_json).read_text())
    check_spec(spec)
    check_privacy()
    check_references()
    if args.spec_only:
        print(
            "PASS: source palette, proportions, reference provenance and privacy; NOT sheet delivery"
        )
    else:
        check_sheets()
        print(
            "PASS: five reference-anchored GPT model sheets and reproducible provenance"
        )


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, OSError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}")
