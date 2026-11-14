# yolo-labz brand assets

Canonical brand system for the org. Everything here is generated from the
SVG masters and the two HTML templates. Regenerate the PNGs, never edit them by hand.

## The mark

The gremlin's head: two pointed ears and two slanted eye slots, on a 16-unit
grid. It was chosen from three directions by a fixed test, not by taste: it is
the only one whose features all survive at 16 px, in colour and in one colour,
on a light and a dark page (`mark/tests.py`, decision in `mark/README.md`). The
grin does not survive 16 px, so it lives in the mascot, not in the mark.

`mark/master.py` holds the geometry; `mark/build.py` writes every file below
from it, so the set cannot drift (`python3 profile/assets/brand/mark/build.py --verify`).
The YL monogram is retired.

## Color

Catppuccin: Mocha for dark surfaces, Latte for light. Token classes only,
never raw hex outside these masters.

| Role | Mocha (dark) | Latte (light) |
|------|--------------|---------------|
| background | `#1e1e2e` base | `#eff1f5` base |
| surface | `#181825` mantle / `#11111b` crust | n/a |
| ink (strokes / text) | `#cdd6f4` text · `#a6adc8` subtext | `#4c4f69` text |
| surface | `#181825` mantle / `#11111b` crust | n/a |
| ink (text, mono mark) | `#cdd6f4` text · `#a6adc8` subtext | `#1e1e2e` |
| gremlin skin | `#a6e3a1` | `#388c26` (3.75:1 on `#eff1f5`) |
| node / accent | `#cba6f7` mauve | `#8839ef` mauve |
| syntax (deck code) | `#a6e3a1` green · `#fab387` peach · `#89b4fa` blue | n/a |

## Type

Anti-slop: not Inter-only. Two families, each with installed-then-system
fallbacks so the SVGs render identically off-box.

- Headings: `"Noto Serif Display", "Noto Serif", "Source Serif Pro", Charter, Georgia, serif`
- Wordmark / code / labels: `"JetBrainsMono Nerd Font", "JetBrains Mono", "FiraCode Nerd Font", ui-monospace, monospace`

Wordmark SVGs ship with the text already **outlined to paths** (via Inkscape),
so they are font-independent on any renderer.

## Inventory

```
brand/
├── logo-mark-{dark,light,mono}.svg   mark only. mono = currentColor.
├── logo-mark-{dark,light}.png        512px raster
├── logo-wordmark-{dark,light}.svg    mark + "yolo-labz", text outlined
├── logo-wordmark-{dark,light}.png    940px-wide raster
├── favicons/
│   ├── favicon.svg                   theme-adaptive (prefers-color-scheme)
│   ├── favicon-{16,32,64,128,512}.png
│   ├── favicon.ico                   multi-res 16+32+64
│   └── apple-touch-icon.png          180px, dark mark on base
├── hero/                             SERVED hero + avatar: hero crops (WebP/AVIF),
│                                     vector avatar at 96/460 px; manifest.json pins bytes
├── mascot/                           the programming gremlin, 5-state character system
│   ├── favicon-{16,32,48,64,128,192,512}.png
│   ├── favicon.ico                   multi-res 16+32+48
│   └── apple-touch-icon.png          180px, square, mark on base
├── mark/                             master, build script, tests, avatar, social template
├── hero/                             SERVED hero + avatar: hero crops (WebP/AVIF),
│                                     vector avatar at 96/460 px; manifest.json pins bytes
├── mascot/                           the programming gremlin, 5-state character system
│   ├── README.md                     grammar + states + binding usage rules
│   ├── gremlin-model-sheet.svg       construction spec (head geometry, palette, rules)
│   ├── gremlin-hero.svg              signature piece, the gremlin programming (240×160)
│   ├── gremlin-avatar.svg            head cut for social avatar / app icon
│   └── gremlin-{idle,working,        state masters (.svg) + 320px rasters (.png)
│       paused,loading,asleep}.{svg,png}
├── og-card.png                       1200×630 Open Graph card        (generated)
├── twitter-card.png                  1200×600 summary_large_image    (generated)
├── social-preview-1280x640.png       1280×640 repo social preview    (generated)
├── cards.json                        sha256 + size contract for the three cards
└── slides/
    ├── deck.html                     6-slide org deck (fragment-navigated)
    └── slide-{1..6}.png              2560×1440 (2× of 1280×720)
```

The cards are **not** hand-made and have no HTML template: `model/cards.py`
renders the gremlin once from `model/params.json` through Blender and typesets
the title in Inter over an SVG that `rsvg-convert` rasterises. Running it twice
must reproduce the committed bytes; `cards.json` is the contract it checks.
`slides/deck.html` is separate (each `#sN` fragment renders one slide).

## Regenerate

```bash
# raster a mark/wordmark SVG
rsvg-convert -w 256 logo-mark-dark.svg -o logo-mark-dark.png

# mascot states (see mascot/README.md for the gremlin state machine + usage rules)
cd mascot && for f in gremlin-idle gremlin-working gremlin-paused gremlin-loading gremlin-asleep gremlin-avatar; do
  rsvg-convert -w 320 "$f.svg" -o "$f.png"; done

# outline wordmark text to paths (font-independent)
inkscape in.svg --export-text-to-path --export-plain-svg --export-filename=out.svg

# OG / Twitter / social-preview cards, rendered from the gremlin model
# (from the repo root; needs blender + rsvg-convert, ~45 s, deterministic)
make cards

# slides: the deck is rendered by a headless browser from deck.html
# (see docs/brand-positioning.md for the approved copy)
CHROME="google-chrome-stable"   # any Chromium build works
"$CHROME" --headless=new --no-sandbox --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1280,720 --screenshot=slides/slide-1.png \
  "file://$PWD/slides/deck.html#s1"   # repeat #s1..#s6

# favicon.ico (multi-res)
magick favicons/favicon-16.png favicons/favicon-32.png favicons/favicon-64.png favicons/favicon.ico
```
