
import c4d

def _ud(name, default):
    for did, bc in op.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == name:
            return op[did]
    return default

def _camera():
    bd = doc.GetRenderBaseDraw()
    cam = bd.GetSceneCamera(doc) if bd else None
    if cam is None and bd:
        cam = bd.GetEditorCamera()
    return cam

def _snap(obj, parent_mg, cam_mg, inv_cam, step_x, step_y, dz, k):
    mg = parent_mg * obj.GetMl()
    if obj.CheckType(c4d.Opoint):
        inv = ~mg
        pts = obj.GetAllPoints()
        out = []
        for p in pts:
            c = inv_cam * (mg * p)
            if c.z > 1e-3:
                sx = round(c.x / c.z / step_x) * step_x
                sy = round(c.y / c.z / step_y) * step_y
                z = c.z if dz <= 0 else max(round(c.z / dz) * dz, dz)
                s = c4d.Vector(sx * z, sy * z, z)
                c = c + (s - c) * k
                out.append(inv * (cam_mg * c))
            else:
                out.append(p)
        obj.SetAllPoints(out)
        obj.Message(c4d.MSG_UPDATE)
    child = obj.GetDown()
    while child:
        _snap(child, mg, cam_mg, inv_cam, step_x, step_y, dz, k)
        child = child.GetNext()

def _touch(obj):
    obj.Touch()
    c = obj.GetDown()
    while c:
        _touch(c)
        c = c.GetNext()

def _clone(child):
    # fresh polygon copy of a child every update (no cache), so the snap follows camera moves too
    tmp = c4d.documents.BaseDocument()
    src = child.GetClone()
    tmp.InsertObject(src)
    res = c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, [src],
                                        c4d.MODELINGCOMMANDMODE_ALL, c4d.BaseContainer(), tmp)
    out = res[0] if isinstance(res, list) and res else src
    out.Remove()
    out.SetMl(child.GetMl())
    return out

def main():
    first = op.GetDown()
    if first is None:
        return None
    root = c4d.BaseObject(c4d.Onull)
    clones = []
    child = first
    while child:
        clone = _clone(child)
        _touch(child)
        if clone:
            clone.InsertUnderLast(root)
            clones.append(clone)
        child = child.GetNext()
    cam = _camera()
    if cam is None:
        return root
    lines = max(int(_ud("Grid lines", 240)), 8)
    dz = float(_ud("Depth steps (cm)", 0.0))
    k = max(0.0, min(1.0, float(_ud("Strength", 1.0))))
    rd = doc.GetActiveRenderData()
    w, h = float(rd[c4d.RDATA_XRES]), float(rd[c4d.RDATA_YRES])
    tan_x = (cam[c4d.CAMERAOBJECT_APERTURE] * 0.5) / max(cam[c4d.CAMERA_FOCUS], 0.01)
    tan_y = tan_x * h / w
    step_y = 2.0 * tan_y / lines
    step_x = step_y                      # square pixels
    cam_mg = cam.GetMg()
    inv_cam = ~cam_mg
    gen_mg = op.GetMg()
    for c in clones:
        _snap(c, gen_mg, cam_mg, inv_cam, step_x, step_y, dz, k)
    return root
