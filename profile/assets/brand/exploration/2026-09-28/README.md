# Programming gremlin — GPT Image Lab directions

28/09/2026 · image-lab · **Exploration only, not approved brand masters.**

## Spec

Produce one original programming-gremlin anchor and two recognizably anchored variants:
a wide wordless hero and a square avatar. Preserve green skin, pointed mischievous ears,
fanged grin, keyboard/programming, and restrained mauve output. Keep the Catppuccin
organization identity separate from the Lectrice/Proso bird. No generated lettering,
film/game character imitation, production asset replacement, or organization settings changes.

Acceptance: three fresh image results at most; inspect the actual pixels; immutable
source images, exact prompts, sanitized receipts, SHA-256 lineage, labelled contact sheet,
and a runnable integrity check. Record limitations honestly; no model-ID guesses.

## Plan

1. Use the merged `.github#8` hero/model-sheet rasters at base `6488088`. Compose them
   into one role-assigned reference board (pixel composition, not new drawing).
2. Use `gpt-image` on the existing server-hosted `chatgpt-c` identity through the shim's
   queue lock. Each invocation submits and collects in one attach. Stop on an ambiguous
   send; no retries, draft clearing, identity changes, or API credit spending.
3. Start an isolated fresh thread. Live `project.py` only edits an existing project's
   instructions and sends a first prompt; it has no project-name/create implementation.
   Do not invoke it against somebody else's project or let that gap block this round.
4. After the anchor, use that exact image as `--ref`, an explicit PRESERVE/CHANGE split,
   and the same owned thread for both edits. Three sends total.
5. Store raw receipts privately in ignored `.private/` (mode 0700), and allowlist only
   safe metadata into public sidecars. Never publish signed CDN or conversation URLs.
6. Render the labelled proof deterministically; labels are typeset, not generated.
   Add a local provenance check, then PR assigned to the verified personal account.

## Tasks

- [x] T1: Read fleet/pipeline methods, Proso editorial lane and Lectrice REIMAGINE report.
- [x] T2: Inspect fleet status, processes/lock, current remote, and create owned worktree.
- [x] T3a: Save all three prompts and pin the reference-source hashes.
- [ ] T3b: Produce the anchor — **blocked before upload/send by CDP attach failure**.
- [ ] T4: Produce the wide hero and square avatar as anchored edits; neither attempted.
- [ ] T5: Inspect fresh pixels, sanitize success receipts and render the contact sheet.
- [x] T6a: Preserve failure receipts privately; syntax-check the provenance gate and
  prove it rejects absent outputs; write the coordinator report.
- [ ] T6b: Run the positive provenance gate and open an assigned PR after genuine images exist.

## Blocked round — 20:14 BRT

One canonical `gpt-image` invocation failed during `BrowserType.connect_over_cdp`,
before reference upload or prompt send. A read-only probe on the documented alternate
identity reproduced `Network.setCacheDisabled: Internal server error, session closed`.
**Zero image sends and zero generated assets.** No browser restart, relogin, draft clearing,
blind resend, or substitute illustration. Backend model and authenticated account were
not observable because attach never completed. `generation-status.json` is sanitized
failure evidence, not an image-success sidecar. `check.py` intentionally fails until the
three real results exist. The prepared reference board is never the anchor.

## Method lineage

Proso's editorial-art lane supplies the prompt/identity/hash sidecar contract; Lectrice's
REIMAGINE round supplies role-assigned references, explicit preserve/change constraints,
size proofs and an honest drift register. These methods do not transfer their bird,
paper/ink/vermilion palette, or private project material into this gremlin direction.

Canonical vector masters remain under `../../mascot/`; nothing in this folder replaces them.
