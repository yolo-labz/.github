"""The rollout contract reads the flagship set from docs/brand-positioning.md.

Regression 02/11/2026: rollout/check.py asserted exactly six README entries, so it
failed the day the profile also listed a non-flagship (#25), and nothing noticed
because no workflow ran it. These tests pin the behaviour that makes the count
irrelevant: the doc's flagship table is the only authority.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROLLOUT = REPO / "profile/assets/brand/rollout"
DOC = REPO / "docs/brand-positioning.md"


def load(name: str):
    spec = importlib.util.spec_from_file_location(
        f"rollout_{name}", ROLLOUT / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check = load("check")


def entry(name: str) -> str:
    return f"- **[{name}](https://github.com/yolo-labz/{name})** does a thing.\n"


class FlagshipContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rollout-contract-")
        self.addCleanup(self.tmp.cleanup)
        self.doc = Path(self.tmp.name) / "brand-positioning.md"

    def write_doc(self, names):
        rows = "".join(
            f"| [{n}][{n[:2].upper()}-R] | Sentence for {n}. | Qualifier. |\n"
            for n in names
        )
        self.doc.write_text(
            "# Positioning\n\n## Some number of flagship propositions\n\n"
            f"| Project | Proposed sentence | Qualifier |\n| --- | --- | --- |\n{rows}\n"
            "### Why not another\n\n| [decoy][DC-R] | not a flagship | x |\n"
        )

    def test_real_profile_satisfies_the_real_doc(self):
        text = (REPO / "profile/README.md").read_text()
        flagships, listed = check.flagship_contract(text, DOC)
        self.assertTrue(set(flagships) <= set(listed))
        self.assertGreaterEqual(len(flagships), 1)

    def test_count_comes_from_the_doc_not_the_script(self):
        for names in (
            ["alpha", "beta"],
            ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta"],
        ):
            with self.subTest(n=len(names)):
                self.write_doc(names)
                text = "".join(entry(n) for n in names)
                flagships, listed = check.flagship_contract(text, self.doc)
                self.assertEqual(flagships, sorted(names))
                self.assertEqual(len(listed), len(names))

    def test_non_flagship_entry_is_allowed(self):
        self.write_doc(["alpha", "beta"])
        flagships, listed = check.flagship_contract(
            entry("alpha") + entry("beta") + entry("extra"), self.doc
        )
        self.assertEqual(flagships, ["alpha", "beta"])
        self.assertEqual(sorted(listed), ["alpha", "beta", "extra"])

    def test_decoy_row_in_a_later_subsection_is_not_a_flagship(self):
        self.write_doc(["alpha"])
        flagships, _ = check.flagship_contract(entry("alpha"), self.doc)
        self.assertNotIn("decoy", flagships)

    def test_missing_flagship_fails(self):
        self.write_doc(["alpha", "beta"])
        with self.assertRaisesRegex(AssertionError, "beta"):
            check.flagship_contract(entry("alpha"), self.doc)

    def test_wrong_link_target_fails(self):
        self.write_doc(["alpha"])
        with self.assertRaisesRegex(AssertionError, "own repository"):
            check.flagship_contract(
                "- **[alpha](https://github.com/elsewhere/alpha)** — x\n", self.doc
            )

    def test_duplicate_entry_fails(self):
        self.write_doc(["alpha"])
        with self.assertRaisesRegex(AssertionError, "twice"):
            check.flagship_contract(entry("alpha") * 2, self.doc)

    def test_missing_table_fails_loudly(self):
        self.doc.write_text("# no table here\n")
        with self.assertRaisesRegex(AssertionError, "No flagship table"):
            check.flagship_contract(entry("alpha"), self.doc)


class RolloutScriptsRunTests(unittest.TestCase):
    """What CI executes: the script as a subprocess, against the real tree."""

    def test_check_passes_against_the_real_tree(self):
        result = subprocess.run(
            [sys.executable, str(ROLLOUT / "check.py")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["flagships"], len(check.flagship_sentences(DOC)))


if __name__ == "__main__":
    unittest.main()
