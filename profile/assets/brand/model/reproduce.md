# Reproduce S1 inputs and resume after the recorded browser hold

**Current result: no new S1 images, 0/8 sends.** These are instructions, not a
generation receipt. The model sheet is incomplete until all five actual outputs
pass the default gate and panel-by-panel visual review.

## Immutable inputs and offline checks

Source: merged SVG kit `64880882f235922007dd22a0cdb22c7ea5f09f83`.
Exact secondary anchor: art commit
`637a7fbd3f47127f157d0e0dbbccc807bff57c87`, repository path
`profile/assets/brand/exploration/2026-09-28/gremlin-anchor.png`.
No private browser URL or vault excerpt is an input.

From the 013 worktree root:

```sh
python3 profile/assets/brand/model/prepare_refs.py
python3 profile/assets/brand/model/check.py --spec-only
python3 -m unittest discover -s profile/assets/brand/model -p 'test_*.py' -v
python3 profile/assets/brand/model/check.py
# Last command MUST currently exit 1: Missing: turnaround.png
python3 profile/assets/brand/model/check.py --spec-only \
  --spec-json fixtures/bad-palette.json
# MUST exit 1: SPEC palette mismatch against SVG kit
```

`prepare_refs.py` only copies/combines existing images, using ImageMagick with
one thread and DejaVu Sans for labels. It reads anchor bytes from the immutable
Git object. It does not generate art or attach to any browser.
Every prepared PNG has its own `*.provenance.json` labelled **reference**,
not an S1 generation. `refs/sources.json` binds every source SVG to Git.
`prompts/manifest.json` pins exact prompt and board hashes.

## Readiness is blocked, not retryable by this row

The observed `browser_identities` result had `isError=true`, `ok=false`:
`fleet host unreachable` / `invalid browser endpoint record`.
Targeted chatgpt-c active status is not an authenticated composer sentinel.
Do not bypass inventory, assign a different endpoint, clear a foreign draft,
restart Chrome, relogin, use a local browser or spend API credits.

Resume only after the supported server discovery/session workflow is genuinely
available and this hold has been reconciled. Use registered **chatgpt-c**, existing
Nix.Server browser, installed **gpt-image** shim. Recheck producer processes and
lock; use no extra workers. The old #2505 candidate wrapper is absent on disk.
If a future invocation reproduces the closed-session error, preserve it and
record the absent candidate as a blocker; do not build/deploy a substitute.

## One prompt at a time, with an actual nonblocking fleet lock

All five runs use `refs/canonical-reference-board.png`; that board includes
the original immutable anchor only as a secondary attitude panel. The canonical
SVG panels and SPEC override its shading/two-visible-claw drift.
Use an owned fresh thread; do not modify another project's instructions.

| Order | Prompt | Public output |
| --- | --- | --- |
| 1 | `prompts/01-turnaround.txt` | `turnaround.png` |
| 2 | `prompts/02-expressions.txt` | `expressions.png` |
| 3 | `prompts/03-poses.txt` | `poses.png` |
| 4 | `prompts/04-hands-keyboard.txt` | `hands-keyboard.png` |
| 5 | `prompts/05-colour-material.txt` | `colour-material.png` |

For each row, after readiness is established, the invocation shape below is
exact. Set `id` to the table's numbered prompt basename. This example does
**not** run automatically and must not be executed while this hold remains.

```bash
set -eo pipefail
source /etc/profiles/per-user/notroot/etc/profile.d/hm-session-vars.sh
set -u
model="$PWD/profile/assets/brand/model"
id=01-turnaround
umask 077
mkdir -p "$model/.private"
exec 9>"$HOME/.cache/gpt-image-queue.lock"
flock -n 9 || exit 9
test ! -e "$model/STOP"
test ! -e "$model/.private/$id.started"
test ! -e "$model/.private/$id.json"
test ! -e "$model/.private/$id.err"
# Count reconciled historical sends/ambiguous attempts first. Never exceed eight.
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sends_used"])' \
  "$model/generation-status.json")" -lt 8
: > "$model/.private/$id.started"
# GPT_QUEUE_LOCK_HELD is valid ONLY because fd 9 actually holds the fleet lock.
GPT_QUEUE_LOCK_HELD=1 gpt-image "$( < "$model/prompts/$id.txt")" \
  --identity chatgpt-c --ref "$model/refs/canonical-reference-board.png" \
  --out "$model/.private/$id-output" --timeout 600 --json \
  > "$model/.private/$id.json" 2> "$model/.private/$id.err"
```

The parent shell keeps the fleet lock while the installed shim runs; there is
no lock bypass. Separate invocations must reconcile the previous result before
the next send. Existing started/json/err files — even empty — prevent a repeat.
A process failure or missing response does not prove a send was absent.
No automatic retry, changed output directory to evade guards, or fallback model.
The shell exits on failure and must be allowed to release fd 9; do not keep a
successful generation's lease while waiting for another seat.

After each invocation, preserve raw output privately, count confirmed **and
ambiguous** sends conservatively, update `generation-status.json`, inspect the
actual image, then decide whether to continue. Five sends are planned; up to
three additional corrections require a concrete recorded drift and a fresh
prompt/attempt ID, never an unchanged retry. Stop at eight or the first exact
blocker. Do not run gpt-clear/project or clear somebody else's draft.

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
No render exists at this checkpoint. Keep the PR draft, assigned phsb5321;
no merge, production deployment, publication or brand-master promotion.
