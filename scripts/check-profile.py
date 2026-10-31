#!/usr/bin/env python3
"""Executable brand/profile gate for yolo-labz/.github.

Offline except for link resolution: the only network access is
raw.githubusercontent.com and api.github.com, bounded by --timeout. No browser,
and no fetch of arbitrary hosts (non-GitHub hosts are reported as skipped, never
silently passed).

Checks
  1. links      every Markdown link/image and HTML img/source in the profile
                README resolves: local path exists, remote returns HTTP 200.
  2. provenance every PNG under an exploration/ or model/ directory is named by
                a provenance JSON record in its own directory.
  3. privacy    no signed or private URLs (chatgpt.com/c/, oaiusercontent,
                ?sig=, ?se=) anywhere in tracked text.
  4. claims     banned unqualified claims from docs/brand-positioning.md are
                absent. The doc is the authority; when it is absent the check is
                reported SKIP unless --strict is passed (CI passes --strict, so a
                branch that drops the doc fails there).
  5. a11y       images in the profile README carry alt text and (HTML img) width.

Usage
  python3 scripts/check-profile.py [--repo PATH] [--offline] [--strict]
                                  [--readme PATH] [--claims-doc PATH]
                                  [--timeout SECONDS]

Exit 0 = pass, 1 = violation, 2 = usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_README = "profile/README.md"
CLAIMS_DOC = "docs/brand-positioning.md"
DEFAULT_TIMEOUT = 10.0

# Directories whose PNGs must be covered by a provenance record.
PROVENANCE_DIRS = ("exploration", "model")

# Signed/private URL shapes that must never reach a public commit.
PRIVATE_PATTERNS = (
    (re.compile(r"chatgpt\.com/c/", re.IGNORECASE), "private ChatGPT conversation URL"),
    (re.compile(r"oaiusercontent", re.IGNORECASE), "OpenAI ephemeral asset host"),
    (re.compile(r"[?&]sig=", re.IGNORECASE), "presigned URL signature parameter"),
    (re.compile(r"[?&]se=", re.IGNORECASE), "signed URL expiry parameter"),
)

# Line-scoped waiver for code that must name a forbidden pattern (a scanner).
PRIVACY_WAIVER = "profile-check: allow-private-pattern"

# The fixtures below intentionally hold every forbidden shape, so they are never
# linted; this script names the patterns for the same reason.
FIXTURE_PREFIX = "tests/fixtures/"
PRIVACY_EXEMPT = ("scripts/check-profile.py", FIXTURE_PREFIX)

TEXT_SUFFIXES = {
    ".md",
    ".json",
    ".txt",
    ".yml",
    ".yaml",
    ".html",
    ".htm",
    ".py",
    ".sh",
    ".cjs",
    ".js",
    ".ts",
    ".toml",
    ".css",
    ".svg",
}

# Banned unqualified claims, keyed to the claim-matrix IDs in
# docs/brand-positioning.md. Each phrase must be wrong on its own, not two words
# that happen to be fine in context.
BANNED_CLAIMS = (
    ("U01", re.compile(r"\bcompliance-grade\b", re.IGNORECASE)),
    ("U01", re.compile(r"\bcompliance[- ]certified\b", re.IGNORECASE)),
    ("U02", re.compile(r"\bsigned attestations\b", re.IGNORECASE)),
    ("U02", re.compile(r"\ball builds are reproducible\b", re.IGNORECASE)),
    ("U03", re.compile(r"Apache-2\.0 \+ MIT throughout", re.IGNORECASE)),
    ("U04", re.compile(r"\bpre-notarized\b", re.IGNORECASE)),
    ("U05", re.compile(r"\bzero (?:user )?configuration\b", re.IGNORECASE)),
    ("U05", re.compile(r"\bcannot select the wrong account\b", re.IGNORECASE)),
    ("U06", re.compile(r"\btrusted-event\b", re.IGNORECASE)),
    ("U06", re.compile(r"\bfirst-party events\b", re.IGNORECASE)),
    ("U07", re.compile(r"\bhard (?:rate|cost|spend) ceilings?\b", re.IGNORECASE)),
    ("U07", re.compile(r"\beliminat\w* upstream rate limits\b", re.IGNORECASE)),
    ("M01", re.compile(r"\bsub-?200\s*ms\b", re.IGNORECASE)),
    ("M01", re.compile(r"\bunder 200\s*ms\b", re.IGNORECASE)),
)

# A banned phrase is tolerated when the surrounding words negate it.
QUALIFIERS = ("not ", "never ", "unsupported", "needs measurement", "cannot ", "avoid")
QUALIFIER_WINDOW = 60

LINK_RE = re.compile(
    r"(!?)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?(?:\s+.*)?$", re.MULTILINE)
REF_USE_RE = re.compile(r"(!?)\[([^\]]*)\]\[([^\]]*)\]")
HTML_IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
HTML_SOURCE_RE = re.compile(r"<source\b([^>]*)>", re.IGNORECASE)
ATTR_RE = re.compile(
    r"([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))"
)


@dataclass(frozen=True)
class Finding:
    check: str
    level: str  # "error" | "warn" | "note"
    message: str

    def render(self) -> str:
        return f"  [{self.level}] {self.check}: {self.message}"


@dataclass(frozen=True)
class Link:
    source: Path
    line: int
    target: str
    is_image: bool = False
    alt: str = ""
    html_attrs: dict = field(default_factory=dict)
    html_tag: str = ""  # "img" | "source" | "" (markdown)


# --------------------------------------------------------------------------- #
# URL classification
# --------------------------------------------------------------------------- #


def classify_url(target: str) -> str:
    """Return one of: skip, local, raw, github, external."""
    lowered = target.strip().lower()
    if not lowered or lowered.startswith("#"):
        return "skip"
    if lowered.startswith(("mailto:", "tel:", "data:")):
        return "skip"
    if lowered.startswith("//"):
        lowered = "https:" + lowered
    parsed = urllib.parse.urlparse(lowered)
    if not parsed.scheme:
        return "local"
    if parsed.scheme not in ("http", "https"):
        return "skip"
    host = parsed.netloc.split(":")[0]
    if host in ("raw.githubusercontent.com", "objects.githubusercontent.com"):
        return "raw"
    if host in ("github.com", "www.github.com", "api.github.com"):
        return "github"
    return "external"


def github_api_target(url: str) -> str | None:
    """Map a github.com URL to the api.github.com endpoint that proves it."""
    parsed = urllib.parse.urlparse(url.strip())
    parts = [p for p in parsed.path.split("/") if p]
    if not parts:
        return None
    if len(parts) == 1:
        return f"/users/{parts[0]}"
    if parts[0] in ("orgs", "users"):
        return f"/{parts[0]}/{parts[1]}"
    owner, repo, rest = parts[0], parts[1], parts[2:]
    if not rest:
        return f"/repos/{owner}/{repo}"
    kind = rest[0]
    if kind in ("blob", "tree") and len(rest) >= 3:
        return f"/repos/{owner}/{repo}/contents/{'/'.join(rest[2:])}?ref={rest[1]}"
    if kind == "releases" and len(rest) >= 3 and rest[1] == "tag":
        return f"/repos/{owner}/{repo}/releases/tags/{rest[2]}"
    if kind == "releases":
        return f"/repos/{owner}/{repo}/releases"
    if kind in ("pull", "pulls", "issue", "issues") and len(rest) >= 2:
        return f"/repos/{owner}/{repo}/issues/{rest[1]}"
    if kind == "actions":
        return None  # no stable REST path for a run/job URL
    return f"/repos/{owner}/{repo}"


def remote_probe(url: str, kind: str) -> str | None:
    """The URL whose HTTP status proves the target exists, or None."""
    if kind == "raw":
        return url
    if kind != "github":
        return None
    endpoint = github_api_target(url)
    return None if endpoint is None else "https://api.github.com" + endpoint


# --------------------------------------------------------------------------- #
# extraction
# --------------------------------------------------------------------------- #


def attrs(raw: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for match in ATTR_RE.finditer(raw):
        value = next(g for g in match.groups()[1:] if g is not None)
        parsed[match.group(1).lower()] = value.strip()
    return parsed


def readme_links(readme: Path) -> list[Link]:
    text = readme.read_text(encoding="utf-8")

    def line_of(offset: int) -> int:
        return text.count("\n", 0, offset) + 1

    refs = {m.group(1).strip().lower(): m.group(2) for m in REF_DEF_RE.finditer(text)}
    links: list[Link] = []
    for match in LINK_RE.finditer(text):
        links.append(
            Link(
                readme,
                line_of(match.start()),
                match.group(3),
                bool(match.group(1)),
                match.group(2),
            )
        )
    for match in REF_USE_RE.finditer(text):
        key = (match.group(3) or match.group(2)).strip().lower()
        if key in refs:
            links.append(
                Link(
                    readme,
                    line_of(match.start()),
                    refs[key],
                    bool(match.group(1)),
                    match.group(2),
                )
            )
    for match in HTML_IMG_RE.finditer(text):
        parsed = attrs(match.group(1))
        if parsed.get("src"):
            links.append(
                Link(
                    readme,
                    line_of(match.start()),
                    parsed["src"],
                    True,
                    parsed.get("alt", ""),
                    parsed,
                    "img",
                )
            )
    for match in HTML_SOURCE_RE.finditer(text):
        parsed = attrs(match.group(1))
        for candidate in (parsed.get("srcset") or parsed.get("src") or "").split(","):
            target = candidate.strip().split(" ")[0]
            if target:
                links.append(
                    Link(
                        readme,
                        line_of(match.start()),
                        target,
                        True,
                        "",
                        parsed,
                        "source",
                    )
                )
    return links


def resolve_local(root: Path, source: Path, target: str) -> Path | None:
    path = urllib.parse.unquote(urllib.parse.urlparse(target).path)
    if not path:
        return None
    if path.startswith("/"):
        return root / path.lstrip("/")
    for candidate in ((source.parent / path).resolve(), (root / path).resolve()):
        if candidate.exists():
            return candidate
    return (source.parent / path).resolve()


# --------------------------------------------------------------------------- #
# network
# --------------------------------------------------------------------------- #


def http_status(url: str, token: str | None, timeout: float) -> int:
    headers = {
        "User-Agent": "yolo-labz-profile-check",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(1)
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"transport error for {url}: {exc}") from exc


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #


def repo_origin(root: Path) -> str | None:
    """`owner/repo` of the local origin remote, when the tree is a Git checkout."""
    try:
        url = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r"[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    return f"{match.group(1)}/{match.group(2)}" if match else None


def unpublished_asset_path(url: str, kind: str, origin: str | None) -> str | None:
    """Repo-relative path of a link that points at this repo's not-yet-published file.

    A front page may legitimately reference an asset that still lives on an open
    branch; that is a merge-order warning, not a dead link.
    """
    parts = [p for p in urllib.parse.urlparse(url).path.split("/") if p]
    if kind == "raw" and len(parts) >= 4:
        slug, rest = f"{parts[0]}/{parts[1]}", parts[3:]
    elif kind == "github" and len(parts) >= 5 and parts[2] in ("blob", "tree"):
        slug, rest = f"{parts[0]}/{parts[1]}", parts[4:]
    else:
        return None
    if origin and slug.lower() != origin.lower():
        return None
    return "/".join(rest)


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #


def check_links(
    root: Path,
    readme: Path,
    *,
    offline: bool,
    token: str | None,
    timeout: float,
    status=http_status,
) -> list[Finding]:
    findings: list[Finding] = []
    probed: dict[str, int] = {}
    origin = repo_origin(root)
    for link in readme_links(readme):
        kind = classify_url(link.target)
        where = f"{readme.name}:{link.line}"
        if kind == "skip":
            continue
        if kind == "local":
            resolved = resolve_local(root, readme, link.target)
            if resolved is None or not resolved.exists():
                findings.append(
                    Finding(
                        "links",
                        "error",
                        f"{where}: local target missing: {link.target}",
                    )
                )
            continue
        probe = remote_probe(link.target, kind)
        if probe is None:
            level = "note" if kind == "external" else "warn"
            findings.append(
                Finding(
                    "links",
                    level,
                    f"{where}: not verifiable under the GitHub-only rule: "
                    f"{link.target}",
                )
            )
            continue
        if offline:
            findings.append(
                Finding(
                    "links",
                    "note",
                    f"{where}: remote not probed (--offline): {link.target}",
                )
            )
            continue
        if probe not in probed:
            try:
                probed[probe] = status(probe, token, timeout)
            except RuntimeError as exc:
                findings.append(Finding("links", "warn", f"{where}: {exc}"))
                continue
        code = probed[probe]
        if code == 200:
            continue
        if code == 404:
            pending = unpublished_asset_path(link.target, kind, origin)
            if pending and (root / pending).is_file():
                findings.append(
                    Finding(
                        "links",
                        "warn",
                        f"{where}: not published yet (HTTP 404), but {pending} is in "
                        f"this tree: merge the asset before the consumer",
                    )
                )
                continue
        if code in (403, 429):
            findings.append(
                Finding(
                    "links",
                    "warn",
                    f"{where}: rate-limited (HTTP {code}), not verified: {link.target}",
                )
            )
        else:
            findings.append(
                Finding("links", "error", f"{where}: HTTP {code}: {link.target}")
            )
    return findings


def names_asset(payload, names: set[str]) -> bool:
    if isinstance(payload, str):
        return payload in names
    if isinstance(payload, dict):
        return any(names_asset(value, names) for value in payload.values())
    if isinstance(payload, list):
        return any(names_asset(value, names) for value in payload)
    return False


def check_provenance(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for png in sorted(root.rglob("*.png")):
        rel = png.relative_to(root)
        if rel.as_posix().startswith(FIXTURE_PREFIX) or ".git" in rel.parts:
            continue
        if not any(part in PROVENANCE_DIRS for part in rel.parts):
            continue
        names = {png.name, rel.as_posix()}
        covered = png.with_suffix(".provenance.json").is_file()
        if not covered:
            for record in sorted(png.parent.glob("*.json")):
                try:
                    payload = json.loads(record.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if names_asset(payload, names):
                    covered = True
                    break
        if not covered:
            findings.append(
                Finding(
                    "provenance",
                    "error",
                    f"{rel.as_posix()}: no provenance record names this PNG "
                    f"(expected {png.stem}.provenance.json or a sibling JSON listing it)",
                )
            )
    return findings


def text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    toplevel = None
    try:
        toplevel = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        listing = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True
        ).stdout.decode()
        files = [root / rel for rel in listing.split("\0") if rel]
    except (OSError, subprocess.CalledProcessError):
        files = []
    # A fixture tree inside a larger work tree must not inherit the outer file
    # list, and a tree without Git history still has to be checked.
    if toplevel != str(root) or not files:
        files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [
        p
        for p in files
        if p.is_file()
        and p.suffix.lower() in TEXT_SUFFIXES
        and not p.relative_to(root).as_posix().startswith(PRIVACY_EXEMPT)
    ]


def check_privacy(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern, label in PRIVATE_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                start = text.rfind("\n", 0, match.start()) + 1
                end = text.find("\n", match.start())
                current = text[start : len(text) if end < 0 else end]
                where = f"{path.relative_to(root).as_posix()}:{line}"
                if PRIVACY_WAIVER in current:
                    # A scanner that names the pattern is not a leak; the waiver is
                    # explicit and line-scoped, so it cannot silence a real URL.
                    findings.append(
                        Finding("privacy", "note", f"{where}: {label} waived in place")
                    )
                    continue
                findings.append(
                    Finding(
                        "privacy",
                        "error",
                        f"{where}: {label} (matched {match.group(0)!r})",
                    )
                )
    return findings


def claims_doc_ids(doc: Path) -> set[str]:
    return set(
        re.findall(
            r"^\|\s*([UM]\d{2})\s*\|", doc.read_text(encoding="utf-8"), re.MULTILINE
        )
    )


def check_claims(
    root: Path, readme: Path, *, claims_doc: Path | None, strict: bool
) -> list[Finding]:
    doc = claims_doc or (root / CLAIMS_DOC)
    if not doc.is_file():
        return [
            Finding(
                "claims",
                "error" if strict else "note",
                f"{CLAIMS_DOC} absent: claim lint SKIPPED (the doc is the authority)",
            )
        ]
    doc_ids = claims_doc_ids(doc)
    findings = [
        Finding(
            "claims",
            "error",
            f"{claim_id} no longer in {doc.name}: update BANNED_CLAIMS",
        )
        for claim_id in sorted({c for c, _ in BANNED_CLAIMS} - doc_ids)
    ]
    text = readme.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for claim_id, pattern in BANNED_CLAIMS:
            match = pattern.search(line)
            if not match:
                continue
            window = lowered[max(0, match.start() - QUALIFIER_WINDOW) : match.start()]
            if any(qualifier in window for qualifier in QUALIFIERS):
                continue
            findings.append(
                Finding(
                    "claims",
                    "error",
                    f"{readme.name}:{line_no}: banned claim {claim_id}: {match.group(0)!r}",
                )
            )
    return findings


def check_a11y(root: Path, readme: Path) -> list[Finding]:
    findings: list[Finding] = []
    for link in readme_links(readme):
        if not link.is_image or link.html_tag == "source":
            continue
        where = f"{readme.name}:{link.line}"
        if link.html_tag == "img":
            if not link.html_attrs.get("alt", "").strip():
                findings.append(
                    Finding("a11y", "error", f"{where}: <img> without alt text")
                )
            if not re.fullmatch(r"\d+", link.html_attrs.get("width", "")):
                findings.append(
                    Finding("a11y", "error", f"{where}: <img> without integer width")
                )
        elif not link.alt.strip():
            findings.append(
                Finding("a11y", "error", f"{where}: image without alt text")
            )
    return findings


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def run(args: argparse.Namespace) -> int:
    root = Path(args.repo).resolve()
    readme = (root / args.readme).resolve()
    if not readme.is_file():
        print(f"check-profile: missing README {readme}", file=sys.stderr)
        return 2
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    claims_doc = Path(args.claims_doc).resolve() if args.claims_doc else None

    findings: list[Finding] = []
    findings += check_links(
        root, readme, offline=args.offline, token=token, timeout=args.timeout
    )
    findings += check_provenance(root)
    findings += check_privacy(root)
    findings += check_claims(root, readme, claims_doc=claims_doc, strict=args.strict)
    findings += check_a11y(root, readme)

    errors = [f for f in findings if f.level == "error"]
    others = [f for f in findings if f.level != "error"]
    print(f"== profile check: {root}")
    for finding in findings:
        print(finding.render())
    per_check: dict[str, int] = {}
    for finding in errors:
        per_check[finding.check] = per_check.get(finding.check, 0) + 1
    summary = (
        ", ".join(f"{name}={count}" for name, count in sorted(per_check.items()))
        or "none"
    )
    print(f"-- violations: {len(errors)} ({summary}); notes/warnings: {len(others)}")
    print("RESULT: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--readme", default=DEFAULT_README)
    parser.add_argument(
        "--claims-doc",
        default=None,
        help=f"claim authority (default: <repo>/{CLAIMS_DOC})",
    )
    parser.add_argument("--offline", action="store_true", help="skip remote probes")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="an absent claims doc is a violation instead of a skip",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
