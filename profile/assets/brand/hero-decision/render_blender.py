"""Blender renders for the hero decision sheet — one session, native pixel sizes.

Run:  blender -b --factory-startup -P render_blender.py -- --model DIR --out DIR

Reuses model/render_hero.py's builders and per-frame camera fit, so each frame is
rendered natively at its slot size (exact-fit by construction), never rescaled.
The avatar slot frames the head only (front view), the way the vector kit's
gremlin-avatar.svg does; every other slot is the published hero pose.
"""

import argparse
import json
import os
import sys

import bpy

HEAD = {
    "head",
    "ear_L",
    "ear_R",
    "eye_0",
    "eye_1",
    "pupil_0",
    "pupil_1",
    "brow_L",
    "brow_R",
    "grin",
    "fang_0",
    "fang_1",
    "fang_2",
}

FRAMES = [
    # name, width, height, focus, view key
    ("org-887x640", 887, 640, None, "hero"),
    ("portfolio-804x770", 804, 770, None, "hero"),
    ("mobile-390x520", 390, 520, None, "hero"),
    ("avatar-96x96", 96, 96, "head", "front"),
]
MARGIN = {None: 0.06, "head": 0.10}


def main():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.model))
    import gremlin
    import render_hero

    with open(os.path.join(args.model, "params.json")) as handle:
        params0 = json.load(handle)
    views = {v["name"]: v for v in params0["render"]["views"]}
    hero = dict(params0["renders"]["view"])
    os.makedirs(args.out, exist_ok=True)

    for name, width, height, focus, key in FRAMES:
        params = json.loads(json.dumps(params0))
        view = hero if key == "hero" else {**views[key], "produced": False}
        params, objects = render_hero.build(params, view)
        camera = gremlin.build_rig(params, gremlin.build_materials(params))
        gremlin.configure_render(params, "workbench")
        scene = bpy.context.scene
        scene.render.resolution_x, scene.render.resolution_y = width, height
        scene.render.threads_mode, scene.render.threads = "FIXED", args.threads
        gremlin.place_camera(camera, 800.0, view["azimuth"], view["elevation"], params)
        fit = [o for o in objects if o.name in HEAD] if focus == "head" else objects
        assert fit, f"focus {focus!r} matched no objects"
        render_hero.fit_camera(camera, fit, width, height, MARGIN[focus])
        path = os.path.join(args.out, name + ".png")
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        gremlin.normalise_png(path)
        print(
            f"render_blender.py: {name} {width}x{height} focus={focus} objects={len(fit)}"
        )


if __name__ == "__main__":
    main()
