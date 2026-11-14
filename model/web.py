#!/usr/bin/env python3
"""Build and check the web-ready gremlin: one .glb, a still per state, a turntable.

    python3 model/web.py --build build/web          # render, encode, write manifest
    python3 model/web.py --build build/web --verify # check build/web against the manifest
    python3 model/web.py --verify                   # check the committed files, no blender

Published to ``profile/assets/brand/character/``:

    gremlin.glb                    rigged, one animation clip per state, under 1.5 MB
    gremlin-<state>.{webp,avif}    a still per state (640 px)
    gremlin-turntable.{webp,avif}  24 frames around the idle pose (400 px)
    manifest.json                  sha256, bytes, alt text

Everything is derived from ``params.json`` (palette, head) and ``character.json``
(body, rig, states, lights, limits). Encoders are pinned to one thread so two runs
write the same bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEST = REPO / "profile/assets/brand/character"
MANIFEST = DEST / "manifest.json"
STATES = ("idle", "working", "paused", "loading", "asleep")
ALT = {
    "idle": "The gremlin standing with its hands down and its tail curled up.",
    "working": "The gremlin leaning over a keyboard, typing, with code brackets floating beside it.",
    "paused": "The gremlin with one hand raised to its chin and two sound arcs beside its ear.",
    "loading": "The gremlin mid-stride, one ear swept back, with speed lines behind it and dashes below.",
    "asleep": "The gremlin with its eyes closed and its ears drooping, a crescent moon above its head.",
    "turntable": "The gremlin standing still while the camera circles it once.",
}
GLB_NAME = "gremlin.glb"
BANNED = ("blender", "cycles", "eevee", "gpt", "openai", "chatgpt", "midjourney",
          "diffusion", "generated", "ai-")


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, **kw):
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def encode_still(png: Path, stem: Path, cfg):
    q = cfg["stills"]["quality"]
    run(["magick", png, "-quality", q["webp"], "-define", "webp:method=4",
         "-define", "webp:thread-level=1", "-define", "webp:alpha-quality=100",
         "-strip", stem.with_suffix(".webp")])
    run(["magick", png, "-quality", q["avif"], "-define", "heic:speed=4",
         "-define", "heic:threads=1", "-strip", stem.with_suffix(".avif")])


def encode_turntable(frames_dir: Path, stem: Path, cfg):
    tt = cfg["turntable"]
    pngs = [frames_dir / ("turn-%02d.png" % i) for i in range(tt["frames"])]
    missing = [p.name for p in pngs if not p.is_file()]
    if missing:
        raise SystemExit("web.py: missing turntable frames: %s" % ", ".join(missing[:4]))
    run(["magick", "-delay", str(round(100 / tt["fps"])), "-loop", "0", *pngs,
         "-quality", tt["quality"]["webp"], "-define", "webp:method=4",
         "-define", "webp:thread-level=1", "-strip", stem.with_suffix(".webp")])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
         "-framerate", tt["fps"], "-i", frames_dir / "turn-%02d.png",
         "-c:v", "libaom-av1", "-cpu-used", "4", "-threads", "1", "-row-mt", "0",
         "-crf", tt["quality"]["avif"], "-b:v", "0", "-pix_fmt", "yuva420p",
         "-map_metadata", "-1", "-f", "avif", stem.with_suffix(".avif")])


def glb_doc(path: Path):
    blob = path.read_bytes()
    magic, version, length = struct.unpack("<4sII", blob[:12])
    if magic != b"glTF" or version != 2 or length != len(blob):
        raise SystemExit("web.py: %s is not a valid GLB 2.0" % path)
    jlen = struct.unpack("<I", blob[12:16])[0]
    return json.loads(blob[20:20 + jlen].decode("utf-8")), blob


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def check_glb(path: Path, params, cfg):
    """Return a list of problems with the .glb; empty means it passes."""
    doc, blob = glb_doc(path)
    bad = []
    if len(blob) > cfg["glb"]["max_bytes"]:
        bad.append("glb is %d bytes, limit %d" % (len(blob), cfg["glb"]["max_bytes"]))
    clips = [a.get("name") for a in doc.get("animations", [])]
    if sorted(clips) != sorted(STATES):
        bad.append("animation clips %s, want %s" % (clips, list(STATES)))
    used = doc.get("extensionsUsed", [])
    if "EXT_meshopt_compression" not in used and "KHR_draco_mesh_compression" not in used:
        bad.append("meshes are not compressed")
    if doc.get("images"):
        bad.append("unexpected textures: %d" % len(doc["images"]))
    if len(doc.get("skins", [])) != 1:
        bad.append("want one skin, found %d" % len(doc.get("skins", [])))
    if "generator" in doc.get("asset", {}) or b"Blender" in blob[:4096]:
        bad.append("asset metadata names its writer")
    want = {}
    for role, spec in cfg["materials"].items():
        hexv = params["palette"][spec["role"]]["hex"].lstrip("#")
        want[role] = [srgb_to_linear(int(hexv[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    got = {m["name"][2:]: m["pbrMetallicRoughness"]["baseColorFactor"][:3] for m in doc["materials"]}
    for role, rgb in want.items():
        if role not in got:
            continue
        if max(abs(a - b) for a, b in zip(rgb, got[role])) > 0.002:
            bad.append("material %s is off palette: %s vs %s" % (role, got[role], rgb))
    return bad


def canonical_triangles(path: Path):
    """Sort every triangle list in an uncompressed GLB, in place.

    The glTF writer emits the same triangles in a different order on every run.
    Sorting them makes the file, and everything compressed from it, repeatable.
    """
    doc, blob = glb_doc(path)
    jlen = struct.unpack("<I", blob[12:16])[0]
    head, binary = blob[:20 + jlen], bytearray(blob[20 + jlen:])
    start = 8  # chunk header
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            acc = doc["accessors"][prim["indices"]]
            view = doc["bufferViews"][acc["bufferView"]]
            fmt, size = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}[acc["componentType"]]
            at = start + view.get("byteOffset", 0) + acc.get("byteOffset", 0)
            flat = struct.unpack("<%d%s" % (acc["count"], fmt), bytes(binary[at:at + acc["count"] * size]))
            tris = [flat[i:i + 3] for i in range(0, len(flat), 3)]
            tris = sorted(min((a, b, c), (b, c, a), (c, a, b)) for a, b, c in tris)
            binary[at:at + acc["count"] * size] = struct.pack(
                "<%d%s" % (acc["count"], fmt), *[v for t in tris for v in t])
    path.write_bytes(head + bytes(binary))


def pack_glb(raw: Path, out: Path, gltfpack):
    """Canonical triangle order, then meshopt compression with the writer string dropped."""
    work = out.with_suffix(".raw.glb")
    work.write_bytes(raw.read_bytes())
    canonical_triangles(work)
    run([gltfpack, "-i", work, "-o", out, "-cc", "-km", "-kn", "-vp", "14", "-vn", "10", "-vt", "12"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    work.unlink()
    doc, blob = glb_doc(out)
    doc.get("asset", {}).pop("generator", None)
    jlen, jtype = struct.unpack("<II", blob[12:20])
    raw_json = json.dumps(doc, separators=(",", ":"), sort_keys=True).encode("utf-8")
    raw_json += b" " * (-len(raw_json) % 4)
    rest = blob[20 + jlen:]
    out.write_bytes(struct.pack("<4sII", b"glTF", 2, 20 + len(raw_json) + len(rest))
                    + struct.pack("<II", len(raw_json), jtype) + raw_json + rest)


def check_names(paths):
    bad = []
    for p in paths:
        if any(word in p.name.lower() for word in BANNED):
            bad.append("file name says how it was made: %s" % p.name)
        blob = p.read_bytes()
        for word in (b"Blender", b"blender", b"Cycles", b"OpenAI", b"ChatGPT"):
            if word in blob[:65536]:
                bad.append("%s carries %s in its header" % (p.name, word.decode()))
    return bad


def outputs(root: Path):
    names = [GLB_NAME]
    for stem in [f"gremlin-{s}" for s in STATES] + ["gremlin-turntable"]:
        names += [stem + ".webp", stem + ".avif"]
    return [root / n for n in names]


def write_manifest(root: Path, cfg):
    files = {}
    for p in outputs(root):
        key = p.stem.replace("gremlin-", "") if p.suffix != ".glb" else "model"
        files.setdefault(key, {})[p.suffix[1:]] = {"file": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
    for key, entry in files.items():
        if key in ALT:
            entry["alt"] = ALT[key]
    entry = files["model"]
    entry["glb"]["limit_bytes"] = cfg["glb"]["max_bytes"]
    entry["clips"] = list(STATES)
    (root / "manifest.json").write_text(json.dumps({"schema": 1, "files": files}, indent=1) + "\n",
                                        encoding="utf-8")


def verify(root: Path, params, cfg):
    bad = []
    manifest = root / "manifest.json"
    if not manifest.is_file():
        return ["%s is missing" % manifest]
    recorded = json.loads(manifest.read_text(encoding="utf-8"))["files"]
    for key, entry in recorded.items():
        for ext, rec in entry.items():
            if not isinstance(rec, dict) or "file" not in rec:
                continue
            p = root / rec["file"]
            if not p.is_file():
                bad.append("missing %s" % rec["file"])
            elif sha(p) != rec["sha256"] or p.stat().st_size != rec["bytes"]:
                bad.append("%s differs from the manifest" % rec["file"])
    for p in outputs(root):
        if not p.is_file():
            bad.append("missing %s" % p.name)
    if not bad:
        bad += check_glb(root / GLB_NAME, params, cfg)
        bad += check_names(outputs(root))
    return bad


def compare(build: Path, root: Path, limit=0.0005):
    """Fresh renders against the committed ones: at most ``limit`` of the pixels may differ.

    Cycles on the CPU is not bit-exact between runs (one pixel in a frame can land
    one level apart), so the images are compared by pixels; the .glb and the
    encoders are byte-exact and are checked by hash.
    """
    bad = []
    for p in outputs(root):
        if p.suffix == ".glb":
            if sha(p) != sha(build / p.name):
                bad.append("%s bytes differ" % p.name)
            continue
        fresh = build / p.name
        frames = (0, 6, 12, 18) if "turntable" in p.name else (0,)
        for n in frames:
            out = subprocess.run(["magick", "compare", "-metric", "AE", "-fuzz", "2%",
                                  "%s[%d]" % (p, n), "%s[%d]" % (fresh, n), "null:"],
                                 capture_output=True, text=True)
            diff = float(out.stderr.split()[0])
            w, h = (int(v) for v in subprocess.run(
                ["magick", "identify", "-format", "%w %h", "%s[%d]" % (p, n)],
                capture_output=True, text=True).stdout.split())
            if diff / (w * h) > limit:
                bad.append("%s frame %d: %.4f%% of pixels differ" % (p.name, n, 100 * diff / (w * h)))
    return bad


def blender(args, build: Path, mode, extra=()):
    run([args.blender, "-b", "--factory-startup", "-t", args.threads, "-P", HERE / "character.py",
         "--", "--out", build, "--mode", mode, *extra])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", type=Path, default=None)
    ap.add_argument("--blender", default="blender")
    ap.add_argument("--threads", default="4")
    ap.add_argument("--gltfpack", default="gltfpack", help="meshopt packer (nixpkgs#meshoptimizer)")
    ap.add_argument("--only", choices=("glb", "stills", "turntable", "encode"), help="one stage; used to split long runs")
    ap.add_argument("--frames", help="turntable frame range a:b")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--compare", type=Path, help="compare this build dir with the committed files")
    args = ap.parse_args()
    params, cfg = load("params.json"), load("character.json")

    if args.compare:
        bad = compare(args.compare, DEST)
        for line in bad:
            print("FAIL", line)
        print("web.py: %s" % ("FAIL" if bad else "fresh build matches the committed files"))
        return 1 if bad else 0

    if args.verify:
        root = args.build if args.build else DEST
        bad = verify(root, params, cfg)
        for line in bad:
            print("FAIL", line)
        print("web.py: %s" % ("FAIL" if bad else "ok (%d files)" % len(outputs(root))))
        return 1 if bad else 0

    build = (args.build or REPO / "build/web").resolve()
    build.mkdir(parents=True, exist_ok=True)
    stage = args.only
    if stage in (None, "glb"):
        blender(args, build, "glb")
        pack_glb(build / "gremlin.glb", build / "gremlin.packed.glb", args.gltfpack)
        (build / "gremlin.packed.glb").replace(build / "gremlin.glb")
    if stage in (None, "stills"):
        blender(args, build, "stills")
    if stage in (None, "turntable"):
        blender(args, build, "turntable", ["--frames", args.frames] if args.frames else [])
    if stage in (None, "encode"):
        for s in STATES:
            encode_still(build / ("still-%s.png" % s), build / ("gremlin-%s" % s), cfg)
        encode_turntable(build, build / "gremlin-turntable", cfg)
        write_manifest(build, cfg)
        bad = verify(build, params, cfg)
        for line in bad:
            print("FAIL", line)
        print("web.py: %s" % ("FAIL" if bad else "built and verified"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
