#!/usr/bin/env python3
"""Render exact worktree assets on an owned page in the existing server fleet."""

import base64
import hashlib
import json
import re
from pathlib import Path

from lib import interactive

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDENTITY = "brave-search"


def embedded_preview(checks):
    profile = (ROOT / "profile/README.md").read_bytes()
    assert hashlib.sha256(profile).hexdigest() == checks["profile_sha256"], (
        "Stale checks"
    )
    html = (HERE / "preview.html").read_text()
    assert f'content="{checks["profile_sha256"]}"' in html, "Stale preview"
    assets = {}
    for name in set(re.findall(r'(?:src|srcset)="(profile/[^"?#]+)"', html)):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), "Invalid preview asset"
        mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
        data = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
        assets[data] = path.name
        html = html.replace(f'="{name}"', f'="{data}"')
    assert assets, "No embedded image assets"
    return html, assets


def render():
    checks = json.loads((HERE / "checks.json").read_text())
    proof = json.loads((HERE / "art-provenance.json").read_text())
    assert checks["mode"] == "exploration-integrated"
    html, assets = embedded_preview(checks)
    results = []
    # The renderer touches only its yielded page; helper maintenance is separate.
    # See render-run.json for the observed pre-attach frozen-target cleanup.
    with interactive.attach(IDENTITY, start_if_down=False, timeout_ms=30000) as (
        _pw,
        browser,
        _context,
        page,
    ):
        page.set_default_timeout(15000)
        page.route("**/*", lambda route: route.abort())
        for theme in ("light", "dark"):
            for width in (1280, 360):
                page.set_viewport_size({"width": width, "height": 960})
                page.emulate_media(color_scheme=theme)
                page.set_content(html, wait_until="load")
                page.evaluate("() => document.fonts.ready")
                page.locator("main img").evaluate_all(
                    "images => Promise.all(images.map(img => img.decode()))"
                )
                evidence = page.evaluate(
                    """assets => ({
                      viewport: innerWidth,
                      contentWidth: document.documentElement.scrollWidth,
                      images: [...document.querySelectorAll('main img')].map(img => ({
                        alt: img.alt, source: assets[img.currentSrc],
                        loaded: img.complete && img.naturalWidth > 0,
                        naturalWidth: img.naturalWidth,
                        displayedWidth: img.getBoundingClientRect().width,
                      })),
                      links: [...document.querySelectorAll('main li strong a')].map(a => a.href),
                    })""",
                    assets,
                )
                assert evidence["contentWidth"] <= width, "Horizontal overflow"
                assert all(img["loaded"] and img["alt"] for img in evidence["images"])
                assert evidence["images"][0]["source"] == f"logo-wordmark-{theme}.svg"
                assert any(img["source"] == proof["file"] for img in evidence["images"])
                assert len(evidence["links"]) == 6, "Missing flagship navigation"
                screenshot = f"exploration-integrated-{width}-{theme}.png"
                page.screenshot(path=str(HERE / screenshot), full_page=True)
                page.locator("main img").evaluate_all(
                    "images => images.forEach(img => img.remove())"
                )
                assert page.locator("main li strong a").count() == 6
                assert page.locator("main h1").is_visible()
                results.append(
                    {
                        "theme": theme,
                        "mode": checks["mode"],
                        "profile_sha256": checks["profile_sha256"],
                        "renderer": "existing NixOS server fleet via interactive.attach",
                        "identity": IDENTITY,
                        "browser_version": browser.version,
                        "network_assets": "none; exact worktree image bytes embedded",
                        **evidence,
                        "screenshot": screenshot,
                        "screenshot_sha256": hashlib.sha256(
                            (HERE / screenshot).read_bytes()
                        ).hexdigest(),
                        "imageFailureNavigation": "pass",
                    }
                )
    (HERE / "renders.json").write_text(json.dumps(results, indent=2) + "\n")
    print(
        "PASS: server-fleet 1280/360 light/dark, decoded exploration art, no overflow, image-failure navigation"
    )


if __name__ == "__main__":
    render()
