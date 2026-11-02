# yolo-labz/.github

Org-level GitHub configuration for [yolo-labz](https://github.com/yolo-labz). Profile README at `profile/README.md` renders at the org page.

## What lives here

- `profile/README.md` — org-page hero (rendered at github.com/yolo-labz)
- (future) `ISSUE_TEMPLATE/` — org-default issue templates
- (future) `workflow-templates/` — reusable GHA workflow templates for plugin repos

## Checks

Both checkers are stdlib-only, read GitHub through `gh`, and accept `--offline <dir>` so the test
suite never touches the network (`python3 -m unittest -v` runs them all).

### Metadata — `scripts/check-repo-metadata.py`

Every public, non-archived repo: a description (the six flagships carry the sentence from
`docs/brand-positioning.md`), a sane homepage, at least three lowercase-hyphenated topics, issues
enabled, and a README that links back to the org. `--fix` applies the mechanical repairs and logs
every before/after pair.

### Security settings — `scripts/check-repo-settings.py`

The baseline is what this account can actually reach, not an abstract ideal — otherwise the report
cries wolf and the real drift hides in the noise:

| column | error (drift) | plan-ceiling (reported, never fails) |
|---|---|---|
| secret scanning | missing on a **public** repo | missing on a **private** repo |
| push protection | missing on a **public** repo | missing on a **private** repo |
| default-branch ruleset | missing on a **public** repo | missing on a **private** repo |
| dependabot config | missing on any repo | — |
| successful run ≤ 30 days | — (a `note`, not a failure) | — |

Why the ceiling is real: the free org plan answers `403 Upgrade to GitHub Pro or make this
repository public` for rulesets and secret scanning on private repos (measured 02/11/2026 on six
private repos). Flagging those as drift would produce 27 permanent errors that nobody can fix
without a plan or visibility change, so they are marked `plan-ceiling` in the table and counted
separately. Dependabot is free everywhere, so a missing config is always a violation. A dormant
repo with no recent run is inactive, not insecure — hence a note.

The check runs weekly (Monday 06:00 UTC) and on `workflow_dispatch` from `.github/workflows/profile-check.yml`;
its own steps are skipped on `pull_request`, where the org-wide token is unavailable.

## Updates

Single canonical edit point for org-level branding + supply-chain + cross-repo composition story. Change here propagates to every repo's GitHub-org-page surface.
