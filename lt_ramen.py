# lt_ramen.py  一番拉面·外壳与门面（全小方块，1像素=1/16格，原点=店西北角地面）
import numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFont
import lt_colors, lt_root, lt_np
ROOT_NAME="ramen_shop"   # 根层 structure 的 name（本脚本当前不输出 children，守卫为将来预留）
MIRROR=False   # 招牌若左右反，改成 True
DIAG=False     # True 时才打印 ⑥ 发光材质诊断（只读，不改蓝图）
LEAKFIX=True   # True 时把"离室内 ≤2 格的墙外发光体素"换成同色不发光假灯
FONTS=[r"C:\Windows\Fonts\simhei.ttf",r"C:\Windows\Fonts\msyh.ttc",r"C:\Windows\Fonts\simsun.ttc"]
def F(h,k="solid"): return lt_colors.fc(h,k)

MATS=[None]; MID={}
def M(n):
    if n not in MID: MID[n]=len(MATS); MATS.append(n)
    return MID[n]
BK=M("minecraft:concrete:15"); DG=M("minecraft:concrete:7"); LG=M("minecraft:concrete:8"); WH=M("minecraft:concrete")
QZ=M("minecraft:quartz_block"); IR=M("minecraft:iron_block"); AN=M("minecraft:stone:6")
DO=M("minecraft:planks:5"); SP=M("minecraft:planks:1")
RW=M("minecraft:wool:14"); WW=M("minecraft:wool"); NV=M("minecraft:wool:11"); KW=M("minecraft:wool:15")
GLASS=M(F("#bdeeff","trans")); STRIP=M(F("#d8efe8","trans"))
WARM=M(F("#ffd9a0","glow")); WHG=M(F("#fff2d8","glow")); CYG=M(F("#40f0ff","glow"))
MAG=M(F("#ff30c0","glow")); REDG=M(F("#ff3030","glow")); GRN=M(F("#40ff80","glow"))
BRASS=M(F("#c8a040")); COPPER=M(F("#b87333")); YEL=M(F("#e8c020"))

OX,OY,OZ=16,0,48; SX,SY,SZ=192,144,288
V=np.zeros((SX,SY,SZ),np.uint8)
def box(m,x1,y1,z1,x2,y2,z2): V[x1+OX:x2+OX,y1+OY:y2+OY,z1+OZ:z2+OZ]=m
def px(m,x,y,z): V[x+OX,y+OY,z+OZ]=m
FACE={"N":lambda u,v,d:(u,v,d),"S":lambda u,v,d:(u,v,207-d),"W":lambda u,v,d:(d,v,u),"E":lambda u,v,d:(143-d,v,u),
      "n":lambda u,v,d:(u,v,7-d),"s":lambda u,v,d:(u,v,200+d),"w":lambda u,v,d:(7-d,v,u),"e":lambda u,v,d:(136+d,v,u)}
def face(sd,u1,u2,v1,v2,paint,back=None):
    P=FACE[sd]
    for u in range(u1,u2):
        for v in range(v1,v2):
            m=paint(u,v)
            if m is None:
                px(0,*P(u,v,0))
                if back: px(back,*P(u,v,1))
            else: px(m,*P(u,v,0))
def ringN(m,x1,x2,y1,y2,z):
    box(m,x1,y1,z,x2,y1+1,z+1); box(m,x1,y2-1,z,x2,y2,z+1)
    box(m,x1,y1,z,x1+1,y2,z+1); box(m,x2-1,y1,z,x2,y2,z+1)
def ringX(m,x,z1,z2,y1,y2):
    box(m,x,y1,z1,x+1,y1+1,z2); box(m,x,y2-1,z1,x+1,y2,z2)
    box(m,x,y1,z1,x+1,y2,z1+1); box(m,x,y1,z2-1,x+1,y2,z2)
# ---------- 文字 ----------
def font(size):
    for fp in FONTS:
        try: return ImageFont.truetype(fp,size)
        except OSError: pass
    raise SystemExit("找不到中文字体：改 FONTS 列表")
def glyphs(s,size):
    img=Image.new("L",(size*len(s)+16,size+16),0)
    ImageDraw.Draw(img).text((8,4),s,fill=255,font=font(size))
    img=img.crop(img.getbbox()); w,h=img.size; p=img.load()
    return [[p[x,y]>110 for x in range(w)] for y in range(h)]
def vglyphs(s,size,gap=2):
    cs=[glyphs(c,size) for c in s]; W=max(len(c[0]) for c in cs); rows=[]
    for i,c in enumerate(cs):
        if i: rows+=[[False]*W for _ in range(gap)]
        pad=(W-len(c[0]))//2
        rows+=[[False]*pad+r+[False]*(W-len(r)-pad) for r in c]
    return rows
G5={"O":"01110 10001 10001 10001 01110","P":"11110 10001 11110 10000 10000","E":"11111 10000 11110 10000 11111",
    "N":"10001 11001 10101 10011 10001","2":"11110 00001 01110 10000 11111","4":"10010 10010 11111 00010 00010",
    "H":"10001 10001 11111 10001 10001"}
def pix5(s):
    rows=[[] for _ in range(5)]
    for i,ch in enumerate(s):
        g=G5[ch].split()
        for r in range(5):
            if i: rows[r].append(False)
            rows[r]+=[c=="1" for c in g[r]]
    return rows
def draw(bm,m,sd,u1,u2,ytop,d):   # sd: N=朝北 W=朝西 E=朝东
    w=len(bm[0]); u0=(u1+u2-w)//2; rev=(sd in "NE")!=MIRROR
    for j,row in enumerate(bm):
        for i,on in enumerate(row):
            if not on: continue
            u=u0+w-1-i if rev else u0+i; y=ytop-1-j
            if sd=="N": px(m,u,y,d)
            else: px(m,d,y,u)
def lantern(cx,cz,yb,yh):
    def disc(m,y,r):
        for dx in range(-r,r):
            for dz in range(-r,r):
                if (dx+.5)**2+(dz+.5)**2<=r*r: px(m,cx+dx,y,cz+dz)
    for y in (yb,yb+1): disc(KW,y,3)
    for i,r in enumerate([3,4,5,5,6,6,6,6,6,6,5,5,4,3]): disc(RW if i in(3,7,10) else REDG,yb+2+i,r)
    for y in (yb+16,yb+17): disc(KW,y,3)
    box(KW,cx,yb+18,cz,cx+1,yh,cz+1)

# ===== 主体 =====
box(BK,0,0,0,144,128,208)
box(0,8,2,8,136,84,200)            # 室内：地面y2~吊顶y84
box(0,4,116,4,140,128,204)         # 屋面下沉留女儿墙
box(DG,4,115,4,140,116,204)
# ===== 墙面 =====
def p_front(u,v):
    if v<4: return AN
    if v<20: return None if u%5==0 else DO
    if v==20: return SP
    return None if (u%16==0 or (v-21)%32==31) else BK
def p_side(u,v):
    if v<4: return AN
    return None if (u%16==0 or (v-4)%32==31) else BK
def p_cust(u,v):
    if v<18: return None if u%6==0 else DO
    if v<20: return SP
    if v>=78: return DO
    return SP if u%24<2 else QZ
def p_kit(u,v):
    if v<58:
        r=(v-2)//4
        return None if ((v-2)%4==3 or (u+4*(r%2))%8==0) else QZ
    return WH
face("N",0,144,0,126,p_front,DG); face("S",0,144,0,126,p_side,DG)
face("W",0,208,0,126,p_side,DG); face("E",0,208,0,126,p_side,DG)
face("n",8,136,2,84,p_cust)
for sd in "we": face(sd,8,112,2,84,p_cust); face(sd,112,200,2,84,p_kit,LG)
face("s",8,136,2,84,p_kit,LG)
box(AN,0,126,0,144,128,208); box(0,4,126,4,140,128,204)
# ===== 地面 =====
box(DO,8,0,8,136,2,112)
for x in range(8,136,6):
    box(KW,x,1,8,x+1,2,112)
    for z in range(8+(x//6%4)*8,112,32): box(KW,x,1,z,x+6,2,z+1)
box(QZ,8,0,112,136,2,200)
for x in range(8,136,8): box(LG,x,1,112,x+1,2,200)
for z in range(112,200,8): box(LG,8,1,z,136,2,z+1)
box(IR,64,1,152,72,2,160)
for x in range(65,72,2): box(BK,x,1,153,x+1,2,159)
box(BRASS,8,1,111,136,2,113)
# ===== 吊顶 =====
box(SP,8,83,8,136,84,112)
for x in range(14,136,12): box(DO,x,82,8,x+2,83,112)
box(0,28,82,20,116,87,100); box(DO,28,86,20,116,87,100)
for x in range(30,116,8): box(WARM,x,86,20,x+2,87,100)
for z in range(20,100,10): box(SP,28,85,z,116,86,z+1)
box(WH,8,83,112,136,84,200)
for x1,z1 in ((24,128),(88,128),(24,172),(88,172)): box(WHG,x1,82,z1,x1+32,83,z1+12)
box(IR,29,84,159,43,134,173); box(0,30,83,160,42,140,172)
box(DG,26,136,156,46,138,176)
for x,z in ((29,159),(41,159),(29,171),(41,171)): box(IR,x,134,z,x+2,136,z+2)
# ===== 门面 =====
for x1 in (0,134): box(DG,x1,4,-2,x1+10,128,0); box(CYG,x1+4,8,-3,x1+6,124,-2)
box(0,48,2,0,96,50,8); box(AN,44,0,-6,100,2,8)
box(SP,45,2,-1,48,53,8); box(SP,96,2,-1,99,53,8); box(SP,45,50,-1,99,53,8)
box(IR,46,49,-3,98,50,-2); box(IR,46,49,-2,47,52,-1); box(IR,97,49,-2,98,52,-1)
# 暖帘（豚骨面三幅）不再属于拉面店蓝图，改到文件末尾单独导出 ramen_curtain.txt（可穿透 noclip）
for x1 in (14,102):
    x2=x1+28
    box(0,x1,20,0,x2,56,8); box(DG,x1,20,2,x2,56,6); box(0,x1+2,22,2,x2-2,54,6)
    box(GLASS,x1+2,22,3,x2-2,54,5); box(DG,x1+2,44,3,x2-2,46,5)
    box(AN,x1-2,18,-2,x2+2,20,2); box(SP,x1-1,18,6,x2+1,20,10)
draw(pix5("OPEN"),REDG,"N",104,128,53,5); box(BK,102,47,6,130,54,7)
b=pix5("24H"); draw(b,CYG,"N",16,40,53,5); w=len(b[0]); u0=(56-w)//2; ringN(CYG,u0-2,u0+w+2,47,54,5); box(BK,u0-2,47,6,u0+w+2,54,7)
for k in range(29):
    z=-1-k; yb=62-k//4
    for x0 in range(6,138,8): box(RW if (x0//8)%2==0 else WW,x0,yb,z,min(x0+8,138),yb+2,z+1)
for x in range(6,138): box(RW if ((x-6)//8)%2==0 else WW,x,49 if (x-6)%8 in(3,4) else 51,-30,x+1,57,-29)
box(WARM,8,55,-27,136,56,-26)
for bx in (8,42,100,134):
    for k in range(23): y=40+k*14//22; box(IR,bx,y,-1-k,bx+2,y+2,-k)
    box(IR,bx,54,-23,bx+2,57,-22)
lantern(20,-22,34,57); lantern(124,-22,34,57)
box(BK,14,66,-4,130,98,0); ringN(MAG,14,130,66,98,-5)
draw(glyphs("一番拉面",24),WHG,"N",14,130,94,-5)
for x,y in ((16,68),(126,68),(16,94),(126,94)): box(IR,x,y,-5,x+2,y+2,-4)
box(KW,14,100,-5,130,101,-4)
for x in range(16,130,6): px(WARM if (x//6)%2 else REDG,x,99,-5)
box(CYG,10,104,-1,134,105,0)
box(BK,139,56,-26,143,126,-4); ringX(MAG,138,-26,-4,56,126); ringX(MAG,143,-26,-4,56,126)
vb=vglyphs("深夜食堂",14,2); draw(vb,WHG,"W",-26,-4,122,138); draw(vb,WHG,"E",-26,-4,122,143)
for y in (58,122): box(IR,140,y,-4,142,y+2,-2)
box(DG,-1,4,30,0,112,31)
box(LG,-3,40,20,-1,58,30); box(YEL,-4,50,23,-3,54,27)
box(WW,-1,30,40,0,58,58)
draw(vglyphs("豚骨",10,2),RW,"W",40,58,56,-2)
box(KW,-2,12,90,-1,14,110); box(IR,-2,60,80,0,74,96)
for y in range(62,74,3): box(DG,-3,y,81,-2,y+1,95)
# ===== 东墙设备 =====
box(IR,144,34,122,152,36,124); box(IR,144,34,142,152,36,144); box(LG,144,36,120,154,54,146)
for y in range(37,54):
    for z in range(121,145):
        d=(y-45)**2+(z-133)**2
        if d<=64: px(KW if (d<=4 or int(d**.5)%2==0) else LG,153,y,z)
for z in (116,118): box(COPPER,144,44,z,145,112,z+1)
box(COPPER,144,44,116,146,45,120)
for y in range(52,112,16): box(IR,144,y,115,146,y+1,120)
box(DG,144,28,60,148,46,72); box(GLASS,148,36,62,149,43,70); box(GRN,147,38,64,148,40,68)
box(DG,144,46,65,146,110,67)
box(IR,144,106,4,148,107,204); box(KW,145,107,4,146,108,204); box(DG,146,107,4,147,108,204)
for z in range(8,204,32): box(IR,144,104,z,148,106,z+1)
# ===== 背面 =====
box(0,100,2,200,128,48,208); box(AN,100,0,200,128,2,208); box(AN,96,0,208,132,2,216)
box(IR,97,2,206,100,51,209); box(IR,128,2,206,131,51,209); box(IR,97,48,206,131,51,209)
box(IR,100,47,203,128,48,205)
for x in range(100,128,4): box(STRIP,x,34,203,x+3,47,204)
box(DG,110,54,208,118,58,212); box(WARM,111,53,209,117,54,211); box(KW,113,58,207,114,84,208)
for x in range(28,53):
    for y in range(60,85):
        d=(x-40)**2+(y-72)**2
        if d<=81:
            px(0,x,y,207); px(KW,x,y,206)
            if y%3==0: px(IR,x,y,207)
        elif d<=110: px(IR,x,y,208)
box(LG,60,30,208,70,44,213); box(GLASS,62,36,213,68,42,214)
box(YEL,64,2,209,66,30,211); box(YEL,70,38,208,82,40,210)
box(DG,138,0,208,141,126,211); box(DG,138,0,211,141,2,216)
for y in range(12,120,24): box(IR,137,y,207,142,y+1,212)
# ===== 屋顶 =====
box(DG,90,116,40,118,132,64)
for y in (118,123,128): box(IR,89,y,39,119,y+1,65)
for x in range(92,116):
    for z in range(42,62):
        d=(x-103.5)**2+(z-51.5)**2
        if d<=100: px(KW if int(d**.5)%3==0 else DG,x,131,z)
box(DG,60,116,80,76,118,96); box(IR,66,118,86,70,119,90)
for z in (168,184): box(IR,120,116,z,122,126,z+2); box(DG,119,126,z-1,123,127,z+3)

# ===== 通行检查（0.6×1.8 玩家，跨步≤9px）=====
def walk():
    occ=np.concatenate([np.ones((SX,1,SZ),bool),V!=0],axis=1)
    A=occ.copy()
    for d in range(1,10): A[:-d]|=occ[d:]
    B=A.copy()
    for d in range(1,10): B[:,:,:-d]|=A[:,:,d:]
    NY=B.shape[1]; C=np.zeros((SX,NY+1,SZ),np.int16); C[:,1:,:]=np.cumsum(B,axis=1,dtype=np.int16)
    hs=np.arange(1,NY-28); valid=((C[:,hs+29,:]-C[:,hs,:])==0)&B[:,hs-1,:]
    cache={}
    def H(x,z):
        if (x,z) not in cache: cache[(x,z)]=np.nonzero(valid[x,:,z])[0].tolist()
        return cache[(x,z)]
    def bfs(s,t):
        sx,sz,tx,tz=s[0]+OX,s[1]+OZ,t[0]+OX,t[1]+OZ
        if not H(sx,sz): return None
        st=(sx,H(sx,sz)[0],sz); seen={st:0}; q=deque([st])
        while q:
            x,h,z=c=q.popleft()
            if (x,z)==(tx,tz): return seen[c]
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,nz=x+dx,z+dz
                if not(0<=nx<SX-10 and 0<=nz<SZ-10): continue
                for nh in H(nx,nz):
                    n=(nx,nh,nz)
                    if h-16<=nh<=h+9 and n not in seen: seen[n]=seen[c]+1; q.append(n)
        return None
    allok=True
    for k,(s,t) in {"门外→客区":((62,-26),(62,60)),"客区→后厨":((62,60),(110,160)),"后厨→后门外":((110,160),(110,222))}.items():
        r=bfs(s,t); allok&=r is not None
        print(k, f"通过，{r}像素≈{r/16:.1f}格" if r is not None else "不通！")
    print("通行检查:","全部通过" if allok else "失败")
# ===== 导出 =====
def export(fn):
    ax=[np.nonzero(V.any(axis=tuple(j for j in range(3) if j!=i)))[0] for i in range(3)]
    lo=[int(a[0]) for a in ax]; hi=[int(a[-1])+1 for a in ax]; base=[l//16*16 for l in lo]
    parts=[];cnt=0;W=np.zeros_like(V)
    for mi in range(1,len(MATS)):
        R=(V==mi)
        if not R.any(): continue
        bx=[]
        for x in range(lo[0],hi[0]):
            sl=R[x]
            while True:
                y,z=divmod(int(sl.argmax()),SZ)
                if not sl[y,z]: break
                r=sl[y,z:]; z2=z+(len(r) if r.all() else int(r.argmin()))
                y2=y+1
                while y2<SY and sl[y2,z:z2].all(): y2+=1
                x2=x+1
                while x2<SX and R[x2,y:y2,z:z2].all(): x2+=1
                R[x:x2,y:y2,z:z2]=False; W[x:x2,y:y2,z:z2]=mi
                bx.append((x-base[0],y-base[1],z-base[2],x2-base[0],y2-base[1],z2-base[2]))
        cnt+=len(bx); b=",".join("[I;%d,%d,%d,%d,%d,%d]"%t for t in bx)
        parts.append(('{bBox:%s,tile:{block:"%s"}}' if len(bx)==1 else '{boxes:[%s],tile:{block:"%s"}}')%(b,MATS[mi]))
    s="{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}"%(",".join(parts),*[lo[i]-base[i] for i in range(3)],*[hi[i]-lo[i] for i in range(3)],cnt)
    # 根有 children ⇒ 根必须有 structure（§3.9）；本脚本当前无 children，此处为不变量守卫
    s=lt_root.fix(s,ROOT_NAME,tag=fn)
    open(fn,"w",encoding="utf-8").write(s)
    off=[(o-b)//16 for o,b in zip((OX,OY,OZ),base)]
    print(fn,f"{len(s.encode())/1024:.0f} KB | 小块 {cnt} | 材质 {len(parts)} | 尺寸 {[(hi[i]-lo[i])/16 for i in range(3)]} 格")
    print("无损校验:",np.array_equal(W,V))
    print(f"蓝图起点格 = 店西北角格 - ({off[0]},{off[1]},{off[2]})")
# ===== ⑥ 发光材质诊断：只读打印，不改蓝图（DIAG=True 时才跑）=====
if DIAG:
    print("=== ⑥ 发光材质诊断：x∈8~40 或 104~136, z∈8~112, y∈2~84 ===")
    _dxs=[x for x in range(8,41)]+[x for x in range(104,137)]
    for _nm in ("WARM","WHG","CYG","MAG","REDG","GRN"):
        _mi=globals()[_nm]; _pts=[]
        for _x in _dxs:
            for _y,_z in np.argwhere(V[_x+OX,2+OY:85+OY,8+OZ:113+OZ]==_mi):
                _pts.append((_x,int(_y)+2,int(_z)+8))
        if not _pts:
            print("  %s (%s): 0 体素"%(MATS[_mi],_nm)); continue
        _b=[min(p[i] for p in _pts) for i in range(3)]+[max(p[i] for p in _pts) for i in range(3)]
        print("  %s (%s): %d 体素  包围盒 x[%d,%d] y[%d,%d] z[%d,%d]"%(MATS[_mi],_nm,len(_pts),_b[0],_b[3],_b[1],_b[4],_b[2],_b[5]))
# ===== 暖帘（豚骨面三幅）：单独导出为可穿透结构（noclip, web:0b）=====
# 结构写法沿用 lt_mech.py 里已验证的暖帘样品；坐标系与拉面店一致（O 相同），W 置 0 = 以店西北角格为原点
SHOP_NW=(-800,4,324)                     # 店西北角格（按 PLAN 的南排位置；换位置只改这三个数）
CV=lt_np.Vol((192,64,64),(16,0,48),(0,0,0))
_CNV=CV.M("minecraft:wool:11"); _CWW=CV.M("minecraft:wool")
def cpx(m,x,y,z): CV.box(m,x,y,z,x+1,y+1,z+1)
def cdraw(bm,m,u1,u2,ytop,d):            # 与 draw() 的 N 面算法一致（含 MIRROR 翻转与居中）
    w=len(bm[0]); u0=(u1+u2-w)//2; rev=(True)!=MIRROR
    for j,row in enumerate(bm):
        for i,on in enumerate(row):
            if on: cpx(m,u0+w-1-i if rev else u0+i, ytop-1-j, d)
for x0 in (48,64,80):
    CV.box(_CNV,x0,34,-2,x0+15,49,-1); CV.box(_CWW,x0,34,-2,x0+15,36,-1)
for x in (63,79): CV.box(0,x-1,34,-2,x+1,49,-1)
for x0,ch in ((80,"豚"),(64,"骨"),(48,"面")):
    cdraw(glyphs(ch,13),_CWW,x0,x0+14,49,-2)
_cs=CV.export("ramen_curtain.txt","ramen_curtain",'{id:"noclip",name:"暖帘",web:0b}')
_ax=[np.nonzero(V.any(axis=tuple(j for j in range(3) if j!=i)))[0] for i in range(3)]
_sb=[int(a[0])//16*16 for a in _ax]
_shs=tuple((_sb[i]-[OX,OY,OZ][i])//16 for i in range(3))          # 拉面店蓝图起点（以店西北角为原点）
print("暖帘导入起点（以店西北角为原点）= %s   ← 相对拉面店蓝图起点 %s 的偏移 = %s 格"
      %(_cs,_shs,tuple(_cs[i]-_shs[i] for i in range(3))))
print("按 PLAN 店西北角格 %s：拉面店导入起点 %s ；暖帘导入起点 %s"
      %(SHOP_NW,tuple(SHOP_NW[i]+_shs[i] for i in range(3)),tuple(SHOP_NW[i]+_cs[i] for i in range(3))))

# ===== 漏光检查：店铺范围外、离任一室内格 ≤2 格的发光体素 → 换成同色假灯（不发光）=====
GLOW=("WARM","WHG","CYG","MAG","REDG","GRN")
# 假灯对照表：同一个 hex 用 F(hex,"solid") 生成，再用 M() 登记成索引（WARM→F("#ffd9a0","solid") 等）
FAKE={WARM:M(F("#ffd9a0","solid")),WHG:M(F("#fff2d8","solid")),CYG:M(F("#40f0ff","solid")),
      MAG:M(F("#ff30c0","solid")),REDG:M(F("#ff3030","solid")),GRN:M(F("#40ff80","solid"))}
assert set(FAKE)==set(globals()[n] for n in GLOW),"假灯对照表与发光材质不一致"
RX=(0,144,16,96,0,208)                                   # 店铺范围 x0,x1,y0,y1,z0,z1（像素，半开）
_cells=[(cx,cy,cz) for cx in range(RX[0]//16,RX[1]//16) for cy in range(RX[2]//16,RX[3]//16)
        for cz in range(RX[4]//16,RX[5]//16)
        if (V[cx*16+OX:(cx+1)*16+OX,cy*16+OY:(cy+1)*16+OY,cz*16+OZ:(cz+1)*16+OZ]==0).any()]
_dil={(i+dx,j+dy,k+dz) for i,j,k in _cells
      for dx in (-2,-1,0,1,2) for dy in (-2,-1,0,1,2) for dz in (-2,-1,0,1,2)}
print("=== 漏光检查（16px 一格）===")
print("店铺范围 x[%d,%d) y[%d,%d) z[%d,%d)；含空气的室内格 %d 个"%(RX[0],RX[1],RX[2],RX[3],RX[4],RX[5],len(_cells)))
_fixed=0
for _nm in GLOW:
    _mi=globals()[_nm]; _idx=[]
    for _a,_b,_c in np.argwhere(V==_mi):
        _x,_y,_z=int(_a)-OX,int(_b)-OY,int(_c)-OZ
        if RX[0]<=_x<RX[1] and RX[2]<=_y<RX[3] and RX[4]<=_z<RX[5]: continue   # 店铺范围内不算
        if _z<0: continue   # 门面霓虹豁免：室内前部有灯槽照明，漏光看不出
        if (_x//16,_y//16,_z//16) in _dil: _idx.append((int(_a),int(_b),int(_c)))
    _gc=sorted({((a-OX)//16,(b-OY)//16,(c-OZ)//16) for a,b,c in _idx})
    print("  %-5s 风险体素 %4d  所在格 %s"%(_nm,len(_idx),_gc if _gc else "无"))
    if _idx and LEAKFIX:
        _A=np.array(_idx); V[_A[:,0],_A[:,1],_A[:,2]]=FAKE[_mi]
        print("        → %d 个换成 %s（同色不发光）"%(len(_idx),MATS[FAKE[_mi]]))
        _fixed+=len(_idx)
if LEAKFIX: print("LEAKFIX: 共替换 %d 个体素为同色不发光假灯"%_fixed)
walk(); export("ramen_shop.txt")