# S1 — Programming gremlin construction specification

30/10/2026 · **Exploration; not an approved replacement brand master.**

## Early handoff to S2 / wT:p6 — Gremlin 3D

**Read this file now; do not wait for generated sheets.**
Absolute handoff path:
`/home/notroot/Documents/Code/yolo-labz/github-profile-013-gremlin-model-sheet/profile/assets/brand/model/SPEC.md`

Palette and 2D construction below are fixed to merged SVG kit commit
`64880882f235922007dd22a0cdb22c7ea5f09f83`. They take precedence over GPT
rasters, including the 28/09/2026 anchor. This is the S1/S2 exchange specification,
not a claim that the org has approved a new 3D master. Back/side depth is an
explicit exploratory extension, not something measured from a front-only SVG.

## Authority and identity

1. `../mascot/gremlin-model-sheet.svg`: primary head construction.
2. `../mascot/gremlin-hero.svg`: three-claw hands, keyboard and output.
3. `../mascot/gremlin-{idle,working,paused,loading,asleep,avatar}.svg`:
   silhouette/state rules. `../mascot/README.md` supplies semantic constraints.
4. `../logo-mark-{dark,light,mono}.svg`: the existing YL **monogram**, not a
   gremlin head. Never replace or redraw it as part of this exploration.
5. 28/09/2026 anchor, source art commit
   `637a7fbd3f47127f157d0e0dbbccc807bff57c87`, SHA-256
   `dcd882cb9d7f99316f0278d03c172a9f14135c195efe67556d451a9bd172baeb`:
   secondary attitude reference only. Its shading, keycap depth, ear asymmetry
   and ambiguous two-claw appearance are **not** construction authority.

## Exact sampled palette

These values are parsed from SVG CSS/fill attributes, not invented or inferred
from antialiased raster pixels. Mocha is the primary generated-sheet palette;
Latte is the existing theme adaptation, not permission for arbitrary recolouring.

| Role | Mocha | Latte | SVG origin |
| --- | --- | --- | --- |
| skin | `#a6e3a1` | `#40a02b` | hero .skin fill |
| eyes / teeth / claws | `#cdd6f4` | `#eff1f5` | hero .pale fill |
| mouth / keyboard case | `#181825` | `#dce0e8` | hero .dark fill |
| pupils / produced output | `#cba6f7` | `#8839ef` | hero .node fill |
| keycaps | `#45475a` | `#9ca0b0` | hero .key fill |
| keyboard detail | `#6c7086` | `#9ca0b0` | hero .kbd stroke |
| sheet background | `#1e1e2e` | `#eff1f5` | logo-mark-dark/light rect fill |
| supporting guide / moon | `#a6adc8` | `#7c7f93` | asleep .sub stroke |

Pupils are mauve in awake states. Extra mauve code/brackets/sparks mean
**produced output**, not idle decoration. Asleep: closed lids, no pupils,
**zero mauve on that character or its props**. Palette swatches elsewhere on
a sheet are reference data, not asleep-state decoration.

## Proportions — head units

Define **H = 80 hero-local units**, the head ellipse's height excluding ears and
same-colour welding stroke. Values below describe centreline/fill geometry;
stroke expands its apparent bounds. Do not renormalize H to include the ears.

| Feature | SVG measurement | In H |
| --- | --- | --- |
| head ellipse | rx 48, ry 40 | width 1.20H; height 1.00H |
| ear-tip span | x −98 to +98 | 2.45H |
| ear tips | x ±98, y −68 | x ±1.225H; y −0.85H |
| ear bases | x ±28…±44 | x ±0.35…±0.55H |
| head + ears, vertical | y −68…+40 | 1.35H |
| eye centres | x ±21, y −8 | x ±0.2625H; y −0.10H |
| eye radius | 11 | 0.1375H |
| pupil radius | 4.5 | 0.05625H |
| grin endpoints | x ±40, y +12 | width 1.00H; endpoints y +0.15H |
| down-fang length | about 15 | about 0.1875H |
| up-fang height | 10 | 0.125H |
| hero torso ellipse | rx 44, ry 26 | width 1.10H; height 0.65H |
| hero hand/forearm stroke | 12 | 0.15H |
| hero keyboard silhouette | x 30…210, y 132…154 | width 2.25H; height 0.275H |

Pupils are intentionally offset in the authored front head: x −19 / +23,
y −7 (not an invented symmetrical ±19). Preserve their attitude rather than
copying raster highlights. Brows run (−36,−25)→(−8,−19), mirrored on the right.
Grin path:
`M -40 12 Q 0 54 40 12 Q 0 32 -40 12 Z`.
The quadratic control point y=54 is **not** a measured mouth bounding box.

The idle state scales H by 0.55: H=44 canvas units; head centre (64,48),
torso centre (64,88), torso rx25/ry16, feet/guide at about y112.
Ear tip y=10.6 to guide y112 gives **2.3045H** overall idle envelope.
That is a seated/crouched state, **not a standing height measurement**.

### S1/S2 depth extension — explicit assumptions, fixed for this exploration

The SVG kit does not define side/back volumes. For an initial 3D blockout only,
use head depth **0.80H**, torso depth **0.60H**, thin leaf-like ear thickness
**0.06H**, and relaxed full-body height **2.30H including ear tips**.
These four are proposed S1 constants, not measurements or an approved model.
Keep them separate in the 3D source so later silhouette review can revise them.
Do not invent a long muzzle, horns, fur, clothes, gender markers or extra anatomy.

## Silhouette, counts and line weights

- **Two** large leaf-sweep pointed ears; broad head, compact rounded body.
- **Two** eyes, **three** triangular fangs: two upper/downward and one
  lower/upward. Never blocky square human teeth.
- **Two** hands with **three claws per hand**, clearly separated in the detail
  sheet; no human five-finger hand. The compact working SVG only exposes two
  marks per hand; the hero and binding grammar establish three.
- Two short unsegmented feet; no invented toe/finger detail.
- **One** curved tail with a single angular arrow-like tip. Back view keeps
  the same tail and ear silhouette; it does not add a second tail or spikes.
- Filled flat forms; same-colour round joins/caps weld overlaps.
  No contrasting outlines, gradients, glow, glossy eyes or 3D lighting.

| Detail | Source units / H | Treatment |
| --- | --- | --- |
| head / ear welding stroke | 6 / 80 = 0.075H | same skin colour, round joins |
| brows | 5 / 80 = 0.0625H | skin stroke, fill none |
| hero claws | 3.5 / 80 = 0.04375H | pale stroke, fill none |
| hero keyboard outline | 2.5 / 80 = 0.03125H | keyboard-detail token |
| hero output brackets | 4 / 80 = 0.05H | mauve, output state only |

## Requested sheets and panel order

Five separate reference-anchored GPT images; planned sends **5**, absolute
request ceiling **8**. All use the same role-labelled canonical reference board.
No generation is authorized when the server/session route is unavailable.

1. `turnaround.png`: front, 3/4, side, back, left-to-right; same scale,
   aligned ground, complete ears/tail/feet. Orthographic, no camera perspective.
2. `expressions.png`: 2×3, row-major: ready/mischievous, focused, curious,
   surprised, pleased, sleepy. Same head, ear roots and three-fang construction.
3. `poses.png`: 2×2, row-major: typing, thinking, celebrating, asleep.
   Only typing/celebrating-produced output may add mauve marks. Asleep has none.
4. `hands-keyboard.png`: readable three-claw left/right hand, side grip,
   flat keyboard/blank keycaps and both hands typing; not five human fingers.
5. `colour-material.png`: one neutral character plus clean flat material
   regions. Exact role/hex callouts are typeset outside the generated artwork;
   a model-painted colour label is not palette authority.

No generated lettering, fake measurements or watermarks. Labels, palette chips
and dimensions come from deterministic source composition, not GPT text.

## Drift register — 30/10/2026

| Render | Actual state / drift |
| --- | --- |
| turnaround | NOT GENERATED — browser discovery hold; no view consistency inspected |
| expressions | NOT GENERATED — six expressions remain unverified |
| poses | NOT GENERATED — no action/asleep semantic validation claimed |
| hands-keyboard | NOT GENERATED — three-claw detail remains unverified |
| colour-material | NOT GENERATED — palette/material matching remains unverified |

Existing anchor drift: shallow shading, dimensional keyboard keys, asymmetric
ears and only two claws clearly visible per hand. These are correction targets,
not approval to carry them into S2.

## Do / don't and acceptance

Do retain recognizable programming attitude, solid green silhouette, fanged
grin, blank-key interface and output semantics. Do inspect every actual panel,
especially the back view, hands and asleep colours. Don't copy a film/game
character, borrow Lectrice/Proso's bird/palette, add costume/props or promote
this draft to a logo/avatar/approved master.

`spec.json` is the machine-readable companion. `check.py --spec-only`
validates source-derived palette/construction without asserting sheet delivery.
Default `check.py` must remain nonzero until all five genuine images and
confirmed, sanitized prompt/reference provenance exist. The bad-palette fixture
must fail before missing-image checks. Generation success is not visual approval.
