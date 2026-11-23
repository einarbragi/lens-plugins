import sys, types, math, json
c4d = types.ModuleType("c4d"); gui = types.ModuleType("c4d.gui")
for k,v in dict(DESCFLAGS_DESC_NONE=0, DESCFLAGS_GET_NONE=0, DESCFLAGS_SET_NONE=0, DESC_NAME="name", DESC_HIDE="hide",
               DESC_CYCLE="cycle", Tpython=1, CAMERA_FOCUS=500, CAMERAOBJECT_APERTURE=501, CAMERAOBJECT_FOCUSOBJECT=502,
               MSG_DESCRIPTION_COMMAND=11, MSG_DESCRIPTION_POSTSETPARAMETER=12, Ocamera=5103).items(): setattr(c4d,k,v)
c4d.EventAdd=lambda: None; c4d.gui=gui
answers={"input":"Hero lens","q":True}
gui.InputDialog=lambda *a: answers["input"]; gui.QuestionDialog=lambda *a: answers["q"]; gui.MessageDialog=lambda *a: print("DIALOG:",a[0][:60])
class BC(dict):
    def SetString(s,k,v): s[k]=v
    def SetContainer(s,k,v): s[k]=v
c4d.BaseContainer=BC
class V:
    def __init__(s,x,y,z): s.x,s.y,s.z=x,y,z
    def __sub__(s,o): return V(s.x-o.x,s.y-o.y,s.z-o.z)
    def Dot(s,o): return s.x*o.x+s.y*o.y+s.z*o.z
    def GetNormalized(s): l=math.sqrt(s.Dot(s)); return V(s.x/l,s.y/l,s.z/l)
class M:
    def __init__(s,off,v3): s.off=off; s.v3=v3
class BO:
    def __init__(s,mg): s._mg=mg; s.p={}; s.tags=[]
    def GetMg(s): return s._mg
    def __getitem__(s,k): return s.p.get(k)
    def __setitem__(s,k,v): s.p[k]=v
    def GetTags(s): return s.tags
c4d.BaseObject=BO
class Time:
    def GetFrame(s,f): return 7
class Doc:
    def GetTime(s): return Time()
    def GetFps(s): return 30
sys.modules["c4d"]=c4d; sys.modules["c4d.gui"]=gui
import re, base64, zlib, types
plug=open("../dist/CharacterLens.pyp").read()
logic=zlib.decompress(base64.b64decode(re.search(r'TAG_LOGIC = _unpack\("""(.*?)"""\)', plug, re.S).group(1).replace("\n",""))).decode()
stub=re.search(r"TAG_CODE = '''(.*?)'''", plug, re.S).group(1)
rt_src=re.search(r"RUNTIME_SRC = r'''(.*?)'''", plug, re.S).group(1)
rt=types.ModuleType("characterlens_runtime"); rt.TAG_LOGIC=logic; exec(rt_src, rt.__dict__); sys.modules["characterlens_runtime"]=rt
g={}; exec(logic, g)          # tables / helpers for the checks below
stubns={}; exec(stub, stubns)
ADV=g["ADV"]
IMG={"Enable Imager":1423,"Exposure":1424,"Saturation":1430,"Gamma":1427,"LUT":1478,"LUT strength":1480,"Post":1520,"Cutoff":1539,"Bloom":1521,"Glare":1522}
class PID(str):
    def __getitem__(s,i): return types.SimpleNamespace(id=IMG.get(str(s),-1))
class T:
    def __init__(s,names,ints,obj): s.names=names; s.vals={n:(0 if n in ints else 0.0) for n in names}; s.obj=obj
    def GetType(s): return 999
    def IsAlive(s): return True
    def GetObject(s): return s.obj
    def GetDescription(s,f): return [({"name":n},PID(n),0) for n in s.names]
    def GetParameter(s,p,f): return s.vals[p]
    def SetParameter(s,p,v,f): s.vals[p]=v
cam=BO(M(V(0,0,0),V(0,0,1))); cam[500]=35.0; cam[501]=36.0
pins=["Enable Imager","Exposure","Saturation","Gamma","LUT","LUT strength","Post","Cutoff","Bloom","Glare","F-stop","LensModel","FStop","FocusDistance","Character","Bokeh","SwirlAmount","Softness","Fringing","Distortion","Vignette","PixelLines","Wobble","EyeDistance","Grain","FocalLength","SensorWidth","Frame","Custom"]+[e[1] for e in ADV]
ints={"LensModel","PixelLines","Custom"}|{e[1] for e in ADV if e[1][2:] in {"blades","proj","glass","stereo","port","noDOF"}}
ot=T(pins,ints,cam); ot.vals["LensModel"]=2; cam.tags=[ot]
ot.vals.update({"Enable Imager":False,"Exposure":1.0,"Saturation":1.0,"Gamma":1.0,"LUT":"C:/mine.cube","LUT strength":0.7,"Post":False,"Cutoff":0.0,"Bloom":1.0,"Glare":0.1})
cube=BO(M(V(10,0,450),V(0,0,1)))
class P:
    def __init__(s):
        s.ud={"Lens":2,"F-stop":1.4,"Focus Object":cube,"Focus distance (cm)":200.0,"Character":1.0,"Bokeh":1.0,"Swirl":1.0,
              "Softness / glow":1.0,"Fringing":1.0,"Distortion":1.0,"Vignette":1.0,"Pixel lines (0 = style default)":0,
              "Wobble / gate weave":1.0,"Anaglyph eye distance (cm)":6.5,"_advanced from":-1,"Full character at":"","Use colour correction":False,"Exposure (stops)":0.0,"Saturation":1.0,"Gamma":1.0,"_imager on":False,"_imager backup":"","Film look (grade, bloom, grain)":1.0,"_saved presets":"{}"}
        for e in ADV: s.ud[e[2]]=0
        s.cyc={}
    def GetObject(s): return cam
    def GetUserDataContainer(s): return [(k,BC({"name":k,"hide":False})) for k in s.ud]
    def SetUserDataContainer(s,did,bc):
        if "cycle" in bc: s.cyc=bc["cycle"]
    def __getitem__(s,k): return s.ud[k]
    def __setitem__(s,k,v): s.ud[k]=v
op=P(); g["op"]=op; g["doc"]=Doc()
class OpWrap:
    pass
stubns["op"]=op; stubns["doc"]=Doc()
op.GetGUID=lambda: 42; op.GetName=lambda: "CharacterLens"; op.GetDocument=lambda: Doc()
def run(): stubns["main"]()
g["main"]=run
g["main"]()
P_=g["PRESET_DIFF"]; D=g["ADV_DEFAULT"]
def expect(lid):
    v=dict(D); v.update(P_[lid]); return v
def check(lid, tag):
    v=expect(lid); bad=[(e[1],ot.vals[e[1]],v[e[0]]) for e in ADV if abs(float(ot.vals[e[1]])-float(v[e[0]]))>1e-6]
    print(tag, "Custom", ot.vals["Custom"], "LensModel", ot.vals["LensModel"], "mismatches:", bad[:5])

P_=g["PRESET_DIFF"]; D=g["ADV_DEFAULT"]
def expect(lid):
    v=dict(D); v.update(P_[lid]); return v
def check(lid, tag):
    v=expect(lid); bad=[(e[1],ot.vals[e[1]],v[e[0]]) for e in ADV if abs(float(ot.vals[e[1]])-float(v[e[0]]))>1e-6]
    print(tag, "Custom", ot.vals["Custom"], "LensModel", ot.vals["LensModel"], "mismatches:", bad[:4])
op.ud["Lens"]=6; run(); check(6,"cooke panchro:")
op.ud["Swirl"]=2.0; run(); print("Look Swirl -> SwirlAmount pin:", ot.vals["SwirlAmount"], "| Swirl strength pin:", ot.vals["A_swirl"])
op.ud["F-stop"]=0.1; run(); print("F-stop pin:", ot.vals["FStop"], "| note:", op.ud["Full character at"]); op.ud["F-stop"]=1.4; run()
print("imager before:", ot.vals["Enable Imager"])
op.ud["Use colour correction"]=True; op.ud["Exposure (stops)"]=1.0; op.ud["Saturation"]=0.5; op.ud["Gamma"]=2.2; run()
print("imager on:", ot.vals["Enable Imager"], "exposure x", ot.vals["Exposure"], "sat", ot.vals["Saturation"], "gamma", ot.vals["Gamma"], "owner", op.ud["_imager on"])
op.ud["Use colour correction"]=False; run(); print("imager off again:", ot.vals["Enable Imager"], "owner", op.ud["_imager on"])
rt.LUT_DIR="/luts"
before={k:ot.vals[k] for k in IMG}
op.ud["Lens"]=115; run()
print("night vision:", {k:ot.vals[k] for k in ("Enable Imager","LUT","LUT strength","Post","Bloom","Cutoff","Grain")})
op.ud["Use colour correction"]=True; op.ud["Saturation"]=0.5; run(); print("  + colour correction: sat", ot.vals["Saturation"], "LUT", ot.vals["LUT"])
op.ud["Use colour correction"]=False; op.ud["Saturation"]=1.0; run()
op.ud["Film look (grade, bloom, grain)"]=0.5; run(); print("  film look 0.5: bloom", ot.vals["Bloom"], "grain", ot.vals["Grain"], "lut strength", ot.vals["LUT strength"])
op.ud["Film look (grade, bloom, grain)"]=1.0
op.ud["Lens"]=6; run()
after={k:ot.vals[k] for k in IMG}
print("back to Cooke: restored", before==after, "| grain", ot.vals["Grain"], "| owner", op.ud["_imager on"], "| backup", repr(op.ud["_imager backup"]))
assert before==after, (before, after)
stubns["message"](c4d.MSG_DESCRIPTION_POSTSETPARAMETER, {}); print("stub message ok")
for lid in [i for i in g["LENS_ORDER"]]:
    op.ud["Lens"]=lid; run()
    v=expect(lid); bad=[e[1] for e in ADV if abs(float(ot.vals[e[1]])-float(v[e[0]]))>1e-6]
    assert not bad, (lid, bad)
print("all", len(g["LENS_ORDER"]), "presets send their values; focal untouched:", cam[500])
