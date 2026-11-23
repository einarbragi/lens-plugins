"""XenoCam for Cinema 4D + Octane  -  v1.1  (single-file plugin)

Install: put this file in your Cinema 4D plugins folder
         (Edit > Preferences > Open Preferences Folder... > plugins), restart.
Open:    Extensions > XenoCam

One cinematic lens: a classic cine prime set (12-300 mm) whose character
follows the camera's focal length, with an Era dial (modern - classic -
vintage), a spherical / anamorphic switch and a Super8 slider. Every control
lives on the XenoCam tag on the camera.

Plugin ID 1000005 is from Maxon's free test range (1000001-1000010); CharacterLens
uses 1000007-1000009, so keep them apart. Before
sharing it widely, register a free permanent ID at developers.maxon.net and
put it in PLUGIN_ID.
"""
import base64, os, tempfile, zlib
import c4d
from c4d import gui

PLUGIN_ID = 1000005
VERSION = "1.1"
OCTANE_CAMERA_TAG_ID = 1029524


def _unpack(blob):
    return zlib.decompress(base64.b64decode("".join(blob.split()))).decode("utf-8")


OSL_SOURCE = _unpack("""@@OSL@@""")
TAG_CODE = _unpack("""@@TAG@@""")


# --------------------------------------------------------------- helpers
def _find(node, name):
    for bc, pid, _g in node.GetDescription(c4d.DESCFLAGS_DESC_NONE):
        if bc[c4d.DESC_NAME] == name:
            return bc, pid
    return None, None


def _octane_camera_tag(cam):
    for t in cam.GetTags():
        n = t.GetTypeName().lower()
        if "octane" in n and "camera" in n:
            return t
    try:
        t = c4d.BaseTag(OCTANE_CAMERA_TAG_ID)
        if t:
            cam.InsertTag(t)
            return t
    except Exception:
        pass
    return None


# ------------------------------------------------------ the tag's controls
def _add(tag, name, dtype, parent=None, default=None, mn=None, mx=None, smin=None, smax=None,
         step=None, gui_=None, cycle=None, hide=False, open_=True):
    bc = c4d.GetCustomDataTypeDefault(dtype)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if parent is not None:
        bc[c4d.DESC_PARENTGROUP] = parent
    if dtype == c4d.DTYPE_GROUP:
        bc[c4d.DESC_COLUMNS] = 1
        bc[c4d.DESC_DEFAULT] = bool(open_)
    for key, val in ((c4d.DESC_MIN, mn), (c4d.DESC_MAX, mx), (c4d.DESC_MINSLIDER, smin),
                     (c4d.DESC_MAXSLIDER, smax), (c4d.DESC_STEP, step)):
        if val is not None:
            bc[key] = val
    if gui_ is not None:
        bc[c4d.DESC_CUSTOMGUI] = gui_
    if cycle is not None:
        cyc = c4d.BaseContainer()
        for k, v in cycle:
            cyc.SetString(k, v)
        bc.SetContainer(c4d.DESC_CYCLE, cyc)
    if hide:
        bc[c4d.DESC_HIDE] = True
    did = tag.AddUserData(bc)
    if default is not None:
        try:
            tag[did] = default
        except Exception:
            pass
    return did


def _old_values(ptag):
    out = {}
    for did, bc in ptag.GetUserDataContainer():
        try:
            dt = did[did.GetDepth() - 1].dtype
        except Exception:
            dt = None
        if dt in (c4d.DTYPE_GROUP, c4d.DTYPE_BUTTON):
            continue
        try:
            out[bc[c4d.DESC_NAME]] = ptag[did]
        except Exception:
            pass
    return out


def build_tag_ui(ptag):
    """(Re)build the XenoCam controls, keeping any values the tag already had."""
    old = _old_values(ptag)
    for did, _bc in list(ptag.GetUserDataContainer()):
        ptag.RemoveUserData(did)
    R, L, G = c4d.DTYPE_REAL, c4d.DTYPE_LONG, c4d.DTYPE_GROUP
    SL, LSL, BTN = c4d.CUSTOMGUI_REALSLIDER, c4d.CUSTOMGUI_LONGSLIDER, c4d.CUSTOMGUI_BUTTON

    def real(name, parent, d, mn, mx, smin, smax, step=0.01):
        _add(ptag, name, R, parent, d, mn=mn, mx=mx, smin=smin, smax=smax, step=step, gui_=SL)

    g = _add(ptag, "Lens & focus", G)
    _add(ptag, "Fisheye", c4d.DTYPE_BOOL, g, False)
    real("F-stop", g, 2.0, 0.5, 64.0, 1.0, 22.0, 0.1)
    real("Widest aperture", g, 2.0, 0.5, 22.0, 1.0, 5.6, 0.1)
    _add(ptag, "Full character at", c4d.DTYPE_STRING, g, "", gui_=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))
    _add(ptag, "Focus Object", c4d.DTYPE_BASELISTLINK, g)
    _add(ptag, "Focus distance (cm)", R, g, 200.0, mn=1.0, mx=1000000.0, step=1.0)
    real("Focus breathing", g, 0.0, -3.0, 3.0, 0.0, 1.5)

    g = _add(ptag, "Look", G)
    real("Character", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Era (0 modern, 0.5 classic, 1 vintage)", g, 0.5, 0.0, 1.0, 0.0, 1.0)
    _add(ptag, "Format", L, g, 0, gui_=c4d.CUSTOMGUI_CYCLE, cycle=[(0, "Spherical"), (1, "Anamorphic")])
    real("Anamorphic squeeze", g, 2.0, 1.0, 3.0, 1.0, 2.0)
    real("Super8", g, 0.0, 0.0, 1.0, 0.0, 1.0)
    _add(ptag, "Reset look", c4d.DTYPE_BUTTON, g, gui_=BTN)

    g = _add(ptag, "Bokeh", G)
    _add(ptag, "Aperture blades (0 = round)", L, g, 8, mn=0, mx=32, smin=0, smax=16, step=1, gui_=LSL)
    real("Blade roundness", g, 0.75, 0.0, 1.0, 0.0, 1.0)
    real("Cat-eye", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Bokeh rim (- creamy, + soap bubble)", g, 0.0, -1.0, 1.0, -1.0, 1.0)

    g = _add(ptag, "Glow & edges", G)
    real("Glow", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Haze", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Swirl", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Edge softness", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Distortion", g, 1.0, -3.0, 5.0, 0.0, 3.0)
    real("Focus plane tilt (deg)", g, 0.0, -45.0, 45.0, -10.0, 10.0, 0.1)

    g = _add(ptag, "Colour", G)
    real("Fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Purple fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Vignette", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Warmth", g, 0.0, -1.0, 1.0, -1.0, 1.0)
    real("Edge colour cast", g, 1.0, 0.0, 5.0, 0.0, 3.0)

    g = _add(ptag, "Tools", G)
    _add(ptag, "Compile shader", c4d.DTYPE_BUTTON, g, gui_=BTN)

    old.pop("Full character at", None)
    anamorphic = bool(old.get("Format", 0))
    for did, bc in ptag.GetUserDataContainer():
        name = bc[c4d.DESC_NAME]
        if name in old and old[name] is not None:
            try:
                ptag[did] = old[name]
            except Exception:
                pass
        if name == "Anamorphic squeeze" and not anamorphic:
            bc[c4d.DESC_HIDE] = True
            ptag.SetUserDataContainer(did, bc)


def _run_before_octane(doc, cam, ptag):
    """The XenoCam tag must run before the Octane Camera tag, or Octane reads
    the focus distance from the previous update. First on the camera, early in
    the expression pass (still after animation)."""
    if cam.GetFirstTag() is not ptag:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, cam)
        ptag.Remove()
        cam.InsertTag(ptag)
    try:
        pd = ptag[c4d.EXPRESSION_PRIORITY]
        pd.SetPriorityValue(c4d.PRIORITYVALUE_MODE, c4d.CYCLE_EXPRESSION)
        pd.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, -100)
        ptag[c4d.EXPRESSION_PRIORITY] = pd
    except Exception:
        pass


# ------------------------------------------------------ set up a camera
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

    bc, pid = _find(otag, "Camera type")
    if pid is not None:
        for k, v in bc.GetContainer(c4d.DESC_CYCLE):
            if isinstance(v, str) and v.strip().lower() == "osl":
                otag[pid] = k
                report.append("Camera type set to OSL")
    otag.Message(c4d.MSG_UPDATE)

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
                c4d.CallButton(otag, comp_pid)
            except Exception:
                pass
        report.append("XenoCam shader set and Compile pressed")
        report.append("IMPORTANT: Octane only compiles an OSL camera while the Live Viewer is\n"
                      "  rendering through it. Start the Live Viewer, then press Compile shader on the tag.")
    else:
        c4d.CopyStringToClipboard(OSL_SOURCE)
        report.append("Could not fill the OSL Code field automatically.\n"
                      "The shader is on your clipboard: click the Code field on the\n"
                      "OSL Camera tab, Ctrl+A, Ctrl+V, then press Compile.")

    ptag = None
    for t in cam.GetTags():
        if t.GetType() == c4d.Tpython and t.GetName() == "XenoCam":
            ptag = t
    if ptag is None:
        ptag = c4d.BaseTag(c4d.Tpython)
        ptag.SetName("XenoCam")
        cam.InsertTag(ptag)
        doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
        report.append("XenoCam tag added - all controls are on it")
    else:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
        report.append("XenoCam tag updated (your settings kept)")
    ptag[c4d.TPYTHON_CODE] = TAG_CODE
    icon_pid = getattr(c4d, "ID_BASELIST_ICON_FILE", None)
    if icon_pid is not None:
        try:
            ptag[icon_pid] = str(PLUGIN_ID)
        except Exception:
            pass
    build_tag_ui(ptag)
    _run_before_octane(doc, cam, ptag)
    doc.SetActiveTag(ptag)
    doc.EndUndo()
    c4d.EventAdd()
    gui.MessageDialog("XenoCam set up on '%s':\n\n- %s\n\nDrag an object into the tag's Focus Object field "
                      "to focus on it." % (cam.GetName(), "\n- ".join(report)))


def export_shader(folder):
    path = os.path.join(folder, "XenoCam.osl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(OSL_SOURCE)
    return path


# ------------------------------------------------------------------ dialog
ID_SETUP, ID_EXPORT = 1000, 1001


class XenoCamDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("XenoCam %s" % VERSION)
        self.GroupBorderSpace(10, 10, 10, 10)
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Select your camera, then:")
        self.AddButton(ID_SETUP, c4d.BFH_SCALEFIT, 0, 0, "Set up XenoCam on selected camera")
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 0, "Everything else is on the XenoCam tag.")
        self.AddButton(ID_EXPORT, c4d.BFH_SCALEFIT, 0, 0, "Save the shader to a folder...")
        return True

    def Command(self, cid, msg):
        if cid == ID_SETUP:
            setup_camera(c4d.documents.GetActiveDocument())
        elif cid == ID_EXPORT:
            folder = c4d.storage.LoadDialog(title="Folder for XenoCam.osl", flags=c4d.FILESELECT_DIRECTORY)
            if folder:
                gui.MessageDialog("Saved:\n" + export_shader(folder))
        return True


class XenoCamCommand(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = XenoCamDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, PLUGIN_ID, defaultw=320, defaulth=120)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = XenoCamDialog()
        return self.dialog.Restore(PLUGIN_ID, secret=sec_ref)


# ------------------------------------------------------------------ icon
ICON_PNG = """@@ICON@@"""


def _load_icon():
    data = base64.b64decode("".join(ICON_PNG.split()))
    for folder in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "xenocam_res"),
                   os.path.join(tempfile.gettempdir(), "xenocam_res")):
        try:
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, "xenocam_icon.png")
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


if __name__ == "__main__":
    _icon = _load_icon()
    if _icon is not None:
        try:
            gui.RegisterIcon(PLUGIN_ID, _icon)
        except Exception:
            pass
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "XenoCam", 0, _icon,
                                      "XenoCam cinematic lens for Octane", XenoCamCommand())
