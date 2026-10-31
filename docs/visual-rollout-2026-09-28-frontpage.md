# Visual rollout — front-page integration

## Restored delivery — 30/10/2026

Draft [PR #9](https://github.com/yolo-labz/.github/pull/9), branch
`011-gremlin-frontpage`, assigned to **phsb5321**.
The former placeholder is now replaced with genuine, visibly labelled
**GPT-generated exploration**, not an approved brand master. No merge,
production deploy, blog/social publication, org-setting change or new image send.

Worktree: `../github-profile-011-gremlin-frontpage`.
Spec → plan → tasks: `specs/011-gremlin-frontpage/`.
Profile: `profile/README.md`. Evidence: `profile/assets/brand/rollout/`.

## Exact inputs and implementation

- Art producer: [draft PR #11](https://github.com/yolo-labz/.github/pull/11),
  source commit `637a7fbd3f47127f157d0e0dbbccc807bff57c87`.
  Exact original `gremlin-wide-hero.png` copied into `rollout/`;
  SHA-256 `da70db22366e8e849b22eb3e8c3dcd0ec53274135ee0bf1ee309cb2704a0d9f4`.
  `art-provenance.json` embeds the sanitized generation record, anchor hash,
  prompt/reference hashes and immutable public source link. No private receipt
  or conversation/CDN URL was copied. The source remains exploration.
- Copy source: [draft PR #10](https://github.com/yolo-labz/.github/pull/10),
  `fb4a5570fade07e9ea97fc85695fe95e22bb7a95`,
  `docs/brand-positioning.md`. Adopted its positioning and six qualified
  flagship choices: wa, chrome-bridge, claude-mac-chrome, fand, kokoro-speakd,
  anthropic-throttle-proxy. Limits remain visible; no blanket compliance,
  licensing, performance or quota claim.
- Existing outlined light/dark SVG wordmarks are byte-identical to merged #8.
  The image is an illustration, never the logo or a production avatar.
- Main freshly fetched: `64880882f235922007dd22a0cdb22c7ea5f09f83`.
  All three restored branches were **0 behind**; no merge/rebase or history
  rewrite was necessary. Existing residue directories were untouched.

## Executed verification

- `check.py` without `--draft`: PASS, exact six links, qualifiers, image
  alternatives, existing wordmark bytes and genuine art hash/provenance.
- GitHub Markdown API generated the sanitized preview; this is not the live org
  page. Main-based asset URLs intentionally become live only after an authorized
  future merge. Worktree bytes were embedded for the preview, not published.
- Actual existing NixOS server fleet rendering via supported
  `interactive.attach("brave-search")`: PASS at **1280 / 360**, light and dark.
  No local browser launch or network asset fetch. All images decoded,
  theme-specific wordmarks selected, no horizontal overflow, six live-text
  project choices survived image removal.
- Screenshots were opened and visually inspected together: readable heading,
  illustration, exploration label, three task groups and all six link choices;
  no clipped art or text. Art retains soft shading/keycap/anatomy drift.
- `verify.py`: PASS, all four screenshot hashes and PNG dimensions bound to
  exact profile SHA-256
  `09fbf802ea139a97daaee4d3ece83f0833963480b62498f4b65e7eda0d3b07e2`.
  Chrome excludes its 15px vertical scrollbar from full-page PNGs:
  1280 viewport → 1265×1471 PNG; 360 viewport → 345×2020 PNG.
- Four offline regression tests: PASS; modified PNG, stale profile and missing
  mobile/theme evidence are rejected. No browser used for these tests.
- Ruff lint/format: PASS. Repository slop/alignment and diff checks are recorded
  in the final delivery receipt. Earlier placeholder renders remain historical
  `draft-*.png`, never evidence for the integrated result.
- One Impeccable detector warning pairs a dark-theme muted token with the
  light-theme background. It is a cross-media false positive: actual CSS pairs
  are #59636e/#ffffff **6.11:1** and #9198a1/#0d1117 **6.50:1**.

### Browser-helper side effect (not hidden)

The canonical attach helper automatically opened a blank page and closed **one
frozen page target** during its pre-attach sanitizer. This was not an explicit
render command and was outside the intended owned-page-only scope. The render
itself used only its yielded page; no login, account setting, generation, manual
foreign-page action or explicit service restart was issued. No further browser
calls were made after observing this side effect. Do not interpret this run as
proof that the current helper is universally side-effect-free. See
`render-run.json`; raw target IDs and unrelated page contents are not published.

## Durable render paths

All under `profile/assets/brand/rollout/`:

- `exploration-integrated-1280-light.png`
- `exploration-integrated-1280-dark.png`
- `exploration-integrated-360-light.png`
- `exploration-integrated-360-dark.png`
- `checks.json`, `renders.json`, `art-provenance.json`, `render-run.json`
- `preview.html`, `preview-template.html`, `render.py`, `verify.py`,
  `test_verify.py` and `README.md` for reproduction.

## PR / CI and remaining gates

Existing #9 and #10 and new #11 are **OPEN / DRAFT**, assigned to phsb5321.
At recovery readback, all report **no CI checks**; absent checks are not green CI.
Main is `protected=false`, effective branch rules `[]`.
Published integration commit: `b40c4fa3eef48b5e67353299dec7da4b07ed2029`.
Exact content-head API readback is in `rollout/delivery-2026-10-30.json`;
its later report-only receipt commit does not change the rendered profile.
Code-slop: PASS, score 98, zero errors/clones; one nonblocking checker-function
length warning. Alignment: PASS, zero errors/warnings. Git diff check: PASS.
GitButler refused commits in this unconfigured restored linked worktree;
worktree-local Git fallback retained existing hooks and left shared main alone.

Operator gate remains **no merge, no production deployment or publication**,
regardless of local acceptance. Nothing in these checks approves the brand,
authorizes use as an org avatar or changes artwork rights.
No new workers, canonical vault edits, other-seat dispatches or residue cleanup.
Before merge, reversal is simply closing the draft PRs; main is unchanged.
