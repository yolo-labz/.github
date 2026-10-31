# S1 — Gremlin model-sheet exploration

30/10/2026 · branch `013-gremlin-model-sheet` · **draft / exploration**.

## Early SPEC handoff — wT:p6 / Gremlin 3D

Palette and measured 2D proportions are fixed; S2 may read now:
`/home/notroot/Documents/Code/yolo-labz/github-profile-013-gremlin-model-sheet/profile/assets/brand/model/SPEC.md`

Companion: `profile/assets/brand/model/spec.json`.
Both are derived from merged SVG kit `6488088`. Side/back depth constants are
explicit exploratory assumptions, not claims about a pre-existing 3D master.
Three claws follow the hero/master grammar, not the prior raster's occlusion.

## Current effects and blocker

Created the requested canonical worktree from freshly fetched origin/main.
No existing branch, residue directory, browser project or other seat changed.

S1 sends used: **0/8**. No upload or prompt send attempted.
The live server browser inventory call returned `isError=true`, `ok=false`,
`fleet host unreachable` with detail `invalid browser endpoint record`.
The offending unrelated identity/path is redacted from public evidence.
The targeted chatgpt-c status returned only active/tunneled=false, not an
authenticated empty-composer sentinel. This does not prove readiness.

Desktop/server producer process checks found no active image generator.
Fleet queue lock had no reported holder; wrapper stale-lock paths were absent.
Those observations are not a lease or session-readiness claim.
No local browser, direct HTTP, API fallback, retry, login, reset, clear or
browser restart was attempted. The former isolated #2505 wrapper store path
is no longer present; no replacement was built or deployed.

## Delivery / acceptance

Early SPEC handoff was pushed as `a5d9ea77dcf82646663f1ecc54a8619566df5add`
and immediately exposed in [draft PR #12](https://github.com/yolo-labz/.github/pull/12),
assigned to verified **phsb5321**. The lead relays the path to wT:p6; no other
pane was prompted or interrupted. SPEC remains the fixed construction handoff.

Durable work is under `profile/assets/brand/model/`: `SPEC.md`, `spec.json`,
`PLAN.md`, `tasks.md`, five prompts plus hash manifest, six imported reference
PNGs and one deterministic labelled board, seven reference provenance sidecars,
source SVG hash manifest, `reproduce.md`, `check.py`, `test_check.py`,
`generation-status.json` and `validation-2026-10-30.json`.
Reference PNGs are explicitly not new S1 GPT renders. There is no fake success
sidecar for any missing sheet. Prompt/reference provenance and private-URL checks
are runnable entirely offline. Historical anchor backend ID remains unknown;
no current UI model was observed or guessed.

Actual executed results:
- **Default `check.py`: exit 1**, `FAIL: Missing: turnaround.png`.
- **`check.py --spec-only`: exit 0**, source palette/proportions/reference hashes
  and privacy pass; expressly NOT sheet delivery.
- **Bad-palette negative fixture: exit 1**, `SPEC palette mismatch against SVG kit`.
- Three offline tests: PASS (valid source inputs, invalid palette, absent sheets).
- Ruff lint and format: PASS. Git diff: PASS. Code-slop: PASS, score 100,
  zero errors/warnings/clones. Alignment: PASS, zero errors/warnings.
  Commit hooks remain enabled; no test or linter suppression was added.

All five GPT sheets remain absent. The row is blocked before attach/upload/send,
not visually complete. S1 sends **0/8**, no retries or recovery mutations.
PR API readback: OPEN / DRAFT, assigned phsb5321, no checks reported (not green CI).
Main remains the original SVG-kit base; no merge was attempted.
GitButler refused this unconfigured linked worktree; worktree-local Git fallback
retained normal hooks and did not modify the shared main checkout.

Private observed-result extract stays under ignored owner-only `.private/`;
it is labelled as an extract, not a fabricated complete transport receipt.
No merge, production deploy, publication, avatar or new brand-master approval.

---

# Update — 31/10/2026 13:30 BRT: four of five sheets generated, quota stop

The 30/10 hold (`invalid browser endpoint record`) is stale and was not reused.
Live route this run: `browser_identities` reported `chatgpt-c` **ready / headed**
on the Nix.Server fleet; the installed `gpt-image` shim attached through
`interactive.attach` to the warm browser (CDP forward `127.0.0.1:9615`, verified
`200` on `/json/version` before each send). No local browser, no API path, no
restart or reset of the shared browser.

## What exists now (hashes are of the committed bytes)

| Sheet | Size | SHA-256 | Send | Drift summary |
| --- | --- | --- | --- | --- |
| `turnaround.png` | 2048×768 | `f37fbfebb1bf3f6ba68641eb1076e9dd4167ba0ccf8556c7b3ae155511b83ff1` | 1 | four views; 3/4 repeats the front angle; soft shadow + floor gradient break flat-fill; pupils ~0.09H vs 0.05625H; side view drops a fang |
| `expressions.png` | 1536×1024 | `4c6cb9f0a2a1e989a70ec024b69d51e6aec1c1cc6bd263b627d883f5f1ad24a2` | 2 | six panels; asleep has zero mauve; fang order not consistent; pupils oversized |
| `poses.png` | 1536×1024 | `a172161cb3e558c4384645f13d433cd87dc91370a0848d7660a942b7d421652a` | 3 | typing/thinking/celebrating/asleep present; celebrating shows 4–5 claws per hand; dimensional keycaps |
| `hands-keyboard.png` | 1213×1296 | `b4918421b24763f4dcd78c943a5f998dc496162fe31ca81af86cae5b40db767f` | 4 | three separated claws in both close-ups; "back" panel is a 3/4 back; keycaps dimensional |
| `colour-material.png` | — | — | 5 (refused) | NOT GENERATED |

Per-file provenance (`<sheet>.provenance.json`) carries identity, timestamp,
prompt and reference hashes, the sanitized receipt (`status: ok`,
`send_confirmed: true`, byte count) and `receipt_sha256` binding the private raw
receipt. Raw receipts — which contain the conversation and blob URLs — stay in
the ignored, owner-only `.private/receipts/`.

## Sends used: 5 of 8

1. `20261031T131349914` ok · 2. `20261031T131649250` ok (attempt 1 never sent:
`/library`, `send_confirmed=false`) · 3. `20261031T131759825` ok ·
4. `20261031T132154223` ok (attempt 1 died on `ECONNREFUSED 9615` during a tunnel
reconcile; nothing sent) · 5. `20261031T132559121` **refused by quota**.

## Exact blocker

The account is not on the Pro plan the pipeline assumes: the page shows a
**Free** badge and, after send 5, *"You've hit the free plan limit for image
generations requests. You can create more images when the limit resets in 3
hours"* plus *"I wasn't able to invoke the image-generation tool, so the
requested character-reference sheet was not created."* Reset ≈ **16:25 BRT**.
The refused send confirmed it was delivered but produced no image, so
`colour-material.png` does not exist and no sidecar was fabricated for it.
This is an account-entitlement finding for the lead, not a code defect: the
pipeline itself worked four times in a row.

## 2D ↔ 3D parity (re-derived from wT:p6 `model/params.json`)

PR #14 merged to main as `ff1abc0` while this row ran, so the 3D single source of
truth now sits beside this worktree. `check.py` re-derives every 2D value from it
and **fails if they disagree** (new `fixtures/bad-geometry.json` plus a unit test
that mutates the 3D eye radius to prove the gate bites):

- head unit 80, head 1.20H, ear span 2.45H, tips ±1.225H / −0.85H, eye 0.1375H,
  pupil 0.05625H, torso 1.10H × 0.65H, 3 fangs, 2 eyes, 2 pupils, 8×3 keys — all
  agree exactly.
- 3D radii are the 2D half-strokes: brows 2.6 vs 2.5, claws 1.8 vs 1.75, output
  2.2 vs 2.0, keyboard rim 2.5 exact.
- **One real divergence:** the hero keyboard outline is 180 units wide at the
  front and 156 at the back (2.25H / 1.95H), while the 3D deck is authored at
  156 / 136 with only 5.5 units of rim per side. Shortfall: **6.5 units per side
  at the front, 4.5 at the back.** Recorded in `SPEC.md` and asserted in
  `check.py`; S2 must widen the rim (or the deck) rather than normalise 2.25H away.

## Gates actually run

- `check.py --spec-only` → **exit 0** (palette, proportions, reference hashes,
  privacy; explicitly not sheet delivery).
- `check.py` (default) → **exit 1**, `FAIL: Missing: colour-material.png`.
  The gate is not weakened for the quota stop.
- `check.py --spec-only --spec-json fixtures/bad-palette.json` → **exit 1**.
- `unittest` (4 tests, incl. the geometry-drift test) → **OK**.

No merge, deploy, publication, account/billing change, foreign Project edit or
new brand master. PR stayed draft and assigned to `phsb5321`.

---

# Update — 31/10/2026 16:30 BRT: fifth sheet delivered, gate green

The quota reset at ~16:26 as the account predicted. One send finished the set.

- `colour-material.png` 1536×1024, SHA-256
  `81eb24688708cf7bb0a7344a176f90ca731c92362644a6b3d90d84a52668ca85`,
  send 6 of the 8-send ceiling, `send_confirmed: true`, receipt
  `05-colour-material.attempt3.json`.
- **`check.py` (default) → exit 0**: `PASS: five reference-anchored GPT model
  sheets and reproducible provenance.`
- `check.py --spec-only` → exit 0; bad-palette fixture → exit 1; 4 offline
  tests → OK.
- Drift for this sheet, from inspection rather than from the prompt's intent: two
  figures instead of one neutral character, six unlabelled swatch chips (correct:
  roles are typeset outside the art), claw counts reaching four or five per hand,
  a plain slab keyboard, and pupils again ~0.09H.

Sends used: **6/8**. No further image work is planned; the remaining two are
reserve for a concrete defect, not for a nicer sheet.
