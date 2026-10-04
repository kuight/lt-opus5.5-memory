# lt_mech.py  机关测试台：卷帘门+按钮 / 吧台翻板 / 冰柜门 / 穿透暖帘
import struct, math, lt_colors, lt_root
ROOT_NAME="测试台"   # 根层 structure 的 name
FLAP=90      # 翻板 rotZ 角度（正负由源码确认）
FRIDGE=90    # 冰柜门 rotY 角度（正负由源码确认）
def F(h,k="solid"): return lt_colors.fc(h,k)
def dbl(v):
    b=struct.unpack(">q",struct.pack(">d",float(v)))[0]; lo=b&0xFFFFFFFF
    return [b>>32, lo-(1<<32) if lo>=1<<31 else lo]
def tl(pts):   # 关键帧 [(tick,值)]，hermite 格式照抄样品
    a=[3,len(pts)]
    for t,v in pts: a+=[t]+dbl(v)
    return "[I;"+",".join(map(str,a+[1,0,0]))+"]"
assert tl([(0,0),(16,2.0)])=="[I;3,2,0,0,0,16,1073741824,0,1,0,0]"
assert tl([(0,0),(44,0.05)])=="[I;3,2,0,0,0,44,1068079513,-1717986918,1,0,0]"
assert tl([(0,0),(15,322)])=="[I;3,2,0,0,0,15,1081352192,0,1,0,0]"
print("关键帧编码与样品一致")

BK="minecraft:concrete:15";DG="minecraft:concrete:7";LG="minecraft:concrete:8"
IR="minecraft:iron_block";SP="minecraft:planks:1";DO="minecraft:planks:5"
NV="minecraft:wool:11";WW="minecraft:wool"
GL=F("#bdeeff","trans");RED=F("#ff3030","glow");CY=F("#40f0ff","glow");WL=F("#fff2d8","glow")
DR=[F("#ff3030","glow"),F("#40ff80","glow"),F("#ffd040","glow"),F("#40a0ff","glow")]
ALL=[]
class G:
    def __init__(s): s.m={}
    def b(s,mat,*c): s.m.setdefault(mat,[]).append(c); ALL.append(c)
    def tiles(s):
        out=[]
        for mat,bx in s.m.items():
            t=",".join("[I;%d,%d,%d,%d,%d,%d]"%c for c in bx)
            out.append(('{bBox:%s,tile:{block:"%s"}}' if len(bx)==1 else '{boxes:[%s],tile:{block:"%s"}}')%(t,mat))
        return "["+",".join(out)+"]"
    def n(s): return sum(map(len,s.m.values()))
def node(g,st,ch=()):
    s="{tiles:%s,structure:{%s}"%(g.tiles(),st)
    if ch: s+=",children:[%s]"%",".join(ch)
    return s+"}"
R,S,A,P,D,C=G(),G(),G(),G(),G(),G()

# ---- 1 卷帘门 x0~40（正面 z 小）----
R.b(IR,0,0,22,4,66,28); R.b(IR,36,0,22,40,66,28)            # 立柱
R.b(DG,4,32,22,36,66,24); R.b(DG,4,32,27,36,66,28); R.b(DG,4,64,24,36,66,27)  # 卷帘箱
R.b(DG,4,32,24,36,33,25); R.b(DG,4,32,26,36,33,27)          # 箱底留 1px 缝
R.b(CY,6,58,21,34,59,22)
S.b(IR,4,0,25,36,2,26)
for y in range(2,32): S.b(DG if y%4==1 else LG,4,y,25,36,y+1,26)
S.b(BK,18,3,24,22,4,25)                                     # 拉手
A.b(DG,36,13,21,40,19,22); A.b(RED,37,15,20,39,17,21)        # 按钮
# ---- 2 吧台翻板 x48~80 ----
for x1 in (48,72): R.b(SP,x1,0,24,x1+8,14,40); R.b(DO,x1,14,24,x1+8,15,40)
P.b(DO,56,14,24,72,15,40); P.b(IR,70,15,30,71,16,34)
# ---- 3 冰柜 x88~112 ----
R.b(IR,88,0,25,112,2,40); R.b(IR,88,30,25,112,32,40)
R.b(IR,88,2,25,90,30,40); R.b(IR,110,2,25,112,30,40); R.b(IR,90,2,38,110,30,40)
R.b(LG,90,15,25,110,16,38); R.b(WL,90,29,26,110,30,38)
for i,x in enumerate(range(92,108,4)):
    R.b(DR[i],x,2,30,x+2,7,32); R.b(DR[3-i],x,16,30,x+2,21,32)
D.b(IR,88,0,24,112,2,25); D.b(IR,88,30,24,112,32,25)
D.b(IR,88,2,24,90,30,25); D.b(IR,110,2,24,112,30,25)
D.b(GL,90,2,24,110,30,25); D.b(BK,107,10,23,108,22,24)
# ---- 4 穿透暖帘 x120~168 ----
R.b(SP,120,0,22,124,48,28); R.b(SP,164,0,22,168,48,28); R.b(SP,124,44,22,164,48,28)
R.b(IR,124,43,24,164,44,25)
for x1,x2 in ((124,137),(138,151),(152,164)):
    C.b(NV,x1,20,25,x2,40,26); C.b(WW,x1,40,25,x2,43,26)

# ---- 校验 ----
def cells(g,f):
    o=set()
    for bx in g.m.values():
        for c in bx:
            for x in range(c[0],c[3]):
                for y in range(c[1],c[4]):
                    for z in range(c[2],c[5]): o.add(f(x+.5,y+.5,z+.5))
    return o
fl=lambda *p: tuple(math.floor(v) for v in p)
seen=set(); ov=0
for c in ALL:
    for x in range(c[0],c[3]):
        for y in range(c[1],c[4]):
            for z in range(c[2],c[5]):
                ov+=(x,y,z) in seen; seen.add((x,y,z))
print("重叠体素:",ov)
sz=1 if FLAP>0 else -1; sy=1 if FRIDGE>0 else -1
for k,g,f in (("卷帘门",S,lambda x,y,z:fl(x,y+32,z)),
              ("翻板",P,lambda x,y,z:fl(56-sz*(y-15),15+sz*(x-56),z)),
              ("冰柜门",D,lambda x,y,z:fl(88+sy*(z-24),y,24-sy*(x-88)))):
    own=cells(g,fl); hit=len(cells(g,f)&(seen-own))
    print(k,"终点空位:","通过" if hit==0 else f"被挡 {hit} 格")

# ---- 对照样品 ----
import re
def shut(drc):
    return ('id:"advancedDoor",name:"卷帘门",duration:60,interpolation:3,activateParent:0b,disableRightClick:%s,events:[],'
            'axisCenter:[I;20,16,25,21,17,26,16],animation:{offGrid:16,offY:%s}')%(drc,tl([(0,0),(60,32)]))
act='id:"doorActivator",name:"卷帘按钮",activate:[I;0],activateParent:0b,disableRightClick:0b'
RS=G()
for mat,bx in R.m.items():
    for c in bx:
        if c[3]<=40: RS.b(mat,*c)          # 只留卷帘门那一段骨架
V={"v1_门可右键_无按钮":[node(S,shut("0b"))],
   "v2_门可右键_有按钮":[node(A,act,[node(S,shut("0b"))])],
   "v3_原版_门禁右键_有按钮":[node(A,act,[node(S,shut("1b"))])]}
BOX=re.compile(r"\[I;([-\d,]+)\]")
for k,ch in V.items():
    bs=[[int(v) for v in t.split(",")] for t in BOX.findall(RS.tiles()+"".join(ch)) if len(t.split(","))==6]
    lo=[min(c[i] for c in bs) for i in range(3)]; hi=[max(c[i+3] for c in bs) for i in range(3)]
    s="{tiles:%s,children:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}"%(RS.tiles(),",".join(ch),*lo,*[hi[i]-lo[i] for i in range(3)],RS.n())
    # 根有 children ⇒ 根必须有 structure（§3.9）；缺了在此自动插入，断言不过直接报错退出
    s=lt_root.fix(s,ROOT_NAME,tag="mech_%s.txt"%k)
    open(f"mech_{k}.txt","w",encoding="utf-8").write(s); print(f"mech_{k}.txt",len(s),"字符", "| 根层:", lt_root.elide(lt_root.root_layer(s)))
