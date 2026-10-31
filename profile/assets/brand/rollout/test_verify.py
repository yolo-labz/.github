"""Offline regression tests for the saved visual evidence contract."""

import contextlib
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

    def test_stale_profile_fails(self):
        original = Path.read_bytes

        def changed(path):
            data = original(path)
            return (
                data + b"stale" if path == verify.ROOT / "profile/README.md" else data
            )

        with (
            patch.object(Path, "read_bytes", changed),
            self.assertRaises(AssertionError),
        ):
            verify.verify()

    def test_missing_mobile_theme_fails(self):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == "renders.json":
                rows = json.loads(text)
                rows[-1] = rows[0]
                return json.dumps(rows)
            return text

        with (
            patch.object(Path, "read_text", changed),
            self.assertRaises(AssertionError),
        ):
            verify.verify()


if __name__ == "__main__":
    unittest.main()
