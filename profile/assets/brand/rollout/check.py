#!/usr/bin/env python3
"""Check the org profile README against the flagship table and the served hero."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = "https://raw.githubusercontent.com/yolo-labz/.github/main/"
HERO = "gremlin-hero-887x640.webp"
BOLD_LINK_RE = re.compile(r"\*\*\[([^]]+)\]\((https://[^)]+)\)\*\*")

sys.path.insert(0, str(ROOT / "scripts"))
from flagships import CLAIMS_DOC, flagship_sentences


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


def flagship_contract(text, doc):
    """README entries vs the flagship table in docs/brand-positioning.md.

    The doc is the single authority for which repositories are flagships, so no
    count or name list lives here: every flagship must be listed once and link to
    its own repository. Other bold project links are allowed (the doc lets the
    profile list a non-flagship outside the flagship headings) but must link to a
    yolo-labz repository of the same name. Returns (flagship names, listed names).
    """
    flagships = sorted(flagship_sentences(doc))
    assert flagships, f"No flagship table found in {doc}"
    entries = BOLD_LINK_RE.findall(text)
    listed = [name for name, _ in entries]
    assert len(set(listed)) == len(listed), "A project is listed twice"
    missing = sorted(set(flagships) - set(listed))
    assert not missing, f"Flagships missing from the profile: {missing}"
    for name, url in entries:
        assert url == f"https://github.com/yolo-labz/{name}", (
            f"{name} must link to its own repository, got {url}"
        )
    return flagships, listed


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    text = (ROOT / "profile/README.md").read_text()
    flagships, listed = flagship_contract(text, ROOT / CLAIMS_DOC)
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
    served = json.loads((HERE.parent / "hero/manifest.json").read_text())
    hero = next(f for f in served["files"] if f["file"] == HERO)
    assert (
        hashlib.sha256((HERE.parent / "hero" / HERO).read_bytes()).hexdigest()
        == hero["sha256"]
    )
    assert f"profile/assets/brand/hero/{HERO}" in text
    assert served["alt"]["hero"] in text, "Hero alt text must match the published one"
    links = sorted(set(re.findall(r"\]\((https://[^)]+)\)", text)))
    receipt = {
        "assets": len(images.paths),
        "flagships": len(flagships),
        "listed_projects": len(listed),
        "links": links,
        "profile_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
