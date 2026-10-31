# Reproduce S1 inputs and resume after the recorded quota hold

**Current result: 4 of 5 sheets, 5 of 8 sends spent.** These are instructions
plus one exact resume step, not a completion claim. The sheet set is incomplete
until `colour-material.png` exists and the default gate exits 0.

## What actually ran (31/10/2026, 13:13–13:26 BRT)

Per sheet, from `profile/assets/brand/model/`:

```bash
P=$(cat prompts/01-turnaround.txt)
gpt-image "$P" --ref refs/canonical-reference-board.png \
  --out .private/staging --identity chatgpt-c --timeout 260 --json \
  > .private/receipts/01-turnaround.json 2> .private/receipts/01-turnaround.err
```

The installed `gpt-image` shim takes the fleet queue lock itself, so no extra
`flock` wrapper is needed or wanted. It attaches through `interactive.attach` to
the warm Nix.Server `chatgpt-c` browser; there is no local browser and no API
path. Raw receipts (which carry the conversation and blob URLs) stay in
`.private/receipts/`, which is git-ignored; only hashes cross into the tracked
sidecars.

Three transport facts to expect on a resume, all observed and all pre-send:

1. The CDP forward flaps during `browser-fleet-tunnel` reconciles. A run that
   dies with `ECONNREFUSED 127.0.0.1:9615` sent nothing; wait for
   `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9615/json/version`
   to return 200, then re-invoke.
2. A fresh chat sometimes lands on `https://chatgpt.com/library`, which returns
   `status: no-conversation`, `send_confirmed: false`. Nothing was sent; one
   re-invoke is correct.
3. Only `send_confirmed: true` counts as a send. Attempts that never confirmed
   are kept under `.attemptN.json` names and are not counted here.

## Exact resume step for the missing fifth sheet

The account hit its free-plan image quota at send 5 (reset around 16:25 BRT,
31/10/2026). After the reset, one send, nothing else:

```bash
P=$(cat prompts/05-colour-material.txt)
gpt-image "$P" --ref refs/canonical-reference-board.png \
  --out .private/staging --identity chatgpt-c --timeout 260 --json \
  > .private/receipts/05-colour-material.attempt3.json \
  2> .private/receipts/05-colour-material.attempt3.err
```

Then rename to `colour-material.png`, write `colour-material.provenance.json`
with the same schema as the other four (`kind: model-sheet`, receipt status ok,
`send_confirmed: true`, prompt/reference hashes, `receipt_sha256`), set
`generated_images` to 5 in `generation-status.json`, and run the default gate.
Do not re-send sheets 1–4; they are accepted inputs now.

Resume only if the remaining send budget still holds (`sends_used` < 8) and the
quota message is gone. If the same quota text is on screen, that is the same
hold, not a new failure: stop and record it.

## Immutable inputs and offline checks

Source: merged SVG kit `64880882f235922007dd22a0cdb22c7ea5f09f83`.
Exact secondary anchor: art commit
`637a7fbd3f47127f157d0e0dbbccc807bff57c87`, repository path
`profile/assets/brand/exploration/2026-09-28/gremlin-anchor.png`.
No private browser URL or vault excerpt is an input.

From the 013 worktree root:

```sh
python3 profile/assets/brand/model/prepare_refs.py
python3 profile/assets/brand/model/check.py --spec-only   # exits 0
python3 -m unittest discover -s profile/assets/brand/model -p 'test_*.py' -v
python3 profile/assets/brand/model/check.py
# Exits 1 today: Missing: colour-material.png (4 of 5 sheets delivered)
python3 profile/assets/brand/model/check.py --spec-only \
  --spec-json fixtures/bad-palette.json
# MUST exit 1: SPEC palette mismatch against SVG kit
```

`check.py` also re-derives every head-unit and line-weight value from the merged
`model/params.json` (PR #14), so the 2D spec and the 3D source cannot drift apart
silently. `prepare_refs.py` only copies/combines existing images, using
ImageMagick with one thread and DejaVu Sans for labels. It reads anchor bytes
from the immutable Git object. It does not generate art or attach to any browser.
Every prepared PNG has its own `*.provenance.json` labelled **reference**, not an
S1 generation. `refs/sources.json` binds every source SVG to Git.
`prompts/manifest.json` pins exact prompt and board hashes.

## Route requirements, for the record

The supported route is: `browser_identities` (or `browser_status`) to confirm the
registered **chatgpt-c** row is live, then the installed **gpt-image** shim, which
attaches only to an existing warm browser. It never starts one. Do not assign a
different endpoint, clear a foreign draft, restart Chrome, relogin, use a local
browser or spend API credits. A retracted CDP manifest and a dead forward are
transport waits, not permission to take another route.

## One prompt at a time, one send per invocation

All five runs use `refs/canonical-reference-board.png`; that board includes
the original immutable anchor only as a secondary attitude panel. The canonical
SVG panels and SPEC override its shading/two-visible-claw drift.
Use an owned fresh thread; do not modify another project's instructions.

| Order | Prompt | Public output | State |
| --- | --- | --- | --- |
| 1 | `prompts/01-turnaround.txt` | `turnaround.png` | delivered |
| 2 | `prompts/02-expressions.txt` | `expressions.png` | delivered |
| 3 | `prompts/03-poses.txt` | `poses.png` | delivered |
| 4 | `prompts/04-hands-keyboard.txt` | `hands-keyboard.png` | delivered |
| 5 | `prompts/05-colour-material.txt` | `colour-material.png` | blocked on quota |

Invocation shape is the `gpt-image` call at the top of this file; the shim holds
the fleet lock for its whole run, so concurrent seats queue instead of typing
into the same composer. Never bypass it with a second lock or a second worker.

After each invocation, preserve raw output privately, count confirmed **and
ambiguous** sends conservatively, update `generation-status.json`, inspect the
actual image, then decide whether to continue. Five sends are planned; the
remaining budget under the ceiling of eight is for a concrete recorded drift
with a fresh prompt/attempt ID, never an unchanged retry. Stop at eight, at the
first exact blocker, or when the account quota refuses.

## Public success sidecar contract (never synthesize one for absent output)

For each actual `<sheet>.png`, create `<sheet>.provenance.json` with:

- `kind: model-sheet`, `classification: exploration-not-approved-master`.
- Exact `image` path, `sha256`, measured `width`/`height`.
- Exact `prompt` path and `prompt_sha256`.
- `references`: image path/hash pairs including the uploaded board.
- `identity: chatgpt-c`, actual observed timestamp and model evidence.
  Backend ID may be null if the UI does not expose it; never guess from a label.
- Sanitized `receipt`: actual status, send_confirmed, byte count;
  `receipt_sha256` binds the privately retained raw receipt.
- No conversation/project URL, signed CDN link, account name or private source.

Copy exact downloaded bytes; do not silently retouch the source PNG.
For colour/material callouts, retain the raw generation and compose labels in a
separately named derivative with its own source hash/provenance. Typeset exact
hex swatches from spec.json, not generated lettering. Do not invent an output
or a success receipt to make the checker green.

## Reproducibility boundary and completion

Prompts, palette, construction, source bytes and lineage are reproducible.
ChatGPT web exposes no deterministic seed or guaranteed exact backend ID, so a
new generation is **not guaranteed byte-identical**. Preserve original outputs
and hashes as the reproducible evidence; the SVG geometry is the construction
authority, not an approximate raster.

Inspect all four views, at least six expressions, all four actions, three-claw
hands and asleep's zero-mauve rule. Record specific drift per actual sheet in
SPEC.md, retain exploration labels, run default check.py and privacy checks.
Four renders exist at this checkpoint and their drift is recorded; the fifth is
blocked on the account quota, not on a design decision. Keep the PR draft,
assigned phsb5321; no merge, production deployment, publication or brand-master
promotion.
