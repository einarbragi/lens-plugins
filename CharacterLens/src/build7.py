"""Build CharacterLens.osl (v0.7) and the tag tables from looks.py + adv_spec.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import looks, adv_spec
sys.path.insert(1, os.path.join(HERE, "..", "v5"))
import build as b5          # gen_lensdata / gen_styledata / options / tag_table (reads looks from HERE first)
assert b5.looks is looks
for _f in ("zoom", "orthoWidth", "revStrength"):
    if _f not in b5.STYLE_FIELDS:
        b5.STYLE_FIELDS.append(_f)


def value(preset_id, key):
    """Effective value the shader would use for this preset (before the Look sliders)."""
    if preset_id >= 100:
        st = looks.style(preset_id)
        ln = looks.lens(st["baseLens"])
    else:
        st = dict(looks.STYLE_DEFAULT)
        st.update(getattr(looks, "LENS_STYLE", {}).get(preset_id, {}))
        ln = looks.lens(preset_id)
    if key.startswith("s:"):
        return st[key[2:]]
    if key.startswith("tint:"):
        return tuple(st["tint"])[int(key[5:])]
    if key in looks.LENS_DEFAULT:
        return ln[key]
    return st[key]


def defaults():
    """Shader defaults for the A_ pins = values with no lens/style table (lens 1 + no style)."""
    out = {}
    for e in adv_spec.ADV:
        k = e[0]
        if k.startswith("s:"):
            out[k] = looks.STYLE_DEFAULT[k[2:]]
        elif k.startswith("tint:"):
            out[k] = 1.0
        elif k in looks.LENS_DEFAULT:
            out[k] = looks.LENS_DEFAULT[k]
        else:
            out[k] = looks.STYLE_DEFAULT[k]
    return out


def osl_lit(e, v):
    name = e[0].split(":")[-1] if not e[0].startswith("tint") else "tint"
    if e[1][2:] in adv_spec.OSL_INT:
        return str(int(v))
    return repr(float(v))


def gen_pins():
    d = defaults()
    lines = []
    for e in adv_spec.ADV:
        typ = "int  " if e[1][2:] in adv_spec.OSL_INT else "float"
        lines.append('    %s %s = %s [[ string page = "Advanced" ]],' % (typ, e[1], osl_lit(e, d[e[0]])))
    return "\n".join(lines)


def gen_apply():
    lines, cur = [], "       "
    toks = []
    for e in adv_spec.ADV:
        k = e[0]
        if k.startswith("tint:"):
            continue
        var = {"s:haze": "sHaze", "s:hazeSpread": "sHazeSpread"}.get(k, k)
        toks.append("%s = %s;" % (var, e[1]))
    toks.append("tint = color(A_tintR, A_tintG, A_tintB);")
    for t in toks:
        if len(cur) + len(t) > 100:
            lines.append(cur); cur = "       "
        cur += " " + t
    lines.append(cur)
    return "\n".join(lines)


def gen_lensstyle():
    ls = getattr(looks, "LENS_STYLE", {})
    out = ["// Real lenses that use a non-standard projection (generated from looks.py).",
           "void lensStyle(int id, output int proj, output int noDOF)", "{"]
    first = True
    for i, d in ls.items():
        out.append("    %s (id == %d) { proj = %d; noDOF = %d; }   // %s" % ("if" if first else "else if", i, d["proj"],
                                                                         d.get("noDOF", 0), looks.LENSES[i][0]))
        first = False
    out.append("}")
    return "\n".join(out)


def options():
    """Mapper options: real lenses in LENS_ORDER, then the styles."""
    order = getattr(looks, "LENS_ORDER", list(looks.LENSES))
    items = [(i, looks.LENSES[i][0]) for i in order] + [(i, n) for i, (n, _) in looks.STYLES.items()]
    for _, n in items:
        assert ":" not in n and "|" not in n, n
    return "|".join("%s:%d" % (n, i) for i, n in items)


def tag_tables():
    d = defaults()
    diff = {}
    ids = list(looks.LENSES) + list(looks.STYLES)
    for i in ids:
        dd = {}
        for e in adv_spec.ADV:
            v = value(i, e[0])
            if isinstance(v, bool):
                v = int(v)
            if abs(float(v) - float(d[e[0]])) > 1e-9:
                dd[e[0]] = v
        diff[i] = dd
    spec = "ADV = [\n" + "\n".join("    %r," % (e,) for e in adv_spec.ADV) + "\n]"
    dflt = "ADV_DEFAULT = %r" % ({k: v for k, v in d.items()},)
    rows = "\n".join("    %d: %r," % (i, diff[i]) for i in ids)
    groups = "ADV_GROUPS = %r" % (adv_spec.LENS_GROUPS + adv_spec.STYLE_GROUPS,)
    order = "LENS_ORDER = %r" % (list(getattr(looks, "LENS_ORDER", list(looks.LENSES))) + list(looks.STYLES),)
    return "\n\n".join([b5.tag_table(), order, spec, groups, dflt, "PRESET_DIFF = {\n" + rows + "\n}"]) + "\n"


if __name__ == "__main__":
    src = open(os.path.join(HERE, "template.osl")).read()
    src = src.replace("//@@LENSDATA@@", b5.gen_lensdata()).replace("//@@STYLEDATA@@", b5.gen_styledata())
    src = src.replace("@@OPTIONS@@", options()).replace("//@@LENSSTYLE@@", gen_lensstyle())
    src = src.replace("//@@ADVPINS@@", gen_pins()).replace("//@@ADVAPPLY@@", gen_apply())
    assert "@@" not in src
    open(os.path.join(HERE, "CharacterLens.osl"), "w").write(src)
    open(os.path.join(HERE, "tag_tables.py"), "w").write(tag_tables())
    print("ok", len(src), "chars;", len(adv_spec.ADV), "advanced inputs")
