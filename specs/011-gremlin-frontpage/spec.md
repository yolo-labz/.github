# 011 — Gremlin front-page integration

Date: 28/09/2026 · Owner: frontpage · Coordinator: home-projects w8:p6

## Outcome

Visitors can identify Yolo Labz, understand its small tool family, and choose
among six flagship projects without scanning an infrastructure inventory.

## Requirements

- Show a restrained hero using the existing outlined wordmark, unchanged logo
  geometry, and one usable GPT-produced gremlin illustration from producer p9.
- Until the producer delivers verifiable art, show an explicit temporary
  placeholder. No old SVG, CSS drawing or unproved file may masquerade as GPT art.
- Preserve text navigation when images fail. Group exactly six flagship links
  by task; adopt only claims supported by copy seat p8's claim matrix.
- Keep Proso/Lectrice ownership and provider/platform limitations accurate.
  No org-wide compliance, licensing, SLSA, release or availability promises.
- Support light/dark themes and 360px mobile without horizontal overflow;
  meaningful image alternatives, readable type, no animation or raster logo.
- Distinguish an integration proposal from an approved brand master. GPT image
  provenance must be inspectable and must not claim editorial approval.
- Leave an executable local-asset/link/layout check and real desktop/mobile
  renders of the final integrated image. A placeholder preview is not acceptance.

## Boundaries

Own only `profile/README.md`, `profile/assets/brand/rollout/`, this spec directory,
and `docs/visual-rollout-2026-09-28-frontpage.md`. No exploration/master edits,
PR #7 adoption or mutation, other seats, org settings, publication, deployment,
new workers, credentials or billing changes. Base protection is a merge gate;
permission to push is not permission to merge an unprotected base.

## Acceptance scenarios

1. Desktop light/dark: correct wordmark variant; final art is visibly loaded;
   all six projects have clear live text labels and working destinations.
2. Mobile light/dark at 360px: no clipped hero, forced table width or horizontal
   scroll; links remain reachable and readable.
3. Image failure: text still identifies the org and explains the project choices.
4. Producer unavailable: draft stays explicitly blocked, final-art check fails,
   and report names the missing proof instead of asserting visual completion.
5. Delivery: assigned PR, actual checks reported, no self-merge unless branch
   protection and every real repository gate permit it.
