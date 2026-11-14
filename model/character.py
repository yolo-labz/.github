"""character.py -- the gremlin as a rigged, web-ready character.

    blender -b --factory-startup -t 4 -P model/character.py -- --out build/web [--mode all]

Modes: ``glb`` (the rigged model with one animation clip per state), ``stills``
(one lit render per state), ``turntable`` (frames of a camera orbit), ``all``.

Numbers come from two files and nothing else:
* ``model/params.json``     palette and the head construction (the 2D mark wins);
* ``model/character.json``  body, rig, the five states, light rig, delivery limits.

The head, face and keyboard builders are the ones ``gremlin.py`` already has; this
file adds the body, the rig, the poses and the export.  Rendering is Cycles on the
CPU with a fixed seed so two runs agree.
"""

import argparse
import json
import math
import os
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gremlin as g
import markshape as ms
from pngmeta import normalise_png

STATES = ("idle", "working", "paused", "loading", "asleep")
PROPS = ("kbd", "line", "dashes", "moon", "code", "signal", "ticks")
HIDDEN = 0.001


def load(name):
    with open(os.path.join(HERE, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="build/web")
    parser.add_argument("--mode", default="all", choices=("glb", "stills", "turntable", "all"))
    parser.add_argument("--states", type=lambda v: v.split(","))
    parser.add_argument("--light", action="store_true")
    parser.add_argument("--azimuth", type=float)
    parser.add_argument("--elevation", type=float)
    parser.add_argument("--samples", type=int)
    parser.add_argument("--size", type=int)
    parser.add_argument("--frames", type=lambda v: range(*map(int, v.split(":"))))
    return vars(parser.parse_args(argv))


# --------------------------------------------------------------------------- #
# geometry
# --------------------------------------------------------------------------- #
def cubic(p0, c1, c2, p1, n):
    out = []
    for i in range(n):
        t = i / float(n - 1)
        u = 1.0 - t
        out.append(tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                         for a, b, c, d in zip(p0, c1, c2, p1)))
    return out


def smooth(obj, angle=48.0):
    """Smooth shading with creases kept where the dihedral angle is large."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    limit = math.radians(angle)
    for face in bm.faces:
        face.smooth = True
    for edge in bm.edges:
        if len(edge.link_faces) == 2 and edge.calc_face_angle(0.0) > limit:
            edge.smooth = False
    bm.to_mesh(obj.data)
    bm.free()


def bake(obj):
    """Replace a curve object by an evaluated mesh object (same name, same place)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    mat = obj.data.materials[0] if obj.data.materials else None
    name = obj.name
    bpy.data.objects.remove(obj)
    out = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(out)
    if mat is not None and not mesh.materials:
        mesh.materials.append(mat)
    return out


def add_face(bm, verts):
    """Add a face unless it collapsed to fewer than three corners or already exists."""
    verts = tuple(verts)
    if len(set(verts)) == len(verts) and len(verts) > 2 and bm.faces.get(verts) is None:
        bm.faces.new(verts)


def loft(name, upper, lower, half_thickness, mat, ring_verts=12, bend=None):
    """A leaf-shaped solid: rings between two edge curves, rounded across Y.

    ``upper`` and ``lower`` are equally long lists of 3D points running base to
    tip; the silhouette seen along Y is exactly the polygon they bound.  The
    cross section is an ellipse, ``half_thickness[i]`` deep at ring ``i``.
    """
    rings = len(upper)
    bm = bmesh.new()
    grid = []
    for i in range(rings):
        u, d = Vector(upper[i]), Vector(lower[i])
        mid, half = (u + d) / 2.0, (u - d) / 2.0
        ring = []
        for k in range(ring_verts):
            th = 2 * math.pi * k / ring_verts
            co = mid + half * math.cos(th) + Vector((0.0, 1.0, 0.0)) * (half_thickness[i] * math.sin(th))
            if bend:
                co.y += bend(i / float(rings - 1))
            ring.append(bm.verts.new(co))
        grid.append(ring)
    for i in range(rings - 1):
        for k in range(ring_verts):
            k2 = (k + 1) % ring_verts
            quad = (grid[i][k], grid[i][k2], grid[i + 1][k2], grid[i + 1][k])
            add_face(bm, quad)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    for cap in (grid[0], grid[-1]):
        add_face(bm, [v for v in cap if v.is_valid])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = g.finish(name, bm, mat)
    smooth(obj, 60.0)
    return obj


def ear(cfg, frame, path, mat, name):
    """An ear lofted between the two edges of the mark's ear path, tip to base."""
    segs = ms.segments(path)
    n = cfg["anatomy"]["ear"]["rings"]
    top = ms.bezier(segs[0][1], n)[::-1]
    bottom = ms.bezier(segs[2][1], n)
    to3 = lambda p: (frame.xz(p)[0], 0.0, frame.xz(p)[1])
    thick = cfg["anatomy"]["ear"]["thickness"]
    prof = [thick / 2.0 * (1.0 - i / float(n - 1)) ** 0.55 for i in range(n)]
    sweep = cfg["anatomy"]["ear"]["sweep"]
    return loft(name, [to3(p) for p in top], [to3(p) for p in bottom], prof, mat,
                ring_verts=cfg["anatomy"]["ear"]["ring_verts"], bend=lambda t: sweep * t * t)


def limb(name, a, b, ra, rb, mat, segments=20):
    return g.cone(name, a, b, ra, rb, mat, segments=segments, squash=1.0)


def ball(name, c, r, mat, squash=(1.0, 1.0, 1.0), segments=24, rings=14):
    obj = g.ellipsoid(name, c, (r * squash[0], r * squash[1], r * squash[2]), mat,
                      segments=segments, rings=rings)
    smooth(obj, 80.0)
    return obj


def tag_smooth(obj, angle=48.0):
    smooth(obj, angle)
    return obj


# --------------------------------------------------------------------------- #
# materials
# --------------------------------------------------------------------------- #
def build_materials(params, cfg, light):
    palette = params["palette_light" if light else "palette"]
    mats = {}
    for role, spec in cfg["materials"].items():
        mat = g.make_material("m_" + role, palette[role]["hex"])
        node = mat.node_tree.nodes["Principled BSDF"]
        node.inputs["Roughness"].default_value = spec["roughness"]
        node.inputs["Specular IOR Level"].default_value = spec["specular"]
        mats[role] = mat
    return mats


# --------------------------------------------------------------------------- #
# the parts, each tagged with the bone that carries it
# --------------------------------------------------------------------------- #
def head_mesh(name, radius_at, depth, mat):
    """A head whose front view is the mark's head path and whose depth is a half ellipsoid."""
    obj = g.ellipsoid(name, (0, 0, 0), (1.0, 1.0, 1.0), mat, segments=64, rings=32)
    for v in obj.data.vertices:
        r = radius_at(math.atan2(v.co.z, v.co.x))
        v.co.x, v.co.y, v.co.z = v.co.x * r, v.co.y * depth, v.co.z * r
    return tag_smooth(obj, 90.0)


def surface_shell(name, outline, front_y, offset, thickness, mat, cuts=5):
    """A thin shell that follows the head surface under ``outline`` (x, z points).

    The outline face is subdivided and every vertex put back on the surface, so the
    shell does not cut a chord through the curved head.
    """
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, 0.0, z)) for x, z in outline])
    bmesh.ops.triangulate(bm, faces=[face])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts:
        v.co.y = front_y(v.co.x, v.co.z) - offset
    back = {v: bm.verts.new((v.co.x, v.co.y + thickness, v.co.z)) for v in bm.verts[:]}
    for f in bm.faces[:]:
        bm.faces.new([back[v] for v in reversed(f.verts)])
    for e in bm.edges[:]:
        if e.verts[0] in back and e.verts[1] in back and len(e.link_faces) == 1:
            a, b = e.verts
            bm.faces.new((a, b, back[b], back[a]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return g.finish(name, bm, mat)


def face_parts(add, cfg, mats, mark):
    """Head, ears, brows, eye sockets, pupils and closed-eye lines, all from the mark's paths."""
    F = cfg["anatomy"]["face"]
    frame = ms.Frame(F["unit"])
    depth = F["depth"]
    radius_at = ms.head_profile(frame, mark.HEAD, [mark.EAR_L, mark.EAR_R], widen=F["widen"])
    add(head_mesh("head", radius_at, depth, mats["skin"]), "head")

    def front_y(x, z):
        rho = min(math.hypot(x, z) / radius_at(math.atan2(z, x)), 1.0)
        return -depth * math.sqrt(1.0 - rho * rho)

    # the mark's right ear is on the +x side of the screen
    add(ear(cfg, frame, mark.EAR_R, mats["skin"], "ear_L"), "ear_L")
    add(ear(cfg, frame, mark.EAR_L, mats["skin"], "ear_R"), "ear_R")

    sockets = {"L": mark.EYE_R, "R": mark.EYE_L}
    for side, path in sockets.items():
        outline = [frame.xz(p) for p in ms.polyline(path, 8)]
        add(tag_smooth(surface_shell("socket_" + side, outline, front_y, F["socket"]["proud"],
                                     F["socket"]["thickness"], mats["feature"]), 40.0), "eyes")
        # brow: a skin ridge along the slanted top edge of the socket
        corner, inner = [frame.xz(p) for p in ms.polyline(path, 2)][:2]
        edge = Vector((inner[0] - corner[0], inner[1] - corner[1]))
        up = Vector((-edge.y, edge.x)).normalized()
        if up.y < 0:
            up = -up
        lift = up * F["brow"]["lift"]
        a = Vector(corner) + lift
        b = Vector(inner) + lift
        r = F["brow"]["radius"]
        steps = 7
        pts = []
        for k in range(steps):
            q = a.lerp(b, k / (steps - 1.0))
            pts.append((q.x, front_y(q.x, q.y) - F["brow"]["proud"], q.y))
        for k in range(steps):
            rk = r * (1.0 - 0.15 * k / (steps - 1.0))
            add(ball("brow_%s_%d" % (side, k), pts[k], rk, mats["skin"], segments=16, rings=8), "head")
            if k:
                add(tag_smooth(limb("brow_%s_seg%d" % (side, k), pts[k - 1], pts[k], rk, rk, mats["skin"], 16), 70.0), "head")
    for i, (cx, cy, rr) in enumerate(mark.DIRS[mark.SHIP]["pupil"]):
        x, z = frame.xz((cx, cy))
        p = F["pupil"]
        add(ball("pupil_%d" % i, (x, front_y(x, z) - p["proud"], z), rr * frame.unit,
                 mats["node"], (1, p["half_depth"] / (rr * frame.unit), 1), 28, 14), "pupils")
        # closed lid line: a downward bow under the pupil
        pts = []
        for k in range(11):
            t = -1.0 + 2.0 * k / 10.0
            lx, lz = x + t * F["lid"]["half_width"], z - F["lid"]["bow"] * (1.0 - t * t) + F["lid"]["lift"]
            pts.append((lx, front_y(lx, lz) - 2.0, lz))
        curve = g.polyline("lid_%d" % i, pts, F["lid"]["radius"], mats["feature"], smooth=True)
        add(bake(curve), "lids")


def metaball_body(prims, res, blend):
    """Union of ball chains and ellipsoids as one blended surface, weighted to the bones.

    ``prims`` is a list of (bone, kind, data). Balls are (centre, radius); ellipsoids are
    (centre, radii). Each vertex takes weights from how far it is from every primitive.
    """
    k = math.sqrt(1.0 - (0.6 / 2.0) ** (1.0 / 3.0))
    mb = bpy.data.metaballs.new("body_mb")
    mb.resolution, mb.render_resolution, mb.threshold = res, res, 0.6
    holder = bpy.data.objects.new("body_mb", mb)
    bpy.context.scene.collection.objects.link(holder)
    for bone, kind, data in prims:
        el = mb.elements.new(type="BALL" if kind == "ball" else "ELLIPSOID")
        el.stiffness = 2.0
        el.co = data[0]
        if kind == "ball":
            el.radius = data[1] * 0.82 / k
        else:
            el.radius = 10.0
            el.size_x, el.size_y, el.size_z = (r / (10.0 * k) for r in data[1])
    bpy.context.view_layer.update()
    mesh = bpy.data.meshes.new_from_object(holder.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(holder)
    bpy.data.metaballs.remove(mb)
    return mesh


def vertex_weights(mesh, prims, blend):
    """{bone: {vertex index: weight}}, nearest primitive first, falling off over ``blend`` units."""
    gap = []
    for bone, kind, data in prims:
        c = Vector(data[0])
        if kind == "ball":
            gap.append((bone, c, data[1], None))
        else:
            gap.append((bone, c, min(data[1]), Vector(data[1])))
    groups = {}
    for v in mesh.vertices:
        best = {}
        for bone, c, r, radii in gap:
            d = v.co - c
            dist = d.length - r if radii is None else (Vector((d.x / radii.x, d.y / radii.y, d.z / radii.z)).length - 1.0) * r
            if dist < best.get(bone, 1e9):
                best[bone] = dist
        low = min(best.values())
        w = {b: math.exp(-(dd - low) / blend) for b, dd in best.items()}
        top = sorted(w.items(), key=lambda kv: -kv[1])[:4]
        total = sum(x for _, x in top)
        for b, x in top:
            if x / total > 0.03:
                groups.setdefault(b, {})[v.index] = x / total
    return groups


def chain_balls(bone, a, b, ra, rb, gap=0.5):
    a, b = Vector(a), Vector(b)
    n = max(2, int(math.ceil((b - a).length / (gap * (ra + rb) / 2.0))) + 1)
    return [(bone, "ball", (tuple(a.lerp(b, i / (n - 1.0))), ra + (rb - ra) * i / (n - 1.0))) for i in range(n)]


def body_parts(add, cfg, mats):
    """Torso, legs, arms, hands and tail as one blended skin, plus fingers and the tail spade."""
    A, bones = cfg["anatomy"], cfg["bones"]
    B = A["body"]
    t = A["torso"]
    prims = [("torso", "ellipsoid", (tuple(t["center"]), tuple(t["radii"])))]
    prims += chain_balls("torso", (0, 3, -43), (0, 3, -36), B["neck"][0], B["neck"][1])
    prims += chain_balls("head", (0, 3, -36), (0, 2, -28), B["neck"][1], B["neck"][1])
    for side in ("L", "R"):
        leg = bones["leg_" + side]
        prims += chain_balls("leg_" + side, leg["head"], leg["tail"], A["thigh"]["r0"], A["thigh"]["r1"])
        f = A["foot"]
        foot = Vector(leg["tail"]) + Vector((0.0, -f["forward"], -f["down"]))
        prims.append(("leg_" + side, "ellipsoid", (tuple(foot), tuple(f["radii"]))))
        arm = A["arm"]
        s, e = bones["upper_arm_" + side]["head"], bones["forearm_" + side]["head"]
        w = bones["hand_" + side]["head"]
        prims += chain_balls("upper_arm_" + side, s, e, arm["r_shoulder"], arm["r_elbow"])
        prims += chain_balls("forearm_" + side, e, w, arm["r_elbow"], arm["r_wrist"])
        axis = (Vector(bones["hand_" + side]["tail"]) - Vector(w)).normalized()
        palm = A["hand"]["palm"]
        prims += chain_balls("hand_" + side, w, Vector(w) + axis * palm["length"], palm["r0"], palm["r1"])
    r = A["tail"]["r"]
    for i, name in enumerate(("tail_1", "tail_2", "tail_3")):
        prims += chain_balls(name, bones[name]["head"], bones[name]["tail"], r[i], r[i + 1])
    prims.append(("tail_3", "ball", (tuple(bones["tail_3"]["tail"]), r[3])))
    mesh = metaball_body(prims, B["resolution"], B["blend"])
    groups = vertex_weights(mesh, prims, B["blend"])
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new("body", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mats["skin"])
    for bone, weights in sorted(groups.items()):
        vg = obj.vertex_groups.new(name=bone)
        for index, w in sorted(weights.items()):
            vg.add([index], w, "REPLACE")
    add(obj, None)

    for side in ("L", "R"):
        hand_parts(add, cfg, mats, side)

    tip = Vector(bones["tail_3"]["tail"])
    sp = A["spade"]
    base_pts = [Vector((p[0], 0.0, p[1])) for p in sp["points"]]
    spade = loft("spade", [base_pts[0], base_pts[1], base_pts[2]], [base_pts[0], base_pts[3], base_pts[2]],
                 [sp["thickness"] / 2.0, sp["thickness"] / 2.0, 0.2], mats["skin"], 10)
    spade.data.transform(Matrix.Translation(tip) @ Matrix.Rotation(math.radians(-14.0), 4, "Y"))
    add(spade, "tail_3")


def hand_parts(add, cfg, mats, side):
    """Three fingers and a thumb with two joints each, bent down towards the keys, and a small claw."""
    A, bones = cfg["anatomy"], cfg["bones"]
    H = A["hand"]
    w = Vector(bones["hand_" + side]["head"])
    axis = (Vector(bones["hand_" + side]["tail"]) - w).normalized()
    down = Vector((0, 0, -1)) - axis * Vector((0, 0, -1)).dot(axis)
    down.normalize()
    lateral = axis.cross(Vector((0, 0, 1))).normalized()
    inner = -lateral if w.x * lateral.x > 0 else lateral
    base = w + axis * H["palm"]["length"]
    bone = "hand_" + side

    def digit(name, start, direction, lengths, radii, bends):
        pos, prev = Vector(start), None
        add(ball(name + "_k0", tuple(pos), radii[0], mats["skin"], segments=16, rings=8), bone)
        total = 0.0
        for i, (length, bend) in enumerate(zip(lengths, bends)):
            total += math.radians(bend)
            step = (direction * math.cos(total) + down * math.sin(total)).normalized() * length
            end = pos + step
            add(tag_smooth(limb("%s_%d" % (name, i), pos, end, radii[i], radii[i + 1], mats["skin"], 14), 70.0), bone)
            add(ball("%s_k%d" % (name, i + 1), tuple(end), radii[i + 1], mats["skin"], segments=16, rings=8), bone)
            prev, pos = step, end
        claw_end = pos + prev.normalized() * H["claw"]
        add(g.cone(name + "_claw", pos, claw_end, radii[-1] * 0.8, 0.25, mats["feature"], segments=10), bone)

    for k in range(3):
        off = (k - 1) * H["spread"]
        digit("finger_%s_%d" % (side, k), base + lateral * off, axis, H["finger"]["lengths"],
              H["finger"]["radii"], H["finger"]["bends"])
    thumb_dir = (axis * 0.7 + inner * 0.55).normalized()
    digit("thumb_" + side, w + axis * (H["palm"]["length"] * 0.35) + inner * H["palm"]["r0"] * 0.8, thumb_dir,
          H["thumb"]["lengths"], H["thumb"]["radii"], H["thumb"]["bends"])


def build_parts(params, cfg, mats):
    parts = []  # (object, bone)
    A = cfg["anatomy"]
    bones = cfg["bones"]

    def add(obj, bone):
        parts.append((obj, bone))
        return obj

    mark = ms.master()
    face_parts(add, cfg, mats, mark)
    body_parts(add, cfg, mats)

    # --- props --------------------------------------------------------------
    kb = g.build_keyboard(params, mats)
    g.tilt_keyboard(kb, params)
    for name, obj in kb.items():
        if obj.type == "CURVE":
            obj = bake(obj)
        else:
            bevel(obj, 0.9)
            tag_smooth(obj, 35.0)
        add(obj, "kbd")

    ln = A["line"]
    lo_ = (-ln["half_length"], ln["y"], ln["z"])
    hi_ = (ln["half_length"], ln["y"], ln["z"])
    line = limb("line", lo_, hi_, ln["radius"], ln["radius"], mats["guide"], 20)
    add(line, "line")
    d = A["dashes"]
    for i in range(d["count"]):
        x = (i - (d["count"] - 1) / 2.0) * d["pitch"]
        add(limb("dash_%d" % i, (x - d["length"] / 2, d["y"], d["z"]), (x + d["length"] / 2, d["y"], d["z"]),
                 d["radius"], d["radius"], mats["guide"], 14), "dashes")

    m = A["moon"]
    steps = 18
    cx, cz = bones["moon"]["head"][0], bones["moon"]["head"][2]
    outer = [(cx + m["outer"] * math.cos(math.radians(40 + 280 * i / (steps - 1))), 0.0,
              cz + m["outer"] * math.sin(math.radians(40 + 280 * i / (steps - 1)))) for i in range(steps)]
    inner = [(cx + m["offset"][0] + m["inner"] * math.cos(math.radians(40 + 280 * i / (steps - 1))), 0.0,
              cz + m["offset"][1] + m["inner"] * math.sin(math.radians(40 + 280 * i / (steps - 1))))
             for i in range(steps)]
    half = [m["thickness"] / 2.0 * math.sin(math.pi * i / (steps - 1)) ** 0.5 + 0.15 for i in range(steps)]
    # the two arcs share their end points: pin them so the crescent closes
    inner[0], inner[-1] = outer[0], outer[-1]
    add(loft("moon", outer, inner, half, mats["ink"], 12), "moon")

    produced = g.build_produced(params, mats)
    for name, obj in produced.items():
        add(bake(obj), "code")

    sg = A["signal"]
    cx, cz = bones["signal"]["head"][0], bones["signal"]["head"][2]
    for i, rad in enumerate(sg["radii"]):
        pts = []
        for k in range(14):
            ang = math.radians(-sg["arc_deg"] / 2 + sg["arc_deg"] * k / 13.0)
            pts.append((cx - rad * math.cos(ang) * 0.35 - 6.0 * i, -8.0, cz + rad * math.sin(ang)))
        mat = mats["guide"] if i == 0 else mats["ink"]
        add(bake(g.polyline("signal_%d" % i, pts, sg["radius"], mat, smooth=True)), "signal")

    tk = A["ticks"]
    for i, (ln_, dz) in enumerate(zip(tk["length"], tk["dz"])):
        x0, z0 = bones["ticks"]["head"][0], bones["ticks"]["head"][2] + dz
        add(limb("tick_%d" % i, (x0 - ln_ / 2, -8.0, z0), (x0 + ln_ / 2, -8.0, z0), tk["radius"], tk["radius"],
                 mats["guide"], 14), "ticks")
    return parts


def bevel(obj, width):
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = 2
    mod.limit_method = "ANGLE"
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.remove(mod)
    old = obj.data
    obj.data = mesh
    if not mesh.materials:
        mesh.materials.append(old.materials[0])
    bpy.data.meshes.remove(old)


# --------------------------------------------------------------------------- #
# rig
# --------------------------------------------------------------------------- #
def build_armature(cfg):
    data = bpy.data.armatures.new("rig")
    obj = bpy.data.objects.new("rig", data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    root = data.edit_bones.new("root")
    root.head, root.tail = Vector((0, 0, -110)), Vector((0, 0, -104))
    made["root"] = root
    pending = dict(cfg["bones"])
    while pending:
        for name, spec in list(pending.items()):
            if spec["parent"] in made:
                eb = data.edit_bones.new(name)
                eb.head, eb.tail = Vector(spec["head"]), Vector(spec["tail"])
                if (eb.tail - eb.head).length < 0.01:
                    eb.tail = eb.head + Vector((0, 0, 1))
                eb.parent = made[spec["parent"]]
                made[name] = eb
                del pending[name]
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def skin(parts, arm, mats):
    """One vertex group per part (weight 1), then merge the parts by material."""
    by_mat = {}
    for obj, bone in parts:
        if bone is not None:
            vg = obj.vertex_groups.new(name=bone)
            vg.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
        by_mat.setdefault(obj.data.materials[0].name, []).append(obj)
    merged = []
    for matname, objs in sorted(by_mat.items()):
        lead = objs[0]
        with bpy.context.temp_override(active_object=lead, object=lead, selected_objects=objs,
                                       selected_editable_objects=objs):
            bpy.ops.object.join()
        lead.name = "gremlin_" + matname[2:]
        lead.data.name = lead.name
        lead.parent = arm
        mod = lead.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        merged.append(lead)
    return merged


def rest_matrix(arm, name):
    return arm.data.bones[name].matrix_local.copy()


def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def set_world(pb, matrix):
    pb.matrix = matrix
    bpy.context.view_layer.update()


def rotate_about_head(arm, name, euler_deg):
    pb = arm.pose.bones[name]
    m0 = pb.matrix.copy()
    h = Vector(pb.head)
    rot = Matrix.Rotation(math.radians(euler_deg[2]), 4, "Z") @ Matrix.Rotation(math.radians(euler_deg[1]), 4, "Y") \
        @ Matrix.Rotation(math.radians(euler_deg[0]), 4, "X")
    set_world(pb, Matrix.Translation(h) @ rot @ Matrix.Translation(-h) @ m0)


def aim(arm, name, target):
    pb = arm.pose.bones[name]
    m0 = pb.matrix.copy()
    h = Vector(pb.head)
    d0 = (m0.to_3x3() @ Vector((0, 1, 0))).normalized()
    d1 = (Vector(target) - h).normalized()
    rot = d0.rotation_difference(d1).to_matrix().to_4x4()
    set_world(pb, Matrix.Translation(h) @ rot @ Matrix.Translation(-h) @ m0)


def solve_arm(arm, side, target, pole, cfg):
    up, fore, hand = "upper_arm_" + side, "forearm_" + side, "hand_" + side
    s = Vector(arm.pose.bones[up].head)
    l1 = (Vector(cfg["bones"][fore]["head"]) - Vector(cfg["bones"][up]["head"])).length
    l2 = (Vector(cfg["bones"][hand]["head"]) - Vector(cfg["bones"][fore]["head"])).length
    d = Vector(target) - s
    dist = min(d.length, l1 + l2 - 0.05)
    dn = d.normalized()
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2.0 * dist)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    pv = Vector(pole)
    perp = (pv - dn * pv.dot(dn)).normalized()
    elbow = s + dn * a + perp * h
    wrist = s + dn * dist
    aim(arm, up, elbow)
    aim(arm, fore, wrist)
    aim(arm, hand, wrist + (wrist - elbow).normalized() * 10.0 + Vector((0, 0, -3.0)))


def apply_pose(arm, spec, cfg):
    reset_pose(arm)
    t = spec["torso"]
    rotate_about_head(arm, "torso", t["rot"])
    rotate_about_head(arm, "head", spec["head"]["rot"])
    for side in ("L", "R"):
        # ears tilt in the XZ plane: about the Y axis
        rotate_about_head(arm, "ear_" + side, (0.0, spec["ears"][side], 0.0))
        solve_arm(arm, side, spec["hands"][side], spec["pole"][side], cfg)
        aim(arm, "leg_" + side, spec["feet"][side])
    aim(arm, "tail_1", spec["tail"][0])
    aim(arm, "tail_2", spec["tail"][1])
    aim(arm, "tail_3", spec["tail"][2])
    shown = set(spec["show"])
    closed = "closed" in shown
    for name in PROPS:
        scale_bone(arm, name, name in shown)
    scale_bone(arm, "eyes", not closed)
    scale_bone(arm, "lids", closed)
    pupils = arm.pose.bones["pupils"]
    pupils.location = (spec["pupils"][0], 0.0, spec["pupils"][1])
    bpy.context.view_layer.update()


def scale_bone(arm, name, visible):
    pb = arm.pose.bones[name]
    k = 1.0 if visible else HIDDEN
    pb.scale = (k, k, k)


def merge_pose(spec, delta):
    out = json.loads(json.dumps(spec))
    for key, val in delta.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key].update(val)
        else:
            out[key] = val
    return out


def key_all(arm, frame):
    for pb in arm.pose.bones:
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("scale", frame=frame)


def build_actions(arm, cfg):
    frames = cfg["animation"]["frames"]
    ad = arm.animation_data_create()
    actions = {}
    for state in STATES:
        spec = cfg["states"][state]
        alt = merge_pose(spec, spec.get("b", {}))
        act = bpy.data.actions.new(state)
        act.use_fake_user = True
        ad.action = act
        for frame, pose in ((1, spec), (frames // 2 + 1, alt), (frames + 1, spec)):
            apply_pose(arm, pose, cfg)
            key_all(arm, frame)
        actions[state] = act
    return actions


def push_nla(arm, actions):
    ad = arm.animation_data
    ad.action = None
    for state in STATES:
        track = ad.nla_tracks.new()
        track.name = state
        strip = track.strips.new(state, 1, actions[state])
        strip.name = state


def use_state(arm, actions, state, frame=1):
    ad = arm.animation_data
    ad.action = actions[state]
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()


# --------------------------------------------------------------------------- #
# scene, light, render
# --------------------------------------------------------------------------- #
def build_scene(params, cfg, light):
    g.reset_scene()
    scene = bpy.context.scene
    scene.render.fps = cfg["animation"]["fps"]
    mats = build_materials(params, cfg, light)
    parts = build_parts(params, cfg, mats)
    arm = build_armature(cfg)
    merged = skin(parts, arm, mats)
    return scene, arm, merged


def build_rig_lights(scene, params, cfg, light):
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = cfg["camera"]["ortho_scale"]
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    centre = Vector(cfg["camera"]["center"])
    for name, spec in cfg["rig"].items():
        data = bpy.data.lights.new("rig_" + name, type="AREA")
        data.energy = spec["energy"]
        data.size = spec["size"]
        data.color = g.hex_to_linear_rgba(spec["tint"])[:3]
        obj = bpy.data.objects.new("rig_" + name, data)
        obj.location = Vector(spec["location"])
        obj.rotation_euler = (centre - obj.location).to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(obj)
    scene.world = bpy.data.worlds.new("w")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    base = params["palette_light" if light else "palette"]["base"]["hex"]
    bg.inputs["Color"].default_value = g.hex_to_linear_rgba(base)
    bg.inputs["Strength"].default_value = cfg["world"]["strength"]
    return cam


def aim_camera(cam, cfg, azimuth, elevation):
    c = cfg["camera"]
    target = Vector(c["center"])
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = target + direction * c["distance"]
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()


def configure_cycles(scene, cfg, size, samples):
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = False
    cy.seed = 1
    cy.use_animated_seed = False
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 6
    cy.filter_width = 1.5
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 1
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.compression = 15
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.dither_intensity = 0.0


def render_to(scene, path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    normalise_png(path)
    print("character.py: wrote %s" % path)


# --------------------------------------------------------------------------- #
# export
# --------------------------------------------------------------------------- #
def export_glb(path, cfg, arm, merged):
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    arm.select_set(True)
    for obj in merged:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_skins=True,
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_nla_strips=True,
        export_force_sampling=True,
        export_frame_range=False,
        export_optimize_animation_size=True,
        export_cameras=False,
        export_lights=False,
        export_extras=False,
        export_yup=True,
        export_draco_mesh_compression_enable=False,
    )
    scrub_glb(path)
    print("character.py: wrote %s (%d bytes)" % (path, os.path.getsize(path)))


def scrub_glb(path):
    """Drop the writer string from asset metadata; the file says what it holds, not how it was made."""
    with open(path, "rb") as handle:
        blob = handle.read()
    magic, version, _ = struct.unpack("<4sII", blob[:12])
    jlen, jtype = struct.unpack("<II", blob[12:20])
    doc = json.loads(blob[20:20 + jlen].decode("utf-8"))
    doc.get("asset", {}).pop("generator", None)
    raw = json.dumps(doc, separators=(",", ":"), sort_keys=True).encode("utf-8")
    raw += b" " * (-len(raw) % 4)
    rest = blob[20 + jlen:]
    total = 12 + 8 + len(raw) + len(rest)
    with open(path, "wb") as handle:
        handle.write(struct.pack("<4sII", magic, version, total))
        handle.write(struct.pack("<II", len(raw), jtype) + raw + rest)


# --------------------------------------------------------------------------- #
def main():
    opts = parse_args(list(sys.argv))
    params, cfg = load("params.json"), load("character.json")
    out = os.path.abspath(opts["out"])
    os.makedirs(out, exist_ok=True)
    mode = opts["mode"]
    scene, arm, merged = build_scene(params, cfg, opts["light"])
    actions = build_actions(arm, cfg)
    stats = {"triangles": 0}
    for obj in merged:
        stats["triangles"] += sum(len(p.vertices) - 2 for p in obj.data.polygons)
    print("character.py: %d triangles, %d bones" % (stats["triangles"], len(arm.data.bones)))

    if mode in ("glb", "all"):
        push_nla(arm, actions)
        export_glb(os.path.join(out, "gremlin.glb"), cfg, arm, merged)
        for track in list(arm.animation_data.nla_tracks):
            arm.animation_data.nla_tracks.remove(track)

    if mode in ("stills", "turntable", "all"):
        cam = build_rig_lights(scene, params, cfg, opts["light"])
        if mode in ("stills", "all"):
            st = cfg["stills"]
            size = [opts["size"]] * 2 if opts["size"] else st["size"]
            configure_cycles(scene, cfg, size, opts["samples"] or st["samples"])
            aim_camera(cam, cfg, cfg["camera"]["azimuth"] if opts["azimuth"] is None else opts["azimuth"],
                       cfg["camera"]["elevation"] if opts["elevation"] is None else opts["elevation"])
            for state in opts["states"] or STATES:
                use_state(arm, actions, state)
                render_to(scene, os.path.join(out, "still-%s.png" % state))
        if mode in ("turntable", "all"):
            tt = cfg["turntable"]
            configure_cycles(scene, cfg, tt["size"], tt["samples"])
            use_state(arm, actions, tt["state"])
            for i in opts["frames"] or range(tt["frames"]):
                aim_camera(cam, cfg, 360.0 * i / tt["frames"], tt["elevation"])
                render_to(scene, os.path.join(out, "turn-%02d.png" % i))
    print("character.py: done (%s)" % mode)


if __name__ == "__main__":
    main()
