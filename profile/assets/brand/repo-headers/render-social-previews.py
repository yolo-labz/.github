#!/usr/bin/env python3
"""Render 1280x640 social previews for the 15 yolo-labz repositories.

Usage: python3 render-social-previews.py [--out DIR]
Needs: magick (ImageMagick 7), rsvg-convert, gh (authenticated), Inter font.
Inputs (relative to this file): assets/icons/<repo>.svg, assets/gremlin-matte.png
Outputs: <repo>.png per repository, contact-sheet-3col.png, manifest.json.
Exits non-zero when a check fails.
"""
import argparse
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

REPOS = [
    "wa", "chrome-bridge", "claude-mac-chrome", "linkedin-chrome-copilot",
    "fand", "kokoro-speakd", "anthropic-throttle-proxy", "claude-classroom-submit",
    "zellij-vertical-tabs", "noctalia-appmenu", "aferidor", "quality-gates",
    "claude-commands", "nixos-ops-skill", "speckit-plugins",
]
ORG = "yolo-labz"

# Canvas and colours (tokens: mocha base, mocha text, mocha subtext0, emerald)
W, H = 1280, 640
BG = "#1e1e2e"
EMERALD = "#00c77a"
NEAR_WHITE = "#cdd6f4"
MUTED = "#a6adc8"
BAR_H = 4

# Layout
ICON_PX = 96
LEFT = 56                      # left margin
TEXT_W = 720                   # left column width (text box and icon)
NAME_PT, NAME_MIN_PT = 64, 48  # name shrinks only when it would not fit TEXT_W
NAME_FONT = "Inter-Bold"
DESC_PT = 28
DESC_FONT = "Inter-Regular"
DESC_W = 560                   # description text box width (packet 22/11/2026)
DESC_MAX_LINES = 3
DESC_LINE_PITCH = 38
CLAUSE_WORDS = {"with", "and", "for", "so"}   # clause boundary: cut before these
BAD_END_WORDS = {"and", "with", "for", "to", "a", "the"}  # never end a cut on these
TEXT_BOTTOM_MARGIN = 24        # text block must stay this far above the bar
GREM_H = 520
GREM_RIGHT = W - 40
GREM_BOTTOM = H - BAR_H        # bottom-aligned on the bar
GAP_ICON_NAME = 28
GAP_NAME_DESC = 16


def sh(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def esc(text):
    return text.replace("%", "%%")


def measure(text, font, pt):
    out = sh(["magick", "-background", "none", "-font", font, "-pointsize", str(pt),
              f"label:{esc(text)}", "-format", "%w %h", "info:"]).stdout.split()
    return int(out[0]), int(out[1])


def label_png(text, font, pt, colour, path):
    sh(["magick", "-background", "none", "-font", font, "-pointsize", str(pt),
        "-fill", colour, f"label:{esc(text)}", path])


def wrap_lines(text):
    """Greedy wrap at DESC_W px. Returns the list of lines (no limit)."""
    words, lines, cur = text.split(" "), [], ""
    for word in words:
        cand = word if not cur else cur + " " + word
        if measure(cand, DESC_FONT, DESC_PT)[0] <= DESC_W or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def shown_text(desc):
    """Return (text, complete). Full description when it fits DESC_MAX_LINES.

    Otherwise the longest prefix that ends at a clause boundary (comma, period,
    or before a CLAUSE_WORDS word), fits, and does not end on a BAD_END_WORDS word.
    No ellipsis is added.
    """
    desc = " ".join(desc.split())
    if len(wrap_lines(desc)) <= DESC_MAX_LINES:
        return desc, True
    words = desc.split(" ")
    cuts = set()
    for i in range(1, len(words)):
        prev, nxt = words[i - 1], words[i].lower().strip(",.;:")
        if prev.endswith((",", ".", ";", ":")) or nxt in CLAUSE_WORDS:
            cuts.add(i)
    for n in sorted(cuts, reverse=True):
        text = " ".join(words[:n]).rstrip(",;:")
        last = text.split(" ")[-1].lower().strip(".,;:")
        if last in BAD_END_WORDS or not text:
            continue
        if len(wrap_lines(text)) <= DESC_MAX_LINES:
            return text, False
    raise SystemExit(f"no clause cut fits {DESC_MAX_LINES} lines: {desc!r}")


def fetch_description(repo):
    out = sh(["gh", "repo", "view", f"{ORG}/{repo}", "--json", "description", "-q", ".description"])
    return out.stdout.strip()


def overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def render(repo, desc_raw, icons_dir, gremlin, tmp, out_dir):
    checks = {}
    # 1. icon
    icon = os.path.join(tmp, f"{repo}-icon.png")
    sh(["rsvg-convert", "-w", str(ICON_PX), "-h", str(ICON_PX), "-o", icon,
        os.path.join(icons_dir, f"{repo}.svg")])

    # 2. name, shrunk only if it does not fit the column
    name_pt = NAME_PT
    nw, _ = measure(repo, NAME_FONT, name_pt)
    if nw > TEXT_W:
        name_pt = max(NAME_MIN_PT, math.floor(NAME_PT * TEXT_W / nw))
        nw, _ = measure(repo, NAME_FONT, name_pt)
    if nw > TEXT_W:
        raise SystemExit(f"{repo}: name does not fit at {NAME_MIN_PT} px")
    name_png = os.path.join(tmp, f"{repo}-name.png")
    label_png(repo, NAME_FONT, name_pt, NEAR_WHITE, name_png)
    _, name_h = measure(repo, NAME_FONT, name_pt)

    # 3. description: full text if it fits 3 lines, else a clause cut
    desc, complete = shown_text(desc_raw)
    lines = wrap_lines(desc)
    line_pngs = []
    for i, line in enumerate(lines):
        p = os.path.join(tmp, f"{repo}-desc{i}.png")
        label_png(line, DESC_FONT, DESC_PT, MUTED, p)
        line_pngs.append((p, measure(line, DESC_FONT, DESC_PT)))
    desc_h = (len(lines) - 1) * DESC_LINE_PITCH + line_pngs[0][1][1]

    # 4. vertical layout of the left column, centred above the bar
    block_h = ICON_PX + GAP_ICON_NAME + name_h + GAP_NAME_DESC + desc_h
    top = (GREM_BOTTOM - block_h) // 2
    icon_y = top
    name_y = icon_y + ICON_PX + GAP_ICON_NAME
    desc_y0 = name_y + name_h + GAP_NAME_DESC
    placements = [(icon, LEFT, icon_y), (name_png, LEFT, name_y)]
    for i, (p, (lw, lh)) in enumerate(line_pngs):
        placements.append((p, LEFT, desc_y0 + i * DESC_LINE_PITCH))

    # 5. gremlin: trimmed, height GREM_H, bottom-aligned, right side
    grem = os.path.join(tmp, f"{repo}-gremlin.png")
    sh(["magick", gremlin, "-trim", "+repage", "-resize", f"x{GREM_H}", grem])
    gw, gh = (int(x) for x in sh(["magick", "identify", "-format", "%w %h", grem]).stdout.split())
    gx, gy = GREM_RIGHT - gw, GREM_BOTTOM - gh
    placements.append((grem, gx, gy))

    # 6. bar
    bar = os.path.join(tmp, "bar.png")
    sh(["magick", "-size", f"{W}x{BAR_H}", f"xc:{EMERALD}", bar])
    placements.append((bar, 0, H - BAR_H))

    # 7. bounding boxes and checks
    text_boxes = [(LEFT, icon_y, LEFT + ICON_PX, icon_y + ICON_PX),
                  (LEFT, name_y, LEFT + nw, name_y + name_h)]
    for i, (_, (lw, lh)) in enumerate(line_pngs):
        y = desc_y0 + i * DESC_LINE_PITCH
        text_boxes.append((LEFT, y, LEFT + lw, y + lh))
    text_box = (LEFT, top, max(b[2] for b in text_boxes), desc_y0 + desc_h)
    grem_box = (gx, gy, gx + gw, gy + gh)
    checks["gremlin_overlaps_text"] = any(overlaps(b, grem_box) for b in text_boxes)
    checks["text_inside_left_column"] = text_box[2] <= LEFT + TEXT_W
    checks["description_complete"] = complete
    checks["description_ellipsis"] = "\u2026" in desc or desc.endswith("...")
    checks["description_ends_on_bad_word"] = desc.split(" ")[-1].lower().strip(".,;:") in BAD_END_WORDS
    checks["description_chars"] = len(desc)
    checks["text_bottom"] = desc_y0 + desc_h
    checks["text_bottom_ok"] = desc_y0 + desc_h <= GREM_BOTTOM - TEXT_BOTTOM_MARGIN
    checks["name_pt"] = name_pt
    checks["desc_lines"] = len(lines)
    if checks["gremlin_overlaps_text"] or not checks["text_inside_left_column"] or not checks["text_bottom_ok"]:
        raise SystemExit(f"{repo}: layout check failed {checks}")

    # 8. compose
    out = os.path.join(out_dir, f"{repo}.png")
    args = ["magick", "-size", f"{W}x{H}", f"xc:{BG}"]
    for p, x, y in placements:
        args += [p, "-geometry", f"+{x}+{y}", "-composite"]
    args += ["-strip", "-define", "png:compression-level=9", out]
    sh(args)

    # 9. file checks
    w, h = (int(x) for x in sh(["magick", "identify", "-format", "%w %h", out]).stdout.split())
    size = os.path.getsize(out)
    checks.update({"size": f"{w}x{h}", "bytes": size, "under_1MB": size < 1_000_000,
                   "is_1280x640": (w, h) == (W, H)})
    if not (checks["under_1MB"] and checks["is_1280x640"]):
        raise SystemExit(f"{repo}: file check failed {checks}")
    return {"repo": repo, "description_raw": desc_raw, "shown": desc,
            "lines": lines, "checks": checks, "file": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--icons", default=os.path.join(HERE, "assets", "icons"))
    ap.add_argument("--gremlin", default=os.path.join(HERE, "assets", "gremlin-matte.png"))
    a = ap.parse_args()
    import tempfile
    tmp = tempfile.mkdtemp(prefix="social-previews-")
    os.makedirs(a.out, exist_ok=True)
    results = []
    for repo in REPOS:
        results.append(render(repo, fetch_description(repo), a.icons, a.gremlin, tmp, a.out))
        print("ok", repo, results[-1]["checks"]["size"], results[-1]["checks"]["bytes"], flush=True)
    # 3-column contact sheet
    sheet = os.path.join(a.out, "contact-sheet-3col.png")
    files = [r["file"] for r in results]
    sh(["magick", "montage", *files, "-tile", "3x", "-geometry", "640x320+12+12",
        "-background", "#11111b", "-label", "%t", "-pointsize", "18", "-fill", "#cdd6f4",
        sheet])
    with open(os.path.join(a.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("sheet", sheet)
    print("all checks passed:", len(results))


if __name__ == "__main__":
    sys.exit(main())
