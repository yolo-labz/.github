"""render_hero.py -- the hero pose at fixed frame sizes, one Blender session.

Called by ``model/renders.py``; not a user entry point.  Every number comes from
``params.json`` and every mesh from ``gremlin.py``, so a published render cannot
disagree with the model or with ``make model``.

The camera is *fitted* to the character per frame instead of cropping a single big
render: an orthographic camera whose ``ortho_scale`` is derived from the evaluated
content bounds, so a 4:3 plate, a square crop and a portrait plate all frame the
gremlin at the same optical size with the same margin, and no empty plate is
carried into a consumer's `<img>`.
"""

import argparse
import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gremlin  # noqa: E402  (needs sys.path first; imports bpy only)


def parse_args(argv):
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="JSON list of frames to render")
    parser.add_argument("--out", required=True)
    parser.add_argument("--threads", type=int, default=4)
    return parser.parse_args(argv)


def build(params, view):
    """Build the character for one pose and return (params, objects to render)."""
    gremlin.reset_scene()
    mats = gremlin.build_materials(params)
    groups = {}
    groups.update(gremlin.build_head(params, mats))
    groups.update(gremlin.build_body(params, mats))
    for pose in ("rest", "reach"):
        groups.update(
            gremlin.build_arm(pose, params["body"]["arms3d"][pose], params, mats)
        )
    groups.update(gremlin.build_keyboard(params, mats))
    gremlin.tilt_keyboard(
        {name: obj for name, obj in groups.items() if name.startswith("kb_")}, params
    )
    groups.update(gremlin.build_produced(params, mats))

    for name, obj in groups.items():
        visible = True
        if name.startswith("arm_") or name.startswith("claw_"):
            visible = ("_%s_" % view["pose"]) in name
        if name.startswith("code_"):
            visible = bool(view["produced"])
        obj.hide_render = not visible
    return params, [obj for obj in groups.values() if not obj.hide_render]


def content_bounds(camera, objects):
    """Camera-space bounds of the evaluated geometry.

    Evaluated, because curves (limbs, brows, the case outline) only have their
    bevel geometry after the depsgraph runs.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    inverse = camera.matrix_world.inverted()
    xs, ys = [], []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            point = inverse @ (evaluated.matrix_world @ Vector(corner))
            xs.append(point.x)
            ys.append(point.y)
    return min(xs), max(xs), min(ys), max(ys)


def fit_camera(camera, objects, width, height, margin):
    """Centre the content and size ``ortho_scale`` so it fills the frame."""
    camera.data.sensor_fit = "HORIZONTAL"
    xmin, xmax, ymin, ymax = content_bounds(camera, objects)
    basis = camera.matrix_world.to_3x3()
    camera.location = (
        camera.location
        + basis @ Vector((1.0, 0.0, 0.0)) * ((xmin + xmax) / 2.0)
        + basis @ Vector((0.0, 1.0, 0.0)) * ((ymin + ymax) / 2.0)
    )
    bpy.context.view_layer.update()
    xmin, xmax, ymin, ymax = content_bounds(camera, objects)
    span_x, span_y = xmax - xmin, ymax - ymin
    camera.data.ortho_scale = max(span_x, span_y * width / float(height)) * (
        1.0 + margin
    )
    return span_x, span_y, camera.data.ortho_scale


def main():
    args = parse_args(list(sys.argv))
    with open(args.spec, "r", encoding="utf-8") as handle:
        spec = json.load(handle)
    with open(spec["params"], "r", encoding="utf-8") as handle:
        base_params = json.load(handle)

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    for frame in spec["frames"]:
        params = json.loads(json.dumps(base_params))
        if frame["theme"] != "dark":
            params["palette"] = params["palette_light"]

        params, objects = build(params, spec["view"])
        camera = gremlin.build_rig(params, gremlin.build_materials(params))
        gremlin.configure_render(params, "workbench")
        scene = bpy.context.scene
        scene.render.resolution_x = int(frame["width"])
        scene.render.resolution_y = int(frame["height"])
        scene.render.threads_mode = "FIXED"
        scene.render.threads = args.threads

        gremlin.place_camera(
            camera, 800.0, spec["view"]["azimuth"], spec["view"]["elevation"], params
        )
        span_x, span_y, scale = fit_camera(
            camera, objects, frame["width"], frame["height"], spec["margin"]
        )
        path = os.path.join(out_dir, frame["file"])
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        gremlin.normalise_png(path)
        print(
            "render_hero.py: %s %dx%d %s content %.0fx%.0f ortho %.1f"
            % (frame["file"], frame["width"], frame["height"], frame["theme"],
               span_x, span_y, scale)
        )

    print("render_hero.py: done, %d frames" % len(spec["frames"]))


if __name__ == "__main__":
    main()
