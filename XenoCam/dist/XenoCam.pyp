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
TAG_CODE = _unpack("""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""")


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
    c4d.plugins.RegisterCommandPlugin(PLUGIN_ID, "XenoCam", 0, _icon,
                                      "XenoCam cinematic lens for Octane", XenoCamCommand())
