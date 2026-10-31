"""Tests for scripts/check-repo-metadata.py.

Fixtures are offline payload snapshots, so nothing here touches GitHub: the CLI
runs with `--offline` and the repair planner is a pure function.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
SCRIPT = REPO / "scripts" / "check-repo-metadata.py"
FIXTURES = TESTS / "fixtures" / "repo-metadata"


def load():
    spec = importlib.util.spec_from_file_location("check_repo_metadata", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_repo_metadata"] = module
    spec.loader.exec_module(module)
    return module


metadata = load()


def run(directory: Path = FIXTURES) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(REPO), "--offline", str(directory)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def repo_from(name: str) -> metadata.Repo:
    payload = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    repo = metadata.Repo.from_payload(payload)
    readme = FIXTURES / f"{name}.md"
    repo.readme = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    return repo


class FlagshipTable(unittest.TestCase):
    def test_table_is_parsed_from_the_positioning_doc(self):
        sentences = metadata.flagship_sentences(REPO / metadata.CLAIMS_DOC)
        self.assertEqual(
            set(sentences),
            {
                "wa",
                "fand",
                "anthropic-throttle-proxy",
                "claude-mac-chrome",
                "chrome-bridge",
                "kokoro-speakd",
            },
        )
        self.assertEqual(
            sentences["fand"],
            "Configure temperature-driven fan modes on supported Apple Silicon Macs.",
        )

    def test_missing_doc_is_a_usage_error(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(TESTS / "fixtures" / "repo-metadata"),
                "--offline",
                str(FIXTURES),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class Rules(unittest.TestCase):
    def setUp(self):
        self.flagships = metadata.flagship_sentences(REPO / metadata.CLAIMS_DOC)

    def errors(self, name: str) -> list[str]:
        return [
            f"{f.rule}: {f.message}"
            for f in metadata.check_repo(repo_from(name), self.flagships)
            if f.level == "error"
        ]

    def test_clean_repo_has_no_findings(self):
        self.assertEqual(self.errors("clean-tool"), [])

    def test_archived_repo_is_exempt(self):
        findings = metadata.check_repo(repo_from("archived-tool"), self.flagships)
        self.assertEqual([f.level for f in findings], ["note"])
        self.assertIn("archived", findings[0].message)

    def test_flagship_description_must_be_the_one_liner(self):
        errors = self.errors("wa")
        self.assertTrue(any(e.startswith("description:") for e in errors), errors)
        self.assertTrue(any("positioning one-liner" in e for e in errors), errors)

    def test_missing_description(self):
        errors = self.errors("no-description")
        self.assertEqual(errors, ["description: missing"])

    def test_github_homepage_is_not_a_site(self):
        errors = self.errors("github-homepage")
        self.assertTrue(any(e.startswith("homepage:") for e in errors), errors)

    def test_site_homepage_must_match_the_map(self):
        errors = self.errors("site-homepage")
        self.assertTrue(
            any("expected https://portfolio.home301server.com.br" in e for e in errors),
            errors,
        )

    def test_topic_count(self):
        errors = self.errors("few-topics")
        self.assertTrue(any(e.startswith("topics:") for e in errors), errors)

    def test_issues_must_be_enabled(self):
        self.assertEqual(self.errors("issues-off"), ["has_issues: issues disabled"])

    def test_readme_must_link_the_org(self):
        errors = self.errors("readme-noorg")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("README does not link back to github.com/yolo-labz", errors[0])


class RepairPlan(unittest.TestCase):
    def setUp(self):
        self.flagships = metadata.flagship_sentences(REPO / metadata.CLAIMS_DOC)

    def test_flagship_gets_the_doc_sentence_and_drops_a_self_link(self):
        changes = metadata.plan_fix(repo_from("wa"), self.flagships)
        self.assertEqual(changes["description"], self.flagships["wa"])
        self.assertEqual(changes["homepage"], "")

    def test_topics_are_merged_from_the_curated_map(self):
        changes = metadata.plan_fix(repo_from("few-topics"), self.flagships)
        self.assertEqual(changes["_topics"], ["cpp", "speech-synthesis", "tts"])

    def test_clean_repo_needs_no_change(self):
        self.assertEqual(metadata.plan_fix(repo_from("clean-tool"), self.flagships), {})

    def test_empty_description_is_not_invented(self):
        changes = metadata.plan_fix(repo_from("no-description"), self.flagships)
        self.assertEqual(changes, {"_description": "needs a human sentence"})


class EndToEnd(unittest.TestCase):
    def test_fixture_run_fails_and_names_every_rule(self):
        code, out = run()
        self.assertEqual(code, 1, out)
        for rule in ("description", "homepage", "topics", "has_issues", "readme"):
            with self.subTest(rule=rule):
                self.assertIn(f"] {rule}", out.replace(": " + rule, "] " + rule))
        self.assertIn("RESULT: FAIL", out)
        self.assertIn("exempt (archived)", out)

    def test_compliant_tree_passes(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for name in ("clean-tool", "archived-tool"):
                for suffix in (".json", ".md"):
                    source = FIXTURES / f"{name}{suffix}"
                    if source.is_file():
                        (target / source.name).write_text(
                            source.read_text(encoding="utf-8"), encoding="utf-8"
                        )
            code, out = run(target)
            self.assertEqual(code, 0, out)
            self.assertIn("RESULT: PASS", out)

    def test_json_log_is_written_once_and_appended(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "log.json"
            for _ in range(2):
                subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--repo",
                        str(REPO),
                        "--offline",
                        str(FIXTURES),
                        "--json-log",
                        str(log),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
            self.assertTrue(log.is_file())
            self.assertIsInstance(json.loads(log.read_text(encoding="utf-8")), list)


if __name__ == "__main__":
    unittest.main()
