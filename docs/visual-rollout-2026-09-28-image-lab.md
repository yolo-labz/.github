# Visual rollout — image-lab — 28/09/2026

## Explicit candidate resume — first anchor available

Candidate implementation `feb109d7` from draft NixOS #2505 is selected only per invocation.
The exact queue-locked 45-second owned-blank-page probe returned **ATTACH_OK, exit 0**,
with empty stderr. Authenticated canonical workflow then passed with an empty composer;
private screenshot shows **Instant / Pro**, not an exact image-backend model ID.

**First anchor for coordinator/consumers:**
`profile/assets/brand/exploration/2026-09-28/gremlin-anchor.png`

- SHA-256: `dcd882cb9d7f99316f0278d03c172a9f14135c195efe67556d451a9bd172baeb`
- 1254×1254 PNG, 1,091,450 bytes, exact downloaded bytes.
- Receipt: `status=ok`, `send_confirmed=true`; one actual image send so far.
- Pixel inspection: recognizable green pointed-ear gremlin, asymmetric grin/fangs,
  mauve pupil/output accents and blank-key keyboard. Drift: shallow shading and
  dimensional keycaps despite the flat brief; only two claws per hand clearly visible.
- Direction only, **not an approved master**. Two anchored edits are next.

The original blocked checkpoint below is retained as history, not current generation status.

## Historical checkpoint — 20:14 BRT

At this checkpoint there was no anchor and zero image sends; those failure receipts remain intact.

## Coordinator handoff (w8:p6; consumers p2/pA/pB)

- Repository: `yolo-labz/.github` (local checkout named `github-profile`).
- Worktree: `/home/notroot/Documents/Code/yolo-labz/github-profile-010-gpt-gremlin-art`.
- Branch: `010-gpt-gremlin-art`, based on freshly fetched `origin/main` `6488088` (`#8`).
- Owned outputs: `profile/assets/brand/exploration/2026-09-28/` and this report only.
- **First anchor path:** see the explicit candidate-resume section above.
  `refs/gremlin-reference-board.png` still only composes the pre-existing reference rasters.
- Local checkpoint: `docs(art): preserve blocked GPT gremlin brief` on the branch above.
  No push or PR: no successful image outputs to publish. Preparation remains incomplete.
- Canonical vault save-state, other seats, shared tooling and existing assets untouched.

## Spec → plan → tasks and prepared paths

The exploration `README.md` contains the bounded spec, technical plan and current tasks.
Relative to `profile/assets/brand/exploration/2026-09-28/`:

| Path | Actual state |
|---|---|
| `prompts/01-anchor.txt` | Original programming-gremlin brief; not submitted |
| `prompts/02-wide-hero.txt` | PRESERVE/CHANGE edit brief; not attempted |
| `prompts/03-square-avatar.txt` | PRESERVE/CHANGE edit brief; not attempted |
| `refs/gremlin-reference-board.png` | Pixel composition of merged hero/model sheet, not new art |
| `refs/sources.json` | Original repository paths, base commit and SHA-256s |
| `generation-status.json` | Sanitized failed-attempt evidence, not a success receipt |
| `check.py` | Offline provenance/lineage/privacy check; correctly rejects absent images |
| `.private/` | Durable ignored raw receipt/stderr and probe/negative-control evidence, mode 0700 |

Method was GPT anchor once, then two edits using that exact anchor as `--ref` in the
same owned thread, maximum three sends, each prompt and result in one attach, serialized
by the installed `gpt-image` shim's queue lock. No image send budget was consumed.
The live project verb edits an existing project's instructions but implements no
project creation; the planned isolated thread avoids altering unrelated projects.
Proso's provenance contract and Lectrice's role-assigned references/drift register informed
the process, not their bird or palette. No private vault material entered a model prompt.

## Evidence and reconciliation

1. Server `browser-fleetctl status chatgpt-c --json` returned ready/headed. Transport
   `/json/version` responded with Chrome `153.0.8010.47`, CDP `1.3`. Neither proves login.
2. A read-only canonical `_ui.session_page("chatgpt-c")` probe failed during attachment:
   `Network.setCacheDisabled: Internal server error, session closed`, then
   `BrowserType.connect_over_cdp: Connection closed while reading from the driver`.
3. One invocation of the installed `gpt-image` shim queued behind an existing caller
   and then returned the same typed attachment failure. No bypass or automatic retry.
   Raw `01-anchor.json` contains only `identity`, `prompt`, `stamp`, `status`, `detail`:
   there is **no `reference`, `send_confirmed`, or `conversation` field**. Together with
   the driver's execution order, this establishes failure before upload/send, not an
   ambiguous submitted image that should be regenerated.
4. Hypothesis: the attach failure was local to `chatgpt-c`. **Falsified** by a queue-locked,
   read-only probe of documented alternate `openai-platform`, which was also ready but
   failed with the same protocol error. No generation was attempted on that identity.
5. Exact underlying driver/browser cause remains unverified. Installed Patchright was
   `1.59.1`; changing shared tooling or restarting a browser is outside this slice and
   could interrupt another seat. No such action was taken. The image process exited.
6. The tool repository's main commit was `5c92c67`; its `_ui.py` had pre-existing local
   modifications, left untouched. Two later fetched commits concern login forms/worker
   exits and Miniflux credentials, not this measured protocol failure.

**Model/identity honesty:** `chatgpt-c` is the configured attempted identity, not an
observed logged-in account claim. Neither UI model label nor image-backend model ID was
observable: attachment failed before the authenticated-page sentinel. No guessed model ID.

## Tests

- `ast.parse(check.py)`, `ruff check`, `ruff format --check`: PASS.
- Staged-file privacy scan: PASS; `.private/` receipts excluded; no private/CDN URLs.
- Missing-result negative control: PASS — running
  `python3 profile/assets/brand/exploration/2026-09-28/check.py` exits nonzero with
  `Missing: 01-anchor.provenance.json`, as required. This is **not** a successful art gate.
- Reference-source hashes and the prepared PNG render are locally verifiable.
- Actual fresh-image inspection, positive provenance gate, and labelled generated-image
  contact sheet: **not run / impossible without generated images**.

## Pending gates and safe continuation

1. Coordinator routes the shared CDP attachment failure to the browser-tooling owner;
   repair/recovery must preserve other seats. Do not restart browsers from this slice.
2. Re-establish authenticated, empty-composer attach. Preserve all failed receipts and
   reconcile them before an explicitly resumed attempt; never delete guards to resend.
3. Generate the anchor and two anchored edits, inspect actual pixels, record observed
   identity/model limitations, hash each prompt/reference/result, build the labelled proof.
4. Pass `check.py`, then commit/push genuine outputs and open a PR assigned to **`phsb5321`**
   (verified by `/user` and repository `/assignees`). No publication or API credits.
5. Recheck repository permissions: `/branches/main` returned **`protected=false`** and
   `/rules/branches/main` returned **`[]`**. This is not the branch-protected self-merge
   class. Do not silently merge or change org/repo settings. No CI success is claimed.

No deployment, release, human send, foreign-draft clearing, global cleanup or shared
worktree pruning occurred. All deliverables/evidence are in this feature worktree, not scratch.
