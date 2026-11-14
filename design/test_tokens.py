"""One runnable check for the token source: python3 -m unittest discover -s design"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

import build

HERE = Path(__file__).resolve().parent
TREE, _ = build.load()


def lum(h: str) -> float:
    def lin(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def resolve(value: str) -> str:
    while value.startswith("{"):
        value = build.lookup(TREE, value[1:-1])["$value"]
    return value


def theme(path: str, mode: str) -> str:
    tok = build.lookup(TREE, path)
    return resolve(tok["$extensions"][build.MODE]["light"] if mode == "light" else tok["$value"])


class Tokens(unittest.TestCase):
    def test_every_leaf_is_valid_dtcg(self):
        for path, tok in build.leaves(TREE):
            self.assertIn("$type", tok, ".".join(path))
            if tok["$type"] == "color":
                self.assertRegex(resolve(tok["$value"]), r"^#[0-9a-f]{6}$", ".".join(path))

    def test_references_resolve(self):
        build.build()  # a dangling {ref} raises KeyError

    def test_text_roles_meet_4_5_on_both_themes(self):
        for mode in ("dark", "light"):
            ground = theme("color.surface.base", mode)
            for role in ("text.default", "text.muted", "text.soft", "accent.default", "link.default"):
                self.assertGreaterEqual(contrast(theme(f"color.{role}", mode), ground), 4.5, f"{role} {mode}")
            fill = theme("color.accent.default", mode)
            self.assertGreaterEqual(contrast(theme("color.accent.on", mode), fill), 4.5, f"accent.on {mode}")

    def test_controls_meet_3_to_1(self):
        for mode in ("dark", "light"):
            ground = theme("color.surface.base", mode)
            for role in ("border.strong", "focus.ring"):
                self.assertGreaterEqual(contrast(theme(f"color.{role}", mode), ground), 3.0, f"{role} {mode}")

    def test_mobile_floors(self):
        px = lambda p: float(build.lookup(TREE, p)["$value"].removesuffix("px"))
        self.assertGreaterEqual(px("touch.min"), 44)
        self.assertGreaterEqual(px("touch.gap"), 8)
        self.assertGreaterEqual(px("text.min-body"), 16)
        self.assertGreaterEqual(px("text.min-text"), 14)
        rem = lambda p: float(build.lookup(TREE, p)["$value"].removesuffix("rem")) * 16
        for k in ("label", "small"):
            self.assertGreaterEqual(rem(f"text.size.{k}"), px("text.min-text"), k)
        self.assertLessEqual(px("viewport.floor"), 360)
        bps = [px(f"breakpoint.{k}") for k in ("sm", "md", "lg", "xl")]
        self.assertEqual(bps, sorted(bps))

    def test_gremlin_skin_is_visible_on_both_grounds(self):
        self.assertGreaterEqual(contrast(theme("color.mark-skin", "dark"), theme("color.surface.base", "dark")), 3.0)
        self.assertGreaterEqual(contrast(theme("color.mark-skin", "light"), theme("color.surface.base", "light")), 3.0)

    def test_build_is_deterministic_and_dist_is_current(self):
        self.assertEqual(build.build(), build.build())
        run = subprocess.run([sys.executable, str(HERE / "build.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
