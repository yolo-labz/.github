#!/usr/bin/env python3
"""Offline provenance/privacy gate; never calls a browser or image generator."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
IDS = ("01-anchor", "02-wide-hero", "03-square-avatar")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(name):
    path = (ROOT / name).resolve()
    assert path.is_relative_to(ROOT), f"Out-of-scope path: {name}"
    assert ".private" not in path.parts, "Public provenance references private data"
    assert path.is_file(), f"Missing: {name}"
    return path


def check():
    receipts = {}
    for asset_id in IDS:
        data = json.loads(local(f"{asset_id}.provenance.json").read_text())
        receipts[asset_id] = data
        image, prompt, ref = (local(data[k]) for k in ("image", "prompt", "reference"))
        for key, path in (
            ("sha256", image),
            ("prompt_sha256", prompt),
            ("reference_sha256", ref),
        ):
            assert sha(path) == data[key], f"Hash mismatch: {path.name}"
        assert data["identity"] == "chatgpt-c"
        assert data["tool"] == "gpt-image (ChatGPT web UI)"
        assert data["classification"] == "exploration-not-approved-master"
        assert data["receipt"]["status"] == "ok"
        assert data["receipt"]["send_confirmed"] is True
        assert data["receipt"]["bytes"] == image.stat().st_size
        assert data["model"]["evidence"], "Model observation must be explicit"
        measured = subprocess.check_output(
            ["magick", "identify", "-format", "%w %h", str(image)], text=True
        ).split()
        assert list(map(int, measured)) == [data["width"], data["height"]]
        assert min(data["width"], data["height"]) >= 512
        if asset_id != "01-anchor":
            assert data["reference"] == receipts["01-anchor"]["image"]
            assert data["reference_sha256"] == receipts["01-anchor"]["sha256"]
            assert "PRESERVE EXACTLY" in prompt.read_text()
            assert "CHANGE ONLY" in prompt.read_text()
    for source in json.loads(local("refs/sources.json").read_text()):
        path = (REPO / source["path"]).resolve()
        assert path.is_relative_to(REPO) and sha(path) == source["sha256"]
    assert local("contact-sheet.png").stat().st_size > 1000
    public = [p for p in ROOT.rglob("*") if p.is_file() and ".private" not in p.parts]
    forbidden = re.compile(
        # profile-check: allow-private-pattern — this regex is the scanner, not a leak.
        r"https?://(?:chatgpt\.com/(?:c|g)/|[^\s]*oaiusercontent\.com)|[?&](?:sig|token|signature)=",
        re.IGNORECASE,
    )
    for path in public:
        if path.suffix in {".md", ".txt", ".json", ".html"}:
            assert not forbidden.search(path.read_text()), f"Private URL: {path.name}"
    tracked = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=REPO)
        .decode()
        .split("\0")
    )
    assert not any(".private" in Path(name).parts for name in tracked)
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(ROOT / ".private" / "privacy-sentinel")],
        cwd=REPO,
        check=False,
    )
    assert ignored.returncode == 0, "Private receipts must remain ignored"
    status = json.loads(local("generation-status.json").read_text())
    assert status["status"] == "complete"
    assert status["image_sends"] == status["generated_images"] == len(IDS)
    print(
        "PASS: 3 confirmed images; hashes, anchor lineage, dimensions and public URL hygiene"
    )


if __name__ == "__main__":
    check()
