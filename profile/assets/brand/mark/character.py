#!/usr/bin/env python3
"""The gremlin character, drawn from the head mark. One vector source for the sheet, the five states and the hero.

Units: 1 head unit (HU) = ear to ear = 16 u = the mark box (mark/master.py, direction A). Every part below is in u.
Tokens (@skin, @feat, ...) are painted per scheme at the end, so the same drawing serves the sheet, the adaptive SVGs and the hero.

    python3 character.py sheet OUT.svg [dark|light]
    python3 character.py state NAME OUT.svg        (idle working paused loading asleep, adaptive)
    python3 character.py hero OUT.svg              (adaptive)
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from master import PAL, EAR_L, EAR_R, HEAD, EYE_L, EYE_R

P = {
 "dark":  dict(PAL["dark"],  kbd="#313244", key="#45475a", line="#7f849c", sub="#a6adc8", ground2="#181825"),
 "light": dict(PAL["light"], kbd="#ccd0da", key="#9ca0b0", line="#7c7f93", sub="#5c5f77", ground2="#dce0e8"),
}
PUPIL = [(5.6, 9.4, .7), (10.4, 9.4, .7)]          # node pupils, from 64 px up (same numbers as the mark)

def tr(d, rot=0, px=0, py=0, dx=0, dy=0, s=1):
    return f'<g transform="translate({dx} {dy}) rotate({rot} {px} {py}) scale({s})">{d}</g>'
def path(d, fill="@skin", extra=""): return f'<path d="{d}" fill="{fill}" {extra}/>'
def stroke(d, w, col="@skin", extra=""): return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'

# ---------- head, three views (head box 0..16 wide, y 0..16) ----------
def mouth(kind="grin", x0=5, x1=11, y=12.0, shift=0):
    """kind grin: dark slot, two pale fangs hanging from the upper lip. closed: a short dark slit. none: nothing."""
    if kind == "none": return ""
    cx = (x0 + x1) / 2
    if kind == "closed":
        return stroke(f"M{x0+1.2} {y+0.9} Q{cx} {y+1.5} {x1-1.2} {y+0.9}", .5, "@feat")
    slot = f"M{x0} {y} Q{cx} {y+2.4} {x1} {y} Q{cx} {y+0.95} {x0} {y} Z"
    f1 = f"M{x0+1.1} {y+0.42} L{x0+2.5} {y+0.62} L{x0+1.8} {y+1.75} Z"
    f2 = f"M{x1-1.1} {y+0.42} L{x1-2.5} {y+0.62} L{x1-1.8} {y+1.75} Z"
    return path(slot, "@feat") + path(f1, "@pale") + path(f2, "@pale")

def pupils(pts, node=True):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="@node"/>' for x, y, r in pts) if node else ""

def lids(eyes):
    """closed eyes: each socket collapses to its slanted top edge, a 0.6 u slit in feature colour"""
    return "".join(stroke(d, .6, "@feat") for d in eyes)

def ear(side, rot=0):
    d = EAR_L if side == "L" else EAR_R
    px = 5 if side == "L" else 11
    return tr(path(d), rot, px, 7)

def head_front(mode="grin", looking="open", ears=(0, 0), pupil=True, pdy=0):
    g = ear("L", ears[0]) + ear("R", ears[1]) + path(HEAD)
    if looking == "open":
        g += path(EYE_L, "@feat") + path(EYE_R, "@feat")
        if pupil: g += pupils([(x, y + pdy, r) for x, y, r in PUPIL])
    else:
        g += lids(["M3.8 8 L7 9.2", "M12.2 8 L9 9.2"])
    return g + mouth(mode, 5.2, 10.8, 12.0)

def head_34(mode="grin", pupil=True):
    """turned to the viewer's right. Near ear (left) large and swept back, far ear (right) small and close."""
    nearE = "M0 1.6 C3.6 1.4 6.6 3.6 7 6.4 L4.8 11 C1.4 9.4 0 5.4 0 1.6 Z"
    farE = "M15.4 3.2 C12.8 3.4 11.6 4.6 11.6 6.4 L13.2 9.4 C14.8 8.2 15.4 6 15.4 3.2 Z"
    mass = "M4.2 9.6 C4.2 6.6 6.2 5 9.1 5 C12.2 5 14.2 6.6 14.2 9.6 C14.2 12.4 12.2 14.5 9.3 14.5 C6.3 14.5 4.2 12.4 4.2 9.6 Z"
    eL = "M5 7.1 L8.4 8.5 L8.4 10 Q8.4 11 6.6 11 Q5 11 5 9.6 Z"
    eR = "M13.4 7.4 L10.5 8.6 L10.5 10 Q10.5 11 11.8 11 Q13.4 11 13.4 9.7 Z"
    g = path(farE) + path(nearE) + path(mass) + path(eL, "@feat") + path(eR, "@feat")
    if pupil: g += pupils([(6.6, 9.4, .7), (11.9, 9.4, .6)])
    return g + mouth(mode, 6.6, 12.4, 12.0)

def head_side(mode="grin", pupil=True):
    """profile, facing right. One ear swept back, one eye socket, the grin runs to the front edge."""
    ear_ = "M0.4 1.6 C4.8 2 8.2 4 8.6 7 L5.8 10.8 C2 8.8 -0.2 5.4 0.4 1.6 Z"
    mass = "M4 9.6 C4 6.8 6 5 9 5 C12.2 5 14.4 7 14.4 9.6 C14.4 12.4 12.2 14.5 9 14.5 C6 14.5 4 12.4 4 9.6 Z"
    nose = "M14 8.6 L15.8 9.9 L14 11 Z"
    eye = "M8.6 7.2 L12.6 8.7 L12.6 10 Q12.6 11 11 11 Q8.6 11 8.6 9.6 Z"
    g = path(ear_) + path(mass) + path(nose) + path(eye, "@feat")
    if pupil: g += pupils([(11.2, 9.4, .7)])
    if mode == "grin":
        g += path("M9.4 12.2 Q12.4 14.2 14.6 12 Q12.2 12.9 9.4 12.2 Z", "@feat") + path("M11.2 12.55 L12.5 12.7 L11.9 13.75 Z", "@pale")
    return g

# ---------- body, 1 HU wide, hangs below the head box ----------
TORSO = "M4.6 16.2 C4.6 14.6 6 14.2 8 14.2 C10 14.2 11.4 14.6 11.4 16.2 L11.4 20 C11.4 22.8 10 24 8 24 C6 24 4.6 22.8 4.6 20 Z"
def hand(x, y, rot=0):
    """three pointed digits, skin colour, no separate claw colour (pale never touches skin)"""
    d = "M-1.1 -0.6 L-1.2 1.3 L-0.45 0.8 L0 1.9 L0.45 0.8 L1.2 1.3 L1.1 -0.6 Z"
    return f'<g transform="translate({x} {y}) rotate({rot})">{path(d)}</g>'
def feet(): return path("M3.4 24.4 Q3.4 23.4 5.2 23.4 L6.8 23.4 Q7.4 24 7.4 24.8 L3.4 24.8 Z") + path("M12.6 24.4 Q12.6 23.4 10.8 23.4 L9.2 23.4 Q8.6 24 8.6 24.8 L12.6 24.8 Z")
def tail(kind="curl"):
    if kind == "curl":
        return stroke("M11.6 21.4 C15 22 17.6 20.4 17.4 17.8", 1.1) + path("M16.4 18 L17.4 15.8 L18.6 18 Z")
    if kind == "low":
        return stroke("M11.6 21.8 C15 23 17.6 22.4 18.4 21", 1.1) + path("M17.8 22 L19.4 20.8 L19.2 22.8 Z")
    return stroke("M11.6 21 C14 18.5 16.5 18.5 17.6 16.4", 1.1) + path("M16.6 16.8 L18.2 15.2 L18.2 17.6 Z")

def arms(kind):
    a = lambda d: stroke(d, 2.1)
    if kind == "knees":   return a("M4.8 16.8 Q1.2 19.2 2.8 22.6") + a("M11.2 16.8 Q14.8 19.2 13.2 22.6") + hand(2.8, 23, 0) + hand(13.2, 23, 0)
    if kind == "type":    return a("M4.8 16.8 Q1.4 19.6 4 22") + a("M11.2 16.8 Q14.6 19.6 12 22") + hand(4.1, 22.4, 0) + hand(11.9, 22.4, 0)
    if kind == "raise":   return a("M4.8 16.8 Q1.2 19.2 2.8 22.6") + hand(2.8, 23, 0) + a("M11.2 16.8 Q16.4 16 15.4 11.4") + hand(15.4, 10.9, 180)
    if kind == "dash":    return a("M4.8 16.8 Q0.8 17.8 -0.6 15.2") + hand(-0.7, 15, 150) + a("M11.2 17 Q15 19.4 13.6 22.6") + hand(13.6, 23, 0)
    if kind == "tuck":    return a("M4.8 17.4 Q1.6 20 4 22.2") + a("M11.2 17.4 Q14.4 20 12 22.2") + hand(4.1, 22.6, 0) + hand(11.9, 22.6, 0)

def line(x0, x1, y): return f'<path d="M{x0} {y} L{x1} {y}" stroke="@line" stroke-width=".5" stroke-linecap="round" fill="none"/>'
def keyboard(): return (f'<path d="M-1.6 22 L17.6 22 L19.4 25.6 L-3.4 25.6 Z" fill="@kbd"/>'
    + "".join(f'<rect x="{x}" y="{y}" width="2" height=".9" rx=".2" fill="@key"/>' for y, xs in ((22.9, (0.2, 2.8, 5.4, 8, 10.6, 13.2)), (24.3, (0.4, 3.2, 6, 8.8, 11.6, 14.4))) for x in xs))
def brackets(): return (stroke("M-1.6 2 L-3.6 4 L-1.6 6", .8, "@node") + stroke("M-0.2 2 L1.8 4 L-0.2 6", .8, "@node")
    + stroke("M17.6 2 L15.6 4 L17.6 6", .8, "@node") + stroke("M19 2 L21 4 L19 6", .8, "@node")
    + stroke("M2 15.6 l-1.4 -1.4 M1.6 18 l-1.8 -.5 M14 15.6 l1.4 -1.4 M14.4 18 l1.8 -.5", .6, "@node"))

# ---------- the five states (body + head, in head-box coordinates, 0..16 wide, 0..26 high) ----------
def state(name):
    if name == "idle":
        return tail("curl") + path(TORSO) + feet() + arms("knees") + head_front("grin") + line(-3, 19, 25.4)
    if name == "working":
        return (tail("curl") + path(TORSO) + keyboard() + arms("type") + head_front("grin", pdy=.5) + brackets())
    if name == "paused":
        sound = stroke("M-1.8 7 Q-3 9.4 -1.8 11.8", .6, "@sub") + stroke("M-3.4 5.8 Q-5.2 9.4 -3.4 13", .6, "@sub")
        return tail("low") + path(TORSO) + feet() + arms("raise") + head_34("grin") + line(-3, 19, 25.4) + sound
    if name == "loading":
        body = tail("up") + path(TORSO) + feet() + arms("dash") + head_front("grin", ears=(-26, 26))
        ticks = "".join(stroke(f"M{x} {y} L{x+3.2} {y}", .6, "@sub") for x, y in ((-7, 14), (-6, 17), (-7.4, 20)))
        dashes = "".join(stroke(f"M{x} 25.4 L{x+1.4} 25.4", .5, "@line") for x in (-6, -3, 0, 3, 6, 9, 12, 15))
        return tr(body, -6, 8, 24) + ticks + dashes
    if name == "asleep":
        body = tail("low") + path(TORSO) + feet() + arms("tuck") + head_front("closed", looking="shut", ears=(-50, 50), pupil=False)
        moon = '<path d="M16 1 A3 3 0 1 0 19 4.6 A2.4 2.4 0 1 1 16 1 Z" fill="@pale"/>'
        return tr(body, 0, 8, 24, 0, 1.2) + moon + line(-3, 19, 25.4)
    raise SystemExit(name)

# ---------- painting ----------
def paint(frag, scheme):
    return re.sub(r"@(\w+)", lambda m: P[scheme][m.group(1)], frag)
def adapt(frag, extra_css=""):
    """one SVG that follows prefers-color-scheme: tokens become classes"""
    def tag(m):
        t = m.group(0); cls = []
        def sub(mm):
            cls.append(("f-" if mm.group(1) == "fill" else "s-") + mm.group(2)); return ""
        t2 = re.sub(r'\s(fill|stroke)="@(\w+)"', sub, t)
        if cls: t2 = t2.replace("<", "<", 1); t2 = re.sub(r"^<(\w+)", lambda q: f'<{q.group(1)} class="{" ".join(cls)}"', t2)
        return t2
    out = re.sub(r"<[a-zA-Z][^>]*>", tag, frag)
    def rules(sch):
        return "".join(f".f-{k}{{fill:{v}}}.s-{k}{{stroke:{v}}}" for k, v in P[sch].items())
    css = rules("dark") + "@media (prefers-color-scheme:light){" + rules("light") + "}"
    return out, css

def wrap(body, vb, title, desc, scheme=None, ground=None):
    if scheme:
        inner = paint(body, scheme); style = ""
    else:
        inner, css = adapt(body); style = f"<style>{css}</style>"
    bg = f'<rect width="100%" height="100%" fill="{P[scheme]["ground"]}"/>' if ground else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>{style}{bg}{inner}</svg>\n')

def at(g, x, y, s): return f'<g transform="translate({x} {y}) scale({s})">{g}</g>'
def txt(x, y, s, size=13, col="@sub", w=400, anchor="start", mono=True):
    fam = "JetBrains Mono, JetBrainsMono Nerd Font Mono, monospace" if mono else "Inter, sans-serif"
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{col}" text-anchor="{anchor}">{s}</text>'
def guide(x0, y0, x1, y1, col="@node", dash="3 3"): return f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{col}" stroke-width="1" stroke-dasharray="{dash}" fill="none" opacity=".85"/>'

STATES = ("idle", "working", "paused", "loading", "asleep")
DESC = {"idle": "The gremlin sitting on a line, arms at its sides, grinning.",
        "working": "The gremlin at a keyboard, mauve code brackets beside its ears.",
        "paused": "The gremlin with its head turned and one hand raised, sound arcs at its side.",
        "loading": "The gremlin leaning forward off a dashed line, ears swept back.",
        "asleep": "The gremlin hunched on a line, eyes shut, a moon above."}

def state_svg(name):
    return wrap(state(name), "-8 -2 36 31", f"yolo-labz gremlin, {name}", DESC[name])

def sheet(scheme="dark"):
    W, H = 1600, 1260
    g = txt(40, 50, "yolo-labz gremlin: character sheet", 28, "@ink", 500)
    g += txt(40, 78, "1 head unit (HU) = ear to ear = 16 u = the mark box. Eyes and brow are the mark's. Skin is the character and is never recoloured.", 14)
    S = 17.5
    views = [("front", head_front(), 40), ("three-quarter", head_34(), 360), ("side", head_side(), 680)]
    for name, h, x in views:
        y = 120
        g += at(h, x, y, S)
        for gy, lab in ((1, "ear tip"), (7, "brow"), (9.4, "pupils"), (12, "mouth")):
            g += guide(x - 8, y + gy * S, x + 16 * S + 8, y + gy * S, "@line", "2 4")
        g += txt(x, y + 16 * S + 30, name, 15, "@ink", 500)
    for gy, lab in ((1, "ear tip"), (7, "brow"), (9.4, "pupils"), (12, "mouth")):
        g += txt(1000, 120 + gy * S + 4, lab, 11, "@line", 400)
    # full body
    g += at(state("idle"), 1120, 112, 15.2)
    g += txt(1120, 112 + 26 * 15.2 + 30, "full body, idle: 1.55 HU tall", 15, "@ink", 500)
    # rules
    y0 = 600
    g += txt(40, y0, "Eyes", 16, "@ink", 500)
    g += at(path(EYE_L, "@feat") + path(EYE_R, "@feat") + pupils(PUPIL), 40, y0 + 12 - 6.5 * 13, 13)
    for i, l in enumerate(["two dark sockets #181825", "slanted top edge = the brow", "node pupils r 0.7 u, 64 px up", "no round eyes, no highlights"]):
        g += txt(40, y0 + 112 + i * 20, l, 12)
    g += txt(330, y0, "Mouth", 16, "@ink", 500)
    g += at(head_front("none", pupil=False), 330, y0 + 14, 7) + at(head_front("grin"), 470, y0 + 14, 7)
    g += txt(330, y0 + 14 + 16 * 7 + 20, "mark: none", 12) + txt(470, y0 + 14 + 16 * 7 + 20, "character: grin", 12)
    g += txt(330, y0 + 14 + 16 * 7 + 40, "grin from 64 px head width up", 12)
    g += txt(330, y0 + 14 + 16 * 7 + 60, "asleep: closed slit", 12)
    g += txt(330, y0 + 14 + 16 * 7 + 80, "fangs sit on the dark slot", 12)
    g += txt(660, y0, "Hands and tail", 16, "@ink", 500)
    g += at(hand(2, 2) + hand(6, 2) + stroke("M9 3 C11 4 13 2 13 0", 1.1), 660, y0 + 40, 14)
    g += txt(660, y0 + 112, "three pointed digits, skin", 12) + txt(660, y0 + 132, "no pale claws", 12) + txt(660, y0 + 152, "tail 1.1 u, spade tip", 12)
    g += txt(960, y0, "Proportions (16 u = 1 HU)", 16, "@ink", 500)
    for i, l in enumerate(["head mass 10 wide, 9.5 high", "ears 16 span, 4 above skull", "torso 7 wide, 10 high", "arms 2.1 thick", "ear tip to sole 25 (1.55 HU)"]):
        g += txt(960, y0 + 28 + i * 22, l, 12)
    # states
    y1 = 830
    g += txt(40, y1, "Five states, one rig", 16, "@ink", 500)
    for i, n in enumerate(STATES):
        x = 40 + i * 310
        g += at(state(n), x + 20, y1 + 30, 8.6) + txt(x + 130, y1 + 30 + 26 * 8.6 + 30, n, 14, "@ink", 500, "middle")
    g += txt(40, H - 28, "Palette: skin #a6e3a1 / #388c26, feature #181825, node #cba6f7 / #8839ef, pale #cdd6f4 / #eff1f5. Mauve means produced by the gremlin; asleep has none.", 12)
    return wrap(g, f"0 0 {W} {H}", "yolo-labz gremlin character sheet", "Front, three-quarter and side views of the head, the full body, the eye and mouth rules and the five states.", scheme, True)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet": open(sys.argv[2], "w").write(sheet(sys.argv[3] if len(sys.argv) > 3 else "dark"))
    elif cmd == "state": open(sys.argv[3], "w").write(state_svg(sys.argv[2]))
