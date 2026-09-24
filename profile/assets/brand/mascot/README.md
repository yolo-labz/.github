# yolo-labz mascot — the programming gremlin

The org's mascot is **the programming gremlin** (Pedro, 23/09: *"the mascot for
the yolo labz is the gremlin programming"*) — the little beast that lives in
the machine and writes the code. Mischievous, capable, permanently mid-hack.

Character construction is frozen in `gremlin-model-sheet.svg` (head geometry,
palette chips, accent rule). Every new pose reuses those numbers — nothing is
freehand.

## The grammar

- **Skin green is the character.** Never recolour it; it is the gremlin, the
  way vermilion is Lectrice's bird.
- **Node pupils** are the YL monogram's fork node — one accent circle across
  mark and mascot.
- **Mauve = produced by the gremlin.** Code brackets and sparks are mauve and
  appear only when it produces output (`working`, `hero`). In `asleep` there is
  no mauve at all: nothing is running.
- **The keyboard is the interface** (the prompt, the socket). In states without
  a keyboard, **the line** carries the same role.

## States

| State | File | Reads as | Appears when |
|---|---|---|---|
| idle / ready | `gremlin-idle.svg` | sitting on the line, arms on knees, grinning | service up, listening on its socket |
| working | `gremlin-working.svg` | hunched over the keyboard, claws on keys, mauve brackets + sparks | serving a request — *the gremlin programming* |
| paused | `gremlin-paused.svg` | head turned to the signal, claw raised | holding for input, rate-limited |
| loading | `gremlin-loading.svg` | scrambling off a dashed line, ears back, motion ticks | cold start, warm-up |
| asleep | `gremlin-asleep.svg` | hunched on the line, lids closed, filled moon | idle timeout, night mode |

Plus two non-state assets: `gremlin-hero.svg` (the signature piece — the
gremlin programming, 240×160) and `gremlin-avatar.svg` (head cut on a rounded
tile for social avatars / app icon).

Every state ships as `.svg` (master) + `.png` (320px raster); hero at 720px,
model sheet at 1080px. Masters are theme-adaptive (`prefers-color-scheme`:
Mocha dark default, Latte light) with the same class contract as
`../favicons/favicon.svg`.

## Usage rules — binding

1. **Meaning, never chrome.** The gremlin appears where the system is coding,
   speaking, waiting or resting. Never on utility surfaces: settings forms,
   file dialogs, disk-space errors.
2. **Mauve = produced.** Node pupils always; code brackets/sparks only in
   `working`/`hero`; zero mauve in `asleep`.
3. **One silhouette weight.** Filled forms with round joins — a filled form may
   carry a same-colour stroke to weld overlaps (never a contrasting outline).
   Stroke-only details (brows, claws, lids, guides) use inline `style="fill:none"`
   or a dedicated class with an explicit stroke. Never outline-render a shape
   among fills. No gradients, glow, or 3D.
4. **Props are load-bearing only.** The keyboard (the interface) and the moon
   (night) are the only props. No hats, scarves, laptops, speech bubbles.
5. **Small-size honesty.** Silhouette survives 32px. At favicon size use
   `gremlin-avatar.svg` or `../favicons/favicon.svg` — the YL monogram.

## Anti-patterns (refuse on sight)

- Recoloured skin (blue gremlin, gold gremlin, …)
- Mauve decoration with nothing produced
- Teeth as white blocky squares — fangs are triangular and jagged
- Glossy eyes, anime highlights, extra fingers (3 claws, always)

## Regenerate

```bash
for f in gremlin-idle gremlin-working gremlin-paused gremlin-loading gremlin-asleep gremlin-avatar; do
  rsvg-convert -w 320 $f.svg -o $f.png; done
rsvg-convert -w 720 gremlin-hero.svg -o gremlin-hero.png
rsvg-convert -w 1080 gremlin-model-sheet.svg -o gremlin-model-sheet.png
```

## Lineage

The 22/09 bird set ("the bird on the line") was removed in this commit: the
bird motif belongs to **Lectrice** (vermilion singer, 21/09). yolo-labz's
character is the gremlin — different species, same discipline: a state
machine, not a sticker pack, and the accent only ever means "produced".
