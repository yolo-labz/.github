# Plan — front-page integration

## Principles

Reuse, don't redesign: keep the shipped outlined wordmark SVGs and logo masters
byte-identical. Use Markdown plus GitHub-supported picture/img HTML, not a new
website, font download, decorative cards or browser account session.

## Implementation

1. Write the single-column profile with a wordmark picture (light/dark), a
   clearly labelled temporary hero slot and six project links in task groups.
2. Read p8's `../github-profile-012-brand-copy/docs/visual-rollout-2026-09-28-copy.md`;
   verify primary repo destinations and use its evidence-scoped copy.
3. Read p9's `../github-profile-010-gpt-gremlin-art/profile/assets/brand/exploration/2026-09-28/`
   plus producer report. Import the exact usable image into `rollout/`, preserve
   bytes, and record source commit/path, SHA-256 and actual generation evidence.
   Never infer GPT provenance from a filename. No generative or vector fallback.
4. Keep checks and their evidence under `profile/assets/brand/rollout/`: Python
   stdlib for local paths, alt text, provenance hashes and destination checks;
   GitHub Markdown API for sanitized rendered content; isolated headless Chrome
   for 1280px desktop and 360px mobile in both color schemes. Preview CSS emulates
   GitHub's content column only; label previews as local, not live org captures.
5. Commit and open an assigned PR via GitHub REST if GraphQL is rate-limited.
   Verify `phsb5321` through authenticated identity and assignability. Report
   checks honestly; zero configured checks is not green CI. Leave open if main
   is unprotected; do not change settings to manufacture a merge gate.

## Dependencies and simplifications

- Sole art producer: p9; sole claim-matrix owner: p8. Coordinate via owned files.
- No production build/deploy exists for this Markdown-only slice.
- No new project dependency: use installed Python/Chrome and GitHub's own Markdown
  renderer; browser-control library is optional tooling, not runtime code.
- Static layout initially; no unnecessary framework or design-token abstraction.
- Final-art acceptance fails closed while the hero is a placeholder.

## Initial observed gates — 28/09/2026

`origin/main = 64880882f235922007dd22a0cdb22c7ea5f09f83` (PR #8 merged).
GitHub REST returned `protected: false`, branch rules `[]`. PR #7 is OPEN and
explicitly held by the operator; do not touch it. Producer/copy worktrees exist
but their reports were not yet present at first inspection.
