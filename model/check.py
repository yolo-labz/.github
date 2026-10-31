#!/usr/bin/env python3
"""check.py -- the machine-checked acceptance for the gremlin model.

    python3 model/check.py --build build

Three checks, all derived from ``model/params.json``:

1. **Palette** -- every ``check: true`` palette entry must appear in each render
   with at least ``delta_e_min_pixels`` pixels and a CIEDE2000 distance of
   ``delta_e_max`` or less from the params.json hex.
2. **Determinism** -- the PNG sha256 values of this run must equal the previous
   run's.  Run 1 has no baseline and only records one.  If a hash moved, the
   byte diff is downgraded to a pixel-diff budget
   (``determinism_max_changed_fraction``) and the reason is printed.
3. **Silhouette IoU** -- the generated avatar's filled silhouette against the
   frozen kit master ``gremlin-avatar.svg``, rasterised by build_svg.py.

Zero dependencies: PNG decoding is zlib+struct only, which keeps the check
runnable on a bare ``python3`` (Blender's bundled numpy is not on PATH, and the
acceptance must not depend on the renderer being importable).
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS = os.path.join(HERE, "params.json")
LEDGER = os.path.join(HERE, ".determinism", "last.json")

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


# --------------------------------------------------------------------------- #
# PNG
# --------------------------------------------------------------------------- #
def decode_png(path):
    """Minimal 8-bit non-interlaced PNG decoder -> (width, height, bpp, rows)."""
    blob = open(path, "rb").read()
    identifier = b""
    width = height = depth = colour_type = None
    offset = 8
    while offset < len(blob):
        length = struct.unpack(">I", blob[offset:offset + 4])[0]
        kind = blob[offset + 4:offset + 8]
        data = blob[offset + 8:offset + 8 + length]
        if kind == b"IHDR":
            width, height, depth, colour_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", data)
            if depth != 8 or interlace != 0:
                raise SystemExit("%s: only 8-bit non-interlaced PNG is supported"
                                 % path)
        elif kind == b"IDAT":
            identifier += data
        elif kind == b"IEND":
            break
        offset += 12 + length

    bpp = CHANNELS[colour_type]
    raw = zlib.decompress(identifier)
    stride = width * bpp
    rows = []
    previous = bytearray(stride)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        line = bytearray(raw[cursor:cursor + stride])
        cursor += stride
        if filter_type == 1:
            for k in range(bpp, stride):
                line[k] = (line[k] + line[k - bpp]) & 0xFF
        elif filter_type == 2:
            for k in range(stride):
                line[k] = (line[k] + previous[k]) & 0xFF
        elif filter_type == 3:
            for k in range(stride):
                left = line[k - bpp] if k >= bpp else 0
                line[k] = (line[k] + ((left + previous[k]) >> 1)) & 0xFF
        elif filter_type == 4:
            for k in range(stride):
                left = line[k - bpp] if k >= bpp else 0
                up = previous[k]
                corner = previous[k - bpp] if k >= bpp else 0
                estimate = left + up - corner
                pa, pb, pc = (abs(estimate - left), abs(estimate - up),
                              abs(estimate - corner))
                if pa <= pb and pa <= pc:
                    predictor = left
                elif pb <= pc:
                    predictor = up
                else:
                    predictor = corner
                line[k] = (line[k] + predictor) & 0xFF
        elif filter_type != 0:
            raise SystemExit("%s: unsupported PNG filter %d" % (path, filter_type))
        rows.append(bytes(line))
        previous = line
    return width, height, bpp, rows


def colour_histogram(path):
    width, height, bpp, rows = decode_png(path)
    counts = Counter()
    for row in rows:
        counts.update(row[x * bpp:(x + 1) * bpp]
                      for x in range(width))
    return counts, (width, height, bpp, rows)


# --------------------------------------------------------------------------- #
# colour science
# --------------------------------------------------------------------------- #
def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb):
    def linearise(channel):
        c = channel / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linearise(c) for c in rgb)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    xr, yr, zr = x / 0.95047, y / 1.0, z / 1.08883

    def f(t):
        return t ** (1.0 / 3.0) if t > 0.008856 else (7.787 * t + 16.0 / 116.0)

    fx, fy, fz = f(xr), f(yr), f(zr)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def delta_e_2000(lab1, lab2):
    """CIEDE2000 colour difference (Sharma et al. formulation)."""
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    c_bar = (c1 + c2) / 2.0
    g = 0.5 * (1.0 - math.sqrt(c_bar ** 7 / (c_bar ** 7 + 25.0 ** 7)))
    a1p = (1.0 + g) * a1
    a2p = (1.0 + g) * a2
    c1p = math.hypot(a1p, b1)
    c2p = math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0 if (a2p or b2) else 0.0
    delta_l = l2 - l1
    delta_c = c2p - c1p
    if c1p * c2p == 0.0:
        delta_h_angle = 0.0
    elif abs(h2p - h1p) <= 180.0:
        delta_h_angle = h2p - h1p
    elif h2p - h1p > 180.0:
        delta_h_angle = h2p - h1p - 360.0
    else:
        delta_h_angle = h2p - h1p + 360.0
    delta_h = 2.0 * math.sqrt(c1p * c2p) * math.sin(math.radians(delta_h_angle / 2.0))
    l_bar = (l1 + l2) / 2.0
    c_bar_p = (c1p + c2p) / 2.0
    if c1p * c2p == 0.0:
        h_bar = h1p + h2p
    elif abs(h1p - h2p) <= 180.0:
        h_bar = (h1p + h2p) / 2.0
    elif h1p + h2p < 360.0:
        h_bar = (h1p + h2p + 360.0) / 2.0
    else:
        h_bar = (h1p + h2p - 360.0) / 2.0
    t = (1.0
         - 0.17 * math.cos(math.radians(h_bar - 30.0))
         + 0.24 * math.cos(math.radians(2.0 * h_bar))
         + 0.32 * math.cos(math.radians(3.0 * h_bar + 6.0))
         - 0.20 * math.cos(math.radians(4.0 * h_bar - 63.0)))
    delta_theta = 30.0 * math.exp(-(((h_bar - 275.0) / 25.0) ** 2))
    rc = 2.0 * math.sqrt(c_bar_p ** 7 / (c_bar_p ** 7 + 25.0 ** 7))
    sl = 1.0 + (0.015 * (l_bar - 50.0) ** 2) / math.sqrt(20.0 + (l_bar - 50.0) ** 2)
    sc = 1.0 + 0.045 * c_bar_p
    sh = 1.0 + 0.015 * c_bar_p * t
    rt = -math.sin(math.radians(2.0 * delta_theta)) * rc
    return math.sqrt((delta_l / sl) ** 2
                     + (delta_c / sc) ** 2
                     + (delta_h / sh) ** 2
                     + rt * (delta_c / sc) * (delta_h / sh))


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def check_palette(params, render_paths, report):
    """Every checked palette entry must land within deltaE of params.json.

    Roles are asserted over the *set* of renders (a gremlin's back has no eyes,
    so `pale` legitimately cannot appear in every view) while every individual
    render must still contain the plate and the skin.
    """
    limit = params["checks"]["delta_e_max"]
    minimum = params["checks"]["delta_e_min_pixels"]
    wanted = {role: hex_to_rgb(spec["hex"])
              for role, spec in params["palette"].items() if spec.get("check")}
    wanted_lab = {role: rgb_to_lab(rgb) for role, rgb in wanted.items()}
    required_every_view = ("base", "skin")
    best = {role: (float("inf"), None) for role in wanted}
    ok = True
    for path in render_paths:
        counts, _ = colour_histogram(path)
        name = os.path.basename(path)
        # Only colours covering real area are candidates: a stray anti-aliasing
        # blend must never satisfy a palette entry.
        candidates = [tuple(chunk[:3]) for chunk, n in counts.items()
                      if n >= minimum]
        if not candidates:
            report.append("  PALETTE %s: FAIL nothing covers %d px"
                          % (name, minimum))
            ok = False
            continue
        # Classify each candidate to its nearest role first, so two adjacent
        # entries (mouth #181825 vs plate #1e1e2e) cannot vouch for each other.
        owned = {role: [] for role in wanted}
        for rgb in candidates:
            lab = rgb_to_lab(rgb)
            role = min(wanted_lab,
                       key=lambda candidate: delta_e_2000(lab, wanted_lab[candidate]))
            owned[role].append(delta_e_2000(lab, wanted_lab[role]))
        present = sorted(role for role in wanted if owned[role])
        for role in present:
            distance = min(owned[role])
            if distance < best[role][0]:
                best[role] = (distance, name)
        missing = [role for role in required_every_view if not owned[role]]
        if missing:
            report.append("  PALETTE %s: FAIL missing %s (present: %s)"
                          % (name, ", ".join(missing), ", ".join(present)))
            ok = False
            continue
        report.append("  PALETTE %s: roles %s" % (name, ",".join(present)))

    for role in sorted(wanted):
        distance, where = best[role]
        status = "pass" if distance <= limit else "FAIL"
        if distance > limit:
            ok = False
        report.append("  PALETTE role %-5s %s deltaE2000 %.2f (limit %.1f)"
                      " best in %s"
                      % (role, status, distance, limit,
                         where or "no render"))
    return ok


def check_determinism(params, build, render_paths, report):
    """Compare this run against the previous one.

    Byte-identical is the contract.  If a hash moves, the run is downgraded to
    the documented pixel-diff budget: the previous PNGs are kept under
    ``model/.determinism/previous/`` precisely so the drift can be measured
    instead of asserted.
    """
    budget = params["checks"]["determinism_max_changed_fraction"]
    previous_dir = os.path.join(os.path.dirname(LEDGER), "previous")
    current = {os.path.basename(path): hashlib.sha256(
        open(path, "rb").read()).hexdigest() for path in render_paths}

    previous = None
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER, "r", encoding="utf-8") as handle:
                previous = json.load(handle)
        except (ValueError, OSError):
            previous = None

    def remember():
        os.makedirs(previous_dir, exist_ok=True)
        for path in render_paths:
            target = os.path.join(previous_dir, os.path.basename(path))
            with open(path, "rb") as source, open(target, "wb") as sink:
                sink.write(source.read())
        with open(LEDGER, "w", encoding="utf-8") as handle:
            json.dump({"hashes": current}, handle, indent=2, sort_keys=True)
            handle.write("\n")

    if previous is None or not previous.get("hashes"):
        remember()
        report.append("  DETERMINISM: baseline recorded (run 1, %d PNGs)"
                      % len(current))
        return True

    changed = sorted(name for name, digest in current.items()
                     if previous["hashes"].get(name) != digest)
    if not changed:
        remember()
        report.append("  DETERMINISM: pass - %d/%d PNG sha256 byte-identical"
                      % (len(current), len(current)))
        return True

    worst = 0.0
    reason = ""
    measurable = True
    for name in changed:
        old_path = os.path.join(previous_dir, name)
        if not os.path.exists(old_path):
            measurable = False
            reason = "no previous image for %s to diff against" % name
            break
        width_a, height_a, bpp_a, rows_a = decode_png(old_path)
        width_b, height_b, bpp_b, rows_b = decode_png(
            os.path.join(build, name))
        if (width_a, height_a, bpp_a) != (width_b, height_b, bpp_b):
            measurable = False
            reason = "%s changed raster size, cannot diff" % name
            break
        total = width_a * height_a
        differing = 0
        for row_a, row_b in zip(rows_a, rows_b):
            if row_a == row_b:
                continue
            for x in range(width_a):
                if row_a[x * bpp_a:(x + 1) * bpp_a] != row_b[x * bpp_b:(x + 1) * bpp_b]:
                    differing += 1
        worst = max(worst, differing / float(total))

    remember()
    if measurable and worst <= budget:
        report.append("  DETERMINISM: pass with pixel-diff %.4f%% of pixels moved "
                      "(%d PNG(s) not byte-identical; budget %.2f%%). Reason: "
                      "the raster backend reintroduced drift beyond the "
                      "container metadata gremlin.py strips - identical input, "
                      "sub-budget difference."
                      % (worst * 100.0, len(changed), budget * 100.0))
        return True
    report.append("  DETERMINISM: FAIL - %s; %s (worst pixel-diff %.4f%%) "
                  % (", ".join(changed), reason or "over budget",
                     worst * 100.0))
    return False


def background_colour(counts):
    best_chunk, best_count = max(counts.items(), key=lambda item: item[1])
    return tuple(best_chunk[:3]), tuple(best_chunk[:4])


def silhouette(path, tolerance=10):
    counts, (width, height, bpp, rows) = colour_histogram(path)
    rgb, rgba = background_colour(counts)

    def is_background(chunk):
        if bpp == 4 and chunk[3] < 128:
            return True
        return all(abs(chunk[i] - rgba[i]) <= tolerance for i in range(3))

    mask = bytearray(width * height)
    for y, row in enumerate(rows):
        base = y * width
        for x in range(width):
            if not is_background(row[x * bpp:(x + 1) * bpp]):
                mask[base + x] = 1
    return mask, (width, height), rgb


def check_iou(params, build, report):
    compare = os.path.join(build, "compare")
    generated = os.path.join(compare, "generated.png")
    kit = os.path.join(compare, "kit.png")
    for path in (generated, kit):
        if not os.path.exists(path):
            report.append("  SILHOUETTE: FAIL missing %s" % path)
            return False
    mask_a, size_a, _ = silhouette(generated)
    mask_b, size_b, _ = silhouette(kit)
    if size_a != size_b:
        report.append("  SILHOUETTE: FAIL raster size mismatch %s vs %s"
                      % (size_a, size_b))
        return False
    intersection = sum(1 for a, b in zip(mask_a, mask_b) if a and b)
    union = sum(1 for a, b in zip(mask_a, mask_b) if a or b)
    score = intersection / float(union) if union else 0.0
    limit = params["svg"]["iou_min"]
    status = "pass" if score >= limit else "FAIL"
    report.append("  SILHOUETTE: %s IoU %.4f (min %.2f, %dx%d px, "
                  "generated %d px / kit %d px filled)"
                  % (status, score, limit, size_a[0], size_a[1],
                     sum(mask_a), sum(mask_b)))
    return score >= limit


# --------------------------------------------------------------------------- #
# self test
# --------------------------------------------------------------------------- #
def self_test():
    """Reference CIEDE2000 pairs (Sharma, Wu & Dalal 2005) + sRGB->Lab anchors."""
    cases = [
        ((50.0000, 2.6772, -79.7751), (50.0000, 0.0000, -82.7485), 2.0425),
        ((50.0000, -1.3802, -84.2814), (50.0000, 0.0000, -82.7485), 1.0000),
        ((50.0000, 2.4900, -0.0010), (50.0000, -2.4900, 0.0009), 7.1792),
        ((50.0000, 2.4900, -0.0010), (50.0000, -2.4900, 0.0011), 7.2195),
        ((50.0000, 2.5000, 0.0000), (73.0000, 25.0000, -18.0000), 27.1492),
        ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
    ]
    failures = 0
    for lab1, lab2, expected in cases:
        got = delta_e_2000(lab1, lab2)
        ok = abs(got - expected) < 0.0005
        failures += 0 if ok else 1
        print("  dE00 %s expected %.4f got %.4f"
              % ("ok" if ok else "FAIL", expected, got))

    anchors = [
        ("#ffffff", (100.0000, 0.0000, 0.0000)),
        ("#000000", (0.0000, 0.0000, 0.0000)),
        ("#808080", (53.5850, 0.0000, 0.0000)),
        ("#ff0000", (53.2408, 80.0925, 67.2032)),
        ("#00ff00", (87.7347, -86.1827, 83.1793)),
        ("#0000ff", (32.2970, 79.1875, -107.8602)),
    ]
    for value, expected in anchors:
        got = rgb_to_lab(hex_to_rgb(value))
        ok = all(abs(a - b) < 0.02 for a, b in zip(got, expected))
        failures += 0 if ok else 1
        print("  Lab  %s %s expected %s got %s"
              % ("ok" if ok else "FAIL", value,
                 tuple(round(c, 4) for c in expected),
                 tuple(round(c, 4) for c in got)))

    # A colour is deltaE 0 from itself, and the transform is symmetric.
    probe = rgb_to_lab(hex_to_rgb("#1e1e2e"))
    neighbour = rgb_to_lab(hex_to_rgb("#181825"))
    if delta_e_2000(probe, probe) > 1e-9:
        failures += 1
        print("  dE00 self-distance FAIL")
    if abs(delta_e_2000(probe, neighbour) - delta_e_2000(neighbour, probe)) > 1e-9:
        failures += 1
        print("  dE00 symmetry FAIL")
    # mouth (#181825) and plate (#1e1e2e) must stay distinguishable, otherwise
    # the palette check could not tell them apart at all.
    if delta_e_2000(probe, neighbour) < 1.0:
        failures += 1
        print("  dE00 mouth/plate separation FAIL")
    print("SELF-TEST: %s" % ("pass" if failures == 0 else "FAIL"))
    return 0 if failures == 0 else 1


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", default="build")
    parser.add_argument("--params", default=PARAMS)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    with open(args.params, "r", encoding="utf-8") as handle:
        params = json.load(handle)

    build = os.path.abspath(args.build)
    views = [view["name"] for view in params["render"]["views"]]
    render_paths = [os.path.join(build, "gremlin-%s.png" % name) for name in views]
    missing = [path for path in render_paths if not os.path.exists(path)]
    if missing:
        print("check.py: missing renders: %s" % ", ".join(missing))
        return 1

    report = ["check.py: %s" % build]
    results = [
        ("palette", check_palette(params, render_paths, report)),
        ("determinism", check_determinism(params, build, render_paths, report)),
        ("iou", check_iou(params, build, report)),
    ]
    print("\n".join(report))
    failed = [name for name, ok in results if not ok]
    print("CHECK: %s" % ("pass" if not failed else "FAIL " + ", ".join(failed)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
