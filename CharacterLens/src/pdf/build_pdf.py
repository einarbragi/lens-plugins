import re, subprocess, markdown, html
SRC = "../CharacterLens_Guide.md"
md = open(SRC).read()
# title + intro go on the cover/contents pages
lines = md.splitlines()
assert lines[0].startswith("# ")
body = "\n".join(lines[1:])
intro, rest = body.split("\n---\n", 1)
rest = re.sub(r"\n---\n", "\n", rest)                 # sections already start on new pages


def fix_lists(text):
    """Python-Markdown wants a blank line before a list and 4-space nesting."""
    out, prev = [], ""
    item = re.compile(r"^(\s*)([-*]|\d+\.)\s")
    for line in text.splitlines():
        m = item.match(line)
        if m:
            ind = len(m.group(1))
            line = " " * (ind * 2) + line[ind:]          # 2-space nesting -> 4-space
            if prev.strip() and not item.match(prev) and not prev.startswith("    "):
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


rest = fix_lists(rest)
h2 = re.findall(r"^## (.+)$", rest, re.M)
md_conv = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
body_html = md_conv.convert(rest)
intro_html = markdown.markdown(intro.strip())
icon = open("../icon/flat_B.svg").read()
icon = re.sub(r'width="64" height="64"', 'width="44" height="44"', icon, count=1)
toc_ids = {t["name"]: t["id"] for t in md_conv.toc_tokens[0]["children"]} if md_conv.toc_tokens and md_conv.toc_tokens[0].get("level") == 1 else {t["name"]: t["id"] for t in md_conv.toc_tokens}
toc = "\n".join('<li><a href="#%s">%s</a></li>' % (toc_ids.get(html.escape(n), ""), html.escape(n)) for n in h2)

css = r"""
@page { size: A4; margin: 20mm 18mm 20mm 18mm;
  @bottom-left { content: "CharacterLens for Octane  \00B7  v0.8"; font: 8pt Inter; color: #8a8f99; }
  @bottom-right { content: counter(page); font: 8pt Inter; color: #8a8f99; } }
@page cover { margin: 0; @bottom-left { content: none; } @bottom-right { content: none; } }
html { font-family: Inter, "DejaVu Sans", sans-serif; font-size: 10.5pt; color: #1d2026; line-height: 1.5; }
body { margin: 0; }
.cover { page: cover; height: 297mm; width: 210mm; background: #1c1f25; color: #f4f4f4;
  display: flex; flex-direction: column; justify-content: center; padding: 0 24mm; box-sizing: border-box; page-break-after: always; }
.cover svg { margin-bottom: 14mm; }
.cover h1 { font-size: 34pt; font-weight: 700; letter-spacing: -0.5pt; margin: 0 0 4mm 0; line-height: 1.1; }
.cover .sub { font-size: 14pt; color: #c9ccd2; margin: 0 0 18mm 0; }
.cover .bar { width: 46mm; height: 2.2mm; background: linear-gradient(90deg, #ff8a2a 0 50%, #2ec7ff 50% 100%); margin-bottom: 8mm; }
.cover .meta { font-size: 10pt; color: #8a8f99; }
.front { page-break-after: always; }
.front h2 { border: none; }
.front .intro { font-size: 11.5pt; color: #2b2f36; margin-bottom: 10mm; }
.front ul.toc { list-style: none; padding-left: 0; font-size: 11.5pt; }
.front ul.toc li { margin: 0; padding: 2.4mm 0; border-bottom: 0.5pt solid #e1e4e9; }
.front a { color: #1d2026; text-decoration: none; }
h2 { font-size: 14pt; font-weight: 700; margin: 7mm 0 3mm 0; padding-bottom: 1.5mm; border-bottom: 1.2pt solid #ff8a2a; page-break-after: avoid; }
.head { display: flex; align-items: center; gap: 4mm; margin-bottom: 3mm; }
.head h1 { font-size: 20pt; margin: 0; line-height: 1.1; }
.head .meta { font-size: 9pt; color: #8a8f99; }
.intro { font-size: 11pt; color: #2b2f36; margin-bottom: 2mm; }
h3 { font-size: 12.5pt; font-weight: 600; margin: 6mm 0 2mm 0; color: #0f6f99; page-break-after: avoid; }
p { margin: 0 0 2.6mm 0; }
ul, ol { margin: 0 0 3mm 0; padding-left: 5.5mm; }
li { margin: 0.8mm 0; }
strong { font-weight: 600; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt; background: #f0f2f5; padding: 0.3mm 1mm; border-radius: 1mm; }
pre { background: #1c1f25; color: #e8e8e8; padding: 3mm 4mm; border-radius: 2mm; font-size: 8.4pt; line-height: 1.45; overflow-wrap: anywhere; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 3mm 0; font-size: 9pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { text-align: left; font-weight: 600; background: #eef1f5; border-bottom: 1pt solid #c9ced6; padding: 1.6mm 2mm; }
td { border-bottom: 0.5pt solid #e1e4e9; padding: 1.1mm 2mm; vertical-align: top; }
em { font-style: italic; color: #0f6f99; }
"""
doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>CharacterLens for Octane: guide</title><style>{css}</style></head><body>
<div class="head">{icon}<div><h1>CharacterLens for Octane</h1>
<div class="meta">Quick guide &nbsp;·&nbsp; v0.9 &nbsp;·&nbsp; Cinema 4D 2027 + Octane</div></div></div>
<div class="intro">{intro_html}</div>
{body_html}
</body></html>"""
open("guide.html", "w").write(doc)
subprocess.check_call(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                       "--print-to-pdf=CharacterLens_Guide.pdf", "file://" + __import__("os").path.abspath("guide.html")],
                      stderr=subprocess.DEVNULL)
print("ok")
