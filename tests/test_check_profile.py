"""Tests for scripts/check-profile.py.

Each negative fixture is a tiny repository that is clean except for exactly one
violation, so a failure can only come from the check under test. The CLI is
exercised as a subprocess (same entry point CI uses); pure helpers are imported.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
CHECKER = REPO / "scripts" / "check-profile.py"
FIXTURES = TESTS / "fixtures"
POSITIVE = FIXTURES / "positive-mini"
CLAIMS_DOC = POSITIVE / "docs" / "brand-positioning.md"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_profile", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_profile"] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def run(repo: Path, *extra: str) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--repo", str(repo), *extra],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


class PositiveFixture(unittest.TestCase):
    def test_positive_fixture_passes(self):
        code, out = run(POSITIVE, "--offline")
        self.assertEqual(code, 0, out)
        self.assertIn("RESULT: PASS", out)

    def test_positive_fixture_reports_no_claim_violations(self):
        code, out = run(POSITIVE, "--offline", "--strict")
        self.assertEqual(code, 0, out)
        self.assertNotIn("[error] claims", out)

    def test_sibling_json_covers_generated_png(self):
        code, out = run(POSITIVE, "--offline")
        self.assertEqual(code, 0, out)
        self.assertNotIn("hero.png", out)


class NegativeFixtures(unittest.TestCase):
    def test_missing_local_asset_fails(self):
        code, out = run(FIXTURES / "negative-local-link", "--offline")
        self.assertEqual(code, 1, out)
        self.assertIn("[error] links:", out)
        self.assertIn("assets/missing.png", out)

    def test_missing_provenance_fails(self):
        code, out = run(FIXTURES / "negative-provenance", "--offline")
        self.assertEqual(code, 1, out)
        self.assertIn("[error] provenance:", out)
        self.assertIn("hero.png", out)

    def test_private_and_signed_urls_fail(self):
        code, out = run(FIXTURES / "negative-private-url", "--offline")
        self.assertEqual(code, 1, out)
        self.assertIn("private ChatGPT conversation URL", out)
        self.assertIn("OpenAI ephemeral asset host", out)
        self.assertIn("presigned URL signature parameter", out)
        self.assertIn("signed URL expiry parameter", out)

    def test_banned_claims_fail(self):
        code, out = run(
            FIXTURES / "negative-banned-claim",
            "--offline",
            "--claims-doc",
            str(CLAIMS_DOC),
        )
        self.assertEqual(code, 1, out)
        self.assertIn("banned claim U01", out)
        self.assertIn("banned claim U04", out)
        self.assertIn("banned claim M01", out)

    def test_missing_alt_and_width_fail(self):
        code, out = run(FIXTURES / "negative-alt-width", "--offline")
        self.assertEqual(code, 1, out)
        self.assertIn("<img> without alt text", out)
        self.assertIn("<img> without integer width", out)


class ClaimLintAuthority(unittest.TestCase):
    def test_absent_claims_doc_skips_instead_of_failing(self):
        _, out = run(FIXTURES / "negative-alt-width", "--offline")
        self.assertIn("claim lint SKIPPED", out)

    def test_strict_turns_absent_claims_doc_into_a_violation(self):
        code, out = run(FIXTURES / "negative-local-link", "--offline", "--strict")
        self.assertEqual(code, 1, out)
        self.assertIn("[error] claims:", out)
        self.assertIn("absent", out)

    def test_claims_doc_missing_an_id_is_drift(self):
        # A doc with no claim-matrix rows cannot back any linted phrase.
        findings = checker.check_claims(
            POSITIVE,
            POSITIVE / "profile" / "README.md",
            claims_doc=FIXTURES / "negative-banned-claim" / "profile" / "README.md",
            strict=False,
        )
        drifted = [f.message for f in findings if "update BANNED_CLAIMS" in f.message]
        self.assertEqual(len(drifted), len({cid for cid, _ in checker.BANNED_CLAIMS}))
        self.assertTrue(all("no longer in" in message for message in drifted))


class RemoteLinks(unittest.TestCase):
    def test_dead_github_link_is_a_violation(self):
        findings = checker.check_links(
            POSITIVE,
            POSITIVE / "profile" / "README.md",
            offline=False,
            token=None,
            timeout=1,
            status=lambda url, token, timeout: 404,
        )
        errors = [f for f in findings if f.level == "error"]
        self.assertEqual(len(errors), 1, findings)
        self.assertIn("HTTP 404", errors[0].message)

    def test_live_github_link_passes(self):
        findings = checker.check_links(
            POSITIVE,
            POSITIVE / "profile" / "README.md",
            offline=False,
            token=None,
            timeout=1,
            status=lambda url, token, timeout: 200,
        )
        self.assertEqual([f for f in findings if f.level == "error"], [])

    def test_rate_limit_is_a_warning_not_a_violation(self):
        findings = checker.check_links(
            POSITIVE,
            POSITIVE / "profile" / "README.md",
            offline=False,
            token=None,
            timeout=1,
            status=lambda url, token, timeout: 429,
        )
        self.assertEqual([f for f in findings if f.level == "error"], [])
        self.assertTrue([f for f in findings if "rate-limited" in f.message])

    def test_offline_skips_remote_probes(self):
        findings = checker.check_links(
            POSITIVE,
            POSITIVE / "profile" / "README.md",
            offline=True,
            token=None,
            timeout=1,
            status=lambda *args: self.fail("offline mode must not probe"),
        )
        self.assertEqual([f for f in findings if f.level == "error"], [])


class UrlPolicy(unittest.TestCase):
    def test_classification(self):
        cases = {
            "https://github.com/yolo-labz/wa": "github",
            "https://raw.githubusercontent.com/yolo-labz/.github/main/profile/README.md": "raw",
            "https://blog.home301server.com.br": "external",
            "https://linkedin.com/in/x": "external",
            "profile/assets/logo.png": "local",
            "#anchor": "skip",
            "mailto:someone@example.test": "skip",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(checker.classify_url(url), expected)

    def test_github_targets(self):
        cases = {
            "https://github.com/yolo-labz/wa": "/repos/yolo-labz/wa",
            "https://github.com/phsb5321": "/users/phsb5321",
            "https://github.com/orgs/yolo-labz/repositories": "/orgs/yolo-labz",
            "https://github.com/yolo-labz/wa/releases/tag/v2.3.0": "/repos/yolo-labz/wa/releases/tags/v2.3.0",
            "https://github.com/yolo-labz/.github/blob/main/profile/README.md": "/repos/yolo-labz/.github/contents/profile/README.md?ref=main",
            "https://github.com/yolo-labz/wa/pull/12": "/repos/yolo-labz/wa/issues/12",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(checker.github_api_target(url), expected)

    def test_non_github_hosts_are_never_probed_through_the_api(self):
        self.assertIsNone(checker.remote_probe("https://linkedin.com/in/x", "external"))
        self.assertIsNone(
            checker.remote_probe("https://github.com/yolo-labz/wa/actions", "github")
        )


class Extraction(unittest.TestCase):
    def test_markdown_html_and_reference_links(self):
        sample = (
            '<img src="a.png" alt="A" width="10">\n'
            '<source media="(prefers-color-scheme: dark)" srcset="b.svg 1x, c.svg 2x">\n'
            "- [inline](https://github.com/yolo-labz/wa) and ![pic](d.png)\n"
            "[ref][id]\n\n[id]: https://github.com/yolo-labz/fand\n"
        )
        # Extraction is pure over text; feed the sample through a temp file.
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text(sample, encoding="utf-8")
            links = checker.readme_links(target)
        targets = [link.target for link in links]
        self.assertIn("a.png", targets)
        self.assertIn("b.svg", targets)
        self.assertIn("c.svg", targets)
        self.assertIn("https://github.com/yolo-labz/wa", targets)
        self.assertIn("d.png", targets)
        self.assertIn("https://github.com/yolo-labz/fand", targets)
        img = next(link for link in links if link.target == "a.png")
        self.assertEqual(img.alt, "A")
        self.assertEqual(img.html_attrs.get("width"), "10")

    def test_local_resolution_falls_back_to_repo_root(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "note.md").write_text("x", encoding="utf-8")
            readme = root / "profile" / "README.md"
            readme.parent.mkdir()
            readme.write_text("x", encoding="utf-8")
            resolved = checker.resolve_local(root, readme, "docs/note.md")
            self.assertEqual(resolved, root / "docs" / "note.md")


class Accessibility(unittest.TestCase):
    def test_source_tag_needs_no_alt_or_width(self):
        import tempfile

        sample = (
            "<picture>\n"
            '<source media="(prefers-color-scheme: dark)" srcset="a.svg 1x">\n'
            '<img src="b.svg" alt="wordmark" width="300">\n'
            "</picture>\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "profile").mkdir()
            readme = root / "profile" / "README.md"
            readme.write_text(sample, encoding="utf-8")
            self.assertEqual(checker.check_a11y(root, readme), [])


class MergeOrder(unittest.TestCase):
    """A consumer may reference an asset that still lives on an open branch."""

    def make_repo(self, root: Path, origin: str) -> Path:
        import subprocess as sp

        sp.run(["git", "init", "-q", str(root)], check=True)
        sp.run(["git", "-C", str(root), "remote", "add", "origin", origin], check=True)
        (root / "profile" / "assets").mkdir(parents=True)
        (root / "profile" / "assets" / "hero.png").write_bytes(b"png")
        readme = root / "profile" / "README.md"
        readme.write_text(
            "![hero](https://raw.githubusercontent.com/yolo-labz/.github/main/"
            "profile/assets/hero.png)\n",
            encoding="utf-8",
        )
        return readme

    def test_unpublished_asset_is_a_warning(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme = self.make_repo(root, "git@github.com:yolo-labz/.github.git")
            findings = checker.check_links(
                root,
                readme,
                offline=False,
                token=None,
                timeout=1,
                status=lambda *args: 404,
            )
            self.assertEqual([f for f in findings if f.level == "error"], [], findings)
            self.assertTrue(any("not published yet" in f.message for f in findings))

    def test_foreign_repo_404_is_still_an_error(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme = self.make_repo(root, "git@github.com:yolo-labz/wa.git")
            findings = checker.check_links(
                root,
                readme,
                offline=False,
                token=None,
                timeout=1,
                status=lambda *args: 404,
            )
            self.assertEqual(len([f for f in findings if f.level == "error"]), 1)


class PrivacyWaiver(unittest.TestCase):
    def test_waiver_is_line_scoped(self):
        import tempfile

        forbidden_host = "oai" + "usercontent"
        private_chat = "chatgpt" + ".com/c/abc"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "scan.py").write_text(
                f'BAD = "{forbidden_host}"  # profile-check: allow-private-pattern\n'
                f'URL = "https://{private_chat}"\n',
                encoding="utf-8",
            )
            findings = checker.check_privacy(root)
            errors = [f for f in findings if f.level == "error"]
            self.assertEqual(len(errors), 1, findings)
            self.assertIn("chatgpt.com/c/", errors[0].message)
            self.assertTrue(any("waived in place" in f.message for f in findings))


if __name__ == "__main__":
    unittest.main()
