#!/usr/bin/env python3
"""Check the org profile. --draft permits the labelled art slot, never final acceptance."""

import argparse
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = "https://raw.githubusercontent.com/yolo-labz/.github/main/"


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            assert attrs.get("alt", "").strip(), "Every image needs meaningful alt text"
            assert 0 < int(attrs["width"]) <= 640, "Hero/wordmark must be restrained"
            self.paths.append(attrs["src"])
        elif tag == "source":
            self.paths.append(attrs["srcset"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", action="store_true")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Render README through GitHub Markdown API",
    )
    args = parser.parse_args()
    text = (ROOT / "profile/README.md").read_text()
    flagships = re.findall(r"\*\*\[([^]]+)\]\((https://[^)]+)\)\*\*", text)
    expected = {
        "wa",
        "chrome-bridge",
        "claude-mac-chrome",
        "fand",
        "kokoro-speakd",
        "anthropic-throttle-proxy",
    }
    assert len(flagships) == 6 and {name for name, _ in flagships} == expected
    assert all(url == f"https://github.com/yolo-labz/{name}" for name, url in flagships)
    for qualifier in (
        "unofficial",
        "macOS only",
        "forced-minimum",
        "default is off",
        "unpacked-extension-capable",
        "Queued does not mean audible",
    ):
        assert qualifier in text, f"Missing claim qualifier: {qualifier}"
    assert not re.search(
        r"compliance-grade|SLSA|Apache-2.0 \+ MIT throughout", text, re.IGNORECASE
    )
    assert not re.search(r"<table|<style|<script|style=", text, re.IGNORECASE), (
        "GitHub-safe content only"
    )
    images = Images()
    images.feed(text)
    for url in images.paths:
        assert url.startswith(RAW), f"Unexpected image origin: {url}"
        path = ROOT / url.removeprefix(RAW)
        assert path.resolve().is_relative_to(ROOT), "Asset escapes repository"
        assert path.is_file() and path.stat().st_size, f"Missing asset: {path}"
    for theme in ("light", "dark"):
        path = f"profile/assets/brand/logo-wordmark-{theme}.svg"
        current = (ROOT / path).read_bytes()
        original = subprocess.check_output(["git", "show", f"6488088:{path}"], cwd=ROOT)
        assert current == original, "Existing outlined wordmark must stay unchanged"
        svg = ET.fromstring(current)
        assert not svg.findall(".//{http://www.w3.org/2000/svg}text"), (
            "Wordmark must remain outlined"
        )
    placeholder = "temporary art placeholder" in text
    if placeholder:
        assert args.draft, "BLOCKED: final GPT artwork not integrated"
        assert "No final GPT artwork is present" in text
    else:
        proof = json.loads((HERE / "art-provenance.json").read_text())
        image = HERE / proof["file"]
        assert image.resolve().is_relative_to(HERE)
        assert hashlib.sha256(image.read_bytes()).hexdigest() == proof["sha256"]
        assert (
            proof["producer"] == "p9" and proof["status"] == "gpt-generated-exploration"
        )
        assert re.fullmatch(r"[0-9a-f]{40}", proof["source_commit"])
        assert proof["generation_evidence"].startswith(
            f"https://github.com/yolo-labz/.github/blob/{proof['source_commit']}/"
        )
        generation = proof["generation_record"]
        assert generation["sha256"] == proof["sha256"]
        assert generation["image"] == proof["file"]
        assert generation["classification"] == "exploration-not-approved-master"
        assert generation["receipt"]["status"] == "ok"
        assert generation["receipt"]["send_confirmed"] is True
        assert generation["reference"] == "gremlin-anchor.png"
        assert generation["receipt"]["bytes"] == image.stat().st_size
        assert proof["copy_source_commit"] == "fb4a5570fade07e9ea97fc85695fe95e22bb7a95"
        assert f"profile/assets/brand/rollout/{proof['file']}" in text
        assert "GPT-generated" in text and "exploration" in text
        assert "not an approved brand master" in text
    links = sorted(set(re.findall(r"\]\((https://[^)]+)\)", text)))
    receipt = {
        "mode": "draft" if placeholder else "exploration-integrated",
        "assets": len(images.paths),
        "flagships": 6,
        "links": links,
        "profile_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }
    if args.preview:
        payload = json.dumps(
            {"text": text, "mode": "gfm", "context": "yolo-labz/.github"}
        )
        html = subprocess.check_output(
            ["gh", "api", "markdown", "--input", "-"],
            input=payload,
            text=True,
            cwd=ROOT,
        )
        html = html.replace(RAW, "")
        template = (HERE / "preview-template.html").read_text()
        assert template.count("<!-- README -->") == 1
        template = template.replace("<!-- PROFILE HASH -->", receipt["profile_sha256"])
        (HERE / "preview.html").write_text(template.replace("<!-- README -->", html))
    (HERE / "checks.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
