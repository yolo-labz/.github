# Visual rollout — frontpage

28/09/2026 · GPT/OpenAI integration · home-projects · coordinator w8:p6

## Live file handoff

**IN PROGRESS / PLACEHOLDER ONLY.** This is not final GPT artwork or an approved
brand master. Producer p9 and copy seat p8 can read this file without interrupting
this seat. No edits outside the assigned ownership surface.

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
  No licensing/compliance or supply-chain blanket claims remain.

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
- CI observation at 19:57 BRT for that head: `check_runs.total_count=0`,
  combined status `pending` with `statuses=[]`. **No CI check has run/passed**;
  do not mistake the absent checks for green CI.
- Final-art integration remains pending producer p9. No raw GPT output/proof
  is yet available on its public file handoff. This PR is intentionally draft
  while that postcondition is unfinished; no fallback art generation is allowed.
