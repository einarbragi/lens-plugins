"""CharacterLens for Cinema 4D + Octane  -  v0.6  (single-file plugin)

Install: put this file in your Cinema 4D plugins folder
         (Edit > Preferences > Open Preferences Folder... > plugins), restart.
Open:    Extensions > CharacterLens

Everything is inside this one file:
  * the CharacterLens OSL camera shader (22 lenses + 26 stylized cameras)
  * the CharacterLens camera tag - every control lives on it (lens, focus, look,
    style, Compile / Reset / PS1 buttons)
  * the PS1 vertex-snap generator
  * the post-process tool (PS1 dither, VHS, night vision, Game Boy, ...)

Plugin ID 1000007 is from Maxon's free test range (1000001-1000010).
If another test plugin already uses it, change PLUGIN_ID below.
"""
import base64, os, shlex, subprocess, sys, tempfile, zlib
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
POST_SCRIPT = _unpack("""@@POST@@""")
PS1_CODE = _unpack("""@@PS1@@""")

POST_LOOKS = [
    ("ps1", "PS1 - 15-bit colour + dither"), ("n64", "N64 - soft 16-bit colour"),
    ("doom", "Doom - 256-colour palette"), ("gameboy", "Game Boy - 4-tone green"),
    ("crt", "CRT - phosphor bloom"), ("vhs", "VHS - tape noise + tracking"),
    ("nightvision", "Night vision - mono green"), ("cctv", "CCTV - timestamp"),
    ("dashcam", "Dashcam - timestamp + speed"), ("webcam", "2000s webcam - JPEG blocks"),
    ("disposable", "Disposable - grain + light leaks"), ("toy", "Toy camera - cross-process"),
    ("super8", "Super 8 - grain, flicker, dust"), ("tiltshift", "Tilt-shift - saturation"),
    ("grain", "Film grain"), ("rolling", "Rolling shutter (from sub-frames)"),
    ("slitscan", "Slit-scan (from frames)"),
]
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


def setup_camera(doc):
    cam = doc.GetActiveObject()
    if cam is None or not cam.CheckType(c4d.Ocamera):
        gui.MessageDialog("Select a camera (Octane Camera or a C4D camera with an Octane Camera tag) first.")
        return
    doc.StartUndo()
    report = []
    otag = _octane_camera_tag(cam)
    if otag is None:
        doc.EndUndo()
        gui.MessageDialog("No Octane Camera tag found on this camera and one could not be created.\n"
                          "Add an Octane Camera tag, then run this again.")
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
        report.append("IMPORTANT: Octane only compiles an OSL camera while the Live Viewer is\n"
                      "  rendering through it. Open Octane > Live Viewer Window, start the render,\n"
                      "  then press Compile on the OSL Camera tab if the Lens controls don't appear.")
    else:
        c4d.CopyStringToClipboard(OSL_SOURCE)
        report.append("Could not fill the OSL Code field automatically.\n"
                      "The shader is on your clipboard: click the Code field on the\n"
                      "OSL Camera tab, Ctrl+A, Ctrl+V, then press Compile.")

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
        report.append("CharacterLens tag updated - all controls are on it")
    build_tag_ui(ptag, otag, LENSES, old_values)
    _run_before_octane(doc, cam, ptag)
    doc.SetActiveTag(ptag)
    doc.EndUndo()
    c4d.EventAdd()

    # compile log, if visible
    _b, log_pid = _find(otag, "Log")
    if log_pid is not None:
        try:
            log = otag.GetParameter(log_pid, c4d.DESCFLAGS_GET_NONE)
            if isinstance(log, str) and log.strip():
                report.append("Octane log: " + log.strip()[:300])
        except Exception:
            pass
    gui.MessageDialog("CharacterLens set up on '%s':\n\n- %s\n\nDrag an object into the CharacterLens tag's "
                      "Focus Object field to focus on it.\nUse the CharacterLens tag for everything - the shader's own pins on the Octane tag are internal." % (cam.GetName(), "\n- ".join(report)))


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


# ------------------------------------------------------ 3. post-process
def _post_path():
    p = os.path.join(tempfile.gettempdir(), "characterlens_post.py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(POST_SCRIPT)
    return p


def run_post(look, src, dst, python, extra):
    if not src or not os.path.exists(src):
        gui.MessageDialog("Pick the folder (or image) with your rendered frames.")
        return
    if not dst:
        dst = src.rstrip("\\/") + "_" + look
    script = _post_path()
    cmd = [python or "python", script, look, src, dst] + shlex.split(extra or "", posix=False)
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/k"] + cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(cmd)
    except Exception as e:
        gui.MessageDialog("Could not start Python (%s).\nSet the Python path to a Python 3 with numpy + Pillow "
                          "(pip install numpy pillow)." % e)
        return
    print("CharacterLens post: %s -> %s (%s)" % (src, dst, look))


def install_deps(python):
    cmd = [python or "python", "-m", "pip", "install", "--user", "numpy", "pillow", "imageio"]
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/k"] + cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(cmd)
    except Exception as e:
        gui.MessageDialog("Could not start Python (%s). Check the Python path." % e)


def export_files(folder):
    if not folder:
        return
    os.makedirs(folder, exist_ok=True)
    for name, text in (("CharacterLens.osl", OSL_SOURCE), ("characterlens_post.py", POST_SCRIPT),
                       ("CharacterLens_Tag.py", TAG_LOGIC), ("CharacterLens_PS1_Snap_generator.py", PS1_CODE)):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(text)
    gui.MessageDialog("Saved CharacterLens.osl, characterlens_post.py and the tag/generator code to:\n" + folder)


# ------------------------------------------------------------- dialog
ID_SETUP, ID_PS1, ID_LOOK, ID_SRC, ID_SRC_B, ID_DST, ID_DST_B, ID_PY, ID_EXTRA, ID_TS, ID_RUN, ID_EXPORT, \
    ID_COPY, ID_DEPS = range(1000, 1014)


class CharacterLensDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("CharacterLens " + VERSION)
        self.GroupBorderSpace(8, 8, 8, 8)

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, "Camera", 0)
        self.GroupBorder(c4d.BORDER_GROUP_IN); self.GroupBorderSpace(6, 6, 6, 6)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Select your camera, then:", 0)
        self.AddButton(ID_SETUP, c4d.BFH_SCALEFIT, 0, 0, "Set up CharacterLens on selected camera")
        self.AddButton(ID_COPY, c4d.BFH_SCALEFIT, 0, 0, "Copy shader code to clipboard")
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, "PS1 geometry", 0)
        self.GroupBorder(c4d.BORDER_GROUP_IN); self.GroupBorderSpace(6, 6, 6, 6)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Vertex wobble for the [Style] PS1 camera:", 0)
        self.AddButton(ID_PS1, c4d.BFH_SCALEFIT, 0, 0, "Add PS1 vertex snap to selected objects")
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 3, 0, "Post-process rendered frames", 0)
        self.GroupBorder(c4d.BORDER_GROUP_IN); self.GroupBorderSpace(6, 6, 6, 6)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Look", 0)
        self.AddComboBox(ID_LOOK, c4d.BFH_SCALEFIT, 0, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "", 0)
        for i, (_k, label) in enumerate(POST_LOOKS):
            self.AddChild(ID_LOOK, i, label)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Frames", 0)
        self.AddEditText(ID_SRC, c4d.BFH_SCALEFIT, 260, 0)
        self.AddButton(ID_SRC_B, c4d.BFH_RIGHT, 0, 0, "...")
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Output", 0)
        self.AddEditText(ID_DST, c4d.BFH_SCALEFIT, 260, 0)
        self.AddButton(ID_DST_B, c4d.BFH_RIGHT, 0, 0, "...")
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Python", 0)
        self.AddEditText(ID_PY, c4d.BFH_SCALEFIT, 260, 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Options", 0)
        self.AddEditText(ID_EXTRA, c4d.BFH_SCALEFIT, 260, 0)
        self.AddCheckbox(ID_TS, c4d.BFH_RIGHT, 0, 0, "Timestamp")
        self.GroupEnd()
        self.AddButton(ID_RUN, c4d.BFH_SCALEFIT, 0, 0, "Run post-process (opens a console window)")
        self.AddButton(ID_DEPS, c4d.BFH_SCALEFIT, 0, 0, "Install numpy + Pillow for the post tool (one time)")

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, "Files", 0)
        self.GroupBorder(c4d.BORDER_GROUP_IN); self.GroupBorderSpace(6, 6, 6, 6)
        self.AddButton(ID_EXPORT, c4d.BFH_SCALEFIT, 0, 0, "Save shader + post tool to a folder...")
        self.GroupEnd()
        return True

    def InitValues(self):
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID) or c4d.BaseContainer()
        self.SetInt32(ID_LOOK, bc.GetInt32(ID_LOOK, 0))
        self.SetString(ID_SRC, bc.GetString(ID_SRC, ""))
        self.SetString(ID_DST, bc.GetString(ID_DST, ""))
        self.SetString(ID_PY, bc.GetString(ID_PY, "python"))
        self.SetString(ID_EXTRA, bc.GetString(ID_EXTRA, ""))
        self.SetBool(ID_TS, bc.GetBool(ID_TS, False))
        return True

    def _store(self):
        bc = c4d.BaseContainer()
        bc.SetInt32(ID_LOOK, self.GetInt32(ID_LOOK))
        for i in (ID_SRC, ID_DST, ID_PY, ID_EXTRA):
            bc.SetString(i, self.GetString(i))
        bc.SetBool(ID_TS, self.GetBool(ID_TS))
        c4d.plugins.SetWorldPluginData(PLUGIN_ID, bc)

    def Command(self, cid, msg):
        doc = c4d.documents.GetActiveDocument()
        if cid == ID_SETUP:
            setup_camera(doc)
        elif cid == ID_COPY:
            c4d.CopyStringToClipboard(OSL_SOURCE)
            gui.MessageDialog("Shader code copied. Paste it into the OSL Camera's Code field and press Compile.")
        elif cid == ID_PS1:
            add_ps1_snap(doc)
        elif cid in (ID_SRC_B, ID_DST_B):
            p = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Choose folder", c4d.FILESELECT_DIRECTORY)
            if p:
                self.SetString(ID_SRC if cid == ID_SRC_B else ID_DST, p)
                self._store()
        elif cid == ID_RUN:
            self._store()
            look = POST_LOOKS[max(0, min(self.GetInt32(ID_LOOK), len(POST_LOOKS) - 1))][0]
            extra = self.GetString(ID_EXTRA)
            if self.GetBool(ID_TS):
                extra += " --timestamp"
            run_post(look, self.GetString(ID_SRC), self.GetString(ID_DST), self.GetString(ID_PY), extra)
        elif cid == ID_DEPS:
            self._store()
            if gui.QuestionDialog("Install numpy, Pillow and imageio into this Python with pip?\n\n" + (self.GetString(ID_PY) or "python")):
                install_deps(self.GetString(ID_PY))
        elif cid == ID_EXPORT:
            p = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Save CharacterLens files to", c4d.FILESELECT_DIRECTORY)
            if p:
                export_files(p)
        else:
            self._store()
        return True


class CharacterLensCommand(c4d.plugins.CommandData):
    dlg = None

    def Execute(self, doc):
        if self.dlg is None:
            self.dlg = CharacterLensDialog()
        return self.dlg.Open(c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=460, defaulth=0)

    def RestoreLayout(self, sec_ref):
        if self.dlg is None:
            self.dlg = CharacterLensDialog()
        return self.dlg.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


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
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "CharacterLens", 0, _icon,
                                      "CharacterLens lens + style camera for Octane", CharacterLensCommand())
