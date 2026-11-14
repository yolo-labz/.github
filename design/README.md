# yolo-labz design system

One source for the blog, the portfolio and the org profile. Tokens live here, the sites vendor a generated copy,
and each site has a gate that fails when its copy differs from this source.

```
design/
  tokens/primitive.json   palettes (Mocha, Latte, emerald), fonts, space, radius, motion, breakpoints, mobile floors
  tokens/semantic.json    surface, border, text, accent, link, focus, role, signal; dark value + light value
  build.py                stdlib only; writes dist/ or checks it (--check)
  dist/tokens.css         CSS custom properties, --yl-*; dark on :root, light on [data-theme="light"]
  dist/tailwind.css       Tailwind v4 @theme preset that points at those properties
  test_tokens.py          format, references, contrast on both themes, mobile floors, dist is current
  docs/                   the written system, one page per topic
```

## Use it

```bash
python3 design/build.py            # after editing tokens/*.json
python3 -m unittest discover -s design
```

A consumer copies `dist/tokens.css` (and `dist/tailwind.css` if it runs Tailwind v4) into its own tree and records
where it came from in a `design-source.json` next to the copy:

```json
{"repo": "yolo-labz/.github", "rev": "<commit sha>", "files": {"tokens.css": "<sha256 of the copy>"}}
```

Its gate does two checks. Offline: the copy's sha256 equals the recorded one, so nobody edited it by hand. Online
(`DESIGN_ONLINE=1`, set in CI): the same file at `rev` in this repo has that sha256, so nobody forged the record.

## Change a token

Edit `tokens/*.json`, run the build, open a PR here, merge it, then bump `rev` and the copy in each consumer.
A token change that fails the contrast tests does not merge.

## Pages

[colour](docs/colour.md) · [type](docs/type.md) · [spacing, radius, motion, breakpoints](docs/spacing.md) ·
[components and page rules](docs/components.md) · [the mark](docs/mark.md) · [voice](docs/voice.md)
