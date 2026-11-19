import ast, base64, os, textwrap, zlib
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
def pack(x):
    return "\n".join(textwrap.wrap(base64.b64encode(zlib.compress(x.encode("utf-8"), 9)).decode(), 100))
osl = open("XenoCam.osl").read(); tag = open("tag_template.py").read()
ast.parse(tag)
t = open("plugin_template.pyp").read()
t = t.replace("@@OSL@@", pack(osl)).replace("@@TAG@@", pack(tag))
t = t.replace("@@ICON@@", "\n".join(textwrap.wrap(base64.b64encode(open("icon/xenocam_icon_64.png", "rb").read()).decode(), 100)))
assert "@@" not in t
ast.parse(t)
os.makedirs("dist", exist_ok=True)
open("dist/XenoCam.pyp", "w").write(t)
print("XenoCam.pyp", len(t), "chars; shader", len(osl), "tag", len(tag))
