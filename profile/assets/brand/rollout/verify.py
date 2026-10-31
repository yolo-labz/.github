#!/usr/bin/env python3
"""Verify saved render evidence offline, without attaching to any browser."""

import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def verify():
    profile_sha = hashlib.sha256((ROOT / "profile/README.md").read_bytes()).hexdigest()
    checks = json.loads((HERE / "checks.json").read_text())
    assert checks["profile_sha256"] == profile_sha, "Stale profile checks"
    assert checks["mode"] == "exploration-integrated"
    assert f'content="{profile_sha}"' in (HERE / "preview.html").read_text()
    results = json.loads((HERE / "renders.json").read_text())
    assert len(results) == 4
    assert {(r["viewport"], r["theme"]) for r in results} == {
        (1280, "light"),
        (1280, "dark"),
        (360, "light"),
        (360, "dark"),
    }
    for result in results:
        assert result["profile_sha256"] == profile_sha, "Stale render receipt"
        assert result["mode"] == checks["mode"]
        assert result["contentWidth"] <= result["viewport"]
        assert result["imageFailureNavigation"] == "pass"
        assert len(result["links"]) == 6
        assert all(img["loaded"] and img["alt"] for img in result["images"])
        assert result["images"][0]["source"] == f"logo-wordmark-{result['theme']}.svg"
        assert any(img["source"] == "gremlin-wide-hero.png" for img in result["images"])
        name = f"exploration-integrated-{result['viewport']}-{result['theme']}.png"
        assert result["screenshot"] == name
        png = (HERE / name).read_bytes()
        assert hashlib.sha256(png).hexdigest() == result["screenshot_sha256"]
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", png[16:24])
        # Chrome full-page capture excludes its 15px vertical scrollbar.
        assert width == result["contentWidth"] and height >= 960
    print("PASS: four saved render hashes, PNG dimensions and exact profile binding")


if __name__ == "__main__":
    verify()
