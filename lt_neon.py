import random,math
from lt_colors import fc
R=random.Random(2077)
GREEBLE=54
X,Y,Z=384,640,384
g=bytearray(X*Y*Z);mats=[None];mid={}
def M(b):
    if b not in mid: mid[b]=len(mats);mats.append(b)
    return mid[b]
def F(h,k='glow'): return M(fc(h,k))
DK=M('minecraft:concrete:15');GR=M('minecraft:concrete:7');LG=M('minecraft:concrete:8');WH=M('minecraft:concrete')
IR=M('minecraft:iron_block');AN=M('minecraft:stone:6');RD=M('minecraft:concrete:14');YL=M('minecraft:concrete:4')
BL=M('minecraft:concrete:11');OR=M('minecraft:concrete:1');OB=M('minecraft:obsidian')
CY=F('#00f0ff');MG=F('#ff1ea8');YG=F('#ffd400');OG=F('#ff6a00');GN=F('#30ff70');WG=F('#f0fbff')
WW=F('#ffd9a0');CO=F('#bfe0ff');PD=F('#6a1058');CD=F('#0a4a5a');SC=F('#061420');RG=F('#ff2020')
GLW=F('#1a3a5a','trans');PUD=F('#3a70b0','trans');HM=F('#ff1ea8','trans');HC=F('#00f0ff','trans')
NEON=[CY,MG,YG,OG,GN];ROOM=[WW,WW,CO,DK,DK,DK,PD,CD]
GRAD=[F(h) for h in('#2a0a40','#5a0a6a','#a0108a','#ff1ea8','#ff6a9a')]
GRAD2=[F(h) for h in('#001a30','#003a5a','#006a8a','#00b0c8','#00f0ff')]
def box(m,x1,y1,z1,x2,y2,z2):
    x1,x2=sorted((x1,x2));y1,y2=sorted((y1,y2));z1,z2=sorted((z1,z2))
    x1,y1,z1=max(0,x1),max(0,y1),max(0,z1);x2,y2,z2=min(X,x2),min(Y,y2),min(Z,z2)
    if x1>=x2 or y1>=y2 or z1>=z2: return
    s=bytes([m])*(x2-x1)
    for y in range(y1,y2):
        for z in range(z1,z2):
            o=(y*Z+z)*X;g[o+x1:o+x2]=s
def put(m,x,y,z):
    if 0<=x<X and 0<=y<Y and 0<=z<Z: g[(y*Z+z)*X+x]=m
def fill(m,x1,y1,z1,x2,y2,z2,f):
    for y in range(y1,y2):
        for z in range(z1,z2):
            for x in range(x1,x2):
                if f(x,y,z): put(m,x,y,z)
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
def cable(p,q,sag,m=DK,lant=0):
    n=int(max(abs(q[i]-p[i]) for i in range(3)))+1
    for i in range(n+1):
        t=i/n;c=(round(p[0]+(q[0]-p[0])*t),round(p[1]+(q[1]-p[1])*t-sag*4*t*(1-t)),round(p[2]+(q[2]-p[2])*t))
        put(m,*c)
        if lant and i%lant==lant//2:
            box(DK,c[0],c[1]-3,c[2],c[0]+1,c[1],c[2]+1);box(RD,c[0]-2,c[1]-9,c[2]-2,c[0]+3,c[1]-3,c[2]+3);box(OG,c[0]-1,c[1]-10,c[2]-1,c[0]+2,c[1]-9,c[2]+2)
def ring(m,x1,x2,z1,z2,y1,y2,t=1):
    box(m,x1-t,y1,z1-t,x2+t,y2,z1);box(m,x1-t,y1,z2,x2+t,y2,z2+t)
    box(m,x1-t,y1,z1,x1,y2,z2);box(m,x2,y1,z1,x2+t,y2,z2)
def face(r,s):
    x1,x2,z1,z2=r
    def f(m,u1,v1,w1,u2,v2,w2):
        if s==0: box(m,x2-u1,v1,z1-w1,x2-u2,v2,z1-w2)
        elif s==1: box(m,x1+u1,v1,z2+w1,x1+u2,v2,z2+w2)
        elif s==2: box(m,x1-w1,v1,z1+u1,x1-w2,v2,z1+u2)
        else: box(m,x2+w1,v1,z2-u1,x2+w2,v2,z2-u2)
    return f,(x2-x1 if s<2 else z2-z1)
FONT={'2':["111","001","111","100","111"],'0':["111","101","101","101","111"],'7':["111","001","010","010","010"],
'N':["101","111","111","111","101"],'E':["111","100","110","100","111"],'O':["111","101","101","101","111"]}
def text(f,s,u0,v0,w1,w2,m,px):
    for i,ch in enumerate(s):
        for r,row in enumerate(FONT[ch]):
            for c,b in enumerate(row):
                if b=='1': f(m,u0+(i*4+c)*px,v0+(4-r)*px,w1,u0+(i*4+c+1)*px,v0+(5-r)*px,w2)
def glyph():
    b=[[R.random()<.4 for c in range(5)] for r in range(5)]
    b[R.randrange(5)]=[True]*5;k=R.randrange(5)
    for r in range(5): b[r][k]=True
    return b
def blade(f,u,v1,v2,W,col):
    f(DK,u,v1,0,u+4,v2,W);f(col,u-1,v1,W-1,u+5,v2,W);f(col,u-1,v2-1,0,u+5,v2,W);f(col,u-1,v1,0,u+5,v1+1,W)
    f(IR,u,v1+8,0,u+4,v1+10,W+2);f(IR,u,v2-10,0,u+4,v2-8,W+2)
    for i in range((v2-v1-8)//36):
        b=glyph();cc=R.choice(NEON)
        for r in range(5):
            for c in range(5):
                if b[r][c]:
                    v=v2-6-i*36-(r+1)*6;w=W//2-15+c*6
                    f(cc,u-1,v,w,u,v+5,w+5);f(cc,u+4,v,w,u+5,v+5,w+5)
def billboard(f,u0,v0,W,H,txt,px,grad):
    f(DK,u0-4,v0-4,6,u0+W+4,v0+H+4,10)
    for k in range(4):
        uu=u0+k*(W-4)//3;f(IR,uu,v0+H//3,0,uu+4,v0+H//3+4,6);f(IR,uu,v0+2*H//3,0,uu+4,v0+2*H//3+4,6)
    n=len(grad)
    for i in range(H//4): f(grad[i*n//(H//4)],u0,v0+i*4,10,u0+W,v0+i*4+4,11)
    for i in range(0,W,4):
        v=v0+H//3+int(H/6*math.sin(i/12));f(WG,u0+i,v,11,u0+i+4,v+2,12)
    tw=len(txt)*4*px-px;text(f,txt,u0+(W-tw)//2,v0+H-5*px-6,11,13,WG,px)
    for m,a in ((MG,v0-5),(MG,v0+H+4)): f(m,u0-5,a,9,u0+W+5,a+1,11)
    f(CY,u0-5,v0-5,9,u0-4,v0+H+5,11);f(CY,u0+W+4,v0-5,9,u0+W+5,v0+H+5,11)
def shell(r,y1,y2,m=DK):
    x1,x2,z1,z2=r;box(m,x1,y1,z1,x2,y2,z2);box(0,x1+4,y1,z1+4,x2-4,y2-4,z2-4)
def corners(r,y1,y2,m):
    x1,x2,z1,z2=r
    for x,z in((x1-2,z1-2),(x2,z1-2),(x1-2,z2),(x2,z2)): box(m,x,y1,z,x+2,y2,z+2)
def facade(r,y1,y2,s):
    f,L=face(r,s)
    for v in range(y1,y2-31,32):
        f(GR,0,v,0,L,v+2,2)
        if R.random()<.35: f(R.choice(NEON),0,v+2,1,L,v+3,2)
        for u in range(8,L-31,32):
            f(0,u+4,v+6,-4,u+28,v+26,0);f(GLW,u+4,v+6,-3,u+28,v+26,-2);f(DK,u+15,v+6,-3,u+17,v+26,-2)
            f(R.choice(ROOM),u+2,v+2,-26,u+30,v+30,-24)
            t=R.random()
            if t<.25:
                f(GR,u+2,v+2,0,u+30,v+4,10);f(IR,u+2,v+12,9,u+30,v+13,10)
                for k in range(2,31,4): f(IR,u+k,v+4,9,u+k+1,v+12,10)
                if R.random()<.5: f(R.choice([GN,DK,RD]),u+R.randrange(4,20),v+4,2,u+R.randrange(22,28),v+R.randint(6,10),R.randint(5,8))
            elif t<.6:
                a=u+R.choice((4,16));f(LG,a,v+1,0,a+10,v+6,6)
                for k in range(0,5,2): f(GR,a+1,v+1+k,6,a+9,v+2+k,7)
            if R.random()<.15: f(R.choice(NEON),u+3,v+26,0,u+29,v+27,1)
            for _ in range(GREEBLE):
                a=u+R.randrange(0,28);vv=v+R.choice((2,3,27,28))
                if R.random()<.2: f(R.choice(NEON),a,vv,0,a+1,vv+1,R.randint(1,3))
                else: f(R.choice([GR,LG,AN,IR,OB]),a,vv,0,a+R.randint(2,6),vv+R.randint(1,3),R.randint(1,3))
def shop(f,u):
    f(0,u+4,6,-4,u+44,54,0);f(LG,u+6,6,-14,u+42,20,-10);f(R.choice(NEON),u+6,20,-14,u+42,21,-10)
    f(WW,u+6,52,-34,u+42,53,-6);f(R.choice([WW,CO,MG,CY,PD]),u+4,6,-36,u+44,52,-34)
    for v in range(40,54,2): f(IR if v%4 else GR,u+4,v,-2,u+44,v+2,-1)
    c=R.choice(NEON);f(DK,u+2,58,0,u+46,74,3);f(c,u+2,57,0,u+46,58,4);f(c,u+2,74,0,u+46,75,4)
    for i in range(4):
        b=glyph()
        for r in range(5):
            for cc in range(5):
                if b[r][cc]: f(c,u+4+i*10+cc*2,60+(4-r)*2,3,u+6+i*10+cc*2,62+(4-r)*2,4)
    cols=[R.choice(NEON+[RD,BL]),WH]
    for w in range(12):
        v=56-w//3
        for k in range(0,40,4): f(cols[(k//4)%2],u+4+k,v,w,u+8+k,v+1,w+1)
    if R.random()<.5:
        for k in (8,20,32):
            f(DK,u+k+1,51,11,u+k+2,53,12);f(RD,u+k,44,10,u+k+4,51,14);f(OG,u+k+1,43,11,u+k+3,44,13)
    f(LG,u+30,77,0,u+44,87,7)
    for k in range(0,10,2): f(GR,u+31,78+k,7,u+43,79+k,8)
A=(64,320,64,320);B=(96,352,48,300);P=(32,352,32,352)
# 街面
box(GR,0,0,0,X,4,Z)
for i in range(0,X,24):
    for a,b2 in ((i,10),(10,i),(i,372),(372,i)): box(YL,a,3,b2,a+(12 if b2 in(10,372) else 2),4,b2+(2 if b2 in(10,372) else 12))
for _ in range(50):
    x,z=R.randrange(0,370),R.choice([R.randrange(0,18),R.randrange(362,380)])
    if R.random()<.5: x,z=z,x
    box(PUD,x,3,z,x+R.randint(6,18),4,z+R.randint(4,12))
box(LG,24,4,24,360,6,360);ring(CY,24,360,24,360,4,5)
# 裙楼
shell(P,6,96);ring(CY,32,352,32,352,92,93);ring(MG,32,352,32,352,8,9)
for x in range(48,340,24): box(CD,x,5,36,x+1,6,348)
for s in range(4):
    f,L=face(P,s)
    for u in range(16,L-47,48): shop(f,u)
    f(BL,2,6,0,14,36,8);f(CY,3,10,8,13,30,9);f(MG,3,32,8,13,34,9)
# 主楼 A / B
shell(A,96,288);shell(B,288,480)
for v in range(96,288,32): box(GR,68,v,68,316,v+2,316)
for v in range(288,480,32): box(GR,100,v,52,348,v+2,296)
for s in range(4): facade(A,96,288,s);facade(B,288,480,s)
corners(A,96,286,MG);corners(B,288,478,CY)
for x in range(100,350,16):
    for z in range(52,298,16):
        if not(64<=x<320 and 64<=z<320): box(CY,x,287,z,x+10,288,z+10)
for z in (80,160,240,300): rod(IR,(320,200,min(z,316)),(348,286,min(z,296)),3)
for x in (120,200,280): rod(IR,(x,200,64),(x,286,52),3)
for k in range(64,321,8): box(IR,64,288,k,65,298,k+1);box(IR,k,288,320,k+1,298,321)
box(IR,64,296,64,65,297,320);box(IR,64,296,320,320,297,321);box(CY,66,288,66,68,289,318);box(CY,66,288,316,318,289,318)
f,L=face(A,2)
for u in (L-40,L-32):
    f(OR,u,96,0,u+4,286,4)
    for v in range(100,286,32): f(IR,u-2,v,0,u+6,v+2,5)
f,L=face(A,0);blade(f,12,110,280,40,MG)
f,L=face(A,3);blade(f,L-16,120,272,36,CY)
f,L=face(A,1);billboard(f,60,180,136,64,'NEON',6,GRAD2)
f,L=face(B,2);blade(f,24,300,470,44,YG)
f,L=face(B,1);blade(f,L-30,310,460,36,GN)
f,L=face(B,3);billboard(f,40,330,168,104,'2077',8,GRAD)
# 楼冠
for k in range(6):
    a=k*10;y=480+k*20;x1,x2,z1,z2=144+a,304-a,96+a,256-a
    box(DK,x1,y,z1,x2,y+20,z2);ring(GLW,x1,x2,z1,z2,y+6,y+14);ring([CY,MG][k%2],x1,x2,z1,z2,y+18,y+19)
    for i in range(x1+8,x2-8,16): box(OB,i,y,z1-3,i+2,y+20,z1);box(OB,i,y,z2,i+2,y+20,z2+3)
    for i in range(z1+8,z2-8,16): box(OB,x1-3,y,i,x1,y+20,i+2);box(OB,x2,y,i,x2+3,y+20,i+2)
cyl(IR,224,176,5,600,632)
for y in (606,614,622): cyl(DK,224,176,8,y,y+2);cyl(CY,224,176,9,y+2,y+3,8)
cyl(RG,224,176,2,632,640)
cyl(HM,224,176,118,520,521,116);cyl(HC,224,176,96,556,557,94)
for i in range(8):
    a=i*math.pi/4;x,z=int(224+117*math.cos(a)),int(176+117*math.sin(a))
    box(HC,x,480,z,x+1,520,z+1)
# 屋顶设施
cyl(DK,328,278,20,480,482);cyl(YG,328,278,20,482,483,18)
box(YL,320,482,270,323,483,286);box(YL,333,482,270,336,483,286);box(YL,323,482,277,333,483,279)
for z in (70,130,190):
    for dx,dz in((-8,-8),(6,-8),(-8,6),(6,6)): box(IR,118+dx,480,z+dz,120+dx,488,z+dz+2)
    cyl(LG,118,z,12,488,516);cyl(RD,118,z,13,500,503,12);cyl(DK,118,z,10,516,518)
for x,z in((180,282),(250,282)):
    box(IR,x-1,480,z-1,x+2,492,z+2)
    fill(WH,x-10,492,z-10,x+11,500,z+11,lambda a,b,c:abs((b-492)-((a-x)**2+(c-z)**2)/14)<1.2 and (a-x)**2+(c-z)**2<=100)
    rod(IR,(x,492,z),(x,504,z),1);box(RG,x-1,504,z-1,x+2,506,z+2)
for z in (70,130,190,240):
    cyl(GR,330,z,12,480,488,10);cyl(DK,330,z,10,480,486)
    box(IR,320,486,z-1,340,487,z+1);box(IR,329,486,z-10,331,487,z+10);cyl(CY,330,z,12,488,489,11)
# 灯杆与电线
pts=[(10,10),(370,10),(370,370),(10,370)]
for x,z in pts:
    box(IR,x,4,z,x+4,180,z+4);box(DK,x-2,176,z-2,x+6,184,z+6);box(CY,x-2,175,z-2,x+6,176,z+6)
    tx=64 if x<100 else 318;tz=64 if z<100 else 318
    for k in range(3): cable((x+2,178-k*4,z+2),(tx,240-k*24,tz),16+k*6)
for i in range(4):
    (x1,z1),(x2,z2)=pts[i],pts[(i+1)%4]
    cable((x1+2,172,z1+2),(x2+2,172,z2+2),36,DK,24);cable((x1+2,166,z1+2),(x2+2,166,z2+2),48)
# 合并导出
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
open('neon_tower.txt','w',encoding='utf-8').write(txt)
print('neon_tower.txt %.2f MB; 小块 %d; 材质 %d; 尺寸(格) %s'%(len(txt)/1048576,cnt,len(out),[(mx[i]-mn[i])/16 for i in range(3)]))