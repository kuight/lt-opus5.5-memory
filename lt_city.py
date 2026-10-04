import math
from PIL import Image,ImageDraw,ImageFont
from lt_colors import fc
MIRROR=True
FONTS=['C:/Windows/Fonts/simhei.ttf','C:/Windows/Fonts/msyh.ttc','C:/Windows/Fonts/simsun.ttc']
X,Y,Z=384,640,400
g=bytearray(X*Y*Z);mats=[None];mid={}
def M(b):
    if b not in mid: mid[b]=len(mats);mats.append(b)
    return mid[b]
def F(h,k='glow'): return M(fc(h,k))
DK=M('minecraft:concrete:15');GR=M('minecraft:concrete:7');LG=M('minecraft:concrete:8');WH=M('minecraft:concrete')
IR=M('minecraft:iron_block');AN=M('minecraft:stone:6');RD=M('minecraft:concrete:14');YL=M('minecraft:concrete:4')
BR=M('minecraft:concrete:12');QZ=M('minecraft:quartz_block');SM=M('minecraft:stone_slab:8') if False else M('minecraft:stone')
WD=M('minecraft:planks:5');OB=M('minecraft:obsidian');CB=M('minecraft:concrete:9');PK=M('minecraft:concrete:6')
CY=F('#00f0ff');MG=F('#ff1ea8');YG=F('#ffd400');OG=F('#ff6a00');GN=F('#30ff70');WG=F('#f0fbff')
WW=F('#ffcf8a');TV=F('#3a8cff');PL=F('#ff6ad0');SC=F('#061420');RG=F('#ff2020');DW=F('#2a1a10')
GL=F('#bdeeff','trans');GLD=F('#1a3a5a','trans');PUD=F('#3a70b0','trans');STM=F('#ffffff','trans')
def box(m,x1,y1,z1,x2,y2,z2):
    x1,x2=sorted((x1,x2));y1,y2=sorted((y1,y2));z1,z2=sorted((z1,z2))
    x1,y1,z1=max(0,x1),max(0,y1),max(0,z1);x2,y2,z2=min(X,x2),min(Y,y2),min(Z,z2)
    if x1>=x2 or y1>=y2 or z1>=z2: return
    s=bytes([m])*(x2-x1)
    for y in range(y1,y2):
        for z in range(z1,z2):
            o=(y*Z+z)*X;g[o+x1:o+x2]=s
def cyl(m,cx,cz,r,y1,y2,rin=0):
    for dz in range(-r,r+1):
        w=int(max(0,(r+.5)**2-dz*dz)**.5);z=cz+dz
        if rin and (rin-.5)**2>dz*dz:
            wi=int(((rin-.5)**2-dz*dz)**.5)
            box(m,cx-w,y1,z,cx-wi,y2,z+1);box(m,cx+wi+1,y1,z,cx+w+1,y2,z+1)
        else: box(m,cx-w,y1,z,cx+w+1,y2,z+1)
def rod(m,p,q,t):
    n=max(abs(q[i]-p[i]) for i in range(3)) or 1
    for i in range(n+1):
        c=[round(p[k]+(q[k]-p[k])*i/n) for k in range(3)]
        box(m,c[0]-t//2,c[1]-t//2,c[2]-t//2,c[0]-t//2+t,c[1]-t//2+t,c[2]-t//2+t)
FONT={}
def font(h):
    if h not in FONT:
        for p in FONTS:
            try: FONT[h]=ImageFont.truetype(p,h);break
            except OSError: pass
        else: raise SystemExit('找不到字体，改 FONTS')
    return FONT[h]
def bitmap(s,h):
    f=font(h);w=int(f.getlength(s))+2
    im=Image.new('L',(w,h+4),0);ImageDraw.Draw(im).text((1,0),s,255,font=f)
    bb=im.getbbox();im=im.crop(bb);W,H=im.size;px=im.load()
    return W,H,[(c,H-1-r) for r in range(H) for c in range(W) if px[c,r]>110]
def sign_s(s,x0,y0,zf,h,m,bg=DK,pad=3,t=2):
    W,H,pts=bitmap(s,h)
    box(bg,x0-pad,y0-pad,zf,x0+W+pad,y0+H+pad,zf+t);box(m,x0-pad-1,y0-pad-1,zf+t-1,x0+W+pad+1,y0-pad,zf+t)
    box(m,x0-pad-1,y0+H+pad,zf+t-1,x0+W+pad+1,y0+H+pad+1,zf+t)
    for c,r in pts:
        xx=x0+(W-1-c if MIRROR else c);box(m,xx,y0+r,zf-1,xx+1,y0+r+1,zf)
    return W
def vsign_e(s,xf,ytop,z0,h,m,bg=DK):
    n=len(s);yb=ytop-n*(h+4)-4;za,zb=z0-h-4,z0+4
    box(bg,xf,yb,za,xf+6,ytop+4,zb)
    box(m,xf+6,yb,za,xf+7,yb+2,zb);box(m,xf+6,ytop+2,za,xf+7,ytop+4,zb)
    box(m,xf+6,yb,za,xf+7,ytop+4,za+2);box(m,xf+6,yb,zb-2,xf+7,ytop+4,zb)
    y=ytop
    for ch in s:
        W,H,pts=bitmap(ch,h);y-=h+4
        for c,r in pts:
            zz=z0-(W-1-c if not MIRROR else c);box(WG,xf+6,y+r,zz,xf+8,y+r+1,zz+1)
def sign_w(s,xf,y0,z0,h,m):
    W,H,pts=bitmap(s,h)
    for c,r in pts:
        zz=z0+(W-1-c if not MIRROR else c);box(m,xf-2,y0+r,zz,xf,y0+r+1,zz+1)
    return W
def stool(x,z):
    box(IR,x,8,z,x+2,22,z+2);box(IR,x-2,8,z-2,x+4,9,z+4);cyl(RD,x+1,z+1,3,22,24)
def arm(bx,by,bz,tx,ty,tz):
    cyl(YL,bx,bz,5,by,by+3);cyl(IR,bx,bz,3,by+3,by+10);e=(bx,by+26,(bz+tz)//2)
    rod(LG,(bx,by+10,bz),e,4);box(DK,e[0]-3,e[1]-3,e[2]-3,e[0]+3,e[1]+3,e[2]+3)
    rod(LG,e,(tx,ty,tz),3);box(DK,tx-2,ty-4,tz-2,tx+3,ty,tz+3);box(CY,tx-1,ty-5,tz-1,tx+2,ty-4,tz+2)
# ===== 地面 =====
FL=8;ZF=64;ZB=176;GH=88
box(GR,0,0,0,X,4,Z);box(LG,0,4,0,X,FL,ZF);box(CY,0,FL-1,ZF-2,X,FL,ZF-1)
for x in range(8,X,32): box(YL,x,3,12,x+16,4,14)
for x,z,w,d in((40,20,14,8),(150,30,20,6),(300,16,10,10),(220,50,12,6)): box(PUD,x,FL-1 if z>=ZF-0 else 3,z,x+w,FL if z>=ZF else 4,z+d)
# ===== 底层 4 店 =====
box(DK,16,FL,ZF,368,FL+GH+8,ZB+4);box(0,20,FL,ZF+4,364,FL+GH,ZB)
box(SM,20,FL-1,ZF+4,364,FL,ZB)
for i in range(5): box(DK,16+i*88,FL,ZF,20+i*88,FL+GH,ZB)
box(MG,16,FL+GH+6,ZF-2,368,FL+GH+7,ZF);box(CY,16,FL+GH+8,ZF-2,368,FL+GH+9,ZF)
def front(x0,col):
    box(0,x0+4,FL,ZF,x0+84,FL+GH-12,ZF+4);box(DK,x0+4,FL+GH-16,ZF,x0+84,FL+GH-12,ZF+4)
    box(GL,x0+4,FL+4,ZF+1,x0+30,FL+GH-16,ZF+2);box(GL,x0+54,FL+4,ZF+1,x0+84,FL+GH-16,ZF+2)
    box(GR,x0+4,FL,ZF,x0+30,FL+4,ZF+4);box(GR,x0+54,FL,ZF,x0+84,FL+4,ZF+4)
    box(col,x0+29,FL,ZF-1,x0+30,FL+GH-16,ZF);box(col,x0+54,FL,ZF-1,x0+55,FL+GH-16,ZF)
    box(WW,x0+8,FL+GH-1,ZF+20,x0+80,FL+GH,ZF+90)
# 拉面
x0=16;front(x0,RD)
for k in range(5): box([RD,WH][k%2],x0+30+k*5,FL+46,ZF-1,x0+35+k*5,FL+GH-16,ZF)
box(WD,x0+8,FL,ZF+60,x0+80,FL+18,ZF+70);box(DW,x0+6,FL+18,ZF+58,x0+82,FL+20,ZF+72);box(OG,x0+8,FL+17,ZF+57,x0+80,FL+18,ZF+58)
for k in range(6): stool(x0+12+k*11,ZF+50)
for k in range(4):
    bx=x0+14+k*17;cyl(WH,bx,ZF+64,3,FL+20,FL+23,2);box(WW,bx-2,FL+22,ZF+62,bx+3,FL+23,ZF+67)
    box(WD,bx+4,FL+20,ZF+61,bx+5,FL+21,ZF+68);box(WD,bx+6,FL+20,ZF+61,bx+7,FL+21,ZF+68)
for k in range(2):
    cx=x0+24+k*36;cyl(IR,cx,ZF+92,8,FL+20,FL+34);cyl(WW,cx,ZF+92,6,FL+34,FL+35);box(STM,cx-3,FL+36,ZF+90,cx+3,FL+50,ZF+95)
box(IR,x0+8,FL,ZF+84,x0+80,FL+20,ZF+104)
sign_s('拉面  28元',x0+14,FL+56,ZB-2,12,WW,WD)
for k in range(3):
    lx=x0+20+k*24;box(DK,lx,FL+GH-12,ZF+40,lx+1,FL+GH,ZF+41);box(RD,lx-3,FL+GH-24,ZF+37,lx+4,FL+GH-12,ZF+44);box(OG,lx-2,FL+GH-25,ZF+38,lx+3,FL+GH-24,ZF+43)
sign_s('拉面',x0+24,FL+GH+14,ZF-4,20,OG)
# 义体诊所
x0=104;front(x0,GN)
box(WH,x0+30,FL,ZF+60,x0+58,FL+10,ZF+70);box(LG,x0+28,FL+10,ZF+56,x0+60,FL+16,ZF+92);rod(LG,(x0+30,FL+16,ZF+92),(x0+30,FL+34,ZF+100),4)
box(LG,x0+28,FL+16,ZF+92,x0+60,FL+34,ZF+96);box(GN,x0+29,FL+16,ZF+91,x0+59,FL+17,ZF+92)
arm(x0+70,FL,ZF+80,x0+46,FL+30,ZF+76);arm(x0+16,FL,ZF+80,x0+40,FL+30,ZF+70)
box(DK,x0+6,FL,ZB-14,x0+82,FL+70,ZB);box(GL,x0+8,FL+4,ZB-15,x0+80,FL+68,ZB-14)
for r in range(3):
    for k in range(6):
        ax=x0+12+k*12;ay=FL+8+r*20;box(IR,ax,ay,ZB-10,ax+4,ay+14,ZB-6);box(IR,ax-1,ay+12,ZB-11,ax+5,ay+16,ZB-5)
        box([CY,MG,GN][r],ax+1,ay+4,ZB-11,ax+3,ay+10,ZB-10)
    box(DK,x0+8,FL+6+r*20,ZB-14,x0+80,FL+8+r*20,ZB)
box(GN,x0+64,FL+GH+10,ZF-4,x0+80,FL+GH+14,ZF);box(GN,x0+70,FL+GH+4,ZF-4,x0+74,FL+GH+20,ZF)
sign_s('义体诊所',x0+6,FL+GH+8,ZF-4,14,GN)
# 便利店
x0=192;front(x0,CY)
for r in range(3):
    zz=ZF+40+r*24;box(WH,x0+10,FL,zz,x0+60,FL+44,zz+6)
    for lv in range(4):
        box(LG,x0+9,FL+4+lv*11,zz-2,x0+61,FL+5+lv*11,zz+8)
        for k in range(12):
            c=[RD,YL,CB,GN,OG,PK,WH,BR][(k*3+lv*5+r*7)%8];box(c,x0+11+k*4,FL+5+lv*11,zz-1,x0+14+k*4,FL+5+lv*11+4+(k+lv)%4,zz+7)
box(WH,x0+66,FL,ZF+40,x0+84,FL+66,ZB-4);box(GL,x0+65,FL+4,ZF+42,x0+66,FL+64,ZB-6)
for lv in range(5):
    box(WG,x0+66,FL+6+lv*12,ZF+42,x0+70,FL+7+lv*12,ZB-6)
    for k in range(0,60,6): box([GN,OG,CB,RD][(k//6+lv)%4],x0+68,FL+7+lv*12,ZF+44+k,x0+72,FL+15+lv*12,ZF+48+k)
box(WH,x0+6,FL,ZF+10,x0+28,FL+20,ZF+26);box(DK,x0+12,FL+20,ZF+14,x0+22,FL+28,ZF+22);box(CY,x0+13,FL+24,ZF+13,x0+21,FL+27,ZF+14)
box(IR,x0+30,FL,ZF+8,x0+40,FL+18,ZF+18);box(OG,x0+31,FL+18,ZF+9,x0+39,FL+19,ZF+17);box(STM,x0+32,FL+20,ZF+10,x0+38,FL+30,ZF+16)
sign_s('便利店 24H',x0+8,FL+GH+10,ZF-4,12,CY,WH)
# 电玩城
x0=280;front(x0,MG)
box(PK,x0+4,FL-1,ZF+4,x0+84,FL,ZB)
for k in range(4):
    cx=x0+8+k*18;box(DK,cx,FL,ZB-30,cx+14,FL+50,ZB-4);box(SC,cx+1,FL+28,ZB-31,cx+13,FL+46,ZB-30)
    box([CY,MG,YG,GN][k],cx+3,FL+32,ZB-32,cx+11,FL+42,ZB-31);box(DK,cx,FL+20,ZB-40,cx+14,FL+26,ZB-30)
    box(IR,cx+3,FL+26,ZB-37,cx+4,FL+31,ZB-36);box(RG,cx+2,FL+31,ZB-38,cx+5,FL+33,ZB-35)
    for b in range(3): box([RG,YG,CY][b],cx+7+b*2,FL+26,ZB-36,cx+8+b*2,FL+27,ZB-35)
    box([MG,CY][k%2],cx,FL+50,ZB-31,cx+14,FL+52,ZB-30)
box(DK,x0+50,FL,ZF+30,x0+78,FL+20,ZF+58);box(GL,x0+50,FL+20,ZF+30,x0+78,FL+60,ZF+58);box(0,x0+51,FL+20,ZF+31,x0+77,FL+59,ZF+57)
for k in range(30): box([RD,YG,CB,GN,PK][k%5],x0+52+(k*7)%22,FL+20,ZF+32+(k*11)%22,x0+56+(k*7)%22,FL+24+(k%3)*2,ZF+36+(k*11)%22)
box(DK,x0+50,FL+60,ZF+30,x0+78,FL+64,ZF+58);box(IR,x0+63,FL+44,ZF+43,x0+65,FL+60,ZF+45);box(IR,x0+60,FL+40,ZF+43,x0+68,FL+44,ZF+45)
sign_s('电玩城',x0+14,FL+GH+8,ZF-4,16,MG)
# ===== 公寓 9 层 =====
Y0=FL+GH+8;FH=48;TX1,TX2,TZ1,TZ2=32,352,ZF+8,ZB+200
box(DK,TX1,Y0,TZ1,TX2,Y0+9*FH,TZ2);box(0,TX1+6,Y0,TZ1+6,TX2-6,Y0+9*FH,TZ2-6)
ROOMS=['tv','bed','pc','pink']
for f in range(9):
    yb=Y0+f*FH;box(GR,TX1+6,yb,TZ1+6,TX2-6,yb+2,TZ2-6);box(GR,TX1-2,yb,TZ1-3,TX2+2,yb+3,TZ1)
    for u in range(5):
        wx=TX1+12+u*62;rt=ROOMS[(f*3+u*2)%4];z0=TZ1
        box(0,wx,yb+8,z0,wx+40,yb+38,z0+6);box(GLD,wx,yb+8,z0+2,wx+40,yb+38,z0+3);box(DK,wx+19,yb+8,z0+2,wx+21,yb+38,z0+3)
        box(GR,wx-2,yb+6,z0-2,wx+42,yb+8,z0+1)
        zr=z0+30;box(DK,wx-4,yb+2,zr+10,wx+44,yb+FH,zr+12)
        if rt=='tv':
            box(DW,wx-4,yb+2,zr+10,wx+44,yb+FH,zr+11);box(DK,wx+8,yb+18,zr+8,wx+32,yb+32,zr+10);box(TV,wx+9,yb+19,zr+7,wx+31,yb+31,zr+8)
            box(BR,wx+4,yb+2,zr-14,wx+36,yb+10,zr-4);box(BR,wx+4,yb+10,zr-6,wx+36,yb+16,zr-4)
        elif rt=='bed':
            box(DW,wx-4,yb+2,zr+10,wx+44,yb+FH,zr+11);box(WH,wx+4,yb+2,zr-16,wx+30,yb+9,zr+8);box(CB,wx+4,yb+9,zr-16,wx+30,yb+10,zr+2)
            box(WH,wx+6,yb+10,zr+2,wx+28,yb+12,zr+7);box(WD,wx+32,yb+2,zr,wx+40,yb+10,zr+8);box(WW,wx+34,yb+10,zr+2,wx+38,yb+16,zr+6)
        elif rt=='pc':
            box(SC,wx-4,yb+2,zr+10,wx+44,yb+FH,zr+11);box(WD,wx+4,yb+12,zr,wx+36,yb+14,zr+8);box(DK,wx+8,yb+16,zr+4,wx+32,yb+28,zr+6)
            box(CY,wx+9,yb+17,zr+3,wx+19,yb+27,zr+4);box(GN,wx+21,yb+17,zr+3,wx+31,yb+27,zr+4);box(DK,wx+14,yb+2,zr-10,wx+24,yb+14,zr-6)
        else:
            box(PL,wx-4,yb+2,zr+10,wx+44,yb+FH,zr+11);box(GN,wx+30,yb+2,zr+2,wx+36,yb+20,zr+8);box(BR,wx+30,yb+2,zr+2,wx+36,yb+8,zr+8)
        ac=wx+44;box(LG,ac,yb+10,z0-8,ac+12,yb+20,z0);cyl(DK,ac+6,z0-8,3,yb+12,yb+19)
        box(GR,ac+3,yb+10,z0-9,ac+9,yb+20,z0-8)
    box([CY,MG][f%2],TX1-2,yb+3,TZ1-3,TX2+2,yb+4,TZ1-2)
box(GR,TX2-8,FL,TZ1-6,TX2-4,Y0+9*FH,TZ1-2)
for y in range(Y0,Y0+9*FH,FH): box(IR,TX2-10,y,TZ1-8,TX2-2,y+2,TZ1)
for x,z in((TX1-4,TZ1-4),(TX2,TZ1-4),(TX1-4,TZ2),(TX2,TZ2)): box(MG,x,Y0,z,x+4,Y0+9*FH,z+4)
vsign_e('霓虹公寓',TX2,Y0+8*FH,TZ1+150,40,MG)
YB=Y0+3*FH;box(DK,TX1-10,YB,TZ1+20,TX1-4,YB+150,TZ2-20)
for i in range(30): box([F('#2a0a40'),F('#6a0a6a'),F('#c0108a'),F('#ff1ea8'),F('#ff6a9a')][i//6],TX1-12,YB+4+i*5,TZ1+24,TX1-10,YB+9+i*5,TZ2-24)
W=sign_w('夜之城',TX1-12,YB+80,TZ1+40,56,WG);sign_w('NIGHT CITY',TX1-12,YB+30,TZ1+50,28,CY)
box(CY,TX1-13,YB,TZ1+20,TX1-12,YB+2,TZ2-20);box(CY,TX1-13,YB+148,TZ1+20,TX1-12,YB+150,TZ2-20)
# ===== 屋顶 =====
YR=Y0+9*FH;box(DK,TX1,YR,TZ1,TX2,YR+4,TZ2);box(CY,TX1,YR+4,TZ1,TX2,YR+6,TZ1+2);box(CY,TX1,YR+4,TZ2-2,TX2,YR+6,TZ2)
cyl(DK,120,TZ2-90,48,YR+4,YR+6);cyl(YG,120,TZ2-90,48,YR+6,YR+7,45)
box(WG,104,YR+6,TZ2-110,110,YR+7,TZ2-70);box(WG,130,YR+6,TZ2-110,136,YR+7,TZ2-70);box(WG,110,YR+6,TZ2-93,130,YR+7,TZ2-87)
for dx,dz in((-10,-10),(8,-10),(-10,8),(8,8)): box(IR,280+dx,YR+4,TZ1+60+dz,282+dx,YR+24,TZ1+62+dz)
cyl(WD,281,TZ1+61,20,YR+24,YR+64);cyl(DK,281,TZ1+61,22,YR+64,YR+70);cyl(IR,281,TZ1+61,21,YR+40,YR+42)
box(IR,300,YR+4,TZ2-40,304,YR+120,TZ2-36);box(RG,299,YR+120,TZ2-41,305,YR+126,TZ2-35)
for y in(YR+50,YR+80,YR+105): box(IR,290,y,TZ2-39,314,y+2,TZ2-37)
# ===== 细节补充 =====
# 街面：路灯、消防栓、垃圾桶、自动售货机、井盖
for lx in (40,200,340):
    box(IR,lx,FL,20,lx+3,FL+90,23);box(IR,lx,FL+87,20,lx+3,FL+90,42)
    box(DK,lx-3,FL+83,34,lx+6,FL+87,44);box(WG,lx-2,FL+82,35,lx+5,FL+83,43)
cyl(RD,100,30,3,FL,FL+10);cyl(RD,100,30,4,FL+10,FL+12);box(RD,96,FL+5,29,105,FL+7,32);box(YL,99,FL+12,29,102,FL+14,32)
cyl(GN,150,24,5,FL,FL+14,4);cyl(DK,150,24,5,FL+14,FL+15);box(WH,148,FL+15,22,153,FL+16,27)
box(RD,260,FL,46,276,FL+32,58);box(GL,262,FL+8,45,274,FL+28,46);box(WG,262,FL+29,45,274,FL+31,46);box(DK,262,FL+2,45,274,FL+6,46)
for r in range(3):
    for k in range(4): box([CY,YG,GN,OG][(k+r)%4],263+k*3,FL+10+r*6,46,265+k*3,FL+14+r*6,48)
cyl(IR,320,30,6,FL-1,FL);cyl(DK,320,30,4,FL-1,FL,3)
# 拉面店：饮料冰柜
x0=16;box(WH,x0+70,FL,ZF+10,x0+82,FL+40,ZF+24);box(GL,x0+69,FL+2,ZF+11,x0+70,FL+38,ZF+23)
for lv in range(4):
    for k in range(4): box([GN,OG,CY,RD][(k+lv)%4],x0+72,FL+4+lv*9,ZF+12+k*3,x0+74,FL+10+lv*9,ZF+14+k*3)
# 义体诊所：心电监护仪 + 地面十字
x0=104;box(IR,x0+64,FL,ZF+62,x0+66,FL+36,ZF+64);box(DK,x0+58,FL+36,ZF+60,x0+72,FL+48,ZF+63);box(SC,x0+59,FL+37,ZF+59,x0+71,FL+47,ZF+60)
for i,h in enumerate([2,2,2,4,0,8,1,2,3,2,2]): box(GN,x0+60+i,FL+38+h,ZF+58,x0+61+i,FL+39+h,ZF+59)
box(GN,x0+40,FL-1,ZF+20,x0+46,FL,ZF+38);box(GN,x0+34,FL-1,ZF+26,x0+52,FL,ZF+32)
# 便利店：杂志架
x0=192;box(WD,x0+6,FL,ZF+30,x0+28,FL+14,ZF+36)
for k in range(5): box([RD,CB,YL,PK,GN][k],x0+7+k*4,FL+14,ZF+31,x0+10+k*4,FL+22,ZF+32)
# 电玩城：兑奖柜 + 顶部霓虹灯管
x0=280;box(DK,x0+8,FL,ZF+12,x0+40,FL+16,ZF+20);box(GL,x0+8,FL+16,ZF+12,x0+40,FL+26,ZF+20);box(0,x0+9,FL+16,ZF+13,x0+39,FL+25,ZF+19)
for k in range(7): box([YG,PK,CB,GN,RD,CY,OG][k],x0+10+k*4,FL+16,ZF+14,x0+13+k*4,FL+19+k%3*2,ZF+18)
box(MG,x0+8,FL+GH-3,ZF+30,x0+80,FL+GH-2,ZF+31);box(CY,x0+8,FL+GH-3,ZF+70,x0+80,FL+GH-2,ZF+71)
# 公寓东/西/北三面窗户（避开招牌），每户空调外机
LITE=[WW,TV,PL,WW,DK,CY]
for f in range(9):
    yb=Y0+f*FH
    for k in range(5):
        a=TZ1+20+k*62;c=LITE[(f*5+k*3)%6]
        if not(f>=4 and a in(154,216)):
            box(0,TX2-6,yb+8,a,TX2,yb+38,a+40);box(GLD,TX2-4,yb+8,a,TX2-3,yb+38,a+40)
            box(c,TX2-34,yb+2,a-4,TX2-32,yb+FH-2,a+44);box(GR,TX2,yb+6,a-2,TX2+3,yb+8,a+42)
            box(LG,TX2,yb+12,a+42,TX2+8,yb+22,a+54);cyl(DK,TX2+8,a+48,3,yb+13,yb+21)
        if not 3<=f<=6:
            box(0,TX1,yb+8,a,TX1+6,yb+38,a+40);box(GLD,TX1+3,yb+8,a,TX1+4,yb+38,a+40)
            box(c,TX1+32,yb+2,a-4,TX1+34,yb+FH-2,a+44);box(GR,TX1-3,yb+6,a-2,TX1,yb+8,a+42)
        b=TX1+12+k*62;c=LITE[(f*3+k)%6]
        box(0,b,yb+8,TZ2-6,b+40,yb+38,TZ2);box(GLD,b,yb+8,TZ2-4,b+40,yb+38,TZ2-3)
        box(c,b-4,yb+2,TZ2-34,b+44,yb+FH-2,TZ2-32);box(GR,b-2,yb+6,TZ2,b+42,yb+8,TZ2+3)
        box(LG,b+44,yb+10,TZ2,b+56,yb+20,TZ2+8);cyl(DK,b+50,TZ2+8,3,yb+12,yb+19)
# 北面消防梯（之字形）
for f in range(1,10):
    yb=Y0+f*FH-FH if f>1 else Y0
    box(IR,96,yb,TZ2,236,yb+2,TZ2+18)
    for x in range(96,237,6): box(IR,x,yb+2,TZ2+16,x+1,yb+14,TZ2+17)
    box(IR,96,yb+13,TZ2+16,236,yb+14,TZ2+17)
    if f<9:
        for i in range(12):
            xs=110+i*8 if f%2 else 214-i*8
            box(IR,xs,yb+2+i*4,TZ2+4,xs+8,yb+3+i*4,TZ2+14)
box(GR,TX1+8,FL,TZ2,TX1+12,YR,TZ2+4);box(GR,TX2-12,FL,TZ2,TX2-8,YR,TZ2+4)
# 架空层：立柱 + 停车位 + 顶棚灯格
for px in (48,192,336):
    for pz in (250,350):
        box(DK,px-5,FL,pz-5,px+5,Y0,pz+5);box(YL,px-5,FL,pz-6,px+5,FL+20,pz-5);box(CY,px-6,FL+40,pz-6,px+6,FL+42,pz+6)
for x in range(56,330,48):
    box(WG,x,FL-1,190,x+2,FL,300);box(WG,x,Y0-1,200,x+30,Y0,203);box(WG,x,Y0-1,280,x+30,Y0,283)
for x in range(66,330,96):
    box(CB,x,FL,215,x+26,FL+14,265);box(GLD,x+2,FL+14,225,x+24,FL+24,252);box(CB,x,FL+14,252,x+26,FL+18,262)
    box(DK,x-1,FL,220,x+27,FL+6,228);box(DK,x-1,FL,252,x+27,FL+6,260)
    box(WG,x+3,FL+8,214,x+9,FL+11,215);box(WG,x+17,FL+8,214,x+23,FL+11,215);box(RG,x+3,FL+8,265,x+23,FL+10,266)
sign_s('P',176,FL+60,TZ2-4,20,CY)
# ===== 导出 =====
done=bytearray(len(g));out={}
for y in range(Y):
    for z in range(Z):
        o=(y*Z+z)*X
        if not any(g[o:o+X]): continue
        x=0
        while x<X:
            m=g[o+x]
            if m==0 or done[o+x]: x+=1;continue
            x2=x+1
            while x2<X and g[o+x2]==m and not done[o+x2]: x2+=1
            seg=bytes([m])*(x2-x);zero=bytes(x2-x)
            def ok(yy,zz):
                oo=(yy*Z+zz)*X;return g[oo+x:oo+x2]==seg and done[oo+x:oo+x2]==zero
            z2=z+1
            while z2<Z and ok(y,z2): z2+=1
            y2=y+1
            while y2<Y and all(ok(y2,zz) for zz in range(z,z2)): y2+=1
            for yy in range(y,y2):
                for zz in range(z,z2): oo=(yy*Z+zz)*X;done[oo+x:oo+x2]=b'\x01'*(x2-x)
            out.setdefault(m,[]).append((x,y,z,x2,y2,z2));x=x2
tiles=[];cnt=0;mn=[9999]*3;mx=[0]*3
for m,bs in out.items():
    cnt+=len(bs)
    for b in bs:
        for i in range(3): mn[i]=min(mn[i],b[i]);mx[i]=max(mx[i],b[i+3])
    bb=','.join('[I;%d,%d,%d,%d,%d,%d]'%b for b in bs)
    tiles.append(('{bBox:%s,tile:{block:"%s"}}'%(bb,mats[m])) if len(bs)==1 else '{boxes:[%s],tile:{block:"%s"}}'%(bb,mats[m]))
txt='{tiles:[%s],min:[I;%d,%d,%d],size:[I;%d,%d,%d],count:%d}'%(','.join(tiles),*mn,*(mx[i]-mn[i] for i in range(3)),cnt)
open('neon_city.txt','w',encoding='utf-8').write(txt)
print('neon_city.txt %.2f MB; 小块 %d; 材质 %d; 尺寸(格) %s'%(len(txt)/1048576,cnt,len(out),[(mx[i]-mn[i])/16 for i in range(3)]))