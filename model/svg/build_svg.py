#!/usr/bin/env python3
"""build_svg.py -- regenerate the flat gremlin avatar from ``model/params.json``.

    python3 model/svg/build_svg.py --out build

The generated SVG is a *derivative*, not a copy: every coordinate, radius and
colour is read out of params.json and mirrored/projected by this script, so
changing a studio number changes the vector mark too.  The script also
rasterises the result next to the frozen kit master so ``model/check.py`` can
score the silhouette IoU.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.dirname(HERE)
REPO = os.path.dirname(MODEL)
PARAMS = os.path.join(MODEL, "params.json")


def num(value):
    text = "%g" % float(value)
    return "0" if text == "-0" else text


def pair(point, sign=1.0):
    return "%s %s" % (num(point[0] * sign), num(point[1]))


def ear_path(ear, sign):
    return (
        "M %s C %s %s %s C %s %s %s Z" % (
            pair(ear["start"], sign),
            pair(ear["c1"], sign), pair(ear["c2"], sign), pair(ear["tip"], sign),
            pair(ear["c3"], sign), pair(ear["c4"], sign), pair(ear["base"], sign),
        )
    )


def grin_path(grin):
    return "M %s Q %s %s Q %s %s Z" % (
        pair(grin["start"]), pair(grin["c1"]), pair(grin["c2"]),
        pair(grin["c3"]), pair(grin["start"]),
    )


def fang_path(fang):
    (x0, y0), (x1, y1), (x2, y2) = fang
    return "M %s L %s L %s Z" % (
        pair((x0, y0)), pair((x1, y1)), pair((x2, y2)))


def build_svg(params):
    head = params["head"]
    palette = params["palette"]
    svg_cfg = params["svg"]
    width = svg_cfg["viewBox"][2]
    height = svg_cfg["viewBox"][3]
    radii = head["ellipse2d"]
    brow = head["brow"]
    eyes = head["eyes"]
    tx, ty = svg_cfg["figure"]["translate"]

    dark_style = (
        "  .bg   { fill: %(base)s; }\n"
        "  .skin { fill: %(skin)s; stroke: %(skin)s;\n"
        "          stroke-linejoin: round; stroke-linecap: round; }\n"
        "  .pale { fill: %(pale)s; stroke: %(pale)s;\n"
        "          stroke-linejoin: round; stroke-linecap: round; }\n"
        "  .dark { fill: %(dark)s; }\n"
        "  .node { fill: %(node)s; }\n"
    ) % {k: palette[k]["hex"] for k in ("base", "skin", "pale", "dark", "node")}

    body = []
    for sign in (1.0, -1.0):
        body.append('    <path class="skin" stroke-width="6" d="%s"/>'
                    % ear_path(head["ear"], sign))
    body.append('    <ellipse class="skin" rx="%s" ry="%s" stroke-width="6"/>'
                % (num(radii[0]), num(radii[1])))
    for center in eyes["centers"]:
        body.append('    <circle class="pale" cx="%s" cy="%s" r="%s"/>'
                    % (num(center[0]), num(center[1]), num(eyes["r"])))
    for pupil in head["pupils"]:
        body.append('    <circle class="node" cx="%s" cy="%s" r="%s"/>'
                    % (num(pupil["at"][0]), num(pupil["at"][1]), num(pupil["r"])))
    for sign in (1.0, -1.0):
        body.append('    <path class="skin" stroke-width="%s" style="fill:none" '
                    'd="M %s L %s"/>'
                    % (num(brow["width"]), pair(brow["outer"], sign),
                       pair(brow["inner"], sign)))
    body.append('    <path class="dark" d="%s"/>' % grin_path(head["grin"]))
    for fang in head["fangs"]:
        body.append('    <path class="pale" d="%s"/>' % fang_path(fang))

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" '
        'height="%s" role="img" aria-labelledby="t d">\n'
        '  <title id="t">yolo-labz avatar \u2014 gremlin head</title>\n'
        '  <desc id="d">Generated from model/params.json by model/svg/build_svg.py. '
        'Pointed ears, node pupils, fang grin \u2014 the org social avatar.</desc>\n'
        '  <!-- GENERATED FILE \u2014 edit model/params.json, not this SVG. -->\n'
        '  <style>\n'
        '%s'
        '    @media (prefers-color-scheme: light) {\n'
        '      .bg   { fill: #eff1f5; }\n'
        '      .skin { fill: #40a02b; stroke: #40a02b; }\n'
        '      .pale { fill: #dce0e8; stroke: #dce0e8; }\n'
        '      .dark { fill: #bcc0cc; }\n'
        '      .node { fill: #8839ef; }\n'
        '    }\n'
        '  </style>\n'
        '  <rect class="bg" width="%s" height="%s" rx="%s"/>\n'
        '  <g transform="translate(%s %s) scale(%s)">\n'
        '%s\n'
        '  </g>\n'
        '</svg>\n'
    ) % (
        num(width), num(height), num(width), num(height),
        dark_style,
        num(width), num(height), num(svg_cfg["tile_radius"]),
        num(tx), num(ty), num(svg_cfg["figure"]["scale"]),
        "\n".join(body),
    )


def rasterise(source, target, pixels):
    subprocess.run(
        ["rsvg-convert", "-w", str(pixels), "-h", str(pixels), source,
         "-o", target],
        check=True,
    )


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build")
    parser.add_argument("--params", default=PARAMS)
    args = parser.parse_args(argv)

    with open(args.params, "r", encoding="utf-8") as handle:
        params = json.load(handle)

    out = os.path.abspath(args.out)
    compare = os.path.join(out, "compare")
    os.makedirs(compare, exist_ok=True)

    generated = os.path.join(out, "gremlin-avatar.svg")
    with open(generated, "w", encoding="utf-8") as handle:
        handle.write(build_svg(params))
    print("build_svg.py: wrote %s" % generated)

    pixels = params["svg"]["raster_px"]
    rasterise(generated, os.path.join(compare, "generated.png"), pixels)
    target = os.path.join(REPO, params["svg"]["compare_target"])
    if not os.path.exists(target):
        print("build_svg.py: missing kit master %s" % target, file=sys.stderr)
        return 1
    rasterise(target, os.path.join(compare, "kit.png"), pixels)
    print("build_svg.py: wrote %s/{generated,kit}.png @ %dpx"
          % (compare, pixels))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
