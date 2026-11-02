#!/usr/bin/env python3
"""Org repo-security settings gate for the yolo-labz repositories.

Reports visibility, secret scanning, push protection, default-branch ruleset,
dependabot config and recent CI for every repo, and fails on the gaps this
account can actually close. Things the free plan refuses on private repos
(rulesets, scanning, push protection) are marked `plan-ceiling` instead of
counted as drift — the full rationale and baseline table live in the README.

Only `gh api` is used: no direct HTTP, no browser, no third-party package.

Usage
  python3 scripts/check-repo-settings.py [--org yolo-labz] [--json-log PATH]
                                         [--offline DIR] [--max-age-days N]

  --offline DIR   read one `<repo>.json` snapshot per repo from DIR instead of
                  calling gh (used by the tests).

Exit 0 = at baseline, 1 = violations remain, 2 = usage/API error.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from org_api import ApiError, api_get, api_optional, gh

ORG = "yolo-labz"
MAX_AGE_DAYS = 30
PLAN_CEILING_MARK = "Upgrade to GitHub Pro"


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Finding:
    repo: str
    rule: str
    level: str  # "error" | "plan-ceiling" | "note"
    message: str

    def render(self) -> str:
        return f"  [{self.level}] {self.repo}: {self.rule}: {self.message}"


@dataclass
class RepoState:
    name: str
    private: bool = False
    archived: bool = False
    default_branch: str = "main"
    secret_scanning: bool = False
    push_protection: bool = False
    ruleset: str | None = None  # name of the protecting ruleset
    ruleset_blocked: str | None = None  # "plan-ceiling" when the API refuses
    updater: str | None = None  # "dependabot" | "renovate"
    last_success: datetime | None = None
    max_age_days: int = MAX_AGE_DAYS

    @property
    def visibility(self) -> str:
        return "private" if self.private else "public"

    @property
    def ci(self) -> str:
        if self.last_success is None:
            return "none"
        age = datetime.now(timezone.utc) - self.last_success
        return "fresh" if age <= timedelta(days=self.max_age_days) else f"stale({age.days}d)"

    def row(self) -> str:
        ruleset = self.ruleset or (
            "plan-ceiling" if self.ruleset_blocked else ("-" if self.private else "MISSING")
        )
        return (
            f"  {self.name:28.28} {self.visibility:7} "
            f"{yn(self.secret_scanning):4} {yn(self.push_protection):4} "
            f"{ruleset:16.16} {self.updater or '-':10.10} {self.ci}"
        )


def yn(flag: bool) -> str:
    return "yes" if flag else "no"


# --------------------------------------------------------------------------- #
# rules
# --------------------------------------------------------------------------- #


def check(state: RepoState) -> list[Finding]:
    """Everything this repo is missing, split by how actionable it is."""
    findings: list[Finding] = []
    ceiling = state.private  # the free plan refuses these three on private repos

    for rule, enabled, label in (
        ("secret_scanning", state.secret_scanning, "secret scanning"),
        ("push_protection", state.push_protection, "push protection"),
    ):
        if enabled:
            continue
        if ceiling:
            findings.append(
                Finding(
                    state.name,
                    rule,
                    "plan-ceiling",
                    f"{label} unavailable on a private repo (free plan)",
                )
            )
        else:
            findings.append(Finding(state.name, rule, "error", f"{label} disabled"))

    if state.ruleset is None:
        if ceiling:
            findings.append(
                Finding(
                    state.name,
                    "ruleset",
                    "plan-ceiling",
                    "rulesets unavailable on a private repo (free plan)",
                )
            )
        else:
            findings.append(
                Finding(
                    state.name,
                    "ruleset",
                    "error",
                    f"no active ruleset on {state.default_branch}",
                )
            )

    if state.updater is None:
        findings.append(
            Finding(
                state.name,
                "updater",
                "error",
                "no .github/dependabot.yml and no renovate config",
            )
        )

    if state.ci == "none":
        findings.append(
            Finding(state.name, "ci", "note", "no successful workflow run ever")
        )
    elif state.ci.startswith("stale"):
        findings.append(
            Finding(state.name, "ci", "note", f"last success {state.ci[6:-1]}")
        )
    return findings


# --------------------------------------------------------------------------- #
# the outside world (only through gh)
# --------------------------------------------------------------------------- #


def covers_default_branch(detail: dict, default_branch: str) -> bool:
    """True when this ruleset actually applies to the default branch.

    Rulesets express the target three ways in the wild: `~DEFAULT_BRANCH`,
    `~ALL`, or the literal `refs/heads/<branch>` (claude-mac-chrome uses the
    last one). An empty include list means "all branches", subject to excludes.
    """
    conditions = (detail.get("conditions") or {}).get("ref_name") or {}
    include = conditions.get("include") or []
    exclude = conditions.get("exclude") or []
    ref = f"refs/heads/{default_branch}"
    if ref in exclude or "~DEFAULT_BRANCH" in exclude:
        return False
    if not include:
        return True
    return any(entry in ("~DEFAULT_BRANCH", "~ALL", ref) for entry in include)


def fetch_rulesets(
    org: str, repo: str, default_branch: str
) -> tuple[str | None, str | None]:
    """(protecting ruleset name, plan-ceiling reason)."""
    listing, error = api_optional(f"repos/{org}/{repo}/rulesets")
    if listing is None:
        if PLAN_CEILING_MARK in error:
            return None, "plan-ceiling"
        raise ApiError(f"rulesets {repo}: {error}")
    for summary in listing if isinstance(listing, list) else []:
        if summary.get("target") != "branch" or summary.get("enforcement") != "active":
            continue
        detail, detail_error = api_optional(
            f"repos/{org}/{repo}/rulesets/{summary['id']}"
        )
        if detail is None:
            raise ApiError(f"ruleset {repo}/{summary['id']}: {detail_error}")
        if covers_default_branch(detail, default_branch):
            return summary.get("name") or str(summary["id"]), None
    return None, None


UPDATE_CONFIGS = (
    (".github/dependabot.yml", "dependabot"),
    (".github/dependabot.yaml", "dependabot"),
    ("renovate.json", "renovate"),
    (".github/renovate.json", "renovate"),
    (".renovaterc", "renovate"),
    (".renovaterc.json", "renovate"),
)


def fetch_updater(org: str, repo: str) -> str | None:
    """Which dependency updater owns this repo, if any.

    Dependabot is not the only correct answer: `wa` and `zellij-vertical-tabs`
    run Renovate, and a second updater there would duplicate every PR. The gate
    asks "is anything maintaining dependencies?", not "is the file called
    dependabot.yml?".
    """
    for name, owner in UPDATE_CONFIGS:
        payload, _ = api_optional(f"repos/{org}/{repo}/contents/{name}")
        if payload is not None:
            return owner
    return None


def fetch_last_success(org: str, repo: str, max_age_days: int) -> datetime | None:
    since = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    payload, _ = api_optional(
        f"repos/{org}/{repo}/actions/runs?status=success&per_page=1&created=>={since}"
    )
    runs = (payload or {}).get("workflow_runs") or []
    if not runs:
        return None
    stamp = runs[0].get("created_at") or runs[0].get("updated_at")
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None


def state_from(
    payload: dict,
    *,
    ruleset: str | None,
    blocked: str | None,
    updater: str | None,
    last_success: datetime | None,
    max_age_days: int,
) -> RepoState:
    """One RepoState from an API/fixture repo payload plus its side data."""
    analysis = payload.get("security_and_analysis") or {}
    return RepoState(
        name=payload["name"],
        private=bool(payload.get("private")),
        archived=bool(payload.get("archived")),
        default_branch=payload.get("default_branch") or "main",
        secret_scanning=((analysis.get("secret_scanning") or {}).get("status")) == "enabled",
        push_protection=(
            (analysis.get("secret_scanning_push_protection") or {}).get("status")
        )
        == "enabled",
        ruleset=ruleset,
        ruleset_blocked=blocked,
        updater=updater,
        last_success=last_success,
        max_age_days=max_age_days,
    )


def live_states(org: str, max_age_days: int) -> list[RepoState]:
    payload = api_get(f"orgs/{org}/repos?per_page=100")
    states: list[RepoState] = []
    for item in payload:
        if item.get("archived"):
            continue
        branch = item.get("default_branch") or "main"
        ruleset, blocked = fetch_rulesets(org, item["name"], branch)
        states.append(
            state_from(
                item,
                ruleset=ruleset,
                blocked=blocked,
                updater=fetch_updater(org, item["name"]),
                last_success=fetch_last_success(org, item["name"], max_age_days),
                max_age_days=max_age_days,
            )
        )
    return states


def fixture_states(directory: Path, max_age_days: int) -> list[RepoState]:
    states: list[RepoState] = []
    for path in sorted(directory.glob("*.json")):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        repo = snapshot.get("repo") or {}
        if repo.get("archived"):
            continue
        rulesets = snapshot.get("rulesets") or {}
        ruleset = None
        blocked = None
        if isinstance(rulesets, dict):
            blocked = (
                "plan-ceiling" if PLAN_CEILING_MARK in json.dumps(rulesets) else None
            )
        else:
            for summary in rulesets:
                if summary.get("target") == "branch" and summary.get("enforcement") == "active":
                    ruleset = summary.get("name")
        last_success = snapshot.get("last_success")
        states.append(
            state_from(
                repo,
                ruleset=ruleset,
                blocked=blocked,
                updater=snapshot.get("updater"),
                last_success=(
                    datetime.fromisoformat(last_success.replace("Z", "+00:00"))
                    if last_success
                    else None
                ),
                max_age_days=max_age_days,
            )
        )
    return states


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def run(args: argparse.Namespace) -> int:
    states = (
        fixture_states(Path(args.offline), args.max_age_days)
        if args.offline
        else live_states(args.org, args.max_age_days)
    )
    findings: list[Finding] = []
    for state in states:
        findings += check(state)

    errors = [f for f in findings if f.level == "error"]
    ceilings = [f for f in findings if f.level == "plan-ceiling"]
    notes = [f for f in findings if f.level == "note"]

    print(f"== repo settings: {len(states)} active repos in {args.org}")
    print(f"  {'repo':28.28} {'vis':7} {'ss':4} {'pp':4} {'ruleset':16.16} {'updater':10.10} ci")
    for state in states:
        print(state.row())

    if errors:
        print("\n-- violations (fixable on this plan):")
        for finding in errors:
            print(finding.render())
    if ceilings:
        print(f"\n-- plan-ceiling ({len(ceilings)} findings, not counted as drift):")
        for finding in ceilings:
            print(finding.render())
    if notes:
        print(f"\n-- notes ({len(notes)}):")
        for finding in notes:
            print(finding.render())

    counts = Counter(finding.rule for finding in errors)
    summary = ", ".join(f"{rule}={n}" for rule, n in sorted(counts.items())) or "none"
    print(
        f"\n-- violations: {len(errors)} ({summary}); "
        f"plan-ceiling: {len(ceilings)}; notes: {len(notes)}"
    )
    print("RESULT: " + ("FAIL" if errors else "PASS"))

    if args.json_log:
        entries = [
            {
                "repo": state.name,
                "visibility": state.visibility,
                "secret_scanning": state.secret_scanning,
                "push_protection": state.push_protection,
                "ruleset": state.ruleset,
                "ruleset_blocked": state.ruleset_blocked,
                "updater": state.updater,
                "ci": state.ci,
            }
            for state in states
        ]
        Path(args.json_log).write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        print(f"-- snapshot: {args.json_log} ({len(entries)} repos)")

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", default=ORG, help="organisation to audit")
    parser.add_argument("--json-log", default=None, help="write a JSON snapshot")
    parser.add_argument("--offline", default=None, help="fixture directory instead of gh")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=MAX_AGE_DAYS,
        help="how old a successful run may be before it is a note",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except ApiError as error:
        sys.stderr.write(f"check-repo-settings: {error}\n")
        raise SystemExit(2) from error


if __name__ == "__main__":
    raise SystemExit(main())
