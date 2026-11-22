# Repository icons

One icon per repository in the yolo-labz org. Each icon marks a project in lists, READMEs and
catalogues. This set is separate from the 16 px UI icons in `design/docs/components/icons.md`.

## Files

```
design/icons/<repository>.svg       one SVG per repository (15 today)
design/icons/contact-sheet-15.png   all icons at 16, 24, 32 and 64 px, light and dark rows
design/icons/contact-sheet-15@2x.png  the same sheet at 2x
```

## Grid

- `viewBox="0 0 24 24"`, `width="24"`, `height="24"`.
- Live area: 2 to 22 on both axes. Keep every shape inside it.
- Keep the optical size of the mark inside the live area. Do not scale a glyph past it to fill the grid.

## Stroke

- `fill="none"` on the root. Shapes use `stroke` only. No `fill` other than `none`.
- `stroke="currentColor"`, `stroke-width="2"`.
- `stroke-linecap="round"` and `stroke-linejoin="round"`.

## Colour

Each SVG sets `color` on the root. `currentColor` reads it.

| Theme   | Token             | Hex       | Use                      |
|---------|-------------------|-----------|--------------------------|
| Light   | `emerald-deep`    | `#007045` | light surfaces           |
| Dark    | `emerald-base`    | `#00c77a` | dark surfaces (file default) |

Use one colour for each theme. Do not mix them on one surface.

## Element limit

- At most 6 shape elements per icon (`path`, `rect`, `circle`, `line`, `ellipse`, `polygon`, `polyline`).
- Shape elements in the files: 2 to 4 today.
- An icon that needs more elements drops detail. It does not add shapes.

## Metaphor rules

- One object per icon. Name the object in the brief, not the logo.
- Do not use a third-party logo or mark (Apple, Chrome, Google, LinkedIn, GitHub, NixOS, Anthropic).
- Do not use the character mascot inside a project icon. The mascot stays out of project icons.

## Checks

Run these before a change lands:

```bash
python3 - <<'PY'
import glob, xml.etree.ElementTree as ET
for f in sorted(glob.glob("design/icons/*.svg")):
    r = ET.parse(f).getroot()
    shapes = [e for e in r.iter() if e.tag.split("}")[-1] in
              ("path", "rect", "circle", "line", "ellipse", "polygon", "polyline")]
    assert r.get("viewBox") == "0 0 24 24", f
    assert {e.get("fill") for e in r.iter()} - {None, "none"} == set(), f
    assert 1 <= len(shapes) <= 6, f
print("ok")
PY
```

## Changing an icon

Edit the SVG, rerun the checks, render the sheet again, and open a PR. The sheet must match the files.
