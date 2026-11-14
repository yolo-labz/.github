"""The gremlin mark's outline in model units.

``profile/assets/brand/mark/master.py`` holds the mark as SVG paths on a 16-unit grid.
This module reads those paths and maps them into the model's x/z plane (x right, z up,
the head centre at the origin) so the 3D face and ears are cut from the same numbers.
No Blender needed: ``python3 model/markshape.py`` prints a summary.
"""
from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

MASTER = Path(__file__).resolve().parent.parent / "profile/assets/brand/mark/master.py"
CENTER = (8.0, 9.75)  # the head's middle on the mark's grid (y down)


def master():
    spec = importlib.util.spec_from_file_location("mark_master", MASTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def segments(d):
    """Parse an absolute M/L/C/Q/Z path into [(command, [points...])]; points start at the pen."""
    tokens = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d)
    out, pen, i = [], None, 0
    need = {"M": 1, "L": 1, "C": 3, "Q": 2}
    while i < len(tokens):
        cmd = tokens[i]
        i += 1
        if cmd == "Z":
            continue
        n = need[cmd]
        pts = [(float(tokens[i + 2 * k]), float(tokens[i + 2 * k + 1])) for k in range(n)]
        i += 2 * n
        if cmd != "M":
            out.append((cmd, [pen] + pts))
        pen = pts[-1]
    return out


def bezier(pts, n):
    out = []
    for k in range(n):
        t = k / float(n - 1)
        row = list(pts)
        while len(row) > 1:
            row = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(row, row[1:])]
        out.append(row[0])
    return out


def polyline(d, n=14):
    """The path as a closed polygon, curves sampled ``n`` times."""
    pts = []
    for cmd, p in segments(d):
        part = [p[0], p[1]] if cmd == "L" else bezier(p, n)
        pts += part if not pts else part[1:]
    if pts and pts[0] == pts[-1]:
        pts.pop()
    return pts


class Frame:
    """Grid point (x, y down) to model (x, z up) for one unit size."""

    def __init__(self, unit):
        self.unit = unit

    def xz(self, p):
        return ((p[0] - CENTER[0]) * self.unit, -(p[1] - CENTER[1]) * self.unit)


def inside(poly, x, y):
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def reach(polys, angle, step=0.25, limit=400.0):
    """Distance from the origin along ``angle`` to the first exit from the union of ``polys``."""
    c, s = math.cos(angle), math.sin(angle)
    r = 0.0
    while r < limit and any(inside(p, r * c, r * s) for p in polys):
        r += step
    return r


def head_profile(frame, head_d, ear_ds, widen=1.25, samples=360, window=9):
    """Radius of the head outline for each angle, as a function of the angle.

    The head follows the mark's head path. Beside the eyes the ears fill the silhouette,
    so the head may grow there, up to ``widen`` times its own radius and never past the
    mark's outline: the eye sockets then sit on the front of the head and not on its rim.
    """
    head = [frame.xz(p) for p in polyline(head_d)]
    ears = [[frame.xz(p) for p in polyline(d)] for d in ear_ds]
    own, wide = [], []
    for k in range(samples):
        a = 2 * math.pi * k / samples
        r_head = reach([head], a)
        own.append(r_head)
        grow = 1.0 + (widen - 1.0) * max(0.0, 1.0 - (math.sin(a) / 0.6) ** 2)
        wide.append(max(r_head, min(reach([head] + ears, a), grow * r_head)))
    half = window // 2
    smooth = [sum(wide[(k + j) % samples] for j in range(-half, half + 1)) / window for k in range(samples)]
    smooth = [max(a, b) for a, b in zip(smooth, own)]

    def radius(angle):
        t = (angle % (2 * math.pi)) / (2 * math.pi) * samples
        k = int(t) % samples
        f = t - int(t)
        return smooth[k] * (1 - f) + smooth[(k + 1) % samples] * f

    return radius


if __name__ == "__main__":
    m = master()
    fr = Frame(9.6)
    prof = head_profile(fr, m.HEAD, [m.EAR_L, m.EAR_R])
    print("head radius at 0, 90, 180, 270 deg:", [round(prof(math.radians(a)), 1) for a in (0, 90, 180, 270)])
    print("eye L corners:", [tuple(round(v, 1) for v in fr.xz(p)) for p in polyline(m.EYE_L)][:4])
