"""Build CharacterLens.osl + the C4D tag lens table from looks.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import looks

HERE = os.path.dirname(os.path.abspath(__file__))
LENS_FIELDS = ["blades", "roundness", "rimBias", "onion", "catEye", "rimRadius", "swirl", "sa", "coma",
               "astig", "fc", "k1", "k2", "latCA", "longCA", "secCA", "sphCA", "natVig", "castAmt",
               "warmth", "breathing", "maxF", "squeeze", "haze", "hazeSpread"]
STYLE_FIELDS = ["proj", "fov", "circle", "pixLines", "pixAspect", "pixSoft", "scan", "mask", "curve", "conv",
                "chromaSmear", "wobble", "weave", "gate", "tint", "tube", "copies", "prismOffset", "kaleido",
                "cells", "glass", "glassAmt", "stereo", "tilt", "port", "apBoost", "lensAmt", "noDOF",
                "extraVig", "extraK1", "extraFC", "haze", "hazeSpread", "baseLens"]
STYLE_OSL_NAMES = {"haze": "sHaze", "hazeSpread": "sHazeSpread"}


def fnum(v):
    s = repr(float(v))
    return s


def lit(name, v, ints):
    if name == "tint":
        return "color(%s, %s, %s)" % tuple(fnum(x) for x in v)
    if name in ints:
        return str(int(v))
    return fnum(v)


def gen_lensdata():
    sig = ",\n    ".join(("output int   " if f == "blades" else "output float ") + f for f in LENS_FIELDS)
    out = ["// Lens library (generated from looks.py).", "void lensData(int id,\n    " + sig + ")", "{"]
    first = True
    for i, (name, _) in looks.LENSES.items():
        d = looks.lens(i)
        body = " ".join("%s = %s;" % (f, lit(f, d[f], {"blades"})) for f in LENS_FIELDS)
        out.append("    %s (id == %d) {   // %s" % ("if" if first else "else if", i, name))
        # wrap
        parts, line = [], "       "
        for tok in body.split("; "):
            tok = tok.rstrip(";") + ";"
            if len(line) + len(tok) > 110:
                parts.append(line); line = "       "
            line += " " + tok
        parts.append(line)
        out += parts + ["    }"]
        first = False
    out.append("}")
    return "\n".join(out)


def gen_styledata():
    ints = looks.STYLE_INT
    sig = []
    for f in STYLE_FIELDS:
        typ = "color" if f == "tint" else ("int  " if f in ints else "float")
        sig.append("output %s %s" % (typ, STYLE_OSL_NAMES.get(f, f)))
    out = ["// Stylized cameras (generated from looks.py).",
           "void styleData(int id,\n    " + ",\n    ".join(sig) + ")", "{"]
    first = True
    for i, (name, _) in looks.STYLES.items():
        d = looks.style(i)
        toks = ["%s = %s;" % (STYLE_OSL_NAMES.get(f, f), lit(f, d[f], ints)) for f in STYLE_FIELDS]
        out.append("    %s (id == %d) {   // %s" % ("if" if first else "else if", i, name))
        line = "       "
        for tok in toks:
            if len(line) + len(tok) > 110:
                out.append(line); line = "       "
            line += " " + tok
        out.append(line)
        out.append("    }")
        first = False
    out.append("}")
    return "\n".join(out)


def options():
    items = [(i, n) for i, (n, _) in looks.LENSES.items()] + [(i, n) for i, (n, _) in looks.STYLES.items()]
    for _, n in items:
        assert ":" not in n and "|" not in n, n
    return "|".join("%s:%d" % (n, i) for i, n in items)


def tag_table():
    rows = []
    for i, (n, _) in looks.LENSES.items():
        d = looks.lens(i)
        rows.append("    %d: (%r, %r, %r)," % (i, n, d["focal"], d["maxF"]))
    for i, (n, _) in looks.STYLES.items():
        s = looks.style(i)
        fstop = s["fstop"] if s["fstop"] is not None else looks.lens(s["baseLens"])["maxF"]
        rows.append("    %d: (%r, %r, %r)," % (i, n, s["focal"], fstop))
    return "LENSES = {\n" + "\n".join(rows) + "\n}"


if __name__ == "__main__":
    src = open(os.path.join(HERE, "template.osl")).read()
    src = src.replace("//@@LENSDATA@@", gen_lensdata()).replace("//@@STYLEDATA@@", gen_styledata())
    src = src.replace("@@OPTIONS@@", options())
    open(os.path.join(HERE, "CharacterLens.osl"), "w").write(src)
    open(os.path.join(HERE, "lens_table.py"), "w").write(tag_table() + "\n")
    print("ok", len(src), "chars;", len(looks.LENSES), "lenses,", len(looks.STYLES), "styles")
