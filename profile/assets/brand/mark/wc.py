def lin(c): c/=255; return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
def L(h): h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16) for i in (0,2,4)]; return .2126*lin(r)+.7152*lin(g)+.0722*lin(b)
def cr(a,b): la,lb=L(a),L(b); hi,lo=max(la,lb),min(la,lb); return (hi+.05)/(lo+.05)
