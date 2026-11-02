"""The one place the org checkers talk to GitHub.

`check-repo-metadata.py` and `check-repo-settings.py` both need the same three
things: run `gh api`, parse the JSON, and tell "the API said no" apart from a
crash. Duplicating that block is what the jscpd ratchet rejects, so it lives
here — stdlib only, no direct HTTP, no browser.
"""

from __future__ import annotations

import json
import subprocess


class ApiError(RuntimeError):
    """`gh` failed in a way the caller cannot treat as data."""


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ApiError(result.stderr.strip() or f"gh {' '.join(args)} failed")
    return result.stdout


def api_get(path: str) -> object:
    return json.loads(gh("api", path))


def api_optional(path: str) -> tuple[object | None, str]:
    """Return (payload, error); a 403/404 is data here, not a crash."""
    result = subprocess.run(
        ["gh", "api", path], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return json.loads(result.stdout), ""
    return None, result.stderr.strip()
