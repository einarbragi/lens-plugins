"""XenoCam tag  -  v1.2
All XenoCam controls live on this tag (User Data). The tag writes them into
the XenoCam OSL shader on the Octane Camera tag, together with the camera's
focal length, sensor width, focus distance and the frame number.

* The lens character follows the camera's focal length (a classic cine prime
  set, 12-300 mm). Era moves the whole set from clean modern to vintage.
* Focus Object: any object. Setup copies the camera's own Focus Object in
  here if this field is empty; if the two differ, this one wins. Empty =
  the camera's own Focus Object, and if neither is set, Focus distance is
  used as typed.
* Super8: 0 off, 1 full Super 8 vibe.
"""
import c4d

# tag control -> shader input
PIN_FOR = {
    "F-stop": "FStop", "Widest aperture": "WidestAperture", "Focus distance (cm)": "FocusDistance",
    "Focus breathing": "Breathing", "Fisheye": "Fisheye",
    "Character": "Character", "Era (0 modern, 0.5 classic, 1 vintage)": "Era", "Format": "Anamorphic",
    "Anamorphic squeeze": "Squeeze", "Super8": "Super8",
    "Aperture blades (0 = round)": "Blades", "Blade roundness": "Roundness", "Cat-eye": "CatEye",
    "Bokeh rim (- creamy, + soap bubble)": "BokehRim",
    "Glow": "Glow", "Haze": "Haze", "Swirl": "Swirl", "Edge softness": "EdgeSoftness",
    "Distortion": "Distortion", "Focus plane tilt (deg)": "Tilt",
    "Fringing": "Fringing", "Purple fringing": "PurpleFringing", "Vignette": "Vignette",
    "Warmth": "Warmth", "Edge colour cast": "EdgeCast",
}
SHADER_PINS = list(PIN_FOR.values()) + ["FocalLength", "SensorWidth", "Frame"]
FIRST, LAST = "FStop", "Frame"
LOOK_DEFAULTS = {
    "Character": 1.0, "Era (0 modern, 0.5 classic, 1 vintage)": 0.5, "Super8": 0.0,
    "Aperture blades (0 = round)": 8, "Blade roundness": 0.75, "Cat-eye": 1.0,
    "Bokeh rim (- creamy, + soap bubble)": 0.0, "Glow": 1.0, "Haze": 1.0, "Swirl": 1.0, "Edge softness": 1.0,
    "Distortion": 1.0, "Focus plane tilt (deg)": 0.0, "Fringing": 1.0, "Purple fringing": 1.0,
    "Vignette": 1.0, "Warmth": 0.0, "Edge colour cast": 1.0,
}
NOTE_UD = "Full character at"
BTN_COMPILE, BTN_RESET = "Compile shader", "Reset look"

_cache = {}


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _pins(otag):
    """DescIDs of the XenoCam shader's inputs (the block from FStop to Frame)."""
    keys = {_norm(p): p for p in SHADER_PINS}
    out, inside = {}, False
    for bc, pid, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        n = _norm(bc[c4d.DESC_NAME] or "")
        if not n:
            continue
        if not inside and n == _norm(FIRST):
            inside = True
        if inside:
            var = keys.get(n)
            if var is not None and var not in out:
                out[var] = pid
            if n == _norm(LAST):
                break
    return out if FIRST in out and len(out) >= 8 else {}


def _find_osl_tag(cam):
    hit = _cache.get(id(cam))
    if hit and hit[0].IsAlive() and hit[0].GetObject() == cam and hit[1]:
        return hit
    for t in cam.GetTags():
        if t.GetType() == c4d.Tpython:
            continue
        pins = _pins(t)
        if pins:
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


def _fnum(x):
    return ("%.1f" % x).rstrip("0").rstrip(".") if x < 10 else "%d" % round(x)


def _update_note(ud):
    if NOTE_UD not in ud or "Widest aperture" not in ud or "F-stop" not in ud:
        return
    maxf = float(op[ud["Widest aperture"]])
    fs = float(op[ud["F-stop"]])
    if fs < maxf - 1e-3:
        text = "T%s - the lens opens no wider, so T%s acts as T%s" % (_fnum(maxf), _fnum(fs), _fnum(maxf))
    elif fs > maxf * 1.05:
        text = "T%s - you're at T%s, so the look is cleaner than wide open" % (_fnum(maxf), _fnum(fs))
    else:
        text = "T%s - you're wide open: full character" % _fnum(maxf)
    if "Super8" in ud and op[ud["Super8"]] > 0.5:
        text += " (Super8 adds deep focus)"
    if op[ud[NOTE_UD]] != text:
        op[ud[NOTE_UD]] = text


# ----------------------------------------------------------------- main
def main():
    cam = op.GetObject()
    if cam is None:
        return
    otag, pins = _find_osl_tag(cam)
    if otag is None:
        return
    ud = _uds()

    # focus object -> focus distance (cm, along the view axis)
    target = op[ud["Focus Object"]] if "Focus Object" in ud else None
    if target is None:
        target = _cam_focus_object(cam)
    if isinstance(target, c4d.BaseObject) and "Focus distance (cm)" in ud:
        mg = cam.GetMg()
        dist = max((target.GetMg().off - mg.off).Dot(mg.v3.GetNormalized()), 1.0)
        fd = ud["Focus distance (cm)"]
        if abs(op[fd] - dist) > 1e-3:
            op[fd] = dist
    _update_note(ud)

    # tag controls -> shader
    for name, var in PIN_FOR.items():
        if name in ud:
            _set(otag, pins, var, op[ud[name]])
    _set(otag, pins, "FocalLength", cam[c4d.CAMERA_FOCUS])
    _set(otag, pins, "SensorWidth", cam[c4d.CAMERAOBJECT_APERTURE])
    _set(otag, pins, "Frame", doc.GetTime().GetFrame(doc.GetFps()))


# ------------------------------------------------------------------ buttons
def _compile():
    cam = op.GetObject()
    d = op.GetDocument()
    otag, _p = _find_osl_tag(cam) if cam else (None, None)
    if otag is None:
        c4d.gui.MessageDialog("No XenoCam shader found on this camera's Octane tag.")
        return
    bd = d.GetActiveBaseDraw() if d else None
    if bd is not None:
        bd.SetSceneCamera(cam)
    for bc, p, _g in otag.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        if bc[c4d.DESC_NAME] == "Compile":
            try:
                c4d.CallButton(otag, p)
            except Exception:
                pass
            break
    c4d.EventAdd()
    c4d.gui.MessageDialog("Compile sent.\n\nOctane only compiles an OSL camera while the Live Viewer is rendering "
                          "through it - if nothing changes, start the Live Viewer and press this again.")


def _reset_look():
    ud = _uds()
    for name, val in LOOK_DEFAULTS.items():
        if name in ud:
            op[ud[name]] = val
    c4d.EventAdd()


def _update_visibility():
    ud = _uds()
    if "Format" not in ud:
        return
    hide = op[ud["Format"]] == 0
    for did, bc in op.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Anamorphic squeeze" and bool(bc[c4d.DESC_HIDE]) != hide:
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


BUTTONS = {BTN_COMPILE: _compile, BTN_RESET: _reset_look}


def message(msg_type, data):
    try:
        if msg_type == c4d.MSG_DESCRIPTION_COMMAND and isinstance(data, dict):
            fn = BUTTONS.get(_ud_name(data.get("id")))
            if fn:
                fn()
        elif msg_type == c4d.MSG_DESCRIPTION_POSTSETPARAMETER:
            _update_visibility()
    except Exception as e:
        print("XenoCam tag:", e)
    return True
