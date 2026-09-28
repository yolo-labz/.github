# Front-page integration evidence

This directory belongs to the frontpage seat. Canonical logo and mascot masters
one level up remain unchanged. New GPT art, if present, is a **labelled exploration
integrated into a profile proposal**, not an approved replacement brand master.

## Reproduce

From the repository root:

```sh
# Requires Python 3 + gh. Online mode reads public link destinations and asks
# GitHub's Markdown API to render the current README; it publishes nothing.
python3 profile/assets/brand/rollout/check.py --online --preview

# Requires an already-installed Playwright and Chrome. No package install needed.
# On this host Playwright is available in the Proso workspace:
NODE_PATH=/home/notroot/Documents/Code/personal/proso/node_modules \
  node profile/assets/brand/rollout/render.cjs
```

For a temporary art slot only, add `--draft` to `check.py`. **That is not final-art
acceptance.** Default checking fails if the placeholder is still present.
`CHROME_BIN` can select an installed Chrome executable. Headless Chrome uses an
isolated ephemeral browser context, never the shared browser or account profiles.

## What the checks prove

- Six flagship destinations, no blanket compliance/SLSA claims, image alt text,
  local asset existence, existing outlined wordmarks unchanged byte-for-byte.
- Final art checksum and p9 provenance sidecar presence; human inspection of the
  producer evidence is still required (a JSON field cannot prove generation).
- Optional HTTP GET validation of every Markdown link; redirects are recorded.
- GitHub-sanitized GFM rendered in a local approximation of its content column.
  Absolute production asset URLs are mapped to the exact worktree files, so
  unmerged art can be previewed without publishing it to the org page.
- Actual decoded images, theme-specific wordmark selection, six text links,
  no horizontal overflow at 1280/360px, and navigation surviving image removal.
- SHA-256 binds checks and preview to the exact profile; stale previews fail.

## Output files

- `checks.json`: local and optional link receipts (scope labelled draft/final-art).
- `preview.html`: GitHub-rendered README in `preview-template.html`'s local shell.
- `renders.json`: viewport, loaded image names/dimensions, navigation and screenshots.
- `{draft,final-art}-{1280,360}-{light,dark}.png`: actual headless browser renders.
- `art-provenance.json` and the cited image: appear **only after** usable p9 art.

These renders are not live GitHub org-page captures and do not assert GitHub's
exact surrounding UI. Production asset URLs resolve only after authorized merge.
The draft prefix remains visible on any placeholder-only render.
