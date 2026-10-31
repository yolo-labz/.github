#!/usr/bin/env python3
"""Org metadata gate for the public yolo-labz repositories.

Checks every public, non-archived repository for:

  1. description   non-empty; the six flagships must carry the exact sentence
                   from docs/brand-positioning.md (the doc stays the source).
  2. homepage      may be empty, but if set it must be an https site URL and not
                   a github.com repository link (a self-link carries nothing).
                   Repos in SITE_HOMEPAGES must match the mapped URL.
  3. topics        at least three, each lowercase-hyphenated and unique.
  4. has_issues    enabled — the repo takes bug reports.
  5. readme        the README links back to the org (github.com/yolo-labz).

Archived repositories are exempt: their metadata is historical.

Only `gh api` is used — no direct HTTP, no browser. `--fix` applies the
mechanical repairs (description, homepage, topics, has_issues) through the same
CLI and records every before/after pair to `--json-log`. README repairs are a
code change, so they are reported, never patched here.

Usage
  python3 scripts/check-repo-metadata.py [--org yolo-labz] [--fix]
                                        [--json-log PATH] [--offline DIR]

  --offline DIR   read repo payloads from DIR/<repo>.json plus DIR/<repo>.md
                  instead of calling gh (used by the tests).

Exit 0 = compliant, 1 = violations remain, 2 = usage/API error.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ORG = "yolo-labz"
CLAIMS_DOC = "docs/brand-positioning.md"
SITE_ROOT = "github.com/yolo-labz"

# Repos with a real site; the homepage must be that site.
SITE_HOMEPAGES = {
    "portfolio": "https://portfolio.home301server.com.br",
}

# Topics for repos that had fewer than three, each taken from that repo's own
# description and stack. Curated, not inferred at runtime.
TOPICS = {
    "cosyvoice.cpp": ["tts", "speech-synthesis", "cpp"],
    "craftcut": ["video-editing", "cli", "opentimelineio"],
    "diploma-equivalence": ["automation", "scraping", "education"],
    "glm-critic": ["llm", "evaluation", "rubric"],
    "n8n-flows": ["n8n", "workflow-automation", "groq"],
    "n8n-nodes-wa": ["n8n", "whatsapp", "automation"],
    "step-audio-editx.cpp": ["tts", "ggml", "vulkan"],
    "zellij-automation": ["zellij", "shell", "automation"],
}

MIN_TOPICS = 3
TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")
FLAGSHIP_ROW_RE = re.compile(
    r"^\|\s*\[([a-z0-9.-]+)\]\[[^\]]*\]\s*\|\s*(.+?)\s*\|", re.MULTILINE
)


@dataclass(frozen=True)
class Finding:
    repo: str
    rule: str
    level: str  # "error" | "note"
    message: str

    def render(self) -> str:
        return f"  [{self.level}] {self.repo}: {self.rule}: {self.message}"


@dataclass
class Repo:
    name: str
    archived: bool = False
    private: bool = False
    description: str | None = None
    homepage: str | None = None
    topics: list[str] = field(default_factory=list)
    has_issues: bool = True
    readme: str = ""

    @classmethod
    def from_payload(cls, payload: dict) -> Repo:
        return cls(
            name=payload["name"],
            archived=bool(payload.get("archived")),
            private=bool(payload.get("private")),
            description=(payload.get("description") or "").strip() or None,
            homepage=(payload.get("homepage") or "").strip() or None,
            topics=list(payload.get("topics") or []),
            has_issues=bool(payload.get("has_issues", True)),
        )


# --------------------------------------------------------------------------- #
# the outside world (only through gh)
# --------------------------------------------------------------------------- #


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def api_get(path: str) -> object:
    return json.loads(gh("api", path))


def api_patch(path: str, fields: dict) -> None:
    # -F gives gh its typed form: a bool becomes JSON true/false, a string stays
    # a string, and an empty homepage is sent as the empty string, not null.
    args = ["api", "-X", "PATCH", path]
    for key, value in fields.items():
        rendered = "true" if value is True else "false" if value is False else value
        args += ["-F", f"{key}={rendered}"]
    gh(*args)


def api_put_topics(repo: str, org: str, topics: list[str]) -> None:
    # The topics endpoint wants a JSON body; gh's -f would send the array as a
    # string and the API answers 422 "not an array".
    body = json.dumps({"names": topics})
    result = subprocess.run(
        [
            "gh",
            "api",
            "-X",
            "PUT",
            f"repos/{org}/{repo}/topics",
            "-H",
            "Accept: application/vnd.github+json",
            "--input",
            "-",
        ],
        input=body,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh topics PUT failed for {repo}: {result.stderr.strip()}")


class LogSink:
    """Append-only JSON evidence file, flushed after every repo.

    A crash mid-run must not lose the record of settings already changed on
    GitHub, so the file is rewritten after each repos' fixes.
    """

    def __init__(self, path: Path | None):
        self.path = path
        self.entries: list[dict] = []
        if path and path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                self.entries = loaded if isinstance(loaded, list) else []
            except json.JSONDecodeError:
                self.entries = []

    def flush(self, new: list[dict]) -> None:
        if self.path is None:
            return
        self.entries.extend(new)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.entries, indent=2) + "\n", encoding="utf-8"
        )

    def close(self, new: list[dict]) -> int:
        # Always leave a file behind: an empty array is evidence that the gate ran
        # and changed nothing.
        self.flush(new)
        return len(self.entries)


class LiveSource:
    """Real API access: repo payloads and README text."""

    def __init__(self, org: str):
        self.org = org

    def repos(self) -> list[Repo]:
        payload = api_get(f"orgs/{self.org}/repos?per_page=100&type=public")
        if not isinstance(payload, list):
            raise TypeError("org repo listing did not return a list")
        repos = []
        for item in payload:
            if not isinstance(item, dict):
                raise TypeError("org repo listing contained a non-object entry")
            repo = Repo.from_payload(item)
            repo.readme = self.readme(repo.name)
            repos.append(repo)
        return repos

    def readme(self, name: str) -> str:
        try:
            payload = api_get(f"repos/{self.org}/{name}/readme")
        except RuntimeError:
            return ""
        content = payload.get("content", "") if isinstance(payload, dict) else ""
        try:
            return base64.b64decode(content).decode("utf-8", "replace")
        except (ValueError, TypeError):
            return ""


class FixtureSource:
    """Offline source: DIR/<repo>.json plus optional DIR/<repo>.md."""

    def __init__(self, directory: Path):
        self.directory = directory

    def repos(self) -> list[Repo]:
        repos = []
        for path in sorted(self.directory.glob("*.json")):
            repo = Repo.from_payload(json.loads(path.read_text(encoding="utf-8")))
            readme = self.directory / f"{path.stem}.md"
            repo.readme = readme.read_text(encoding="utf-8") if readme.is_file() else ""
            repos.append(repo)
        return repos


# --------------------------------------------------------------------------- #
# rules
# --------------------------------------------------------------------------- #


def flagship_sentences(doc: Path) -> dict[str, str]:
    if not doc.is_file():
        return {}
    text = doc.read_text(encoding="utf-8")
    start = text.find("## Six flagship propositions")
    if start < 0:
        return {}
    section = text[start:]
    return {m.group(1): m.group(2).strip() for m in FLAGSHIP_ROW_RE.finditer(section)}


def normalize(text: str) -> str:
    return " ".join(text.split())


def check_repo(repo: Repo, flagships: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    if repo.archived:
        return [Finding(repo.name, "archived", "note", "exempt (archived)")]
    if repo.private:
        return [Finding(repo.name, "private", "note", "exempt (not public)")]

    def fail(rule: str, message: str) -> None:
        findings.append(Finding(repo.name, rule, "error", message))

    if not repo.description:
        fail("description", "missing")
    elif repo.name in flagships and normalize(repo.description) != normalize(
        flagships[repo.name]
    ):
        fail(
            "description",
            f"not the positioning one-liner ({repo.description[:60]!r})",
        )

    if repo.name in SITE_HOMEPAGES:
        expected = SITE_HOMEPAGES[repo.name]
        if (repo.homepage or "").rstrip("/") != expected.rstrip("/"):
            fail("homepage", f"expected {expected}, found {repo.homepage!r}")
    elif repo.homepage:
        if not repo.homepage.startswith("https://"):
            fail("homepage", f"not an https URL: {repo.homepage!r}")
        elif re.match(r"^https?://(www\.)?github\.com/", repo.homepage):
            fail("homepage", f"GitHub repository link, not a site: {repo.homepage!r}")

    bad_topics = [t for t in repo.topics if not TOPIC_RE.fullmatch(t)]
    if bad_topics:
        fail("topics", f"invalid topic names: {bad_topics}")
    if len(set(repo.topics)) < MIN_TOPICS:
        fail("topics", f"{len(set(repo.topics))} < {MIN_TOPICS}: {repo.topics}")

    if not repo.has_issues:
        fail("has_issues", "issues disabled")

    if not repo.readme.strip():
        fail("readme", "no README")
    elif SITE_ROOT not in repo.readme:
        fail("readme", f"README does not link back to {SITE_ROOT}")
    return findings


# --------------------------------------------------------------------------- #
# fixes
# --------------------------------------------------------------------------- #


def plan_fix(repo: Repo, flagships: dict[str, str]) -> dict:
    """The API fields this repo needs, and nothing else."""
    changes: dict = {}
    if repo.name in flagships and normalize(repo.description or "") != normalize(
        flagships[repo.name]
    ):
        changes["description"] = flagships[repo.name]
    elif not repo.description:
        changes["_description"] = "needs a human sentence"

    if repo.name in SITE_HOMEPAGES:
        if (repo.homepage or "").rstrip("/") != SITE_HOMEPAGES[repo.name].rstrip("/"):
            changes["homepage"] = SITE_HOMEPAGES[repo.name]
    elif repo.homepage and re.match(r"^https?://(www\.)?github\.com/", repo.homepage):
        changes["homepage"] = ""

    wanted = set(repo.topics) | set(TOPICS.get(repo.name, []))
    if len(wanted) < MIN_TOPICS or any(not TOPIC_RE.fullmatch(t) for t in wanted):
        # No curated set: a human must name the topics, the tool will not invent them.
        changes.setdefault("_manual", []).append("topics")
    elif wanted != set(repo.topics):
        changes["_topics"] = sorted(wanted)

    if not repo.has_issues:
        changes["has_issues"] = True
    return changes


def apply_fix(
    repo: Repo, changes: dict, org: str, log: list[dict], sink: LogSink | None = None
) -> None:
    """Apply the API part of a plan and record every before/after pair."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fields = {k: v for k, v in changes.items() if not k.startswith("_")}

    def record(field_name: str, before, after) -> None:
        log.append(
            {
                "at": stamp,
                "repo": repo.name,
                "field": field_name,
                "before": before,
                "after": after,
                "applied": True,
            }
        )

    if fields:
        api_patch(f"repos/{org}/{repo.name}", fields)
        for name, value in fields.items():
            record(name, getattr(repo, name) or "", value)
    if "_topics" in changes:
        api_put_topics(repo.name, org, changes["_topics"])
        record("topics", repo.topics, changes["_topics"])
    if sink is not None:
        sink.flush(log)


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def run(args: argparse.Namespace) -> int:
    root = Path(args.repo).resolve()
    flagships = flagship_sentences(root / CLAIMS_DOC)
    if not flagships:
        print(
            f"check-repo-metadata: no flagship table in {root / CLAIMS_DOC}",
            file=sys.stderr,
        )
        return 2
    source = FixtureSource(Path(args.offline)) if args.offline else LiveSource(args.org)
    repos = source.repos()

    log: list[dict] = []
    sink = LogSink(Path(args.json_log) if args.json_log else None)
    pending_readme: list[str] = []
    if args.fix:
        for repo in repos:
            if repo.archived or repo.private:
                continue
            changes = plan_fix(repo, flagships)
            manual = changes.get("_manual", [])
            if manual:
                print(f"manual {repo.name}: {manual} needs a human value")
            applied = {k: v for k, v in changes.items() if not k.startswith("_")}
            if applied or "_topics" in changes:
                apply_fix(repo, changes, args.org, log, sink=sink)
                print(
                    f"fixed {repo.name}: {sorted(applied) + (['topics'] if '_topics' in changes else [])}"
                )
        repos = source.repos()  # re-read so the report reflects the applied state

    findings: list[Finding] = []
    for repo in repos:
        findings += check_repo(repo, flagships)
    errors = [f for f in findings if f.level == "error"]
    notes = [f for f in findings if f.level != "error"]
    pending_readme = sorted({f.repo for f in errors if f.rule == "readme"})

    print(f"== repo metadata: {len(repos)} public repos in {args.org}")
    for finding in notes:
        print(finding.render())
    for finding in errors:
        print(finding.render())
    per_rule: dict[str, int] = {}
    for finding in errors:
        per_rule[finding.rule] = per_rule.get(finding.rule, 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in sorted(per_rule.items())) or "none"
    print(f"-- violations: {len(errors)} ({summary}); notes: {len(notes)}")
    if pending_readme:
        print(f"-- README repairs are code changes, not settings: {pending_readme}")
    print(f"-- settings changed in this run: {len(log)}")
    print("RESULT: " + ("FAIL" if errors else "PASS"))

    if args.json_log:
        total = sink.close(log)
        print(f"-- log: {args.json_log} ({total} entries)")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    here = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", default=ORG, help="organisation to audit")
    parser.add_argument(
        "--repo", default=str(here), help="checkout holding the claims doc"
    )
    parser.add_argument("--fix", action="store_true", help="apply setting repairs")
    parser.add_argument("--json-log", default=None)
    parser.add_argument(
        "--offline", default=None, help="fixture directory instead of gh"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
