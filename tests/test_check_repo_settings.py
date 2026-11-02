"""Tests for scripts/check-repo-settings.py.

Fixtures are offline snapshots of one repo's settings, so nothing here touches
GitHub: the CLI runs with `--offline` and `check()` is a pure function.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
SCRIPT = REPO / "scripts" / "check-repo-settings.py"
FIXTURES = TESTS / "fixtures" / "repo-settings"
CLEAN = TESTS / "fixtures" / "repo-settings-clean"


def load():
    spec = importlib.util.spec_from_file_location("check_repo_settings", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_repo_settings"] = module
    spec.loader.exec_module(module)
    return module


settings = load()


def run(directory: Path, *extra: str) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--offline", str(directory), *extra],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def levels(findings: list) -> dict[str, int]:
    counted: dict[str, int] = {}
    for finding in findings:
        counted[finding.level] = counted.get(finding.level, 0) + 1
    return counted


class CheckTests(unittest.TestCase):
    def test_public_repo_missing_everything_is_an_error(self) -> None:
        findings = settings.check(settings.RepoState(name="r", private=False))
        rules = {f.rule for f in findings if f.level == "error"}
        self.assertEqual(rules, {"secret_scanning", "push_protection", "ruleset", "updater"})
        self.assertNotIn("plan-ceiling", {f.level for f in findings})

    def test_private_repo_missing_protection_is_plan_ceiling_not_drift(self) -> None:
        findings = settings.check(
            settings.RepoState(name="r", private=True, updater="dependabot")
        )
        self.assertEqual(
            {f.rule for f in findings if f.level == "plan-ceiling"},
            {"secret_scanning", "push_protection", "ruleset"},
        )
        self.assertEqual([f for f in findings if f.level == "error"], [])

    def test_dependabot_is_an_error_on_private_repos_too(self) -> None:
        findings = settings.check(
            settings.RepoState(
                name="r",
                private=True,
                secret_scanning=True,
                push_protection=True,
                ruleset="main-protection",
                last_success=datetime.now(timezone.utc) - timedelta(days=1),
            )
        )
        self.assertEqual([(f.rule, f.level) for f in findings], [("updater", "error")])

    def test_renovate_satisfies_the_updater_rule(self) -> None:
        """wa and zellij-vertical-tabs run Renovate; a second updater would duplicate PRs."""
        findings = settings.check(
            settings.RepoState(
                name="r",
                secret_scanning=True,
                push_protection=True,
                ruleset="main-protection",
                updater="renovate",
                last_success=datetime.now(timezone.utc) - timedelta(days=1),
            )
        )
        self.assertEqual(findings, [])

    def test_compliant_repo_has_no_findings(self) -> None:
        findings = settings.check(
            settings.RepoState(
                name="r",
                secret_scanning=True,
                push_protection=True,
                ruleset="main-protection",
                updater="dependabot",
                last_success=datetime.now(timezone.utc) - timedelta(days=1),
            )
        )
        self.assertEqual(findings, [])

    def test_stale_ci_is_a_note_never_an_error(self) -> None:
        stale = datetime.now(timezone.utc) - timedelta(days=90)
        findings = settings.check(
            settings.RepoState(
                name="r",
                secret_scanning=True,
                push_protection=True,
                ruleset="main-protection",
                updater="dependabot",
                last_success=stale,
            )
        )
        self.assertEqual([(f.rule, f.level) for f in findings], [("ci", "note")])


class CliTests(unittest.TestCase):
    def test_mixed_fixtures_fail_with_counts(self) -> None:
        code, output = run(FIXTURES)
        self.assertEqual(code, 1, output)
        # public-bare: scanning + push + ruleset + updater. private-bare has a
        # dependabot config, so its three gaps are plan-ceiling, not violations.
        self.assertIn("violations: 4", output)
        self.assertIn("plan-ceiling: 3", output)
        self.assertIn("RESULT: FAIL", output)
        # The archived repo is exempt and never appears in the table.
        self.assertNotIn("archived ", output)

    def test_clean_fixtures_pass(self) -> None:
        code, output = run(CLEAN, "--max-age-days", "36500")
        self.assertEqual(code, 0, output)
        self.assertIn("violations: 0", output)
        self.assertIn("RESULT: PASS", output)

    def test_json_log_snapshot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "settings.json"
            code, output = run(CLEAN, "--max-age-days", "36500", "--json-log", str(log))
            self.assertEqual(code, 0, output)
            rows = json.loads(log.read_text(encoding="utf-8"))
            self.assertEqual([row["repo"] for row in rows], ["public-clean", "renovate-repo"])
            self.assertTrue(rows[0]["ruleset"])


class RulesetTargetTests(unittest.TestCase):
    """Rulesets name the default branch three different ways in the wild."""

    def covers(self, include: list[str], exclude: list[str] | None = None) -> bool:
        detail = {"conditions": {"ref_name": {"include": include, "exclude": exclude or []}}}
        return settings.covers_default_branch(detail, "main")

    def test_default_branch_marker(self) -> None:
        self.assertTrue(self.covers(["~DEFAULT_BRANCH"]))

    def test_literal_ref_is_the_shape_claude_mac_chrome_uses(self) -> None:
        self.assertTrue(self.covers(["refs/heads/main"]))

    def test_all_marker(self) -> None:
        self.assertTrue(self.covers(["~ALL"]))

    def test_empty_include_means_all_branches(self) -> None:
        self.assertTrue(self.covers([]))

    def test_other_branch_does_not_count(self) -> None:
        self.assertFalse(self.covers(["refs/heads/release"]))

    def test_excluded_default_branch_does_not_count(self) -> None:
        self.assertFalse(self.covers(["~ALL"], ["refs/heads/main"]))


if __name__ == "__main__":
    unittest.main()
