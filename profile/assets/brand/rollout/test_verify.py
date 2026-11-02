"""Offline regression tests for the saved visual evidence contract."""

import contextlib
import hashlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import verify


class RenderEvidenceTests(unittest.TestCase):
    def test_saved_evidence_passes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            verify.verify()

    def test_modified_png_fails(self):
        original = Path.read_bytes

        def changed(path):
            data = original(path)
            return data + b"tampered" if path.suffix == ".png" else data

        with (
            patch.object(Path, "read_bytes", changed),
            self.assertRaises(AssertionError),
        ):
            verify.verify()

    def test_stale_profile_is_reported_not_an_integrity_failure(self):
        """The evidence is internally sound; only its README binding has drifted."""
        original = Path.read_bytes

        def changed(path):
            data = original(path)
            return (
                data + b"stale" if path == verify.ROOT / "profile/README.md" else data
            )

        with patch.object(Path, "read_bytes", changed):
            bound = verify.verify()
            self.assertIn("re-render", verify.freshness(bound))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(verify.main([]), 0)
                self.assertEqual(verify.main(["--require-fresh"]), verify.STALE)

    def test_evidence_bound_to_the_current_readme_is_fresh(self):
        readme = verify.ROOT / "profile/README.md"
        bound = hashlib.sha256(readme.read_bytes()).hexdigest()
        self.assertIsNone(verify.freshness(bound))

    def assert_rows_fail(self, mutate):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name != "renders.json":
                return text
            rows = json.loads(text)
            mutate(rows)
            return json.dumps(rows)

        with (
            patch.object(Path, "read_text", changed),
            self.assertRaises(AssertionError),
        ):
            verify.verify()

    def test_receipts_bound_to_different_profiles_fail(self):
        self.assert_rows_fail(lambda rows: rows[0].update(profile_sha256="0" * 64))

    def test_missing_mobile_theme_fails(self):
        self.assert_rows_fail(lambda rows: rows.__setitem__(-1, rows[0]))


if __name__ == "__main__":
    unittest.main()
