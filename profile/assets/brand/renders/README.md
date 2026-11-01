# Hero plates

The programming gremlin in its hero pose, published at the sizes downstream
surfaces ask for. Generated, never drawn: `make renders` renders them from
`model/params.json` through `model/render_hero.py`, which reuses the same
`gremlin.py` builders `make model` uses.

| | |
|---|---|
| source | `model/params.json` (geometry + palette), `model/gremlin.py` (meshes) |
| renderer | Blender Workbench, flat lighting, Standard view transform, dither off |
| camera | orthographic, fitted per frame: `ortho_scale` comes from the evaluated content bounds plus a 6 % margin, so each plate is the artwork rather than a crop of a larger render |
| pose | the hero pose (`reach`, produced marks on): claws on the keys, mauve code marks |
| themes | Mocha (`dark`, the character's default) and Latte (`light`, the kit's own light query) |
| formats | PNG (the render, metadata-stripped), WebP (`-quality 88`, `method=4`), AVIF (`-quality 60`, `speed=4`) |

## Sizes

| Size | Who asks for it |
|---|---|
| 1600 × 1200 | generic 4:3 hero plate |
| 800 × 600 | 1× / 2× mid-size hero |
| 390 × 520 | portrait plate for phone-first layouts |
| 804 × 770 | the portfolio home render's large width (as shipped before this set existed) |
| 402 × 385 | the same render's small width |

The last two exist because a consumer already ships them; the first three are the
generic set. Sizes are data (`model/params.json` → `renders.sizes`), not a code
path, so adding one is a params edit plus `make renders`.

## Byte contract

`manifest.json` pins, for each of the 30 files, the sha256, the byte count, the
pixel size, the format and the theme; it also pins the sha256 of `params.json`,
`gremlin.py` and `render_hero.py`, plus the Blender and ImageMagick versions and
the exact encoder settings.

- `make renders` renders and re-encodes into `build/`, then compares. It prints
  `reproduced 30/30 plates byte-identically` and writes nothing when the model is
  unchanged, and fails loudly with the drifting files when it is not. A deliberate
  visual change is `python3 model/renders.py --update`.
- `make renders-verify` is the blender-free gate: sha256, pixel size and format
  for every committed file. CI can run it without a GPU or a Blender install.

Both formats are encoded single-threaded with a fixed method/speed: multithreaded
WebP/AVIF encoding is not byte-stable, and the sha256 contract would be
unverifiable if it were left on the default thread count.

## Using them

```html
<picture>
  <source type="image/avif"
          srcset="/brand/renders/gremlin-hero-800x600-dark.avif 800w,
                  /brand/renders/gremlin-hero-1600x1200-dark.avif 1600w"
          media="(prefers-color-scheme: dark)">
  <source type="image/webp" srcset="/brand/renders/gremlin-hero-800x600-light.webp 800w">
  <img src="/brand/renders/gremlin-hero-800x600-light.png" width="800" height="600"
       alt="…">
</picture>
```

The plate colour is the theme's `base` — `#1e1e2e` (Mocha) and `#eff1f5` (Latte) —
which is what the profile surface uses, so a plate sits on the page ground with no
frame. Never retouch, letter, filter or re-encode these outside `model/`: the
sha256 in `manifest.json` is the only reason a consumer can trust the bytes.
