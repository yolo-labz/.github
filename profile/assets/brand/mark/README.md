# The gremlin head mark

One master (`master.py`), one build (`build.py`), one test (`tests.py`). Direction `A` ships; `B` and `C` stay so the
decision can be re-run.

```sh
python3 profile/assets/brand/mark/build.py                      # write every logo, icon and avatar
python3 profile/assets/brand/mark/build.py --verify             # rebuild to a temp dir, compare bytes
python3 profile/assets/brand/mark/build.py --social out.png --repo NAME --line "one line"   # 1280x640 card
uv run --with pillow --with numpy python profile/assets/brand/mark/tests.py                 # the decision tests
```

Needs `rsvg-convert` and ImageMagick. `tests.py` also needs pillow and numpy.

## Why A

The rule was written before the first run. A direction is eligible only if every required feature survives at 16 px
in four forms (colour on a dark tile, colour on a light tile, one colour on dark, one colour on light): at least one
pixel with coverage of 0.5 or more, and at least 3:1 contrast against its surround. Among the eligible, the lowest
edge blur wins.

| direction | features | eligible | worst case at 16 px |
|---|---|---|---|
| A | ears + eyes | yes | eyes 3.17:1 (colour, light tile) |
| B | ears + grin | no | grin 1.43:1 (colour, light tile) |
| C | eyes + grin, short ears | no | grin 1.28:1 (colour, light tile), 2.95:1 (one colour, dark) |

Numbers: `tests.json` in the loop evidence for row NX-BRAND-MARK; rerun `tests.py` to reproduce.

## Rules

- Skin is the character and is never recoloured: `#a6e3a1` on dark, `#388c26` on light. Eye slots are `#181825`.
- Pupils (`#cba6f7` / `#8839ef`) appear from 64 px up only.
- One silhouette weight, no outline, no gradient, no glow, no shadow. Coordinates sit on a 16-unit grid, so 16, 32, 64
  and 128 px are exact multiples.
- Clear space: one ear-to-head gap (1/16 of the mark width) on every side; a tile keeps the mark at 82% of its width
  (70% for the org avatar so the ear tips survive a circle crop).
- Minimum size: 16 px as the tile (favicon). Loose mark: 24 px.
