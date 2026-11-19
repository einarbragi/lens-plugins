import math, subprocess
R_OUT, R_GLASS, R_HEX = 30.0, 23.5, 10.8
C = 32.0
ROT = math.radians(14)

def pt(r, a):
    return (C + r * math.cos(a), C + r * math.sin(a))

hexv = [pt(R_HEX, ROT + i * math.pi / 3) for i in range(6)]
# blade edges: from each hexagon vertex along the next edge direction out to the glass circle
lines = []
for i in range(6):
    x0, y0 = hexv[i]; x1, y1 = hexv[(i + 1) % 6]
    dx, dy = x0 - x1, y0 - y1                     # extend backwards past vertex i
    L = math.hypot(dx, dy); dx, dy = dx / L, dy / L
    # solve |p0 + t d - C| = R_GLASS
    px, py = x0 - C, y0 - C
    b = px * dx + py * dy; c = px * px + py * py - R_GLASS ** 2
    t = -b + math.sqrt(b * b - c)
    lines.append(((x0, y0), (x0 + t * dx, y0 + t * dy)))
hexpath = "M" + " L".join("%.2f,%.2f" % v for v in hexv) + " Z"
blade_lines = "\n".join('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>' % (a[0], a[1], b[0], b[1]) for a, b in lines)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <radialGradient id="barrel" cx="0.4" cy="0.35" r="0.75">
      <stop offset="0" stop-color="#f2f2f2"/><stop offset="1" stop-color="#9a9da3"/>
    </radialGradient>
    <linearGradient id="blade" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#4a5060"/><stop offset="1" stop-color="#262a33"/>
    </linearGradient>
    <radialGradient id="bokeh" cx="0.5" cy="0.5" r="0.6">
      <stop offset="0" stop-color="#fff4d6"/><stop offset="0.45" stop-color="#ffc061"/><stop offset="1" stop-color="#f07a2a"/>
    </radialGradient>
  </defs>
  <circle cx="32" cy="32" r="{R_OUT}" fill="url(#barrel)"/>
  <circle cx="32" cy="32" r="{R_OUT - 3.2}" fill="#1b1e24"/>
  <!-- chromatic fringe on the glass rim: warm one side, cool the other -->
  <circle cx="31.2" cy="31.2" r="{R_GLASS + 1.3}" fill="none" stroke="#ff8a3d" stroke-width="1.6" opacity="0.95"/>
  <circle cx="32.8" cy="32.8" r="{R_GLASS + 1.3}" fill="none" stroke="#3fd0ff" stroke-width="1.6" opacity="0.95"/>
  <circle cx="32" cy="32" r="{R_GLASS + 0.3}" fill="#1b1e24"/>
  <circle cx="32" cy="32" r="{R_GLASS}" fill="url(#blade)"/>
  <g stroke="#11131a" stroke-width="1.7" stroke-linecap="round">
{blade_lines}
  </g>
  <path d="{hexpath}" fill="url(#bokeh)" stroke="#11131a" stroke-width="1.2" stroke-linejoin="round"/>
  <ellipse cx="25" cy="21" rx="5.5" ry="2.6" fill="#ffffff" opacity="0.18" transform="rotate(-35 25 21)"/>
</svg>
'''
open("characterlens_icon.svg", "w").write(svg)
for size in (64, 32, 512):
    subprocess.check_call(["rsvg-convert", "-w", str(size), "-h", str(size), "characterlens_icon.svg", "-o", "characterlens_icon_%d.png" % size])
print("ok")
