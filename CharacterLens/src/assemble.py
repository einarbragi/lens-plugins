"""Assemble the v0.7 tag code and CharacterLens.pyp."""
import ast, base64, os, textwrap, zlib, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
subprocess.check_call([sys.executable, "-I", "build7.py"])
tables = open("tag_tables.py").read().strip()
gen = open("ps1_gen.py").read()
assert '"""' not in gen
tag = open("tag_template.py").read().replace("#@@TABLES@@", tables).replace("#@@PS1@@", gen)
ast.parse(tag)
assert "'''" not in tag
open("CharacterLens_Tag.py", "w").write(tag)

s = open("plugin_template.pyp").read()
a = s.index("# ---- CharacterLens tag UI builder")
b = s.index("# ------------------------------------------------------ 1. camera setup")
s = s[:a] + tables + "\n\n\n" + open("builder.py").read() + "\n\n" + s[b:]
s = s.replace('VERSION = "0.6"', 'VERSION = "0.8"').replace("v0.6  (single-file plugin)", "v0.8  (single-file plugin)")
s = s.replace("    style, Compile / Reset / PS1 buttons)", "    style, Advanced per-lens values, saved lenses, Compile / Reset / PS1 buttons)")
open("plugin_template_v7.pyp", "w").write(s)


def pack(x):
    return "\n".join(textwrap.wrap(base64.b64encode(zlib.compress(x.encode("utf-8"), 9)).decode(), 100))


t = s
icon = base64.b64encode(open("icon/characterlens_icon_64.png", "rb").read()).decode()
t = t.replace("@@ICON@@", "\n".join(textwrap.wrap(icon, 100)))
for k, v in (("@@OSL@@", open("CharacterLens.osl").read()), ("@@TAG@@", tag),
             ("@@POST@@", open("characterlens_post.py").read()), ("@@PS1@@", gen)):
    assert k in t, k
    t = t.replace(k, pack(v))
ast.parse(t)
os.makedirs("dist", exist_ok=True)
open("dist/CharacterLens.pyp", "w").write(t)
print("tag", len(tag), "plugin", len(t))
