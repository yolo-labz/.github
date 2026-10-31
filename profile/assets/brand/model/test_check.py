"""Offline discriminating checks; no browser attach, network or image send."""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import check as model_check

HERE = Path(__file__).resolve().parent


def run_check(*args):
    return subprocess.run(
        [sys.executable, str(HERE / "check.py"), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class AcceptanceTests(unittest.TestCase):
    def test_source_spec_and_references_pass(self):
        result = run_check("--spec-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NOT sheet delivery", result.stdout)

    def test_bad_palette_fixture_is_rejected(self):
        result = run_check("--spec-only", "--spec-json", "fixtures/bad-palette.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SPEC palette mismatch", result.stderr)

    def test_missing_gpt_sheets_cannot_pass(self):
        original = model_check.local

        def missing(name):
            if name == "turnaround.png":
                raise AssertionError("Missing: turnaround.png")
            return original(name)

        with (
            patch.object(model_check, "local", missing),
            self.assertRaisesRegex(AssertionError, "Missing: turnaround.png"),
        ):
            model_check.check_sheets()


if __name__ == "__main__":
    unittest.main()
