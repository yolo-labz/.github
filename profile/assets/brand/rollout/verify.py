#!/usr/bin/env python3
"""Verify saved render evidence offline, without attaching to any browser.

Two questions, kept apart because only one is an error:

* integrity -- do checks.json, preview.html, renders.json and the four screenshots
  agree with each other and with their own hashes? A failure here is a bug or
  tampering, so it always exits 1.
* freshness -- is that evidence bound to the README as it is now? Re-rendering
  needs the server browser fleet (see README.md), which CI cannot do, so drift is
  reported, not failed: a warning by default, exit 3 with --require-fresh (the
  scheduled run uses it so the drift stays visible until someone re-renders).
"""

import argparse
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STALE = 3


def verify():
    """Integrity of the saved evidence. Returns the profile hash it is bound to."""
    checks = json.loads((HERE / "checks.json").read_text())
    bound = checks["profile_sha256"]
    assert checks["mode"] == "exploration-integrated"
    assert f'content="{bound}"' in (HERE / "preview.html").read_text(), (
        "preview.html is bound to a different profile"
    )
    results = json.loads((HERE / "renders.json").read_text())
    assert len(results) == 4
    assert {(r["viewport"], r["theme"]) for r in results} == {
        (1280, "light"),
        (1280, "dark"),
        (360, "light"),
        (360, "dark"),
    }
    # Receipts written before listed_projects existed counted every listed project
    # as a flagship, so fall back to that field for them.
    expected_links = checks.get("listed_projects", checks["flagships"])
    for result in results:
        assert result["profile_sha256"] == bound, "Render receipts disagree"
        assert result["mode"] == checks["mode"]
        assert result["contentWidth"] <= result["viewport"]
        assert result["imageFailureNavigation"] == "pass"
        assert len(result["links"]) == expected_links
        assert all(img["loaded"] and img["alt"] for img in result["images"])
        assert result["images"][0]["source"] == f"logo-wordmark-{result['theme']}.svg"
        assert any(img["source"] == "gremlin-hero-gpt-887x640.webp" for img in result["images"])
        name = f"exploration-integrated-{result['viewport']}-{result['theme']}.png"
        assert result["screenshot"] == name
        png = (HERE / name).read_bytes()
        assert hashlib.sha256(png).hexdigest() == result["screenshot_sha256"]
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", png[16:24])
        # Chrome full-page capture excludes its 15px vertical scrollbar.
        assert width == result["contentWidth"] and height >= 960
    return bound


def freshness(bound):
    """None when the evidence is bound to the current README, else a message."""
    current = hashlib.sha256((ROOT / "profile/README.md").read_bytes()).hexdigest()
    if current == bound:
        return None
    return (
        f"saved renders are bound to README {bound[:12]} but profile/README.md is "
        f"{current[:12]}; re-render (rollout/README.md, 'Fresh preview/render': check.py --preview, "
        "then render.py)"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-fresh",
        action="store_true",
        help=f"exit {STALE} when the evidence is not bound to the current README",
    )
    args = parser.parse_args(argv)
    bound = verify()
    print("PASS: four saved render hashes, PNG dimensions and receipt agreement")
    stale = freshness(bound)
    if stale is None:
        print("FRESH: evidence is bound to the current profile/README.md")
        return 0
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning title=Rollout render evidence is stale::{stale}")
    print(f"STALE: {stale}")
    return STALE if args.require_fresh else 0


if __name__ == "__main__":
    sys.exit(main())
