"""gremlin.py -- procedural build of the yolo-labz programming gremlin.

    blender -b --factory-startup -t 4 -P model/gremlin.py -- --out build/

Every proportion and colour comes from ``model/params.json`` (one source of
truth).  Nothing here is freehand: the 2D sections of params.json are lifted
from the frozen masters in ``profile/assets/brand/mascot/`` and this script
only re-interprets them in three dimensions.

Rendering defaults to Blender *Workbench* with FLAT lighting and
``view_transform='Standard'``.  That combination writes the material albedo
byte-for-byte to the PNG, so the palette check in ``model/check.py`` can assert
an exact (deltaE 0) match against params.json and the whole run is analytically
deterministic -- no stochastic sampling, no denoiser, no seed to leak.  It is
also the brand's own grammar: filled forms, flat ink, no gradients (mascot
README rule 3), so shading would be a defect rather than a nicety.

``--engine eevee`` switches to a shaded pass through the fixed camera/light rig
for a volume reference; that pass is *not* part of the acceptance contract.
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# PNG normalisation is shared with model/cards.py: one implementation, because a
# second copy is how the two outputs would drift apart.
from pngmeta import normalise_png

PARAMS = os.path.join(HERE, "params.json")


# --------------------------------------------------------------------------- #
# arguments
# --------------------------------------------------------------------------- #
def parse_args(argv):
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    opts = {"out": "build", "engine": "workbench", "views": None}
    it = iter(argv)
    for arg in it:
        if arg == "--out":
            opts["out"] = next(it)
        elif arg == "--engine":
            opts["engine"] = next(it)
        elif arg == "--views":
            opts["views"] = next(it).split(",")
        else:
            raise SystemExit("gremlin.py: unknown argument %r" % arg)
    return opts


# --------------------------------------------------------------------------- #
# colour
# --------------------------------------------------------------------------- #
def srgb_to_linear(channel):
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear_rgba(value, alpha=1.0):
    value = value.lstrip("#")
    return tuple(srgb_to_linear(int(value[i:i + 2], 16)) for i in (0, 2, 4)) + (alpha,)


def make_material(name, hex_value):
    mat = bpy.data.materials.new(name)
    rgba = hex_to_linear_rgba(hex_value)
    # Workbench reads diffuse_color; Eevee reads the Principled BSDF.
    mat.diffuse_color = rgba
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    if node is not None:
        for socket, value in (("Base Color", rgba), ("Roughness", 0.55),
                              ("Specular IOR Level", 0.15)):
            if socket in node.inputs:
                node.inputs[socket].default_value = value
    return mat


# --------------------------------------------------------------------------- #
# mesh helpers
# --------------------------------------------------------------------------- #
def finish(name, bm, material):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def ellipsoid(name, center, radii, material, segments=48, rings=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    cx, cy, cz = center
    rx, ry, rz = radii
    for vert in bm.verts:
        vert.co = Vector((vert.co.x * rx + cx,
                          vert.co.y * ry + cy,
                          vert.co.z * rz + cz))
    bm.normal_update()
    return finish(name, bm, material)


def cone(name, start, end, r_start, r_end, material, segments=20, squash=1.0,
         thin_dir=(0.0, 1.0, 0.0)):
    """Tapered cone from ``start`` to ``end``, flattened along ``thin_dir``.

    The basis is built explicitly (thin axis projected into the plane
    perpendicular to the ear axis) so the blade stays a blade no matter how the
    axis is swept -- ``to_track_quat`` would silently rotate the squash axis.
    """
    start, end = Vector(start), Vector(end)
    axis = end - start
    length = axis.length
    unit = axis.normalized()
    thin = Vector(thin_dir) - unit * Vector(thin_dir).dot(unit)
    if thin.length < 1e-6:
        thin = Vector((1.0, 0.0, 0.0)) - unit * unit.x
    thin.normalize()
    side = thin.cross(unit).normalized()
    basis = Matrix((side, thin, unit)).transposed().to_4x4()
    transform = (
        Matrix.Translation((start + end) / 2.0)
        @ basis
        @ Matrix.Diagonal(Vector((1.0, squash, 1.0, 1.0)))
    )
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=r_start,
        radius2=r_end,
        depth=length,
        matrix=transform,
    )
    bm.normal_update()
    return finish(name, bm, material)


def prism(name, outline_xy, z_bottom, z_top, material):
    """Extrude a closed outline given in the XY plane between two Z heights."""
    bm = bmesh.new()
    bottom = [bm.verts.new((x, y, z_bottom)) for x, y in outline_xy]
    top = [bm.verts.new((x, y, z_top)) for x, y in outline_xy]
    bm.faces.new(bottom)
    bm.faces.new(top)
    count = len(outline_xy)
    for i in range(count):
        j = (i + 1) % count
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(name, bm, material)


def surface_patch(name, outline_xz, radii, offset, thickness, material):
    """A closed shell hugging the front of the head ellipsoid.

    ``outline_xz`` is projected onto the ellipsoid so the mouth and fangs wrap
    around the face instead of floating in front of it.
    """
    rx, ry, rz = radii

    def project(x, z):
        t = 1.0 - (x / rx) ** 2 - (z / rz) ** 2
        t = math.sqrt(t) if t > 0.0 else 0.0
        return -ry * t - offset

    bm = bmesh.new()
    front = [bm.verts.new((x, project(x, z), z)) for x, z in outline_xz]
    back = [bm.verts.new((x, project(x, z) + thickness, z)) for x, z in outline_xz]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    count = len(outline_xz)
    for i in range(count):
        j = (i + 1) % count
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(name, bm, material)


def polyline(name, points, radius, material, smooth=False):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    curve.fill_mode = "FULL"
    curve.use_fill_caps = True
    if smooth:
        spline = curve.splines.new("BEZIER")
        spline.bezier_points.add(len(points) - 1)
        for point, co in zip(spline.bezier_points, points):
            point.co = Vector(co)
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    else:
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, co in zip(spline.points, points):
            point.co = Vector(co).to_4d()
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


# --------------------------------------------------------------------------- #
# 2D -> 3D projection helpers
# --------------------------------------------------------------------------- #
def quad_samples(p0, c, p1, count):
    """Sample a quadratic bezier, endpoints included."""
    out = []
    for i in range(count):
        t = i / float(count - 1)
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
                    u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]))
    return out


def head_surface_y(x, z, radii):
    rx, ry, rz = radii
    t = 1.0 - (x / rx) ** 2 - (z / rz) ** 2
    t = math.sqrt(t) if t > 0.0 else 0.0
    return -ry * t


def svg_to_xz(point):
    """SVG head-local [x, y] (y down) -> 3D [x, z] (z up)."""
    return point[0], -point[1]


# --------------------------------------------------------------------------- #
# scene
# --------------------------------------------------------------------------- #
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("world")
    return scene


def build_materials(params):
    mats = {}
    for role, spec in params["palette"].items():
        mats[role] = make_material("m_" + role, spec["hex"])
    return mats


def build_head(params, mats):
    head = params["head"]
    radii = head["radii3d"]
    objs = {"head": ellipsoid("head", (0, 0, 0), radii, mats["skin"])}

    ear = head["ear"]
    mid = ((ear["start"][0] + ear["base"][0]) / 2.0,
           (ear["start"][1] + ear["base"][1]) / 2.0)
    for side, sign in (("L", 1.0), ("R", -1.0)):
        base_point = Vector((sign * mid[0], 0.0, -mid[1]))
        tip_point = Vector((sign * ear["tip"][0], ear["sweep3d"], -ear["tip"][1]))
        # Bury the cone's base inside the skull, otherwise its rim leaves a
        # visible notch where it grazes the head surface.
        axis_dir = (tip_point - base_point).normalized()
        objs["ear_" + side] = cone(
            "ear_" + side,
            base_point - axis_dir * ear["inset3d"],
            tip_point,
            ear["base_radius3d"],
            ear["tip_radius3d"],
            mats["skin"],
            segments=24,
            squash=ear["squash3d"],
        )

    eyes = head["eyes"]
    for index, center in enumerate(eyes["centers"]):
        x, z = svg_to_xz(center)
        depth = eyes["depth3d"]
        y = head_surface_y(x, z, radii) - eyes["proud3d"] + depth
        objs["eye_%d" % index] = ellipsoid(
            "eye_%d" % index, (x, y, z), (eyes["r"], depth, eyes["r"]),
            mats["pale"], segments=32, rings=16)

    for index, pupil in enumerate(head["pupils"]):
        x, z = svg_to_xz(pupil["at"])
        pupil3d = head["pupil3d"]
        y = head_surface_y(x, z, radii) - pupil3d["proud3d"]
        objs["pupil_%d" % index] = ellipsoid(
            "pupil_%d" % index, (x, y, z),
            (pupil["r"], pupil3d["half_depth"], pupil["r"]),
            mats["node"], segments=24, rings=12)

    brow = head["brow"]
    brow3d = head["brow3d"]
    for side, sign in (("L", 1.0), ("R", -1.0)):
        points = []
        for step in range(7):
            t = step / 6.0
            sx = brow["outer"][0] + (brow["inner"][0] - brow["outer"][0]) * t
            sy = brow["outer"][1] + (brow["inner"][1] - brow["outer"][1]) * t
            x, z = svg_to_xz((sx, sy))
            points.append((sign * x,
                           head_surface_y(x, z, radii) - brow3d["proud3d"], z))
        objs["brow_" + side] = polyline("brow_" + side, points, brow3d["radius"],
                                        mats["skin"])

    grin = head["grin"]
    scale = grin["z_scale3d"]
    lower = quad_samples(grin["start"], grin["c1"], grin["c2"], grin["samples"])
    upper = quad_samples(grin["c2"], grin["c3"], grin["start"], grin["samples"])
    outline = [svg_to_xz(p) for p in (lower + upper[1:-1])]
    outline = [(x, z * scale) for x, z in outline]
    objs["grin"] = surface_patch("grin", outline, radii, grin["proud3d"],
                                 grin["thickness3d"], mats["dark"])

    fang3d = head["fang3d"]
    for index, fang in enumerate(head["fangs"]):
        pts = [svg_to_xz(p) for p in fang]
        pts = [(x, z * scale) for x, z in pts]
        objs["fang_%d" % index] = surface_patch(
            "fang_%d" % index, pts, radii, fang3d["proud3d"],
            fang3d["thickness3d"], mats["pale"])
    return objs


def build_body(params, mats):
    torso = params["body"]["torso"]
    center2d = torso["center"]
    rx, rz = torso["radii2d"]
    torso_obj = ellipsoid(
        "torso", (center2d[0], 0.0, -center2d[1]),
        (rx, torso["depth3d"], rz), mats["skin"])
    return {"torso": torso_obj}


def build_arm(name, arm, params, mats):
    radius = params["body"]["arm_radius3d"]
    claws = params["body"]["claws3d"]
    objs = {}
    for side, sign in (("L", 1.0), ("R", -1.0)):
        points = [(sign * arm[key][0], arm[key][1], arm[key][2])
                  for key in ("shoulder", "elbow", "hand")]
        objs["arm_%s_%s" % (name, side)] = polyline(
            "arm_%s_%s" % (name, side), points, radius, mats["skin"], smooth=True)
        hand = points[-1]
        for index in range(3):
            offset = (index - 1) * claws["spread"] * 0.5
            start = (hand[0] + offset, hand[1] - 1.0, hand[2] - claws["drop"] * 0.4)
            end = (start[0] + offset * 0.12, start[1] - claws["drop"] * 0.55,
                   start[2] - claws["length"])
            objs["claw_%s_%s_%d" % (name, side, index)] = cone(
                "claw_%s_%s_%d" % (name, side, index),
                start, end, claws["radius"], 0.35, mats["pale"], segments=10)
    return objs


def build_keyboard(params, mats):
    deck = params["keyboard"]["deck"]
    rim = params["keyboard"]["rim3d"]
    keys = params["keyboard"]["keys"]
    objs = {}
    def outline(pad):
        return [
            (-deck["back_half_width"] - pad, deck["y_back"] - pad),
            (deck["back_half_width"] + pad, deck["y_back"] - pad),
            (deck["front_half_width"] + pad, deck["y_front"] + pad),
            (-deck["front_half_width"] - pad, deck["y_front"] + pad),
        ]

    objs["kb_rim"] = prism("kb_rim", outline(rim["pad"]),
                           deck["z_top"] - deck["thickness"] - rim["thickness"],
                           deck["z_top"] - deck["thickness"],
                           mats["guide"])
    objs["kb_deck"] = prism("kb_deck", outline(0.0),
                            deck["z_top"] - deck["thickness"], deck["z_top"],
                            mats["dark"])

    rows = keys["rows"] + keys["spacebar"]["rows_after"]
    for row in range(keys["rows"]):
        t = (row + 0.5) / rows
        half = deck["back_half_width"] + (deck["front_half_width"] -
                                         deck["back_half_width"]) * t
        y = deck["y_back"] + (deck["y_front"] - deck["y_back"]) * t
        for col in range(keys["cols"]):
            u = (col + 0.5) / keys["cols"]
            x = -half + 2 * half * u
            w = keys["width"] * (0.82 if col == 0 else 1.0)
            objs["kb_key_%d_%d" % (row, col)] = prism(
                "kb_key_%d_%d" % (row, col),
                [(x - w / 2, y - keys["depth"] / 2),
                 (x + w / 2, y - keys["depth"] / 2),
                 (x + w / 2, y + keys["depth"] / 2),
                 (x - w / 2, y + keys["depth"] / 2)],
                deck["z_top"], deck["z_top"] + keys["height"], mats["key"])

    if keys["spacebar"]["rows_after"]:
        t = (keys["rows"] + 0.5) / rows
        half = deck["back_half_width"] + (deck["front_half_width"] -
                                         deck["back_half_width"]) * t
        y = deck["y_back"] + (deck["y_front"] - deck["y_back"]) * t
        inset = keys["spacebar"]["inset"]
        objs["kb_space"] = prism(
            "kb_space",
            [(-half + inset, y - keys["depth"] / 2),
             (half - inset, y - keys["depth"] / 2),
             (half - inset, y + keys["depth"] / 2),
             (-half + inset, y + keys["depth"] / 2)],
            deck["z_top"], deck["z_top"] + keys["height"], mats["key"])
    return objs


def tilt_keyboard(objs, params):
    """Lean the deck toward the camera so the key bed reads at elevation 0.

    A flat slab is edge-on from a level front camera; a real keyboard in front
    of a seated gremlin tilts its far edge down, which is what this reproduces.
    The hinge is the back edge, so the deck never climbs into the body.
    """
    deck = params["keyboard"]["deck"]
    angle = math.radians(deck["tilt_deg"])
    pivot = Vector((0.0, deck["y_back"], deck["z_top"]))
    matrix = (Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, "X")
              @ Matrix.Translation(-pivot))
    for obj in objs.values():
        obj.data.transform(matrix)
        obj.data.update()


def build_produced(params, mats):
    produced = params["produced3d"]
    y = produced["y"]
    radius = produced["radius"]
    objs = {}
    for index, bracket in enumerate(produced["brackets"]):
        for side, sign in (("L", 1.0), ("R", -1.0)):
            points = [(sign * x, y, z) for x, z in bracket]
            objs["code_bracket_%d_%s" % (index, side)] = polyline(
                "code_bracket_%d_%s" % (index, side), points, radius, mats["node"])
    for index, spark in enumerate(produced["sparks"]):
        points = [(x, y, z) for x, z in spark]
        objs["code_spark_%d" % index] = polyline(
            "code_spark_%d" % index, points, radius * 0.9, mats["node"])
    return objs


def build_rig(params, mats):
    scene = bpy.context.scene
    render = params["render"]
    data = bpy.data.cameras.new("rig_camera")
    data.type = "ORTHO"
    data.ortho_scale = render["ortho_scale"]
    camera = bpy.data.objects.new("rig_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    for spec in render["lights"]:
        light_data = bpy.data.lights.new("rig_" + spec["name"], type="AREA")
        light_data.energy = spec["energy"]
        light_data.size = spec["size"]
        light = bpy.data.objects.new("rig_" + spec["name"], light_data)
        light.location = Vector(spec["location"])
        direction = Vector(render["framing_center"]) - light.location
        light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(light)

    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = hex_to_linear_rgba(
            params["palette"]["base"]["hex"])
        background.inputs["Strength"].default_value = 1.0
    return camera


def place_camera(camera, cache, azimuth_deg, elevation_deg, params):
    render = params["render"]
    target = Vector(render["framing_center"])
    azimuth = math.radians(azimuth_deg)
    elevation = math.radians(elevation_deg)
    distance = cache
    direction = Vector((
        math.sin(azimuth) * math.cos(elevation),
        -math.cos(azimuth) * math.cos(elevation),
        math.sin(elevation),
    ))
    camera.location = target + direction * distance
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()


def configure_render(params, engine):
    scene = bpy.context.scene
    render = params["render"]
    scene.render.resolution_x, scene.render.resolution_y = render["resolution"]
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.threads_mode = "FIXED"
    scene.render.threads = render["threads"]
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 15
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    # Dither would scatter +-1 LSB noise over every flat fill: it breaks the
    # byte-exact palette contract and makes the PNG hash unstable for no gain.
    scene.render.dither_intensity = 0.0

    if engine == "workbench":
        scene.render.engine = "BLENDER_WORKBENCH"
        shading = scene.display.shading
        shading.light = "FLAT"
        shading.color_type = "MATERIAL"
        shading.show_cavity = False
        shading.show_shadows = False
        shading.show_specular_highlight = False
        shading.show_object_outline = False
        shading.show_xray = False
        shading.background_type = "VIEWPORT"
        shading.background_color = hex_to_linear_rgba(
            params["palette"]["base"]["hex"])[:3]
        scene.display.render_aa = render["aa"]
    elif engine == "eevee":
        scene.render.engine = "BLENDER_EEVEE"
        scene.eevee.taa_render_samples = render["eevee_samples"]
        scene.eevee.taa_samples = render["eevee_samples"]
    else:
        raise SystemExit("gremlin.py: unknown engine %r" % engine)


def main():
    opts = parse_args(list(sys.argv))
    with open(PARAMS, "r", encoding="utf-8") as handle:
        params = json.load(handle)

    out_dir = os.path.abspath(opts["out"])
    os.makedirs(out_dir, exist_ok=True)

    scene = reset_scene()
    mats = build_materials(params)

    groups = {}
    groups.update(build_head(params, mats))
    groups.update(build_body(params, mats))
    for pose in ("rest", "reach"):
        groups.update(build_arm(pose, params["body"]["arms3d"][pose], params, mats))
    groups.update(build_keyboard(params, mats))
    tilt_keyboard({k: v for k, v in groups.items() if k.startswith("kb_")}, params)
    groups.update(build_produced(params, mats))

    camera = build_rig(params, mats)
    configure_render(params, opts["engine"])

    wanted = opts["views"]
    for view in params["render"]["views"]:
        if wanted and view["name"] not in wanted:
            continue
        pose = view["pose"]
        for name, obj in groups.items():
            visible = True
            if name.startswith("arm_") or name.startswith("claw_"):
                visible = ("_%s_" % pose) in name
            if name.startswith("code_"):
                visible = view["produced"]
            obj.hide_render = not visible

        place_camera(camera, 800.0, view["azimuth"], view["elevation"], params)
        scene.render.filepath = os.path.join(out_dir, "gremlin-%s.png" % view["name"])
        bpy.ops.render.render(write_still=True)
        normalise_png(scene.render.filepath)
        print("gremlin.py: wrote %s" % scene.render.filepath)

    count = len(wanted) if wanted else len(params["render"]["views"])
    print("gremlin.py: done (%s, %d views)" % (opts["engine"], count))


if __name__ == "__main__":
    main()
