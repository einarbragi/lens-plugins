"""CharacterLens tag  -  v0.8
All CharacterLens controls live on this tag (User Data). The tag writes them
into the CharacterLens OSL shader on the Octane Camera tag, so the shader's
own pins are internal - change things here.

* Lens: picking a lens sets every value in the Advanced group. Focal length
  and F-stop stay as you set them; "Full character at" shows the lens's
  widest aperture (stopping down past it cleans the look up, like real glass).
* Focus Object: any object; empty = the camera's own Focus Object, and if
  neither is set, Focus distance is used as typed.
* Look sliders scale the Advanced values (1 = as set there).
* Advanced: every per-lens and per-style value. Edit any of them; "Use preset
  values" puts them back, "Save as preset" adds the current setup to the Lens
  list (stored on this tag, so it travels with the camera).
"""
import c4d
import json

#@@TABLES@@

# tag control name -> shader pin (variable name)
PIN_FOR = {
    "F-stop": "FStop", "Focus distance (cm)": "FocusDistance", "Depth of field (1 = real)": "DepthOfField",
    "Character": "Character", "Bokeh": "Bokeh", "Swirl": "SwirlAmount", "Softness / glow": "Softness",
    "Fringing": "Fringing", "Distortion": "Distortion", "Vignette": "Vignette",
    "Pixel lines (0 = style default)": "PixelLines", "Wobble / gate weave": "Wobble",
    "Anaglyph eye distance (cm)": "EyeDistance",
}
# shader pin labels, so pins are found whether C4D shows variable names or labels
PIN_LABELS = {
    "LensModel": "Lens", "FStop": "F-stop", "FocusDistance": "Focus distance (cm)",
    "DepthOfField": "Depth of field (1 = real)",
    "Character": "Character", "Bokeh": "Bokeh", "SwirlAmount": "Swirl", "Softness": "Softness / glow",
    "Fringing": "Fringing", "Distortion": "Distortion", "Vignette": "Vignette",
    "PixelLines": "Pixel lines (0 = style default)", "Wobble": "Wobble / gate weave",
    "EyeDistance": "Anaglyph eye distance (cm)", "FocalLength": "Focal length (mm)",
    "SensorWidth": "Sensor width (mm)", "Frame": "Frame", "Custom": "Use Advanced values",
}
for _e in ADV:
    PIN_LABELS[_e[1]] = _e[1]
FIRST, LAST = "LensModel", ADV[-1][1]
LOOK = ["Character", "Depth of field (1 = real)", "Bokeh", "Swirl", "Softness / glow", "Fringing", "Distortion",
        "Vignette"]
# colour correction drives the Octane camera tag's own imager
CC_USE, CC_OWNER = "Use colour correction", "_imager on"
CC_MAP = (("Exposure (stops)", "Exposure", lambda v: 2.0 ** float(v)),
          ("Saturation", "Saturation", float), ("Gamma", "Gamma", float))
STYLE_ONLY = ["Pixel lines (0 = style default)", "Wobble / gate weave", "Anaglyph eye distance (cm)"]
BTN_COMPILE, BTN_RESET, BTN_PS1 = "Compile shader", "Reset look", "Add PS1 snap to selected"
BTN_PRESET, BTN_SAVE, BTN_DELETE = "Use preset values", "Save as preset...", "Delete saved preset"
ADV_UD, SAVED_UD, NOTE_UD = "_advanced from", "_saved presets", "Full character at"
MAXF_UD, NODOF_UD = "Widest aperture (f-number)", "No depth of field"
SAVED_BASE = 1000

PS1_CODE = r"""#@@PS1@@"""

_cache = {}


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _pins(otag):
    """DescIDs of the shader's own pins (the block from LensModel to the last
    Advanced pin). Matches the exact variable names first; labels as fallback."""
    entries = [(_norm(bc[c4d.DESC_NAME] or ""), pid) for bc, pid, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE)]
    for use_labels in (False, True):
        keys = {v: ({_norm(v), _norm(l)} if use_labels else {_norm(v)}) for v, l in PIN_LABELS.items()}
        lookup = {}
        for var, ks in keys.items():
            for k in ks:
                lookup.setdefault(k, var)
        out, inside = {}, False
        for n, pid in entries:
            if not n:
                continue
            if not inside and n in keys[FIRST]:
                inside = True
            if inside:
                var = lookup.get(n)
                if var is not None and var not in out:
                    out[var] = pid
                if n in keys[LAST]:
                    break
        if FIRST in out and len(out) >= 8:
            return out
    return {}


def _find_osl_tag(cam):
    hit = _cache.get(id(cam))
    if hit and hit[0].IsAlive() and hit[0].GetObject() == cam and hit[1]:
        return hit
    for t in cam.GetTags():
        if t.GetType() == c4d.Tpython:
            continue
        pins = _pins(t)
        if FIRST in pins:
            _cache[id(cam)] = (t, pins)
            return t, pins
    return None, None


def _set(otag, pins, var, value):
    pid = pins.get(var)
    if pid is None or value is None:
        return
    cur = otag.GetParameter(pid, c4d.DESCFLAGS_GET_NONE)
    try:
        if abs(float(cur) - float(value)) < 1e-6:
            return
    except (TypeError, ValueError):
        pass
    if isinstance(cur, bool):
        value = bool(value)
    elif isinstance(cur, int):
        value = int(round(float(value)))
    else:
        value = float(value)
    otag.SetParameter(pid, value, c4d.DESCFLAGS_SET_NONE)


def _uds():
    return {bc[c4d.DESC_NAME]: did for did, bc in op.GetUserDataContainer()}


def _cam_focus_object(cam):
    for attr in ("CAMERAOBJECT_FOCUSOBJECT", "CAMERAOBJECT_TARGETOBJECT"):
        pid = getattr(c4d, attr, None)
        if pid is None:
            continue
        try:
            obj = cam[pid]
        except Exception:
            obj = None
        if isinstance(obj, c4d.BaseObject):
            return obj
    return None


# ------------------------------------------------------------- presets
def _saved(ud=None):
    ud = ud or _uds()
    if SAVED_UD not in ud:
        return {}
    try:
        return {int(k): v for k, v in json.loads(op[ud[SAVED_UD]] or "{}").items()}
    except Exception:
        return {}


def _store_saved(saved, ud=None):
    ud = ud or _uds()
    if SAVED_UD in ud:
        op[ud[SAVED_UD]] = json.dumps({str(k): v for k, v in saved.items()})


def _lens_info(lens, saved=None):
    """(name, focal, f-stop, built-in id the shader uses) for a built-in or saved lens."""
    if lens >= SAVED_BASE:
        s = (saved if saved is not None else _saved()).get(lens)
        if s:
            return s["name"], s.get("focal"), s.get("fstop"), s["base"]
        return None
    if lens in LENSES:
        n, f, fs = LENSES[lens]
        return n, f, fs, lens
    return None


def _preset_values(lens, saved=None):
    vals = dict(ADV_DEFAULT)
    if lens >= SAVED_BASE:
        s = (saved if saved is not None else _saved()).get(lens)
        if s:
            vals.update(s.get("values", {}))
    else:
        vals.update(PRESET_DIFF.get(lens, {}))
    return vals


def _ud_value(kind, v):
    if kind == "bool":
        return bool(v)
    if kind in ("int", "cycle"):
        return int(round(float(v)))
    return float(v)


def _fill_adv(lens, ud=None):
    ud = ud or _uds()
    vals = _preset_values(lens)
    for e in ADV:
        key, label, kind = e[0], e[2], e[3]
        if label in ud:
            op[ud[label]] = _ud_value(kind, vals.get(key, ADV_DEFAULT[key]))
    if ADV_UD in ud:
        op[ud[ADV_UD]] = lens


def _cycle_items(saved):
    items = [(k, LENSES[k][0]) for k in LENS_ORDER if k in LENSES]
    items += [(k, "[Saved] " + s["name"]) for k, s in sorted(saved.items())]
    return items


def _refresh_cycle(saved):
    for did, bc in op.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Lens":
            cyc = c4d.BaseContainer()
            for k, n in _cycle_items(saved):
                cyc.SetString(k, n)
            bc.SetContainer(c4d.DESC_CYCLE, cyc)
            op.SetUserDataContainer(did, bc)
            return


def _fnum(x):
    return ("%.1f" % x).rstrip("0").rstrip(".") if x < 10 else "%d" % round(x)


def _update_aperture_note(ud):
    if NOTE_UD not in ud:
        return
    if NODOF_UD in ud and op[ud[NODOF_UD]]:
        text = "No depth of field on this camera (F-stop does nothing)"
    elif MAXF_UD in ud:
        maxf = float(op[ud[MAXF_UD]])
        fs = float(op[ud["F-stop"]]) if "F-stop" in ud else maxf
        if fs < maxf - 1e-3:
            text = "f/%s - this lens opens no wider, so f/%s acts as f/%s" % (_fnum(maxf), _fnum(fs), _fnum(maxf))
        elif fs > maxf * 1.05:
            text = "f/%s - you're at f/%s, so the look is cleaner than wide open" % (_fnum(maxf), _fnum(fs))
        else:
            text = "f/%s - you're wide open: full character" % _fnum(maxf)
    else:
        return
    if op[ud[NOTE_UD]] != text:
        op[ud[NOTE_UD]] = text


def _imager_ids(otag):
    """DescIDs of the Octane camera tag's imager settings, by name."""
    hit = _cache.get(("imager", id(otag)))
    if hit:
        return hit
    want = {"Enable Imager"} | {m[1] for m in CC_MAP}
    out = {}
    for bc, pid, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        n = bc[c4d.DESC_NAME]
        if n in want and n not in out:
            out[n] = pid
    _cache[("imager", id(otag))] = out
    return out


def _colour_correction(otag, ud):
    if CC_USE not in ud:
        return
    ids = _imager_ids(otag)
    if "Enable Imager" not in ids:
        return
    on = bool(op[ud[CC_USE]])
    owner = bool(op[ud[CC_OWNER]]) if CC_OWNER in ud else False
    if on:
        _set(otag, ids, "Enable Imager", 1)
        if CC_OWNER in ud and not owner:
            op[ud[CC_OWNER]] = True
        for ud_name, oct_name, conv in CC_MAP:
            if ud_name in ud and oct_name in ids:
                _set(otag, ids, oct_name, conv(op[ud[ud_name]]))
    elif owner:
        # we switched the camera imager on, so switch it back off
        _set(otag, ids, "Enable Imager", 0)
        op[ud[CC_OWNER]] = False


# ----------------------------------------------------------------- main
def main():
    cam = op.GetObject()
    if cam is None:
        return
    otag, pins = _find_osl_tag(cam)
    if otag is None:
        return
    ud = _uds()
    if "Lens" not in ud:
        return
    lens = op[ud["Lens"]]
    saved = _saved(ud) if lens >= SAVED_BASE else {}
    info = _lens_info(lens, saved)

    # 1. lens changed -> its Advanced values (focal length and F-stop stay yours)
    if ADV_UD in ud and op[ud[ADV_UD]] != lens:
        _fill_adv(lens, ud)
    _update_aperture_note(ud)

    # 2. focus object -> focus distance (cm, along the view axis)
    target = op[ud["Focus Object"]] if "Focus Object" in ud else None
    if target is None:
        target = _cam_focus_object(cam)
    if isinstance(target, c4d.BaseObject) and "Focus distance (cm)" in ud:
        mg = cam.GetMg()
        dist = max((target.GetMg().off - mg.off).Dot(mg.v3.GetNormalized()), 1.0)
        fd = ud["Focus distance (cm)"]
        if abs(op[fd] - dist) > 1e-3:
            op[fd] = dist

    # 3. tag controls -> shader
    if info:
        _set(otag, pins, "LensModel", info[3])
    for name, var in PIN_FOR.items():
        if name in ud:
            _set(otag, pins, var, op[ud[name]])
    if ADV_UD in ud:
        _set(otag, pins, "Custom", 1)
        for e in ADV:
            if e[2] in ud:
                _set(otag, pins, e[1], op[ud[e[2]]])
    _colour_correction(otag, ud)
    _set(otag, pins, "FocalLength", cam[c4d.CAMERA_FOCUS])
    _set(otag, pins, "SensorWidth", cam[c4d.CAMERAOBJECT_APERTURE])
    _set(otag, pins, "Frame", doc.GetTime().GetFrame(doc.GetFps()))


# ------------------------------------------------------------------ buttons
def _compile():
    cam = op.GetObject()
    d = op.GetDocument()
    otag, _p = _find_osl_tag(cam) if cam else (None, None)
    if otag is None:
        c4d.gui.MessageDialog("No CharacterLens shader found on this camera's Octane tag.")
        return
    bd = d.GetActiveBaseDraw() if d else None
    if bd is not None:
        bd.SetSceneCamera(cam)
    pid = None
    for bc, p, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        if bc[c4d.DESC_NAME] == "Compile":
            pid = p
            break
    if pid is not None:
        try:
            c4d.CallButton(otag, pid)
        except Exception:
            pass
    c4d.EventAdd()
    c4d.gui.MessageDialog("Compile sent.\n\nOctane only compiles an OSL camera while the Live Viewer is rendering "
                          "through it - if nothing changes, start the Live Viewer and press this again.")


def _reset_look():
    ud = _uds()
    for n in LOOK:
        if n in ud:
            op[ud[n]] = 1.0
    for n, v in (("Exposure (stops)", 0.0), ("Saturation", 1.0), ("Gamma", 1.0)):
        if n in ud:
            op[ud[n]] = v
    c4d.EventAdd()


def _use_preset():
    ud = _uds()
    if "Lens" in ud:
        _fill_adv(op[ud["Lens"]], ud)
    c4d.EventAdd()


def _save_preset():
    ud = _uds()
    if "Lens" not in ud:
        return
    lens = op[ud["Lens"]]
    saved = _saved(ud)
    info = _lens_info(lens, saved)
    if info is None:
        return
    default = info[0] if lens >= SAVED_BASE else "My " + info[0]
    name = c4d.gui.InputDialog("Name for this lens (it is added to the Lens list):", default)
    if not name:
        return
    name = name.strip()
    values = {}
    for e in ADV:
        if e[2] in ud:
            v = op[ud[e[2]]]
            values[e[0]] = int(v) if isinstance(v, bool) else v
    new_id = max([SAVED_BASE] + list(saved.keys())) + 1
    for k, s_ in saved.items():          # same name -> overwrite that one
        if s_["name"] == name:
            new_id = k
    saved[new_id] = {"name": name, "base": info[3], "values": values}
    _store_saved(saved, ud)
    _refresh_cycle(saved)
    ud = _uds()
    op[ud["Lens"]] = new_id
    if ADV_UD in ud:
        op[ud[ADV_UD]] = new_id
    c4d.EventAdd()


def _delete_preset():
    ud = _uds()
    if "Lens" not in ud:
        return
    lens = op[ud["Lens"]]
    saved = _saved(ud)
    if lens < SAVED_BASE or lens not in saved:
        c4d.gui.MessageDialog("Pick a saved lens ([Saved] ...) in the Lens list first, then press Delete.")
        return
    s = saved[lens]
    if not c4d.gui.QuestionDialog("Delete the saved lens \"%s\"?\n\nThe current values stay on the tag." % s["name"]):
        return
    base = s["base"]
    del saved[lens]
    _store_saved(saved, ud)
    _refresh_cycle(saved)
    ud = _uds()
    op[ud["Lens"]] = base
    if ADV_UD in ud:
        op[ud[ADV_UD]] = base        # keep the current Advanced values
    c4d.EventAdd()


def _add_ps1():
    d = op.GetDocument()
    sel = [o for o in d.GetActiveObjects(getattr(c4d, "GETACTIVEOBJECTFLAGS_NONE", 0)) if not o.CheckType(c4d.Ocamera)]
    if not sel:
        c4d.gui.MessageDialog("Select the objects that should get the PS1 vertex wobble (in the Object Manager), "
                              "then select this tag again and press the button.")
        return
    d.StartUndo()
    gen = c4d.BaseObject(c4d.Opython)
    gen.SetName("PS1 Vertex Snap")
    gen[c4d.OPYTHON_CODE] = PS1_CODE
    opt = getattr(c4d, "OPYTHON_OPTIMIZE", None)
    if opt is not None:
        gen[opt] = False
    for name, dtype, val in (("Grid lines", c4d.DTYPE_LONG, 240), ("Depth steps (cm)", c4d.DTYPE_REAL, 0.0),
                             ("Strength", c4d.DTYPE_REAL, 1.0)):
        bc = c4d.GetCustomDataTypeDefault(dtype)
        bc[c4d.DESC_NAME] = name
        bc[c4d.DESC_SHORT_NAME] = name
        gen[gen.AddUserData(bc)] = val
    first = sel[0]
    d.InsertObject(gen, first.GetUp(), first.GetPred())
    d.AddUndo(c4d.UNDOTYPE_NEW, gen)
    for o in sel:
        mg = o.GetMg()
        d.AddUndo(c4d.UNDOTYPE_CHANGE, o)
        o.Remove()
        o.InsertUnderLast(gen)
        o.SetMg(mg)
    d.EndUndo()
    c4d.EventAdd()


def _update_visibility():
    ud = _uds()
    if "Lens" not in ud:
        return
    info = _lens_info(op[ud["Lens"]])
    hide = (info[3] if info else op[ud["Lens"]]) < 100
    for did, bc in op.GetUserDataContainer():
        if (bc[c4d.DESC_NAME] in STYLE_ONLY or bc[c4d.DESC_NAME] == "Style") and bool(bc[c4d.DESC_HIDE]) != hide:
            bc[c4d.DESC_HIDE] = hide
            op.SetUserDataContainer(did, bc)


def _ud_name(did):
    """Name of the User Data entry a DescID points at (DescIDs aren't hashable)."""
    try:
        idx = did[did.GetDepth() - 1].id
    except Exception:
        return None
    for d_, bc in op.GetUserDataContainer():
        try:
            if d_[d_.GetDepth() - 1].id == idx:
                return bc[c4d.DESC_NAME]
        except Exception:
            pass
    return None


BUTTONS = {BTN_COMPILE: _compile, BTN_RESET: _reset_look, BTN_PS1: _add_ps1,
           BTN_PRESET: _use_preset, BTN_SAVE: _save_preset, BTN_DELETE: _delete_preset}


def message(msg_type, data):
    try:
        if msg_type == c4d.MSG_DESCRIPTION_COMMAND and isinstance(data, dict):
            fn = BUTTONS.get(_ud_name(data.get("id")))
            if fn:
                fn()
        elif msg_type == c4d.MSG_DESCRIPTION_POSTSETPARAMETER:
            _update_visibility()
    except Exception as e:
        print("CharacterLens tag:", e)
    return True
