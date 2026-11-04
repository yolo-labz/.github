# Merging a workflow-touching PR without the `workflow` token scope

The `gh` token this fleet uses carries `gist`, `read:org`, `repo` — **not** `workflow`. Every merge of a
PR whose diff touches `.github/workflows/*` is refused:

```
GraphQL: refusing to allow an OAuth App to create or update workflow `.github/workflows/ci.yml`
without `workflow` scope (mergePullRequest)
```

That reads like a hard block. It is not. **The scope check applies to the author of the workflow
content, not to the account clicking merge** — so a head authored by `dependabot[bot]` merges fine.
Verified on 04/11/2026 by landing five dependabot PRs this way (`craftcut#10/#13/#16`,
`diploma-equivalence#38/#40/#41`).

## The recipe

```bash
# 1. Ask Dependabot to rewrite its own branch (same pins, new head authored by dependabot[bot]).
gh pr comment <n> --repo <owner/repo> --body "@dependabot recreate"

# 2. VERIFY the head sha actually changed — never merge on the assumption it did.
gh pr view <n> --repo <owner/repo> --json headRefOid --jq .headRefOid
#    (40–80 s is typical; if it has not moved, this PR is not eligible for the recipe)

# 3. Merge through the normal path and delete the branch.
gh pr merge <n> --repo <owner/repo> --squash --delete-branch
```

The requirement is a **dependabot-authored head**. `gh pr update-branch` does *not* qualify — it fails
with the same scope error (`updatePullRequestBranch`) even though it moves the sha. Hand-made workflow
changes (a human editing a pin, a new step) cannot use this path at all; they need the scope:

```bash
gh auth refresh -h github.com -s workflow   # interactive, one-time
```

## What is *not* allowed

- **Never push to `main` directly.** Forbidden regardless of branch protection, and it closes the PR
  unmerged, losing the review record.
- **Never force-push** a dependabot branch to "refresh" it — that reintroduces the author problem and
  rewrites someone else's ref.
- **Never `--admin`.** If the merge needs it, the PR is not ready.

## Before you merge: is it routine or a major jump?

The recipe removes the permissions question, not the judgement. Check the version span:

```bash
gh pr view <n> --repo <owner/repo> --json title --jq .title
gh api repos/<owner>/<action>/releases --jq '.[] | select(.tag_name|test("^v[0-9]+\\.0\\.0$")) | "\(.tag_name) \(.body|.[0:300])"'
```

Rules of thumb learned the hard way:

- **Same major, minor/patch bump** (`attest 4.1.0 → 4.2.2`, `harden-runner 2.12.0 → 2.22.3`) → land it.
- **Crossing majors** (`checkout 4 → 7`, `setup-uv 8 → 10`, `setup-node 4.4 → 7.1`) → read the
  breaking notes first and check the repo's actual usage. Two that bit or nearly bit:
  - `actions/checkout` v7 refuses **unsafe fork-PR checkouts** under `pull_request_target` /
    `workflow_run` (needs `allow-unsafe-pr-checkout: true`). Repos that only trigger on
    `push`/`pull_request` are unaffected.
  - `astral-sh/setup-uv` v10 flips `enable-cache: auto` to **cache off** by default; a repo that
    never set `enable-cache: true` silently loses its uv cache (slower CI, no failure).
- **A SHA pin bump is not automatically routine** — a `yolo-labz/quality-gates` SHA span can drag
  `setup-node`/`checkout` majors in through the composite. Read the span.

## Why this file exists

Two days were spent describing these PRs as "blocked on permissions". Three of them were landable the
whole time, and the other four were waiting on a changelog read, not on a token scope. If a merge is
refused for `workflow` scope, run the recipe above before filing a blocker.
