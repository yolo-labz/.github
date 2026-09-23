# yolo-labz mascot — the bird on the line

A five-state character system in the family bird grammar (perched singer + the
line). It exists because leading character systems are **state machines, not
sticker packs** — Duo's expression is a function of what the app is doing. The
same is true here: one bird, five states, each meaning exactly one thing.

## The grammar

- **The line** is the interface — socket, pipe, log. The bird perches on it.
  It leaves the line only in `loading`, where the line stays behind, dashed.
- **The node eye** is the YL monogram's fork node: same circle, same accent.
- **The output line** (open beak + a thin line leaving it) is the family voice
  gesture — the one way the bird "speaks".

## States

| State | File | Reads as | Appears when |
|---|---|---|---|
| idle / ready | `mascot-idle.svg` | perched on the line, beak closed, node eye lit | service up, listening on its socket |
| working | `mascot-working.svg` | beak open, mauve output line leaving it | a request is being served, output flowing |
| paused | `mascot-paused.svg` | head turned over the shoulder, arcs arriving at the face | holding for input, rate-limited wait |
| loading | `mascot-loading.svg` | lifting off a dashed line, wings half-spread | cold start, model load, first-reply wait |
| asleep | `mascot-asleep.svg` | hunched, head tucked, moon up, node dark | idle timeout, night mode |

Every state ships as `.svg` (master) + `.png` (320px raster). Masters are
theme-adaptive (`prefers-color-scheme`: Mocha dark default, Latte light) with
the same class contract as `../favicons/favicon.svg`.

## Usage rules — binding

1. **Meaning, never chrome.** The bird appears where the system is speaking,
   working, waiting or resting. It never appears on utility surfaces: settings
   forms, file dialogs, disk-space errors.
2. **Mauve = produced by the bird.** The eye node is always the accent; a
   second accent element (the output line) exists only in `working`. In
   `asleep` even the node is dark — nothing is running.
3. **One silhouette weight.** Filled forms with round joins; never
   outlines-plus-fill mixing, gradients, glow, or 3D.
4. **No anthropomorphic props.** No hats, scarves, laptops, speech bubbles.
   The output line is the only speech this bird has.
5. **Small-size honesty.** Silhouette must survive 32px (the aferidor rule).
   At favicon size use `../favicons/favicon.svg` — the YL monogram, not the bird.

## Regenerate

```bash
rsvg-convert -w 320 mascot-idle.svg -o mascot-idle.png   # repeat per state
```

## Family note

The Lectrice brand moved its bird to vermilion `#C8462C` on paper (Pedro,
21/09). This mascot keeps yolo-labz's Catppuccin accent to match the shipped
kit (monogram, wordmarks, favicons, OG cards); a vermilion pass is a single
`.voice` / `.node` style-block recolour if that decision extends to the org.
