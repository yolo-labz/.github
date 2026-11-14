"""Decision tests for the gremlin head mark. Pre-declared rule (written before the first run):
  1. A direction is eligible only if every one of its required features survives at 16 px in all four forms
     (colour on dark tile, colour on light tile, mono ink on dark, mono ink on light): at least one pixel with
     feature coverage >= 0.5, and feature-vs-surround contrast >= 3:1 (WCAG non-text).
  2. Among the eligible, the lowest mean edge-blur fraction at 16 and 32 px wins (share of silhouette pixels whose
     coverage sits between 0.2 and 0.8: the fewer, the crisper the pixel grid).
  3. Tie (within 0.02): the higher mean peak feature coverage at 16 px.
"""
import io, json, re, subprocess, sys
import numpy as np
from PIL import Image
from master import DIRS, PAL, svg
from wc import cr

def rast(s, n):
    p = subprocess.run(["rsvg-convert","-w",str(n),"-h",str(n),"-f","png"], input=s.encode(), capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode())
    return np.array(Image.open(io.BytesIO(p.stdout)).convert("RGBA")).astype(float)

def wrap(inner, tile, scale=0.82):
    if tile:
        t=(1-scale)*8
        inner=f'<g transform="translate({t:.3f} {t+0.2:.3f}) scale({scale})">{inner}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" fill="#fff"/>{inner}</svg>'
def cov_of(paths, n, tile):
    a = rast(wrap("".join(f'<path d="{d}" fill="#000"/>' for d in paths), tile), n)
    return 1 - a[...,0]/255
def hexs(rgb): return '#%02x%02x%02x'%tuple(int(round(v)) for v in rgb)

FORMS = [("colour","dark",True),("colour","light",True),("mono","dark",False),("mono","light",False)]
def run():
    out = {}
    for k,D in DIRS.items():
        res = {"name":D["name"], "forms":{}}
        for mode,sch,tile in FORMS:
            key=f"{mode}-{sch}"+("-tile" if tile else "")
            P=PAL[sch]; r={}
            full16 = rast(svg(k,mode,sch,tile), 16)
            # mono is drawn loose on its ground; paint it
            ground = P["ground"]; g = np.array([int(ground[i:i+2],16) for i in (1,3,5)],float)
            def flat(a): return a[...,:3]*(a[...,3:4]/255) + g*(1-a[...,3:4]/255)
            img16 = flat(full16)
            sil16 = cov_of(D["sil"],16,tile)
            for n in (16,32):
                s = cov_of(D["sil"],n,tile); m = s>0.05
                r[f"blur{n}"] = round(float(((s>0.2)&(s<0.8))[m].mean()),3)
            # surround = pixels deep in the silhouette, away from every feature
            allf = cov_of(list(D["feat"].values())+D["teeth"],16,tile)
            sur = img16[(sil16>=0.95)&(allf<=0.02)]
            surround = sur.mean(axis=0) if len(sur) else img16[sil16>=0.95].mean(axis=0)
            feats = {}
            for fn in D["required"]:
                c = cov_of([D["feat"][fn]],16,tile); px = c>=0.5
                if px.sum()==0: feats[fn]=dict(px=0,peak=round(float(c.max()),2),contrast=None); continue
                fc = img16[px].mean(axis=0)
                feats[fn]=dict(px=int(px.sum()),peak=round(float(c.max()),2),contrast=round(cr(hexs(fc),hexs(surround)),2))
            r["features"]=feats
            r["surround"]=hexs(surround)
            r["survive"]=all(f["px"]>0 and f["contrast"]>=3 for f in feats.values())
            res["forms"][key]=r
        # blur error: colour dark tile at 16 (nearest-up to 128) against the 128 render, luminance
        a16 = rast(svg(k,"colour","dark",True),16); a128 = rast(svg(k,"colour","dark",True),128)
        L = lambda a: (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])/255
        up = np.kron(L(a16), np.ones((8,8))); ref = L(a128)
        res["fidelity_err16"] = round(float(np.abs(up-ref).mean()/ (ref.std()+1e-9)),3)
        f = res["forms"]
        res["eligible"] = all(v["survive"] for v in f.values())
        res["mean_blur"] = round(float(np.mean([v[b] for v in f.values() for b in ("blur16","blur32")])),3)
        res["mean_peak16"] = round(float(np.mean([x["peak"] for v in f.values() for x in v["features"].values()])),3)
        out[k]=res
    el = [k for k in out if out[k]["eligible"]]
    win=None
    if el:
        el.sort(key=lambda k:(out[k]["mean_blur"],-out[k]["mean_peak16"]))
        win=el[0]
        if len(el)>1 and abs(out[el[0]]["mean_blur"]-out[el[1]]["mean_blur"])<=0.02:
            win=max(el[:2], key=lambda k: out[k]["mean_peak16"])
    return out, win
if __name__=="__main__":
    out, win = run(); json.dump(dict(results=out, winner=win), open(sys.argv[1] if len(sys.argv)>1 else "tests.json","w"), indent=1)
    for k,v in out.items():
        print(k, v["name"], "eligible" if v["eligible"] else "NOT eligible", "mean_blur",v["mean_blur"],"peak16",v["mean_peak16"],"fid_err",v["fidelity_err16"])
        for fk,fv in v["forms"].items(): print("   ",fk.ljust(18), "survive" if fv["survive"] else "FAIL   ", "blur16",fv["blur16"],"blur32",fv["blur32"], fv["features"])
    print("WINNER", win)
