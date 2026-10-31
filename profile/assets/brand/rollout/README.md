# Front-page exploration integration evidence

This is a draft profile proposal, not the live organization page or an approved
brand master. Existing vector wordmarks remain unchanged. The exact GPT wide
hero and sanitized lineage are in `art-provenance.json`; copy is pinned to #10.

## Offline acceptance (no browser)

From the repository root:

```sh
python3 profile/assets/brand/rollout/check.py
python3 profile/assets/brand/rollout/verify.py
python3 -m unittest discover -s profile/assets/brand/rollout -p 'test_*.py' -v
ruff check profile/assets/brand/rollout/*.py
ruff format --check profile/assets/brand/rollout/*.py
```

The gate checks six flagship destinations and caveats, meaningful alt text,
local assets, immutable vector wordmarks, exact art checksum and source evidence.
Saved renders are bound to the profile hash. Regression tests reject modified
screenshots, stale source and a missing viewport/theme combination.

## Fresh preview/render (existing server fleet only)

Read the current browser-automation procedure first and confirm the dedicated
anonymous identity `brave-search` is ready through the server toolset.
No local browser, direct HTTP link probes, browser restart or account mutation.

```sh
# GitHub's Markdown API sanitizes the README; this does not publish it.
python3 profile/assets/brand/rollout/check.py --preview

# Existing installed driver and supported fleet attach; no browser launch.
PYTHONPATH=/home/notroot/Documents/Code/personal/web-automation \
  browser-patchright profile/assets/brand/rollout/render.py
```

`render.cjs` is only a compatibility entrypoint to that Python runner.
Each render embeds exact worktree asset bytes into the owned blank page; no
network fonts/images or account material. The surrounding CSS approximates
GitHub's content column, not its full live UI.

**Maintenance caveat:** the canonical attach helper auto-sanitized one frozen
target on the recorded run. Its cleanup behavior is not owned by this repo.
Do not rerun under an absolute no-foreign-target-mutation requirement without
a separately verified compatible helper. No further browser calls were made
after observing the side effect; offline verification remains safe.

## Evidence

- `checks.json`: exact profile hash, links and asset checks.
- `preview.html`: sanitized GitHub Markdown in the local preview shell.
- `renders.json`: server Chrome version, identity, image decoding, actual
  widths, screenshot hashes and image-failure navigation.
- `exploration-integrated-{1280,360}-{light,dark}.png`: four real server renders.
  Full-page PNGs exclude Chrome's 15px vertical scrollbar, while the requested
  viewports are exactly 1280/360.
- `render-run.json`: sanitized runtime outcome and helper side effect.
- Historical `draft-*.png`: placeholder-only renders, not current acceptance.

Live main asset URLs are not expected to resolve for unmerged additions.
No new HTTP availability check is claimed; prior link receipts are historical.
No self-merge, publication or artwork approval follows from render success.
