# ---- CharacterLens tag UI builder (shared by the plugin and the test script) ----
# Needs LENSES, ADV, ADV_GROUPS, ADV_DEFAULT from the tag tables.
import json as _cl_json

CL_SAVED_BASE = 1000


def _cl_norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _cl_pin_values(otag):
    """Current values of the shader's main pins, keyed by variable name."""
    names = {"lensmodel": "LensModel", "fstop": "FStop", "focusdistance": "FocusDistance",
             "character": "Character", "bokeh": "Bokeh", "swirlamount": "SwirlAmount",
             "softness": "Softness", "fringing": "Fringing", "distortion": "Distortion",
             "vignette": "Vignette", "pixellines": "PixelLines", "wobble": "Wobble",
             "eyedistance": "EyeDistance"}
    out, inside = {}, False
    for bc, pid, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        n = _cl_norm(bc[c4d.DESC_NAME] or "")
        if n == "lensmodel":
            inside = True
        if inside and n in names and names[n] not in out:
            try:
                out[names[n]] = otag.GetParameter(pid, c4d.DESCFLAGS_GET_NONE)
            except Exception:
                pass
        if inside and n == "frame":
            break
    return out


def _cl_add(tag, name, dtype, parent=None, default=None, mn=None, mx=None, smin=None, smax=None,
            step=None, gui=None, cycle=None, hide=False, columns=None, open_=True):
    bc = c4d.GetCustomDataTypeDefault(dtype)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if parent == "root":
        bc[c4d.DESC_PARENTGROUP] = c4d.DescID(0)      # its own tab in the Attribute Manager
    elif parent is not None:
        bc[c4d.DESC_PARENTGROUP] = parent
    if columns is not None:
        bc[c4d.DESC_COLUMNS] = columns
    if mn is not None:
        bc[c4d.DESC_MIN] = mn
    if mx is not None:
        bc[c4d.DESC_MAX] = mx
    if smin is not None:
        bc[c4d.DESC_MINSLIDER] = smin
    if smax is not None:
        bc[c4d.DESC_MAXSLIDER] = smax
    if step is not None:
        bc[c4d.DESC_STEP] = step
    if gui is not None:
        bc[c4d.DESC_CUSTOMGUI] = gui
    if cycle is not None:
        cyc = c4d.BaseContainer()
        for k, v in cycle:
            cyc.SetString(k, v)
        bc.SetContainer(c4d.DESC_CYCLE, cyc)
    if hide:
        bc[c4d.DESC_HIDE] = True
    if dtype == c4d.DTYPE_GROUP:
        bc[c4d.DESC_DEFAULT] = bool(open_)     # unfolded or folded
    did = tag.AddUserData(bc)
    if default is not None:
        try:
            tag[did] = default
        except Exception:
            pass
    return did


def _cl_old_values(ptag):
    """Every value on the tag's existing User Data, by name (groups/buttons skipped)."""
    out = {}
    for did, bc in ptag.GetUserDataContainer():
        try:
            dt = did[did.GetDepth() - 1].dtype
        except Exception:
            dt = None
        if dt in (c4d.DTYPE_GROUP, c4d.DTYPE_BUTTON, getattr(c4d, "DTYPE_SEPARATOR", -999)):
            continue
        try:
            out[bc[c4d.DESC_NAME]] = ptag[did]
        except Exception:
            pass
    return out


def build_tag_ui(ptag, otag, lenses, old=None):
    """(Re)build the CharacterLens tag's controls. Keeps every existing value
    (Focus Object, saved lenses, Advanced edits) and takes the rest from the
    shader's current pins. `old` carries values over from a replaced tag."""
    if old is None:
        old = _cl_old_values(ptag)
    for did, _bc in list(ptag.GetUserDataContainer()):
        ptag.RemoveUserData(did)
    # wipe the stored values too: Cinema 4D keeps them by slot number, so a
    # reordered control would otherwise inherit an old value of the wrong type
    try:
        ptag.GetDataInstance().RemoveData(c4d.ID_USERDATA)
    except Exception:
        pass

    try:
        saved = {int(k): s for k, s in _cl_json.loads(old.get("_saved presets") or "{}").items()}
    except Exception:
        saved = {}

    v = _cl_pin_values(otag) if otag is not None else {}
    lens = int(old.get("Lens", v.get("LensModel", 6)) or 6)
    if (lens >= CL_SAVED_BASE and lens not in saved) or (lens < CL_SAVED_BASE and lens not in lenses):
        lens = int(v.get("LensModel", 6) or 6)
    if lens < CL_SAVED_BASE and lens not in lenses:
        lens = 6                                       # a removed preset -> Cooke Panchro
    base = saved[lens]["base"] if lens in saved else lens
    g = lambda k, d: v.get(k) if v.get(k) is not None else d
    R, L, B = c4d.DTYPE_REAL, c4d.DTYPE_LONG, c4d.DTYPE_BOOL
    SL, LSL = c4d.CUSTOMGUI_REALSLIDER, c4d.CUSTOMGUI_LONGSLIDER
    BTN = c4d.CUSTOMGUI_BUTTON

    items = [(k, lenses[k][0]) for k in LENS_ORDER if k in lenses]
    items += [(k, "[Saved] " + s["name"]) for k, s in sorted(saved.items())]

    top = _cl_add(ptag, "Character Lens", c4d.DTYPE_GROUP, "root", columns=1)
    gc = _cl_add(ptag, "Colour correction", c4d.DTYPE_GROUP, top, columns=1)
    _cl_add(ptag, "Use colour correction", B, gc, False)
    _cl_add(ptag, "Exposure (stops)", R, gc, 0.0, mn=-10.0, mx=10.0, smin=-3.0, smax=3.0, step=0.05, gui=SL)
    _cl_add(ptag, "Saturation", R, gc, 1.0, mn=0.0, mx=4.0, smin=0.0, smax=2.0, step=0.01, gui=SL)
    _cl_add(ptag, "Gamma", R, gc, 1.0, mn=0.1, mx=5.0, smin=0.5, smax=2.5, step=0.01, gui=SL)
    _cl_add(ptag, "About colour correction", c4d.DTYPE_STRING, gc,
            "Uses this camera's Octane imager (Imager tab), which then replaces the global one",
            gui=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))

    gl = _cl_add(ptag, "Lens & focus", c4d.DTYPE_GROUP, top, columns=1)
    _cl_add(ptag, "Lens", L, gl, lens, gui=c4d.CUSTOMGUI_CYCLE, cycle=items)
    _cl_add(ptag, "F-stop", R, gl, float(g("FStop", 1.4)), mn=0.02, mx=256.0, smin=0.1, smax=22.0, step=0.01, gui=SL)
    _cl_add(ptag, "Full character at", c4d.DTYPE_STRING, gl, "", gui=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))
    _cl_add(ptag, "Focus Object", c4d.DTYPE_BASELISTLINK, gl, None)
    _cl_add(ptag, "Focus distance (cm)", R, gl, float(g("FocusDistance", 200.0)), mn=1.0, mx=1000000.0, step=1.0)

    gk = _cl_add(ptag, "Look", c4d.DTYPE_GROUP, top, columns=1)
    for name, var, mx, smax in (("Character", "Character", 3.0, 2.0),
                                ("Bokeh", "Bokeh", 3.0, 2.0), ("Swirl", "SwirlAmount", 5.0, 3.0),
                                ("Softness / glow", "Softness", 5.0, 3.0), ("Fringing", "Fringing", 10.0, 3.0),
                                ("Distortion", "Distortion", 10.0, 5.0), ("Vignette", "Vignette", 5.0, 3.0)):
        _cl_add(ptag, name, R, gk, float(g(var, 1.0)), mn=0.0, mx=mx, smin=0.0, smax=smax, step=0.01, gui=SL)
    _cl_add(ptag, "Reset look", c4d.DTYPE_BUTTON, gk, gui=BTN)

    is_style = base >= 100
    has_film = base in (115, 111, 114, 109, 108, 106, 14)    # styles with a live film look (see STYLE_LOOK)
    gs = _cl_add(ptag, "Style", c4d.DTYPE_GROUP, top, columns=1, hide=not (is_style or has_film))
    _cl_add(ptag, "Film look (grade, bloom, grain)", R, gs, 1.0, mn=0.0, mx=2.0, smin=0.0, smax=2.0,
            step=0.01, gui=SL, hide=not has_film)
    _cl_add(ptag, "Pixel lines (0 = style default)", L, gs, int(g("PixelLines", 0)), mn=0, mx=2160,
            smin=0, smax=720, hide=not is_style, gui=LSL)
    _cl_add(ptag, "Wobble / gate weave", R, gs, float(g("Wobble", 1.0)), mn=0.0, mx=3.0, smin=0.0, smax=2.0,
            step=0.01, gui=SL, hide=not is_style)
    _cl_add(ptag, "Anaglyph eye distance (cm)", R, gs, float(g("EyeDistance", 6.5)), mn=0.0, mx=50.0, smin=0.0,
            smax=15.0, step=0.1, gui=SL, hide=not is_style)

    ga = _cl_add(ptag, "Advanced", c4d.DTYPE_GROUP, top, columns=1, open_=False)
    _cl_add(ptag, "Use preset values", c4d.DTYPE_BUTTON, ga, gui=BTN)
    _cl_add(ptag, "Save as preset...", c4d.DTYPE_BUTTON, ga, gui=BTN)
    _cl_add(ptag, "Delete saved preset", c4d.DTYPE_BUTTON, ga, gui=BTN)
    sub = {}
    for gname in ADV_GROUPS:
        sub[gname] = _cl_add(ptag, gname, c4d.DTYPE_GROUP, ga, columns=1, open_=False)
    for key, _pin, label, kind, mn, mx, smin, smax, step, gname, cyc in ADV:
        d = ADV_DEFAULT[key]
        parent = sub[gname]
        if kind == "bool":
            _cl_add(ptag, label, B, parent, bool(d))
        elif kind == "cycle":
            _cl_add(ptag, label, L, parent, int(d), gui=c4d.CUSTOMGUI_CYCLE, cycle=cyc)
        elif kind == "int":
            _cl_add(ptag, label, L, parent, int(d), mn=int(mn), mx=int(mx), smin=int(smin), smax=int(smax),
                    step=int(step), gui=LSL)
        else:
            _cl_add(ptag, label, R, parent, float(d), mn=mn, mx=mx, smin=smin, smax=smax, step=step, gui=SL)

    gt = _cl_add(ptag, "Tools", c4d.DTYPE_GROUP, top, columns=1)
    _cl_add(ptag, "Compile shader", c4d.DTYPE_BUTTON, gt, gui=BTN)
    _cl_add(ptag, "Add PS1 snap to selected", c4d.DTYPE_BUTTON, gt, gui=BTN)
    _cl_add(ptag, "Copy shader code", c4d.DTYPE_BUTTON, gt, gui=BTN)
    _cl_add(ptag, "Save shader to a folder...", c4d.DTYPE_BUTTON, gt, gui=BTN)

    _cl_add(ptag, "_advanced from", L, top, -1, hide=True)        # -1 = fill Advanced from the preset
    _cl_add(ptag, "_saved presets", c4d.DTYPE_STRING, top, _cl_json.dumps({str(k): s for k, s in saved.items()}),
            hide=True)
    _cl_add(ptag, "_imager on", B, top, False, hide=True)
    _cl_add(ptag, "_imager backup", c4d.DTYPE_STRING, top, "", hide=True)

    # put back everything the tag already had (v0.6+ values, Advanced edits)
    keep = dict(old)
    keep.pop("_last lens", None)
    keep.pop("Full character at", None)
    keep.pop("About colour correction", None)
    dof = old.get("Depth of field (1 = real)")
    keep.pop("Depth of field (1 = real)", None)
    if dof is not None and abs(float(dof) - 1.0) > 1e-4 and float(dof) > 0 and "F-stop" in old:
        # v0.8 had a separate Depth of field multiplier: fold it into the F-stop
        mf = float(old.get("Widest aperture (f-number)") or 1.4)
        keep["F-stop"] = max(max(float(old["F-stop"]), mf) / float(dof), 0.02)
    if "Swirl strength" not in old and "Swirl" in old:
        # v0.7 had two controls called "Swirl"; the stored one is the Advanced value
        keep["Swirl strength"] = old["Swirl"]
        keep["Swirl"] = 1.0
    keep.pop("_saved presets", None)
    keep["Lens"] = lens
    # v0.9 halved the presets' natural vignetting: update it unless it was edited
    try:
        nv_new = float(PRESET_DIFF.get(lens, {}).get("natVig", ADV_DEFAULT["natVig"]))
        nv_old = keep.get("Natural vignetting")
        if nv_old is not None and abs(float(nv_old) - 2.0 * nv_new) < 1e-3:
            keep["Natural vignetting"] = nv_new
    except Exception:
        pass
    for did, bc in ptag.GetUserDataContainer():
        name = bc[c4d.DESC_NAME]
        if name in keep and keep[name] is not None:
            try:
                ptag[did] = keep[name]
            except Exception:
                pass
