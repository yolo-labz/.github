// Loads gremlin.glb (meshopt + quantized, one skin, five clips) and draws it with WebGL2.
// No dependencies besides ./meshopt_decoder.mjs. Entry point: render(canvas, options).
import { MeshoptDecoder } from "./meshopt_decoder.mjs";

const TYPES = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
const ARRAYS = { 5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
const LIMITS = { 5120: 127, 5121: 255, 5122: 32767, 5123: 65535 };

// Light-ground colours: the .glb ships the dark palette (model/params.json palette_light).
export const THEMES = {
  dark: {},
  light: { skin: "#388c26", node: "#8839ef", key: "#9ca0b0", guide: "#9ca0b0", dark: "#dce0e8", feature: "#181825", ink: "#1e1e2e" },
};
// The camera and the three lights are the ones the still images use (model/character.json).
const CAMERA = { azimuth: 24, elevation: 9, scale: 292, center: [0, -36, 0] };
const LIGHTS = [
  { dir: [-0.486, 0.532, 0.694], color: [1.0, 1.0, 1.0] },
  { dir: [0.748, 0.201, 0.633], color: [0.8, 0.8, 0.8] },
  { dir: [0.242, 0.538, -0.807], color: [0.9, 0.9, 0.9] },
];

// ---- matrices (column-major, 16 floats) -------------------------------------------
const mul = (a, b) => {
  const o = new Float32Array(16);
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
    o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
  }
  return o;
};
export const fromTRS = (t, q, s) => {
  const [x, y, z, w] = q;
  const o = new Float32Array(16);
  o[0] = (1 - 2 * (y * y + z * z)) * s[0]; o[1] = 2 * (x * y + z * w) * s[0]; o[2] = 2 * (x * z - y * w) * s[0];
  o[4] = 2 * (x * y - z * w) * s[1]; o[5] = (1 - 2 * (x * x + z * z)) * s[1]; o[6] = 2 * (y * z + x * w) * s[1];
  o[8] = 2 * (x * z + y * w) * s[2]; o[9] = 2 * (y * z - x * w) * s[2]; o[10] = (1 - 2 * (x * x + y * y)) * s[2];
  o[12] = t[0]; o[13] = t[1]; o[14] = t[2]; o[15] = 1;
  return o;
};

// ---- GLB --------------------------------------------------------------------------
export async function parseGlb(buffer) {
  const view = new DataView(buffer);
  if (view.getUint32(0, true) !== 0x46546c67) throw new Error("not a GLB");
  const jsonLength = view.getUint32(12, true);
  const doc = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 20, jsonLength)));
  const bin = new Uint8Array(buffer, 28 + jsonLength, view.getUint32(20 + jsonLength, true));
  await MeshoptDecoder.ready;
  const views = doc.bufferViews.map((v) => {
    const ext = v.extensions && v.extensions.EXT_meshopt_compression;
    if (!ext) return { bytes: bin.subarray(v.byteOffset || 0, (v.byteOffset || 0) + v.byteLength), stride: v.byteStride || 0 };
    const out = new Uint8Array(ext.count * ext.byteStride);
    MeshoptDecoder.decodeGltfBuffer(out, ext.count, ext.byteStride, bin.subarray(ext.byteOffset, ext.byteOffset + ext.byteLength), ext.mode, ext.filter || "NONE");
    return { bytes: out, stride: ext.byteStride };
  });
  return { doc, views };
}

// An accessor as a Float32Array (normalised integers are scaled to 0..1 or -1..1).
export function readFloats(glb, index) {
  const a = glb.doc.accessors[index], v = glb.views[a.bufferView];
  const n = TYPES[a.type], T = ARRAYS[a.componentType], size = T.BYTES_PER_ELEMENT * n;
  const stride = v.stride || size, out = new Float32Array(a.count * n);
  const dv = new DataView(v.bytes.buffer, v.bytes.byteOffset, v.bytes.byteLength);
  const get = { 5120: "getInt8", 5121: "getUint8", 5122: "getInt16", 5123: "getUint16", 5125: "getUint32", 5126: "getFloat32" }[a.componentType];
  for (let i = 0; i < a.count; i++) for (let k = 0; k < n; k++) {
    let x = dv[get]((a.byteOffset || 0) + i * stride + k * T.BYTES_PER_ELEMENT, true);
    if (a.normalized) x = Math.max(x / LIMITS[a.componentType], -1);
    out[i * n + k] = x;
  }
  return out;
}

// ---- animation --------------------------------------------------------------------
export function buildRig(glb) {
  const { doc } = glb;
  const parent = new Array(doc.nodes.length).fill(-1);
  doc.nodes.forEach((n, i) => (n.children || []).forEach((c) => (parent[c] = i)));
  const rest = doc.nodes.map((n) => ({ t: n.translation || [0, 0, 0], q: n.rotation || [0, 0, 0, 1], s: n.scale || [1, 1, 1] }));
  const clips = {};
  for (const an of doc.animations) {
    const tracks = an.channels.map((ch) => {
      const s = an.samplers[ch.sampler];
      return { node: ch.target.node, path: ch.target.path, times: readFloats(glb, s.input), values: readFloats(glb, s.output), step: s.interpolation === "STEP" };
    });
    clips[an.name] = { tracks, duration: Math.max(...tracks.map((t) => t.times[t.times.length - 1])) };
  }
  const skin = doc.skins[0];
  return { doc, parent, rest, clips, joints: skin.joints, ibm: readFloats(glb, skin.inverseBindMatrices), meshNodes: doc.nodes.map((n, i) => (n.mesh !== undefined ? i : -1)).filter((i) => i >= 0) };
}

// Local transforms of every node for a clip at time t (seconds, looped).
export function samplePose(rig, clip, t) {
  const pose = rig.rest.map((r) => ({ t: r.t.slice(), q: r.q.slice(), s: r.s.slice() }));
  const time = clip.duration > 0 ? t % clip.duration : 0;
  for (const tr of clip.tracks) {
    const n = tr.times.length, w = tr.path === "rotation" ? 4 : 3;
    let i = 0;
    while (i < n - 1 && tr.times[i + 1] <= time) i++;
    const j = Math.min(i + 1, n - 1);
    const f = tr.step || i === j ? 0 : (time - tr.times[i]) / (tr.times[j] - tr.times[i]);
    const a = tr.values.subarray(i * w, i * w + w), b = tr.values.subarray(j * w, j * w + w);
    const out = pose[tr.node][{ translation: "t", rotation: "q", scale: "s" }[tr.path]];
    for (let k = 0; k < w; k++) out[k] = a[k] + (b[k] - a[k]) * f;
    if (w === 4) { const l = Math.hypot(...out); for (let k = 0; k < 4; k++) out[k] /= l; }
  }
  return pose;
}

export function blendPose(a, b, f) {
  return a.map((x, i) => {
    const y = b[i], dot = x.q[0] * y.q[0] + x.q[1] * y.q[1] + x.q[2] * y.q[2] + x.q[3] * y.q[3], sg = dot < 0 ? -1 : 1;
    const q = x.q.map((v, k) => v + (sg * y.q[k] - v) * f), l = Math.hypot(...q);
    return { t: x.t.map((v, k) => v + (y.t[k] - v) * f), q: q.map((v) => v / l), s: x.s.map((v, k) => v + (y.s[k] - v) * f) };
  });
}

// Skin matrices: global joint transform times the inverse bind matrix; the mesh nodes
// carry the dequantisation, which is applied to the vertex first.
export function jointMatrices(rig, pose, out) {
  const global = new Array(pose.length);
  const world = (i) => global[i] || (global[i] = rig.parent[i] < 0 ? fromTRS(pose[i].t, pose[i].q, pose[i].s)
    : mul(world(rig.parent[i]), fromTRS(pose[i].t, pose[i].q, pose[i].s)));
  rig.joints.forEach((node, j) => out.set(mul(world(node), rig.ibm.subarray(j * 16, j * 16 + 16)), j * 16));
  return out;
}

// ---- drawing ----------------------------------------------------------------------
const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]; };
const toLinear = (c) => c.map((x) => (x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));

const VERT = `#version 300 es
in vec3 aPos; in vec3 aNormal; in vec4 aWeights; in uvec4 aJoints;
uniform mat4 uJoint[26]; uniform mat4 uMesh; uniform mat4 uView;
out vec3 vN;
void main() {
  mat4 s = aWeights.x * uJoint[aJoints.x] + aWeights.y * uJoint[aJoints.y] + aWeights.z * uJoint[aJoints.z] + aWeights.w * uJoint[aJoints.w];
  vec4 p = s * (uMesh * vec4(aPos, 1.0));
  vN = normalize(mat3(s) * aNormal);
  gl_Position = uView * p;
}`;
const FRAG = `#version 300 es
precision highp float;
in vec3 vN; uniform vec3 uBase; uniform float uRough; uniform vec3 uLight[3]; uniform vec3 uLightColor[3];
out vec4 o;
void main() {
  vec3 n = normalize(vN), v = vec3(0.4, 0.15, 0.9), c = uBase * 0.32;
  for (int i = 0; i < 3; i++) {
    vec3 l = normalize(uLight[i]);
    float d = max(dot(n, l), 0.0);
    float h = pow(max(dot(n, normalize(l + v)), 0.0), mix(60.0, 10.0, uRough));
    c += uLightColor[i] * (uBase * d * 0.78 + vec3(h * (1.0 - uRough) * 0.12));
  }
  o = vec4(pow(c, vec3(1.0 / 2.2)), 1.0);
}`;

function program(gl) {
  const make = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
  const p = gl.createProgram();
  gl.attachShader(p, make(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, make(gl.FRAGMENT_SHADER, FRAG));
  gl.bindAttribLocation(p, 0, "aPos"); gl.bindAttribLocation(p, 1, "aNormal"); gl.bindAttribLocation(p, 2, "aWeights"); gl.bindAttribLocation(p, 3, "aJoints");
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  return p;
}

function viewMatrix(azimuth, aspect) {
  const az = (azimuth * Math.PI) / 180, el = (CAMERA.elevation * Math.PI) / 180;
  const dir = [Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)];
  const z = dir, x = [z[2], 0, -z[0]], lx = Math.hypot(x[0], x[2]);
  x[0] /= lx; x[2] /= lx;
  const y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]];
  const c = CAMERA.center, d = (u) => u[0] * c[0] + u[1] * c[1] + u[2] * c[2];
  const look = new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -d(x), -d(y), -d(z), 1]);
  const h = CAMERA.scale / 2, far = 2000;
  const ortho = new Float32Array([1 / (h * aspect), 0, 0, 0, 0, 1 / h, 0, 0, 0, 0, -2 / far, 0, 0, 0, -1, 1]);
  return mul(ortho, look);
}

// options: { src, state, theme, azimuth, interactive, onReady } -> controller
export async function render(canvas, options) {
  const gl = canvas.getContext("webgl2", { alpha: true, premultipliedAlpha: true, antialias: true });
  if (!gl) throw new Error("no webgl2");
  const glb = parseGlb(await (await fetch(options.src)).arrayBuffer());
  const model = await glb, rig = buildRig(model), doc = model.doc;
  const prog = program(gl);
  const loc = (n) => gl.getUniformLocation(prog, n);
  const buffers = model.views.map((v, i) => {
    if (!doc.bufferViews[i].target) return null;
    const b = gl.createBuffer();
    gl.bindBuffer(doc.bufferViews[i].target, b);
    gl.bufferData(doc.bufferViews[i].target, v.bytes, gl.STATIC_DRAW);
    return b;
  });
  const meshOf = (node) => doc.meshes[doc.nodes[node].mesh];
  const draws = [];
  for (const node of rig.meshNodes) {
    const n = doc.nodes[node], matrix = fromTRS(n.translation || [0, 0, 0], n.rotation || [0, 0, 0, 1], n.scale || [1, 1, 1]);
    for (const prim of meshOf(node).primitives) {
      const vao = gl.createVertexArray();
      gl.bindVertexArray(vao);
      const attr = (name, slot, ints) => {
        const a = doc.accessors[prim.attributes[name]], v = model.views[a.bufferView];
        gl.bindBuffer(gl.ARRAY_BUFFER, buffers[a.bufferView]);
        gl.enableVertexAttribArray(slot);
        if (ints) gl.vertexAttribIPointer(slot, TYPES[a.type], a.componentType, v.stride, a.byteOffset || 0);
        else gl.vertexAttribPointer(slot, TYPES[a.type], a.componentType, !!a.normalized, v.stride, a.byteOffset || 0);
      };
      attr("POSITION", 0); attr("NORMAL", 1); attr("WEIGHTS_0", 2); attr("JOINTS_0", 3, true);
      const idx = doc.accessors[prim.indices];
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffers[idx.bufferView]);
      const m = doc.materials[prim.material];
      draws.push({ vao, count: idx.count, type: idx.componentType, offset: idx.byteOffset || 0, matrix, role: m.name.replace(/^m_/, ""),
        base: m.pbrMetallicRoughness.baseColorFactor, rough: m.pbrMetallicRoughness.roughnessFactor });
    }
  }
  gl.bindVertexArray(null);

  const joints = new Float32Array(rig.joints.length * 16);
  let state = options.state && rig.clips[options.state] ? options.state : "idle", previous = null, mixStart = 0;
  let theme = options.theme || "dark", azimuth = options.azimuth ?? CAMERA.azimuth, running = false, raf = 0, clock = 0, last = 0;
  const colour = (d) => (THEMES[theme][d.role] ? toLinear(hex(THEMES[theme][d.role])) : d.base.slice(0, 3));

  function frame(now) {
    const dt = last ? Math.min((now - last) / 1000, 0.1) : 0;
    last = now; clock += dt;
    const w = canvas.clientWidth, h = canvas.clientHeight, dpr = Math.min(devicePixelRatio || 1, 2);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); }
    let pose = samplePose(rig, rig.clips[state], clock);
    if (previous) {
      const f = Math.min((clock - mixStart) / 0.25, 1);
      pose = blendPose(samplePose(rig, rig.clips[previous], clock), pose, f);
      if (f >= 1) previous = null;
    }
    jointMatrices(rig, pose, joints);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.DEPTH_TEST);
    gl.useProgram(prog);
    gl.uniformMatrix4fv(loc("uJoint"), false, joints);
    gl.uniformMatrix4fv(loc("uView"), false, viewMatrix(azimuth, canvas.width / canvas.height));
    gl.uniform3fv(loc("uLight"), LIGHTS.flatMap((l) => l.dir));
    gl.uniform3fv(loc("uLightColor"), LIGHTS.flatMap((l) => l.color));
    for (const d of draws) {
      gl.uniformMatrix4fv(loc("uMesh"), false, d.matrix);
      gl.uniform3fv(loc("uBase"), colour(d));
      gl.uniform1f(loc("uRough"), d.rough);
      gl.bindVertexArray(d.vao);
      gl.drawElements(gl.TRIANGLES, d.count, d.type, d.offset);
    }
    if (running) raf = requestAnimationFrame(frame);
  }
  const api = {
    clips: Object.keys(rig.clips),
    draw: () => frame(performance.now()),
    play() { if (!running) { running = true; last = 0; raf = requestAnimationFrame(frame); } },
    pause() { running = false; cancelAnimationFrame(raf); },
    setState(name) { if (rig.clips[name] && name !== state) { previous = state; state = name; mixStart = clock; } },
    setTheme(name) { if (THEMES[name]) theme = name; },
    setAzimuth(deg) { azimuth = deg; },
    destroy() { api.pause(); gl.getExtension("WEBGL_lose_context")?.loseContext(); },
  };
  return api;
}
