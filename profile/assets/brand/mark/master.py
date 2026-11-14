"""Master geometry for the gremlin head mark. SHIP names the direction in use; the other two stay so the decision can be re-run (tests.py).
One master per direction, all on a 16-unit grid (integer coordinates, so 16, 32, 64, 128 px are exact multiples).
A direction = silhouette parts (skin) + features. Features are cut out of the silhouette in mono and filled `feature` in colour."""
SHIP = "A"
PAL = {
 "dark":  dict(ground="#1e1e2e", skin="#a6e3a1", feat="#181825", pale="#cdd6f4", node="#cba6f7", ink="#cdd6f4"),
 "light": dict(ground="#eff1f5", skin="#388c26", feat="#181825", pale="#eff1f5", node="#8839ef", ink="#1e1e2e"),
}
EAR_L="M0 1 C4 1.2 6.6 3.4 6.6 6 L3.4 11 C0.8 9 0 5 0 1 Z"
EAR_R="M16 1 C12 1.2 9.4 3.4 9.4 6 L12.6 11 C15.2 9 16 5 16 1 Z"
HEAD="M3 9.5 C3 6.6 5 5 8 5 C11 5 13 6.6 13 9.5 C13 12.4 11 14.5 8 14.5 C5 14.5 3 12.4 3 9.5 Z"
EYE_L="M3.6 7 L7.2 8.4 L7.2 10 Q7.2 11 5.4 11 Q3.6 11 3.6 9.6 Z"
EYE_R="M12.4 7 L8.8 8.4 L8.8 10 Q8.8 11 10.6 11 Q12.4 11 12.4 9.6 Z"
DIRS = {
 # A: ears + eyes. The ear span is the silhouette; two slanted eyes give the glare. No mouth.
 "A": dict(name="A ears+eyes", sil=[EAR_L,EAR_R,HEAD], feat=dict(eyeL=EYE_L, eyeR=EYE_R),
   pupil=[(5.6,9.4,0.7),(10.4,9.4,0.7)], teeth=[], required=["eyeL","eyeR"]),
 # B: ears + grin. The fanged grin is the face; no eyes.
 "B": dict(name="B ears+grin", sil=[EAR_L,EAR_R,HEAD], feat=dict(grin="M3.4 9 Q8 16.4 12.6 9 Q8 11.2 3.4 9 Z"),
   pupil=[], teeth=["M5.2 10.2 L7.2 10.7 L6.2 12.8 Z","M10.8 10.2 L8.8 10.7 L9.8 12.8 Z"], required=["grin"]),
 # C: compact face. Short ears inside the box; eyes + grin. Built for the square tile.
 "C": dict(name="C eyes+grin, short ears", sil=["M1 3.5 C3.4 3.5 5 4.6 5 6.4 L3 9.4 C1 8.4 1 5.5 1 3.5 Z","M15 3.5 C12.6 3.5 11 4.6 11 6.4 L13 9.4 C15 8.4 15 5.5 15 3.5 Z",
        "M2 9 C2 5.4 4.6 3.4 8 3.4 C11.4 3.4 14 5.4 14 9 C14 12.4 11.4 15 8 15 C4.6 15 2 12.4 2 9 Z"],
   feat=dict(eyeL="M3 6.2 L7 7.6 L7 8.8 Q7 9.6 5.2 9.6 Q3 9.6 3 8.4 Z", eyeR="M13 6.2 L9 7.6 L9 8.8 Q9 9.6 10.8 9.6 Q13 9.6 13 8.4 Z", grin="M4.2 11 Q8 15 11.8 11 Q8 12.6 4.2 11 Z"),
   pupil=[(5.2,8.3,0.6),(10.8,8.3,0.6)], teeth=["M5.8 11.7 L7.3 12 L6.5 13.4 Z","M10.2 11.7 L8.7 12 L9.5 13.4 Z"], required=["eyeL","eyeR","grin"]),
}

def svg(key, mode="colour", scheme="dark", tile=False, size=None, only=None, scale=0.82, pupils=False, rx=3.4):
    D=DIRS[key]; P=PAL[scheme]; s=f' width="{size}" height="{size}"' if size else ""
    vb='0 0 16 16'
    body=[]
    sk = P["skin"] if mode=="colour" else P["ink"]
    inner=[]
    if only is None or only=="sil":
        if mode=="colour":
            inner.append(f'<g fill="{P["skin"]}" stroke="{P["skin"]}" stroke-width="0" shape-rendering="geometricPrecision">'+"".join(f'<path d="{d}"/>' for d in D["sil"])+'</g>')
            for n,d in D["feat"].items(): inner.append(f'<path d="{d}" fill="{P["feat"]}"/>')
            for d in D["teeth"]: inner.append(f'<path d="{d}" fill="{P["pale"] if scheme=="dark" else "#eff1f5"}"/>')
            if pupils:
                for cx,cy,rr in D["pupil"]: inner.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{P["node"]}"/>')
        else:
            holes="".join(f'<path d="{d}" fill="#000"/>' for d in D["feat"].values())
            inner.append(f'<mask id="m" maskUnits="userSpaceOnUse" x="-1" y="-1" width="18" height="18"><rect x="-1" y="-1" width="18" height="18" fill="#fff"/>{holes}</mask>')
            inner.append(f'<g mask="url(#m)" fill="{P["ink"]}">'+"".join(f'<path d="{d}"/>' for d in D["sil"])+'</g>')
            for d in D["teeth"]: inner.append(f'<path d="{d}" fill="{P["ink"]}"/>')
    g="".join(inner)
    if tile:
        t=(1-scale)*8
        g=f'<rect width="16" height="16" rx="{rx}" fill="{P["ground"]}"/><g transform="translate({t:.3f} {t+0.2:.3f}) scale({scale})">{g}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{s}>{g}</svg>'
