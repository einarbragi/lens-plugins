import math, subprocess
C = 32.0
ORANGE, CYAN, WHITE = "#ff8a2a", "#2ec7ff", "#f4f4f4"

def pt(r, a):
    return (C + r * math.cos(a), C + r * math.sin(a))

def aperture_gaps(R, rh, rot, n=6):
    hexv = [pt(rh, rot + i * 2 * math.pi / n) for i in range(n)]
    out = []
    for i in range(n):
        x0, y0 = hexv[i]; x1, y1 = hexv[(i + 1) % n]
        dx, dy = x0 - x1, y0 - y1; L = math.hypot(dx, dy); dx, dy = dx / L, dy / L
        px, py = x0 - C, y0 - C
        b = px * dx + py * dy; c = px * px + py * py - (R + 2) ** 2
        t = -b + math.sqrt(b * b - c)
        out.append((x0, y0, x0 + t * dx, y0 + t * dy))
    return hexv, out

def poly(v):
    return "M" + " L".join("%.2f,%.2f" % p for p in v) + " Z"

# ---- A: flat aperture iris
hexv, gaps = aperture_gaps(28, 11, math.radians(15))
lines = "".join('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % g for g in gaps)
A = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<defs><mask id="m"><circle cx="32" cy="32" r="28" fill="#fff"/>
<g stroke="#000" stroke-width="3.2" stroke-linecap="butt">{lines}</g>
<path d="{poly(hexv)}" fill="#000" stroke="#000" stroke-width="3.2" stroke-linejoin="round"/></mask></defs>
<rect width="64" height="64" fill="{WHITE}" mask="url(#m)"/>
<path d="{poly([pt(7.4, math.radians(15) + i*math.pi/3) for i in range(6)])}" fill="{ORANGE}" stroke="{ORANGE}" stroke-width="1.5" stroke-linejoin="round"/>
</svg>'''

# ---- B: chromatic rings (colour fringing) around a bokeh hexagon
B = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<circle cx="29.6" cy="29.6" r="24" fill="none" stroke="{ORANGE}" stroke-width="5"/>
<circle cx="34.4" cy="34.4" r="24" fill="none" stroke="{CYAN}" stroke-width="5"/>
<circle cx="32" cy="32" r="24" fill="none" stroke="{WHITE}" stroke-width="5"/>
<path d="{poly([pt(10.5, math.radians(0) + i*math.pi/3) for i in range(6)])}" fill="{WHITE}" stroke="{WHITE}" stroke-width="2" stroke-linejoin="round"/>
</svg>'''

# ---- C: cat-eye bokeh (two overlapping circles) inside a lens ring
# lens-shaped intersection of two circles r=15 offset +-7 along a diagonal
a = math.radians(-35)
ox, oy = 8.5 * math.cos(a), 8.5 * math.sin(a)
C2 = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<defs><clipPath id="k"><circle cx="{32+ox:.2f}" cy="{32+oy:.2f}" r="18"/></clipPath></defs>
<circle cx="32" cy="32" r="26.5" fill="none" stroke="{WHITE}" stroke-width="5"/>
<circle cx="{32-ox:.2f}" cy="{32-oy:.2f}" r="18" fill="{ORANGE}" clip-path="url(#k)"/>
</svg>'''

for name, svg in (("A", A), ("B", B), ("C", C2)):
    open("flat_%s.svg" % name, "w").write(svg)
    for size in (64, 32, 400):
        subprocess.check_call(["rsvg-convert", "-w", str(size), "-h", str(size), "flat_%s.svg" % name, "-o", "flat_%s_%d.png" % (name, size)])
print("ok")
