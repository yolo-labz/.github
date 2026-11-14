#!/usr/bin/env python3
"""Build the yolo-labz design tokens into CSS. Stdlib only.

    python3 design/build.py            write design/dist/*
    python3 design/build.py --check    fail if design/dist/* is not what the sources build

Sources: design/tokens/primitive.json, semantic.json (W3C Design Tokens format).
Outputs:
    dist/tokens.css    CSS custom properties (--yl-*), dark on :root, light on [data-theme="light"]
    dist/tailwind.css  Tailwind v4 `@theme` preset that points at those properties
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = HERE / "tokens"
DIST = HERE / "dist"
MODE = "org.yolo-labz.mode"
TAILWIND = "org.yolo-labz.tailwind"
EMPTY: dict = {}
REF = re.compile(r"^\{([^{}]+)\}$")


def merge(into: dict, extra: dict) -> None:
    for key, val in extra.items():
        if isinstance(val, dict) and isinstance(into.get(key), dict):
            merge(into[key], val)
        else:
            into[key] = val


def load() -> tuple[dict, str]:
    raw = b"".join((TOKENS / n).read_bytes() for n in ("primitive.json", "semantic.json"))
    tree: dict = {}
    for name in ("primitive.json", "semantic.json"):
        merge(tree, json.loads((TOKENS / name).read_text()))
    return tree, hashlib.sha256(raw).hexdigest()


def leaves(node: dict, path: tuple[str, ...] = ()):
    """Yield (path, token) for every token (an object that has $value)."""
    for key, val in node.items():
        if key.startswith("$"):
            continue
        if "$value" in val:
            yield path + (key,), val
        else:
            yield from leaves(val, path + (key,))


def mode_of(tok: dict) -> str | None:
    """The light-theme value of a semantic token, or None for a primitive."""
    ext = tok.get("$extensions", EMPTY)
    return ext[MODE]["light"] if MODE in ext else None


def prop(path: tuple[str, ...]) -> str:
    return "--yl-" + "-".join(path)


def lookup(tree: dict, dotted: str) -> dict:
    node = tree
    for part in dotted.split("."):
        node = node[part]
    if "$value" not in node:
        raise KeyError(f"{dotted} is a group, not a token")
    return node


def render(tree: dict, value, type_: str) -> str:
    """One token value as CSS. A reference becomes var(--yl-...), so the chain stays visible."""
    if isinstance(value, str):
        m = REF.match(value)
        if m:
            lookup(tree, m.group(1))  # fails loudly on a dangling reference
            return f"var({prop(tuple(m.group(1).split('.')))})"
        return value
    if type_ == "cubicBezier":
        return "cubic-bezier(" + ", ".join(f"{n:g}" for n in value) + ")"
    return f"{value:g}" if isinstance(value, float) else str(value)


def build() -> dict[str, str]:
    tree, digest = load()
    prim, sem = [], {"dark": [], "light": []}
    for path, tok in leaves(tree):
        name = prop(path)
        css = render(tree, tok["$value"], tok.get("$type", ""))
        light = mode_of(tok)
        if light is None:
            prim.append((name, css))
        else:
            sem["dark"].append((name, css))
            sem["light"].append((name, render(tree, light, tok.get("$type", ""))))
    head = (
        "/* @yolo-labz/design: GENERATED, do not edit. Source: yolo-labz/.github design/tokens.\n"
        f" * inputs sha256:{digest} */\n"
    )
    block = lambda sel, rows, extra="": sel + " {\n" + extra + "".join(f"  {n}: {v};\n" for n, v in rows) + "}\n"
    tokens_css = (
        head
        + block(":root", prim + sem["dark"], "  color-scheme: dark;\n")
        + block(':root[data-theme="light"]', sem["light"], "  color-scheme: light;\n")
    )

    tw: list[tuple[str, str]] = []
    for path, tok in leaves(tree):
        name = tok.get("$extensions", EMPTY).get(TAILWIND)
        if name:
            tw.append((f"--color-{name}", f"var({prop(path)})"))
    for path, tok in leaves(tree):
        if path[:2] == ("text", "size") and path[2].startswith("step-"):
            tw.append((f"--text-{path[2]}", f"var({prop(path)})"))
        elif path[0] == "breakpoint":
            tw.append((f"--breakpoint-{path[1]}", tok["$value"]))  # literal: @media cannot take var()
        elif path[:2] == ("ease", "out-expo"):
            tw.append(("--ease-out-expo", f"var({prop(path)})"))
    tailwind_css = (
        head
        + "/* Tailwind v4 preset. Plain @theme, not `inline`: utilities read var(--color-x), so an app can still\n"
        + " * override --color-x (prefers-contrast) after this file. Breakpoints are literals because a media\n"
        + " * query cannot take var(). Fonts and radius are left to the app: next/font wires the font file, and\n"
        + " * Tailwind's radius defaults are what the portfolio ships today. */\n"
        + block("@theme", tw)
    )
    return {"tokens.css": tokens_css, "tailwind.css": tailwind_css}


def stats() -> dict:
    tree, _ = load()
    toks = list(leaves(tree))
    sem = [p for p, t in toks if mode_of(t) is not None]
    return {"tokens": len(toks), "semantic": len(sem), "primitive": len(toks) - len(sem)}


def main(argv: list[str]) -> int:
    out = build()
    if "--check" in argv:
        bad = [n for n, text in out.items() if not (DIST / n).exists() or (DIST / n).read_text() != text]
        if bad:
            print("design/dist is stale: " + ", ".join(bad) + "; run python3 design/build.py", file=sys.stderr)
            return 1
        print("design/dist is current", stats())
        return 0
    DIST.mkdir(exist_ok=True)
    for name, text in out.items():
        (DIST / name).write_text(text)
    print("wrote", ", ".join(f"dist/{n} ({len(t)} B)" for n, t in out.items()), stats())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
