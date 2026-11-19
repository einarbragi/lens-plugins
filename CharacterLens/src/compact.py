"""Compact CharacterLens.osl for pasting: no comment lines, tables hold only non-default values."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import looks, build7
b5 = build7.b5
L, S = b5.LENS_FIELDS, b5.STYLE_FIELDS
LD = looks.LENS_DEFAULT; SD = looks.STYLE_DEFAULT

def lens_fn():
    sig = ", ".join(("output int " if f == "blades" else "output float ") + f for f in L)
    out = ["void lensData(int id, " + sig + ")", "{"]
    first = True
    for i in looks.LENSES:
        d = looks.lens(i)
        toks = ["%s=%s;" % (f, b5.lit(f, d[f], {"blades"})) for f in L if d[f] != LD[f]]
        out.append(" %s(id==%d){%s}" % ("if" if first else "else if", i, "".join(toks))); first = False
    return "\n".join(out + ["}"])

def style_fn():
    ints = looks.STYLE_INT
    sig = ", ".join("output %s %s" % ("color" if f == "tint" else ("int" if f in ints else "float"), b5.STYLE_OSL_NAMES.get(f, f)) for f in S)
    out = ["void styleData(int id, " + sig + ")", "{"]
    first = True
    for i in looks.STYLES:
        d = looks.style(i)
        toks = ["%s=%s;" % (b5.STYLE_OSL_NAMES.get(f, f), b5.lit(f, d[f], ints)) for f in S
                if (tuple(d[f]) if f == "tint" else d[f]) != (tuple(SD[f]) if f == "tint" else SD[f])]
        out.append(" %s(id==%d){%s}" % ("if" if first else "else if", i, "".join(toks))); first = False
    return "\n".join(out + ["}"])

src = open(os.path.join(HERE, "template.osl")).read()
src = src.replace("//@@LENSDATA@@", lens_fn()).replace("//@@STYLEDATA@@", style_fn())
src = src.replace("@@OPTIONS@@", build7.options()).replace("//@@LENSSTYLE@@", build7.gen_lensstyle())
src = src.replace("//@@ADVPINS@@", build7.gen_pins()).replace("//@@ADVAPPLY@@", build7.gen_apply())
out = []
for line in src.splitlines():
    st = line.strip()
    if not st or st.startswith("//"):
        if st.startswith("#") : out.append(line)
        continue
    if '"' not in line and "//" in line:
        line = line[:line.index("//")].rstrip()
    out.append(line.rstrip())
res = "// CharacterLens.osl v0.7 (compact)\n" + "\n".join(out) + "\n"
open(os.path.join(HERE, "CharacterLens_compact.osl"), "w").write(res)
print(len(res))
