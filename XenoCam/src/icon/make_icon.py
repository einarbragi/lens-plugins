import subprocess
ORANGE, CYAN, WHITE = "#ff8a2a", "#2ec7ff", "#f4f4f4"
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<circle cx="32" cy="32" r="26.5" fill="none" stroke="{WHITE}" stroke-width="5"/>
<rect x="3" y="30.6" width="58" height="2.8" rx="1.4" fill="{CYAN}"/>
<ellipse cx="32" cy="32" rx="13.5" ry="9" fill="{ORANGE}"/>
</svg>'''
open("xenocam_icon.svg", "w").write(svg)
for s in (64, 32, 400):
    subprocess.check_call(["rsvg-convert", "-w", str(s), "-h", str(s), "xenocam_icon.svg", "-o", "xenocam_icon_%d.png" % s])
