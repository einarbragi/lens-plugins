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


OSL_SOURCE = _unpack("""eNqtXHtz27ay/9+fAied6aFetqiH7dhxOo4d35w57mkn7m3vTMaToSXK4jVF0iRlW+3Nd7+/3QVIgJKcR6NpDRLELhb7wmIBZG9P
nXzH387enlL/EybpWbDYTYtYqZ5SD/6uzx9+SUI1iZJwEZTRRMVhUqhZmqtfJmWQhO/DZBrmyvvl6lIBOswDlaTTsLULUIY+VZM4
KApAEg6V5dEiVEVYKm+BdnEcTlWaqHIeqrM0vQvV1WgvUrNgEcWrrvIHvWG/rxaLFuN6nKcFaJkHeTAp0essjeP0sWDoCXf+T6Jt
EsRE5m05P1KP0TQs1C36uwnyPIwZzzQqyjQvozTpqmmQ36lJmidhXnSBpeyFq1DdgJS5CpKpCqe3oDedlUlYFMcqTpNb5oFgZXST
PAwWK4HpgvYoKVUWJZNlMUcXjCVb5lkcqlkeJbf4b1f9HsRLoAhy9BUTD6eM6iYsH8MQ/MD/9kCKip9v8+BI6V8fvA2DRBEn80Td
EqNZdv3dccV2j7hDDA8KZVje4la+egCpwW0ogkqCRZpn82hypNIH9KzHU9wvw/DPsItxmAYWA3l0kxhy6YHeZaFeLJaLrHjBKC+i
Yg5uMr3h/TIq0jiaqpnUQhXS/w0nhOSYJWiPVxVlFMdENkuXsdm/WRTGUJwZRhA+Ku+w54+hJWq2BJDG32VZQUtOIKikBPcfgzwT
RbpaZmF+eKSZmM5mYIcv0PxJHQLxTai826AEXBg8AF2eLklOiuq6rBJQxTDI1ohjOXTVbQ5N6KrwKUuLJeQ8i6PJXZh3iY4FNK0o
oX1hmClmnBD29iHMV+UcKqLCGLq+WMZllMVRKErO8lOejzFBmtDs6DaBNCvlOM+jB2jOzYpba4tWELHybO6CemhwClK4axQ5rIfR
QGgsRpJwkExCFRUqStTZ6FxNwEUYb5mHxa7610xFpXpMk3+CC+kii2LiiTaI/756+/Hq17dnv70/vVRlCnWk6u/qsXZ+mIYzcihO
Xz7qo5lTh4pkEi+noXqVssfqwcFB7WGJu/PXOz/A9qLZDtF3CsGXJKh0WcaEOg+mEVgRwHSSW+gPVF94P4lyGF5rV/2axqtbGIE2
YRprQKikAcmBlYZcx+7OLE4Jle7lPSM/LT2pBu6uIsdxEweQK0TC1RV4XVG2dv7aITXDQD1prV6pYWvHqF8eAn+i/N3+MdcJYBHe
gvLBbl+11c8ff/2X2lPSdUtw2G0DPJ2Qsnk05B51SsK9beGZXEubXhzkDDBJC6/63EIHVBG0pKGmahE9eRgMiOuSh1pknjXEPtXi
Uwswn1gmb59KzCjTEA4azhuGN4VUkmm6UMlycQOXjW+k8/AqOSplTsIkUD6mMlNJ64r7eTLVDA8MR2/Mw51hrCZ1AleZpFERelkK
yRBcmnsBhrc/Hg/3QSZDou7GqbvDm39gj+K7an4xD2jG1cbtMcXoo9f4qUsa/o9i4WtfLdldXJVpplXjwwc4XpqjVBzcwNOcqBcX
Pbj67IVh0gLO4ISUoKoInlCxPzLvMC6QJ838RiU3HQzU9XXXIuAPmqLLyvq2UiLtKgP6HElr/bBjOzd+DQ36mwfs+j9vsmg1uvLd
jvw+/xq9vUFQII6caHumpxvTsNFLb+h2M6w6IDdRTa6E3kKOeIeCHWDH3DS5e5M+vajgNmoJgq7ntOOsCrZOyDKpJ4fr22iUWgQr
IprPwPmNsdWxyFcMTxBeSbhSq9EzkmuSK2FBLbAvongTV99w+LiRrTLAN+K3TxBooB+qq3rhFyGvqcHvjatkEg++nKtalkH5lhXm
6wXJA3ofLTbzpud/DXP+CzE7HBMF1s86Jm73JcSOG8S+C/4Mvwnw6jHK42+CfIvBXOlFwjchOK8j6o3gTW/QhP8tisstwhk1HONo
/Kx4ztI4XebPzhh6FfNFA/WbjvFXXgr9PRy/U9xblt+my38g/MYK4ys1uZbzGSL3r5TxJj6fLhEtehy21OvXLtYdAb8jaG89KwSK
5y9lsYSuPufqBusz1BWvATCrMobh/mcwHDbhL2jRYPyzy0SeEDfNkoyCcSDIzpaIe1N2iFgiKWag/e0Bq0MkGqZRvv5NUKvyZ0G+
29+DNE0At4HdX/UzUaM12Gk6+zC4Rld/SaRBc9oniWwxIQUlpqebZRl6L0SOR2gvSDCr47llR8s5rSEIYf/aqR7oat+pvv/gH5oK
cMMjfkXEj2MUr5R/iLLTqcP/+w8R0UmRbg4R5oOuCfS9SHWU39K0gEn3R5RCEHvPsDhV/6eGvX0zDZqkB2qRh/FHak5+FS/jrr8P
qcxmFBnAY+18PdNZxTlAx5qxSwsle31q8Fk/fyDFIReDMRdDKaD89DvgN+gZF/LNP+Q3SSLZunv6we9f86rlL+CmdQfacjEYczGU
YsxrEuDmpUlfVijyDbipGFKl0QXBXmKmZfxaXQ67nJLpczEacDHcl0IqB2Mp5M0XAF+aYOgudszD7wk9077bHxHtu/2xFIdc+H0p
BlJIE1+aMFoUB1wM+uvYK9p7fUZPxViKQy4IPRUDKaSJL00IvVWMG+ivHmOLNf0DHmJfRspDQTGUYvD5wm9i13LV2McOds1VzWPB
4Etf/mhT0WT8WboIDONrYY1ttGZA4y8YSQP7aWErTSV8m/YvQrsZ+8WZzZlnaR99Pe3/9h2+j9hD9km5SUjyRmOgYiia1B/oUiuY
0bD+vi4Pmn0M6j6ogVbCGmCgMwhisvJ3a9FAfmlZLIxCGr2UYl+K0Xi7xTaKptJfIhNZK85QQEd92y3sS3EgxaEUL8WM+33bqIdN
2q/CiaU4TVJsonWXeiS65/HYJaCJPZtb2DUiU2waiYuvWTSwI5Kz+K49VF8zQRAdOPjGzkiGDZms+WGxKa2WLx1b2ndMylX6zUUD
O60zLOwDUb2Bo/Ru4TYxhTEWQm/hn9FSRHJkVrDXpbmrf83Fy2s9l8uiMupzWOCGCncUHh2jeKVeorAjBUogopPXJ4Tr7rolCO7s
MT5WJHhxeovWlAKkJ0BE/esWZfm86p3Ci+tmCyutd1xlbS9/Q2KQk4EBtcLmggFHery1812iOAk0kIKwxhOqakBvKdq2SLMa/Y5G
Xqhek7q11E/03JPnNmcVjgjuWHMRZOptFIWkxTIpbUxngulVhYnixp4Kt2GS/Zx1PD9TPhbc8sW/QSHDM8JR1Q247vfWsUaEHFOe
B7yerPYQcgvjhGJ+ROZeleBhZrSO1cYfMC5gS0gDadr+joQk8HuQHTDvqc4xtSxl1pltDtHerGWocysTUmVF7AYTyXUwOJSNIjKH
X+zVGzz0ue53qtOpkjb45HSLyEs2BQQrRWKtRoM3USDpcE+3kKy5D2SCG6zvVAkVJ4vO6QdVAyNWaqEt5F0BS4qiSVcRGEEZyFNq
DLXp8CxfgXNOpQmN/ZvAQDOv8K7B225mowkJlYhuLUiEMF8GOJvUBBPgxdmXwd35Lty//YYEx0aCVkJlDcmggWTwDUiwGXF2aiG5
DOqhV8mNNSDEAQKlgfBeQTUSI2syDidOh5j1vxg0m7ug2fxLQZOApugaFC8NZg0Ms6qkzJp+QU1OF6Vli0XTGDc5tL5BXCVdmogf
JZMjas96XhtLbXRnldFJ5sfGwEta23BoTt9MW4dDh8qSOMnYJIjQXWVI6E8lvSQE9YUiuyE874Xpl7ywuwfC6QXHr1wpy8Ct7Pg/
0A3NK4TjymzU03yGmYU3AI2ftjbveXv6iJf35PVRHZoN/VDOOxTV/uJaV39V0YP2sJ0TXkBs8pn00wbLrbBq2GJSPNCJ1XK83RHQ
T/sdaXv4fFttqNx22N9snZ++W8Shkye28R1WIYd82xZ10FYn2RoPylFzOn+wXs1nE9Zqi0M+mWDVU4InVyVNqyfy4tV9k5BB4Wue
/C3pmhlF2MZ7uoc1TyuzEe2lVx7VAbdr1VrfBKqMw4BJBQPvC9hIcNRwxgUxKfsNpBbXfN7btj8aHw3I4fpH7Ys7BDlofDTzE/c5
anw0k1Ct1PZX45T466DJOeMLa7NxYFnSzFe7miUt1ZyVcIG0xOUrlte6S7U1kptF8aKXxdgpR5SF1J/H8MUiiOPebbBEIBstEM7W
C4VSQjKlg9Bah7q1Pu3rTX0s20aorySoTUuUkEaP/QVyYppNr5nouquftvfAuNl6DgaoR65ZI9FnBiocR1twAPDQIJF6wtFzkBx/
uyeA5B9CfXxpj06pJQnOm9UR7WSeU6BFyzG7dqInMN9ZW6pK3v3jdQl6cCc30wBz3HjcTxa0CvPpwbb3ea70qYza4tcOx1hOJv4w
uq59QiOpTTiO6vEVyGojNrUdBqelp5SMp2VnizgrhyPusVqFRo6Y4cPK8bBeyXyGrgF5LaMhN8SjMe6LG85p//ljkWFHIF8uPO6I
dh5+IryyiuoqXes7tTtb7MC0HmzEMbRrjSbLkSxrBjQCHRhV/4Fa7DS/6TNGhrXmE7458ykvyTYzb8jMGzjMY1QEw/My//5S5OI5
O3KseSbSH1ZpMVnjfar9Jw3JQoV4usLSb2CRdPdWLO5PsCAvNz7YgMWgqrD8zRmYfRo6SPNphPnCRDBsYTivhq0b27qyQKaLZ/Zv
AJTGSwpToOp4aT3TNouecDaJlRONs6DlLpGoniQrmzBEDWQKG7YqfBIyA9rBJBuTnNha0gFFMo22Rni85hPmYXQ7L9UyiUpEd/MV
Hdv7gP1M/9rGuapxPmicTgD7RCmg+ZNTt+K6lVN3QQcwacPKA5ltorVDyPG04pyQHrYhl1I7OrsAUvkMHR+5tcQUxBFHOb4b+vCg
TqxgdlvEArz1ac066HiiqVbm1TZn4mjocqzrBaIxHPQjmfEBL9nQpFajYdds8/Vbls1hhN+I7WADNlBsnyk1p5DrIETCvPsnHS/N
gpsC7KZ8guFvjyFbXctN2ZArB3LFkBQmbQFjx39P8qS/HUbQ5r+vhcK2wFWy6juD2RxGNESho5W2gm8bXqOTe8w7tXYPbLcv7LYh
xgKxvw2ClICO3cKfxTiHHCKypImYTpqEdLRWn3SVk92Ng7lN7pHL2ixashJ0vM9ejMyjejFCP9gd+raotR63RRwkgg7n4TlUI7bm
TVnUEKa1jq4/q3D+7oFetr7crYj4ZHuWp4SNHHa67kzAwUc+EsCOhNJzlR9pWShWjGJVo/guK6hqW9hOFdUrX/vMA5tf33czJHyg
gVpaZxvc9Xk8+0PH17qx4OmPHURPVZdPtExlMKfBqmqwqhpQdq7Z2XkU0NLEfC/u81JL37uqeEdabL86HvkdWX9BsjL4nK9k4cVq
y9c5Oeh3ZM/vyJzfkTW/c/04s4Komg/c2ee8Xt65ByfF7+FwB6ta381TPEQLGi99O6dp4Bx26h5+eHiL0/baK1EetDomCR4wNAGQ
/tIyxwX9z6wmiQ6tdjmN0tqY5OBbCEesT/oCg5rmacanufm6gjn6XqSqWN7QRQRcHcHcHiZ22oVCsqvjremQylq5YSXYyjdpZys5
KckB0BJ2T527h53NALIlDtJj7b2gyyIeksnqhrLJCBHmOPYqdwBucnIMnOjADQrEPaFtl3fwaqo66J2lj97IOmot2Wlsl/pW51b2
ep4yhwmMuEznR/ywd9DitiCbsDsQdD5cuefK2zhy4tgKkU4XFpoH3/nIuznu7p4C133UPlCQtKV0wqvsPe1yUCDCObU9aEkzfzeW
5ajt4vQtjyOZrhRPV/ZtDHuIZIDEmXZFBZ1rB/Ucjen+91zbz1ZrQAWCeheoljtn/o/4wgEOwUBhg2JOt1tI3qIT5ZynJL7tlGLF
OuVvlKxzNhDImvUOwXxgZXgeJV5SP/4Ik39NQh3bsZPJQIm7gDNphhIhjefdatOnjObJjJxMSE4mIycTrtZa8WpAmq2qZk/NZhNj
4GI4xWOX9y+seRHdQR8mmyZKq5KFRk2JqB717hLF8pHvTE1pUVMvRcxtsD2VZrj7BtE8SI4b/uqI7xjIpTLa9inkkLsKJnlaFLXk
LPGkRNTEZEnfOUF2unK+OU46Jw7XW0/t+rmWsJfRONMn9jrVM7wRRornldSb59fAuRbFGTQdC03HQtOx0HQ2ozGMuwojuqhUb0Ii
kBA9TlJcA4gRvvBlGbqdB96Gie3CMnZgrCpZpVGZw5HsXdXkXdXEZVoRXJLGFYFxwx29DdJWpbtAe/pIVoPmbepad8p7Ym2zVEJ/
hpiM+6Q1zpCRSipaN2FikDsk62MIp6NVs6PVlo5WVUerbR2t3I6coQdXUFWdGvb5No4d6jgh07QgnSQWtDWY+5W0kuiuvxoRW+f/
ZCshoUncExeFOWuVLhXdHMGJxkdHvNNC57hHRDkyPmHvZS0jzPsHLCL8+c/MIeZWVcFKT7hFxwzIWeCI5PhaT1VmRit4tcGdtQlW
vLYzTwFs35ygKFbN5uSvNzavOVDtZHh3mDnE6OdpHv2Z4jxA7F5SJCuiC0w5PpydOvzQ0hIG3Pki1A5tU2rxzp0JNZRlN4eUddzH
lrlWKXC6i70Tw2XuJKw6CeWP27paeUgWXSsPycZJVJL+XFE4XpA1mp44zHPa6UB1rYnhJqXjo3JJ6ZuYbBVXvhLczV2BWdiigoPR
V0ThAGnqrnORNisfdOxpSPV0kh9EC05+9kqu4LhsOHRDoIdYT0Aci3aAsop0gdJpeh7r3gCDUBd/Jda1L2zI2ecZfRdd0hErz0Fy
9PlS3B0v4dijEVBXXJo81gGRBrlQNUidTuudxw59ajJQdp5L1y4Y+JxopjFaWRVzo6i508dbBvLJq67xImSjuG/GdgLZlMHeoNU6
ouC1cZWX1tr6vqmbLRCROjd55drv+r3uXTpt25uGt3mo0wr6juVuI4DI742PKImXJTnkklhZrjadbQEdgk3f9cRInWwI0LX5rPdr
Php34Pf3D+0ZbxPCm3AF1eWjx0JwM6PD5+1FHQLiHqV7TUddq5+1hM6SM4JoyhHcIW38lhSuoeZIOQlz3X613n61sX191P4CIPLm
iWTJsSyhhdYbbub3yJvi1aLxYpNScpKuI4jbpHUdg33KDuOKbKLLMw0/9Oss4WSZ88VOtnlWk2awyOtbIUS4Z1Ez4W/sPvF3227Y
uvT0XXGj8DPKZuGC+OYdALIMcUm8m+bxLRyoMNaSuB1Nsx+CnJu0LNNFa43XNaNLsLdcybKstSaUpG5Y89VfS9xx3/84aaZFrbCA
0q68xEgKbm0h4H3WRj89knjg8/ZZQQ9W+08NUUwTvrtQevALyZrelpL/piTkNGmJNu6TNhLE2tDIjxEWKCrQHkFp3IEC2ys9TEZs
f6cLaqg0rq1WTaOZJfn+KWXgO8rRQP3Blw8rp3Jw3VQsWQ7r2XSDp9mpmWTEDUdGKSxMEpdZPe1hs2KZOwsL5XXM8hQXmfEPDMAx
5pUethoL42qdO2FNH5ilvmya21kGnQ6gJmbT3ApmHsIops5pT/4IF8Cr2A6eOQ9WWN1MKDmC838qjkpYSDVr8FmAanWJIAnXZF4x
HlsNDReSj5xV5UXAn6FHXFnXeLl/bhTm4wc6VEpHKF+Sztj64lcu5sjU++5WVxP1ja8cAni1Rp3gCGprQ3OeQq1GN/6admNZPtge
mA6bgSmHWKIMxI2OfS6izbgQoWyKVUfXJEMMoLMxNtWfB27ClyQk01VzVqcrVzAW3FIqcFh4YXazkE5+8Zjm8RQPl5lNc5R/rn1D
mpRKll1+OkAg0zn+CRf+d1AAe1ylMPhcgAqm00JOI1kZjuaeSH2O4DdeMMt5gvb6jr98MeZgjl20q50r3pF2s3DVgYqwXCAThbDA
eyH/ZsQRNjDT5e0cN88wTNrNbFc2qIlp8yC3bRXr+22/uux0HK69Ly632qoZ+tPOp53/BzVDrtM=""")
TAG_LOGIC = _unpack("""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""")

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
    real("Widest aperture", g, 2.0, 0.5, 22.0, 1.0, 5.6, 0.1)
    _add(ptag, "Full character at", c4d.DTYPE_STRING, g, "", gui_=getattr(c4d, "CUSTOMGUI_STATICTEXT", None))
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
ICON_PNG = """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
5BRO4RTqwn8Bu2XBvqHbwhYAAAAASUVORK5CYII="""


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
