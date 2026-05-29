# yolo-labz brand assets

Canonical brand system for the org. Everything here is generated from the
SVG masters and the two HTML templates — regenerate, never hand-edit the PNGs.

## The mark

A `YL` monogram: the `Y` is drawn as a forked letterform, the `L` shares its
baseline, and a single mauve node sits at the fork. It was chosen over the
other concepts because it is the only mark that stays legible at both 16px
(favicon) and as a circular GitHub org avatar.

Canonical geometry (viewBox `0 0 128 128`):

```
Y: M32 28 L52 60 L52 100   +   M72 28 L52 60     (fork + stem)
L: M88 28 L88 80           +   M52 100 L96 100   (riser + shared base)
node: circle cx=52 cy=60   (mauve, at the fork)
```

Stroke width 6 (7 in the favicon/OG lockup for small-size weight),
`stroke-linecap`/`stroke-linejoin` round.

## Color

Catppuccin — Mocha for dark surfaces, Latte for light. Token classes only,
never raw hex outside these masters.

| Role | Mocha (dark) | Latte (light) |
|------|--------------|---------------|
| background | `#1e1e2e` base | `#eff1f5` base |
| surface | `#181825` mantle / `#11111b` crust | — |
| ink (strokes / text) | `#cdd6f4` text · `#a6adc8` subtext | `#4c4f69` text |
| node / accent | `#cba6f7` mauve | `#8839ef` mauve |
| syntax (deck code) | `#a6e3a1` green · `#fab387` peach · `#89b4fa` blue | — |

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
├── logo-mark-{dark,light}.png        256px raster
├── logo-wordmark-{dark,light}.svg    mark + "yolo-labz", text outlined
├── logo-wordmark-{dark,light}.png    940px-wide raster
├── favicons/
│   ├── favicon.svg                   theme-adaptive (prefers-color-scheme)
│   ├── favicon-{16,32,64,128,512}.png
│   ├── favicon.ico                   multi-res 16+32+64
│   └── apple-touch-icon.png          180px, dark mark on base
├── og-card.png                       1200×630 social card
├── twitter-card.png                  1200×630 (same copy)
└── slides/
    ├── deck.html                     6-slide org deck (fragment-navigated)
    └── slide-{1..6}.png              2560×1440 (2× of 1280×720)
```

The two source templates live one level up at `../og-card-template.html`
(renders `og-card.png` + `twitter-card.png`) and `slides/deck.html`
(each `#sN` fragment renders one slide).

## Regenerate

```bash
# raster a mark/wordmark SVG
rsvg-convert -w 256 logo-mark-dark.svg -o logo-mark-dark.png

# outline wordmark text to paths (font-independent)
inkscape in.svg --export-text-to-path --export-plain-svg --export-filename=out.svg

# OG / Twitter card + slides (Chrome headless, works on NixOS)
google-chrome-stable --headless=new --no-sandbox --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1200,630 --screenshot=og-card.png \
  "file://$PWD/../og-card-template.html"

google-chrome-stable --headless=new --no-sandbox --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1280,720 --screenshot=slides/slide-1.png \
  "file://$PWD/slides/deck.html#s1"   # repeat #s1..#s6

# favicon.ico (multi-res)
magick favicons/favicon-16.png favicons/favicon-32.png favicons/favicon-64.png favicons/favicon.ico
```
