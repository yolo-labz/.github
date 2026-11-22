# Repository headers

Social preview images for the 15 yolo-labz repositories. Each README of a
project that shows the project card links to its own PNG here, pinned to a
commit SHA.

## Files

- `<repository>.png`: 1280 × 640 PNG, under 1 MB, one per repository.
- `manifest.json`: per repository, the text shown, the GitHub description,
  the line breaks and the layout checks that passed.
- `render-social-previews.py`: renders all 15 images and the manifest.
- `assets/icons/`: one SVG icon per repository (input).
- `assets/gremlin-matte.png`: the gremlin mark (input).

## Layout rules

- Text block: left column, up to 3 lines at 28 px, 560 px wide.
- The description is shown in full when it fits. Otherwise the script cuts
  at a clause boundary. It never adds an ellipsis.
- The gremlin sits on the right. Text never overlaps it.
- The text stays at least 24 px above the bar at the bottom.

## Render again

Needs ImageMagick 7 (`magick`), `rsvg-convert`, an authenticated `gh` CLI
and the Inter font.

```bash
cd profile/assets/brand/repo-headers
python3 render-social-previews.py --out .
```

The script exits non-zero when a layout check fails. Check the new
`manifest.json` before you commit the PNGs.

## Use in a README

```html
<img src="https://raw.githubusercontent.com/yolo-labz/.github/<commit-sha>/profile/assets/brand/repo-headers/<repository>.png" alt="<repository>: <description>" width="100%">
```

Use the commit SHA in the URL, not `main`. A SHA stays fixed when `main` moves.

## Upload

The GitHub social preview setting has no API. Upload each PNG by hand in
each repository's Settings, under Social preview.
