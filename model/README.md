# Gremlin model — the mascot as reproducible code

The programming gremlin, rebuilt from source. Nothing here is a hand-edited
binary: `model/params.json` is the single source of truth and both outputs — the
Blender turnaround and the flat vector avatar — are generated from it.

```bash
make model      # render + regenerate + machine-check   (run twice: the second
                # run must reproduce the first byte for byte)
make cards      # the OG / Twitter / social-preview cards, same character
make cards-verify  # sizes + sha256 of the committed cards, no blender needed
make check      # the checker's own self-test (CIEDE2000 reference pairs)
make clean      # drop build/ and the determinism baseline
```

Needs `blender` (5.x), `rsvg-convert` and a bare `python3`. No pip packages, no
Python dependencies inside Blender beyond what ships with it.

## Outputs (`build/`)

| File | What |
|---|---|
| `gremlin-front.png` | turnaround, front |
| `gremlin-three-quarter.png` | turnaround, 3/4 |
| `gremlin-side.png` | turnaround, side |
| `gremlin-back.png` | turnaround, back |
| `gremlin-hero.png` | the signature pose — claws on the keys, mauve brackets |
| `gremlin-avatar.svg` | flat vector avatar regenerated from the same numbers |
| `compare/{generated,kit}.png` | silhouette pair used for the IoU check |

900×900, orthographic, one fixed camera/light rig.

## Sources

| File | Role |
|---|---|
| `params.json` | every proportion and colour. 2D sections are SVG units, `[x, y]`, y down; `*3d` sections are `[x, z]`, z up (`z = -y`). |
| `gremlin.py` | Blender `bpy` script: builds body, head, ears, eyes, node pupils, brows, grin, fangs, claws, keyboard and the produced-output marks, then renders the five views. |
| `svg/build_svg.py` | regenerates the flat avatar from the same numbers and rasterises it beside the frozen kit master. |
| `check.py` | the acceptance checks (below). |
| `cards.py` | the social cards: one hero render, typeset title, `rsvg-convert`. |
| `pngmeta.py` | strips volatile PNG metadata so identical pixels == identical bytes. |

Numbers are lifted from the frozen masters in
`profile/assets/brand/mascot/` — `gremlin-model-sheet.svg` (construction),
`gremlin-avatar.svg` (head cut), `gremlin-hero.svg` (body, limbs, keyboard).
`params.json` records where each one came from; nothing is freehand.

## Why Workbench, flat

The render is Blender **Workbench**, `light=FLAT`, `color_type=MATERIAL`,
`view_transform=Standard`, dither off. That combination writes the material
albedo to the PNG unchanged, which buys three things at once:

- the palette check can assert an *exact* (`ΔE00 = 0`) match against
  `params.json` instead of a tolerance;
- there is no stochastic sampling, denoiser or seed to drift, so two runs are
  byte-identical;
- flat filled forms are the brand's own grammar (mascot README rule 3 — "no
  gradients, glow, or 3D"). Shading here would be a defect, not a nicety.

`--engine eevee` renders the same geometry through the fixed light rig for a
volume reference. It is not part of the acceptance.

Blender still stamps `tEXt Date` and `tEXt RenderTime` into every PNG, which
changes on each run even when the pixels do not. `gremlin.py:normalise_png`
drops those metadata chunks, so identical pixels mean identical bytes.

## Social cards (`make cards`)

`model/cards.py` produces the three images the org is actually seen through:

| File (in `profile/assets/brand/`) | Size | Consumer |
| --- | --- | --- |
| `og-card.png` | 1200×630 | Open Graph `og:image` |
| `twitter-card.png` | 1200×600 | Twitter/X `summary_large_image` |
| `social-preview-1280x640.png` | 1280×640 | GitHub repository social preview |

Each card is a deterministic compose of two generated things: the character,
rendered from `params.json` through Blender exactly as `make model` does (one
`hero` view), and the title, typeset in a real font over an SVG template that
`rsvg-convert` rasterises — never generated lettering, never a screenshot of a
hand-made HTML page. Colours come from `params.json`, so a palette change moves
the cards with the character.

`profile/assets/brand/cards.json` records each card's size and sha256. A run
compares against it and fails on any byte difference, which is what makes "run
it twice" a check rather than a hope. After a deliberate visual change:
`python3 model/cards.py --update`.

## Acceptance (`check.py`)

| Check | Contract |
|---|---|
| geometry | the 3D case reaches the 2D hero outline exactly: `deck + rim == hero2d` per edge (2.25H front, 1.95H back), the outline stroke equals the 2D `.kbd` stroke, and `hero2d` is re-read from `gremlin-hero.svg` rather than trusted |
| case width | the rendered front view's dark case measures the hero width in pixels (±2 units, anti-aliasing), so a mesh that hangs outside the case cannot hide behind correct arithmetic |
| palette | every `check: true` palette entry appears in the renders at ≥200 px and within `ΔE00 ≤ 3` of its `params.json` hex |
| determinism | this run's five PNG sha256 values equal the previous run's |
| silhouette | generated avatar vs kit master IoU `≥ 0.85` |

`make cards` adds its own three contracts: exact platform sizes, every checked
palette role within `ΔE00 ≤ 3` of `params.json` (it reuses the same check), and
byte-identical output against `profile/assets/brand/cards.json`.

Candidates are classified to their nearest palette role first, so the two
adjacent dark entries (`#181825` mouth vs `#1e1e2e` plate) cannot vouch for each
other, and a colour only counts once it covers real area — an anti-aliasing
blend can never satisfy an entry.

Run 1 has no previous run to compare with, so it records the baseline and
passes. `make clean` drops the baseline; after an intentional change to the
geometry, `make clean && make model` twice.

If the two runs ever stop being byte-identical, the checker measures the moved
pixel fraction against the previous run's kept PNGs and only passes it under
`determinism_max_changed_fraction` (0.5 %) with the reason printed. It has never
triggered; the container-metadata strip is what makes the byte comparison hold.
