# Visual rollout — frontpage

28/09/2026 · GPT/OpenAI integration · home-projects · coordinator w8:p6

## Live file handoff

**BLOCKED INTEGRATION DRAFT / PLACEHOLDER ONLY — 20:09 BRT.** Layout and
executable draft checks are delivered; final-art acceptance is **not complete**.
No final GPT artwork or approved brand master is claimed. Producer p9 still
reports its anchor in flight/queue, not a delivered image; this is a dependency
blocker, **not a claim that generation definitively failed**. No sibling was
interrupted and no edits left this seat's ownership surface.

- Worktree: `../github-profile-011-gremlin-frontpage`
- Branch: `011-gremlin-frontpage`, based on `6488088` (`origin/main`, PR #8).
- Profile: `profile/README.md`
- Spec/plan/tasks: `specs/011-gremlin-frontpage/`
- Integration assets, checks and previews: `profile/assets/brand/rollout/`
- Existing outlined wordmarks will be used unchanged; gremlin art is illustration,
  never a replacement logo. One image, no generated lettering, single-column
  layout and grouped live-text links. Planned renders: 1280px + 360px, light/dark.

## Producer inputs

- p9: exact usable GPT image plus generation provenance from
  `../github-profile-010-gpt-gremlin-art/profile/assets/brand/exploration/2026-09-28/`.
  Integration will copy bytes into owned `rollout/`, hash them and cite source.
  Current hero is an explicit text placeholder, not old SVG artwork.
- p8: claim matrix from
  `../github-profile-012-brand-copy/docs/visual-rollout-2026-09-28-copy.md`.
  Read p8's `docs/brand-positioning.md` and rollout claim-matrix handoff at
  19:55 BRT; the six flagships are
  **wa, chrome-bridge, claude-mac-chrome, fand, kokoro-speakd,
  anthropic-throttle-proxy**. The provisional reader-tool links were replaced,
  not copied from held PR #7. Platform/protocol/runtime qualifiers remain visible.
  No licensing/compliance or supply-chain blanket claims remain. Immutable copy
  source: `74f6cd01a4ce9a121f1fa15d7b0c270ab1caa9b3`,
  [copy PR #10](https://github.com/yolo-labz/.github/pull/10).

## Gates observed

- `gh api user`: `phsb5321`; repository assignee endpoint accepted that identity.
- REST `repos/yolo-labz/.github/branches/main`: `protected: false`.
- REST `repos/yolo-labz/.github/rules/branches/main`: `[]`.
- **Merge blocked unless a genuinely protected base is independently established.**
  No settings changes are authorized. Will open an assigned PR, not self-merge
  around this gate. PR #7 remains OPEN and untouched per the bounded instruction.
- No production deploy, release, avatar, pin, browser-account mutation, blog/social
  publication or human-directed send performed.

## Evidence / delivery

- Implemented single-column task groups and exact existing light/dark vector
  wordmarks in `profile/README.md`; no master or exploration changes.
- Runnable `profile/assets/brand/rollout/check.py` checks six links, local assets,
  wordmark byte identity, alt text, final-art checksum and placeholder refusal.
- `render.cjs` renders GitHub-sanitized Markdown, checks image decoding, theme
  selection and overflow at 1280/360px, then tests image-failure navigation.
- First four **draft-only** renders passed; final-art acceptance correctly
  refused the placeholder. These are not final-art or live GitHub screenshots.
- After adopting all six p8 flagship choices: seven public Markdown destinations
  returned HTTP 200; four fresh draft previews passed 1280/360px light/dark.
  `checks.json` and `renders.json` bind these receipts to the exact profile SHA-256.
- Layout/checks commit: `f95ccbfc90e8435f5a73c68e54d1fb786c19ba72`.
- PR: [yolo-labz/.github#9](https://github.com/yolo-labz/.github/pull/9), OPEN,
  **DRAFT**, assignee `phsb5321` (read back through REST).
- Evidence/report follow-up commit: `9344184554a27a7e5f6efc229812426698fedfcc`.
- Fresh CI observation at 20:09 BRT for that head: `check_runs.total_count=0`,
  combined status `pending` with `statuses=[]`. **No CI check has run/passed**;
  do not mistake the absent checks for green CI. The repo has no checked-in CI
  workflow; this slice does not add one or replace branch authorization.
- Fresh protection readback at 20:09 BRT: main still `6488088`,
  `protected=false`, rules `[]`. PR #7 is OPEN/unmerged at unchanged `9bfcb26`.
- Sole producer's public handoff inspected through 20:09 BRT, including a bounded
  six-minute file-only wait: reference board, prompts and integrity check exist;
  **no generated anchor/hero/provenance sidecar** exists. Its report remains
  `in progress`, with the anchor invocation in flight/queue and an earlier CDP
  attach failure. No browser attachment, retry or service change was made here.
- Therefore only **draft** render evidence is supplied. Actual final-image
  desktop/mobile acceptance cannot be truthfully marked passed.

## Render receipts and rerun

All paths below are relative to the repo. Screenshots were opened and inspected,
not inferred from tool exit status. Readable vector type, six links and three
sections remain visible without cropping or horizontal scrolling.

- `profile/assets/brand/rollout/draft-1280-light.png`
- `profile/assets/brand/rollout/draft-1280-dark.png`
- `profile/assets/brand/rollout/draft-360-light.png`
- `profile/assets/brand/rollout/draft-360-dark.png`
- `profile/assets/brand/rollout/checks.json`: seven HTTP 200 destinations,
  six exact flagship links, local SVGs and qualifiers checked.
- `profile/assets/brand/rollout/renders.json`: decoded theme-correct wordmarks,
  content widths 1280/360 equal to viewports; image-failure text navigation passes.

```sh
python3 profile/assets/brand/rollout/check.py --draft --online --preview
NODE_PATH=/home/notroot/Documents/Code/personal/proso/node_modules \
  node profile/assets/brand/rollout/render.cjs
git diff --check
# Expected to FAIL while art is absent; never describe --draft as this pass:
python3 profile/assets/brand/rollout/check.py
```

## First unfinished postcondition / coordinator handoff

1. **T05, producer dependency:** consume p9's actual usable GPT output only after
   inspecting its image and sanitized prompt/reference/generation proof. Copy
   exact bytes into owned `rollout/`; do not copy the existing reference board.
   Write `art-provenance.json` with `file`, `sha256`, `producer: p9`,
   `status: gpt-generated-exploration`, full `source_commit`, and
   `generation_evidence` pointing to immutable public proof. No signed URLs,
   account secrets, conversation URLs or private vault excerpts.
2. Replace the explicit placeholder with that illustration (not a logo), useful
   alt text and a visible GPT-generated exploration label. Keep unchanged vector
   wordmarks. Rerun **without `--draft`**, then render and inspect all four final
   previews. Only then can T05–T07 be completed and the PR leave draft status.
3. **Repository authorization blocker:** self-merge remains ineligible while main
   is unprotected. Coordinator/repository owner must handle any protection change
   through a separately authorized process. No settings mutation or bypass here.
   Preserve any checks/reviews subsequently configured; absent CI is not success.

No new workers or advisory model reviewer were launched. No canonical vault note
was edited. Reversal before merge: close this proposal, leaving main unchanged;
after a later authorized squash merge, use a normal `git revert <merge-sha>` PR.
All durable artifacts are in this feature worktree and pushed branch, not scratch.
