"""XenoCam for Cinema 4D + Octane  -  v1.3  (single-file plugin)

Install: put this file in your Cinema 4D plugins folder
         (Edit > Preferences > Open Preferences Folder... > plugins), restart.
Use:     select a camera (or nothing) and click Extensions > XenoCam,
         or add the XenoCam tag to a camera from the Tags menu.

One cinematic lens: a classic cine prime set (12-300 mm) whose character
follows the camera's focal length, with an Era dial (modern - classic -
vintage), a spherical / anamorphic switch and a Super8 slider. Every control
lives on the XenoCam tag on the camera.

Plugin IDs 1000005, 1000006 (tag) and 1000004 (auto set-up) are from Maxon's
free test range (1000001-1000010); CharacterLens uses 1000007-1000009. Before
sharing it widely, register free permanent IDs at developers.maxon.net.
"""
import base64, os, sys, tempfile, zlib
import c4d
from c4d import gui

PLUGIN_ID = 1000005
VERSION = "1.3"
OCTANE_CAMERA_TAG_ID = 1029524


def _unpack(blob):
    return zlib.decompress(base64.b64decode("".join(blob.split()))).decode("utf-8")


OSL_SOURCE = _unpack("""@@OSL@@""")
TAG_LOGIC = _unpack("""@@TAG@@""")

# Fallback only (if the XenoCam tag type can't be registered): a Python tag that
# carries just this stub; the logic runs inside the plugin either way.
TAG_CODE = '''"""XenoCam camera tag. The controls are on the XenoCam tab; the logic lives
in the XenoCam plugin, so this tag needs the plugin installed."""
try:
    import xenocam_runtime as _xc
except ImportError:
    _xc = None


def main():
    if _xc is not None:
        _xc.run(op, doc)


def message(msg_type, data):
    if _xc is not None:
        return _xc.message(op, msg_type, data)
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
        ns = {"__name__": "xenocam_tag"}
        exec(compile(TAG_LOGIC, "XenoCam tag", "exec"), ns)
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
    mod = types.ModuleType("xenocam_runtime")
    mod.TAG_LOGIC = TAG_LOGIC
    exec(RUNTIME_SRC, mod.__dict__)
    sys.modules["xenocam_runtime"] = mod
    return mod


_xc_runtime = _install_runtime()


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


def build_tag_ui(ptag, old=None):
    """(Re)build the XenoCam controls, keeping any values the tag already had
    (or those of a replaced tag, passed as `old`)."""
    if old is None:
        old = _old_values(ptag)
    for did, _bc in list(ptag.GetUserDataContainer()):
        ptag.RemoveUserData(did)
    # wipe the stored values too: Cinema 4D keeps them by slot number, so a
    # reordered control would otherwise inherit an old value of the wrong type
    try:
        ptag.GetDataInstance().RemoveData(c4d.ID_USERDATA)
    except Exception:
        pass
    R, L, G = c4d.DTYPE_REAL, c4d.DTYPE_LONG, c4d.DTYPE_GROUP
    SL, LSL, BTN = c4d.CUSTOMGUI_REALSLIDER, c4d.CUSTOMGUI_LONGSLIDER, c4d.CUSTOMGUI_BUTTON

    def real(name, parent, d, mn, mx, smin, smax, step=0.01):
        _add(ptag, name, R, parent, d, mn=mn, mx=mx, smin=smin, smax=smax, step=step, gui_=SL)

    top = _add(ptag, "XenoCam", G, c4d.DescID(0))      # its own tab, not "User Data"
    g = _add(ptag, "Lens & focus", G, top)
    _add(ptag, "Fisheye", c4d.DTYPE_BOOL, g, False)
    real("F-stop", g, 2.0, 0.5, 64.0, 1.0, 22.0, 0.1)
    _add(ptag, "Aperture", c4d.DTYPE_STRING, g, "", gui_=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))
    _add(ptag, "Focus Object", c4d.DTYPE_BASELISTLINK, g)
    _add(ptag, "Focus distance (cm)", R, g, 200.0, mn=1.0, mx=1000000.0, step=1.0)
    real("Focus breathing", g, 0.0, -3.0, 3.0, 0.0, 1.5)

    g = _add(ptag, "Look", G, top)
    real("Character", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Era (0 modern, 0.5 classic, 1 vintage)", g, 0.5, 0.0, 1.0, 0.0, 1.0)
    _add(ptag, "Format", L, g, 0, gui_=c4d.CUSTOMGUI_CYCLE, cycle=[(0, "Spherical"), (1, "Anamorphic")])
    real("Anamorphic squeeze", g, 2.0, 1.0, 3.0, 1.0, 2.0)
    real("Super8", g, 0.0, 0.0, 1.0, 0.0, 1.0)
    _add(ptag, "Reset look", c4d.DTYPE_BUTTON, g, gui_=BTN)

    g = _add(ptag, "Bokeh", G, top)
    _add(ptag, "Aperture blades (0 = round)", L, g, 8, mn=0, mx=32, smin=0, smax=16, step=1, gui_=LSL)
    real("Blade roundness", g, 0.75, 0.0, 1.0, 0.0, 1.0)
    real("Cat-eye", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Bokeh rim (- creamy, + soap bubble)", g, 0.0, -1.0, 1.0, -1.0, 1.0)

    g = _add(ptag, "Glow & edges", G, top)
    real("Glow", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Haze", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Swirl", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Edge softness", g, 1.0, 0.0, 5.0, 0.0, 3.0)
    real("Distortion", g, 1.0, -3.0, 5.0, 0.0, 3.0)
    real("Focus plane tilt (deg)", g, 0.0, -45.0, 45.0, -10.0, 10.0, 0.1)

    g = _add(ptag, "Colour", G, top)
    real("Fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Purple fringing", g, 1.0, 0.0, 10.0, 0.0, 3.0)
    real("Vignette", g, 1.0, 0.0, 3.0, 0.0, 2.0)
    real("Warmth", g, 0.0, -1.0, 1.0, -1.0, 1.0)
    real("Edge colour cast", g, 1.0, 0.0, 5.0, 0.0, 3.0)

    g = _add(ptag, "Tools", G, top)
    _add(ptag, "Compile shader", c4d.DTYPE_BUTTON, g, gui_=BTN)
    _add(ptag, "Copy shader code", c4d.DTYPE_BUTTON, g, gui_=BTN)
    _add(ptag, "Save shader to a folder...", c4d.DTYPE_BUTTON, g, gui_=BTN)

    for gone in ("Full character at", "Aperture", "Widest aperture"):
        old.pop(gone, None)
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


def _cam_focus_object(cam):
    """The Focus Object set in the camera's own Object settings, if any."""
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


def _inherit_focus_object(cam, ptag):
    """Copy the camera's Focus Object into the tag's Focus Object field, but
    only if the tag's field is empty. The tag's own choice always wins."""
    for did, bc in ptag.GetUserDataContainer():
        if bc[c4d.DESC_NAME] != "Focus Object":
            continue
        try:
            if isinstance(ptag[did], c4d.BaseObject):
                return None
        except Exception:
            return None
        obj = _cam_focus_object(cam)
        if obj is not None:
            ptag[did] = obj
        return obj
    return None


def _run_before_octane(doc, cam, ptag):
    """The XenoCam tag must run before the Octane Camera tag, or Octane reads
    the focus distance from the previous update. First on the camera, early in
    the expression pass (still after animation)."""
    if cam.GetFirstTag() is not ptag:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, cam)
        ptag.Remove()
        cam.InsertTag(ptag)
    if ptag.GetType() != c4d.Tpython:
        return                                   # the XenoCam tag sets its own priority
    try:
        pd = ptag[c4d.EXPRESSION_PRIORITY]
        pd.SetPriorityValue(c4d.PRIORITYVALUE_MODE, c4d.CYCLE_EXPRESSION)
        pd.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, -100)
        ptag[c4d.EXPRESSION_PRIORITY] = pd
    except Exception:
        pass


# ------------------------------------------------------ set up a camera
def _status(text):
    print("XenoCam: " + text.replace("\n", " "))
    try:
        (getattr(c4d.gui, "StatusSetText", None) or c4d.StatusSetText)("XenoCam: " + text.split("\n")[0])
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
        report.append("new camera '%s' made from the view" % cam.GetName())
    otag = _octane_camera_tag(cam)
    if otag is None:
        doc.EndUndo()
        _status("no Octane Camera tag could be added to '%s' - is Octane installed?" % cam.GetName())
        return
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, otag)

    bc, pid = _find(otag, "Camera type")
    if pid is not None:
        for k, v in bc.GetContainer(c4d.DESC_CYCLE):
            if isinstance(v, str) and v.strip().lower() == "osl":
                otag[pid] = k
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
        _b, comp_pid = _find(otag, "Compile")
        if comp_pid is not None:
            try:
                c4d.CallButton(otag, comp_pid[comp_pid.GetDepth() - 1].id)
            except Exception as e:
                print("XenoCam: Compile button failed:", e)
        report.append("shader set; Live Viewer restarted to compile it")
    else:
        c4d.CopyStringToClipboard(OSL_SOURCE)
        report.append("could not fill the OSL Code field - the shader is on your clipboard: paste it into "
                      "the OSL Camera's Code field and press Compile")

    # the XenoCam tag: the plugin's own tag type, or a Python tag if that type
    # couldn't be registered; an old Python XenoCam tag is replaced (settings kept)
    ptag, old_py = None, None
    for t in cam.GetTags():
        if t.GetType() == TAG_ID:
            ptag = t
        elif t.GetType() == c4d.Tpython and t.GetName() == "XenoCam":
            old_py = t
    old_values = None
    if ptag is None and _TAG_OK:
        ptag = c4d.BaseTag(TAG_ID)
        ptag.SetName("XenoCam")
        cam.InsertTag(ptag)
        doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
        if old_py is not None:
            old_values = _old_values(old_py)
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, old_py)
            old_py.Remove()
            report.append("old Python XenoCam tag replaced (settings kept)")
        else:
            report.append("XenoCam tag added")
    elif ptag is None:
        ptag = old_py
        if ptag is None:
            ptag = c4d.BaseTag(c4d.Tpython)
            ptag.SetName("XenoCam")
            cam.InsertTag(ptag)
            doc.AddUndo(c4d.UNDOTYPE_NEW, ptag)
            report.append("XenoCam tag added")
        else:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
            report.append("XenoCam tag updated (settings kept)")
        ptag[c4d.TPYTHON_CODE] = TAG_CODE
        icon_pid = getattr(c4d, "ID_BASELIST_ICON_FILE", None)
        if icon_pid is not None:
            try:
                ptag[icon_pid] = str(PLUGIN_ID)
            except Exception:
                pass
    else:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, ptag)
        report.append("XenoCam tag updated (settings kept)" if _has_controls(ptag) else "XenoCam tag added")
    build_tag_ui(ptag, old_values)
    focus = _inherit_focus_object(cam, ptag)
    if focus is not None:
        report.append("Focus Object '%s' taken from the camera" % focus.GetName())
    _run_before_octane(doc, cam, ptag)
    doc.SetActiveTag(ptag)
    doc.EndUndo()
    c4d.EventAdd()
    if ok and not _restart_live_viewer():
        report.append("start the Live Viewer to compile the shader")
    _status("set up on '%s': %s." % (cam.GetName(), "; ".join(report)))


def export_shader(folder):
    path = os.path.join(folder, "XenoCam.osl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(OSL_SOURCE)
    return path


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
        print("XenoCam: could not restart the Live Viewer:", e)
    return False


def _hook_setup(doc, cam=None):
    setup_camera(doc, cam)


def _hook_copy(doc):
    c4d.CopyStringToClipboard(OSL_SOURCE)
    _status("shader code copied - paste it into the OSL Camera's Code field and press Compile")


def _hook_export(doc):
    folder = c4d.storage.LoadDialog(title="Folder for XenoCam.osl", flags=c4d.FILESELECT_DIRECTORY)
    if folder:
        _status("saved " + export_shader(folder))


class XenoCamCommand(c4d.plugins.CommandData):
    def Execute(self, doc):
        setup_camera(doc)
        return True


# ------------------------------------------------------ the XenoCam tag type
TAG_ID = 1000006          # Maxon test-range ID
AUTO_ID = 1000004         # Maxon test-range ID, for the auto set-up message
_TAG_OK = False
_AUTO_ASKED = set()

_RES_FILES = {
    "res/c4d_symbols.h": "enum\n{\n\t_DUMMY_ELEMENT_\n};\n",
    "res/description/Txenocam.h":
        "#ifndef _Txenocam_H_\n#define _Txenocam_H_\n\nenum\n{\n\tXENOCAM_DUMMY = 1000\n};\n\n#endif\n",
    "res/description/Txenocam.res": "CONTAINER Txenocam\n{\n\tNAME Txenocam;\n\tINCLUDE Tbase;\n}\n",
    "res/strings_en-US/description/Txenocam.str": "STRINGTABLE Txenocam\n{\n\tTxenocam \"XenoCam\";\n}\n",
    "res/strings_en-US/c4d_strings.str": "STRINGTABLE\n{\n}\n",
}


def _write_res():
    """The tag type needs a description resource; write it next to the plugin so
    XenoCam stays a single .pyp file."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xenocam_res")
    for rel, text in _RES_FILES.items():
        path = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path).read() != text:
            with open(path, "w") as f:
                f.write(text)
    return base


def _guid(node):
    try:
        return node.GetGUID()
    except Exception:
        return id(node)


def _has_controls(tag):
    for _did, bc in tag.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == "Character":
            return True
    return False


def _walk(obj):
    while obj is not None:
        yield obj
        for o in _walk(obj.GetDown()):
            yield o
        obj = obj.GetNext()


class XenoCamTag(c4d.plugins.TagData):
    """Runs the XenoCam logic with no code tab."""

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
            _xc_runtime.run(tag, doc)
        except Exception as e:
            print("XenoCam tag:", e)
        return c4d.EXECUTIONRESULT_OK

    def Message(self, node, msg_type, data):
        if msg_type in (c4d.MSG_DESCRIPTION_COMMAND, c4d.MSG_DESCRIPTION_POSTSETPARAMETER):
            try:
                _xc_runtime.message(node, msg_type, data)
            except Exception as e:
                print("XenoCam tag:", e)
        return True


class XenoCamAutoSetup(c4d.plugins.MessageData):
    """A XenoCam tag added by hand sets up its own camera."""

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
                        _status("the XenoCam tag only works on a camera - removed it from '%s'" % obj.GetName())
        return True


def _register_tag(icon):
    global _TAG_OK
    try:
        base = _write_res()
        res = c4d.plugins.GeResource()
        if not res.Init(base):
            print("XenoCam: tag resource not loaded; using a Python tag instead")
            return
        _TAG_OK = bool(c4d.plugins.RegisterTagPlugin(
            id=TAG_ID, str="XenoCam", info=c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION,
            g=XenoCamTag, description="Txenocam", icon=icon, res=res))
    except Exception as e:
        print("XenoCam: tag type not registered (%s); using a Python tag instead" % e)
        _TAG_OK = False


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
    _register_tag(_icon)
    _xc_runtime.HOOKS = {"copy": _hook_copy, "export": _hook_export, "setup": _hook_setup}
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "XenoCam %s" % VERSION, 0, _icon,
                                      "Add XenoCam to the selected camera (or a new camera from the view)",
                                      XenoCamCommand())
    if _TAG_OK:
        c4d.plugins.RegisterMessagePlugin(AUTO_ID, "XenoCam auto set-up", 0, XenoCamAutoSetup())
