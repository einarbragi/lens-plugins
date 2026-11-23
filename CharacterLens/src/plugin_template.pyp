"""CharacterLens for Cinema 4D + Octane  -  v0.6  (single-file plugin)

Install: put this file in your Cinema 4D plugins folder
         (Edit > Preferences > Open Preferences Folder... > plugins), restart.
Use:     select a camera (or nothing) and click Extensions > CharacterLens,
         or add the CharacterLens tag to a camera from the Tags menu.

Everything is inside this one file:
  * the CharacterLens OSL camera shader (22 lenses + 26 stylized cameras)
  * the CharacterLens camera tag - every control lives on it (lens, focus, look,
    style, Compile / Reset / PS1 buttons)
  * the PS1 vertex-snap generator
  * colour grades (LUTs) for the styles' live film looks, written next to it

Plugin ID 1000007 is from Maxon's free test range (1000001-1000010).
If another test plugin already uses it, change PLUGIN_ID below.
"""
import base64, os, sys, tempfile, zlib
import c4d
from c4d import gui

PLUGIN_ID = 1000007
VERSION = "0.6"

def _unpack(blob):
    return zlib.decompress(base64.b64decode("".join(blob.split()))).decode("utf-8")

OSL_SOURCE = _unpack("""@@OSL@@""")
TAG_LOGIC = _unpack("""@@TAG@@""")

# The tag on the camera only carries this stub; its logic runs inside the plugin
# (the characterlens_runtime module below), so the Tag tab stays short and every
# camera picks up plugin updates automatically.
TAG_CODE = '''"""CharacterLens camera tag.

The controls are on the Character Lens tab. The logic lives in the CharacterLens
plugin (Extensions > CharacterLens), so this tag needs the plugin installed.
Without it the camera keeps rendering with its last settings.
"""
try:
    import characterlens_runtime as _cl
except ImportError:
    _cl = None


def main():
    if _cl is not None:
        _cl.run(op, doc)


def message(msg_type, data):
    if _cl is not None:
        return _cl.message(op, msg_type, data)
    return True
'''

RUNTIME_SRC = r'''
import c4d

_spaces = {}


def _key(op):
    try:
        return ("guid", op.GetGUID())
    except Exception:
        obj = op.GetObject()
        return ("name", obj.GetName() if obj else "", op.GetName())


def _space(op):
    k = _key(op)
    ns = _spaces.get(k)
    if ns is None:
        ns = {"__name__": "characterlens_tag"}
        exec(compile(TAG_LOGIC, "CharacterLens tag", "exec"), ns)
        _spaces[k] = ns
    return ns


def run(op, doc):
    ns = _space(op)
    ns["op"], ns["doc"] = op, doc
    ns["main"]()


def message(op, msg_type, data):
    ns = _space(op)
    ns["op"], ns["doc"] = op, op.GetDocument()
    return ns["message"](msg_type, data)
'''


def _install_runtime():
    import types
    mod = types.ModuleType("characterlens_runtime")
    mod.TAG_LOGIC = TAG_LOGIC
    exec(RUNTIME_SRC, mod.__dict__)
    sys.modules["characterlens_runtime"] = mod
    return mod


_cl_runtime = _install_runtime()
PS1_CODE = _unpack("""@@PS1@@""")

OCTANE_CAMERA_TAG_ID = 1029524


# --------------------------------------------------------------- helpers
def _entries(node):
    return [(bc, pid) for bc, pid, _g in node.GetDescription(c4d.DESCFLAGS_DESC_NONE)]


def _find(node, name, dtype=None):
    for bc, pid in _entries(node):
        if bc[c4d.DESC_NAME] == name:
            if dtype is None or pid[pid.GetDepth() - 1].dtype == dtype:
                return bc, pid
    return None, None


def _octane_camera_tag(cam, create=True):
    for t in cam.GetTags():
        n = t.GetTypeName().lower()
        if "octane" in n and "camera" in n:
            return t
    if create:
        try:
            t = c4d.BaseTag(OCTANE_CAMERA_TAG_ID)
            if t:
                cam.InsertTag(t)
                return t
        except Exception:
            pass
    return None


def _add_ud(obj, name, dtype, default=None, hide=False):
    bc = c4d.GetCustomDataTypeDefault(dtype)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if hide:
        bc[c4d.DESC_HIDE] = True
    did = obj.AddUserData(bc)
    if default is not None:
        obj[did] = default
    return did


def _ud_names(obj):
    return [bc[c4d.DESC_NAME] for _d, bc in obj.GetUserDataContainer()]


# ---- CharacterLens tag UI builder (shared by the plugin and the test script) ----
def _cl_norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _cl_pin_values(otag):
    """Current values of the shader pins, keyed by variable name."""
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
            step=None, gui=None, cycle=None, unit=None, hide=False, columns=None):
    bc = c4d.GetCustomDataTypeDefault(dtype)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if parent is not None:
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
    if unit is not None:
        bc[c4d.DESC_UNIT] = unit
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
        bc[c4d.DESC_DEFAULT] = True          # group starts unfolded
    did = tag.AddUserData(bc)
    if default is not None:
        try:
            tag[did] = default
        except Exception:
            pass
    return did


def build_tag_ui(ptag, otag, lenses):
    """(Re)build the CharacterLens tag's controls. Keeps the Focus Object and
    takes starting values from the shader's current pins."""
    old_focus = None
    old_last = -1
    for did, bc in ptag.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Focus Object":
            old_focus = ptag[did]
        if bc[c4d.DESC_NAME] == "_last lens":
            old_last = ptag[did]
    for did, _bc in list(ptag.GetUserDataContainer()):
        ptag.RemoveUserData(did)

    v = _cl_pin_values(otag) if otag is not None else {}
    lens = int(v.get("LensModel", 2) or 2)
    g = lambda k, d: v.get(k, d) if v.get(k) is not None else d
    R, L = c4d.DTYPE_REAL, c4d.DTYPE_LONG
    SL = c4d.CUSTOMGUI_REALSLIDER

    gl = _cl_add(ptag, "Lens & focus", c4d.DTYPE_GROUP, columns=1)
    _cl_add(ptag, "Lens", L, gl, lens, gui=c4d.CUSTOMGUI_CYCLE,
            cycle=[(k, n) for k, (n, _f, _s) in sorted(lenses.items())])
    _cl_add(ptag, "F-stop", R, gl, float(g("FStop", 1.4)), mn=0.7, mx=256.0, smin=0.95, smax=22.0, step=0.1, gui=SL)
    _cl_add(ptag, "Focus Object", c4d.DTYPE_BASELISTLINK, gl, old_focus)
    _cl_add(ptag, "Focus distance (cm)", R, gl, float(g("FocusDistance", 200.0)), mn=1.0, mx=1000000.0, step=1.0)

    gk = _cl_add(ptag, "Look", c4d.DTYPE_GROUP, columns=1)
    for name, var in (("Character", "Character"), ("Bokeh", "Bokeh"), ("Swirl", "SwirlAmount"),
                      ("Softness / glow", "Softness"), ("Fringing", "Fringing"), ("Distortion", "Distortion"),
                      ("Vignette", "Vignette")):
        _cl_add(ptag, name, R, gk, float(g(var, 1.0)), mn=0.0, mx=3.0, smin=0.0, smax=2.0, step=0.01, gui=SL)
    _cl_add(ptag, "Reset look", c4d.DTYPE_BUTTON, gk, gui=c4d.CUSTOMGUI_BUTTON)

    is_style = lens >= 100
    gs = _cl_add(ptag, "Style", c4d.DTYPE_GROUP, columns=1, hide=not is_style)
    _cl_add(ptag, "Pixel lines (0 = style default)", L, gs, int(g("PixelLines", 0)), mn=0, mx=2160,
            smin=0, smax=720, hide=not is_style, gui=c4d.CUSTOMGUI_LONGSLIDER)
    _cl_add(ptag, "Wobble / gate weave", R, gs, float(g("Wobble", 1.0)), mn=0.0, mx=3.0, smin=0.0, smax=2.0,
            step=0.01, gui=SL, hide=not is_style)
    _cl_add(ptag, "Anaglyph eye distance (cm)", R, gs, float(g("EyeDistance", 6.5)), mn=0.0, mx=50.0, smin=0.0,
            smax=15.0, step=0.1, gui=SL, hide=not is_style)

    gt = _cl_add(ptag, "Tools", c4d.DTYPE_GROUP, columns=1)
    _cl_add(ptag, "Compile shader", c4d.DTYPE_BUTTON, gt, gui=c4d.CUSTOMGUI_BUTTON)
    _cl_add(ptag, "Add PS1 snap to selected", c4d.DTYPE_BUTTON, gt, gui=c4d.CUSTOMGUI_BUTTON)
    _cl_add(ptag, "_last lens", L, None, lens, hide=True)   # no focal jump on upgrade


LENSES = {
    1: ('Zeiss Ultra Prime 50 T1.9 (clean)', 50, 1.9),
    2: ('Nikkor 85mm f1.4', 85, 1.4),
    3: ('Voigtlander Nokton Classic 40 f1.4', 40, 1.4),
    4: ('Canon 50 f0.95 Dream Lens', 50, 0.95),
    5: ('Canon FD 24 f1.4 SSC Aspherical', 24, 1.4),
    6: ('Cooke Panchro Classic 21 T2.2', 21, 2.2),
    7: ('LOMO Illumina 25 T1.3', 25, 1.3),
    8: ('Blackwing7 20.7 T1.9 X-Tuned', 20.7, 1.9),
    9: ('Angenieux 10x25 zoom 55 T3.7', 55, 3.7),
    10: ('Petzval Pro 55 T1.8', 55, 1.8),
    11: ('Helios 44-2 58 f2', 58, 2.0),
    12: ('Deakinizer #2A 32 T2.1', 32, 2.1),
    13: ('Civil War detuned', 35, 2.0),
    14: ('Pocket Dispo 28 f10', 28, 10.0),
    15: ('Lensbaby Obscura 16 f90', 16, 90.0),
    16: ('7Artisans Floral Bloom 37 T2.9', 37, 2.9),
    17: ('Soap Bubble 100 f2.8 (Trioplan)', 100, 2.8),
    18: ('Anamorphic 2x 50 T2', 50, 2.0),
    19: ('Pinhole f150', 30, 150.0),
    101: ('[Style] PS1', 31, 1.9),
    102: ('[Style] N64', 31, 1.9),
    103: ('[Style] Doom / Build engine', 18, 1.9),
    104: ('[Style] Game Boy Camera', 38, 10.0),
    105: ('[Style] CRT TV', 35, 1.9),
    106: ('[Style] VHS camcorder', 35, 3.7),
    107: ('[Style] Disposable camera', 30, 10),
    108: ('[Style] Toy camera (Holga)', 40, 10),
    109: ('[Style] Super 8', 30, 3.7),
    110: ('[Style] Skate fisheye (VX1000)', 10, 1.9),
    111: ('[Style] CCTV security', 12, 1.9),
    112: ('[Style] Bodycam / dashcam', 12, 10.0),
    113: ('[Style] Peephole', 8, 1.9),
    114: ('[Style] 2000s webcam', 35, 10.0),
    115: ('[Style] Night vision', 50, 1.3),
    116: ('[Style] Anaglyph 3D (red/cyan)', 35, 1.9),
    117: ('[Style] Prism filter', 50, 1.9),
    118: ('[Style] Kaleidoscope', 35, 1.9),
    119: ('[Style] Compound eye', 25, 1.9),
    120: ('[Style] Frosted glass', 50, 1.9),
    121: ('[Style] Ribbed glass', 50, 1.9),
    122: ('[Style] Shower door glass', 50, 1.9),
    123: ('[Style] Underwater (flat port)', 24, 1.9),
    124: ('[Style] Tilt-shift miniature', 50, 1.9),
    125: ('[Style] Tiny planet', 6, 1.9),
    126: ('[Style] Mirror ball', 50, 1.9),
    127: ('[Style] 360 equirectangular', 12, 1.9),
    128: ('[Style] Isometric (orthographic)', 50, 1.9),
}


# ------------------------------------------------------ 1. camera setup
def _run_before_octane(doc, cam, ptag):
    """The CharacterLens tag has to run before the Octane Camera tag, otherwise
    Octane reads the focus distance from the previous update (focus lags one
    move behind). Put it first on the camera and early in the expression pass
    (still after animation, so animated cameras and focus objects are right)."""
    if cam.GetFirstTag() is not ptag:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, cam)
        ptag.Remove()
        cam.InsertTag(ptag)
    if ptag.GetType() != c4d.Tpython:
        return                                   # the CharacterLens tag sets its own priority
    try:
        pd = ptag[c4d.EXPRESSION_PRIORITY]
        pd.SetPriorityValue(c4d.PRIORITYVALUE_MODE, c4d.CYCLE_EXPRESSION)
        pd.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, -100)
        ptag[c4d.EXPRESSION_PRIORITY] = pd
    except Exception:
        pass


def _status(text):
    print("CharacterLens: " + text.replace("\n", " "))
    try:
        (getattr(c4d.gui, "StatusSetText", None) or c4d.StatusSetText)("CharacterLens: " + text.split("\n")[0])
    except Exception:
        pass


def _camera_from_view(doc):
    """A new camera where the viewport is looking from."""
    cam = c4d.BaseObject(c4d.Ocamera)
    cam.SetName("Octane Camera")
    bd = doc.GetActiveBaseDraw()
    view = bd.GetSceneCamera(doc) if bd is not None else None
    if view is not None:
        cam.SetMg(view.GetMg())
        try:
            cam[c4d.CAMERA_FOCUS] = view[c4d.CAMERA_FOCUS]
        except Exception:
            pass
    doc.InsertObject(cam)
    doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
    return cam


def _selected_camera(doc):
    cam = doc.GetActiveObject()
    if cam is not None and cam.CheckType(c4d.Ocamera):
        return cam
    tag = doc.GetActiveTag()
    obj = tag.GetObject() if tag is not None else None
    if obj is not None and obj.CheckType(c4d.Ocamera):
        return obj
    return None


def setup_camera(doc, cam=None):
    """One click: set up the selected camera, or make a new one from the view."""
    doc.StartUndo()
    report = []
    if cam is None:
        cam = _selected_camera(doc)
    if cam is None:
        cam = _camera_from_view(doc)
        report.append("New camera '%s' made from the view" % cam.GetName())
    otag = _octane_camera_tag(cam)
    if otag is None:
        doc.EndUndo()
        _status("no Octane Camera tag could be added to '%s' - is Octane installed?" % cam.GetName())
        return
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, otag)

    # camera type -> OSL
    bc, pid = _find(otag, "Camera type")
    if pid is not None:
        cyc = bc.GetContainer(c4d.DESC_CYCLE)
        osl_val = None
        for k, v in cyc:
            if isinstance(v, str) and v.strip().lower() == "osl":
                osl_val = k
        if osl_val is not None:
            otag[pid] = osl_val
            report.append("Camera type set to OSL")
    otag.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()

    # OSL code -> compile
    ok = False
    _b, code_pid = _find(otag, "Code")
    if code_pid is not None:
        try:
            otag.SetParameter(code_pid, OSL_SOURCE, c4d.DESCFLAGS_SET_NONE)
            got = otag.GetParameter(code_pid, c4d.DESCFLAGS_GET_NONE)
            ok = isinstance(got, str) and got.strip()[:40] == OSL_SOURCE.strip()[:40]
        except Exception:
            ok = False
    if ok:
        bd = doc.GetActiveBaseDraw()
        if bd is not None:
            bd.SetSceneCamera(cam)
            report.append("Viewport set to look through '%s'" % cam.GetName())
        _b, comp_pid = _find(otag, "Compile")
        if comp_pid is not None:
            try:
                c4d.CallButton(otag, comp_pid[comp_pid.GetDepth() - 1].id)
                report.append("Shader code set and Compile pressed")
            except Exception:
                report.append("Shader code set")
        else:
            report.append("Shader code set")
        report.append("Live Viewer restarted to compile it")
    else:
        c4d.CopyStringToClipboard(OSL_SOURCE)
        report.append("Could not fill the OSL Code field automatically - the shader is on your clipboard: "
                      "paste it into the OSL Camera's Code field and press Compile")

    # CharacterLens tag with all the controls: the plugin's own tag type, or a
    # Python tag if that type couldn't be registered
    ptag, old_py = None, None
    for t in cam.GetTags():
        if t.GetType() == TAG_ID:
            ptag = t
        elif t.GetType() == c4d.Tpython and t.GetName() == "CharacterLens":
            old_py = t
    old_values = None
    if ptag is None and _TAG_OK:
        ptag = c4d.BaseTag(TAG_ID)
        ptag.SetName("CharacterLens")
        cam.InsertTag(ptag)
        doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
        if old_py is not None:
            old_values = _cl_old_values(old_py)
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, old_py)
            old_py.Remove()
            report.append("Old Python CharacterLens tag replaced by the CharacterLens tag (settings kept)")
        else:
            report.append("CharacterLens tag added - all controls are on it")
    elif ptag is None:
        ptag = old_py
        if ptag is None:
            ptag = c4d.BaseTag(c4d.Tpython)
            ptag.SetName("CharacterLens")
            cam.InsertTag(ptag)
            doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
            report.append("CharacterLens tag added - all controls are on it")
        else:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
            report.append("CharacterLens tag updated - all controls are on it")
        ptag[c4d.TPYTHON_CODE] = TAG_CODE
        icon_pid = getattr(c4d, "ID_BASELIST_ICON_FILE", None)
        if icon_pid is not None:
            try:
                ptag[icon_pid] = str(PLUGIN_ID)     # the CharacterLens icon (registered above)
            except Exception:
                pass
    else:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
        report.append("CharacterLens tag updated - all controls are on it" if _has_controls(ptag)
                      else "CharacterLens tag added - all controls are on it")
    build_tag_ui(ptag, otag, LENSES, old_values)
    _run_before_octane(doc, cam, ptag)
    doc.SetActiveTag(ptag)
    doc.EndUndo()
    c4d.EventAdd()
    if ok and not _restart_live_viewer():
        report.append("start the Live Viewer to compile the shader")
    _status("set up on '%s'. %s." % (cam.GetName(), "; ".join(report)))


# ------------------------------------------------------ 2. PS1 snap
def add_ps1_snap(doc):
    flags = getattr(c4d, "GETACTIVEOBJECTFLAGS_NONE", 0)
    sel = doc.GetActiveObjects(flags)
    sel = [o for o in sel if not o.CheckType(c4d.Ocamera)]
    if not sel:
        gui.MessageDialog("Select the objects that should get the PS1 vertex wobble, then press this again.")
        return
    doc.StartUndo()
    gen = c4d.BaseObject(c4d.Opython)
    gen.SetName("PS1 Vertex Snap")
    gen[c4d.OPYTHON_CODE] = PS1_CODE
    opt = getattr(c4d, "OPYTHON_OPTIMIZE", None)
    if opt is not None:
        gen[opt] = False
    _add_ud(gen, "Grid lines", c4d.DTYPE_LONG, 240)
    _add_ud(gen, "Depth steps (cm)", c4d.DTYPE_REAL, 0.0)
    _add_ud(gen, "Strength", c4d.DTYPE_REAL, 1.0)
    first = sel[0]
    doc.InsertObject(gen, first.GetUp(), first.GetPred())
    doc.AddUndo(c4d.UNDOTYPE_NEW, gen)
    for o in sel:
        mg = o.GetMg()
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, o)
        o.Remove()
        o.InsertUnderLast(gen)
        o.SetMg(mg)
    doc.EndUndo()
    doc.SetActiveObject(gen)
    c4d.EventAdd()


# ------------------------------------------------------ 3. shader files
def export_files(folder):
    if not folder:
        return
    os.makedirs(folder, exist_ok=True)
    for name, text in (("CharacterLens.osl", OSL_SOURCE), ("CharacterLens_Tag.py", TAG_LOGIC),
                       ("CharacterLens_PS1_Snap_generator.py", PS1_CODE)):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(text)
    _status("saved CharacterLens.osl and the tag/generator code to " + folder)


# --------------------------------------------- start / restart the Live Viewer
OCTANE_START = 1033873    # Octane's "Start OctaneRender" (restarts it if it's running)


def _restart_live_viewer():
    """Octane compiles a new OSL camera, and links its inputs, reliably only when
    the Live Viewer (re)starts through it - pressing Compile from a plugin can
    leave the inputs unlinked. So set-up ends with Octane's own start command."""
    try:
        if c4d.plugins.FindPlugin(OCTANE_START, c4d.PLUGINTYPE_COMMAND) is not None:
            c4d.CallCommand(OCTANE_START)
            return True
    except Exception as e:
        print("CharacterLens: could not restart the Live Viewer:", e)
    return False


def _hook_setup(doc, cam=None):
    setup_camera(doc, cam)


def _hook_copy(doc):
    c4d.CopyStringToClipboard(OSL_SOURCE)
    _status("shader code copied - paste it into the OSL Camera's Code field and press Compile")


def _hook_export(doc):
    p = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Save CharacterLens shader to", c4d.FILESELECT_DIRECTORY)
    if p:
        export_files(p)


# ------------------------------------------------------ 4. film looks (colour grades)
def _luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _clamp(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _grade(r, g, b, sat=1.0, contrast=0.0, lift=(0, 0, 0), gain=(1, 1, 1), gamma=(1, 1, 1)):
    y = _luma(r, g, b)
    out = []
    for i, c in enumerate((r, g, b)):
        c = _clamp(y + (c - y) * sat)
        c = c + (c * c * (3.0 - 2.0 * c) - c) * contrast          # S-curve
        c = _clamp(c) ** gamma[i]
        out.append(_clamp(lift[i] + (gain[i] - lift[i]) * c))
    return out


def _nightvision(r, g, b):
    y = _clamp(_luma(r, g, b))                                      # one phosphor: monochrome green
    y = y + (y * y * (3.0 - 2.0 * y) - y) * 0.6                      # contrast: murky mids, bright highlights
    return (0.015 + 0.3 * y ** 1.6, 0.02 + 0.92 * y ** 1.3, 0.005 + 0.12 * y ** 1.8)


FILM_LUTS = {
    "nightvision": _nightvision,
    "cctv": lambda r, g, b: _grade(r, g, b, 0.25, 0.5, (0.0, 0.01, 0.01), (0.92, 1.0, 0.97), (1.1, 1.0, 1.02)),
    "webcam": lambda r, g, b: _grade(r, g, b, 0.85, 0.45, (0.0, 0.0, 0.02), (0.95, 1.0, 1.08), (1.05, 1.0, 0.95)),
    "super8": lambda r, g, b: _grade(r, g, b, 1.1, 0.25, (0.07, 0.05, 0.03), (1.0, 0.95, 0.8), (0.92, 1.0, 1.12)),
    "toy": lambda r, g, b: _grade(r, g, b, 1.35, 0.6, (0.0, 0.04, 0.07), (1.0, 0.98, 0.78), (1.15, 1.0, 0.85)),
    "vhs": lambda r, g, b: _grade(r, g, b, 0.8, 0.2, (0.06, 0.04, 0.07), (0.95, 0.94, 0.97), (1.0, 1.03, 0.98)),
    "disposable": lambda r, g, b: _grade(r, g, b, 1.15, 0.35, (0.02, 0.04, 0.02), (1.0, 0.97, 0.86), (0.95, 1.0, 1.08)),
}


def _cube(fn, n=17):
    lines = ["TITLE \"CharacterLens\"", "LUT_3D_SIZE %d" % n]
    for bi in range(n):
        for gi in range(n):
            for ri in range(n):
                c = fn(ri / (n - 1.0), gi / (n - 1.0), bi / (n - 1.0))
                lines.append("%.5f %.5f %.5f" % tuple(c))
    return "\n".join(lines) + "\n"


def _write_luts():
    """Write the looks' .cube files next to the plugin (or to temp); returns the folder."""
    for base in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "characterlens_res"),
                 os.path.join(tempfile.gettempdir(), "characterlens_res")):
        folder = os.path.join(base, "luts")
        try:
            os.makedirs(folder, exist_ok=True)
            for name, fn in FILM_LUTS.items():
                path = os.path.join(folder, name + ".cube")
                text = _cube(fn)
                if not os.path.exists(path) or open(path).read() != text:
                    with open(path, "w") as f:
                        f.write(text)
            return folder
        except Exception:
            continue
    return ""


# ------------------------------------------------------ 5. the one-click command
class CharacterLensCommand(c4d.plugins.CommandData):
    def Execute(self, doc):
        setup_camera(doc)
        return True


# ------------------------------------------------------ icon
ICON_PNG = """@@ICON@@"""


def _load_icon():
    """Write the embedded icon next to the plugin (or to temp) and load it."""
    data = base64.b64decode("".join(ICON_PNG.split()))
    for folder in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "characterlens_res"),
                   os.path.join(tempfile.gettempdir(), "characterlens_res")):
        try:
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, "characterlens_icon.png")
            if not os.path.exists(path) or os.path.getsize(path) != len(data):
                with open(path, "wb") as f:
                    f.write(data)
            bmp = c4d.bitmaps.BaseBitmap()
            res = bmp.InitWith(path)
            if (res[0] if isinstance(res, tuple) else res) == c4d.IMAGERESULT_OK:
                return bmp
        except Exception:
            pass
    return None


# ------------------------------------------------------ the CharacterLens tag type
TAG_ID = 1000008          # Maxon test-range ID, like PLUGIN_ID
_TAG_OK = False

_RES_FILES = {
    "res/c4d_symbols.h": "enum\n{\n\t_DUMMY_ELEMENT_\n};\n",
    "res/description/Tcharacterlens.h":
        "#ifndef _Tcharacterlens_H_\n#define _Tcharacterlens_H_\n\nenum\n{\n"
        "\tCHARACTERLENS_DUMMY = 1000\n};\n\n#endif\n",
    "res/description/Tcharacterlens.res":
        "CONTAINER Tcharacterlens\n{\n\tNAME Tcharacterlens;\n\tINCLUDE Tbase;\n}\n",
    "res/strings_en-US/description/Tcharacterlens.str":
        "STRINGTABLE Tcharacterlens\n{\n\tTcharacterlens \"CharacterLens\";\n}\n",
    "res/strings_en-US/c4d_strings.str": "STRINGTABLE\n{\n}\n",
}


def _write_res():
    """The tag type needs a description resource; write it next to the plugin so
    CharacterLens stays a single .pyp file."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "characterlens_res")
    for rel, text in _RES_FILES.items():
        path = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path).read() != text:
            with open(path, "w") as f:
                f.write(text)
    return base


class CharacterLensTag(c4d.plugins.TagData):
    """Runs the CharacterLens logic (the same code a Python tag ran) with no code tab."""

    def Init(self, node, *args):
        return True

    def AddToExecution(self, tag, prio_list):
        # early in the expression pass: after animation, before the Octane Camera tag
        prio_list.Add(tag, c4d.EXECUTIONPRIORITY_EXPRESSION - 100, 0)
        return True

    def Execute(self, tag, doc, op, bt, priority, flags):
        if not _has_controls(tag):
            # added from the Tags menu: set its camera up (on the main thread)
            key = _guid(tag)
            if key not in _AUTO_ASKED:
                _AUTO_ASKED.add(key)
                c4d.SpecialEventAdd(AUTO_ID)
            return c4d.EXECUTIONRESULT_OK
        try:
            _cl_runtime.run(tag, doc)
        except Exception as e:
            print("CharacterLens tag:", e)
        return c4d.EXECUTIONRESULT_OK

    def Message(self, node, msg_type, data):
        if msg_type in (c4d.MSG_DESCRIPTION_COMMAND, c4d.MSG_DESCRIPTION_POSTSETPARAMETER):
            try:
                _cl_runtime.message(node, msg_type, data)
            except Exception as e:
                print("CharacterLens tag:", e)
        return True


AUTO_ID = 1000009         # Maxon test-range ID, for the auto set-up message
_AUTO_ASKED = set()


def _guid(node):
    try:
        return node.GetGUID()
    except Exception:
        return id(node)


def _has_controls(tag):
    for _did, bc in tag.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Lens":
            return True
    return False


def _walk(obj):
    while obj is not None:
        yield obj
        for o in _walk(obj.GetDown()):
            yield o
        obj = obj.GetNext()


class CharacterLensAutoSetup(c4d.plugins.MessageData):
    """A CharacterLens tag added by hand sets up its own camera."""

    def CoreMessage(self, mid, bc):
        if mid != AUTO_ID:
            return True
        doc = c4d.documents.GetActiveDocument()
        for obj in list(_walk(doc.GetFirstObject())):
            for t in list(obj.GetTags()):
                if t.GetType() == TAG_ID and not _has_controls(t):
                    if obj.CheckType(c4d.Ocamera):
                        setup_camera(doc, obj)
                    else:
                        # a stray tag on a non-camera: take it off again (undoable) and say why, once
                        doc.StartUndo()
                        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, t)
                        t.Remove()
                        doc.EndUndo()
                        c4d.EventAdd()
                        _status("the CharacterLens tag only works on a camera - removed it from '%s'" % obj.GetName())
        return True


def _register_tag(icon):
    global _TAG_OK
    try:
        base = _write_res()
        res = c4d.plugins.GeResource()
        if not res.Init(base):
            print("CharacterLens: tag resource not loaded; using a Python tag instead")
            return
        _TAG_OK = bool(c4d.plugins.RegisterTagPlugin(
            id=TAG_ID, str="CharacterLens", info=c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION,
            g=CharacterLensTag, description="Tcharacterlens", icon=icon, res=res))
    except Exception as e:
        print("CharacterLens: tag type not registered (%s); using a Python tag instead" % e)
        _TAG_OK = False


if __name__ == "__main__":
    _icon = _load_icon()
    if _icon is not None:
        try:
            gui.RegisterIcon(PLUGIN_ID, _icon)      # lets the CharacterLens tag use it too
        except Exception:
            pass
    _register_tag(_icon)
    _cl_runtime.LUT_DIR = _write_luts()
    _cl_runtime.HOOKS = {"copy": _hook_copy, "export": _hook_export, "setup": _hook_setup}
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "CharacterLens", 0, _icon,
                                      "Add CharacterLens to the selected camera (or a new camera from the view)",
                                      CharacterLensCommand())
    if _TAG_OK:
        c4d.plugins.RegisterMessagePlugin(AUTO_ID, "CharacterLens auto set-up", 0, CharacterLensAutoSetup())
