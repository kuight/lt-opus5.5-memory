import re
from lt_colors import fc
import lt_root
ROOT_NAME="nexus_lab"   # 根层 structure 的 name
B=16; X,Y,Z=18*B,13*B,13*B
g=bytearray(X*Y*Z); mats=[None]; mid={}
def M(b):
    if b not in mid: mid[b]=len(mats); mats.append(b)
    return mid[b]
def F(h,k): return M(fc(h,k))
DK=M('minecraft:concrete:15');GR=M('minecraft:concrete:7');LG=M('minecraft:concrete:8');WH=M('minecraft:concrete')
QZ=M('minecraft:quartz_block');QC=M('minecraft:quartz_block:1');QP=M('minecraft:quartz_block:2')
AN=M('minecraft:stone:6');IR=M('minecraft:iron_block');PR=M('minecraft:prismarine:2')
YL=M('minecraft:concrete:4');RD=M('minecraft:concrete:14');OR=M('minecraft:concrete:1');GN=M('minecraft:concrete:13')
CB=M('minecraft:concrete:9');BL=M('minecraft:concrete:11')
CY=F('#00e5ff','glow');MG=F('#ff2bd6','glow');WG=F('#e8fbff','glow');LGN=F('#39ff88','glow')
RG=F('#ff3030','glow');AM=F('#ffb000','glow');SC=F('#0a2a4a','glow')
GL=F('#bdeeff','trans');HC=F('#00e5ff','trans');FL=F('#39ff88','trans');BU=F('#ffffff','trans');XR=F('#ff9a3c','trans')
def box(m,x1,y1,z1,x2,y2,z2):
    x1,x2=sorted((x1,x2));y1,y2=sorted((y1,y2));z1,z2=sorted((z1,z2))
    x1,y1,z1=max(0,x1),max(0,y1),max(0,z1);x2,y2,z2=min(X,x2),min(Y,y2),min(Z,z2)
    if x1>=x2 or y1>=y2 or z1>=z2: return
    s=bytes([m])*(x2-x1)
    for y in range(y1,y2):
        for z in range(z1,z2):
            o=(y*Z+z)*X; g[o+x1:o+x2]=s
def put(m,x,y,z):
    if 0<=x<X and 0<=y<Y and 0<=z<Z: g[(y*Z+z)*X+x]=m
def fill(m,x1,y1,z1,x2,y2,z2,f):
    for y in range(y1,y2):
        for z in range(z1,z2):
            for x in range(x1,x2):
                if f(x,y,z): put(m,x,y,z)
def cyl(m,cx,cz,r,y1,y2,rin=0):
    for dz in range(-r,r+1):
        w=int(max(0,(r+.5)**2-dz*dz)**.5); z=cz+dz
        if rin and (rin-.5)**2>dz*dz:
            wi=int(((rin-.5)**2-dz*dz)**.5)
            box(m,cx-w,y1,z,cx-wi,y2,z+1); box(m,cx+wi+1,y1,z,cx+w+1,y2,z+1)
        else: box(m,cx-w,y1,z,cx+w+1,y2,z+1)
def diskx(m,x1,x2,yc,zc,r,rin=0):
    fill(m,x1,yc-r,zc-r,x2,yc+r+1,zc+r+1,lambda x,y,z:rin*rin<=(y-yc)**2+(z-zc)**2<=(r+.5)**2)
def rod(m,p,q,t):
    n=max(abs(q[i]-p[i]) for i in range(3)) or 1
    for i in range(n+1):
        c=[round(p[k]+(q[k]-p[k])*i/n) for k in range(3)]
        box(m,c[0]-t//2,c[1]-t//2,c[2]-t//2,c[0]-t//2+t,c[1]-t//2+t,c[2]-t//2+t)
X0,X1,Z0,Z1=16,272,32,192; Fl=8; C=88; R=96
def orow(z,ins,c=40):
    a,b,za,zb=X0+ins,X1-ins,Z0+ins,Z1-ins
    if z<za or z>=zb: return None
    d=min(z-za,zb-1-z); cut=max(0,int(c-d-ins*0.41)); return a+cut,b-cut
def slab(m,y1,y2,ins):
    for z in range(Z):
        r=orow(z,ins)
        if r: box(m,r[0],y1,z,r[1],y2,z+1)
# ===== 外壳 =====
slab(AN,0,4,-6); slab(CY,4,5,-5); slab(DK,5,Fl,-3); slab(QZ,5,Fl,0)
slab(DK,Fl,R,0); slab(GR,Fl,Fl+6,-1); slab(MG,R-4,R-2,-1); slab(CY,Fl+8,Fl+9,-1)
slab(GL,56,80,0); slab(DK,54,56,-1); slab(DK,80,82,-1)
slab(QZ,Fl,C,3); slab(0,Fl,C,6); slab(AN,C-2,C,6)
slab(DK,R,R+8,-2); slab(0,R,R+8,2); slab(CY,R+8,R+10,-2); slab(0,R+8,R+10,0)
slab(MG,C-3,C-2,6); slab(0,C-3,C-2,8)
for x in range(X0+6,X1-6,32): box(AN,x,Fl-1,Z0+6,x+1,Fl,Z1-6)
for z in range(Z0+6,Z1-6,32): box(AN,X0+6,Fl-1,z,X1-6,Fl,z+1)
for (sx,sz) in ((0,0),(1,0),(0,1),(1,1)):
    x=X0+17 if sx==0 else X1-20; z=Z0+17 if sz==0 else Z1-20
    box(MG,x,Fl+6,z,x+3,R-6,z+3); box(IR,x-1,Fl,z-1,x+4,Fl+6,z+4)
for x in range(X0+48,X1-44,32):
    for y in range(Fl,R):
        d=2+(y-Fl)//14; box(DK,x,y,Z0-d,x+3,y+1,Z0); box(DK,x,y,Z1,x+3,y+1,Z1+d)
    box(CY,x+1,Fl+10,Z0-3,x+2,54,Z0-2)
for x in range(X0+40,X1-40,16):
    box(DK,x,56,Z0+4,x+2,80,Z0+6); box(DK,x,56,Z1-6,x+2,80,Z1-4)
# ===== 入口 =====
box(0,X0-1,Fl,104,X0+7,Fl+32,120)
box(CY,X0-1,Fl,102,X0+1,Fl+34,104); box(CY,X0-1,Fl,120,X0+1,Fl+34,122); box(CY,X0-1,Fl+32,102,X0+1,Fl+34,122)
box(0,X0+2,Fl,120,X0+6,Fl+32,136)
box(DK,X0-40,Fl+40,86,X0,Fl+44,138)
for i in range(0,52,4): box(YL if (i//4)%2 else DK,X0-41,Fl+40,86+i,X0-40,Fl+44,90+i)
for x in range(X0-38,X0,6):
    for z in range(88,136,6): box(WG,x,Fl+39,z,x+4,Fl+40,z+4)
rod(IR,(X0-36,4,90),(X0-30,Fl+40,92),3); rod(IR,(X0-36,4,134),(X0-30,Fl+40,132),3)
box(AN,X0-48,0,96,X0-6,4,128)
for x in range(X0-46,X0-6,6): put(CY,x,4,98); put(CY,x,4,125)
font={'N':["101","111","111","101","101"],'E':["111","100","110","100","111"],'X':["101","101","010","101","101"],'U':["101","101","101","101","111"],'S':["111","100","111","001","111"]}
box(DK,X0-3,Fl+46,80,X0,Fl+66,144); box(CY,X0-4,Fl+46,80,X0-3,Fl+47,144); box(CY,X0-4,Fl+65,80,X0-3,Fl+66,144)
for i,ch in enumerate("NEXUS"):
    for r,row in enumerate(font[ch]):
        for c,v in enumerate(row):
            if v=='1': box(MG,X0-5,Fl+62-r*3,84+i*12+c*3,X0-3,Fl+65-r*3,87+i*12+c*3)
# 安检
for z0 in (94,124):
    box(IR,30,Fl,z0,38,Fl+20,z0+6); box(SC,38,Fl+12,z0+1,39,Fl+19,z0+5); box(LGN,38,Fl+14,z0+2,39,Fl+15,z0+4)
box(LG,42,Fl,98,46,Fl+44,102); box(LG,42,Fl,122,46,Fl+44,126); box(LG,42,Fl+40,98,46,Fl+44,126)
box(CY,46,Fl+2,101,47,Fl+42,102); box(CY,46,Fl+2,122,47,Fl+42,123); box(RG,43,Fl+44,111,45,Fl+45,113)
box(DK,24,Fl,70,64,Fl+10,82); box(GR,24,Fl+10,72,64,Fl+11,80)
for x in range(25,64,3): box(AN,x,Fl+10,72,x+1,Fl+11,80)
box(IR,36,Fl+10,68,52,Fl+26,84); box(0,36,Fl+11,72,52,Fl+22,80); box(XR,37,Fl+22,72,51,Fl+23,80); box(SC,40,Fl+18,67,48,Fl+24,68)
for x in range(30,110,8): box(CY,x,Fl-1,111,x+3,Fl,113)
# ===== 反应柱 =====
cx,cz=144,112
cyl(DK,cx,cz,26,Fl,Fl+3); cyl(CY,cx,cz,24,Fl+3,Fl+4,22); cyl(IR,cx,cz,22,Fl+3,Fl+6)
cyl(GL,cx,cz,18,Fl+6,C-12,16); cyl(FL,cx,cz,15,Fl+6,Fl+46); cyl(MG,cx,cz,4,Fl+6,C-12)
for i in range(14):
    bx=cx+[-9,7,-3,10,-11,4][i%6]; bz=cz+[5,-8,10,2,-4,-11][i%6]; by=Fl+8+i*3
    box(BU,bx,by,bz,bx+2,by+2,bz+2)
for y in (Fl+16,Fl+32,Fl+48,C-16): cyl(IR,cx,cz,20,y,y+2,17); cyl(CY,cx,cz,21,y,y+1,19)
cyl(IR,cx,cz,20,C-12,C-6); cyl(DK,cx,cz,14,C-6,C); cyl(MG,cx,cz,21,C-9,C-8,19)
for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
    rod(OR,(cx+dx*22,Fl+4,cz+dz*22),(cx+dx*34,Fl-2,cz+dz*34),3)
    rod(DK,(cx+dx*18,C-10,cz+dz*18),(cx+dx*30,C-1,cz+dz*30),3)
# 地面格栅
for z1,z2 in ((Z0+6,90),(134,Z1-6)):
    box(0,128,Fl-6,z1,160,Fl,z2); box(CY,128,Fl-6,z1,160,Fl-5,z2)
    box(OR,132,Fl-5,z1,136,Fl-2,z2); box(CB,140,Fl-5,z1,143,Fl-2,z2); box(GN,150,Fl-5,z1,154,Fl-2,z2)
    for x in range(128,160,4): box(IR,x,Fl-1,z1,x+1,Fl,z2)
    for z in range(z1,z2,16): box(IR,128,Fl-1,z,160,Fl,z+1)
    box(DK,126,Fl-1,z1,128,Fl,z2); box(DK,160,Fl-1,z1,162,Fl,z2)
# ===== 天花灯盘 =====
for x in range(40,250,48):
    for z in range(56,170,48):
        if abs(x+14-cx)<44 and abs(z+14-cz)<44: continue
        box(IR,x-1,C-4,z-1,x+29,C-2,z+29); box(WG,x,C-3,z,x+28,C-2,z+28)
        for k in range(7,28,7): box(IR,x+k,C-4,z,x+k+1,C-3,z+28); box(IR,x,C-4,z+k,x+28,C-3,z+k+1)
# ===== 墙面模块（南墙西段） =====
def wallp(x1,x2,zf,s):
    zz=zf if s>0 else zf-1
    for x in range(x1,x2,32): box(QZ,x+1,Fl+5,zz,x+31,53,zz+s); box(QP,x,Fl+5,zz,x+1,53,zz+2*s)
    box(AN,x1,Fl,zz,x2,Fl+5,zz+2*s); box(CY,x1,53,zz,x2,54,zz+s); box(QC,x1,54,zz,x2,56,zz+2*s)
wallp(64,164,Z0+6,1); wallp(124,180,Z1-6,-1)
# ===== 机柜 =====
for i,x in enumerate(range(170,250,16)):
    box(DK,x,Fl,38,x+15,Fl+46,52); box(GR,x+1,Fl+2,51,x+14,Fl+44,52)
    box(MG,x+1,Fl+2,52,x+2,Fl+44,53)
    for u in range(10):
        y=Fl+4+u*4; box(DK,x+3,y,51,x+14,y+3,53)
        for k in range(3):
            h=(i*37+u*13+k*7)%11; box([LGN,AM,CY,LGN][h%4],x+4+h,y+1,53,x+5+h,y+2,54)
box(IR,168,C-10,40,252,C-8,62)
for k,m in enumerate((OR,CB,GN)): box(m,172,C-8,44+k*5,248,C-6,47+k*5); box(m,172+k*30,Fl+46,44+k*5,175+k*30,C-8,47+k*5)
# ===== 北墙实验台+通风橱 =====
box(IR,40,Fl,170,124,Fl+14,186); box(AN,40,Fl,168,124,Fl+2,170)
for x in range(40,124,14):
    box(QZ,x+1,Fl+2,169,x+13,Fl+13,170); box(DK,x+5,Fl+10,168,x+9,Fl+11,169)
box(WH,38,Fl+14,166,126,Fl+16,186); box(CY,38,Fl+13,165,126,Fl+14,166)
box(IR,40,Fl+16,182,72,Fl+46,186); box(IR,40,Fl+16,168,42,Fl+46,182); box(IR,70,Fl+16,168,72,Fl+46,182)
box(IR,40,Fl+44,168,72,Fl+48,186); box(GL,42,Fl+24,168,70,Fl+42,169); box(DK,42,Fl+23,167,70,Fl+24,169)
box(WG,43,Fl+43,170,69,Fl+44,180); box(GR,52,Fl+48,174,60,C,184); box(IR,51,Fl+48,173,61,Fl+50,185)
for k,m in enumerate((FL,XR,HC)): box(m,46+k*7,Fl+16,174,50+k*7,Fl+24,178); box(GL,47+k*7,Fl+24,175,49+k*7,Fl+27,177)
cyl(LG,84,176,6,Fl+16,Fl+24); cyl(DK,84,176,4,Fl+24,Fl+25); box(LGN,83,Fl+18,169,85,Fl+20,170)
box(DK,104,Fl+16,182,118,Fl+30,184); box(SC,105,Fl+18,181,117,Fl+29,182)
for i in range(10): box(CY,106+i,Fl+20+(i*5)%7,180,107+i,Fl+21+(i*5)%7,181)
def arm(bx,by,bz,s):
    fill(YL,bx-8,by,bz-8,bx+9,by+3,bz+9,lambda x,y,z:(x-bx)**2+(z-bz)**2<=72 and ((x+z)//3)%2==0)
    fill(DK,bx-8,by,bz-8,bx+9,by+3,bz+9,lambda x,y,z:(x-bx)**2+(z-bz)**2<=72 and ((x+z)//3)%2==1)
    cyl(IR,bx,bz,5,by+3,by+14); cyl(DK,bx,bz,6,by+14,by+19); cyl(CY,bx,bz,7,by+16,by+17,6)
    e=(bx,by+40,bz+s*14); w=(bx,by+26,bz+s*30)
    rod(LG,(bx,by+19,bz),e,5); rod(DK,(bx+3,by+19,bz),(e[0]+3,e[1],e[2]),1)
    box(DK,e[0]-4,e[1]-4,e[2]-4,e[0]+4,e[1]+4,e[2]+4); box(CY,e[0]+4,e[1]-1,e[2]-1,e[0]+5,e[1]+1,e[2]+1)
    rod(LG,e,w,4); box(DK,w[0]-3,w[1]-6,w[2]-3,w[0]+3,w[1],w[2]+3); box(MG,w[0]-3,w[1]-3,w[2]-3,w[0]+3,w[1]-2,w[2]+3)
    box(IR,w[0]-4,w[1]-14,w[2]-1,w[0]-2,w[1]-6,w[2]+1); box(IR,w[0]+2,w[1]-14,w[2]-1,w[0]+4,w[1]-6,w[2]+1)
    box(IR,w[0]-4,w[1]-15,w[2]-1,w[0]-1,w[1]-14,w[2]+1); box(IR,w[0]+1,w[1]-15,w[2]-1,w[0]+4,w[1]-14,w[2]+1)
arm(96,Fl+16,178,-1)
box(GR,180,Fl,164,262,Fl+14,186); box(IR,178,Fl+14,162,264,Fl+16,186); box(YL,178,Fl+13,161,264,Fl+14,162)
for x in range(182,262,10): box(DK,x,Fl+2,163,x+8,Fl+12,164); box(AM,x+3,Fl+10,162,x+5,Fl+11,163)
arm(236,Fl+16,178,-1)
box(LG,204,Fl+16,166,220,Fl+20,180); cyl(DK,212,173,4,Fl+20,Fl+26); box(CY,211,Fl+26,172,213,Fl+27,174)
# ===== 管线阀门墙（东墙） =====
box(GR,262,Fl,48,266,56,160)
for x0 in range(262,266): pass
for k,(y,m) in enumerate(((Fl+8,OR),(Fl+18,RD),(Fl+28,CB),(Fl+38,IR))):
    box(m,256,y,48,260,y+4,160)
    for z in range(52,160,24): box(DK,255,y-1,z,261,y+5,z+2)
    zc=60+k*26; diskx(RD,252,253,y+2,zc,6,4)
    box(RD,252,y+1,zc-6,253,y+3,zc+6); box(RD,252,y-4,zc-1,253,y+8,zc+1); box(IR,253,y+1,zc-1,256,y+3,zc+1)
    gz=zc+12; diskx(WH,254,255,y+2,gz,4); diskx(DK,253,254,y+2,gz,4,4)
    box(DK,253,y+2,gz,254,y+5,gz+1); box(RG,253,y+2,gz,254,y+3,gz+1)
    box(m,256,Fl,148+k*3,260,y,151+k*3)
    box(YL,261,y+5,zc-4,262,y+8,zc+4); box(DK,261,y+6,zc-3,262,y+7,zc+3)
box(CY,261,52,48,262,53,160)
# ===== 全息桌 =====
hx,hz=212,112
cyl(DK,hx,hz,14,Fl,Fl+12); cyl(IR,hx,hz,13,Fl+12,Fl+14); cyl(CY,hx,hz,15,Fl+12,Fl+13,13); cyl(WG,hx,hz,3,Fl+14,Fl+15)
hy=Fl+34
fill(HC,hx-12,hy-12,hz-12,hx+13,hy+13,hz+13,lambda x,y,z:110<=(x-hx)**2+(y-hy)**2+(z-hz)**2<=144)
for dy in (-8,0,8): r=int((144-dy*dy)**.5); cyl(CY,hx,hz,r,hy+dy,hy+dy+1,r-1)
rod(HC,(hx,Fl+15,hz),(hx,hy-12,hz),1)
# ===== 工作站 =====
for wz in (60,140):
    box(WH,70,Fl+12,wz,92,Fl+14,wz+30); box(CY,92,Fl+11,wz,93,Fl+12,wz+30)
    box(DK,70,Fl,wz,72,Fl+12,wz+30); box(DK,88,Fl,wz+2,90,Fl+12,wz+4); box(DK,88,Fl,wz+26,90,Fl+12,wz+28)
    for k,(dz,dx) in enumerate(((1,2),(10,0),(19,2))):
        box(DK,71+dx,Fl+16,wz+dz,73+dx,Fl+30,wz+dz+10); box(SC,73+dx,Fl+17,wz+dz+1,74+dx,Fl+29,wz+dz+9)
        for i in range(8): h=(i*3+k*5)%9+2; box([LGN,MG,CY][k],74+dx,Fl+18,wz+dz+1+i,75+dx,Fl+18+h,wz+dz+2+i)
    box(IR,74,Fl+14,wz+13,76,Fl+16,wz+17); box(LG,78,Fl+14,wz+9,84,Fl+15,wz+21)
# ===== 东侧外饰 =====
for az in (72,128):
    box(LG,X1,Fl+4,az,X1+12,Fl+22,az+18); diskx(DK,X1+12,X1+13,Fl+13,az+9,7); box(IR,X1+12,Fl+12,az+2,X1+14,Fl+14,az+16)
    for y in range(Fl+6,Fl+21,3): box(GR,X1+12,y,az+1,X1+13,y+1,az+3)
for pz in (40,176):
    box(IR,X1+1,Fl,pz,X1+4,R+12,pz+3); box(DK,X1,Fl+30,pz-1,X1+5,Fl+32,pz+4); box(DK,X1,R-10,pz-1,X1+5,R-8,pz+4)
# ===== 屋顶 =====
box(DK,150,R,60,284,R+4,164); box(GL,150,R+4,60,284,R+40,164); box(0,152,R+4,62,282,R+40,162)
box(DK,146,R+40,56,286,R+44,168); box(MG,146,R+44,56,286,R+45,58); box(MG,146,R+44,166,286,R+45,168); box(CY,284,R+44,56,286,R+45,168)
for x in range(150,284,16): box(DK,x,R+4,60,x+2,R+40,62); box(DK,x,R+4,162,x+2,R+40,164)
for z in range(60,164,16): box(DK,282,R+4,z,284,R+40,z+2)
box(WG,154,R+38,64,280,R+39,66); box(WG,154,R+38,158,280,R+39,160)
rod(IR,(272,R-30,70),(282,R,70),3); rod(IR,(272,R-30,154),(282,R,154),3)
for z in range(56,172,14):
    for dz in range(12): box(BL,30,R+4+dz//3,z+dz,124,R+5+dz//3,z+dz+1)
    box(LG,30,R+4,z+12,124,R+8,z+13); box(IR,40,R,z+4,42,R+5,z+6); box(IR,112,R,z+4,114,R+5,z+6)
    for x in range(30,124,16): rod(LG,(x,R+4,z),(x,R+8,z+11),1)
box(IR,130,R,40,133,R+90,43); box(RG,129,R+90,39,134,R+94,44)
for y in (R+40,R+60,R+80): box(IR,122,y,41,142,y+1,42); box(CY,122,y-1,41,124,y,42); box(CY,140,y-1,41,142,y,42)
dxc,dzc,dyc=126,178,R+14
box(IR,dxc-1,R,dzc-1,dxc+2,dyc,dzc+2)
fill(WH,dxc-12,dyc,dzc-12,dxc+13,dyc+12,dzc+13,lambda x,y,z:abs((y-dyc)-((x-dxc)**2+(z-dzc)**2)/14)<1.2 and (x-dxc)**2+(z-dzc)**2<=144)
rod(IR,(dxc,dyc,dzc),(dxc,dyc+16,dzc),1); box(RG,dxc-1,dyc+16,dzc-1,dxc+2,dyc+18,dzc+2)
for fx in (190,240):
    cyl(LG,fx,184,8,R,R+8,6); cyl(DK,fx,184,6,R,R+2)
    box(IR,fx-6,R+5,183,fx+7,R+6,185); box(IR,fx-1,R+5,178,fx+1,R+6,191); cyl(CY,fx,184,8,R+8,R+9,7)
# ===== 合并导出 =====
done=bytearray(len(g)); out={}
for y in range(Y):
    for z in range(Z):
        o=(y*Z+z)*X
        if not any(g[o:o+X]): continue
        x=0
        while x<X:
            m=g[o+x]
            if m==0 or done[o+x]: x+=1; continue
            x2=x+1
            while x2<X and g[o+x2]==m and not done[o+x2]: x2+=1
            seg=bytes([m])*(x2-x); zero=bytes(x2-x)
            def ok(yy,zz):
                oo=(yy*Z+zz)*X; return g[oo+x:oo+x2]==seg and done[oo+x:oo+x2]==zero
            z2=z+1
            while z2<Z and ok(y,z2): z2+=1
            y2=y+1
            while y2<Y and all(ok(y2,zz) for zz in range(z,z2)): y2+=1
            for yy in range(y,y2):
                for zz in range(z,z2): oo=(yy*Z+zz)*X; done[oo+x:oo+x2]=b'\x01'*(x2-x)
            out.setdefault(m,[]).append((x,y,z,x2,y2,z2)); x=x2
def ext(t,key,o,c):
    i=t.index(key+':')+len(key)+1; d=0
    for j in range(i,len(t)):
        if t[j]==o: d+=1
        elif t[j]==c:
            d-=1
            if d==0: return t[i:j+1]
P6=r'\[I;(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+),(-?\d+)\]'
def child(fn,dx,dy,dz,rot=False,st=None):
    t=open(fn,encoding='utf-8').read()
    tl=ext(t,'tiles','[',']')
    if rot:
        W=max(int(v[3]) for v in re.findall(P6,tl))
        def r(mm):
            a=list(map(int,mm.groups()))
            return '[I;%d,%d,%d,%d,%d,%d]'%(a[2],a[1],W-a[3],a[5],a[4],W-a[0])
        tl=re.sub(P6,r,tl)
    tl=re.sub(P6,lambda mm:'[I;%d,%d,%d,%d,%d,%d]'%tuple(int(v)+d for v,d in zip(mm.groups(),(dx,dy,dz)*2)),tl)
    s=ext(t,'structure','{','}') if 'structure:' in t else None
    if s and st:
        for k,v in st.items(): s=re.sub(r'\b'+k+r':-?\d+',k+':'+str(v),s)
    return '{tiles:%s%s}'%(tl,',structure:'+s if s else '')
kids=[child('lab_door.txt',X0+2,Fl,104,True,{'direction':3,'distance':16}),
      child('office_chair.txt',93,Fl,68,True),child('office_chair.txt',93,Fl,148,True)]
tiles=[];cnt=0;mn=[9999]*3;mx=[0]*3
for m,bs in out.items():
    cnt+=len(bs)
    for b in bs:
        for i in range(3): mn[i]=min(mn[i],b[i]); mx[i]=max(mx[i],b[i+3])
    bb=','.join('[I;%d,%d,%d,%d,%d,%d]'%b for b in bs)
    tiles.append(('{bBox:%s,tile:{block:"%s"}}'%(bb,mats[m])) if len(bs)==1 else '{boxes:[%s],tile:{block:"%s"}}'%(bb,mats[m]))
txt='{tiles:[%s],children:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'%(','.join(tiles),','.join(kids),*mn,*(mx[i]-mn[i] for i in range(3)),cnt)
# 根有 children ⇒ 根必须有 structure（§3.9）；缺了在此自动插入，断言不过直接报错退出
txt=lt_root.fix(txt,ROOT_NAME,tag='nexus_lab.txt')
open('nexus_lab.txt','w',encoding='utf-8').write(txt)
print('nexus_lab.txt',len(txt),'字节; 小块',cnt,'; 材质',len(out),'; 尺寸(格)',[(mx[i]-mn[i])/16 for i in range(3)])